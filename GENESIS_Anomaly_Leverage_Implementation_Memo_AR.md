# Virtual-GENESIS - مذكرة تنفيذ الاستفادة من الشذوذ
# Anomaly Leverage Implementation Memo (Option A - Minimal)

> Document Type: Implementation Memo
> Status: Completed
> Date: 2026-06-01
> Cycle: Minimal Anomaly Leverage (A1-A3)

---

## 1. الغرض من هذه المذكرة

هذه المذكرة توثق تنفيذ **الاستفادة الدنيا من الشذوذ** (Minimal Anomaly Leverage) كما تم اتخاذ القرار في Decision Memo.

### 1.1 مرجع القرار

في Decision Memo (القسم 2.2)، تم تحديد أن:
> "anomaly candidates تتحول إلى شيء يتجاوز reporting"

وفي القسم 4.1 (Bottleneck D - Governance-to-control bridge):
> "كيف نحول contradictions/anomalies/theories من artifacts إلى control signals مفيدة دون overengineering؟"

### 1.2 القرار المتخذ

بدلاً من بناء full anomaly manager (الذي لا نوصي به الآن - القسم 7)، نفذنا **Minimal Anomaly Leverage**:
- الشذوذ يؤثر في السلوك لكن لا يتحكم فيه بالكامل
- مُفعّل خلف flag (`use_anomaly_leverage=False` افتراضياً)
- لا يغير السلوك الحالي المجمد إلا عند التفعيل الصريح

---

## 2. آلية قياس شدة الشذوذ (Severity Scoring)

### 2.1 المصدر

- **5.31 - Chandola et al. (Anomaly Detection Survey)**: تصنيف الشذوذ وقياس شدته
- **6.8 - Predictive Processing**: anomaly_severity = prediction error signal

### 2.2 التنفيذ

الدالة `compute_anomaly_severity_score()` في `virtual_genesis/runtime/anomaly_runtime/service.py`:

```python
def compute_anomaly_severity_score(candidates: list[AnomalyCandidate]) -> float:
    """
    تحسب شدة مركبة (0.0-1.0) بناءً على:
    - count_factor: عدد المرشحين (يتشبع عند 5)
    - max_severity: أقصى شدة بين المرشحين
    - diversity_factor: تنوع source_types
    """
```

### 2.3 المنطق

- **العدد**: كلما زاد عدد مرشحي الشذوذ، زادت احتمالية وجود مشكلة حقيقية
- **الشدة القصوى**: مرشح واحد شديد الخطورة يكفي لرفع النتيجة
- **التنوع**: شذوذ من مصادر متنوعة (property_gap + shortcut_pattern + family_failure) أخطر من نوع واحد متكرر

### 2.4 العلاقة بـ Predictive Processing

الـ severity هي ترجمة مباشرة لـ "prediction error magnitude":
- severity = 0.0: لا خطأ تنبؤي، النموذج يعمل كما هو متوقع
- severity = 0.5: خطأ تنبؤي متوسط، الواقع يختلف عن التوقع
- severity = 1.0: خطأ تنبؤي أقصى، النموذج الحالي فاشل هنا تماماً

---

## 3. التحقق الواعي بالشذوذ (Anomaly-Aware Verification)

### 3.1 المصدر

- **6.3 - Kuhn**: الشذوذ المتراكم يتطلب استجابة أقوى (ليس مجرد ملاحظة)
- **5.30 - Ribeiro et al. (CheckList)**: اختبار سلوكي أشد عند وجود إشارات خطر

### 3.2 التنفيذ

الدالة `verify_output_anomaly_aware()` في `virtual_genesis/runtime/verification_runtime/service.py`:

عند `anomaly_severity > 0.5`:
- **جميع** required_properties يجب أن تنجح (لا partial credit)
- يتطلب evidence markers إضافية
- يتطلب 2 primary_markers على الأقل (بدلاً من 1)

### 3.3 المنطق

عندما يرى النظام إشارات شذوذ سابقة:
- يعني أن هذا النوع من المهام قد فشل من قبل
- الثقة في "حسناً بما فيه الكفاية" يجب أن تنخفض
- التحقق الأشد يقلل احتمال تمرير إجابات ضعيفة

---

## 4. التوجيه الاقتصادي الواعي بالشذوذ (Anomaly-Aware Economy Routing)

### 4.1 المصدر

- **6.12 - Ashby (Requisite Variety)**: ضغط أعلى يتطلب تنوعاً أعلى في الاستجابة
- **5.32 - PagerDuty/Datadog**: تصعيد تلقائي بناءً على شدة الإشارة

### 4.2 التنفيذ: اختيار المستوى

