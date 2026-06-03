# Virtual-GENESIS Data Schema Plan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي أول خطوة عملية جدًا نحو التنفيذ النظيف.

بعد أن حددنا:
- النظرية
- الـ ontology
- الـ specs
- prototype slice
- implementation preplan

نحتاج الآن إلى الإجابة على السؤال:

> كيف ستُمثَّل الكيانات الأساسية في البيانات؟

أي:
- ما الـ schemas الأساسية؟
- ما الحقول الضرورية؟
- ما الذي يجب أن يكون strict؟
- ما الذي يمكن أن يبقى flexible؟
- كيف نربط الكيانات ببعضها؟
- كيف نحافظ على versioning وtraceability؟

هذه الوثيقة ليست كودًا بعد، لكنها blueprint مباشرة لـ:
- Pydantic models
- JSON documents
- database tables/collections
- event logs

---

# 1) المبادئ العامة للـ schemas

## Principle 1 — IDs first
كل object أساسي يجب أن يملك معرفًا ثابتًا وواضحًا.

## Principle 2 — References over duplication
إذا كان object يُستخدم في أكثر من مكان، الأفضل الإشارة إليه reference بدل نسخه نصيًا كل مرة.

## Principle 3 — Typed core, flexible extensions
الحقول المركزية strict، لكن يجب وجود مساحة `meta` أو `extras` لتوسعات لاحقة.

## Principle 4 — Version everything important
أي artifact أو object يُستخدم في الاستدلال أو التقييم أو governance يجب أن يكون versioned.

## Principle 5 — Provenance is mandatory
أي شيء له أثر معرفي أو قراري يجب أن نعرف مصدره.

## Principle 6 — Snapshots are first-class
الـ runtime state المهمة يجب أن يكون لها snapshots قابلة للحفظ والمراجعة.

## Principle 7 — Separation of content and control
لا نخلط بين:
- raw content
- summary
- decision metadata
- provenance
- status/lifecycle

---

# 2) مستويات الـ schema
نقترح أربع طبقات من التمثيل:

## Layer A — Core Object Schemas
- Task
- Blackboard
- MemoryUnit
- Concept
- Skill
- Theory
- Policy
- Decision
- Test
- Identity

## Layer B — Supporting Embedded Schemas
- Provenance
- Scope
- CostProfile
- VerificationSummary
- TriggerSet
- ConfidenceProfile
- LifecycleStatus

## Layer C — Runtime Event Schemas
- RetrievalEvent
- EscalationEvent
- VerificationEvent
- ConceptProposalEvent
- SnapshotEvent

## Layer D — Report Schemas
- TaskRunReport
- PremiumROIReport
- ConceptUtilityReport
- MemoryUtilityReport
- EvaluationSummary

---

# 3) القوالب العامة المشتركة

## 3.1 BaseObject
أي object persistent أو artifact-like يجب أن ترث من BaseObject منطقيًا.

### fields
- `id: str`
- `object_type: str`
- `version: str`
- `created_at: datetime`
- `updated_at: datetime`
- `status: str`
- `provenance: Provenance`
- `meta: dict[str, Any] | None`

---

## 3.2 Provenance
### fields
- `source_kind: str`
  - user
  - model
  - tool
  - verifier
  - memory_consolidation
  - concept_engine
  - human_override
- `source_id: str | None`
- `source_ref: str | None`
- `generated_by_run_id: str | None`
- `timestamp: datetime`
- `notes: str | None`

---

## 3.3 Scope
### fields
- `task_families: list[str]`
- `positive_conditions: list[str]`
- `negative_conditions: list[str]`
- `ambiguity_zone: list[str]`
- `confidence: float | None`

---

## 3.4 ConfidenceProfile
### fields
- `score: float | None`
- `source: str | None`
- `calibration_band: str | None`
- `notes: str | None`

---

## 3.5 CostProfile
### fields
- `prompt_tokens: int | None`
- `completion_tokens: int | None`
- `total_tokens: int | None`
- `latency_ms: int | None`
- `estimated_cost_usd: float | None`
- `premium_share: float | None`

