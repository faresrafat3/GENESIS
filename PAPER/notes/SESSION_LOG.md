# 📝 SESSION LOG — سجل الجلسات

---

## Session 1 — 2026-06-04 (Partial, initial exploration)

**الحالة:** بداية العمل على المشروع. تشخيص run_53 + بداية بناء infrastructure.

### ما تم:
- Clone الـ repo وتحليل البنية
- اكتشاف bug case mismatch في run_53 (q.get('question') vs 'Question')
- بناء `tools/diagnose_run_53.py` — تشخيص آلي
- بناء `tools/gpqa_pure_baseline.py` — قياس النموذج بدون GENESIS
- تحليل run_53: توزيع عشوائي (χ²=10.36)، accuracy 30%
- تشغيل smoke test v1: extract_letter بـ 4 patterns → invalid rate 35%
- بناء `tools/api_key_pool.py` — 11-key rotation
- بناء `tools/model_registry.py` — 13 نموذج
- بناء `tools/run_multi_model_benchmark.py`
- رفع commits: `33ada0a` → `6c840c6`

### الـ Open Threads:
- GENESIS scaffolding fix لم يُطبق بعد
- Multi-provider pool لم يُبنَ

---

## Session 2 — 2026-06-04/05 (Major infrastructure + fix)

**الحالة:** جلسة مكثفة. بناء البنية التحتية الكاملة + إصلاح GENESIS.

### ما تم:

**Smoke Test v2 (Agent Run):**
- تشغيل smoke test بـ 3 نماذج × 20 سؤال
- اكتشاف: content="" في 35% من الـ requests (reasoning consumes all tokens)
- إصلاح: `extract_response_text()` مع fallback على reasoning text
- إصلاح: pool round-robin rotation (كان بيستخدم key واحد)
- إصلاح: force-letter follow-up ذكي
- نتائج: nemotron-3-nano 55% → 65% (+10), lfm-2.5 15% → 25% (+10)

**Pure Baseline النهائي:**
- تشغيل gpt-oss-120b على 20 سؤال GPQA
- النتيجة: **75.00%** (15/20), 0 invalid, 3 recovered via followup
- Physics 81.8%, Chemistry 66.7%, Biology 66.7%
- الفجوة من official 80.1%: −5.1 (مقبول للـ free tier)

**GENESIS Scaffolding Fix:**
- إنشاء `genesis/llm_helpers.py` (220 سطر)
- 5 bugs موثقة ومُصلحة
- تحديث orchestrator META_AGENT_PROMPT + FEEDBACK_AGENT_PROMPT
- 35 اختبار جديد في `tests/test_llm_helpers.py`
- 463/463 tests passing

**Multi-Provider Infrastructure:**
- `tools/providers.py`: كتالوج 9 مزودين
- تحديث `.env.example` لكل المزودين
- GitHub Models: اكتشاف GPT-5 مجاناً على PAT فارس

**Paper Infrastructure:**
- `PAPER_PROTOCOL.md`: بروتوكول العمل على الورقة
- `PAPER.md`: الورقة الرئيسية v0.1 (skeleton كامل + كل النتائج)
- `PAPER/notes/HANDOFF.md`
- `PAPER/notes/SESSION_LOG.md` (هذا الملف)
- `PAPER/notes/TODO_HIGH.md` + `TODO_MEDIUM.md` + `OPEN_QUESTIONS.md`
- `PAPER/figures/README.md` + `PAPER/tables/README.md`

### الـ Commits:
- `91cd9ea`: Extract response text + 6 fixes
- `a609c90`: Pure baseline 75% RESULT
- `6240094`: 9 providers documented
- `3a16a87`: THE FIX — genesis/llm_helpers + orchestrator
- `3cbe48b`: Comprehensive research report

### اكتشافات هذا الـ session:
1. Reasoning saturation effect (more tokens → less accuracy)
2. Domain asymmetry (Physics easy, Chemistry hard)
3. Empty content phenomenon (35% of responses)
4. Case sensitivity bug confirmed mathematically
5. GitHub Models GPT-5 available for free

---

## Session 3 — 2026-06-05 (Paper consolidation + first real architecture comparison)

**الحالة:** تحويل الشغل من مسار بطيء غير عملي (198 سؤال) إلى مسار بحثي سريع ومفيد (20 سؤال)، ثم تنفيذ أول مقارنة حقيقية بعد الإصلاحات.

### ما تم:

**Paper consolidation:**
- كتابة `PAPER.md` كـ master paper
- كتابة `PAPER_PROTOCOL.md`
- بناء `PAPER/notes/` system كامل
- بناء 8 figures + aggregated data + per-question matrix

**Quick-path infrastructure:**
- إنشاء `tasks/gpqa_subset_20`
- إضافة دعم `--task_dir` في `run_openrouter_benchmark.py`
- توثيق `QUICK_RUN_20Q_GUIDE_AR.md`
- إصلاح preference لـ `./.venv/bin/python` لو موجود

**Critical bug #6:**
- اكتشاف bug جديد: `extract_response_text()` from `genesis.llm_helpers` returns `(text, meta)` tuple
- meta-agent generated code was treating it as string
- النتيجة: `'tuple' object has no attribute 'strip'`
- تم إصلاح الـ prompt + التحقق من generation الجديدة

