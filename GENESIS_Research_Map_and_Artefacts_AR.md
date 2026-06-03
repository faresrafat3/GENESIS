# Virtual-GENESIS Research Map & Artefacts (Arabic)

## الهدف من هذه الوثيقة
تحويل البحث النظري المتوسع إلى:
1. خريطة توترات/تناقضات يجب حلها
2. مسارات تطوير واكتشاف
3. قائمة artefacts هندسية وبحثية يجب إنتاجها

## أولاً: التناقضات الجوهرية في المجال
### 1) Search vs Memory
- search المكثف يرفع الجودة لكنه مكلف على free tier
- memory تقلل الكلفة لكنها قد تلوث النظام أو تجعله متحجرًا

**قرارنا:**
- memory-first for repeated structure
- search-on-demand for novelty/anomaly
- replay lab لاكتشاف الحد الفاصل الأمثل

### 2) Prompt evolution vs Skill evolution
- prompt evolution أسرع وأرخص
- skill evolution أبطأ لكن أكثر إعادة استخدامًا

**قرارنا:**
- quick fixes → prompt patches
- repeated reusable patterns → skill capsules

### 3) Reflection vs Verification
- reflection تنتج إصلاحات إبداعية
- verification يمنع الهلوسة لكنه قد يخنق الإبداع

**قرارنا:**
- reflection يولّد hypotheses
- verification ينتقي ويضبط
- لا نسمح لأي lesson بالترقية دون test or evidence

### 4) Compression vs Fidelity
- traces الكاملة غنية جدًا
- التخزين الكامل مكلف، والقراءة بطيئة

**قرارنا:**
- raw trace retained
- layered distillation فوقه
- drill-down possible always

### 5) Generality vs Domain specialization
- العمومية تجعل النظام usable على مدى واسع
- التخصص يرفع الأداء كثيرًا في مجال بعينه

**قرارنا:**
- base general architecture
- domain packs فوقها
- skill branches per domain

### 6) Stable system vs Self-changing system
- النظام الثابت أسهل في الضبط
- النظام المتغير قد يتحسن أسرع لكنه يهدد الاستقرار

**قرارنا:**
- shadow changes only
- manifests + rollback
- no direct live mutation of production defaults

### 7) Single best policy vs policy portfolio
- single best policy بسيطة
- portfolio أكثر مرونة ويطبق Ashby’s law (variety absorbs variety)

**قرارنا:**
- policy portfolio by task family and budget band

## ثانيًا: القوانين التصميمية المشتقة
### قانون 1 — No expensive thought without a trigger
لا نستخدم deep reasoning أو multi-candidate أو judge-heavy mode إلا عند trigger واضح.

### قانون 2 — Every success should become reusable
كل نجاح متكرر يتحول إلى:
- example
- lesson
- skill
- routing hint

### قانون 3 — Every failure should leave a scar and a tool
كل فشل ينتج:
- anti-pattern
- regression case
- lesson
- maybe skill fork

### قانون 4 — Controllers evolve before models
طالما setup API-only/free-first، تحسين policy/controller أولى من محاولة internal adaptation.

### قانون 5 — Rich evidence beats scalar reward
التحسين المبني على traces + evidence corpus أقوى من score-only.

### قانون 6 — Variety absorbs variety
يجب أن يمتلك النظام repertoire متنوعًا من:
- skills
- policies
- verification paths
- model routes
كي يوازي تنوع البيئة.

## ثالثًا: مسارات البحث والتطوير الجديدة
### Path A — Memory Operating System
#### سؤال البحث
كيف ننظم memory بحيث تبقى:
- مضغوطة
- قابلة للاستدعاء
- قابلة للتحديث
- وقابلة للتدقيق؟

#### نستلهم من
- Mem0
- MemOS
- SimpleMem
- MemGPT/Letta
- LongMemEval / AMA-Bench

#### المنتج المتوقع
- MemoryCube-like schema
- lifecycle rules
- memory quality metrics
- memory conflict resolution

### Path B — Procedural Memory / Skillization
#### سؤال البحث
كيف نحول الخبرة من narrative traces إلى procedures قابلة للتنفيذ؟

#### نستلهم من
- Voyager
- SkillClaw
- ProcMEM
- MemSkill / SkillRL (كمسارات لاحقة)

#### المنتج المتوقع
- Skill Capsule format
- Skill Genome
- skill promotion criteria
- skill retirement policy

### Path C — Proof-Driven Reasoning
#### سؤال البحث
كيف نجعل الإجابة بنية حجاجية قابلة للفحص، لا مجرد text blob؟

#### نستلهم من
- Lakatos
- Toulmin
- Reflexion
- GEPA

#### المنتج المتوقع
- Answer object = claim/grounds/warrant/backing/rebuttal/qualifier
- verifier interfaces لكل عنصر
- counterexample taxonomy

### Path D — Blackboard Coordination
#### سؤال البحث
كيف نسمح لعدة specialists بالتعاون دون coupling هش؟

#### نستلهم من
- Blackboard architecture
- Society of Mind
- AHE component observability

#### المنتج المتوقع
- Task Blackboard schema
- blackboard event model
- specialist write permissions
- conflict resolution rules

### Path E — Adaptive Control Under Scarcity
#### سؤال البحث
كيف نقرر متى نفكر أكثر ومتى نكتفي؟

#### نستلهم من
- OODA
- Simon bounded rationality
- AutoTTS
- Dreyfus skill stages

#### المنتج المتوقع
- Budget governor
- escalation policy
- aspiration thresholds
- fast/slow cognition controller

