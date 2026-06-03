# Virtual-GENESIS Task Framing Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تأتي استجابة مباشرة لاكتشاف Prototype v4:

> **Task Framing / Family Assignment أصبحت bottleneck بنيوية**

فقد ظهر أن كثيرًا من المهام الحدودية لا تقع cleanly داخل:
- comparison
- synthesis
- procedure

بل تحمل إشارات متداخلة.

لذلك لم يعد كافيًا أن نعامل `task_family` كـ label واحدة صلبة.

هذه الوثيقة تهدف إلى تحديد:
1. ما المقصود بـ Task Framing؟
2. ما الفرق بين framing وclassification؟
3. ما الـ objects اللازمة؟
4. كيف يجب أن يتعامل النظام مع ambiguity؟
5. كيف ترتبط task framing بالـ memory والـ concepts والـ routing؟
6. ما minimal implementation path؟

---

# 1) التعريف المركزي
## Task Framing
Task Framing هو العملية التي يحوّل بها النظام الإدخال الخام إلى:
- تمثيل تشغيلي للمشكلة
- hypotheses عن نوعها
- توقعات عن شكل الحل المناسب
- إشارات إلى المهارات والـ verifiers والـ topologies ذات الصلة

### الصياغة المختصرة
Task Framing =
**operational problem representation under uncertainty**

---

# 2) لماذا framing أعمق من classification؟
## Classification التقليدية
تجيب عن:
- أي label تنطبق؟

## Task Framing
تجيب عن:
- ما نوع المشكلة؟
- ما الأبعاد المختلطة فيها؟
- ما طريقة التفكير الأنسب؟
- ما المخاطر إذا عاملناها كـ family واحدة؟
- ما uncertainty in problem representation نفسها؟

إذًا:

> classification هي ناتج فرعي من task framing، وليست task framing كلها.

---

# 3) المشكلة التي كشفها Prototype v4
في boundary stress slice، ظهرت مهام مثل:
- comparison + synthesis
- comparison + procedure
- synthesis + procedure
- comparison + synthesis + procedure

والنتيجة كانت:
- match rate منخفضة نسبيًا
- ambiguity rate مرتفعة

هذا يكشف أن:
1. family labels ليست mutually exclusive دائمًا
2. routing المعتمد على single family قد يكون fragile
3. concept activation قد تُفقد إذا أُسقطت المهمة في family واحدة خاطئة
4. evaluation نفسها قد تُشوّه إذا استخدمت expected family ساذجة

---

# 4) الفرضيات الأساسية للنظرية/الـ spec
### Hypothesis 1
كثير من مهام العالم الحقيقي ليست أحادية العائلة، بل **composite tasks**.

### Hypothesis 2
التمثيل الأفضل للمهمة في المراحل المبكرة هو:
- ranked frame candidates
أو
- multi-label representation
وليس single hard label فقط.

### Hypothesis 3
جزء معتبر من فشل الـ agent قد يكون **framing failure** لا reasoning failure.

### Hypothesis 4
تحسين task framing سيؤثر في:
- retrieval quality
- concept activation
- verifier choice
- tier routing
- cost discipline

### Hypothesis 5
task framing itself should be revisable during the task, not frozen forever at ingress.

---

# 5) ما هو Frame؟
نقترح أن الـ frame ليست مجرد اسم family، بل object فيه:

1. `family_label`
2. `confidence / score`
3. `why this frame fits`
4. `expected solution style`
5. `expected evidence style`
6. `expected failure modes`
7. `recommended topology`
8. `recommended verifier emphasis`

### مثال
Frame: `comparison`
- why: task asks to distinguish between alternatives
- solution style: contrastive judgment
- evidence style: comparative support
- likely failure mode: unsupported preference
- topology hint: linear or argument-based comparison

Frame: `procedure`
- why: task asks for stable structured output
- solution style: field extraction and reformatting
- evidence style: exact field grounding
- likely failure mode: formatting drift
- topology hint: procedural template

---

