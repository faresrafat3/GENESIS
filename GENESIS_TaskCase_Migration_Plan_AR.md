# Virtual-GENESIS TaskCase Migration Plan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تحدد كيف ننتقل من الوضع الحالي حيث أغلب task sets هي:
- string-based prompts

إلى وضع أكثر نضجًا حيث task sets تصبح:
- **TaskCase-based**

وذلك بدون:
- كسر الـ runners الحالية
- فقدان المقارنات السابقة
- أو جعل migration نفسها bottleneck توقف التطوير

---

# 1) لماذا نحتاج migration أصلًا؟
بسبب الاكتشافات الأخيرة، أصبح واضحًا أن:
- prompt text وحدها غير كافية لتمثيل مهمة تقييمية/تشغيلية ناضجة
- hidden evaluation contract ضرورية
- framing ambiguity يجب تمثيلها صراحة
- required properties وforbidden shortcuts أصبحت مهمة جدًا

إذًا الانتقال إلى TaskCase ليس تحسينًا تجميليًا، بل:
# **تصحيح في مستوى تمثيل المهمة نفسها**

---

# 2) مبدأ migration
نحن لا نريد big-bang rewrite.

بل نريد:

> **progressive compatibility-preserving migration**

أي:
1. ندعم formatين مؤقتًا
   - string tasks
   - TaskCase tasks
2. ننتقل أولًا في slices التي تحتاج hidden evaluation أكثر
3. نحافظ على المقارنات السابقة قدر الإمكان
4. نسمح للـ harness أن تقرأ كلا النوعين خلال المرحلة الانتقالية

---

# 3) القاعدة الذهبية
لا نكسر التشغيل الحالي إذا كانت migration غير مكتملة.

### Therefore
كل runner أو verifier أو task ingress يجب أن يكون لديها:
- string-path
- TaskCase-path

إلى أن ننهي التحويل بالكامل.

---

# 4) مراحل migration

## Phase 0 — Compatibility Layer
### الهدف
إضافة support لقراءة TaskCase بدون إزالة دعم string tasks.

### deliverables
- `normalize_task_input(...)` تقبل str أو TaskCase dict/object
- `run_condition(...)` تقبل الاثنين
- verification runtime يمكنها العمل:
  - old mode: heuristic family-based
  - new mode: TaskCase contract-based

### النجاح
تشغيل task string القديمة ما زال ممكنًا.

---

## Phase 1 — Introduce TaskCase for prototype_v4 first
### لماذا v4 أولًا؟
لأنها الأكثر احتياجًا لـ:
- hidden evaluation
- family overlap
- framing ambiguity handling

### deliverables
- `prototype_v4_cases` تتحول إلى TaskCase objects كاملة
- classification report تستفيد من expected_primary/secondary families
- verifier تستخدم required_properties + forbidden_shortcuts

### النجاح
v4 تصبح case-based بالكامل وتظل قابلة للمقارنة داخليًا.

---

## Phase 2 — Migrate prototype_v3
### لماذا بعدها؟
لأن v3 أيضًا boundary-oriented لكن أقل تشخيصية من v4.

### deliverables
- convert v3 إلى TaskCases
- preserve original visible prompts
- add moderate hidden contract

---

## Phase 3 — Migrate prototype_v2
### لماذا أخيرًا؟
لأن v2 تعمل الآن كمقياس thesis-level clean نسبيًا، ولا نريد destabilize baseline بسرعة.

### deliverables
- represent v2 as TaskCases with minimal hidden contract
- keep old comparisons available for one cycle

---

## Phase 4 — Deprecate string-only path (later)
### لا يحدث الآن
يُفعل فقط بعد استقرار TaskCase-based evaluation.

---

# 5) Migration object model
نحتاج طبقة صغيرة مساعدة:

## TaskInputUnion
نوع إدخال يسمح بـ:
- `str`
- `TaskCaseObject`

## TaskCaseObject
كما عرّفنا في TaskCase Schema Spec.

## NormalizedTaskEnvelope
object داخلية موحدة نمررها للـ runtime، بحيث مهما كان input:
- string أو TaskCase
يخرج envelope موحد يحتوي على:
- visible prompt
- optional hidden contract
- framing expectations
- diagnostic metadata

---

# 6) ما الذي يتحول أولًا داخل كل task؟
عند migration task string إلى TaskCase، نضيف الحقول بالترتيب التالي:

