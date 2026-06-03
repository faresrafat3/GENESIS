from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


def _make_bucket():
    return {
        "task_count": 0,
        "contradiction_tasks": 0,
        "anomaly_tasks": 0,
        "theory_tasks": 0,
    }


def _finalize(buckets: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, b in buckets.items():
        count = b["task_count"]
        out[key] = {
            "task_count": count,
            "contradiction_task_rate": (b["contradiction_tasks"] / count) if count else 0.0,
            "anomaly_task_rate": (b["anomaly_tasks"] / count) if count else 0.0,
            "theory_hint_task_rate": (b["theory_tasks"] / count) if count else 0.0,
        }
    return out


def generate_governance_curriculum_analytics(task_results: List[dict]) -> Dict[str, Any]:
    by_level = defaultdict(_make_bucket)
    by_perturbation = defaultdict(_make_bucket)

    for run in task_results:
        task_meta = run.get("task", {}).get("meta", {}) or {}
        env = task_meta.get("normalized_envelope", {}) or {}
        meta = env.get("meta", {}) or {}
        level = str(meta.get("curriculum_level", "base"))
        perturb = meta.get("perturbation_type", "base")
        contradictions = run.get("blackboard", {}).get("contradictions", []) or []
        anomalies = run.get("anomaly_candidates", []) or []
        theory_hints = run.get("blackboard", {}).get("retrieved_memory_pack", {}).get("theory_hints", []) or []

        for bucket in (by_level[level], by_perturbation[perturb]):
            bucket["task_count"] += 1
            bucket["contradiction_tasks"] += int(bool(contradictions))
            bucket["anomaly_tasks"] += int(bool(anomalies))
            bucket["theory_tasks"] += int(bool(theory_hints))

    return {
        "by_level": _finalize(by_level),
        "by_perturbation": _finalize(by_perturbation),
    }
