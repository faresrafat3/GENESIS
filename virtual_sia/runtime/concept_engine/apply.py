from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Any

from ...core.objects.concept import ConceptCard
from .config import (
    DEFAULT_FAMILY_SELECTIVITY,
    DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS,
    DEFAULT_MIN_ACTIVATION_SCORE,
    DEFAULT_MIN_OVERLAP,
    FAMILY_SELECTIVITY_STRATEGY,
)


@dataclass(slots=True)
class ConceptActivationDecision:
    concept_ref: str
    activation_score: int
    family_fit: int
    contract_fit: int
    semantic_fit: int
    redundancy_penalty: int
    selected: bool
    rank: int
    family: str
    notes: str = ""


def _tokenize(text: str) -> set[str]:
    return {t.strip('.,:;!?()[]{}').lower() for t in text.split() if t.strip()}


def _contract_tokens(task_contract: Mapping[str, Any] | None) -> set[str]:
    tokens = set()
    if task_contract:
        for key in ["required_properties", "forbidden_shortcuts", "diagnostic_purpose"]:
            for item in task_contract.get(key, []) or []:
                tokens |= _tokenize(str(item))
    return tokens


def _family_policy(task_family: str, max_active: int | None, min_activation_score: int | None) -> tuple[int, int, str]:
    if max_active is not None and min_activation_score is not None:
        strategy = FAMILY_SELECTIVITY_STRATEGY.get(task_family, 'semantic_balanced')
        return max_active, min_activation_score, strategy
    family_cfg = DEFAULT_FAMILY_SELECTIVITY.get(task_family, {})
    fam_max = family_cfg.get('max_active', DEFAULT_GLOBAL_MAX_ACTIVE_CONCEPTS)
    fam_min = family_cfg.get('min_score', DEFAULT_MIN_ACTIVATION_SCORE)
    strategy = FAMILY_SELECTIVITY_STRATEGY.get(task_family, 'semantic_balanced')
    return (
        fam_max if max_active is None else max_active,
        fam_min if min_activation_score is None else min_activation_score,
        strategy,
    )


def select_applicable_concepts(
    task_family: str,
    task_text: str,
    concepts: Iterable[ConceptCard],
    limit: int | None = None,
    min_overlap: int | None = None,
    min_activation_score: int | None = None,
    task_contract: Mapping[str, Any] | None = None,
) -> tuple[List[ConceptCard], List[ConceptActivationDecision]]:
    fam_limit, fam_min_score, strategy = _family_policy(task_family, limit, min_activation_score)
    min_overlap = DEFAULT_MIN_OVERLAP if min_overlap is None else min_overlap

    task_tokens = _tokenize(task_text)
    contract_tokens = _contract_tokens(task_contract)
    decisions: List[ConceptActivationDecision] = []

    scored_rows = []
    for concept in concepts:
        if task_family not in concept.scope.task_families:
            continue
        concept_tokens = _tokenize(concept.name + ' ' + concept.definition + ' ' + concept.operational_meaning)
        semantic_fit = len(task_tokens & concept_tokens)
        contract_fit = len(contract_tokens & concept_tokens)
        family_fit = 2

        # Strategy-differentiated scoring.
        # Note: structural_only differentiation is in the high-threshold fallback
        # below, not in the scoring formula itself.
        if strategy == 'contract_heavy':
            base_score = family_fit + (contract_fit * 2) + semantic_fit
        else:
            base_score = family_fit + contract_fit + semantic_fit

        if semantic_fit >= min_overlap or contract_fit > 0:
            scored_rows.append((base_score, family_fit, contract_fit, semantic_fit, concept))

    scored_rows.sort(key=lambda x: x[0], reverse=True)

    selected: List[ConceptCard] = []
    used_token_sets: List[set[str]] = []
    for rank, (score, family_fit, contract_fit, semantic_fit, concept) in enumerate(scored_rows, start=1):
        concept_tokens = _tokenize(concept.name + ' ' + concept.definition + ' ' + concept.operational_meaning)
        redundancy_penalty = 0
        if used_token_sets:
            max_overlap = max(len(concept_tokens & prev) for prev in used_token_sets)
            redundancy_penalty = 1 if max_overlap >= 4 else 0
        adjusted = score - redundancy_penalty
        select = adjusted >= fam_min_score and len(selected) < fam_limit

        # semantic_balanced strategy: allow a secondary concept if it also exceeds threshold
        if not select and strategy == 'semantic_balanced' and len(selected) == 1 and fam_limit >= 2:
            secondary_threshold = fam_min_score
            if adjusted >= secondary_threshold:
                select = True

        # structural_only strategy: high-threshold fallback allows 1 concept
        if not select and strategy == 'structural_only' and len(selected) == 0:
            if adjusted >= 10:
                select = True

        if select:
            selected.append(concept)
            used_token_sets.append(concept_tokens)
        decisions.append(
            ConceptActivationDecision(
                concept_ref=concept.id,
                activation_score=adjusted,
                family_fit=family_fit,
                contract_fit=contract_fit,
                semantic_fit=semantic_fit,
                redundancy_penalty=redundancy_penalty,
                selected=select,
                rank=rank,
                family=task_family,
                notes=concept.name,
            )
        )

    return selected, decisions


