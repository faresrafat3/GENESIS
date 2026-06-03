# GENESIS - Concept Engine Deep Analysis
# التحليل المعمق لمحرك المفاهيم

> Document Type: Architecture and Design Analysis
> Status: Current Regime (Frozen)
> Date: 2026-05-31

---

## 1. Architecture Overview

The Concept Engine is the subsystem responsible for forming, storing, and activating learned concepts that improve task performance without scaling the underlying model. It consists of six modules located in `virtual_genesis/runtime/concept_engine/`:

### Module Map

| Module | File | Role |
|--------|------|------|
| Selector | `selector.py` | Builds contrastive groups from episodic memory |
| Proposer | `proposer.py` | Creates ConceptCandidate objects from groups |
| Registry | `registry.py` | InMemoryConceptRegistry stores candidates and promoted ConceptCards |
| Apply | `apply.py` | Scores and selects applicable concepts at query time |
| Config | `config.py` | Defines family selectivity policies and strategy descriptors |
| Cycle | `cycle.py` | Orchestrates the full concept formation pipeline |

### Data Flow

```
episodic memories -> selector.build_contrastive_groups()
    -> proposer.propose_concepts_from_groups()
        -> scope.draft_scope()
            -> registry.add_candidate()
                -> proposer.promote_candidate()
                    -> registry.add_concept()
```

At query time:
```
task (family, text, contract) -> apply.select_applicable_concepts()
    -> retriever.retrieve_memory() caps by family max_active
        -> BlackboardMemoryPack with concept_refs + concept_hints
```

---

## 2. Module Details

### 2.1 Selector (`selector.py`)

The `build_contrastive_groups()` function takes a list of `MemoryUnit` objects and identifies three types of contrastive groups:

1. **family_contrast** - Groups episodes by task_family, splitting into success/failure buckets based on `meta.good_enough`. A group is created when both successes and failures exist for a family.

2. **property_gap** - Groups by (family, required_property) tuple, using `meta.property_checks` to determine pass/fail. Creates a group when both passing and failing episodes exist, or when there are at least 2 failures.

3. **shortcut_gap** - Groups by (family, forbidden_shortcut) tuple, using `meta.shortcut_checks` to detect violations. Same creation threshold as property_gap.

### 2.2 Proposer (`proposer.py`)

The `propose_concepts_from_groups()` function maps each contrastive group to a `ConceptCandidate` using family-specific templates:

- **comparison** family_contrast produces "Evidence Sufficiency Contrast" - emphasizes forcing evidence-backed contrast instead of generic preference.
- **synthesis** family_contrast produces "Ungrounded Synthesis Risk" - emphasizes anchoring conclusions to observed evidence.
- **procedure** family_contrast produces "Stable Procedure Reuse Opportunity" - favors checklist/workflow reuse over regeneration.

Property gap and shortcut gap candidates are dynamically named (e.g., "Comparison Evidence_strength Gap", "Synthesis Summary_without_distinction Avoidance").

The `promote_candidate()` function converts a candidate into a `ConceptCard` by assigning an `operational_meaning` string and setting initial `confidence_score=0.6` and `transfer_score=0.3`.

### 2.3 Registry (`registry.py`)

`InMemoryConceptRegistry` provides two-level storage:

- **Candidates** (`_candidates` dict, indexed by `_candidate_name_index`) - deduplicates by `proposed_name`; if a name already exists, returns the existing candidate without creating a duplicate.
- **Concepts** (`_concepts` dict, indexed by `_concept_name_index`) - same deduplication logic for promoted ConceptCards.

This ensures that repeated concept cycles do not inflate the registry with redundant entries.

### 2.4 Apply (`apply.py`)

The `select_applicable_concepts()` function is the query-time scoring engine. Its signature:

