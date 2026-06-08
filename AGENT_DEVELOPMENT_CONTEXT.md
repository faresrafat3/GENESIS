# GENESIS — AGENT DEVELOPMENT CONTEXT
# ════════════════════════════════════════════════════════════════
# هذا الملف = المرجع الوحيد لأي AI Agent يعمل على تطوير GENESIS
# يُحدَّث بعد كل phase — آخر تحديث: 2026-06-08
# ════════════════════════════════════════════════════════════════

---

## 0. HOW TO READ THIS FILE

أي AI agent يعمل على هذا المشروع يقرأ هذا الملف أولاً.
يحتوي على:
- ما هو المشروع وما فلسفته
- كل component موجود: من أين جاء، ما وظيفته، كيف يُستدعى
- كل component مطلوب: ما هو، من أين يُسرق، أين يُوضع
- Rules لا تُكسر
- الحالة الحالية بالأرقام

---

## 1. GENESIS — ما هو

```
GENESIS = Agentic Self-Development Loop
الفكرة: النظام يكتب agents → يشغّلها → يقيّمها → يحسّنها → يكرر
الـ agent نفسه يفكر → يبحث → ينفذ → يتحقق → يُنتج

ليس: chatbot | RAG system | fine-tuning pipeline
هو: self-improving agent factory
```

**الأرقام الحالية:**
- 232 ملف Python
- 937 test — كلهم passing (يجب أن يبقوا كذلك بعد كل تغيير)
- 6 sections رئيسية (A→F)
- 53+ runs حقيقية على GPQA

---

## 2. RULES — لا تُكسر أبداً

```
RULE 1: لا تكسر الـ 937 tests الموجودة
  ← دائماً: python3 -m pytest tests/ -q قبل كل commit

RULE 2: لا تكتب API keys في ملفات — env vars فقط
  ← SERPER_API_KEY, OPENAI_API_KEY, etc. من os.getenv()

RULE 3: backward compatibility مقدّسة
  ← from genesis.tools.web_search import web_search يجب أن يبقى يعمل
  ← أي import قديم في orchestrator.py يبقى يعمل

RULE 4: كل ملف جديد له header documentation
  ← الـ docstring الأولى تحتوي: Source + Stolen from + Usage + Integration

RULE 5: كل section لها __init__.py بـ clean public API
  ← الـ orchestrator يستورد من __init__.py فقط

RULE 6: git commit بعد كل phase كاملة تشتغل
  ← رسالة: "feat: {SectionName} — {description}, {N} tests"

RULE 7: لا تغيّر orchestrator.py core logic
  ← فقط أضف imports وinjections في الأماكن المحددة
```

---

## 3. PROJECT STRUCTURE — الحالة الحالية

```
genesis/                    ← الـ package الرئيسي
├── orchestrator.py         ← 1915 lines — القلب (لا تعدّل core logic)
├── util.py                 ← make_openai_client(), run_agent()
├── llm_helpers.py          ← LLM utilities للـ agents
├── constitution.json       ← constitutional rules
│
├── tools/                  ← [LEGACY — يُبقى، يُغلَّف بـ tool_hub]
│   └── web_search.py       ← SearchResult, EvidenceLog, web_search()
│
├── goal_specification.py   ← INTENT ENGINE (Section 0 في orchestrator)
├── open_task_evaluator.py  ← CRITIC ENGINE open tasks (Section 5a.1)
├── constitutional_evaluator.py ← CRITIC ENGINE rules (Section 5a.2)
├── enhanced_pipeline_bridge.py ← COGNITIVE ENGINE signals (Section 5a.2.5)
├── spin_feedback.py        ← FEEDBACK ENGINE semantic gap
├── context_manager.py      ← MEMORY ENGINE context.md
├── research_memory.py      ← MEMORY ENGINE cross-run (SQLite)
└── cognitive_bridge.py     ← COGNITIVE BRIDGE (مش موصول في orchestrator!)

virtual_genesis/            ← Inner Pipeline — لا تعدّل
tools/                      ← Infrastructure (api_key_pool, model_registry)
tests/                      ← 937 tests — لا تحذف أياً منها
PAPER/                      ← توثيق وتحليل
```

---

## 4. COMPONENT CATALOG — كل component بتفاصيله

### FORMAT لكل component:

```
COMPONENT_ID: {اسم فريد}
LOCATION: {المسار في المشروع}
STATUS: BUILT ✅ | PARTIAL ⚠️ | PLANNED ❌
SOURCE: {من أين جاء — ورقة بحثية أو مشروع}
STOLEN_FROM: {اسم المشروع + arXiv ID}
WHAT_WAS_STOLEN: {ما أخذناه بالضبط}
WHAT_WAS_MISSED: {ما فوّتناه من الأصل}
GENESIS_ADAPTATION: {كيف اختلف تطبيقنا عمداً}
CALLED_BY: {من يستدعيه}
CALLS: {ماذا يستدعي}
ARTIFACT_IN: {ما يُنتج من ملفات}
ARTIFACT_OUT: {ما يقرأ من ملفات}
INVOCATION: {كيف يُستدعى — كود}
TESTS: {ملف الاختبارات}
```

---

### 4.1 EXISTING COMPONENTS (مبنية ✅)

---

