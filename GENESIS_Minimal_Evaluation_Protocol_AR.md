# Virtual-GENESIS Minimal Evaluation Protocol (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تحدد **أقل بروتوكول تقييم جاد** يمكن أن نستخدمه لاختبار الفرضيتين المركزيتين للمشروع دون الوقوع في:
- benchmark chasing
- أو evaluation inflation
- أو بناء framework ضخمة قبل وجود evidence أولي

الهدف هو بناء:

> **Evaluation protocol صغير لكن كافٍ لإنتاج أول evidence محترمة**

للفرضيتين:

## Thesis 1
**Concept Formation beats retrieval-only adaptation**

## Thesis 2
**Cognitive Economy beats stronger-model-only scaling**

---

# 1) فلسفة البروتوكول
هذا البروتوكول ليس benchmark نهائية للمشروع كله.
بل هو:
- **minimal**: أقل ما يمكن لبناء evidence
- **falsifiable**: يمكن أن يفشل ويُضعف الفرضية
- **comparative**: يعتمد على baselines صريحة
- **budget-aware**: لا يفترض compute ضخمة
- **artifact-aware**: لا يقيس accuracy فقط، بل يقيس quality of epistemic artifacts

---

# 2) أسئلة التقييم الأساسية

## Q1 — Thesis 1
هل نظامًا يكوّن Concepts ويستخدمها في retrieval/routing/skill activation يتفوق على نظام retrieval-only؟

## Q2 — Thesis 2
هل نظامًا يخصص cognition بعقلانية (routing/escalation/verification/search depth) يتفوق على نظام fixed policy أو premium-always policy من حيث **quality/cost frontier**؟

## Q3 — Cross-cutting
هل التحسين، إن وجد، يأتي من artefact-level growth فعلاً، أم فقط من استخدام model أقوى أو prompts أطول؟

---

# 3) وحدات التقييم الأساسية
نقترح ثلاث وحدات تقييم فقط في البداية، لتبقى التجربة manageable:

## Unit A — Recurrent Analytical Tasks
مهام يتكرر فيها pattern أو family لكن تختلف التفاصيل:
- مقارنة بين وثيقتين/فكرتين
- تشخيص failure mode بسيط
- synthesis ذات evidence متناثرة نسبيًا

## Unit B — Procedural / Skill Reuse Tasks
مهام فيها workflows متكررة:
- structured extraction with verification
- إصلاح تنسيق/تحويل/فرز
- coding micro-workflows

## Unit C — Boundary / Transfer Tasks
حالات قريبة من مهام Unit A/B لكنها تتطلب:
- slight abstraction shift
- different wording
- different evidence arrangement
- changed scope assumptions

### rationale
- Unit A تخدم concept formation
- Unit B تخدم skill/procedure reuse
- Unit C تخدم transfer and overfitting detection

---

# 4) حجم المجموعة الأولية
### Minimal dataset size
نقترح كبداية:
- **40 task** في Unit A
- **30 task** في Unit B
- **30 task** في Unit C

إجمالي = **100 task**

### التوزيع
- 60 task للتطوير والتحليل الداخلي
- 20 task validation
- 20 task holdout

### القاعدة
الـ holdout يجب ألا تُستخدم لصناعة concepts أو tuning مباشر.

---

# 5) الشروط التجريبية الأساسية
نحتاج على الأقل أربع conditions:

## Condition 0 — Fixed Baseline
- retrieval بسيط
- prompt ثابت
- tier ثابت أو policy بسيطة
- no concept formation
- no economy-aware routing

## Condition 1 — Retrieval+Memory Baseline
- Memory OS retrieval
- no concept formation
- no economy-aware routing

## Condition 2 — Concept Condition
- Memory OS + Concept Formation Engine
- لكن routing ثابتة نسبيًا
- الهدف: isolate Thesis 1

## Condition 3 — Economy Condition
- Memory OS + economy-aware routing/escalation
- no concept activation or only minimal
- الهدف: isolate Thesis 2

