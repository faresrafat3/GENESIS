# Virtual-GENESIS Build Checklist (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي آخر مستوى تنظيمي قبل الدخول شبه المباشر إلى الكود.

هي لا تشرح النظرية، ولا تعيد specs، بل تترجم كل ما سبق إلى:
- checklist تنفيذية
- شروط صغيرة وواضحة
- ملفات/مكونات يجب أن توجد
- اختبارات سريعة قبل الانتقال للخطوة التالية

الهدف منها هو منع:
- التشتت أثناء البناء
- نسيان dependencies
- بناء أشياء غير مرتبطة بالميلستون الحالية
- وتجاوز مراحل قبل أن تكون جاهزة فعلًا

---

# 1) قواعد استخدام الـ checklist

## Rule 1
لا نبدأ milestone جديدة قبل أن تتحقق شروط done للميلستون السابقة.

## Rule 2
أي بند لا يخدم Thesis 1 أو 2 أو يدعم attribution واضح يُؤجل.

## Rule 3
كل item في الـ checklist يجب أن يكون observable:
- file exists
- object validates
- function runs
- report generated

## Rule 4
لا نعتبر “الفكرة موجودة” بديلاً عن artifact موجودة.

---

# 2) Milestone 0 Checklist — Workspace & Object Skeleton

## M0.1 Project Structure
- [ ] إنشاء بنية مجلدات واضحة (`core`, `runtime`, `eval`, `configs`, `docs`)
- [ ] تثبيت naming convention موحدة
- [ ] تحديد مكان specs والـ theory docs بالنسبة للكود

## M0.2 Base Schemas
- [ ] BaseObject schema
- [ ] Provenance schema
- [ ] Scope schema
- [ ] ConfidenceProfile schema
- [ ] CostProfile schema

## M0.3 Core Object Skeletons
- [ ] TaskObject skeleton
- [ ] BlackboardObject skeleton
- [ ] MemoryUnit skeleton
- [ ] ConceptCandidate skeleton
- [ ] ConceptCard skeleton
- [ ] TierDecisionObject skeleton
- [ ] LedgerEntry skeleton
- [ ] EvaluationResult skeleton

## M0.4 Validation sanity checks
- [ ] يمكن إنشاء instance valid لكل object
- [ ] IDs mandatory
- [ ] provenance fields موجودة
- [ ] serialization إلى JSON works
- [ ] roundtrip parse → serialize → parse works

## M0 Gate
### Stop if:
- [ ] أي object critical ما زال تعريفه غامض
- [ ] serialization fails repeatedly

### Go if:
- [ ] كل object critical يمكن إنشاؤه والتحقق منه بنجاح

---

# 3) Milestone 1 Checklist — Blackboard + Task Flow Minimal

## M1.1 Task ingress
- [ ] وظيفة ingest_task موجودة
- [ ] normalize_task موجودة
- [ ] difficulty/criticality heuristics موجودة
- [ ] success criteria template generation موجودة

## M1.2 Blackboard creation
- [ ] create_blackboard يعمل
- [ ] sections الأساسية موجودة
- [ ] update_blackboard يعمل بطريقة typed
- [ ] get_blackboard works

## M1.3 Blackboard snapshots
- [ ] snapshot_blackboard يعمل
- [ ] snapshot object محفوظ وقابل للاسترجاع
- [ ] reason/phase موجودان في snapshot

## M1.4 Minimal flow sanity
- [ ] task خام تتحول إلى TaskObject
- [ ] TaskObject تتحول إلى Blackboard initialized
- [ ] يمكن كتابة Context Snapshot وSituation Model

## M1 Gate
### Stop if:
- [ ] blackboard تتحول إلى dump نصي غير typed
- [ ] updates غير auditable
- [ ] snapshots غير واضحة أو useless

### Go if:
- [ ] يمكن تمثيل task واحدة بالكامل على blackboard مع snapshot نظيفة

---

# 4) Milestone 2 Checklist — Memory OS Minimal

