from __future__ import annotations

from ...core.objects.concept import ConceptCandidate, ConceptCard
from ...core.objects.memory import MemoryUnit
from .registry import InMemoryConceptRegistry


def _family_contrast_candidate(family: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    if family == "comparison":
        name = "Evidence Sufficiency Contrast"
        definition = "Comparison tasks often fail when the answer states differences without enough supporting evidence anchors."
    elif family == "synthesis":
        name = "Ungrounded Synthesis Risk"
        definition = "Synthesis tasks often fail when multiple snippets are merged without explicit grounding of claims to evidence fragments."
    elif family == "procedure":
        name = "Stable Procedure Reuse Opportunity"
        definition = "Some procedure tasks repeatedly benefit from reusing a consistent workflow instead of reasoning from scratch."
    else:
        name = f"{family.title()} Pattern Contrast"
        definition = f"The {family} family shows a recurring contrast between successful and failed episodes worth abstracting."

    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"{len(successes)} successful episodes",
        f"{len(failures)} failed episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:3] + failures[:3]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}"]
    candidate.candidate_scope.negative_conditions = ["insufficient supporting examples outside family"]
    candidate.candidate_value = 0.6
    candidate.recommendation = "validate_as_concept"
    return candidate


def _property_gap_candidate(family: str, prop: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    name = f"{family.title()} {prop.title()} Gap"
    definition = f"{family.title()} tasks become unreliable when the required property `{prop}` is not satisfied consistently."
    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"property={prop}",
        f"{len(successes)} passing episodes",
        f"{len(failures)} failing episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:2] + failures[:4]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}", f"requires_property == {prop}"]
    candidate.candidate_scope.negative_conditions = ["do not over-apply outside matching evaluation contract"]
    candidate.candidate_value = 0.7 if len(failures) >= 2 else 0.55
    candidate.recommendation = "validate_as_concept"
    return candidate


def _shortcut_gap_candidate(family: str, shortcut: str, successes: list[MemoryUnit], failures: list[MemoryUnit]) -> ConceptCandidate:
    name = f"{family.title()} {shortcut.title()} Avoidance"
    definition = f"{family.title()} tasks frequently fail when the shortcut `{shortcut}` is triggered; successful handling must explicitly avoid this pattern."
    candidate = ConceptCandidate.create(name, definition)
    candidate.contrastive_basis = [
        f"shortcut={shortcut}",
        f"{len(successes)} shortcut-free episodes",
        f"{len(failures)} shortcut-violating episodes",
    ]
    candidate.supporting_episode_refs = [m.id for m in successes[:2] + failures[:4]]
    candidate.candidate_scope.task_families = [family]
    candidate.candidate_scope.positive_conditions = [f"task_family == {family}", f"avoid_shortcut == {shortcut}"]
    candidate.candidate_scope.negative_conditions = ["may be irrelevant when shortcut is structurally impossible"]
    candidate.candidate_value = 0.75 if len(failures) >= 2 else 0.55
    candidate.recommendation = "validate_as_concept"
    return candidate


def propose_concepts_from_groups(groups: list[dict]) -> list[ConceptCandidate]:
    candidates: list[ConceptCandidate] = []
    for group in groups:
        family = group["family"]
        successes = group["successes"]
        failures = group["failures"]
        group_type = group["group_type"]
        prop = group.get("property_name")
        shortcut = group.get("shortcut_name")

        if group_type == "family_contrast":
            candidate = _family_contrast_candidate(family, successes, failures)
        elif group_type == "property_gap" and prop is not None:
            candidate = _property_gap_candidate(family, prop, successes, failures)
        elif group_type == "shortcut_gap" and shortcut is not None:
            candidate = _shortcut_gap_candidate(family, shortcut, successes, failures)
        else:
            continue
        candidates.append(candidate)
    return candidates


def _operational_meaning_for_candidate(candidate: ConceptCandidate) -> str:
    name = candidate.proposed_name.lower()
    if "evidence sufficiency contrast" in name:
        return "When comparing options, force an explicit evidence-backed contrast instead of a generic preference."
    if "ungrounded synthesis risk" in name:
        return "When synthesizing fragments, anchor every major conclusion to observed evidence and avoid unsupported merging."
    if "stable procedure reuse opportunity" in name:
        return "Prefer a stable checklist or field-oriented workflow instead of regenerating the structure from scratch."
    if "gap" in name and "comparison" in name:
        return "Make the comparison criterion explicit and tie the preferred option to evidence, not just wording."
    if "gap" in name and "synthesis" in name:
        return "Separate observations from inference and preserve at least one explicit evidence hook for the conclusion."
    if "avoidance" in name and "summary without distinction" in name:
        return "Do not collapse the answer into a generic summary; preserve the decisive distinction and the evidence behind it."
    if "avoidance" in name and "generic preference without evidence" in name:
        return "Avoid choosing an option without stating why the evidence makes it stronger or safer."
    return "Use this concept to influence retrieval, verification emphasis, or procedural reuse decisions."


