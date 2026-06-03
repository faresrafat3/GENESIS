# Virtual-GENESIS - مذكرة دورة ضغط التقييم
# Evaluation Pressure Cycle Memo (Option C)

> Document Type: Implementation Memo
> Status: Completed
> Date: 2026-06-01
> Cycle: Evaluation Pressure (C1-C4)

---

## 1. الغرض من هذه المذكرة

هذه المذكرة توثق دورة **ضغط التقييم** (Evaluation Pressure Cycle) التي تم تنفيذها كجزء من Option C.
الهدف: زيادة الضغط على النظام لكشف نقاط الضعف الحقيقية وضمان أن الأداء الحالي ليس نتيجة shortcuts.

---

## 2. ما عوامل الاضطراب التي أضفناها ولماذا؟

### 2.1 العوامل الخمسة الجديدة

| العامل | الهدف | المصدر (السرقة) |
|--------|-------|-----------------|
| `support_removal` | كشف الاعتماد على أدلة محددة vs فهم عام | 5.24 - Zeiler & Fergus (Ablation) |
| `evidence_reordering` | كشف الاعتماد على ترتيب المعلومات | 5.25 - Hogarth & Einhorn (Order Effects) |
| `contrast_weakening` | كشف الاعتماد على إشارات تباين لفظية واضحة | 5.26 - Nie et al. / Gardner et al. (Contrast Sets) |
| `structure_weakening` | كشف الاعتماد على التنسيق الشكلي | 5.27 - Mann & Thompson (RST) |
| `stronger_shortcut_lures` | كشف الاعتماد على مسارات مختصرة | 5.28 - Goodfellow / Geirhos (Adversarial/Shortcuts) |

### 2.2 لماذا هذه العوامل تحديداً؟

كل عامل يستهدف نوعاً مختلفاً من "الذكاء الزائف":
- **support_removal**: هل النظام يفهم فعلاً أم يردد أدلة محفوظة؟
- **evidence_reordering**: هل الفهم مستقل عن العرض أم مرتبط بالترتيب؟
- **contrast_weakening**: هل يميز الفروق الجوهرية أم يعتمد على كلمات مفتاحية؟
- **structure_weakening**: هل يفهم المحتوى أم يعتمد على التنسيق؟
- **stronger_shortcut_lures**: هل يتبع المنطق الصحيح أم أسهل مسار متاح؟

### 2.3 التصميم التقني

كل عامل يتبع نمطاً موحداً (من `taskcase_variants.py`):
```python
def apply_<name>(case: TaskCase) -> TaskCase:
    new_case = clone_case(case)
    # تعديل prompt_text
    new_case.tags.append('perturb_<name>')
    new_case.meta['perturbation_type'] = '<name>'
    return new_case
```

---

## 3. تصميم مجموعة مهام v6

### 3.1 البنية

مجموعة `prototype_v6_cases` تحتوي 18 مهمة:
- 6 مهام comparison (مقارنة)
- 6 مهام synthesis (تركيب)
- 6 مهام procedure (إجراء)

### 3.2 الفرق عن v5

| الجانب | v5 | v6 |
|--------|----|----|
| عدد المهام | 15 | 18 |
| مستوى الصعوبة | متوسط | أعلى من v5 |
| الاضطرابات المتاحة | 4 مستويات | 6 مستويات |
| الهدف | تأسيس baseline | ضغط لكشف حدود النظام |

### 3.3 تصميم المهام

المهام في v6 صُممت لتكون:
- أكثر تعقيداً في الصياغة
- أقل اعتماداً على إشارات واضحة
- أكثر تطلباً لفهم عميق
- مناسبة لاختبار العوامل الخمسة الجديدة

---

## 4. توسيع المنهج الدراسي إلى 6 مستويات

### 4.1 المستويات

مصدر السرقة: **5.29 - Bengio et al. (Curriculum Learning)**

| المستوى | الاضطراب | الهدف |
|---------|----------|-------|
| 0 | بدون | baseline الأصلي |
| 1 | keyword_noise | ضوضاء خفيفة |
| 2 | sentence_injection | حقن جملة مشتتة |
| 3 | full_reformulation | إعادة صياغة كاملة |
| 4 | support_removal + contrast_weakening | إزالة الدعم + إضعاف التباين |
| 5 | evidence_reordering + stronger_shortcut_lures + structure_weakening | أقصى ضغط مركب |

