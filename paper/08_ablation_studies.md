# §8 Ablation Studies

## Status: 🔴 Pending T3 Experiment (after T1 provides fixed-scaffolding baseline)

## 8.1 Motivation

بعد ما نعرف Whether GENESIS post-fix > baseline (in §7)، نحتاج نفهم **أي component بيضيف قيمة**؟

Currently in GENESIS pipeline:
1. Meta-Agent (essential - writes the code)
2. Cognitive Pipeline (Virtual-GENESIS)
3. Evolutionary Discovery (AlphaEvolve-style)
4. Feedback Agent (verify-revise, Aletheia-style)
5. Constitutional Evaluator

## 8.2 Ablation Design (T3)

### Table 8.1: Planned Ablation Runs (all on 20q)

| Run ID | Meta+Target | Pipeline | Evo Discovery | Feedback | Constitutional | Expected |
|---|---|---|---|---|---|---|
| T3-A (full) | ✅ | ✅ | ✅ | ✅ | ✅ | T1 baseline |
| T3-B (no evo) | ✅ | ✅ | ❌ | ✅ | ✅ | test if evo adds anything |
| T3-C (no feedback) | ✅ | ✅ | ✅ | ❌ (Gen 1 only) | ✅ | test verify-revise value |
| T3-D (no pipeline) | ✅ | ❌ | ✅ | ✅ | ✅ | test cognitive substrate value |
| T3-E (minimal) | ✅ | ❌ | ❌ | ❌ | ❌ | just meta+target ≈ pure baseline? |
| T3-F (pure) | direct | ❌ | ❌ | ❌ | ❌ | actual §5 result |

### Table 8.2 (planned): Ablation Attribution

| Component removed | Δ accuracy | Δ time | Δ cost | Verdict |
|---|---|---|---|---|
| Evolutionary Discovery | ? | ? | ? | ? |
| Feedback Agent | ? | ? | ? | ? |
| Cognitive Pipeline | ? | ? | ? | ? |
| All non-essential | ? | ? | ? | ? |

## 8.3 Reference to AlphaEvolve Ablations

AlphaEvolve paper (§2.1) reported ablations:
- Without evolution: lost 15-30% of improvement
- Without population diversity: lost 5-10%
- Without evaluator strictness: system collapsed

**Our expectation:** similar pattern IF our evolutionary discovery is functional. If ablation shows 0 impact, need to investigate skeleton quality.

## 8.4 Reference to Aletheia Ablations

Aletheia showed:
- Without verification: -25% on IMO problems
- Without revision (just restart): -15%
- Verify + revise combined: full performance

**Our expectation:** feedback agent (our verify-revise) should show measurable benefit IF working properly.

## 8.5 Statistical Power

For 20q ablation runs to detect 10-point differences:
- Requires p<0.05 → need effect size >12pt or larger n
- **Plan:** Repeat each ablation 3× for stable mean

Total T3 compute: 6 setups × 3 reps × 30 min = ~9 hours

---

**Section status:** 🔴 Awaiting T1 completion first, then T3 execution