**COMPONENT_ID: WEB_SEARCH_TOOL**
```yaml
LOCATION: genesis/tools/web_search.py
STATUS: BUILT ✅
SOURCE: Research papers 2025-2026
STOLEN_FROM:
  - DeepResearcher (arXiv:2504.03160): tool call format + reasoning-before-action
  - A-RAG (arXiv:2602.03442): 3-level modes (quick/deep/read)
  - SAGE (arXiv:2602.05975): keyword extraction before query (BM25 insight)
  - Rulers (arXiv:2601.08654): EvidenceLog — claim→source anchoring
WHAT_WAS_STOLEN:
  - SearchResult dataclass (title, url, snippet, date, mode, credibility_hint)
  - EvidenceClaim: (claim, source_url, confidence, quote)
  - EvidenceLog: saves to evidence_log.json, computes hallucination_rate
  - web_search(query, mode) → list[SearchResult]
  - extract_keywords(query) → list[str] (SAGE: BM25 precision)
  - multi_query_search(queries) → list[SearchResult] (DeepResearcher)
WHAT_WAS_MISSED:
  - Sandbox lifecycle tools (create_sandbox, sandbox_run, etc.)
  - Short-term memory compression
  - Cross-session persistence
GENESIS_ADAPTATION:
  - Uses Serper API + Jina Reader (not Docker containers)
  - EvidenceLog writes to gen_dir/evidence_log.json (not agent-internal)
  - hallucination_rate feeds Regime Detector (original MUSE doesn't have this)
CALLED_BY: target_agent.py (when --use_web_search flag)
CALLS: Serper API, Jina r.jina.ai
ARTIFACT_IN: SERPER_API_KEY (env var)
ARTIFACT_OUT: evidence_log.json (per gen)
INVOCATION: |
  from genesis.tools.web_search import web_search, EvidenceLog
  results = web_search("query", mode="quick")
  log = EvidenceLog()
  log.add_claim("claim", source_url="...", confidence="HIGH")
  log.save("evidence_log.json")
TESTS: tests/test_web_search.py (39 tests)
```

---

**COMPONENT_ID: INTENT_ENGINE**
```yaml
LOCATION: genesis/goal_specification.py
STATUS: BUILT ✅
SOURCE: Research papers 2025
STOLEN_FROM:
  - MA-RAG (arXiv:2505.20096): Planner/Step Definer architecture
  - Enterprise Deep Research (arXiv:2510.17797): task annotation with priority+domain
  - HTN Planning: hierarchical goal decomposition
  - SAGE (arXiv:2602.05975): keyword extraction per sub-goal
WHAT_WAS_STOLEN:
  - SubGoal dataclass: id, description, priority, success_criterion, search_queries, keywords, domain, scope, local_filter
  - GoalSpec: primary_goal, success_criteria, priority_principle, sub_goals ordered by priority
  - decompose_task_with_llm(): LLM decomposes task.md → GoalSpec
  - _heuristic_decompose(): fallback without LLM
  - GoalSpec.to_prompt_section(): formats for META_AGENT_PROMPT injection
WHAT_WAS_MISSED:
  - Integration with Skill Library (sub-goals could recommend skills)
  - Replanning after each gen based on results
GENESIS_ADAPTATION:
  - "global_then_local" scope: searches globally FIRST, then Egypt filter
  - This fixes the geographic bias problem identified in micro_task run
  - goal_spec.json saved per run (not per gen — runs once)
CALLED_BY: genesis/orchestrator.py Section 0 (once per run)
CALLS: LLM via make_openai_client()
ARTIFACT_IN: task.md, --local_filter arg
ARTIFACT_OUT: goal_spec.json (runs/run_N/goal_spec.json)
INVOCATION: |
  from genesis.goal_specification import run_goal_specification
  spec = run_goal_specification(
      task_md=TASK_MD, task_name="micro_task",
      run_dir=RUN_DIRECTORY, llm_client=client,
      local_filter="Egypt"
  )
  goal_spec_section = spec.to_prompt_section()
TESTS: tests/test_goal_specification.py (31 tests)
```

---

**COMPONENT_ID: CRITIC_ENGINE_OPEN**
```yaml
LOCATION: genesis/open_task_evaluator.py
STATUS: BUILT ✅
SOURCE: Research papers 2026
STOLEN_FROM:
  - Rulers (arXiv:2601.08654): schema-constrained judge, evidence_quote per verdict
  - InfoDeepSeek (arXiv:2505.15872): IA@5 — evidence_score independent of output_score
  - G-Eval (confident-ai): step-by-step criteria evaluation
WHAT_WAS_STOLEN:
  - CriterionVerdict: criterion, met, score, evidence_quote (must quote from output)
  - OpenTaskResult: output_score, evidence_score, hallucination_rate, overall_score
  - extract_rubric_from_task(): extracts criteria from task.md
  - find_output_file(): searches gen_dir for report.md, submission.json, etc.
  - run_open_task_evaluation(): full pipeline
  - Weighted formula: overall = output*0.5 + evidence*0.3 - hallucination*0.2
WHAT_WAS_MISSED:
  - Skill extraction on success (when score > threshold, create skill)
GENESIS_ADAPTATION:
  - overall_score feeds Regime Detector (new signal — original papers don't do this)
  - evidence_log.json from WEB_SEARCH_TOOL feeds hallucination_rate
  - Caches results (force=False) to avoid re-running judge
CALLED_BY: genesis/orchestrator.py Section 5a.1 (when no evaluate.py)
CALLS: LLM (same model as meta_model)
ARTIFACT_IN: gen_dir/, task.md, evidence_log.json
ARTIFACT_OUT: open_task_eval.json (runs/run_N/gen_M/open_task_eval.json)
INVOCATION: |
  from genesis.open_task_evaluator import run_open_task_evaluation
  result = run_open_task_evaluation(
      gen_dir=current_gen_directory,
      task_dir=task_dir,
      judge_model=meta_model
  )
  open_task_score = result.overall_score
TESTS: tests/test_open_task_evaluator.py (36 tests)
```

