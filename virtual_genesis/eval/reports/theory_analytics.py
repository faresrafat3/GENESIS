from __future__ import annotations

from typing import Any, Dict, List


def generate_theory_analytics(theories: List[dict]) -> Dict[str, Any]:
    family_counts: Dict[str, int] = {}
    mechanism_claim_count = 0
    predictive_claim_count = 0
    prescriptive_implication_count = 0

    for theory in theories:
        scopes = theory.get("scope", {}).get("task_families", [])
        for fam in scopes:
            family_counts[fam] = family_counts.get(fam, 0) + 1
        mechanism_claim_count += len(theory.get("mechanism_claims", []) or [])
        predictive_claim_count += len(theory.get("predictive_claims", []) or [])
        prescriptive_implication_count += len(theory.get("prescriptive_implications", []) or [])

    return {
        "theory_count": len(theories),
        "family_counts": family_counts,
        "mechanism_claim_count": mechanism_claim_count,
        "predictive_claim_count": predictive_claim_count,
        "prescriptive_implication_count": prescriptive_implication_count,
    }
