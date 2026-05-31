# Virtual-SIA: مذكرة تنفيذ حوكمة هوية الوكيل (H9)

> Document Type: Implementation Memo
> Status: Current
> Date: 2026-06-01
> Feature: Agent Identity Governance (H9)
> Gating: `use_identity_governance: bool = False`

---

## 1. ما تم بناؤه

### ID1: Identity Object (`AgentIdentityObject`)

**الملف**: `virtual_sia/core/objects/identity.py`

كائن هوية الوكيل كـ dataclass يحتوي على:
- `agent_id: str` - معرف فريد للوكيل
- `commitments: List[str]` - الالتزامات الاساسية (الدستور)
- `self_model: str` - وصف الوكيل لذاته
- `lineage: List[str]` - تاريخ التطور والتفريعات
- `drift_score: float` - مقياس الانحراف عن الالتزامات (0.0 - 1.0)
- `accountability_log: List[Dict]` - سجل القرارات والتبريرات

يُنشأ عبر classmethod `.create()` وفق النمط الموحد في المشروع.

### ID2: Drift Detection (كشف الانجراف)

**الملف**: `virtual_sia/runtime/identity_runtime/drift_detector.py`

آلية قياس انحراف السلوك الحالي عن الالتزامات المعلنة:
- **الآلية**: token overlap بين نص السلوك/القرار وبين الالتزامات
- **الحساب**: `1.0 - (overlap_tokens / max(commitment_tokens, 1))`
- **المخرج**: drift_score بين 0.0 (تطابق كامل) و 1.0 (انحراف كامل)
- كلما زاد التداخل اللفظي بين السلوك والالتزامات، انخفض الانحراف

### ID3: Commitment Ledger (سجل الالتزامات)

**الملف**: `virtual_sia/runtime/identity_runtime/commitment_ledger.py`

سجل يتتبع حالة كل التزام عبر الزمن:
- `active_commitments: List[str]` - الالتزامات النشطة حاليا
- `violations: List[Dict]` - الانتهاكات المسجلة مع السبب والتوقيت
- `evolutions: List[Dict]` - التطورات المشروعة (تعديل/اضافة/ازالة مبررة)

يسمح بتتبع تاريخ الالتزامات: هل تُحترم؟ هل تُنتهك؟ هل تتطور بشكل مشروع؟

### ID4: Identity-Aware Governance (حوكمة واعية بالهوية)

**الملف**: `virtual_sia/runtime/identity_runtime/governance.py`

فحص كل قرار كبير مقابل الالتزامات قبل التنفيذ:
- **المدخل**: القرار المقترح + identity object
- **العملية**: حساب drift_score للقرار مقابل الالتزامات
- **المخرج**: recommendation واحدة من ثلاث:
  - `continue` - الانحراف منخفض (drift < 0.5)، يمكن المتابعة
  - `review_decision` - الانحراف متوسط (0.5 <= drift <= 0.7)، يحتاج مراجعة
  - `halt_and_review` - الانحراف مرتفع (drift > 0.7)، يجب التوقف والمراجعة

### ID5: Pipeline Integration (تكامل مع خط الانابيب)

**الملف**: `virtual_sia/runtime/pipeline/minimal_run.py`

- **المعامل**: `use_identity_governance: bool = False`
- **الشرط**: يجب تمرير identity object عند التفعيل
- عند التفعيل: يحسب drift_score ويصدر recommendation قبل كل قرار
- النتائج تُضاف الى dict المخرجات: `identity_drift_score`, `identity_recommendation`

---

## 2. كيف يعمل

### 2.1 مسار التنفيذ

```
Input: task + identity_object + use_identity_governance=True
  |
  v
[1] compute_drift_score(task_text, identity.commitments)
  |
  v
[2] check_identity_alignment(drift_score)
  |
  v
[3] recommendation = continue | review_decision | halt_and_review
  |
  v
[4] add to output: drift_score + recommendation
  |
  v
Output: pipeline result + identity governance info
```

### 2.2 آلية كشف الانجراف

كشف الانجراف يعمل عبر token overlap:
1. يُقسَّم نص القرار/السلوك الى tokens (كلمات)
2. تُقسَّم الالتزامات الى tokens
3. يُحسب التقاطع (intersection) بين المجموعتين
4. drift_score = 1 - (حجم التقاطع / حجم tokens الالتزامات)

