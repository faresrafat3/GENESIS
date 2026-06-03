from __future__ import annotations

from typing import TYPE_CHECKING

from .utility import compute_all_utilities, compute_lesson_importance

if TYPE_CHECKING:
    from .store import InMemoryMemoryStore


def apply_forgetting_policy(
    store: "InMemoryMemoryStore",
    utility_threshold: float = 0.3,
    max_archive_ratio: float = 0.3,
    current_tick: int | None = None,
    protect_negative_lessons: bool = True,
    min_lessons_per_family: int = 1,
) -> dict:
    """Apply productive forgetting policy with strategic lesson preservation.

    Enhanced version that:
    1. Computes utility for all active memories
    2. Protects negative lessons from being forgotten too aggressively
    3. Ensures at least min_lessons_per_family memories remain per task family
    4. Uses lesson importance for smarter forgetting decisions
    5. Sorts by utility ascending
    6. Archives memories below utility_threshold (respect max_archive_ratio)
    7. Deprecates memories with utility < utility_threshold * 0.5
    8. Returns report dict with: archived_count, deprecated_count, total_active, decisions

    Parameters
    ----------
    store : InMemoryMemoryStore
        The memory store to apply policy to.
    utility_threshold : float
        Memories below this utility will be considered for archival.
    max_archive_ratio : float
        Maximum fraction of active memories that can be archived.
    current_tick : int | None
        Current tick for utility computation.
    protect_negative_lessons : bool
        If True, negative memories get a utility boost to prevent forgetting.
    min_lessons_per_family : int
        Minimum number of memories to keep per task family.
    """
    utilities = compute_all_utilities(store, current_tick=current_tick)
    total_active = len(utilities)

    if total_active == 0:
        return {
            "archived_count": 0,
            "deprecated_count": 0,
            "total_active": 0,
            "decisions": [],
            "protected_families": {},
        }

    # Apply lesson protection: boost negative memories
    if protect_negative_lessons:
        for mem_id, util in utilities.items():
            mem = store.get(mem_id)
            if mem and mem.memory_type == "negative":
                # Boost negative lessons by 20%
                utilities[mem_id] = min(1.0, util * 1.2)

    # Compute lesson importance for all memories
    all_active = store.get_active_memories()
    importance_scores = {}
    for mem in all_active:
        importance_scores[mem.id] = compute_lesson_importance(mem, all_active)

    # Identify families that need protection
    family_counts: dict[str, int] = {}
    for mem in all_active:
        for family in mem.scope.task_families:
            family_counts[family] = family_counts.get(family, 0) + 1

    # Identify memories that are the last representatives of their family
    protected_by_family: set[str] = set()
    if min_lessons_per_family > 0:
        family_remaining: dict[str, int] = dict(family_counts)
        # Sort memories by utility descending to find the ones we want to keep
        sorted_by_utility = sorted(utilities.items(), key=lambda x: x[1], reverse=True)
        
        for mem_id, util in sorted_by_utility:
            mem = store.get(mem_id)
            if not mem:
                continue
            needs_protection = False
            for family in mem.scope.task_families:
                if family_remaining.get(family, 0) <= min_lessons_per_family:
                    needs_protection = True
                    break
            if needs_protection:
                protected_by_family.add(mem_id)
                for family in mem.scope.task_families:
                    family_remaining[family] = max(0, family_remaining.get(family, 0) - 1)

    # Sort by utility ascending (lowest utility first)
    sorted_items = sorted(utilities.items(), key=lambda x: x[1])

    max_archive_count = int(total_active * max_archive_ratio)
    deprecation_threshold = utility_threshold * 0.5

    archived_count = 0
    deprecated_count = 0
    decisions = []
    protected_count = 0

    for memory_id, utility in sorted_items:
        if utility >= utility_threshold:
            break

        # Skip protected memories
        if memory_id in protected_by_family:
            protected_count += 1
            decisions.append({
                "memory_id": memory_id,
                "utility": utility,
                "action": "protected",
                "reason": "last_representative_of_family",
            })
            continue

        # Use lesson importance to influence the decision
        importance = importance_scores.get(memory_id, 0.5)
        
        if utility < deprecation_threshold:
            # High-importance lessons get archived instead of deprecated
            if importance > 0.7 and archived_count < max_archive_count:
                store.archive_memory(memory_id)
                archived_count += 1
                decisions.append({
                    "memory_id": memory_id,
                    "utility": utility,
                    "importance": importance,
                    "action": "archived",
                    "reason": "high_importance_preserved",
                })
            else:
                store.deprecate_memory(memory_id)
                deprecated_count += 1
                decisions.append({
                    "memory_id": memory_id,
                    "utility": utility,
                    "importance": importance,
                    "action": "deprecated",
                })
        elif archived_count < max_archive_count:
            store.archive_memory(memory_id)
            archived_count += 1
            decisions.append({
                "memory_id": memory_id,
                "utility": utility,
                "importance": importance,
                "action": "archived",
            })

    remaining_active = total_active - archived_count - deprecated_count
    return {
        "archived_count": archived_count,
        "deprecated_count": deprecated_count,
        "total_active": remaining_active,
        "decisions": decisions,
        "protected_count": protected_count,
        "protected_families": {fam: count for fam, count in family_counts.items()},
    }