# GENESIS — الجرد الكامل للمشروع
# تاريخ: 2026-06-08 | يُحدَّث مع كل تغيير
# 232 ملف Python | 937 test passing | 53+ runs حقيقية

---

## نظرة عامة — الأرقام الحقيقية

```
المشروع يتكوّن من:
  232  ملف Python
  139  ملف .md (توثيق + خطط)
  35   test file  →  937 test passing
  6    task types (GPQA, lawbench, chess, titanic, micro_task, ...)
  53+  runs حقيقية على GPQA
  11   OpenRouter API keys
  9    Google AI Studio keys
```

---

## التقسيم الحالي — 6 Sections طبيعية

```
SECTION A: INFRASTRUCTURE        (tools/ + genesis/tools/ + genesis/util.py)
SECTION B: ORCHESTRATOR          (genesis/orchestrator.py)
SECTION C: OUTER LOOP ENGINES    (genesis/*.py بدون orchestrator)
SECTION D: INNER PIPELINE        (virtual_genesis/runtime/)
SECTION E: EVALUATION SUITE      (virtual_genesis/eval/)
SECTION F: KNOWLEDGE & DOCS      (GENESIS_*.md + PAPER/)
```

---

## SECTION A: INFRASTRUCTURE
**الوظيفة:** كل ما يشغّل الـ system من تحت — API، models، keys، utilities

### A1: API Key Management
```
tools/api_key_pool.py          620 lines
  Classes: KeyStats, APIKeyPool
  Functions: load_keys_from_env(), get_default_pool(), rotate_key()
  الوظيفة: 11 OpenRouter key rotation + rate limit tracking
  يُستخدَم في: orchestrator (SERPER, OPENAI), genesis/util.py
  الحالة: ✅ مبني بالكامل
```

### A2: Model Registry
```
tools/model_registry.py
  الوظيفة: سجل النماذج المتاحة + capabilities
  يُستخدَم في: orchestrator --meta_model flag
  الحالة: ✅ مبني

tools/providers.py
  الوظيفة: مزودي الـ API (OpenRouter, Google, Pioneer)
  الحالة: ✅ مبني
```

### A3: Core Utilities
```
genesis/util.py                 448 lines
  Functions: run_agent(), make_openai_client(), make_anthropic_client()
  الوظيفة: LLM client factory + agent subprocess runner
  يُستخدَم في: orchestrator (كل LLM call)
  الحالة: ✅ مبني
```

### A4: Web Search Tool
```
genesis/tools/web_search.py     437 lines
  Classes: SearchResult, EvidenceClaim, EvidenceLog
  Functions: web_search(), extract_keywords(), multi_query_search()
  الوظيفة: Serper API + Jina Reader، 3 modes (quick/deep/read)
  مسروق من: DeepResearcher + A-RAG + SAGE + Rulers
  يُستخدَم في: target_agent.py (عند --use_web_search)
  الحالة: ✅ مبني (39 test)
  ينقصه: ينتقل لـ Tool Hub (Section D في المستقبل)
```

### A5: Benchmark Tools
```
tools/gpqa_pure_baseline.py     — baseline بدون pipeline
tools/run_multi_model_benchmark.py — multi-model comparison
tools/diagnose_run_53.py        — diagnostic tool
الحالة: ✅ utility scripts
```

### A6: Persistence (SQLite)
```
virtual_genesis/persistence/
  sqlite_store.py               — memory store
  sqlite_concept_registry.py    — concept DB
  sqlite_theory_registry.py     — theory DB
  sqlite_identity_store.py      — identity DB
  checkpoint.py                 — state checkpointing
  migrations.py                 — DB migrations
الوظيفة: كل الـ SQLite databases للـ virtual_genesis pipeline
الحالة: ✅ مبني
```

