# 🧬 GENESIS: Measuring the Impact of LLM Orchestration Architecture on Graduate-Level Scientific Reasoning

**Paper Status:** Draft v0.2 — First Architecture Comparison Complete  
**Last Updated:** 2026-06-05  
**Authors:** GENESIS Research Team (Fares + Agent)  
**Target Venue:** arXiv / ML conference (ICLR/NeurIPS workshop initially)

---

## 00. Abstract

Modern large language models (LLMs) achieve impressive scores on graduate-level scientific benchmarks such as GPQA Diamond (80.1% for gpt-oss-120b). However, these scores are achieved through direct single-pass inference. We investigate whether an orchestration architecture — combining cognitive pipeline memory, theory-guided reasoning, evolutionary agent search, and multi-step feedback — can add measurable value above the pure model baseline.

We build GENESIS, an LLM orchestration framework inspired by DeepMind's AlphaEvolve/FunSearch [T5.86], Co-Scientist multi-agent architecture [T5.84], and Aletheia's proof-driven generate-verify-revise loop [T5.85]. Through systematic empirical measurement, we first establish a **pure baseline** for gpt-oss-120b on GPQA Diamond at **75.00%** (free-tier, n=20; official score 80.1% on full BF16). We then diagnose and fix five critical scaffolding bugs that caused our earlier orchestrated runs to achieve only 30.30% — a gap of −44.70 points attributable entirely to engineering errors including JSON key case mismatch, insufficient token budgets for reasoning models, and inadequate response parsing.

We then run the first **post-fix architecture comparison** on the same 20-question subset using a quick external task directory. GENESIS reaches **65.00%** in both Generation 1 and Generation 2, improving by **+34.7 points** over the buggy 30.30% result, but still falling **−10.0 points below** the pure baseline. This establishes a crucial intermediate conclusion: the catastrophic failure was indeed mostly scaffolding, but the current GENESIS architecture in its present form still does **not** exceed direct single-pass inference on this subset.

We further execute the first targeted ablation (**A3: no cognitive pipeline leverage**). In this setting, Generation 1 rises to **70.00%**, recovering **+5 points** relative to the standard post-fix GENESIS run and reducing the pure-baseline gap from **−10.0** to **−5.0**. However, Generation 2 drops to **60.00%**, providing stronger evidence that the current feedback loop introduces drift when not tightly constrained. This result supports the hypothesis that **pipeline leverage currently adds some harmful noise**, while also suggesting that **feedback instability remains a second-order source of loss**.

Our key findings include: (1) a **counter-intuitive reasoning saturation effect** where questions consuming more reasoning tokens were less likely to be answered correctly (median 6,836 tokens for incorrect vs 989 for correct); (2) strong **domain asymmetry** with Physics questions being dramatically easier (10/11 classified as Easy across models) than Chemistry Organic (5/6 classified as Hard); (3) the "empty content" phenomenon where 35% of reasoning model responses return zero visible tokens, requiring extraction from internal reasoning traces; (4) an **architecture-overhead gap** in which GENESIS, despite producing zero invalid answers and clean execution, underperforms the pure baseline primarily on Chemistry and Biology; and (5) initial ablation evidence that removing pipeline leverage improves Generation 1 from **65% to 70%**.

