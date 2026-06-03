"""SQLite-backed concept registry with same interface as InMemoryConceptRegistry."""
from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from ..core.objects.concept import ConceptCandidate, ConceptCard
from ..core.objects.scope import Scope
from .migrations import initialize_database


class SQLiteConceptRegistry:
    """Persistent concept registry backed by SQLite.

    Drop-in replacement for InMemoryConceptRegistry with the same interface.
    Uses a single persistent connection per instance.
    """

    def __init__(self, db_path: str = "./sia_data.db") -> None:
        self._db_path = db_path
        initialize_database(db_path)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def add_candidate(self, candidate: ConceptCandidate) -> ConceptCandidate:
        # Check for existing candidate with same proposed_name
        existing = self._conn.execute(
            "SELECT id FROM candidates WHERE proposed_name = ?",
            (candidate.proposed_name,),
        ).fetchone()
        if existing:
            return self._load_candidate(existing["id"])
        data = {
            "short_definition": candidate.short_definition,
            "contrastive_basis": candidate.contrastive_basis,
            "supporting_episode_refs": candidate.supporting_episode_refs,
            "supporting_pattern_refs": candidate.supporting_pattern_refs,
            "candidate_scope": {
                "task_families": candidate.candidate_scope.task_families,
                "positive_conditions": candidate.candidate_scope.positive_conditions,
                "negative_conditions": candidate.candidate_scope.negative_conditions,
                "ambiguity_zone": candidate.candidate_scope.ambiguity_zone,
                "confidence": candidate.candidate_scope.confidence,
            },
            "counterexample_refs": candidate.counterexample_refs,
            "candidate_value": candidate.candidate_value,
            "recommendation": candidate.recommendation,
            "meta": candidate.meta,
        }
        self._conn.execute(
            "INSERT INTO candidates (id, object_type, proposed_name, data_json) VALUES (?, ?, ?, ?)",
            (candidate.id, candidate.object_type, candidate.proposed_name, json.dumps(data)),
        )
        self._conn.commit()
        return candidate

    def get_candidate(self, candidate_id: str) -> Optional[ConceptCandidate]:
        return self._load_candidate(candidate_id)

    def add_concept(self, concept: ConceptCard) -> ConceptCard:
        existing = self._conn.execute(
            "SELECT id FROM concepts WHERE name = ?",
            (concept.name,),
        ).fetchone()
        if existing:
            return self._load_concept(existing["id"])
        from dataclasses import asdict
        scope_data = asdict(concept.scope)
        data = {
            "operational_meaning": concept.operational_meaning,
            "activation_conditions": concept.activation_conditions,
            "supporting_pattern_refs": concept.supporting_pattern_refs,
            "supporting_episode_refs": concept.supporting_episode_refs,
            "counterexample_refs": concept.counterexample_refs,
            "linked_skill_refs": concept.linked_skill_refs,
            "linked_policy_refs": concept.linked_policy_refs,
            "transfer_score": concept.transfer_score,
            "promotion_stage": concept.promotion_stage,
            "meta": concept.meta,
        }
        self._conn.execute(
            """INSERT INTO concepts (id, object_type, name, definition, scope_json,
               confidence_score, predictive_value, data_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                concept.id,
                concept.object_type,
                concept.name,
                concept.definition,
                json.dumps(scope_data),
                concept.confidence_score or 0.0,
                concept.transfer_score or 0.0,
                json.dumps(data),
            ),
        )
        self._conn.commit()
        return concept

    def list_candidates(self) -> List[ConceptCandidate]:
        rows = self._conn.execute("SELECT * FROM candidates").fetchall()
        return [self._row_to_candidate(r) for r in rows]

    def list_concepts(self) -> List[ConceptCard]:
        rows = self._conn.execute("SELECT * FROM concepts").fetchall()
        return [self._row_to_concept(r) for r in rows]

    def _load_candidate(self, candidate_id: str) -> Optional[ConceptCandidate]:
        row = self._conn.execute(
            "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_candidate(row)

    def _load_concept(self, concept_id: str) -> Optional[ConceptCard]:
        row = self._conn.execute(
            "SELECT * FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_concept(row)

    def _row_to_candidate(self, row: sqlite3.Row) -> ConceptCandidate:
        data = json.loads(row["data_json"])
        scope_data = data.get("candidate_scope", {})
        return ConceptCandidate(
            id=row["id"],
            object_type=row["object_type"],
            proposed_name=row["proposed_name"],
            short_definition=data.get("short_definition", ""),
            contrastive_basis=data.get("contrastive_basis", []),
            supporting_episode_refs=data.get("supporting_episode_refs", []),
            supporting_pattern_refs=data.get("supporting_pattern_refs", []),
            candidate_scope=Scope(
                task_families=scope_data.get("task_families", []),
                positive_conditions=scope_data.get("positive_conditions", []),
                negative_conditions=scope_data.get("negative_conditions", []),
                ambiguity_zone=scope_data.get("ambiguity_zone", []),
                confidence=scope_data.get("confidence"),
            ),
            counterexample_refs=data.get("counterexample_refs", []),
            candidate_value=data.get("candidate_value"),
            recommendation=data.get("recommendation", "keep_as_heuristic"),
            meta=data.get("meta"),
        )

    def _row_to_concept(self, row: sqlite3.Row) -> ConceptCard:
        data = json.loads(row["data_json"])
        scope_data = json.loads(row["scope_json"])
        return ConceptCard(
            id=row["id"],
            object_type=row["object_type"],
            name=row["name"],
            definition=row["definition"],
            scope=Scope(
                task_families=scope_data.get("task_families", []),
                positive_conditions=scope_data.get("positive_conditions", []),
                negative_conditions=scope_data.get("negative_conditions", []),
                ambiguity_zone=scope_data.get("ambiguity_zone", []),
                confidence=scope_data.get("confidence"),
            ),
            confidence_score=row["confidence_score"],
            transfer_score=data.get("transfer_score"),
            operational_meaning=data.get("operational_meaning", ""),
            activation_conditions=data.get("activation_conditions", []),
            supporting_pattern_refs=data.get("supporting_pattern_refs", []),
            supporting_episode_refs=data.get("supporting_episode_refs", []),
            counterexample_refs=data.get("counterexample_refs", []),
            linked_skill_refs=data.get("linked_skill_refs", []),
            linked_policy_refs=data.get("linked_policy_refs", []),
            promotion_stage=data.get("promotion_stage", "validated_concept"),
            meta=data.get("meta"),
        )
