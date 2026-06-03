# Virtual-GENESIS Current Reference Index (Arabic)

## الغرض
هذه الوثيقة هي **فهرس مرجعي سريع** للحالة الحالية للمشروع.

لا تضيف نظرية جديدة، ولا تغيّر regime، بل تساعد على:
- معرفة ما الوثائق المرجعية الأهم الآن
- معرفة ما الملفات التنفيذية الأساسية
- معرفة ما أوامر التشغيل الحالية
- معرفة ما أفضل slices للتقييم

هذه الوثيقة مفيدة جدًا أثناء:
- التثبيت
- أو العودة للمشروع بعد فترة
- أو تسليم العمل لشخص آخر

---

# 1) الوثائق المرجعية العليا

## A. الرؤية العامة
- `Virtual_SIA_Master_Architecture_AR.md`
- `Virtual_SIA_Meta_Theory_AR.md`
- `Virtual_SIA_Research_Program_AR.md`
- `Virtual_SIA_Theory_Convergence_AR.md`

## B. القرار والحالة الحالية
- `Virtual_SIA_Decision_Memo_AR.md`
- `Virtual_SIA_Current_Regime_Memo_AR.md`
- `Virtual_SIA_Current_Evidence_Package_AR.md`
- `Virtual_SIA_Stabilization_Checklist_AR.md`

## C. النظريات الأساسية
- `Virtual_SIA_Concept_Formation_Theory_AR.md`
- `Virtual_SIA_Productive_Forgetting_Theory_AR.md`
- `Virtual_SIA_Contradiction_Theory_AR.md`
- `Virtual_SIA_Anomaly_Crisis_Paradigm_Theory_AR.md`
- `Virtual_SIA_Cognitive_Economy_Theory_AR.md`
- `Virtual_SIA_Local_Theory_Building_AR.md`
- `Virtual_SIA_Self_Benchmarking_Theory_AR.md`
- `Virtual_SIA_Agent_Identity_Theory_AR.md`

---

# 2) الوثائق الرسمية للبناء والتنفيذ

## Ontology / Specs
- `Virtual_SIA_Core_Ontology_AR.md`
- `Virtual_SIA_Task_Blackboard_Spec_AR.md`
- `Virtual_SIA_Memory_OS_Spec_AR.md`
- `Virtual_SIA_Concept_Formation_Engine_Spec_AR.md`
- `Virtual_SIA_Cognitive_Economy_Ledger_And_Tier_Router_Spec_AR.md`
- `Virtual_SIA_Task_Framing_Spec_AR.md`
- `Virtual_SIA_Verifier_Redesign_Spec_AR.md`
- `Virtual_SIA_Concept_Selectivity_Spec_AR.md`

## Implementation planning
- `Virtual_SIA_Prototype_Slice_Plan_AR.md`
- `Virtual_SIA_Implementation_Preplan_AR.md`
- `Virtual_SIA_Data_Schema_Plan_AR.md`
- `Virtual_SIA_Module_API_Contracts_AR.md`
- `Virtual_SIA_Milestone_Execution_Plan_AR.md`
- `Virtual_SIA_Build_Checklist_AR.md`
- `Virtual_SIA_First_Implementation_Order_AR.md`

---

# 3) أهم مذكرات evidence الحالية

## Most important runtime/evidence memos
- `Virtual_SIA_Expanded_Evidence_Memo_AR.md`
- `Virtual_SIA_Prototype_V3B_Curriculum_Evidence_Memo_AR.md`
- `Virtual_SIA_Prototype_V4_Boundary_Stress_Memo_AR.md`
- `Virtual_SIA_Prototype_V5_Evidence_Memo_AR.md`
- `Virtual_SIA_Concept_Selectivity_Update_Memo_AR.md`
- `Virtual_SIA_Contradiction_Analytics_Update_Memo_AR.md`
- `Virtual_SIA_Minimal_Anomaly_Candidate_Memo_AR.md`
- `Virtual_SIA_Minimal_Local_Theory_Builder_Memo_AR.md`
- `Virtual_SIA_Theory_Leverage_Update_Memo_AR.md`
- `Virtual_SIA_Evaluation_Regime_Status_Memo_AR.md`
- `Virtual_SIA_Family_Selectivity_Ablation_Results_Memo_AR.md`
- `Virtual_SIA_TaskCase_V4_Evidence_Memo_AR.md`
- `Virtual_SIA_Curriculum_Analytics_Update_Memo_AR.md`
- `Virtual_SIA_Concept_Engine_TaskCase_Refinement_Memo_AR.md`
- `Virtual_SIA_Task_Framing_Runtime_Update_Memo_AR.md`