## Condition 4 — Combined Condition
- Memory OS + Concept Formation + Economy-aware routing
- الهدف: معرفة هل هناك additive gains أو interactions

---

# 6) اختبارات Thesis 1 بالتحديد
## المقارنة الأساسية
Condition 2 vs Condition 1

### القياس المطلوب
1. هل concepts تُستخدم فعلًا؟
2. هل تقل الحاجة إلى raw episodic retrieval؟
3. هل تتحسن decisions أو transfer؟
4. هل concepts تقلل repeated failure loops؟

### مؤشرات النجاح
- higher transfer accuracy on Unit C
- lower raw-case retrieval count per solved task
- improved task success on recurrent families
- evidence أن concepts أثرت على skill/policy selection

### مؤشرات الفشل
- concepts generated but never used
- no gain over retrieval-only
- gains only in memorized/repeated tasks without transfer
- concept proliferation دون utility

---

# 7) اختبارات Thesis 2 بالتحديد
## المقارنة الأساسية
Condition 3 vs Condition 0 and vs premium-always control

### نضيف condition خاصة
## Condition 5 — Premium-Always
- دائمًا escalate to strongest available model path for main reasoning
- minimal economy logic

### القياس المطلوب
1. cost per successful task
2. premium call frequency
3. committee usage frequency
4. quality/cost frontier
5. reusable artifact yield per premium call

### مؤشرات النجاح
- same or better quality than fixed baseline at lower cost
- close quality to premium-always with much better cost profile
- premium reasoning producing reusable artefacts لاحقًا تقلل التكلفة

### مؤشرات الفشل
- economy-aware policy underthinks وتنهار الجودة
- أو overspends بلا عائد
- أو لا تتفوق على policy ثابتة بسيطة

---

# 8) المقاييس الأساسية
نقسم metrics إلى أربع عائلات:

## 8.1 Performance Metrics
- task success rate
- correctness / verifier pass rate
- groundedness / evidence sufficiency
- format validity

## 8.2 Economic Metrics
- total tokens
- latency
- premium token share
- cost per successful task
- committee invocation rate

## 8.3 Epistemic Metrics
- concept usage rate
- concept reuse rate
- concept transfer score
- artifact yield (lessons/skills/concepts/theory notes)

## 8.4 Developmental Metrics
- repeated failure reduction over time
- raw episodic retrieval decline
- increase in higher-order artifact retrieval
- premium ROI over successive batches

---

# 9) Artifact-centric metrics
هذه metrics مهمة جدًا لأنها ما يثبت أن gains ليست superficial فقط.

## 9.1 Concept Yield
عدد concept candidates التي تم اقتراحها ÷ عدد tasks الغنية بالأنماط

## 9.2 Concept Activation Rate
عدد tasks التي استُخدمت فيها concepts فعلاً ÷ عدد tasks التي كانت concepts متاحة لها

## 9.3 Concept Utility Rate
عدد activations التي حسّنت outcome أو decision ÷ إجمالي activations

## 9.4 Raw Retrieval Compression Ratio
متوسط عدد episodic items قبل وبعد concept usage

## 9.5 Premium Reuse Ratio
عدد premium-invoked tasks التي أنتجت artefact reusable ÷ إجمالي premium-invoked tasks

## 9.6 Learning Investment Return
عدد tasks المستقبلية التي استفادت من artefact جديد ÷ عدد artefacts المنتجة

---

# 10) Event logging requirements
كل run يجب أن ينتج traces كافية، وإلا لن يمكن تفسير النتائج.

## required logs
- task_id
- condition_id
- retrieved memory types and counts
- concept candidates proposed
- concepts activated
- tier decisions
- escalation triggers
- verification outcomes
- contradictions detected
- final outcome
- token/cost/latency stats
- learning artifacts produced

---

# 11) مفهوم الحزمة الزمنية Evaluation in Batches
لأن بعض الفرضيات developmental، نحتاج التقييم على batches.

## Proposed batches
- Batch 1: cold start
- Batch 2: after first memory accumulation
- Batch 3: after concept formation cycle
- Batch 4: after economy policy adjustments

