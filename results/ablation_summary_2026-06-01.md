# Cycle 5.1 — Governance Ablation Summary
# ملخص استئصال الحوكمة

> Date: 2026-06-01
> Question: هل الحوكمة (B) بتزود peak performance ولا robustness فقط؟
> Status: ✅ **LIVE RUN مُنفَّذ فعليًا** (sandbox · pyenv python 3.11.15) — يحلّ محل التقدير التحليلي السابق
> Runner: `virtual_genesis.eval.runners.run_local_eval_v3b_curriculum`
> Slice: `prototype_v3b_curriculum` (72 task) · Canonical condition: `condition_c_combined`

---

## 1) جدول المقارنة (3 runs على المسار المعتمد v3b_curriculum)

الأرقام مأخوذة من الـ canonical condition (`condition_c_combined`) في كل run:

| Run | success_rate | cost_avg | cost ×baseline | errors | الحالة |
|-----|:---:|:---:|:---:|:---:|:---:|
| **Baseline** (B=OFF) | **0.9861** | **0.000736** | 1.00× | 0 | ✅ live |
| **+ theory_leverage** | **0.9861** | **0.002167** | **2.94×** | 0 | ✅ live |
| **+ anomaly_leverage** | **1.0000** | **0.010000** | **13.59×** | 0 | ✅ live |

ملف الأرقام الخام: `results/v3b_baseline.json` · `results/v3b_theory.json` · `results/v3b_anomaly.json`
وملخّص مُجمَّع: `results/ablation_live_2026-06-01.json`

> **القراءة السريعة:**
> - **theory_leverage**: لم يحرّك النجاح إطلاقًا (98.61% → 98.61%) لكنه **ضاعف التكلفة ~3×**.
> - **anomaly_leverage**: رفع النجاح **98.61% → 100%** (أصلح المهمة الوحيدة الساقطة) لكن **بتكلفة ~13.6×** —
>   وهي بالضبط تكلفة `tier_2`-always (0.010). أي أنه فعليًا **صعّد كل المهام إلى الـ premium tier**.

> ⚠️ تصحيح مهم: التقدير التحليلي في النسخة السابقة من هذا الملف ادّعى أن الحالات الثلاث **متطابقة**
> (0.000736 للجميع). التشغيل الحيّ يكذّب هذا: التكلفة تختلف جوهريًا، و anomaly يرفع السقف فعلًا.
> **هذا هو سبب وجوب التشغيل الحيّ بدل الاستنتاج النظري.**

---

## 2) الإجابة المباشرة على سؤال الجودة

> **هل theory_leverage رفع الـ 98.6%؟ — لا.** بقي عند 98.61% بالضبط، وفقط رفع التكلفة ~2.94×.
>
> **هل anomaly_leverage رفع الـ 98.6%؟ — نعم، إلى 100%** — لكن **ليس مجانًا**: دفع تكلفة الـ premium
> الكاملة (~13.6×) لأنه صعّد القرار إلى `tier_2` على كل المسار.
>
> **إذن: هل الحوكمة B تزود peak ولا robustness؟**
> الحوكمة **لا تشتري ذروة رخيصة**. theory_leverage = متانة/انضباط بلا ذروة (تكلفة أعلى فقط).
> anomaly_leverage = الميل الوحيد الذي يلمس الذروة، لكنه يفعل ذلك بشراء أقصى مورد حسابي — وهذا
> سلوك **متانة (حذر تحت إغراء/خطر تاريخي)**، لا كفاءة ذروة. القيمة الحقيقية للحوكمة تظهر على
> الشريحة العدائية الصعبة (0%→50%، shortcut 33%→16.7%)، لا على شريحة v3b المشبعة.

---

## 3) التبرير من الكود (لماذا الأرقام طلعت كده)

من `runtime/pipeline/minimal_run.py` + الدوال المرتبطة:

**theory_leverage (98.61% بلا تغيير، تكلفة 2.94×):**
- `choose_tier_theory_guided()`: عند تنبؤ الصعوبة → يمنع `tier_0`؛ عند تنبؤ الفشل → يدفع نحو `tier_2`.
  → **يرفع التكلفة** (من 0.000736 إلى 0.002167) لكنه لا يحوّل فشلًا إلى نجاح على شريحة ناجحة أصلًا.
