from __future__ import annotations

from typing import Dict, List

from ...core.objects.concept import ConceptCandidate, ConceptCard


class InMemoryConceptRegistry:
    def __init__(self) -> None:
        self._candidates: Dict[str, ConceptCandidate] = {}
        self._concepts: Dict[str, ConceptCard] = {}
        self._candidate_name_index: Dict[str, str] = {}
        self._concept_name_index: Dict[str, str] = {}

    def add_candidate(self, candidate: ConceptCandidate) -> ConceptCandidate:
        existing_id = self._candidate_name_index.get(candidate.proposed_name)
        if existing_id:
            return self._candidates[existing_id]
        self._candidates[candidate.id] = candidate
        self._candidate_name_index[candidate.proposed_name] = candidate.id
        return candidate

    def get_candidate(self, candidate_id: str) -> ConceptCandidate | None:
        return self._candidates.get(candidate_id)

    def add_concept(self, concept: ConceptCard) -> ConceptCard:
        existing_id = self._concept_name_index.get(concept.name)
        if existing_id:
            return self._concepts[existing_id]
        self._concepts[concept.id] = concept
        self._concept_name_index[concept.name] = concept.id
        return concept

    def list_candidates(self) -> List[ConceptCandidate]:
        return list(self._candidates.values())

    def list_concepts(self) -> List[ConceptCard]:
        return list(self._concepts.values())
