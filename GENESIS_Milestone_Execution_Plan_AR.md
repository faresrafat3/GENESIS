# Virtual-GENESIS Milestone Execution Plan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تحوّل:
- النظرية
- الـ ontology
- الـ specs
- الـ prototype slice
- الـ module contracts

إلى:
# **خطة بناء مرحلية**

هي تجيب عن:
1. ما ترتيب التنفيذ؟
2. ما deliverables كل مرحلة؟
3. ما الذي يُعتبر Done؟
4. ما نقاط التوقف/المراجعة؟
5. ما الذي لا يجب أن يدخل مبكرًا؟
6. متى نكون جاهزين لأول تجربة end-to-end؟

الوثيقة لا تفترض team كبيرة أو infra معقدة. هي صالحة حتى لو كان البناء سيتم تدريجيًا وبمجهود محدود.

---

# 1) مبدأ التنفيذ المرحلي
نحن لا نبني “النظام” ثم نقيّمه.
بل نبني:

> **أصغر طبقة مفيدة**
> ثم نختبرها
> ثم نضيف طبقة ثانية
> ثم نختبرها

هذا مهم لسببين:
1. نحافظ على القدرة على العزو attribution
2. نمنع scope creep والـ hidden complexity

---

# 2) المسار العام
نقترح 6 milestones فقط في النسخة الحالية:

## Milestone 0 — Workspace & Object Skeleton
## Milestone 1 — Blackboard + Task Flow Minimal
## Milestone 2 — Memory OS Minimal
## Milestone 3 — Reasoning + Verification Baselines
## Milestone 4 — Concept Formation Minimal
## Milestone 5 — Cognitive Economy + Tier Routing
## Milestone 6 — Minimal Comparative Evaluation

### ملاحظة
يمكن اعتبار Milestone 0 تحضيرية وسريعة.
أما أول “نظام حي” فعليًا فسيظهر مع Milestone 3.

---

# 3) Milestone 0 — Workspace & Object Skeleton
## الهدف
إنشاء الهيكل الأساسي للبيانات والمجلدات والعقود الدنيا قبل أي منطق تشغيلي.

## Deliverables
1. project directory layout
2. core objects skeletons
3. shared enums / statuses
4. provenance / scope / cost helper schemas
5. config stubs for tiers and task families

## Required objects
- TaskObject
- BlackboardObject
- BlackboardSnapshot
- MemoryUnit
- ConceptCandidate
- ConceptCard
- TierDecisionObject
- LedgerEntry
- EvaluationResult (minimal)

## Done criteria
- كل object يمكن إنشاؤه serializably
- كل object له IDs واضحة
- كل object يمر validation أساسي
- folder layout ثابت ومفهوم

## Stop/Go Check
### Stop if:
- schemas نفسها غير مستقرة
- أو metadata/provenance design ما زال مبهمًا

### Go when:
- يمكن عمل serialization/roundtrip clean
- ويمكن بناء examples objects يدويًا لكل نوع

---

# 4) Milestone 1 — Blackboard + Task Flow Minimal
## الهدف
بناء أول flow task-local منظم.

## What gets built
### Modules
- task_ingress
- blackboard_core

### Runtime path
- ingest task
- normalize task
- estimate basic properties
- create blackboard
- update sections الأساسية
- create snapshots

## Blackboard scope in this milestone
نفعّل فقط:
- Task Core
- Context Snapshot
- Situation Model
- Decisions & Actions (minimal)
- Outcome & Learning Hooks (minimal placeholders)

## Deliverables
1. task ingestion flow
2. blackboard create/update/read
3. snapshot mechanism
4. sample task run with no memory and no reasoning integration yet

## Done criteria
- task can enter system and produce blackboard cleanly
- blackboard sections validate
- snapshots can be created and stored
- no hidden state outside explicit objects for this slice

## Stop/Go Check
### Stop if:
- blackboard becomes dumpy or too prose-heavy
- snapshot semantics still unclear

### Go when:
- one task can be represented fully inside blackboard
- manual inspection shows traceability good enough

---

# 5) Milestone 2 — Memory OS Minimal
## الهدف
إدخال persistent memory بطريقة بسيطة لكن حقيقية.

