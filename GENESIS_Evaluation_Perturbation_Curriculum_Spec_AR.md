# Virtual-GENESIS Evaluation Perturbation & Curriculum Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تأتي استجابة مباشرة لاكتشاف مهم في الـ prototype:

> **الشرائح اليدوية hand-authored وحدها لا تكفي للحفاظ على قوة التمييز مع تحسن النظام.**

فقد ظهر لنا نمط متكرر:
- بعض الشرائح تصبح سهلة جدًا فتتشبع
- وبعضها تصبح قاسية جدًا فتتحول إلى diagnostic slice أكثر من كونها thesis slice

لذلك نحتاج طبقة جديدة ليست agent-layer، بل evaluation-layer:

# **Evaluation Perturbation & Curriculum Layer**

هدفها:
1. توليد مستويات صعوبة متعددة من نفس TaskCase
2. الحفاظ على hidden contract بينما نغيّر شكل الضغط الظاهر
3. إنتاج curriculum تقييمية بدل قائمة slices مفككة
4. خلق slices أكثر قدرة على اختبار Thesis 1 و2 بعد تحسن النظام

---

# 1) المشكلة التي تحاول هذه الطبقة حلها
حتى الآن رأينا:
- `v2` و`v5` تميلان إلى saturation
- `v4` ممتازة تشخيصيًا لكنها harsh وغير مستقرة بما يكفي كـ thesis slice
- `v3b` أفضل thesis slice حاليًا لكنها قد تتشبع هي أيضًا إذا تحسن النظام أكثر

هذا يعني أن المشكلة ليست فقط “اختيار الحالات”، بل:

> **كيف نُنتج ضغطًا تقييميًا متدرجًا وقابلًا للضبط من نفس family المعرفية؟**

---

# 2) الفرضية الأساسية
### Hypothesis
القدرة على **توليد perturbations موجهة** على TaskCases ستعطينا شرائح تقييمية أفضل من مجرد كتابة قوائم جديدة يدويًا كل مرة.

أي:
- نحافظ على task semantics
- لكن نغيّر level of surface cues / evidence fragmentation / overlap / anti-shortcut pressure
- فنحصل على curriculum ذات مستويات

---

# 3) التعريف المركزي
## Perturbation
تغيير مضبوط في TaskCase أو prompt أو hidden contract أو framing cues، بهدف تعديل صعوبة أو نوع الضغط الاختباري **دون تدمير الغرض الأساسي للمهمة**.

## Evaluation Curriculum
مجموعة TaskCases مرتبة عبر مستويات صعوبة/غموض/ضغط، بحيث يمكن قياس:
- أين تتشبع الشرائح؟
- أين يظهر الفرق بين conditions؟
- وكيف يتغير behavior عبر مستويات الضغط؟

---

# 4) أنواع الـ perturbations
نقترح ستة أنواع أولية:

## P1 — Lexical Softening
تقليل الكلمات المفتاحية الواضحة التي تسهّل framing أو retrieval.

### مثال
- "compare" → "determine which is more defensible"
- "checklist" → "operator-ready note"

## P2 — Evidence Fragmentation
زيادة تشتت الدليل في prompt أو جعل العلاقة بين القطع أقل مباشرة.

## P3 — Overlap Injection
إضافة إشارة خفيفة إلى family ثانوية دون تحويل task إلى chaos مثل v4.

## P4 — Contract Tightening
رفع hidden evaluation standards:
- إضافة required property جديدة
- أو forbidden shortcut جديدة

## P5 — Structure Obfuscation
جعل الحاجة إلى structure implicit أكثر، دون حذفها تمامًا.

## P6 — Perspective Shift
إعادة صياغة task من زاوية أخرى:
- audit note
- handoff note
- release memo
- executive update
مع الحفاظ على core reasoning need نفسها.

---

# 5) ما الذي لا يجب أن تفعله perturbations؟

## No semantic collapse
لا يجب أن تتحول المهمة إلى شيء مختلف كليًا.

## No evaluation leakage
لا نضيف cues ظاهرة تجعل hidden contract تافهة.

## No random hardness
الصعوبة يجب أن تكون مفسرة، لا noisy فقط.