---

**COMPONENT_ID: CRITIC_ENGINE_RULES**
```yaml
LOCATION: genesis/constitutional_evaluator.py
STATUS: BUILT ✅
STOLEN_FROM: Constitutional AI (Meta, 2022)
WHAT_WAS_STOLEN:
  - 5 constitutional rules: regression_free, verifiability, simplicity, learning, traceability
  - evaluate_constitutional(): checks all 5 on agent code
  - ConstitutionalReport: violations list + passed/failed + scores
GENESIS_ADAPTATION:
  - Applied to generated target_agent.py code (not LLM outputs)
  - Violations logged to constitutional_report.json
  - Injected into FEEDBACK_AGENT_PROMPT as constitutional_section
CALLED_BY: orchestrator Section 5a.2
ARTIFACT_OUT: constitutional_report.json
TESTS: (inline tests in test_full_integration.py)
```

---

**COMPONENT_ID: COGNITIVE_BRIDGE_SIGNALS**
```yaml
LOCATION: genesis/enhanced_pipeline_bridge.py
STATUS: BUILT ✅ (but agents rarely write enhanced_signals.json)
STOLEN_FROM: Virtual GENESIS Pipeline (LadderAscent + SemanticVerifier + Value)
WHAT_WAS_STOLEN:
  - LadderStateSummary: current_level, entropy, transition_possible, semantic_verdict
  - extract_enhanced_signals_from_gen(): reads agent artifacts
  - LadderStateSummary.to_feedback_section(): formats for Feedback Agent
WHAT_WAS_MISSED:
  - Target agents don't reliably write enhanced_signals.json yet
GENESIS_ADAPTATION:
  - Bridge pattern: doesn't re-run pipeline, extracts from artifacts
CALLED_BY: orchestrator Section 5a.2.5
ARTIFACT_IN: enhanced_signals.json (if exists) or agent_execution.json
ARTIFACT_OUT: ladder_state.json, enhanced_feedback_section (string)
TESTS: tests/test_enhanced_pipeline_bridge.py (31 tests)
```

---

**COMPONENT_ID: EVOLUTION_ENGINE**
```yaml
LOCATION:
  - genesis/orchestrator.py (evolutionary_discovery_engine inline)
  - virtual_genesis/eval/runners/regime_transition_detector.py
  - virtual_genesis/eval/runners/regime_orchestrator_bridge.py
  - virtual_genesis/eval/runners/conditions_runner.py
  - virtual_genesis/eval/runners/failure_extractor.py
STATUS: BUILT ✅ (AlphaEvolve skeleton only)
STOLEN_FROM:
  - Wang & Buehler arXiv:2606.01444: 3-signal regime detection
  - AlphaEvolve (DeepMind): population-based evolution
WHAT_WAS_STOLEN:
  - Saturation + Degradation + Blind Spot signals
  - 2-of-3 trigger for regime change
  - Regime verdict feeds FEEDBACK_AGENT_PROMPT
WHAT_WAS_MISSED: GRASP gating, real LLM mutation/crossover
CALLED_BY: orchestrator Section 5a.3 (evo) + 5a.4 (regime)
ARTIFACT_OUT: regime_transition_report.json, evolutionary_discovery.json
TESTS: tests/test_regime_transition.py (55 tests) + test_conditions_runner.py (48)
```

---

**COMPONENT_ID: FEEDBACK_ENGINE**
```yaml
LOCATION: genesis/spin_feedback.py + genesis/context_manager.py
STATUS: BUILT ✅
STOLEN_FROM:
  - SPIN (DeepSeek): semantic gap analysis between generations
CALLED_BY: orchestrator Section 5b
ARTIFACT_OUT: spin_section (string) + context.md update
TESTS: (via integration tests)
```

---

**COMPONENT_ID: MEMORY_ENGINE_CROSS_RUN**
```yaml
LOCATION: genesis/research_memory.py
STATUS: BUILT ✅
STOLEN_FROM: AutoResearch-2 (ByteDance): research memory across runs
WHAT_WAS_STOLEN:
  - ResearchMemoryStore (SQLite): add_entry, get_insights_for_task, search
  - Insights text → META_AGENT_PROMPT (Section 2.5)
WHAT_WAS_MISSED: Skill Library (procedural memory) — this is text insights only
CALLED_BY: orchestrator Section 2.5 + Section 7
ARTIFACT_OUT: research_memory.db (persistent, gitignored)
TESTS: (inline)
```

---

### 4.2 PLANNED COMPONENTS (مطلوب بناؤها ❌)

---

