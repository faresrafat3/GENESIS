# Virtual SIA - Current Regime Status
# حالة النظام الحالي

> Document Type: Stabilization Package
> Status: Frozen Regime
> Date: 2026-05-31
> Phase: Option B - Stabilize and Package (from Decision Memo)

---

## 1. Frozen Defaults

The following configuration values are frozen as the current operating regime. Changes require new evaluation evidence.

### 1.1 Concept Engine Configuration

Source: `virtual_sia/runtime/concept_engine/config.py`

```python
DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = 1
DEFAULT_MIN_OVERLAP = 2
DEFAULT_MIN_ACTIVATION_SCORE = 7
```

### 1.2 Family-Specific Selectivity

```python
DEFAULT_FAMILY_SELECTIVITY = {
    'comparison': {'max_active': 1, 'min_score': 7},
    'synthesis': {'max_active': 2, 'min_score': 7},
    'procedure': {'max_active': 0, 'min_score': 99},
}

FAMILY_SELECTIVITY_STRATEGY = {
    'comparison': 'contract_heavy',
    'synthesis': 'semantic_balanced',
    'procedure': 'structural_only',
}
```

### 1.3 Rationale for Frozen Values

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Global max_active | 1 | Selectivity ablation: top2 gives identical success (0.986) and activation_rate (0.653) as top1 |
| Min activation score | 7 | Score 6 and score 7 produce identical results on current concept set; 7 is more conservative for future growth |
| Comparison max_active | 1 | Family ablation: current_default already achieves maximum success |
| Synthesis max_active | 2 | Raised to enable secondary concept admission when a competitive second concept exists via semantic_balanced strategy |
| Procedure max_active | 0 | procedure_top1 raises activation_rate (0.653 to 0.708) without improving success |
| Comparison strategy | contract_heavy | Contract alignment is the primary distinguishing signal for comparison tasks |
| Synthesis strategy | semantic_balanced | Broader token matching suits multi-source integration tasks |
| Procedure strategy | structural_only | Conservative - procedure concepts not yet proven beneficial |

---

## 2. Current Best Path

### 2.1 Optimal Operating Condition

**condition_c_combined** (concept-aware + economy-aware tier routing) is the current best operating path:

- Success rate: 0.986 (v3b_curriculum, 72 tasks)
- Average inference cost: 0.00068 per task
- Versus premium-always: +12.5pp success at 14.7x lower cost
- Versus baseline (retrieval-only): +19.4pp success at same cost order

### 2.2 Curriculum-Based Evaluation

The evaluation operates under a `TaskCase`-based curriculum model:

1. Tasks are organized by family (comparison, synthesis, procedure)
2. Each family has 4 difficulty levels in the curriculum
3. The warmup phase runs concept cycles on all curriculum tasks to build the concept registry
4. Post-warmup: 8 concepts + 4 theories available for activation
5. At inference time, concepts are selected per-family using the frozen selectivity configuration

### 2.3 Tier Routing Logic

The economy-aware tier router (condition_b / condition_c):
- Defaults to standard model (cost=0.001)
- Escalates to premium model (cost=0.010) when estimated difficulty exceeds threshold
- On v3b_curriculum: escalates 13 out of 72 tasks (18% escalation rate)
- Combined with concepts, escalation drops to 0 tasks (concepts handle the difficulty)

---

## 3. What Remains Open

### 3.1 Synthesis Top-2 Policy

**Status**: Enabled (max_active=2).

- Raised synthesis to max_active=2 to enable secondary concept admission when a competitive second concept exists
- The semantic_balanced strategy admits a secondary concept if it also exceeds the min_score threshold
- Result on current concept set: identical success (0.986) and identical activation rate (0.653) since no competitive second candidate exists yet
- **Decision**: Keep synthesis at max_active=2 so the secondary admission path is available as the concept set grows

### 3.2 Procedure Concept Activation

**Status**: Currently disabled (max_active=0).