### A7: FastAPI (Internal)
```
virtual_genesis/api/
  app.py         — FastAPI application
  config.py      — API configuration
  llm_adapter.py — LLM abstraction
  llm_reasoning.py
  session.py
الوظيفة: REST API للتواصل الداخلي (غير مُستخدَم في main flow)
الحالة: ✅ مبني (مش في main loop)
```

---

## SECTION B: ORCHESTRATOR
**الوظيفة:** القلب الرئيسي — يُشغَّل مرة لكل run، يُكرّر الـ generation loop

```
genesis/orchestrator.py         1915 lines

الـ Sections الداخلية:
  CLI Args     → --task, --max_gen, --backend, --use_goal_spec,
                 --use_web_search, --use_regime_detection,
                 --use_evolutionary_discovery,
                 --local_filter, --use_goal_spec
  SECTION 0    → Goal Specification (INTENT ENGINE)
  SECTION 1    → Load Task Files
  SECTION 2    → Setup Run Directories
  SECTION 2.5  → Initialize Research Memory
  SECTION 3    → Define Prompts (META + FEEDBACK)
  SECTION 4    → Meta-Agent (Gen 1 writer)
  SECTION 5    → Generation Loop:
    5a         → Run Target Agent
    5a.1       → Evaluation (closed + open LLM judge)
    5a.2       → Constitutional Check
    5a.2.5     → Enhanced Pipeline Signal Extraction
    5a.3       → Evolutionary Discovery
    5a.4       → Regime Transition Check
    5b         → Feedback Agent (next gen writer)
  SECTION 7    → Record in Research Memory

الحالة: ✅ مبني (1915 lines)
ينقصه في Sections:
  - Safety Monitor (A2 — قبل SECTION 5)
  - Telemetry events (في كل section)
  - Meta-Optimizer (5a.5 — جديد)
  - Skill extraction (في 5a.1)
  - Agent Hub loading (في SECTION 0)
```

---

## SECTION C: OUTER LOOP ENGINES
**الوظيفة:** الـ Engines التي تُشغَّل من الـ orchestrator لكل generation

### C1: INTENT ENGINE
```
genesis/goal_specification.py   484 lines
  Classes: SubGoal, GoalSpec
  Functions: decompose_task_with_llm(), run_goal_specification()
  الوظيفة: LLM يُجزّئ task → sub-goals مرتبة + search queries
  مسروق من: MA-RAG + HTN + SAGE
  يُنتج: goal_spec.json (per run)
  يُستخدَم في: META_AGENT_PROMPT (Section 3)
  الحالة: ✅ مبني (31 test)
  ينقصه: Skill Library integration
```

### C2: CRITIC ENGINE — Open Tasks
```
genesis/open_task_evaluator.py  600 lines
  Classes: CriterionVerdict, OpenTaskResult
  Functions: run_open_task_evaluation(), extract_rubric_from_task()
  الوظيفة: LLM-as-judge للـ open-ended tasks (بدون evaluate.py)
  مسروق من: Rulers + InfoDeepSeek + G-Eval
  يُنتج: open_task_eval.json (per gen)
  يُستخدَم في: Section 5a.1
  الحالة: ✅ مبني (36 test)
```

### C3: CRITIC ENGINE — Rules
```
genesis/constitutional_evaluator.py  334 lines
  Classes: RuleViolation, ConstitutionalReport
  Functions: check_regression_free(), check_verifiability(), evaluate_constitutional()
  الوظيفة: 5 rule-based checks على الـ target agent code
  مسروق من: Constitutional AI (Meta)
  يُنتج: constitutional_report.json (per gen)
  يُستخدَم في: Section 5a.2
  الحالة: ✅ مبني
```

