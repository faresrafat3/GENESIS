from __future__ import annotations

import json
import os
from pathlib import Path

from .compare_conditions import compare_conditions
from ..reports.curriculum_analytics import generate_curriculum_analytics
from ..reports.summary import summarize_comparison
from ..task_sets.prototype_v3b_curriculum import PROTOTYPE_V3B_CURRICULUM

DEFAULT_CONDITIONS = [
    "baseline_1",
    "baseline_2_premium_always",
    "condition_a_concept_ready",
    "condition_b_economy",
    "condition_c_combined",
]

CANONICAL_CONDITION = "condition_c_combined"


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def run_local_eval_v3b_curriculum(
    output_path: str | None = None,
    *,
    use_theory_leverage: bool | None = None,
    use_anomaly_leverage: bool | None = None,
) -> dict:
    # Governance leverage is gated and defaults to OFF (the locked approved path).
    # It can be turned on for ablation via env vars without changing the default behaviour.
    if use_theory_leverage is None:
        use_theory_leverage = _env_flag("VIRTUAL_SIA_USE_THEORY_LEVERAGE")
    if use_anomaly_leverage is None:
        use_anomaly_leverage = _env_flag("VIRTUAL_SIA_USE_ANOMALY_LEVERAGE")

    # Keep the canonical artifact clean: only the OFF/OFF run overwrites the
    # canonical summary; leverage variants are written to suffixed files.
    if output_path is None:
        suffix = ""
        if use_theory_leverage:
            suffix += "_theory"
        if use_anomaly_leverage:
            suffix += "_anomaly"
        output_path = f"virtual_genesis/eval/results/prototype_v3b_curriculum_summary{suffix}.json"

    results = compare_conditions(
        DEFAULT_CONDITIONS,
        PROTOTYPE_V3B_CURRICULUM,
        task_set_ref="prototype_v3b_curriculum",
        use_theory_leverage=use_theory_leverage,
        use_anomaly_leverage=use_anomaly_leverage,
    )
    summary = summarize_comparison(results)
    curriculum_reports = {
        cid: generate_curriculum_analytics(payload['task_results'])
        for cid, payload in results.items()
    }
    payload = {
        "task_count": len(PROTOTYPE_V3B_CURRICULUM),
        "conditions": DEFAULT_CONDITIONS,
        "leverage": {
            "use_theory_leverage": use_theory_leverage,
            "use_anomaly_leverage": use_anomaly_leverage,
        },
        "summary": summary,
        "curriculum_reports": curriculum_reports,
        "raw_results": results,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def _ablation_record(payload: dict) -> dict:
    """Compact, machine-readable ablation row for stdout redirection."""
    raw = payload.get("raw_results", {})
    canonical = raw.get(CANONICAL_CONDITION, {})
    aggregate = canonical.get("aggregate_metrics", {})
    task_results = canonical.get("task_results", [])
    # An "error" here means a task that failed to execute (produced no verification
    # state). Functional task failures are captured by success_rate, not errors.
    errors = sum(
        1
        for run in task_results
        if not (run.get("blackboard", {}).get("verification_state"))
    )
    per_condition = {
        cid: {
            "success_rate": payload["summary"]["conditions"].get(cid, {}).get("success_rate", 0.0),
            "avg_estimated_cost": payload["summary"]["conditions"].get(cid, {}).get("avg_estimated_cost", 0.0),
        }
        for cid in payload.get("conditions", [])
    }
    return {
        "leverage": payload.get("leverage", {}),
        "task_count": payload.get("task_count", 0),
        "canonical_condition": CANONICAL_CONDITION,
        "success_rate": aggregate.get("success_rate", 0.0),
        "cost_avg": aggregate.get("avg_estimated_cost", 0.0),
        "errors": errors,
        "per_condition": per_condition,
        "thesis_signals": payload["summary"]["thesis_signals"],
    }


if __name__ == "__main__":
    payload = run_local_eval_v3b_curriculum()
    print(json.dumps(_ablation_record(payload), indent=2, ensure_ascii=False))
