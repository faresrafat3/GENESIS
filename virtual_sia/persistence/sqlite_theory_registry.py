"""SQLite-backed theory registry with same interface as InMemoryTheoryRegistry."""
from __future__ import annotations

import json
import sqlite3
from typing import List

from ..core.objects.theory import LocalTheoryObject
from ..core.objects.scope import Scope
from .migrations import initialize_database


class SQLiteTheoryRegistry:
    """Persistent theory registry backed by SQLite.

    Drop-in replacement for InMemoryTheoryRegistry with the same interface.
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

    def add_theory(self, theory: LocalTheoryObject) -> LocalTheoryObject:
        existing = self._conn.execute(
            "SELECT id FROM theories WHERE name = ?",
            (theory.name,),
        ).fetchone()
        if existing:
            return self._load_theory(existing["id"])
        claims = theory.mechanism_claims + theory.predictive_claims
        data = {
            "core_question": theory.core_question,
            "concept_refs": theory.concept_refs,
            "contradiction_refs": theory.contradiction_refs,
            "anomaly_candidate_refs": theory.anomaly_candidate_refs,
            "mechanism_claims": theory.mechanism_claims,
            "predictive_claims": theory.predictive_claims,
            "prescriptive_implications": theory.prescriptive_implications,
            "confidence_score": theory.confidence_score,
            "scope": {
                "task_families": theory.scope.task_families,
                "positive_conditions": theory.scope.positive_conditions,
                "negative_conditions": theory.scope.negative_conditions,
                "ambiguity_zone": theory.scope.ambiguity_zone,
                "confidence": theory.scope.confidence,
            },
            "meta": theory.meta,
        }
        self._conn.execute(
            """INSERT INTO theories
               (id, object_type, name, family, claims_json,
                predictive_value, explanatory_power, prediction_count,
                correct_predictions, data_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                theory.id,
                theory.object_type,
                theory.name,
                "",
                json.dumps(claims),
                theory.predictive_value,
                theory.explanatory_power,
                theory.prediction_count,
                theory.correct_predictions,
                json.dumps(data),
            ),
        )
        self._conn.commit()
        return theory

    def list_theories(self) -> List[LocalTheoryObject]:
        rows = self._conn.execute("SELECT * FROM theories").fetchall()
        return [self._row_to_theory(r) for r in rows]

    def _load_theory(self, theory_id: str) -> LocalTheoryObject:
        row = self._conn.execute(
            "SELECT * FROM theories WHERE id = ?", (theory_id,)
        ).fetchone()
        return self._row_to_theory(row)

    def _row_to_theory(self, row: sqlite3.Row) -> LocalTheoryObject:
        data = json.loads(row["data_json"])
        scope_data = data.get("scope", {})
        return LocalTheoryObject(
            id=row["id"],
            object_type=row["object_type"],
            name=row["name"],
            core_question=data.get("core_question", ""),
            scope=Scope(
                task_families=scope_data.get("task_families", []),
                positive_conditions=scope_data.get("positive_conditions", []),
                negative_conditions=scope_data.get("negative_conditions", []),
                ambiguity_zone=scope_data.get("ambiguity_zone", []),
                confidence=scope_data.get("confidence"),
            ),
            concept_refs=data.get("concept_refs", []),
            contradiction_refs=data.get("contradiction_refs", []),
            anomaly_candidate_refs=data.get("anomaly_candidate_refs", []),
            mechanism_claims=data.get("mechanism_claims", []),
            predictive_claims=data.get("predictive_claims", []),
            prescriptive_implications=data.get("prescriptive_implications", []),
            confidence_score=data.get("confidence_score"),
            predictive_value=row["predictive_value"],
            explanatory_power=row["explanatory_power"],
            prediction_count=row["prediction_count"],
            correct_predictions=row["correct_predictions"],
            meta=data.get("meta"),
        )
