# §3 GENESIS Architecture & Methodology

## 3.1 System Overview

GENESIS هو LLM orchestration framework بيشتغل بـ 3 مراحل:
1. **Meta-Agent** ينتج `target_agent.py` من task spec
2. **Target Agent** ينفذ المهمة الفعلية
3. **Feedback Agent** يقرأ نتائج Gen N ويحسن للـ Gen N+1

عبر متعدد الأجيال، النظام يعمل self-improvement.

### Figure 3.1: High-Level Architecture

```
                        User provides
                     ┌─────────────────────┐
                     │  Task Specification │
                     │   (task.md, data)   │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │    Meta-Agent       │
                     │  (writes code)      │
                     └──────────┬──────────┘
                                │ Gen 1 target_agent.py
                                ▼
        ┌───────────────────────────────────────────────┐
        │              Generation Loop                  │
        │  ┌─────────────────┐    ┌──────────────────┐  │
        │  │  Target Agent   │───►│  Task Execution  │  │
        │  │   (runs code)   │    │  → results       │  │
        │  └─────────────────┘    └────────┬─────────┘  │
        │                                  │            │
        │  ┌─────────────────────────────────▼─────┐    │
        │  │   Cognitive Pipeline (Virtual-GENESIS)│    │
        │  │   • Memory  • Concepts  • Theory      │    │
        │  │   • Tier Decision  • Verification     │    │
        │  └─────────────────────────────────┬─────┘    │
        │                                    │          │
        │            ┌───────────────────────▼────┐     │
        │            │   Evaluator + Constitutional │    │
        │            │   Checks + Evolutionary      │    │
        │            │   Discovery                  │    │
        │            └───────────────┬──────────────┘    │
        │                            │ Gen N+1           │
        │            ┌───────────────▼──────────────┐    │
        │            │       Feedback Agent         │    │
        │            │   (revises target_agent.py)  │    │
        │            └──────────────────────────────┘    │
        └───────────────────────────────────────────────┘
```

## 3.2 Meta-Agent (Code Generation)

**Function:** يقرأ `task.md` + reference agent + sample execution، ثم يكتب `target_agent.py` كامل.

**Prompt design** (in `genesis/orchestrator.py:META_AGENT_PROMPT`):
- Explicit imports at top (prevents scope errors)
- Pipeline call template (safe dict access)
- Q&A guidance section (post-fix, references `genesis.llm_helpers`)
- Robust execution logging template

**Post-fix additions** (commit `3a16a87`):
- 5 CRITICAL warnings for each bug category (§6)
- Explicit multi-case JSON key reading
- `max_tokens=16384` for reasoning models
- `SCIENTIFIC_MCQ_SYSTEM_PROMPT` template

## 3.3 Target Agent (Task Execution)

**Function:** الـ agent المولد يحل المهمة الفعلية. Uses:
- Cognitive pipeline for reasoning guidance
- LLM client for final decisions
- `genesis.llm_helpers` for robust response parsing

**Isolation:** Runs in dedicated venv (`runs/run_X/venv/`) with packages: `pandas, numpy, sklearn, openai, virtual_genesis`.

## 3.4 Evolutionary Discovery (AlphaEvolve-inspired)

**Function:** بعد كل generation، نطبق evolutionary search على agent code:
- **Population** = variants of current agent (size=6)
- **Mutation** = LLM-driven code edits (skeleton currently)
- **Selection** = multi-objective (performance + robustness − cost + diversity bonus)
- **Generations** = 1-2 per orchestrator generation

**Reference:** AlphaEvolve/FunSearch (§2.1)

**Skeleton implementation:** `evolutionary_discovery_engine()` in `orchestrator.py`
- Uses real pipeline calls as evaluator
- Uses `evaluation_results.json` for fitness (real accuracy, not proxy)
- Uses `constitutional_report.json` for robustness

**Known limitations:**
- Mutation is currently deterministic string edits (needs LLM upgrade)
- No cross-over between variants (single-parent lineage)
- Fitness weighting is heuristic (0.6 fitness + 0.3 robustness − 0.1 cost)

## 3.5 Feedback Agent (Verify-Revise, Aletheia-inspired)

**Function:** يقرأ Gen N execution log + eval results + constitutional report، ثم يكتب `target_agent.py` محسّن.