def build_concept_hints(concepts: Iterable[ConceptCard]) -> list[str]:
    hints: list[str] = []
    for concept in concepts:
        hints.append(f"{concept.name}: {concept.operational_meaning}")
    return hints


def select_applicable_concepts_theory_guided(
    task_family: str,
    task_text: str,
    concepts: Iterable[ConceptCard],
    theory: "LocalTheoryObject",
    limit: int | None = None,
    min_overlap: int | None = None,
    min_activation_score: int | None = None,
    task_contract: Mapping[str, Any] | None = None,
) -> tuple[List[ConceptCard], List[ConceptActivationDecision]]:
    """Theory-guided concept activation that boosts theory-aligned concepts.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 5.35: Theory-Theory of Concepts - Gopnik & Wellman (1994)
    ما الذي اخذناه؟
        المفاهيم ليست مجرد تصنيفات بل هي جزء من نظريات ضمنية.
        النظرية توجه اختيار المفاهيم ذات الصلة: المفاهيم المرتبطة بالنظرية
        تحصل على تفعيل اقوى لانها جزء من اطار تفسيري متماسك.
    ما الذي لم ناخذه الان؟
        البنية الكاملة للنظريات الضمنية عند الاطفال والبالغين.
        لم ناخذ التحولات المفاهيمية الكاملة (conceptual change).
    ماذا اصبح عندنا؟
        المفاهيم المذكورة في concept_refs للنظرية تحصل على دفعة +3
        في درجة التفعيل.

    المصدر 5.36: Explanation-Based Learning - DeJong & Mooney (1986)
    ما الذي اخذناه؟
        التعلم المبني على التفسير: النظرية تسمح بادخال مفاهيم
        لم تكن لتفعل بدونها، لان النظرية توفر تفسيرا لملاءمتها.
        المفاهيم القريبة من العتبة تدخل اذا كانت مرتبطة بالنظرية.
    ما الذي لم ناخذه الان؟
        التعميم الكامل من مثال واحد والتفسير السببي الكامل.
    ماذا اصبح عندنا؟
        المفاهيم غير المختارة التي درجتها قريبة من الحد الادنى (ضمن 2)
        تدخل اذا كانت في concept_refs للنظرية (theory-guided admission).
    """
    from ...core.objects.theory import LocalTheoryObject as _TheoryType  # noqa: F811

    selected, decisions = select_applicable_concepts(
        task_family, task_text, concepts,
        limit=limit, min_overlap=min_overlap,
        min_activation_score=min_activation_score,
        task_contract=task_contract,
    )

    theory_concept_refs = set(theory.concept_refs) if theory.concept_refs else set()
    if not theory_concept_refs:
        return selected, decisions

    # Determine family min score for theory-guided admission
    _, fam_min_score, _ = _family_policy(task_family, limit, min_activation_score)

    # Boost selected concepts that are in theory refs + admit near-threshold concepts
    admitted: List[ConceptCard] = []
    updated_decisions: List[ConceptActivationDecision] = []

    for decision in decisions:
        if decision.concept_ref in theory_concept_refs:
            if decision.selected:
                # Boost score
                new_decision = ConceptActivationDecision(
                    concept_ref=decision.concept_ref,
                    activation_score=decision.activation_score + 3,
                    family_fit=decision.family_fit,
                    contract_fit=decision.contract_fit,
                    semantic_fit=decision.semantic_fit,
                    redundancy_penalty=decision.redundancy_penalty,
                    selected=True,
                    rank=decision.rank,
                    family=decision.family,
                    notes=decision.notes + " [theory_boost]",
                )
                updated_decisions.append(new_decision)
            elif decision.activation_score >= (fam_min_score - 2):
                # Theory-guided admission
                new_decision = ConceptActivationDecision(
                    concept_ref=decision.concept_ref,
                    activation_score=decision.activation_score + 3,
                    family_fit=decision.family_fit,
                    contract_fit=decision.contract_fit,
                    semantic_fit=decision.semantic_fit,
                    redundancy_penalty=decision.redundancy_penalty,
                    selected=True,
                    rank=decision.rank,
                    family=decision.family,
                    notes=decision.notes + " [theory_admission]",
                )
                updated_decisions.append(new_decision)
                admitted.append(decision.concept_ref)
            else:
                updated_decisions.append(decision)
        else:
            updated_decisions.append(decision)

    # Resolve admitted concepts back to ConceptCard objects
    if admitted:
        all_concepts_list = list(concepts) if not isinstance(concepts, list) else concepts
        for concept in all_concepts_list:
            if concept.id in admitted and concept not in selected:
                selected.append(concept)

    return selected, updated_decisions
