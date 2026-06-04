# سرقة شرعية: FunSearch + AlphaEvolve من Google DeepMind
## GENESIS DeepMind Science Thefts — Cycle 6 (Evolutionary Discovery)

> **المصدر الرئيسي**: 
> - FunSearch (Nature, ديسمبر 2023) — Bernardino Romera-Paredes et al.
> - AlphaEvolve (تحديثات 2025-2026، DeepMind blogs وأوراق) — تطور لـ FunSearch مع تركيز على الـ agentic evolutionary search.
> - روابط رئيسية: https://www.nature.com/articles/s41586-023-06924-6 | DeepMind blogs عن AlphaEvolve وتأثيره على data centers و chip design.

**تاريخ السرقة**: 2026-06-04  
**الحالة المقترحة**: 🟢 (مبدأ + تنفيذ جزئي في الـ orchestrator + concept/theory layers)  
**الأولوية**: 🔴 حرجة (تدعم مباشرة Phase 1 من الـ Strategic Plan: ربط الـ Orchestrator بالـ cognitive pipeline وتحويل الـ "keyword matching" إلى genuine discovery).

---

## 1. الفكرة الأساسية (ما هي القوة الكامنة؟)

FunSearch و AlphaEvolve هما **نظام تطوري (evolutionary search) مدعوم بـ LLM + Evaluator**.

- الـ LLM يولد "candidates" (كود، خوارزميات، heuristics، أو في حالتنا: prompts, skills, concepts, theories, policies).
- الـ Evaluator (برنامج خارجي أو verifier) يقيّم الـ candidates بموضوعية (صحة، أداء، تكلفة).
- يتم التطور عبر أجيال (population-based search + mutation + selection) مع التركيز على التنوع + التحسين التدريجي.

**القوة الحقيقية (الدليل)**:
- FunSearch حل مشكلة Cap Set (أكبر تقدم في أكتر من 20 سنة) في أبعاد 8-12.
- حسّن heuristics لـ online bin-packing تفوق الطرق البشرية.
- AlphaEvolve استخدم في تحسين كفاءة Google data centers، chip design، و AI training processes (تأثير عملي حقيقي داخل Google).
- المنهجية: LLM مش بيحل لوحده، لكن بيولد + يتطور تحت إشراف evaluator صارم. ده يخلق "discovery engine" مش مجرد "reasoner".

ده بالظبط اللي يناسب GENESIS: مش "نستخدم LLM أقوى"، لكن "نبني harness تطوري يستخدم الـ LLM كـ generator داخل loop معرفي".

---

## 2. السرقة الشرعية (ما أخذناه / ما تركناه / ما أصبح عندنا)

### ما أخذناه (الجوهر القابل للتشغيل):
- **Evolutionary search over artifacts**: مش بس prompts، لكن أي "artifact" قابل للتقييم (skills, concepts, theories, policies, code snippets, reasoning structures).
- **LLM + Evaluator closed loop**: الـ LLM يقترح، الـ Evaluator يحكم بصرامة (صحة + utility + cost).
- **Population + mutation + selection مع التركيز على التنوع**: عشان نتجنب الـ local optima (مش بس "best of"، لكن "diverse high-quality population").
- **Iterative refinement مع feedback**: كل جيل يستفيد من نتايج الجيل السابق (trace-rich substrate زي Meta-Harness).
- **Scalable discovery**: القدرة على توليد واختبار آلاف الـ candidates في parallel (كما في Computational Discovery في Gemini for Science).

### ما تركناه عمدًا (عشان يتوافق مع قفلنا الداخلي):
- الاعتماد الكامل على LLM كـ "الذكاء الرئيسي" (نحافظ على harness-first: الـ LLM generator بس، الـ intelligence في الـ evaluator + selection + memory).
- التركيز على مشاكل رياضية/كود فقط (نوسعه ليشمل scientific concepts + theories + cognitive policies).
- الـ "black-box evolution" بدون تفسير (نضيف traceability من خلال الـ blackboard + ledger + provenance).
- التطور بدون "cognitive economy" (نضيف tiered evaluation + cost-aware selection).

