"""Tests for agent identity governance: identity object, drift detection, commitment ledger, governance, pipeline."""
from __future__ import annotations

from virtual_genesis.core.objects.identity import AgentIdentityObject
from virtual_genesis.runtime.identity_runtime.drift_detector import measure_drift
from virtual_genesis.runtime.identity_runtime.commitment_ledger import CommitmentLedger
from virtual_genesis.runtime.identity_runtime.governance import check_identity_alignment
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_identity(
    commitments: list[str] | None = None,
    self_model: dict | None = None,
) -> AgentIdentityObject:
    return AgentIdentityObject.create(
        commitments=commitments or ["transparency in reasoning", "avoid harmful outputs"],
        self_model=self_model or {"capability": "text generation", "limitation": "no real-time data"},
    )


# ---------------------------------------------------------------------------
# TestAgentIdentityObject
# ---------------------------------------------------------------------------

class TestAgentIdentityObject:
    def test_creation(self):
        identity = _make_identity()
        assert identity.id.startswith("identity_")
        assert identity.object_type == "agent_identity"
        assert identity.commitments == ["transparency in reasoning", "avoid harmful outputs"]
        assert identity.self_model == {"capability": "text generation", "limitation": "no real-time data"}

    def test_fields_default(self):
        identity = _make_identity()
        assert identity.drift_score == 0.0
        assert identity.lineage == []
        assert identity.accountability_log == []
        assert identity.policy_signature == []

    def test_lineage_append(self):
        identity = _make_identity()
        identity.lineage.append("v0.1 initial creation")
        identity.lineage.append("v0.2 added safety commitment")
        assert len(identity.lineage) == 2
        assert "v0.2 added safety commitment" in identity.lineage

    def test_to_dict(self):
        identity = _make_identity()
        d = identity.to_dict()
        assert d["object_type"] == "agent_identity"
        assert d["commitments"] == ["transparency in reasoning", "avoid harmful outputs"]
        assert d["self_model"] == {"capability": "text generation", "limitation": "no real-time data"}
        assert d["drift_score"] == 0.0
        assert "id" in d
        assert "created_at" in d

    def test_status_active_by_default(self):
        identity = _make_identity()
        assert identity.status == "active"


# ---------------------------------------------------------------------------
# TestDriftDetector
# ---------------------------------------------------------------------------

class TestDriftDetector:
    def test_zero_drift_same_text(self):
        commitments = ["always be transparent"]
        behavior = ["always be transparent"]
        score = measure_drift(behavior, commitments)
        assert score == 0.0

    def test_full_drift_completely_different(self):
        commitments = ["alpha beta gamma"]
        behavior = ["delta epsilon zeta"]
        score = measure_drift(behavior, commitments)
        assert score == 1.0

    def test_partial_drift(self):
        commitments = ["transparency in reasoning", "safety first"]
        behavior = ["transparency is important for trust"]
        score = measure_drift(behavior, commitments)
        assert 0.0 < score < 1.0

    def test_empty_commitments_returns_zero(self):
        score = measure_drift(["some behavior"], [])
        assert score == 0.0

    def test_empty_behavior_returns_one(self):
        score = measure_drift([], ["some commitment"])
        assert score == 1.0

    def test_overlapping_tokens(self):
        commitments = ["ensure safety and fairness"]
        behavior = ["safety is our priority"]
        score = measure_drift(behavior, commitments)
        # "safety" overlaps, so drift < 1.0
        assert score < 1.0

    def test_case_insensitive(self):
        commitments = ["ALWAYS BE TRANSPARENT"]
        behavior = ["always be transparent"]
        score = measure_drift(behavior, commitments)
        assert score == 0.0


# ---------------------------------------------------------------------------
# TestCommitmentLedger
# ---------------------------------------------------------------------------

class TestCommitmentLedger:
    def test_add_commitment(self):
        ledger = CommitmentLedger()
        ledger.add_commitment("be transparent")
        assert "be transparent" in ledger.get_active()

    def test_record_violation(self):
        ledger = CommitmentLedger()
        ledger.record_violation("be transparent", "withheld information", "performance pressure")
        violations = ledger.get_violations()
        assert len(violations) == 1
        assert violations[0]["commitment"] == "be transparent"
        assert violations[0]["decision"] == "withheld information"
        assert violations[0]["reason"] == "performance pressure"

    def test_evolve_commitment_removes_old_adds_new(self):
        ledger = CommitmentLedger()
        ledger.add_commitment("be fast")
        ledger.evolve_commitment("be fast", "be accurate", "accuracy matters more")
        active = ledger.get_active()
        assert "be fast" not in active
        assert "be accurate" in active

    def test_get_active(self):
        ledger = CommitmentLedger()
        ledger.add_commitment("c1")
        ledger.add_commitment("c2")
        assert ledger.get_active() == ["c1", "c2"]

    def test_get_violations(self):
        ledger = CommitmentLedger()
        ledger.record_violation("c1", "d1", "r1")
        ledger.record_violation("c2", "d2", "r2")
        assert len(ledger.get_violations()) == 2

    def test_get_violation_count(self):
        ledger = CommitmentLedger()
        assert ledger.get_violation_count() == 0
        ledger.record_violation("c1", "d1", "r1")
        assert ledger.get_violation_count() == 1
        ledger.record_violation("c2", "d2", "r2")
        assert ledger.get_violation_count() == 2

    def test_evolve_records_in_evolutions_list(self):
        ledger = CommitmentLedger()
        ledger.add_commitment("old rule")
        ledger.evolve_commitment("old rule", "new rule", "updated policy")
        assert len(ledger.evolutions) == 1
        assert ledger.evolutions[0]["old_commitment"] == "old rule"
        assert ledger.evolutions[0]["new_commitment"] == "new rule"
        assert ledger.evolutions[0]["reason"] == "updated policy"


