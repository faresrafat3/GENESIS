# Virtual-GENESIS Selectivity Ablation Results Memo (Arabic)

## الغرض
تلخيص أول micro-ablations موجهة لسؤال واحد:

> ما أثر انتقائية المفاهيم على الأداء والكلفة ونمط التفعيل؟

تم تشغيل ablations على `prototype_v3b_curriculum` تحت أربع إعدادات:
1. `top1_score6`
2. `top2_score6`
3. `top1_score7`
4. `top2_score7`

## الملاحظة المنهجية
هذه الجولة لا تهدف إلى إثبات thesis جديدة، بل إلى ضبط **شكل استخدام المفاهيم** بعد أن أصبحت Thesis 1 تمتلك evidence واعدة.

---

## القراءة العامة
### النتيجة الأساسية
الرفع من threshold من 6 إلى 7:
- خفّض concept activation rate
- دون أن يضر success في الشريحة الحالية

بينما التبديل بين `top1` و`top2`:
- لم يغيّر النتائج بشكل يذكر في هذه الجولة

## ماذا يعني هذا؟
1. هناك over-activation جزئي عند threshold أخف
2. second concept لا تضيف فرقًا واضحًا في هذه الشريحة الحالية
3. رفع threshold قليلًا يبدو promising كطريقة لزيادة discipline دون خسارة واضحة

---

## Thesis 1 side
### عند score6
- concept success ≈ **0.9167**
- concept activation ≈ **0.8194**

### عند score7
- concept success ≈ **0.9167**
- concept activation ≈ **0.7083**

### القراءة
هذا مهم جدًا:
- استطعنا تقليل التفعيل بحوالي 11 نقطة مئوية تقريبًا
- دون خسارة performance ملحوظة في هذه الشريحة

إذًا هناك دعم أولي لفكرة أن:
# **concept discipline can improve without sacrificing gains**

---

## Thesis 2 side
إضافة baseline_2 وcondition_b في الـ ablation تؤكد أن:
- economy path ما زالت أقوى بكثير اقتصاديًا من premium-always
- مع نجاح متقارب في هذه الشريحة

هذا يعني أن tuning selectivity لم تكسر economy frontier.

---

## Combined condition
### score6
- combined success ≈ **0.9167**
- avg cost ≈ **0.001458**

### score7
- combined success ≈ **0.9167**
- avg cost ≈ **0.001347**

### القراءة
رفع threshold من 6 إلى 7 حسن economy قليلًا وخفض activation دون penalty ظاهرة في success.

---

## الاستنتاج المرحلي
### 1. Threshold matters more than top-1 vs top-2 here
هذا هو أهم اكتشاف في هذه الجولة.

### 2. current evidence suggests moving toward stricter activation
على الأقل في `prototype_v3b_curriculum`.

### 3. top-2 does not yet justify itself
في هذه الشريحة، second concept لا تضيف مكسبًا واضحًا.

---

## القرار المقترح
1. اعتماد `score7` كخيار افتراضي تجريبي مؤقت
2. إبقاء `top1` كسياسة concept activation افتراضية مؤقتة
3. اختبار ذلك لاحقًا على slices أصعب/أكثر تداخلاً

## الحكم الحالي
هذه الجولة لا تنهي Concept Selectivity، لكنها تعطي أول دليل أن:
- **زيادة الانضباط في التفعيل ممكنة**
- وبدون خسارة ظاهرة في الأداء داخل الشريحة الحالية

وهذا بالضبط ما كنا نحتاج إثباته قبل أي توسيع أكبر في Thesis 1.
