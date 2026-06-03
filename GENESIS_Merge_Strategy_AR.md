# Virtual-GENESIS - استراتيجية الدمج النهائية
# Final Merge Strategy

> Document Type: Merge Strategy
> Status: Current
> Date: 2026-06-01

---

## 1. مقدمة

هذه الوثيقة تحدد الاستراتيجية المثلى لدمج جميع فروع التطوير في الفرع الرئيسي (main).
المشروع مر بسبع مراحل تطوير متتالية، كل مرحلة بُنيت فوق سابقتها في سلسلة خطية (linear chain).
هذا التوثيق يضمن عملية دمج نظيفة وقابلة للتحقق.

---

## 2. ترتيب الدمج

الفروع تُدمج بالترتيب التالي (كل فرع يعتمد على سابقه):

### PR #2: feat/stabilize-and-package-v2
- **المحتوى:** تثبيت الحزمة، pyproject.toml، بنية المشروع الاساسية
- **المخرجات:** virtual_genesis/ package قابل للتثبيت، pytest working، CI-ready
- **الاعتمادية:** يُبنى على main الاصلي

### PR #3: feat/eval-pressure-anomaly-leverage
- **المحتوى:** نظام تقييم الضغط، اكتشاف الشذوذات، anomaly leverage في الـ pipeline
- **المخرجات:** eval framework كامل، anomaly_runtime، perturbation operators
- **الاعتمادية:** يُبنى على PR #2

### PR #4: feat/theory-leverage-cycle
- **المحتوى:** بناء النظريات المحلية، التنبؤ النظري، theory-guided routing
- **المخرجات:** theory_runtime، predictive_value tracking، theory-guided tier selection
- **الاعتمادية:** يُبنى على PR #3

### PR #5: feat/wave3-self-benchmark-forgetting
- **المحتوى:** الـ Self-Benchmarking cycle + Productive Forgetting
- **المخرجات:** benchmark_generator، forgetting_policy، decay mechanics، blind spot discovery
- **الاعتمادية:** يُبنى على PR #4

### PR #6: feat/broader-domain-cycle
- **المحتوى:** تقييم النطاق الاوسع، مجالات جديدة (security, data engineering, etc.)
- **المخرجات:** v7 broader domain cases، domain_transfer report، extended curriculum
- **الاعتمادية:** يُبنى على PR #5

### PR #7: feat/wave3-identity-paradigm
- **المحتوى:** حوكمة هوية الوكيل (H9)، كشف الازمات، التفريع النموذجي
- **المخرجات:** identity_runtime، crisis_detector، paradigm_fork، commitment_ledger
- **الاعتمادية:** يُبنى على PR #6

### PR #8: feat/production-integration
- **المحتوى:** اختبار التكامل الكامل، API الانتاجي، البحث العلمي، استراتيجية الدمج
- **المخرجات:** API (http.server + OpenRouter)، full integration runner، research paper draft
- **الاعتمادية:** يُبنى على PR #7

---

## 3. استراتيجية الدمج

### التوصية: Squash Merge
نوصي باستخدام **squash-merge** لكل PR:
- كل PR يصبح commit واحد نظيف على main
- يحافظ على نظافة تاريخ main
- يسهل العودة (revert) لأي مرحلة كاملة
- رسالة الـ commit تلخص محتوى المرحلة بالكامل

### لماذا ليس merge commit عادي؟
- الفروع تحتوي على commits تطويرية كثيرة (fix, chore, refactor)
- هذه التفاصيل مفيدة خلال التطوير لكنها ضوضاء في main
- التاريخ المفصل يبقى متاحا في الـ PR نفسه

### لماذا ليس rebase؟
- الفروع طويلة ومعقدة
- rebase قد يسبب conflicts غير ضرورية
- squash اكثر امانا ونظافة

---

## 4. الحالة النهائية لـ main بعد الدمج

بعد دمج جميع الفروع، سيحتوي main على:

