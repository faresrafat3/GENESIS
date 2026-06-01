# Virtual-SIA — قفل النظام الداخلي
# Internal Regime Lock (Single Source of Architectural Truth)

> Document Type: Internal Regime Lock / Coherence Guard
> Status: AUTHORITATIVE — يعلو على أي وصف آخر عند التعارض
> Date: 2026-06-01
> Purpose: حماية اتساع المشروع (anti-sprawl) لا إضافة قدرات

---

## 0) لماذا هذه الوثيقة؟ (تشخيص المرحلة)

المشروع توسّع بسرعة عبر عدة جبهات في وقت قصير:
broader domain · real-world upgrades · API · persistence · identity governance ·
anomaly leverage · paradigm forking · real-LLM eval.

هذا قوي، لكنه أدخل المشروع في **منطقة خطر جديدة: التشعّب (platform sprawl)** —
الخطر لم يعد "نقص أفكار" بل "تحوّل المنظومة إلى عدة مشاريع فرعية داخل repo واحد بلا
hierarchy واضحة".

**العلاج ليس تنظيرًا جديدًا ولا features جديدة، بل قفل داخلي** يحدد بوضوح:
ما هو النواة؟ ما هو التوسّع الاختياري؟ ما هو الإنتاجي؟ ما هو البحثي فقط؟ ما هو المؤقت؟
وما هو الـ regime المعتمد؟

> هذه الوثيقة هي **مرجع الاتساع**: أي توسّع قادم يجب أن يُقاس مقابلها، لا أن يسحب النواة بعيدًا.

---

## 1) الطبقات الثلاث للمشروع (التصنيف البنيوي المعتمد)

### الطبقة A — Core Epistemic Engine (النواة — قلب القيمة) 🔒 مقفولة
هذه الطبقة هي **مركز الثقل**، ويجب أن تبقى محكومة وواضحة ومقاسة. لا تُلمَس إلا بمبرر تجريبي.

| المكوّن | الموقع | الحالة |
|---------|--------|--------|
| Task framing / ingress | `runtime/task_ingress/` | 🔒 مقفول |
| Memory OS (تخزين/استرجاع) | `runtime/memory_os/store.py`, `retriever.py` | 🔒 مقفول |
| Concept formation + selectivity | `runtime/concept_engine/` | 🔒 مقفول |
| Economy-aware routing | `runtime/economy_control/router.py`, `escalation.py` | 🔒 مقفول |
| Verification (contracts) | `runtime/verification_runtime/` | 🔒 مقفول |
| Blackboard | `runtime/blackboard_core/` | 🔒 مقفول |
| Pipeline orchestrator | `runtime/pipeline/minimal_run.py` | 🔒 مقفول |
| Evaluation regimes (v3b primary) | `eval/runners/`, `eval/task_sets/` | 🔒 مقفول |

### الطبقة B — Governance Expansion (توسّع الحوكمة) 🧪 تجريبية/مُقيَّدة
موجودة كـ artifacts + plumbing، وتأثيرها السلوكي **خفيف وغير مُثبَت بالكامل**. كلها **gated (OFF افتراضيًا)**.

| المكوّن | البوابة (flag) | مستوى النضج |
|---------|----------------|-------------|
| Contradiction runtime | داخلي | 🟡 plumbing |
| Anomaly leverage | `use_anomaly_leverage=False` | 🟡 مُقيَّد |
| Theory leverage | `use_theory_leverage=False` | 🟡 مُقيَّد |
| Self-benchmarking | `use_self_benchmarking=False` | 🟡 مُقيَّد |
| Productive forgetting | `use_productive_forgetting=False` | 🟡 مُقيَّد |
| Identity governance | `use_identity_governance=False` | 🟡 مُقيَّد |
| Paradigm forking | `use_paradigm_fork=False` | 🟡 مُقيَّد |

> **قاعدة الطبقة B:** أي flag هنا يبقى OFF في الـ canonical path حتى يُثبَت تجريبيًا أنه يضيف قيمة.

### الطبقة C — Interface / Infrastructure Expansion (الواجهة/البنية) 🔌 production-facing / مساعِدة
أدوات تخدم التشغيل والتوسّع، **لا** تُعرّف القيمة العلمية للمشروع.

