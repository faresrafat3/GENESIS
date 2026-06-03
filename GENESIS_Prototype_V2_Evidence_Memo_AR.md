# Virtual-GENESIS Prototype V2 Evidence Memo (Arabic)

## الغرض
هذه مذكرة evidence بعد توسيع task slice إلى `prototype_v2` وتحسين concept-use loop وربط الـ concepts مباشرة بالـ retrieval والـ reasoning والـ tier routing.

## إعداد التجربة
- task set: `prototype_v2`
- عدد المهام: **18**
- العائلات:
  - comparison (6)
  - synthesis (6 تقريبًا مع task classification current)
  - procedure (6)
- conditions:
  - baseline_0
  - baseline_1
  - baseline_2_premium_always
  - condition_a_concept_ready
  - condition_b_economy
  - condition_c_combined

## أهم التحسينات قبل التشغيل
1. concept-aware retrieval أصبحت تضيف `concept_hints` لا `concept_refs` فقط.
2. reasoning runtime أصبحت أكثر family-sensitive.
3. tier router أصبحت تستخدم وجود concepts كإشارة ضد escalation غير الضرورية.
4. verification procedural أصبحت أعدل وأقل تحيزًا للفشل الزائف.
5. concept registry أصبحت تمنع inflation الناتجة عن التكرار الاسمي، فعدد الـ concepts صار أكثر معقولية.

---

## النتائج المختصرة
### Thesis 1 — Concept Formation vs retrieval-only
- baseline_1 success = **0.8889**
- condition_a_concept_ready success = **1.0**
- same cost order = **true**
- concept activation rate = **0.6111**
- concept_count after dedup = **2**
- warmup concept_count_after_warmup = **2**

### القراءة
هذه أقوى إشارة حتى الآن لصالح Thesis 1 داخل الشريحة الحالية:
- retrieval-only baseline قوية أصلًا
- ومع ذلك concept-aware path ما زالت أفضل
- مع تفعيل فعلي للـ concepts في >60% من المهام
- وبدون انفجار في عدد المفاهيم بعد ضبط registry

### caveat
هذه tasks ما تزال مصطنعة ومضبوطة نسبيًا، وبالتالي لا يجب تعميم النتيجة خارج هذا slice بعد.

---

### Thesis 2 — Economy-aware vs premium-always
- premium-always success = **0.8889**
- premium-always avg cost = **0.01**
- economy-aware success = **0.8889**
- economy-aware avg cost = **0.001611...**
- premium_run_count in economy-aware = **2** فقط (مقابل 18 في premium-always)

### القراءة
هذه ما تزال من أقوى النتائج التجريبية في المشروع:
- نفس النجاح تقريبًا
- مع cost أقل بكثير
- ومع premium usage أقل بشكل واضح جدًا

إذًا Thesis 2 تظل الأقوى والأوضح حتى الآن.

---

### Combined condition
- success = **1.0**
- avg cost = **0.000611...**
- concept activation rate = **0.6111**
- premium_run_count = **0**

### القراءة
هذه النتيجة مثيرة جدًا للاهتمام داخل الشريحة الحالية:
- أعلى نجاح
- أقل تكلفة تقريبًا
- concept use حقيقي

لكن لا يجب إساءة تفسيرها؛ من المحتمل أن الشريحة الحالية ملائمة جدًا لهذا المسار، لذا نحتاج task slices أصعب وأكثر boundary pressure قبل أي claims قوية.

---

## Family-wise observations
### Condition A — concept_ready
- comparison = 1.0
- synthesis = 1.0
- procedure = 1.0

### Condition B — economy
- comparison ≈ 0.8333
- synthesis = 0.8
- procedure = 1.0

### القراءة
- economy-aware routing ممتازة اقتصاديًا لكن ما تزال تخسر بعض النجاح في comparison/synthesis مقارنة بالـ concept-enhanced paths.
- procedure tasks أصبحت مستقرة جدًا بعد تعديل verification/runtime family handling.

---

## الاستنتاج المرحلي
### ما الذي أصبح واضحًا؟
1. **Thesis 2**: عندها evidence قوية مبكرة ومستمرة.
2. **Thesis 1**: عندها الآن evidence واعدة وقوية داخل هذا slice، خاصة بعد concept dedup وربط المفاهيم مباشرة بالـ runtime.
3. **Condition C**: مرشحة قوية جدًا، لكن تحتاج اختبارات أصعب قبل اعتبارها المسار المفضل النهائي.

### ما الذي لم يُثبت بعد؟
- performance على مهام أعقد أو أقل cleanly classifiable
- behavior تحت contradictions/anomalies حقيقية
- انتقال حقيقي across richer domains
- economic accounting that fully includes warmup/training-like passes للمفاهيم

---

## أولويات التنفيذ التالية
1. رفع صعوبة task slice تدريجيًا دون كسر attribution
2. قياس warmup cost وreuse returns بوضوح أكبر
3. تحسين family classification والتغطية على الحالات الحدودية
4. فقط بعد ذلك التفكير هل نضيف contradiction/anomaly runtime layers أم نواصل sharpening للـ core thesis pair

## الحكم الحالي
الـ prototype لم تعد مجرد skeleton تجريبية. هي الآن:
- **usable experimental slice**
- تنتج signals thesis-level
- وتدعم القرار بالاستمرار في Thesis 1 + Thesis 2 بدل التوسع المبكر في governance الكبرى
