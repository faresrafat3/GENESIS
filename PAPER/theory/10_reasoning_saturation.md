# Theory-10 — Reasoning Saturation (The Inverted-U of Internal Reasoning)

**Source:** Agent-initiated synthesis of Empirical Discovery #1 + external literature
**Related ideas:** [Idea-001] (LEAP — confirmed domain-asymmetry pattern), [Idea-002] (Attribution Rule)
**Related findings:** Empirical Discovery #1 (reasoning saturation), Empirical Discovery #3 (empty content, 35%)
**External literature (anchored as full thefts after Session 10):**
- **T5.93** — Wu et al. 2025 (arXiv:2502.07266) — formal inverted-U + scaling laws. See `GENESIS_External_Inverted_U_Wu2025_Theft_AR.md`.
- **T5.94** — Chen et al. 2026 (UVA + Google, arXiv:2602.13517) — DTR + Think@n on same model family + GPQA-Diamond. See `GENESIS_External_DTR_ChenMeng2026_Theft_AR.md`.
- Supplementary citations: Chen et al. 2024b (overthinking in o1); Su et al. 2025 (thinking-content compensation, arXiv:2508.17627); OptimalThinkingBench (arXiv:2508.13141); "When More Thinking Hurts" (arXiv:2604.10739).
**Status:** Draft Theory v1.0
**Tag:** `[Theory-10]`

---

## 1. الظاهرة المُلاحظة

في pure baseline run بتاعنا (gpt-oss-120b على GPQA-20):

| Metric | Correct (n=15) | Incorrect (n=5) | Ratio |
|---|---|---|---|
| **Avg reasoning tokens** | 3,001 | 5,104 | **+70%** أعلى للـ incorrect |
| **Median reasoning tokens** | 989 | 6,836 | **+591%** أعلى للـ incorrect |
| **Empty content rate** | 0/15 (0%) | 7/20 إجمالي (35%) | كلها incorrect |
| **finish_reason="length"** | 0/15 | كل الـ 7 empty | reasoning استهلك max_tokens |

**الـ counter-intuitive observation:**
> **النموذج اللي بيفكر أكثر بيخطئ أكثر، مش العكس.**

هذا يخالف الـ prevailing assumption في كل أدبيات test-time compute scaling (Snell et al. 2024; Wei et al. 2022; OpenAI o1 family) اللي تفترض monotonic relationship بين reasoning length و accuracy.

## 2. الفرضية المركزية

نقترح أن الـ reasoning يتبع **inverted U-shape** على محور الـ length:

```
Accuracy
   │
   │           ╱─────╲
   │         ╱         ╲ ← OVERTHINKING REGION
   │       ╱             ╲   (Theory-10)
   │     ╱                 ╲
   │   ╱                     ╲
   │ ╱                         ╲___________
   │
   │  UNDERTHINKING               STEEP DECLINE
   │  REGION                       Confusion + drift
   │
   └──────────────────────────────────────────► Reasoning Length
      Sweet spot
      (~800-3000 tokens
       for GPQA-difficulty)
```

هذه النظرية ليست أصلية بالكامل عندنا — Wu et al. 2025 (arXiv:2502.07266) قدموها صراحة، والـ UVA-Google paper (arXiv:2602.13517) قاسوها على نفس النماذج تقريباً (gpt-oss, DeepSeek-R1, Qwen3) وحصلوا **correlation = -0.54** بين token length و accuracy. مساهمتنا الأصلية هي:

1. **تأكيد مستقل** للظاهرة على gpt-oss-120b على GPQA-20.
2. **ربطها بـ architecture design** (يربط مع Theory-07 و Theory-08).
3. **استنتاج consequences** للـ GENESIS orchestration design.

## 3. الـ Axioms

### Axiom 1 — Error Accumulation (Wu et al. 2025)
كل reasoning step يحمل احتمال خطأ صغير ε. سلسلة من N خطوات تحمل احتمال خطأ تراكمي ≈ 1−(1−ε)^N. عند N كبيرة، الـ accumulated error يطغى على أي gain من الـ decomposition.

### Axiom 2 — Confusion Spiral (مُلاحَظ في run_57)
لما النموذج يقابل سؤال خارج capacity-window بتاعه، الـ extended reasoning يولّد **competing hypotheses متعددة** بدل ما يصل لإجابة واحدة. كل hypothesis تستهلك tokens، والـ model يفقد الـ original anchor.