---

# 4) Core Schemas

## 4.1 TaskObject
### purpose
تمثيل المهمة الداخلة للنظام.

### fields
- `task_id: str`
- `raw_text: str`
- `normalized_text: str`
- `task_family: str`
- `subtask_family: str | None`
- `criticality_level: str`
- `difficulty_estimate: str`
- `deadline_class: str | None`
- `success_criteria: list[str]`
- `failure_cost_class: str`
- `input_artifacts: list[str]`
- `context_refs: list[str]`
- `meta: dict | None`

### strict fields
- task_id
- raw_text
- task_family
- criticality_level
- success_criteria

### flexible fields
- subtask_family
- context_refs
- meta

---

## 4.2 BlackboardObject
### purpose
تمثيل الحالة التشغيلية task-local.

### fields
- `blackboard_id: str`
- `task_ref: str`
- `state: str`
- `task_core: BlackboardTaskCore`
- `context_snapshot: BlackboardContextSnapshot`
- `retrieved_memory_pack: BlackboardMemoryPack`
- `situation_model: BlackboardSituationModel`
- `candidate_claims: list[ClaimObject]`
- `arguments: list[ArgumentObject]`
- `deliberation_state: DeliberationState`
- `skill_policy_state: SkillPolicyState`
- `verification_state: VerificationState`
- `contradiction_anomaly_state: ContradictionAnomalyState`
- `decisions: list[DecisionObject]`
- `outcome_learning_hooks: OutcomeLearningHooks`
- `snapshots: list[str]`

### note
بعض sub-schemas يمكن أن تكون embedded objects، لكن snapshots الأفضل أن تكون objects مستقلة references.

---

## 4.3 BlackboardSnapshot
### purpose
حفظ state مجمدة عند نقطة مهمة.

### fields
- `snapshot_id: str`
- `blackboard_ref: str`
- `phase: str`
- `snapshot_time: datetime`
- `serialized_state_ref: str | dict`
- `reason: str`

---

## 4.4 MemoryUnit
### purpose
تمثيل وحدة ذاكرة واحدة typed.

### fields
- `memory_id: str`
- `memory_type: str`
  - working
  - episodic
  - semantic
  - strategic
  - procedural
  - anomaly
  - negative
  - archived
- `content_type: str`
  - episode_summary
  - fact
  - heuristic
  - concept_ref
  - skill_ref
  - theory_ref
  - anomaly_ref
  - anti_pattern
- `content_ref: str | None`
- `summary: str`
- `scope: Scope`
- `utility_score: float | None`
- `staleness_score: float | None`
- `salience: float | None`
- `identity_relevance: str`
- `ownership: str`
- `status: str`
- `linked_objects: list[str]`
- `last_used_at: datetime | None`

### strict fields
- memory_id
- memory_type
- summary
- status

### flexible fields
- utility_score
- salience
- linked_objects

---

## 4.5 ConceptCard
### purpose
تمثيل مفهوم validated أو candidate.

### fields
- `concept_id: str`
- `name: str`
- `definition: str`
- `operational_meaning: str`
- `activation_conditions: list[str]`
- `scope: Scope`
- `supporting_pattern_refs: list[str]`
- `supporting_episode_refs: list[str]`
- `counterexample_refs: list[str]`
- `linked_skill_refs: list[str]`
- `linked_policy_refs: list[str]`
- `confidence_profile: ConfidenceProfile`
- `transfer_score: float | None`
- `promotion_stage: str`

### strict fields
- concept_id
- name
- definition
- operational_meaning
- scope

---

## 4.6 ConceptCandidate
### purpose
نسخة قبل اعتماد المفهوم.

### fields
- `candidate_id: str`
- `proposed_name: str`
- `short_definition: str`
- `contrastive_basis: list[str]`
- `supporting_episode_refs: list[str]`
- `supporting_pattern_refs: list[str]`
- `candidate_scope: Scope`
- `counterexample_refs: list[str]`
- `candidate_value: float | None`
- `recommendation: str`
  - reject
  - keep_as_heuristic
  - validate_as_concept
  - split

