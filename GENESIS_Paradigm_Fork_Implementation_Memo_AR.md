# Virtual-GENESIS: مذكرة تنفيذ التفريع النموذجي / إعادة التصميم الذاتي

> Document Type: Implementation Memo
> Status: Current
> Date: 2026-06-01
> Feature: Paradigm Forking / Self-Redesign
> Gating: `use_paradigm_fork: bool = False`

---

## 1. ما تم بناؤه

### PF1: Crisis Detection (كشف الأزمة)

**الملف**: `virtual_genesis/runtime/paradigm_runtime/service.py`

نظام مراقبة يكشف متى يصل الوكيل الى ازمة بنيوية تستدعي اعادة تصميم:

- **ثلاثة مؤشرات مُراقبة**:
  1. `anomaly_count` - عدد الشذوذات المتراكمة (من anomaly store)
  2. `theory_failures` - عدد النظريات الفاشلة (predictive_value < 0.4)
  3. `identity_drift` - مقياس انجراف الهوية (drift_score)

- **ثلاثة مستويات**:
  - `normal` - لا ازمة، اصلاح محلي كافٍ
  - `warning` - مؤشرات مقلقة، شرطان من ثلاثة متحققان
  - `crisis` - ازمة كاملة، الشروط الثلاثة متحققة، fork مبرر

- **عتبات الازمة**:
  - anomaly_count >= 5
  - theory_failures >= 2
  - identity_drift > 0.6

### PF2: Paradigm Fork Protocol (بروتوكول التفريع النموذجي)

**الملف**: `virtual_genesis/runtime/paradigm_runtime/service.py`

آلية اقتراح وتنفيذ التفريع عند ثبوت الازمة:

- **`propose_fork()`** - يقترح تفريع مع:
  - `preserved`: ما يبقى في الهوية الجديدة (الالتزامات الناجحة، النظريات الصالحة)
  - `discarded`: ما يُؤرشف (السياسات الفاشلة، النظريات المنحطة)
  - `justification`: تبرير واضح لسبب التفريع

- **`execute_fork()`** - ينفذ التفريع فعليا:
  - ينشئ identity object جديد
  - يحتفظ بالـ preserved في الهوية الجديدة
  - يؤرشف الـ discarded في `archived_policies`
  - يضيف الـ fork الى lineage

### PF3: Fork Safety (حراسات الأمان)

**الملف**: `virtual_genesis/runtime/paradigm_runtime/service.py`

حراسات تمنع التفريع غير المبرر او المتكرر:

- **`MINIMUM_CYCLES_BETWEEN_FORKS = 10`** - حد ادنى 10 دورات بين تفريعين
- **justification مطلوب** - لا يُقبل fork بدون تبرير نصي
- **crisis level مطلوب** - لا fork الا اذا detect_crisis اعاد "crisis"
- **lineage محفوظ** - كل fork يسجل في lineage مع وصف وتوقيت
- **no overlap** - الـ preserved والـ discarded لا يتداخلان

---

## 2. كيف يعمل كشف الأزمة

### 2.1 المسار الكامل

```
Input: anomaly_store + theory_registry + identity_object
  |
  v
[1] count anomalies from store (anomaly_count)
  |
  v
[2] count failing theories: predictive_value < 0.4 AND prediction_count > 0
  |
  v
[3] read identity drift_score
  |
  v
[4] evaluate conditions:
    - anomaly_count >= 5?
    - theory_failures >= 2?
    - identity_drift > 0.6?
  |
  v
[5] determine level:
    - 3/3 conditions met -> "crisis"
    - 2/3 conditions met -> "warning"
    - 0-1/3 conditions met -> "normal"
  |
  v
Output: CrisisLevel + indicators dict
```

### 2.2 لماذا ثلاثة مؤشرات معا؟

التصميم يتطلب تحقق **الثلاثة** للأزمة الكاملة لان:
- شذوذات كثيرة وحدها قد تكون ضوضاء طبيعية
- فشل نظريات وحده قد يكون مشكلة محلية في نظرية واحدة
- انجراف هوية وحده قد يكون تطور طبيعي مشروع
- **التراكم المشترك** هو ما يميز الازمة البنيوية عن المشاكل المحلية

هذا مستوحى مباشرة من Kuhn: ليس الشذوذ المفرد بل تراكم الشذوذات مع عجز النموذج عن الاستيعاب هو ما يولد الازمة.

---

## 3. خطوات بروتوكول التفريع

### 3.1 الخطوة 1: propose_fork

```
Input: crisis_indicators + identity_object + justification
  |
  v
[Safety Check 1] crisis_level == "crisis"? (else reject)
  |
  v
[Safety Check 2] justification non-empty? (else reject)
  |
  v
[Safety Check 3] cycles_since_last_fork >= MINIMUM_CYCLES_BETWEEN_FORKS? (else reject)
  |
  v
[Compute] determine preserved (successful commitments, theories with good predictive_value)
[Compute] determine discarded (violated commitments, theories with predictive_value < 0.4)
  |
  v
Output: ForkProposal(preserved, discarded, justification, approved=True/False)
```

### 3.2 الخطوة 2: execute_fork

```
Input: approved ForkProposal + current identity
  |
  v
[1] Create new identity with preserved commitments
[2] Archive discarded items in archived_policies
[3] Add fork event to lineage
[4] Reset drift_score to 0.0
[5] Update accountability_log
  |
  v
Output: new AgentIdentityObject (forked)
```

---

## 4. حراسات الأمان