| المكوّن | الموقع | التصنيف |
|---------|--------|---------|
| REST API | `api/app.py` | production-facing |
| LLM adapter (OpenRouter) | `api/llm_adapter.py`, `llm_reasoning.py` | production-facing |
| Session management | `api/session.py` | production-facing |
| SQLite persistence | `persistence/` | production-facing |
| Broader-domain eval | `eval/.../prototype_v7_*` | research-only |
| Real-LLM eval runners | `eval/runners/run_real_llm_*`, `run_adversarial_*` | research-only |

> **القاعدة الذهبية:** الطبقة A لا تعتمد على B أو C. النواة تعمل وحدها. B وC اختياريتان.

---

## 2) المسار المعتمد الحالي (Current Canonical Path)

> لو سُئلت: "شغّل أفضل نسخة حالية واختبر الأطروحة الأساسية" — هذه **الإجابة الواحدة**، لا ستّ إجابات.

### 2.1 الـ Canonical Runner (واحد فقط)
```bash
python -m virtual_sia.eval.runners.run_local_eval_v3b_curriculum
```

### 2.2 الـ Canonical Evidence Path — الشرائح المعتمدة (Official Slices)
- **`primary_thesis_slice = prototype_v3b_curriculum`** (72 task) — شريحة الأطروحة الأساسية (peak performance، مع B=OFF).
- **`primary_diagnostic_slice = adversarial_hard_cases`** (6 tasks) — الشريحة التشخيصية الرسمية (robustness، تكشف قيمة B).
- **شريحة تشخيصية ثانوية:** `prototype_v4_cases`
- **شرائح المعايرة:** v2 / v3
- **التحقق الحقيقي (LLM):** `run_adversarial_llm_eval` (أول دليل غير متشبّع: A=0% → B/C=50%)

> **التمييز الجوهري:** الشريحة الأساسية تقيس **الأداء الأقصى** (هل النظام يحل المهام؟)، والشريحة
> التشخيصية تقيس **المتانة** (هل يقاوم الاختصارات تحت الإغراء؟). الحوكمة B تُقيَّم على الثانية لا الأولى.

### 2.3 الـ Canonical Configuration (defaults مجمّدة)
```python
# concept_engine/config.py
DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = 1
DEFAULT_MIN_ACTIVATION_SCORE = 7
DEFAULT_FAMILY_SELECTIVITY = {
    'comparison': {'max_active': 1, 'min_score': 7},   # contract_heavy
    'synthesis':  {'max_active': 2, 'min_score': 7},   # semantic_balanced
    'procedure':  {'max_active': 0, 'min_score': 99},  # structural_only
}
# pipeline: كل flags الحوكمة = False في المسار المعتمد
```

### 2.4 الـ Canonical Best Condition
**`condition_c_combined`** (concept-aware + economy-aware) — أفضل مسار تشغيلي مُثبَت:
success=0.986، cost=0.00068 على v3b_curriculum.

---

## 3) إجابات الأسئلة الخمسة (مراجعة ذاتية صريحة)

| السؤال | الإجابة الصريحة |
|--------|------------------|
| 1. هل ما زالت هناك primary thesis regime واحدة؟ | **نعم** — `prototype_v3b_curriculum` + `condition_c_combined`. لم تتغيّر. |
| 2. هل API + persistence + broader domain تخدم الـ core theses؟ | **جزئيًا** — persistence تخدم H1/H3 (التراكم)، broader domain تخدم H2 (النقل)، لكن API مسار C مستقل لا يخدم الأطروحة مباشرة. مُصنَّف بوضوح الآن. |
| 3. هل layers الحوكمة دخلت أسرع من نضج الأدلة؟ | **نعم، باعتراف** — لذلك كلها **gated OFF** ومُصنَّفة 🟡 في الطبقة B. لا تُفعَّل في المسار المعتمد. |
| 4. هل هناك current canonical path؟ | **نعم الآن** — راجع §2: runner واحد، evidence path واحد، defaults واحدة، condition واحدة. |
| 5. هل الـ docs تعكس الـ code؟ | **لم تكن** — الـ README كان متأخرًا. تمّت مزامنته مع هذا القفل (راجع `virtual_sia/README.md`). |

---

## 4) خريطة التوثيق المعتمدة (Canonical Docs Map)