- procedure_top1 configuration increases activation_rate from 0.653 to 0.708
- No improvement in success rate
- Procedure tasks rely on structural workflow reuse rather than concept-guided reasoning
- **Decision**: Leave disabled until evidence shows concept activation improves procedure outcomes

### 3.3 Governance-to-Control Bridge

**Status**: Not yet implemented.

- The governance layer (theory runtime, anomaly detection) currently operates independently
- A bridge to control concept formation (e.g., governance can veto concept promotion) is architecturally planned
- **Decision**: Deferred to next cycle - requires design specification before implementation

### 3.4 V4 Classification Accuracy

**Status**: Known limitation.

- Top-1 match rate is 0.667 on v4's deliberately ambiguous tasks
- Top-2 match rate is 0.917, showing the ranker identifies the correct family within its top 2
- The 50% ambiguity rate means many tasks genuinely belong to multiple families
- **Decision**: Accept as a characteristic of the diagnostic slice. The top-2 performance is adequate for concept selection.

### 3.5 Cross-Family Concept Transfer

**Status**: Not yet explored.

- Currently each concept is scoped to exactly one family
- A concept like "Evidence Sufficiency Contrast" could potentially benefit both comparison and synthesis
- **Decision**: Deferred. Requires new eval slice that tests transfer scenarios.

---

## 4. Evidence Confidence Assessment

### 4.1 Thesis 1: Concept Formation Beats Retrieval-Only

| Dimension | Assessment |
|-----------|-----------|
| Signal strength | +19.4pp on primary slice (0.792 to 0.986) |
| Consistency | Positive across v2, v3, v3b, v3b_curriculum, v3c_curriculum |
| Cost parity | Yes - concept-aware runs at same cost as baseline (0.001/task) |
| Exceptions | v4 diagnostic shows no separation (expected - high ambiguity blocks activation) |
| Overall confidence | **Moderate-to-high** |

**Caveats**: The evaluation is simulated (deterministic contract checking rather than live LLM output). The concept set is small (8-11 concepts). The task families are limited to comparison/synthesis/procedure.

### 4.2 Thesis 2: Cognitive Economy Matches Premium

| Dimension | Assessment |
|-----------|-----------|
| Signal strength | Equal success at 4-6x lower cost across all slices |
| Consistency | Perfect across every evaluated slice |
| Combined effect | When paired with concepts: 14.7x cost reduction with +12.5pp improvement |
| Exceptions | None observed |
| Overall confidence | **High** |

**Caveats**: The cost model is simplified (two discrete tiers). Real-world API pricing may differ. The escalation heuristic has not been tested against streaming or latency-sensitive workloads.

---

## 5. Next Cycle Options

From the Decision Memo (Option B stabilization), the following cycles are available:

### 5.1 Concept Leverage Cycle

**Goal**: Increase the benefit derived from existing concepts.

- Explore cross-family concept transfer
- Test concept combinations (when max_active > 1 becomes relevant)
- Add concept confidence decay based on activation outcomes
- Estimated effort: Medium

### 5.2 Governance Control Cycle

**Goal**: Connect governance runtime to concept formation decisions.

- Implement governance veto on concept promotion
- Add anomaly-triggered concept re-evaluation
- Build the theory-to-concept feedback loop
- Estimated effort: High

### 5.3 Broader Domain Cycle

**Goal**: Validate findings beyond the current three families.

- Design v5 task set with new families (classification, extraction, generation)
- Test whether concept formation advantage transfers to unfamiliar domains
- Measure whether the economy advantage holds with larger task diversity
- Estimated effort: Medium-High

### 5.4 Live Model Validation Cycle

**Goal**: Move from simulated evaluation to live LLM-backed verification.

- Replace deterministic contract checking with actual LLM output evaluation
- Measure real latency and cost under API constraints
- Validate that simulated success rates correspond to real performance
- Estimated effort: High (requires API budget)

---

## 6. Regime Summary Table