```python
select_applicable_concepts(
    task_family: str,
    task_text: str,
    concepts: Iterable[ConceptCard],
    limit: int | None = None,
    min_overlap: int | None = None,
    min_activation_score: int | None = None,
    task_contract: Mapping[str, Any] | None = None,
) -> tuple[List[ConceptCard], List[ConceptActivationDecision]]
```

**Selection logic:**

1. Filter concepts whose `scope.task_families` includes the current `task_family`.
2. Tokenize `task_text` and extract `contract_tokens` from `task_contract` (required_properties, forbidden_shortcuts, diagnostic_purpose).
3. Compute per-concept scores using the family strategy (see Section 3).
4. Sort by score descending.
5. Apply redundancy penalty (1 if token overlap with previously-selected concept >= 4).
6. Select concepts that meet both `fam_min_score` and `fam_limit` constraints.

The function also handles strategy-specific secondary selection rules (see Section 3).

### 2.5 Config (`config.py`)

Frozen defaults as of current regime:

```python
DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS = 1
DEFAULT_MIN_OVERLAP = 2
DEFAULT_MIN_ACTIVATION_SCORE = 7

DEFAULT_FAMILY_SELECTIVITY = {
    'comparison': {'max_active': 1, 'min_score': 7},
    'synthesis': {'max_active': 1, 'min_score': 7},
    'procedure': {'max_active': 0, 'min_score': 99},
}

FAMILY_SELECTIVITY_STRATEGY = {
    'comparison': 'contract_heavy',
    'synthesis': 'semantic_balanced',
    'procedure': 'structural_only',
}
```

### 2.6 Cycle (`cycle.py`)

The `run_concept_cycle()` function orchestrates the full formation pipeline:

```python
def run_concept_cycle(memory_store, registry) -> dict:
    groups = build_contrastive_groups(memory_store.all())
    candidates = propose_concepts_from_groups(groups)
    for candidate in candidates:
        candidate = draft_scope(candidate)
        registered_candidate = registry.add_candidate(candidate)
        if registered_candidate.recommendation == "validate_as_concept":
            concept = promote_candidate(registry, registered_candidate.id)
    return { group_count, candidate_count, promoted_count, concept_ids }
```

---

## 3. Family-Specific Selectivity Design

### 3.1 The Three Strategies

| Strategy | Family | Scoring | Rationale |
|----------|--------|---------|-----------|
| `contract_heavy` | comparison | `family_fit(2) + contract_fit*2 + semantic_fit` | Comparison tasks benefit most from explicit contract alignment; doubling contract weight prioritizes concepts that match task requirements |
| `semantic_balanced` | synthesis | `family_fit(2) + contract_fit + semantic_fit` | Synthesis tasks need broader conceptual support; balanced weighting avoids over-indexing on a single dimension |
| `structural_only` | procedure | `family_fit(2) + contract_fit + semantic_fit` | Procedure tasks currently receive zero concepts by default (max_active=0); the formula exists only for the high-threshold fallback |

### 3.2 Strategy-Specific Selection Rules

- **semantic_balanced**: If `fam_limit >= 2` and exactly 1 concept is already selected, a secondary concept can be admitted if its adjusted score meets `fam_min_score`. This allows synthesis tasks to benefit from two complementary concepts.
- **structural_only**: If no concept has been selected, allows exactly 1 concept if its adjusted score exceeds 10 (the high-threshold fallback). This prevents noisy activation for procedure tasks while permitting an overwhelmingly strong concept.
- **contract_heavy**: Strict top-N only. No secondary admission rules.

### 3.3 Rationale for Current Defaults

The family selectivity ablation (72 tasks, v3b_curriculum) demonstrated:

- `current_default` (comparison top1/7, synthesis top1/7, procedure top0): concept_success=0.986, activation_rate=0.653
- `synthesis_top2` (allow 2 concepts for synthesis): identical success and activation rate - no benefit
- `procedure_top1` (enable concepts for procedure): same success but higher activation_rate (0.708) - additional noise without improvement
- `synthesis_top2_procedure_top1`: same success, higher activation_rate (0.708) - combined permissive policy does not help