### ما أصبح عندنا (التحويل العملي في GENESIS):
- **في الـ Orchestrator**: الـ meta-agent + feedback agent يتحولوا لـ "Evolutionary Discovery Agent" يستخدم الـ pipeline كـ substrate + يولد ويقيّم أجيال من الـ target_agents / skills / concepts.
- **في الـ Concept Engine**: الـ proposer يتطور لـ "Evolutionary Concept Proposer" (يولد populations من concepts، يقيّمهم بـ regression budget + utility).
- **في الـ Theory Runtime**: الـ theory_registry يدعم evolutionary refinement (theories تتطور عبر أجيال مع predictive value كـ fitness).
- **في الـ Improvement Plane**: "Replay Research Lab" يتحول لـ "AlphaEvolve-style Replay Engine" مع population management + multi-objective selection (performance + cost + robustness).
- **في الـ Evaluation**: نضيف "Evolutionary Evaluator" يدعم parallel scoring + diversity metrics (مش بس success rate).
- **النتيجة المتوقعة**: الـ self-improvement loop بتاعنا يبقى "discovery engine" حقيقي، مش بس refinement. ده هيحول الـ 98.6% من "keyword matching" إلى "evolutionary scientific discovery".

---

## 3. الدمج العملي (نقاط التنفيذ المحددة)

### المرحلة 1 (فورية — تدعم الـ Bridge Task):
- في `genesis/orchestrator.py`: أضف evolutionary loop داخل الـ meta/feedback agents.
  - بدل "اكتب target_agent.py واحد" → "ولد population من 8-16 variants، قيّمهم باستخدام الـ pipeline + real LLM evaluator، اختار الـ top-k مع diversity".
- استخدم الـ existing `run_minimal_pipeline` كـ core evaluator (مع الـ concept/theory/memory كـ guidance).
- أضف "population ledger" في الـ research_memory (يسجل fitness, lineage, mutations).

### المرحلة 2 (عالية — بعد الـ Bridge):
- في `virtual_genesis/runtime/concept_engine/proposer.py`: حوّل الـ propose_concepts_from_groups إلى evolutionary proposer.
  - يولد population من ConceptCandidates.
  - يستخدم الـ existing redundancy check + evidence scoring كـ fitness.
  - يطبق mutation (تعديل definition/scope) + crossover بين concepts ناجحة.
- في `virtual_genesis/runtime/theory_runtime/`: أضف evolutionary theory refinement (مش بس update predictive value، لكن mutate الـ mechanism_claims).

### المرحلة 3 (متوسطة — للـ Governance):
- أضف flag جديد: `use_evolutionary_discovery`.
- يفعل population-based search في الـ Improvement Plane مع hard regression budget (زي GRASP اللي سرقتوه قبل كده).
- يربط بالـ anomaly/theory leverage (الـ evaluator يفضل candidates اللي بتحسن الـ robustness).

### أدوات مساعدة مطلوبة (من السرقات السابقة):
- الـ "acceptance gate" من GRASP.
- الـ graph-structured memory من ExpGraph (عشان الـ population تكون graph من الـ lineages).
- الـ BenchTrace (Failure Avoidance Rate) كـ جزء من الـ multi-objective fitness.

---

## 4. التأثير المتوقع على GENESIS (لماذا هتفرق جدًا)

- **في الـ Self-Improvement**: الـ orchestrator هيبقى مش بس "يحسن target_agent"، لكن "يكتشف عائلات جديدة من الـ strategies" عبر أجيال.
- **في الـ Concept & Theory**: هيحول الـ "mining من الذاكرة" إلى "تطور نشط" — مفاهيم ونظريات بتتولد وتتنافس وتتحسن.
- **في الـ Cognitive Economy**: الـ evaluator هيقدر يختار candidates حسب الـ tier والـ cost (cheap candidates أولاً، premium للـ high-uncertainty).
- **في الـ Evaluation**: هيضيف "evolutionary robustness" — مش بس success rate، لكن "كمية الـ discovery" و "التنوع" و "الـ transfer".
- **الدليل من DeepMind**: نفس المنهجية حسّنت مشاكل رياضية وعملية داخل Google. عندنا الـ harness أقوى (الـ 3 layers + memory OS + verification)، فالنتيجة هتبقى أقوى.

**الخطر الرئيسي**: الـ evaluator يبقى "الكنز" — لو الـ evaluator ضعيف، التطور هيضلل. عشان كده لازم نربطه بقوة بالـ existing verification + contracts + anomaly detection.

---

## 5. الخطوات التنفيذية المقترحة (Task جديد في الـ Strategic Plan)

