# Virtual-SIA - مذكرة دورة الاستفادة من النظريات
# Theory Leverage Cycle Implementation Memo

> Document Type: Implementation Decisions Memo
> Status: Current
> Date: 2026-06-01
> Cycle: Theory Leverage (Option B) - Local Theory Leverage

---

## 1. نظرة عامة (Overview)

هذه الدورة تضيف قدرة النظام على استخدام النظريات المحلية (LocalTheoryObject) كمحركات استباقية تؤثر في ثلاثة مسارات:

1. **التحقق (Verification - B1)**: تشديد معايير القبول عندما تتنبا النظرية بالفشل
2. **تفعيل المفاهيم (Concept Activation - B2)**: دفع المفاهيم المرتبطة بالنظرية وادخال مفاهيم قريبة من العتبة
3. **التوجيه (Routing - B3)**: رفع طبقة المعالجة عندما تتنبا النظرية بالصعوبة
4. **التنبؤ والتحديث (Prediction - B4)**: توليد تنبؤات قابلة للتكذيب وتحديث ثقة النظرية
5. **تفسير التناقضات (Contradiction - B5)**: فحص قدرة النظرية على تفسير التناقضات المكتشفة

الدورة كاملة مغلقة خلف بوابة `use_theory_leverage=False` (مطفاة تلقائيا).

---

## 2. قرارات التصميم (Design Decisions)

### 2.1 لماذا Gated (مغلقة بالافتراض)؟

| السبب | التفصيل |
|-------|---------|
| الحفاظ على السلوك المجمد | الـ 88 اختبار القائمة يجب ان تمر بدون اي تغيير |
| المقارنة المتحكمة | يمكن تشغيل with/without لقياس الفائدة |
| منع التغييرات غير المقصودة | لا تاثير على النتائج المحققة سابقا |
| الاتساق مع نمط anomaly_leverage | نفس نمط البوابة المستخدم في الدورة الثانية |

### 2.2 لماذا Laplace Smoothing؟

الصيغة: `predictive_value = (correct_predictions + 1) / (prediction_count + 2)`

| الخاصية | القيمة |
|---------|--------|
| القيمة الابتدائية | 0.5 (محايد) |
| بعد تنبؤ صحيح واحد | 0.667 |
| بعد تنبؤ خاطئ واحد | 0.333 |
| الحد الادنى الممكن | > 0.0 دائما (لا يقين مطلق بالفشل) |
| الحد الاقصى الممكن | < 1.0 دائما (لا يقين مطلق بالنجاح) |

**لماذا هذا الاختيار:**
- يتجنب القيم المتطرفة عندما تكون البيانات قليلة (cold start)
- بسيط حسابيا ولا يحتاج prior distribution
- مفهوم ومتوقع السلوك -- لا مفاجآت
- كافٍ لهدفنا الحالي (5-20 مهمة لكل نظرية)

### 2.3 لماذا Token Overlap للتنبؤ والتفسير؟

**get_theory_prediction_for_task**: تستخدم تداخل الرموز بين predictive_claims ونص المهمة لتحديد الملاءمة.

**check_theory_explains_contradiction**: تستخدم تداخل الرموز (عتبة 2+) بين claims ومحتوى التناقض.

| البديل | لماذا رفضناه |
|--------|-------------|
| Semantic embeddings | يحتاج نموذج خارجي، لا يتسق مع pure Python |
| Regex matching | هش جدا، لا يتعامل مع تنويعات اللغة |
| Exact string match | متشدد جدا، لن يجد تطابقات |
| Full NLP pipeline | تعقيد مفرط لهذه المرحلة |

**Token overlap بسيط ولكنه كافٍ** لان:
- النظريات المحلية تستخدم نفس مفردات المهام (same vocabulary space)
- العتبة المنخفضة (1 token للتنبؤ، 2 للتفسير) تضمن حساسية كافية
- Tokenizer بسيط (split + lowercase + strip punctuation) متسق مع concept engine

### 2.4 عتبات القرار

