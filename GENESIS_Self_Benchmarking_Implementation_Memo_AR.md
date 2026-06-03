# Virtual-GENESIS Self-Benchmarking Implementation Memo
# مذكرة تنفيذ التقييم الذاتي

> Document Type: Implementation Memo
> Status: Implemented
> Date: 2026-06-01
> Hypothesis: H8 - Self-Benchmarking (Tier S)

---

## 1. الغرض

هذه المذكرة توثق ما تم بناؤه لتنفيذ فرضية Self-Benchmarking (H8) من البرنامج البحثي.

الهدف: تحويل نظام التقييم من benchmark ثابت الى نظام تقييم ذاتي النمو يحول اشارات الفشل (anomaly candidates) الى ضغط تقييمي جديد.

المرجع النظري: `Virtual_SIA_Self_Benchmarking_Theory_AR.md` (القسم 1-17)

---

## 2. المكونات المنفذة

### 2.1 benchmark_generator.py
**المسار**: `virtual_genesis/eval/benchmark_generator.py`

يولد TaskCase objects تشخيصية من anomaly candidates. كل anomaly (property_gap, shortcut_pattern, contradiction_pattern) يتحول الى مهمة اختبار تستهدف اعادة انتاج نفس نمط الخلل.

### 2.2 blind_spot_discovery.py
**المسار**: `virtual_genesis/eval/reports/blind_spot_discovery.py`

يحلل تغطية التقييم عبر (family, perturbation_type, difficulty_class) ويكتشف:
- المناطق التي لم يصلها اي اختبار (untested_combinations)
- المناطق المشبوهة بنسبة نجاح 100% (suspiciously_easy_regions)
- نسبة التغطية الاجمالية (coverage_ratio)

### 2.3 diagnostic_value.py
**المسار**: `virtual_genesis/eval/reports/diagnostic_value.py`

يقيس القيمة التشخيصية لكل اختبار: كم يميز بين conditions مختلفة. اختبار يعطي نفس النتيجة تحت كل الظروف ليس تشخيصيا.

### 2.4 run_self_benchmark_cycle.py
**المسار**: `virtual_genesis/eval/runners/run_self_benchmark_cycle.py`

يربط الكل في دورة واحدة: تقييم اولي -> تحليل anomalies -> اكتشاف blind spots -> توليد اختبارات جديدة -> تقييم ثان -> قياس diagnostic value -> تقرير شامل.

---

## 3. قرارات التصميم

### 3.1 source_type mapping
بدلا من توليد عشوائي، كل نوع anomaly يتحول الى prompt مخصص:
- `property_gap` -> "Reproduce a scenario where required properties are not met..."
- `shortcut_pattern` -> "Reproduce a scenario where forbidden shortcuts are triggered..."
- `contradiction_pattern` -> "Reproduce a scenario where contradictions emerge..."

هذا يضمن ان الاختبار المولد يستهدف نفس نمط الخلل الذي اكتشفه الـ anomaly detector.

### 3.2 صيغة diagnostic value
```
diagnostic_value = 4 * p * (1 - p)
```
حيث p = نسبة النجاح عبر conditions. هذه الصيغة (variance of Bernoulli * 4) تعطي:
- 0.0 عندما كل conditions تنجح او كلها تفشل (لا تمييز)
- 1.0 عندما الانقسام 50/50 (اقصى تمييز)

### 3.3 coverage matrix approach
Coverage matrix تبنى من ثلاثة محاور: family, perturbation_type, difficulty_class. هذا يكشف الفجوات بشكل منهجي بدلا من الاعتماد على حدس المصمم.

### 3.4 difficulty_class mapping
Anomalies بـ severity >= 0.7 تتحول الى اختبارات "hard"، والباقي "medium". هذا يربط شدة الخلل بصعوبة الاختبار الناتج.

---

## 4. كيفية الاستخدام

```python
from virtual_genesis.eval.runners.run_self_benchmark_cycle import run_self_benchmark_cycle
from virtual_genesis.eval.task_sets.prototype_v6_cases import build_v6_cases

# تحضير مجموعة المهام
task_cases = build_v6_cases()

# تشغيل دورة التقييم الذاتي
report = run_self_benchmark_cycle(
    task_cases=task_cases,
    conditions=["baseline_0", "condition_c_combined"],
    use_self_benchmarking=True,
)

# النتائج
print(f"Anomalies found: {report['anomaly_candidates_count']}")
print(f"New cases generated: {report['new_cases_generated']}")
print(f"Coverage ratio: {report['blind_spot_report']['coverage_ratio']}")
print(f"Avg diagnostic value: {report['diagnostic_report']['avg_diagnostic_value']}")
```

لتعطيل التقييم الذاتي (الحصول فقط على النتائج الاساسية):
```python
report = run_self_benchmark_cycle(
    task_cases=task_cases,
    use_self_benchmarking=False,
)
# report يحتوي فقط على base_results
```

---

## 5. الحالة الحالية

- الميزة مبوبة خلف `use_self_benchmarking: bool = False` في run_self_benchmark_cycle
- **ليست** ضمن الـ frozen defaults حاليا
- لم تدخل بعد في الـ pipeline الاساسي (minimal_run.py)
- 39 اختبار يغطون جميع المكونات

---

## 6. الخطوات التالية

1. **ربط blind spots بـ auto-curriculum**: المناطق العمياء المكتشفة يمكن ان تتحول تلقائيا الى اهداف لتوليد مهام جديدة (بدلا من توليد من anomalies فقط)
2. **Benchmark Synthesis Engine** (القسم 17 من وثيقة النظرية): بناء محرك كامل يدير دورات توليد-تقييم-تنقية
3. **توصيل بالـ pipeline**: عند اثبات الفائدة، يمكن ان يعمل run_self_benchmark_cycle كـ background process يغذي الـ eval بمهام جديدة
4. **تجارب مقارنة**: تشغيل النظام مع/بدون self-benchmarking على فترة طويلة لقياس هل يتحسن الاداء

---

*نهاية مذكرة تنفيذ التقييم الذاتي*