| Category | Item | Value | Status |
|----------|------|-------|--------|
| Config | max_active_concepts | 1 | Frozen |
| Config | min_activation_score | 7 | Frozen |
| Config | min_overlap | 2 | Frozen |
| Config | comparison strategy | contract_heavy | Frozen |
| Config | synthesis strategy | semantic_balanced | Frozen |
| Config | procedure activation | disabled | Frozen |
| Eval | primary slice | v3b_curriculum (72 tasks) | Active |
| Eval | diagnostic slice | v4 (12 tasks) | Active |
| Eval | stress slice | v3c_curriculum (72 tasks) | Active |
| Result | best success | 0.986 (combined) | Verified |
| Result | best cost | 0.00068/task (combined) | Verified |
| Result | concept count post-warmup | 8 | Stable |
| Result | theory count post-warmup | 4 | Stable |
| Thesis | Thesis 1 confidence | Moderate-to-high | Documented |
| Thesis | Thesis 2 confidence | High | Documented |
| Open | synthesis top-2 | Enabled (max_active=2), no second candidate yet | Monitor |
| Open | procedure concepts | No benefit observed | Monitor |
| Open | governance bridge | Not implemented | Deferred |
| Open | cross-family transfer | Not explored | Deferred |

---

## 7. Expanded Evaluation Regime (Cycle 2 - Evaluation Pressure)

> Added: 2026-06-01
> Source: Evaluation Pressure Cycle (Option C)

### 7.1 New Perturbation Operators

Five new operators added to `virtual_sia/eval/perturbations/taskcase_variants.py`:

| Operator | Function | Theft Source |
|----------|----------|-------------|
| `support_removal` | Removes supporting evidence phrases | 5.24 - Zeiler & Fergus |
| `evidence_reordering` | Shuffles sentence order | 5.25 - Hogarth & Einhorn |
| `contrast_weakening` | Replaces strong contrast words with weaker ones | 5.26 - Nie et al. / Gardner et al. |
| `structure_weakening` | Removes structural cues (numbering, lists) | 5.27 - Mann & Thompson |
| `stronger_shortcut_lures` | Adds misleading shortcut paths | 5.28 - Goodfellow / Geirhos |

### 7.2 Extended Curriculum (6 Levels)

Source: 5.29 - Bengio et al. (Curriculum Learning)

| Level | Perturbation | Composition |
|-------|-------------|-------------|
| 0 | None | Original task |
| 1 | keyword_noise | Light noise |
| 2 | sentence_injection | Distracting sentence |
| 3 | full_reformulation | Complete rewrite |
| 4 | support_removal + contrast_weakening | Evidence weakening |
| 5 | evidence_reordering + stronger_shortcut_lures + structure_weakening | Maximum compound pressure |

### 7.3 V6 Task Set

- **File**: `virtual_sia/eval/task_sets/prototype_v6_cases.py`
- **Size**: 18 base cases (6 comparison + 6 synthesis + 6 procedure)
- **Curriculum output**: 108 cases (18 x 6 levels)
- **Runner**: `virtual_sia/eval/runners/run_local_eval_v6.py`
- **Difficulty**: Higher than v5, designed to stress-test the system

### 7.4 Perturbation Resistance Report

- **File**: `virtual_sia/eval/reports/perturbation_resistance.py`
- **Source**: 5.30 - Ribeiro et al. (CheckList)
- **Outputs**: success_rate per perturbation_type, per curriculum_level, breaking_point, per-family resistance scores

### 7.5 Anti-Shortcut Benchmark

- **File**: `virtual_sia/eval/task_sets/anti_shortcut_benchmark.py`
- **Source**: 5.28 - Goodfellow / Geirhos
- **Size**: 9 cases (3 per family)
- **Purpose**: Tasks that can only pass if shortcuts are genuinely avoided

---

## 8. Anomaly Leverage Mechanism (Cycle 2 - Minimal Anomaly Leverage)

> Added: 2026-06-01
> Source: Minimal Anomaly Leverage (Option A)
> Status: Gated behind `use_anomaly_leverage=False` (default OFF)

