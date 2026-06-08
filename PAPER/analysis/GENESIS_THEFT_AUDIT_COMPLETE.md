# GENESIS — Theft Audit الكامل
# تاريخ: 2026-06-08
# قراءة كاملة للكود الأصلي + مقارنة بما بنيناه + تحديد الثغرات

---

## منهجية الفحص

لكل مشروع:
1. ما هي المكونات الكاملة في الكود الأصلي؟
2. ما الذي أخذناه فعلاً؟
3. ما الذي فوّتناه أو أخذناه بشكل ناقص؟
4. ما الذي يختلف بشكل مقصود؟

---

## ══════════════════════════════════════
## THEFT #1: MUSE-Autoskill (arXiv:2605.27366)
## ByteDance + Rochester Institute, May 2026
## ══════════════════════════════════════

### الكود الأصلي — المكونات الكاملة

#### A. Agent Framework (ReAct Loop)
```
المكونات:
  Master Agent     → runs ReAct: Planning → Action → Observation
  Built-in tools:
    skill_create   ← لإنشاء skills جديدة
    web_search     ← للبحث
    sandbox tools: create_sandbox, sandbox_run, sandbox_upload/download, close_sandbox
  
الـ loop:
  Planning → يقرأ catalog → يختار skill أو يُنشئ واحدة
  Action   → يستدعي skill أو يُنشئها
  Observation → يُحلّل النتيجة
```

#### B. Skill Lifecycle — 5 مراحل
```
1. Creation (skill_create):
   - يُوّلد SKILL.md (interface definition)
   - يُخطّط scripts/, resources/, tests/
   - يُولّد الملفات
   - يُشغّل tests → إذا نجحت → register في Skill Bank
   - إذا فشلت → update_skill → إعادة test (loop)

2. Memory (3 مستويات):
   - Skill-level memory: .memory.md لكل skill (يتراكم عبر tasks)
   - Short-term memory: current task context (مع adaptive compression)
   - Long-term memory: persistent notes عبر sessions

3. Management:
   - Skill catalog يُحقن في system prompt (progressive disclosure)
   - Agent يقرأ SKILL.md body فقط عند الحاجة
   - Maintenance: refinement + merging + pruning

4. Evaluation:
   - pytest-compatible tests في tests/ directory
   - create → evaluate → register loop
   - failed tests → يُعيد إلى Refinement

5. Refinement:
   - update_skill على أساس error trace
   - يُعيد test
```

#### C. Skill Format (Anthropic SKILL.md)
```
skill_name/
├── SKILL.md          ← YAML frontmatter + instructions
│   ---
│   name: skill_name
│   description: "..."  ← في system prompt (minimal tokens)
│   ---
│   # Instructions (full body — loaded on demand)
├── scripts/          ← executable Python/Bash/JS
│   └── main.py
├── tests/            ← pytest tests
│   └── test_skill.py
├── resources/        ← data files, templates
└── .memory.md        ← per-skill experience (hidden from catalog)
```

#### D. Context Management (DAG of turns)
```
كل turn = node: (plan, action, observation) + token count
active chain = subgraph of full history
full history = immutable (للـ replay)

Compression:
  Level 1: ضغط node كبير منفرد → summary
  Level 2: دمج nodes متعددة → synthetic node

State persistence عبر sessions:
  يحفظ: conversation history + skill usage + execution metadata
```

#### E. Performance
```
SkillsBench (51 tasks, Docker-evaluated):
  MUSE with generated skills: 68.4% (+15.21pp over baseline)
  On 35 successful tasks: 87.94% (تجاوز human-skill ceiling!)
  Cross-agent transfer: +10.51pp إلى agent مختلف
```

### ما أخذناه نحن