### Axiom 3 — Token Budget Exhaustion (Empirical Discovery #3)
لما الـ reasoning يستهلك كل max_tokens، الـ `content` يرجع فاضي و `finish_reason="length"`. ده mechanism specific لـ reasoning models (gpt-oss, o-series, DeepSeek-R1, Gemini Thinking) حيث الـ internal reasoning tokens محسوبة من الـ budget بس مش مرئية في الـ output.

### Axiom 4 — Inverse Capability Scaling (Wu et al. 2025)
الـ optimal CoT length **ينقص** مع زيادة model capability. النماذج الأقوى تحتاج reasoning أقصر للوصول للإجابة. هذا هو الـ **simplicity bias** المنشأ تجريبياً.

## 4. الـ Propositions المشتقة

### Prop 1 — Optimal Length is Domain × Capability Dependent
الـ optimal reasoning length دالة لمتغيرين:
- **Task difficulty (T)**: يزيد مع زيادة الصعوبة.
- **Model capability (M)**: ينقص مع زيادة القدرة.

صياغة Wu et al. 2025 الـ closed-form:
$$N_{opt}(M, T) = \frac{T \cdot Z}{M \cdot (Z+1)}, \quad Z = W_{-1}\left(-\frac{1-T/C}{e}\right)$$

حيث $W_{-1}$ هو negative branch of Lambert W function.

**التطبيق على نتائجنا:**
- GPQA-20 (T moderate-to-hard) × gpt-oss-120b (M frontier-grade) → $N_{opt}$ متوسط.
- نتائجنا تتسق: median للـ correct = 989 tokens، median للـ incorrect = 6,836 (تجاوز sweet spot).

### Prop 2 — Hard Questions Both Need More AND Hit Saturation Faster
الأسئلة الصعبة (Chemistry Organic في data بتاعنا) عندها **double bind**:
- تحتاج reasoning أطول (Axiom 1, higher T).
- لكن قدرة النموذج فيها أضعف (lower effective M في هذا الـ domain).

النتيجة: $N_{opt}$ موجود في window ضيق جداً. لو تخطى → confusion spiral.

ده يفسر **directly** ليه Chemistry Organic = 5/6 hard في data بتاعنا.

### Prop 3 — Empty Content is a Symptom, Not a Bug
الـ 35% empty content rate في pure baseline ليس bug في الـ infrastructure. هو **منطقي تحت Axiom 3**: لما النموذج يدخل confusion spiral، يستنفد budget في reasoning بدون ما يصل لـ output. الـ infrastructure fix (`extract_response_text`) فقط يـ rescue الإجابة من الـ reasoning trace.

### Prop 4 — Reasoning Saturation Interacts with Architecture
هذا الـ insight الجديد اللي يخص GENESIS تحديداً (لا يوجد في الأدبيات الخارجية بهذا الشكل):

**عندما الـ architecture تحقن signals في prompt (Theory-07 Type B), النموذج يحتاج reasoning إضافي لـ:**
- (a) parsing الـ injected signals.
- (b) deciding whether to trust أو ignore them.
- (c) reconciling مع internal reasoning.

→ ده يدفع الـ reasoning تجاه الـ overthinking region أسرع.

**التنبؤ:** GENESIS (injection-based) → الـ reasoning saturation يحدث عند tokens أقل مقارنة بـ pure baseline.

**الـ empirical signature المتوقع:**
- pure baseline empty content rate: 35%
- GENESIS (if measured): predicted **>40%** for same questions

(لم نقس هذا بعد — هو prediction للـ Track B.3 في Future Work.)

### Prop 5 — DTR Predicts Better Than Length (UVA-Google 2026)
الـ Deep Thinking Ratio (DTR) — measuring how many tokens involve deep-layer revision — correlates with accuracy at **r=0.683** vs raw length **r=-0.54**.

التطبيق: مش الـ tokens عددها اللي بيفرق، بل **جودة الـ reasoning per token**. هذا يفصل بين:
- "Filler" tokens (شائعة الكلمات، تستقر في shallow layers).
- "Deep thinking" tokens (تتغير في deep layers).

**Hypothesis للـ GENESIS:** الـ injected pipeline signals → الـ النموذج يقضي tokens إضافية في الـ filler-like processing → DTR ينخفض → accuracy ينخفض.