### Path F — Anomaly Science for Agents
#### سؤال البحث
كيف نميز بين:
- bug بسيط
- failure mode متكرر
- crisis في paradigm نفسه؟

#### نستلهم من
- Kuhn
- AHE manifests
- HyperAgents meta-improvement

#### المنتج المتوقع
- anomaly detector
- crisis report template
- paradigm fork protocol

### Path G — Antifragile Improvement
#### سؤال البحث
كيف نجعل النظام يستفيد من shocks والأخطاء بدل مجرد النجاة منها؟

#### نستلهم من
- Taleb antifragility
- Schön reflective practice
- Postmortem culture

#### المنتج المتوقع
- failure-to-asset pipeline
- postmortem schema
- negative knowledge store

## رابعًا: Artefacts يجب بناؤها
### A. Core Design Artefacts
1. Architecture Decision Records (ADRs)
2. Task Blackboard Schema
3. Memory OS Schema
4. Skill Capsule Schema
5. Skill Genome Schema
6. Lesson Schema
7. Anti-pattern Schema
8. Failure Taxonomy
9. Verifier Interface Spec
10. Routing Policy Spec
11. Budget / Escalation Spec
12. Replay Research Lab Spec
13. Anomaly / Crisis Protocol
14. Shadow Evaluation Protocol
15. Regression Suite Spec

### B. Data / Knowledge Artefacts
1. Verified Example Bank
2. Success Pattern Library
3. Failure Pattern Library
4. Domain Packs
5. Prompt Patch Archive
6. Policy Portfolio Registry
7. Benchmark Gold Set
8. Holdout Set
9. Memory Quality Reports
10. Skill Evolution Histories

### C. Observability Artefacts
1. Trace Schema
2. Cost Ledger
3. Token Budget Reports
4. Provider/Model Reliability Table
5. Lesson Provenance Graph
6. Skill Provenance Graph
7. Improvement Contracts Log
8. Rollback Ledger

### D. Research Artefacts
1. Ablation matrix
2. Benchmark methodology note
3. Theory note: Externalized Recursive Intelligence
4. Theory note: Proof-Driven Agent Cognition
5. Theory note: Antifragile Harness Improvement
6. Theory note: Memory as Operating System for API agents

## خامسًا: أفكار جديدة قابلة للتحويل إلى system modules
### 1) Argument Graph Memory
بدل تخزين facts فقط، نخزن أيضًا:
- claims
- evidence links
- counterexamples
- confidence
يفيد في البحث، المقارنة، والتفكير النظري.

### 2) Negative Knowledge Store
قاعدة معرفة لما **لا** يجب فعله:
- failed prompts
- brittle skills
- misleading heuristics
- domains where a model underperforms

### 3) Skill Maturity Levels
مستلهم من Dreyfus:
- Novice Skill
- Advanced Skill
- Competent Skill
- Proficient Skill
- Expert Skill
بناءً على transferability + stability + low-cost execution.

### 4) Leverage-Point Optimizer
مستلهم من Meadows:
يفرق بين تدخلات سطحية وعميقة:
- parameter tweak
- retrieval tweak
- rule change
- information flow change
- system goal change
- paradigm change

### 5) Requisite Variety Monitor
مستلهم من Ashby:
إذا البيئة/task families أكثر تنوعًا من repertoire النظام → system fragility alert.

### 6) Reflection-in-Action / Reflection-on-Action Split
مستلهم من Schön:
- during-task micro-reflection
- after-task postmortem reflection

### 7) Case-Based Adaptation Layer
مستلهم من CBR:
Retrieve → Reuse → Revise → Retain
لكن فوق skill/examples/lessons وليس فقط factual memory.

## سادسًا: فرضيات بحثية جديدة
1. Argument-structured answers outperform plain-text answers in verifier-heavy tasks.
2. Negative knowledge stores reduce repeated failure loops faster than positive-memory-only systems.
3. Skill maturity staging improves routing stability.
4. Layered trace distillation preserves enough causal signal while reducing token load.
5. Requisite-variety monitoring predicts where new skill families are needed.
6. Leverage-point analysis helps prioritize deeper, more durable improvements over shallow prompt tweaks.
7. Case-based adaptation improves efficiency for recurring task motifs under free-tier constraints.

## سابعًا: ما الذي نؤجله عمدًا؟
1. full weight updates
2. online RL loops
3. large-scale self-modifying code
4. multimodal OS agents in v1
5. broad multi-user shared skill evolution in initial prototype

## ثامنًا: تعريف “أساس صلب” للمشروع
الأساس الصلب هنا يعني أن النظام:
- قابل للفهم
- قابل للقياس
- قابل للتراجع rollback
- قابل للتوسع عبر gateways لاحقًا
- غير مرهون بموديل واحد
- غير مرهون بخدعة prompt واحدة
- يستفيد من الفشل
- وينتج artefacts معرفية حقيقية بمرور الوقت

## تاسعًا: الصيغة الفلسفية النهائية
النظام الذي نريد بناءه ليس “مجيبًا ذكيًا” فقط، بل:
**نظام نقدي-تجريبي-تراكمي**

- نقدي: لأنه يفحص نفسه ويستقبل counterexamples
- تجريبي: لأنه لا يثق في الفرضيات دون verifier
- تراكمي: لأنه يحول الخبرة إلى memory/skills/policies قابلة لإعادة الاستخدام

## عاشرًا: الخطوة التالية المنطقية
من هذه الوثيقة، نكتب specs دقيقة لـ:
1. Argument Graph + Blackboard
2. Memory OS
3. Skill Genome
4. Budget/OODA Controller
5. Anomaly/Crisis Manager
