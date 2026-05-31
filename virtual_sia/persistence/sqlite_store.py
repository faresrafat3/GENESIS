"""SQLite-backed memory store with same interface as InMemoryMemoryStore."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from typing import List, Optional

from ..core.objects.memory import MemoryUnit
from ..core.objects.scope import Scope
from .migrations import initialize_database


class SQLiteMemoryStore:
    """Persistent memory store backed by SQLite.

    Drop-in replacement for InMemoryMemoryStore with the same interface.
    Uses a single persistent connection per instance.
    """

    def __init__(self, db_path: str = "./sia_data.db") -> None:
        self._db_path = db_path
        initialize_database(db_path)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        # Restore _tick from persisted data so decay calculations
        # remain correct across process restarts.
        row = self._conn.execute(
            "SELECT MAX(last_accessed) AS max_tick FROM memories"
        ).fetchone()
        self._tick: int = row["max_tick"] if row["max_tick"] is not None else 0
        self._last_decay_tick: int = -1

    def close(self) -> None:
        """Close the underlying database connection."""
        self._conn.close()

    def store_memory(self, unit: MemoryUnit) -> MemoryUnit:
        self._tick += 1
        unit.last_accessed = self._tick
        self._conn.execute(
            """INSERT OR REPLACE INTO memories
               (id, object_type, memory_type, content_type, summary,
                scope_json, utility_score, staleness_score, salience,
                identity_relevance, ownership, linked_objects_json,
                decay_score, last_accessed, access_count, memory_status, meta_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                unit.id,
                unit.object_type,
                unit.memory_type,
                unit.content_type,
                unit.summary,
                json.dumps(asdict(unit.scope)),
                unit.utility_score,
                unit.staleness_score,
                unit.salience,
                unit.identity_relevance,
                unit.ownership,
                json.dumps(unit.linked_objects),
                unit.decay_score,
                unit.last_accessed,
                unit.access_count,
                unit.memory_status,
                json.dumps(unit.meta) if unit.meta else "{}",
            ),
        )
        self._conn.commit()
        return unit

    def get(self, memory_id: str) -> Optional[MemoryUnit]:
        row = self._conn.execute(
            "SELECT * FROM memories WHERE id = ?", (memory_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_unit(row)

    def all(self) -> List[MemoryUnit]:
        rows = self._conn.execute("SELECT * FROM memories").fetchall()
        return [self._row_to_unit(r) for r in rows]

    def apply_decay(self, decay_rate: float = 0.05) -> None:
        """Reduce decay_score for all active memories based on staleness."""
        if self._tick == self._last_decay_tick:
            return
        rows = self._conn.execute(
            "SELECT id, decay_score, last_accessed FROM memories WHERE memory_status = 'active'"
        ).fetchall()
        for row in rows:
            staleness = (self._tick - row["last_accessed"]) * decay_rate
            new_score = max(0.0, min(1.0, row["decay_score"] - staleness))
            self._conn.execute(
                "UPDATE memories SET decay_score = ? WHERE id = ?",
                (new_score, row["id"]),
            )
        self._conn.commit()
        self._last_decay_tick = self._tick

    def archive_memory(self, memory_id: str) -> None:
        """Set memory_status to 'archived'."""
        self._update_status(memory_id, "archived")

    def deprecate_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deprecated'."""
        self._update_status(memory_id, "deprecated")

    def delete_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deleted'."""
        self._update_status(memory_id, "deleted")

    def get_active_memories(self) -> List[MemoryUnit]:
        """Return only memories with status 'active'."""
        rows = self._conn.execute(
            "SELECT * FROM memories WHERE memory_status = 'active'"
        ).fetchall()
        return [self._row_to_unit(r) for r in rows]

    def record_access(self, memory_id: str, tick: Optional[int] = None) -> None:
        """Update last_accessed and increment access_count."""
        effective_tick = tick if tick is not None else self._tick
        self._conn.execute(
            "UPDATE memories SET last_accessed = ?, access_count = access_count + 1 WHERE id = ?",
            (effective_tick, memory_id),
        )
        self._conn.commit()

    def _update_status(self, memory_id: str, status: str) -> None:
        self._conn.execute(
            "UPDATE memories SET memory_status = ? WHERE id = ?",
            (status, memory_id),
        )
        self._conn.commit()

    def _row_to_unit(self, row: sqlite3.Row) -> MemoryUnit:
        scope_data = json.loads(row["scope_json"])
        meta_data = json.loads(row["meta_json"])
        linked = json.loads(row["linked_objects_json"])
        return MemoryUnit(
            id=row["id"],
            object_type=row["object_type"],
            memory_type=row["memory_type"],
            content_type=row["content_type"],
            summary=row["summary"],
            scope=Scope(**scope_data),
            utility_score=row["utility_score"],
            staleness_score=row["staleness_score"],
            salience=row["salience"],
            identity_relevance=row["identity_relevance"],
            ownership=row["ownership"],
            linked_objects=linked,
            decay_score=row["decay_score"],
            last_accessed=row["last_accessed"],
            access_count=row["access_count"],
            memory_status=row["memory_status"],
            meta=meta_data if meta_data else None,
        )