## M2.1 Memory storage
- [ ] store_memory works
- [ ] status values handled correctly
- [ ] ownership موجودة
- [ ] utility/salience placeholders موجودة

## M2.2 Retrieval
- [ ] retrieve_memory(query, mode, budget) يعمل
- [ ] memory pack returns typed refs
- [ ] empty retrieval لا يسبب crash
- [ ] retrieval rationale يسجل

## M2.3 Memory states
- [ ] active → archived transition supported
- [ ] active → deprecated transition supported
- [ ] contested status supported minimally

## M2.4 Blackboard integration
- [ ] blackboard memory pack section populated
- [ ] task flow يمكنه استخدام retrieved memories

## M2.5 Sanity examples
- [ ] تخزين success episode كـ episodic memory
- [ ] تخزين anti-pattern كـ negative memory
- [ ] تخزين procedure placeholder كـ procedural memory

## M2 Gate
### Stop if:
- [ ] retrieval مجرد dump بلا typing/rationale
- [ ] ownership/provenance ignored

### Go if:
- [ ] Baseline retrieval-only path أصبح runnable

---

# 5) Milestone 3 Checklist — Reasoning + Verification Baselines

## M3.1 Reasoning runtime
- [ ] run_reasoning works with no memory
- [ ] run_reasoning works with memory pack
- [ ] candidate claims generated in structured form
- [ ] reasoning cost profile captured

## M3.2 Verification runtime
- [ ] schema check works
- [ ] evidence sufficiency check works (even heuristic)
- [ ] task-family rule check works minimally
- [ ] verification summary object produced

## M3.3 End-to-end baseline runs
- [ ] Baseline 0 runnable
- [ ] Baseline 1 runnable
- [ ] Baseline 2 runnable (if premium API configured)
- [ ] Baseline 3 runnable

## M3.4 Episode persistence
- [ ] after run, episode summary stored
- [ ] blackboard final snapshot stored
- [ ] result object recorded

## M3 Gate
### Stop if:
- [ ] outputs غير مربوطة بالقرارات والـ blackboard
- [ ] verification opaque

### Go if:
- [ ] 10–20 tasks يمكن تشغيلها end-to-end على الأقل تحت baseline conditions

---

# 6) Milestone 4 Checklist — Concept Formation Minimal

## M4.1 Data preparation
- [ ] success/failure episode grouping available
- [ ] contrastive selection working minimally
- [ ] pattern extraction stub available

## M4.2 Concept proposal
- [ ] propose_concepts يعمل
- [ ] ConceptCandidate objects valid
- [ ] short_definition / operational meaning موجودان

## M4.3 Scope drafting
- [ ] positive scope generated
- [ ] negative scope generated
- [ ] ambiguity zone optional but supported

## M4.4 Promotion path
- [ ] promote_concept works minimally
- [ ] demote_to_heuristic supported
- [ ] concept registry stores validated concepts

## M4.5 Use in future tasks
- [ ] at least one concept gets activated in later task
- [ ] concept affects retrieval or routing or skill choice

## M4.6 Reports
- [ ] concept utility report basic version exists

## M4 Gate
### Stop if:
- [ ] concepts are just renamed summaries
- [ ] concepts never affect runtime behavior

### Go if:
- [ ] Condition A concept-aware can be run meaningfully

---

# 7) Milestone 5 Checklist — Cognitive Economy + Tier Routing

## M5.1 Tier Router
- [ ] choose_tier works
- [ ] chosen tier written as TierDecisionObject
- [ ] trigger refs recorded

## M5.2 Escalation
- [ ] should_escalate works minimally
- [ ] one-step escalation supported
- [ ] fallback path defined

## M5.3 Ledger
- [ ] record_cognitive_spend works
- [ ] LedgerEntry captures estimate vs actual minimally
- [ ] cognitive action types distinguish retrieval / reasoning / escalation / verification / learning

## M5.4 Reports
- [ ] task cost profile report
- [ ] premium ROI report basic
- [ ] escalation explainability report basic