def _compute_evidence_strength(candidate: ConceptCandidate) -> tuple[float, float]:
    """Compute (confidence_score, transfer_score) from evidence strength.

    Factors:
      - Number of supporting episodes (more = higher confidence)
      - Contrastive basis count (more contrastive axes = higher value)
      - Presence of counterexamples (narrows transfer)
      - Scope breadth (broader scope = higher transfer risk)
    """
    n_support = len(candidate.supporting_episode_refs or [])
    n_basis = len(candidate.contrastive_basis or [])
    n_counter = len(candidate.counterexample_refs or [])
    n_families = len(candidate.candidate_scope.task_families or [])

    # Confidence: evidence volume + contrastive richness
    base_confidence = 0.5
    support_bonus = min(n_support * 0.04, 0.25)  # up to +0.25
    basis_bonus = min(n_basis * 0.05, 0.15)       # up to +0.15
    counterexample_penalty = min(n_counter * 0.03, 0.1)
    confidence = min(base_confidence + support_bonus + basis_bonus - counterexample_penalty, 0.95)
    confidence = max(confidence, 0.3)

    # Transfer: inversely related to specificity
    base_transfer = 0.3
    family_penalty = max(0, (n_families - 1) * 0.05)  # multi-family = slightly riskier
    counterexample_transfer_penalty = min(n_counter * 0.04, 0.15)
    transfer = max(base_transfer - family_penalty - counterexample_transfer_penalty, 0.1)
    # Strong evidence can slightly raise transfer
    if n_support >= 4 and n_basis >= 2:
        transfer = min(transfer + 0.1, 0.5)

    return round(confidence, 2), round(transfer, 2)


def _is_redundant(candidate: ConceptCandidate, existing_concepts: list[ConceptCard]) -> bool:
    """Check if a candidate is semantically redundant with an existing concept.

    Uses token overlap on name + definition to detect near-duplicates.
    """
    candidate_tokens = _tokenize(candidate.proposed_name + " " + candidate.short_definition)
    for concept in existing_concepts:
        existing_tokens = _tokenize(concept.name + " " + concept.definition)
        if len(candidate_tokens) == 0 or len(existing_tokens) == 0:
            continue
        overlap = len(candidate_tokens & existing_tokens)
        union = len(candidate_tokens | existing_tokens)
        jaccard = overlap / union if union > 0 else 0.0
        # Threshold: 60% Jaccard overlap OR exact family+type match with high token overlap
        if jaccard >= 0.6:
            return True
        if overlap >= 5:
            return True
    return False


def _tokenize(text: str) -> set[str]:
    """Tokenize with basic stopword filtering to reduce noise in comparisons."""
    _STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "about", "between",
        "through", "during", "before", "after", "above", "below", "not",
        "no", "nor", "and", "but", "or", "if", "than", "that", "this",
        "these", "those", "it", "its", "when", "where", "how", "what",
        "which", "who", "whom", "while", "because", "so", "very", "too",
        "also", "just", "then", "there", "here", "each", "every", "all",
        "both", "few", "more", "most", "other", "some", "such", "only",
        "own", "same", "often", "repeatedly", "worth", "without",
    }
    raw = {t.strip('.,:;!?()[]{}').lower() for t in text.split()}
    return {t for t in raw if t and t not in _STOPWORDS and len(t) > 1}


def promote_candidate(
    registry: InMemoryConceptRegistry,
    candidate_id: str,
    skip_redundancy_check: bool = False,
) -> ConceptCard | None:
    candidate = registry.get_candidate(candidate_id)
    if not candidate:
        return None

    # --- Drift guard: reject promotion if redundant with existing concepts ---
    if not skip_redundancy_check and _is_redundant(candidate, registry.list_concepts()):
        return None

    # --- Evidence-based scoring instead of hardcoded values ---
    confidence, transfer = _compute_evidence_strength(candidate)

    concept = ConceptCard.from_candidate(
        candidate,
        operational_meaning=_operational_meaning_for_candidate(candidate),
    )
    concept.activation_conditions = candidate.candidate_scope.positive_conditions.copy()
    concept.confidence_score = confidence
    concept.transfer_score = transfer
    registry.add_concept(concept)
    return concept