# 6) Task Framing Object
نقترح object جديدة:

## TaskFrameCandidate
### fields
- `frame_id`
- `task_ref`
- `family_label`
- `score`
- `rationale`
- `expected_solution_style`
- `expected_evidence_style`
- `recommended_topology`
- `recommended_verifier_bias`
- `known_risks`
- `status` (candidate / active / demoted / merged)

## TaskFramingState
### fields
- `task_ref`
- `frame_candidates: list[TaskFrameCandidate]`
- `primary_frame: str | None`
- `secondary_frames: list[str]`
- `ambiguity_score`
- `framing_conflicts`
- `framing_revision_history`

---

# 7) single-label vs multi-label vs ranked frames
نقترح عدم الالتزام دائمًا بتمثيل واحد.

## Mode A — Single-label framing
مناسب عندما:
- one family dominates clearly
- ambiguity منخفضة

## Mode B — Multi-label framing
مناسب عندما:
- أكثر من family لها signals مهمة
- task clearly composite

## Mode C — Ranked frame candidates
مناسب عندما:
- ambiguity متوسطة
- نريد أن نختار primary frame لكن نحتفظ بالبدائل

### توصية prototype الحالية
في المدى القريب:
# **Ranked frame candidates + primary frame**
أفضل من single hard label فقط.

---

# 8) Framing lifecycle
1. `initial_frame_candidates`
2. `primary_frame_selected`
3. `frame_contested`
4. `frame_revised`
5. `frame_stabilized`
6. `frame_split` (if task decomposes into subframes)

### مهم
task framing ليست ثابتة بالضرورة؛
يمكن أن تبدأ comparison، ثم يظهر أثناء التحقق أنها synthesis-procedure hybrid.

---

# 9) كيف تُولد frame candidates؟
نقترح أربع قنوات:

## Channel 1 — lexical / surface cues
keyword/signal based

## Channel 2 — structural cues
هل المطلوب:
- choose between alternatives?
- merge evidence?
- format output?

## Channel 3 — memory cues
هل لدينا concepts/skills strongly associated مع family معينة؟

## Channel 4 — verification cues (later-stage)
إذا verifier failures تشير إلى mismatch مع framing الحالية

---

# 10) ما الذي يجب أن تفعله framing layer downstream؟
Task framing ليست decorative metadata.
يجب أن تؤثر فعليًا على:

## 10.1 Memory retrieval
- comparison frame → retrieve contrastive memories
- synthesis frame → retrieve grounding/evidence integration concepts
- procedure frame → retrieve procedural skills/templates

## 10.2 Concept activation
frame candidates تحدد أي concepts تُعطى أولوية.

## 10.3 Tier routing
high ambiguity in framing itself قد يبرر:
- higher tier
- more verification
- or delayed commitment

## 10.4 Verification emphasis
- comparison → argument adequacy
- synthesis → evidence coverage
- procedure → format/field integrity

## 10.5 Reasoning topology
- comparison → contrastive/argument mode
- synthesis → graph/merge-oriented mode
- procedure → procedural template mode

---

# 11) framing ambiguity as first-class signal
نقترح:

## ambiguity_score
ليس مجرد side note، بل signal تدخل في economy and routing.

### effects of high ambiguity_score
1. avoid overcommitting to one family early
2. retrieve cross-family memory candidates
3. increase verification weight
4. possibly use more structured reasoning
5. allow frame revision mid-task

---

# 12) Frame revision
### لماذا revision مهمة؟
لأن task may reveal its true nature only after:
- memory retrieval
- failed verification
- contradiction signal
- first draft answer

### triggers for revision
- verifier mismatch with current frame
- repeated failure signatures associated with another frame
- concept hints from another family dominate
- answer format repeatedly wrong despite content correctness

### revision actions
- re-rank frame candidates
- activate secondary frame
- merge two frames into composite interpretation
- switch primary frame

---

# 13) Composite frames
نقترح أن بعض المهام تُعامل صراحة كـ composites.

