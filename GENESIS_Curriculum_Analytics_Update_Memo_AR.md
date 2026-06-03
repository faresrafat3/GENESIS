# Virtual-GENESIS Curriculum Analytics Update Memo (Arabic)

## الغرض
توثيق التحديث الذي أضاف **curriculum analytics** إلى evaluation regime بدل الاكتفاء بمتوسطات النجاح والتكلفة فقط.

## ما الذي تغيّر؟
1. perturbation metadata (source_case_id / curriculum_level / perturbation_type / tags) أصبحت تنتقل من TaskCase إلى NormalizedTaskEnvelope ثم إلى نتائج التشغيل.
2. أُضيف report جديد:
   - `curriculum_analytics.py`
3. أصبح بإمكاننا تلخيص الأداء حسب:
   - curriculum level
   - perturbation type

## لماذا هذا مهم؟
لأن النجاح الكلي على curriculum قد يخفي أسئلة أهم مثل:
- هل الضعف يظهر فقط عند lexical softening؟
- هل overlap injection هي ما يدفع إلى التصعيد؟
- هل contract tightening هي التي تكشف الحاجة إلى concepts؟

بدون هذه الطبقة، كنا سنفقد تفسيرًا مهمًا جدًا لما يحدث داخل curriculum.

---

## النتائج الحالية على `prototype_v3b_curriculum`
في condition_c_combined ظهرت مؤشرات مثل:
- Level 0 success = 1.0
- Level 1 success = 1.0
- Level 2 success = 1.0
- Level 3 success = 1.0

وكذلك عبر perturbation types:
- base = 1.0
- lexical_soften = 1.0
- overlap_procedure = 1.0
- overlap_synthesis = 1.0
- tight_contract = 1.0

## القراءة
هذا لا يعني أن analytics غير مفيدة، بل يعني أن:
- الشريحة الحالية ما زالت غير ضاغطة بما يكفي على المسار combined
- لكننا الآن نملك أداة تمكننا من اكتشاف **أين** ينكسر النظام بمجرد أن تظهر الفروق

أي أننا بنينا أداة تشخيص قبل الحاجة الحادة إليها، وهذا شيء جيد جدًا.

---

## الدرس المهم
الآن لم يعد سؤال evaluation فقط:
- هل condition X أفضل من Y؟

بل أيضًا:
- تحت أي perturbation type يحدث الفرق؟
- تحت أي curriculum level يتغير المسار؟
- أين تتشبع الفرضيات؟

وهذا هو المستوى الصحيح التالي من النضج في evaluation regime.

---

## القرار العملي الحالي
1. الإبقاء على curriculum analytics كجزء دائم من أي curriculum run
2. عندما نصمم slices أصعب لاحقًا، سيكون لدينا instrumentation جاهزة لتفسيرها
3. لا حاجة الآن إلى layer تقييمية جديدة؛ بل نحتاج cases أكثر discriminative أو operators أقسى

## الحكم
هذا التحديث لا يغيّر النتائج الجوهرية، لكنه يرفع قدرتنا على **فهم النتائج عندما تصبح أصعب**.