**COMPONENT_ID: TOOL_HUB**
```yaml
LOCATION: genesis/tool_hub/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 1, Week 1
SOURCE: MCP (Model Context Protocol, Anthropic/Linux Foundation 2026)
STOLEN_FROM:
  - MCP Specification: dynamic tool discovery, ToolSpec schema, catalog pattern
  - MUSE-Autoskill (arXiv:2605.27366): sandbox lifecycle tools
WHAT_TO_STEAL:
  - ToolSpec: name, description, input_schema, output_schema, preconditions,
               failure_modes, cost_per_call_usd, requires_sandbox, executor
  - ToolRegistry: register(), discover(), catalog(), invoke()
  - Progressive disclosure: catalog = name+description only in system prompt
  - SandboxExecutor: create(), run(code,args), upload(), download(), close()
    → Implementation: subprocess in tmpdir (NOT Docker — free tier)
GENESIS_ADAPTATION:
  - Tools are Python callables (not JSON-RPC like MCP)
  - SandboxExecutor = tmpdir subprocess (simpler than Docker)
  - catalog() → YAML injected in META_AGENT_PROMPT
  - Wraps existing genesis/tools/web_search.py (backward compatible)
FILES_TO_CREATE:
  genesis/tool_hub/__init__.py       ← clean API: get_tool, invoke, catalog
  genesis/tool_hub/registry.py       ← ToolSpec, ToolRegistry
  genesis/tool_hub/executor.py       ← SandboxExecutor
  genesis/tool_hub/tools/
    web_search.py                    ← wraps genesis/tools/web_search.py
    code_exec.py                     ← sandbox Python execution
    file_ops.py                      ← read/write files safely
    llm_call.py                      ← wraps api_key_pool + util.py
    skill_use.py                     ← calls skill_engine.execute() [Phase 2]
CALLED_BY:
  - orchestrator Section 3: catalog() → META_AGENT_PROMPT injection
  - target_agent.py: from genesis.tool_hub import invoke
CALLS: genesis/tools/web_search.py, api_key_pool.py, subprocess
ARTIFACT_OUT: tool_catalog.yaml (auto-generated, in META_AGENT_PROMPT)
TESTS: tests/test_tool_hub.py (35+ tests)
INTEGRATION_POINT: |
  # orchestrator.py Section 3:
  from genesis.tool_hub import catalog as tool_catalog
  TOOL_CATALOG_SECTION = f"AVAILABLE TOOLS:\n{tool_catalog()}"
  META_AGENT_PROMPT = TOOL_CATALOG_SECTION + "\n\n" + META_AGENT_PROMPT
NAMING_RATIONALE: >
  "tool_hub" لأنه مركز الأدوات — كل tool تُسجَّل هنا
  وأي agent يستدعي من هنا بدل ما يعرف من وين الـ tool جاية
```

---

**COMPONENT_ID: SKILL_ENGINE**
```yaml
LOCATION: genesis/skill_engine/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 2, Weeks 2-4
SOURCE: Multiple papers 2026
STOLEN_FROM:
  PRIMARY — MUSE-Autoskill (arXiv:2605.27366, ByteDance+Rochester, May 2026):
    - SKILL.md format (Anthropic Agent Skills standard)
    - 5-stage lifecycle: creation → memory → management → evaluation → refinement
    - .memory.md per skill: accumulates experience across tasks
    - create→evaluate→register loop (only register if tests pass)
    - Skill Bank with catalog (progressive disclosure)
    - Adaptive context compression (Level 1: node | Level 2: chain)
    - Performance: +15.21pp on SkillsBench, 87.94% on successful tasks

  SECONDARY — EvoSkill (arXiv:2603.02766, Sentient+VT, March 2026):
    - 3-agent architecture: Executor + Proposer + Skill-Builder
    - Proposer: analyzes failures, maintains feedback_history H
    - Skill-Builder: materializes proposal → skill folder
    - Frontier management: top-K programs, evict weakest
    - Git-backed lineage per program
    - Performance: +7.3% OfficeQA, +12.1% SealQA, cross-task transfer

  TERTIARY — SkillOps (arXiv:2605.13716, Emory+UIUC, May 2026):
    - Skill Contract (P, O, A, V, F): Precondition, Operation, Artifact, Validator, Failure
    - HSEG: dep/comp/red/alt edges between skills
    - Hybrid retrieval: r(s,τ) = λ·BM25 + (1-λ)·semantic
    - Library-Time maintenance: merge, repair, retire, add_validator (O(N), ~0 LLM)
    - Performance: 79.5% ALFWorld standalone (+8.8pp)

  QUATERNARY — SoK: Agentic Skills (arXiv:2602.20867, Feb 2026):
    - 7 design patterns taxonomy
    - Formal definition: S = (C, π, T, R)
    - Quality control: self-generated skills avg -1.3pp without sandbox testing

WHAT_WAS_MISSED_FROM_ORIGINALS:
  - MUSE: DAG context management (plan/action/observation per node)
  - MUSE: Cross-session state persistence
  - EvoSkill: git branch per program (use SQLite lineage instead)
  - SkillOps: full CGPD risk propagation

GENESIS_ADAPTATION:
  - Skills = agent code patterns (not Minecraft functions or office workflows)
  - Skill extraction from target_agent.py (not from runtime interaction traces)
  - SandboxExecutor = tmpdir subprocess (not Docker)
  - EvidenceLog from web_search feeds skill quality metric
  - Skills integrate with Regime Detector (skill quality = signal)

FILES_TO_CREATE:
  genesis/skill_engine/
    __init__.py          ← API: register, retrieve, execute, evolve, get_catalog
    skill.py             ← Skill, SkillContract(P,O,A,V,F), SkillFolder
    library.py           ← SkillLibrary: CRUD + frontier + maintenance
    evaluator.py         ← SkillEvaluator: sandbox pytest execution
    extractor.py         ← SkillExtractor + FailureCollector
    graph.py             ← SkillGraph HSEG: dep/comp/red/alt
    retriever.py         ← SkillRetriever: BM25+semantic hybrid
    evolver.py           ← EvoSkillLoop + ProposerAgent + SkillBuilderAgent
    skills/              ← skill packages (filesystem)
      catalog.yaml       ← auto-generated, injected in system prompt
      web_search_arabic/ ← first real skill
        SKILL.md
        scripts/search.py
        tests/test_search.py
        .memory.md
      evidence_tracking/ ← second skill
        SKILL.md
        ...

CALLED_BY:
  - orchestrator Section 3: get_catalog() → SKILL_SECTION in META_AGENT_PROMPT
  - orchestrator Section 5a.1: SkillExtractor.extract_from_agent() on success
  - orchestrator Section 5a.3: EvoSkillLoop.run() (replaces AlphaEvolve skeleton)
  - orchestrator Section 5b: retrieve() best skills → FEEDBACK_AGENT_PROMPT
  - genesis/tool_hub/tools/skill_use.py: execute() at runtime

CALLS:
  - genesis/tool_hub (SandboxExecutor for testing)
  - LLM client (Proposer + SkillBuilder agents)
  - genesis/tools/web_search.py (skill content)

ARTIFACT_IN:
  - target_agent.py (successful gen)
  - open_task_eval.json (success score)
  - gen results (failures for EvoSkill)

ARTIFACT_OUT:
  - genesis/skill_engine/skills/catalog.yaml
  - genesis/skill_engine/skills/{name}/ (per skill)
  - skill_registry.db (gitignored)
  - skill_extraction.json (per gen)

TESTS: tests/test_skill_engine.py (60+ tests)

INTEGRATION_POINTS: |
  # Section 3 (Prompts):
  from genesis.skill_engine import get_catalog as skill_catalog
  SKILL_SECTION = f"AVAILABLE SKILLS:\n{skill_catalog()}"

  # Section 5a.1 (after evaluation):
  if overall_score > 70:
      from genesis.skill_engine import SkillExtractor
      extractor = SkillExtractor(llm_client)
      new_skills = extractor.extract_from_agent(target_agent_path, overall_score)
      for s in new_skills: register(s)

  # Section 5b (Feedback):
  from genesis.skill_engine import retrieve
  best_skills = retrieve(query=TASK_MD, top_k=2)
  SKILL_FEEDBACK = "\n".join(s.get_full_body() for s in best_skills)

NAMING_RATIONALE: >
  "skill_engine" لأنه المحرك الكامل لدورة حياة الـ skills
  مش "skill_library" لأنها مجرد storage
  المحرك يشمل: creation + evaluation + evolution + retrieval + maintenance
```

