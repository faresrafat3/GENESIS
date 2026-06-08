# GENESIS — خطة الثلاثة ركائز الكبيرة
# تاريخ: 2026-06-08
# بحث عميق في 25+ ورقة · خطة تفصيلية لكل ركيزة

---

## نظرة عامة — ما نبنيه وليه

الـ system حالياً عنده مشكلتان جوهريتان:
1. **كل generation يبدأ من صفر** — لا يتذكر "كيف نجحت"
2. **الـ feedback agent ناقد — ليس محسّناً** — يقول "غلط" لكن لا يقول "ابنِ على الناجح"

الحل = 3 ركائز:
```
PILLAR 1: SKILL ENGINE     — الذاكرة القابلة للتنفيذ
PILLAR 2: META ENGINE      — المحسّن الاستراتيجي
PILLAR 3: AGENT FRAMEWORK  — العقل الكامل (للمستقبل)
```

الرابع (Architecture Evolution) = تأجيل حتى تكتمل البنية الأساسية.

---

## ═══════════════════════════════════════
## PILLAR 1: SKILL ENGINE — الذاكرة القابلة للتنفيذ
## ═══════════════════════════════════════

### ما وصله المجال — أعمق بحث

#### الخط التطوري:
```
2023: Voyager (NVIDIA+Stanford) — أول skill library حقيقية
      ← skills = JavaScript functions في Minecraft
      ← vector DB + natural language retrieval
      ← حفظت skills ناجحة، استرجعتها لمهام جديدة

2025: Agent Skills (Anthropic) — المعيار الصناعي
      ← SKILL.md format (Markdown + YAML)
      ← Progressive Disclosure: metadata أولاً، instructions عند الطلب
      ← Claude Code, Cursor, OpenAI Codex CLI كلهم بيستخدموه

2026: الموجة الجديدة — skills تتطور وتُدار بذكاء
      ← EvoSkill (arXiv:2603.02766) — git-backed skill evolution
      ← MUSE-Autoskill (arXiv:2605.27366) — sandbox testing + .memory.md
      ← SkillOS (arXiv:2605.06614) — RL-trained skill curator
      ← SkillOps (arXiv:2605.13716) — HSEG graph + maintenance loop
      ← SkillRT (arXiv:2604.03088) — JIT compilation → 50x speedup
      ← SkillFoundry (arXiv:2604.03964) — mining from heterogeneous sources
```

#### أقوى 4 أوراق نسرقها:

**① MUSE-Autoskill (arXiv:2605.27366 — May 2026)** — الأكمل والأقوى
```
البنية:
  skill_name/
    SKILL.md         ← instructions + YAML frontmatter
    scripts/         ← executable Python/Bash/JS
    tests/           ← pytest-compatible validation
    resources/       ← data files, prompt fragments
    .memory.md       ← ذاكرة خاصة بالـ skill (خارج الـ publish)

الإجراء:
  1. create: LLM يبني SKILL.md + scripts
  2. evaluate: pytest يشغّل tests/ → pass/fail
  3. register: لو pass → يدخل الـ skill bank
  4. retrieve: YAML catalog (name + description فقط) في system prompt
  5. load: agent يقرأ body عند الحاجة (progressive disclosure)
  6. .memory.md: agent يُضيف notes بعد كل استخدام

الإنجاز: +7.3% exact match على SWE-bench عند دمج skills
```

**② SkillOps (arXiv:2605.13716 — May 2026)** — أقوى Lifecycle Management
```
كل skill = contract: (P, O, A, V, F)
  P = precondition (متى تُستخدَم)
  O = operation (ماذا تفعل)
  A = artifact (ما تُنتج)
  V = validator (كيف تتحقق)
  F = failure modes (كيف تفشل)

HSEG (Hierarchical Skill Execution Graph):
  - nodes = skills
  - edges = dependencies + compatibility
  - يُخطط: candidate skills → filter by P → stitch → execute

Maintenance Loop (O(N) — nearly zero LLM calls):
  - merge: يُدمج skills متشابهة
  - repair: يُصلح scripts مكسورة
  - retire: يُزيل skills ضعيفة
  - add_validator: يُضيف V لـ skills بدون validation
```