### C4: COGNITIVE ENGINE BRIDGE
```
genesis/enhanced_pipeline_bridge.py  398 lines
  Classes: LadderStateSummary
  Functions: run_enhanced_pipeline_check(), extract_enhanced_signals_from_gen()
  الوظيفة: يستخرج signals من enhanced pipeline (LadderAscent, Semantic, Value)
  يُنتج: ladder_state.json (per gen)
  يُستخدَم في: Section 5a.2.5 → FEEDBACK_AGENT_PROMPT
  الحالة: ✅ مبني (31 test)
  ينقصه: target agents نادراً تكتب enhanced_signals.json
```

### C5: FEEDBACK ENGINE — SPIN
```
genesis/spin_feedback.py        342 lines
  Classes: GapReport
  Functions: compute_semantic_gap(), generate_spin_feedback()
  الوظيفة: يحسب cosine distance بين gens → يكتشف stagnation
  مسروق من: SPIN (DeepSeek)
  يُنتج: spin_section في FEEDBACK_AGENT_PROMPT
  الحالة: ✅ مبني
```

### C6: MEMORY ENGINE — Context
```
genesis/context_manager.py      546 lines
  Classes: ContextManager
  Functions: initialize(), add_generation(), finalize()
  الوظيفة: context.md تراكمي + LLM summary كل generation
  يُنتج: context.md (per run, grows)
  يُستخدَم في: Section 3 + 5b
  الحالة: ✅ مبني
```

### C7: MEMORY ENGINE — Cross-Run
```
genesis/research_memory.py      288 lines
  Classes: ResearchEntry, ResearchMemory, ResearchMemoryStore (SQLite)
  Functions: add_entry(), get_insights_for_task(), search()
  الوظيفة: insights نصية تتراكم عبر runs → تُغذّي META_AGENT_PROMPT
  يُستخدَم في: Section 2.5 + Section 7
  الحالة: ✅ مبني
  ينقصه: Skill Library (procedural memory)
```

### C8: COGNITIVE BRIDGE
```
genesis/cognitive_bridge.py     472 lines
  Classes: BridgeMode, CognitiveContext, CognitiveBridge, OrchestratorCognitiveIntegration
  Functions: build_cognitive_context(), enhance_prompt(), get_tier_recommendation()
  الوظيفة: يُغذّي META_AGENT_PROMPT بـ concepts + theories + tier recommendation
  مسروق من: DeepMind LEAP/Aletheia
  الحالة: ✅ مبني
  ملاحظة: مش موصول مباشرة من orchestrator! (موجود لكن غير مستدعي)
```

### C9: LLM HELPERS
```
genesis/llm_helpers.py
  Functions: extract_response_text(), extract_letter(), build_mcq_prompt()
  الوظيفة: battle-tested LLM utilities للـ target agents
  يُستخدَم في: target_agent.py templates
  الحالة: ✅ مبني
```

### C10: المطلوب إضافته (❌ غير موجود)
```
genesis/telemetry.py            ← TELEMETRY ENGINE (Phase A)
genesis/safety_monitor.py       ← SAFETY ENGINE (Phase A)
genesis/skill_library.py        ← SKILL ENGINE (Phase B)
genesis/skill_extractor.py      ← SKILL ENGINE (Phase B)
genesis/meta_optimizer.py       ← META ENGINE (Phase C)
genesis/agent_hub/              ← AGENT HUB (Phase current)
```

---

## SECTION D: INNER PIPELINE (Virtual GENESIS)
**الوظيفة:** يُشغَّل داخل كل target_agent.py — العقل الداخلي للـ agent

### D1: Pipeline Entry Points
```
virtual_genesis/runtime/pipeline/minimal_run.py     381 lines
  Functions: run_minimal_pipeline()
  الوظيفة: الـ pipeline الأساسي — يُشغّل 8 components بالترتيب
  يُستخدَم في: كل target_agent.py (required)
  الحالة: ✅ مبني

virtual_genesis/runtime/enhanced_pipeline/enhanced_run.py  261 lines
  Functions: run_enhanced_pipeline()
  الوظيفة: pipeline كامل + LadderAscent + SemanticVerifier + Value
  يُستخدَم في: target_agent.py (optional، يُقترح في template)
  الحالة: ✅ مبني (لكن agents نادراً تستخدمه)
```