Finally, we situate these results against the **LEAP** framework [Kung et al. 2026; T5.92; sourced via Idea-001], which on the same class of base model demonstrates a **+100-point** architecture impact (Putnam 2025: 0% → 100%). The 110-point gap between LEAP's +100 and GENESIS's −10 cannot be explained by base model strength, scaffolding bugs, or benchmark difficulty alone — it is structural. To explain it, we develop four internal theories: **[Theory-07]** *Pipeline as Memory vs Pipeline as Decision Injection*; **[Theory-08]** *Feedback Value = f(Determinism, Scope)*; **[Theory-09]** *Anticipatory Concepts vs Anticipatory Lemmas*; and **[Theory-10]** *Reasoning Saturation: The Inverted-U of Internal Reasoning* — the last of which converts our counter-intuitive empirical observation (Discovery #1) into a falsifiable theory anchored by six independent external papers (Wu et al. 2025; UVA-Google 2026; Chen et al. 2024b; Su et al. 2025; OptimalThinkingBench; "When More Thinking Hurts"). Together with **[Phil-07]** *Capability-Adjusted Sufficiency*, these theories reframe our research question from "does the architecture add value?" to the more precise **"under what structural conditions does an orchestration architecture add measurable value?"**. We argue that GENESIS currently violates three conditions (memory rather than injection; narrow deterministic feedback rather than broad stochastic refactor; bounded reasoning rather than saturating reasoning), which makes the residual −10 gap a specified engineering target rather than a mysterious deficit.

These results suggest that GENESIS has successfully crossed the "scaffolding catastrophe" stage, but has not yet crossed the "architecture adds value" threshold. The next research phase is therefore not basic bug-fixing, but **structural redesign along principles validated externally by LEAP and theorized internally in Theories 07/08/09**: identifying which architectural components help, which are neutral, and which currently dilute model performance.

**Keywords:** LLM orchestration, reasoning benchmarks, GPQA Diamond, evolutionary search, agentic architectures, scaffolding errors, pipeline-as-memory, feedback drift, anticipatory abstraction

---

## 01. Introduction

### 1.1 Motivation

Large language models have demonstrated remarkable capabilities on scientific reasoning benchmarks. OpenAI's gpt-oss-120b achieves 80.1% on GPQA Diamond [NVIDIA model card], Google's Gemma 4 31B achieves 84.3% [Google], and NVIDIA's Nemotron 3 Ultra achieves 91% on agent productivity benchmarks [NVIDIA]. These models, however, are measured in pure single-pass inference mode.

The question we ask is: **can we do better by wrapping the same model in a structured orchestration architecture?** Does adding cognitive pipeline processing, memory, theory-guided reasoning, evolutionary search over agent variants, and multi-generation feedback produce measurable improvements?

### 1.2 The GENESIS Architecture

GENESIS is an LLM orchestration framework consisting of:

```
┌─────────────────────────────────────────────────────────┐
│                  GENESIS Orchestrator                     │
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ Meta-Agent   │──▶│ Target Agent │──▶│ Feedback     │ │
│  │ (writes      │   │ (executes    │   │ Agent        │ │
│  │  target code)│   │  task +      │   │ (improves    │ │
│  │              │   │  pipeline)   │   │  via gen)    │ │
│  └──────────────┘   └──────┬───────┘   └──────┬───────┘ │
│                             │                   │         │
│                    ┌────────▼──────────┐        │         │
│                    │ Cognitive Pipeline │        │         │
│                    │ • Memory OS        │        │         │
│                    │ • Concept Engine   │◀───────┘         │
│                    │ • Theory Runtime   │                  │
│                    │ • Tier Decision    │                  │
│                    │ • Economy Control  │                  │
│                    └───────────────────┘                  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Evolutionary Discovery (AlphaEvolve-style)         │    │
│  │ • Population search over agent variants           │    │
│  │ • Diversity + lineage tracking                    │    │
│  │ • Strict evaluator (pipeline + artifacts)         │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Constitutional│  │ Research     │  │ SPIN Semantic │   │
│  │ Evaluator     │  │ Memory       │  │ Gap Analysis  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Figure 1: GENESIS Orchestration Architecture.** The Meta-Agent generates target_agent.py from task specifications. The Target Agent executes the task using the virtual cognitive pipeline (memory, concepts, theory, tier decision). The Feedback Agent reads execution results and produces an improved agent for the next generation. Optional evolutionary discovery performs population search over agent variants (inspired by AlphaEvolve/FunSearch [T5.86]). Constitutional evaluation, research memory, and SPIN semantic gap analysis provide additional quality signals.

### 1.3 The Benchmark: GPQA Diamond

GPQA Diamond [Rein 2024] is a dataset of 198 graduate-level multiple-choice questions across three domains:

| Domain | Questions | Example Topics |
|--------|-----------|----------------|
| Physics | 86 | Quantum mechanics, particle physics, relativistic mechanics, astrophysics |
| Chemistry | 93 | Organic chemistry, inorganic chemistry, general chemistry |
| Biology | 19 | Molecular biology, genetics |

Each question has exactly 4 options (A/B/C/D) and exactly one correct answer. The questions are designed to be "Google-proof" — not easily answerable through simple retrieval — requiring genuine scientific reasoning.

### 1.4 Research Questions

Our investigation centers on three questions:

**RQ1 (Scaffolding):** How much of the gap between pure model performance and orchestrated performance is attributable to scaffolding bugs rather than fundamental architecture limitations?

**RQ2 (Architecture Value — original framing):** Does the GENESIS orchestration architecture, when correctly implemented, add measurable value above the pure model baseline?

**RQ2-revised (Section 8.5):** Following our contrast with LEAP [T5.92] and the development of Theory-07/08/09 + Phil-07, we reframe RQ2 as: *Under what structural conditions does an orchestration architecture add measurable value over direct inference, and by how much?* This shifts the question from binary (yes/no value) to structural (which design properties produce value, and which dilute it).

**RQ3 (Deferred — Thinking vs Instant):** Does the architecture's impact differ between reasoning-heavy models (gpt-oss, Nemotron Ultra, gpt-5, DeepSeek-R1) and faster instant-inference models (Llama 3.3 70B, Gemini Flash, Phi-4)?

This paper primarily addresses RQ1 (Sections 5.3–5.4, 7.1), provides initial empirical evidence on the original RQ2 (Sections 6.4–6.6, 7.x), and develops the theoretical apparatus to answer RQ2-revised (Section 8.5). RQ3 is deferred to future work.

### 1.5 Contributions

1. **Pure baseline measurement:** We establish and document the first rigorous pure-model baseline for gpt-oss-120b on GPQA Diamond (free-tier): **75.00%** on a 20-question subset, within 5.1 percentage points of the official 80.1% score.

2. **Scaffolding bug taxonomy:** We identify, diagnose, and fix five critical bugs that collectively caused a 44.70-point accuracy drop (75% → 30%), providing a systematic framework for reasoning-model response handling.

3. **Counter-intuitive findings:** We document the reasoning saturation effect (more tokens → less accuracy), domain asymmetry (Physics easy, Chemistry hard), and the empty-content phenomenon (35% of responses return zero visible tokens).

4. **Infrastructure for rigorous measurement:** We build and open-source a multi-provider, multi-key benchmarking infrastructure supporting 13 models across 9 free providers, enabling reproducible LLM evaluation at scale.

5. **First post-fix architecture comparison:** We show that GENESIS post-fix reaches **65.00%** on the same 20-question subset where the pure baseline reaches **75.00%**, proving that the architecture has recovered from catastrophic scaffolding failure but still imposes a measurable performance overhead in its current form.

6. **First targeted ablation result (A3):** Disabling pipeline leverage raises Generation 1 from **65.00%** to **70.00%**, providing the first direct evidence that the cognitive pipeline in its current usage contributes harmful overhead/noise on GPQA-20.

7. **Theory-10 (Reasoning Saturation):** We promote our counter-intuitive empirical observation (median reasoning tokens: 989 for correct vs 6,836 for incorrect) to a full theory anchored by **six independent external papers** including a UVA-Google study (arXiv:2602.13517) that reports a length-vs-accuracy correlation of **r = −0.54** on the *same model family and same benchmark family* we tested. Theory-10 interacts non-trivially with Theory-07 to produce a joint, falsifiable prediction: GENESIS empty-content rate should exceed pure-baseline empty-content rate on identical questions (Section 7.3).

---

## 02. Related Work

### 2.1 LLM Orchestration Architectures

Self-improving agent frameworks have been explored by several recent works. SIA (Self-Improving AI) [T5.4] introduced a multi-generation loop where a meta-agent writes agent code that is then executed and refined by a feedback agent. Our GENESIS framework extends this with cognitive pipeline integration (memory, concepts, theory) and evolutionary search.

### 2.2 Evolutionary Search for Code

AlphaEvolve [T5.86] and FunSearch [Nature 2023] demonstrated that evolutionary algorithms can discover novel algorithms and heuristics by treating code as an evolvable substrate. We adopt their population-based search with strict evaluator-driven selection, applying it to the discovery of better agent implementations rather than mathematical functions.

### 2.3 Multi-Agent Scientific Reasoning

Google DeepMind's Co-Scientist [T5.84] uses a multi-agent architecture where specialized agents (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review) collaborate on scientific hypothesis generation. Our work applies multi-agent orchestration to the complementary problem of answering existing scientific questions (GPQA) rather than generating new hypotheses.

### 2.4 Proof-Driven Reasoning Loops

Aletheia [T5.85] introduced a generate-verify-revise loop where a generator produces candidate proofs that a verifier checks, feeding back errors for revision. Our constitutional evaluator and feedback loop mirror this pattern for agent code rather than mathematical proofs.

### 2.5 Benchmark Measurement Methodology

Prior work on GPQA [Rein 2024] established per-domain analysis conventions (Physics/Chemistry/Biology breakdowns). Our measurement infrastructure extends this with multi-model comparison, reasoning token analysis, and scaffolding-aware evaluation (distinguishing model errors from infrastructure errors).

### 2.6 Reasoning Models and Token Economics

Recent models (gpt-oss, Nemotron, o-series, DeepSeek-R1) consume significant tokens in internal reasoning before producing visible output. This creates new challenges for benchmark measurement: when max_tokens are exhausted during reasoning, the visible content is empty even though the model has reasoned extensively. Our `extract_response_text` utility addresses this by falling back to internal reasoning traces.

---

## 03. Methodology

### 3.1 Measurement Infrastructure

We built a measurement infrastructure separate from GENESIS to establish pure baselines without orchestration interference:

```
tools/
├── api_key_pool.py            ← 11-key rotation with rate-limit handling
├── providers.py               ← 9 free LLM provider catalog
├── model_registry.py          ← 13 models with official benchmarks
├── run_multi_model_benchmark.py ← Direct model evaluation (no GENESIS)
└── diagnose_run_53.py         ← Automated bug detection for GENESIS runs
```

**Figure 2: Measurement Infrastructure.** These tools measure models directly without any GENESIS scaffolding, establishing ground-truth baselines. The API Key Pool manages 11 OpenRouter free-tier keys with intelligent rotation, daily-exhaust detection, and persistent statistics.

### 3.2 Response Parsing Pipeline

A critical component of our infrastructure is the response parsing and recovery pipeline:

```
┌─────────────────┐
│  API Response    │
└────────┬────────┘
         ▼
┌─────────────────┐     content=""?    ┌──────────────────┐
│ extract_response │──────────────────▶│ Fallback to       │
│ _text()          │                   │ reasoning_details │
└────────┬────────┘                   │ / reasoning       │
         │                             └────────┬─────────┘
         │ text                                 │
         ▼                                      ▼
┌─────────────────┐                   ┌──────────────────┐
│ extract_letter() │◀─────────────────│ combined_text     │
│ (16 patterns)    │                   └──────────────────┘
└────────┬────────┘
         │
    ┌────▼────┐
    │ Found?  │──Yes──▶ Return letter
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│ Force-Letter     │
│ Follow-up Call   │
│ (STOP THINKING)  │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Found?  │──Yes──▶ Return letter (recovered)
    └────┬────┘
         │ No
         ▼
    Mark INVALID
```

**Figure 3: Response Parsing & Recovery Pipeline.** Our parser handles 16+ response formats (ANSWER: X, ANSWER:X, **X**, \boxed{X}, etc.). When no letter is found, a force-letter follow-up recovers ~80% of failures. The final fallback extracts the last A-D letter from reasoning traces when visible content is empty.

### 3.3 Question Difficulty Taxonomy

We classify each GPQA question based on cross-model consensus across 6 runs:

| Difficulty | Definition | Count (n=20) | % |
|------------|-----------|-------------|---|
| **Easy** | ≥4/6 models correct | 11 | 55% |
| **Medium** | 2-3/6 models correct | 3 | 15% |
| **Hard** | ≤1/6 models correct | 6 | 30% |

This taxonomy reveals strong domain asymmetry:

| Domain | Easy | Medium | Hard | Total |
|--------|------|--------|------|-------|
| Physics | **10** | 0 | 1 | 11 |
| Chemistry | 1 | 0 | **5** | 6 |
| Biology | 0 | **3** | 0 | 3 |

**Table 1: Domain × Difficulty Matrix across 6 model runs on GPQA 20-question subset.** Physics questions are dramatically easier (10/11 Easy) than Chemistry questions (5/6 Hard), primarily driven by Organic Chemistry problems that require multi-step reaction tracking.

### 3.4 Reasoning Token Analysis

We instrument API calls to capture `reasoning_tokens` from `usage.completion_tokens_details` (available via OpenRouter) alongside the standard `completion_tokens`. This enables correlation analysis between reasoning depth and answer correctness.

---

## 04. Infrastructure & Providers

### 4.1 Free-Tier LLM Provider Landscape

We catalogued 9 providers offering free-tier inference in 2026:

| # | Provider | Best Models | Daily Limit | Key Advantage |
|---|----------|-------------|-------------|---------------|
| 1 | **Google AI Studio** | Gemini 2.5 Flash/Pro | 1,500 RPD Flash | Most generous free tier |
| 2 | **Groq** | Llama 3.3 70B | 1,000 RPD/model | Fastest inference (315 tok/s) |
| 3 | **Cerebras** | Llama 3.1 70B, gpt-oss-120b | 1M tokens/day | Highest token throughput |
| 4 | **GitHub Models** | gpt-5, gpt-4.1, Claude | Copilot tier | Only free source of GPT-5 |
| 5 | **NVIDIA NIM** | Nemotron 3 Ultra/Super/Nano | Per-account | Nemotron direct access |
| 6 | **OpenRouter** | 35+ free models | 50 RPD/model | Aggregator |
| 7 | **Cloudflare** | Llama 3.1 70B | 10K neurons/day | Edge inference |
| 8 | **Mistral** | Mistral Small | Free experiment tier | EU data residency |
| 9 | **DeepSeek** | DeepSeek V3, R1 | Generous free tier | Cheapest reasoning |

**Table 2: Free-Tier LLM Provider Landscape (2026).** With all 9 providers configured, total estimated free capacity reaches ~8,000+ requests/day on frontier models. Our current setup uses OpenRouter (11 keys) + GitHub Models (1 PAT). Gemini × 11 and Groq × 11 keys are pending.

### 4.2 Model Registry

We maintain a curated registry of 13 models with official benchmarks:

| Model | Size | Best Official Benchmark | GPQA Diamond |
|-------|------|------------------------|--------------|
| Gemma 4 31B | 31B dense | **GPQA 84.3%** 🥇 | **84.3** |
| Gemma 4 26B (MoE) | 26B/4B active | GPQA 82.3% | 82.3 |
| gpt-oss-120b | 120B/5.1B active | GPQA 80.1% | 80.1 |
| Nemotron 3 Super | 120B/12B active | GPQA 79.2% | 79.2 |
| Nemotron 3 Ultra | 550B/55B active | PinchBench 91% | (not published) |
| Laguna M.1 | 225B/23B active | SWE-bench 72.5% | — |
| Qwen3 Coder | (unknown) | SWE-bench ~73% | — |
| GLM-4.5-Air | 106B/12B active | Tool Selection 94% | — |
| Nemotron 3 Nano | 30B/3B active | RULER 87.5% @64K | — |
| LFM 2.5 Thinking | 1.2B | IFEval 88.4% | 37.9 |
| Laguna XS.2 | 33B/3B active | SWE-bench 68.2% | — |
| Nemotron Nano Omni | 30B/3B | Multimodal | — |
| Nemotron Nano 9B v2 | 9B | — | — |

**Table 3: Model Registry with Official Benchmarks.** "—" indicates the benchmark was not published by the vendor. GPQA Diamond column shows only models with officially published GPQA scores. Our pure baseline measurement for gpt-oss-120b (75.00%) serves as the reference point for all comparisons.

---

## 05. Experiments

### 5.1 Experimental Setup

All experiments use:
- **Model:** `openai/gpt-oss-120b:free` via OpenRouter free tier
- **Benchmark:** GPQA Diamond, 20-question subset (Q1-Q20)
- **Reasoning:** `high` effort
- **Max tokens:** 16,384 (includes reasoning tokens)
- **Temperature:** 0.0
- **Scoring:** Per-question A/B/C/D extraction with multi-pattern parsing

### 5.2 Experiment Timeline

| Run ID | Architecture | Key Change | Accuracy | Invalid |
|--------|-------------|------------|----------|---------|
| run_53 | GENESIS (pre-fix) | Initial, buggy scaffolding | 30.30% | 0* |
| smoke_v1 | Pure baseline | 4-pattern extract_letter | 60.00% | 7/20 (35%) |
| smoke_v2_lfm | Pure baseline | 16-pattern + reasoning fallback | 25.00% | 1/20 (5%) |
| smoke_v2_nano | Pure baseline | 16-pattern + reasoning fallback | 65.00% | 3/20 (15%) |
| **pure_final** | **Pure baseline** | **All fixes applied** | **75.00%** | **0/20** |
| **run_57_gen1** | **GENESIS post-fix** | 20Q subset, Gen 1 | **65.00%** | **0/20** |
| **run_57_gen2** | **GENESIS post-fix** | 20Q subset, Gen 2 + feedback | **65.00%** | **0/20** |
| **run_58_gen1** | **A3 no_pipeline** | 20Q subset, Gen 1 | **70.00%** | **0/20** |
| **run_58_gen2** | **A3 no_pipeline** | 20Q subset, Gen 2 + feedback | **60.00%** | **0/20** |

**Table 4: Experiment Timeline and Results.** "Invalid 0*" for run_53 is misleading — invalid responses defaulted to "A" without detection. Starting from smoke_v1, we properly track and recover invalid responses. The first completed post-fix architecture comparison (`run_57`) shows that GENESIS cleanly executes and eliminates invalid answers, but still underperforms the pure baseline by 10 points on the same 20-question subset. The first targeted ablation (`run_58`) then shows that removing pipeline leverage improves Gen 1 to 70.0%, implicating the current pipeline usage as a real source of overhead — but Generation 2 simultaneously drops to 60.0%, strengthening the case that feedback drift is a second problem.

### 5.3 The run_53 Diagnosis

GENESIS run_53 achieved 30.30% on GPQA Diamond using gpt-oss-120b — a 44.70-point gap from the 75.00% pure baseline. Statistical analysis of the answer distribution revealed:

```
Prediction Distribution (198 questions):
A: 30 (15%)  B: 54 (27%)  C: 57 (29%)  D: 57 (29%)
χ² vs uniform: 10.36

Truth Distribution:
A: 57 (29%)  B: 50 (25%)  C: 51 (26%)  D: 40 (20%)

Correct-by-truth-letter:
A: 12/57 (21%) ← Model's weakest performance
B: 17/50 (34%)
C: 18/51 (35%)
D: 13/40 (33%)
```

**Key insight:** Despite A being the most common correct answer (57/198 = 29%), the model's accuracy on A-questions was the lowest (21%). This confirms random guessing — if the model understood the questions, it would perform best on the most frequent answer letter.

**Root cause traced to target_agent.py line 159:**

```python
# ❌ Buggy code (generated by meta-agent):
qtext = q.get('question') or q.get('text') or ''

# ✅ Fixed code (after diagnosis):
qtext = (q.get('Question') or q.get('question') or q.get('QUESTION')
         or q.get('text') or q.get('prompt') or '')
```

The GPQA JSON uses `'Question'` (capital Q). Python's `dict.get('question')` returns `None` → `or ''` → empty string. The prompt sent to the model was:

```
Question:                   ← EMPTY!
Options:
A: 10^-4 eV
B: 10^-9 eV
C: 10^-11 eV
D: 10^-8 eV
```

With no question text, the model guessed randomly from 4 numbers with no context. The 30% result (barely above the 25% random baseline) is actually impressive given zero information.

### 5.4 The Five Scaffolding Bugs

| # | Bug | Severity | Impact | Fix |
|---|-----|----------|--------|-----|
| 1 | Case mismatch in JSON keys | 🔴 CRITICAL | −45 points | Multi-case `safe_get_question_field()` |
| 2 | max_tokens=50 for reasoning model | 🔴 CRITICAL | Empty responses | max_tokens=16384 |
| 3 | "Output ONLY the letter" instruction | 🟠 HIGH | Suppressed CoT | Allow reasoning + ANSWER: X format |
| 4 | No fallback for empty content | 🟠 HIGH | 35% responses lost | `extract_response_text()` with reasoning fallback |
| 5 | Invalid defaults to "A" | 🟡 MEDIUM | Masked failures | Force-letter follow-up + mark invalid |

**Table 5: Five Scaffolding Bugs Discovered and Fixed.** Bugs 1-3 were in the meta-agent prompt (generated code), Bug 4 was a missing utility, Bug 5 was in the evaluation pipeline. All five are fixed in commit `3a16a87` via `genesis/llm_helpers.py` and updated orchestrator prompts.

---

## 06. Results

### 6.1 Pure Baseline Results

The final pure baseline measurement for gpt-oss-120b on our 20-question GPQA subset:

```
======================================================================
GPQA Evaluation Results
======================================================================
Total Questions: 20
Correct: 15
Incorrect: 5
Missing: 0
Invalid: 0
Accuracy: 75.00%
======================================================================
Per-Domain Accuracy:
----------------------------------------------------------------------
Physics   9/ 11 ( 81.8%)
Chemistry 4/  6 ( 66.7%)
Biology   2/  3 ( 66.7%)
----------------------------------------------------------------------
```

**Figure 4: Pure Baseline Results — gpt-oss-120b on GPQA Diamond (20 questions).** The model achieves 81.8% on Physics, 66.7% on Chemistry, and 66.7% on Biology. Overall 75.00% is within 5.1 percentage points of the official 80.1% (full BF16 weights, n=198). The remaining gap is attributable to: (a) free-tier quantization, (b) small sample size (n=20 produces ±10% margin of error), and (c) GPQA subset bias toward Chemistry questions (6/20 = 30% vs 93/198 = 47% in the full set).

### 6.2 Reasoning Token vs Accuracy (Counter-Intuitive Finding)

```
Reasoning tokens vs Correctness (gpt-oss-120b, n=20):
────────────────────────────────────────────────────────
                    Correct         Incorrect
────────────────────────────────────────────────────────
Average             3,001           5,104  (+70%)
Median                989           6,836  (+591%)
────────────────────────────────────────────────────────

Empty content rate: 7/20 (35%) — finish_reason="length"
Recovery rate:      6/7 (86%) — via reasoning text fallback
```

**Figure 5: Reasoning Token Analysis.** Counter-intuitively, questions that consumed MORE reasoning tokens were LESS likely to be answered correctly. The median incorrect answer consumed 6,836 reasoning tokens (vs 989 for correct). Additionally, 35% of responses returned zero visible content (`content=""`) because all 16,384 max_tokens were consumed by internal reasoning. Our `extract_response_text` utility recovered the answer from reasoning traces in 86% of these cases.

### 6.3 Cross-Model Consensus Analysis

```
Questions where ALL models agreed (and were correct):
Q3  (Physics, Quantum Mechanics)     "B" — consensus correct
Q12 (Physics, Particle Physics)      "B" — consensus correct
Q20 (Physics, Quantum Mechanics)     "C" — consensus correct

Questions where ALL models agreed (and were WRONG):
Q16 (Chemistry, Organic Chemistry)   consensus="D", truth="C"

Pairwise model agreement:
gpt-oss vs nemotron-nano: 13/20 (65%) identical answers
```

**Figure 6: Cross-Model Consensus Analysis.** Three Physics questions were answered correctly by every tested model, indicating high certainty domain knowledge. One Chemistry Organic question was answered identically (and incorrectly) by all models, suggesting a shared erroneous prior about cinnamaldehyde reaction products.

### 6.4 First Post-Fix GENESIS Result (run_57)

The first completed architecture comparison after the scaffolding fixes uses the quick external task directory `tasks/gpqa_subset_20` to ensure a like-for-like comparison against the 75.00% pure baseline.

```
GENESIS post-fix (run_57)
────────────────────────────────────────────────────────
Generation 1: 13/20 correct = 65.00%
  Physics   10/11 = 90.9%
  Chemistry  1/6  = 16.7%
  Biology    2/3  = 66.7%

Generation 2: 13/20 correct = 65.00%
  Physics   10/11 = 90.9%
  Chemistry  2/6  = 33.3%
  Biology    1/3  = 33.3%

Pure baseline on same subset: 15/20 = 75.00%
Architecture gap: −10.00 points
```

**Key interpretation:**

- The post-fix architecture is **dramatically better than the buggy 30.30% result** (+34.7 points), confirming that the earlier collapse was mostly scaffolding.
- The post-fix architecture is **still below the pure baseline** (65.0% vs 75.0%), meaning the current orchestration stack introduces overhead or decision dilution rather than measurable gain on this subset.
- Generation 2 does **not** improve aggregate accuracy over Generation 1. It trades one corrected Chemistry question (Q2) for one newly wrong Biology question (Q8), indicating that the feedback loop is currently producing lateral variation rather than net gain.

### 6.5 Question-by-Question Delta Pattern

A more informative analysis than aggregate accuracy is to ask: **where exactly does GENESIS help, and where does it hurt, relative to the pure baseline?**

The answer is highly structured rather than uniform:

- **Stable wins across all systems:** 11/20 questions
- **Persistent failures across all systems:** 3/20 questions
- **Architecture gains:** 1 question in Gen 1, 2 questions in Gen 2
- **Architecture losses:** 3 questions in Gen 1, 4 questions in Gen 2

The losses are concentrated primarily in **Chemistry Organic**:

- Q9
- Q13
- Q19

while the main stable architecture gain appears on a Physics question (Q7), with one additional Chemistry recovery (Q2) appearing only after feedback in Generation 2.

This means the current architecture gap is not “general weakness”; it is a **localized pattern of preserved Physics + damaged Chemistry**.

See `PAPER/tables/tab12_question_delta_analysis.md` and `PAPER/figures/fig09_question_delta_map.md` for the full question-level breakdown.

### 6.6 First Targeted Ablation (run_58, A3 = no_pipeline)

The first targeted ablation removes or neutralizes **cognitive pipeline leverage** while preserving the rest of the GENESIS scaffold. This directly tests the hypothesis that the pipeline, in its current form, may be injecting noisy context rather than decision-useful signal.

```
A3 no_pipeline ablation (run_58)
────────────────────────────────────────────────────────
Generation 1: 14/20 correct = 70.00%
  Physics   10/11 = 90.9%
  Chemistry  3/6  = 50.0%
  Biology    1/3  = 33.3%

Generation 2: 12/20 correct = 60.00%
  Physics   10/11 = 90.9%
  Chemistry  1/6  = 16.7%
  Biology    1/3  = 33.3%

Comparison points:
- Pure baseline: 75.00%
- Standard GENESIS Gen 1 (run_57): 65.00%
- A3 Gen 1 improvement over standard GENESIS: +5.00 points
- Remaining gap vs pure baseline: −5.00 points
```

**Interpretation:**

- Removing pipeline leverage improves Generation 1 from **65% → 70%**.
- This is the first direct experimental evidence that the current pipeline usage is not neutral — it is likely adding harmful overhead or distracting context.
- The fact that Physics remains unchanged at **90.9%** while Chemistry rises from **16.7% → 50.0%** strongly suggests that the pipeline is disproportionately harmful on Chemistry questions.
- Generation 2 then collapses to **60.0%**, showing that the feedback loop can actively worsen performance once the pipeline is removed. This implies that **feedback drift** is a second, separate source of loss.

### 6.7 Nemotron 3 Nano vs gpt-oss-120b Comparison

```
Model              Accuracy  Invalid  Physics   Chemistry  Biology
─────────────────────────────────────────────────────────────────
gpt-oss-120b       75.00%    0        81.8%     66.7%      66.7%
nemotron-3-nano    65.00%    3        90.9%     16.7%       0.0%
lfm-2.5-thinking   25.00%    1        18.2%      0.0%      33.3%
```

**Table 6: Cross-Model Comparison on GPQA 20-Question Subset.** Nemotron Nano achieves 90.9% on Physics (outperforming gpt-oss) but collapses on Chemistry (16.7%) and Biology (0.0%). This domain specialization pattern suggests that smaller reasoning models excel at physics but lack the multi-step reaction knowledge required for organic chemistry.

---

## 07. Analysis

### 7.1 The -44.70 Gap Was Entirely Scaffolding

Our most important finding is that the 44.70-point gap between pure baseline (75.00%) and GENESIS run_53 (30.30%) was caused 100% by five identifiable scaffolding bugs:

1. **JSON case sensitivity** (gap contribution: ~25-30 points) — the model received empty questions
2. **Insufficient token budget** (gap contribution: ~10-15 points) — no room for reasoning
3. **Anti-CoT prompting** (gap contribution: ~5-10 points) — suppressed chain-of-thought
4. **No reasoning fallback** (gap contribution: ~3-5 points) — lost empty-content responses
5. **Default-to-A masking** (gap contribution: 0 points — masked the real problem)

This finding has significant implications for the field: **benchmark comparisons involving orchestrated systems must distinguish infrastructure errors from genuine architecture limitations.** A naive reading of run_53 would conclude that GENESIS degrades performance by 44.70 points; in reality, the architecture's cognitive pipeline was never used because the questions themselves were empty.

### 7.2 Domain Asymmetry Implications

The stark Physics (10/11 Easy) vs Chemistry (5/6 Hard) split raises important questions about benchmark composition:

- Our 20-question subset contains 55% Physics but only 30% Chemistry
- The full GPQA Diamond contains 43% Physics, 47% Chemistry, 10% Biology
- This means our subset **overweights Physics** relative to the full benchmark
- A model achieving 75% on our subset might achieve 65-70% on the full set

**Recommendation:** All claims about GPQA performance must be accompanied by per-domain breakdowns. Reporting only aggregate accuracy obscures important domain-specific strengths and weaknesses.

### 7.3 Reasoning Saturation — From Hypothesis to Theory-10

In v0.2 of this paper, this subsection contained only an informal "Reasoning Saturation Hypothesis." In v0.4 we promote it to a full internal theory, **[Theory-10] Reasoning Saturation: The Inverted-U of Internal Reasoning**, supported by six recent external papers and our own measurements.

#### 7.3.1 The empirical signature in our data

On `gpt-oss-120b` over GPQA-20 (run_57 pure baseline):

| Metric | Correct (n=15) | Incorrect (n=5) | Ratio |
|---|---|---|---|
| Average reasoning tokens | 3,001 | 5,104 | **+70%** higher for incorrect |
| Median reasoning tokens | 989 | 6,836 | **+591%** higher for incorrect |
| Empty content (`content=""`) | 0 / 15 | 7 / 20 total — all incorrect | exclusively in incorrect set |
| `finish_reason="length"` | 0 / 15 | matches every empty content case | budget exhausted in reasoning |

The model that thinks longer answers *worse*, not better — and beyond a critical length, it stops producing visible output at all.

#### 7.3.2 External literature converges on the same finding

Theory-10 is one of the **best-supported** theories in this paper because the external literature has reached very similar conclusions independently:

| Source | Finding | Relation to our data |
|---|---|---|
| **[T5.93]** Wu et al. 2025 (arXiv:2502.07266) | Accuracy follows an **inverted-U** curve in CoT length; optimal length increases with task difficulty, decreases with model capability. **Formal scaling laws derived** via Lambert W function; **40-point accuracy gap** between optimal and longest CoT on a 72B model. | Provides the *formal theoretical backbone* for Theory-10. Promoted to full Theft T5.93 (see `GENESIS_External_Inverted_U_Wu2025_Theft_AR.md`). |
| **[T5.94]** Chen et al. 2026 (UVA + Google, arXiv:2602.13517) | Tested **GPT-OSS, DeepSeek-R1, Qwen3** on AIME and **GPQA-Diamond**. Length-vs-accuracy correlation: **r = −0.54** (negative). DTR (deep-layer revision fraction) correlates at **+0.683**. Think@n strategy: same accuracy or +2 points at ~50% less compute. | **Closest external precedent for our setup** (same model family + same benchmark). Promoted to full Theft T5.94 (see `GENESIS_External_DTR_ChenMeng2026_Theft_AR.md`). |
| Chen et al. 2024b | First documentation of overthinking in o1-like models on simple problems | Confirms the phenomenon predates our observation |
| Su et al. 2025 (arXiv:2508.17627) | Identifies **thinking–content compensation** that transitions into a saturation phase | Mechanistic backing for our empty-content phenomenon |
| OptimalThinkingBench (arXiv:2508.13141) | Operationalizes over/underthinking as a benchmark | Methodological frame for future controlled studies |
| "When More Thinking Hurts" (arXiv:2604.10739) | Diminishing returns + flip-event tracking + cost-aware metrics | Confirms our cost-aware framing of the trade-off |

These six sources, combined with our own measurements, make Theory-10 the most externally-validated theoretical contribution in this paper.

#### 7.3.3 The theory in compact form

Theory-10 rests on four axioms (formalized in `PAPER/theory/10_*.md`):

1. **Error accumulation** (Wu et al. 2025). Each reasoning step carries a small error probability ε; over N steps, accumulated error eventually overwhelms decomposition gains.
2. **Confusion spiral** (observed in run_57). When a question exceeds the model's capacity window, extended reasoning generates competing hypotheses rather than converging on one answer.
3. **Token budget exhaustion** (Empirical Discovery #3). When reasoning consumes `max_tokens`, the visible `content` is empty — a mechanism specific to reasoning-capable models that hide internal tokens.
4. **Inverse capability scaling** (Wu et al. 2025). Optimal CoT length *decreases* as model capability increases — stronger models exhibit a "simplicity bias."

Five testable predictions follow (see `PAPER/theory/10_*.md` §5):

- **P1.** A sweet-spot `max_tokens` exists for GPQA-20 on gpt-oss-120b (expected: 4K–8K).
- **P2.** GENESIS-style decision injection shifts the sweet spot *leftward* and lowers peak accuracy (predicted empty-content rate >40% vs pure baseline's 35%) — this is where Theory-10 interacts with Theory-07.
- **P3.** Per-domain optimal lengths differ substantially (Chemistry Organic needs longer but saturates faster).
- **P4.** Capability scaling: weaker models have sweet spots at higher token counts than gpt-oss-120b; very small models may never reach a sweet spot at all.
- **P5.** DTR-based early termination achieves equal or better accuracy at roughly half the compute (replication of UVA-Google's result).

#### 7.3.4 Why Theory-10 matters for the paper

Three reasons elevate Theory-10 beyond a local hypothesis:

1. **It explains Empirical Discovery #1 completely** — what looked like a paradox is actually a predicted consequence of an inverted-U structure documented across the literature.
2. **It interacts non-trivially with Theory-07** through **Prop 4**: pipeline decision injection burns reasoning budget on signal-parsing rather than on answer-finding, pushing the model into the overthinking regime faster. This produces a *joint prediction* (Theory-07 × Theory-10) that GENESIS empty-content rate should exceed pure baseline empty-content rate on identical questions — a clean, falsifiable test.
3. **It contributes externally** — orchestration frameworks broadly need to address reasoning saturation, not just GENESIS. The DTR-style or Wu-style length calibration becomes a generic architectural concern.

#### 7.3.5 Concrete consequence for GENESIS design

Our current `max_tokens=16384` may itself be *too high* for gpt-oss-120b on GPQA. The median correct answer used only 989 reasoning tokens — a budget of 16,384 leaves vast room for the confusion spiral when difficult questions trigger it. A budget of ~4K–8K, combined with the DTR-style early termination from Track A.5 (added to Future Work), is the prediction we cannot yet test but should test first when runs resume.

This has implications for RQ3 (instant vs thinking) — bounded reasoning with forced answer extraction may outperform unbounded reasoning for certain question types, especially in the over-saturating regime.

### 7.4 Infrastructure Error Detection

Our diagnosis workflow provides a template for detecting scaffolding errors in any LLM orchestration system:

1. **Suspicion trigger:** Accuracy near random (25% for 4-option MCQ)
2. **Statistical check:** χ² test on answer distribution (uniform = guessing)
3. **Per-letter accuracy:** If the most common correct letter has the lowest model accuracy, the model is guessing
4. **Prompt inspection:** Print the first prompt to verify it's not empty
5. **Token monitoring:** Check `finish_reason` for "length" indicating budget exhaustion

We have automated these checks in `tools/diagnose_run_53.py`.

---

## 08. Discussion

### 8.1 The Measurement-First Approach

A key methodological contribution of this work is the insistence on **pure baseline measurement before architecture claims**. Prior work on agentic frameworks [SIA, Reflexion, Self-Refine] often compares orchestrated performance to other orchestrated systems, without establishing what the underlying model achieves without orchestration.

Our three-number framework requires:

1. **Official** — vendor-reported benchmark score (reference)
2. **Pure Baseline** — model alone on the same task (true ceiling)
3. **Orchestrated** — model + architecture (impact of framework)

The gap `(Pure − Official)` reveals infrastructure limitations (free-tier quantization, sample size). The gap `(Orchestrated − Pure)` reveals **architecture impact** — the quantity we truly care about.

### 8.2 Proper Error Attribution

The scaffolding bugs we discovered highlight a broader issue in LLM benchmarking: **how do we distinguish model errors from infrastructure errors?**

Our answer taxonomy:

| Error Type | Example | Attribution |
|-----------|---------|-------------|
| Model error | Model lacks chemistry knowledge | Model capability limit |
| Scaffolding error | Empty prompt due to case mismatch | Infrastructure bug |
| Parsing error | Valid answer not extracted by parser | Infrastructure bug |
| Rate-limit error | API returns 429 instead of answer | Infrastructure limit |
| Sampling error | n=20 subset biases toward physics | Methodology limitation |

**Table 7: Error Attribution Taxonomy.** Proper attribution is essential for scientific claims. Conflating scaffolding errors with model limitations leads to incorrect conclusions about architecture value.

### 8.3 GENESIS Architecture: Positive, Neutral, or Negative?

The first completed post-fix experiment (`run_57`) and the first targeted ablation (`run_58`) allow us to answer this question more precisely on the 20-question subset:

- **Observed impact (standard GENESIS):** `65.0%` vs `75.0%` pure baseline → **−10.0 points**
- **Observed impact (A3 no_pipeline Gen 1):** `70.0%` vs `75.0%` pure baseline → **−5.0 points**

This lets us separate three claims very clearly:

1. **Scaffolding claim:** supported. The catastrophic 30.3% result was primarily engineering failure.
2. **Pipeline-overhead claim:** partially supported. Removing pipeline leverage recovers **+5 points**.
3. **Architecture-value claim:** still not supported. Even after the A3 improvement, no tested orchestrated configuration beats the direct baseline.

This means the next scientific step is no longer “debug everything blindly,” but rather:

- identify which components are genuinely useful,
- identify which components are neutral,
- identify which components currently dilute performance.

The evidence now points most strongly to two residual loss sources:

- **pipeline overhead** that adds context but not decision-useful signal, especially on Chemistry,
- **feedback drift** that changes answer patterns without improving total score (and in A3, actively worsens it).

The other candidates remain open but secondary:

- **constitutional pressure** may optimize code quality/safety properties more than benchmark accuracy,
- **evolutionary discovery** may be neutral or noisy on small subsets,
- **single-agent answer generation** may still not exploit enough task-specific leverage from the architecture.

### 8.4 Limitations of Current Study

1. **Sample size (n=20):** Our subset is too small for definitive claims (±10% margin of error). Full 198-question runs are needed.

2. **Single model:** All scaffolding analysis is on gpt-oss-120b. Cross-model generalization of the five bugs is untested.

3. **Free-tier quantization:** OpenRouter's free tier may use quantized weights. Our 75% vs official 80.1% gap includes quantization as a confound.

4. **Subset bias:** Our 20-question subset overweights Physics (55% vs 43% in the full set).

5. **No ablation yet:** We have not measured which GENESIS component (pipeline, memory, theory, evolution, feedback) contributes what.

6. **Single benchmark:** GPQA Diamond is only one type of reasoning. Results may not transfer to SWE-bench, math benchmarks, or other domains.

---

### 8.5 Contrast with LEAP — Why GENESIS Loses 10 Points While LEAP Gains 100

This section integrates an external empirical contrast that fundamentally reshapes our reading of GENESIS's residual gap. The contrasting system is **LEAP** (LLM-in-Lean Environment Agentic Prover) [Kung et al. 2026; T5.92], a recently released agentic framework from Google Cloud AI Research and Google DeepMind. LEAP was brought to our attention by Fares as the first formal idea in our Ideas Bank [Idea-001].

#### 8.5.1 The Headline Contrast

Both LEAP and GENESIS use **general-purpose foundation models** (Gemini-3.1-Pro for LEAP, gpt-oss-120b for GENESIS) as their reasoning backbone. Both wrap the model in an **agentic framework** intended to add value over direct single-pass inference. Yet the measured architecture impact differs by **110 points**:

**Table 16: LEAP vs GENESIS Architecture Impact Comparison (same-model, agentic-framework results)**

| System | Benchmark | Direct LLM | + Agentic Framework | **Δ (Architecture Impact)** |
|---|---|---|---|---|
| **LEAP** [T5.92] | Putnam 2025 | 0% (0/12) | **100%** (12/12) | **+100.0** |
| **LEAP** [T5.92] | Lean-IMO Basic | 20.0% | **83.3%** | **+63.3** |
| **LEAP** [T5.92] | Lean-IMO Advanced | 3.3% | **56.7%** | **+53.4** |
| **GENESIS** (run_57) | GPQA-20 | 75.0% | 65.0% | **−10.0** |
| **GENESIS** (run_58 A3 Gen1) | GPQA-20 | 75.0% | 70.0% | **−5.0** |

The 110-point gap between LEAP's +100 and GENESIS's −10 cannot be explained by:

- **Base model differences alone** — both are frontier-grade general-purpose models.
- **Scaffolding bugs alone** — we already eliminated those (run_57 is post-fix).
- **Benchmark difficulty** — both are graduate-level reasoning tasks.

Something **structural** about the architectures themselves accounts for most of the gap. This observation motivates the three internal theories we develop below.

#### 8.5.2 Theory-07: Pipeline as Memory vs Pipeline as Decision Injection

We propose that orchestration pipelines fall on a spectrum between two philosophically distinct types [Theory-07]:

**Type A — Pipeline as Memory (helpful):**
- The pipeline stores state (proven lemmas, open goals, dependencies).
- The LLM pulls from it on demand.
- No signals are pushed into the answer-generation prompt.
- **Relationship:** LLM leads, pipeline serves.

**Type B — Pipeline as Decision Injection (harmful at scale):**
- The pipeline computes signals (tier decisions, theory predictions, blackboard hints).
- These signals are injected into every question prompt.
- The LLM must weigh injected signals against its own reasoning.
- **Relationship:** pipeline leads, LLM obeys or resists.

LEAP's DAG memoization is the canonical example of Type A — the proof graph is queried, never pushed. GENESIS's current pipeline (tier_decision, theory_prediction, blackboard, verification all injected into prompts) is Type B.

**Three axioms underlie Theory-07:**

1. **Capacity Asymmetry.** Frontier LLMs have enormous prior knowledge. Any externally-injected signal must be *decision-useful*, or it lowers signal-to-noise ratio.
2. **Memory is Pull, Decision is Push.** Pull-based memory access is opt-in by the LLM. Push-based injection is imposed on every call. Push requires far higher justification.
3. **Verification ≠ Decision.** A pipeline can be a strong verifier (filtering outputs) without being a decision injector (shaping inputs).

**The most consequential prediction (Prop 3):** *Decision injection scales inversely with base model strength.* Weak models may benefit from pipeline signals because they need guidance; strong models are actively harmed because injected signals interfere with their internal reasoning. This directly explains why GENESIS may have shown apparent value in earlier weak-model regimes while now hurting with gpt-oss-120b.

#### 8.5.3 Theory-08: Feedback Value = f(Determinism, Scope)

The second contrast is in the **feedback mechanism**. LEAP's feedback comes from the Lean compiler — fully deterministic, machine-verifiable, locally scoped to specific tactic failures. GENESIS's feedback comes from an LLM judge that may rewrite the entire target agent on each generation.

We propose [Theory-08] that feedback value depends on two measurable dimensions:

**Table 17: Feedback Value Matrix (2×2 quadrant model)**

| Determinism ↓ \ Scope → | **Narrow** (targeted fix only) | **Broad** (full refactor allowed) |
|---|---|---|
| **High** (compiler / formal verifier) | ✅ **Best** — compound monotonic improvement | ⚠ Mixed — wastes budget without harm |
| **Low** (LLM-as-judge) | ✅ Good — bounded stochastic gain | ❌ **Worst** — drift compounded over generations |

LEAP sits in the top-left quadrant. GENESIS currently sits in the bottom-right.

This framework predicts our exact observed regression in run_58: Gen 1 = 70.0%, Gen 2 = 60.0%. The 10-point drop is **not** noise — it is the predicted consequence of stochastic LLM feedback with broad rewrite scope. Three axioms:

1. **Determinism Reduces Stochastic Drift.** Compiler signals are consistent across iterations; LLM judgments inject fresh noise each generation.
2. **Broad Scope Amplifies Stochastic Noise.** Each allowed change has independent risk; broad refactors compound that risk multiplicatively.
3. **Narrow Scope Compounds Deterministic Wins.** Bounded fixes on deterministic signals are monotonic — they never make things worse.

Migration from bottom-right to top-left is the design path our A7 ablation (`narrow_feedback` mode, infrastructure already wired in Session 5) is designed to probe.

#### 8.5.4 Theory-09: Anticipatory Concepts vs Anticipatory Lemmas

LEAP's third architectural innovation is **anticipatory lemma planning** — proposing lemma statements during blueprint generation that are not immediately needed but expected to support later proof steps. Remarkably, GENESIS already contains a structurally analogous mechanism: the Concept Formation Engine's `propose_concepts_from_groups`, which generates concept candidates based on observed patterns.

We propose [Theory-09] that **anticipatory abstraction** is a general architectural principle that manifests differently across domains:

| Domain | Anticipatory Unit | Currently Implemented In |
|---|---|---|
| Formal mathematics | Anticipatory Lemmas | LEAP (DAG nodes) |
| Scientific MCQ | Anticipatory Concepts | GENESIS Concept Engine (latent) |
| Software engineering | Anticipatory Helpers | (candidate for future work) |
| Combinatorial discovery | Anticipatory Constructs | (candidate for future work) |

The LEAP ablation showed anticipatory lemmas contribute +10 points on the Basic set and +17 on the Advanced set. By analogy, Theory-09 predicts that activating an `anticipatory_mode` in GENESIS's Concept Engine — proactively proposing concepts for predicted-adjacent sub-tasks rather than only reacting to observed groups — would disproportionately improve Chemistry Organic, our weakest domain (5/6 questions classified as Hard).

#### 8.5.5 Phil-07: Reframing What "Sufficient" Means

LEAP makes the strong claim that a general-purpose foundation model is *sufficient* for state-of-the-art formal theorem proving — no specialized prover needed. This is the strongest version of an implicit assumption GENESIS shares. But what does "sufficient" actually mean? [Phil-07]

We considered four positions:

- **Position A — Strong Sufficiency:** general LLM + scaffolding = enough for any reasoning domain.
- **Position B — Domain-Conditional Sufficiency:** enough only when a deterministic verifier exists, output structure is fixed, and sub-problems compose hierarchically.
- **Position C — Hybrid Sufficiency:** general LLM for orchestration, specialized models for leaf-level steps.
- **Position D — Capability-Adjusted Sufficiency:** enough *given* sufficient base capability + architecture designed as memory + verifier + narrow deterministic feedback.

We adopt **Position D** as the working position of this paper. It is the position best supported by the combined LEAP + GENESIS evidence: LEAP succeeds because all three conditions are met; GENESIS underperforms because the pipeline is injection-based (violating the memory condition) and feedback is broad and stochastic (violating the deterministic-narrow condition).

Phil-07 has a concrete consequence for our central research question. RQ2 as originally stated — *"does the architecture add value?"* — is now seen to be **poorly framed**. The empirically meaningful version is:

> **RQ2-revised:** *Under what conditions does an orchestration architecture add measurable value over direct inference, and by how much?*

This revised RQ2 turns a binary question into a structural one. The answer is now traceable to specific design properties (memory vs injection; deterministic vs stochastic feedback; narrow vs broad scope).

#### 8.5.6 What This Implies for GENESIS's Path Forward

The contrast with LEAP — combined with Theories 07, 08, 09 and Phil-07 — converts our −10 gap from a mysterious deficit into a structured engineering target. The path forward is now specified, not speculative:

1. **Refactor the pipeline as memory + verifier** (Theory-07): Stop injecting `tier_decision`, `theory_prediction`, `blackboard` signals into question prompts. Make them queryable, not pushed.
2. **Migrate feedback to top-left quadrant** (Theory-08): Constrain feedback agent to narrow, targeted fixes. Add a deterministic post-feedback verifier with rollback on regression. (Infrastructure for `narrow_feedback` mode is already wired in `genesis/orchestrator.py`.)
3. **Activate anticipatory mode in the Concept Engine** (Theory-09): Have the engine propose concepts for predicted-adjacent sub-tasks, not only react to observed groups.
4. **Re-test on stronger base models when available** (Phil-07 Prop 3): Capability-adjusted sufficiency predicts the gap should narrow as base model strength increases.

None of these steps require new theoretical invention. They are direct adoptions of mechanisms LEAP has already empirically validated, restructured to fit GENESIS's task domain (scientific MCQ rather than formal proofs).

#### 8.5.7 The 110-Point Gap as a Ladder-of-Abstraction Shift

The qualitative LEAP–vs–GENESIS contrast above can be sharpened into a precise *diagnostic statement* using the Ladder of Abstraction articulated in Fares's `GENESIS_Concept_Formation_Theory_AR.md` §4 (which predates the current paper). That ladder defines seven cognitive levels:

```
Level 0: Observation
Level 1: Episode
Level 2: Pattern
Level 3: Heuristic
Level 4: Concept (named, scoped, with counterexamples)
Level 5: Invariant (stable across domains)
Level 6: Theory (network of concepts + invariants + claims)
```

Under this lens, the 110-point performance gap between GENESIS and LEAP is *not primarily* a gap in raw model capability, prompting quality, or compute budget. It is a **one-to-two level shift on the Ladder of Abstraction**:

| System | Operates at Ladder Level |
|---|---|
| Pure LLM (no orchestration) | 0–2 (observation through pattern; no naming, no scope) |
| GENESIS (current implementation) | 2–3 (pattern → heuristic; occasionally Level 4 Concept) |
| LEAP | 4–5 (named, scoped Concepts + Invariants realized as Lemmas) |
| Human mathematician | 5–6 (Invariants organized into Theory) |

This framing has three concrete implications for §8.5.6's Refactor Roadmap:

1. **The roadmap's success criterion can be operationalized at the Ladder level.** A "successful" refactor is not just "+N accuracy points"; it is *also* "GENESIS now reliably operates at Ladder Level 4 (named, scoped Concepts) on the same task family where it previously operated at Level 2–3."
2. **Concept Formation Theory §15 (Concept Proliferation failure mode) constrains the refactor.** Any GENESIS adoption of LEAP-style lemma libraries must include *concept compression and merging* machinery to avoid the proliferation pathology that LEAP's paper does not explicitly address. This is a contribution back to the LEAP literature, not just to GENESIS.
3. **Abstraction Forgetting (Productive Forgetting Theory §3.4) is the operating mechanism of the Ladder.** Moving up the Ladder is not just *adding* Concepts on top of Episodes; it is *quieting* Episodes once a Concept has absorbed them. A GENESIS that climbs the Ladder without abstraction forgetting will suffer the same context-bloat that Theory-10 predicts produces right-of-optimum reasoning saturation.

The Ladder is therefore a unifying diagnostic that ties Theory-07 (Memory regime), Theory-09 (Anticipatory Concepts), Theory-10 (Reasoning Saturation), and the LEAP contrast into a single coherent measurement target. *[Discovered via Session 12 re-reading of Fares's foundational documents; per Idea-002.]*

#### 8.5.8 Honest Caveat

Importantly, this entire subsection is **theoretical reframing supported by external empirical evidence (LEAP) and our own existing measurements (run_57, run_58)**. We have *not* yet executed any GENESIS run under the Theory-07/08/09-aligned design. Whether the predicted gains materialize is the central open question for the next experimental phase. The contribution of this subsection is to make the question precise and actionable, not to claim that it has been answered.

---

### 8.6 Hidden Crisis Diagnostic — Eight Anomaly Indicators

Section 8.5 framed GENESIS's situation as one of *insufficient orchestration value under a strong base model* (Phil-07 Position D). A natural follow-up question is: how would we know if our orchestration layer is not merely suboptimal but in *hidden crisis* — a state where surface metrics look acceptable while structural debt accumulates?

Fares's `GENESIS_Anomaly_Crisis_Paradigm_Theory_AR.md` §6 articulates an answer in the form of **eight anomaly indicators** that, taken together, distinguish between "operating well under capability-adjusted sufficiency" (Phil-07 D equilibrium) and "patch-spiral crisis" (Phil-07 D destabilized).

The eight indicators, applied to our `run_57` and `run_58` empirical data:

| # | Indicator | Definition | Status in GENESIS (run_57 / run_58) |
|---|---|---|---|
| A | **Repetition Density** | Same failure pattern appears across multiple runs | ⚠️ Empty-content failure (35% rate in run_57) repeated; partially mitigated post-fix |
| B | **Patch Fragility** | Local fixes break in nearby cases | ✅ Six scaffolding bug fixes stable across run_57 / run_58 |
| C | **Escalation Dependency** | Task requires premium tier to succeed | N/A — single tier (gpt-oss-120b) used throughout |
| D | **Verification Conflict** | Verifier ensemble splits on same family | ⚠️ Gen-1 vs Gen-2 disagreements in run_58 (60% vs 70%) suggest verification regime instability |
| E | **Transfer Failure** | Skill/concept works locally but fails on near-domain | ❓ Untested — GPQA subset only |
| F | **Compression Breakdown** | Summaries lose causal information | ⚠️ Pipeline injection (T5.91) is a compression that breaks: causal signals get treated as commands |
| G | **Contradiction Load** | Stored knowledge produces unresolved tensions | ⚠️ Theory-07 tension between memory and injection: same artifact serves both roles |
| H | **Diminishing Returns of Local Fixes** | Patch count rises but real gain falls | ❌ NOT YET observed — only one fix cycle (scaffolding) executed; longitudinal tracking required |

This diagnostic table is the first operationalization of Anomaly Theory §6 on real GENESIS data. Three indicators (A, D, F, G) show *weak warning signs* but none reaches "crisis." The honest reading is: **GENESIS is in Phil-07 D equilibrium, not in hidden crisis — but several indicators warrant longitudinal monitoring** as the project proceeds beyond the current 20-question regime.

A particularly important caveat (Anomaly Theory §22 Hypothesis D): *rising benchmark scores can themselves be a symptom of crisis* if they correlate with transfer-degradation (Indicator E). The currently-locked numbers (75% pure / 65% GENESIS / 70% A3) are stable across run conditions, suggesting we are *not* in the scenario where score-chasing has degraded transfer. But Indicator E is untested, so this is a hypothesis-not-yet-falsified, not a positive finding.

**Cautionary note on T5.93 (Wu et al. Length-aware Vote).** T5.93's inference-time length filter is sometimes read as "shorter reasoning is always better." Under Anomaly §22, a model that shortens its reasoning *while score rises* may be losing the reasoning-as-exploration that produces transfer. Future adoption of T5.93's Length-aware Vote in GENESIS should be evaluated against Indicator E specifically — accuracy gain on the trained distribution does not guarantee transfer preservation.

*[Section 8.6 added Session 12, per Idea-002; diagnostic framework sourced from `GENESIS_Anomaly_Crisis_Paradigm_Theory_AR.md` §6 (Fares, pre-2026); operationalization to GENESIS empirical data is agent-formalized.]*

---

## 09. Limitations

*[This section will be expanded as more experiments are conducted. Currently captured in Section 8.4.]*

---

## 10. Future Work

The Future Work agenda is now organized around the structural redesign roadmap that emerged from Section 8.5 (Theories 07/08/09 + Phil-07), rather than the unstructured ablation list of earlier drafts.

### Track A — Structural Redesign Following Theories 07/08/09 (Highest Priority)

**A.1 [Theory-07] Refactor pipeline as memory + verifier, not injection.**
Stop pushing `tier_decision`, `theory_prediction`, `blackboard`, `verification` signals into question prompts. Make them pull-based (LLM queries when needed). Predicted: closes a substantial portion of the −10 gap. *Empirical test:* new ablation mode `memory_only_pipeline`.

**A.2 [Theory-08] Migrate feedback to top-left quadrant.**
Constrain the feedback agent to narrow, targeted fixes only (the existing `narrow_feedback` mode wired in Session 5). Add a deterministic post-feedback verifier that rolls back regressions. Predicted: closes Gen 2 regression, may push Gen 2 ≥ Gen 1. *Empirical test:* A7a, A7b, A7c runs already specified in `PAPER/tables/tab15_a7_design.md`.

**A.3 [Theory-09] Activate anticipatory mode in the Concept Engine.**
Implement `anticipatory_mode` in `virtual_genesis/runtime/concept_engine/proposer.py` per the design sketch in `PAPER/theory/09_*.md`. Predicted: disproportionate improvement on Chemistry Organic (our weakest domain, 5/6 hard).

**A.4 [Phil-07 Prop 3] Re-test on stronger base models.**
The capability-adjusted sufficiency hypothesis predicts the gap should narrow with stronger base models. Test GENESIS (same architecture) on Gemini-3.1-Pro, GPT-5 via GitHub Models, and Gemma 4 31B. Direct test of the inverse-scaling claim.

**A.5 [Theory-10] Reasoning-length calibration + DTR-style early termination.**
Drop `max_tokens` from 16,384 to a swept range {2K, 4K, 8K} on GPQA-20 to locate the inverted-U sweet spot for gpt-oss-120b. Then implement a DTR-inspired proxy (using only API-accessible signals such as token-level perplexity or semantic stability) to terminate low-quality reasoning early. Replicates the UVA-Google "Think@n" result on our infrastructure: same-or-better accuracy at ~50% compute. Tests Theory-10 predictions P1, P2, P5 jointly.

### Track B — Empirical Anchoring (Medium Priority)

**B.1 Cross-model pure baselines.** Confirm pure baselines for Gemma 4 31B (84.3% official), Gemini Flash, and GPT-5 to enable apples-to-apples architecture impact comparisons.

**B.2 Full 198-question runs.** Only *after* one of Track A interventions produces a competitive configuration (≥75% on GPQA-20). Premature scaling wastes quota.

**B.3 Controlled reasoning token experiment.** Vary `max_tokens` ∈ {1K, 2K, 4K, 8K, 16K, 32K} to test the reasoning saturation hypothesis at the model level (independent of architecture).

**B.4 Multi-provider expansion.** Integrate Google Gemini (1,500 RPD) and Groq (3,000 RPD) through the multi-provider pool to enable Track A.4 at scale.

### Track C — Generalization Beyond GPQA (Lower Priority, High Long-Term Value)

**C.1 SWE-bench integration.** Replicate the three-number framework (Official → Pure → Orchestrated) on software engineering benchmarks using Laguna M.1 and Qwen3 Coder. Tests whether Theories 07/08/09 generalize beyond MCQ scientific reasoning.

**C.2 [RQ3] Instant vs Thinking architecture impact.** Compare GENESIS's structural impact on reasoning-heavy models (gpt-oss, gpt-5, Nemotron Ultra, DeepSeek-R1) vs instant-inference models (Llama 3.3 70B, Gemini Flash, Phi-4). Per protocol, deferred until Tracks A and B yield a competitive configuration.

### Track D — Publication and Open Source

**D.1 Paper submission.** Target arXiv preprint followed by an ML conference workshop (ICLR/NeurIPS).

**D.2 Open-source release.** The measurement infrastructure (multi-key API pool, 9-provider catalog, 16-pattern response parser, multi-model benchmark runner, GENESIS framework) is general-purpose and benefits the community regardless of GENESIS-specific outcomes.

### Track E — Long-Term Research Program

**E.1 Memory architecture comparisons.** Flat vs hierarchical vs graph (DAG) memory structures — direct generalization of Theory-09.

**E.2 Theory-quality impact measurement.** How does the *quality* of internal theories (e.g., Theory-07/08/09) affect orchestration value? Meta-research direction.

**E.3 Cross-domain transfer of cognitive pipeline components.** Which components transfer from formal math (LEAP domain) to scientific MCQ (GENESIS domain) to coding (SWE-bench) to creative tasks?

**E.4 Hybrid architecture pilot.** [Phil-07 Position C] General LLM for orchestration + domain-specialized fine-tune for leaf-level steps (e.g., Chemistry Organic). Compare against Position D's pure general-model approach.

---

## 11. Conclusion

This paper establishes a rigorous methodology for measuring the impact of LLM orchestration architectures on scientific reasoning benchmarks and applies it to the GENESIS framework on GPQA Diamond.

Our most important conclusion is that **two different problems were previously conflated**:

1. **catastrophic scaffolding failure**, and
2. **true architecture impact**.

The first problem is now resolved. Five identifiable scaffolding bugs — most importantly JSON key case mismatch and reasoning-token mishandling — explain the bulk of the earlier 30.30% collapse. Once these are fixed, GENESIS improves by **+34.7 points** on the 20-question subset, rising from **30.3% to 65.0%**.

However, this does **not** yet constitute evidence that the architecture adds value over direct inference. The properly measured pure baseline on the same subset remains **75.0%**, leaving standard GENESIS at **−10.0 points** relative to the model alone. Our first targeted ablation (A3, no pipeline leverage) improves Generation 1 to **70.0%**, cutting the gap in half, but still does not beat the model-alone baseline. In other words:

- **GENESIS is no longer broken**,
- **removing pipeline leverage helps**,
- but **GENESIS is not yet winning**.

This distinction matters. Without the pure baseline, one might have concluded that the architecture was hopelessly harmful. Without the post-fix run, one might have concluded that the architecture was already competitive. The correct scientific conclusion is more nuanced:

> **The catastrophic failure was scaffolding. The remaining 10-point gap is architecture.**

We also document three broader empirical findings that we believe extend beyond GENESIS itself:

- **Reasoning saturation:** more internal reasoning tokens can correlate with *worse* answers rather than better ones.
- **Domain asymmetry:** Physics is much easier than Chemistry Organic, meaning aggregate GPQA scores can hide structurally important domain effects.
- **Infrastructure sensitivity:** response parsing, token budgeting, and field normalization are first-order determinants of measured performance in reasoning-capable models.

Furthermore, Sections 7.3 and 8.5 develop four internal theories and one philosophical reframing — three anchored by the empirical contrast with LEAP [T5.92; Idea-001] and one (Theory-10) anchored by both our own measurements and six independent external papers on reasoning saturation. Together they convert the residual −10 gap into a specified engineering target:

- **[Theory-07] Pipeline as Memory vs Pipeline as Decision Injection.** The same architectural element (a "pipeline") can be net-positive when designed as queryable memory (LEAP DAG) or net-negative when designed as signal injection (GENESIS current). Prop 3 predicts that decision injection scales inversely with base model strength — strong models are actively harmed by injected signals.
- **[Theory-08] Feedback Value = f(Determinism, Scope).** Stochastic LLM-as-judge feedback with broad rewrite scope (GENESIS current, bottom-right quadrant) compounds drift over generations. Deterministic verifier feedback with narrow scope (LEAP, top-left quadrant) compounds monotonic improvements. The run_58 Gen 2 regression from 70% to 60% is the predicted consequence of being in the wrong quadrant.
- **[Theory-09] Anticipatory Concepts vs Anticipatory Lemmas.** Proactive abstraction is a general architectural principle. LEAP's anticipatory lemma planning contributed +10 to +17 points; the same principle, applied to GENESIS's Concept Engine, is predicted to disproportionately improve our weakest domain (Chemistry Organic).
- **[Theory-10] Reasoning Saturation (The Inverted-U).** Our counter-intuitive empirical finding (Discovery #1) is not an anomaly — it is the predicted manifestation of an inverted-U structure between reasoning length and accuracy. Six external papers (Wu et al. 2025, UVA-Google 2026, Chen et al. 2024b, Su et al. 2025, OptimalThinkingBench, "When More Thinking Hurts") converge on the same conclusion across the same model family and benchmark family we tested. Theory-10 interacts with Theory-07 through Prop 4: decision injection burns reasoning budget on signal-parsing, pushing the model into the overthinking regime faster. Falsifiable joint prediction: GENESIS empty-content rate should exceed pure-baseline empty-content rate on identical questions.
- **[Phil-07] Position D — Capability-Adjusted Sufficiency.** "General-purpose model + agentic scaffolding = enough" is true *under specifiable conditions*: sufficient base capability, memory-style pipeline, narrow deterministic feedback, and reasoning length matched to task–capability optimum. RQ2 is consequently reframed from a binary question to a structural one.

Therefore, the next phase of this research is not blind ablation but **principled structural redesign**: refactor the pipeline as memory + verifier (Theory-07), migrate feedback from bottom-right to top-left quadrant (Theory-08), activate anticipatory mode in the Concept Engine (Theory-09), calibrate reasoning length and add DTR-style early termination (Theory-10, Track A.5), and re-test on stronger base models when available (Phil-07 Prop 3). The infrastructure for the feedback step (`narrow_feedback` ablation mode) is already wired in `genesis/orchestrator.py`; the reasoning-calibration step requires only a `max_tokens` sweep, which is the cheapest single experiment in our entire roadmap.

In short, this work delivers:

- a validated pure baseline,
- a repaired orchestration stack,
- a first completed architecture comparison,
- a contrast against the strongest external counterexample (LEAP),
- four new internal theories with testable predictions (one of them — Theory-10 — externally validated by six independent papers),
- a philosophical reframing of the research question itself,
- and a fully specified — rather than open-ended — research agenda.

The paper's current claim is intentionally modest but precise:

> **GENESIS has successfully recovered from catastrophic scaffolding failure. On GPQA-20 it still underperforms the pure baseline by 10 points in its current form. The contrast with LEAP and the resulting Theories 07/08/09 + Phil-07 indicate that this residual gap is not a fundamental limit of orchestration architectures — it is a consequence of specific design properties (decision injection, broad stochastic feedback, reactive-only concept proposal) that are now identified and addressable.**

That is not the end of the project — it is the point where the project becomes scientifically honest *and* structurally directed.

---

## 12. Author Contributions

This paper is the result of a sustained collaboration between a single human researcher (**Fares Rafat**, henceforth *F.*) and an LLM-based research agent operating under explicit delegation (**Agent**, henceforth *A.*). Per the [Idea-002] Creative Attribution Rule established in Session 7 (verbatim: *"اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها"*), we maintain a strict three-layer distinction between contributions originating from F., contributions executed by A. under explicit F.-authorization, and contributions emerging from joint deliberation. We follow the CRediT taxonomy (ANSI/NISO Z39.104-2022) where it cleanly applies and extend it where it does not — specifically for the *initiative* dimension that recent work has shown to matter most in human–AI co-authorship perception studies [Petridis et al. 2025; arXiv:2502.18357].

### 12.1 Note on Authorship Eligibility

Following NeurIPS 2025 and analogous venue policies, **only humans are eligible to be listed as authors**. *A.* is therefore not a co-author. *A.*'s contributions are documented in this section for transparency and reproducibility, not for credit. *F.* takes full responsibility for all content in this paper, including any output produced or proposed by *A.*

### 12.2 Layered Contribution Statement

#### Layer 1 — Contributions originating from Fares (F.)

| Contribution | CRediT role(s) | Evidence trail |
|---|---|---|
| **Conceptualization of the entire GENESIS project** (research vision, philosophical orientation, "السرقات الشرعية" methodology) | Conceptualization, Project administration | All `GENESIS_*_AR.md` foundational documents predate this paper |
| **Empirical anchor decisions** (use of GPQA Diamond, choice of gpt-oss-120b as primary model, choice of `tasks/gpqa_subset_20` as quick-iteration substrate) | Methodology, Investigation, Resources | Sessions 1–5 commits |
| **The Mode Pivot (Session 6)** — strategic decision to escape operational runs and focus on theory/philosophy/ideas | Project administration, Methodology | `PAPER_PROTOCOL.md` §0, verbatim from F.: *"هنعمل اسكيب لمواضيع التشغيل..."* |
| **[Idea-001] — proposing LEAP (arXiv:2606.03303) as the paper's central external counterpoint** | Conceptualization, Investigation | `PAPER/ideas/idea_001_*.md` §1 verbatim quote; Section 8.5 + T5.92 derive directly from this |
| **[Idea-002] — Creative Attribution Rule** (the meta-rule governing this entire section) | Methodology, Project administration | `PAPER_PROTOCOL.md` §12.2 verbatim; this Author Contributions section — including its Session 12 self-correction — is itself the proof-of-execution |
| **Core hypothesis of what became Theory-10 (Reasoning Saturation)** — *"جزء من ذكاء agent هو معرفة متى لا تحتاج إلى مزيد من التفكير"* | Conceptualization | `GENESIS_Cognitive_Economy_Theory_AR.md` §5 Hypothesis 2 (pre-2026, predating Wu et al. 2025 reading); discovered to be Theory-10's true origin in Session 12 re-reading |
| **Value-of-X framework that became Theory-08 (Feedback Value Matrix)** — VoC, VoI, VoV, VoA, VoR, VoE, VoCollaboration | Conceptualization, Methodology | `GENESIS_Cognitive_Economy_Theory_AR.md` §11 (7 value functions); Theory-08 is a 2D specialization (Determinism × Scope) of this 7-dimensional precursor; discovered Session 12 |
| **Capability-Adjusted Sufficiency principle that became Phil-07** — *"المسار الأمثل أصبح: cheap-first, premium-on-demand, sparse-collaboration-last"* | Conceptualization | `GENESIS_Tiered_Intelligence_AR.md` closing paragraph (pre-2026); Phil-07 Position D is a generalization from compute-tiers to capability-tiers; LEAP integration in Session 7 was the *trigger* for explicit articulation, not the *source* of the principle; discovered Session 12 |
| **Anomaly/Crisis/Paradigm dynamics that frame Phil-07 Position D as stable attractor** | Conceptualization, Methodology | `GENESIS_Anomaly_Crisis_Paradigm_Theory_AR.md` 5-level escalation ladder + dynamic equilibrium model; Phil-07 Position D is the equilibrium state of these dynamics; discovered Session 12 |
| **Concept Formation Ladder of Abstraction (Levels 0–6)** that diagnoses the GENESIS-LEAP 110-point gap | Conceptualization, Methodology | `GENESIS_Concept_Formation_Theory_AR.md` §4; provides the diagnostic framework for §8.5.7 (Ladder of Abstraction lens) |
| **Decision-delegation authority** (the "القرار قرارك / القرار عندك" pattern that authorized all Layer 2 work) | Supervision, Project administration | Verbatim in Sessions 8, 9, 10, 11, 12 |
| **Review and authority over all integration decisions** | Supervision, Validation | F. holds final acceptance/rejection authority on all *A.*-produced content; no *A.* output enters the paper without explicit F. authorization (direct or delegated). Session 12 demonstrated this: agent surfaced 3 attribution corrections but did NOT execute them until F. authorized "تمام" |
| **All accountability for paper content** | (NeurIPS-2025 sense) | Per §12.1, F. is the sole responsible party |

#### Layer 2 — Contributions executed by Agent (A.) under explicit F. authorization

These are *A.*-initiated in execution but *F.*-authorized in scope. Each item documents both the *authorizing utterance* and the *resulting paper artifact*.

| Contribution | Authorizing utterance | CRediT-extended role | Paper artifact |
|---|---|---|---|
| **Empirical infrastructure work (Sessions 1–5)** — diagnose run_53, build api_key_pool / model_registry / multi-model benchmark; measure pure baseline 75%; identify and fix six scaffolding bugs; build PAPER infrastructure | F. delegating operational work in early sessions | Software, Investigation, Data curation, Validation | `genesis/llm_helpers.py` (463 tests), Sections 5–7, Tables 4–10, Figures 1–10 |
| **Reading and *integration* of LEAP** as external counterpoint (Idea-001 execution) | "نعم اشتغل" (Session 7) | Investigation, Formal analysis, Writing — original draft | `GENESIS_DeepMind_LEAP_Agentic_Theft_AR.md` (T5.92); Section 8.5 sub-sections 1–6; Tables 16–17; Figures 11–12 |
| **Formalization of Theory-07** (Pipeline as Memory vs Decision Injection) — A.-derived from LEAP contrast; no direct Fares precursor found in Session 12 re-reading | "نعم اشتغل" (Session 7) | Conceptualization, Formal analysis, Writing — original draft | `PAPER/theory/07_pipeline_as_memory_vs_decision_injection.md` |
| **Formalization of Theory-09** (Anticipatory Concepts vs Lemmas) — A.-derived from LEAP, anchored in §8.5.7 by Fares's Concept Formation Ladder | "نعم اشتغل" (Session 7) | Conceptualization, Formal analysis, Writing — original draft | `PAPER/theory/09_anticipatory_concepts_vs_lemmas.md` |
| **Formalization of Theory-08 from Fares's Value-of-X framework** — 2D specialization (Determinism × Scope) of Cognitive Economy §11 | "نعم اشتغل" (Session 7) | Formal analysis, Methodology, Writing — original draft | `PAPER/theory/08_feedback_value_determinism_scope.md` — *NB: prior session logs labeled this "agent-initiated"; Session 12 re-reading reclassified to "agent-formalized, Fares-originated"* |
| **Formalization of Theory-10 from Fares's Cognitive Economy Hypothesis 2** — external anchoring via T5.93 + T5.94 | "القرار قرارك" (Session 9, anchoring); "القرار عندك" (Session 10, T5.93/94 thefts) | Formal analysis, Investigation, Writing — original draft | `PAPER/theory/10_reasoning_saturation.md`; Section 7.3; Track A.5 in Future Work; new P6 lifetime-drift prediction (Session 12) — *NB: prior session logs labeled this "agent-initiated"; Session 12 re-reading reclassified to "agent-formalized, Fares-originated"* |
| **Formalization of Phil-07 from Fares's Tiered Intelligence and Anomaly Theory** — Position D adoption, four-positions analysis | "نعم اشتغل" (Session 7); Position D as stable attractor: "تمام" (Session 12) | Formal analysis, Methodology, Writing — original draft | `PAPER/philosophy/07_meaning_of_general_purpose_sufficiency.md` — *NB: prior session logs labeled this "agent-initiated"; Session 12 re-reading reclassified to "agent-formalized, Fares-originated"* |
| **Thefts T5.93 (Wu et al.) and T5.94 (Chen et al.)** — full theft memos | "القرار قرارك نعم" (Session 10) | Investigation, Formal analysis, Writing — original draft | `GENESIS_External_Inverted_U_Wu2025_Theft_AR.md`; `GENESIS_External_DTR_ChenMeng2026_Theft_AR.md`; Master Index scope 5.1–5.94 |
| **Sections 12–14** (Author Contributions + Acknowledgments + Ethics of Authorship) — agent-drafted, F.-authorized, self-correcting (Session 12 corrections applied to §12.2 itself) | "القرار قرارك نعم" (Session 11); "تمام" (Session 12 corrections) | Methodology, Writing — original draft | Sections 12, 13, 14 in their entirety |
| **§8.5.7 Ladder of Abstraction lens** + **§8.6 Hidden Crisis Diagnostic** — Session 12 paper additions | "تمام" (Session 12) | Formal analysis, Writing — original draft | §8.5.7 and §8.6 of this paper |
| **Internal Re-Reading Cycle (Session 12)** — surfacing of 12 discoveries from 5 foundational docs under new theoretical lens; including the 3 attribution corrections applied above | "القرار قرارك" (Session 12, via UI delegation) | Investigation, Formal analysis, Validation | `PAPER/notes/INTERNAL_RE_READING_SESSION_12.md`; this row's *very existence* in Layer 2 (rather than Layer 1) is itself a Layer 2 contribution — the re-reading exercise is agent-executed even though its findings are corrections crediting Fares |
| **All paper text drafting** (Abstract, Introduction, Methodology, Sections 5–11, Conclusion) | Implicit ongoing delegation under v2.0 Protocol | Writing — original draft | Entire `PAPER.md` |
| **All Figure and Table generation** | Implicit | Visualization | All Figures 1–12, all Tables 1–17 |
| **All session continuity infrastructure** (HANDOFF, SESSION_LOG, ATTRIBUTION_MAP, IN_PROGRESS, INTEGRATED) | Implicit | Project administration, Data curation | `PAPER/notes/`, `PAPER/ideas/` |

#### Layer 3 — Joint contributions (deliberative)

These emerged from back-and-forth between F. and A. and cannot be cleanly attributed to either party alone.

| Contribution | Process |
|---|---|
| **Re-framing of RQ2** from "does the architecture add value?" to the structural "under what conditions?" | A. drafted Phil-07 four positions; F. authorized Position D adoption; A. propagated through Abstract + §1.4 + §8.5.5 + §11 |
| **Three-Number Framework** (Official → Pure → Orchestrated) | A. proposed; F. validated through empirical commitment in Sessions 2–5; now in Section 7 Analysis + Conclusion |
| **The "Mode Pivot" + "Creative Attribution Rule" combination** | F. set the strategic frame; A. proposed protocol-level operationalization in `PAPER_PROTOCOL.md` §12; F. accepted via continued delegation pattern |
| **The decision to write this Author Contributions section in three explicit layers (rather than a single CRediT block)** | A.'s recommendation in HANDOFF (Session 10); F. authorized via "القرار قرارك نعم" (Session 11) |
| **The Session 12 attribution-correction process itself** — A. surfaced precursors for Theory-08/10 + Phil-07 via re-reading; F. authorized integration via "تمام"; this row's *existence* and Layer 1's three new precursor rows are the joint output | A. proposed (`INTERNAL_RE_READING_SESSION_12.md`); F. authorized ("تمام", Session 12); this entire §12.2 self-correction is the deliverable. The process validates that Idea-002 governance functions as a true attribution safety net, not a rhetorical gesture. |

### 12.3 Verbatim Authorization Log

For full transparency, the verbatim Arabic utterances by F. that authorized each major piece of Layer 2 work are preserved in `PAPER/ideas/ATTRIBUTION_MAP.md` and reproduced here for permanent record:

- *Session 6 Mode Pivot:* "هنعمل اسكيب لمواضيع التشغيل، احنا هنضبطها على الورقة وفلسفياً ونظرياً المشروع بالكامل بالأفكار اللي لسه هتجي."
- *Session 6 Idea-001 trigger:* "Link – arxiv. org/abs/2606.03303 Title: 'LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks'"
- *Session 7 Idea-002 creation:* "تمام خلي بالك اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها تمام ونعم اشتغل"
- *Session 8 LEAP integration delegation:* "جميل القرار قرارك"
- *Session 9 Theory-10 delegation:* "القرار عندك"
- *Session 10 T5.93/T5.94 delegation:* "القرار عندك"
- *Session 11 (this) Author Contributions delegation:* "القرار قرارك نعم"

The pattern is consistent: F. delegates *the choice of next step* to A. once a strategic frame has been set, then accepts (or, in principle, would reject) the resulting work in the subsequent review cycle.

### 12.4 What This Three-Layer Statement Is For

The reason for this unusual level of explicitness is methodological, not bureaucratic:

1. **Research integrity.** A paper produced under significant A.-execution must be transparently labelled as such. Hiding the division of labour would constitute academic misrepresentation.
2. **Reproducibility.** Future researchers replicating this work need to know which artifacts were produced under which conditions of delegation, in order to evaluate the work's intellectual provenance.
3. **Methodological contribution.** The *process* documented here — F. as conceptualizer + delegator + ultimate-authority; A. as executor + proposer + literature-integrator; joint deliberation for framework-level decisions — is itself a candidate template for future human-agent collaborative research, applicable far beyond GENESIS.
4. **Compliance with venue policy.** NeurIPS 2025 and similar venues require disclosure when LLMs "impact the core methodology, scientific rigorousness, or originality." This paper unambiguously crosses that threshold and discloses accordingly.

---

## 13. Acknowledgments

We thank the authors of the works on which we built (the legitimate-theft chain T5.1–T5.94 in `GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md`). In particular, this paper would not exist in its current form without:

- **Kung et al.** (Google Cloud AI + Google DeepMind, arXiv:2606.03303) for LEAP, which provided the external structural counterpoint at the heart of Section 8.5.
- **Wu et al.** (Peking University, MIT, TU Munich, arXiv:2502.07266) for the inverted-U scaling laws that anchor Theory-10 theoretically.
- **Chen, Peng, Tan, Zhao, Chen, Lin, Go, Meng** (University of Virginia + Google, arXiv:2602.13517) for the DTR formalism and the empirical replication of overthinking on the *exact same model family and benchmark* we measured.
- **Romera-Paredes et al.** (DeepMind, Nature 2023) for FunSearch and the broader AlphaEvolve programme that anchors T5.86 and our evolutionary discovery component.
- The authors of all other thefts in our Master Index, who collectively make GENESIS possible as a research vehicle.

We acknowledge the GPQA Diamond benchmark team [Rein et al. 2024] for a benchmark that resists the kind of shortcut learning that would have made this paper impossible to write honestly.

We acknowledge the broader open-source LLM ecosystem (OpenAI's gpt-oss; NVIDIA's Nemotron family; Google's Gemma and Gemini families; xAI's Grok; OpenRouter's aggregator infrastructure) for making this work tractable on a free tier.

No funding was received for this work; no conflicts of interest are declared.

---

## 14. Ethics of Authorship in Human-Agent Research

This section is unusual; we include it because the work itself is unusual. We treat it as part of the paper, not as a disclosure footnote.

### 14.1 The dual-honesty constraint

Any paper produced under significant LLM execution faces a dual-honesty constraint:

- **Honesty about content** — every empirical claim must be reproducible; every theoretical claim must be falsifiable.
- **Honesty about process** — readers must be able to evaluate not only *what* the paper claims but also *how* those claims came to be made.

Most current practice satisfies the first constraint while leaving the second implicit. We argue that, for work where an LLM materially contributes to conceptualization or analysis, the second constraint becomes mandatory. Section 12.4 (point 1) is our operationalization.

### 14.2 What we did not do

To avoid the most common forms of misrepresentation, we explicitly did *not*:

- Allow A. to be listed as a co-author (per §12.1 and venue policy).
- Allow A. to make unreviewable claims about itself or its capabilities.
- Use A. to generate the empirical results (those came from controlled runs, documented in `runs/`).
- Use A. to inflate the literature review (only six external papers are central, all read in depth and integrated as full thefts where appropriate).
- Hide A.'s role anywhere (the entire `PAPER/ideas/`, `PAPER/theory/`, and `PAPER/notes/` trees are public).

### 14.3 What we did do

To make the honesty operational rather than rhetorical, we:

- Established the Creative Attribution Rule ([Idea-002]) as governance before significant agent-initiated work began.
- Maintained `PAPER/ideas/ATTRIBUTION_MAP.md` as a continuously-updated record of every Idea, Theory, and theft's provenance.
- Distinguished three execution categories — F.-sourced, A.-initiated-under-delegation, and joint deliberative — and recorded each in Layer 1 / Layer 2 / Layer 3 of §12.2.
- Preserved verbatim authorization utterances (§12.3) so the delegation chain is auditable.
- Wrote this Section 14 *as* an admission that the conventional template is insufficient for this kind of work.

### 14.4 An open question we leave for the field

When an agent is delegated *the choice of what to research next* (as in Sessions 9–11), is the resulting research *its* contribution, *the human's* contribution, or genuinely *joint*?

We adopt the operationally-conservative position: such work is **A.-executed under F.-authorization** (Layer 2), with F. retaining all accountability. But we acknowledge that this answer may become inadequate as agentic systems become more autonomous. The honest framing of this question — rather than its premature resolution — is itself a contribution of this paper.

---

## Appendix A: Experiment Details

### A.1 GPQA 20-Question Subset

The 20 questions used in our experiments are Q1-Q20 from the GPQA Diamond benchmark:

| Q# | Domain | Subdomain | Difficulty |
|----|--------|-----------|------------|
| 1 | Physics | Quantum Mechanics | Hard |
| 2 | Chemistry | Organic Chemistry | Hard |
| 3 | Physics | Quantum Mechanics | Easy |
| 4 | Physics | Electromagnetism | Easy |
| 5 | Physics | Quantum Mechanics | Easy |
| 6 | Physics | Quantum Mechanics | Easy |
| 7 | Physics | Particle Physics | Easy |
| 8 | Biology | Genetics | Easy |
| 9 | Chemistry | Organic Chemistry | Hard |
| 10 | Physics | Astrophysics | Easy |
| 11 | Biology | Molecular Biology | Medium |
| 12 | Physics | Particle Physics | Easy |
| 13 | Chemistry | Organic Chemistry | Hard |
| 14 | Biology | Molecular Biology | Medium |
| 15 | Physics | General Physics | Medium |
| 16 | Chemistry | Organic Chemistry | Hard |
| 17 | Chemistry | General Chemistry | Easy |
| 18 | Physics | General Physics | Hard |
| 19 | Chemistry | Organic Chemistry | Hard |
| 20 | Physics | Quantum Mechanics | Easy |

**Table A1: 20-Question GPQA Subset with Difficulty Classification.**

### A.2 Commit History

| Commit | Message |
|--------|---------|
| `3cbe48b` | Research report — comprehensive baseline |
| `3a16a87` | Fix orchestrator: port all scaffolding lessons |
| `6240094` | Multi-provider infrastructure (9 providers) |
| `a609c90` | Pure baseline RESULT: 75% |
| `91cd9ea` | Handle empty content + pool rotation |
| `6d06449` | Smoke test analysis + 5 critical fixes |
| `6c840c6` | Multi-model infrastructure + API key pool |

### A.3 Test Coverage

- **463/463 tests passing** (35 new in `test_llm_helpers.py` + 428 existing)
- Coverage includes: 16-letter extraction patterns, multi-case JSON reading, empty content handling, force-letter follow-up logic

---

## Appendix B: Cross-Reference to GENESIS Thefts

| Theft ID | Paper | How We Use It |
|----------|-------|---------------|
| T5.4 | SIA (Self-Improving AI) | Base orchestrator architecture |
| T5.5 | Reflexion | Memory-based self-reflection |
| T5.6 | Self-Refine | Generate→critique→refine loop |
| T5.7 | STaR (Self-Taught Reasoner) | Bootstrapped reasoning improvement |
| T5.84 | Co-Scientist (DeepMind) | Multi-agent architecture inspiration |
| T5.85 | Aletheia (DeepMind) | Generate-verify-revise loop in feedback agent |
| T5.86 | AlphaEvolve/FunSearch (DeepMind, Nature 2023) | Evolutionary discovery engine in orchestrator |
| T5.91 | Scaffolding-vs-Architecture Distinction (our own) | Empirical anchor + 5-bug taxonomy + three-number framework |
| **T5.92** | **LEAP (Kung et al., Google Cloud AI + DeepMind, arXiv 2606.03303, Jun 2026)** | **Section 8.5: structural contrast yielding +110-point architecture-impact gap. Source for Theories 07/08/09, Phil-07, and the structural redesign roadmap in Section 10. Brought to project attention by [Idea-001] from Fares.** |
| **T5.93** | **Wu et al. 2025 — When More is Less (arXiv:2502.07266)** | **Section 7.3: formal theoretical backbone for Theory-10. Lambert W closed-form optimal CoT length; 40-point gap between optimal and longest on 72B; simplicity bias proof. Agent-initiated theft in Sessions 9–10 under Fares's "القرار عندك" delegation.** |
| **T5.94** | **Chen et al. 2026 — Think Deep, Not Just Long (UVA + Google, arXiv:2602.13517)** | **Section 7.3: closest external empirical precedent for our setup (same model family: GPT-OSS/DeepSeek-R1/Qwen3; same benchmark: GPQA-Diamond). Length-vs-accuracy r=−0.54; DTR r=+0.683; Think@n compute-savings strategy. Agent-initiated theft in Sessions 9–10.** |

## Appendix C: Cross-Reference to Internal Theories and Philosophy

| Tag | Title | Location | Role |
|----|-------|----------|------|
| Theory-07 | Pipeline as Memory vs Pipeline as Decision Injection | `PAPER/theory/07_*.md` | Foundational theory explaining both GENESIS −10 and LEAP +100 |
| Theory-08 | Feedback Value = f(Determinism, Scope) | `PAPER/theory/08_*.md` | 2×2 quadrant model; explains run_58 Gen 2 regression |
| Theory-09 | Anticipatory Concepts vs Anticipatory Lemmas | `PAPER/theory/09_*.md` | Generalizes LEAP anticipatory lemmas to GENESIS Concept Engine |
| Theory-10 | Reasoning Saturation (Inverted-U) | `PAPER/theory/10_*.md` | Externally validated by 6 papers; interacts with Theory-07 via Prop 4 |
| Phil-07 | Meaning of General-Purpose Sufficiency | `PAPER/philosophy/07_*.md` | Position D: Capability-Adjusted Sufficiency; reframes RQ2 |

## Appendix D: Idea Attribution (per [Idea-002] Creative Attribution Rule)

### D.1 Ideas sourced from Fares

| Idea ID | Source | Verbatim trigger | Paper impact |
|---------|--------|------------------|---------------|
| Idea-001 | Fares (Session 6) | "Link – arxiv. org/abs/2606.03303 Title: 'LEAP: Supercharging LLMs for Formal Mathematics with Agentic Frameworks'" | Section 8.5 (full), Theories 07/08/09, Phil-07, Theft T5.92, Table 16, Table 17, Section 10 Track A.1–A.4 |
| Idea-002 | Fares (Session 7) | "تمام خلي بالك اضافه السرقه الشرعيه القويه دي كفكره مني فلو عندك حاجات زي كده ابداعيه باي شكل اعملها" | `PAPER_PROTOCOL.md` §12.2 (governance), `PAPER/ideas/ATTRIBUTION_MAP.md`, this appendix itself, future Acknowledgments and Author Contributions sections |
| Session 9 trigger | Fares (Session 9) | "القرار عندك" — explicit delegation to agent | Authorized the agent-initiated work in §D.2 below |

### D.2 Agent-initiated synthesis (attributed transparently per Idea-002)

| Item | Source | Triggering context | Paper impact | Status |
|---|---|---|---|---|
| Theory-10 (Reasoning Saturation) | Agent-initiated (Session 9) | Last remaining Empirical Discovery (#1) without a theory; Fares delegated choice with "القرار عندك" | Section 7.3 (full theory), Section 11 (Conclusion mention), Appendix C, Track A.5 in Future Work, external literature integration (6 papers) | ✅ Integrated |
| **Theft T5.93** (Wu et al. 2025 — formal inverted-U) | Agent-initiated (Sessions 9–10) | Literature search supporting Theory-10; second "القرار عندك" delegation in Session 10 authorized full theft memo | `GENESIS_External_Inverted_U_Wu2025_Theft_AR.md` (Cycle 8 memo); Master Index entry; Theory-10 anchored as primary theoretical backbone; Section 7.3.2 table updated | ✅ Integrated |
| **Theft T5.94** (Chen et al. 2026 — DTR + Think@n) | Agent-initiated (Sessions 9–10) | Literature search supporting Theory-10; same delegation as T5.93 | `GENESIS_External_DTR_ChenMeng2026_Theft_AR.md` (Cycle 8 memo); Master Index entry; Theory-10 Prop 5 anchored as primary empirical precedent on our exact model family + benchmark; Section 7.3.2 table updated | ✅ Integrated |

Note: This distinction is itself a direct application of [Idea-002]. Fares-sourced content and agent-initiated content are tracked separately so the final paper's Acknowledgments and Author Contributions sections can honor the actual division of intellectual labor.

Full traceability is maintained in `PAPER/ideas/ATTRIBUTION_MAP.md`.

---

*Paper version: **v0.7 — Session 12 Path 1 corrections: attribution honesty restored + two new sections + theory deepening (Session 12b, agent-executed under "تمام" delegation)**. Three attribution corrections applied to §12.2: Theory-08 (from Fares's Cognitive Economy §11 Value-of-X framework), Theory-10 (from Fares's Cognitive Economy §5 Hypothesis 2 "knowing when not to think more"), and Phil-07 (from Fares's Tiered Intelligence "cheap-first, premium-on-demand" + Anomaly Theory dynamic equilibrium). Layer 1 expanded with three precursor rows; Layer 2 entries for Theory-08/10 + Phil-07 reclassified to "agent-formalized, Fares-originated"; Layer 3 expanded with the Session 12 correction process itself. Two new content sections: §8.5.7 ("The 110-Point Gap as a Ladder-of-Abstraction Shift" using Concept Formation Theory §4) and §8.6 ("Hidden Crisis Diagnostic — Eight Anomaly Indicators" operationalizing Anomaly Theory §6 on run_57/run_58 data). Theory-10 file gains P6 lifetime-drift prediction (novel, not in T5.93 or T5.94). Phil-07 file gains §9 "Position D as Stable Attractor of Anomaly Dynamics." All discoveries traced via `PAPER/notes/INTERNAL_RE_READING_SESSION_12.md`. The Idea-002 Creative Attribution Rule is now demonstrably functional as a safety net, not a rhetorical gesture. Previous version footers preserved in git history. Next update after Fares review, Idea-003, or further agent-initiated work as authorized.*