**③ EvoSkill (arXiv:2603.02766 — March 2026)** — أفضل Evolution Strategy
```
git-backed skill versioning:
  - كل skill = git branch (program/skill-name)
  - كل iteration = child branch
  - frontier = bounded set (K=3) أفضل skills
  - eviction: الأضعف يُحذف
  - lineage: يمكن trace الأصل

Proposer Agent:
  - يُحلّل failure modes
  - يقترح skill جديدة أو تعديل على موجودة
  - يُحدد target: skill-only OR prompt-only

النتيجة: skill-merge → +7.3% (complementary skills من runs مختلفة)
```

**④ SoK: Agentic Skills (arXiv:2602.20867 — Feb 2026)** — أشمل taxonomy
```
7 Design Patterns:
  1. Metadata-driven progressive disclosure  ← نستخدمه
  2. Code-as-skill (executable)             ← نستخدمه
  3. Workflow enforcement                   ← نستخدمه (constitutional)
  4. Self-evolving libraries                ← نبنيه (EvoSkill)
  5. Hybrid NL+code macros                 ← نستخدمه
  6. Meta-skills (skills that create skills) ← مستقبلاً
  7. Plugin/marketplace distribution        ← مستقبلاً (vibe web!)

Quality Control Challenge:
  - SkillsBench: self-generated skills = -1.3% average!
  - النجاح يعتمد على: domain specificity + automated verification
  - الحل: sandbox execution testing قبل التسجيل
```

### ما نبنيه في GENESIS — بالتفاصيل

#### بنية الـ Skill

```
genesis/skills/                    ← skill bank (filesystem)
├── skill_catalog.yaml             ← name + description فقط (للـ agent system prompt)
├── skill_registry.db              ← SQLite: metadata + stats + lineage
│
└── web_search_arabic/             ← مثال skill
    ├── SKILL.md                   ← instructions (Anthropic format)
    ├── scripts/
    │   └── search.py              ← executable Python
    ├── tests/
    │   └── test_search.py         ← pytest validation
    ├── resources/
    │   └── arabic_stopwords.txt   ← auxiliary data
    └── .memory.md                 ← usage notes (خارج catalog)
```

#### SKILL.md Format (Anthropic format مع extensions)

```yaml
---
name: web_search_arabic
description: "Search web for Arabic micro-task platforms with credibility verification"
version: 1.2.0
domain: grounding
task_types: [research, micro_task, fact_finding]
preconditions:
  - "Task requires real-world information unavailable in training data"
  - "Platform availability needs verification (Egypt, Arabic)"
artifacts:
  - type: evidence_log
    format: JSON
    path: evidence_log.json
validators:
  - "evidence_log.json exists with hallucination_rate < 0.5"
failure_modes:
  - "Serper API rate limit → fallback to DuckDuckGo"
  - "No results → broaden query"
performance_score: 0.82
usage_count: 15
source_run: run_55_gen_2
---

# Web Search Arabic

## When to use
- Task requires finding micro-task platforms, payment proofs, platform reviews
- Information needed is recent (2024+) and not in training data
- Egypt availability needs explicit verification

## Core principles
1. Search globally first — never filter by Egypt in first query
2. Extract keywords before searching (SAGE principle)
3. Track every claim in EvidenceLog
4. Mark unverified claims explicitly

## Recommended tools
- `web_search(query, mode="quick")` for broad discovery
- `web_search(url, mode="read")` for deep reading
- `extract_keywords(query, llm_client)` before searching

## Workflow
1. Decompose task into 3-5 search sub-goals
2. For each sub-goal: extract keywords → search globally → deep read top result
3. For each claim: log in EvidenceLog with source URL
4. Save evidence_log.json to WORKING_DIR
```

