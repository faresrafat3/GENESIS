# Virtual-GENESIS Task Blackboard Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي أول Spec رسمي runtime-level في المشروع.

بعد أن عرّفنا:
- الـ Meta-Theory
- الـ Research Program
- والـ Core Ontology

ننتقل الآن إلى أول مكوّن تشغيلي محوري:

# **Task Blackboard**

وهو المساحة المشتركة التي:
- تُكتب عليها حالة المهمة
- وتُضاف إليها الذاكرة المسترجعة
- وتُسجَّل عليها الفرضيات والحجج والاعتراضات
- ومنها تتخذ السياسات والمهارات والـ verifiers قراراتها

بمعنى آخر:

> إذا كانت الـ Ontology هي قاموس الوجود،
> فالـ Blackboard هو **مسرح الوجود أثناء المهمة**.

---

# 1) التعريف المركزي
## Task Blackboard
هي بنية حالة مشتركة، قابلة للتحديث التدريجي، تمثل **الصورة العاملة الحالية** للمهمة عند الوكيل.

هي ليست مجرد log.
وليست مجرد prompt context.
وليست مجرد scratchpad.

بل:

> **Shared structured state for perception, orientation, reasoning, verification, and decision.**

---

# 2) لماذا نحتاج Blackboard أصلًا؟
بدون Blackboard، يحدث أحد أمرين:
1. كل subcomponent يعمل في عزلة ويعيد بناء فهمه من الصفر
2. أو تُدفع كل المعلومات في prompt linear طويلة وغير منظمة

كلاهما ضعيف.

أما Blackboard فتوفر:
- تمثيلًا مشتركًا للحالة
- فصلًا بين الـ data والـ policies
- traceability للقرارات
- مكانًا طبيعيًا لظهور contradictions/anomalies
- إمكانية تشغيل Specialists متعددي الأدوار

---

# 3) المبادئ التصميمية للـ Blackboard

## Principle 1 — Shared but typed
الـ Blackboard مشتركة، لكن كل شيء فيها يجب أن يكون typed لا مجرد نص حر.

## Principle 2 — Mutable but auditable
يمكن تحديثها أثناء المهمة، لكن كل تعديل يجب أن يترك provenance.

## Principle 3 — Layered visibility
ليست كل المكونات ترى كل شيء بنفس الشكل؛ بعضهم يقرأ summary، وبعضهم يستطيع drill-down.

## Principle 4 — State, not story
الـ Blackboard تمثل حالة عمل قابلة للاستعلام، لا مجرد سرد زمني.

## Principle 5 — Contradictions must be representable
إذا ظهرت اعتراضات أو تعارضات، لا يجوز إخفاؤها داخل prose فقط.

## Principle 6 — Blackboard should support interruption
يجب أن تسمح للوكيل بأن يوقف reasoning أو يصعّد أو يبدّل topology دون فقدان coherence.

---

# 4) ما الذي تحتويه الـ Blackboard؟
نقترح أن تتكون من 12 أقسام منطقية:

## Section A — Task Core
تمثيل المهمة الأساسية.

### fields
- `task_id`
- `task_text_raw`
- `task_text_normalized`
- `task_family`
- `subtask_family` (optional)
- `criticality_level`
- `difficulty_estimate`
- `deadline_or_latency_class`
- `success_criteria`
- `failure_cost_class`

---

## Section B — Context Snapshot
ما الذي نعرفه عن الوضع الحالي؟

### fields
- `user_context_summary`
- `conversation_state`
- `relevant_history_refs`
- `environment_state_refs`
- `tool_availability`
- `model_tier_options`
- `constraints`

---

## Section C — Retrieved Memory Pack
الذاكرة التي تم استرجاعها للمهمة الحالية.

### fields
- `episodic_memories[]`
- `semantic_memories[]`
- `strategic_memories[]`
- `procedural_memories[]`
- `negative_memories[]`
- `memory_retrieval_rationale`
- `memory_noise_risk`

كل entry يجب أن يكون reference أو object مختصر، لا نص خام فقط.

---

## Section D — Situation Model
هذا القسم يمثل “Orient” في OODA.

### fields
- `task_interpretation`
- `knowns`
- `unknowns`
- `uncertainties`
- `assumptions`
- `missing_information`
- `candidate_problem_frames[]`
- `current_scope_assessment`

---

## Section E — Hypotheses / Claims
الفرضيات أو الإجابات المرشحة.

### fields
- `candidate_claims[]`

Each candidate claim object contains:
- `claim_id`
- `claim_text`
- `confidence`
- `support_refs`
- `risk_flags`
- `status` (draft / active / challenged / rejected / adopted)

---

## Section F — Argument Layer
طبقة الحِجاج الداخلي.

### fields
- `arguments[]`

Each argument contains:
- `argument_id`
- `claim_ref`
- `grounds_refs`
- `warrant_text`
- `backing_refs`
- `qualifier`
- `rebuttal_refs`
- `argument_strength`

---

## Section G — Search / Deliberation State
يصف هيكل التفكير الحالي.

