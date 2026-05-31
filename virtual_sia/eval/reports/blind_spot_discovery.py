from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Tuple


def _extract_combo(result: dict) -> Tuple[str, str, str]:
    """Extract (family, perturbation, difficulty) from a run result."""
    task = result.get("task", {})
    family = task.get("task_family", "unknown")
    # perturbation comes from stress_type or diagnostic_purpose
    perturbation = task.get("stress_type") or "none"
    if perturbation == "none":
        diag = task.get("diagnostic_purpose", [])
        if diag:
            perturbation = diag[0] if isinstance(diag, list) else str(diag)
    difficulty = task.get("difficulty_class", "medium")
    return (family, perturbation, difficulty)


def _extract_combo_from_case(case: object) -> Tuple[str, str, str]:
    """Extract (family, perturbation, difficulty) from a TaskCase object."""
    family = getattr(case, "expected_primary_family", "unknown")
    perturbation = getattr(case, "stress_type", None) or "none"
    if perturbation == "none":
        diag = getattr(case, "diagnostic_purpose", [])
        if diag:
            perturbation = diag[0] if isinstance(diag, list) else str(diag)
    difficulty = getattr(case, "difficulty_class", "medium")
    return (family, perturbation, difficulty)


def _is_success(result: dict) -> bool:
    """Determine if a run result was successful."""
    blackboard = result.get("blackboard", {})
    verification = blackboard.get("verification_state", {})
    summary = verification.get("verification_summary", {})
    return bool(summary.get("good_enough", False))


def discover_blind_spots(all_results: list[dict], all_cases: list) -> dict:
    """Identify untested and suspiciously easy regions.

    Returns dict with:
    - untested_combinations: list of (family, perturbation, difficulty) never tested
    - suspiciously_easy_regions: list of combos with 100% success rate
    - coverage_matrix: dict mapping combo tuples to stats
    - coverage_ratio: float (tested/total possible combos)
    """
    # Build set of all possible combos from all_cases
    all_possible: set = set()
    for case in all_cases:
        combo = _extract_combo_from_case(case)
        all_possible.add(combo)

    # Build coverage matrix from results
    coverage_matrix: Dict[Tuple[str, str, str], Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "success": 0}
    )
    for result in all_results:
        combo = _extract_combo(result)
        all_possible.add(combo)
        coverage_matrix[combo]["total"] += 1
        if _is_success(result):
            coverage_matrix[combo]["success"] += 1

    # Find untested combinations
    tested_combos = set(coverage_matrix.keys())
    untested_combinations: List[Tuple[str, str, str]] = sorted(
        all_possible - tested_combos
    )

    # Find suspiciously easy regions (100% success with at least 1 run)
    suspiciously_easy_regions: List[Tuple[str, str, str]] = []
    for combo, stats in sorted(coverage_matrix.items()):
        if stats["total"] > 0 and stats["success"] == stats["total"]:
            suspiciously_easy_regions.append(combo)

    # Coverage ratio
    if not all_possible:
        coverage_ratio = 1.0
    else:
        coverage_ratio = len(tested_combos) / len(all_possible)

    # Serialize coverage matrix for JSON-friendliness
    serialized_matrix: Dict[str, Dict[str, Any]] = {}
    for combo, stats in coverage_matrix.items():
        key = f"{combo[0]}|{combo[1]}|{combo[2]}"
        serialized_matrix[key] = dict(stats)

    return {
        "untested_combinations": untested_combinations,
        "suspiciously_easy_regions": suspiciously_easy_regions,
        "coverage_matrix": serialized_matrix,
        "coverage_ratio": coverage_ratio,
    }