---

## 4.7 SkillCapsule
### purpose
تمثيل skill قابلة للتنفيذ.

### fields
- `skill_id: str`
- `name: str`
- `goal: str`
- `trigger_conditions: list[str]`
- `execution_steps: list[str]`
- `required_tools: list[str]`
- `compatible_tiers: list[str]`
- `verifier_recipe: list[str]`
- `failure_signatures: list[str]`
- `maturity_level: str`
- `utility_score: float | None`
- `scope: Scope`
- `lineage_refs: list[str]`
- `status: str`

---

## 4.8 LocalTheoryObject
### purpose
تمثيل نظرية محلية.

### fields
- `theory_id: str`
- `name: str`
- `core_question: str`
- `scope: Scope`
- `concept_refs: list[str]`
- `invariant_refs: list[str]`
- `contradiction_refs: list[str]`
- `mechanism_claims: list[str]`
- `predictive_claims: list[str]`
- `prescriptive_implications: list[str]`
- `counterexample_refs: list[str]`
- `confidence_profile: ConfidenceProfile`
- `transfer_score: float | None`
- `revision_history_refs: list[str]`
- `status: str`

---

## 4.9 ContradictionObject
### purpose
تمثيل تناقض explicit.

### fields
- `contradiction_id: str`
- `type: str`
- `elements_involved: list[str]`
- `shared_context: str | None`
- `incompatibility_reason: str`
- `possible_resolutions: list[str]`
- `severity: float | None`
- `decision_impact: str | None`
- `status: str`

---

## 4.10 AnomalyObject
### purpose
تمثيل anomaly family.

### fields
- `anomaly_id: str`
- `label: str`
- `failure_family: str`
- `affected_subsystems: list[str]`
- `symptoms: list[str]`
- `failed_explanation_refs: list[str]`
- `severity_score: float | None`
- `spread_score: float | None`
- `patch_cost_trend: str | None`
- `recommended_action_class: str | None`
- `status: str`

---

## 4.11 PolicyObject
### purpose
تمثيل policy قابلة للتفعيل والتحديث.

### fields
- `policy_id: str`
- `policy_type: str`
- `conditions: list[str]`
- `action_rule: str`
- `scope: Scope`
- `cost_profile: CostProfile | None`
- `lineage_refs: list[str]`
- `stability: float | None`
- `status: str`

---

## 4.12 DecisionObject
### purpose
تمثيل قرار واحد أثناء runtime.

### fields
- `decision_id: str`
- `decision_type: str`
- `task_ref: str`
- `blackboard_snapshot_ref: str`
- `selected_option: str`
- `used_argument_refs: list[str]`
- `used_policy_refs: list[str]`
- `expected_value: float | None`
- `actual_outcome_summary: str | None`
- `timestamp: datetime`

---

## 4.13 TierDecisionObject
### purpose
قرار tier/escalation explicitly.

### fields
- `tier_decision_id: str`
- `task_ref: str`
- `chosen_tier: str`
- `decision_reason: str`
- `trigger_refs: list[str]`
- `expected_immediate_gain: float | None`
- `expected_reuse_gain: float | None`
- `expected_cost: float | None`
- `expected_delay_penalty: float | None`
- `confidence_in_decision: float | None`
- `fallback_option: str | None`
- `timestamp: datetime`

---

## 4.14 LedgerEntry
### purpose
تمثيل cognitive spend event.

### fields
- `ledger_entry_id: str`
- `task_ref: str`
- `phase: str`
- `cognitive_action_type: str`
- `tier_used: str | None`
- `topology_used: str | None`
- `trigger_refs: list[str]`
- `estimated_immediate_gain: float | None`
- `estimated_reuse_gain: float | None`
- `estimated_learning_gain: float | None`
- `estimated_cost: float | None`
- `estimated_delay_penalty: float | None`
- `estimated_noise_risk: float | None`
- `actual_cost_profile: CostProfile | None`
- `actual_immediate_effect: str | None`
- `actual_reuse_effect: str | None`
- `actual_learning_effect: str | None`
- `would_repeat: bool | None`
- `notes: str | None`