### D2: Task Processing
```
virtual_genesis/runtime/task_ingress/
  service.py      — TaskIngress: normalize + classify + detect_type
  normalize.py    — text normalization
الوظيفة: الـ gate الأول — يفهم ما هو الـ task
الحالة: ✅ مبني (test: test_task_ingress.py)
```

### D3: Concept Engine (15 مفهوم → 5 مُختار)
```
virtual_genesis/runtime/concept_engine/
  cycle.py       — run_concept_cycle()
  proposer.py    — ConceptProposer
  selector.py    — ConceptSelector (selectivity filter)
  registry.py    — InMemoryConceptRegistry
  apply.py       — ConceptApply
  config.py      — selectivity config
  scope.py       — concept scope
الوظيفة: يُكوّن concepts من الـ task → يُصفّي الأهم
الحالة: ✅ مبني (test: test_concept_engine.py)
```

### D4: Economy Control (Tier Router)
```
virtual_genesis/runtime/economy_control/
  router.py      — choose_tier(), choose_tier_anomaly_aware()
  ledger.py      — InMemoryLedgerStore, LedgerEntry
  escalation.py  — EscalationPolicy
  reports.py     — generate_economy_report()
الوظيفة: يختار Tier 1/2/3 حسب complexity + budget
الحالة: ✅ مبني (test: test_value_computation.py)
```

### D5: Memory OS (داخل الـ agent)
```
virtual_genesis/runtime/memory_os/
  store.py         — InMemoryMemoryStore
  retriever.py     — MemoryRetriever (semantic search)
  utility.py       — utility scoring
  forgetting_policy.py — productive forgetting
الوظيفة: ذاكرة داخل الـ agent (per-run، in-memory)
مسروق من: DeepMind
الحالة: ✅ مبني (test: test_productive_forgetting.py)
ملاحظة: هذا DIFFERENT من Research Memory (cross-run) في Section C7
```

### D6: Theory Runtime
```
virtual_genesis/runtime/theory_runtime/
  builder.py    — LocalTheoryBuilder
  registry.py   — InMemoryTheoryRegistry
  apply.py      — TheoryApply
الوظيفة: يبني theories من الـ task → يطبّقها على الـ reasoning
مسروق من: DeepMind CoScientist
الحالة: ✅ مبني (test: test_theory_leverage.py)

virtual_genesis/runtime/theory_executables/
  theories.py   — executable theories (tested against live evidence)
الحالة: ✅ مبني (test: test_theory_executables.py)
```

### D7: Anomaly Runtime
```
virtual_genesis/runtime/anomaly_runtime/
  service.py    — AnomalyRuntime
الوظيفة: يكتشف anomalies → يُحوّلها لـ leverage
مسروق من: DeepMind Aletheia
الحالة: ✅ مبني (test: test_anomaly_leverage.py)
```

### D8: Identity Runtime
```
virtual_genesis/runtime/identity_runtime/
  governance.py         — check_identity_alignment()
  drift_detector.py     — IdentityDriftDetector
  crisis_detector.py    — IdentityCrisisDetector
  paradigm_fork.py      — ParadigmFork
  commitment_ledger.py  — CommitmentLedger
الوظيفة: يُحافظ على identity consistency + يكتشف paradigm shifts
مسروق من: DeepMind LEAP
الحالة: ✅ مبني (test: test_identity_governance.py, test_paradigm_fork.py)
```

