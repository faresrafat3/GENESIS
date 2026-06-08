# GENESIS Architecture Redesign Plan
# تاريخ: 2026-06-08
# بعد البحث في 15+ ورقة + تحليل الـ codebase الكامل

---

## المشكلة الأصلية

التقسيم الحالي "Layers 1-4" مبني على ترتيب التنفيذ مش على وظيفة فعلية:
- Layer 1 = Web Search (tool)
- Layer 2 = Open Task Eval (evaluator)
- Layer 3 = Goal Spec (planner)
- Layer 4 = Enhanced Pipeline (cognitive core)

ده **مش architecture** — ده ترتيب زمني لإضافات.
المجال وصل لـ reference architectures حقيقية بـ components محددة الوظيفة.

---

## ما وصله المجال — الـ Reference Architectures

### 1. Architectures for Building Agentic AI (arXiv:2512.09458 — Springer)
**أقوى ورقة هيكلية في المجال:**

```
8 Components الإلزامية لأي agentic system موثوق:
  1. Goal Manager     — ينظّم الأهداف والقيود
  2. Planner          — يُجزّئ لـ sub-tasks
  3. Tool Router      — يختار الـ tool المناسب
  4. Executor         — ينفّذ في sandbox
  5. Memory           — episodic + semantic
  6. Verifier/Critic  — يفحص النتائج
  7. Safety Monitor   — budgets + escalation
  8. Telemetry        — observability + audit trail
```

### 2. Six-Layer Reference Architecture (arXiv:2604.26275)
**للـ agentic software engineering:**

```
Layer 1: Intent & Specification (ما يريد المستخدم)
Layer 2: Planning & Decomposition (كيف يُنفَّذ)
Layer 3: Tool & Environment (ما يُستخدَم)
Layer 4: Execution & Validation (التنفيذ والتحقق)
Layer 5: Memory & State (الذاكرة والحالة)
Layer 6: Governance & Observability (الحوكمة والمراقبة)
```

### 3. Self-Evolving Agents Survey (arXiv:2507.21046)
**الـ evolutionary pillars:**

```
What evolves:
  - Models (parameters)
  - Context (instructions + memory)
  - Tools (skill library)
  - Architecture (the system itself)

Darwin Gödel Machine: الـ agent يُعدّل نفسه recursively
AgentSquare: evolutionary search على الـ architecture
MemEvolve: يُطوّر نظام الذاكرة نفسه
```

### 4. Layered Recursive Stack (2026 State of Art)

```
User Goal
  → Orchestrator (Plan & Delegate)
    → Task Agent (Execute + Tools)
      → Secure Sandbox (Test)
        → Evaluator/Critic (Measure)
          → if Fail: Self-Correction Loop
          → if Pass: Meta-Optimizer (Distill Skill)
            → Skill Library (Store)
              → feeds back to Orchestrator
```

---

## GENESIS الحالي — أين هو بالضبط؟

```
✅ موجود ويعمل:
  - Goal Manager (partial) → Goal Specification Layer 3
  - Planner → Meta-Agent (partial)
  - Tool Router → Economy Control (Tier 1/2/3) ← هذا tool router!
  - Executor → target agent في venv
  - Memory → Research Memory + Memory OS
  - Verifier → Constitutional Check + Semantic Verifier
  - Self-Improvement Loop → الـ main loop نفسه
  - Telemetry (partial) → agent_execution.json

❌ ناقص أو ضعيف:
  - Safety Monitor → مفيش budget hard limits
  - Observability → مش unified
  - Skill Library → مفيش persistent skill storage
  - Meta-Optimizer → الـ feedback agent بيكتب code بس مش بيبني skills
  - Architecture Self-Evolution → AlphaEvolve skeleton فقط
  - Tool Creation → الـ agent مش بيبني tools جديدة
```

---

## الخطة الكاملة — من الهيكل للـ Names للـ Implementation

### أولاً: إعادة التسمية (بدون code — فكري فقط)

**الاسم الجديد للـ "Layers":**

```
قديم (ترتيب زمني):           جديد (وظيفة حقيقية):
Layer 1: Web Search       →  GROUNDING ENGINE
Layer 2: Open Task Eval   →  CRITIC ENGINE  
Layer 3: Goal Spec        →  INTENT ENGINE
Layer 4: Enhanced Pipeline →  COGNITIVE ENGINE
```