**Input signals:**
- `execution_status` (success/failure)
- `evaluation_results.json` (accuracy)
- `constitutional_report.json` (rule violations)
- Full previous code

**Post-fix additions** (commit `3a16a87`):
- Diagnostic framework: "if accuracy ~25% → check B1", "if invalid >10% → check B4/B5", etc.
- Each diagnosis maps to specific fix

**Reference:** Aletheia's Generator-Verifier-Reviser (§2.2)

## 3.6 Multi-Agent Structure (Co-Scientist-inspired)

**Current implementation: Sequential (not debate)**
- Meta → Target → Feedback → Target(N+1) → ...

**Deferred to §11:**
- Full multi-agent debate (Co-Scientist style)
- Argument generation between critic agents

## 3.7 Cognitive Pipeline (Virtual-GENESIS)

**Function:** Provides "cognitive substrate" for reasoning:
- **Memory OS:** persistent memory across generations
- **Concept Engine:** concept formation
- **Theory Registry:** theory-based prediction
- **Tier Decision:** cognitive tier selection
- **Verification:** self-verification

**Used by target_agent:**
```python
result = run_minimal_pipeline(
    raw_task=task_text,
    store=store, concept_registry=..., theory_registry=..., ledger_store=...,
    use_memory=True, use_economy=True, use_concepts=False,
)
tier = result['tier_decision']['chosen_tier']
verification = result['blackboard']['verification_state']
```

**Purpose:** Guides target_agent's LLM calls (informs prompts with tier info, verification feedback).

**Known concern (from data):** Currently unclear if pipeline data actually influences final answers. §8 ablation will test this.

## 3.8 Constitutional Evaluator

**Function:** Rule-based automated review of target_agent code.
- Checks for: forbidden patterns, unsafe practices, quality heuristics
- Outputs: `constitutional_report.json` with `passed`, `total_score`, `violations`

**Note:** No LLM evaluation currently (`llm_evaluation=False`).

## 3.9 Data Flow Summary

### Table 3.1: What Each Component Contributes to Final Answer

| Component | Direct effect on answer? | Indirect effect? |
|---|---|---|
| Meta-Agent | ✅ Writes the code that produces answer | — |
| Target Agent | ✅ Executes and produces answer | — |
| Cognitive Pipeline | ❌ (currently) | ✅ (informs prompts) |
| Evolutionary Discovery | ❌ (post-hoc) | ✅ (may evolve better agent) |
| Feedback Agent | ❌ (next generation only) | ✅ (improves Gen N+1) |
| Constitutional Eval | ❌ | ✅ (informs feedback) |

**Critical observation:** Only Meta-Agent + Target Agent affect current generation's accuracy. Everything else affects **future generations**. This has ablation implications (§8).

## 3.10 Evaluation Protocol

### Primary Metric: Accuracy on GPQA Diamond
- **Correct:** predicted letter matches truth (A/B/C/D)
- **Incorrect:** wrong letter
- **Invalid:** no valid letter extracted
- Accuracy = correct / total (invalid counts against, no fallback to "A")

### Secondary Metrics
- **Invalid rate:** % where extraction failed
- **Recovered:** % that succeeded on follow-up call
- **Reasoning tokens per question**
- **Empty content rate:** % where `content=""`
- **Per-domain accuracy** (Physics/Chemistry/Biology)

### Comparison Setups
1. **Pure baseline:** direct API call, no GENESIS scaffolding
2. **GENESIS pre-fix:** original orchestrator (run_53)
3. **GENESIS post-fix:** with `genesis/llm_helpers.py` (T1, pending)
4. **GENESIS ablations:** each component removed (T3, pending)

## 3.11 Implementation Details

### Runtime Environment
- Python 3.13
- Per-run isolated venv
- Packages: openai, pandas, numpy, scikit-learn, python-dotenv, pydantic

### Testing
- **463 total tests passing** (35 llm_helpers + 428 existing)
- pytest configuration in `pyproject.toml`

### Reproducibility
- All prompts version-controlled in git
- All seeds fixed (temperature=0)
- All API responses logged raw

---

## References

- AlphaEvolve/FunSearch → §2.1
- Aletheia → §2.2  
- Co-Scientist → §2.3

**Section status:** 🟡 Skeleton with content. Needs Figure 3.1 as proper SVG.