```
✅ أخذناه:
  - SKILL.md format (YAML frontmatter + sections)
  - Progressive disclosure (catalog فقط في system prompt)
  - .memory.md per skill
  - create → evaluate → register loop (conceptually)
  - sandbox testing before registration
  - 5 lifecycle stages framework

⚠️ أخذناه ناقصاً:
  - skill_create كـ built-in tool (فكرة موجودة لكن مش tool رسمي)
  - DAG context management (مش مبني — عندنا context.md فقط)
  - Cross-session state persistence (مش مبني)
  - Adaptive compression (مش مبني)

❌ فوّتناه كلياً:
  - sandbox lifecycle tools: create_sandbox, sandbox_run, etc.
    (عندنا venv subprocess — مختلف!)
  - update_skill function (تحديث skill موجودة)
  - merging skills (unified merge function)
  - pruning skills (retire low-use skills)
  - Long-term memory مستقل (عندنا research_memory.py لكن مختلف)
  - Short-term memory compression (مش موجود)
  - Master Agent architecture (الـ orchestrator مش ReAct loop)
```

### ما يختلف بشكل مقصود
```
MUSE: skill_create يُشغَّل داخل agent loop في runtime
GENESIS: skill extraction تحدث بعد كل generation (offline)

MUSE: sandbox = Docker container لكل skill invocation
GENESIS: venv = Python venv للـ target agent كله (مش per-skill)

MUSE: Master Agent يكتب SKILL.md بنفسه
GENESIS: Skill Extractor يستخرج skills من target_agent.py الناجح
```

### الأجزاء المهمة التي يجب إضافتها
```
Priority 1:
  SkillEvaluator.run_tests()    ← sandbox execution + pytest
  SkillLibrary.update(skill)    ← تحديث skill موجودة
  SkillLibrary.merge(a, b)      ← دمج skills متشابهة
  SkillLibrary.prune()          ← حذف skills ضعيفة

Priority 2:
  Context compression (Level 1 + Level 2) في context_manager.py
  .memory.md write after each skill use
```

---

## ══════════════════════════════════════
## THEFT #2: EvoSkill (arXiv:2603.02766)
## Sentient + Virginia Tech, March 2026
## ══════════════════════════════════════

### الكود الأصلي — المكونات الكاملة

#### A. 3 Collaborating Agents
```
1. Executor Agent (A):
   - يُشغّل tasks تحت governance الـ current program
   - Base program = no skills

2. Proposer Agent (P):
   - يُحلّل failure traces + predicted vs ground-truth answers
   - يراجع execution traces
   - يُحدّد capability gaps
   - يُدقق existing skills
   - يُنتج proposal π: new skill OR edit existing
   - يحتفظ بـ feedback history H (cumulative)

3. Skill-Builder Agent (S):
   - يأخذ proposal π → يُجسّدها كـ skill folder
   - مُجهّز بـ meta-skill لـ best practices
   - Only agent مع write access لـ skills/
```

#### B. EvoSkill Loop (Algorithm)
```python
# Algorithm (من الورقة):
H = []  # feedback history
G = {A}  # frontier of top-k programs
s_A = Eval(A, V)  # baseline score

for t in 1..T:
    # Round-robin parent selection
    i = t % |G|
    p = G[i]
    
    # Collect failures (score < threshold)
    F = CollectFailures(p)
    if not F: continue
    
    # Propose new skill or edit
    π = P(F, H)
    
    # Build candidate program
    p̃ = S(p, π)
    
    # Evaluate on held-out validation
    s̃ = Eval(p̃, V)
    
    # Update frontier
    if |G| < k or s̃ > min(Score(q) for q in G):
        G = G ∪ {p̃}
        if |G| > k:
            G = G \ {argmin Score(q) for q in G}
    
    # Update history
    H.append((π, s̃))

return argmax Score(q) for q in G
```

#### C. Git-backed Program Structure
```
git repository:
  main branch = base agent
  program/{name} = each evolved program (branch)
  
Each branch has:
  .claude/program.yaml:
    name: program_name
    parent: parent_branch
    generation: 3  # mutation depth from root
    system_prompt: "..."
    allowed_tools: [...]
    validation_score: 0.67
  
  skills/
    skill_a/SKILL.md
    skill_b/SKILL.md

frontier/ tags = top-K programs
```

#### D. Data Setup
```
Dataset D → split:
  Training set: للـ failure detection
  Validation set: لـ frontier scoring
  Test set: hidden (final evaluation only)

Category-aware sampling:
  K categories (LLM classifier)
  Stratified split
  Training = category-keyed pools
```