| الحراسة | الهدف | التنفيذ |
|---------|-------|--------|
| Justification Required | منع التفريع العشوائي | fork مرفوض اذا justification فارغ |
| Minimum Cycle Gap (10) | منع التغيير المتكرر (punctuated equilibrium) | عداد دورات منذ آخر fork |
| Crisis Level Required | التفريع فقط عند ازمة حقيقية | الشروط الثلاثة يجب ان تتحقق |
| No Overlap | وضوح ما يبقى وما يُزال | preserved و discarded لا يتقاطعان |
| Lineage Preserved | عدم فقدان التاريخ | كل fork يسجل مع الوقت والسبب |

### 4.1 لماذا MINIMUM_CYCLES_BETWEEN_FORKS = 10؟

- يمنع "oscillation" - التأرجح بين حالتين دون استقرار
- يعطي الهوية الجديدة وقتا كافيا لاثبات نفسها
- يعكس مبدأ punctuated equilibrium: الاستقرار هو القاعدة، والتفريع استثناء
- 10 دورات كافية لتقييم ما اذا كان التفريع ناجحا ام لا

---

## 5. الاتصال بالنظرية

مرجع: `Virtual_SIA_Anomaly_Crisis_Paradigm_Theory_AR.md`

| القسم النظري | المكون المنفذ | العلاقة |
|-------------|-------------|---------|
| القسم 9: تراكم الشذوذات | anomaly_count >= 5 | تنفيذ مباشر بعتبة محددة |
| القسم 11: مؤشرات انحطاط البرنامج | theory_failures (predictive_value < 0.4) | تبسيط تشغيلي لـ Lakatos |
| القسم 13: بروتوكول التفريع | propose_fork + execute_fork | تنفيذ مباشر |
| القسم 14: حراسات الامان | MINIMUM_CYCLES + justification + crisis-only | تنفيذ مباشر |

**القسم 9** يحدد ان تراكم الشذوذات فوق حد معين هو اشارة ازمة. التنفيذ يحدد الحد بـ 5 كقيمة عملية.

**القسم 11** يحدد ان فشل النظريات في التنبؤ يشير الى انحطاط. التنفيذ يستخدم predictive_value < 0.4 كعتبة الفشل.

**القسم 13** يحدد بروتوكول التفريع النظري. التنفيذ يترجمه الى propose_fork (اقتراح) + execute_fork (تنفيذ) كخطوتين منفصلتين.

**القسم 14** يحدد حراسات الامان النظرية. التنفيذ يترجمها الى قيود محددة قابلة للفحص آليا.

---

## 6. ملخص الاختبارات

**الملف**: `tests/test_paradigm_fork.py`

| الصنف | عدد الاختبارات | ما يُختبر |
|-------|---------------|----------|
| TestCrisisDetection | 6 | كشف المستويات الثلاثة، العتبات، الحالات الحدية |
| TestForkProposal | 6 | اقتراح التفريع، الرفض عند عدم الازمة، preserved vs discarded |
| TestForkExecution | 5 | تنفيذ التفريع، الهوية الجديدة، الارشفة، السلالة |
| TestForkSafety | 4 | الحد الادنى للدورات، التبرير المطلوب، منع التكرار |

**المجموع**: 21 اختبار عبر 4 اصناف

---

## 7. القيود المعروفة

1. **عتبات ثابتة (Fixed Thresholds)**: العتبات (anomaly >= 5, failures >= 2, drift > 0.6) ثابتة في الكود. لا تتكيف مع حجم النظام او تاريخه. قد تحتاج تعديل مع نمو المشروع.

2. **تاريخ شذوذات بسيط من المخزن**: anomaly_count يأتي من anomaly store ببساطة (عدد). لا تمييز بين شذوذات قديمة وجديدة، ولا وزن حسب الخطورة.

3. **لا تحليل فعلي لطبقة النموذج**: الـ fork يغير الهوية (commitments, policies) لكنه لا يغير فعليا بنية الكود او الخوارزميات. هو fork على مستوى البيانات الوصفية (metadata level).

4. **لا مقارنة بين مسارات**: بعد التفريع، لا توجد آلية لمقارنة اداء الهوية الجديدة مع الهوية القديمة. لا A/B testing.

5. **Archived policies غير قابلة للاسترداد**: ما يُؤرشف في discarded لا توجد حاليا آلية لاعادته. الارشفة نهائية (one-way).

6. **لا يوجد consensus mechanism**: قرار التفريع يتم آليا عند تحقق الشروط. لا يوجد "تصويت" او مراجعة خارجية قبل التنفيذ (الحراسات الآلية هي البديل).

---

## 8. التكامل مع خط الأنابيب

**المعامل**: `use_paradigm_fork: bool = False`

عند التفعيل في `run_minimal_pipeline`:
1. يُحسب anomaly_count من anomaly_candidates
2. يُحسب theory_failures من theory_registry
3. يُقرأ drift_score من identity object (اذا متوفر)
4. يُستدعى detect_crisis مع المؤشرات الثلاثة
5. اذا crisis: يُقترح fork تلقائيا (لكن لا يُنفذ بدون تاكيد)
6. النتائج تُضاف الى المخرجات: `crisis_level`, `crisis_indicators`

**ملاحظة**: التنفيذ الفعلي للـ fork (`execute_fork`) لا يحدث تلقائيا في الـ pipeline. يُقترح فقط ويعود القرار للمستدعي.

---

*نهاية مذكرة تنفيذ التفريع النموذجي*