#### genesis/skill_library.py — الكود

```python
# المكونات:
class Skill:
    name, version, domain, task_types
    preconditions, artifacts, validators, failure_modes
    performance_score, usage_count, source_run
    skill_dir: Path           # filesystem location
    
class SkillContract:          # SkillOps: (P, O, A, V, F)
    precondition: str
    operation: str
    artifact: str
    validator: str
    failure_modes: list[str]

class SkillLibrary:
    # Storage
    registry_db: SQLite       # metadata + stats
    skills_dir: Path          # filesystem skill packages
    
    # Core ops
    register(skill_dir) → Skill   # validate → register
    retrieve(domain, task_type, top_k=3) → list[Skill]
    update(skill, feedback, score)
    retire(skill)             # SkillOps: maintenance
    
    # Catalog
    get_catalog_yaml() → str  # للـ system prompt (name + description فقط)
    get_skill_body(name) → str  # عند الطلب
    
    # Evolution (EvoSkill)
    propose_new_skill(failure_analysis, proposer_llm) → Skill
    merge_skills(skill_a, skill_b) → Skill
    frontier: list[Skill]     # top-K best skills

class SkillExtractor:
    # من target_agent.py ناجح → Skill
    extract_from_agent(agent_path, score, run_id, gen_id) → list[Skill]
    
class SkillEvaluator:
    # MUSE-Autoskill: sandbox testing
    run_tests(skill) → TestResult
    validate_artifact(skill, artifact_path) → bool
```

#### Integration في Orchestrator

```
Section 3 (Prompts):
  skills = skill_library.retrieve(domain, task_type, top_k=3)
  catalog = skill_library.get_catalog_yaml()
  META_AGENT_PROMPT += f"AVAILABLE SKILLS:\n{catalog}"

Section 5a.1 (after evaluation):
  if score > threshold:
    new_skills = extractor.extract_from_agent(target_agent_path, score)
    for skill in new_skills:
      evaluator.run_tests(skill)  # sandbox validation
      if passed: library.register(skill)

Section 5b (Feedback Agent):
  best_skills = library.retrieve(domain, top_k=2)
  FEEDBACK_AGENT_PROMPT += f"PROVEN SKILLS TO BUILD ON:\n{best_skill.body}"
```

#### الـ Artifacts

```
genesis/skills/              ← في git (skill packages)
  skill_catalog.yaml         ← auto-generated
  skill_registry.db          ← gitignored (بيانات runtime)
  web_search_arabic/
  evidence_tracking/
  micro_task_research/
  ...

runs/run_N/gen_M/
  skill_extraction.json      ← ما تم استخراجه من هذا الـ gen
  skill_performance.json     ← كيف أدّت الـ skills المستخدمة
```

---

## ═══════════════════════════════════════
## PILLAR 2: META ENGINE — المحسّن الاستراتيجي
## ═══════════════════════════════════════

### ما وصله المجال

#### الخط التطوري:
```
2024: TextGrad (Stanford) — backpropagation عبر text
      ← "textual gradient descent"
      ← LLM يُولّد feedback كـ "gradient"
      ← يُحدّث variables (prompts, code) بدل parameters

2025: metaTextGrad (arXiv:2505.18524) — optimizes the optimizer itself
      ← meta-structure optimizer
      ← يُحسّن الـ optimizer prompt بدل مجرد الـ output

2025: ScoreFlow — preference optimization للـ agent workflows
      ← generates multiple workflows → evaluates → DPO
      ← Score-DPO: يستخدم الـ scores مباشرة بدل binary preference

2025: OPTO — execution trace + feedback
      ← optimizer يرى: trace + output + feedback معاً
      ← أقوى من TextGrad لأنه يرى الـ process مش بس الـ result

2026: ExpeL (Experience Extraction) → insights عبر tasks
      ← يُحوّل episodes لـ insights قابلة للاستخدام
```

