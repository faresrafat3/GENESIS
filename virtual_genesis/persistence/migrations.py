"""Database schema creation and versioning."""
from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 1

# Module-level set tracking which db_paths have already been initialized
# in this process. Avoids running DDL on every store instantiation.
_initialized_paths: set[str] = set()


def initialize_database(db_path: str) -> None:
    """Create all tables and enable WAL mode.

    Only runs DDL on the first call for a given db_path within this process.
    """
    if db_path in _initialized_paths:
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            object_type TEXT DEFAULT 'memory',
            memory_type TEXT DEFAULT 'episodic',
            content_type TEXT DEFAULT 'episode_summary',
            summary TEXT DEFAULT '',
            scope_json TEXT DEFAULT '{}',
            utility_score REAL,
            staleness_score REAL,
            salience REAL,
            identity_relevance TEXT DEFAULT 'low',
            ownership TEXT DEFAULT 'task-derived',
            linked_objects_json TEXT DEFAULT '[]',
            decay_score REAL DEFAULT 1.0,
            last_accessed INTEGER DEFAULT 0,
            access_count INTEGER DEFAULT 0,
            memory_status TEXT DEFAULT 'active',
            meta_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS concepts (
            id TEXT PRIMARY KEY,
            object_type TEXT DEFAULT 'concept',
            name TEXT UNIQUE,
            definition TEXT DEFAULT '',
            scope_json TEXT DEFAULT '{}',
            confidence_score REAL DEFAULT 0.0,
            predictive_value REAL DEFAULT 0.0,
            data_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            object_type TEXT DEFAULT 'concept_candidate',
            proposed_name TEXT UNIQUE,
            data_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS theories (
            id TEXT PRIMARY KEY,
            object_type TEXT DEFAULT 'local_theory',
            name TEXT UNIQUE,
            family TEXT DEFAULT '',
            claims_json TEXT DEFAULT '[]',
            predictive_value REAL DEFAULT 0.5,
            explanatory_power REAL DEFAULT 0.0,
            prediction_count INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            data_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS identity (
            id TEXT PRIMARY KEY,
            object_type TEXT DEFAULT 'agent_identity',
            commitments_json TEXT DEFAULT '[]',
            self_model_json TEXT DEFAULT '{}',
            lineage_json TEXT DEFAULT '[]',
            drift_score REAL DEFAULT 0.0,
            accountability_log_json TEXT DEFAULT '[]',
            policy_signature_json TEXT DEFAULT '[]',
            meta_json TEXT DEFAULT '{}',
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            state_json TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(memory_status);
        CREATE INDEX IF NOT EXISTS idx_checkpoints_session ON checkpoints(session_id);
    """)

    # Record schema version
    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
        (SCHEMA_VERSION,),
    )
    conn.commit()
    conn.close()

    _initialized_paths.add(db_path)
