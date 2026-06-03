"""Paradigm Fork Protocol - propose and execute identity forks under crisis."""
from __future__ import annotations

from typing import Dict, List

from ...core.objects.base import make_id
from ...core.objects.identity import AgentIdentityObject

MINIMUM_CYCLES_BETWEEN_FORKS = 10


def propose_fork(crisis_report: Dict, identity: AgentIdentityObject) -> Dict:
    """Propose a paradigm fork in response to a crisis.

    Generates a ForkProposal dict describing what to change, preserve, and discard.
    """
    reasons = crisis_report.get("reasons", [])

    # Generate proposed changes from crisis reasons
    proposed_changes: List[str] = [
        f"Update commitment due to: {reason}" for reason in reasons
    ]

    # Preserve all lineage items + first half of commitments as core
    half = len(identity.commitments) // 2
    preserved_commitments = identity.commitments[:max(half, 1)] if identity.commitments else []
    preserved: List[str] = list(identity.lineage) + preserved_commitments

    # Discard: second half of commitments (those potentially related to failure)
    discarded: List[str] = identity.commitments[max(half, 1):] if len(identity.commitments) > 1 else []

    # Justification from crisis reasons
    justification = "; ".join(reasons) if reasons else ""

    fork_id = make_id("fork")

    return {
        "proposed_changes": proposed_changes,
        "preserved": preserved,
        "discarded": discarded,
        "justification": justification,
        "fork_id": fork_id,
    }


def execute_fork(
    proposal: Dict,
    identity: AgentIdentityObject,
    current_cycle: int = 0,
) -> Dict:
    """Execute a paradigm fork, creating an updated identity.

    Safety checks:
    1. Refuses without explicit justification.
    2. Enforces minimum cycle gap between forks.
    3. Ensures preserved and discarded do not overlap.
    """
    # Safety check 1: justification required
    justification = proposal.get("justification", "")
    if not justification:
        return {"success": False, "reason": "no justification"}

    # Safety check 2: minimum cycle gap
    last_fork_cycle = -MINIMUM_CYCLES_BETWEEN_FORKS
    if identity.meta is not None:
        last_fork_cycle = identity.meta.get("last_fork_cycle", -MINIMUM_CYCLES_BETWEEN_FORKS)
    if current_cycle - last_fork_cycle < MINIMUM_CYCLES_BETWEEN_FORKS:
        return {"success": False, "reason": "minimum cycle gap not met"}

    # Safety check 3: preserved/discarded must not overlap
    preserved_set = set(proposal.get("preserved", []))
    discarded_set = set(proposal.get("discarded", []))
    if preserved_set & discarded_set:
        return {"success": False, "reason": "preserved/discarded overlap"}

    # Build new commitments: keep existing commitments that are in preserved, add proposed_changes
    existing_preserved = [c for c in identity.commitments if c in preserved_set]
    new_commitments = existing_preserved + proposal.get("proposed_changes", [])

    # Build new lineage: copy old lineage + append fork_id
    new_lineage = list(identity.lineage) + [proposal["fork_id"]]

    # Create new identity
    new_identity = AgentIdentityObject.create(
        commitments=new_commitments,
        self_model=dict(identity.self_model),
    )
    new_identity.lineage = new_lineage
    new_identity.drift_score = 0.0
    new_identity.meta = {"last_fork_cycle": current_cycle}

    return {
        "success": True,
        "new_identity": new_identity,
        "archived_policies": proposal.get("discarded", []),
        "reset_drift_score": 0.0,
    }