---

**COMPONENT_ID: META_ENGINE**
```yaml
LOCATION: genesis/meta_engine/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 3, Week 5
SOURCE: Research papers 2024-2025
STOLEN_FROM:
  PRIMARY — TextGrad (Stanford, 2024, github.com/zou-group/textgrad):
    - TextVariable: value + requires_grad + gradient (textual gradient)
    - TextLoss: LLM evaluates quality → loss description
    - TGD (Textual Gradient Descent): applies gradient to update variable
    - backward(): LLM generates "what should change to reduce loss"
    - PyTorch-style API: variable, loss_fn, optimizer
    - KEY INSIGHT: target_agent.py = Variable, score = Loss, gradient = "what to fix"

  SECONDARY — metaTextGrad (arXiv:2505.18524, May 2025):
    - Meta-level: optimizes the optimizer itself
    - Initialize-Propose-Update-Extract cycle
    - Validation set separation

  TERTIARY — ExpeL (cross-episode insights):
    - GenerationTrajectory: maps full run history
    - extract_winning_pattern(): what worked → reusable insight
    - cross-generation knowledge transfer

  QUATERNARY — OPTO (execution trace analysis):
    - Receives: trace + output + feedback together
    - Stronger than TextGrad (sees the process, not just result)

GENESIS_ADAPTATION:
  - Variable = target_agent.py code (not a prompt or molecule)
  - Loss = overall_score from CRITIC_ENGINE (not human feedback)
  - Gradient = "what patterns in agent code led to improvement"
  - TGD.step() = new FEEDBACK_AGENT_PROMPT instruction (not code rewrite)
  - Trajectory = GENESIS generations (not ML training steps)

FILES_TO_CREATE:
  genesis/meta_engine/
    __init__.py          ← API: analyze, gradient, synthesize, run
    textgrad.py          ← TextVariable, TextLoss, TGD (PyTorch-style)
    trajectory.py        ← GenerationTrajectory, GenerationPoint
    proposer.py          ← ProposerAgent (EvoSkill-inspired, meta level)
    optimizer.py         ← MetaOptimizer: entry point for orchestrator

CALLED_BY: orchestrator Section 5a.5 (NEW section — after Regime, before Feedback)
CALLS: LLM, skill_engine.retrieve(), open_task_eval.json, regime_transition_report.json
ARTIFACT_IN: all gen artifacts (scores, code, signals)
ARTIFACT_OUT: meta_optimization.json (per gen), meta_section (string for feedback)
TESTS: tests/test_meta_engine.py (40+ tests)

INTEGRATION_POINT: |
  # NEW Section 5a.5 in orchestrator.py:
  from genesis.meta_engine import MetaOptimizer
  meta_opt = MetaOptimizer(llm_client=meta_llm)
  meta_result = meta_opt.run(RUN_DIRECTORY, current_gen)
  META_SECTION = meta_result.meta_instruction
  # META_SECTION goes into SPIN_SECTION (fed to Feedback Agent)

NAMING_RATIONALE: >
  "meta_engine" لأنه يُحسّن عملية التحسين نفسها
  مش "feedback_optimizer" لأنه أكبر — يشمل trajectory analysis + TextGrad
```

