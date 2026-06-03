"""Tests for paradigm forking / self-redesign: crisis detection, fork protocol, safety, pipeline."""
from __future__ import annotations

from virtual_genesis.core.objects.identity import AgentIdentityObject
from virtual_genesis.core.objects.theory import LocalTheoryObject
from virtual_genesis.runtime.identity_runtime.crisis_detector import detect_crisis
from virtual_genesis.runtime.identity_runtime.paradigm_fork import (
    MINIMUM_CYCLES_BETWEEN_FORKS,
    execute_fork,
    propose_fork,
)
from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
from virtual_genesis.runtime.theory_runtime.registry import InMemoryTheoryRegistry
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_identity(
    commitments: list[str] | None = None,
    self_model: dict | None = None,
    lineage: list[str] | None = None,
    drift_score: float = 0.0,
    meta: dict | None = None,
) -> AgentIdentityObject:
    identity = AgentIdentityObject.create(
        commitments=commitments or ["transparency", "avoid harm", "be accurate", "respect privacy"],
        self_model=self_model or {"capability": "reasoning"},
    )
    if lineage:
        identity.lineage = lineage
    identity.drift_score = drift_score
    if meta is not None:
        identity.meta = meta
    return identity


def _make_crisis_report(level: str = "crisis", reasons: list[str] | None = None) -> dict:
    return {
        "level": level,
        "anomaly_count": 6,
        "theory_failure_count": 3,
        "drift_score": 0.75,
        "reasons": reasons or ["anomaly_count=6 >= 5", "theory_failures=3 >= 2", "drift_score=0.75 > 0.6"],
    }


def _make_anomaly_history(count: int) -> list[dict]:
    return [{"task_family": f"family_{i}", "good_enough": False} for i in range(count)]


# ---------------------------------------------------------------------------
# TestCrisisDetection
# ---------------------------------------------------------------------------

class TestCrisisDetection:
    def test_normal_level(self):
        report = detect_crisis([], 0, 0.1)
        assert report["level"] == "normal"
        assert report["anomaly_count"] == 0
        assert report["theory_failure_count"] == 0
        assert report["drift_score"] == 0.1
        assert len(report["reasons"]) > 0

    def test_warning_on_high_anomaly_count(self):
        report = detect_crisis(_make_anomaly_history(3), 0, 0.2)
        assert report["level"] == "warning"
        assert report["anomaly_count"] == 3

    def test_warning_on_high_drift(self):
        report = detect_crisis([], 0, 0.55)
        assert report["level"] == "warning"
        assert report["drift_score"] == 0.55

    def test_crisis_level_all_conditions(self):
        report = detect_crisis(_make_anomaly_history(5), 2, 0.7)
        assert report["level"] == "crisis"
        assert report["anomaly_count"] == 5
        assert report["theory_failure_count"] == 2
        assert report["drift_score"] == 0.7
        assert len(report["reasons"]) == 3

    def test_crisis_requires_all_three_conditions(self):
        # High anomaly + high failures but low drift -> warning (not crisis)
        report = detect_crisis(_make_anomaly_history(5), 2, 0.4)
        assert report["level"] == "warning"

        # High anomaly + high drift but low failures -> warning
        report2 = detect_crisis(_make_anomaly_history(5), 1, 0.7)
        assert report2["level"] == "warning"

        # High failures + high drift but low anomalies -> warning (drift > 0.5)
        report3 = detect_crisis(_make_anomaly_history(2), 3, 0.7)
        assert report3["level"] == "warning"

    def test_empty_anomaly_history(self):
        report = detect_crisis([], 0, 0.0)
        assert report["level"] == "normal"
        assert report["anomaly_count"] == 0


# ---------------------------------------------------------------------------
# TestProposeFork
# ---------------------------------------------------------------------------

class TestProposeFork:
    def test_returns_valid_proposal(self):
        identity = _make_identity()
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        assert "proposed_changes" in proposal
        assert "preserved" in proposal
        assert "discarded" in proposal
        assert "justification" in proposal
        assert "fork_id" in proposal

    def test_preserves_lineage(self):
        identity = _make_identity(lineage=["v0.1", "v0.2"])
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        # All lineage items must be in preserved
        for item in identity.lineage:
            assert item in proposal["preserved"]

    def test_fork_id_generated(self):
        identity = _make_identity()
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        assert proposal["fork_id"].startswith("fork_")

    def test_justification_from_reasons(self):
        reasons = ["anomaly_count=6 >= 5", "drift_score=0.75 > 0.6"]
        identity = _make_identity()
        crisis = _make_crisis_report(reasons=reasons)
        proposal = propose_fork(crisis, identity)
        for reason in reasons:
            assert reason in proposal["justification"]


