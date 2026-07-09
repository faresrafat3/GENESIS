# §2 Related Work

هذا القسم يستعرض الأوراق الرئيسية اللي بنيت مساهماتنا فوقها أو تختلف عنها. بالتحديد، ركزنا على أنظمة LLM orchestration الحديثة من DeepMind، وبنشير لبعض الاتجاهات الفلسفية المكملة.

## 2.1 AlphaEvolve & FunSearch (Google DeepMind, 2024)

### The Idea
**FunSearch** [1] استخدم "LLM + Evaluator closed loop" لاكتشاف خوارزميات جديدة (cap set problem). **AlphaEvolve** [2] عمم الفكرة لأي "artifact قابل للتقييم": code snippets, mathematical constructs, agent policies.

### Their Key Findings
- Evolutionary search بيكتشف حلول جديدة لا يقدر LLM لوحده يوصلها في single shot
- المهم مش الـ LLM القوي بس، بل الـ **evaluator** الصارم
- **Population diversity** أهم من "best of N" — يمنع local optima

### Curves We Adopt
- **AlphaEvolve Figure 3-like:** score vs generation (progress curve)
- **FunSearch Table 1-like:** baseline vs discovered method comparison

### How We Differ / Contribute Back
- ✅ **We implement AlphaEvolve-style skeleton** في `evolutionary_discovery_engine()` (population=6, gens=2, diversity_weight=0.3)
- ⏳ **T3 ablation:** هل الـ evolutionary discovery في GENESIS بيضيف قيمة قابلة للقياس؟ (لسه ما جربناش)
- 🆕 **Novel angle:** نحن نسأل إذا كانت مكاسب AlphaEvolve نفسها ممكن تكون مساهمة scaffolding — لأنهم لم يفصلوا الاتنين

### Their Blind Spot We Address
AlphaEvolve/FunSearch **لا يوثقون scaffolding hygiene** بشكل صريح. من الممكن أن جزء من "الاكتشافات" الجديدة كانت pure LLM كافي لعملها لو الـ scaffolding كان صحيح.

### Cross-Reference in Our Paper
- §3.4 (Architecture)
- §6.2 (B1 — they may share this bug)
- §7 (Results — comparable format)
- §8 (Ablation without evo)

---

## 2.2 Aletheia / Gemini Deep Think (DeepMind, 2025)

### The Idea
**Aletheia** [3] تقدم **Tripartite Generator-Verifier-Reviser loop**:
1. Generate candidate answer
2. Natural-language verification (critique + gap analysis)
3. Targeted revision or restart

### Their Key Findings
- Verification-in-natural-language أقوى من scalar rewards
- Model يقدر يقول "critically flawed → restart" بدل ما يضيع compute
- Iteration count ⟺ accuracy: curves converging

### Curves We Adopt
- **Aletheia Figure 2-like:** iteration count vs correctness (converging curve)

### How We Differ
- ✅ **Our feedback_agent** = Aletheia's Verifier + Reviser combined
- ⚠️ **We use programmatic verification** (constitutional_report + evaluation.log) بدل full natural language critique
- ⏳ **T3 ablation:** هل الـ feedback agent (verify-revise) بيضيف قيمة؟

### Their Blind Spot We Address
Aletheia يستخدم Gemini Deep Think (huge context, deep reasoning) — احتمال كبير أن ال scaffolding عندهم robust. لكن **ما اختبروش على smaller models** حيث scaffolding bugs بتظهر بشكل أوضح.

### Cross-Reference in Our Paper
- §3.5 (Feedback Agent as Verify-Revise)
- §6.5 (B4 — reasoning extraction, related)
- §8 (Ablation without feedback)

---

## 2.3 Co-Scientist / Gemini for Science (DeepMind, 2025)

### The Idea
**Co-Scientist** [4] بيقدم multi-agent system لـ scientific research:
- Multiple specialized agents (idea generators, critics, evaluators)
- "Idea tournament": agents يتناقشوا حول hypotheses
- Human-AI collaboration (مش استبدال)

### Their Key Findings
- Multi-agent debate بيتفوق على single-agent على مهام research جديدة
- Tool integration (databases, literature) essential
- Transparency + citations required

### Curves We Adopt
- **Co-Scientist Table 2-like:** multi-agent vs single-agent metrics comparison

### How We Differ
- ✅ **We have 3 agents** (meta, target, feedback) لكن مش "debate" — sequential
- ⏳ **Deferred:** implementation of agent debate (in §11)

### Their Blind Spot We Address
Co-Scientist مركز على research generation، مش على standard MCQ benchmarks زي GPQA. الـ pattern of failure/success بيختلف بين النوعين. **Also**, لم يوثقوا scaffolding bugs يمكن كانوا يحسنوا performance بدون multi-agent.

### Cross-Reference in Our Paper
- §3.6 (Sequential Agents vs Debate)
- §11.1 (Future: agent debate)

---

## 2.4 Other LLM Orchestration Frameworks (Brief Survey)

### LangChain / LangGraph
- Popular open-source framework
- **Known scaffolding pitfalls:** JSON parsing errors common in community reports
- **B1, B4 particularly common**
- We don't compare directly (different design goals) but our library `genesis/llm_helpers.py` is drop-in compatible

