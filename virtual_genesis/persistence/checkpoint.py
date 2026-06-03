"""Session state checkpointing for resumability."""
from __future__ import annotations

import json
import sqlite3
from typing import Optional

from .migrations import initialize_database


def save_checkpoint(session_id: str, state_dict: dict, db_path: str) -> int:
    """Save full state as JSON checkpoint. Returns checkpoint ID."""
    initialize_database(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO checkpoints (session_id, state_json) VALUES (?, ?)",
            (session_id, json.dumps(state_dict)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def load_checkpoint(session_id: str, db_path: str) -> Optional[dict]:
    """Load latest checkpoint for session_id. Returns state dict or None."""
    initialize_database(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT state_json FROM checkpoints WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row["state_json"])
    finally:
        conn.close()
