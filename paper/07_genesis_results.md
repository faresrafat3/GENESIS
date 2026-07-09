# §7 GENESIS Results (Post-Fix)

## Status: 🔴 Pending T1 Experiment

هذا القسم سيتم ملؤه بعد تشغيل **T1** (GENESIS مع scaffolding fixes على 20-question subset).

## Planned Structure

### 7.1 T1 Setup
- Same model: `gpt-oss-120b:free`
- Same benchmark: GPQA Diamond 20q
- Full GENESIS pipeline (meta + target + feedback + pipeline + constitutional + evolutionary discovery)
- With `genesis/llm_helpers.py` integrated

### 7.2 T1 Results (⏳)

**Table 7.1 (planned):** GENESIS vs Baseline
| Setup | Accuracy | Invalid | Recovered | Time | Notes |
|---|---|---|---|---|---|
| Pure baseline (§5) | 75.00% | 0 | 3 | 35.9min | reference |
| GENESIS pre-fix (run_53) | 30.30% | 0 (fake) | 0 | ? | historic |
| **GENESIS post-fix (T1)** | **?** | ? | ? | ? | to measure |

### 7.3 Comparison to Reference Papers

Once we have T1 numbers:
- Compare to AlphaEvolve (Figure 3-style progress curves)
- Compare to Aletheia (iteration → correctness convergence)
- Note where our scale/domain differs

### 7.4 Three Scenarios

Depending on T1 outcome:

**Scenario A (GENESIS > 75%):** Architecture adds value ✨
- Analyze which generations contribute
- Compare Gen 1 vs Gen 2
- Test with/without evolutionary discovery
- **Section becomes primary claim of paper**

**Scenario B (GENESIS ≈ 75%):** Architecture neutral
- No benefit, no harm
- Discuss whether scaffolding is the entirety of "value" in current systems
- Sub-question: is the pipeline being used at all?

**Scenario C (GENESIS < 75%):** Architecture hurts
- More bugs to diagnose
- Ablation becomes critical
- Discuss possible causes (over-orchestration, wrong pipeline signals, etc.)

### 7.5 T2 Setup (Full 198q)

If T1 promising → run T2 (full benchmark).
- 5-8 hours runtime
- Confidence interval ±3.5%

### 7.6 T2 Results (⏳)
[TBD]

---

**When agents fill this section, cross-reference:**
- §5 (baseline)
- §6 (bugs fixed)
- §8 (ablation attribution)
- §9 (interpretation)

**Section status:** 🔴 Awaiting T1 execution