### DSPy (Stanford, 2023)
- Schema-based approach reduces B1 risk
- Still susceptible to B2, B3, B4, B5
- Our library complements DSPy: schema validation is orthogonal to reasoning extraction

### CrewAI, AutoGen
- Multi-agent frameworks
- Complex enough that all 5 bugs plausibly present
- Would benefit from adopting our diagnostic toolkit (`tools/diagnose_run_53.py`)

**Table 2.1: Framework Susceptibility Estimates** (from §6.8)

| Framework | B1 | B2 | B3 | B4 | B5 |
|---|---|---|---|---|---|
| LangChain | Possible | Possible | Depends | **Likely** | Depends |
| DSPy | Unlikely | Possible | Possible | **Likely** | Yes |
| CrewAI | Possible | Possible | Possible | **Likely** | Possible |
| AutoGen | Possible | Possible | Possible | **Likely** | Possible |
| Custom | **V. Likely** | **V. Likely** | Common | **V. Likely** | Common |

---

## 2.5 The GPQA Benchmark

### The Benchmark
**GPQA** [5] (Google-Proof Q&A) — 448 questions × PhD-level science:
- Physics, Chemistry, Biology
- Written by domain experts
- "Diamond" subset (198q) is hardest
- **Human PhD accuracy: ~65%** (with time + Google)
- **Untrained non-experts: ~34%** (with Google, unlimited time)

### Their Key Findings
- Frontier LLMs (GPT-4, Claude 3.5, gpt-oss-120b) reach 60-80%
- Physics tends to be easier for LLMs than Chemistry/Biology (**we replicate this in §5**)

### How We Use It
- **Primary evaluation benchmark** for all our experiments
- 20-question subset for rapid iteration (T1)
- Full 198q run planned (T2)

### Cross-Reference in Our Paper
- §4.2 (Setup)
- §5.4 (Per-domain analysis replicates GPQA authors' finding)

---

## 2.6 gpt-oss Model Card (OpenAI/NVIDIA, arXiv:2508.10925)

### The Card
Documentation for `gpt-oss-120b` and `gpt-oss-20b` — OpenAI's open-weights models targeting frontier reasoning.

### Their Key Findings
- **Reasoning effort tunable:** `low` (67.1%), `medium` (73.1%), `high` (80.1%) on GPQA
- **Reasoning tokens can dominate** completion budget
- **131K context** window

### How We Use It
- **Primary model for our baseline** — 75.00% on 20q subset (matches official 80.1%±10% CI)
- **Access via OpenRouter free tier** (quantization impacts accuracy slightly)

### Our Emergent Contribution vs Their Documentation
- ⚠️ **They document reasoning effort as monotonically improving accuracy**
- 🆕 **We observe per-question reasoning tokens correlate NEGATIVELY with accuracy** (§5.5)
- **Interpretation:** their claim holds AT AGGREGATE LEVEL (average of thousands of questions), but at PER-QUESTION LEVEL, hard questions consume more reasoning AND are more likely wrong. This is nuance the model card doesn't discuss.

### Cross-Reference
- §4.1 (Model choice)
- §5.5 (Reasoning saturation)
- §9.2 (Discussion of reasoning saturation)

---

## 2.7 What's Missing from the Literature

Based on our review:

1. **No paper explicitly documents "empty content"** as a scaffolding bug requiring reasoning extraction (B4). We appear to be first.

2. **No paper explicitly documents reasoning saturation at per-question level.** gpt-oss card discusses aggregate scaling but not this pattern.

3. **No paper provides "scaffolding hygiene checklist"** for LLM orchestration systems. Our diagnostic toolkit is first.

4. **No paper attempts to attribute performance gaps** to bugs vs architecture. Most conflate them.

**These gaps** motivate our contributions (C1-C5 in §1.3).

---

## 2.8 Positioning of Our Work

```
       "Architecture innovation"                    "Scaffolding hygiene"
     (AlphaEvolve, Aletheia, Co-Sci)                    (this paper)
             ↑                                                 ↑
             |                                                 |
             |                          gap                    |
             |         •——————————————————————————————•       |
             |         claims of +5 to +20 pts                |
             |         but no scaffolding audit                |
             |                                                 |
             |                                                 |
Pure LLM baseline ——————————————————————————→ 45 points of "scaffolding scope"
                                                  (this paper measures this)
```

Our work is **complementary**, not competitive:
- We don't claim our architecture is better than AlphaEvolve/Aletheia
- We claim: before comparing architectures, **fix your scaffolding**
- Once scaffolding is fixed, architectural comparisons become interpretable

---

## References

[1] Romera-Paredes et al. — "Mathematical discoveries from program search with large language models" — Nature 2024 (FunSearch)
[2] AlphaEvolve — DeepMind whitepaper 2024/2025
[3] Aletheia / Gemini Deep Think — DeepMind 2025
[4] Co-Scientist / Gemini for Science — DeepMind 2025
[5] Rein et al. — "GPQA: A Graduate-Level Google-Proof Q&A Benchmark" — arXiv:2311.12022 (2023)
[6] gpt-oss Model Card — arXiv:2508.10925 (2025)
[7] Wei et al. — "Chain-of-Thought Prompting Elicits Reasoning in LLMs" — NeurIPS 2022

**Section status:** 🟡 Draft. Needs BibTeX generation + more citations for §2.4 frameworks.