**Task 6: Evolutionary Discovery Engine (AlphaEvolve-style)**
- **الأولوية**: 🔴 حرجة (بعد أو مع الـ Bridge).
- **الوصف**: أضف evolutionary search layer فوق الـ orchestrator و الـ concept/theory engines.
- **النجاح**: 
  - الـ orchestrator يولد ويقيّم population من الـ agents/concepts/theories.
  - تحسن ملموس في الـ transfer و الـ discovery rate على الـ broader domain slices.
  - وثيقة جديدة: "GENESIS_Evolutionary_Discovery_Memo_AR.md".
- **الاعتمادات**: يعتمد على الـ Bridge task + الـ GRASP/ExpGraph thefts السابقة.

---

## 6. ملاحظات إضافية (للجودة العالية)

- **التوافق مع الـ Regime Lock**: الـ evolutionary search يبقى في Layer B أو Improvement Plane أولاً (gated). Layer A (الـ core pipeline) يفضل "locked" ويُستخدم كـ evaluator ثابت.
- **القياس**: نضيف metrics جديدة في الـ curriculum reports: "discovery_rate"، "population_diversity"، "lineage_depth".
- **السرقات المرتبطة**: 
  - GRASP (gated regression-aware).
  - ExpGraph (graph memory للـ lineages).
  - FunSearch نفسها (evolutionary).
  - AlphaEvolve (النسخة الـ agentic).
- **الخطوة التالية الموصى بها**: ابدأ بـ prototype صغير في `tests/test_evolutionary_discovery.py` + runner جديد `run_evolutionary_discovery.py` على slice صغير (مثل 10 tasks).

---

**هذه السرقة هتكون من أعلى جودة لأنها**:
- مباشرة تدعم الـ "self-improving" vision بتاع GENESIS.
- بتستغل الـ harness القوي اللي عندكم (مش مجرد LLM).
- بتكمل السرقات السابقة (GRASP + ExpGraph + Meta-Harness).
- ليها دليل عملي قوي من DeepMind نفسه.

لو عايز نكمل بنفس الجودة لـ Co-Scientist أو Aletheia أو GNoME، قولي وأنا أعمل memo مماثل فورًا.

جاهز للـ "حلب" بأعلى جودة. قولي الخطوة التالية. 🏴‍☠️

---

## سرقة شرعية إضافية 5.87 (امتداد مباشر لـ AlphaEvolve 5.84): Robust Target Agent Code Gen + Execution Logging من تجارب الـ Evolutionary Discovery