---

**COMPONENT_ID: AGENT_HUB**
```yaml
LOCATION: genesis/agent_hub/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 4, Weeks 6-7
SOURCE: Multiple projects 2026
STOLEN_FROM:
  PRIMARY — OpenClaw SOUL.md (2026 industry standard):
    - SOUL.md = Constitution (non-negotiable) — personality, values, boundaries
    - AGENTS.md = Behavior guidelines + safety rules (SEPARATE from soul!)
    - USER.md = User profile + working contract
    - TOOLS.md = Tool usage guidance
    - MEMORY.md = Curated facts (small + structured + expiry dates)
    - Loading order: AGENTS.md → SOUL.md → USER.md → TOOLS.md → Skills
    - CRITICAL RULE: never_auto_write_soul (security invariant)
    - Multi-agent: shared AGENTS.md + individual SOUL.md per agent

  SECONDARY — BDI Architecture (arXiv:2512.09458):
    - Beliefs = Memory (what agent knows)
    - Desires = Goal Contract (what agent wants)
    - Intentions = target_agent.py (what agent committed to do)
    - Commitment strategy: stable (don't replan every step)
    - Intention revision trigger: only on regime_change

  TERTIARY — MAGMA (arXiv:2601.03236, best memory 2026):
    - 4 subgraphs: semantic + temporal + causal + entity
    - Intent-guided retrieval (not just similarity)
    - Dual-stream consolidation: episodic → semantic
    - Performance: 0.70 on LoCoMo (best 2026)
    - Use SQLite now, graph later (pragmatic)

  QUATERNARY — MemGPT/Letta (arXiv:2310.08560):
    - LLM = OS: working_memory = RAM, external = Disk
    - Function calls: memory_read(), memory_write()
    - Paging: working → episodic when overflow

GENESIS_ADAPTATION:
  - SOUL.md content includes "global_before_local" value (fixes geographic bias)
  - BDI Intentions = target_agent.py code (not classical plan steps)
  - BDI Beliefs update after each gen (score, hallucination_rate)
  - Memory Procedural = SkillLibrary (direct bridge)
  - Memory Episodic = generation history (not conversation turns)
  - AgentSpec is JSON-serializable from Day 1 (future vibe-web foundation)

FILES_TO_CREATE:
  genesis/agent_hub/
    __init__.py          ← API: create_agent, load_agent, AgentSpec
    agent.py             ← AgentSpec (Soul+Memory+Tools+Skills+BDI)
    registry.py          ← AgentRegistry (CRUD + REST foundation)
    soul/
      soul.py            ← AgentSoul dataclass
      souls/             ← soul.md files per agent type
        research_agent.soul.md   ← for micro_task and research tasks
        coding_agent.soul.md     ← for GPQA and coding tasks
        default.soul.md          ← fallback
        shared_agents.md         ← shared rules (AGENTS.md equivalent)
    memory/
      manager.py         ← AgentMemoryManager (4-tier orchestrator)
      working.py         ← WorkingMemory (context window, MemGPT paging)
      episodic.py        ← EpisodicMemory (timestamped, expires)
      semantic.py        ← SemanticMemory (facts, atemporal)
      procedural.py      ← ProceduralMemory → bridge to SkillEngine

CALLED_BY:
  - orchestrator Section 0 (before everything): create_agent() + soul_section
  - orchestrator Section 5b: update BDI beliefs after gen
CALLS: skill_engine (procedural bridge), research_memory (extends it)
ARTIFACT_IN: task.md, task_name, run_history
ARTIFACT_OUT:
  - agent_registry.db (gitignored)
  - soul section (string for META_AGENT_PROMPT)
  - BDI state (in-memory, updated each gen)
TESTS: tests/test_agent_hub.py (50+ tests)

INTEGRATION_POINT: |
  # NEW — orchestrator Section 0 (first thing before goal_spec):
  from genesis.agent_hub import AgentRegistry, AgentSpec
  registry = AgentRegistry()
  spec = AgentSpec.for_task(task_name, soul_type="research")
  SOUL_SECTION = spec.soul.to_soul_md()
  META_AGENT_PROMPT = SOUL_SECTION + "\n\n" + META_AGENT_PROMPT

  # After each gen (Section 5b):
  spec.update_beliefs({"last_score": score, "hallucination_rate": h})
  registry.update(spec.id, spec)

VIBE_WEB_FOUNDATION: >
  AgentSpec.to_dict() → JSON → REST API → drag-and-drop UI (future)
  AgentRegistry.list() → agent cards in UI
  ToolRegistry.discover() → tool cards in UI
  SkillLibrary.get_catalog() → skill cards in UI

NAMING_RATIONALE: >
  "agent_hub" لأنه مركز تعريف الـ agents وإدارتها
  soul/ subdir لأن الـ soul files متعددة وبحاجة لـ version control
  memory/ subdir لأن الذاكرة 4 أنواع منفصلة
```

