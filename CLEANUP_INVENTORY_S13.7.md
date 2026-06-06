# 🧹 CLEANUP_INVENTORY — Session 13.7

**Date:** 2026-06-06
**Triggered by:** Fares: *"عايزك تحصي ليا ايه الحاجات القديمه يعني اللي موجوده وملهاش لازمه بس لازم تبقي دقيق وتلف المشروع كامله وتقراءه كامله وتفهمه كامل عشان تلقط حاجه زي كده عشان تقولي هي ايه وتخلي قرار الحذف او التنظيف او الدمج او غيره من الموقف المناسب باختياري"*

**Translation:** Inventory the old/redundant/unneeded things. Be precise. Read the whole project. Tell me what each is so I can decide to delete / clean up / merge / keep.

**Authorization scope:** Inventory ONLY — agent does NOT delete/modify anything. Every item below has an explicit "RECOMMENDED ACTION" field for **Fares to decide on**. Nothing happens to any file until Fares explicitly authorizes.

---

## 📊 Project at a glance

| Metric | Value |
|---|---|
| Total .md files at root | 134 (122 GENESIS_*_AR.md + 12 master/Layer-A docs) |
| Total .md files (whole project) | 211 |
| Total .py files | 200 |
| Total .json files | 109 |
| Largest directory | `virtual_genesis/` (96 MB — mostly `eval/results/` JSONs) |
| **GENESIS_*_AR.md REFERENCED by paper-era master docs** | **18 of 122 (15%)** |
| **GENESIS_*_AR.md UNREFERENCED** | **104 of 122 (85%)** |

**Headline:** 85% of foundational docs are not referenced anywhere in the paper-era documentation. They are **not necessarily junk** — but every one needs a deliberate decision: archive, merge, keep-as-is, or delete.

---

## ⚠️ How to read this inventory

Every item has 5 fields:

| Field | Meaning |
|---|---|
| **Item** | What the file/group is |
| **Size / count** | How much it is |
| **What it contains** | Brief description |
| **Why it might be obsolete** | Honest reasoning |
| **RECOMMENDED ACTION** (for Fares to decide) | One of: 🟢 KEEP / 🟡 ARCHIVE / 🟠 MERGE / 🔴 DELETE / ⚪ UNCERTAIN — agent recommendation only |

**Action key:**
- 🟢 **KEEP** — actively used; do not touch
- 🟡 **ARCHIVE** — useful as history but not active; move to `archive/` subdir
- 🟠 **MERGE** — overlaps with another doc; combine and delete original
- 🔴 **DELETE** — dead weight; safe to remove
- ⚪ **UNCERTAIN** — need Fares's call on whether it has value

---

# Section 1 — Layer A Prototype Evidence Files (8 files, ~36 KB)

## Item 1.1 — Prototype Evidence Memos (V2 → V5)

**Files:**
- `GENESIS_Prototype_V2_Evidence_Memo_AR.md` (5.3 KB)
- `GENESIS_Prototype_V3_Evidence_Memo_AR.md` (4.9 KB)
- `GENESIS_Prototype_V3B_Evidence_Memo_AR.md` (4.5 KB)
- `GENESIS_Prototype_V3B_Curriculum_Evidence_Memo_AR.md` (4.5 KB)
- `GENESIS_Prototype_V4_Boundary_Stress_Memo_AR.md` (4.4 KB)
- `GENESIS_Prototype_V5_Evidence_Memo_AR.md` (3.0 KB)
- `GENESIS_TaskCase_V4_Evidence_Memo_AR.md` (5.3 KB)

**What it contains:** Sequential evidence memos from Layer A pre-paper prototype iterations (May 2026). Each documents a specific prototype version's experimental results on `prototype_v3b_curriculum`.

**Why it might be obsolete:** All Layer A prototype iterations (V2-V5) have been superseded by Layer B paper-era empirical anchors (75% pure / 65% GENESIS / 70% A3 on GPQA Diamond). The V3B 98.6% result is mentioned in the original `README.md` only as historical context. None are referenced from paper-era docs.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — move to `archive/layer_a_prototype_evidence/`. They document the project's empirical history but are no longer active references. Worth keeping for provenance.

---

## Item 1.2 — Prototype Plan/Status docs

**Files:**
- `GENESIS_Prototype_Slice_Plan_AR.md` (11.8 KB)
- `GENESIS_Prototype_Status_Memo_AR.md` (3.2 KB)

**What it contains:** Planning + status snapshots for Layer A prototype iterations.

**Why it might be obsolete:** Same as Item 1.1.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — same destination.

