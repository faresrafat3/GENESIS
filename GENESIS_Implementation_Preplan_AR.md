# Virtual-GENESIS Implementation Preplan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي الانتقال الرسمي من:
- النظرية
- والـ ontology
- والـ specs
- والـ prototype slice

إلى:
- **خطة بناء تقنية**

ليست كتابة كود كاملة بعد، لكنها تحدد:
1. ما الذي سنبنيه أولًا؟
2. بأي ترتيب؟
3. ما الموديولات الأساسية؟
4. ما الـ interfaces الأولية؟
5. ما الذي يمكن تبسيطه أو mockه؟
6. ما الذي يجب تأجيله عمدًا؟

هذه الوثيقة يجب أن تمنع:
- التشتت أثناء البناء
- والـ overengineering
- و“البدء من كل مكان في نفس الوقت”

---

# 1) مبدأ التنفيذ المركزي
نحن لا نبني النظام الكامل.

نحن نبني:

# **Prototype Slice for Thesis 1 & 2**

أي:
- Concept Formation
- Memory OS
- Cognitive Economy / Tier Routing

داخل نطاق task families محدودة
وبـ minimal evaluation harness

### نتيجة ذلك
كل قرار تقني من الآن يجب أن يُسأل عنه:

> هل يخدم هذه الشريحة؟
> هل يخدم Thesis 1 أو Thesis 2؟
> هل يمكن تأجيله؟

إذا كانت الإجابة “لا”، فغالبًا يؤجل.

---

# 2) ما الذي لن نبنيه الآن؟
حتى نحافظ على التركيز، نثبت صراحة ما لن يدخل التنفيذ الأول.

## Deferred for later
- Local Theory Builder الكامل
- Anomaly/Crisis Manager الكامل
- Agent Identity runtime governance الكامل
- Sparse committee execution
- Self-benchmarking generation engine
- GUI/web/OS environments
- multi-user memory
- fork orchestration
- fully dynamic skill synthesis at scale

### لماذا؟
لأن وجودها الآن سيصنع ضوضاء أكثر من المعرفة.

---

# 3) الهيكل التنفيذي المقترح
نقترح أن يبنى prototype على ست طبقات تنفيذية فقط:

## Layer 1 — Task Ingress
- task normalization
- task family assignment
- difficulty/criticality estimation

## Layer 2 — Blackboard Runtime
- create and manage task-local blackboard
- attach context
- store claims / decisions / verification state

## Layer 3 — Memory OS Runtime
- store/retrieve typed memory units
- apply minimal forgetting/archival
- provide memory packs للـ blackboard

## Layer 4 — Concept Formation Runtime
- analyze episodes/patterns
- produce concept candidates
- validate/persist minimal concepts

## Layer 5 — Economy & Tier Control
- choose tier
- decide on escalation
- record cognitive spend in ledger

## Layer 6 — Evaluation Harness
- run conditions/baselines
- collect metrics
- generate reports

---

# 4) الموديولات الرئيسية

## Module A — `task_ingress`
### الوظيفة
استقبال المهمة وتحويلها إلى task object منظم.

### responsibilities
- normalize text
- classify family
- estimate difficulty
- assign criticality
- define success criteria template

### outputs
- `TaskObject`
- initial blackboard seed data

---

## Module B — `blackboard_core`
### الوظيفة
إدارة Task Blackboard lifecycle.

### responsibilities
- initialize blackboard
- maintain sections
- create snapshots
- update sections with typed entries
- provide read/write API للموديولات الأخرى

### outputs
- `BlackboardObject`
- `BlackboardSnapshot`

---

## Module C — `memory_os`
### الوظيفة
إدارة الذاكرة persistent.

### submodules
1. `memory_store`
2. `memory_retriever`
3. `memory_consolidator` (minimal)
4. `memory_forgetting` (minimal)
5. `memory_reports`

### responsibilities
- store typed memory units
- retrieve memory packs for tasks
- archive/deprecate low-value memories
- emit memory utility reports

---

## Module D — `concept_engine`
### الوظيفة
تحويل episodes/patterns إلى concept candidates ثم validated concepts.