| الغرض | الوثيقة المرجعية |
|-------|------------------|
| **القفل البنيوي (هذه)** | `Virtual_SIA_Internal_Regime_Lock_AR.md` ← الأعلى عند التعارض |
| المعمارية النظرية الكاملة | `Virtual_SIA_Master_Architecture_AR.md` |
| حالة النظام الحالية | `Virtual_SIA_Current_Regime_Status_AR.md` |
| سجل السرقات الموحّد | `Virtual_SIA_Legitimate_Thefts_MASTER_INDEX_AR.md` |
| البرنامج البحثي + الفرضيات | `Virtual_SIA_Research_Program_AR.md` |
| الأدلة التجريبية (محاكاة) | `Virtual_SIA_Current_Evidence_Package_AR.md` |
| الأدلة التجريبية (LLM حقيقي) | `Virtual_SIA_Adversarial_Validation_Memo_AR.md` |
| قرار التثبيت | `Virtual_SIA_Decision_Memo_AR.md` |

> **عند التعارض بين أي وثيقتين:** هذا القفل ثم `Current_Regime_Status` هما المرجع.

---

## 5) قواعد التوسّع المستقبلي (Anti-Sprawl Rules)

1. **لا توسّع في الطبقة A** إلا بمبرر تجريبي مقاس (ablation يثبت تحسنًا).
2. **أي flag في الطبقة B** يبقى OFF افتراضيًا حتى يثبت قيمته على الـ canonical evidence path.
3. **الطبقة C لا تدخل المسار المعتمد** — تبقى production/research-only منفصلة.
4. **كل expansion جديد** يجب أن يُصنَّف فورًا (A/B/C) ويُسجَّل هنا.
5. **كل feature جديدة** تتبع منهجية السرقة الشرعية (مصدر + ما أُخذ + ما أصبح).
6. **تحديث هذا القفل + الـ README** شرط لقبول أي توسّع كبير.

---

## 6) السرقات الشرعية لفكرة "القفل الداخلي" نفسها

> حتى منهجيتنا في حماية الاتساع مسروقة بوعي — تطبيقًا لمبدأ المشروع.

## 5.81 من Model Cards (Mitchell et al. 2019, Google)
### ما الذي أخذناه؟
- فكرة توثيق "بطاقة" رسمية تحدد النطاق المعتمد للنظام، استخدامه المقصود، وحدوده، كمرجع واحد.
- [Model Cards](https://arxiv.org/abs/1810.03993)
### ما الذي لم نأخذه الآن؟
- حقول الإنصاف/التحيّز الديموغرافي وبطاقات per-model القياسية.
### ماذا أصبح عندنا؟
- هذا القفل الداخلي كـ "بطاقة معمارية" واحدة تحدد النواة والنطاق والحدود.

## 5.82 من Golden Configuration / Configuration Baselines (ITIL / NIST SP 800-128)
### ما الذي أخذناه؟
- مفهوم "التهيئة الذهبية" المجمّدة كخط أساس مرجعي، وأي انحراف عنها يجب أن يُبرَّر.
- [NIST SP 800-128](https://csrc.nist.gov/pubs/sp/800/128/final)
### ما الذي لم نأخذه الآن؟
- أدوات الـ configuration drift detection الآلية.
### ماذا أصبح عندنا؟
- الـ Canonical Configuration المجمّدة في §2.3 + قاعدة "كل flag حوكمة OFF افتراضيًا".

## 5.83 من Semantic Versioning + Trunk-Based Release Trains (Preston-Werner)
### ما الذي أخذناه؟
- التمييز بين النواة المستقرة (stable trunk) والتوسّعات (feature branches) التي لا تدخل النواة قبل النضج.
- [SemVer](https://semver.org/)
### ما الذي لم نأخذه الآن؟
- أرقام الإصدار الدلالية الكاملة وأتمتة الـ release.
### ماذا أصبح عندنا؟
- التصنيف A/B/C + قواعد منع التشعّب في §5 (النواة مستقرة، B/C لا تسحبها).

---

## 7) الخلاصة بجملة واحدة

> المشروع الآن أقوى من مجرد prototype بحثية، ويحتاج قدرًا مساويًا من **"حماية الاتساع"**
> مثلما احتاج سابقًا **"حماية الفكرة"**. هذا القفل هو أداة الحماية: نواة A مقفولة وواضحة
> ومقاسة، حوكمة B مُقيَّدة وموثّقة، بنية C منفصلة ومُصنَّفة — ومسار معتمد واحد لا ستّة.

---

*نهاية قفل النظام الداخلي — المرجع الأعلى للاتساع البنيوي في Virtual-SIA.*
