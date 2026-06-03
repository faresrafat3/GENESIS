from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, Mapping, Sequence, Any

from ...core.objects.blackboard import BlackboardMemoryPack
from ...core.objects.concept import ConceptCard
from ...core.objects.memory import MemoryUnit
from ...core.objects.theory import LocalTheoryObject
from ..concept_engine.apply import build_concept_hints, select_applicable_concepts
from ..concept_engine.config import DEFAULT_FAMILY_SELECTIVITY, DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS
from ..theory_runtime.apply import build_theory_hints, select_applicable_theories
from .utility import compute_memory_utility


def _matches_any_family(item_families: list[str], candidate_families: Sequence[str]) -> bool:
    if not item_families:
        return True
    return any(f in item_families for f in candidate_families)


def _calculate_strategic_priority(memory: MemoryUnit, utility_scores: dict[str, float], 
                                 current_tick: int = 0) -> float:
    """Calculate strategic priority for memory retrieval.
    
    Prioritizes:
    1. High utility memories (proven useful)
    2. Recent negative lessons (prevent repeating mistakes)
    3. Memories with high access frequency (frequently needed)
    4. Memories with high salience (important but underused)
    """
    base_utility = utility_scores.get(memory.id, 0.5)
    
    # Boost negative lessons (they're critical for learning)
    lesson_boost = 0.0
    if memory.memory_type == "negative":
        lesson_boost = 0.3
    elif (memory.meta or {}).get("good_enough", True) == False:
        lesson_boost = 0.2
    
    # Recency boost for episodic memories
    recency_boost = 0.0
    if memory.memory_type == "episodic" and current_tick > 0:
        age = current_tick - memory.last_accessed
        recency_boost = 0.1 * (1.0 / (1.0 + age * 0.1))
    
    # Salience boost for under-accessed but important memories
    salience_boost = 0.0
    if memory.salience is not None and memory.access_count < 3:
        salience_boost = 0.1 * memory.salience
    
    return base_utility + lesson_boost + recency_boost + salience_boost


def retrieve_memory(
    task_family: str,
    task_text: str,
    store_items: list[MemoryUnit],
    budget: int = 5,
    concept_items: Iterable[ConceptCard] | None = None,
    theory_items: Iterable[LocalTheoryObject] | None = None,
    family_candidates: Sequence[str] | None = None,
    task_contract: Mapping[str, Any] | None = None,
    active_only: bool = False,
    current_tick: int = 0,
    utility_scores: dict[str, float] | None = None,
    prioritize_lessons: bool = True,
) -> BlackboardMemoryPack:
    """Retrieve memories with strategic prioritization.
    
    Enhanced version that:
    1. Computes utility scores if not provided
    2. Prioritizes negative lessons and recent failures
    3. Uses strategic scoring for memory selection
    4. Ensures diverse memory types in retrieval
    """
    candidate_families = list(family_candidates or [task_family])
    if task_family not in candidate_families:
        candidate_families.insert(0, task_family)

    if active_only:
        store_items = [item for item in store_items if getattr(item, 'memory_status', 'active') == 'active']

    # Compute utility scores if not provided
    if utility_scores is None:
        utility_scores = {}
        for item in store_items:
            utility_scores[item.id] = compute_memory_utility(item, current_tick=current_tick)

    episodic, semantic, procedural, negative, concept_refs, theory_refs = [], [], [], [], [], []
    rationale_parts = []

    # Select concepts with family-based selectivity
    family_selected = []
    all_decisions = []
    seen = set()
    for family in candidate_families:
        selected, decisions = select_applicable_concepts(
            family,
            task_text,
            concept_items or [],
            task_contract=task_contract,
        )
        all_decisions.extend(decisions)
        for c in selected:
            if c.id not in seen:
                seen.add(c.id)
                family_selected.append(c)

    # Use the max of all candidate families' max_active values as the cap.
    family_max_active = max(
        (DEFAULT_FAMILY_SELECTIVITY.get(fam, {}).get('max_active', DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS)
         for fam in candidate_families),
        default=DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS,
    )
    applicable_concepts = family_selected[:family_max_active]
    
    # Select applicable theories
    applicable_theories = []
    for family in candidate_families:
        applicable_theories.extend(select_applicable_theories(family, theory_items or [], limit=1))
    seen_theories = set()
    dedup_theories = []
    for t in applicable_theories:
        if t.id not in seen_theories:
            seen_theories.add(t.id)
            dedup_theories.append(t)
    applicable_theories = dedup_theories[:1]

    # Strategic memory selection with prioritization
    candidate_memories = []
    for item in store_items:
        if not _matches_any_family(item.scope.task_families, candidate_families):
            continue
        # Calculate strategic priority
        if prioritize_lessons:
            priority = _calculate_strategic_priority(item, utility_scores, current_tick)
        else:
            priority = utility_scores.get(item.id, 0.5)
        candidate_memories.append((item, priority))
    
    # Sort by priority (highest first)
    candidate_memories.sort(key=lambda x: x[1], reverse=True)
    
    # Select memories ensuring type diversity
    type_limits = {
        "episodic": budget,
        "semantic": budget,
        "procedural": budget,
        "negative": budget,
    }
    
    for item, priority in candidate_memories:
        if item.memory_type == "procedural" and len(procedural) < type_limits["procedural"]:
            procedural.append(item.id)
        elif item.memory_type == "semantic" and len(semantic) < type_limits["semantic"]:
            semantic.append(item.id)
        elif item.memory_type == "negative" and len(negative) < type_limits["negative"]:
            negative.append(item.id)
        elif item.memory_type == "episodic" and len(episodic) < type_limits["episodic"]:
            episodic.append(item.id)

    # Record retrieval access on selected memories
    selected_ids = set(episodic + semantic + procedural + negative)
    for item in store_items:
        if item.id in selected_ids:
            item.access_count += 1

    # Add concept and theory references
    for concept in applicable_concepts:
        concept_refs.append(concept.id)
    for theory in applicable_theories:
        theory_refs.append(theory.id)

    # Build rationale
    if concept_refs:
        rationale_parts.append(f"concept-guided retrieval active across {candidate_families}")
    if theory_refs:
        rationale_parts.append("theory-guided interpretation available")
    if procedural:
        rationale_parts.append(f"{len(procedural)} procedural strategies retrieved")
    if semantic:
        rationale_parts.append(f"{len(semantic)} semantic knowledge retrieved")
    if episodic:
        rationale_parts.append(f"{len(episodic)} episodic examples retrieved")
    if negative:
        rationale_parts.append(f"{len(negative)} negative lessons prioritized")
    
    # Add strategic prioritization note
    if prioritize_lessons and negative:
        rationale_parts.append("negative lessons strategically prioritized")

    total_refs = len(episodic) + len(semantic) + len(procedural) + len(negative) + len(concept_refs) + len(theory_refs)
    pack = BlackboardMemoryPack(
        episodic_refs=episodic,
        semantic_refs=semantic,
        procedural_refs=procedural,
        negative_refs=negative,
        concept_refs=concept_refs,
        concept_hints=build_concept_hints(applicable_concepts),
        theory_refs=theory_refs,
        theory_hints=build_theory_hints(applicable_theories),
        retrieval_rationale="; ".join(rationale_parts) or "no relevant memory",
        memory_noise_risk=0.1 if total_refs < budget else 0.4,
    )
    pack.meta = {
        "concept_activation_decisions": [asdict(d) for d in all_decisions],
        "strategic_prioritization": prioritize_lessons,
        "utility_scores_used": len(utility_scores) > 0,
    }
    return pack