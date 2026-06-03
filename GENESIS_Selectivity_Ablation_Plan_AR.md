# Virtual-GENESIS Selectivity Ablation Plan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تحدد خطة ablation مركزة على سؤال واحد فقط:

> ما المستوى الأمثل لانتقائية المفاهيم بحيث نحافظ على الجزء المفيد من Thesis 1 دون الوقوع في over-activation أو under-activation؟

بعد الجولات الأخيرة أصبح واضحًا أن:
- المفاهيم useful
- لكن طريقة اختيارها وتفعيلها جزء من جوهر الأداء

إذًا نحتاج micro-ablations منظمة بدل tweaks عشوائية.

---

# 1) السؤال المركزي
كيف يؤثر كل من العوامل التالية على:
- success
- cost
- concept utility
- concept activation discipline

العوامل:
1. عدد المفاهيم المسموح بها per task (Top-1 vs Top-2)
2. activation threshold
3. family-specific selectivity
4. contract-weighted vs semantic-weighted selection

---

# 2) الهدف
نريد الوصول إلى:
# **Selectivity regime**
يحقق توازنًا جيدًا بين:
- performance gain
- limited concept sprawl
- interpretable usage
- reasonable activation rate

---

# 3) ما الذي سنثبته أو ننفيه؟

## H1
Top-1 concept selection قد تكون كافية لمعظم tasks، وتقلل over-conditioning دون loss كبير في الأداء.

## H2
بعض task families (خصوصًا synthesis) قد تستفيد من Top-2 أكثر من comparison أو procedure.

## H3
contract-fit قد يكون أكثر predictive of useful concept activation من lexical/semantic overlap وحده.

## H4
activation threshold المنخفض يرفع performance أحيانًا لكنه يخلق apparent gains inflated by overuse.

---

# 4) المتغيرات التي سنغيّرها

## Variable A — `max_active_concepts`
القيم:
- 0 (control)
- 1
- 2

## Variable B — `min_activation_score`
القيم المقترحة:
- 5
- 6
- 7

## Variable C — selection emphasis
- semantic-heavy
- contract-heavy
- balanced

## Variable D — family-specific policy
- shared global selectivity policy
- comparison/synthesis/procedure each with own settings

---

# 5) ما الذي سنثبته ثابتًا؟
لتجنب confounds:
- same task set (`prototype_v3b_curriculum` first)
- same verifier contract
- same routing logic if possible
- same warmup concept cycle
- same reporting logic

---

# 6) القياسات المطلوبة

## Core metrics
1. success_rate
2. avg_estimated_cost
3. concept_activation_rate
4. avg_concepts_per_task
5. concept utility proxy
6. premium_run_count

## Secondary metrics
7. family-wise success
8. candidate_count_per_task
9. average activation score of selected concepts
10. zero-concept rate

---

# 7) جدول الـ ablations الأولي
نقترح 4 تجارب صغيرة بدل grid كاملة ضخمة:

## Ablation A — Top-1 vs Top-2
- threshold ثابت
- scoring policy ثابت
- نغير فقط max_active_concepts

### ما نريد معرفته
هل second concept تضيف gain فعليًا أم noise؟

---

## Ablation B — Threshold sensitivity
- max_active_concepts ثابتة
- scoring policy ثابت
- thresholds مختلفة

### ما نريد معرفته
هل activation الحالية رخوة أكثر من اللازم أم صارمة أكثر من اللازم؟

---

## Ablation C — Contract-heavy vs Semantic-heavy
- max_active_concepts ثابتة
- threshold ثابتة

### ما نريد معرفته
هل required_properties/forbidden_shortcuts هي المفتاح الأفضل للاختيار؟

---

## Ablation D — Family-specific selectivity
- comparison top-1
- synthesis top-2
- procedure top-0 أو top-1

### ما نريد معرفته
هل family-specific tuning تعطي frontier أوضح من policy واحدة للجميع؟

---

# 8) الفرضية العملية الحالية قبل الاختبار
أكثر regime مرجحة الآن:
- comparison: Top-1
- synthesis: Top-2
- procedure: Top-0 أو Top-1
- threshold متوسطة (حوالي 6)
- contract-weighted stronger than semantic-only

هذه ليست نتيجة نهائية، بل prior قابل للاختبار.

---

# 9) success criteria
نعتبر ablation ناجحة إذا أعطت:
1. same or near-same success with lower activation rate
2. أو better family-wise performance without exploding concept usage
3. أو interpretable selectivity pattern consistent with task families

---

# 10) failure criteria
فشل policy selectivity إذا:
- activation rate remains near 1.0 بلا حاجة
- أو success تنهار sharply عند خفض activation قليلًا
- أو family patterns remain opaque
- أو second concept لا تضيف شيئًا consistent

---

# 11) الناتج المتوقع
هذه الخطة يجب أن تخرج لنا:
1. preferred global selectivity policy
أو
2. evidence لصالح family-specific selectivity policy

وبعدها يمكن تثبيت Concept Activation policy في prototype الأساسية بدل تركها under continuous tuning.

---

# 12) لماذا هذه الخطة مهمة؟
لأنها تنقلنا من:
- tuning بالحدس
إلى:
- controlled micro-evidence on concept usage policy

وهذا ضروري إذا أردنا أن تتحول Thesis 1 من promising mechanism إلى controlled mechanism.
