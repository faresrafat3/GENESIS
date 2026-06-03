# Virtual-GENESIS Cognitive Economy Ledger & Tier Router Spec (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة هي الـ Spec التنفيذية الأساسية التي تضرب مباشرة في **Thesis 2**:

> **Cognitive Economy beats stronger-model-only scaling**

بعد أن عرّفنا:
- Core Ontology
- Task Blackboard
- Memory OS
- Concept Formation Engine

ننتقل الآن إلى المكوّن الذي يقرر:
- متى نكتفي؟
- متى نفكر أكثر؟
- متى نسترجع؟
- متى نصعّد؟
- متى نستخدم premium model؟
- متى نستخدم committee؟
- ومتى نستثمر في learning artefacts بدل answer فورية فقط؟

هذه الوثيقة تصف مكوّنين مترابطين:
1. **Cognitive Economy Ledger**
2. **Tier Router & Escalation Engine**

---

# 1) التعريف المركزي
## 1.1 Cognitive Economy Ledger
هو السجل الذي يسجل ويقيّم **أين صُرفت cognition** داخل المهمة، ولماذا، وما العائد المتوقع والفعلي من هذا الصرف.

## 1.2 Tier Router
هو المكوّن الذي يختار **درجة القدرة/الكلفة** المناسبة في كل مرحلة من المهمة:
- free / ultra-cheap
- cheap paid
- premium reasoning
- sparse collaboration

### الصياغة المختصرة
Cognitive Economy Layer =
**bounded, value-aware governance of reasoning, retrieval, verification, escalation, and learning investments**

---

# 2) لماذا ledger + router معًا؟
لو عندنا Router بلا Ledger:
- سيصعد أو يتراجع بلا تعلم بنيوي من قراراته السابقة
- لن نعرف أين يحدث الهدر المعرفي

ولو عندنا Ledger بلا Router:
- سنقيس الاقتصاد المعرفي لكن لن نطبقه runtime

إذًا:
- **Router** = policy-in-action
- **Ledger** = memory-of-allocation + basis for improvement

---

# 3) المبادئ التصميمية الكبرى

## Principle 1 — No cognition is free
حتى إن كانت token cost صفرية أو منخفضة، هناك:
- latency cost
- noise cost
- attention cost
- verification overhead
- opportunity cost

## Principle 2 — Reasoning depth must be earned
لا يجوز الانتقال إلى deeper search أو premium model أو committee بلا trigger أو value estimate.

## Principle 3 — Premium compute must buy reusable cognition
أي تصعيد مكلف يجب أن ينتج واحدًا أو أكثر من:
- reasoning scaffold
- lesson
- skill patch
- concept candidate
- theory refinement
- anomaly evidence

## Principle 4 — Good-enough is sometimes optimal
الهدف ليس دائمًا الوصول إلى أفضل جواب ممكن نظريًا، بل إلى أفضل جواب **ضمن القيود ومع قيمة marginal مناسبة**.

## Principle 5 — Solve-now and learn-for-later compete for the same budget
بعض cognition يجب أن تذهب إلى:
- answer now
وبعضها قد يكون أكثر قيمة إن ذهب إلى:
- concept/skill/theory/test generation

## Principle 6 — Escalation should be explainable
كل escalation decision يجب أن تكون قابلة للشرح، لا فقط triggered by hidden heuristics.

---

# 4) طبقات tiers الرسمية
هذه ليست فقط model list، بل درجات قدرة/كلفة ذات semantics تشغيلية.

## Tier 0 — Free / ultra-cheap
### الاستخدام
- task triage
- light extraction
- formatting
- shallow critique
- retrieval pre-processing
- low-risk classification

### الخصائص
- low cost
- low commitment
- high interruptibility
- low justification burden

---

## Tier 1 — Cheap paid / standard worker
### الاستخدام
- standard planning
- answer drafting
- common coding assistance
- moderate synthesis
- normal verification support

### الخصائص
- medium cost
- default mainline execution for many tasks
- can produce reusable artefacts cheaply enough

---