### examples
- `comparison+procedure`
- `synthesis+procedure`
- `comparison+synthesis`
- `comparison+synthesis+procedure`

### لماذا هذا مفيد؟
لأن بعض المهام لا ينبغي إجبارها على family واحدة.

### لكن
لا نريد انفجار combinatorial كامل.
لذلك في prototype near-term يمكننا:
- تسجيل composite possibility
- لكن نختار primary + secondary frame فقط

---

# 14) علاقة Task Framing بـ Thesis 1
إذا كانت framing سيئة، فإن:
- concepts الصحيحة قد لا تُفعل
- retrieval ستسحب artefacts غلط
- verification قد تقيس dimension خاطئ

إذًا task framing bottleneck قد تُخفي أو تُضعف قيمة concept formation.

### نتيجة مهمة
قبل أن نحكم على حدود Thesis 1، يجب أن نعالج task framing بما يكفي.

---

# 15) علاقة Task Framing بـ Thesis 2
framing ambiguity تؤثر على:
- escalation
- verification spend
- topology choice
- premium necessity

إذا فُهمت المهمة بطريقة خاطئة، قد نصرف cognition في الاتجاه الخاطئ.

إذًا:

> بعض failures of cognitive economy هي في الحقيقة failures of task framing.

---

# 16) Failure modes في Task Framing
## Failure Mode 1 — Hard label collapse
إجبار المهمة على family واحدة رغم التداخل الواضح.

## Failure Mode 2 — Keyword overfitting
الاعتماد الزائد على surface cues.

## Failure Mode 3 — Frame inertia
التمسك بالـ frame الأولى رغم evidence لاحقة ضدها.

## Failure Mode 4 — Frame explosion
توليد frames كثيرة بلا ranking أو governance.

## Failure Mode 5 — Hidden ambiguity
وجود ambiguity عالية لكن النظام لا يسجلها.

## Failure Mode 6 — Downstream blindness
framing موجودة لكن لا تؤثر على retrieval/routing/verification.

---

# 17) اختبارات Task Framing layer
## Test A — Match rate
مدى مطابقة التوقع البشري/المرجعي للفريم الأساسي

## Test B — Ambiguity sensitivity
هل النظام يلتقط التداخل بدل تجاهله؟

## Test C — Downstream utility
هل استخدام framing يحسن retrieval/routing/verification؟

## Test D — Revision quality
هل يعدل framing عندما تظهر إشارات قوية؟

## Test E — Composite robustness
هل يتعامل جيدًا مع overlap tasks؟

---

# 18) Minimal implementation path
لأننا ما زلنا في prototype، نوصي بالخطوات التالية:

## Step 1
تحويل classifier من single-label heuristic إلى:
- `family_scores`
- `ambiguity_score`
- `primary_frame`
- `secondary_frames`

## Step 2
تمرير framing info إلى blackboard بوضوح

## Step 3
جعل memory retrieval تقرأ primary/secondary frames

## Step 4
جعل verification تستفيد من framing signals

## Step 5
إضافة `framing_report` إلى evaluation outputs

---

# 19) ما الذي لا نفعله الآن؟
- لا نبني learned classifier معقد الآن
- لا ندخل full theory-based framing revision loop
- لا نبني compositional ontology ضخمة جدًا الآن

### لماذا؟
لأن هدفنا الحالي هو:
- إزالة bottleneck
- لا بناء subsystem عملاقة جديدة

---

# 20) القرار العملي الحالي
هذه الوثيقة تقول بوضوح:

> **Task Framing أصبحت الآن أولوية تنفيذية أعلى من التوسع إلى contradiction/anomaly runtime layers**

لأنها bottleneck upstream تؤثر على كل شيء downstream.

### وبالتالي الخطوة التالية المنطقية هي:
1. تحسين task framing representation في runtime
2. إعادة تشغيل boundary slices
3. فقط بعدها نقرر هل governance layers التالية تستحق الدخول أم لا

وهذا يحافظ على المشروع في مسار disciplined بدل التشتت.