### D9: Cognitive Components (الباقية)
```
virtual_genesis/runtime/semantic_verifier/
  verifier.py    — SemanticVerifier, TheoryFalsificationEngine
الوظيفة: يتحقق من reasoning semantically
الحالة: ✅ مبني (test: test_semantic_verifier.py)

virtual_genesis/runtime/semantic_grounding/
  grounding_checker.py — GroundingChecker
  integration.py       — GroundingAwareConceptEngine
الحالة: ✅ مبني (test: test_semantic_grounding.py)

virtual_genesis/runtime/ladder_ascent/
  engine.py    — LadderAscentEngine (levels 0→4), LadderState
الوظيفة: تتبّع epistemic progression (Foundation→Mastery)
الحالة: ✅ مبني (test: test_ladder_ascent.py)

virtual_genesis/runtime/value_computation/
  value_functions.py — CognitiveReturnCalculator, VoC/VoI/VoV
الوظيفة: يحسب الـ economic value of cognitive operations
الحالة: ✅ مبني (test: test_value_computation.py)

virtual_genesis/runtime/contradiction_runtime/
  service.py    — ContradictionRuntime
الحالة: ✅ مبني (test: test_concept_schema.py)

virtual_genesis/runtime/blackboard_core/
  service.py    — BlackboardService (central state)
الحالة: ✅ مبني

virtual_genesis/runtime/reasoning_runtime/
  service.py    — ReasoningRuntime
الحالة: ✅ مبني

virtual_genesis/runtime/verification_runtime/
  service.py    — VerificationRuntime
الحالة: ✅ مبني
```

### D10: Core Objects (Data Models)
```
virtual_genesis/core/objects/
  memory.py       — MemoryUnit
  concept.py      — ConceptObject
  theory.py       — LocalTheoryObject
  anomaly.py      — AnomalyObject
  blackboard.py   — BlackboardObject
  identity.py     — AgentIdentityObject
  task.py         — TaskObject
  task_case.py    — TaskCase
  ledger.py       — LedgerEntry
  cost.py         — CostObject
  decision.py     — DecisionObject
  eval.py         — EvalObject
  contradiction.py — ContradictionObject
  provenance.py   — ProvenanceObject
  scope.py        — ScopeObject
  base.py         — BaseObject
الحالة: ✅ مبنية (الـ data models الأساسية)

virtual_genesis/core/concept_schema.py — ConceptSchema
virtual_genesis/core/ontology/enums.py — domain enums
```

---

## SECTION E: EVALUATION SUITE
**الوظيفة:** قياس، تحليل، تطوير — عبر كل الـ generations

### E1: Regime Detection (H8 — مسروق Wang & Buehler)
```
virtual_genesis/eval/runners/regime_transition_detector.py  462 lines
  Classes: SignalStatus, TransitionVerdict, RegimeTransitionDecision
  Functions: detect_saturation(), detect_degradation(), detect_blind_spot()
  الوظيفة: 3 signals → 2-of-3 → regime change verdict
  الحالة: ✅ مبني (55 test)

virtual_genesis/eval/runners/regime_orchestrator_bridge.py  239 lines
  Functions: run_regime_check(), load_regime_history()
  الوظيفة: الـ entry point للـ orchestrator
  الحالة: ✅ مبني (يستقبل open_task_score الآن)

virtual_genesis/eval/runners/conditions_runner.py  424 lines
  Classes: ConditionProfile (6 profiles), ComparisonConfig
  Functions: run_conditions_comparison(), run_multi_ablation()
  الحالة: ✅ مبني (48 test)

virtual_genesis/eval/runners/failure_extractor.py  344 lines
  Functions: extract_failures_from_generation(), build_accuracy_history()
  الحالة: ✅ مبني (34 test)

virtual_genesis/eval/runners/run_self_benchmark_cycle.py
  Functions: run_self_benchmark_cycle()
  الحالة: ✅ مبني (39 test)

virtual_genesis/eval/negative_memory_adversarial.py
  Functions: generate_from_negative_memory()
  الوظيفة: T-13→H8 bridge (failures → adversarial tests)
  الحالة: ✅ مبني (14 test)
```