Conclusion: the conservative default already captures the full benefit.

---

## 4. Scoring Formula

The activation score for each candidate concept is computed as:

```
activation_score = family_fit + contract_fit_weighted + semantic_fit - redundancy_penalty
```

Where:
- **family_fit** = 2 (constant; awarded if the concept's scope includes the current task family)
- **contract_fit_weighted** = `contract_fit * weight` where weight = 2 for contract_heavy, 1 otherwise
  - `contract_fit` = number of shared tokens between concept definition and task contract fields (required_properties, forbidden_shortcuts, diagnostic_purpose)
- **semantic_fit** = number of shared tokens between concept text (name + definition + operational_meaning) and task text
- **redundancy_penalty** = 0 or 1 (1 if the concept overlaps >= 4 tokens with any already-selected concept)

A concept is selected when:
1. `activation_score >= fam_min_score` (default: 7)
2. The number of selected concepts is below `fam_limit` (default: 1 for comparison/synthesis, 0 for procedure)
3. At least one of: `semantic_fit >= min_overlap` (default: 2) or `contract_fit > 0`

---

## 5. Integration with Retriever

The retriever (`virtual_genesis/runtime/memory_os/retriever.py`) calls `select_applicable_concepts()` in a multi-family loop:

```python
for family in candidate_families:
    selected, decisions = select_applicable_concepts(
        family, task_text, concept_items, task_contract=task_contract
    )
    # deduplicate across families
    for c in selected:
        if c.id not in seen:
            family_selected.append(c)
```

After the loop, the retriever caps the total selected concepts:

```python
primary_family_cfg = DEFAULT_FAMILY_SELECTIVITY.get(task_family, {})
family_max_active = primary_family_cfg.get('max_active', DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS)
applicable_concepts = family_selected[:family_max_active]
```

This means:
- The per-family selection respects each family's own `max_active` and `min_score`.
- The global cap is determined by the primary task family's `max_active` setting.
- Deduplication prevents the same concept from being counted twice when it appears across multiple candidate families.

The selected concepts are then embedded into the `BlackboardMemoryPack` as `concept_refs` (IDs for traceability) and `concept_hints` (name + operational_meaning strings for downstream reasoning).

---

## 6. Known Limitations

1. **Deterministic activation decisions** - Concept activation is purely rule-based (token overlap scoring). There is no learned model or feedback loop that refines activation thresholds based on outcome data.

2. **No concept decay** - Once promoted, a ConceptCard remains in the registry indefinitely. There is no mechanism to reduce confidence or retire concepts that stop being useful.

3. **Procedure family gets zero concepts by default** - The `structural_only` strategy with `max_active=0` and `min_score=99` effectively disables concept activation for procedure tasks. The high-threshold fallback (score >= 10) is reachable in theory but has not fired in practice across current eval sets.

4. **No cross-family transfer** - A concept scoped to `comparison` cannot benefit a `synthesis` task, even when the underlying pattern is relevant to both families.

5. **Token-based scoring is vocabulary-sensitive** - The scoring depends on exact token overlap, making it sensitive to wording variations that preserve meaning but change vocabulary.

6. **No warmup cost amortization model** - The warmup phase (running concept cycles on training episodes) has a fixed cost that is not factored into the economy comparison.

---

## 7. Summary of Key Design Decisions

| Decision | Value | Evidence |
|----------|-------|----------|
| Global max active concepts | 1 | Selectivity ablation: top2 does not improve success |
| Min activation score | 7 | Score 7 gives same success as 6 while maintaining cleaner activation |
| Comparison strategy | contract_heavy | Aligns concept scoring with task contract requirements |
| Synthesis strategy | semantic_balanced | Broader token matching suits multi-fragment reasoning |
| Procedure default | disabled (max_active=0) | Enabling procedure concepts raises activation_rate 0.653->0.708 with zero success gain |

---

*End of Concept Engine Deep Analysis*