## M5.5 Runtime behavior
- [ ] economy-aware route differs from fixed route on at least some tasks
- [ ] premium escalation not always-on
- [ ] no silent escalation

## M5 Gate
### Stop if:
- [ ] router behaves like prestige bias or random switching
- [ ] ledger exists but gives no interpretable value

### Go if:
- [ ] Condition B and C become runnable and distinguishable

---

# 8) Milestone 6 Checklist — Minimal Comparative Evaluation

## M6.1 Evaluation harness
- [ ] run_condition works
- [ ] compare_conditions works
- [ ] aggregate metrics computed
- [ ] family-wise grouping exists

## M6.2 Run all target conditions
- [ ] Baseline 0
- [ ] Baseline 1
- [ ] Baseline 2
- [ ] Baseline 3
- [ ] Condition A
- [ ] Condition B
- [ ] Condition C

## M6.3 Reports
- [ ] summary table by condition
- [ ] cost-quality comparison
- [ ] concept utility report
- [ ] premium ROI report
- [ ] at least 3 qualitative cases documented

## M6.4 Thesis interpretation
- [ ] preliminary verdict for Thesis 1 written
- [ ] preliminary verdict for Thesis 2 written
- [ ] confounds noted explicitly

## M6 Gate
### Stop if:
- [ ] conditions cannot be separated causally
- [ ] logs insufficient for interpretation
- [ ] baselines inconsistent

### Go if:
- [ ] we have first real evidence memo

---

# 9) Cross-cutting build hygiene checklist

## Traceability
- [ ] every important object has ID
- [ ] every important update has provenance
- [ ] every important decision references blackboard snapshot or state

## Versioning
- [ ] concepts versioned
- [ ] skills versioned
- [ ] policies versioned

## Minimality
- [ ] no unnecessary module added early
- [ ] no premature committee support
- [ ] no premature identity governance runtime

## Evaluation discipline
- [ ] holdout not used in concept extraction
- [ ] same-model controls used where needed
- [ ] premium gains not confused with theory gains

---

# 10) What not to do checklist
- [ ] لا نضيف Local Theory Builder قبل انتهاء M6
- [ ] لا نضيف full anomaly manager قبل evidence أولية
- [ ] لا نضيف self-benchmark generator الآن
- [ ] لا ننقل state الحرجة داخل prompts بدل objects
- [ ] لا نعتبر artifact موجودة نجاحًا إذا لم تؤثر فعليًا على decisions
- [ ] لا نُوسع task families قبل تشغيل الشريحة الأولى جيدًا

---

# 11) Deliverable package after M6
إذا انتهينا من M6 بنجاح، يجب أن نملك package واضحة:

1. runnable prototype slice
2. evaluation results
3. concept utility evidence
4. premium ROI evidence
5. causal case studies
6. prioritized next-step decision:
   - proceed to contradiction/anomaly/theory builder
   - or revise Thesis 1/2 assumptions

---

# 12) القرار التالي بعد هذه الـ checklist
بعد هذه الوثيقة، نكون فعليًا وصلنا إلى آخر محطة تنظيمية قبل التنفيذ المباشر.

الخطوة التالية المنطقية ليست وثيقة عامة جديدة، بل أحد خيارين:

## Option A — Start implementation
والبدء فعليًا من Milestone 0 skeleton ثم M1

## Option B — very small execution companion
وثيقة مساعدة صغيرة جدًا مثل:
`Virtual_SIA_First_Implementation_Order_AR.md`
تترجم M0/M1 إلى:
- file-by-file order
- object-by-object order

### رأيي الصريح
إذا أردنا البقاء عقلانيين، فأنا أرى أن:

> **الوثائق أصبحت كافية جدًا**

والأفضل الآن هو **البدء الفعلي في التنفيذ** بدل مزيد من التوثيق.

لكن لو أردنا آخر ورقة تنظيمية دقيقة جدًا قبل الكود، فستكون فقط:

# `Virtual_SIA_First_Implementation_Order_AR.md`

ثم بعدها مباشرة ندخل في البناء.