**First architecture comparison completed:**
- تشغيل `run_57` على `tasks/gpqa_subset_20`
- **Generation 1 = 65.00%**
- **Generation 2 = 65.00%**
- 0 invalid answers في الجيلين
- architecture recovered from 30.3% buggy result, but still under pure baseline 75.0%

### الـ Commits:
- `db68f47`: paper protocol + handoff system
- `8b018ce`: complete 8 figures + aggregated data
- `a5e6d6b`: add GPQA 20-question subset + task_dir support
- `8bbdb93`: prefer repo .venv python + document fast path
- `c62835f`: tuple unpacking fix in orchestrator prompt
- `b905901`: first post-fix architecture comparison in paper
- `6dd35c2`: question-by-question delta map
- `7d1d5d0`: ablation matrix + decision tree

---

## Session 4 — 2026-06-05 (A3 ablation: no pipeline leverage)

**الحالة:** أول ablation فعلي على architecture gap.

### ما تم:

**A3 implementation:**
- إضافة `--ablation_mode` إلى `run_openrouter_benchmark.py`
- إضافة `--ablation_mode` إلى `genesis.orchestrator`
- تنفيذ mode جديد: `no_pipeline`
- meta-agent prompt بقى يقدر يكتب target_agent يحتفظ بالـ scaffold لكن يعطل pipeline leverage على answer generation
- feedback prompt بقى aware بالـ ablation mode عشان ما يرجعش pipeline influence بالغلط

**A3 experiment completed (`run_58`):**
- `run_58 gen_1 = 70.00%`
- `run_58 gen_2 = 60.00%`
- مقارنة بـ `run_57 gen_1 = 65.00%`
- النتيجة: إزالة pipeline leverage رفعت Gen 1 بـ **+5 points**
- لكن feedback في هذا الوضع هبطت Gen 2 إلى **60.00%**

**Paper updates:**
- تحديث `PAPER.md` بالـ A3 result
- إنشاء `PAPER/data/run58_a3_no_pipeline_20q.json`
- إنشاء `PAPER/tables/tab14_a3_no_pipeline_results.md`
- تحديث `aggregated_results.json`
- تحديث `HANDOFF.md` و `TODO_HIGH.md`

### الاستنتاج العلمي الجديد:
1. **pipeline leverage currently hurts** (supported by +5 gain when removed)
2. **feedback drift is real** (Gen 2 drops from 70 → 60 under A3)
3. المشكلة المتبقية لم تعد غامضة: عندنا الآن culpritين مرشحين بقوة
   - pipeline overhead/noise
   - feedback instability

### الـ Open Threads:
- ⏭ A4 / A7 feedback-focused ablation
- ⏭ Cross-model same-subset comparison (Gemini / GPT-5 / Gemma)
- ⏭ Decide whether constitutional pressure or feedback scope comes next

---

## Session 5 — 2026-06-05 (A7 infrastructure: narrow_feedback ablation)

**الحالة:** السيشن السابقة (Session 4) علقت بعد ما رفعت `78430fc`. هذه السيشن استلمت من نفس النقطة وكملت بدون تكرار.

### ما تم

**A7 infrastructure wired:**
- إضافة `narrow_feedback` كـ `--ablation_mode` choice جديد في:
  - `genesis/orchestrator.py`
  - `run_openrouter_benchmark.py`
- إضافة `no_pipeline+narrow_feedback` كـ choice مركّب (A7b).
- تفكيك `ablation_mode` إلى flags مستقلة: `no_pipeline_active`, `narrow_feedback_active`.
- كتابة instruction block صريحة جداً للـ feedback agent تحظر:
  - broad refactoring
  - renaming / reorganizing
  - new features or abstractions
  - touching code paths غير الأسئلة الغلط
  وتسمح فقط بـ:
  - targeted fixes for the specific wrong-answer questions
  - minimal prompt additions
  - bug fixes that prevent crashes/invalid answers
  - outputting identical code إذا لم يوجد fix مستهدف.

**Paper updates:**
- إنشاء `PAPER/tables/tab15_a7_design.md`:
  - 3 تجارب مخططة (A7a, A7b, A7c)
  - CLI كاملة قابلة للتشغيل
  - hypotheses مسجلة مسبقاً (pre-registered)
  - decision rule صريح
- تحديث `HANDOFF.md` ليعكس حالة Session 5.
- تحديث `TODO_HIGH.md` بـ A7 priorities.

### ما لم يتم (مقصود)

- **لم يتم تشغيل A7 فعلياً** في هذه السيشن. السبب:
  - free tier quota محدود
  - الـ sandbox هنا مش الـ machine بتاع فارس
  - الأنسب يشغّلها فارس عنده بالـ CLI الموثقة في Table 15
- لذلك السيشن دي infrastructure-only — أعدّت المشروع للخطوة التالية بدون استهلاك أي API calls.

### الـ Commit (بعد الـ push)

- `(pending)`: A7 infrastructure + Table 15 + HANDOFF Session 5 update

