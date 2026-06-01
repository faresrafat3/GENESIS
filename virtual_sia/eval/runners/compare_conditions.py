from __future__ import annotations

from typing import Dict, Iterable

from .run_condition import run_condition


def compare_conditions(
    condition_ids: list[str],
    tasks: Iterable[str],
    task_set_ref: str = "local_dev",
    *,
    use_theory_leverage: bool = False,
    use_anomaly_leverage: bool = False,
) -> Dict[str, dict]:
    results: Dict[str, dict] = {}
    task_list = list(tasks)
    for condition_id in condition_ids:
        run = run_condition(
            condition_id,
            task_list,
            task_set_ref=task_set_ref,
            use_theory_leverage=use_theory_leverage,
            use_anomaly_leverage=use_anomaly_leverage,
        )
        results[condition_id] = run.to_dict()
    return results
