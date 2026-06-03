# Virtual-GENESIS Core Ontology (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي أول انتقال رسمي من:
- الـ Meta-Theory
إلى:
- **لغة نظام formal** يمكن أن نبني بها specs لاحقًا

هي لا تصف implementation بعد، بل تصف:
1. ما الكيانات الأساسية في النظام؟
2. ما العلاقات بينها؟
3. ما الحالات التي تمر بها؟
4. ما قواعد الترقية/الخفض بينها؟
5. ما القيود invariants التي يجب الحفاظ عليها؟

هذه الوثيقة تمثل **قاموس الوجود** داخل Virtual-GENESIS.

---

# 1) المبادئ الوجودية الكبرى
نقترح أن عالم Virtual-GENESIS يتكون من أربع طبقات من الوجود:

## A. كيانات الخبرة Experience Entities
ما ينتج مباشرة عن التفاعل مع العالم أو المستخدم أو الأدوات.

## B. كيانات المعرفة Knowledge Entities
ما يُستخلص من الخبرة ويُحفظ للاستعمال لاحقًا.

## C. كيانات الحوكمة Governance Entities
ما ينظم القرار، الصراع، النسيان، التصعيد، والمراجعة.

## D. كيانات الهوية والتنمية Identity/Development Entities
ما يحفظ استمرارية الذات، lineages، مسار التحسن، والاختبارات الذاتية.

---

# 2) القاعدة الأساسية للأنطولوجيا
أي شيء داخل النظام لا بد أن يقع ضمن واحد أو أكثر من الأنواع الآتية:

1. **Observation**
2. **Episode**
3. **Memory**
4. **Pattern**
5. **Heuristic**
6. **Concept**
7. **Invariant**
8. **Skill**
9. **Theory**
10. **Argument**
11. **Contradiction**
12. **Anomaly**
13. **Crisis**
14. **Policy**
15. **Benchmark/Test**
16. **Identity**
17. **Agent**
18. **Environment**
19. **Decision**
20. **Artefact**

وفي هذه الوثيقة سنعرّفها واحدة واحدة.

---

# 3) الكيانات الأساسية

## 3.1 Observation
### التعريف
أصغر وحدة أولية ناتجة عن:
- user input
- tool output
- verifier output
- environment state
- model completion fragment

### أمثلة
- نتيجة بحث
- error trace
- ملف JSON مستخرج
- screenshot OCR text
- execution result

### الخصائص الأساسية
- `observation_id`
- `source_type`
- `timestamp`
- `content`
- `modality`
- `provenance`
- `confidence` (إن وُجد)
- `task_context`

### العلاقات
- Observation **belongs_to** Episode
- Observation **supports/challenges** Claim
- Observation **feeds** Pattern Mining

---

## 3.2 Episode
### التعريف
وحدة خبرة كاملة مرتبطة بمحاولة أو مهمة أو subtask.

### تتكون من
- input
- sequence of actions
- retrieved memories
- outputs
- verifier results
- outcome

### الخصائص
- `episode_id`
- `task_id`
- `goal`
- `action_trace`
- `outcome`
- `cost`
- `latency`
- `success_label`
- `episode_scope_tags`

### العلاقات
- Episode **contains** Observations
- Episode **yields** Patterns / Lessons
- Episode **is_referenced_by** Skills, Concepts, Theories

---

## 3.3 Memory
### التعريف
تمثيل محفوظ لشيء من الخبرة أو المعرفة بحيث يمكن استرجاعه لاحقًا.

### الأنواع الفرعية
1. WorkingMemory
2. EpisodicMemory
3. SemanticMemory
4. StrategicMemory
5. ProceduralMemory
6. AnomalyMemory
7. NegativeMemory
8. ArchivedMemory

### الخصائص المشتركة
- `memory_id`
- `memory_type`
- `content_ref`
- `salience`
- `utility_score`
- `staleness_score`
- `scope_tags`
- `ownership`
- `status`
- `created_at`
- `last_used_at`

### الحالات الممكنة
- active
- low_priority
- archived
- deprecated
- contested
- superseded

### العلاقات
- Memory **derived_from** Episode / Concept / Skill / Theory
- Memory **owned_by** Agent Identity
- Memory **queried_by** Retrieval Policy

---

## 3.4 Pattern
### التعريف
انتظام متكرر مستخرج من عدة observations أو episodes لكنه لم يُرقَّ بعد إلى heuristic أو concept.