**المصدر (+ رابط)**: 
- الـ run_49 (2026-06-04) على spaceship-titanic مع --use_evolutionary_discovery + gpt-oss-120b:free عبر OpenRouter (من run_openrouter_benchmark.py + orchestrator.py).
- الدليل: log كامل في الـ user message (Gen1 فشل في كتابة agent_execution.json بسبب "cannot access local variable 'json' where it is not associated with a value" + data shape (870, 2) مش full؛ Gen2 اتظبط بالـ feedback؛ evo fitness 0.800/score 0.880؛ constitutional 0/10 PASSED؛ accuracy داخلية 1.0000 (مش موثوقة لأن proxy + ممكن data leak في الـ generated agent)؛ no 'Mars' error (الـ generalization السابق نجح)؛ final LLM summary للـ changes بين gen1/gen2 (cosmetic فقط).

**الفكرة الأساسية (السرقة)**: 
- الـ LLM generator (meta/feedback) في الـ evolutionary loop (AlphaEvolve style) بيولد كود target_agent.py، لكن الـ LLM (حتى الـ free tier) بيغلط في الـ imports scope، الـ data loading الجزئي، والـ logging — ده بيخلي الـ feedback يفشل و الـ evo loop يضعف.
- السرقة: نحول الـ "prompt engineering" لـ "robust template enforcement" مع GENERAL principles (مش specific لـ titanic columns) عشان الـ evo يكون موثوق و ينتج agents قابلة للـ feedback + real eval.

**ما أخذناه**: 
- الـ error logs + run artifacts من run_49 كـ "failure cases" للـ generator.
- الـ prompt patterns من الـ previous generalization (تبقى GENERAL لـ "any tabular/data task" أو "ANY task").
- الـ robust logging block + data loading template + "imports at VERY TOP" rule + CRITICAL instructions في الـ FEEDBACK.

**ما تركناه عمدًا**: 
- أي hardcode لـ spaceship-titanic columns (زي 'Mars' أو 'HomePlanet' — كارثة زي ما حذرت).
- الاعتماد على الـ LLM يتبع الـ examples لوحده (نفرض الـ template بالـ "MUST include EXACT" + fallback في الـ orchestrator).

**ما أصبح عندنا (المكوّن التشغيلي)**: 
- في `genesis/orchestrator.py` (META_AGENT_PROMPT + FEEDBACK_AGENT_PROMPT): 
  - MUST imports at top مع datetime, pandas, numpy + explicit warning ضد scope errors.
  - CRITICAL GENERAL DATA HANDLING section مع full pd.read_csv + shape print + general target detection (no specific cols).
  - Mandatory ROBUST EXECUTION LOGGING block (مع try/except + fallback write) اللي بيضمن agent_execution.json دايمًا موجود للـ feedback + load_agent_execution.
  - CRITICAL instructions في feedback للـ json error + wrong shape.
- النتيجة: run_49 نجح (Gen2 كتب الـ json بنجاح، evo اشتغل مرتين، no file-not-found زي run_48).
- ربط بالـ MASTER_INDEX_AR.md (5.87 جديد) + تحديث الـ theft memo.

**الدليل (evidence من الـ ablations/runs)**:
- قبل الـ fix (run_48): Gen2 "can't open file .../gen_2/target_agent.py" (feedback ما كتبش).
- run_49 (بعد الـ first generalization + هذا الـ fix): Gen1 عنده الـ json error + (870,2)، لكن feedback + evo + robust template خلّى Gen2 ينجح و يكتب الـ json + constitutional PASSED.
- الـ evo fitness ثابت 0.800 (proxy من constitutional + pipeline).
- الـ constitutional score 0/10 (🟢 no violations، بس الـ score لسه low لأن الـ checks heuristic زي check_regression_free بترن pytest كل gen).
- الـ accuracy 1.0000 داخل الـ agent (مش حقيقي — proxy task + ممكن الـ generated agent بيستخدم train labels أو بيحسب على val غلط؛ لازم نروح لـ gpqa/SWE-bench للـ real metrics).
- الـ 'Mars' error اختفى (الـ GENERAL prompt نجح).
- الـ research memory: 18 entries, 61% success (من الـ log).

**نقاط الدمج (integration points)**:
- orchestrator.py (الـ prompts + evo evaluator اللي بيستخدم الـ artifacts).
- run_openrouter_benchmark.py (للـ real runs مع --use_evolutionary_discovery).
- MASTER_INDEX_AR.md + هذا الـ memo (للـ provenance).
- الـ context.md في الـ runs (بيحتوي الـ LLM summaries للـ changes).
- الـ constitutional_evaluator + load_agent_execution (بيستفيدوا من الـ robust logs).
- Strategic Plan Task 6 + Task 9 (الـ real benchmark).

**المخاطر + التحذيرات (عشان الـ project vision)**:
- الـ overfitting للـ proxy (spaceship-titanic accuracy 1.0 مش معناه حاجة — زي ما قلت "كارثه وتهديد كبير علي المشروع" لو عملنا حاجة مخصوصة للـ test ده).
- الـ LLM generator (gpt-oss-120b:free) لسه flaky (cosmetic changes بس في الـ summary) — الـ evo fitness proxy مش real task success.
- Constitutional 0/10 دايمًا (الـ checks بترن pytest كل مرة، و heuristic بسيط).
- لازم نروح لـ serious benchmarks (SWE-bench, gpqa) عشان نقيس الـ lift الحقيقي من الـ thefts (AlphaEvolve + prior) vs baseline 98.6% keyword.

**الـ Tasks المقترحة (تكملة للـ Strategic Plan)**:
- Task 6.1 (فوري): شغّل run_50 مع --max_gen 3 + --use_evolutionary_discovery على gpqa (harder reasoning) عشان تختبر الـ transfer للـ GENERAL prompts (بدون titanic).
- Task 6.2: أضف real metrics extraction في الـ target_agent template (val split accuracy + submission validation) + ربط مع run_evaluation.
- Task 9 (real benchmark): بعد الـ fix، اعمل runs على SWE-bench (via --task_dir) + قارن % resolved vs baseline.
- Update الـ theft memos + MASTER_INDEX بـ 5.88+ لو لقينا patterns جديدة من الـ runs.
- في الـ evo engine: استخدم الـ real agent_execution.json + constitutional_report كـ fitness بدل الـ proxy 0.8 (يربط أقوى بالـ AlphaEvolve evaluator).

**الحالة**: 🟢 (prompts محسنة + run_49 + run_50 evidence موثق + GENERAL protected).

**ما أصبح عندنا دلوقتي**: الـ evolutionary loop بقى أكثر استقرارًا (من run_48 فشل → run_49 نجاح جزئي مع bugs مصححة بالـ feedback → run_50 على gpqa بدون أي crash في الـ format). الـ AlphaEvolve theft (5.84) + 5.87 (robust logging) + 5.88 (QA guidance) بيخلّي الـ generator أقوى و الـ self-improvement أقرب للـ "discovery engine" الحقيقي.

### سرقة شرعية إضافية 5.88 (امتداد لـ AlphaEvolve + run_50 على gpqa)

**المصدر (+ رابط)**: 
- الـ run_50 (2026-06-04) على gpqa (الـ hard reasoning benchmark) مع --use_evolutionary_discovery + gpt-oss-120b:free.
- الدليل: الـ log الكامل (الـ crash السابق "KeyError: 'train_df'" اختفى، الـ target_agent اتولد بنجاح في الـ gen_1 و gen_2، الـ execution log اتكتب صح، الـ evaluate.py اشتغل وطلع evaluation_results.json لـ 198 سؤال، constitutional ارتفع من 0/10 لـ 5/10 في Gen2، evo اشتغل مرتين بنفس الـ fitness 0.800. بس الـ agent قال "No recognizable data files found for task." و الـ accuracy 0.00% (198 missing) لأنه ما عملش processing حقيقي للـ JSON questions).

**الفكرة الأساسية (السرقة)**: 
- أول run حقيقي على benchmark صعب (gpqa diamond — graduate science multiple choice).
- الـ LLM generator لسه بيستخدم fallback عام ("no data files") بدل ما يعمل الـ logic الصح لـ QA tasks (load json, per question pipeline + client reasoning لـ اختيار A/B/C/D).
- السرقة: نضيف guidance قوي و GENERAL في الـ prompt للـ Q&A tasks عشان الـ evo ينتج agents بترد على أسئلة حقيقية مش بس بتكتب كود generic.

**ما أخذناه**: 
- الـ run_50 log + الـ evaluation output كـ evidence أن الـ harness شغال (evaluate.py + constitutional + evo + logging).
- الـ failure mode ("No recognizable data files") كـ signal للـ prompt improvement.

**ما تركناه عمدًا**: 
- أي hardcoding لـ gpqa file names أو domains (biology/chemistry/physics) — كل حاجة GENERAL لـ "Q&A/reasoning tasks".

**ما أصبح عندنا**: 
- في `genesis/orchestrator.py`: قسم جديد "**DEDICATED GUIDANCE FOR Q&A / MULTIPLE-CHOICE / GRADUATE REASONING TASKS**" (load json, per-question pipeline + client for letter choice, per-question try/except, write answers for evaluate.py).
- FEEDBACK prompt محدث بنفس الـ guidance.
- الـ run_50 نجح كامل (أول hard benchmark مع evo بدون crash في الـ prompt).

**الدليل**: 
- run_50 log: no KeyError, evo x2, constitutional 0→5/10, evaluate.py ran on 198 questions and saved evaluation_results.json (even if 0%).
- الـ agent لسه generic (0%) — ده الـ signal اللي خلّانا نضيف الـ QA section.

**نقاط الدمج**: orchestrator prompts + run_openrouter_benchmark + MASTER_INDEX (5.88) + theft memo.

**المخاطر**: لسه الـ accuracy 0% (الـ agent ما بيجاوبش الأسئلة) — لازم نراجع الـ generated target_agent.py من الـ run_50 عشان نشوف الـ code الفعلي ونحسن أكتر.

**الـ Tasks المقترحة**: 
- Task 6.3: بعد الـ prompt الجديد، اعمل run_51 على gpqa و قارن الـ accuracy و الـ agent code.
- Task 9: استمر في الـ real benchmarks (gpqa lift + SWE-bench).

**الحالة**: 🟢 (5.88 مضاف + prompt pushed).

**الدليل الكامل**: الـ log اللي بعته لـ run_50 + الـ commit 40a4a72 + MASTER_INDEX update.

🏴‍☠️ سرقة شرعية عالية الجودة — protected the long-term vision. 

لو عايز نكمل "حلب" أو نعدل الـ prompt أكتر (أو نشوف الـ generated code من run_50)، قولي فورًا. الـ next step المقترح: git pull + rm -rf runs/run_50 + re-run نفس الـ command عشان تشوف تأثير الـ QA section الجديد.