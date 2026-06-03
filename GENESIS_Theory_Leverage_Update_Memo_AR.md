# Virtual-GENESIS Theory Leverage Update Memo (Arabic)

## الغرض
توثيق أول محاولة لإدخال **Theory Hints** إلى الـ runtime بشكل minimal.

## ما الذي أُضيف؟
1. `theory_runtime/apply.py` لاختيار النظريات المناسبة وبناء hints منها.
2. BlackboardMemoryPack أصبحت تدعم:
   - `theory_refs`
   - `theory_hints`
3. memory retrieval أصبحت تستقبل `theory_items` وتسترجع theory hints حسب family.
4. reasoning runtime أصبحت قادرة على استيعاب `theory_hints` داخل generation path.

## ما الذي لاحظناه؟
في الوضع الحالي، `used_theories_count = 0` في العينات المطبوعة من `v3b_curriculum`.

### التفسير
هذا لا يعني أن النظرية useless، بل يعني غالبًا أن:
- retrieval الحالية لا تزال concept-first بقوة
- أو أن theory objects لا تضيف discrimination كافية فوق ما توفره concepts الآن
- أو أن task families الحالية صغيرة لدرجة أن theory hints لا تُفعل بشكل مستقل

## الحكم
هذه الجولة لم تضف gain جديدة واضحة، لكنها حققت شيئًا مهمًا:

> **أصبح لدينا plumbing جاهزة لتمرير النظريات إلى runtime حين تصبح ذات قيمة تشغيلية أعلى.**

وهذا يحوّل Theory Layer من:
- reports only
إلى:
- dormant-but-connectable runtime resource

## القرار الحالي
لا نضغط الآن على theory leverage أكثر.
بل نعتبر هذه الطبقة:
- موجودة
- موصولة
- لكن غير فعّالة بعد

ونعود إلى core regime حتى تظهر حاجة أقوى لها.

## الخلاصة
هذه ليست خطوة فاشلة، بل خطوة تأسيسية:
- لا تقدم performance gain الآن
- لكنها تمنعنا من العودة لاحقًا لعمل refactor كبير عندما نحتاج theory-guided behavior فعلاً.