## Tier 2 — Premium reasoner
### الاستخدام
- hard reasoning
- long-horizon planning
- anomaly resolution
- difficult debugging
- dense synthesis
- theory-sensitive tasks

### الخصائص
- high capability
- non-trivial cost
- must usually justify itself through stronger expected return

---

## Tier 3 — Sparse collaborative cognition
### الاستخدام
- major verifier split
- multi-perspective synthesis
- adversarial ambiguity
- persistent unresolved uncertainty after single-premium pass

### الخصائص
- highest orchestration cost
- not default
- should be rare

---

# 5) Cognitive actions to be governed
Router لا تختار model فقط، بل تختار بين أفعال معرفية متعددة.

## Action classes
1. `answer_now`
2. `retrieve_more`
3. `verify_more`
4. `reason_deeper`
5. `switch_topology`
6. `escalate_tier`
7. `invoke_sparse_committee`
8. `abstain_or_qualify`
9. `invest_in_learning_artifact`
10. `fork_to_anomaly_analysis`

---

# 6) مدخلات الـ Tier Router
الـ Router يجب أن تعمل على Blackboard state وليس على prompt raw فقط.

## Required input fields
### Task-related
- `task_family`
- `difficulty_estimate`
- `criticality_level`
- `failure_cost_class`
- `deadline_or_latency_class`

### State-related
- `knowns`
- `unknowns`
- `uncertainties`
- `assumptions`
- `missing_information`

### Memory-related
- `memory_noise_risk`
- `available_high_order_artifacts`
- `episodic_dependency_level`
- `negative_memory_triggers`

### Reasoning-related
- `reasoning_topology`
- `branch_instability`
- `candidate_claim_count`
- `argument_strength_profile`

### Verification-related
- `verification_summary`
- `verifier_disagreement_score`
- `evidence_sufficiency_score`

### Governance-related
- `active_contradictions_count`
- `anomaly_signal_level`
- `crisis_indicators`

### Economic-related
- `budget_remaining`
- `premium_budget_remaining`
- `committee_budget_remaining`
- `latency_spent`
- `token_spent`
- `learning_investment_budget_remaining`

---

# 7) القرار الأساسي: ماذا نقدر؟
الـ Router يجب أن يقدّر أربع كميات على الأقل لكل cognitive action candidate:

## 7.1 Estimated Immediate Utility Gain
كم نتوقع أن تتحسن مهمة الآن؟

## 7.2 Estimated Future Reuse Gain
هل سينتج artefact reusable؟

## 7.3 Estimated Cost
- token cost
- latency cost
- orchestration cost
- noise risk

## 7.4 Estimated Delay / Opportunity Penalty
هل مزيد التفكير الآن سيضيع قيمة بسبب التأخير أو لأنه يمنع جهدًا آخر؟

---

# 8) الصيغة الاقتصادية الأساسية
لكل action candidate `a`:

**Expected Cognitive Return(a) = Immediate Gain(a) + Reuse Gain(a) + Learning Gain(a) - Cost(a) - Delay Penalty(a) - Noise Risk(a)**

### ملاحظات
- ليست معادلة نهائية، لكنها contract رسمي للفكر التصميمي.
- لا يلزم أن تكون كل terms رقمية تمامًا في v1؛ يمكن أن تبدأ hybrid ordinal/heuristic.

---

# 9) Trigger system — متى نصعّد؟
نقترح triggers عالية الأولوية:

## Trigger A — High uncertainty
إذا uncertainty مرتفعة والجواب الحالي weakly grounded.

## Trigger B — Verifier split
إذا verifier disagreement يتجاوز threshold.

## Trigger C — Evidence insufficiency
إذا answer مرشحة لكن evidence coverage ضعيفة.

## Trigger D — Anomaly pressure
إذا anomaly signals متوسطة أو مرتفعة.

## Trigger E — Theory-sensitive task
إذا المهمة من نوع synthesis/comparison/diagnosis وتحتاج structure deeper.

## Trigger F — High-value task
إذا failure cost مرتفع.

## Trigger G — Learning opportunity
إذا المهمة غنية بما يكفي لإنتاج concept/skill/theory worth the extra compute.

---

