from __future__ import annotations

from ...runtime.memory_os.store import InMemoryMemoryStore
from .proposer import promote_candidate, propose_concepts_from_groups
from .registry import InMemoryConceptRegistry
from .scope import draft_scope
from .selector import build_contrastive_groups

# Minimum evidence threshold: a candidate must have at least this many
# supporting episodes to be considered for promotion.  Prevents flimsy
# concepts from being formed on 1-2 data points.
MIN_SUPPORTING_EPISODES = 2

# Minimum failure count for gap/avoidance concepts.  A single failure
# is not enough evidence of a systematic gap.
MIN_FAILURES_FOR_GAP = 2


def _validate_candidate(candidate, groups: list[dict]) -> bool:
    """Gate: reject candidates whose evidence is below minimum thresholds.

    This prevents concept proliferation on thin data, a major source of
    semantic drift (concepts that are too specific to noise).
    """
    n_support = len(candidate.supporting_episode_refs or [])
    if n_support < MIN_SUPPORTING_EPISODES:
        return False

    # For gap/shortcut concepts, require a minimum failure count
    name_lower = candidate.proposed_name.lower()
    if "gap" in name_lower or "avoidance" in name_lower:
        # Find the matching group to count failures
        for group in groups:
            group_families = [group.get("family", "")]
            if any(f in name_lower for f in group_families):
                failures = group.get("failures", [])
                if len(failures) < MIN_FAILURES_FOR_GAP:
                    return False
                break

    return True


def run_concept_cycle(memory_store: InMemoryMemoryStore, registry: InMemoryConceptRegistry) -> dict:
    groups = build_contrastive_groups(memory_store.all())
    candidates = propose_concepts_from_groups(groups)
    promoted = []

    for candidate in candidates:
        # --- Step 1: Draft scope with specificity guards ---
        candidate = draft_scope(candidate)

        # --- Step 2: Validate evidence strength before registering ---
        if not _validate_candidate(candidate, groups):
            continue

        registered_candidate = registry.add_candidate(candidate)
        if registered_candidate.recommendation == "validate_as_concept":
            concept = promote_candidate(registry, registered_candidate.id)
            if concept:
                promoted.append(concept)

    return {
        "group_count": len(groups),
        "candidate_count": len(candidates),
        "promoted_count": len({c.id for c in promoted}),
        "concept_ids": list({c.id for c in promoted}),
    }