# ---------------------------------------------------------------------------
# TestGovernance
# ---------------------------------------------------------------------------

class TestGovernance:
    def test_aligned_decision(self):
        identity = AgentIdentityObject.create(
            commitments=["transparency in reasoning", "safety first"],
            self_model={},
        )
        result = check_identity_alignment("transparency in reasoning is key", identity)
        assert result["aligned"] is True
        assert result["recommendation"] == "continue"
        assert result["drift_score"] < 0.5

    def test_drifted_decision(self):
        identity = AgentIdentityObject.create(
            commitments=["alpha beta gamma"],
            self_model={},
        )
        result = check_identity_alignment("delta epsilon zeta", identity)
        assert result["aligned"] is False
        assert result["drift_score"] >= 0.5

    def test_recommendation_continue(self):
        identity = AgentIdentityObject.create(
            commitments=["safety and fairness"],
            self_model={},
        )
        result = check_identity_alignment("safety and fairness matter", identity)
        assert result["recommendation"] == "continue"

    def test_recommendation_review_decision(self):
        identity = AgentIdentityObject.create(
            commitments=["alpha beta gamma delta epsilon"],
            self_model={},
        )
        # Partially overlapping - should result in moderate drift
        result = check_identity_alignment("alpha zeta theta kappa lambda", identity)
        # drift_score = 1 - (1 overlap / 5 commitment tokens) = 0.8
        assert result["recommendation"] in ("review_decision", "halt_and_review")

    def test_recommendation_halt_and_review(self):
        identity = AgentIdentityObject.create(
            commitments=["alpha beta gamma"],
            self_model={},
        )
        result = check_identity_alignment("delta epsilon zeta", identity)
        assert result["recommendation"] == "halt_and_review"
        assert result["drift_score"] > 0.7

    def test_violated_commitments_detection(self):
        identity = AgentIdentityObject.create(
            commitments=["transparency in reasoning", "safety first", "honesty always"],
            self_model={},
        )
        result = check_identity_alignment("transparency in reasoning is good", identity)
        # "safety first" and "honesty always" have no token overlap with the decision
        assert "safety first" in result["violated_commitments"]
        assert "honesty always" in result["violated_commitments"]
        assert "transparency in reasoning" not in result["violated_commitments"]


# ---------------------------------------------------------------------------
# TestPipelineIntegration
# ---------------------------------------------------------------------------

class TestPipelineIntegration:
    def test_pipeline_governance_false_returns_none(self):
        result = run_minimal_pipeline("test task for identity", use_identity_governance=False)
        assert result["alignment_report"] is None
        assert result["use_identity_governance"] is False

    def test_pipeline_governance_true_with_identity(self):
        identity = AgentIdentityObject.create(
            commitments=["test task reasoning"],
            self_model={"cap": "general"},
        )
        result = run_minimal_pipeline(
            "test task for identity",
            use_identity_governance=True,
            identity=identity,
        )
        assert result["alignment_report"] is not None
        assert "aligned" in result["alignment_report"]
        assert "drift_score" in result["alignment_report"]
        assert "violated_commitments" in result["alignment_report"]
        assert "recommendation" in result["alignment_report"]
        assert result["use_identity_governance"] is True

    def test_pipeline_governance_true_identity_none_returns_none(self):
        result = run_minimal_pipeline(
            "test task for identity",
            use_identity_governance=True,
            identity=None,
        )
        assert result["alignment_report"] is None

    def test_pipeline_default_unchanged(self):
        result = run_minimal_pipeline("simple task")
        # Default behavior: governance off
        assert result["alignment_report"] is None
        assert result["use_identity_governance"] is False
        # Existing fields still present
        assert "task" in result
        assert "blackboard" in result
        assert "tier_decision" in result

    def test_pipeline_accountability_log_on_drift(self):
        identity = AgentIdentityObject.create(
            commitments=["alpha beta gamma"],
            self_model={},
        )
        result = run_minimal_pipeline(
            "delta epsilon zeta different words entirely",
            use_identity_governance=True,
            identity=identity,
        )
        report = result["alignment_report"]
        if not report["aligned"]:
            assert len(identity.accountability_log) > 0
            assert "decision" in identity.accountability_log[0]
            assert "drift_score" in identity.accountability_log[0]
            assert "recommendation" in identity.accountability_log[0]
