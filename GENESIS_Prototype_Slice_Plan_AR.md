# Virtual-GENESIS Prototype Slice Plan (Arabic)

## 0) الغرض من هذه الوثيقة
هذه الوثيقة تجيب عن السؤال:

> ما هي **أصغر نسخة قابلة للبناء والاختبار** من Virtual-GENESIS بحيث تختبر الفرضيتين المركزيتين، دون أن نحاول بناء النظام الكامل دفعة واحدة؟

الهدف هنا هو منع خطرين:
1. **formal overgrowth** — الاستمرار في كتابة specs بلا تماس مع الواقع
2. **implementation chaos** — القفز إلى تنفيذ واسع قبل اختيار مركز الثقل

لذلك نريد:

# **Prototype Slice**
أي شريحة صغيرة من النظام:
- قابلة للبناء
- قابلة للتقييم
- ذات علاقة مباشرة بـ Thesis 1 وThesis 2
- وتُنتج evidence واضحة

---

# 1) الفرضيتان اللتان يجب أن تخدمهما الشريحة

## Thesis 1
**Concept Formation beats retrieval-only adaptation**

## Thesis 2
**Cognitive Economy beats stronger-model-only scaling**

إذًا أي مكوّن لا يخدم هاتين الفرضيتين مباشرة أو غير مباشرة يجب ألا يدخل prototype الأولى.

---

# 2) القرار الاستراتيجي
نرفض هنا بناء النظام الكامل.

## لن نبني في Prototype 1:
- Local Theory Builder الكامل
- Anomaly/Crisis Manager الكامل
- Identity governance الكامل
- Sparse committee كاملة
- Self-benchmarking engine الكامل
- multimodal/OS/web interaction full stack
- distributed/decentralized memory

## سنبني فقط ما يلزم لاختبار الفرضيتين:
1. Task Blackboard minimal
2. Memory OS minimal
3. Concept Formation Engine minimal
4. Tier Router minimal
5. Cognitive Economy Ledger minimal
6. Minimal evaluator harness

---

# 3) ما هو “minimal” هنا؟
minimal لا يعني “بدائي”، بل يعني:
- أقل عدد مكونات
- أقل عدد task families
- أقل عدد decision branches
- أعلى وضوح causal attribution

أي:

> إذا فشلنا، نعرف لماذا.
> وإذا نجحنا، نعرف من أين جاء النجاح.

---

# 4) صورة الـ Prototype الأولى

## Core flow
Task → Blackboard → Memory Retrieval → Candidate Answer → Verification → Optional Concept Formation → Optional Tier Escalation → Final Output → Logging

### وبعد عدة tasks
Episodes/Patterns → Concept Candidates → Validated Concepts → Reused in future tasks

### وفي parallel
Tier decisions + costs → Cognitive Economy Ledger → policy insight

---

# 5) نطاق الشريحة الأولى
نحتاج مجالًا ضيقًا لكنه غني بما يكفي.

## الاختيار المقترح
### **Text-based analytical tasks with recurring structures**

مثال:
- comparison
- classification with rationale
- synthesis over 2–4 evidence snippets
- failure diagnosis of short artifacts
- structured extraction with validation

### لماذا هذا الاختيار؟
لأنه:
- لا يحتاج web/GUI infrastructure الآن
- يسمح بتكرار patterns
- يسمح بقياس transfer
- يسمح concept formation
- يسمح قياس escalation economics
- يمكن تشغيله على free/cheap/premium بسهولة

---

# 6) ما هي task families في Prototype 1؟
نقترح 3 families فقط:

## Family A — Comparative Reasoning
المهمة: مقارنة خيارين/نصين/حلين/تفسيرين.

### لماذا؟
تظهر فيها:
- claims
- evidence sufficiency
- contradictions
- structure-sensitive reasoning

## Family B — Evidence Synthesis
المهمة: دمج عدة snippets أو facts في answer منظمة.

### لماذا؟
تظهر فيها:
- topology mismatch
- ungrounded completion
- evidence coverage
- usefulness of concepts