### E2: Eval Runners (Legacy)
```
virtual_genesis/eval/runners/
  run_local_eval.py         — v1 local evaluation
  run_local_eval_v2.py      — v2
  run_local_eval_v3.py      — v3 + cases
  run_local_eval_v3b.py     — v3b curriculum
  run_local_eval_v3c_curriculum.py
  run_local_eval_v4.py      — v4
  run_local_eval_v5.py      — v5
  run_local_eval_v6.py      — v6
  run_real_llm_eval.py      — real LLM eval
  run_real_llm_broader.py   — broader domain
  run_broader_domain_eval.py
  run_adversarial_llm_eval.py
  run_family_selectivity_ablation.py
  run_selectivity_ablation.py
  run_full_integration.py
  run_condition.py
  compare_conditions.py
الحالة: ✅ مبنية (legacy — تُستخدَم للبحث والتحليل)
```

### E3: Reports Suite (14+)
```
virtual_genesis/eval/reports/
  concept_selectivity.py    — concept selection analysis
  concept_utility.py        — concept utility scoring
  domain_transfer.py        — cross-domain performance
  theory_analytics.py       — theory effectiveness
  theory_usage.py           — which theories used when
  curriculum_analytics.py   — learning progression
  contradiction_analytics.py — contradictions found
  anomaly_candidates.py     — anomaly analysis
  blind_spot_discovery.py   — blind spots
  family_breakdown.py       — task family analysis
  family_selectivity_detail.py
  perturbation_resistance.py
  premium_roi.py            — Tier 3 worth it?
  diagnostic_value.py
  governance_curriculum_analytics.py
  integration_summary.py
  summary.py                — overall summary
الحالة: ✅ مبنية (تُستخدَم للبحث)
```

### E4: Perturbations & Adversarial
```
virtual_genesis/eval/perturbations/
  contract_perturbations.py   — contract-based perturbations
  taskcase_variants.py        — task case variations
  taskcase_variants_hard.py   — hard variants
الحالة: ✅ مبنية (test: test_contract_perturbations.py)

virtual_genesis/eval/task_sets/
  prototype_v1.py → prototype_v7_broader_domain.py  (7 versions)
  adversarial_hard_cases.py
  anti_shortcut_benchmark.py
الحالة: ✅ مبنية (task sets للتقييم)

virtual_genesis/eval/benchmark_generator.py
الحالة: ✅ مبني
```

---

## SECTION F: KNOWLEDGE & DOCS
**الوظيفة:** التوثيق، الخطط، نتائج البحث

### F1: Analysis Papers (PAPER/analysis/)
```
GENESIS_MASTER_ARCHITECTURE.md         — الخريطة الكاملة
GENESIS_ARCHITECTURE_REDESIGN_PLAN.md  — 5 phases plan
GENESIS_THREE_PILLARS_PLAN.md          — Skills+Meta+Agents
GENESIS_AGENT_HUB_ARCHITECTURE.md      — Agent Hub design
GENESIS_FULL_INVENTORY.md              — هذا الملف
WEB_SEARCH_DEEP_RESEARCH_THEFT_STRATEGY.md
REGIME_TRANSITION_INJECTION_ROADMAP.md
SELF_BENCHMARKING_AS_REGIME_DETECTOR.md
THEFT_2606.01444_analysis.md
THEFT_2606_01444_DEEP.md
```

### F2: Theory Memos (Root level GENESIS_*.md — 124 ملف)
```
فئات:
  Theory       → GENESIS_*_Theory_AR.md (فلسفة ونظرية)
  Spec         → GENESIS_*_Spec_AR.md (مواصفات تقنية)
  Memo         → GENESIS_*_Memo_AR.md (قرارات وتحليلات)
  Theft        → GENESIS_DeepMind_*_Theft_AR.md (سرقات مُوثّقة)
  Evidence     → GENESIS_*_Evidence_Memo_AR.md (نتائج تجريبية)
الحالة: توثيق بحثي — المرجع الأساسي للقرارات
```