#### التشخيص الدقيق لمشكلة GENESIS:

```
المشكلة الحالية:
  Gen 1: target_agent_1 → score 60%
  Feedback Agent: "كذا كان غلط → اصلحه"
  Gen 2: target_agent_2 → score 65%
  Feedback Agent: "كذا كان غلط → اصلحه"
  Gen 3: target_agent_3 → score 63%   ← regression!
  Feedback Agent: "كذا كان غلط → اصلحه"   ← نفس النوع!

المشكلة: الـ feedback agent مش بيشوف الـ trajectory كاملة
          بيشوف gen N فقط بدون Gen 1-N history
          مش بيعرف "Gen 2 نجح لأن X" → "اعمل X+ في Gen 3"

الحل (TextGrad + OPTO):
  Gen N+1 Feedback = f(trajectory_1_to_N + winning_pattern + losing_pattern)
```

### ما نبنيه في GENESIS

#### genesis/meta_optimizer.py

```python
class GenerationPoint:
    gen: int
    score: float              # overall_score
    hallucination_rate: float
    ladder_level: int
    key_changes: list[str]    # ما غيّره عن Gen N-1
    winning_elements: list[str]  # من code analysis
    losing_elements: list[str]

class GenerationTrajectory:
    """كل تاريخ الـ run"""
    points: list[GenerationPoint]
    
    def find_peak() → GenerationPoint
    def find_regression() → tuple[GenerationPoint, GenerationPoint]
    def extract_winning_pattern() → str  # TextGrad: "textual gradient"
    def extract_delta(gen_a, gen_b) → str  # ما تغيّر بين نقطتين
    def compute_textual_gradient() → str  # OPTO style

class WinningStrategy:
    """المسروق من TextGrad + OPTO"""
    description: str          # ما أدى للنجاح
    code_patterns: list[str]  # أنماط code ناجحة
    anti_patterns: list[str]  # أنماط فاشلة
    confidence: float
    
class MetaOptimizer:
    def analyze(run_dir, current_gen) → GenerationTrajectory
    
    def compute_textual_gradient(trajectory) → str:
        """
        مسروق من TextGrad:
        بدل numeric gradient → LLM يُولّد "textual gradient"
        "الـ Gen 2 تحسّن لأن X — الـ Gen 3 تراجع لأن Y"
        → الـ gradient = "افعل X أكثر، تجنّب Y"
        """
    
    def synthesize_meta_instruction(trajectory, winning_strategy) → str:
        """
        يُدمج:
        - textual_gradient (TextGrad)
        - execution_trace analysis (OPTO)  
        - winning skills (Skill Library)
        - goal_contract compliance
        → instruction واضحة للـ feedback agent
        """
    
    def apply_to_feedback_prompt(base_prompt, meta_instruction) → str:
        """يُضيف meta_section في بداية الـ feedback prompt"""
```

#### Integration في Orchestrator

```python
# Section 5a.5 (جديد — بعد Regime, قبل Feedback):
from genesis.meta_optimizer import MetaOptimizer

optimizer = MetaOptimizer()
trajectory = optimizer.analyze(RUN_DIRECTORY, current_gen)
meta_instruction = optimizer.compute_textual_gradient(trajectory)
meta_section = optimizer.synthesize_meta_instruction(trajectory, skills)

# يدخل FEEDBACK_AGENT_PROMPT:
SPIN_SECTION += meta_section
```

#### الـ Artifacts

```
runs/run_N/gen_M/
  meta_optimization.json:
    {
      "trajectory_summary": "Gen 1→2 +5%, Gen 2→3 -2% (regression)",
      "winning_pattern": "web_search + evidence tracking + global-first",
      "losing_pattern": "Egypt filter too early + no source citation",
      "textual_gradient": "Focus more on X, avoid Y in next gen",
      "confidence": 0.78
    }
```

---

