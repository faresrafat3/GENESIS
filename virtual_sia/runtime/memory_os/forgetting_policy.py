from __future__ import annotations

from typing import TYPE_CHECKING

from .utility import compute_all_utilities

if TYPE_CHECKING:
    from .store import InMemoryMemoryStore


def apply_forgetting_policy(
    store: "InMemoryMemoryStore",
    utility_threshold: float = 0.3,
    max_archive_ratio: float = 0.3,
    current_tick: int | None = None,
) -> dict:
    """Apply productive forgetting policy.

    1. Compute utility for all active memories
    2. Sort by utility ascending
    3. Archive memories below utility_threshold (respect max_archive_ratio)
    4. Deprecate memories with utility < utility_threshold * 0.5
    5. Return report dict with: archived_count, deprecated_count, total_active, decisions
    """
    utilities = compute_all_utilities(store, current_tick=current_tick)
    total_active = len(utilities)

    if total_active == 0:
        return {
            "archived_count": 0,
            "deprecated_count": 0,
            "total_active": 0,
            "decisions": [],
        }

    # Sort by utility ascending (lowest utility first)
    sorted_items = sorted(utilities.items(), key=lambda x: x[1])

    max_archive_count = int(total_active * max_archive_ratio)
    deprecation_threshold = utility_threshold * 0.5

    archived_count = 0
    deprecated_count = 0
    decisions = []

    for memory_id, utility in sorted_items:
        if utility >= utility_threshold:
            break

        if utility < deprecation_threshold:
            store.deprecate_memory(memory_id)
            deprecated_count += 1
            decisions.append({
                "memory_id": memory_id,
                "utility": utility,
                "action": "deprecated",
            })
        elif archived_count < max_archive_count:
            store.archive_memory(memory_id)
            archived_count += 1
            decisions.append({
                "memory_id": memory_id,
                "utility": utility,
                "action": "archived",
            })

    remaining_active = total_active - archived_count - deprecated_count
    return {
        "archived_count": archived_count,
        "deprecated_count": deprecated_count,
        "total_active": remaining_active,
        "decisions": decisions,
    }
