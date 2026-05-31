# مذكرة تقييم LLM الحقيقي
# Virtual SIA Real LLM Evaluation Memo

> Document Type: Technical Evaluation Memo
> Date: 2026-05-31
> Status: Implemented

---

## 1. المشكلة

كل التقييمات السابقة في Virtual SIA كانت محاكاة (simulated): التحقق يتم بمقارنة نص
المخرجات مع كلمات مفتاحية محددة (markers) بدون تشغيل LLM حقيقي.

هذا يعني اننا لا نعرف:
- هل LLM حقيقي ينتج مخرجات تمر من التحقق؟
- هل concept hints تحسن جودة المخرجات فعليا؟
- هل theory hints تضيف قيمة فوق concept hints؟

## 2. المنهجية

### 2.1 التصميم التجريبي (A/B/C Conditions)

نشغل نفس المهام عبر 3 conditions:

| Condition | الوصف | المدخلات |
|-----------|--------|----------|
| A_raw | بدون اي اضافات | prompt فقط |
| B_concept | مع concept hints | prompt + concept_hints |
| C_full | الحوكمة الكاملة | prompt + concept_hints + theory_hints |

### 2.2 اختيار المهام

- 6 مهام (2 من كل عائلة: comparison, synthesis, procedure)
- من مجموعة prototype_v6_cases الصعبة
- المهام لها required_properties و forbidden_shortcuts محددة

### 2.3 المقاييس

- **concept_lift**: نسبة نجاح B_concept - نسبة نجاح A_raw
- **theory_lift**: نسبة نجاح C_full - نسبة نجاح B_concept
- **total_lift**: نسبة نجاح C_full - نسبة نجاح A_raw

### 2.4 التحقق

نستخدم نفس verify_output() من verification_runtime/service.py:
- فحص property_checks لكل required_property
- فحص shortcut_checks لكل forbidden_shortcut
- النتيجة: good_enough = True/False

## 3. التنفيذ

### 3.1 الملفات

| الملف | الغرض |
|-------|--------|
| `virtual_sia/api/config.py` | ثوابت API key و model |
| `virtual_sia/api/llm_adapter.py` | محول LLM مع تتبع التكلفة |
| `virtual_sia/api/llm_reasoning.py` | بناء prompts مع concept/theory hints |
| `virtual_sia/eval/runners/run_real_llm_eval.py` | محرك التقييم الحقيقي |

### 3.2 النموذج المستخدم

- **Model**: openrouter/owl-alpha
- **Provider**: OpenRouter API
- **تكلفة تقديرية**: ~$0.001 لكل مكالمة
- **اجمالي المكالمات**: 18 (6 مهام x 3 conditions)

### 3.3 بناء الـ Prompt

الـ prompt المُوسَّع (augmented) يتكون من:
1. قسم Relevant Concepts (اذا وُجدت hints)
2. قسم Applicable Theories (اذا وُجدت)
3. قسم Task (المهمة نفسها)
4. قسم Instructions (تعليمات استخدام المفاهيم)

### 3.4 تتبع التكلفة

LLMAdapter يتتبع:
- عدد المكالمات الكلي
- التكلفة التقديرية الاجمالية
- عدد المكالمات لكل model

## 4. السرقات الشرعية

### 5.73 - SWE-bench (Jimenez et al. 2024)
اخذنا: منهجية التقييم على مهام حقيقية مع مقارنة A/B
لم ناخذ: Full repository-level evaluation

### 5.74 - LATS (Zhou et al. 2024)
اخذنا: البروتوكول التجريبي لنفس prompts عبر configurations مختلفة
لم ناخذ: Tree search وMonte Carlo sampling

### 5.75 - DSPy (Khattab et al. 2024)
اخذنا: Metric-driven prompt optimization
لم ناخذ: Automatic prompt compilation

## 5. الحدود والقيود

- التقييم يعتمد على keyword matching لا semantic understanding
- owl-alpha قد لا يكون افضل model لهذه المهام
- 6 مهام فقط (عينة صغيرة)
- لا يوجد human evaluation للمخرجات
- التكلفة التقديرية غير دقيقة (نستخدم $0.001 ثابتة)

## 6. التشغيل

```bash
# تشغيل التقييم الحقيقي (يكلف مال!)
cd virtual_sia/eval/runners
python -m virtual_sia.eval.runners.run_real_llm_eval
```

النتائج تُحفظ في: `virtual_sia/eval/results/real_llm_eval_summary.json`

---

*نهاية المذكرة*