### الخصائص
- `pattern_id`
- `supporting_episodes`
- `pattern_signature`
- `frequency`
- `confidence`
- `candidate_scope`

### العلاقات
- Pattern **emerges_from** Episodes
- Pattern **may_promote_to** Heuristic أو Concept

---

## 3.5 Heuristic
### التعريف
قاعدة تشغيل تقريبية تساعد على الفعل أو الحكم لكنها لا تزال محدودة أو غير مستقرة بما يكفي لتكون concept أو invariant.

### الخصائص
- `heuristic_id`
- `rule_text`
- `applicable_scope`
- `risk_level`
- `estimated_value`
- `counterexamples`
- `linked_skills`

### الحالات
- candidate
- active
- scoped
- weak
- deprecated

### العلاقات
- Heuristic **derived_from** Patterns / Lessons
- Heuristic **guides** Policy / Skill selection
- Heuristic **may_promote_to** Concept or Invariant

---

## 3.6 Concept
### التعريف
تجريد مضغوط يلتقط انتظامًا له:
- معنى تشغيلي
- شروط استعمال
- scope
- حدود

### الخصائص
- `concept_id`
- `name`
- `definition`
- `operational_meaning`
- `activation_conditions`
- `scope`
- `counterexamples`
- `confidence`
- `transfer_score`
- `linked_skills`
- `linked_theories`

### الحالات
- candidate
- validated
- contested
- revised
- split
- archived

### العلاقات
- Concept **compresses** Patterns / Episodes
- Concept **supports** Theory
- Concept **constrains** Skill activation
- Concept **is_refined_by** Contradictions / Counterexamples

---

## 3.7 Invariant
### التعريف
انتظام عالي الثبات عبر حالات أو domains متعددة نسبيًا.

### الخصائص
- `invariant_id`
- `statement`
- `scope`
- `evidence_base`
- `stability_score`
- `exceptions`

### العلاقات
- Invariant **supports** Local Theory
- Invariant **emerges_from** multiple validated Concepts or repeated Theory confirmations

---

## 3.8 Skill
### التعريف
إجراء أو workflow قابل للتنفيذ لإنتاج سلوك نافع في نوع معين من المهام.

### Skill Capsule fields
- `skill_id`
- `name`
- `goal`
- `trigger_conditions`
- `execution_steps`
- `required_tools`
- `compatible_tiers`
- `verifier_recipe`
- `failure_signatures`
- `maturity_level`
- `utility_score`
- `scope`
- `lineage`

### Skill states
- draft
- candidate
- active
- scoped
- deprecated
- archived
- anti_pattern_reference

### العلاقات
- Skill **operationalizes** Concept / Theory
- Skill **validated_by** Tests
- Skill **selected_by** Policy
- Skill **owned_by** Identity or shared registry

---

## 3.9 Theory
### التعريف
بنية معرفية مترابطة تفسر وتوجه السلوك داخل scope محدد عبر ربط concepts, invariants, contradictions, and implications.

### Local Theory Object fields
- `theory_id`
- `name`
- `core_question`
- `scope`
- `concepts_involved`
- `invariants`
- `contradictions_handled`
- `mechanism_claims`
- `predictive_claims`
- `prescriptive_implications`
- `counterexamples`
- `confidence`
- `transfer_score`
- `revision_history`

### الحالات
- draft
- candidate
- active
- contested
- forked
- superseded
- archived

### العلاقات
- Theory **uses** Concepts and Invariants
- Theory **explains** Failure Families or Task Families
- Theory **recommends** Skills / Policies / Benchmark generation
- Theory **threatened_by** Anomalies

---

## 3.10 Argument
### التعريف
بنية claim-level تُستخدم لتبرير answer أو decision أو theory move.

### fields
- `argument_id`
- `claim`
- `grounds`
- `warrant`
- `backing`
- `qualifier`
- `rebuttal`
- `linked_evidence`
- `confidence`

### العلاقات
- Argument **supports** Decision / Theory / Answer
- Argument **challenged_by** Counterexample or Contradiction

---

## 3.11 Contradiction
### التعريف
وجود عنصرين أو أكثر يقودان إلى استنتاجات أو أفعال أو تقييمات غير قابلة للتوافق المباشر تحت تمثيل مشترك.

### fields
- `contradiction_id`
- `type`
- `elements_involved`
- `shared_context`
- `incompatibility_reason`
- `possible_resolutions`
- `severity`
- `decision_impact`
- `status`