# 10) De-escalation conditions — متى نكبح؟
كما توجد triggers للصعود، نحتاج كوابح:

## Brake 1 — Good-enough confidence
إذا الجواب وصل threshold مناسب + verifier stable.

## Brake 2 — Diminishing returns
إذا عدة خطوات إضافية لم تغير state materially.

## Brake 3 — Budget fragility
إذا التصعيد سيأكل نسبة كبيرة من budget المتبقية دون عائد متوقع واضح.

## Brake 4 — Committee not justified
إذا premium single-pass or extra verification likely enough.

## Brake 5 — Noise escalation
إذا retrieval or extra paths likely to inject clutter أكثر من الفائدة.

---

# 11) Tier Router Outputs
كل routing action يجب أن ينتج object واضح.

## Tier Decision Object
- `tier_decision_id`
- `chosen_tier`
- `decision_reason`
- `trigger_refs`
- `expected_immediate_gain`
- `expected_reuse_gain`
- `expected_cost`
- `expected_delay_penalty`
- `confidence_in_decision`
- `fallback_option`
- `timestamp`

هذا object يكتب إلى:
- Blackboard Section H
- Blackboard Section K
- Cognitive Economy Ledger

---

# 12) Cognitive Economy Ledger — تعريف رسمي
الـ Ledger هو سجل لجميع الاستثمارات الإدراكية المهمة.

### Ledger Entry fields
- `ledger_entry_id`
- `task_id`
- `phase`
- `cognitive_action_type`
- `chosen_tier`
- `topology_if_any`
- `trigger_refs`
- `estimated_immediate_gain`
- `estimated_reuse_gain`
- `estimated_learning_gain`
- `estimated_cost`
- `estimated_delay_penalty`
- `estimated_noise_risk`
- `actual_cost`
- `actual_latency`
- `actual_immediate_effect`
- `actual_reuse_effect` (can be filled later)
- `actual_learning_effect` (can be delayed)
- `would_repeat`
- `notes`

### الهدف
أن يتعلم النظام ليس فقط من answers، بل من **كيف صرف cognition**.

---

# 13) Ledger categories
يمكن تصنيف entries إلى:

## Category A — Reasoning Investments
- deeper reasoning
- topology switch
- more branches

## Category B — Retrieval Investments
- layered retrieval
- contrastive retrieval
- anomaly memory retrieval

## Category C — Verification Investments
- extra tests
- judge invocation
- committee judge

## Category D — Tier Escalation Investments
- cheap → premium
- premium → sparse committee

## Category E — Learning Investments
- lesson extraction
- concept proposal
- skill update
- benchmark generation

---

# 14) Solve-now vs Learn-for-later
هذه من أهم النقاط التي يجب أن يحكمها الـ Ledger.

### مبدأ
ليس كل budget يجب أن تذهب إلى answer الحالية.

بعض المواقف تستحق تخصيص جزء من cognition إلى:
- concept formation
- skill patch
- theory note
- anomaly report
- benchmark candidate

### القاعدة
إذا كانت task:
- high novelty
- rich in contradiction/anomaly
- expensive to solve
- likely to recur

فـ **learning investment** قد يكون عقلانيًا جدًا.

---

# 15) Premium reasoning rule
### قانون رسمي
أي invocation لـ Tier 2 أو Tier 3 يجب أن يمر بـ one of these intents:
1. `hard-task resolution`
2. `anomaly disambiguation`
3. `theory-sensitive synthesis`
4. `reusable artifact generation`
5. `high-stakes verification`

إذا لم يتحقق intent واضح، فالتصعيد suspicious اقتصاديًا.

---

# 16) Committee invocation policy
committee ليست مجرد tier أعلى، بل modality مختلفة.

## committee allowed when:
- single-premium pass still unstable
- disagreement structurally important
- multiple perspectives likely to add non-redundant value
- budget remains sufficient

## committee denied when:
- failure likely due to missing evidence only
- problem is formatting or simple retrieval
- premium solo reasoning not yet attempted
- expected diversity gain low