## Family C — Structured Procedure Tasks
المهمة: extraction / formatting / categorization مع خطوات متكررة.

### لماذا؟
تظهر فيها:
- skill reuse
- raw retrieval vs procedure guidance
- low-cost vs overthinking tradeoffs

---

# 7) dataset / task set المقترحة
## الحجم الأولي
- 20 task من Family A
- 20 task من Family B
- 20 task من Family C

إجمالي = **60 task** كبداية صريحة وصغيرة.

## التقسيم
- 30 task development
- 15 task validation
- 15 task holdout

### ملاحظة
نريد version صغيرة أولًا قبل الانتقال إلى مجموعة 100 task المذكورة في Minimal Evaluation Protocol.

---

# 8) المكونات التي ستدخل النسخة الأولى فعلاً

## 8.1 Task Blackboard Minimal
### سنُفعّل فقط هذه الأقسام من الـ Blackboard Spec:
- Task Core
- Context Snapshot
- Retrieved Memory Pack
- Situation Model
- Candidate Claims
- Verification State
- Decisions & Actions
- Outcome & Learning Hooks

### ما الذي سنؤجله؟
- Argument layer الكامل
- Contradictions/Anomalies section بصيغتها الغنية
- branch graphs الكاملة

### لماذا؟
لأننا نريد reduced state complexity مع بقاء الأجزاء الجوهرية.

---

## 8.2 Memory OS Minimal
### سنفعل فقط الطبقات التالية:
- Working Memory
- Episodic Memory
- Semantic Memory
- Procedural Memory
- Negative Memory

### سنؤجل الآن:
- Anomaly Memory
- Strategic Memory الكاملة كطبقة مستقلة
- inherited/delegated memory complexities

### لماذا؟
لأن الهدف الأول هو اختبار:
- retrieval-only vs concept-aware retrieval
- procedure reuse
- forgetting policy بسيطة

---

## 8.3 Concept Formation Engine Minimal
### ستعمل على:
- success/failure pairs
- repeated patterns in dev set
- generating concept candidates
- scope drafting (basic)
- acceptance tests محدودة

### سنؤجل:
- split/merge theory-rich operations
- concept graph المعقد
- heavy counterexample generation

### الناتج المتوقع
- 3 إلى 10 Concept Objects مبدئية ذات utility واضحة

---

## 8.4 Tier Router Minimal
### tiers المستخدمة فعليًا
- Tier 0 / free or ultra-cheap path
- Tier 1 / cheap paid default
- Tier 2 / premium on demand

### سنؤجل:
- Tier 3 / sparse committee

### لماذا؟
لأن committee ستدخل confounds كثيرة مبكرًا.

---

## 8.5 Cognitive Economy Ledger Minimal
### سنسجل فقط:
- retrieval decisions
- escalation decisions
- verification spending
- learning investment spending
- immediate vs later reuse gain where possible

### سنؤجل:
- full portfolio optimization
- complex policy learning
- dynamic expected value calibration

---

## 8.6 Verification Harness Minimal
### verification modes
- schema/format check
- evidence sufficiency check
- simple judge or rubric check
- task-specific rule checks

### سنؤجل:
- multi-judge adversarial loops
- execution-heavy tests (except maybe small structured ones in Family C)

---

# 9) Baselines التي يجب أن نقارن بها

## Baseline 0 — Fixed Prompt / No Memory
stateless direct generation baseline

## Baseline 1 — Retrieval-only Memory
episodic/semantic retrieval بدون concepts

## Baseline 2 — Premium-Always
يستخدم النموذج الأقوى دائمًا على main reasoning path

## Baseline 3 — Fixed Cheap Policy
cheap-first لكن بلا economy-aware logic

## Experimental Condition A
Concept-aware memory + fixed routing

## Experimental Condition B
Economy-aware routing + retrieval memory only

## Experimental Condition C
Concept-aware + economy-aware combined

---

# 10) ما الذي نريد أن نراه في النتائج؟

