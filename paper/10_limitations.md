# §10 Limitations

نقدم الـ limitations بصراحة كاملة، منظمة حسب الفئة:

## 10.1 Statistical Limitations

### L1: Small Sample Size
- Primary results on **20-question subset** (of 198 total)
- **95% CI: ±10 points** — cannot detect small effects
- Cross-model comparisons underpowered
- **Mitigation:** planned 198q run (T2)

### L2: Physics-Biased Subset
- Our 20q sample is 55% Physics (vs 43% in full benchmark)
- **Real-world implication:** our headline accuracy (75%) may drop 3-5 points on full 198q
- **Mitigation:** clearly report per-domain in all comparisons; run T2

### L3: Single Model Family for Deep Analysis
- Detailed analysis (reasoning tokens, empty content) only on `gpt-oss-120b`
- May not generalize to non-reasoning models (Phi-4, Llama)
- **Mitigation:** cross-model reasoning analysis planned (T4)

## 10.2 Benchmark Limitations

### L4: Single Task Family (MCQ)
- All results on GPQA (multiple-choice)
- Doesn't test:
  - Open-ended generation (WritingBench, HumanEval)
  - Multi-step tool use (SWE-bench, AgentBench)
  - Long-horizon planning
- **Mitigation:** future work SWE-bench (deferred)

### L5: GPQA-Specific Idiosyncrasies
- GPQA has known quirks:
  - Some questions have ambiguous phrasing
  - Ground truth occasionally disputed
  - Options sometimes hint via length/complexity
- Our results reflect these; direct comparison to other MCQ benchmarks (MMLU, ARC) may differ

## 10.3 Model Access Limitations

### L6: Free Tier Only (So Far)
- All experiments on OpenRouter free tier
- Free variants may have:
  - Quantization (BF16 vs FP8 vs MXFP4)
  - Different context sizes
  - Rate limits affecting reproducibility
- **Mitigation:** compare to official benchmarks (§5.3) — 75% vs 80.1% suggests quantization impact <10pts

### L7: Rate Limit Interference
- NVIDIA Nemotron models exhausted daily during testing
- Gemma 4 31B (highest official GPQA) not tested due to rate limits
- **Mitigation:** multi-provider infrastructure (§4.3.2) designed for this; needs implementation

## 10.4 Methodological Limitations

### L8: No Human Baseline
- We compare to model official numbers, not human performers
- Would strengthen claims to have expert human evaluation of same 20q
- **Note:** GPQA paper reports human PhD ~65% (see §2.5)

### L9: No Multi-Framework Comparison
- We only ran GENESIS (our own framework)
- Cannot claim scaffolding bugs are universal without testing on LangChain/DSPy/CrewAI/AutoGen
- **Mitigation:** Table 6.3 discusses estimated susceptibility; empirical replication is future work

### L10: Reasoning Analysis Depends on API Metadata
- `reasoning_tokens` reporting varies by provider
- Some providers don't expose `reasoning_details`
- Cannot analyze non-reasoning models this way
- **Mitigation:** documented in §4; reported when available

## 10.5 Interpretation Limitations

### L11: Correlation vs Causation for Reasoning Saturation
- Data shows: incorrect answers have more reasoning tokens
- **Cannot conclude:** more reasoning CAUSES worse answers
- Could be: harder questions → more reasoning → more errors (confound)
- **Mitigation:** T-Reasoning-Cap experiment proposed (§9.2)

### L12: Bug Attribution is Estimated
- We estimate B1 = -30pts, B2 = -15pts, etc.
- These are **not measured in perfect isolation**
- Compound effects mean total exceeds sum
- **Mitigation:** Table 6.2 discusses; ablation studies (T3) could improve

## 10.6 Deferred Work

### L13: Multi-Provider Pool Not Yet Built
- 9 providers documented, only OpenRouter active
- Cannot leverage Gemini's 1500/day for full 198q runs yet
- **Explicit user deferral** (per session 2026-06-05)

### L14: Instant vs Thinking Study Not Yet Started
- Original T5 experiment proposal
- **Explicit user deferral** — do it "at the end" after baseline solid

### L15: Router/Engineering Deferred
- Multiple asked "just build it" — user vetoed; research first
- Correct posture given research goals

## 10.7 What Could Overturn Our Conclusions

Following Popperian tradition, we identify falsifiable predictions:

1. **If T1 shows GENESIS post-fix >> 75%**: our "scaffolding is 100% of gap" claim is wrong; some architectural value exists
2. **If T-Reasoning-Cap shows accuracy monotonically increases with cap**: H3a wins over H3b; no saturation phenomenon
3. **If bugs are absent in one major framework tested (LangChain/DSPy)**: our "generality" claim needs qualification
4. **If per-domain asymmetry reverses on other benchmarks**: our Physics >> Chemistry claim was GPQA-specific

## 10.8 Honest Assessment

**Confidence high (well-supported):**
- ✅ Pure baseline for gpt-oss-120b on 20q GPQA = 75%
- ✅ Original GENESIS had 5 identifiable bugs
- ✅ Fixes are implemented and tested (35/35 unit tests)
- ✅ Reasoning tokens correlate with correctness (empirical observation, not causation)

**Confidence medium (needs validation):**
- 🟡 GENESIS post-fix accuracy (awaiting T1)
- 🟡 Bug impact estimates (isolated)
- 🟡 Generality of bugs across frameworks

**Confidence low (speculative):**
- 🔴 Reasoning saturation hypothesis (H3b)
- 🔴 Chemistry Organic weakness generalizes to non-GPQA benchmarks
- 🔴 45pt gap represents typical scaffolding scope in field

---

**Section status:** 🟡 Draft. Update after T1/T3.