#### E. Performance
```
OfficeQA: 60.6% → 67.9% (+7.3%)
SealQA: 26.6% → 38.7% (+12.1%)
Cross-task transfer: SealQA skill → BrowseComp +5.3%
```

### ما أخذناه نحن
```
✅ أخذناه:
  - Frontier concept (top-K programs)
  - Failure analysis → skill proposal
  - git-based lineage (concept)
  - round-robin parent selection (concept)

⚠️ أخذناه ناقصاً:
  - Frontier management (موجود conceptually لكن مش implemented)
  - Cumulative feedback history H (مش explicit)

❌ فوّتناه كلياً:
  - 3-agent architecture: Executor + Proposer + Skill-Builder
    (عندنا orchestrator يُشغّل كل شيء)
  - Proposer Agent مع feedback history
  - Skill-Builder Agent مع meta-skill
  - git branch per program (مش مبني)
  - Program YAML with lineage
  - Category-aware data sampling
  - Held-out validation set (منفصل عن test)
  - Textual feedback descent (الـ core algorithm)
  - CollectFailures with score threshold
```

### الأجزاء المهمة التي يجب إضافتها
```
Priority 1:
  FailureCollector class:
    collect_failures(gen_dir, threshold=0.6) → list[FailureCase]
  
  ProposerAgent:
    __init__(feedback_history=[])
    propose(failures, existing_skills) → SkillProposal
    # يُحدّد: new_skill OR edit_existing
  
  SkillBuilderAgent:
    materialize(proposal) → SkillFolder
    # مُجهّز بـ meta-skill
  
  EvoSkillLoop:
    run(executor, proposer, builder, validation_set, k=3, T=10)
    # يشتغل مع الـ GENESIS generation loop

Priority 2:
  Feedback history persistence (H.json)
  git branch per program (أو SQLite lineage)
```

---

## ══════════════════════════════════════
## THEFT #3: SkillOps (arXiv:2605.13716)
## Emory University + UIUC, May 2026
## ══════════════════════════════════════

### الكود الأصلي — المكونات الكاملة

#### A. Skill Contract (P, O, A, V, F)
```
s = (P, O, A, V, F)
  P = Preconditions (متى يُستخدَم)
  O = Operation (ماذا يفعل — executable)
  A = Artifact (ما يُنتج — typed)
  V = Validator (كيف يتحقق من صحة A)
  F = Failure Modes (أسباب الفشل المعروفة)

validation gap = V = ∅ (لا يوجد validator)
```

#### B. HSEG (Hierarchical Skill Ecosystem Graph)
```
Graph: L = (S, R)
  S = set of skills
  R = typed relations:
    dep: si → sj (artifact of si satisfies precondition of sj)
    comp: si → sj (output type compatible with input type)
    red: si → sj (equivalent interfaces — redundant)
    alt: si → sj (same goal, different operation)

Two levels:
  Internal: each skill as contract graph (P, O, A, V, F nodes)
  External: graph-of-graphs via dep/comp/red/alt edges
```

#### C. Task-Time Loop
```
Stage 1: Skill Matching
  r(s, τ) = λ·rBM25(s, τ) + (1-λ)·rsem(s, τ)
  C = {s ∈ S : r(s, τ) ≥ θ AND preconditions satisfied}

Stage 2: Dependency Stitching
  π* = argmax Σ r(st, τ)
       subject to: st → dep st+1 AND st → comp st+1

Stage 3: Validator + Adapter Insertion
  if V(s) = ∅ → insert validator node
  if dep edge WITHOUT comp edge → insert adapter node aij
    accept only if type(A_aij) ⊆ type(P_sj)

Stage 4: Local Repair
  if skill sk fails:
    try substitute with alt neighbor
    OR repair(sk) with error trace
    if impossible → log to Library-Time buffer
```

#### D. Library-Time Loop (Maintenance)
```
Health Diagnosis dimensions:
  1. utility: usage_count, success_rate
  2. redundancy: body-hash collisions, interface equivalence
  3. compatibility: type mismatches across dep edges
  4. failure-risk: failure_log frequency
  5. validation-gap: V = ∅

Maintenance Actions:
  merge(si, sj): collapse redundant pair (red edge)
  repair(s): rewrite O using execution feedback
  retire(s): remove obsolete/failing skill + edges
  add_validator(s): insert V when V = ∅
  add_adapter(si, sj): insert type-conversion shim
  instantiate(s, arg): bind task-specific argument at task time

Cost: O(N) — nearly zero LLM calls at library time!
```

