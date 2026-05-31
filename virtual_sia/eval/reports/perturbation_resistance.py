from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

from ...core.objects.task_case import TaskCase


def generate_perturbation_resistance_report(
    task_results: List[dict],
    curriculum_cases: Optional[List[TaskCase]] = None,
) -> Dict[str, Any]:
    """Analyze task results grouped by perturbation_type and curriculum_level.

    Computes:
    - success_rate per perturbation_type
    - success_rate per curriculum_level
    - breaking_point: first level where success drops below 0.8
    - per-family resistance scores

    Legitimate Theft source: Curriculum learning (Bengio et al. 2009) and
    robustness evaluation from adversarial ML. The idea of measuring degradation
    across ordered difficulty is taken from progressive stress testing in
    materials science and adapted for cognitive evaluation.
    """
    # Build a lookup from case metadata if curriculum_cases provided
    case_meta_by_index: Dict[int, Dict[str, Any]] = {}
    if curriculum_cases:
        for idx, case in enumerate(curriculum_cases):
            meta = case.meta or {}
            case_meta_by_index[idx] = {
                "perturbation_type": meta.get("perturbation_type", "none"),
                "curriculum_level": meta.get("curriculum_level", 0),
                "family": case.expected_primary_family,
            }

    # Collect stats by perturbation_type
    by_perturbation: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "success": 0}
    )
    # Collect stats by curriculum_level
    by_level: Dict[int, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "success": 0}
    )
    # Collect stats by family
    by_family: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"total": 0, "success": 0}
    )
    # Combined: family x level
    by_family_level: Dict[str, Dict[int, Dict[str, Any]]] = defaultdict(
        lambda: defaultdict(lambda: {"total": 0, "success": 0})
    )

    for idx, run in enumerate(task_results):
        # Determine success
        verification = run.get("blackboard", {}).get("verification_state", {})
        summary = verification.get("verification_summary", {})
        good = bool(summary.get("good_enough", False))

        # Get metadata from case lookup or from run itself
        if idx in case_meta_by_index:
            meta = case_meta_by_index[idx]
        else:
            task_meta = run.get("task", {}).get("meta", {}) or {}
            meta = {
                "perturbation_type": task_meta.get("perturbation_type", "none"),
                "curriculum_level": task_meta.get("curriculum_level", 0),
                "family": run.get("task", {}).get("task_family", "unknown"),
            }

        ptype = meta["perturbation_type"]
        level = meta["curriculum_level"]
        family = meta["family"]

        by_perturbation[ptype]["total"] += 1
        by_perturbation[ptype]["success"] += int(good)

        by_level[level]["total"] += 1
        by_level[level]["success"] += int(good)

        by_family[family]["total"] += 1
        by_family[family]["success"] += int(good)

        by_family_level[family][level]["total"] += 1
        by_family_level[family][level]["success"] += int(good)

    # Compute success rates per perturbation type
    perturbation_rates: Dict[str, float] = {}
    for ptype, data in by_perturbation.items():
        perturbation_rates[ptype] = (
            data["success"] / data["total"] if data["total"] else 0.0
        )

    # Compute success rates per level
    level_rates: Dict[int, float] = {}
    for level in sorted(by_level.keys()):
        data = by_level[level]
        level_rates[level] = data["success"] / data["total"] if data["total"] else 0.0

    # Compute breaking point: first level where success < 0.8
    breaking_point: Optional[int] = None
    for level in sorted(level_rates.keys()):
        if level_rates[level] < 0.8:
            breaking_point = level
            break

    # Per-family resistance scores (avg success rate across all levels for that family)
    family_resistance: Dict[str, Dict[str, Any]] = {}
    for family, data in by_family.items():
        overall_rate = data["success"] / data["total"] if data["total"] else 0.0
        # Per-level breakdown for this family
        family_levels = {}
        for level in sorted(by_family_level[family].keys()):
            ldata = by_family_level[family][level]
            family_levels[level] = ldata["success"] / ldata["total"] if ldata["total"] else 0.0
        # Family-specific breaking point
        family_bp = None
        for level in sorted(family_levels.keys()):
            if family_levels[level] < 0.8:
                family_bp = level
                break
        family_resistance[family] = {
            "overall_success_rate": overall_rate,
            "per_level_rates": family_levels,
            "breaking_point": family_bp,
        }

    return {
        "total_tasks_analyzed": len(task_results),
        "success_rate_by_perturbation_type": perturbation_rates,
        "success_rate_by_curriculum_level": {str(k): v for k, v in level_rates.items()},
        "breaking_point": breaking_point,
        "family_resistance": family_resistance,
    }