### الحالات
- unresolved
- under_review
- scoped_apart
- merged_by_abstraction
- archived
- escalated_to_anomaly
- escalated_to_crisis

### العلاقات
- Contradiction **involves** Concepts / Skills / Theories / Verifiers / Goals
- Contradiction **may_trigger** Theory refinement or Anomaly creation

---

## 3.12 Anomaly
### التعريف
failure pattern لا تحتويه أو لا تفسره المفاهيم أو النظريات الحالية بصورة كافية.

### fields
- `anomaly_id`
- `label`
- `failure_family`
- `affected_subsystems`
- `symptoms`
- `failed_explanations`
- `severity_score`
- `spread_score`
- `patch_cost_trend`
- `recommended_action_class`

### الحالات
- observed
- clustered
- persistent
- crisis_candidate
- resolved
- archived

### العلاقات
- Anomaly **emerges_from** Failure Patterns and Contradictions
- Anomaly **pressures** Theory / Policy / Paradigm layers
- Anomaly **yields** Benchmarks

---

## 3.13 Crisis
### التعريف
تراكم anomalies مع تآكل coherence أو جدوى الإصلاحات المحلية.

### fields
- `crisis_id`
- `linked_anomalies`
- `affected_layers`
- `why_local_fixes_fail`
- `cost_regression_signature`
- `candidate_forks`
- `fork_decision`

### الحالات
- emerging
- active
- fork_in_progress
- stabilized
- unresolved

### العلاقات
- Crisis **arises_from** persistent Anomalies
- Crisis **may_require** Paradigm Fork

---

## 3.14 Policy
### التعريف
قاعدة حاكمة لاتخاذ قرار تشغيلي أو معرفي.

### الأنواع
- routing policy
- escalation policy
- forgetting policy
- committee policy
- retrieval policy
- verification policy
- skill selection policy

### fields
- `policy_id`
- `policy_type`
- `conditions`
- `action_rule`
- `cost_model`
- `scope`
- `lineage`
- `stability`

### العلاقات
- Policy **governs** Decisions
- Policy **updated_by** Lessons / Theories / Economy reports
- Policy **belongs_to** Policy Signature of Identity

---

## 3.15 Benchmark / Test
### التعريف
وحدة فحص مصممة لقياس capability أو boundary أو anomaly أو theory discrimination.

### fields
- `test_id`
- `test_type`
- `target_subsystem`
- `setup`
- `expected_signal`
- `diagnostic_value`
- `learning_value`
- `cost_estimate`
- `linked_anomalies`
- `linked_theories`

### الحالات
- proposed
- validated
- active
- stale
- deprecated

### العلاقات
- Test **generated_from** Anomaly / Theory / Skill boundary
- Test **evaluates** Skills / Theories / Policies / Identity drift

---

## 3.16 Identity
### التعريف
البنية التي تمنح agent continuity عبر الذاكرة والالتزامات والسياسات والنظريات والمساءلة.

### Identity Object fields
- `identity_id`
- `agent_id`
- `lineage_id`
- `branch_id`
- `core_commitments`
- `self_theories`
- `policy_signature`
- `theory_signature`
- `identity_defining_memories`
- `risk_posture`
- `delegation_rules`
- `drift_alerts`

### العلاقات
- Identity **owns** certain Memories / Policies / Skills
- Identity **persists_across** Episodes
- Identity **forks_into** Branches

---

## 3.17 Agent
### التعريف
كيان تنفيذي-معرفي يعمل تحت هوية معينة، ويستعمل مكونات الذاكرة والسياسات والمهارات لتحقيق أهداف.

### fields
- `agent_id`
- `identity_ref`
- `runtime_state`
- `active_tier`
- `active_blackboard`
- `available_tools`
- `available_skills`
- `current_goals`

### العلاقات
- Agent **instantiates** Identity at runtime
- Agent **acts_in** Environment
- Agent **generates** Episodes

---

## 3.18 Environment
### التعريف
العالم أو المهمة أو sandbox أو benchmark context الذي يتفاعل معه agent.

### fields
- `environment_id`
- `environment_type`
- `interface_contract`
- `available_actions`
- `state_model`
- `validators`
- `cost_profile`

### العلاقات
- Environment **produces** Observations
- Environment **receives** Actions
- Environment **part_of** Benchmarks

---

## 3.19 Decision
### التعريف
اختيار agent لخطوة معينة في لحظة معينة.

### الأنواع
- answer decision
- escalation decision
- retrieval decision
- search topology decision
- benchmark decision
- forgetting decision
- fork decision