**مثال**: اذا الالتزامات تحتوي 10 tokens والقرار يتقاطع مع 7 منها، فـ drift = 1 - 7/10 = 0.3

---

## 3. استراتيجية البوابة (Gating Strategy)

- **الافتراضي**: `use_identity_governance = False` (معطل)
- **السبب**: الحفاظ على السلوك المجمد الحالي لكل الاختبارات القائمة
- **التفعيل**: يتطلب:
  1. تمرير `use_identity_governance=True` صراحةً
  2. تمرير `identity` object صالح
- **عند عدم التفعيل**: خط الانابيب يعمل كالمعتاد بدون اي تغيير
- **النمط**: مطابق لنمط `use_anomaly_leverage` و `use_theory_leverage`

---

## 4. الاتصال بالنظرية

مرجع: `Virtual_SIA_Agent_Identity_Theory_AR.md`

| القسم النظري | المكون المنفذ | العلاقة |
|-------------|-------------|---------|
| القسم 7: الهوية كاستمرارية الالتزامات | AgentIdentityObject.commitments | تنفيذ مباشر |
| القسم 10: آلية كشف الانجراف | compute_drift_score (token overlap) | تبسيط تشغيلي |
| القسم 16: سجل المساءلة | accountability_log + CommitmentLedger | تنفيذ مباشر |
| القسم 17: الحوكمة كشرط مسبق | check_identity_alignment + recommendations | تنفيذ مباشر |

**القسم 7** يحدد ان الهوية = استمرارية الالتزامات (وليس جوهر ثابت). المكون ينفذ هذا عبر جعل `commitments` هي الحامل الاساسي للهوية في الـ dataclass.

**القسم 10** يحدد آلية كشف الانجراف النظرية. التنفيذ يبسّط هذا الى token overlap كتقريب عملي قابل للقياس.

**القسم 16** يحدد ضرورة تسجيل كل قرار مع تبريره. المكون ينفذ هذا عبر accountability_log و CommitmentLedger.

**القسم 17** يحدد ان الحوكمة شرط مسبق لا يُتجاوز. المكون ينفذ هذا عبر gated governance check قبل كل قرار كبير.

---

## 5. ملخص الاختبارات

**الملف**: `tests/test_identity_governance.py`

| الصنف | عدد الاختبارات | ما يُختبر |
|-------|---------------|----------|
| TestAgentIdentityObject | 6 | انشاء الكائن، الحقول، القيم الافتراضية، create classmethod |
| TestDriftDetection | 6 | حساب drift_score، حالات حدية (تطابق كامل، انحراف كامل، فارغ) |
| TestCommitmentLedger | 6 | اضافة التزامات، تسجيل انتهاكات، تسجيل تطورات |
| TestIdentityGovernance | 6 | فحص المحاذاة، التوصيات الثلاث، حالات حدية |
| TestPipelineIntegration | 6 | التكامل مع الـ pipeline، التفعيل/التعطيل، المخرجات |

**المجموع**: 30 اختبار عبر 5 اصناف

---

## 6. القيود المعروفة

1. **عدم فلترة stop-words في التوكنة**: حساب drift_score لا يفلتر الكلمات الشائعة (the, is, a, ...) مما قد يضخم التقاطع في النصوص الانجليزية. هذا مقبول كتبسيط اولي.

2. **الحوكمة استشارية وليست مانعة**: `check_identity_alignment` يصدر recommendation لكنه لا يمنع فعليا تنفيذ القرار. القرار النهائي يبقى لمن يستدعي الـ pipeline. هذا تصميم مقصود (advisory not blocking).

3. **Token overlap كتقريب بسيط**: قياس الانحراف عبر تقاطع الكلمات تبسيط كبير. لا يلتقط المعنى الدلالي. نص يعني نفس الشيء بكلمات مختلفة سيظهر كانحراف عالٍ. مقبول كخطوة اولى.

4. **لا يوجد تاريخ drift**: drift_score يُحسب لحظيا ولا يُخزّن تاريخيا. لا يمكن حاليا رسم منحنى الانجراف عبر الزمن.

5. **الالتزامات ثابتة**: لا توجد حاليا آلية لتطوير الالتزامات ذاتها (meta-governance). التطور يتم فقط عبر CommitmentLedger.evolutions يدويا.

---

*نهاية مذكرة تنفيذ حوكمة هوية الوكيل*
