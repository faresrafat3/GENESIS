from __future__ import annotations

from ...core.objects.concept import ConceptCandidate


def draft_scope(candidate: ConceptCandidate) -> ConceptCandidate:
    """Strengthen scope boundaries to prevent semantic drift.

    1. Add ambiguity_zone if missing.
    2. Derive specificity guards from contrastive basis so the concept
       does not over-generalise beyond the evidence that supports it.
    3. Cap scope breadth: a concept grounded in a single family should
       not claim broad applicability unless evidence says otherwise.
    """
    if not candidate.candidate_scope.ambiguity_zone:
        candidate.candidate_scope.ambiguity_zone = [
            "near-domain tasks with mixed structure may require manual review"
        ]

    # --- Specificity guard: encode key discriminators from contrastive basis ---
    # If the contrastive basis mentions a property or shortcut, record it as
    # a negative-condition so the concept is NOT applied where that axis is
    # structurally absent.
    props = [b for b in candidate.contrastive_basis if "property=" in b.lower()]
    shortcuts = [b for b in candidate.contrastive_basis if "shortcut=" in b.lower()]

    existing_neg = set(candidate.candidate_scope.negative_conditions or [])
    for p in props:
        guard = f"do not apply when {p.strip()} is not part of evaluation contract"
        if guard not in existing_neg:
            candidate.candidate_scope.negative_conditions.append(guard)
            existing_neg.add(guard)
    for s in shortcuts:
        guard = f"do not apply when {s.strip()} cannot occur in task structure"
        if guard not in existing_neg:
            candidate.candidate_scope.negative_conditions.append(guard)
            existing_neg.add(guard)

    # --- Breadth cap: keep single-family concepts scoped tightly ---
    families = candidate.candidate_scope.task_families or []
    if len(families) == 1:
        existing_pos = set(candidate.candidate_scope.positive_conditions or [])
        fam_guard = f"task_family == {families[0]}"
        if fam_guard not in existing_pos:
            candidate.candidate_scope.positive_conditions.append(fam_guard)

    return candidate
