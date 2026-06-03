from __future__ import annotations

from typing import List, Optional

from .compare_conditions import compare_conditions
from ..reports.anomaly_candidates import generate_anomaly_candidate_report
from ..reports.blind_spot_discovery import discover_blind_spots
from ..reports.diagnostic_value import compute_diagnostic_value_report
from ..benchmark_generator import generate_from_anomaly_candidates


_DEFAULT_CONDITIONS = ["baseline_0", "baseline_1", "condition_c_combined"]


def run_self_benchmark_cycle(
    task_cases: list,
    conditions: list[str] | None = None,
    use_self_benchmarking: bool = True,
) -> dict:
    """Run a self-benchmarking cycle.

    1. Run current eval via compare_conditions
    2. Analyze for anomaly candidates
    3. Discover blind spots
    4. Generate new benchmark cases from anomalies
    5. Run conditions against new cases
    6. Compute diagnostic values
    7. Return combined report
    """
    condition_ids = conditions or _DEFAULT_CONDITIONS

    # Step 1: Run current eval
    base_results = compare_conditions(condition_ids, task_cases)

    if not use_self_benchmarking:
        return {
            "base_results": base_results,
            "self_benchmarking_enabled": False,
        }

    # Step 2: Analyze for anomaly candidates
    # Collect all task results across conditions
    all_task_results: List[dict] = []
    all_results_by_condition: dict = {}
    for cond_id, cond_result in base_results.items():
        task_results = cond_result.get("task_results", [])
        all_task_results.extend(task_results)
        all_results_by_condition[cond_id] = task_results

    anomaly_report = generate_anomaly_candidate_report(all_task_results)

    # Collect individual anomaly candidate dicts
    anomaly_candidates: List[dict] = []
    for result in all_task_results:
        for candidate in result.get("anomaly_candidates", []) or []:
            anomaly_candidates.append(candidate)

    # Step 3: Discover blind spots
    blind_spot_report = discover_blind_spots(all_task_results, task_cases)

    # Step 4: Generate new benchmark cases from anomalies
    new_cases = generate_from_anomaly_candidates(anomaly_candidates)

    # Step 5: Run conditions against new cases (if any were generated)
    new_results = {}
    if new_cases:
        new_results = compare_conditions(condition_ids, new_cases)

    # Step 6: Compute diagnostic values for all cases
    # Combine base and new results by condition
    combined_by_condition: dict = {}
    for cond_id in condition_ids:
        combined_by_condition[cond_id] = list(
            base_results.get(cond_id, {}).get("task_results", [])
        )
        if new_results:
            combined_by_condition[cond_id].extend(
                new_results.get(cond_id, {}).get("task_results", [])
            )

    diagnostic_report = compute_diagnostic_value_report(combined_by_condition)

    # Step 7: Return combined report
    return {
        "self_benchmarking_enabled": True,
        "base_results": base_results,
        "anomaly_report": anomaly_report,
        "anomaly_candidates_count": len(anomaly_candidates),
        "blind_spot_report": blind_spot_report,
        "new_cases_generated": len(new_cases),
        "new_results": new_results,
        "diagnostic_report": diagnostic_report,
    }