---

# Section 2 — Layer A Selectivity/Ablation Cycle Docs (8 files, ~36 KB)

**Files:**
- `GENESIS_Concept_Selectivity_Spec_AR.md` (8.6 KB)
- `GENESIS_Concept_Selectivity_Update_Memo_AR.md` (4.5 KB)
- `GENESIS_Family_Selectivity_Ablation_Memo_AR.md` (1.7 KB)
- `GENESIS_Family_Selectivity_Ablation_Results_Memo_AR.md` (3.8 KB)
- `GENESIS_Family_Specific_Selectivity_Plan_AR.md` (1.8 KB)
- `GENESIS_Selectivity_Ablation_Plan_AR.md` (5.4 KB)
- `GENESIS_Selectivity_Ablation_Results_Memo_AR.md` (3.5 KB)
- `GENESIS_Selectivity_Default_Config_Memo_AR.md` (1.9 KB)

**What it contains:** Iterative experiments on "selectivity" (which concepts to apply when) in Layer A prototype. Specific to `family_selectivity` mechanism not used in Layer B paper.

**Why it might be obsolete:** Layer A-specific mechanism. The paper-era `genesis/orchestrator.py` uses different ablation modes (`no_pipeline`, `narrow_feedback`). No paper-era reference.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_selectivity/`. May be useful if you ever return to Layer A's selectivity mechanism, but currently inactive.

---

# Section 3 — Layer A Smoke Test / Evaluation Iterations (10 files, ~62 KB)

**Files:**
- `GENESIS_Smoke_Test_Analysis_AR.md` (7.8 KB) — pre-paper smoke test investigation
- `GENESIS_Smoke_Test_v2_Results_AR.md` (7.8 KB) — pre-paper smoke test results
- `GENESIS_Eval_System_Analysis_AR.md` (12.6 KB)
- `GENESIS_Evaluation_Perturbation_Curriculum_Spec_AR.md` (8.2 KB)
- `GENESIS_Evaluation_Pressure_Cycle_Memo_AR.md` (8.1 KB)
- `GENESIS_Evaluation_Redesign_Memo_AR.md` (3.3 KB)
- `GENESIS_Evaluation_Regime_Status_Memo_AR.md` (4.8 KB)
- `GENESIS_Evaluation_Slice_Strategy_AR.md` (4.2 KB)
- `GENESIS_Minimal_Evaluation_Protocol_AR.md` (12.3 KB)
- `GENESIS_Perturbation_Operator_Expansion_Results_Memo_AR.md` (4.3 KB)
- `GENESIS_Perturbation_Operator_Refinement_Memo_AR.md` (4.4 KB)

**What it contains:** Layer A's evaluation methodology evolution. Bones of how the prototype was tested before GPQA Diamond was adopted in Session 1.

**Why it might be obsolete:** Layer B paper uses GPQA Diamond + `tasks/gpqa_subset_20` exclusively. The Smoke Test analysis (Session 2) found the 5 bugs that became Session 1-3 empirical foundation — *that's* what's preserved in PAPER.md §5.3 + §5.4. The original docs themselves are historical.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_evaluation/`. Note: Smoke Test analysis docs (`GENESIS_Smoke_Test_Analysis_AR.md` and `_v2_Results_AR.md`) are particularly worth archiving (not deleting) because they contain the diagnostic detail that led to the 5-bug discovery.

---

# Section 4 — Layer A "Cycle" Progression Docs (6 files, ~37 KB)

**Files:**
- `GENESIS_Broader_Domain_Cycle_Memo_AR.md` (10.9 KB)
- `GENESIS_Next_Cycle_Decision_Anomaly_vs_Theory_AR.md` (4.6 KB)
- `GENESIS_Next_Cycle_Options_AR.md` (7.7 KB)
- `GENESIS_Theory_Leverage_Cycle_Memo_AR.md` (12.7 KB)
- `GENESIS_Theory_Leverage_Activation_Memo_AR.md` (2.5 KB)
- `GENESIS_Theory_Leverage_Update_Memo_AR.md` (2.1 KB)
- `GENESIS_Theory_Warmup_Leverage_Memo_AR.md` (1.9 KB)

**What it contains:** Layer A iteration cycles — each "cycle" documents a phase of pre-paper prototype work.