### لماذا؟
لأن نجاحنا ليس static فقط، بل يجب أن يظهر:
- change in slope
- not just one-shot score

---

# 12) وحدة التحليل الأساسية
نقترح أن تكون وحدة التحليل ليست task فقط، بل ثلاثة مستويات:

## Level 1 — Per task
هل نجحت المهمة؟ وكم كلفت؟

## Level 2 — Per task family
هل تحسننا في نوع مشاكل معيّن؟

## Level 3 — Per development batch
هل البنية تنتج تراكمًا حقيقيًا؟

---

# 13) الاختبارات الكيفية الضرورية
إلى جانب المقاييس الرقمية، نحتاج تحليلًا كيفيًا للحالات التالية:

## Case Type A
task solved due to concept activation

## Case Type B
task overspent due to poor economy decision

## Case Type C
concept proposed but should have remained heuristic

## Case Type D
premium reasoning produced reusable artifact later reused

## Case Type E
retrieval-only failed but concept-aware succeeded on transfer task

هذه الcases ليست optional؛ هي مطلوبة لتفسير الآلية.

---

# 14) ضوابط ضد الـ confounds
حتى لا نخدع أنفسنا، نحتاج controls واضحة:

## Control 1 — Same base model family where possible
عند اختبار Thesis 1، لا نخلط gain from concept formation مع gain from switching to stronger model.

## Control 2 — Fixed budget runs
بعض runs يجب أن تكون تحت budget موحدة لتقييم economy logic بعدل.

## Control 3 — Holdout tasks
concepts لا تُستخرج من holdout مباشرة.

## Control 4 — Frozen prompts where needed
عند مقارنة retrieval-only vs concept-aware، نثبت prompt scaffold الأساسي قدر الإمكان.

## Control 5 — Artifact existence is not enough
لا نعتبر concept أو skill نجاحًا إلا إذا استُخدمت وأثرت.

---

# 15) بروتوكول judgment النهائي لكل thesis

## Thesis 1 judgment
### Positive evidence if:
- Condition 2 > Condition 1 on transfer or recurrent-family stability
- with reduced dependence on raw episodic retrieval
- and concepts show real activation/use

### Negative evidence if:
- concepts produced but not operationalized
- no transfer gain
- retrieval-only matches or beats concept-aware with equal budget

---

## Thesis 2 judgment
### Positive evidence if:
- Condition 3 improves cost-quality frontier vs Condition 0
- and approaches Condition 5 quality with lower cost
- and premium calls yield reusable artifacts

### Negative evidence if:
- economy-aware policy performs worse or only matches fixed baselines with added complexity
- or premium-on-demand behaves like premium-always in cost

---

# 16) Minimum publishable evidence
إذا أردنا future paper أو memo محترمة، فالحد الأدنى البرهاني الذي نحتاجه هو:

1. One controlled comparison for Thesis 1
2. One controlled comparison for Thesis 2
3. Artifact-level evidence
4. At least some holdout transfer analysis
5. At least 3–5 detailed qualitative case studies

---

# 17) Outputs of the protocol
كل evaluation cycle يجب أن ينتج:

1. summary table by condition
2. family-wise analysis
3. cost-quality plots
4. concept utility report
5. premium ROI report
6. failure analysis notes
7. recommendations for next refinement cycle

---

# 18) القرار التالي بعد هذه الوثيقة
بعد Minimal Evaluation Protocol، نكون جاهزين منطقيًا لواحد من مسارين:

## المسار A
بدء formal specs governance التالية:
- Contradiction Ledger Spec
- Anomaly/Crisis Manager Spec
- Local Theory Builder Spec

## المسار B
البدء في prototype architecture slice
لبناء أصغر نسخة قابلة للاختبار من:
- Memory OS
- Concept Formation
- Economy-aware routing
- Logging / evaluation

### رأيي الحالي
قبل مزيد من specs governance، أصبح من المناسب جدًا تجهيز:
# **Prototype Slice Plan**
لأننا وصلنا لحد formalization كافٍ لاختيار minimal build path.