### submodules
1. `contrastive_selector`
2. `pattern_extractor`
3. `concept_proposer`
4. `scope_drafter`
5. `counterexample_checker` (minimal)
6. `concept_registry`

### responsibilities
- propose concepts
- test basic scope
- promote or demote
- persist concept cards

---

## Module E — `economy_control`
### الوظيفة
إدارة cognition allocation.

### submodules
1. `tier_router`
2. `escalation_engine`
3. `cognitive_ledger`
4. `economy_reports`

### responsibilities
- decide retrieval depth
- choose model tier
- decide whether to escalate
- log cognitive actions and costs

---

## Module F — `reasoning_runtime`
### الوظيفة
تنفيذ المسار الأساسي للإجابة.

### responsibilities
- run selected model tier
- use memory pack
- produce candidate claims
- call minimal verifier
- update blackboard

### note
لن نبني full search topology engine الآن؛ سنبدأ بشكل أبسط:
- linear by default
- optional light self-consistency if needed later

---

## Module G — `verification_runtime`
### الوظيفة
تشغيل الـ checks الأساسية.

### responsibilities
- schema validation
- evidence sufficiency check
- simple task-family rules
- optional rubric/judge call

---

## Module H — `evaluation_harness`
### الوظيفة
تشغيل conditions والـ baselines وتسجيل النتائج.

### responsibilities
- run all conditions on task set
- capture metrics
- compare baselines
- create summary reports

---

# 5) الموديولات المسموح لها بالـ mock
حتى لا نتعطل، بعض الأجزاء يمكن أن تبدأ بشكل mocked أو heuristic.

## can be mocked initially
### 5.1 Task family classifier
- rule-based or prompt-based lightweight classifier

### 5.2 Difficulty estimator
- heuristic thresholds بدل model complex

### 5.3 Concept scoring
- heuristic/ordinal scoring بدل model learned

### 5.4 Economy return estimation
- approximate rules بدل expected-value estimator كامل

### 5.5 Counterexample checker
- basic holdout / negative example probing بدل generator كامل

### 5.6 Verification judge
- single rubric-based model call بدل multi-judge

---

# 6) ترتيب البناء المقترح
نقترح ست مراحل تنفيذية:

## Build Phase 1 — Skeleton & Objects
### نبني أولًا
- TaskObject
- BlackboardObject
- MemoryUnit
- ConceptCandidate
- TierDecisionObject
- LedgerEntry

### الهدف
تثبيت data model قبل أي logic.

---

## Build Phase 2 — Blackboard Runtime
### نبني
- blackboard initialization
- section APIs
- snapshot creation
- minimal typed update functions

### الهدف
أي شيء بعد ذلك يعمل فوق state substrate واضحة.

---

## Build Phase 3 — Memory OS Minimal
### نبني
- store/retrieve
- typed memory layers
- simple archival/deprecate rules
- memory pack generation للـ blackboard

### الهدف
إتاحة Baseline 1 بسرعة.

---

## Build Phase 4 — Reasoning + Verification Minimal
### نبني
- basic answer generation path
- memory-aware retrieval path
- verification checks
- result writing into blackboard

### الهدف
تشغيل Baseline 0 و1 و2 و3.

---

## Build Phase 5 — Concept Formation Minimal
### نبني
- collect successful/failed episodes
- contrastive grouping
- concept proposal
- concept registry
- concept activation in retrieval/routing

### الهدف
اختبار Thesis 1 فعليًا.

---

## Build Phase 6 — Economy Control Minimal
### نبني
- tier router
- escalation triggers
- cognitive ledger writes
- economy reports

### الهدف
اختبار Thesis 2 فعليًا.

---

# 7) ترتيب تشغيل Prototype 1
داخل run واحدة، flow مبدئيًا:

1. ingest task
2. initialize blackboard
3. retrieve memory pack
4. route tier
5. run reasoning
6. verify result
7. possibly escalate once
8. finalize output
9. record ledger entry
10. store episode
11. periodically run concept engine over accumulated episodes

### periodic concept cycle
مثلاً بعد كل 5–10 tasks في dev batch:
- concept formation run
- validated concepts added to concept registry
- next tasks can use them