- `verify_output_theory_guided()`: تحقّق **أصرم** عند تنبؤ الفشل (markers + كل properties).
  الصرامة الأعلى = مرشّح أضيق، لا تُنشئ نجاحًا جديدًا. لذلك السقف ثابت.

**anomaly_leverage (100%، تكلفة 13.59× = premium-always):**
- يبني `anomaly_severity` من الذاكرات الساقطة تاريخيًا. مع تراكم الإخفاقات على v3b، تتجاوز الـ severity
  العتبة (>0.7) فيفرض `choose_tier_anomaly_aware` / المنطق المُركَّب `tier_2` على المسار كله.
- النتيجة: `cost_avg = 0.010` (مطابق تمامًا لـ `baseline_2_premium_always`)، والقدرة الحسابية الإضافية
  في `tier_2` + التحقق الأصرم أصلحت المهمة الساقطة الوحيدة → 100%.
- **ملاحظة دقيقة:** عند نفس التكلفة (0.010)، `baseline_2_premium_always` حقّق **86% فقط**، بينما
  anomaly_leverage حقّق **100%** — لأن الأخير يجمع premium + المفاهيم + انضباط الحوكمة. أي أن
  الحوكمة **تستثمر الـ premium بذكاء أعلى**، لكنها تظل تدفع سعر الـ premium الكامل.

**الخلاصة الميكانيكية:** آليات B تعمل على **التكلفة/الصرامة/الحذر**. الذروة الوحيدة الملموسة
(anomaly → 100%) تأتي حصرًا عبر **صرف أقصى مورد**، وهو منطق متانة لا منطق كفاءة.

---

## 4) هل كسرت الحوكمة أي اختبارات؟

- **لا.** الس‌ويت كامل: **424 passed in ~4.3s** بعد توصيل الـ flags (تشغيل حيّ بعد التعديل).
- التعديل كله **plumbing مُبوَّب (gated)**: أضفت `use_theory_leverage` / `use_anomaly_leverage`
  (default = `False`) إلى `run_condition` و`compare_conditions`، وقراءة env في الـ runner.
- المسار المعتمد (بدون env) **مطابق بايت-ببايت**: baseline الحيّ أعاد إنتاج 0.9861 / 0.000736 بالضبط.
- لم يُلمَس Core A، ولا أُضيف أي feature جديد؛ flags الحوكمة كانت موجودة سلفًا في الـ pipeline.

---

## 5) طريقة إعادة التشغيل (reproducible)

```bash
pyenv global 3.11.15
python -m pip install -e ".[dev]"

# Baseline (B=OFF) — المسار المعتمد
python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum > results/v3b_baseline.json

# theory_leverage فقط
VIRTUAL_SIA_USE_THEORY_LEVERAGE=true  python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum > results/v3b_theory.json

# anomaly_leverage فقط
VIRTUAL_SIA_USE_ANOMALY_LEVERAGE=true python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum > results/v3b_anomaly.json

pytest -q   # => 424 passed
```

> الـ flags مُبوَّبة عبر env (default OFF). تفعيلها يكتب ملفات مُلحَقة (`*_theory.json` / `*_anomaly.json`)
> في `eval/results/` ولا يلمس الـ canonical summary، حفاظًا على نظافة المسار المعتمد.

---

## 6) الخلاصة بجملة واحدة

> **الحوكمة (B) تشتري المتانة (robustness)، لا الذروة الرخيصة.** على v3b المشبعة:
> theory_leverage لا يرفع 98.6% (تكلفة ×3 فقط)، و anomaly_leverage يرفعها إلى 100% **فقط** بدفع
> أقصى تكلفة (×13.6 = premium-always). لذلك القرار المعماري سليم: **B تبقى OFF في المسار المعتمد
> (peak/efficiency)، وتُفعَّل حيث المتانة تستحق ثمنها** (الشريحة العدائية الصعبة).
