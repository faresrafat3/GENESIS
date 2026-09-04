# Virtual-GENESIS

**A harness-first cognitive agent layer on top of LLM APIs.**  
Testing two central hypotheses:

> **🚀 For complete setup, OpenRouter configuration (gpt-oss-120b:free), evolutionary discovery, and running on serious benchmarks (SWE-bench, gpqa, etc.):**  
> **See the full guide: `SETUP_AND_RUN_GUIDE.md`** (includes exact commands for real paper-level experiments after cloning).

---

1. **Concept Formation** outperforms retrieval-only adaptation.
2. **Cognitive Economy** (intelligent tiered routing + resource allocation) outperforms stronger-model-only scaling.

> ⚠️ **Primary reference:** The internal regime lock and current status documents (Arabic). All other descriptions are subordinate to them.

---

## Key Results (Live Runs)

**Primary thesis slice** (`prototype_v3b_curriculum` — 72 tasks):

| Condition                  | Success Rate | Avg Cost (simulated) | Notes |
|---------------------------|--------------|----------------------|-------|
| Baseline (retrieval only) | 79.2%       | —                    | — |
| + Concept Formation       | **98.6%**   | 0.000736             | +24.5% absolute improvement |
| + Cognitive Economy       | 98.6%       | **0.0023** (vs 0.010 premium-always) | **4.3× cost reduction** at same performance |
| Combined (Canonical)      | **98.6%**   | **0.000736**         | Best efficiency |

**Governance Ablation (Cycle 5.1)** — Does Layer B buy peak performance or robustness?

- `use_theory_leverage`: No gain in success (still 98.61%), but **2.94× cost**.
- `use_anomaly_leverage`: Reaches **100%**, but at **13.59× cost** (forces premium tier on everything).

**Conclusion from live data**: Governance buys **robustness**, not cheap peak performance. This is why Layer B remains gated (OFF by default) on the canonical path.

Full details: `results/ablation_summary_2026-06-01.md`

---

## Architecture (3 Layers)

### Layer A — Core Epistemic Engine (Locked 🔒)
The value core. Only touched with strong empirical justification.

- Task framing (6 families: comparison, synthesis, procedure, analysis, extraction, planning)
- Memory OS (lifecycle, clustering, productive forgetting, consolidation)
- Concept Formation Engine (proposer from success/failure contrasts + family-specific selectivity)
- Economy Control (tier router with expected value calculation, anomaly/theory overrides)
- Verification Runtime (contract-based: required properties + forbidden shortcuts)
- Minimal Pipeline runner

### Layer B — Governance Expansions (Gated, OFF by default 🧪)
Experimental mechanisms that add robustness at a cost:

- Anomaly leverage
- Theory leverage
- Productive forgetting
- Identity governance
- Paradigm fork
- Self-benchmarking
- Contradiction detection

### Layer C — Interface & Infrastructure
- REST API + OpenRouter adapter
- SQLite persistence
- Evaluation runners and perturbation curricula (research-only)

**Canonical path** (the approved, locked path for the main thesis):
```bash
python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum
```

Governance flags are available for ablation only:
```bash
VIRTUAL_SIA_USE_THEORY_LEVERAGE=true  python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum
VIRTUAL_SIA_USE_ANOMALY_LEVERAGE=true python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum
```

---

## Quickstart

**Requirements**: Python 3.10+

```bash
git clone https://github.com/faresrafat3/GENESIS.git
cd GENESIS
pip install -e ".[dev]"
pytest -q          # ~460 tests should pass (463 collected as of 2026-09-04)
```

**Run the canonical evaluation** (no API key needed — fully local simulation):
```bash
python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum
```

**Real LLM experiments** (research-only):
```bash
export OPENROUTER_API_KEY=your_key
python -m virtual_genesis.eval.runners.run_adversarial_llm_eval
```

For the full self-improving orchestrator (advanced):
```bash
python -m genesis.orchestrator --task <bundled_task> --max_gen 3
```

See `genesis/tasks/` for the self-evolution missions (including the critical cognitive integration bridge task).

---

## Current Status (snapshot: 2026-06-05 comprehensive baseline; minimal code churn since)

> ⚠️ **Temporal honesty**: This section was authored when the comprehensive baseline report `GENESIS_RESEARCH_REPORT_Current_State_2026-06-05_AR.md` was committed (2026-06-05, commit `3cbe48b`). The status bullets describe the implementation as of that snapshot. Since then, the code has had only a few minimal commits (notably the `pyproject` dev-deps addition in `07d1ab0` and the test-count correction in `81ae910`), none of which change the architectural state described below. The 463 tests in the bullet are verified as passing in 4.51s on 2026-09-04. For a fully-current status, see the most recent `git log --oneline -20`.

- **Strongly implemented**: Task ingress, Blackboard, Memory OS, Concept Engine (with proposer + selectivity), Economy-aware routing, evaluation framework, ~460 tests, live ablations.
- **Scaffolding / Template-based**: Reasoning and verification (currently keyword + template driven — explicitly acknowledged as a limitation).
- **Critical pending work**: Full integration of the orchestrator with the Virtual-GENESIS cognitive pipeline as a reasoning substrate for real LLMs (see `genesis/tasks/genesis_cognitive_integration/` — this is Phase 1 of the strategic plan).
- **Research output**: Detailed Arabic research memos, Master Architecture, and a full Research Paper Draft (`GENESIS_Research_Paper_Draft_AR.md`).

This is an advanced **research/execution prototype**, not a finished production system. Layer A is partially validated (strongest on H2 & H6). Layers B and C are maturing.

---

## Documentation Map

| Purpose                          | Document                                      |
|----------------------------------|-----------------------------------------------|
| Highest structural lock          | GENESIS_Internal_Regime_Lock_AR.md (or Virtual_SIA_...) |
| Current regime & status          | GENESIS_Current_Regime_Status_AR.md          |
| Theoretical architecture         | GENESIS_Master_Architecture_AR.md            |
| Research program (H1–H9)         | GENESIS_Research_Program_AR.md               |
| Full paper draft                 | GENESIS_Research_Paper_Draft_AR.md           |
| Strategic development plan       | STRATEGIC_DEVELOPMENT_PLAN_2026_06.md        |
| Live ablation evidence           | results/ablation_summary_2026-06-01.md       |
| 75+ "Legitimate Thefts" sources  | GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md |

All primary documentation is in Arabic. English summaries are being added.

---

## Installation & Development

```bash
pip install -e ".[dev]"
pytest -q
```

The core has **zero external runtime dependencies** (stdlib only: urllib, sqlite3, etc.). `pytest` is dev-only.

---

## Roadmap Highlights (from Strategic Plan)

**Phase 1 (Critical)**: Bridge the orchestrator with the cognitive pipeline so real LLM calls are guided by concepts, memory, tier decisions, and theories — moving beyond pure templates.

**Phase 2+**: Concept gating with regression budgets, graph-structured memory, stronger self-benchmarking, self-healing orchestration.

See the full plan in `STRATEGIC_DEVELOPMENT_PLAN_2026_06.md`.

---

## Contributing

This is currently a solo research project with heavy internal documentation. Contributions are welcome, especially around:

- Strengthening reasoning & verification beyond keywords/templates
- Real LLM integration experiments
- Expanding the perturbation curriculum
- English documentation & examples

Please read the regime lock and current status documents before proposing changes to Layer A.

---

## License

Proprietary for now (research phase). License may change as the project matures.

---

**Virtual-GENESIS** — Building intelligence through externalized cognitive mechanisms rather than model scaling alone.

For the deepest context, start with the Research Paper Draft and the Master Architecture document.