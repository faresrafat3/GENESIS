from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseObject, make_id
from .scope import Scope
from .provenance import Provenance


@dataclass(slots=True)
class ConceptCandidate(BaseObject):
    proposed_name: str = ""
    short_definition: str = ""
    contrastive_basis: List[str] = field(default_factory=list)
    supporting_episode_refs: List[str] = field(default_factory=list)
    supporting_pattern_refs: List[str] = field(default_factory=list)
    candidate_scope: Scope = field(default_factory=Scope)
    counterexample_refs: List[str] = field(default_factory=list)
    candidate_value: Optional[float] = None
    recommendation: str = "keep_as_heuristic"

    @classmethod
    def create(cls, proposed_name: str, short_definition: str) -> "ConceptCandidate":
        return cls(
            id=make_id("concept_candidate"),
            object_type="concept_candidate",
            proposed_name=proposed_name,
            short_definition=short_definition,
        )


@dataclass(slots=True)
class ConceptCard(BaseObject):
    name: str = ""
    definition: str = ""
    operational_meaning: str = ""
    activation_conditions: List[str] = field(default_factory=list)
    scope: Scope = field(default_factory=Scope)
    supporting_pattern_refs: List[str] = field(default_factory=list)
    supporting_episode_refs: List[str] = field(default_factory=list)
    counterexample_refs: List[str] = field(default_factory=list)
    linked_skill_refs: List[str] = field(default_factory=list)
    linked_policy_refs: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    transfer_score: Optional[float] = None
    promotion_stage: str = "validated_concept"

    @classmethod
    def from_candidate(
        cls,
        candidate: ConceptCandidate,
        operational_meaning: str,
    ) -> "ConceptCard":
        return cls(
            id=make_id("concept"),
            object_type="concept",
            name=candidate.proposed_name,
            definition=candidate.short_definition,
            operational_meaning=operational_meaning,
            scope=candidate.candidate_scope,
            supporting_pattern_refs=candidate.supporting_pattern_refs,
            supporting_episode_refs=candidate.supporting_episode_refs,
            counterexample_refs=candidate.counterexample_refs,
        )