### 4.2 المنطق

- المستويات 0-3 كانت موجودة سابقاً
- المستوى 4 يستهدف "الثقة الزائفة": يزيل الأدلة ويضعف الإشارات
- المستوى 5 يستهدف "المتانة الحقيقية": يعيد الترتيب + يضيف shortcuts + يزيل البنية
- التدرج يكشف "نقطة الانكسار" بدقة

### 4.3 الحجم الناتج

- 18 مهمة اصلية x 6 مستويات = 108 حالة في المنهج الكامل
- كل حالة تحمل tags و meta تحدد نوع ومستوى الاضطراب

---

## 5. تصميم تقرير مقاومة الاضطراب

### 5.1 المصدر

مصدر السرقة: **5.30 - Ribeiro et al. (CheckList)**

### 5.2 ما يحسبه التقرير

`perturbation_resistance.py` ينتج:

```python
{
    "by_perturbation_type": {
        "support_removal": {"success_rate": float, "count": int},
        "evidence_reordering": {"success_rate": float, "count": int},
        ...
    },
    "by_curriculum_level": {
        "0": {"success_rate": float, "count": int},
        "1": {"success_rate": float, "count": int},
        ...
    },
    "breaking_point": int,  # أول مستوى ينخفض فيه النجاح عن 0.8
    "by_family": {
        "comparison": {"resistance_score": float},
        "synthesis": {"resistance_score": float},
        "procedure": {"resistance_score": float}
    }
}
```

### 5.3 الاستخدام

- يكشف أي عامل اضطراب هو الأخطر
- يحدد "نقطة الانكسار" في المنهج
- يقارن مقاومة العائلات المختلفة
- يعطي baseline لأي تحسين مستقبلي

---

## 6. تصميم Anti-Shortcut Benchmark

### 6.1 المصدر

مصدر السرقة: **5.28 - Goodfellow et al. / Geirhos et al. (Adversarial Examples / Shortcut Learning)**

### 6.2 الفكرة

`anti_shortcut_benchmark.py` ينتج مهام لا يمكن النجاح فيها إلا بتجنب shortcuts فعلاً:
- لكل نوع forbidden_shortcut، 3+ مهام مصممة بحيث:
  - الشورتكت يعطي إجابة خاطئة
  - الإجابة الصحيحة تتطلب تجاوز الإغراء
  - الـ verification يتحقق من عدم استخدام الشورتكت

### 6.3 البنية

```python
# لكل عائلة (comparison, synthesis, procedure):
# - 3 مهام anti-shortcut
# - كل مهمة تحمل tag 'anti_shortcut'
# - كل مهمة تحدد forbidden_shortcuts في meta
```

### 6.4 التقاطع مع عوامل الاضطراب

- stronger_shortcut_lures يضيف shortcuts
- anti-shortcut benchmark يختبر المقاومة لها
- معاً يشكلان اختباراً كاملاً: هل النظام يقاوم الإغراء وهل ينجح بدونه؟

---

## 7. النتائج والملاحظات

### 7.1 ما تم تنفيذه

- 5 عوامل اضطراب جديدة في `taskcase_variants.py`
- 18 مهمة v6 في `prototype_v6_cases.py`
- منهج 6 مستويات ينتج 108 حالة
- v6 runner في `run_local_eval_v6.py`
- تقرير المقاومة في `perturbation_resistance.py`
- Anti-shortcut benchmark (9 مهام، 3 لكل عائلة)
- 27+ اختبار جديد يغطي كل المكونات

### 7.2 ملاحظة عن evidence_reordering

العامل يعمل فقط على نصوص تحتوي 3+ جمل. النصوص ذات الجملتين لا يمكن إعادة ترتيبها بشكل مفيد (لا يوجد "وسط" لعكسه).

---

## 8. الخلاصة

دورة ضغط التقييم حققت هدفها:
- وسعت قدرة النظام على اختبار نفسه
- أضافت أدوات كشف shortcuts جديدة
- رفعت سقف التحدي بمستويين إضافيين
- وثقت كل قرار بمرجع بحثي واضح (السرقات الشرعية)

النظام الآن يملك أدوات تقييم أقوى بكثير من المرحلة السابقة.

---

*نهاية مذكرة دورة ضغط التقييم*
