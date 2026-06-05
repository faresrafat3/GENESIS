# Table 15: A7 Ablation Design — Narrow Feedback (with optional pipeline removal)

## Motivation

After `run_57` and `run_58`, two clear suspects remain for the residual architecture gap:

1. **Pipeline overhead** (partially confirmed by A3: removing it raised Gen 1 from 65 → 70)
2. **Feedback drift** (suggested by both runs — Gen 2 either stagnant in `run_57` or actively worse in `run_58`)

A3 attacked suspect #1.
A7 attacks suspect #2.

---

## Design

A7 introduces a new `narrow_feedback` ablation flag that **restricts the feedback agent** to:

| Allowed | Forbidden |
|---|---|
| Targeted fixes for the specific wrong-answer questions | Broad refactoring or restructuring |
| Minimal prompt additions that demonstrably help on those wrong questions | Renaming variables, reorganizing imports |
| Bug fixes that prevent crashes or invalid answers | Adding new features, abstractions, helpers |
| Outputting the same code byte-for-byte if no targeted fix is found | Touching code paths unrelated to wrong-answer questions |

This isolates whether feedback drift is caused by **over-broad rewriting** as opposed to feedback being fundamentally net-negative.

---

## Three planned A7 experiments

| Ablation ID | Configuration | Purpose |
|---|---|---|
| **A7a** | Standard GENESIS + `narrow_feedback` | Does narrowing feedback alone close the Gen2 gap? |
| **A7b** | `no_pipeline` + `narrow_feedback` | Does combining the two fixes give us the strongest configuration so far? |
| **A7c** | Standard GENESIS + no feedback (Gen 1 only) | Control: confirm whether feedback adds anything when removed entirely (vs narrowed) |

---

## CLI invocation (for reproducibility)

```bash
# A7a — narrow feedback only
python run_openrouter_benchmark.py \
  --task_dir tasks/gpqa_subset_20 \
  --max_gen 2 \
  --run_id 59 \
  --meta_model openai/gpt-oss-120b:free \
  --task_model openai/gpt-oss-120b:free \
  --ablation_mode narrow_feedback

# A7b — no_pipeline + narrow feedback (the strongest combined hypothesis)
python run_openrouter_benchmark.py \
  --task_dir tasks/gpqa_subset_20 \
  --max_gen 2 \
  --run_id 60 \
  --meta_model openai/gpt-oss-120b:free \
  --task_model openai/gpt-oss-120b:free \
  --ablation_mode no_pipeline+narrow_feedback

# A7c — Gen 1 only (no feedback at all)
python run_openrouter_benchmark.py \
  --task_dir tasks/gpqa_subset_20 \
  --max_gen 1 \
  --run_id 61 \
  --meta_model openai/gpt-oss-120b:free \
  --task_model openai/gpt-oss-120b:free
```

---

## Pre-registered hypotheses

| Outcome | Interpretation |
|---|---|
| **A7a Gen2 > A3 Gen2 (60%)** | Narrow feedback fixes the drift even with pipeline still active. |
| **A7b Gen2 ≥ 70%** | The combined configuration is the first competitive GENESIS variant. Strong paper result. |
| **A7b Gen2 ≥ 75%** | GENESIS finally meets or beats the pure baseline. Architecture value provisionally supported. |
| **A7a ≈ run_57** | Feedback drift is not about scope — feedback is fundamentally net-neutral or harmful in current form. |
| **A7c > A7a** | No feedback beats narrow feedback → feedback should be removed entirely until redesigned. |

---

## Decision rule

We adopt the same paper-honesty standard as Table 13:

**No configuration receives credit unless it produces a controlled score delta on the same 20-question GPQA subset, with a clear question-level explanation of where the delta came from.**

If A7b reaches or beats 75%, that becomes the first positive answer to RQ2 in the paper.
If not, we proceed to A5 (constitutional pressure) and A6 (evolutionary discovery).