## What gets built
### Modules
- memory_store
- memory_retriever
- memory_forgetting (minimal)
- memory_report stub

## Layers activated
- WorkingMemory
- EpisodicMemory
- SemanticMemory
- ProceduralMemory (placeholder allowed)
- NegativeMemory

## Deliverables
1. store_memory
2. retrieve_memory
3. archive/deprecate minimal actions
4. blackboard memory pack injection
5. memory pack summary generation

## Special constraints
- no fancy vector infra required in first pass if unnecessary
- simple retrieval acceptable, but must be typed and auditable
- provenance mandatory

## Done criteria
- can store episode summaries as MemoryUnits
- can retrieve by task family / objective basic rules
- blackboard receives memory pack references
- forgetting action works for at least active → archived/deprecated minimal transitions

## Stop/Go Check
### Stop if:
- retrieval is blob dumping
- or memory ownership/status fields are ignored

### Go when:
- Baseline 1 becomes runnable: retrieval-only memory path exists

---

# 6) Milestone 3 — Reasoning + Verification Baselines
## الهدف
امتلاك أول نظام end-to-end يجيب ويُتحقق منه ويترك traces منظمة.

## What gets built
### Modules
- reasoning_runtime
- verification_runtime
- minimal answer finalizer

## Supported conditions at this stage
- Baseline 0 — no memory/stateless
- Baseline 1 — retrieval-only memory
- Baseline 2 — premium-always (if API available)
- Baseline 3 — fixed cheap policy

## Deliverables
1. run_reasoning
2. verify_output
3. good_enough heuristic
4. task result object
5. per-task cost/latency capture
6. store episode after each run

## Done criteria
- one task can run end-to-end from input to validated output
- blackboard contains claims + verification summary + decisions
- cost and latency recorded
- episode summary stored in Memory OS

## Stop/Go Check
### Stop if:
- outputs are not recoverably linked to decisions
- verification cannot be mapped back to task state

### Go when:
- 10–20 tasks can run reproducibly under baselines

---

# 7) Milestone 4 — Concept Formation Minimal
## الهدف
إعطاء النظام أول قدرة حقيقية على تجاوز retrieval-only.

## What gets built
### Modules
- contrastive_selector
- pattern_extractor
- concept_proposer
- scope_drafter
- promote/demote minimal logic
- concept_registry

## Operating mode
- batch-level or periodic, not fully online first
- runs over accumulated episodes from Milestone 3

## Deliverables
1. concept candidate generation from success/failure sets
2. concept cards persisted
3. concept activation hooks into retrieval or routing
4. concept utility report minimal

## Done criteria
- produce at least a handful of interpretable concept candidates
- validate or demote some of them
- show at least one case where concept affects future run

## Stop/Go Check
### Stop if:
- concepts are only renamed summaries
- or none of them affect any decision path

### Go when:
- Condition A (concept-aware) becomes runnable

---

# 8) Milestone 5 — Cognitive Economy + Tier Routing
## الهدف
اختبار هل cognition allocation تحسن الأداء/الكلفة فعلًا.

## What gets built
### Modules
- tier_router
- escalation_engine
- cognitive_ledger
- economy_reports

## Scope
- Tier 0 / Tier 1 / Tier 2 only
- no committee yet
- one-step escalation enough in first pass

## Deliverables
1. choose_tier
2. should_escalate
3. record_cognitive_spend
4. escalation explainability
5. premium ROI and task cost reports

## Done criteria
- routing decisions are explicit and logged
- premium escalation can happen and be audited
- economy reports summarize where cognition was spent
- Condition B and C become runnable

## Stop/Go Check
### Stop if:
- routing behaves like random or prestige bias
- ledger exists but has no explanatory use

### Go when:
- we can compare fixed vs economy-aware conditions on same tasks

---

# 9) Milestone 6 — Minimal Comparative Evaluation
## الهدف
الحصول على أول evidence حقيقية للفريضتين.

## What gets built
### Modules
- evaluation_harness runners
- condition config layer
- metrics aggregation
- family-wise reporting
- concept utility report
- premium ROI report

## Conditions to run
- Baseline 0
- Baseline 1
- Baseline 2
- Baseline 3
- Condition A (concept-aware)
- Condition B (economy-aware)
- Condition C (combined)