### 8.1 Anomaly Severity Scoring

- **Function**: `compute_anomaly_severity_score()` in `anomaly_runtime/service.py`
- **Source**: 5.31 - Chandola et al. + 6.8 - Predictive Processing
- **Range**: 0.0 to 1.0
- **Factors**: candidate count, max severity, source_type diversity

### 8.2 Anomaly Pattern Matching

- **Function**: `matches_known_anomaly_pattern()` in `anomaly_runtime/service.py`
- **Source**: 6.3 - Kuhn (anomaly accumulation -> behavioral change)
- **Patterns detected**: property_gap + shortcut co-occurrence, repeated family failures, contradiction clustering

### 8.3 Anomaly-Aware Verification

- **Function**: `verify_output_anomaly_aware()` in `verification_runtime/service.py`
- **Behavior**: When severity > 0.5, requires ALL properties to pass, adds extra markers, raises threshold
- **Source**: 6.3 - Kuhn + 5.30 - Ribeiro CheckList

### 8.4 Anomaly-Aware Economy Routing

- **Function**: `choose_tier_anomaly_aware()` in `economy_control/router.py`
- **Source**: 6.12 - Ashby (Requisite Variety)
- **Behavior**:
  - severity > 0.4: never tier_0 (minimum tier_1)
  - severity > 0.7: forces tier_2

### 8.5 Anomaly-Aware Escalation

- **Function**: `should_escalate_anomaly_aware()` in `economy_control/escalation.py`
- **Source**: 5.32 - PagerDuty/Datadog
- **Behavior**: severity > 0.5 and not tier_2 -> always escalate

### 8.6 Pipeline Integration

- **File**: `virtual_sia/runtime/pipeline/minimal_run.py`
- **Parameter**: `use_anomaly_leverage: bool = False`
- **When enabled**: severity computed from anomaly_candidates, passed to verification/routing/escalation

### 8.7 Gating Decision

The mechanism is OFF by default to:
- Preserve existing frozen behavior
- Allow controlled comparison (with/without)
- Prevent unintended behavioral changes
- Require explicit opt-in for evaluation

---

## 9. New Conditions Available

### 9.1 Evaluation Conditions

| Condition | Description | Status |
|-----------|-------------|--------|
| v6_baseline | V6 tasks, no perturbation | Available |
| v6_curriculum | V6 tasks, all 6 levels | Available |
| v6_anti_shortcut | Anti-shortcut benchmark | Available |
| v6_perturbation_resistance | Full resistance analysis | Available |

### 9.2 Runtime Conditions

| Condition | Description | Status |
|-----------|-------------|--------|
| anomaly_leverage_off | Pipeline with use_anomaly_leverage=False | Default |
| anomaly_leverage_on | Pipeline with use_anomaly_leverage=True | Available (opt-in) |

### 9.3 Relationship to Frozen Defaults

All frozen defaults from Section 1 remain **unchanged**:
- Concept selectivity: unchanged
- Family policies: unchanged
- Tier routing base behavior: unchanged

The new mechanisms are **additive** - they layer on top when explicitly enabled, they do not modify any frozen configuration.

---

## 10. Updated Regime Summary Table