### F3: PAPER/
```
PAPER/
  data/         — run results (JSON)
  figures/      — figure descriptions
  analysis/     — خطط وتحليلات (Section F1)
  ideas/        — أفكار قيد الدراسة
  notes/        — ملاحظات
  philosophy/   — الفلسفة الأساسية
  references/   — مراجع
  tables/       — جداول نتائج
  theory/       — نظريات مفصّلة
```

### F4: Root Documentation
```
README.md                    — الواجهة الرئيسية
PROJECT_README.md            — تفاصيل المشروع
SETUP_AND_RUN_GUIDE.md       — دليل التشغيل
AGENT_OPERATING_MANUAL.md    — دليل تشغيل الـ agents
MASTER_TIMELINE.md           — الجدول الزمني
PAPER.md                     — مسودة الورقة البحثية
STRATEGIC_DEVELOPMENT_PLAN_2026_06_v2.md — الخطة الاستراتيجية
```

---

## Tasks Library — المهام المتاحة

```
genesis/tasks/
├── gpqa/                    ← GPQA Diamond (198 Q) — الرئيسي
│   ├── data/public/
│   │   ├── task.md
│   │   ├── evaluate.py      ← closed eval
│   │   └── diamond_questions.json
│   └── reference/
│       └── reference_target_agent.py
│
├── micro_task/              ← Micro-Task Economy Research (جديد، open)
│   ├── data/public/task.md  ← no evaluate.py (open task)
│   └── reference/
│       └── reference_target_agent.py  ← 3-turn pipeline
│
├── lawbench/                ← Legal QA
├── longcot-chess/           ← Chess reasoning
├── spaceship-titanic/       ← Tabular ML
├── genesis_cognitive_integration/  ← GENESIS self-test
├── genesis_optimization/    ← GENESIS optimization
└── _shared/                 ← shared reference agent
```

---

## Tests Coverage Map

```
Section A (Infrastructure):
  test_web_search.py              39 tests  ← genesis/tools/web_search.py
  
Section C (Outer Loop Engines):
  test_goal_specification.py      31 tests  ← INTENT ENGINE
  test_open_task_evaluator.py     36 tests  ← CRITIC ENGINE
  test_enhanced_pipeline_bridge.py 31 tests ← COGNITIVE BRIDGE
  test_cognitive_bridge.py        ?  tests  ← cognitive_bridge.py
  test_llm_helpers.py             ?  tests  ← llm_helpers.py
  
Section D (Inner Pipeline):
  test_concept_engine.py          ?  tests  ← concept_engine/
  test_concept_schema.py          ?  tests  ← core/concept_schema.py
  test_task_ingress.py            ?  tests  ← task_ingress/
  test_theory_leverage.py         ?  tests  ← theory_runtime/
  test_theory_executables.py      ?  tests  ← theory_executables/
  test_anomaly_leverage.py        ?  tests  ← anomaly_runtime/
  test_identity_governance.py     ?  tests  ← identity_runtime/
  test_paradigm_fork.py           ?  tests  ← identity_runtime/paradigm_fork.py
  test_ladder_ascent.py           ?  tests  ← ladder_ascent/
  test_value_computation.py       ?  tests  ← value_computation/
  test_semantic_verifier.py       ?  tests  ← semantic_verifier/
  test_semantic_grounding.py      ?  tests  ← semantic_grounding/
  test_semantic_grounding_v2.py   ?  tests
  test_productive_forgetting.py   ?  tests  ← memory_os/forgetting_policy.py
  test_enhanced_pipeline.py       ?  tests  ← enhanced_pipeline/
  test_persistence.py             ?  tests  ← persistence/
  
Section E (Evaluation):
  test_regime_transition.py       55 tests  ← regime_transition_detector.py
  test_conditions_runner.py       48 tests  ← conditions_runner.py
  test_failure_extractor.py       34 tests  ← failure_extractor.py
  test_self_benchmarking.py       39 tests  ← run_self_benchmark_cycle.py
  test_contract_perturbations.py  ?  tests  ← perturbations/
  test_perturbation_operators.py  ?  tests
  test_adversarial_validation.py  ?  tests
  test_broader_domain.py          ?  tests
  test_evolutionary_discovery.py  ?  tests  ← evolutionary_discovery_engine
  test_eval_runners.py            ?  tests
  test_full_integration.py        ?  tests
  test_real_llm.py                ?  tests
  test_api.py                     ?  tests  ← virtual_genesis/api/

TOTAL: 937 tests — كلهم passing
```