### fields
- `decision_id`
- `decision_type`
- `belief_state_snapshot`
- `used_arguments`
- `used_policies`
- `expected_value`
- `actual_outcome`

### العلاقات
- Decision **made_by** Agent
- Decision **governed_by** Policy
- Decision **justified_by** Argument
- Decision **logged_in** Accountability chain

---

## 3.20 Artefact
### التعريف
أي كيان خارجي منظم يمكن استخدامه، مراجعته، ترقيته، أو أرشفته.

### قاعدة عامة
كل Concept, Skill, Theory, Test, Anomaly, Contradiction, Policy, Identity Object هو Artefact.

### fields المشتركة
- `artefact_id`
- `artefact_type`
- `version`
- `status`
- `lineage`
- `provenance`
- `utility`
- `owner`
- `linked_objects`

---

# 4) العلاقات العليا بين الكيانات

## 4.1 توليد المعرفة
Observation → Episode → Pattern → Heuristic → Concept → Invariant → Theory

## 4.2 التشغيل
Theory → Policy → Skill Selection → Decision → Action → New Episode

## 4.3 التصحيح
Contradiction → Concept Refinement or Theory Revision
Anomaly → Crisis Candidate → Paradigm/Fork Decision

## 4.4 التقييم
Theory / Skill / Policy → Benchmark/Test → Outcome → Lesson / Anomaly / Update

## 4.5 الهوية
Identity → owns Policies + Core Memories + Commitments + Self-Theories
Agent → runtime realization of Identity

---

# 5) القيود العليا (Global Invariants)

## Invariant 1
لا يوجد Concept نشط بلا scope أو counterexample policy.

## Invariant 2
لا يوجد Skill نشطة بلا verifier recipe أو failure signatures.

## Invariant 3
لا يوجد Theory نشطة بلا predictive claim أو prescriptive implication.

## Invariant 4
لا يوجد Contradiction مهمة بلا status واضح.

## Invariant 5
لا يوجد Anomaly persistent بلا اختبارات مشتقة أو خطة احتواء.

## Invariant 6
أي Premium reasoning يجب أن ينتج artefact reusable أو justification اقتصادية واضحة.

## Invariant 7
أي Fork يجب أن تحافظ على lineage وaccountability chain.

## Invariant 8
أي Forgetting action يجب أن تملك provenance وسببًا.

## Invariant 9
أي Identity يجب أن تملك core commitments قابلة للمراجعة الصريحة.

---

# 6) حالات الترقية والخفض (Promotion / Demotion Rules)

## Pattern → Heuristic
إذا ظهر انتظام متكرر وله قيمة تشغيلية أولية.

## Heuristic → Concept
إذا أصبحت القاعدة:
- مضغوطة
- ذات scope
- قابلة للنقل جزئيًا
- وقابلة للتشغيل

## Concept → Invariant
إذا صمدت عبر مجالات/مهمات متعددة مع استثناءات محدودة.

## Concepts/Invariants → Theory
إذا أمكن ربطها في mechanism + prediction + prescription.

## Skill candidate → Active Skill
إذا اجتازت tests وامتلكت failure signatures واضحة.

## Theory → Forked Theory
إذا ظهرت contradictions/anomalies لا تُحتوى داخل scope الحالية.

## Active Memory → Archived Memory
إذا انخفضت utility وارتفعت staleness أو abstraction dominance.

## Active Skill → Deprecated
إذا تكررت أضرارها أو حُلّت محلها skill أفضل.

---

# 7) حالة lifecycle العامة لأي Artefact
نقترح lifecycle موحدة:

1. proposed
2. candidate
3. validated
4. active
5. contested
6. revised
7. deprecated
8. archived
9. forked / superseded

وهذه lifecycle تنطبق مع تعديلات طفيفة على:
- Concept
- Skill
- Theory
- Policy
- Test
- Anomaly response plans

---

# 8) ما التالي بعد هذه الأنطولوجيا؟
بعد هذه الوثيقة، يمكن الانتقال إلى Specs أكثر تحديدًا، مثل:
1. Task Blackboard Spec
2. Memory OS Spec
3. Concept Formation Engine Spec
4. Productive Forgetting Engine Spec
5. Contradiction Ledger Spec
6. Anomaly/Crisis Manager Spec
7. Cognitive Economy Ledger Spec
8. Identity Object & Drift Monitoring Spec

هذه الوثيقة تمنحنا اللغة الرسمية اللازمة لصياغة كل ذلك.
