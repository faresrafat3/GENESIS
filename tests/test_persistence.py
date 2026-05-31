"""Tests for SQLite persistence package."""
from __future__ import annotations

import os
import tempfile

import pytest

from virtual_sia.core.objects.concept import ConceptCandidate, ConceptCard
from virtual_sia.core.objects.identity import AgentIdentityObject
from virtual_sia.core.objects.memory import MemoryUnit
from virtual_sia.core.objects.scope import Scope
from virtual_sia.core.objects.theory import LocalTheoryObject
from virtual_sia.persistence import (
    SQLiteConceptRegistry,
    SQLiteIdentityStore,
    SQLiteMemoryStore,
    SQLiteTheoryRegistry,
    initialize_database,
    load_checkpoint,
    save_checkpoint,
)


@pytest.fixture
def db_path():
    """Create a temporary database path and clean up after test."""
    path = tempfile.mktemp(suffix=".db")
    yield path
    # Cleanup
    for suffix in ("", "-wal", "-shm"):
        try:
            os.unlink(path + suffix)
        except FileNotFoundError:
            pass


class TestMigrations:
    def test_initialize_creates_tables(self, db_path):
        import sqlite3

        initialize_database(db_path)
        conn = sqlite3.connect(db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "memories" in table_names
        assert "concepts" in table_names
        assert "candidates" in table_names
        assert "theories" in table_names
        assert "identity" in table_names
        assert "checkpoints" in table_names
        assert "schema_version" in table_names
        conn.close()

    def test_wal_mode_enabled(self, db_path):
        import sqlite3

        initialize_database(db_path)
        conn = sqlite3.connect(db_path)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"
        conn.close()

    def test_schema_version_recorded(self, db_path):
        import sqlite3

        initialize_database(db_path)
        conn = sqlite3.connect(db_path)
        version = conn.execute("SELECT version FROM schema_version").fetchone()[0]
        assert version == 1
        conn.close()

    def test_initialize_idempotent(self, db_path):
        """Calling initialize twice does not raise."""
        initialize_database(db_path)
        initialize_database(db_path)


class TestSQLiteMemoryStore:
    def test_store_and_get(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("test memory", memory_type="episodic")
        stored = store.store_memory(mem)
        assert stored.id == mem.id
        retrieved = store.get(mem.id)
        assert retrieved is not None
        assert retrieved.summary == "test memory"
        assert retrieved.memory_type == "episodic"

    def test_get_nonexistent_returns_none(self, db_path):
        store = SQLiteMemoryStore(db_path)
        assert store.get("nonexistent_id") is None

    def test_all_returns_all_memories(self, db_path):
        store = SQLiteMemoryStore(db_path)
        m1 = MemoryUnit.create("memory one")
        m2 = MemoryUnit.create("memory two")
        store.store_memory(m1)
        store.store_memory(m2)
        all_mems = store.all()
        assert len(all_mems) == 2
        ids = {m.id for m in all_mems}
        assert m1.id in ids
        assert m2.id in ids

    def test_apply_decay_reduces_score(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("decaying memory")
        mem.decay_score = 1.0
        store.store_memory(mem)
        # Advance tick to create staleness
        store._tick = 10
        store.apply_decay(decay_rate=0.1)
        updated = store.get(mem.id)
        assert updated.decay_score < 1.0

    def test_apply_decay_skips_at_same_tick(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("memory")
        store.store_memory(mem)
        store._tick = 5
        store.apply_decay(0.1)
        first_score = store.get(mem.id).decay_score
        # Calling again at same tick should not compound
        store.apply_decay(0.1)
        second_score = store.get(mem.id).decay_score
        assert first_score == second_score

    def test_archive_memory(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("to archive")
        store.store_memory(mem)
        store.archive_memory(mem.id)
        updated = store.get(mem.id)
        assert updated.memory_status == "archived"

    def test_deprecate_memory(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("to deprecate")
        store.store_memory(mem)
        store.deprecate_memory(mem.id)
        updated = store.get(mem.id)
        assert updated.memory_status == "deprecated"

    def test_delete_memory(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("to delete")
        store.store_memory(mem)
        store.delete_memory(mem.id)
        updated = store.get(mem.id)
        assert updated.memory_status == "deleted"

    def test_get_active_memories(self, db_path):
        store = SQLiteMemoryStore(db_path)
        m1 = MemoryUnit.create("active")
        m2 = MemoryUnit.create("will archive")
        store.store_memory(m1)
        store.store_memory(m2)
        store.archive_memory(m2.id)
        active = store.get_active_memories()
        assert len(active) == 1
        assert active[0].id == m1.id

    def test_record_access(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("accessed memory")
        store.store_memory(mem)
        store.record_access(mem.id, tick=42)
        updated = store.get(mem.id)
        assert updated.last_accessed == 42
        assert updated.access_count == 1

    def test_record_access_increments(self, db_path):
        store = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("multi access")
        store.store_memory(mem)
        store.record_access(mem.id, tick=1)
        store.record_access(mem.id, tick=2)
        updated = store.get(mem.id)
        assert updated.access_count == 2
        assert updated.last_accessed == 2

    def test_persistence_across_instances(self, db_path):
        """Data persists when we create a new store pointing to same db."""
        store1 = SQLiteMemoryStore(db_path)
        mem = MemoryUnit.create("persistent data")
        store1.store_memory(mem)
        # Create new store instance
        store2 = SQLiteMemoryStore(db_path)
        retrieved = store2.get(mem.id)
        assert retrieved is not None
        assert retrieved.summary == "persistent data"


class TestSQLiteConceptRegistry:
    def test_add_and_list_candidates(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        c = ConceptCandidate.create("test_concept", "a test concept")
        result = reg.add_candidate(c)
        assert result.id == c.id
        candidates = reg.list_candidates()
        assert len(candidates) == 1
        assert candidates[0].proposed_name == "test_concept"

    def test_get_candidate(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        c = ConceptCandidate.create("get_me", "definition")
        reg.add_candidate(c)
        retrieved = reg.get_candidate(c.id)
        assert retrieved is not None
        assert retrieved.proposed_name == "get_me"

    def test_get_candidate_nonexistent(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        assert reg.get_candidate("nonexistent") is None

    def test_add_candidate_dedup_by_name(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        c1 = ConceptCandidate.create("same_name", "first")
        c2 = ConceptCandidate.create("same_name", "second")
        result1 = reg.add_candidate(c1)
        result2 = reg.add_candidate(c2)
        assert result1.id == result2.id
        assert len(reg.list_candidates()) == 1

    def test_add_and_list_concepts(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        candidate = ConceptCandidate.create("promoted", "a concept")
        concept = ConceptCard.from_candidate(candidate, operational_meaning="used for X")
        result = reg.add_concept(concept)
        assert result.id == concept.id
        concepts = reg.list_concepts()
        assert len(concepts) == 1
        assert concepts[0].name == "promoted"
        assert concepts[0].operational_meaning == "used for X"

    def test_add_concept_dedup_by_name(self, db_path):
        reg = SQLiteConceptRegistry(db_path)
        c1 = ConceptCandidate.create("dup_concept", "first")
        concept1 = ConceptCard.from_candidate(c1, operational_meaning="v1")
        c2 = ConceptCandidate.create("dup_concept", "second")
        concept2 = ConceptCard.from_candidate(c2, operational_meaning="v2")
        r1 = reg.add_concept(concept1)
        r2 = reg.add_concept(concept2)
        assert r1.id == r2.id
        assert len(reg.list_concepts()) == 1


class TestSQLiteTheoryRegistry:
    def test_add_and_list_theories(self, db_path):
        reg = SQLiteTheoryRegistry(db_path)
        t = LocalTheoryObject.create("my_theory", "does X cause Y?")
        result = reg.add_theory(t)
        assert result.id == t.id
        theories = reg.list_theories()
        assert len(theories) == 1
        assert theories[0].name == "my_theory"
        assert theories[0].core_question == "does X cause Y?"

    def test_add_theory_dedup_by_name(self, db_path):
        reg = SQLiteTheoryRegistry(db_path)
        t1 = LocalTheoryObject.create("same_theory", "q1")
        t2 = LocalTheoryObject.create("same_theory", "q2")
        r1 = reg.add_theory(t1)
        r2 = reg.add_theory(t2)
        assert r1.id == r2.id
        assert len(reg.list_theories()) == 1

    def test_theory_fields_preserved(self, db_path):
        reg = SQLiteTheoryRegistry(db_path)
        t = LocalTheoryObject.create("detailed_theory", "complex question")
        t.predictive_value = 0.8
        t.explanatory_power = 0.6
        t.prediction_count = 5
        t.correct_predictions = 4
        t.mechanism_claims = ["claim1", "claim2"]
        reg.add_theory(t)
        loaded = reg.list_theories()[0]
        assert loaded.predictive_value == 0.8
        assert loaded.explanatory_power == 0.6
        assert loaded.prediction_count == 5
        assert loaded.correct_predictions == 4
        assert loaded.mechanism_claims == ["claim1", "claim2"]


class TestSQLiteIdentityStore:
    def test_save_and_load_identity(self, db_path):
        store = SQLiteIdentityStore(db_path)
        identity = AgentIdentityObject.create(
            commitments=["accuracy", "ethics"],
            self_model={"version": "1.0"},
        )
        store.save_identity(identity)
        loaded = store.load_identity(identity.id)
        assert loaded is not None
        assert loaded.commitments == ["accuracy", "ethics"]
        assert loaded.self_model == {"version": "1.0"}

    def test_load_nonexistent(self, db_path):
        store = SQLiteIdentityStore(db_path)
        assert store.load_identity("nonexistent") is None

    def test_load_latest(self, db_path):
        store = SQLiteIdentityStore(db_path)
        i1 = AgentIdentityObject.create(
            commitments=["old"], self_model={"v": "1"}
        )
        i2 = AgentIdentityObject.create(
            commitments=["new"], self_model={"v": "2"}
        )
        store.save_identity(i1)
        store.save_identity(i2)
        latest = store.load_latest()
        assert latest is not None
        # Should be the second one saved (latest updated_at)
        assert latest.id == i2.id

    def test_load_latest_empty(self, db_path):
        store = SQLiteIdentityStore(db_path)
        assert store.load_latest() is None


class TestCheckpoint:
    def test_save_returns_id(self, db_path):
        cp_id = save_checkpoint("session_1", {"key": "value"}, db_path)
        assert isinstance(cp_id, int)
        assert cp_id >= 1

    def test_load_returns_state(self, db_path):
        save_checkpoint("session_1", {"counter": 42}, db_path)
        state = load_checkpoint("session_1", db_path)
        assert state == {"counter": 42}

    def test_load_returns_latest(self, db_path):
        save_checkpoint("sess", {"version": 1}, db_path)
        save_checkpoint("sess", {"version": 2}, db_path)
        state = load_checkpoint("sess", db_path)
        assert state == {"version": 2}

    def test_load_nonexistent_session(self, db_path):
        initialize_database(db_path)
        state = load_checkpoint("nonexistent", db_path)
        assert state is None

    def test_sessions_isolated(self, db_path):
        save_checkpoint("session_a", {"data": "a"}, db_path)
        save_checkpoint("session_b", {"data": "b"}, db_path)
        assert load_checkpoint("session_a", db_path) == {"data": "a"}
        assert load_checkpoint("session_b", db_path) == {"data": "b"}


class TestSessionWithPersistence:
    def test_session_uses_sqlite_stores(self, db_path):
        from virtual_sia.api.config import APIConfig
        from virtual_sia.api.session import Session

        config = APIConfig(use_persistence=True, db_path=db_path)
        session = Session(config=config)
        assert isinstance(session.memory_store, SQLiteMemoryStore)
        assert isinstance(session.concept_registry, SQLiteConceptRegistry)
        assert isinstance(session.theory_registry, SQLiteTheoryRegistry)

    def test_session_without_persistence_uses_inmemory(self):
        from virtual_sia.api.config import APIConfig
        from virtual_sia.api.session import Session
        from virtual_sia.runtime.memory_os.store import InMemoryMemoryStore

        config = APIConfig(use_persistence=False)
        session = Session(config=config)
        assert isinstance(session.memory_store, InMemoryMemoryStore)

    def test_session_no_config_uses_inmemory(self):
        from virtual_sia.api.session import Session
        from virtual_sia.runtime.memory_os.store import InMemoryMemoryStore

        session = Session()
        assert isinstance(session.memory_store, InMemoryMemoryStore)