| القرار | العتبة | المبرر |
|--------|--------|--------|
| يمنع tier_0 | confidence >= 0.5 و predicts_difficulty | 0.5 = النظرية اثبتت جدارتها (اكثر من المحايد) |
| يفرض tier_2 | confidence >= 0.6 و predicts_failure | 0.6 = ثقة اعلى مطلوبة لفرض الطبقة الاغلى |
| Theory boost | +3 للمفاهيم في concept_refs | يكفي لرفع مفهوم من score 5 الى score 8 (فوق العتبة 7) |
| Theory admission | ضمن 2 نقطة من fam_min_score | يدخل مفاهيم بدرجة 5-6 اذا كانت مرتبطة بالنظرية |
| Contradiction explanation | تداخل 2+ رموز | يمنع التطابقات العشوائية مع حفظ الحساسية |
| Explanatory power increment | +0.1 لكل تفسير ناجح | تراكم تدريجي، يحتاج 10 تفسيرات للوصول الى 1.0 |

---

## 3. الهيكل المعماري (Architecture)

### 3.1 الملفات المعدلة

| الملف | نوع التغيير | الدوال المضافة |
|-------|------------|---------------|
| `virtual_sia/core/objects/theory.py` | Extension | 4 حقول جديدة في LocalTheoryObject |
| `virtual_sia/runtime/theory_runtime/apply.py` | Addition | get_theory_prediction_for_task, update_theory_predictive_value, check_theory_explains_contradiction |
| `virtual_sia/runtime/verification_runtime/service.py` | Addition | verify_output_theory_guided |
| `virtual_sia/runtime/concept_engine/apply.py` | Addition | select_applicable_concepts_theory_guided |
| `virtual_sia/runtime/economy_control/router.py` | Addition | choose_tier_theory_guided |
| `virtual_sia/runtime/pipeline/minimal_run.py` | Integration | تكامل كل الدوال ضمن run_minimal_pipeline |

### 3.2 الحقول الجديدة في LocalTheoryObject

```python
predictive_value: float = 0.5      # Laplace-smoothed prediction accuracy
prediction_count: int = 0          # Total predictions made
correct_predictions: int = 0       # Correct predictions count
explanatory_power: float = 0.0     # Contradiction explanation accumulator
```

### 3.3 قائمة الدوال الجديدة

| الدالة | الموقع | المدخلات الرئيسية | المخرج |
|--------|--------|------------------|--------|
| `get_theory_prediction_for_task` | theory_runtime/apply.py | theory, task_family, task_text | dict: predicts_failure, predicts_difficulty, confidence, relevant_claims |
| `update_theory_predictive_value` | theory_runtime/apply.py | theory, prediction_correct | None (mutates theory) |
| `check_theory_explains_contradiction` | theory_runtime/apply.py | theory, contradiction | bool (mutates theory.explanatory_power) |
| `verify_output_theory_guided` | verification_runtime/service.py | task_family, output_text, theory_prediction, ... | dict (verification result) |
| `select_applicable_concepts_theory_guided` | concept_engine/apply.py | task_family, task_text, concepts, theory, ... | (selected, decisions) |
| `choose_tier_theory_guided` | economy_control/router.py | task, blackboard, memory_pack, theory_prediction | TierDecisionObject |

---

## 4. نمط التكامل (Integration Pattern)

### 4.1 التطبقة مع Anomaly Leverage

```
Pipeline Flow:
1. Task ingestion
2. Memory retrieval
3. Theory selection (if use_theory_leverage=True)
4. Theory prediction (B4)
5. Tier routing:
   - Theory-guided first (if theory predicts difficulty/failure)
   - Anomaly-aware layers on top (if both active)
6. Concept selection:
   - Theory-guided (if use_theory_leverage + use_concepts)
   - OR base selection
7. Reasoning execution
8. Verification:
   - Theory-guided first (if theory predicts difficulty/failure)
   - Anomaly-aware layers on top (takes stricter result)
9. Post-processing:
   - Update theory predictive value (B4)
   - Check theory explains contradictions (B5)
10. Memory storage
```

### 4.2 قواعد الاولوية

| الوضع | السلوك |
|-------|--------|
| theory_leverage=False, anomaly_leverage=False | السلوك الاصلي المجمد |
| theory_leverage=True, anomaly_leverage=False | Theory-guided فقط |
| theory_leverage=False, anomaly_leverage=True | Anomaly-aware فقط (الدورة الثانية) |
| theory_leverage=True, anomaly_leverage=True | Theory-guided اولا، ثم anomaly-aware يطبق فوقه |

### 4.3 قاعدة "الاشد يفوز"

