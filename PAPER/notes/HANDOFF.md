# 📋 HANDOFF — آخر حالة للمشروع

**آخر تحديث:** 2026-06-05 (Session 5)
**آخر commit (قبل ما السيشن تعلق):** `78430fc`

---

## ✅ المكتمل

- ✅ PAPER.md v0.2 + 10 figures + aggregated data
- ✅ PAPER_PROTOCOL.md + handoff system
- ✅ genesis/llm_helpers.py (463 tests passing)
- ✅ 11 OpenRouter keys + 5 Gemini keys + GitHub PAT (gpt-5)
- ✅ **Bug #6 fixed:** extract_response_text tuple unpacking
- ✅ `tasks/gpqa_subset_20` for fast paper-grade iteration
- ✅ `run_openrouter_benchmark.py` supports `--task_dir` + `--ablation_mode`
- ✅ `run_57` — first post-fix architecture comparison (65%)
- ✅ `run_58` — A3 ablation (no_pipeline) → Gen1 = 70%
- ✅ **A7 infrastructure ready** — `narrow_feedback` and `no_pipeline+narrow_feedback` modes wired into orchestrator (this session)

---

## 🔴 الحالة البحثية الحالية

| Run | Architecture | Gen 1 | Gen 2 | Delta vs pure |
|---|---|---|---|---|
| Pure baseline | none | 75.0% | — | 0 |
| `run_53` | GENESIS pre-fix (buggy) | 30.3% | — | −44.7 |
| `run_57` | GENESIS post-fix (standard) | 65.0% | 65.0% | −10.0 |
| `run_58` | A3 (no_pipeline) | **70.0%** | 60.0% | −5.0 / −15.0 |
| `run_59` (pending) | A7a (narrow_feedback) | ? | ? | ? |
| `run_60` (pending) | A7b (no_pipeline + narrow_feedback) | ? | ? | ? |
| `run_61` (pending) | A7c (no feedback at all) | ? | — | ? |

---

## 🎯 Next: Run the three A7 experiments

This session **wired the code** for A7 but did not execute the runs (free tier consumption + sandbox limits).
The orchestrator now accepts `--ablation_mode narrow_feedback` and `--ablation_mode no_pipeline+narrow_feedback`.

### Highest priority next runs (on Fares's machine)

See **Table 15** (`PAPER/tables/tab15_a7_design.md`) for full CLI commands and pre-registered hypotheses.

Recommended order:
1. **A7b first** (`no_pipeline+narrow_feedback`) — combines both confirmed/suspected fixes, highest expected score.
2. **A7a second** (`narrow_feedback` only) — isolates whether narrow feedback alone fixes Gen 2 drift.
3. **A7c third** (`max_gen=1`) — control to confirm feedback adds anything at all.

### After A7 results

- If A7b ≥ 75%: GENESIS finally matches/beats pure baseline → first positive RQ2 answer.
- If A7b < 75%: move to A5 (constitutional pressure) and A6 (evolutionary discovery).

---

## 📊 الأرقام الحرجة المحفوظة

- Pure baseline: **75.00%** (n=20)
- GENESIS pre-fix (run_53): **30.30%** (n=198)
- GENESIS post-fix (run_57 gen1/gen2): **65.00% / 65.00%**
- A3 no_pipeline (run_58 gen1/gen2): **70.00% / 60.00%**
- Recovery from buggy run: **+34.7 points**
- Half of residual gap explained by pipeline overhead (+5 from A3)
- Tests: 463/463

---

## ✍️ What changed in this session

1. Added `narrow_feedback` and `no_pipeline+narrow_feedback` to `--ablation_mode` choices in both:
   - `genesis/orchestrator.py`
   - `run_openrouter_benchmark.py`
2. Decomposed `ablation_mode` into independent flags (`no_pipeline_active`, `narrow_feedback_active`) so they can be combined cleanly.
3. Added a strict feedback-agent instruction block that forbids broad refactoring and only allows targeted fixes for the specific wrong-answer questions.
4. Created `PAPER/tables/tab15_a7_design.md` with pre-registered hypotheses and reproducible CLI commands.
5. Updated this HANDOFF + SESSION_LOG + TODO.

**No new actual ablation runs were executed in this session** — only the infrastructure to make A7 runnable.
