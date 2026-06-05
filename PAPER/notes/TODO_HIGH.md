# 🔴 TODO — أولويات حرجة

1. **[ABLATION — A7 RUNS]** Execute the three A7 experiments on Fares's machine.
   - A7b first: `--ablation_mode no_pipeline+narrow_feedback` (highest expected score)
   - A7a second: `--ablation_mode narrow_feedback`
   - A7c third: `--max_gen 1` (control — no feedback)
   - Full CLI in `PAPER/tables/tab15_a7_design.md`.
   - Infrastructure for this is already wired in `genesis/orchestrator.py` (this session).

2. **[ABLATION — DECISION]** Based on A7 results:
   - If A7b ≥ 75% → first positive RQ2 answer. Update Abstract + Conclusion.
   - If A7b < 75% → proceed to A5 (constitutional pressure) then A6 (evolutionary discovery).

3. **[PAPER]** After A7 runs complete, update:
   - Abstract (with A7 numbers)
   - Section 6.6+ (new A7 results section)
   - Section 8.3 (architecture-value claim — now answerable)
   - Conclusion (revised final claim)
   - `PAPER/data/aggregated_results.json` (add run_59, run_60, run_61)

4. **[DATA]** Only after a configuration becomes competitive (≈75%) on the 20Q subset, scale to full 198 GPQA.

5. **[INFRA — OPTIONAL]** Activate Gemini × 11 keys (Fares will provide).
   - 1,500 RPD/model → enables cross-model baseline experiments.

6. **[INFRA — OPTIONAL]** Activate Groq × 11 keys.
   - 315 tok/s → enables fast iteration.