## بالنسبة لـ Thesis 1
نتوقع من Condition A أو C أن تُظهر:
- انخفاض raw episodic retrieval reliance
- تحسنًا في Family B وholdout transfer
- activation واضح لمفاهيم محددة
- تقليل repeated failure patterns

## بالنسبة لـ Thesis 2
نتوقع من Condition B أو C أن تُظهر:
- fewer unnecessary premium escalations
- cost-quality frontier أفضل من Baseline 2 أو 3
- better ROI من premium calls
- قدرة على التوقف early عندما يكفي

---

# 11) ما الـ artifacts المطلوبة في Prototype 1؟

## Runtime artifacts
1. Blackboard snapshots
2. Tier decision objects
3. Ledger entries
4. Retrieved memory packs
5. Final outputs + verification records

## Knowledge artifacts
6. Episode summaries
7. Memory units
8. Concept candidates
9. Validated concepts
10. Negative memory entries
11. Skill capsules (limited to Family C)

## Evaluation artifacts
12. Per-task result sheets
13. Per-family summary
14. Concept utility report
15. Premium ROI report

---

# 12) الـ validated concepts المتوقعة مبدئيًا
لا نضمنها، لكن نتوقع concepts من النوع التالي:
- Ungrounded Completion
- Evidence Fragmentation
- Topology Mismatch
- Over-Verification Waste
- Stable Procedure Reuse Opportunity
- Cheap-path Sufficiency Pattern

هذه مجرد expectations، وليست assumptions ثابتة.

---

# 13) Acceptance criteria for Prototype 1

## Acceptance A — Buildability
يمكن تشغيل flow كاملة end-to-end على task set صغيرة.

## Acceptance B — Traceability
يمكن تفسير لماذا استُخدم concept أو لماذا حدث escalation.

## Acceptance C — Artifact reality
concepts and ledger entries ليست مجرد logs؛ بل تؤثر على decisions.

## Acceptance D — Comparative value
على الأقل أحد condition التجريبية يتفوق بوضوح على baseline المناسبة.

## Acceptance E — No hidden dependence
النجاح لا يأتي فقط من premium model always-on.

---

# 14) What we do NOT need in Prototype 1
هذه نقطة مهمة.

لا نحتاج الآن إلى:
- perfect taxonomy
- polished UI
- complete identity system
- full contradiction ledger
- anomaly manager الكامل
- benchmark synthesis engine
- autonomous skill design at scale

إذا أدخلنا كل ذلك الآن، سنخسر وضوح الفرضيتين.

---

# 15) المخاطر في Prototype 1

## Risk 1 — Too weak tasks
لو المهام بسيطة جدًا فلن تظهر قيمة concepts أو economy routing.

## Risk 2 — Too hard tasks
لو المهام صعبة جدًا سننسب الفشل لكل شيء.

## Risk 3 — Artifact placebo
concepts/logs موجودة لكن لا تؤثر على السلوك.

## Risk 4 — Premium confound
gains تأتي فقط من premium model path.

## Risk 5 — Overengineering the slice
نحاول حشر كل النظرية في prototype واحدة.

### العلاج
- small scope
- explicit ablations
- hard acceptance rules
- focus on 2 theses only

---

# 16) الترتيب العملي التالي بعد هذه الوثيقة
الخطوة التالية ليست نظرية جديدة، بل إما:

## Option A — More specs to support the slice
1. Contradiction Ledger Spec (minimal)
2. Minimal Evaluation Harness Data Schema
3. Tier Router Decision Heuristics Table

## Option B — Implementation planning
1. Project folder structure
2. Module boundaries
3. Data schemas in JSON/Pydantic form
4. Execution order of the first prototype

### رأيي الحالي
بما أننا وصلنا إلى slice واضحة، فالخطوة الذكية التالية هي:

# **Virtual_SIA_Implementation_Preplan_AR.md**

أي:
- نحول specs الحالية إلى خطة بناء تقنية مرتبة
- من غير ما نغرق مباشرة في كود كامل

وهذا سيكون الانتقال الصحيح من formalization إلى engineering.
