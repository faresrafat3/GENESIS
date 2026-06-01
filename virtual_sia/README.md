# Virtual-SIA

طبقة ذكاء تشغيلية فوق LLM APIs (harness-first cognitive agent). تختبر فرضيتين مركزيتين:
1. **Concept Formation** يتفوق على الاسترجاع وحده (retrieval-only).
2. **Cognitive Economy** يتفوق على مجرد تكبير الموديل (stronger-model-only scaling).

> ⚠️ **المرجع الأعلى للبنية:** `Virtual_SIA_Internal_Regime_Lock_AR.md` (قفل النظام الداخلي).
> عند أي تعارض في الوصف، القفل الداخلي ثم `Current_Regime_Status` هما المعتمدان.

---

## البنية: 3 طبقات

### الطبقة A — Core Epistemic Engine (النواة — مقفولة) 🔒
قلب القيمة، محكوم ومقاس. لا يُلمَس إلا بمبرر تجريبي.
- `runtime/task_ingress/` — تأطير المهمة (6 عائلات: comparison, synthesis, procedure, analysis, extraction, planning)
- `runtime/memory_os/` — تخزين/استرجاع
- `runtime/concept_engine/` — تكوين المفاهيم + selectivity حسب العائلة
- `runtime/economy_control/` — التوجيه الاقتصادي للـ tiers
- `runtime/verification_runtime/` — التحقق من العقود (contracts)
- `runtime/pipeline/minimal_run.py` — المنسّق

### الطبقة B — Governance Expansion (مُقيَّدة، كلها OFF افتراضيًا) 🧪
artifacts + plumbing، تأثير سلوكي خفيف غير مُثبَت بالكامل:
- contradiction · `use_anomaly_leverage` · `use_theory_leverage`
- `use_self_benchmarking` · `use_productive_forgetting`
- `use_identity_governance` · `use_paradigm_fork`

### الطبقة C — Interface / Infrastructure 🔌
- `api/` — REST API + OpenRouter adapter + sessions (production-facing)
- `persistence/` — SQLite persistence (production-facing)
- `eval/.../prototype_v7_*`, `run_real_llm_*`, `run_adversarial_*` — research-only

---

## المسار المعتمد (Canonical Path) — إجابة واحدة لا ستّة

```bash
# الـ runner المعتمد الوحيد لاختبار الأطروحة الأساسية:
python -m virtual_sia.eval.runners.run_local_eval_v3b_curriculum
```
- الشريحة الأساسية: `prototype_v3b_curriculum` (72 مهمة)
- أفضل condition: `condition_c_combined` (concept + economy) → success≈0.986، cost≈0.00068
- كل flags الحوكمة (الطبقة B) = **OFF** في هذا المسار.

### الشرائح المعتمدة (Official Slices)
- `primary_thesis_slice = prototype_v3b_curriculum` (72 task) — قياس الأداء الأقصى (B=OFF).
- `primary_diagnostic_slice = adversarial_hard_cases` (6 tasks) — قياس المتانة (تكشف قيمة الحوكمة B).

### التحقق الحقيقي مع LLM (research-only)
```bash
export OPENROUTER_API_KEY=...   # owl-alpha أو أي نموذج
python -m virtual_sia.eval.runners.run_adversarial_llm_eval   # أول دليل غير متشبّع: A=0% → B/C=50%
```

### شرائح/أدوات إضافية (تشخيصية)
```bash
python -m virtual_sia.eval.runners.run_local_eval_v4              # شريحة تشخيصية
python -m virtual_sia.eval.runners.run_selectivity_ablation       # معايرة المفاهيم
python -m virtual_sia.eval.runners.run_family_selectivity_ablation
```

---

## التشغيل والاختبار
- **Python:** 3.10+ مطلوب (يستخدم `dataclass(slots=True)`).
- **التبعيات:** لا شيء خارجي (stdlib فقط: `urllib`, `sqlite3`, `http.server`). `pytest` للتطوير فقط.
```bash
pip install -e ".[dev]"
pytest -q          # 424 اختبار
```

---

## خريطة التوثيق
| الغرض | الوثيقة |
|-------|---------|
| **القفل البنيوي (الأعلى)** | `Virtual_SIA_Internal_Regime_Lock_AR.md` |
| حالة النظام الحالية | `Virtual_SIA_Current_Regime_Status_AR.md` |
| المعمارية النظرية | `Virtual_SIA_Master_Architecture_AR.md` |
| سجل السرقات الموحّد (93) | `Virtual_SIA_Legitimate_Thefts_MASTER_INDEX_AR.md` |
| البرنامج البحثي (H1–H9) | `Virtual_SIA_Research_Program_AR.md` |
| الأدلة (LLM حقيقي) | `Virtual_SIA_Adversarial_Validation_Memo_AR.md` |

---

## ملاحظة
هذه research/execution prototype متقدمة (ليست production system مكتمل). الطبقة A مُثبتة
جزئيًا (H2, H6 الأقوى)؛ الطبقتان B وC قيد النضج. راجع القفل الداخلي قبل أي توسّع.
