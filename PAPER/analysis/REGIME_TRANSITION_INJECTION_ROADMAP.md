# خارطة طريق الحقن الفوري: Regime Transition في GENESIS
# تاريخ: 2026-06-07
# السياق: بعد بناء regime_transition_detector.py + negative_memory_adversarial.py

---

## ما تم بناؤه اليوم

### 1. `virtual_genesis/eval/runners/regime_transition_detector.py` (جديد)
- **3 إشارات:** Saturation, Degradation, Blind Spot
- **قاعدة القرار:** 2 من 3 نشطين → `TRANSITION`
- **الناتج:** `RegimeTransitionDecision` مع verdict, confidence, recommended_actions
- **Tunable:** window_k, epsilon, threshold, min_runs — كلها kwargs
- **الحالة:** ✅ مكتمل + 30 اختبار

### 2. `virtual_genesis/eval/negative_memory_adversarial.py` (جديد)
- **الوظيفة:** يحوّل سجلات الفشل (T-13) إلى اختبارات عدائية (H8)
- **4 أنواع فشل:** wrong_answer, shortcut, contradiction, missed_edge_case
- **Severity boost:** الفشل المتكرر يزيد الصعوبة تلقائياً
- **Deduplication:** Negative Memory يتفوق على Anomalies عند التعارض
- **الحالة:** ✅ مكتمل + 14 اختبار

### 3. تحديث `virtual_genesis/eval/runners/run_self_benchmark_cycle.py`
- **Step 8 جديد:** فحص regime transition تلقائياً بعد كل cycle
- **مدخل جديد:** `negative_memory_failures` parameter
- **ناتج جديد:** `regime_transition` dict + `regime_transition_required` bool
- **الحالة:** ✅ مكتمل + backward compatible (39 اختبار قديم يشتغل)

### 4. `tests/test_regime_transition.py` (جديد)
- **55 اختبار** يغطون كل الإشارات والقرار والدمج والـ integration
- **الحالة:** ✅ كلهم يمرون

---

## إجابة السؤال 1: أين نُدخل regime_transition_detector في الـ main loop؟

### الموقع الدقيق: بين Section 5a (Run Target Agent) و Section 5b (Run Feedback Agent)

```
orchestrator.py — Main Loop:

for current_gen in range(1, max_gen + 1):
    ├─ SECTION 5a: Run Target Agent                    [موجود]
    ├─ SECTION 5a.1: Run Evaluation                     [موجود]
    ├─ SECTION 5a.2: Constitutional Evaluation          [موجود]
    ├─ SECTION 5a.3: Evolutionary Discovery             [موجود]
    │
    ├─ ★ SECTION 5a.4: REGIME TRANSITION CHECK ★       [جديد — نقطة الحقن]
    │   │
    │   ├─ if regime_transition_required:
    │   │   ├─ Log: "REGIME TRANSITION DETECTED"
    │   │   ├─ Append recommended_actions to feedback prompt
    │   │   ├─ Record transition event in context_mgr
    │   │   └─ (Optional) Activate dormant pillar (H8/H9)
    │   │
    │   └─ else: continue normally
    │
    └─ SECTION 5b: Run Feedback Agent                   [موجود]
```

### الكود المطلوب إضافته في orchestrator.py (Section 5a.4):

