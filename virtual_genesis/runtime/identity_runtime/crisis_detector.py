"""Crisis detection for paradigm forking."""
from __future__ import annotations

from typing import Dict, List


def detect_crisis(
    anomaly_history: List[Dict],
    theory_failures: int,
    drift_score: float,
) -> Dict:
    """Detect whether the agent is in an identity/paradigm crisis.

    Returns a CrisisReport dict with level, counts, drift_score, and reasons.
    """
    anomaly_count = len(anomaly_history)
    reasons: List[str] = []

    # Determine level
    if anomaly_count >= 5 and theory_failures >= 2 and drift_score > 0.6:
        level = "crisis"
        reasons.append(f"anomaly_count={anomaly_count} >= 5")
        reasons.append(f"theory_failures={theory_failures} >= 2")
        reasons.append(f"drift_score={drift_score:.2f} > 0.6")
    elif anomaly_count >= 3 or drift_score > 0.5:
        level = "warning"
        if anomaly_count >= 3:
            reasons.append(f"anomaly_count={anomaly_count} >= 3")
        if drift_score > 0.5:
            reasons.append(f"drift_score={drift_score:.2f} > 0.5")
    else:
        level = "normal"
        reasons.append("all metrics within normal bounds")

    return {
        "level": level,
        "anomaly_count": anomaly_count,
        "theory_failure_count": theory_failures,
        "drift_score": drift_score,
        "reasons": reasons,
    }
