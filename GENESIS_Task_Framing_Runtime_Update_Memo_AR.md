# Virtual-GENESIS Task Framing Runtime Update Memo (Arabic)

## الغرض
توثيق التحديث الأولي على Task Framing runtime بعد اكتشاف bottleneck في Prototype v4.

## ما الذي تغيّر؟
1. task ingress لم تعد تُخرج family واحدة فقط، بل:
   - `family_scores`
   - `ranked_frames`
   - `primary_frame`
   - `secondary_frames`
   - `family_ambiguity`
2. memory retrieval أصبحت تستطيع استخدام أكثر من family candidate بدل primary label فقط.
3. tier router أصبحت ambiguity-aware بدرجة أولية.
4. evaluation v4 أصبحت تقيس ليس فقط `match_rate`، بل أيضًا `top2_match_rate`.

## أهم نتيجة
- `match_rate` بقيت منخفضة = **0.4167**
- لكن `top2_match_rate` ارتفعت إلى **0.6667**

### القراءة
هذا يعني أن framing layer البدائية ما زالت ضعيفة إذا أُجبرت على hard single-label prediction،
لكنها بدأت تلتقط البنية الصحيحة جزئيًا إذا سمحنا بمنطق:
- ranked frames
- primary + secondary interpretation

بمعنى آخر:

> النظام لا يزال لا “يحسم” framing جيدًا دائمًا، لكنه صار أفضل في **تمثيل ambiguity** بدل دفنها.

## أثر ذلك على thesis signals
### Thesis 1
- baseline retrieval-only = **0.9167**
- concept-ready = **1.0**
- concept activation = **0.4167**

### Thesis 2
- premium-always = **0.9167**
- economy-aware = **0.9167**
- economy avg cost بقيت أقل بكثير من premium-always

### Combined
- success = **1.0**
- avg cost منخفضة جدًا

## القراءة الحذرة
التحديث الحالي على framing لم يرفع match_rate المباشرة بعد، لكنه:
1. جعل ambiguity visible
2. أتاح استخدام secondary frames في retrieval
3. حافظ على قوة thesis-level signals

وهذا يعني أن framing layer بدأت تتحرك من:
- brittle labeling
إلى:
- operational ambiguity handling

## الخطوة التالية المقترحة
1. جعل verification نفسها framing-aware
2. جعل concept activation تستفيد من secondary frames بشكل أقوى
3. تصميم boundary tasks where expected success depends on multi-frame handling explicitly

## الحكم الحالي
Task framing ما زالت bottleneck، لكنها لم تعد hidden bottleneck.
وهذا في حد ذاته تقدم مهم، لأن النظام بدأ يتحول من:
- تصنيف قاطع هش
إلى:
- تمثيل problem ambiguity كجزء من state.