### Runtime Core (virtual_genesis/runtime/)
- task_ingress: استقبال المهام مع ranked framing
- blackboard_core: حالة محلية لكل مهمة
- memory_os: ذاكرة + retrieval + forgetting + decay
- concept_engine: تكوين المفاهيم + selectivity
- economy_control: routing + ledger + escalation
- reasoning_runtime: استدلال مدرك للعائلة
- verification_runtime: تحقق TaskCase-based
- contradiction_runtime: كشف التناقضات
- anomaly_runtime: اكتشاف الشذوذات + severity scoring
- theory_runtime: بناء نظريات + تنبؤ + تقييم
- identity_runtime: هوية + drift detection + paradigm fork
- pipeline: minimal_run مع 5 governance flags

### Evaluation Framework (virtual_genesis/eval/)
- runners: 10+ runner scripts (v1-v7, integration, self-benchmark, ablation)
- reports: 18+ report generators (summary, analytics, selectivity, etc.)
- task_sets: 14+ task set files (v1-v7 + curricula)
- perturbations: curriculum builder + operators
- benchmark_generator: توليد اختبارات من الشذوذات

### Production API (virtual_genesis/api/)
- app.py: REST server (http.server based)
- config.py: model mapping + governance flags
- llm_adapter.py: OpenRouter integration + mock
- session.py: session lifecycle management

### Core Objects (virtual_genesis/core/)
- objects: 10+ domain objects (Task, Blackboard, Memory, Concept, Theory, Identity, etc.)
- ontology: type definitions

### Tests (tests/)
- 297+ tests across 12+ test files
- Full coverage: engine, runners, governance, API, integration

### Documentation (*.md)
- 80+ Arabic documentation files
- Research paper draft
- Legitimate thefts registry (5.01 - 5.64)
- Theory documents
- Implementation memos
- Evidence packages

---

## 5. منهجية السرقة الشرعية في سياق الدمج

### 5.1 المبدأ
يتبع هذا المشروع منهجية "السرقة الشرعية" (Legitimate Theft): ناخذ مجهود الغير من ابحاث ومشاريع وافكار، نستخلص الجوهر القابل للتشغيل، ونحوله الى مكون عملي في نظامنا مع توثيق كامل لما اخذناه وما تركناه وما اصبح عندنا.

### 5.2 توزيع السرقات على مراحل الدمج
كل PR يحمل مجموعة سرقات شرعية موثقة:

| PR | المرحلة | السرقات | الملف المرجعي |
|----|---------|---------|---------------|
| #2 | stabilize-and-package | 5.01-5.10 | Virtual_SIA_Legitimate_Thefts_AR.md |
| #3 | eval-pressure-anomaly | 5.11-5.24 | Virtual_SIA_Legitimate_Thefts_Cycle2_AR.md |
| #4 | theory-leverage | 5.25-5.34 | Virtual_SIA_Legitimate_Thefts_Cycle3_AR.md |
| #5 | self-benchmark-forgetting | 5.45-5.54 | Virtual_SIA_Legitimate_Thefts_Wave3_AR.md |
| #6 | broader-domain | 5.35-5.44 | Virtual_SIA_Legitimate_Thefts_Cycle4_AR.md |
| #7 | identity-paradigm | 5.55-5.62 | Virtual_SIA_Legitimate_Thefts_Wave3b_AR.md |
| #8 | production-integration | 5.63-5.64 | Virtual_SIA_Legitimate_Thefts_Production_AR.md |

### 5.3 التحقق بعد الدمج
- [ ] التاكد من وجود جميع ملفات السرقات الشرعية (6 ملفات)
- [ ] التاكد من تغطية النطاق الكامل: 5.01 حتى 5.64
- [ ] التاكد ان كل سرقة موثقة بـ: المصدر، ما اخذناه، ما تركناه، ما اصبح عندنا
- [ ] التاكد من ان Research Paper يشير الى المنهجية ويعدد المصادر (75+ مصدر)