### fields
- `reasoning_topology` (linear / tree / graph / debate-lite / self-consistency)
- `search_budget_remaining`
- `branch_count`
- `active_branches[]`
- `pruned_branches[]`
- `reasoning_scaffold_refs`
- `committee_status` (none / proposed / active / resolved)

---

## Section H — Skill & Policy Activation
ما المهارات والسياسات المفعلة الآن؟

### fields
- `active_skills[]`
- `candidate_skills[]`
- `rejected_skills[]`
- `active_policies[]`
- `policy_rationales[]`
- `tier_router_decision`
- `escalation_status`

---

## Section I — Verification State
ما الذي تم التحقق منه؟ وما الذي ما زال معلقًا؟

### fields
- `verification_plan`
- `schema_checks`
- `rule_checks`
- `evidence_checks`
- `test_execution_results`
- `judge_results`
- `consistency_checks`
- `verification_disagreements[]`
- `verification_summary`

---

## Section J — Contradictions / Anomalies
هذا من أهم أقسام الـ Blackboard.

### fields
- `active_contradictions[]`
- `resolved_contradictions[]`
- `anomaly_signals[]`
- `crisis_indicators[]`
- `scope_conflicts[]`

كل contradiction أو anomaly يجب أن يكون reference إلى object رسمي من الـ ontology.

---

## Section K — Decisions & Actions
ما القرارات التي اتخذها agent أثناء المهمة؟

### fields
- `decisions[]`

Each decision contains:
- `decision_id`
- `decision_type`
- `input_state_snapshot_ref`
- `selected_option`
- `expected_value`
- `actual_outcome`
- `decision_justification_refs`
- `timestamp`

---

## Section L — Outcome & Learning Hooks
ما النتيجة النهائية؟ وما الذي يجب استخراجه منها للتعلم؟

### fields
- `final_output_ref`
- `task_outcome`
- `cost_summary`
- `latency_summary`
- `confidence_summary`
- `lessons_to_extract[]`
- `candidate_concepts[]`
- `candidate_skill_updates[]`
- `candidate_tests[]`
- `candidate_anomalies[]`

---

# 5) الحالة العامة للـ Blackboard
نقترح أن Blackboard نفسها تمر بحالات lifecycle:

1. `initialized`
2. `contextualized`
3. `oriented`
4. `deliberating`
5. `verifying`
6. `resolving_conflicts`
7. `finalizing`
8. `closed`
9. `archived`

### ملاحظة
هذه الحالات ليست حتمًا خطية 100%.
قد نرجع من `verifying` إلى `deliberating` أو من `resolving_conflicts` إلى `oriented`.

---

# 6) من يقرأ ويكتب على الـ Blackboard؟
نقترح أدوارًا أساسية:

## Writers
- Task Normalizer
- Memory Retriever
- Planner
- Reasoner
- Skill Router
- Verifier(s)
- Judge
- Contradiction Analyzer
- Anomaly Detector
- Outcome Consolidator

## Readers
- كل ما سبق +
- Tier Router
- Cognitive Economy Controller
- Replay Logger
- Lesson Compiler

### القاعدة
لا توجد write privileges كاملة للجميع على كل الأقسام.

مثال:
- Verifier يكتب أساسًا في Section I وJ
- Memory Retriever يكتب في Section C
- Planner يكتب في D وG
- Contradiction Analyzer يكتب في J

---

# 7) ما الفرق بين Blackboard وMemory؟
## Blackboard
- runtime-local
- task-scoped
- mutable heavily
- reflects current situation model

## Memory
- cross-task
- persistent
- curated / governed
- retrieved into Blackboard

### العلاقة
Memory feeds Blackboard,
but Blackboard is not memory itself.

بل Blackboard هي:
> **working theater of cognition**

---

# 8) ما الفرق بين Blackboard وPrompt؟
Prompt هي أحد outputs الممكنة من بعض أجزاء Blackboard.

لكن Blackboard أوسع لأنها:
- structured
- multi-view
- auditable
- not flattened by default
- supports multiple specialists

إذًا:
- prompt = projection
- blackboard = state substrate

---

# 9) ما الفرق بين Blackboard وLog؟
Log زمني غالبًا.
Blackboard حالي/بنيوي.

### log answers:
- ماذا حدث؟

### blackboard answers:
- ما هي الحالة الآن؟
- ما الفرضيات؟
- ما الاعتراضات؟
- ما الذي تم التحقق منه؟
- ما القرار التالي؟

---

# 10) القواعد البنيوية للـ Blackboard

## Rule 1 — No important free text without a typed anchor
أي ادعاء مهم يجب أن يرتبط بـ object من نوع claim/argument/decision/etc.

## Rule 2 — Every high-impact decision must cite state
أي قرار مهم يجب أن يحمل references إلى الحالة التي بُني عليها.

## Rule 3 — Every contradiction must live somewhere explicit
لا يجوز bury contradictions داخل prose.

## Rule 4 — Blackboard must support partial answers
في anytime mode، يجب أن تحمل partial outputs + confidence + next-best actions.

## Rule 5 — Blackboard must separate evidence from interpretation
Observation ≠ claim.
Memory ≠ theory.
Verifier result ≠ final decision.

