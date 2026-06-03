# Virtual-GENESIS Verifier Redesign Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تأتي مباشرة بعد:
- اكتشاف coupling بين generation وevaluation
- وصياغة TaskCase Schema

الهدف هو إعادة تصميم الـ verifier بحيث:
1. لا تعتمد فقط على lexical markers سطحية
2. تستفيد من TaskCase hidden contract
3. تظل discriminative enough لتمييز conditions
4. لا تصبح permissive أكثر من اللازم تحت ambiguity
5. تدعم thesis evaluation بدل أن تطمسها

---

# 1) المشكلة الحالية
الـ verifier الحالية في النسخة الأولية تعتمد في جوهرها على:
- family-specific textual markers
- simple schema presence
- shallow evidence cues

هذا نفع في البدايات، لكنه مع تحسن reasoning runtime أدى إلى:
- رفع success baselines بطريقة قد تخفي الفروق
- ضعف discriminative power
- صعوبة التفريق بين genuine improvement وsurface compliance

إذًا المشكلة لم تعد في “هل يوجد verifier؟” بل في:

> **ما الذي تقيسه verifier؟ وكيف؟**

---

# 2) التعريف المركزي
## Verifier
الـ verifier ليست مجرد function تُرجع pass/fail.
بل هي:

> **نظام حكم منظّم يطبّق hidden evaluation contract على output النظام، مع حساسية كافية للتمييز بين success الحقيقية وsuccess السطحية.**

### الصياغة المختصرة
Verifier =
**contract-based, discriminative, artifact-aware evaluation layer**

---

# 3) المبادئ التصميمية الكبرى

## Principle 1 — Separate visible prompt from hidden evaluation contract
ما يراه الـ agent لا يجب أن يكون كافيًا وحده لمعرفة exactly كيف ينجح verifier.

## Principle 2 — Verify properties, not just markers
وجود كلمات معينة لا يعني تحقق الخاصية المطلوبة.

## Principle 3 — Use framing as guidance, not as a loophole
framing candidates تساعد الـ verifier على فهم المطلوب، لكنها لا يجب أن تخفف المعيار لدرجة إخفاء الفروق.

## Principle 4 — Distinguish positive evidence from anti-shortcut violations
النجاح الحقيقي ليس فقط presence of good signals، بل أيضًا absence of fake shortcuts.

## Principle 5 — Verifier must remain comparable across conditions
إذا تغير سلوك verifier بحيث تُسهل النجاح لكل المسارات، ضاع معنى التقييم.

---

# 4) Verifier architecture المقترحة
نقترح أن verifier تتكون من خمس طبقات:

## Layer 1 — Schema / Structural Checks
هل output في الشكل المتوقع؟

## Layer 2 — Required Property Checks
هل output يحقق الخصائص المطلوبة في TaskCase؟

## Layer 3 — Forbidden Shortcut Checks
هل النجاح الحالي superficial أو shortcut-based؟

## Layer 4 — Framing-Aware Weighting
ما وزن كل check given primary/secondary frames؟

## Layer 5 — Final Scoring / Pass Logic
كيف نجمع النتائج؟

---

# 5) ما الذي تقرأه الـ Verifier؟
الـ verifier الجديدة يجب أن تستقبل على الأقل:

1. `TaskCase`
2. `TaskObject`
3. `BlackboardObject`
4. `candidate_output`
5. `framing_state`
6. optionally `tier_decision` or `reasoning_metadata`

### لماذا؟
- TaskCase تعطي hidden contract
- Blackboard تعطي state context
- framing_state توضح overlap/ambiguity
- output وحدها لا تكفي

---

# 6) Verification contract object
نقترح object صريحة:

## VerificationResult
### fields
- `verification_id`
- `task_case_ref`
- `output_ref or output_text`
- `schema_checks`
- `property_checks`
- `shortcut_checks`
- `framing_considerations`
- `score_components`
- `final_score`
- `pass_decision`
- `notes`

### لكل subcheck
يمكن أن يحتوي:
- `name`
- `passed`
- `weight`
- `evidence`
- `failure_reason`

---

# 7) Required Property Checks
بدل marker matching فقط، نحتاج checks من نوع:

## Property types
### A — Evidence Grounding
هل الادعاء المركزي مدعوم explicitly؟

### B — Contrast Presence
في tasks comparison: هل الفرق مُصاغ بوضوح؟

### C — Structure Preservation
في tasks procedure: هل output قابلة للاستعمال كـ checklist/field layout؟

### D — Fact vs Inference Separation
في بعض synthesis tasks: هل هناك تمييز ضمني/صريح بين observed and inferred؟

### E — Decision Explicitness
هل task التي تطلب اختيارًا اتخذت اختيارًا فعلاً؟

### F — Coverage
هل output غطت العناصر الجوهرية أم تركت جزءًا محوريًا؟

---

# 8) Forbidden Shortcut Checks
هذه من أهم الإضافات.

## Shortcut types
### Shortcut 1 — Generic preference
إجابة تختار خيارًا دون evidence كافية.

### Shortcut 2 — Summary without distinction
تلخيص عام يمر كأنه synthesis أو comparison.

### Shortcut 3 — Structure theater
output تبدو منظمة شكليًا لكن fields المطلوبة غير موجودة فعليًا.

### Shortcut 4 — Marker compliance only
وجود كلمات مثل “evidence” أو “supported” دون أن يكون هناك support meaningful.