| Category | Item | Value | Status |
|----------|------|-------|--------|
| Config | max_active_concepts | 1 | Frozen |
| Config | min_activation_score | 7 | Frozen |
| Config | min_overlap | 2 | Frozen |
| Config | comparison strategy | contract_heavy | Frozen |
| Config | synthesis strategy | semantic_balanced | Frozen |
| Config | procedure activation | disabled | Frozen |
| Config | use_anomaly_leverage | False | Frozen (default OFF) |
| Config | **use_theory_leverage** | **False** | **Frozen (default OFF)** |
| Eval | primary slice | v3b_curriculum (72 tasks) | Active |
| Eval | diagnostic slice | v4 (12 tasks) | Active |
| Eval | stress slice | v3c_curriculum (72 tasks) | Active |
| Eval | **pressure slice** | **v6_curriculum (108 tasks)** | **New** |
| Eval | **anti-shortcut slice** | **v6_anti_shortcut (9 tasks)** | **New** |
| Eval | **perturbation operators** | **8 total (3 original + 5 new)** | **Expanded** |
| Eval | **curriculum levels** | **6 (was 4)** | **Expanded** |
| Result | best success | 0.986 (combined, v3b) | Verified |
| Result | best cost | 0.00068/task (combined) | Verified |
| Result | concept count post-warmup | 8 | Stable |
| Result | theory count post-warmup | 4 | Stable |
| Runtime | **anomaly severity scoring** | **0.0-1.0 composite** | **New (gated)** |
| Runtime | **anomaly-aware verification** | **stricter when severity > 0.5** | **New (gated)** |
| Runtime | **anomaly-aware routing** | **bias to higher tier** | **New (gated)** |
| Runtime | **anomaly-aware escalation** | **auto-escalate at severity > 0.5** | **New (gated)** |
| Runtime | **theory-guided verification** | **stricter when theory predicts failure** | **New (gated)** |
| Runtime | **theory-guided routing** | **bias to higher tier on theory prediction** | **New (gated)** |
| Runtime | **theory-guided concept activation** | **boost + admission for theory-aligned concepts** | **New (gated)** |
| Runtime | **theory predictive value** | **Laplace-smoothed accuracy (0.0-1.0)** | **New (gated)** |
| Runtime | **theory-contradiction interaction** | **explanatory_power accumulation** | **New (gated)** |
| Thesis | Thesis 1 confidence | Moderate-to-high | Documented |
| Thesis | Thesis 2 confidence | High | Documented |
| Open | synthesis top-2 | Enabled (max_active=2), no second candidate yet | Monitor |
| Open | procedure concepts | No benefit observed | Monitor |
| Open | governance bridge | **Further implemented via theory leverage** | **Updated** |
| Open | cross-family transfer | Not explored | Deferred |

---

## 11. Theory Leverage Mechanism (Cycle 3 - Local Theory Leverage)

> Added: 2026-06-01
> Source: Local Theory Leverage (Option B)
> Status: Gated behind `use_theory_leverage=False` (default OFF)

### 11.1 Theory Predictive Value (B4)

- **Function**: `get_theory_prediction_for_task()` in `theory_runtime/apply.py`
- **Source**: 5.33 - Popper (Falsifiability) + 5.37 - Scientific Realism (Boyd)
- **Behavior**: Generates prediction dict with `predicts_failure`, `predicts_difficulty`, `confidence`, `relevant_claims`
- **Mechanism**: Token overlap between theory.predictive_claims and task_text; confidence = theory.predictive_value
- **Update**: `update_theory_predictive_value()` applies Laplace smoothing: `(correct+1)/(total+2)`
- **Source (Update)**: 5.34 - Bayesian Epistemology (Howson & Urbach)

### 11.2 Theory-Contradiction Interaction (B5)

- **Function**: `check_theory_explains_contradiction()` in `theory_runtime/apply.py`
- **Source**: 6.2 - Lakatos (Research Programmes) + 6.3 - Kuhn (Scientific Revolutions)
- **Behavior**: If theory.predictive_claims tokens overlap contradiction content (threshold 2+ tokens), returns True
- **Side Effect**: theory.explanatory_power += 0.1 (capped at 1.0) on successful explanation
- **Scope Check**: Only applies when contradiction.task_family is in theory.scope.task_families

### 11.3 Theory-Guided Verification (B1)

- **Function**: `verify_output_theory_guided()` in `verification_runtime/service.py`
- **Source**: 6.8 - Predictive Processing (Friston) + 5.33 - Popper
- **Behavior**:
  - When theory predicts failure: requires 2 primary markers AND all properties pass
  - When theory predicts difficulty: requires base evidence AND secondary marker hit
  - When no prediction: returns base verification result unchanged
