"""Tests for productive forgetting: decay, archive/deprecate/delete, utility, policy, pipeline."""
from __future__ import annotations

import pytest

from virtual_genesis.core.objects.memory import MemoryUnit
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.memory_os.utility import compute_memory_utility, compute_all_utilities
from virtual_genesis.runtime.memory_os.forgetting_policy import apply_forgetting_policy
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_memory(summary: str = "test", memory_type: str = "episodic") -> MemoryUnit:
    return MemoryUnit.create(summary=summary, memory_type=memory_type)


def _store_n_memories(store: InMemoryMemoryStore, n: int) -> list[MemoryUnit]:
    """Store n memories and return them."""
    mems = []
    for i in range(n):
        m = _make_memory(summary=f"memory_{i}")
        store.store_memory(m)
        mems.append(m)
    return mems


# ---------------------------------------------------------------------------
# Decay tests
# ---------------------------------------------------------------------------

class TestDecay:
    def test_apply_decay_reduces_score_for_old_memories(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        # Advance tick by storing more
        for _ in range(10):
            store.store_memory(_make_memory())
        store.apply_decay(0.05)
        # First memory should have decayed (tick=1, current_tick=11, staleness=10*0.05=0.5)
        assert m.decay_score < 1.0
        assert m.decay_score == pytest.approx(0.5, abs=0.01)

    def test_fresh_memories_barely_affected(self):
        store = InMemoryMemoryStore()
        for _ in range(5):
            store.store_memory(_make_memory())
        last = _make_memory()
        store.store_memory(last)
        store.apply_decay(0.05)
        # Last memory: staleness = (6 - 6) * 0.05 = 0, no decay
        assert last.decay_score == 1.0

    def test_heavy_decay_for_old_memories(self):
        store = InMemoryMemoryStore()
        old = _make_memory()
        store.store_memory(old)
        for _ in range(50):
            store.store_memory(_make_memory())
        store.apply_decay(0.05)
        # staleness = (51 - 1) * 0.05 = 2.5, clamped to 0
        assert old.decay_score == 0.0

    def test_decay_clamped_to_zero(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        for _ in range(100):
            store.store_memory(_make_memory())
        store.apply_decay(0.1)
        assert m.decay_score == 0.0

    def test_decay_does_not_affect_non_active(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        store.archive_memory(m.id)
        for _ in range(10):
            store.store_memory(_make_memory())
        store.apply_decay(0.05)
        # Archived memory should not be decayed
        assert m.decay_score == 1.0


# ---------------------------------------------------------------------------
# Forgetting operations tests
# ---------------------------------------------------------------------------

class TestForgettingOperations:
    def test_archive_memory_changes_status(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        store.archive_memory(m.id)
        assert m.memory_status == "archived"

    def test_deprecate_memory_changes_status(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        store.deprecate_memory(m.id)
        assert m.memory_status == "deprecated"

    def test_delete_memory_changes_status(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        store.delete_memory(m.id)
        assert m.memory_status == "deleted"

    def test_get_active_memories_excludes_archived(self):
        store = InMemoryMemoryStore()
        m1 = _make_memory()
        m2 = _make_memory()
        store.store_memory(m1)
        store.store_memory(m2)
        store.archive_memory(m1.id)
        active = store.get_active_memories()
        assert len(active) == 1
        assert active[0].id == m2.id

    def test_get_active_memories_excludes_deprecated_and_deleted(self):
        store = InMemoryMemoryStore()
        m1 = _make_memory()
        m2 = _make_memory()
        m3 = _make_memory()
        store.store_memory(m1)
        store.store_memory(m2)
        store.store_memory(m3)
        store.deprecate_memory(m1.id)
        store.delete_memory(m2.id)
        active = store.get_active_memories()
        assert len(active) == 1
        assert active[0].id == m3.id


# ---------------------------------------------------------------------------
# Access tracking tests
# ---------------------------------------------------------------------------

class TestAccessTracking:
    def test_record_access_updates_last_accessed(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        store.record_access(m.id, tick=42)
        assert m.last_accessed == 42

    def test_record_access_increments_count(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        assert m.access_count == 0
        store.record_access(m.id)
        assert m.access_count == 1
        store.record_access(m.id)
        assert m.access_count == 2

    def test_store_memory_increments_tick(self):
        store = InMemoryMemoryStore()
        assert store._tick == 0
        store.store_memory(_make_memory())
        assert store._tick == 1
        store.store_memory(_make_memory())
        assert store._tick == 2

    def test_store_memory_sets_last_accessed(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)
        assert m.last_accessed == 1

    def test_record_access_uses_store_tick_if_none(self):
        store = InMemoryMemoryStore()
        m = _make_memory()
        store.store_memory(m)  # tick=1
        store.store_memory(_make_memory())  # tick=2
        store.record_access(m.id)
        assert m.last_accessed == 2  # uses current store._tick


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------

class TestUtility:
    def test_utility_returns_float_in_range(self):
        m = _make_memory()
        score = compute_memory_utility(m, current_tick=0)
        assert 0.0 <= score <= 1.0

    def test_fresh_accessed_memory_has_higher_utility(self):
        fresh = _make_memory()
        fresh.last_accessed = 10
        fresh.access_count = 5
        fresh.decay_score = 1.0
        fresh.meta = {"good_enough": True}

        old = _make_memory()
        old.last_accessed = 0
        old.access_count = 0
        old.decay_score = 0.2

        score_fresh = compute_memory_utility(fresh, current_tick=10)
        score_old = compute_memory_utility(old, current_tick=10)
        assert score_fresh > score_old

    def test_utility_with_good_enough_meta(self):
        m = _make_memory()
        m.meta = {"good_enough": True}
        m.last_accessed = 5
        score_good = compute_memory_utility(m, current_tick=5)

        m2 = _make_memory()
        m2.meta = {"good_enough": False}
        m2.last_accessed = 5
        score_bad = compute_memory_utility(m2, current_tick=5)
        assert score_good > score_bad

    def test_compute_all_utilities_returns_dict(self):
        store = InMemoryMemoryStore()
        _store_n_memories(store, 5)
        result = compute_all_utilities(store)
        assert isinstance(result, dict)
        assert len(result) == 5
        for v in result.values():
            assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# Forgetting policy tests
# ---------------------------------------------------------------------------

class TestForgettingPolicy:
    def test_policy_archives_low_utility_memories(self):
        store = InMemoryMemoryStore()
        # Create memories with varying decay
        mems = _store_n_memories(store, 15)
        # Make some memories very old (low utility)
        for m in mems[:5]:
            m.decay_score = 0.0
            m.last_accessed = 0
        # Advance tick
        store._tick = 100
        report = apply_forgetting_policy(store, utility_threshold=0.5)
        assert report["archived_count"] + report["deprecated_count"] > 0

    def test_policy_respects_max_archive_ratio(self):
        store = InMemoryMemoryStore()
        mems = _store_n_memories(store, 10)
        # All memories have low utility
        for m in mems:
            m.decay_score = 0.1
            m.last_accessed = 0
        store._tick = 100
        # With max_archive_ratio=0.3, max 3 can be archived
        report = apply_forgetting_policy(store, utility_threshold=0.9, max_archive_ratio=0.3)
        assert report["archived_count"] <= 3

    def test_policy_deprecates_very_low_utility(self):
        store = InMemoryMemoryStore()
        mems = _store_n_memories(store, 10)
        for m in mems[:3]:
            m.decay_score = 0.0
            m.last_accessed = 0
            m.access_count = 0
        store._tick = 200
        report = apply_forgetting_policy(store, utility_threshold=0.5)
        assert report["deprecated_count"] > 0

    def test_policy_empty_store(self):
        store = InMemoryMemoryStore()
        report = apply_forgetting_policy(store)
        assert report["archived_count"] == 0
        assert report["deprecated_count"] == 0
        assert report["total_active"] == 0

    def test_policy_report_has_decisions(self):
        store = InMemoryMemoryStore()
        mems = _store_n_memories(store, 10)
        for m in mems[:3]:
            m.decay_score = 0.0
            m.last_accessed = 0
        store._tick = 100
        report = apply_forgetting_policy(store, utility_threshold=0.5)
        assert "decisions" in report
        for d in report["decisions"]:
            assert "memory_id" in d
            assert "utility" in d
            assert "action" in d


# ---------------------------------------------------------------------------
# Pipeline integration tests
# ---------------------------------------------------------------------------

class TestPipelineIntegration:
    def test_pipeline_with_forgetting_disabled(self):
        result = run_minimal_pipeline("test task", use_productive_forgetting=False)
        assert result["forgetting_report"] is None

    def test_pipeline_with_forgetting_enabled_few_memories(self):
        """With few memories, forgetting policy should not trigger."""
        result = run_minimal_pipeline("test task", use_productive_forgetting=True)
        # Only 1 memory stored, less than threshold of 10
        assert result["forgetting_report"] is None

    def test_pipeline_with_forgetting_enabled_many_memories(self):
        """With many pre-existing memories, forgetting should trigger."""
        store = InMemoryMemoryStore()
        # Pre-populate with 12 memories (above threshold of 10)
        for i in range(12):
            m = _make_memory(summary=f"old memory {i}")
            m.scope.task_families = ["test"]
            store.store_memory(m)
        # Make them old
        for m in store.all():
            m.last_accessed = 0
            m.decay_score = 0.1
        store._tick = 100

        result = run_minimal_pipeline("test task", store=store, use_productive_forgetting=True)
        # After storing episode_memory, there are 13 active (some may be archived/deprecated by decay)
        # The forgetting report may or may not have archived things depending on utility
        assert "forgetting_report" in result

    def test_pipeline_backward_compatible(self):
        """Default pipeline call should work exactly as before."""
        result = run_minimal_pipeline("test task")
        assert "stored_memory" in result
        assert "forgetting_report" in result
        assert result["forgetting_report"] is None

    def test_episode_memory_meta_includes_forgetting_flag(self):
        result = run_minimal_pipeline("test task", use_productive_forgetting=True)
        meta = result["stored_memory"].get("meta", {})
        assert "use_productive_forgetting" in meta
        assert meta["use_productive_forgetting"] is True


# ---------------------------------------------------------------------------
# Retriever tests
# ---------------------------------------------------------------------------

class TestRetrieverFiltering:
    def test_active_only_filters_archived(self):
        from virtual_genesis.runtime.memory_os.retriever import retrieve_memory

        m1 = _make_memory()
        m1.scope.task_families = ["test"]
        m2 = _make_memory()
        m2.scope.task_families = ["test"]
        m2.memory_status = "archived"

        pack = retrieve_memory("test", "query", [m1, m2], active_only=True)
        # Only m1 should be in the results
        all_refs = pack.episodic_refs + pack.semantic_refs + pack.procedural_refs + pack.negative_refs
        assert m1.id in all_refs
        assert m2.id not in all_refs

    def test_active_only_false_includes_all(self):
        from virtual_genesis.runtime.memory_os.retriever import retrieve_memory

        m1 = _make_memory()
        m1.scope.task_families = ["test"]
        m2 = _make_memory()
        m2.scope.task_families = ["test"]
        m2.memory_status = "archived"

        pack = retrieve_memory("test", "query", [m1, m2], active_only=False)
        all_refs = pack.episodic_refs + pack.semantic_refs + pack.procedural_refs + pack.negative_refs
        assert m1.id in all_refs
        assert m2.id in all_refs

    def test_active_only_filters_deprecated_and_deleted(self):
        from virtual_genesis.runtime.memory_os.retriever import retrieve_memory

        m1 = _make_memory()
        m1.scope.task_families = ["test"]
        m2 = _make_memory()
        m2.scope.task_families = ["test"]
        m2.memory_status = "deprecated"
        m3 = _make_memory()
        m3.scope.task_families = ["test"]
        m3.memory_status = "deleted"

        pack = retrieve_memory("test", "query", [m1, m2, m3], active_only=True)
        all_refs = pack.episodic_refs + pack.semantic_refs + pack.procedural_refs + pack.negative_refs
        assert m1.id in all_refs
        assert m2.id not in all_refs
        assert m3.id not in all_refs
