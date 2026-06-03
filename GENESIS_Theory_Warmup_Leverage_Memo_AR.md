# Virtual-GENESIS Theory Warmup Leverage Memo (Arabic)

## الغرض
توثيق التحديث الذي سمح للنظريات المحلية بأن تكون موجودة أثناء التشغيل الفعلي عبر:
- بناء النظريات تدريجيًا في warmup
- تحديثها أثناء run series
- وتمريرها إلى memory retrieval ومن ثم reasoning runtime

## ما الذي تغيّر؟
قبل هذا التحديث:
- theory objects كانت تُبنى بعد انتهاء run condition
- وبالتالي `used_theories_count = 0`
- أي أن theory layer كانت موجودة في reports فقط

بعد التحديث:
- theory registry تُبنى تدريجيًا أثناء warmup/loop
- يمكن للـ runtime أن ترى theories من الحالات السابقة
- أصبح لدينا metric جديدة:
  - `theory_hint_task_rate`

## لماذا هذه الخطوة مهمة؟
لأنها أول مرة تنتقل فيها Theory Layer من:
- post-hoc artifact
إلى:
- **potentially active runtime resource**

## ما الحكم؟
إذا ظهرت theory hints مستخدمة فعليًا، فهذا لا يعني أن theory leverage نضجت بالكامل، لكنه يعني أن:
- runtime باتت قادرة على استدعاء مستويات تفسير أعلى من concepts فقط
- Local Theory Building لم تعد endpoint فقط، بل بدأت تصبح جزءًا من epistemic loop

## ما الذي يبقى مطلوبًا؟
حتى لو ظهرت theory hints، ما زال يلزم لاحقًا:
- قياس أثرها السلوكي بدقة
- مقارنة runs with/without theory hints
- ضبط متى should theory matter ومتى لا

لكن هذه الخطوة تُعد انتقالًا مهمًا من “theories as reports” إلى “theories as candidate control signals”.