---

## 6. قائمة التحقق بعد الدمج

بعد دمج كل PR بالترتيب، تحقق من:

### 6.1 التحقق الفوري بعد كل PR
- [ ] تشغيل pytest: `python -m pytest tests/ -q --tb=short`
- [ ] التاكد من عدم وجود import errors: `python -c "import virtual_genesis"`
- [ ] التاكد من عدد الاختبارات المتوقع لكل مرحلة

### 6.2 التحقق النهائي بعد دمج جميع PRs
- [ ] تشغيل الاختبارات الكاملة: `python -m pytest tests/ -v`
- [ ] تأكد من 297+ test passing
- [ ] التأكد من بنية الـ import: `python -c "from virtual_genesis.api.app import create_app; from virtual_genesis.eval.runners.run_full_integration import run_full_integration"`
- [ ] تشغيل API في mock mode: `python -c "from virtual_genesis.api.app import create_app; s = create_app(); print('Server ready on', s.server_address)"`
- [ ] تأكد من تشغيل eval runners: `python -c "from virtual_genesis.eval.runners.run_condition import run_condition; r = run_condition('baseline_0', ['test task']); print('Success rate:', r.aggregate_metrics['success_rate'])"`
- [ ] فحص اكتمال الوثائق: التأكد من وجود Virtual_SIA_Research_Paper_Draft_AR.md و Virtual_SIA_Merge_Strategy_AR.md
- [ ] التأكد من الـ legitimate thefts: 5.01 حتى 5.64 موثقة

### 6.3 العدد المتوقع من الاختبارات لكل مرحلة
| PR | اسم الفرع | العدد المتوقع |
|----|-----------|-------------|
| #2 | stabilize-and-package-v2 | ~90 tests |
| #3 | eval-pressure-anomaly-leverage | ~145 tests |
| #4 | theory-leverage-cycle | ~185 tests |
| #5 | wave3-self-benchmark-forgetting | ~225 tests |
| #6 | broader-domain-cycle | ~250 tests |
| #7 | wave3-identity-paradigm | ~285 tests |
| #8 | production-integration | ~297 tests |

---

## 7. ملاحظات مهمة

### 7.1 لا تعارضات متوقعة
بما ان كل فرع بُني فوق سابقه مباشرة (linear chain)، لا نتوقع اي merge conflicts.
كل PR يضيف ملفات جديدة ويوسع الملفات الموجودة بدون تعديل ما سبق.

### 7.2 الترتيب حاسم
لا يمكن دمج PR #4 قبل #3 مثلا، لان theory_runtime يعتمد على anomaly_runtime.
الترتيب الخطي هو الترتيب الوحيد الصحيح.

### 7.3 السرقات الشرعية كضمان جودة
منهجية السرقة الشرعية تضمن ان كل مكون في النظام له اصل بحثي او عملي واضح.
عند الدمج، هذا يعني ان كل PR ليس فقط كود بل ايضا توثيق معرفي كامل:
- من اين جاءت الفكرة (المصدر الاصلي)
- ما الذي اخذناه منها (الجوهر القابل للتشغيل)
- ما الذي تركناه (القيود او ما لا يناسبنا)
- ما الذي اصبح عندنا (التحويل الى مكون عملي)

هذه المنهجية تضمن الشفافية الكاملة وتمنع اي ادعاء بأصالة مطلقة، بينما تؤكد ان ما ناخذه يصبح جزءا عضويا من النظام لا مجرد استعارة سطحية.

### 7.4 ما بعد الدمج
بعد اكتمال الدمج، الخطوات التالية:
1. اضافة CI/CD (GitHub Actions) على main
2. اضافة tags لكل مرحلة (v0.1.0 - v0.8.0)
3. بدء العمل على real LLM integration (OpenRouter مع مفتاح فعلي)
4. توسيع curricula والمجالات
5. اختبار حقيقي مع مستخدمين

---

*نهاية استراتيجية الدمج*