عند تفعيل كلا المسارين للتحقق:
1. يتم تطبيق verify_output_theory_guided اولا
2. اذا anomaly_severity > 0.5: يتم تطبيق verify_output_anomaly_aware ايضا
3. اذا نتيجة anomaly-aware اشد (not good_enough): تؤخذ كنتيجة نهائية
4. هذا يمنع ان يتجاوز theory-guided الحذر المطلوب عند وجود شذوذ فعلي

---

## 5. الدليل والتحقق (Evidence and Verification)

### 5.1 نتائج الاختبارات

| المجموعة | العدد | النتيجة |
|----------|-------|---------|
| الاختبارات القائمة (Cycle 1+2) | 88 | كلها تمر بنجاح |
| اختبارات Theory Leverage الجديدة | 38 | كلها تمر بنجاح |
| **المجموع** | **126** | **كلها تمر** |

### 5.2 حفظ الاساس (Baseline Preservation)

تم التحقق من ان:
- `run_minimal_pipeline('test')` مع `use_theory_leverage=False` ينتج نتائج مطابقة تماما للسلوك السابق
- theory_prediction = None و theory_predictive_value = None عند الاطفاء
- لا تاثير على مسارات anomaly_leverage الموجودة

### 5.3 التغطية الاختبارية

| الدالة | عدد الاختبارات | ما يتم اختباره |
|--------|--------------|---------------|
| get_theory_prediction_for_task | 4+ | تطابق/عدم تطابق claims مع task text |
| update_theory_predictive_value | 4+ | Laplace smoothing، تحديثات متعددة |
| check_theory_explains_contradiction | 3+ | تداخل/عدم تداخل، تحديث explanatory_power |
| verify_output_theory_guided | 4+ | وضع عادي، تنبؤ فشل، تنبؤ صعوبة |
| select_applicable_concepts_theory_guided | 3+ | boost، admission، عدم تاثير |
| choose_tier_theory_guided | 3+ | منع tier_0، فرض tier_2، لا تغيير |
| Pipeline integration | 4+ | on/off، مع نظريات، مع كلا المسارين |

---

## 6. ما لم نفعله (What We DID NOT Do)

### 6.1 شبكات بايزية كاملة (Full Bayesian Networks)
- **ماذا يعني**: نمذجة العلاقات الاحتمالية بين كل النظريات والمفاهيم والمهام في شبكة واحدة
- **لماذا لا**: تعقيد O(n^3) للاستدلال الدقيق، يحتاج مكتبات خارجية، مبالغة لـ 4 نظريات

### 6.2 عتبات ديناميكية (Dynamic Thresholds)
- **ماذا يعني**: تعديل عتبات القرار (0.5، 0.6) تلقائيا بناء على الاداء التراكمي
- **لماذا لا**: يجعل السلوك غير متوقع، يصعب التصحيح (debugging)، لا يوجد دليل كافٍ على العتبات المثلى

### 6.3 تنافس النظريات (Theory Competition/Selection Pressure)
- **ماذا يعني**: نظريات متعددة تتنافس على نفس المهمة، والاقوى تفوز وتحصل على مزيد من الفرص
- **لماذا لا**: حاليا نختار نظرية واحدة فقط (limit=1)، التنافس يحتاج اكثر من 4 نظريات ليكون ذا معنى

### 6.4 تكذيب واستبعاد النظرية (Theory Falsification/Retirement)
- **ماذا يعني**: عند انخفاض predictive_value تحت عتبة معينة، تُزال النظرية من الخدمة
- **لماذا لا**: لا نريد فقدان نظريات بشكل نهائي في مرحلة مبكرة، الاسترداد مكلف

### 6.5 تفسير سببي كامل (Full Causal Explanations)
- **ماذا يعني**: بناء رسم بياني سببي (causal graph) يشرح لماذا فشلت المهمة
- **لماذا لا**: يحتاج inference engine خارجي، خارج نطاق pure Python prototype

### 6.6 تنبؤ متعدد النظريات (Multi-Theory Ensemble Prediction)
- **ماذا يعني**: جمع تنبؤات عدة نظريات (weighted average) لانتاج تنبؤ مركب
- **لماذا لا**: حاليا limit=1، لا توجد آلية وزن بين النظريات، يمكن اضافتها لاحقا

---

*نهاية مذكرة دورة الاستفادة من النظريات*
