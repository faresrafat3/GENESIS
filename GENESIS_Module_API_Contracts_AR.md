# Virtual-GENESIS Module API Contracts (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي الجسر الأخير تقريبًا قبل الكود.

بعد أن حددنا:
- النظرية
- الـ ontology
- الـ specs
- prototype slice
- implementation preplan
- data schema plan

نحتاج الآن إلى تحديد:

> من يستدعي من؟
> ما المدخلات والمخرجات؟
> ما الذي sync وما الذي async؟
> ما الذي يُعتبر failure contract؟
> وما أقل runtime path يمكن أن نعتبره coherent؟

هذه الوثيقة لا تصف networking أو framework محدد بالضرورة، بل **عقود modules**.

---

# 1) المبدأ المركزي
كل module في النظام يجب أن تُفهم كـ:
- خدمة معرفية أو تشغيلية
- لها contract واضح
- تقرأ من state أو objects محددة
- وتنتج outputs منظمة
- ويمكن فشلها بطرق معروفة

إذا لم نحدد ذلك الآن، فسنقع سريعًا في:
- hidden coupling
- prompt-state leakage
- fragile orchestration
- untraceable failures

---

# 2) قائمة الموديولات المشمولة في Prototype 1
نركز فقط على ما يخدم Prototype Slice الحالية:

1. `task_ingress`
2. `blackboard_core`
3. `memory_os`
4. `reasoning_runtime`
5. `verification_runtime`
6. `concept_engine`
7. `economy_control`
8. `evaluation_harness`

نترك modules أخرى المستقبلية (anomaly manager, theory builder, etc.) خارج العقود الحالية إلا حيث تظهر future hooks.

---

# 3) أنماط العقود العامة
نقترح ثلاث فئات من API contracts:

## Contract Type A — Query contracts
قراءة أو استعلام دون تغيير كبير في state.

## Contract Type B — Update contracts
تغيير object أو state أو blackboard أو memory.

## Contract Type C — Run/Evaluate contracts
تشغيل عملية أكبر قد تنتج عدة objects أو reports.

---

# 4) Module: task_ingress
## الدور
استقبال المهمة وتحويلها إلى TaskObject أولي.

## Primary contracts
### `ingest_task(raw_input, optional_context) -> TaskObject`
#### inputs
- raw_input: text / structured payload
- optional_context: history refs / files / metadata

#### outputs
- TaskObject

#### failure modes
- unsupported input type
- empty or malformed task
- context too ambiguous to classify

#### notes
إذا فشل التصنيف الدقيق، يجب أن يخرج task_family = `unknown` بدل crash.

### `estimate_task_properties(task: TaskObject) -> TaskObject`
#### effects
- fills difficulty_estimate
- criticality_level
- failure_cost_class
- success_criteria template

---

# 5) Module: blackboard_core
## الدور
إدارة Task Blackboard lifecycle والـ snapshots.

## Primary contracts
### `create_blackboard(task: TaskObject) -> BlackboardObject`
#### outputs
- initialized blackboard with task core set

### `update_blackboard(blackboard_id, section_name, payload) -> BlackboardObject`
#### inputs
- section_name must be valid
- payload must match section schema or accepted update shape

#### failure modes
- invalid section
- invalid payload
- blackboard not found

### `get_blackboard(blackboard_id) -> BlackboardObject`

### `snapshot_blackboard(blackboard_id, phase, reason) -> BlackboardSnapshot`

### `close_blackboard(blackboard_id, outcome_summary) -> BlackboardObject`

#### invariants
- snapshots are append-only
- updates must preserve typed structure
- high-impact updates should include provenance

---

# 6) Module: memory_os
## الدور
إدارة lifecycle الذاكرة retrieval/store/consolidation/forgetting.

## Primary contracts
### `store_memory(unit: MemoryUnit) -> MemoryUnit`
#### failure modes
- invalid memory type
- missing required provenance
- missing summary

### `retrieve_memory(query, mode, budget) -> BlackboardMemoryPack`
#### query includes
- task_family
- uncertainty hints
- objective
- risk flags

#### outputs
- layered memory pack

#### failure modes
- no relevant memory found (should return empty pack, not crash)
- invalid retrieval mode

### `update_memory(memory_id, patch) -> MemoryUnit`