---

## الـ Artifacts الكاملة (per run)

```
runs/run_N/
├── goal_spec.json              ← INTENT ENGINE (once/run)
│
├── gen_1/
│   ├── target_agent.py         ← Meta-Agent writes
│   ├── target_agent_stdout.log ← execution log
│   ├── agent_execution.json    ← cognitive pipeline result
│   ├── enhanced_signals.json   ← COGNITIVE ENGINE (optional, rarely written)
│   ├── evidence_log.json       ← GROUNDING ENGINE (when --use_web_search)
│   ├── open_task_eval.json     ← CRITIC ENGINE open tasks
│   ├── evaluation_results.json ← CRITIC ENGINE closed tasks (evaluate.py)
│   ├── constitutional_report.json ← CRITIC ENGINE rules
│   ├── regime_transition_report.json ← EVOLUTION ENGINE
│   ├── regime_history.json     ← EVOLUTION ENGINE
│   ├── ladder_state.json       ← COGNITIVE BRIDGE
│   ├── evolutionary_discovery.json ← EVOLUTION ENGINE
│   ├── meta_agent_prompt.txt   ← transparency
│   ├── feedback_agent_prompt.txt ← transparency
│   └── context.md              ← MEMORY ENGINE (cumulative)
│
├── gen_2/ ... gen_N/           ← same structure
└── (no run_summary.json yet — needs TELEMETRY ENGINE)

Persistent (cross-run):
  research_memory.db            ← MEMORY ENGINE cross-run
  (skill_library.db)            ← SKILL ENGINE (❌ not yet)
  (agent_registry.db)           ← AGENT HUB (❌ not yet)
```

---

## ما ينقص — Gap Summary

```
Section A: ينقص
  genesis/telemetry.py        (TELEMETRY ENGINE)
  genesis/safety_monitor.py   (SAFETY ENGINE)

Section C: ينقص
  genesis/skill_library.py    (SKILL ENGINE)
  genesis/skill_extractor.py
  genesis/meta_optimizer.py   (META ENGINE)
  genesis/agent_hub/          (AGENT HUB — current focus)

Section D: جزئي
  enhanced_signals.json — نادراً ما تكتبه الـ agents
  Tool Hub — tools مش في hub منفصل

Section E: مكتمل تقريباً
  Evidence Coverage Report فقط ناقص

Section F: مكتمل
  (التوثيق يُحدَّث مع كل phase)
```

---

## الأولوية — ماذا نبني أولاً؟

```
الآن (current focus):    AGENT HUB foundation
  genesis/agent_hub/
    soul.py           ← SOUL section
    memory/           ← MEMORY section
    tool_hub/         ← TOOL HUB section
    agent.py          ← AgentSpec
    registry.py       ← AgentRegistry

ثم:                      SKILL ENGINE
  genesis/skill_library.py
  genesis/skills/

ثم:                      META ENGINE
  genesis/meta_optimizer.py

ثم:                      TELEMETRY + SAFETY
  genesis/telemetry.py
  genesis/safety_monitor.py

أخيراً:                  ARCHITECTURE EVOLUTION
  (بعد اكتمال الباقي)
```