---

## 4.15 TestObject
### purpose
تمثيل benchmark/test case.

### fields
- `test_id: str`
- `test_type: str`
- `target_subsystem: str`
- `setup_ref: str | dict`
- `expected_signal: str`
- `diagnostic_value: float | None`
- `learning_value: float | None`
- `cost_estimate: float | None`
- `linked_anomaly_refs: list[str]`
- `linked_theory_refs: list[str]`
- `status: str`

---

## 4.16 IdentityObject
### purpose
تمثيل الهوية.

### fields
- `identity_id: str`
- `agent_ref: str | None`
- `lineage_id: str`
- `branch_id: str`
- `core_commitments: list[str]`
- `self_theory_refs: list[str]`
- `policy_signature_refs: list[str]`
- `theory_signature_refs: list[str]`
- `identity_defining_memory_refs: list[str]`
- `risk_posture: str`
- `delegation_rules: list[str]`
- `drift_alerts: list[str]`
- `status: str`

---

# 5) Embedded helper schemas المطلوبة
بدل تكرار نفس البنية، نحتاج sub-schemas مثل:

## BlackboardTaskCore
- task_id
- task_family
- criticality_level
- difficulty_estimate
- success_criteria

## BlackboardContextSnapshot
- user_context_summary
- relevant_history_refs
- tool_availability
- constraints

## BlackboardMemoryPack
- episodic_refs
- semantic_refs
- procedural_refs
- negative_refs
- retrieval_rationale
- memory_noise_risk

## BlackboardSituationModel
- knowns
- unknowns
- uncertainties
- assumptions
- missing_information
- candidate_frames

## DeliberationState
- reasoning_topology
- active_branches
- pruned_branches
- branch_instability
- search_budget_remaining

## SkillPolicyState
- active_skills
- candidate_skills
- active_policies
- tier_router_decision_ref
- escalation_status

## VerificationState
- schema_checks
- evidence_checks
- rule_checks
- judge_results
- disagreements
- verification_summary

## ContradictionAnomalyState
- active_contradiction_refs
- anomaly_signal_refs
- crisis_indicator_refs

## OutcomeLearningHooks
- final_output_ref
- task_outcome
- lessons_to_extract
- candidate_concepts
- candidate_skill_updates
- candidate_tests
- candidate_anomalies

---

# 6) العلاقات الرسمية بين الـ schemas

## Core relational rules
- TaskObject **owns** BlackboardObject
- BlackboardObject **references** MemoryUnits, Decisions, Claims, Arguments
- Episodes **generate** MemoryUnits and Reports
- MemoryUnits **support** ConceptCandidates or SkillCapsules
- ConceptCards **influence** retrieval/routing/skill activation
- LocalTheoryObjects **depend_on** ConceptCards and Invariants
- ContradictionObjects **connect** Concepts/Skills/Theories/Policies
- AnomalyObjects **aggregate** Failure Patterns and Contradictions
- TierDecisionObjects **spawn** LedgerEntries
- TestObjects **evaluate** Skills / Concepts / Theories / Policies
- IdentityObjects **govern** memory ownership + policy signature + self-theories

---

# 7) ما الذي يجب أن يكون strict جدًا؟

## Strict entities
1. IDs
2. object_type
3. status
4. provenance
5. task_family
6. chosen_tier when tier decision exists
7. scope presence for Concept/Skill/Theory
8. linked refs for contradictions/anomalies/theories where needed

### لماذا؟
لأن أي تساهل هنا سيدمر traceability وattribution.

---

# 8) ما الذي يمكن أن يكون flexible؟

## Flexible fields
- meta
- notes
- narrative summaries
- optional confidence scores
- early heuristic cost estimates
- extra custom tags

### القاعدة
الـ core formal، والـ edges flexible.

---

# 9) serialization strategy المقترحة
في النسخة الأولى:

## Primary format
- JSON-compatible objects

