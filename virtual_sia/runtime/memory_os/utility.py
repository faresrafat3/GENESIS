from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.objects.memory import MemoryUnit
    from .store import InMemoryMemoryStore

# ---------------------------------------------------------------------------
# Weight constants (tuned for balanced consolidation / forgetting)
# ---------------------------------------------------------------------------
_WEIGHT_RETRIEVAL_FREQ = 0.18
_WEIGHT_RECENCY = 0.22
_WEIGHT_DECAY = 0.12
_WEIGHT_OUTCOME = 0.15
_WEIGHT_LESSON_VALUE = 0.11
_WEIGHT_IDENTITY_RELEVANCE = 0.10
_WEIGHT_SALIENCE = 0.07
_WEIGHT_CONSOLIDATION = 0.05

# Identity-relevance bonus map
_IDENTITY_RELEVANCE_MAP = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.2,
}

# Memory type lesson multipliers (conservative to preserve ordering invariant)
_LESSON_MULTIPLIERS = {
    "negative": 1.4,      # Negative memories are critical for learning
    "procedural": 1.2,    # Procedural memories encode reusable strategies
    "semantic": 1.0,      # Semantic memories are neutral
    "episodic": 0.85,     # Episodic memories are less reusable as lessons
}


def compute_memory_utility(memory_unit: "MemoryUnit", current_tick: int = 0) -> float:
    """Compute utility score for a memory unit with enhanced lesson valuation.

    Combines:
    - retrieval_frequency: access_count normalized (sigmoid-like saturation)
    - recency: based on (current_tick - last_accessed), more recent = higher
    - decay_score: direct contribution from decay state
    - outcome_quality: from meta['good_enough'] if available
    - lesson_value: enhanced bonus for negative/warning memories with type multipliers
    - identity_relevance: from memory_unit.identity_relevance field
    - salience: direct salience score if set
    - consolidation_bonus: bonus for memories in active clusters

    NOTE: For episodic memories with identical properties, good_enough=True
    will always produce higher utility than good_enough=False, preserving the
    invariant that successful outcomes are preferred.

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

    # Enhanced lesson value with memory type multipliers
    lesson_value = 0.0
    base_lesson = 0.0
    
    if memory_unit.memory_type == "negative":
        base_lesson = 1.0
    elif not meta.get("good_enough", True):
        # Failed episodic memories carry moderate lesson value
        base_lesson = 0.6
    elif memory_unit.memory_type == "procedural":
        # Procedural memories encode reusable strategies
        base_lesson = 0.4
    
    # Apply memory type multiplier
    type_multiplier = _LESSON_MULTIPLIERS.get(memory_unit.memory_type, 1.0)
    lesson_value = base_lesson * type_multiplier
    
    # Additional lesson boost for recently accessed failures
    if not meta.get("good_enough", True) and age < 10:
        lesson_value = min(1.0, lesson_value * 1.15)

    # Identity relevance: how important this memory is to the agent's identity
    identity_relevance = _IDENTITY_RELEVANCE_MAP.get(
        getattr(memory_unit, "identity_relevance", "low"), 0.2
    )

    # Salience: direct salience score if set, default to moderate
    salience = getattr(memory_unit, "salience", None)
    if salience is None:
        salience = 0.5  # neutral default

    # Consolidation bonus: small boost for memories in active clusters
    # (This will be computed externally and passed in via meta)
    consolidation_bonus = 0.0
    if meta.get("in_active_cluster", False):
        consolidation_bonus = 0.1

    # Weighted combination with enhanced lesson weighting
    utility = (
        _WEIGHT_RETRIEVAL_FREQ * retrieval_frequency
        + _WEIGHT_RECENCY * recency
        + _WEIGHT_DECAY * decay
        + _WEIGHT_OUTCOME * outcome_quality
        + _WEIGHT_LESSON_VALUE * lesson_value
        + _WEIGHT_IDENTITY_RELEVANCE * identity_relevance
        + _WEIGHT_SALIENCE * salience
        + _WEIGHT_CONSOLIDATION * consolidation_bonus
    )

    return max(0.0, min(1.0, utility))


def compute_all_utilities(store: "InMemoryMemoryStore", current_tick: int | None = None) -> dict[str, float]:
    """Compute utility for all active memories in a store.

    Returns dict mapping memory_id -> utility score.
    """
    tick = current_tick if current_tick is not None else store._tick
    result: dict[str, float] = {}
    
    # First pass: compute base utilities
    for mem in store.get_active_memories():
        result[mem.id] = compute_memory_utility(mem, current_tick=tick)
    
    # Second pass: apply consolidation bonuses
    result = consolidate_utility_scores(result, store.get_active_memories())
    
    return result


def consolidate_utility_scores(utilities: dict[str, float], memories: list["MemoryUnit"]) -> dict[str, float]:
    """Apply consolidation bonus: memories that reinforce each other get a boost.

    Memories within the same task family and of the same outcome polarity
    (success vs failure) reinforce each other.  This encourages keeping
    coherent lesson clusters together rather than pruning individual
    entries from an otherwise useful cluster.

    Enhanced version with:
    1. Cross-type consolidation for related lessons
    2. Stronger negative lesson clusters
    3. Temporal consolidation for recent memories

    *Does not mutate* the input dict; returns a new dict.
    """
    if len(utilities) <= 1:
        return dict(utilities)

    # Build family -> count of same-polarity memories
    family_outcome_counts: dict[tuple[str, bool], int] = {}
    family_type_counts: dict[tuple[str, str], int] = {}
    mem_by_id: dict[str, "MemoryUnit"] = {}
    
    for mem in memories:
        mem_by_id[mem.id] = mem
        families = mem.scope.task_families
        outcome_good = (mem.meta or {}).get("good_enough", True)
        for fam in families:
            # Count by family and outcome
            key = (fam, outcome_good)
            family_outcome_counts[key] = family_outcome_counts.get(key, 0) + 1
            
            # Count by family and type
            type_key = (fam, mem.memory_type)
            family_type_counts[type_key] = family_type_counts.get(type_key, 0) + 1

    result = dict(utilities)
    for mem_id, util in result.items():
        mem = mem_by_id.get(mem_id)
        if mem is None:
            continue
        
        families = mem.scope.task_families
        outcome_good = (mem.meta or {}).get("good_enough", True)
        consolidation_bonus = 0.0
        
        for fam in families:
            # Outcome-based consolidation
            count = family_outcome_counts.get((fam, outcome_good), 0)
            if count > 1:
                # Consolidation bonus (capped at +0.08)
                bonus = min(0.08, 0.02 * (count - 1))
                consolidation_bonus = max(consolidation_bonus, bonus)
            
            # Type-based consolidation (stronger for negative lessons)
            type_count = family_type_counts.get((fam, mem.memory_type), 0)
            if type_count > 1 and mem.memory_type == "negative":
                # Extra bonus for negative lesson clusters
                type_bonus = min(0.06, 0.02 * (type_count - 1))
                consolidation_bonus += type_bonus
        
        # Apply consolidation bonus
        if consolidation_bonus > 0:
            result[mem_id] = min(1.0, result[mem_id] + consolidation_bonus)
        
        # Mark memory as being in an active cluster for future utility calculations
        if consolidation_bonus > 0.02:
            mem.meta = mem.meta or {}
            mem.meta["in_active_cluster"] = True

    return result


def compute_lesson_importance(memory_unit: "MemoryUnit", all_memories: list["MemoryUnit"] = None) -> float:
    """Compute the importance of a memory as a lesson.
    
    Higher values indicate more important lessons that should be preserved.
    Useful for selective forgetting decisions.
    """
    importance = 0.0
    
    # Base importance by type
    if memory_unit.memory_type == "negative":
        importance = 0.8
    elif memory_unit.memory_type == "procedural":
        importance = 0.6
    elif memory_unit.memory_type == "semantic":
        importance = 0.4
    else:  # episodic
        importance = 0.3
    
    # Boost for failure lessons
    meta = memory_unit.meta or {}
    if not meta.get("good_enough", True):
        importance *= 1.3
    
    # Boost for high-access memories
    if memory_unit.access_count > 3:
        importance *= 1.2
    
    # Boost for high-salience memories
    salience = getattr(memory_unit, "salience", None) or 0.5
    importance *= (0.5 + salience * 0.5)
    
    # Cluster importance: if this memory is part of a larger cluster, it's more valuable
    if all_memories:
        family_count = sum(1 for m in all_memories 
                         if set(memory_unit.scope.task_families).intersection(m.scope.task_families))
        if family_count > 1:
            importance *= (1.0 + 0.1 * min(family_count - 1, 3))
    
    return min(1.0, importance)