## Step A — Minimal wrapping
- case_id
- prompt_text
- expected_primary_family
- target_thesis

## Step B — Overlap/framing info
- expected_secondary_families
- family_overlap_type
- diagnostic_purpose

## Step C — Evaluation contract
- required_properties
- forbidden_shortcuts
- required_structure

## Step D — Metadata
- tags
- authoring notes
- status
- provenance

### rationale
بهذا نتحرك من أبسط wrapper إلى case كاملة بالتدرج.

---

# 7) Compatibility strategy for runners
## Current state
runners تقرأ tasks كنصوص فقط.

## Migration target
runners يجب أن تفعل:
1. if task is string → wrap minimally into legacy envelope
2. if task is TaskCase → use full contract

### proposed helper
`normalize_task_input(task_input) -> NormalizedTaskEnvelope`

### envelope fields
- `prompt_text`
- `expected_primary_family`
- `expected_secondary_families`
- `required_properties`
- `forbidden_shortcuts`
- `diagnostic_purpose`
- `raw_input_type`

---

# 8) Compatibility strategy for task ingress
Task ingress should:
- use visible prompt for runtime reasoning
- use expected families only for evaluation / framing analysis where appropriate
- never leak hidden contract into the prompt path by default

### important
لا يجوز أن تتحول TaskCase إلى prompt leakage
وإلا نعيد نفس coupling المشكلة السابقة.

---

# 9) Compatibility strategy for verifier
Verifier يجب أن تعمل في وضعين:

## Legacy mode
- when task is plain string
- uses heuristic family-based checks

## TaskCase mode
- uses required_properties
- forbidden_shortcuts
- required_structure
- framing overlap info

### rule
if TaskCase fields exist, prefer TaskCase mode.

---

# 10) الحفاظ على المقارنات التاريخية
هذه نقطة حساسة جدًا.

## لا نريد أن نفقد القدرة على قول:
- v2 القديمة قالت X
- v2 الجديدة قالت Y

### لذلك نقترح:
1. حفظ نسخة frozen من old string-based sets
2. تشغيل old and migrated versions لفترة قصيرة بالتوازي على sample صغير
3. توثيق الفروق الناتجة عن migration نفسها

### report needed
`migration_comparison_report`
يجيب:
- هل تغيرت success rates لأن التقييم تحسن أم لأن runtime تغيرت؟

---

# 11) ما الذي يُعد نجاح migration؟

## Success A
تشغيل runners مع كلا النوعين من الإدخال دون breakage.

## Success B
TaskCase-based v4 تصبح أكثر تشخيصية من string-based v4.

## Success C
Verifier تصبح أكثر discriminative وأقل marker-dependent.

## Success D
يمكن مقارنة old and migrated slices بوضوح عبر reports.

## Success E
لا يحدث hidden leakage من hidden contract إلى prompt path.

---

# 12) Failure modes في migration

## Failure Mode 1 — Hidden contract leakage
المعلومات المخفية تتسرب إلى prompt.

## Failure Mode 2 — Legacy breakage
task string القديمة تتوقف.

## Failure Mode 3 — Overcomplicated migration
TaskCase تصبح عبئًا إداريًا أكبر من فائدتها الحالية.

## Failure Mode 4 — False comparability
نقارن old/new results كأنهما نفس المعيار رغم تغير evaluation contract.

## Failure Mode 5 — Mixed-mode confusion
بعض modules تستخدم task string assumptions وأخرى تستخدم TaskCase assumptions بلا وضوح.

---

# 13) الترتيب المقترح الآن
## Immediate order
1. add TaskInput normalization helper
2. support TaskCase in runners
3. migrate prototype_v4 first
4. update verifier to read TaskCase fields
5. rerun v4
6. write migration comparison memo

## Then
7. migrate v3
8. migrate v2
9. only later consider deprecating string-only path

---

# 14) القرار النهائي
TaskCase migration ليست الآن شيء اختياري.
هي:
# **شرط لتحسين جودة القياس**

ومادام هدفنا ليس فقط تشغيل النظام، بل **فهم ما إذا كانت الفرضيات صحيحة فعلًا**،
فلا بد أن نرفع تمثيل المهمة نفسها من prompt إلى case.

### الخطوة التالية الطبيعية بعد هذه الوثيقة
هي:
# **تنفيذ طبقة TaskInput normalization + تحديث runners/verifier لقراءة TaskCase**

وهذا سيكون أول تنفيذ مباشر لهذه الخطة.