- **Layering**: When both theory and anomaly leverage active, takes the stricter result

### 11.4 Theory-Guided Concept Activation (B2)

- **Function**: `select_applicable_concepts_theory_guided()` in `concept_engine/apply.py`
- **Source**: 5.35 - Theory-Theory (Gopnik & Wellman) + 5.36 - Explanation-Based Learning (DeJong & Mooney)
- **Behavior**:
  - Concepts in theory.concept_refs get +3 activation score boost [theory_boost]
  - Non-selected concepts within 2 points of fam_min_score get admitted if in theory.concept_refs [theory_admission]
  - Non-aligned concepts remain unchanged

### 11.5 Theory-Guided Routing (B3)

- **Function**: `choose_tier_theory_guided()` in `economy_control/router.py`
- **Source**: 5.34 - Bayesian Epistemology + 5.38 - DevOps Runbook Automation (Google SRE)
- **Behavior**:
  - predicts_difficulty AND confidence >= 0.5: prevents tier_0 (minimum tier_1)
  - predicts_failure AND confidence >= 0.6: forces tier_2
  - No prediction or low confidence: no change from base routing
- **Layering**: When both active, anomaly_severity layers on top of theory-guided decision

### 11.6 Pipeline Integration

- **File**: `virtual_sia/runtime/pipeline/minimal_run.py`
- **Parameter**: `use_theory_leverage: bool = False`
- **When enabled**:
  1. Selects applicable theories for task_family
  2. Generates prediction from first applicable theory
  3. Routes via choose_tier_theory_guided (with anomaly layering if both active)
  4. Selects concepts via select_applicable_concepts_theory_guided (if use_concepts=True)
  5. Verifies via verify_output_theory_guided (with anomaly layering if both active)
  6. Post-processes: updates predictive_value, checks contradiction explanations
- **Return dict additions**: `use_theory_leverage`, `theory_prediction`, `theory_predictive_value`

### 11.7 Gating Decision

The mechanism is OFF by default to:
- Preserve existing frozen behavior (all 88 baseline tests pass unchanged)
- Allow controlled comparison (with/without theory leverage)
- Prevent unintended behavioral changes to verified results
- Require explicit opt-in for evaluation
- Maintain consistency with the anomaly_leverage gating pattern from Cycle 2
- Enable incremental activation: theory_leverage can be enabled independently or combined with anomaly_leverage

---

---

## الدورة الرابعة: التوسع المجالي (Option D) - مكتملة

### ما تم إضافته
- 3 عائلات مهام جديدة: analysis, extraction, planning
- 18 مهمة جديدة عبر العائلات الثلاث في prototype_v7_broader_domain.py
- تقرير النقل المفاهيمي (domain_transfer.py) يقيس انتقال المفاهيم عبر المجالات
- محرك تقييم التوسع المجالي (run_broader_domain_eval.py)
- تهيئة محرك المفاهيم للعائلات الجديدة (selectivity + strategy)
- 37 اختبار جديد (المجموع الحالي: 163 اختبار)

### السرقات الشرعية الجديدة
- 5.39: Bloom's Taxonomy -> عائلة التحليل
- 5.40: Information Extraction (Sarawagi 2008) -> عائلة الاستخراج
- 5.41: Classical AI Planning (STRIPS/PDDL) -> عائلة التخطيط
- 5.42: Transfer Learning (Pan & Yang 2010) -> تقرير النقل المفاهيمي
- 5.43: Curriculum Learning (Bengio et al 2009) -> منهج التوسع المجالي
- 5.44: Meta-Learning (Thrun 1998) -> حكم القابلية للنقل

### الحالة الحالية
- إجمالي السرقات: 5.01 - 5.44
- إجمالي الاختبارات: 163
- الدورات المكتملة: Stabilize, Eval Pressure, Anomaly Leverage, Theory Leverage, Broader Domain

---

*End of Current Regime Status*