## Strong model candidate
- Pydantic models لاحقًا في التنفيذ

## References
- string IDs داخل objects
- no deep recursive embedding by default

### لماذا؟
لتفادي:
- object bloat
- serialization nightmares
- duplication

---

# 10) versioning strategy
كل artefact persistent يجب أن تكون versioned.

## version formats possible
- semantic-ish string: `v0.1`, `v0.2`
- or timestamped revision ID

## minimum rule
إذا تغير:
- definition
- scope
- activation logic
- policy semantics

فهذا version bump mandatory.

### applies to
- ConceptCard
- SkillCapsule
- LocalTheoryObject
- PolicyObject
- IdentityObject (at least signatures)
- TestObject

---

# 11) storage strategy المبدئية
بما أننا ما زلنا قبل الكود الكامل، نقترح conceptual separation:

## Store A — Runtime store
للـ blackboards والسnapshots الجارية

## Store B — Memory store
لـ MemoryUnits

## Store C — Knowledge artifact store
لـ Concepts, Skills, Theories, Contradictions, Anomalies, Tests

## Store D — Evaluation store
لـ LedgerEntries, reports, run summaries

## Store E — Identity store
لـ IdentityObjects and lineage artifacts

في التنفيذ قد يكون هذا:
- ملفات JSON
- SQLite/Postgres
- أو hybrid
لكن المفهوم يجب أن يبقى واضحًا الآن.

---

# 12) data flow الرسمي

## Flow 1 — Task run
TaskObject → BlackboardObject → Memory retrieval → TierDecision → Reasoning → Verification → Decision logs → Episode summary

## Flow 2 — Memory growth
Episodes → MemoryUnits → Consolidation → ConceptCandidates / Skills / Negative memories

## Flow 3 — Governance
Contradiction refs + Anomaly refs + Ledger reports → Theory/Policy update later

## Flow 4 — Evaluation
Task runs + conditions → EvaluationResult / Reports

---

# 13) validation rules مبدئية

## Validation Rule A
أي ConceptCard بلا scope invalid.

## Validation Rule B
أي SkillCapsule بلا verifier_recipe invalid.

## Validation Rule C
أي DecisionObject بلا snapshot ref invalid.

## Validation Rule D
أي LedgerEntry بلا action type invalid.

## Validation Rule E
أي AnomalyObject بلا failed explanation أو symptoms invalid.

## Validation Rule F
أي IdentityObject بلا core_commitments invalid.

---

# 14) migration policy المبدئية
لأن النظام سيكبر، نحتاج سياسة migration مبكرة.

## Rule 1
old versions never silently overwritten

## Rule 2
superseded objects remain referenceable

## Rule 3
lineage refs mandatory when splitting/forking concepts, theories, or skills

## Rule 4
identity-defining objects require explicit migration notes

---

# 15) minimum schema subset for first code
إذا أردنا أقل subset للبدء فعلاً، فهي:

1. TaskObject
2. BlackboardObject
3. MemoryUnit
4. ConceptCandidate
5. ConceptCard
6. TierDecisionObject
7. LedgerEntry
8. EvaluationResult (simple report object)

### هذا يكفي لبناء أول prototype slice.

---

# 16) ما التالي بعد هذه الوثيقة؟
الآن بعد أن حددنا الـ data schemas plan، فالخطوة الأكثر منطقية هي واحدة من اثنتين:

## Option A — API Contracts Plan
تحديد interfaces والدوال/الخدمات بين modules

## Option B — Milestone Execution Plan
تحديد sprint-like milestones:
- week 1 objects
- week 2 blackboard
- week 3 memory
- etc.

### رأيي الحالي
الخطوة التالية الذكية جدًا هي:

# **Virtual_SIA_Module_API_Contracts_AR.md**

لأننا بعد أن عرفنا البيانات، يجب أن نعرف:
- من يستدعي من؟
- ما المدخلات والمخرجات؟
- ما الترتيب؟
- ما الذي sync وما الذي async؟

وهذا سيكون آخر جسر نظيف قبل الدخول الفعلي إلى code.