---

# 8) البنية الملفية/المجلدية المقترحة
اقتراح أولي فقط:

```text
virtual_genesis/
  core/
    objects/
      task.py
      blackboard.py
      memory.py
      concept.py
      decision.py
      ledger.py
    ontology/
      enums.py
      relations.py

  runtime/
    task_ingress/
    blackboard_core/
    memory_os/
    reasoning_runtime/
    verification_runtime/
    concept_engine/
    economy_control/

  eval/
    task_sets/
    conditions/
    metrics/
    reports/
    runners/

  configs/
    tiers/
    policies/
    tasks/

  docs/
    theory/
    specs/
```

هذه ليست نهائية لكنها تمنع الفوضى منذ البداية.

---

# 9) ما هي الـ objects التي يجب أن تكون قوية من البداية؟
بعض objects لا يجب أن تبدأ بشكل sloppy.

## critical objects
1. TaskObject
2. BlackboardObject
3. MemoryUnit
4. ConceptCard / ConceptCandidate
5. TierDecisionObject
6. LedgerEntry
7. EvaluationResult

### لماذا؟
لأن أي ارتباك فيها سيصعب attribution لاحقًا.

---

# 10) ما هي الـ policies التي تكفي كبداية؟
لا نحتاج policies ذكية جدًا من اليوم الأول.

## Minimal policies
### Retrieval policy v0
- semantic + type-priority ordering

### Forgetting policy v0
- age + utility thresholds → active / archived / deprecated

### Tier routing v0
- difficulty + uncertainty + verification signals → choose tier

### Escalation v0
- one or two escalation triggers max

### Concept promotion v0
- basic acceptance criteria from spec

---

# 11) أول ما يجب أن ينتج من النظام (Outputs)
قبل أي sophistication، لازم النظام ينتج outputs قابلة للفحص:

## Required outputs
1. task result
2. blackboard snapshot
3. retrieved memory pack summary
4. tier decision summary
5. verification summary
6. ledger entry
7. episode summary
8. candidate concept list (periodic)

بدون هذه، لن نستطيع أن نعرف من أين جاءت gains أو failures.

---

# 12) ما الذي سيُعد “نجاحًا تقنيًا مبكرًا”؟

## Technical Success A
كل task run تترك blackboard + memory retrieval + decision + verification trace منظّمة.

## Technical Success B
يمكن تشغيل Baseline 0 و1 و2 و3 end-to-end على 10–20 tasks أولًا.

## Technical Success C
concept cycle ينتج candidates مفهومة ومخزنة.

## Technical Success D
tier router تكتب decisions مفهومة بدل silent behavior.

## Technical Success E
evaluation harness تُخرج تقارير conditions المقارنة.

---

# 13) ماذا لا نفعل أثناء التنفيذ؟

## Anti-pattern 1
لا نكتب framework عامة قبل أن نثبت slice.

## Anti-pattern 2
لا ندخل web/GUI/tools complex integration الآن.

## Anti-pattern 3
لا نحاول حل contradiction/anomaly governance كاملة قبل وجود prototype runs.

## Anti-pattern 4
لا نُخفي state في prompts بدل objects.

## Anti-pattern 5
لا ننتظر “النظام المثالي” قبل أول batch evaluable.

---

# 14) ما الوثائق التالية مباشرة بعد هذه الخطة؟
الآن أصبح لدينا اختياران مشروعان:

## Path A — Continue formal governance specs
- Contradiction Ledger Spec
- Anomaly/Crisis Manager Spec
- Local Theory Builder Spec

## Path B — Move closer to implementation
- JSON/Pydantic data schema plan
- module-by-module API contracts
- build order with milestones

### recommendation
أرى أن الخطوة التالية الذكية الآن هي:

# **Virtual_SIA_Data_Schema_Plan_AR.md**

لأننا بعد أن حددنا:
- what modules exist
- what objects matter
- what slice we build

نحتاج تحويل الكيانات الأساسية إلى data schema plan واضحة تمهيدًا لأي implementation clean.

هذا سيكون أول جسر حقيقي جدًا إلى code.