### Shortcut 5 — Framing collapse
إجابة تتجاهل الجزء المختلط من task وتتعامل معها كعائلة واحدة فقط.

---

# 9) Framing-aware verification — الشكل الصحيح
لا نريد broad OR permissiveness.

## المقترح
### Rule 1
الـ primary frame تحدد **الخصائص الأساسية الإلزامية**.

### Rule 2
الـ secondary frames تضيف:
- bonus checks
- or supplementary required properties
لكن لا تلغي الأساسية.

### Rule 3
ambiguity العالية قد ترفع tolerance على الشكل النهائي قليلًا،
لكن لا يجب أن تُسقط required properties الأساسية.

### مثال
Task primary = comparison, secondary = procedure

#### then:
- must have explicit comparative choice or contrast
- must have evidence support
- if possible, should also present outcome in structured/handoff-friendly form

أي:
- procedure part تكميلي
- comparison part لا يجوز أن تختفي

---

# 10) Pass logic
نقترح في البداية منطقًا بسيطًا لكنه أقوى من الحالي:

## Hard requirements
- all critical property checks for primary frame must pass
- no major forbidden shortcut should trigger

## Soft requirements
- secondary frame checks improve score or determine stronger pass quality

## Final decision
- `fail`
- `weak_pass`
- `strong_pass`

### لماذا ثلاث حالات؟
لأن binary فقط قد يخفي فروقًا مفيدة جدًا بين conditions.

---

# 11) Family-aware templates for verification
نقترح verifier templates مبدئية:

## Comparison template
Critical properties:
- explicit contrast or choice
- evidence-backed distinction

Forbidden shortcuts:
- vague preference
- no real distinction
- unsupported confidence

## Synthesis template
Critical properties:
- merging of fragments into coherent answer
- evidence trail preserved
- no unsupported leap

Forbidden shortcuts:
- generic summary
- evidence collapse
- blending facts and inferences indiscriminately

## Procedure template
Critical properties:
- stable structure
- field integrity
- usability as checklist/layout

Forbidden shortcuts:
- cosmetic formatting only
- missing key fields
- unnormalized structure

---

# 12) التعامل مع unknown / ambiguous tasks
عندما تكون framing غير محسومة:

## Policy
- لا نسمح للـ verifier بأن تصبح lax جدًا
- بل نطلب:
  1. minimal core adequacy
  2. at least one strong property aligned with primary candidate
  3. no major shortcut violations

### note
الـ ambiguity ليست excuse للـ low-quality success.

---

# 13) Failure modes في verifier design

## Failure Mode 1 — Marker worship
الـ verifier تخلط بين الإشارة اللفظية وتحقيق الخاصية.

## Failure Mode 2 — Over-permissive framing fusion
أي hint من أي frame يُحتسب success.

## Failure Mode 3 — Over-strict formalism
Verifier ترفض outputs جيدة لأن wording لا تطابق قالبًا جامدًا.

## Failure Mode 4 — Shortcut blindness
Outputs شكلها جيد لكنها في الحقيقة فارغة معرفيًا.

## Failure Mode 5 — Loss of discriminative power
جميع conditions تبدو ناجحة رغم اختلافها الحقيقي.

---

# 14) Minimal implementation path
في النسخة القريبة، نقترح:

## Step 1
TaskCase object with:
- required_properties
- forbidden_shortcuts
- expected_primary_family
- expected_secondary_families

## Step 2
verification_runtime takes TaskCase, not task text only

## Step 3
implement property evaluators as explicit functions

## Step 4
implement shortcut detectors as explicit functions

## Step 5
return structured VerificationResult with pass quality levels

---

# 15) ما الذي نحتاجه في الـ data layer لدعم ذلك؟
يجب أن تصبح task sets case-based لا string-based.

### required additions
- `expected_primary_family`
- `expected_secondary_families`
- `required_properties`
- `forbidden_shortcuts`
- `diagnostic_purpose`

وهذا يرتبط مباشرة بـ TaskCase Schema.

---

# 16) العلاقة مع Thesis 1 و2
## Thesis 1
لن نعرف هل concept formation مفيدة إذا كانت verifier تمرر retrieval-only outputs بسهولة بسبب lexical markers.

## Thesis 2
لن نعرف هل economy-aware routing smart إذا كانت verifier لا تميز بين:
- cheap shallow pass
- and genuinely grounded pass

إذًا verifier redesign شرط لحماية الفرضيتين من القياس المضلل.

---

# 17) ما التالي بعد هذه الوثيقة؟
الخطوة المنطقية التالية بعد Verifier Redesign Spec هي:

1. تحويل `prototype_v2/v3/v4` إلى **TaskCase-based sets**
2. تحديث `verification_runtime` لتعمل بالـ hidden contract
3. إعادة تشغيل comparative evaluations

فنيًا، لو أردنا الاستمرار في خط التنفيذ، فالوثيقة التالية العملية جدًا ستكون:

# **Virtual_SIA_TaskCase_Migration_Plan_AR.md**

لأنها ستحدد:
- كيف نحوّل task strings الحالية إلى TaskCases تدريجيًا
- بدون كسر runners الحالية
- ومع الحفاظ على المقارنات السابقة قدر الإمكان

وهذا هو الطريق الأكثر انضباطًا من هنا.
