from __future__ import annotations

from ...core.objects.identity import AgentIdentityObject
from .drift_detector import _tokenize, measure_drift


def check_identity_alignment(decision: str, identity: AgentIdentityObject) -> dict:
    """Check whether a decision aligns with the agent's identity commitments.

    Returns a dict with: aligned, drift_score, violated_commitments, recommendation.
    """
    drift_score = measure_drift([decision], identity.commitments)

    decision_tokens = _tokenize(decision)
    violated_commitments: list[str] = []
    for commitment in identity.commitments:
        commitment_tokens = _tokenize(commitment)
        if not (commitment_tokens & decision_tokens):
            violated_commitments.append(commitment)

    aligned = drift_score < 0.5

    if drift_score > 0.7:
        recommendation = "halt_and_review"
    elif drift_score >= 0.5:
        recommendation = "review_decision"
    else:
        recommendation = "continue"

    return {
        "aligned": aligned,
        "drift_score": drift_score,
        "violated_commitments": violated_commitments,
        "recommendation": recommendation,
    }