#### E. Performance
```
ALFWorld (standalone): 79.5% (+8.8pp over strongest baseline)
Retrieval improvement: +0.68 to +2.90pp
Library maintenance cost: ~0 LLM calls
```

### ما أخذناه نحن
```
✅ أخذناه:
  - Skill Contract (P, O, A, V, F) — dataclass موجود
  - merge, repair, retire actions — موجودة كـ methods
  - validation-gap concept

⚠️ أخذناه ناقصاً:
  - Contract enforcement (P, V) — موجود structurally لكن مش enforced
  - Health diagnosis — موجود conceptually لكن مش systematic

❌ فوّتناه كلياً:
  - HSEG Graph (الأهم!) — dep/comp/red/alt edges
    بدونها لا يمكن dependency stitching
  - Hybrid retrieval: BM25 + semantic (عندنا BM25 فقط من SAGE)
  - Precondition checking قبل selection
  - Adapter insertion (type mismatch repair)
  - Validator insertion (validation gap filling)
  - Library health diagnosis (5 dimensions)
  - CGPD (Cascaded Graph Propagation for Dependency)
  - O(N) maintenance pass (nearly zero LLM calls)
```

### الأجزاء المهمة التي يجب إضافتها
```
Priority 1:
  SkillGraph class:
    add_edge(skill_i, skill_j, relation_type)  # dep/comp/red/alt
    check_compatibility(skill_i, skill_j)
    find_plan(task) → list[Skill]  # dependency stitching
  
  HealthDiagnoser:
    diagnose(library) → HealthReport
    # utility + redundancy + compatibility + failure-risk + validation-gap
  
  MaintenanceEngine:
    run(library, health_report) → maintained_library
    # merge + repair + retire + add_validator + add_adapter
    # O(N) — zero LLM calls

Priority 2:
  Hybrid retrieval: BM25Score + SemanticScore (lambda weighting)
  Precondition checker before skill selection
```

---

## ══════════════════════════════════════
## THEFT #4: SoK Agentic Skills (arXiv:2602.20867)
## Feb 2026 — Taxonomy Reference
## ══════════════════════════════════════

### المكونات الرئيسية

#### A. Formal Skill Definition
```
S = (C, π, T, R)
  C = Conditions (applicability conditions — like preconditions)
  π = Policy/Procedure (the skill itself)
  T = Termination Criteria
  R = Reusable Interface (input/output contract)

Skills vs Tools vs Plans vs Memory:
  Tools   = atomic primitives, fixed interfaces
  Plans   = one-time reasoning scaffolds
  Memory  = stored observations
  Skills  = executable + reusable + governable + applicability conditions
```

#### B. 7 Design Patterns
```
1. Metadata-driven progressive disclosure  [نستخدمه]
2. Code-as-skill (executable scripts)      [نستخدمه]
3. Workflow enforcement (gating)           [constitutional evaluator]
4. Self-evolving libraries                 [نبنيه]
5. Hybrid NL+code macros                   [SKILL.md]
6. Meta-skills (skills that create skills) [المستقبل]
7. Plugin/marketplace distribution         [vibe web المستقبل]
```

#### C. Quality Control Challenge
```
SkillsBench finding: self-generated skills avg -1.3pp (بدون verification)!
النجاح يعتمد على:
  1. Domain specificity
  2. Automated verification (sandbox testing)
  3. Iterative refinement

الحل: كل skill لازم تعدي: create → sandbox_test → register
```

#### D. Security Considerations
```
Supply-chain risks:
  - Malicious SKILL.md → prompt injection
  - Scripts that exfiltrate data
  - Soul.md modification attacks (OpenClaw)

Trust model:
  - Operator-level authority من لحظة installation
  - Never auto-write soul.md

GENESIS محمي لأن:
  - Skills تُستخرج من GENESIS code نفسه (مش من marketplace)
  - venv isolation
  - constitutional_evaluator يراجع
```