## ═══════════════════════════════════════
## PILLAR 3: AGENT FRAMEWORK — العقل الكامل
## ═══════════════════════════════════════

### ما وصله المجال (بحث عميق)

#### Memory Architectures 2026:

```
MAGMA (arXiv:2601.03236) — أفضل أداء على LoCoMo (0.70):
  - 4 graphs: semantic + temporal + causal + entity
  - intent-guided subgraph traversal
  - multi-hop temporal reasoning

Letta/MemGPT (arXiv:2310.08560):
  - LLM = OS (working memory = RAM, external = disk)
  - function calls لإدارة الذاكرة
  - tiered storage: context window → external DB

A-MEM (Zettelkasten method):
  - atomic notes + dynamic linking
  - evolving "living" graph of knowledge

MemoryOS (arXiv:2506.06326):
  - STM → MTM → LPM (hierarchical)
  - heat-based eviction
  - persona module

Zep (Graphiti arXiv:2501.13956):
  - temporal knowledge graph
  - valid_at + invalid_at per node/edge
  - best for "what did agent know at time T?"
```

#### Agent "Soul" — ما هو؟

```
من الأبحاث، الـ "soul" = identity + values + behavioral consistency:

Identity:
  - اسم + شخصية + قيم ثابتة
  - لا تتغير حتى لو تغيّر الـ task
  - GENESIS لديه: identity_runtime/ + governance.py

Values:
  - ما يُقدّر الـ agent (accuracy, honesty, efficiency)
  - يُحدّد قرارات الـ trade-off
  - GENESIS لديه: constitutional_evaluator.py (partial)

Behavioral Consistency:
  - نفس الطريقة في التفكير عبر tasks
  - GENESIS لديه: LadderAscent (partial)
```

#### ما نبنيه للـ Agent Framework

**المرحلة المباشرة: Agent Hub (بعد Skills + Meta)**

```
genesis/agent_hub/
├── agent_spec.py          ← تعريف الـ agent
├── agent_registry.py      ← سجل الـ agents
├── agent_memory.py        ← memory architecture
└── agent_soul.py          ← identity + values

AgentSpec:
  name: str
  description: str
  soul: AgentSoul          ← identity + values
  memory: AgentMemory      ← MAGMA/Letta inspired
  skills: list[str]        ← من Skill Library
  tools: list[str]         ← web_search, etc.
  constitution: list[str]  ← rules
  
AgentMemory (مسروق من MAGMA + Letta):
  working: dict            ← current context (RAM)
  episodic: EpisodicStore  ← past experiences (timestamped)
  semantic: SemanticStore  ← facts + relationships
  procedural: SkillLibrary ← how-to knowledge (= Skill Engine!)
  
AgentSoul:
  name: str
  core_values: list[str]   ← "accuracy > speed", "cite sources"
  persona: str             ← "دقيق، محايد، يعترف بالشك"
  identity_hash: str       ← fingerprint للتحقق من الثبات
```

**المرحلة البعيدة: Vibe Web Interface**

```
هذا للمستقبل — نبني الـ foundation الآن:
  - كل Agent = node في graph
  - كل Skill = tool attached to agent
  - كل Memory = state of agent
  - الـ interface = drag-and-drop composition

Foundation الآن:
  - AgentSpec must be JSON-serializable
  - AgentRegistry must support REST queries
  - SkillLibrary must be importable by any agent
  - All artifacts must have stable schemas
```

---

## ═══════════════════════════════════════
## PILLAR 4 (مؤجّل): ARCHITECTURE EVOLUTION
## ═══════════════════════════════════════

### لماذا نؤجّله؟

```
Architecture Evolution يعتمد على:
  1. Skill Library (لأنه يُطوّر skill compositions)
  2. Meta Engine (لأنه يحتاج trajectory analysis)
  3. Agent Framework (لأنه يُعدّل agent architectures)

بدون الثلاثة → Architecture Evolution = blind search
```