## 5. التوقعات القابلة للاختبار

### P1: max_tokens Sweet Spot Exists for GPQA
لو نختبر max_tokens ∈ {2K, 4K, 8K, 16K, 32K} على gpt-oss-120b على GPQA-20:
- **التوقع:** accuracy ↗ ثم ↘ (inverted U).
- **Sweet spot:** متوقع بين 4K و 8K (بناءً على median correct ≈ 989 لكن مع margin للأسئلة الأصعب).

### P2: Architecture Overhead Shifts the Curve Leftward
لو نشغل GENESIS على نفس max_tokens range:
- **التوقع:** sweet spot ينتقل إلى max_tokens أقل (لأن الـ pipeline signals تستهلك budget).
- **التوقع:** peak accuracy أقل (لأن الـ signal-to-noise ratio أقل).

### P3: Domain-Difficulty Conditions Optimal Length
- Physics (easy in our data) → short reasoning sufficient، sweet spot أقل.
- Chemistry Organic (hard) → longer reasoning needed، sweet spot أعلى، لكن saturation أسرع.

التوقع: per-domain analysis للـ reasoning length distribution يكشف فروق واضحة.

### P4: Capability Scaling Confirms Inverse Relationship
لو نختبر نفس الـ GPQA على نماذج مختلفة:
- gpt-oss-120b (frontier): sweet spot عند ~2-4K tokens.
- Phi-4 (smaller): sweet spot عند ~6-10K tokens.
- LFM-2.5 (1.2B): sweet spot عند ~12K+ tokens (أو لا يصل لأن capacity غير كافية).

هذا يطابق Wu et al. 2025 Axiom 4.

### P5: DTR-Based Early Termination Beats Fixed Budget (Google paper)
لو نقيس DTR للـ first 50 tokens من كل response:
- High-DTR → continue reasoning.
- Low-DTR → terminate early، use partial answer.

التوقع (من Google paper): same/better accuracy + ~50% compute reduction.

### P6: Lifetime Right-Drift Due to Non-Forgetting (NEW — Session 12)

