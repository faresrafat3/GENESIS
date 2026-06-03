# Virtual-GENESIS Evaluation Slice Strategy (Arabic)

## الغرض
توثيق الاستنتاج التنفيذي الحالي بعد عدة جولات من:
- prototype_v2
- prototype_v3
- prototype_v4
- TaskCase migration
- verifier redesign
- concept engine refinement

والخروج باستراتيجية أوضح لكيفية استخدام الشرائح المختلفة بدل محاولة جعل slice واحدة تؤدي كل الأدوار.

---

## الاستنتاج الرئيسي
الـ slices الحالية لا يجب أن تُعامل بالطريقة نفسها.

نقترح رسميًا فصلها إلى ثلاثة أدوار:

# 1) Thesis Slice
- هدفها: قياس Thesis 1 وThesis 2
- يجب أن تكون discriminative but not brutal
- يجب ألا تكون permissive جدًا ولا boundary-chaotic جدًا

# 2) Diagnostic Slice
- هدفها: كشف bottlenecks
- تسمح بالغموض والتداخل والضغط على framing والverification
- لا تُستخدم وحدها للحكم النهائي على الـ theses

# 3) Calibration Slice
- هدفها: التأكد أن baseline path ما زالت سليمة
- بسيطة نسبيًا
- تمنعنا من الخلط بين runtime breakage and real difficulty

---

## أين تقع الشرائح الحالية؟
### prototype_v2
- أقرب إلى **Calibration / light Thesis Slice**
- مفيدة لإظهار signals أولية
- لكنها تميل أحيانًا إلى السهولة أو saturation

### prototype_v3_cases
- أصبحت بعد بعض التعديلات **too easy** under TaskCase contract الحالي
- وبالتالي ليست thesis-discriminative بما يكفي الآن

### prototype_v4_cases
- أقرب إلى **Diagnostic Slice**
- مفيدة جدًا لاكتشاف framing/verification issues
- لكنها قاسية وغير مستقرة بما يكفي لكي تكون thesis benchmark الرئيسية وحدها

---

## المشكلة الحالية
بعد عدة تعديلات، وصلنا إلى وضع فيه:
- بعض slices permissive جدًا
- وبعض slices punitive جدًا

إذًا المشكلة لم تعد بناء layer جديدة، بل:
# **إدارة سُلَّم الصعوبة والتمييز بين أدوار الـ slices**

---

## القرار الاستراتيجي
بدل patching المتتابع على نفس slice، نقترح:

### A. تثبيت v4 كـ Diagnostic Slice
- لا نطلب منها إثبات thesis نهائيًا
- نستخدمها لاكتشاف bottlenecks في framing/verification/concept leverage

### B. الاحتفاظ بـ v2 كمرجع baseline-friendly
- useful for trend and sanity checks

### C. تصميم slice جديدة وسطية
اسم مقترح:
# `prototype_v3b_cases`

### خصائصها
- TaskCase-based
- أقل غموضًا من v4
- أقل permissiveness من v2/v3 الحالية
- hidden contracts tighter لكن غير brutal
- موجهة specifically لتمييز Thesis 1 وThesis 2

---

## كيف نصمم v3b؟
### Families
- comparison
- synthesis
- procedure

### لكن
- overlap أقل من v4
- hidden contracts أوضح من v2
- anti-shortcut checks حاضرة لكن غير مبالغ فيها
- concepts should matter
- premium should help but not dominate

### الغرض
خلق “middle slice” تكون:
- discriminative enough
- stable enough
- interpretable enough

---

## ما الذي نتوقف عن فعله الآن؟
1. لا نزيد verifier permissiveness أكثر
2. لا نجعل كل slice تحمل كل أنواع الضغط مرة واحدة
3. لا نفسر أي spike/downturn في performance خارج role السlice نفسها

---

## الخطوة العملية التالية المقترحة
1. Freeze current v2, v4 behavior as references
2. Design `prototype_v3b_cases`
3. Run all core conditions عليها
4. Compare:
   - v2 (easy/clean)
   - v3b (middle/discriminative)
   - v4 (hard/diagnostic)

### النتيجة المرجوة
نحصل على evaluation ladder:
- easy / sanity
- middle / thesis discrimination
- hard / bottleneck discovery

وهذا سيكون أكثر نضجًا بكثير من البحث عن slice واحدة “تفعل كل شيء”.