---

**COMPONENT_ID: SAFETY_ENGINE**
```yaml
LOCATION: genesis/safety_engine/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 5, Week 8
SOURCE: arXiv:2512.09458 (Architectures for Building Agentic AI)
STOLEN_FROM: Safety Supervisor + Budget Guards concept
GENESIS_ADAPTATION:
  - HallucinationGuard: hallucination_rate from CRITIC_ENGINE feeds here
  - BudgetGuard: max_cost_usd from soul.md (agent-specific)
FILES_TO_CREATE:
  genesis/safety_engine/
    __init__.py
    budget.py         ← BudgetGuard
    hallucination.py  ← HallucinationGuard
    escalation.py     ← EscalationPolicy (warn→pause→halt)
CALLED_BY: orchestrator Section 5 (start of each gen)
TESTS: tests/test_safety_engine.py (25+ tests)
```

---

**COMPONENT_ID: TELEMETRY_ENGINE**
```yaml
LOCATION: genesis/telemetry/  [CREATE NEW]
STATUS: PLANNED ❌ — Phase 5, Week 8
SOURCE: arXiv:2512.09458 (immutable audit trail)
GENESIS_ADAPTATION:
  - Events per orchestrator section (section_start/end, llm_call, signal)
  - Enables replay and debugging
FILES_TO_CREATE:
  genesis/telemetry/
    __init__.py
    telemetry.py      ← RunTelemetry, TelemetryEvent
    reporter.py       ← run_summary.json
CALLED_BY: orchestrator (every section)
ARTIFACT_OUT: run_telemetry.json, run_summary.json
TESTS: tests/test_telemetry.py (20+ tests)
```

---

## 5. ORCHESTRATOR INJECTION MAP

الـ orchestrator.py عنده sections محددة — هنا بالظبط أين تدخل كل component جديدة:

```python
# genesis/orchestrator.py — INJECTION POINTS

def main():
    # ────────────────────────────────────────
    # PRE-SECTION 0: Safety + Telemetry init
    # ────────────────────────────────────────
    # [NEW Phase 5] TELEMETRY_ENGINE: start run telemetry
    telemetry = RunTelemetry(run_id)
    
    # [NEW Phase 5] SAFETY_ENGINE: load budget from soul
    safety = SafetyEngine(max_cost=spec.soul.max_cost_usd)

    # ────────────────────────────────────────
    # SECTION 0: [NEW Phase 4] AGENT_HUB — load soul
    # ────────────────────────────────────────
    spec = AgentSpec.for_task(task_name)
    SOUL_SECTION = spec.soul.to_soul_md()

    # ────────────────────────────────────────
    # SECTION 0 (cont): [EXISTING] INTENT_ENGINE
    # ────────────────────────────────────────
    goal_spec = run_goal_specification(...)

    # ────────────────────────────────────────
    # SECTION 3: Define Prompts
    # ────────────────────────────────────────
    # [NEW Phase 1] TOOL_HUB: catalog
    TOOL_CATALOG = tool_catalog()
    
    # [NEW Phase 2] SKILL_ENGINE: catalog
    SKILL_CATALOG = skill_catalog()
    
    # [EXISTING] Goal spec section
    META_AGENT_PROMPT = (
        SOUL_SECTION + "\n\n"        # [NEW Phase 4]
        + TOOL_CATALOG + "\n\n"      # [NEW Phase 1]
        + SKILL_CATALOG + "\n\n"     # [NEW Phase 2]
        + goal_spec_section + "\n\n" # [EXISTING]
        + META_AGENT_PROMPT_BASE     # [EXISTING]
    )

    # ════ GENERATION LOOP ════════════════════
    for current_gen in range(1, max_gen + 1):

        # ────────────────────────────────────
        # SECTION 5a: Run Target Agent
        # ────────────────────────────────────
        # [NEW Phase 5] SAFETY: check budget before each gen
        safety.check_or_halt(current_budget)
        
        # [EXISTING] run target agent subprocess
        run_target_agent(...)

        # ────────────────────────────────────
        # SECTION 5a.1: Evaluation
        # ────────────────────────────────────
        # [EXISTING] evaluate.py (closed tasks)
        run_evaluation(...)
        
        # [EXISTING] open_task_evaluator (open tasks)
        open_task_score = run_open_task_evaluation(...)
        
        # [NEW Phase 2] SKILL_ENGINE: extract on success
        if open_task_score > 70:
            new_skills = SkillExtractor().extract_from_agent(...)

        # ────────────────────────────────────
        # SECTION 5a.2: Constitutional Check [EXISTING]
        # ────────────────────────────────────

        # ────────────────────────────────────
        # SECTION 5a.2.5: Cognitive Signals [EXISTING]
        # ────────────────────────────────────

        # ────────────────────────────────────
        # SECTION 5a.3: Evolution [EXISTING → Phase 2 upgrade]
        # ────────────────────────────────────
        # [NEW Phase 2] Replace AlphaEvolve skeleton with EvoSkillLoop
        evo_skills = EvoSkillLoop().run(failures, library, ...)

        # ────────────────────────────────────
        # SECTION 5a.4: Regime Detection [EXISTING]
        # ────────────────────────────────────

        # ────────────────────────────────────
        # SECTION 5a.5: [NEW Phase 3] META_ENGINE
        # ────────────────────────────────────
        meta_result = MetaOptimizer().run(RUN_DIRECTORY, current_gen)
        META_SECTION = meta_result.meta_instruction

        # ────────────────────────────────────
        # SECTION 5b: Feedback Agent
        # ────────────────────────────────────
        # [NEW Phase 2] Add best skills to feedback
        best_skills = retrieve(TASK_MD, top_k=2)
        SKILL_FEEDBACK = build_skill_feedback(best_skills)
        
        SPIN_SECTION = (
            spin_section
            + regime_section    # [EXISTING]
            + enhanced_section  # [EXISTING]
            + META_SECTION      # [NEW Phase 3]
            + SKILL_FEEDBACK    # [NEW Phase 2]
        )
        
        # [NEW Phase 4] Update BDI beliefs
        spec.update_beliefs({"last_score": open_task_score})
```

