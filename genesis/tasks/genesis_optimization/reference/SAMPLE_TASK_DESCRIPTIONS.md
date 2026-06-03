# Sample Tasks

## Task 1: Concept Generalization Refinement
- **Input:** `virtual_genesis/runtime/concept_engine/builder.py`
- **Objective:** Modify the concept generalized prompt builder to strictly extract structured evidence and avoid speculative extensions.
- **Expected Outcome:** High specificity in concept formation, zero unit test failures in `tests/test_concept_engine.py`.

## Task 2: Cognitive Budget Allocation
- **Input:** `virtual_genesis/runtime/economy_control/router.py`
- **Objective:** Implement a dynamic cost-latency trade-off formula to decide between cheap (Tier 1) and premium (Tier 2/3) models.
- **Expected Outcome:** Optimal performance vs. token consumption balance.
