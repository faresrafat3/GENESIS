from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.objects.memory import MemoryUnit
    from .store import InMemoryMemoryStore


def compute_memory_utility(memory_unit: "MemoryUnit", current_tick: int = 0) -> float:
    """Compute utility score for a memory unit.

    Combines:
    - retrieval_frequency: access_count normalized (sigmoid-like saturation)
    - recency: based on (current_tick - last_accessed), more recent = higher
    - decay_score: direct contribution from decay state
    - outcome_quality: from meta['good_enough'] if available

    Returns 0.0-1.0 float.
    """
    # Retrieval frequency: sigmoid-like normalization of access_count
    # 0 accesses -> 0.0, 5 accesses -> ~0.71, 10 -> ~0.83
    access = memory_unit.access_count
    retrieval_frequency = access / (access + 5.0) if access > 0 else 0.0

    # Recency: exponential decay based on time since last access
    age = max(0, current_tick - memory_unit.last_accessed)
    recency = math.exp(-0.1 * age)

    # Decay score: direct contribution
    decay = memory_unit.decay_score

    # Outcome quality: from meta if available
    meta = memory_unit.meta or {}
    outcome_quality = 1.0 if meta.get("good_enough", False) else 0.5

    # Weighted combination
    utility = (
        0.25 * retrieval_frequency
        + 0.30 * recency
        + 0.25 * decay
        + 0.20 * outcome_quality
    )

    return max(0.0, min(1.0, utility))


def compute_all_utilities(store: "InMemoryMemoryStore", current_tick: int | None = None) -> dict[str, float]:
    """Compute utility for all active memories in a store.

    Returns dict mapping memory_id -> utility score.
    """
    tick = current_tick if current_tick is not None else store._tick
    result: dict[str, float] = {}
    for mem in store.get_active_memories():
        result[mem.id] = compute_memory_utility(mem, current_tick=tick)
    return result