### الخطة عند العودة إليه

```
AgentSquare (arXiv:2507.21046):
  - modular design space: planner × memory × tool × executor
  - evolutionary search على الـ space
  - يختار: أفضل combination لكل task type

EvoFlow:
  - يختار: أفضل LLM لكل sub-task
  - يُدمج: مع الـ model pool (11 OpenRouter + 9 Google)

Darwin Gödel Machine:
  - الـ agent يُعدّل codebase نفسه
  - growing archive of stepping stones
  - validation قبل قبول أي تعديل
```

---

## Artifact Architecture — التصميم الكامل

### فلسفة الـ Artifacts

```
كل artifact عنده:
  schema_version: str       ← للـ backward compatibility
  created_by: str           ← أي engine أنتجه
  consumed_by: list[str]    ← من يقرأه
  format: str               ← JSON/YAML/MD/DB
  lifecycle: str            ← per_gen / per_run / persistent
```

### الـ Schema الكامل لكل Artifact

```yaml
# goal_spec.json (INTENT ENGINE → META_AGENT_PROMPT)
schema_version: "1.0"
created_by: INTENT_ENGINE
consumed_by: [META_AGENT, FEEDBACK_AGENT, META_ENGINE]
lifecycle: per_run
format: JSON

# evidence_log.json (GROUNDING ENGINE → CRITIC ENGINE)
schema_version: "1.0"  
created_by: GROUNDING_ENGINE (target agent)
consumed_by: [CRITIC_ENGINE, REGIME_DETECTOR, META_ENGINE]
lifecycle: per_gen
format: JSON

# skill_extraction.json (CRITIC ENGINE → SKILL ENGINE)  [NEW]
schema_version: "1.0"
created_by: CRITIC_ENGINE (on success)
consumed_by: [SKILL_ENGINE, META_AGENT]
lifecycle: per_gen
format: JSON

# meta_optimization.json (META ENGINE → FEEDBACK ENGINE)  [NEW]
schema_version: "1.0"
created_by: META_ENGINE
consumed_by: [FEEDBACK_AGENT]
lifecycle: per_gen
format: JSON

# skill_catalog.yaml (SKILL ENGINE → TARGET AGENT)  [NEW]
schema_version: "1.0"
created_by: SKILL_ENGINE
consumed_by: [META_AGENT, TARGET_AGENT]
lifecycle: persistent
format: YAML
```

---

## خطة التنفيذ الكاملة — بالترتيب

### Week 1-2: Telemetry + Safety (مذكور سابقاً — أساس)

### Week 3-5: SKILL ENGINE (الأهم)

```
Week 3: Core Skill Library
  - genesis/skill_library.py
    - Skill dataclass (SKILL.md format)
    - SkillContract (SkillOps: P,O,A,V,F)
    - SkillLibrary (register, retrieve, catalog)
  - genesis/skills/ directory structure
  - Tests: 50+ tests

Week 4: Skill Extraction + Testing
  - genesis/skill_extractor.py
    - extract_from_agent(target_agent_path, score)
    - MUSE-Autoskill pattern: create → evaluate → register
  - genesis/skill_evaluator.py
    - sandbox testing (pytest)
    - artifact validation
  - Tests: 30+ tests

Week 5: Integration في Orchestrator
  - Section 3: catalog → META_AGENT_PROMPT
  - Section 5a.1: extraction on success
  - Section 5b: best skills → FEEDBACK_AGENT_PROMPT
  - EvoSkill: frontier management
  - Tests: 20+ tests
```

### Week 6-7: META ENGINE

```
Week 6: Core Meta Optimizer
  - genesis/meta_optimizer.py
    - GenerationTrajectory (point history)
    - TextGrad: compute_textual_gradient()
    - OPTO: execution trace analysis
  - Tests: 40+ tests

Week 7: Integration في Orchestrator
  - Section 5a.5 (new): MetaOptimizer.analyze()
  - META_SECTION في FEEDBACK_AGENT_PROMPT
  - meta_optimization.json artifact
  - Tests: 20+ tests
```