**الـ Main Loop الجديد:**

```
GENESIS = A-SDLC (Agentic Software Development Loop)

Round 0 (once per run):
  INTENT ENGINE      — Goal Contract + decomposition
  
For each Generation:
  GROUNDING ENGINE   — web search + evidence collection
  COGNITIVE ENGINE   — Virtual GENESIS pipeline (tier/concept/theory)
  TARGET EXECUTION   — sandbox run
  CRITIC ENGINE      — eval + hallucination + LLM-judge
  SAFETY MONITOR     — constitutional + budget
  EVOLUTION ENGINE   — AlphaEvolve + Regime Detection
  FEEDBACK ENGINE    — contextual + semantic + ladder signals
  MEMORY ENGINE      — skills + insights + failure patterns
```

---

### ثانياً: الخطة التفصيلية — 5 مراحل

---

## المرحلة A: Observability & Telemetry (أسبوع واحد)
**مصدر: arXiv:2512.09458 (Safety Monitor + Telemetry)**

**المشكلة:** كل gen يكتب artifacts مختلفة بـ formats مختلفة. مفيش unified view.

**ما نبنيه:**
```
genesis/telemetry.py
  - RunTelemetry class
  - يُسجّل كل event: section_start/end, scores, signals
  - يكتب run_telemetry.json في الـ run directory
  - unified dashboard per run
```

**ما نسرقه:**
- arXiv:2512.09458: "immutable audit trail + structured logs"
- Agentic SDLC: "observability makes all components replayable"

**الأثر:** أي section تفشل — نعرف بالضبط وين وليه.

---

## المرحلة B: Safety Monitor (أسبوع واحد)
**مصدر: arXiv:2512.09458 (Safety Supervisor)**

**المشكلة:** مفيش hard limits على:
- عدد API calls
- cost per generation
- timeout per generation
- hallucination_rate threshold (يوقف التقدم لو عالي جداً)

**ما نبنيه:**
```
genesis/safety_monitor.py
  - BudgetGuard: max_api_calls, max_cost_usd, max_time_sec
  - HallucinationGuard: يوقف لو hallucination_rate > threshold
  - EscalationPolicy: warn → pause → halt
  - يُدمج في orchestrator كـ check قبل كل generation
```

**ما نسرقه:**
- arXiv:2512.09458: "budgets, termination conditions, safe-halt rules"
- MAESTRO framework: "escalation control + immutable logging"

---

## المرحلة C: Skill Library (أسبوعان)
**مصدر: Self-Evolving Agents Survey (arXiv:2507.21046) + Darwin Gödel Machine**

**المشكلة الكبيرة:** الـ feedback agent بيكتب code جديد كل مرة من صفر.
مش بيبني على "skills" تعلّمها في runs سابقة.
Research Memory موجود بس بيحفظ insights نصية — مش skills قابلة للتنفيذ.

**ما نبنيه:**
```
genesis/skill_library.py
  - Skill: اسم + كود + domain + performance_score + usage_count
  - SkillLibrary: SQLite store للـ skills
  - extract_skill(): من target agent ناجح → skill قابلة للاستخدام
  - retrieve_skills(): لـ meta-agent عشان يُدمج skills سابقة
  - evolve_skill(): يُطوّر skill موجودة بدل ما يُعيد اختراعها
```

**ما نسرقه:**
- AgentSquare: "modular skill library"
- MemEvolve: "يُطوّر آلية الذاكرة نفسها"
- Darwin Gödel Machine: "growing archive of stepping stones"

**الأثر:** Gen N+1 يبدأ من Gen N الناجح + skills محددة — مش من صفر.

---

## المرحلة D: Meta-Optimizer (أسبوعان)
**مصدر: Layered Recursive Stack + DGM-Hyperagents**

**المشكلة:** الـ feedback agent = critic فقط. مش optimizer.
الـ meta-agent = writer فقط. مش meta-learner.

**الفرق:**
```
Critic: "هذا الكود غلط لأن X"
Optimizer: "استخرج الـ pattern الناجح من gen_3 وادمجه في gen_4"
```