الدالة `choose_tier_anomaly_aware()` في `virtual_genesis/runtime/economy_control/router.py`:

| anomaly_severity | السلوك |
|------------------|--------|
| 0.0 - 0.4 | اختيار عادي (choose_tier الأصلية) |
| 0.4 - 0.7 | لا يختار tier_0 أبداً (minimum tier_1) |
| > 0.7 | يفرض tier_2 (أقصى موارد) |

### 4.3 التنفيذ: التصعيد

الدالة `should_escalate_anomaly_aware()` في `virtual_genesis/runtime/economy_control/escalation.py`:

- عند `anomaly_severity > 0.5` و `current_tier != tier_2`: **دائماً يصعّد**
- المنطق: "عند الشك، صعّد" (من DevOps Incident Management)

### 4.4 لماذا Requisite Variety هنا؟

مبدأ Ashby يقول: "only variety can absorb variety"
- الشذوذ العالي = variety عالية في المشاكل المحتملة
- الاستجابة يجب أن تكون بـ variety مكافئة
- tier_2 (premium model) = أقصى variety متاحة في الاستجابة
- tier_0 (cheapest) = أقل variety -> لا تكفي لامتصاص الشذوذ العالي

---

## 5. تكامل الـ Pipeline

### 5.1 التنفيذ

في `virtual_genesis/runtime/pipeline/minimal_run.py`:

```python
def run_minimal_pipeline(prompt: str, *, use_anomaly_leverage: bool = False) -> dict:
    ...
    if use_anomaly_leverage:
        severity = compute_anomaly_severity_score(anomaly_candidates)
        # يمرر severity لكل مرحلة لاحقة
```

### 5.2 نقاط التكامل

1. **بعد استخراج anomaly_candidates**: حساب severity
2. **عند التحقق**: استخدام verify_output_anomaly_aware(severity)
3. **عند اختيار المستوى**: استخدام choose_tier_anomaly_aware(severity)
4. **عند قرار التصعيد**: استخدام should_escalate_anomaly_aware(severity)

### 5.3 الـ Gating Flag

`use_anomaly_leverage=False` افتراضياً:
- لا يغير أي سلوك مجمد حالياً
- يتطلب تفعيلاً صريحاً
- يحمي من تأثيرات غير مقصودة
- يسمح بمقارنة with/without في التقييم

---

## 6. الأدلة من الاختبارات

### 6.1 التغيير السلوكي المُثبت

الاختبارات تؤكد:
- عند severity=0.0: السلوك مطابق تماماً للنظام الأصلي
- عند severity=0.6: التحقق أشد (يرفض ما كان يقبله سابقاً)
- عند severity=0.6: التصعيد يحدث تلقائياً
- عند severity=0.8: tier_2 مفروض (لا خيار آخر)

### 6.2 عدد الاختبارات

- 27 اختبار جديد في `tests/test_anomaly_leverage.py`
- جميعها تمر بنجاح
- تغطي: severity scoring, verification, routing, escalation, pipeline integration

---

## 7. العلاقة بالقرارات السابقة

### 7.1 ما لم ننفذه (كما في Decision Memo القسم 7)

- لم ننفذ full anomaly manager
- لم ننفذ full local theory-guided control
- لم نبني anomaly-driven concept re-evaluation (مؤجل)

### 7.2 ما نفذناه

- **الحد الأدنى المفيد**: شذوذ -> شدة -> تأثير سلوكي محدود ومحسوب
- **لا overengineering**: ثلاث دوال بسيطة + تكامل pipeline
- **قابل للإيقاف**: flag واحد يعيد النظام لسلوكه الأصلي

### 7.3 الخطوة التالية المحتملة

بعد تجميع أدلة كافية من التشغيل مع `use_anomaly_leverage=True`:
- يمكن تفعيله كـ default
- يمكن إضافة anomaly-triggered concept re-evaluation
- يمكن بناء governance control cycle كاملة

---

## 8. ملخص السرقات المستخدمة

| المكون | المصدر الرئيسي | المبدأ |
|--------|---------------|--------|
| Severity scoring | 5.31 Chandola + 6.8 Predictive Processing | شدة = prediction error |
| Pattern matching | 6.3 Kuhn | تراكم الشذوذ -> تغيير سلوكي |
| Stricter verification | 6.3 Kuhn + 5.30 CheckList | شذوذ -> فحص أشد |
| Tier selection | 6.12 Ashby | variety absorbs variety |
| Escalation caution | 5.32 PagerDuty/Datadog | عند الشك، صعّد |

---

*نهاية مذكرة تنفيذ الاستفادة من الشذوذ*
