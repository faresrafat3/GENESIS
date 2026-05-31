"""SQLite-backed identity store for persisting AgentIdentityObject."""
from __future__ import annotations

import json
import sqlite3
from typing import Optional

from ..core.objects.identity import AgentIdentityObject
from .migrations import initialize_database


class SQLiteIdentityStore:
    """Persistent identity store backed by SQLite.

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

    def save_identity(self, identity: AgentIdentityObject) -> None:
        """Persist an identity object (insert or replace)."""
        self._conn.execute(
            """INSERT OR REPLACE INTO identity
               (id, object_type, commitments_json, self_model_json,
                lineage_json, drift_score, accountability_log_json,
                policy_signature_json, meta_json, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (
                identity.id,
                identity.object_type,
                json.dumps(identity.commitments),
                json.dumps(identity.self_model),
                json.dumps(identity.lineage),
                identity.drift_score,
                json.dumps(identity.accountability_log),
                json.dumps(identity.policy_signature),
                json.dumps(identity.meta) if identity.meta else "{}",
            ),
        )
        self._conn.commit()

    def load_identity(self, identity_id: str) -> Optional[AgentIdentityObject]:
        """Load identity by ID."""
        row = self._conn.execute(
            "SELECT * FROM identity WHERE id = ?", (identity_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_identity(row)

    def load_latest(self) -> Optional[AgentIdentityObject]:
        """Load the most recently updated identity."""
        row = self._conn.execute(
            "SELECT * FROM identity ORDER BY updated_at DESC, rowid DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return self._row_to_identity(row)

    def _row_to_identity(self, row: sqlite3.Row) -> AgentIdentityObject:
        meta_data = json.loads(row["meta_json"])
        return AgentIdentityObject(
            id=row["id"],
            object_type=row["object_type"],
            commitments=json.loads(row["commitments_json"]),
            self_model=json.loads(row["self_model_json"]),
            lineage=json.loads(row["lineage_json"]),
            drift_score=row["drift_score"],
            accountability_log=json.loads(row["accountability_log_json"]),
            policy_signature=json.loads(row["policy_signature_json"]),
            meta=meta_data if meta_data else None,
        )