**Source:** Cross-synthesis of `GENESIS_Productive_Forgetting_Theory_AR.md` §17 ("retrieval consumes tokens, attention, latency") with `GENESIS_Cognitive_Economy_Theory_AR.md` §5 Hypothesis 2 (Theory-10's core thesis); discovered Session 12.

**Prediction (falsifiable):**

> Systems that operate without an explicit productive-forgetting policy will systematically drift **right-of-optimum** on the reasoning-length axis over their lifetime, because non-forgotten context monotonically grows even when no individual task increases its length budget.

**Why this is novel relative to T5.93 and T5.94:**

- Wu et al. 2025 (T5.93) study *within-task* length-vs-accuracy. The inverted-U is measured per-question.
- Chen et al. 2026 (T5.94) study *within-response* deep-vs-long thinking via DTR. Also per-question.
- **Neither addresses across-task lifetime drift.** P6 predicts that even a system with locally-optimal per-question length will drift right-of-optimum if it accumulates retrieved context (memory, prior episodes, prior verifier judgments) without abstraction forgetting (per Productive Forgetting Theory §3.4 / §9).

**Operationalizable test:**

1. Fix a model + benchmark + per-question max_tokens.
2. Variant A (Control): no memory; each question is independent.
3. Variant B: memory accumulates raw episodes across questions (no forgetting).
4. Variant C: memory accumulates but with abstraction forgetting (episodes → concepts; episodes quieted once absorbed).
5. **Prediction P6:** Variant B's effective per-question reasoning length grows over time and its accuracy degrades on later questions, even though Variant A and C stay flat.

If P6 holds, it identifies a *third* mechanism of saturation (lifetime drift) distinct from the two studied in the literature (per-task length excess and per-response length-vs-depth confusion). This would be a genuine novel claim attributable to the GENESIS project (with Fares as conceptual originator via Productive Forgetting Theory + Cognitive Economy Theory; agent as cross-synthesis formalizer in Session 12).

**Status:** Prediction stated. Not yet tested. Listed in Future Work for execution if/when the project resumes operational runs.

## 6. الـ Empirical Checks الموجودة

| Check | المصدر | يدعم Theory-10؟ |
|---|---|---|
| Median tokens (correct vs incorrect): 989 vs 6,836 | run_57 pure baseline (ours) | ✅ نعم — saturation signature واضح |
| 35% empty content rate | run_57 (ours) | ✅ نعم — Prop 3 |
| Correlation length-vs-accuracy = -0.54 | UVA-Google (arXiv:2602.13517) | ✅ نعم — على نفس نماذجنا |
| Inverted U formal proof | Wu et al. 2025 (arXiv:2502.07266) | ✅ نعم — theoretical backing |
| Overthinking in o1 models | Chen et al. 2024b | ✅ نعم — consistent across model families |
| Thinking-content compensation → saturation | Su et al. 2025 (arXiv:2508.17627) | ✅ نعم — mechanism هو نفسه |
| OptimalThinkingBench (over/under-thinking) | arXiv:2508.13141 | ✅ نعم — confirms operational gap |

**الـ external evidence base قوية بشكل غير عادي.** هذا الـ theory هو الأكثر تأييداً تجريبياً من external sources بين كل theories بتاعتنا.

## 7. الـ Empirical Checks اللي تنقص (للمستقبل، Track B)

| Check | كيف نختبره | الأولوية |
|---|---|---|
| P1: GPQA sweet spot curve | max_tokens sweep | high (controlled, single run × 5 budgets) |
| P2: Architecture-induced shift | GENESIS sweep vs pure sweep | high (دليل مباشر لـ Theory-07 ↔ Theory-10 interaction) |
| P3: Per-domain optimal length | per-question analysis on existing run_57 logs | **low cost, can do now** ✅ |
| P4: Cross-model capability scaling | Phi-4 + LFM-2.5 baselines | medium |
| P5: DTR-based termination | requires deep-layer hidden states (only some providers expose) | low (infrastructure-heavy) |

## 8. الـ Implications على GENESIS

### Direct Implications
1. **max_tokens=16384 قد يكون too high** للـ gpt-oss-120b على GPQA. الـ sweet spot قد يكون 4K-8K.
2. **GENESIS injection-based design** يدفع للـ saturation أسرع (Prop 4) — يربط مباشرة مع Theory-07.
3. **Chemistry Organic gap** عندنا له تفسير double: domain-difficulty (Axiom 4) + saturation (Theory-10).

### Architectural Implications
1. **DTR-style termination** يمكن إضافته كـ component جديد في GENESIS (مرشح لـ Track A.5).
2. **Adaptive max_tokens** based on detected task difficulty (يربط مع tier_decision pipeline).
3. **Reasoning-length-aware verifier** كـ Layer جديد في Theory-08's verification stack.

### Paper-Level Implications
1. الـ counter-intuitive finding بتاعنا (Empirical Discovery #1) بقى **له نظرية كاملة + 6 external papers تدعمها**.
2. الـ paper يضيف **theoretical contribution مستقل عن GENESIS**: ربط overthinking literature بـ orchestration design.
3. الـ Conclusion يصبح أقوى: مش بس "scaffolding fixes + LEAP integration"، لكن "reasoning saturation + architecture design interact in specifiable ways".

## 9. الروابط بالنظريات الأخرى

### نظريات داخلية
- **Theory-07 (Pipeline as Memory vs Injection):** Theory-10 يفسر **لماذا** injection يضر بشكل أعمق — يدفع للـ saturation. Prop 4 هو ربط نظري مباشر.
- **Theory-08 (Feedback Value):** Feedback drift في Gen 2 (run_58: 70→60) قد يكون **partial result للـ saturation** — الـ feedback agent نفسه يدخل overthinking spiral.
- **Theory-09 (Anticipatory Concepts):** Anticipatory abstraction يقلل reasoning length per task (lemmas pre-computed). يربط بـ Wu et al. simplicity bias.
- **Cognitive Economy Theory (internal):** Theory-10 يعطي صيغة كمية لـ "cost of thinking" — مباشر لـ economy ledger.
- **Tiered Intelligence (internal):** Tier decision يصبح "أي reasoning budget مناسب؟" بدل "أي pipeline path؟".

### نظريات خارجية / مراجع
- **Wu et al. 2025 (arXiv:2502.07266):** الـ primary theoretical anchor. Inverted U + scaling laws.
- **UVA-Google DTR (arXiv:2602.13517):** Empirical confirmation على نفس نماذجنا. DTR > length كـ predictor.
- **Chen et al. 2024b:** First documentation of overthinking in o1.
- **Su et al. 2025 (arXiv:2508.17627):** Thinking-content compensation mechanism.
- **arXiv:2508.13141 (OptimalThinkingBench):** Operational benchmark for over/underthinking.
- **arXiv:2604.10739 ("When More Thinking Hurts"):** Flip event tracking + cost-aware evaluation.
- **Reconsidering Overthinking (arXiv:2508.02178):** Distinction between internal vs external redundancy.

## 10. الـ Connections بـ السرقات الشرعية (potential new thefts)

من الأدبيات الجديدة دي، عندنا **مرشحين قويين للسرقة الشرعية:**

### T5.93 المرشح: Wu et al. 2025 — Inverted U + CoT Calibration
- **ما نأخذه:** الـ scaling laws الـ formal + length-aware filtering مفهوم + RL-based calibration insight.
- **ما نتركه:** الـ specific RL training setup (نحن orchestration، مش fine-tuning).
- **ما يصبح عندنا:** صيغة كمية لـ "متى نوقف الـ reasoning؟" داخل GENESIS pipeline.

### T5.94 المرشح: UVA-Google DTR — Deep Thinking Ratio
- **ما نأخذه:** الـ concept of distinguishing deep vs surface tokens + Think@n strategy.
- **ما نتركه:** الـ requirement للـ hidden state access (mostly impractical via API).
- **ما يصبح عندنا:** proxy DTR using only API-accessible signals (e.g., token-level perplexity, semantic similarity).

(تسجيل T5.93/T5.94 يستحق session منفصل، attribution: agent-initiated — لا تأتي من فكرة فارس مباشرة، بل من البحث الأدبي اللي أجريته كاستجابة لـ Theory-10 task.)

## 11. الروابط بأقسام الورقة

- **Abstract:** Theory-10 يُذكر كأحد internal theories (تصبح 4 بدلاً من 3).
- **Section 7.3 (Reasoning Saturation Hypothesis):** القسم الحالي placeholder — Theory-10 يحوله إلى نظرية كاملة.
- **Section 8.5 (Contrast with LEAP):** Theory-10 يدخل كـ 8.5.X جديد، يربط مع Theory-07 (Prop 4).
- **Section 10 (Future Work):** P1, P2, P3 ينضموا لـ Track B (Empirical Anchoring).
- **Section 11 (Conclusion):** يُذكر كـ بُعد رابع للـ paper contributions.
- **Appendix C:** Theory-10 يضاف للجدول.

## 12. Citation

```
Theory-10 — Reasoning Saturation (The Inverted-U of Internal Reasoning).
Internal theory developed in PAPER/theory/10_*.md (Session 9, agent-initiated).
External anchors: Wu et al. 2025; UVA-Google DTR 2026; Chen et al. 2024b;
Su et al. 2025; OptimalThinkingBench 2025; "When More Thinking Hurts" 2026.
Empirical anchor: GENESIS run_57 pure baseline (median 989 vs 6,836 reasoning tokens
for correct vs incorrect; 35% empty content rate; finish_reason=length on all empties).
```

## 13. Attribution Note

هذا الـ theory **agent-initiated** — لم تأتي من فكرة محددة من فارس. الـ context هو:
- Session 9 بدأت بـ "القرار قرارك" من فارس.
- اختار الـ agent (أنا) أن يكتب Theory-10 لأنها كانت آخر Empirical Discovery كبيرة بدون نظرية.
- الـ Idea-002 (Creative Attribution Rule) يطلب صراحة تتبع المصدر. مصدر Theory-10 هو **agent-initiated synthesis** of:
  - Our own Empirical Discovery #1 (Session 2-3 measurements).
  - External literature search (this session).

هذا التمييز مهم للورقة النهائية: الـ Acknowledgments ستذكر صراحة أن Theory-07/08/09 + Phil-07 جاءوا من Idea-001 (Fares), بينما Theory-10 + theft candidates T5.93/T5.94 جاءوا من agent-initiated work building on existing empirical anchors.

## 14. Status

- ✅ Drafted (Session 9, agent-initiated).
- ⏳ Pending Fares review.
- ⏳ Pending integration into PAPER.md Section 7.3 (expansion from placeholder to full theory).
- ⏳ Pending decision on T5.93/T5.94 theft memos.
- ⏳ Pending ATTRIBUTION_MAP update for agent-initiated content.