# ---------------------------------------------------------------------------
# TestExecuteFork
# ---------------------------------------------------------------------------

class TestExecuteFork:
    def test_success_creates_new_identity(self):
        identity = _make_identity(meta={"last_fork_cycle": 0})
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is True
        assert result["new_identity"] is not None
        assert result["new_identity"].id != identity.id
        assert result["reset_drift_score"] == 0.0

    def test_refuses_without_justification(self):
        identity = _make_identity()
        proposal = {
            "proposed_changes": ["new commitment"],
            "preserved": [],
            "discarded": [],
            "justification": "",
            "fork_id": "fork_test123",
        }
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is False
        assert result["reason"] == "no justification"

    def test_refuses_minimum_cycle_gap(self):
        identity = _make_identity(meta={"last_fork_cycle": 15})
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        # current_cycle=20, last_fork_cycle=15, gap=5 < 10
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is False
        assert result["reason"] == "minimum cycle gap not met"

    def test_refuses_preserved_discarded_overlap(self):
        identity = _make_identity()
        proposal = {
            "proposed_changes": ["new commitment"],
            "preserved": ["item_a", "item_b"],
            "discarded": ["item_b", "item_c"],
            "justification": "valid reason",
            "fork_id": "fork_test123",
        }
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is False
        assert result["reason"] == "preserved/discarded overlap"

    def test_resets_drift_score(self):
        identity = _make_identity(drift_score=0.8, meta={"last_fork_cycle": 0})
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is True
        assert result["new_identity"].drift_score == 0.0

    def test_appends_to_lineage(self):
        identity = _make_identity(lineage=["v0.1", "v0.2"], meta={"last_fork_cycle": 0})
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is True
        new_lineage = result["new_identity"].lineage
        assert "v0.1" in new_lineage
        assert "v0.2" in new_lineage
        assert proposal["fork_id"] in new_lineage
        assert len(new_lineage) == 3

    def test_meta_none_treated_as_no_previous_fork(self):
        """When identity.meta is None, treat as no previous fork (allow fork)."""
        identity = _make_identity()
        assert identity.meta is None
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is True

    def test_archived_policies_from_discarded(self):
        identity = _make_identity(meta={"last_fork_cycle": 0})
        crisis = _make_crisis_report()
        proposal = propose_fork(crisis, identity)
        result = execute_fork(proposal, identity, current_cycle=20)
        assert result["success"] is True
        assert result["archived_policies"] == proposal["discarded"]


# ---------------------------------------------------------------------------
# TestPipelineParadigmFork
# ---------------------------------------------------------------------------

class TestPipelineParadigmFork:
    def test_disabled_by_default_returns_none(self):
        result = run_minimal_pipeline("What is 2+2?")
        assert result["crisis_report"] is None
        assert result["fork_result"] is None
        assert result["use_paradigm_fork"] is False

    def test_enabled_no_crisis_returns_normal_report(self):
        identity = _make_identity(drift_score=0.1)
        result = run_minimal_pipeline(
            "What is 2+2?",
            use_paradigm_fork=True,
            identity=identity,
        )
        assert result["crisis_report"] is not None
        assert result["crisis_report"]["level"] == "normal"
        assert result["fork_result"] is None

    def test_enabled_with_crisis_executes_fork(self):
        store = InMemoryMemoryStore()
        theory_registry = InMemoryTheoryRegistry()

        # Create failing theories
        for i in range(3):
            theory = LocalTheoryObject.create(name=f"bad_theory_{i}", core_question="why fail?")
            theory.prediction_count = 10
            theory.predictive_value = 0.2
            theory_registry.add_theory(theory)

        # Pre-populate store with failing memories to create anomaly history
        from virtual_genesis.core.objects.memory import MemoryUnit
        for i in range(6):
            mem = MemoryUnit.create(summary=f"failed task {i}", memory_type="episodic")
            mem.meta = {"good_enough": False, "task_family": "test"}
            store.store_memory(mem)

        identity = _make_identity(drift_score=0.75)

        result = run_minimal_pipeline(
            "What is 2+2?",
            store=store,
            theory_registry=theory_registry,
            use_paradigm_fork=True,
            identity=identity,
        )
        assert result["crisis_report"] is not None
        assert result["crisis_report"]["level"] == "crisis"
        assert result["fork_result"] is not None
        assert result["fork_result"]["success"] is True
        assert result["fork_result"]["new_identity"] is not None