### ما أخذناه نحن
```
✅ أخذناه كلياً:
  - 7 design patterns كـ reference
  - Quality control principle (sandbox testing)
  - Progressive disclosure pattern

⚠️ أخذناه ناقصاً:
  - Formal definition S = (C, π, T, R)
    (عندنا P, O, A, V, F من SkillOps — أفضل!)
  - Termination Criteria T (مش محدد في GENESIS skills)

❌ فوّتناه:
  - Lifecycle model كامل (7 stages)
  - Security governance layer
  - Trust-tiered execution
```

---

## ══════════════════════════════════════
## THEFT #5: TextGrad (Stanford, 2024)
## Automatic Differentiation via Text
## ══════════════════════════════════════

### الكود الأصلي — المكونات الكاملة

#### A. Core Concept
```
Neural networks: numeric gradients
TextGrad: textual gradients

∂L/∂v = ∪(w ∈ Succ(v)) LLM_backward(v, w, ∂L/∂w)

TGD.step(variable_old, ∂L/∂variable_old) → variable_new

Variables: prompts, code snippets, molecules, text
Loss function: LLM evaluates quality
```

#### B. PyTorch-style API
```python
# من GitHub الأصلي:
answer = tg.Variable(
    "Initial answer here",
    requires_grad=True,
    role_description="concise and accurate answer"
)
optimizer = tg.TGD(parameters=[answer])
evaluation_instruction = "Evaluate this answer: ..."
loss_fn = tg.TextLoss(evaluation_instruction)

for _ in range(5):
    loss = loss_fn(answer)
    loss.backward()
    optimizer.step()
```

#### C. Computation Graph
```
AI system = computation graph
  nodes = variables (text, code, prompts)
  edges = functions (LLM calls, operations)

Backpropagation:
  Forward: compute outputs
  Backward: LLM generates "gradient" text
  Update: apply textual gradient to variable
```

#### D. Applications (من الورقة)
```
1. Question Answering: optimizes answer text
2. Code generation: optimizes code
3. Molecule optimization: optimizes SMILES strings
4. Radiotherapy planning: optimizes treatment parameters
5. Multi-agent workflows: optimizes agent instructions
```

### ما أخذناه نحن
```
✅ أخذناه (conceptually):
  - "textual gradient" concept
  - LLM as loss function
  - Iterative refinement idea

❌ فوّتناه كلياً:
  - PyTorch-style API (tg.Variable, tg.TGD, tg.TextLoss)
  - Computation graph structure
  - backward() propagation through the graph
  - The key insight: treating the FULL generation history as a graph
  - optimizer.step() as explicit operation

الـ MetaOptimizer اللي خططنا له = TextGrad مبسّط جداً
المفروض:
  target_agent.py = Variable (requires_grad=True)
  score = TextLoss(agent_code, task)
  gradient = LLM_backward(agent, score)
  new_agent = TGD.step(agent, gradient)
```

### الأجزاء المهمة التي يجب إضافتها
```
genesis/meta_optimizer.py يجب أن يُطبّق:

class TextVariable:
    value: str          # agent code or prompt
    requires_grad: bool
    role: str
    gradient: str = ""  # textual gradient

class TextLoss:
    def __call__(self, variable) → TextVariable:
        # LLM evaluates quality → produces loss description
    
    def backward(self, loss) → str:
        # LLM generates "textual gradient"

class TGD:  # Textual Gradient Descent
    def __init__(self, parameters: list[TextVariable])
    def step(self):
        # Updates each variable using its gradient
        for param in self.parameters:
            param.value = LLM_update(param.value, param.gradient)
    def zero_grad(self):
        for param in self.parameters:
            param.gradient = ""
```

---

## ══════════════════════════════════════
## THEFT #6: metaTextGrad (arXiv:2505.18524)
## May 2025 — Optimizes the Optimizer
## ══════════════════════════════════════

### المكونات الرئيسية

#### Meta-Structure Optimizer
```
Loop:
  Initialize: run optimizer on validation → get initial best
  Propose: meta optimizer proposes improved optimizer
           (using reference optimizers + prior best)
  Update: test proposed optimizer → update if better
  Extract: return best optimizer found

The optimizer itself becomes optimizable!
```