## Rule 6 — Blackboard must preserve drill-down paths
أي summary يجب أن يرتبط بالمصادر الأصلية references.

---

# 11) ما الذي يجعل Blackboard جيدة؟
نقترح 6 معايير جودة:

## Quality A — Clarity
هل الحالة الحالية واضحة أم ممزوجة؟

## Quality B — Minimal sufficient structure
هل فيها enough structure without overengineering؟

## Quality C — Contradiction visibility
هل تظهر النزاعات أم تختفي؟

## Quality D — Decision traceability
هل نعرف لماذا تم اختيار skill/tier/topology؟

## Quality E — Learning extractability
هل يمكن بسهولة استخراج:
- lessons
- concepts
- anomalies
- tests

## Quality F — Cost discipline
هل تساعد على تقليل redundant rethinking؟

---

# 12) Failure modes في Blackboard design

## Failure Mode 1 — Blackboard as dump
كل شيء يُلقى فيها دون typing أو hierarchy.

## Failure Mode 2 — Blackboard too rigid
تصبح ثقيلة ومعقدة لدرجة تعطل runtime.

## Failure Mode 3 — Hidden state outside blackboard
المكونات تحتفظ باستدلالات مهمة خارجها، فيفقد النظام traceability.

## Failure Mode 4 — Over-summarization
نضغط الحالة لدرجة ضياع evidence والاعتراضات.

## Failure Mode 5 — Under-separation
facts, claims, and decisions تختلط ببعض.

## Failure Mode 6 — Blackboard-Memory collapse
تصير كل memory task-local clutter داخل blackboard.

---

# 13) العمليات الأساسية على الـ Blackboard
نقترح 8 عمليات مجردة:

1. `initialize_blackboard(task)`
2. `attach_context(blackboard, context_pack)`
3. `inject_retrieved_memory(blackboard, memory_pack)`
4. `propose_hypothesis(blackboard, claim)`
5. `attach_argument(blackboard, argument)`
6. `record_verification(blackboard, verification_result)`
7. `register_contradiction(blackboard, contradiction_ref)`
8. `finalize_blackboard(blackboard, outcome)`

لاحقًا يمكن توسيعها إلى APIs أدق.

---

# 14) snapshots وstate transitions
لأن الـ Blackboard mutable، نحتاج snapshot semantics:

## Blackboard Snapshot
نسخة مجمدة من الحالة عند لحظة قرار/تحقق/تصعيد.

### لماذا؟
- decision accountability
- replay
- anomaly diagnosis
- lesson extraction

### متى نصنع snapshots؟
- قبل تصعيد tier
- بعد retrieval كبير
- قبل verifier ensemble run
- عند contradiction escalation
- عند final decision

---

# 15) العلاقة مع الـ Tier Router
Tier Router لا تعمل في الفراغ.
هي تقرأ من Blackboard:
- uncertainty
- evidence sufficiency
- contradictions
- anomaly signals
- task criticality
- candidate branch instability

ثم تكتب قرارها في:
- Section H
- Section K

إذًا Blackboard هي substrate القرار الاقتصادي والمعرفي.

---

# 16) العلاقة مع Concept Formation Engine
Concept Formation Engine يقرأ من Blackboard:
- episodes
- claims
- contradictions
- verification results
- lessons_to_extract

ثم ينتج candidate_concepts توضع مبدئيًا في Section L.

إذًا Blackboard هي مصدر raw structured material للتجريد.

---

# 17) العلاقة مع Contradiction Theory
Contradiction Theory تحتاج مكانًا يظهر فيه:
- claims المتعارضة
- verifier disagreements
- policy clashes
- skill clashes

وهذا المكان الطبيعي هو Section J.

أي Blackboard الجيدة يجب أن تكون:
# **contradiction-friendly**
لا contradiction-suppressing.

---

# 18) العلاقة مع Self-Benchmarking
أي anomaly أو scope boundary أو skill misuse داخل Blackboard يمكن أن يتحول إلى:
- benchmark candidate
- boundary test
- anti-shortcut test

لذلك وجود Section L مهم، لأنه يربط التشغيل بالتعلم والتقييم اللاحق.

---

# 19) العلاقات الرسمية المختصرة
- Blackboard **contains** Task state
- Blackboard **references** Memories, Skills, Theories, Tests
- Blackboard **hosts** Claims, Arguments, Contradictions, Decisions
- Blackboard **feeds** Concept Formation, Lesson Extraction, Replay
- Blackboard **is governed by** Policies and Identity rules

---

# 20) ما الذي نفعله بعد هذه الوثيقة؟
الخطوة التالية المنطقية هي أحد خيارين:

## الخيار A
**Memory OS Spec**
لأن Blackboard لا تعمل جيدًا دون معرفة كيف تُبنى memory packs وتُدار lifecycle.

## الخيار B
**Concept Formation Engine Spec**
لأن Blackboard تعطينا المادة الخام للانتقال إلى المفاهيم.

رأيي الحالي:
ابدأ بـ **Memory OS Spec** ثم Concept Formation Engine Spec.

هذه الوثيقة صارت الآن المسرح الرسمي الذي سيعتمد عليه كلاهما.
