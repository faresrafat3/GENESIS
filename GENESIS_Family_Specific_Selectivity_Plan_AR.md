# Virtual-GENESIS Family-Specific Selectivity Plan (Arabic)

## الغرض
هذه الوثيقة تثبّت الخطوة التالية بعد نجاح `Concept Selectivity` العامة نسبيًا:

> الانتقال من selectivity global إلى **family-specific selectivity**

## لماذا؟
النتائج السابقة أظهرت أن:
- comparison, synthesis, procedure لا تتصرف بالطريقة نفسها
- بعض العائلات تستفيد من concepts أكثر
- وبعضها تتشبع أو تكتفي بإجراءات ثابتة أسرع

إذًا policy واحدة لكل families قد تكون suboptimal.

---

## القرار الحالي في الكود
أُضيفت default family-specific selectivity في:
`virtual_genesis/runtime/concept_engine/config.py`

### القيم الحالية
- comparison:
  - `max_active = 1`
  - `min_score = 7`
- synthesis:
  - `max_active = 1`
  - `min_score = 7`
- procedure:
  - `max_active = 0`
  - `min_score = 99`

### rationale
- comparison: concept useful لكن نريد explicit restraint
- synthesis: concept useful لكن avoid overloading
- procedure: try zero-concept by default because procedural structure may be enough in many cases

---

## ما الذي نحتاج اختباره لاحقًا؟
1. هل synthesis تحتاج top-2 بدل top-1؟
2. هل procedure فعلًا تستفيد من zero-concept policy؟
3. هل comparison تستفيد من contract-heavy selection أكثر من semantic-heavy selection؟

## النتيجة
الآن concept selectivity لم تعد فقط tuning عامة، بل بدأت تصبح policy قابلة للتخصيص حسب family.

وهذا ينسجم مع نضج Thesis 1 من:
- existence of concepts
إلى:
- governed and scoped concept use.