#### Meta-Prompt Optimizer
```
Initialize: evaluate initial prompt on validation
Propose: sample training data → analyze task → improve prompt
         (randomly samples examples, not all data)
Update: test on validation → update if better
Extract: return best prompt

Only LLM calls in Propose stage.
```

### ما أخذناه نحن
```
⚠️ أخذناه ناقصاً:
  - Meta-optimizer concept موجود في خطتنا

❌ فوّتناه:
  - Optimizer optimizing itself (meta-level)
  - Initialize-Propose-Update-Extract cycle
  - Validation set separation
```

---

## ══════════════════════════════════════
## THEFT #7: MAGMA Memory (arXiv:2601.03236)
## Best memory performance 2026
## ══════════════════════════════════════

### المكونات الكاملة

#### A. Multi-Graph Architecture
```
4 subgraphs:
  Semantic: entities + relationships + facts (atemporal)
  Temporal: events + timestamps + sequences
  Causal: cause-effect relationships
  Entity: named entities + attributes

Cross-graph edges: connect same concept across subgraphs
```

#### B. Intent-Guided Retrieval
```
query → detect intent type
intent → select relevant subgraph(s)
subgraph traversal → multi-hop reasoning
cross-graph → combine evidence
result → context injection
```

#### C. Dual-Stream Consolidation
```
Fast stream: immediate write to episodic
Slow stream: periodic consolidation to semantic
  → compress multiple episodes → single fact
  → resolve conflicts
  → update entity attributes
```

#### D. Performance
```
LoCoMo benchmark: 0.70 judge score (best 2026)
vs MemoryOS: 0.553
vs A-MEM: 0.58
vs Nemori: 0.59
```

### ما أخذناه نحن
```
✅ أخذناه (في الخطة):
  - 4 memory types concept
  - Intent-guided retrieval

❌ فوّتناه (مش مبني بعد):
  - الـ graph structure نفسه (SQLite فقط)
  - Cross-graph traversal
  - Dual-stream consolidation
  - Temporal subgraph (timestamps على events)
  - Causal subgraph

الـ AgentMemory اللي خططنا له ≠ MAGMA
AgentMemory = 4 SQLite tables (أبسط بكثير)
MAGMA = 4 interconnected graphs (أقوى بكثير)
```

---

## ══════════════════════════════════════
## THEFT #8: OpenClaw SOUL.md
## 2026 Industry Standard
## ══════════════════════════════════════

### المكونات الكاملة

#### A. File Hierarchy
```
~/.openclaw/workspace/
├── SOUL.md      ← personality, values, constitution (NON-NEGOTIABLE)
├── AGENTS.md    ← behavior guidelines + safety rules
├── USER.md      ← user profile + working contract
├── TOOLS.md     ← available tools guide
├── IDENTITY.md  ← name, role, routing metadata
├── MEMORY.md    ← curated durable facts (small + structured)
└── HEARTBEAT.md ← recurring task checklist

Loading order: AGENTS.md → SOUL.md → USER.md → TOOLS.md → Skills → merge
Priority: CLI > env vars > config files > defaults
```

#### B. SOUL.md Sections
```markdown
---
name: Agent Name
role: Role Label
version: 1.0.0
---

## Identity
Who the agent is.

## Communication Style
- Format preferences
- Tone

## Values
- accuracy_over_speed
- cite_sources_always

## Boundaries (Constitution)
- never_fabricate_links
- never_auto_write_soul  ← CRITICAL security rule
- always_sandbox_code

## Example Responses
Good: ...
Bad: ...
```

#### C. Security Principles
```
soul.md = control plane → يتغير نادراً
memory.md = small + structured → يتضمن expiry dates
user.md = stable profile → لا يُخزّن secrets

Never auto-write identity files!
Trust: soul.md → operator level authority
```

#### D. Multi-Agent
```
كل agent له workspace منفصل مع SOUL.md خاص
shared AGENTS.md لـ common rules
CSS-like cascade: most specific wins
```

