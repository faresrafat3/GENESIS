from __future__ import annotations

from typing import Any, Dict, List

from ...core.objects.contradiction import ContradictionObject
from ...core.objects.decision import TierDecisionObject
from ...core.objects.task import TaskObject


def detect_contradictions(
    task: TaskObject,
    verification_state: Dict[str, Any],
    tier_decision: TierDecisionObject,
) -> List[ContradictionObject]:
    contradictions: List[ContradictionObject] = []
    meta = task.meta or {}
    envelope = meta.get("normalized_envelope", {}) or {}

    expected_primary = envelope.get("expected_primary_family")
    predicted_primary = task.task_family
    ranked_frames = meta.get("ranked_frames", []) or []
    ambiguity = bool(meta.get("family_ambiguity", False))

    property_checks = verification_state.get("property_checks", {}) or {}
    shortcut_checks = verification_state.get("shortcut_checks", {}) or {}
    primary_hit = bool(verification_state.get("evidence_checks", {}).get("primary_hit", False))
    secondary_hit = bool(verification_state.get("evidence_checks", {}).get("secondary_hit", False))
    good_enough = bool(verification_state.get("verification_summary", {}).get("good_enough", False))

    if expected_primary and predicted_primary != expected_primary:
        contradictions.append(
            ContradictionObject.create(
                "framing_mismatch",
                task.id,
                f"Expected primary frame `{expected_primary}` but ingress predicted `{predicted_primary}`.",
                elements_involved=[expected_primary, predicted_primary],
                severity=0.7,
            )
        )

    if ambiguity and secondary_hit and not good_enough:
        contradictions.append(
            ContradictionObject.create(
                "framing_overlap_failure",
                task.id,
                "Task shows overlapping frame evidence, but current answer still fails the verification contract.",
                elements_involved=ranked_frames[:2],
                severity=0.6,
            )
        )

    if property_checks and any(shortcut_checks.values()) and all(property_checks.values()):
        contradictions.append(
            ContradictionObject.create(
                "property_shortcut_conflict",
                task.id,
                "Required properties appear satisfied while a forbidden shortcut is also triggered.",
                elements_involved=list(property_checks.keys()) + [k for k, v in shortcut_checks.items() if v],
                severity=0.8,
            )
        )

    if tier_decision.chosen_tier == "tier_1" and not good_enough and primary_hit:
        contradictions.append(
            ContradictionObject.create(
                "sufficient_evidence_but_failure",
                task.id,
                "Primary evidence signal is present but the result still fails, suggesting reasoning or contract handling mismatch.",
                elements_involved=[predicted_primary, tier_decision.chosen_tier],
                severity=0.5,
            )
        )

    return contradictions
