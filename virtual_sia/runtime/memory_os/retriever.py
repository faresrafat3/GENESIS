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


def _matches_any_family(item_families: list[str], candidate_families: Sequence[str]) -> bool:
    if not item_families:
        return True
    return any(f in item_families for f in candidate_families)


def retrieve_memory(
    task_family: str,
    task_text: str,
    store_items: list[MemoryUnit],
    budget: int = 5,
    concept_items: Iterable[ConceptCard] | None = None,
    theory_items: Iterable[LocalTheoryObject] | None = None,
    family_candidates: Sequence[str] | None = None,
    task_contract: Mapping[str, Any] | None = None,
) -> BlackboardMemoryPack:
    candidate_families = list(family_candidates or [task_family])
    if task_family not in candidate_families:
        candidate_families.insert(0, task_family)

    episodic, semantic, procedural, negative, concept_refs, theory_refs = [], [], [], [], [], []
    rationale_parts = []

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

    # Use the primary family's max_active setting instead of the single global cap
    primary_family_cfg = DEFAULT_FAMILY_SELECTIVITY.get(task_family, {})
    family_max_active = primary_family_cfg.get('max_active', DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS)
    applicable_concepts = family_selected[:family_max_active]
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

    for item in store_items:
        if not _matches_any_family(item.scope.task_families, candidate_families):
            continue
        if item.memory_type == "procedural" and len(procedural) < budget:
            procedural.append(item.id)
        elif item.memory_type == "semantic" and len(semantic) < budget:
            semantic.append(item.id)
        elif item.memory_type == "negative" and len(negative) < budget:
            negative.append(item.id)
        elif item.memory_type == "episodic" and len(episodic) < budget:
            episodic.append(item.id)

    for concept in applicable_concepts:
        concept_refs.append(concept.id)
    for theory in applicable_theories:
        theory_refs.append(theory.id)

    if concept_refs:
        rationale_parts.append(f"concept-guided retrieval active across {candidate_families}")
    if theory_refs:
        rationale_parts.append("theory-guided interpretation available")
    if procedural:
        rationale_parts.append("procedural memories available")
    if semantic:
        rationale_parts.append("semantic support retrieved")
    if episodic:
        rationale_parts.append("episodic exemplars retrieved")
    if negative:
        rationale_parts.append("negative warnings retrieved")

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
    pack.meta = {"concept_activation_decisions": [asdict(d) for d in all_decisions]}
    return pack