### ما أخذناه نحن
```
✅ أخذناه:
  - SOUL.md concept + sections
  - Security principle: never_auto_write_soul
  - Separation: soul (constitution) vs memory (facts)

⚠️ أخذناه ناقصاً:
  - AGENTS.md (behavior guidelines منفصل عن soul)
  - USER.md (لا نفكر في الـ user context)
  - HEARTBEAT.md (recurring tasks)
  - Loading order + priority cascade

❌ فوّتناه:
  - Multi-agent inheritance (shared AGENTS.md)
  - File expiry dates في MEMORY.md
  - CSS-like cascade resolution
```

---

## ══════════════════════════════════════
## خلاصة — Gap Matrix الكامل
## ══════════════════════════════════════

### ما بنيناه مقابل ما ينقصنا

```
┌─────────────────────────────────────────────────────────────────┐
│ SKILL ENGINE                                                    │
├──────────────────────────┬──────────────────────────────────────┤
│ ✅ مبني                  │ ❌ ناقص                              │
├──────────────────────────┼──────────────────────────────────────┤
│ SKILL.md format          │ Sandbox tools (create/run/close)     │
│ Progressive disclosure   │ update_skill function                │
│ .memory.md concept       │ merge() + prune()                    │
│ create→evaluate→register │ HSEG graph (SkillOps)               │
│ Skill Contract (P,O,A,V,F)│ Hybrid retrieval (BM25+semantic)   │
│ merge/repair/retire ideas │ 3-agent evolution (EvoSkill)       │
│ EvidenceLog concept      │ Feedback history H                   │
│ web_search tool          │ git branch per program               │
│                          │ Short-term memory compression        │
│                          │ Long-term memory persistence         │
│                          │ Context DAG management               │
└──────────────────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ META ENGINE                                                     │
├──────────────────────────┬──────────────────────────────────────┤
│ ✅ مبني                  │ ❌ ناقص                              │
├──────────────────────────┼──────────────────────────────────────┤
│ GenerationTrajectory     │ TextGrad PyTorch-style API           │
│  concept                 │ tg.Variable + tg.TGD + tg.TextLoss  │
│ Textual gradient idea    │ backward() computation graph          │
│ SPIN semantic gap        │ Meta-level optimizer (optimizes opt) │
│ Regime detection         │ Validation set separation            │
│                          │ Explicit gradient accumulation       │
└──────────────────────────┴──────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AGENT HUB / MEMORY                                              │
├──────────────────────────┬──────────────────────────────────────┤
│ ✅ مبني                  │ ❌ ناقص                              │
├──────────────────────────┼──────────────────────────────────────┤
│ SOUL.md concept          │ MAGMA 4-graph structure              │
│ Identity runtime         │ Cross-graph traversal                │
│ Research memory (SQLite) │ Dual-stream consolidation           │
│ Memory OS (in-agent)     │ AGENTS.md + USER.md files           │
│ Ladder Ascent            │ Multi-agent SOUL inheritance         │
│ AgentSpec concept        │ HEARTBEAT.md                        │
│                          │ Memory expiry dates                  │
│                          │ Context window management            │
└──────────────────────────┴──────────────────────────────────────┘
```

### أولوية الإضافات — بالترتيب الدقيق

```
الأسبوع 1 (الأساس):
  1. SkillEvaluator.run_tests() ← sandbox execution (MUSE)
  2. SkillGraph HSEG minimal ← dep/comp edges فقط (SkillOps)
  3. Hybrid retrieval ← BM25 + semantic (SkillOps)

الأسبوع 2 (الأهم للـ EvoSkill):
  4. ProposerAgent ← failure analysis + proposal (EvoSkill)
  5. FeedbackHistory ← cumulative H (EvoSkill)
  6. SkillBuilder ← materialize proposal → skill folder (EvoSkill)

الأسبوع 3 (TextGrad):
  7. TextVariable + TGD ← PyTorch-style (TextGrad)
  8. TextLoss ← LLM evaluator (TextGrad)
  9. backward() ← textual gradient computation (TextGrad)

الأسبوع 4 (Memory):
  10. AGENTS.md + HEARTBEAT.md ← missing soul files (OpenClaw)
  11. Memory expiry ← dates on entries (OpenClaw)
  12. Episodic timestamp ← temporal layer (MAGMA)
```