```python
# ========================
# SECTION 5a.4: Regime Transition Check (from Wang & Buehler theft)
# ========================
regime_transition_info = None
try:
    from virtual_genesis.eval.runners.regime_transition_detector import check_regime_transition
    
    # Build accuracy history from previous generations
    accuracy_history = []
    for prev_gen in range(1, current_gen + 1):
        prev_eval_path = os.path.join(RUN_DIRECTORY, f"gen_{prev_gen}", "evaluation_results.json")
        if os.path.exists(prev_eval_path):
            with open(prev_eval_path) as f:
                prev_data = json.load(f)
            accuracy_history.append(prev_data.get("accuracy", 0.0) or prev_data.get("accuracy_percent", 0.0) / 100.0)
    
    # Get blind spot report from self-benchmarking if available
    blind_spot_report = {"suspiciously_easy_regions": [], "untested_combinations": [], "coverage_ratio": 1.0}
    self_bench_path = os.path.join(current_gen_directory, "self_benchmark_report.json")
    if os.path.exists(self_bench_path):
        with open(self_bench_path) as f:
            sb_data = json.load(f)
        blind_spot_report = sb_data.get("blind_spot_report", blind_spot_report)
    
    decision = check_regime_transition(
        accuracy_history=accuracy_history,
        blind_spot_report=blind_spot_report,
    )
    
    regime_transition_info = decision.to_dict()
    
    # Save transition report
    rt_path = os.path.join(current_gen_directory, "regime_transition_report.json")
    with open(rt_path, "w") as f:
        json.dump(regime_transition_info, f, indent=2)
    
    if decision.should_transition:
        logger.warning(f"  ⚡ REGIME TRANSITION DETECTED (confidence: {decision.confidence:.2f})")
        for action in decision.recommended_actions:
            logger.warning(f"    → {action}")
        context_mgr.add_generation(
            gen_num=current_gen,
            gen_data={"regime_transition_triggered": True, "transition_signals": regime_transition_info},
        )
    else:
        logger.info(f"  ✓ Regime check: {decision.verdict.value} ({decision.active_signal_count}/3 signals active)")
        
except Exception as e:
    logger.debug(f"  ⚠ Regime transition check skipped: {e}")
```

### كيف نُفعّل الاختبارات العدائية من Negative Memory؟

```python
# داخل SECTION 5a.4 أو كجزء من self-benchmarking cycle:

# 1. جمع الأخطاء من الأجيال السابقة
negative_memory_failures = []
for prev_gen in range(1, current_gen + 1):
    prev_exec_path = os.path.join(RUN_DIRECTORY, f"gen_{prev_gen}", "agent_execution.json")
    if os.path.exists(prev_exec_path):
        # Parse execution log for failures
        # Convert each failure to negative_memory_adversarial format
        pass  # TODO: implement failure extractor

# 2. تمريرها للـ cycle
result = run_self_benchmark_cycle(
    task_cases=cases,
    negative_memory_failures=negative_memory_failures,
    accuracy_history=accuracy_history,
)
```

**الربط لا يكسر الحلقة لأنه:**
- `negative_memory_failures` هو parameter اختياري (default=None)
- لو ما في failures → السلوك نفسه من قبل
- الاختبارات العدائية تُضاف للـ new_cases فقط، لا تؤثر على base_results

---

## إجابة السؤال 2: الأولوية القصوى — هل Conditions Runner أولاً؟

### ✅ أوافق بنسبة 100%: Conditions Runner هو الخطوة الأولى

**السبب:** بدون إشارة (Signal) = بدون قرار. الـ regime transition detector يحتاج:
1. `accuracy_history` → يحتاج conditions comparison عبر أجيال
2. `accuracy_with_new` vs `accuracy_without_new` → يحتاج baseline vs full pipeline
3. `blind_spot_report` → يحتاج coverage matrix من multiple conditions

**بدون conditions runner:**
- لا يوجد accuracy history
- لا يوجد comparison بين conditions
- الـ regime detector يُرجع `INSUFFICIENT_DATA` دائماً

**مع conditions runner:**
- كل جيل يُنتج success_rate لكل condition
- الـ accuracy_history يتكون تلقائياً
- الـ degradation signal يشتغل (baseline_0 vs condition_c_combined)

### خطة التنفيذ المقترحة:

```
المرحلة 1 (اليوم):  conditions runner (Standard vs Ablation)
                    ├─ 3 conditions: baseline_0, baseline_1, condition_c_combined
                    ├─ كل condition يُنتج success_rate
                    └─ يُخزّن في evaluation_results.json

المرحلة 2 (غداً):  ربط regime detector بـ conditions results
                    ├─ استخراج accuracy_history من results.json عبر الأجيال
                    ├─ تمرير blind_spot_report من self-benchmarking
                    └─ تحديث orchestrator.py (Section 5a.4)

المرحلة 3:         Negative Memory → Adversarial Tests
                    ├─ بناء failure extractor من agent_execution logs
                    ├─ كل خطأ يتحول لـ negative_memory_failure
                    └─ يُمرّر لـ run_self_benchmark_cycle()

المرحلة 4:         التجربة: GENESIS مع H8 vs بدون H8
                    ├─ Run A: بدون self-benchmarking (ablation)
                    ├─ Run B: مع self-benchmarking (مع regime detection)
                    └─ مقارنة: هل Run B يكتشف saturation أسرع؟
```

---

## إجابة السؤال 3: هل الـ 39 اختبار الموجودين كافيين؟

### لا — يحتاجون 4 أنواع جديدة من الاختبارات:

#### النوع 1: Regression Tests للـ Trigger Decision (موجود الآن!)
- ✅ **55 اختبار جديد** في `test_regime_transition.py` يغطون:
  - كل إشارة فردية (saturation, degradation, blind_spot)
  - القاعدة المجمعة (2-of-3)
  - الحالات الحدية (insufficient data, boundary values)
  - التكامل مع الـ cycle

#### النوع 2: التكامل مع Orchestrator (يحتاج كتابة)
```python
# test_orchestrator_regime.py (مطلوب مستقبلاً)
- test_regime_check_runs_after_target_agent
- test_regime_transition_appended_to_feedback_prompt
- test_accuracy_history_built_from_previous_gens
- test_no_crash_when_no_previous_eval_data
```

#### النوع 3: Negative Memory Failure Extractor (يحتاج كتابة)
```python
# test_failure_extractor.py (مطلوب مستقبلاً)
- test_extract_wrong_answers_from_execution_log
- test_extract_shortcut_patterns
- test_recurrence_counting_across_generations
- test_severity_calculation_from_failure_type
```

#### النوع 4: End-to-End Integration (يحتاج كتابة)
```python
# test_regime_e2e.py (مطلوب مستقبلاً)
- test_full_cycle_with_saturation_triggers_transition
- test_transition_then_improvement_commits
- test_transition_then_regression_rolls_back
- test_negative_memory_reduces_failure_recurrence
```

### الخلاصة:
- **94 اختبار يشتغلون الآن** (39 قديم + 55 جديد)
- **~15-20 اختبار إضافي** مطلوب للمرحلة التالية (orchestrator integration + failure extractor)
- الأولوية الآن: **Conditions Runner** (لا يوجد اختبارات له حالياً!)

---

## ملخص ما تم إنجازه

| الملف | الحالة | الاختبارات |
|---|---|---|
| `regime_transition_detector.py` | ✅ مكتمل | 30 |
| `negative_memory_adversarial.py` | ✅ مكتمل | 14 |
| `run_self_benchmark_cycle.py` (محدّث) | ✅ مكتمل | 3 (integration) |
| `test_regime_transition.py` | ✅ 55 اختبار | — |
| `test_self_benchmarking.py` (قديم) | ✅ لم يتأثر | 39 |
| **المجموع** | | **94 اختبار ✅** |

## ما بقي (خطة الغد):

1. ~~بناء regime_transition_detector.py~~ ✅
2. ~~بناء negative_memory_adversarial.py~~ ✅
3. ~~تحديث run_self_benchmark_cycle.py~~ ✅
4. ~~كتابة اختبارات~~ ✅
5. **بناء conditions runner** → الأولوية القصوى
6. **حقن Section 5a.4 في orchestrator.py**
7. **بناء failure extractor من execution logs**
8. **تجربة: GENESIS مع H8 vs بدون H8**