### `archive_memory(memory_id, reason) -> MemoryUnit`

### `deprecate_memory(memory_id, reason) -> MemoryUnit`

### `generate_memory_report(scope) -> MemoryReport`

#### notes
for Prototype 1, consolidate_memory can be internal/periodic and not exposed broadly yet.

---

# 7) Module: reasoning_runtime
## الدور
تنفيذ reasoning path الأساسي داخل المهمة.

## Primary contracts
### `run_reasoning(task, blackboard, memory_pack, tier_decision) -> ReasoningResult`

#### inputs
- TaskObject
- BlackboardObject
- BlackboardMemoryPack
- TierDecisionObject

#### outputs
- candidate claims
- optional arguments
- reasoning metadata
- cost profile

#### failure modes
- provider/model failure
- malformed structured output
- timeout
- insufficient context

#### retry policy
ليس داخل هذا contract مباشرة، بل governed by economy_control.

### `generate_candidate_claims(...) -> list[ClaimObject]`

### `attach_reasoning_to_blackboard(...) -> BlackboardObject`

#### note
في Prototype 1، reasoning topology تكون بسيطة:
- linear default
- optional self-consistency later

---

# 8) Module: verification_runtime
## الدور
تشغيل checks الأساسية على candidate claims/output.

## Primary contracts
### `verify_output(task, blackboard, candidate_output) -> VerificationState`

#### outputs may include
- schema_checks
- evidence_checks
- rule_checks
- optional judge results
- disagreement markers
- verification summary

#### failure modes
- verifier unavailable
- unverifiable output form
- unsupported task family rule set

### `record_verification(blackboard_id, verification_state) -> BlackboardObject`

### `is_good_enough(verification_state) -> bool`

#### note
`is_good_enough` should be policy-aware لاحقًا، لكن يمكن أن تبدأ heuristic.

---

# 9) Module: economy_control
## الدور
اختيار tier والتصعيد وتسجيل الاقتصاد الإدراكي.

## Primary contracts
### `choose_tier(task, blackboard, memory_pack) -> TierDecisionObject`

#### outputs
- chosen tier
- reason
- trigger refs
- expected gains/costs
- fallback

### `should_escalate(task, blackboard, verification_state, current_tier) -> EscalationDecision`

#### outputs
- yes/no
- target tier if yes
- why
- expected value

### `record_cognitive_spend(entry: LedgerEntry) -> LedgerEntry`

### `generate_economy_report(scope) -> EconomyReport`

#### failure modes
- insufficient signals to estimate value
- missing cost profile from previous step

#### rule
if insufficient signals, must return conservative or abstaining decision, not hidden escalation.

---

# 10) Module: concept_engine
## الدور
تشغيل concept formation periodic أو on-demand محدود.

## Primary contracts
### `propose_concepts(episode_refs or cluster) -> list[ConceptCandidate]`

### `contrastive_concept_search(success_refs, failure_refs) -> list[ConceptCandidate]`

### `draft_scope(candidate: ConceptCandidate) -> ConceptCandidate`

### `search_counterexamples(candidate: ConceptCandidate) -> CounterexampleReport`

### `promote_concept(candidate_id) -> ConceptCard | PromotionFailure`

### `demote_to_heuristic(candidate_id) -> HeuristicObject | None`

#### failure modes
- insufficient contrastive evidence
- candidate too vague / no operational meaning
- no scope clarity

#### note
في Prototype 1 يمكن أن تكون بعض هذه العمليات batch-level لا task-level.

---

# 11) Module: evaluation_harness
## الدور
تشغيل conditions/baselines على task sets وإخراج مقارنة.

## Primary contracts
### `run_condition(condition_id, task_set_ref) -> EvaluationRunResult`

### `compare_conditions(condition_ids, task_set_ref) -> ComparisonReport`

### `generate_concept_utility_report(run_refs) -> ConceptUtilityReport`

### `generate_premium_roi_report(run_refs) -> PremiumROIReport`

### `generate_summary_dashboard(run_refs) -> EvaluationSummary`

#### failure modes
- missing logs
- invalid condition definition
- mismatched task family configuration

---

# 12) Supporting contract objects
نحتاج objects مساعدة لبعض العقود:

## 12.1 ReasoningResult
- candidate_claims
- argument_refs (optional)
- cost_profile
- notes

## 12.2 EscalationDecision
- escalate: bool
- target_tier: str | None
- reason: str
- expected_value: float | None
- blockers: list[str]

## 12.3 PromotionFailure
- candidate_id
- failure_reason
- suggested_action

## 12.4 CounterexampleReport
- candidate_id
- counterexample_refs
- severity
- recommendation

## 12.5 EvaluationRunResult
- run_id
- condition_id
- task_set_ref
- task_results
- aggregate_metrics

---

# 13) Orchestration sequence — minimal runtime path
نحدد أقل path coherent للتشغيل:

1. `task_ingress.ingest_task`
2. `task_ingress.estimate_task_properties`
3. `blackboard_core.create_blackboard`
4. `memory_os.retrieve_memory`
5. `economy_control.choose_tier`
6. `reasoning_runtime.run_reasoning`
7. `verification_runtime.verify_output`
8. `blackboard_core.snapshot_blackboard` (before escalation if needed)
9. `economy_control.should_escalate`
10. if escalate → back to reasoning_runtime with new tier
11. finalize output
12. `economy_control.record_cognitive_spend`
13. `memory_os.store_memory` (episode summary, relevant memories)
14. periodic `concept_engine.propose_concepts`
15. optional `concept_engine.promote_concept`

هذا هو أول backbone قابل للتنفيذ فعلاً.

---

# 14) Sync vs Async boundaries
لكي لا يختلط علينا التنفيذ:

## synchronous in Prototype 1
- task_ingress
- create/update blackboard
- retrieve memory
- choose tier
- run reasoning
- verify output
- finalize task result

## asynchronous or periodic in Prototype 1
- concept proposal over accumulated episodes
- memory reports
- economy reports
- concept utility reports
- premium ROI reports

### السبب
نريد runtime path بسيطة، وننقل التحليل الثقيل إلى batch-level.

---

# 15) Failure contracts العامة
كل module يجب أن تتبع ثلاث قواعد:

## Failure Rule 1 — Fail typed
أي failure يجب أن تعود object أو status منظم، لا مجرد نص حر.

## Failure Rule 2 — Fail with provenance
إذا فشلت step، نعرف أين ولماذا.

## Failure Rule 3 — Fail degradably where possible
بدل crash التام:
- empty memory pack
- unknown task family
- verification unavailable → limited path
- concept promotion fail → keep as candidate/heuristic

---

# 16) Cross-module invariants

## Invariant A
أي Decision high-impact يجب أن تشير إلى BlackboardSnapshot أو state ref.

## Invariant B
أي retrieval تدخل في reasoning يجب أن تسجل retrieval rationale ولو مختصر.

## Invariant C
أي escalation يجب أن تنتج TierDecisionObject أو EscalationDecision object.

## Invariant D
أي promoted concept يجب أن يكون لها scope + operational meaning + supporting refs.

## Invariant E
أي stored memory يجب أن تملك provenance and ownership.

## Invariant F
أي evaluation comparison يجب أن تعرف conditions بوضوح.

---

# 17) ما الذي يُسمح أن يبقى heuristic داخل العقود؟
ليس كل شيء يحتاج exact scoring في البداية.

## allowed heuristic zones
- difficulty estimation
- expected gain estimates
- escalation thresholds
- concept candidate scoring
- good_enough verification threshold

### لكن
شكل الـ object والعقد يجب أن يكون ثابتًا حتى لو كانت القيم heuristic.

---

# 18) ما الوثيقة التالية؟
الآن بعد:
- Data Schema Plan
- Module API Contracts

يمكن الانتقال إلى أحد طريقين:

## Path A — Milestone Execution Plan
خطة زمنية مرتبة للبناء sprint by sprint

## Path B — Start implementation artifacts
مثلاً كتابة skeleton JSON/Pydantic models فعليًا

### recommendation
الخطوة الأذكى قبل الكود الكامل هي:

# **Virtual_SIA_Milestone_Execution_Plan_AR.md**

لأنها ستحدد:
- ما الذي نبنيه في Milestone 1
- ما الذي بعده
- what counts as done
- وما deliverables كل مرحلة

وبعدها يصبح الدخول في الكود منظمًا جدًا.
