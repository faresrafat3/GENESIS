from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def compute_diagnostic_value(case_results_across_conditions: dict[str, bool]) -> float:
    """Compute how well a test case discriminates between conditions.

    Args:
        case_results_across_conditions: maps condition_id -> bool (success/fail)

    Returns:
        0.0 if all conditions have same result (not discriminating)
        approaches 1.0 as spread increases
    """
    if not case_results_across_conditions:
        return 0.0

    values = list(case_results_across_conditions.values())
    n = len(values)
    if n <= 1:
        return 0.0

    # Proportion that succeeded
    success_count = sum(1 for v in values if v)
    p = success_count / n

    # Diagnostic value = 4 * p * (1 - p)
    # This gives 0.0 when all same, 1.0 when split 50/50
    return 4.0 * p * (1.0 - p)


def compute_diagnostic_value_report(all_results_by_condition: dict[str, list[dict]]) -> dict:
    """Compute diagnostic value for all cases across conditions.

    Args:
        all_results_by_condition: maps condition_id -> list of run result dicts

    Returns dict with:
    - case_diagnostic_values: dict mapping case_id -> float
    - avg_diagnostic_value: float
    - low_value_cases: list of case_ids with value < 0.2
    - high_value_cases: list of case_ids with value > 0.8
    """
    # Build per-case results across conditions
    case_condition_results: Dict[str, Dict[str, bool]] = defaultdict(dict)

    for condition_id, results in all_results_by_condition.items():
        for result in results:
            task = result.get("task", {})
            case_id = task.get("id", "")
            if not case_id:
                continue
            blackboard = result.get("blackboard", {})
            verification = blackboard.get("verification_state", {})
            summary = verification.get("verification_summary", {})
            success = bool(summary.get("good_enough", False))
            case_condition_results[case_id][condition_id] = success

    # Compute diagnostic value per case
    case_diagnostic_values: Dict[str, float] = {}
    for case_id, condition_map in case_condition_results.items():
        case_diagnostic_values[case_id] = compute_diagnostic_value(condition_map)

    # Aggregate metrics
    values = list(case_diagnostic_values.values())
    avg_diagnostic_value = sum(values) / len(values) if values else 0.0
    low_value_cases = [cid for cid, v in case_diagnostic_values.items() if v < 0.2]
    high_value_cases = [cid for cid, v in case_diagnostic_values.items() if v > 0.8]

    return {
        "case_diagnostic_values": case_diagnostic_values,
        "avg_diagnostic_value": avg_diagnostic_value,
        "low_value_cases": low_value_cases,
        "high_value_cases": high_value_cases,
    }