### Committee Decision Object
- `committee_decision_id`
- `committee_mode`
- `proposers`
- `aggregator`
- `expected_diversity_gain`
- `expected_cost`
- `stop_condition`

---

# 17) Topology selection policy
Tier Router must also choose reasoning topology.

## topology choice hints
### choose linear when:
- extraction
- low ambiguity
- low task value
- no conflict indicators

### choose self-consistency when:
- moderate reasoning uncertainty
- multiple paths cheap enough

### choose tree when:
- explicit planning/decomposition needed
- branch choices matter early

### choose graph when:
- synthesis/comparison/theory tasks
- distributed evidence integration
- topology mismatch signals active

### choose debate-lite when:
- competing arguments need explicit confrontation
- contradiction or verifier split is central

---

# 18) Economy reports
الـ system needs derived reports, not raw entries only.

## Report types
1. `task_cost_profile`
2. `escalation_roi_report`
3. `premium_dependency_report`
4. `committee_utility_report`
5. `retrieval_waste_report`
6. `verification_overkill_report`
7. `learning_investment_report`

هذه reports ستغذي لاحقًا:
- policy updates
- self-theories
- anomaly detection
- benchmark generation

---

# 19) Failure modes

## Failure Mode 1 — Prestige bias
اختيار premium لأن “الأقوى أفضل” فقط.

## Failure Mode 2 — Cheapness bias
البخل في التصعيد لدرجة إنتاج answers هشة.

## Failure Mode 3 — Ledger blindness
تسجيل المعلومات دون استخدامها في policy improvement.

## Failure Mode 4 — Reuse illusion
الاعتقاد أن premium reasoning useful لاحقًا دون evidence of actual reuse.

## Failure Mode 5 — Committee fetish
استخدام collaboration كثيرًا رغم low marginal gain.

## Failure Mode 6 — Learning starvation
كل cognition تذهب إلى solving now ولا شيء يذهب إلى epistemic capital formation.

---

# 20) Success criteria
### Criterion A
تحسن واضح في cost-quality frontier

### Criterion B
انخفاض unnecessary premium escalations

### Criterion C
تحسن premium ROI عبر الزمن

### Criterion D
زيادة نسبة cognition التي تنتج reusable artifacts

### Criterion E
تراجع retrieval/verification waste

### Criterion F
وجود explainable, auditable routing behavior

---

# 21) Global interfaces
نقترح واجهات مجردة:

1. `estimate_cognitive_return(action, state)`
2. `choose_tier(task_state)`
3. `should_escalate(task_state)`
4. `should_open_committee(task_state)`
5. `should_invest_in_learning(task_state)`
6. `record_cognitive_spend(entry)`
7. `generate_economy_report(scope)`

---

# 22) العلاقة مع Blackboard
الـ Blackboard هي substrate القراءة والكتابة للـ Router والـ Ledger.

### Router reads
- task core
- situation model
- memory pack
- argument layer
- contradictions/anomalies
- verification state
- budget info

### Router writes
- tier decisions
- escalation status
- active policies
- decision objects

### Ledger writes
- cognitive spend entries
- later outcome updates

---

# 23) العلاقة مع Concept Formation Engine
Concept Formation Engine يحتاج budget.

### implication
Router must decide:
- هل هذه المهمة تستحق concept-building effort؟
- أم يكفي solve-and-move-on؟

وهذا من أهم نقاط الربط بين Thesis 1 وThesis 2.

---

# 24) ما التالي بعد هذه الوثيقة؟
بعد Cognitive Economy Ledger & Tier Router Spec، تصبح الخطوات الطبيعية التالية:

1. Minimal Evaluation Protocol
2. Contradiction Ledger Spec
3. Anomaly/Crisis Manager Spec
4. Local Theory Builder Spec

لكن إذا أردنا الاستمرار في خدمة الفرضيتين المركزيتين أولًا، فالخطوة الأذكى الآن هي:

# **Virtual_SIA_Minimal_Evaluation_Protocol_AR.md**

لأننا نحتاج طريقة واضحة لاختبار:
- retrieval-only vs concept-aware
- fixed routing vs economy-aware routing
قبل توسيع governance layers أكثر.