---

## 6. ARTIFACT SCHEMA REGISTRY

كل artifact له schema ثابت — أي AI agent يعرف بالظبط ما يجده:

```python
# genesis/schemas/ [CREATE Phase 1]

# tool_spec.v1.json:
{
    "schema_version": "1.0",
    "component": "TOOL_HUB",
    "fields": ["name", "description", "version", "input_schema",
               "output_schema", "preconditions", "failure_modes",
               "cost_per_call_usd", "requires_sandbox"]
}

# skill.v1.json:
{
    "schema_version": "1.0",
    "component": "SKILL_ENGINE",
    "fields": ["name", "version", "domain", "description", "instructions",
               "contract": {"P", "O", "A", "V", "F"},
               "performance_score", "usage_count", "source_run",
               "generation", "parent_skill"]
}

# agent_spec.v1.json:
{
    "schema_version": "1.0",
    "component": "AGENT_HUB",
    "fields": ["id", "name", "soul", "memory_config", "tool_names",
               "skill_names", "beliefs", "desires", "intentions",
               "pipeline_config", "run_history"]
}

# meta_result.v1.json:
{
    "schema_version": "1.0",
    "component": "META_ENGINE",
    "fields": ["trajectory_summary", "textual_gradient", "winning_pattern",
               "losing_pattern", "meta_instruction", "confidence"]
}
```

---

## 7. TESTING PROTOCOL

قبل كل commit:
```bash
# 1. Run all existing tests (must stay 937+)
python3 -m pytest tests/ -q

# 2. Run specific new section tests
python3 -m pytest tests/test_tool_hub.py -v
python3 -m pytest tests/test_skill_engine.py -v

# 3. Verify backward compat
python3 -c "from genesis.tools.web_search import web_search; print('OK')"
python3 -c "from genesis.goal_specification import run_goal_specification; print('OK')"

# 4. Commit
git add .
git commit -m "feat: {SectionName} — {description}, {N} new tests, {M} total"
git push https://{GITHUB_TOKEN}@github.com/faresrafat3/GENESIS.git HEAD:main
```

---

## 8. CURRENT STATE SNAPSHOT

```
Date: 2026-06-08
Tests: 937 passing
Phases completed: 0/5 (planning complete, implementation starting)
Next action: Phase 1 — Tool Hub

Built ✅:
  WEB_SEARCH_TOOL        (39 tests)
  INTENT_ENGINE          (31 tests)
  CRITIC_ENGINE_OPEN     (36 tests)
  CRITIC_ENGINE_RULES    (inline)
  COGNITIVE_BRIDGE       (31 tests)
  EVOLUTION_ENGINE       (176 tests)
  FEEDBACK_ENGINE        (inline)
  MEMORY_ENGINE          (inline)

Planned ❌:
  TOOL_HUB              (Phase 1, Week 1)
  SKILL_ENGINE          (Phase 2, Weeks 2-4)
  META_ENGINE           (Phase 3, Week 5)
  AGENT_HUB             (Phase 4, Weeks 6-7)
  SAFETY_ENGINE         (Phase 5, Week 8)
  TELEMETRY_ENGINE      (Phase 5, Week 8)
```

---

## 9. KEY DECISIONS LOG

```
DECISION-001: global_before_local scope in INTENT_ENGINE
  Date: 2026-06-08
  Reason: micro_task run showed geographic bias (Egypt filter too early)
  Impact: sub-goals search globally first, Egypt filter in last sub-goal only

DECISION-002: Sandbox = tmpdir subprocess (not Docker)
  Date: 2026-06-08
  Reason: free tier infrastructure, Docker adds complexity
  Impact: SKILL_ENGINE tests run in tmpdir, not isolated containers

DECISION-003: backward_compat — old imports stay working
  Date: 2026-06-08
  Reason: orchestrator has many import points, changing all = risk
  Impact: genesis/tools/web_search.py never deleted, only wrapped

DECISION-004: AgentSpec JSON-serializable from day 1
  Date: 2026-06-08
  Reason: future vibe-web interface requires REST API
  Impact: all AgentHub dataclasses must have to_dict() + from_dict()

DECISION-005: TextVariable = target_agent.py (not a prompt)
  Date: 2026-06-08
  Reason: GENESIS optimizes agents not prompts
  Impact: TextGrad gradient = "what patterns in agent code led to improvement"

DECISION-006: Skill extraction offline (after gen) not online (during gen)
  Date: 2026-06-08
  Reason: runtime skill_create requires Docker-grade sandbox
  Impact: SKILL_ENGINE extracts from successful target_agent.py after evaluation
```
