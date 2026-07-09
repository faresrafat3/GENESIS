# §11 Future Work

## 11.1 Instant vs Thinking Architecture Interaction (Primary Future Direction)

**User-specified priority.** Not yet started per explicit request (research first, this after baseline solid).

### The Question
> **Does GENESIS orchestration interact differently with reasoning-heavy models vs instant models?**

### Preliminary Hypothesis
- **Instant models** (Llama 3.3 70B on Groq, Gemini Flash, Phi-4): may benefit MORE from architecture (which "adds thinking" externally)
- **Thinking models** (gpt-oss-120b, Nemotron Ultra, gpt-5, o-series, DeepSeek-R1): may benefit LESS or even be hurt (double-thinking)

### Experimental Design (F1)

| Model Class | Model | GENESIS Δ | Interpretation |
|---|---|---|---|
| Thinking, big | gpt-oss-120b | (from T1) | reference |
| Thinking, medium | Nemotron-Nano | ? | Δ vs T1 |
| Thinking, tiny | LFM-2.5-thinking | ? | Δ vs T1 |
| Instant, big | Llama-3.3-70B | ? | key comparison |
| Instant, medium | Phi-4 | ? | — |
| Instant, tiny | Llama-3.1-8B | ? | — |

**Predicted pattern:**
```
GENESIS_Δ over pure_baseline
     ↑
+15% |                        instant
     |                    •
+10% |               •
     |          •
 +5% |     •
     |•                                thinking
   0 |—————————————————————•——————•
     |                                  •
 -5% |
     └────────────────────────────────────→
       Model reasoning depth
```

### What This Would Answer
1. Does architecture "compensate" for shallow reasoning in instant models?
2. Does architecture add friction to already-reasoning models?
3. Where's the optimal "reasoning depth × architecture complexity" trade-off?

**This is potentially standalone paper #2.**

## 11.2 SWE-bench Integration

### Motivation
GPQA = knowledge benchmark. SWE-bench = real software engineering (fix GitHub issues).

Different signal:
- Multi-step planning
- Tool use (grep, edit, run tests)
- Verifiable outcome (tests pass or don't)

### Implementation Path
- Adapt `run_openrouter_benchmark.py --task swe_bench`
- Requires: SWE-bench-Verified task data (public)
- Requires: Docker sandbox for test execution

### Expected Insights
- Does scaffolding matter as much on non-MCQ tasks?
- Do reasoning saturation patterns generalize?
- Do agentic systems (multi-step planning) actually beat pure LLM here?

## 11.3 Multi-Agent Debate (Co-Scientist-style)

Currently GENESIS uses sequential 3-agent pipeline (meta → target → feedback). Extension:

- **Debate mode**: 2+ target agents produce answers; 1 debater agent argues; 1 judge decides
- Reference: Co-Scientist [4], Multi-Agent Debate literature (Du et al. 2023)

### Expected
- Debate likely helps on ambiguous questions
- Cost: 3-5× more API calls per question
- Time-quality trade-off analysis

## 11.4 Multi-Provider Pool Implementation

Currently 9 providers documented, only OpenRouter active. Full implementation would enable:

- **Parallel** Google Gemini + Groq + OpenRouter → 7000+ req/day
- **Full 198q runs** in <2 hours
- **Cross-provider consistency checks**

**Deferred per user** (research first).

## 11.5 Router/Model Selection Study

**Only after** thinking/instant study (F1) provides data. Then:

- Design router: task complexity → model choice
- Study cost/quality trade-offs
- Compare with/without router

**Explicit note:** user vetoed "just build router" — this must be research-motivated.

## 11.6 Cross-Framework Validation

Replicate our scaffolding audit on:
- LangChain / LangGraph
- DSPy
- CrewAI
- AutoGen

**Method:**
1. Take a public example from each framework's docs
2. Run on GPQA Diamond
3. Apply `tools/diagnose_run_53.py`
4. Report bug counts and impact estimates

**Expected finding:** most frameworks have B4 (empty content) and B5 (invalid retry) bugs. B1 (case) less common in schema-based frameworks (DSPy).

## 11.7 Reasoning-Cap Study (T-Reasoning-Cap)

Test H3b (saturation) vs H3a (confound):
- Same questions × 5 max_tokens settings (2K, 4K, 8K, 16K, 32K)
- 5 reps each = 25 runs per question
- Statistical: paired within-question comparison

**Expected:** IF saturation exists, we see peak at intermediate cap.

## 11.8 Human Baseline

Recruit science PhDs to answer same 20q:
- Compare to gpt-oss-120b 75%
- Compare per-domain (are humans also weak in Chemistry Organic?)
- Provides interpretive frame for "hard" vs "easy" questions

## 11.9 Long-term: Constitutional Learning

Currently constitutional evaluator is rule-based (`llm_evaluation=False`).

Extension: LLM-based evaluation that **learns from feedback**:
- Track which rules matter for accuracy
- Auto-generate new rules from patterns
- Similar to Constitutional AI (Anthropic)

## 11.10 Ordered Roadmap

### Q3 2026 (immediate):
- T1: GENESIS post-fix on 20q → §7
- T2: Full 198q run → §7
- T3: Ablation studies → §8

### Q4 2026:
- F1: Instant vs Thinking study → paper #2 potentially
- T4: Cross-model baseline (Gemma 4 31B, Nemotron Ultra, gpt-5)
- Multi-provider pool implementation

### 2027:
- SWE-bench integration
- Multi-agent debate
- Router with research backing
- Cross-framework validation

### Long-term:
- Human baseline studies
- Constitutional learning
- Publish standardized "scaffolding audit" protocol as benchmark itself

---

**Section status:** 🟡 Skeleton clear. Roadmap intentional and prioritized.