**ما نبنيه:**
```
genesis/meta_optimizer.py
  - analyze_generation_trajectory(): يقرأ كل gens → يُحدد patterns
  - extract_winning_strategy(): من gens ناجحة → strategy قابلة للتعميم
  - synthesize_next_agent(): بيدمج:
      - winning strategy من history
      - relevant skills من Skill Library
      - goal contract من Intent Engine
      - feedback من Critic
  - يستبدل جزء من FEEDBACK_AGENT_PROMPT
```

**ما نسرقه:**
- DGM-Hyperagents: "meta-level modification procedure is itself editable"
- TextGrad: "textual gradients propagate feedback backward through workflow"
- ScoreFlow: "trains generator using preference optimization"

---

## المرحلة E: Architecture Self-Evolution (شهر)
**مصدر: AgentSquare + AlphaEvolve (already partial) + EvoFlow**

**المشكلة:** AlphaEvolve موجود كـ skeleton للـ code evolution.
لكن مفيش evolution على الـ architecture نفسها.

**ما نبنيه:**
```
genesis/architecture_evolution.py
  - ComponentRegistry: كل component عنده version + performance_history
  - ArchitectureSearch: يُجرّب combinations مختلفة من الـ components
  - ComponentMutation: يُعدّل component parameters (مش code)
  - يُدمج مع AlphaEvolve الموجود
```

**ما نسرقه:**
- AgentSquare: "evolutionary algorithm على modular design space"
- EvoFlow: "يختار أفضل LLM لكل task من pool متنوع"
- Regime Detection الموجود: يُحدد متى تتغير الـ architecture

---

## الجدول الزمني الكامل

```
Week 1-2:   المرحلة A (Telemetry) + المرحلة B (Safety Monitor)
            → أساس الـ observability والأمان
            → tests: 40+ tests

Week 3-4:   المرحلة C (Skill Library)
            → أهم تغيير معماري — يُحوّل الـ loop من stateless لـ stateful
            → tests: 50+ tests

Week 5-6:   المرحلة D (Meta-Optimizer)
            → يُحوّل الـ feedback agent من critic لـ optimizer
            → tests: 40+ tests

Week 7-8:   المرحلة E (Architecture Self-Evolution)
            → يُكمّل الـ AlphaEvolve skeleton
            → tests: 30+ tests

Week 9:     Rename + Restructure + Documentation
            → الـ CLI الجديد مع الأسماء الجديدة
            → الخريطة المحدثة
```

---

## الـ CLI الجديد (بعد كل المراحل)

```bash
python genesis/orchestrator.py \
  --task micro_task \
  --max_gen 5 \
  --backend openai \
  \
  # INTENT ENGINE
  --use_goal_spec \
  --local_filter "Egypt" \
  \
  # GROUNDING ENGINE
  --use_web_search \
  \
  # CRITIC ENGINE
  --use_open_eval \
  \
  # EVOLUTION ENGINE
  --use_regime_detection \
  --use_evolution \
  \
  # SAFETY MONITOR (جديد)
  --max_cost_usd 5.0 \
  --halt_on_hallucination 0.8 \
  \
  # META-OPTIMIZER (جديد)
  --use_skill_library \
  --use_meta_optimizer
```

---

## ترتيب الأولوية

```
Priority 1 (مش اختياري): Safety Monitor + Telemetry
  → بدونهم الـ system مش controllable

Priority 2 (أهم تغيير): Skill Library
  → يُحوّل كل gen من stateless لـ stateful learning

Priority 3 (أكبر leverage): Meta-Optimizer
  → يُضاعف قيمة كل الـ components الأخرى

Priority 4 (أقوى innovation): Architecture Self-Evolution
  → GENESIS يُطوّر نفسه — مش بس الـ agents

Priority 5 (cosmetic لكن مهم): Rename + Restructure
  → بعد كل ده يبقى الـ naming منطقي
```

---

## الأوراق المراد سرقتها في كل مرحلة

| المرحلة | الأوراق | العناصر المسروقة |
|---------|---------|-----------------|
| A (Telemetry) | arXiv:2512.09458 | immutable audit trail, structured logs, replay capability |
| B (Safety) | arXiv:2512.09458, MAESTRO | budget guards, halt rules, escalation policy |
| C (Skills) | arXiv:2507.21046, DGM | skill extraction, archive building, stepping stones |
| D (Meta-Opt) | DGM-Hyperagents, TextGrad | meta-level modification, textual gradients |
| E (Arch-Evo) | AgentSquare, EvoFlow | modular design space search, heterogeneous LLM selection |