---

# 4) أفضل evaluation slices الحالية

## Primary thesis regime
- `prototype_v3b_curriculum`
  - file: `virtual_genesis/eval/task_sets/prototype_v3b_curriculum.py`
  - runner: `virtual_genesis/eval/runners/run_local_eval_v3b_curriculum.py`

## Diagnostic regime
- `prototype_v4_cases`
  - file: `virtual_genesis/eval/task_sets/prototype_v4_cases.py`
  - runner: `virtual_genesis/eval/runners/run_local_eval_v4.py`

## Calibration references
- `prototype_v2`
- `prototype_v3`
- `prototype_v3_cases`

---

# 5) أهم ملفات الكود الحالية

## Core objects
- `virtual_genesis/core/objects/task.py`
- `virtual_genesis/core/objects/task_case.py`
- `virtual_genesis/core/objects/blackboard.py`
- `virtual_genesis/core/objects/memory.py`
- `virtual_genesis/core/objects/concept.py`
- `virtual_genesis/core/objects/contradiction.py`
- `virtual_genesis/core/objects/anomaly.py`
- `virtual_genesis/core/objects/theory.py`
- `virtual_genesis/core/objects/decision.py`
- `virtual_genesis/core/objects/ledger.py`

## Runtime modules
- `virtual_genesis/runtime/task_ingress/service.py`
- `virtual_genesis/runtime/task_ingress/normalize.py`
- `virtual_genesis/runtime/blackboard_core/service.py`
- `virtual_genesis/runtime/memory_os/store.py`
- `virtual_genesis/runtime/memory_os/retriever.py`
- `virtual_genesis/runtime/reasoning_runtime/service.py`
- `virtual_genesis/runtime/verification_runtime/service.py`
- `virtual_genesis/runtime/economy_control/router.py`
- `virtual_genesis/runtime/economy_control/escalation.py`
- `virtual_genesis/runtime/concept_engine/*`
- `virtual_genesis/runtime/contradiction_runtime/service.py`
- `virtual_genesis/runtime/anomaly_runtime/service.py`
- `virtual_genesis/runtime/theory_runtime/*`
- `virtual_genesis/runtime/pipeline/minimal_run.py`

## Evaluation modules
- `virtual_genesis/eval/runners/*`
- `virtual_genesis/eval/reports/*`
- `virtual_genesis/eval/perturbations/taskcase_variants.py`
- `virtual_genesis/eval/task_sets/*`

---

# 6) أوامر التشغيل المهمة الآن

## Run current primary thesis curriculum
```bash
python -m virtual_genesis.eval.runners.run_local_eval_v3b_curriculum
```

## Run diagnostic boundary slice
```bash
python -m virtual_genesis.eval.runners.run_local_eval_v4
```

## Run selectivity ablation
```bash
python -m virtual_genesis.eval.runners.run_selectivity_ablation
```

## Run family-specific selectivity ablation
```bash
python -m virtual_genesis.eval.runners.run_family_selectivity_ablation
```

---

# 7) Default current operating assumptions
- TaskCase-based evaluation preferred when available
- Concept selectivity defaults:
  - comparison: top1 / score7
  - synthesis: top1 / score7
  - procedure: top0
- economy-aware routing is trusted more than premium-always for cost frontier
- v3b_curriculum = primary thesis regime
- v4_cases = diagnostic slice only

---

# 8) إن أردت البدء من الصفر في القراءة
### fastest reading path
1. `Virtual_SIA_Current_Regime_Memo_AR.md`
2. `Virtual_SIA_Current_Evidence_Package_AR.md`
3. `Virtual_SIA_Decision_Memo_AR.md`
4. `Virtual_SIA_Stabilization_Checklist_AR.md`
5. `Virtual_SIA_Prototype_V3B_Curriculum_Evidence_Memo_AR.md`
6. ثم Specs/Runtime حسب الحاجة

---

# 9) القرار الحالي باختصار
إذا سألنا: “ما المرجع الحالي الرسمي السريع؟”
فالجواب هو:
- **Regime:** `Virtual_SIA_Current_Regime_Memo_AR.md`
- **Evidence:** `Virtual_SIA_Current_Evidence_Package_AR.md`
- **Primary runtime evaluation:** `run_local_eval_v3b_curriculum`
- **Diagnostic evaluation:** `run_local_eval_v4`

هذه الوثيقة فقط تجعل العثور على ذلك سريعًا وواضحًا.