### Week 8-10: AGENT FRAMEWORK (Foundation)

```
Week 8: AgentSpec + AgentSoul
  - genesis/agent_hub/agent_spec.py
  - genesis/agent_hub/agent_soul.py
  - JSON-serializable, REST-queryable

Week 9: AgentMemory (MAGMA-inspired)
  - genesis/agent_hub/agent_memory.py
  - episodic + semantic + procedural tiers
  - procedural = Skill Library integration

Week 10: AgentRegistry + Hub
  - genesis/agent_hub/agent_registry.py
  - CRUD for agents
  - Foundation للـ vibe web interface
```

### Week 11: Architecture Evolution Planning (فقط docs)

```
- تحليل AgentSquare + EvoFlow في context GENESIS
- تصميم ArchitectureSearch
- لا implementation بعد
```

---

## فحص المصداقية — هل سرقنا صح؟

### ما أخذناه بالكامل (رابط حرفي بالفلسفة):

| نظرية | المصدر | ما أخذناه | التطبيق في GENESIS |
|-------|--------|----------|-------------------|
| SKILL.md format | Anthropic Agent Skills | progressive disclosure pattern | genesis/skills/*/SKILL.md |
| Skill Contract (P,O,A,V,F) | SkillOps 2605.13716 | contract schema | SkillContract dataclass |
| git-backed lineage | EvoSkill 2603.02766 | frontier management, eviction | SkillLibrary.frontier |
| .memory.md per skill | MUSE-Autoskill 2605.27366 | skill-level episodic memory | .memory.md في كل skill dir |
| sandbox testing before register | MUSE-Autoskill | create-evaluate-register loop | SkillEvaluator.run_tests() |
| textual gradient descent | TextGrad | "gradient" = LLM feedback | MetaOptimizer.compute_textual_gradient() |
| execution trace analysis | OPTO | trace + output + feedback | MetaOptimizer.analyze_trace() |
| trajectory → winning pattern | ExpeL | cross-episode insights | GenerationTrajectory.extract_winning_pattern() |
| Score-DPO preference | ScoreFlow | prefer high-score over low-score | MetaOptimizer preference weighting |

### ما اختلف في GENESIS:

```
الاختلاف المقصود:

1. Skills في GENESIS = agent-level code patterns
   (لا = tool functions كما في Voyager/Minecraft)
   الـ GENESIS skill = "كيف تكتب target_agent.py أفضل"

2. Skill Extraction = من target_agent.py (auto-generated code)
   (لا = من interaction traces كما في SkillOS)
   
3. TextGrad في GENESIS = على الـ agent code نفسه
   (لا = على prompt أو answer)
   الـ "variable" = target_agent.py
   الـ "gradient" = ما يجعل الـ agent يُنتج score أعلى

4. Memory في GENESIS:
   - Episodic = Research Memory (موجود)
   - Procedural = Skill Library (جديد)
   - Semantic = لا (Virtual GENESIS theory/concept stores = هذا)
   - Working = Context Window + context.md

5. Vibe Web = لم يُبنَ بعد — لكن الـ foundation موجود في:
   - JSON-serializable schemas
   - REST-queryable registries
   - Stable artifact format
```

---

## مقياس الإنجاز المتوقع بعد الثلاثة ركائز

```
قبل:                          بعد:
  Tests: 937                   Tests: 1200+
  Engines: 8                   Engines: 11
  Artifacts: 14                Artifacts: 19
  Persistent storage: 1 DB     Persistent storage: 3 DB
  
الأهم:
  Gen N+1 يبدأ من صفر    →    Gen N+1 يبدأ من Skills الناجحة
  Feedback = critic        →    Feedback = optimizer (TextGrad)
  Memory = text insights   →    Memory = executable skills + trajectories
```
