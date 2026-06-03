from __future__ import annotations

from typing import Iterable, List

from ...core.objects.concept import ConceptCard
from ...core.objects.contradiction import ContradictionObject
from ...core.objects.anomaly import AnomalyCandidate
from ...core.objects.theory import LocalTheoryObject
from .registry import InMemoryTheoryRegistry


def build_local_theory(
    *,
    task_family: str,
    concepts: Iterable[ConceptCard],
    contradictions: Iterable[dict],
    anomaly_candidates: Iterable[dict],
) -> LocalTheoryObject | None:
    relevant_concepts = [c for c in concepts if task_family in c.scope.task_families]
    contradiction_list = [c for c in contradictions]
    anomaly_list = [a for a in anomaly_candidates if a.get("task_family") == task_family]

    if not relevant_concepts and not contradiction_list and not anomaly_list:
        return None

    theory = LocalTheoryObject.create(
        name=f"{task_family.title()} Local Theory",
        core_question=f"What governs success and failure in {task_family} tasks under the current runtime regime?",
    )
    theory.scope.task_families = [task_family]
    theory.concept_refs = [c.id for c in relevant_concepts]
    theory.contradiction_refs = [c.get("id", "") for c in contradiction_list]
    theory.anomaly_candidate_refs = [a.get("id", "") for a in anomaly_list]

    if task_family == "comparison":
        theory.mechanism_claims.append(
            "Comparison tasks succeed when the system makes an explicit evidence-backed contrast instead of a generic preference."
        )
        theory.predictive_claims.append(
            "If concept support is absent, comparison tasks are more likely to fall back to weak preference-style outputs."
        )
        theory.prescriptive_implications.append(
            "Prefer contrast-preserving reasoning templates and evidence-backed comparison concepts."
        )
    elif task_family == "synthesis":
        theory.mechanism_claims.append(
            "Synthesis tasks fail when the answer collapses into a generic summary instead of preserving grounded support and the fact/inference boundary."
        )
        theory.predictive_claims.append(
            "Shortcut pressure and weak concept guidance will increase summary-style failures under tighter hidden contracts."
        )
        theory.prescriptive_implications.append(
            "Use synthesis-specific anti-shortcut concepts and keep observed/inferred structure explicit."
        )
    elif task_family == "procedure":
        theory.mechanism_claims.append(
            "Procedure tasks often succeed through stable structure templates, while extra conceptual guidance may have low marginal value."
        )
        theory.predictive_claims.append(
            "Allowing many concepts in procedure tasks may increase activation without meaningful success gains."
        )
        theory.prescriptive_implications.append(
            "Default to structured procedural templates and keep concept activation sparse."
        )
    else:
        theory.mechanism_claims.append(
            f"{task_family} tasks exhibit recurring behavior patterns that need localized interpretation."
        )

    if contradiction_list:
        theory.prescriptive_implications.append(
            "Inspect contradiction patterns before adding stronger governance layers; some failure families may already be partially explained."
        )
    if anomaly_list:
        theory.predictive_claims.append(
            "Repeated anomaly candidates suggest that local improvements may be insufficient for all sub-regimes of this family."
        )

    theory.confidence_score = 0.55 if relevant_concepts else 0.4
    return theory


def build_and_register_theories(
    *,
    task_family: str,
    concepts: Iterable[ConceptCard],
    contradictions: Iterable[dict],
    anomaly_candidates: Iterable[dict],
    registry: InMemoryTheoryRegistry,
) -> LocalTheoryObject | None:
    theory = build_local_theory(
        task_family=task_family,
        concepts=concepts,
        contradictions=contradictions,
        anomaly_candidates=anomaly_candidates,
    )
    if not theory:
        return None
    return registry.add_theory(theory)