## No unfair distortion
لا نحول المهمة إلى نوع لا تختبر نفس المهارة/النظرية أصلًا.

---

# 6) TaskCase perturbation object
يمكن تمثيل perturbation applied على case كالتالي:

## PerturbedTaskCase metadata
- `source_case_id`
- `perturbation_id`
- `perturbation_type`
- `intensity`
- `preserved_contract_fields`
- `modified_visible_fields`
- `difficulty_delta_expected`
- `diagnostic_goal`

وهذا مهم جدًا حتى لا تصبح generated cases بلا lineage.

---

# 7) Curriculum levels المقترحة

## Level 0 — Clean Base
case الأصلية baseline النظيفة.

## Level 1 — Softened Surface
نفس hidden contract تقريبًا، لكن cues أقل مباشرة.

## Level 2 — Mild Overlap
إدخال secondary frame واحدة بشكل خفيف.

## Level 3 — Tight Contract
نفس الـ prompt تقريبًا، لكن hidden contract أشد.

## Level 4 — Combined Stress
softening + overlap + tighter contract

### ملاحظة
ليس مطلوبًا استخدام كل levels لكل family.
المهم أن تكون levels **مقيسة ومفهومة**.

---

# 8) ما الذي نريد أن نراه من curriculum؟
نريد أن نعرف:
1. متى تتشبع baseline؟
2. متى تبدأ concepts أن تكون ضرورية؟
3. متى يصبح premium reasoning worth it؟
4. متى تفشل economy policy؟
5. هل combined path تصعد gracefully مع difficulty؟

أي أن curriculum ليست فقط أداة ضغط، بل أداة لرسم **curves**.

---

# 9) Curves مهمة نريدها
### Curve A — Concept Utility vs Difficulty
متى تبدأ concepts أن تعطي عائدًا حقيقيًا؟

### Curve B — Economy Benefit vs Difficulty
متى يكون التوفير الذكي مفيدًا؟ ومتى يصبح underinvestment؟

### Curve C — Premium ROI vs Difficulty
متى تستحق premium فعلاً؟

### Curve D — Combined Path Stability
هل المسار المركب يصمد عبر مستويات الضغط؟

---

# 10) أين تستخدم هذه الطبقة؟
## Use 1 — Thesis slices generation
توليد middle slices جديدة بطريقة أكثر systematic.

## Use 2 — Stress testing
إنتاج حالات diagnostic دون كتابة lists جديدة كل مرة.

## Use 3 — Regression monitoring
نفس case عبر perturbation ladder يمكنها كشف إذا كان improvement حقيقيًا أو surface-bound.

## Use 4 — Future self-benchmarking
هذه الطبقة قد تصبح لاحقًا أساسًا لـ self-benchmarking engine.

---

# 11) Success criteria
### Criterion A
تنتج curriculum ذات مستويات صعوبة مفهومة ومفسرة.

### Criterion B
تسمح بظهور thesis-level separation أو failure curves أوضح من hand-authored static slices.

### Criterion C
تحافظ على comparability عبر source_case_id lineage.

### Criterion D
لا تسرب hidden contract إلى visible prompt بشكل مفرط.

---

# 12) Failure modes
### Failure Mode 1 — Perturbation drift
case الجديدة لم تعد تمثل نفس المهمة جوهريًا.

### Failure Mode 2 — Artificial hardness
زيادة صعوبة noisy لا diagnostic.

### Failure Mode 3 — Contract corruption
الحفاظ على prompt لكن كسر hidden evaluation logic.

### Failure Mode 4 — Lineage loss
لا نعرف أي generated case أتت من أي أصل.

---

# 13) القرار العملي التالي
هذه الوثيقة توصي بالخطوة التالية التالية:
1. بناء utility بسيطة لتوليد TaskCase variants
2. تطبيقها أولًا على `v3b` لاستخراج curriculum صغيرة
3. مقارنة levels المختلفة على conditions الأساسية

وهذا سيجعلنا ننتقل من:
- كتابة slices يدويًا واحدة واحدة
إلى:
- **evaluation regime more programmatic and scalable**

بدون القفز فورًا إلى self-benchmarking الكامل.