## Deliverables
1. run all conditions on minimal task set
2. compare metrics
3. produce qualitative cases
4. produce verdict memo for Thesis 1 and 2

## Done criteria
- complete run over minimal dataset
- tables and plots (or summaries) available
- at least 3–5 qualitative cases with causal interpretation
- clear statement: evidence for / against each thesis so far

## Stop/Go Check
### Stop if:
- conditions not separable
- baselines inconsistent
- logging insufficient for attribution

### Go when:
- we have first reliable memo of empirical evidence

---

# 10) ترتيب التنفيذ الزمني المفضل
لا نربط ذلك بأسابيع صلبة، لكن بالمنطق:

## Sequence
M0 → M1 → M2 → M3 → M4 → M5 → M6

### Important rule
لا ننتقل milestone كاملة قبل أن تنجح السابقة وفق Done criteria.

### Exception
يمكن بدء بعض scaffolding لميلستون لاحقة أثناء الانتظار، لكن دون full expansion.

---

# 11) ما الذي يُعتبر أول “نجاح حقيقي” للمشروع؟
ليس نجاحًا أن نملك docs كثيرة.
وليس نجاحًا أن نملك codebase نظيفة فقط.

## First real success
هو أن نصل إلى M6 ونخرج memo يقول مثلًا:
- concept-aware path reduced raw episodic retrieval and improved transfer on Family B/C by X
- economy-aware path matched or approached premium-always quality with lower cost by Y

أي:
# **أول نجاح حقيقي = أول evidence منضبطة لصالح Thesis 1 أو 2**

---

# 12) ما الذي نفعله لو فشل M6؟
هذه نقطة مهمة جدًا.

## Failure branch A
إذا فشلت Thesis 1:
- نراجع concept candidate quality
- نراجع scope drafting
- نراجع whether tasks actually contain reusable abstraction structure

## Failure branch B
إذا فشلت Thesis 2:
- نراجع triggers and brakes
- نراجع whether budget modeling too crude
- نراجع whether task set too easy أو too hard لإظهار الفرق

## Failure branch C
إذا فشل كل شيء:
- نعود إلى prototype slice assumptions
- لا نبرر النتائج قسرًا

الفشل هنا informative وليس catastrophic.

---

# 13) آلية إدارة المخاطر أثناء التنفيذ

## Risk 1 — Scope creep
### mitigation
كل feature جديدة يجب أن تربط بميلستون محددة وthesis واضحة.

## Risk 2 — Hidden coupling
### mitigation
respect module contracts strictly.

## Risk 3 — Data chaos
### mitigation
use schema-first discipline before behavior-first hacks.

## Risk 4 — Premature optimization
### mitigation
keep heuristics simple until M6 evidence exists.

## Risk 5 — Theory abandonment due to implementation friction
### mitigation
always tie implementation artifact to one explicit theoretical claim.

---

# 14) ما الذي يمكن إضافته فقط بعد M6؟
بعد أول evidence، يمكننا تبرير إضافة:
- Contradiction Ledger full
- Anomaly/Crisis Manager
- Local Theory Builder
- Sparse committee
- Self-benchmarking engine
- Identity governance runtime

### القاعدة
لا تضفها قبل وجود empirical justification or pressing need.

---

# 15) القرار التنفيذي النهائي
الآن بعد هذه الوثيقة، أصبح عندنا:
- ما سنبنيه
- بأي ترتيب
- وما معنى done
- وما نقطة أول اختبار حقيقي

إذًا الخطوة التالية المنطقية ليست Spec جديدة أولًا، بل:

# **تحويل هذه الخطة إلى Build Checklist / Task Breakdown**

أي وثيقة عملية جدًا مثل:

## `Virtual_SIA_Build_Checklist_AR.md`

تحتوي على:
- checklist تنفيذية لكل milestone
- الملفات/الموديولات المطلوبة
- الاختبارات الصغيرة المطلوبة
- وما الذي يجب مراجعته قبل الانتقال للميلستون التالية

وهذا سيكون آخر مستوى تنظيمي قبل أن يصبح الدخول في الكود شبه مباشر.