**Why it might be obsolete:** Layer A planning vocabulary. The paper-era equivalent is sessions (S1, S2, etc.) documented in MASTER_TIMELINE.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_cycles/`. Internal cycle history; useful only if researching the project's lifecycle.

---

# Section 5 — Layer A "Current Regime" Snapshots (4 files, ~64 KB) ⚠️ MISLEADING NAMES

**Files:**
- `GENESIS_Current_Evidence_Package_AR.md` (7.8 KB) — *NOT current; dated May 2026*
- `GENESIS_Current_Reference_Index_AR.md` (7.0 KB) — *NOT current; dated May 2026*
- `GENESIS_Current_Regime_Memo_AR.md` (9.6 KB) — *NOT current; dated May 2026*
- `GENESIS_Current_Regime_Status_AR.md` (36.8 KB) — *NOT current; dated 2026-05-31*

**What it contains:** Snapshots labeled "current" but referring to Layer A's state in late May 2026, before paper era began in Session 1.

**Why it might be obsolete:** **The word "Current" is actively misleading.** Anyone reading the filename thinks these reflect today's project state. They actually reflect a state 2+ weeks ago, pre-paper.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE + RENAME** — move to `archive/layer_a_snapshots/` AND rename with date suffix:
- `GENESIS_Current_Regime_Status_AR.md` → `archive/layer_a_snapshots/GENESIS_Regime_Status_2026-05-31_AR.md`
- Same pattern for the other 3

This removes the misleading "Current" label.

---

# Section 6 — Old Theft Wave Files SUPERSEDED by Master Index (7 files, ~95 KB)

**Files:**
- `GENESIS_Legitimate_Thefts_Cycle2_AR.md` (15.0 KB)
- `GENESIS_Legitimate_Thefts_Cycle3_AR.md` (16.7 KB)
- `GENESIS_Legitimate_Thefts_Cycle4_AR.md` (14.4 KB)
- `GENESIS_Legitimate_Thefts_Production_AR.md` (4.8 KB)
- `GENESIS_Legitimate_Thefts_RealWorld_AR.md` (4.6 KB)
- `GENESIS_Legitimate_Thefts_Wave3_AR.md` (16.5 KB)
- `GENESIS_Legitimate_Thefts_Wave3b_AR.md` (14.4 KB)

**What it contains:** Earlier iterations of the "legitimate thefts" cataloging system. Each wave/cycle added new thefts.

**Why it might be obsolete:** **`GENESIS_Legitimate_Thefts_MASTER_INDEX_AR.md` is the canonical consolidated index (scope 5.1-5.94 + classical 6.1-6.13).** It supersedes all wave/cycle files.

**RECOMMENDED ACTION:** 🟠 **MERGE-VERIFY then ARCHIVE** — agent should:
1. Verify every theft from Cycle2/3/4/Wave3/Wave3b/Production/RealWorld appears in MASTER_INDEX
2. If any are missing, surface them
3. Then move the wave files to `archive/layer_a_theft_waves/`

Estimated effort: 1-2 hours of careful reading. **Worth doing before archiving** because thefts are first-class artifacts.

---

# Section 7 — Layer A Old Research Paper/Report Predecessors (6 files, ~135 KB) ⚠️ POTENTIAL CONFUSION

**Files:**
- `GENESIS_RESEARCH_REPORT_Current_State_2026-06-05_AR.md` (25.3 KB) — pre-Session-1 baseline report
- `GENESIS_Research_Agenda_And_Theory_AR.md` (13.5 KB)
- `GENESIS_Research_Blueprint_AR.md` (14.5 KB)
- `GENESIS_Research_Map_and_Artefacts_AR.md` (11.0 KB)
- `GENESIS_Research_Paper_Draft_AR.md` (57.8 KB) ← **largest in this batch**
- `GENESIS_Research_Program_AR.md` (15.7 KB)

**What it contains:**
- `GENESIS_Research_Paper_Draft_AR.md` — **A separate paper draft (57 KB) from Jun 1, 2026 titled "Virtual-GENESIS: تسخير الذكاء عبر آليات معرفية خارجية فوق نماذج لغوية ثابتة"**. Different paper, predates PAPER.md.
- The other 5 are Layer A research planning/agenda docs.

**Why it might be obsolete:** ⚠️ **Critical concern:** Having a `Research_Paper_Draft_AR.md` at root that is NOT the current paper risks confusing any reader (including future agents) about which is the "real" paper. PAPER.md (v0.7) is the authoritative paper.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE WITH STRONG LABELING** — move to `archive/layer_a_old_paper_drafts/` with a README.md explaining "These are Layer A pre-paper drafts. The authoritative paper is `PAPER.md` v0.7 at repo root."

The other 5 Layer A research docs → `archive/layer_a_research_planning/`.

---

# Section 8 — Layer A First/Build/Implementation/Milestone Docs (7 files, ~64 KB)

**Files:**
- `GENESIS_Build_Checklist_AR.md` (11.2 KB)
- `GENESIS_Deep_Continuation_AR.md` (4.6 KB)
- `GENESIS_Deep_Foundations_AR.md` (12.9 KB)
- `GENESIS_First_Evidence_Memo_AR.md` (3.9 KB)
- `GENESIS_First_Implementation_Order_AR.md` (6.8 KB)
- `GENESIS_Implementation_Preplan_AR.md` (12.3 KB)
- `GENESIS_Milestone_Execution_Plan_AR.md` (12.6 KB)

**What it contains:** Layer A bootstrap/planning docs — "how to start building" stuff from when the prototype was being designed.

**Why it might be obsolete:** Layer A-only. Layer B doesn't follow this milestone plan.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_planning/`. Useful for someone trying to understand "how did the project originally get built?"

