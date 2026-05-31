from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional


def generate_domain_transfer_report(
    task_results: List[dict],
    original_families: Optional[List[str]] = None,
    new_families: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Analyze concept transfer across task families.

    Measures whether concepts formed from original families activate on new families.
    Computes transfer coefficients and a family-pair transfer matrix.

    Legitimate Theft source: Transfer learning metrics from domain adaptation
    literature (Ben-David et al. 2010). The concept of measuring activation
    overlap across domains is adapted from cross-domain representation analysis
    in neural transfer learning. What we took: the measurement framework.
    What we left: the neural-network-specific implementation. What we have now:
    a symbolic concept-transfer metric suitable for cognitive agent evaluation.
    """
    original_families = original_families or ['comparison', 'synthesis', 'procedure']
    new_families = new_families or ['analysis', 'extraction', 'planning']

    all_families = original_families + new_families

    # Track concept activations per family
    # concept_activations[family] = total count of concepts used in that family
    concept_activations_per_family: Dict[str, int] = defaultdict(int)
    task_count_per_family: Dict[str, int] = defaultdict(int)

    # Track per-concept activation across families
    # concept_family_counts[concept_id][family] = activation count
    concept_family_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for run in task_results:
        task_info = run.get("task", {})
        family = task_info.get("task_family", "unknown")
        task_count_per_family[family] += 1

        # Count concepts used in this run
        used_concepts_count = run.get("used_concepts_count", 0)
        concept_activations_per_family[family] += used_concepts_count

        # Track individual concept activations if available
        blackboard = run.get("blackboard", {})
        concept_activations = blackboard.get("concept_activations", [])
        for activation in concept_activations:
            concept_id = activation.get("concept_id", "unknown_concept")
            concept_family_counts[concept_id][family] += 1

    # Compute concept activation rate per family (avg concepts per task)
    activation_rate_per_family: Dict[str, float] = {}
    for family in all_families:
        count = task_count_per_family.get(family, 0)
        if count > 0:
            activation_rate_per_family[family] = concept_activations_per_family[family] / count
        else:
            activation_rate_per_family[family] = 0.0

    # Compute transfer coefficients per concept
    # transfer_coefficient = activation_on_new / activation_on_old (capped at concept level)
    transfer_coefficients: List[Dict[str, Any]] = []
    for concept_id, family_counts in concept_family_counts.items():
        old_activations = sum(family_counts.get(f, 0) for f in original_families)
        new_activations = sum(family_counts.get(f, 0) for f in new_families)
        coeff = new_activations / old_activations if old_activations > 0 else (1.0 if new_activations > 0 else 0.0)
        transfer_coefficients.append({
            "concept_id": concept_id,
            "old_activations": old_activations,
            "new_activations": new_activations,
            "transfer_coefficient": coeff,
        })

    # Compute overall transfer rate
    total_old = sum(concept_activations_per_family.get(f, 0) for f in original_families)
    total_new = sum(concept_activations_per_family.get(f, 0) for f in new_families)
    overall_transfer_rate = total_new / total_old if total_old > 0 else (1.0 if total_new > 0 else 0.0)

    # Compute family pair transfer matrix
    # matrix[old_family][new_family] = number of concepts that activated on both
    family_pair_transfer_matrix: Dict[str, Dict[str, int]] = {}
    for old_f in original_families:
        family_pair_transfer_matrix[old_f] = {}
        for new_f in new_families:
            shared_count = 0
            for concept_id, family_counts in concept_family_counts.items():
                if family_counts.get(old_f, 0) > 0 and family_counts.get(new_f, 0) > 0:
                    shared_count += 1
            family_pair_transfer_matrix[old_f][new_f] = shared_count

    # Compute new family success rates
    new_family_success_rates: Dict[str, float] = {}
    for family in new_families:
        successes = 0
        total = 0
        for run in task_results:
            task_info = run.get("task", {})
            if task_info.get("task_family") == family:
                total += 1
                verification = run.get("blackboard", {}).get("verification_state", {})
                summary = verification.get("verification_summary", {})
                if summary.get("good_enough", False):
                    successes += 1
        new_family_success_rates[family] = successes / total if total > 0 else 0.0

    return {
        "concept_activation_rate_per_family": activation_rate_per_family,
        "transfer_coefficients": transfer_coefficients,
        "overall_transfer_rate": overall_transfer_rate,
        "family_pair_transfer_matrix": family_pair_transfer_matrix,
        "new_family_success_rates": new_family_success_rates,
        "task_count": len(task_results),
    }
