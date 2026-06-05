# GPQA-style benchmark (`diamond_questions.json`) — 20-question QUICK subset

This is a **speed-optimized subset** of GPQA Diamond for fast iteration on GENESIS.

- Total questions: **20**
- Question IDs: **1–20** from the original GPQA Diamond ordering
- Domains included: Physics, Chemistry, Biology

## Purpose

Use this subset to:

1. debug target_agent generation quickly
2. compare **pure baseline vs GENESIS** on the *same* subset
3. measure whether scaffolding fixes actually work before paying the cost of the full 198-question run

## Data

Each record in `diamond_questions.json` has:

- `id` — stable question identifier
- `domain`, `subdomain` — topic labels
- `Question` — stem
- `options` — dict with keys `A`, `B`, `C`, `D`

## Objective

**Maximize correct answers on the 20-question subset.**

This subset is intentionally small for iteration speed. Any promising result here should later be validated on the full 198-question benchmark.

## Output Format

Write answers to `answers.json` and/or `submission.json` in this format:

```json
{
  "details": [
    {"question_id": 1, "model_answer": "A"}
  ]
}
```

## Important

- The scorer uses the private copy of this same 20-question subset.
- This benchmark is for **fast research iteration**, not final paper-level reporting.
- Final claims should be confirmed on the full GPQA Diamond benchmark.