---

# Section 9 — Layer A "Minimal" Starter Docs (4 files, ~17 KB)

**Files:**
- `GENESIS_Minimal_Anomaly_Candidate_Memo_AR.md` (1.7 KB)
- `GENESIS_Minimal_Contradiction_Runtime_Memo_AR.md` (1.9 KB)
- `GENESIS_Minimal_Evaluation_Protocol_AR.md` (12.3 KB)
- `GENESIS_Minimal_Local_Theory_Builder_Memo_AR.md` (2.2 KB)

**What it contains:** Layer A "minimal viable" prototypes of subsystems.

**Why it might be obsolete:** Layer A-specific.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_minimal_starters/`.

---

# Section 10 — Layer A Architecture/Spec Docs (8 files, ~120 KB)

**Files:**
- `GENESIS_Master_Architecture_AR.md` (27.1 KB) ← **biggest**
- `GENESIS_Core_Ontology_AR.md` (17.1 KB)
- `GENESIS_Data_Schema_Plan_AR.md` (18.6 KB)
- `GENESIS_Memory_OS_Spec_AR.md` (15.2 KB)
- `GENESIS_Module_API_Contracts_AR.md` (12.6 KB)
- `GENESIS_Concept_Formation_Engine_Spec_AR.md` (14.1 KB)
- `GENESIS_Verifier_Redesign_Spec_AR.md` (11.0 KB)
- `GENESIS_Task_Blackboard_Spec_AR.md` (15.0 KB)
- `GENESIS_Task_Case_Schema_Spec_AR.md` (7.7 KB)
- `GENESIS_Task_Framing_Spec_AR.md` (12.4 KB)

**What it contains:** Layer A system architecture and module specifications. These describe `virtual_genesis/` code organization.

**Why it might be obsolete:** ⚠️ **Subtle:** These describe `virtual_genesis/` which still exists (96 MB!) but is NOT used in Layer B paper era. Layer B uses `genesis/` instead.

**RECOMMENDED ACTION:** ⚪ **UNCERTAIN** — depends on Fares's intent for `virtual_genesis/`:
- If you'll ever return to Layer A operations → 🟢 KEEP these specs (they describe the active code)
- If Layer A is permanently retired → 🟡 ARCHIVE alongside `virtual_genesis/` itself

See Section 13 (virtual_genesis/ directory) below for related decision.

---

# Section 11 — Layer A Theory/Local-Theory Building Docs (5 files, ~50 KB)

**Files:**
- `GENESIS_Local_Theory_Building_AR.md` (18.9 KB) ← **In HANDOFF priority queue for batch 4 reading**
- `GENESIS_Theory_Convergence_AR.md` (11.2 KB)
- `GENESIS_Research_Agenda_And_Theory_AR.md` (13.5 KB) — already covered in §7

**What it contains:** Layer A's theory infrastructure. `Local_Theory_Building_AR.md` is specifically mentioned in HANDOFF as one of the priority docs for the next re-reading batch.

**Why it might be obsolete:** Not yet read! May contain Fares precursors for additional Theories.

**RECOMMENDED ACTION:** 🟢 **KEEP** all three. `Local_Theory_Building_AR.md` is a high-value re-read candidate. The others may surface in future S14+ batches.

---

# Section 12 — Layer A Implementation Memos for specific subsystems (12 files, ~80 KB)

**Files:**
- `GENESIS_Adversarial_Validation_Memo_AR.md` (10.6 KB)
- `GENESIS_Anomaly_Leverage_Implementation_Memo_AR.md` (8.6 KB)
- `GENESIS_Concept_Engine_Deep_Analysis_AR.md` (12.3 KB)
- `GENESIS_Concept_Engine_TaskCase_Refinement_Memo_AR.md` (3.4 KB)
- `GENESIS_Contract_Perturbation_Memo_AR.md` (3.4 KB)
- `GENESIS_Contradiction_Analytics_Update_Memo_AR.md` (3.6 KB)
- `GENESIS_Curriculum_Analytics_Update_Memo_AR.md` (2.9 KB)
- `GENESIS_Identity_Governance_Implementation_Memo_AR.md` (8.7 KB)
- `GENESIS_Level_Wise_Governance_Analytics_Memo_AR.md` (2.4 KB)
- `GENESIS_Paradigm_Fork_Implementation_Memo_AR.md` (10.6 KB)
- `GENESIS_Persistence_Implementation_Memo_AR.md` (3.9 KB)
- `GENESIS_Productive_Forgetting_Implementation_Memo_AR.md` (8.2 KB)
- `GENESIS_Self_Benchmarking_Implementation_Memo_AR.md` (5.7 KB)

**What it contains:** Implementation notes for `virtual_genesis/` subsystems (concept engine, anomaly leverage, paradigm fork, etc.).

**Why it might be obsolete:** Same as Section 10 — tied to `virtual_genesis/` Layer A code.

**RECOMMENDED ACTION:** ⚪ **UNCERTAIN** — same as Section 10. If `virtual_genesis/` is retired, archive these. If kept, keep these too.

---

# Section 13 — `virtual_genesis/` Directory (96 MB!) 🚨 LARGEST DECISION

**Location:** `virtual_genesis/`
**Size:** **96 MB** (96% of which is `virtual_genesis/eval/results/` JSON files)

**Contents:**
- `virtual_genesis/api/` (40 KB) — API layer
- `virtual_genesis/core/` (108 KB) — core epistemic objects
- `virtual_genesis/eval/` (96 MB) — evaluation infrastructure + **HUGE result files**
  - `virtual_genesis/eval/results/` — 15 JSON files including:
    - `selectivity_ablation_summary.json` (24.4 MB)
    - `family_selectivity_ablation_summary.json` (24.4 MB)
    - `prototype_v6_summary.json` (13.0 MB)
    - `broader_domain_summary.json` (12.5 MB)
    - `prototype_v3c_curriculum_summary.json` (6.0 MB)
    - `prototype_v3b_curriculum_summary.json` (5.8 MB)
    - (9 more smaller files)
- `virtual_genesis/persistence/` (44 KB) — SQLite stores
- `virtual_genesis/runtime/` (376 KB) — runtime engines

**What it is:** The complete Layer A prototype codebase. The 98.6% result mentioned in `README.md` was produced by this code.

**Why it might be obsolete:** Layer B paper uses `genesis/` exclusively. The 23 tests in `tests/` actually test `virtual_genesis/` (see `tests/test_persistence.py` which imports `from virtual_genesis.core.objects.concept ...`).

**RECOMMENDED ACTIONS (Fares to choose):**

| Option | Action | Pros | Cons |
|---|---|---|---|
| **A** | 🟢 KEEP everything as-is | Layer A code stays functional; tests still pass | 96 MB bloat; confuses paper-era readers |
| **B** | 🟡 **ARCHIVE `eval/results/` only** (the 96 MB of old JSONs); keep code | Removes 95 MB bloat; code still functional; can re-generate results if needed | Tests that depend on these JSONs may fail |
| **C** | 🟡 ARCHIVE entire `virtual_genesis/` directory (move to `archive/`) | Cleanest separation; paper-era only at top level | Breaks 23 tests; loses easy access to Layer A code |
| **D** | 🔴 DELETE `virtual_genesis/eval/results/*.json` (keep only 1 sample) | Frees ~95 MB | Loses pre-paper experimental data permanently |

**Agent recommendation:** **Option B** — archive the 96 MB of result JSONs (they're reproducible, not source) but keep the code structure so Layer A tests still pass. This is the cleanest middle ground.

---

# Section 14 — Strategic Plan Docs (2 files, ~27 KB) — DUPLICATES

**Files:**
- `STRATEGIC_DEVELOPMENT_PLAN_2026_06.md` (18.9 KB) — dated 2026-06-04
- `STRATEGIC_DEVELOPMENT_PLAN_2026_06_v2.md` (8.0 KB) — dated 2026-06-02 (yes, v2 is OLDER than v1!)

**What it contains:** Two Strategic Development Plans (dated Jun 2 and Jun 4 — both pre-Session 1). v2 file is older despite name (v2 was likely renamed/superseded conceptually).

**Why it might be obsolete:** **Both predate paper era.** Layer A planning. Confusing naming (v2 is older). Neither is referenced from paper-era docs.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE BOTH** — `archive/layer_a_strategic_plans/`. Optionally rename to reflect actual dates.

---

# Section 15 — `test_pioneer.py` at Root (1 file, ~2 KB) — 🔴 DEAD CODE

**File:** `test_pioneer.py` (1.8 KB)

**What it contains:** Test script for Pioneer API with DeepSeek-V4-Pro. **Requires `.pioneer_key` file which does not exist in repo.** Dead dependency.

**Why it's obsolete:** Layer A operational artifact from when DeepSeek-V4-Pro on Pioneer API was being evaluated. No longer used. Reads a key file that doesn't exist.

**RECOMMENDED ACTION:** 🔴 **DELETE** — pure dead code with broken dependency. Or 🟡 ARCHIVE to `archive/layer_a_scripts/` if you want to preserve it as historical curiosity.

---

# Section 16 — Layer A Task Framing Memos (3 files, ~9 KB)

**Files:**
- `GENESIS_Task_Framing_Runtime_Update_Memo_AR.md` (2.6 KB)
- `GENESIS_Task_Framing_Verification_Interaction_Memo_AR.md` (2.8 KB)
- `GENESIS_TaskCase_Migration_Plan_AR.md` (8.8 KB)

**What it contains:** Task-framing subsystem memos for Layer A.

**Why it might be obsolete:** Layer A-specific.

**RECOMMENDED ACTION:** 🟡 **ARCHIVE** — `archive/layer_a_task_framing/`.

---

# Section 17 — Layer A Infrastructure/Decision Docs (5 files, ~50 KB)

**Files:**
- `GENESIS_Decision_Memo_AR.md` (8.7 KB)
- `GENESIS_Free_LLM_Providers_2026_AR.md` (12.6 KB) — **partially still relevant** (covers free providers including OpenRouter Gemini etc.)
- `GENESIS_Merge_Strategy_AR.md` (11.1 KB)
- `GENESIS_Multi_Model_Infrastructure_AR.md` (10.7 KB) — **partially still relevant** (Layer B uses tools/providers.py based on similar logic)
- `GENESIS_Nemotron_3_Ultra_Memo_AR.md` (12.1 KB) — **still relevant** (Session 1 nemotron docs)
- `GENESIS_Orchestrator_Scaffolding_Fix_AR.md` (7.9 KB) — **still relevant** (documents the 6 scaffolding bugs that became §5.4)

**What it contains:** Mixed bag — some Layer A planning, some still-relevant infrastructure documentation.

**Why it might be obsolete:** Mixed. The provider/model/scaffolding docs are arguably **paper-era reference material** that should be promoted.

**RECOMMENDED ACTION:** 🟢 **KEEP** the still-relevant ones (Free_LLM_Providers, Multi_Model_Infrastructure, Nemotron_3_Ultra, Orchestrator_Scaffolding_Fix) and consider linking from PROJECT_README. 🟡 ARCHIVE the rest (`Decision_Memo`, `Merge_Strategy`) to `archive/layer_a_infra/`.

---

# Section 18 — Layer A Stabilization/Lock Docs (3 files, ~24 KB) ⚠️ MISLEADING

**Files:**
- `GENESIS_Internal_Regime_Lock_AR.md` (14.4 KB) — referenced from `README.md` and `virtual_genesis/README.md` as authoritative
- `GENESIS_Governance_Aware_Current_Snapshot_AR.md` (8.8 KB)
- `GENESIS_Stabilization_Checklist_AR.md` (8.4 KB)

**What it contains:** Layer A's "we promise not to change these things" lock files. `Internal_Regime_Lock` is referenced from Layer A READMEs as primary reference.

**Why it might be misleading:** ⚠️ **Confusion risk** — `README.md` and `virtual_genesis/README.md` say "The internal regime lock and current status documents (Arabic) are primary reference. All other descriptions are subordinate to them." This contradicts paper-era hierarchy (where `PROJECT_README.md` + `PAPER.md` are primary).

**RECOMMENDED ACTION:** 🟢 **KEEP** the lock file (it's referenced) but **UPDATE Layer A READMEs to clarify** they refer to Layer A scope only, not the whole project. The lock concept itself remains valid as Layer A artifact.

---

# Section 19 — `results/` Directory at Root (~250 KB)

**Files:**
- `ablation_live_2026-06-01.json` + `ablation_summary_2026-06-01.md`
- `agent_smoke_test/`, `agent_smoke_v2/`, `quick_sanity/`, `quick_sanity2/`
- `run_gemma_20q/`, `run_gpt-oss-120b_20q/`, `run_ultra_20q/`, `run_ultra_focused/`
- `v3b_anomaly.json`, `v3b_baseline.json`, `v3b_theory.json`

**What it contains:** Mix of Layer A ablation results AND some 20q runs that look paper-era.

**Why it might be obsolete:** ⚠️ **Mixed** — `run_gpt-oss-120b_20q/` and `run_ultra_20q/` could be relevant to paper era, while `agent_smoke_test/`, `quick_sanity/`, `v3b_*.json` are Layer A.

**RECOMMENDED ACTION:** ⚪ **UNCERTAIN** — needs inspection. Best to:
1. Check each subdirectory's actual relevance to paper-era runs
2. Move Layer A items to `archive/layer_a_results/`
3. Keep paper-era runs in `results/` or move to `runs/` for consistency with `runs/run_53/`

---

# Section 20 — `runs/` Directory (308 KB)

**File:** `runs/run_53/` containing `context.md`, `gen_1/`, `gen_2/`
- Logs: `runs/run_53/gen_1/evaluation.log`, `target_agent_stdout.log` (and same for gen_2)

**What it contains:** The actual run artifacts for `run_53` (the buggy 30.30% run that started paper-era investigation).

**Why it might be obsolete:** Historical record. **The run_53 result is the foundation of the entire 6-bug-fix story.** Important to keep.

**RECOMMENDED ACTION:** 🟢 **KEEP** — primary empirical artifact. **However:** consider adding a `runs/README.md` explaining what's there and which runs would be added in future (run_57, run_58 results referenced in paper but stored elsewhere — should they be here?).

---

# Section 21 — Layer A Pre-Paper Setup/Quick-Run Docs (3 files, ~20 KB)

**Files:**
- `SETUP_AND_RUN_GUIDE.md` (9.2 KB) — operational setup
- `QUICK_RUN_20Q_GUIDE_AR.md` (2.4 KB)
- `API_GENESIS_Design_Arabic.md` (4.7 KB)

**What it contains:** Operational guides + original system design.

**Why it might be obsolete:** SETUP_AND_RUN_GUIDE is referenced from original `README.md` — still potentially useful for anyone setting up the project. The others are pre-paper.

**RECOMMENDED ACTIONS:**
- `SETUP_AND_RUN_GUIDE.md` → 🟢 KEEP (operational reference)
- `QUICK_RUN_20Q_GUIDE_AR.md` → 🟢 KEEP (relates to active `tasks/gpqa_subset_20/`)
- `API_GENESIS_Design_Arabic.md` → 🟡 ARCHIVE (pre-paper original design)

---

# Section 22 — Project Documentation Files (10 files at root — ALL KEEP) ✅

These are the **canonical paper-era docs** — all should remain:

| File | Purpose | Action |
|---|---|---|
| `PROJECT_README.md` | Master entry point | 🟢 KEEP |
| `MASTER_TIMELINE.md` | Canonical chronology | 🟢 KEEP |
| `CONTRIBUTION_LEDGER.md` | Attribution source-of-truth | 🟢 KEEP |
| `AUDIT_REPORT_S13.6.md` | Last audit | 🟢 KEEP |
| `PAPER.md` | The paper itself (v0.7) | 🟢 KEEP |
| `PAPER_PROTOCOL.md` | Working rules v2.0 | 🟢 KEEP |
| `README.md` | Layer A overview (still useful as Layer A entry) | 🟢 KEEP |
| `.gitignore` | Required | 🟢 KEEP |
| `pyproject.toml` | Required | 🟢 KEEP |
| `.env.example` | Required | 🟢 KEEP |

---

# Section 23 — Active Code (KEEP ALL) ✅

| Item | Purpose | Action |
|---|---|---|
| `genesis/` | Layer B code | 🟢 KEEP |
| `tools/` | Active tooling (api_key_pool, providers, etc.) | 🟢 KEEP |
| `tests/` | 23 test files, 463 tests passing (Note: many test `virtual_genesis` not `genesis` — see Section 13 implications) | 🟢 KEEP (with note) |
| `tasks/gpqa_subset_20/` | Active benchmark | 🟢 KEEP |
| `scripts/setup_keys_local.sh.example` | Setup helper | 🟢 KEEP |
| `run_openrouter_benchmark.py` | Active runner | 🟢 KEEP |
| `push_runs.sh` | Operational script (the file-permission diff issue — not agent work; leave it) | 🟢 KEEP |

---

# Section 24 — `PAPER/` Directory (KEEP ALL) ✅

Every file under `PAPER/` is paper-era and active. No cleanup needed.

---

# Section 25 — Foundational Theory Docs Referenced From Paper (KEEP ALL) ✅

The 18 GENESIS_*_AR.md files that ARE referenced from paper-era docs (Theory-08/10 originators, T5.92/93/94 thefts, Meta-Theory, etc.) all stay.

---

# 📊 Summary by recommended action

| Action | Files | Approximate size |
|---|---|---|
| 🟢 KEEP as-is | ~30 files (paper-era + active + referenced foundational) | ~500 KB |
| 🟡 ARCHIVE (move to `archive/`) | ~90 files (Layer A docs + waves + cycles + prototypes) | ~1.2 MB |
| 🟠 MERGE-VERIFY then ARCHIVE | 7 theft wave files | ~95 KB |
| 🔴 DELETE | 1 file (`test_pioneer.py` — dead dep) | ~2 KB |
| ⚪ UNCERTAIN (Fares decision) | `virtual_genesis/` directory + Section 10/12 specs | ~96 MB + ~200 KB |

**Net effect if all 🟡 + 🔴 actions taken:** repo root .md count drops from 134 → ~40 (~30% of current). Main `archive/` subdir holds ~95 files cleanly labeled by Layer A category. **Total disk savings depend on `virtual_genesis/` decision** (95+ MB possible).

---

# 🗂️ Proposed `archive/` structure (if Fares approves)

```
archive/
├── README.md                                  # explains "These are Layer A pre-paper artifacts"
├── layer_a_prototype_evidence/               # Section 1 + 2 (16 files)
├── layer_a_selectivity/                      # Section 2 (8 files)
├── layer_a_evaluation/                       # Section 3 (10 files)
├── layer_a_cycles/                           # Section 4 (6 files)
├── layer_a_snapshots/                        # Section 5 (4 files, RENAMED to remove "Current")
├── layer_a_theft_waves/                      # Section 6 (7 files, AFTER merge-verify)
├── layer_a_old_paper_drafts/                 # Section 7 (6 files)
├── layer_a_planning/                         # Section 8 (7 files)
├── layer_a_minimal_starters/                 # Section 9 (4 files)
├── layer_a_task_framing/                     # Section 16 (3 files)
├── layer_a_infra/                            # Section 17 partial (2 files)
├── layer_a_strategic_plans/                  # Section 14 (2 files)
├── layer_a_results/                          # Section 19 partial (subdirs)
└── (optional) virtual_genesis_results/       # If Section 13 Option B chosen (96 MB JSONs)
```

Each subdirectory should contain a small README.md saying:
> "Layer A pre-paper artifacts. Authoritative paper is at `../../PAPER.md` v0.7+. See `PROJECT_README.md` for current project structure."

---

# 🎯 Decision request for Fares

For each section above, Fares to indicate one of:
- ✅ **Yes, do the recommended action**
- ❌ **No, keep as-is**
- ✏️ **Different action: [specify]**

Or alternatively, Fares can give a **blanket policy**:
- **Policy A:** "نفّذ كل الـ recommendations" (execute all)
- **Policy B:** "نفّذ ARCHIVE فقط، ما تحذفش حاجة" (archive everything, delete nothing)
- **Policy C:** "ابدأ بالـ critical فقط (Section 13 virtual_genesis decision + Section 15 dead code)" (start with critical only)
- **Policy D:** "خلي كل حاجة زي ما هي، ده فقط reference inventory" (keep everything; this is just reference inventory)

---

# ⚠️ Important notes before any action

1. **Nothing is deleted/moved without explicit Fares authorization.** This document is inventory only.
2. **Git history preserves everything** — even if a file is deleted from the working tree, it exists in git history forever. So "delete" decisions can always be reversed via `git show <hash>:path/to/file`.
3. **`archive/` is in working tree** (not deleted) — files moved there remain visible and grepable, just out of the main namespace.
4. **The 3 critical fixes from S13.6 audit (PAPER.md header / authors / table count) are unrelated to this cleanup** — they were active misrepresentations that needed immediate fixing.
5. **`AGENT_OPERATING_MANUAL.md` (the companion deliverable for this session, see below)** documents the rules so future agents do not create more cleanup debt.
