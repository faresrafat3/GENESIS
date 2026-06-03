"""Tests for anomaly leverage (Cycle 2): severity scoring, anomaly-aware verification,
anomaly-aware tier routing, anomaly-aware escalation, and pipeline integration."""
from __future__ import annotations

from virtual_genesis.core.objects.anomaly import AnomalyCandidate
from virtual_genesis.core.objects.task import TaskObject
from virtual_genesis.core.objects.blackboard import BlackboardObject, BlackboardMemoryPack
from virtual_genesis.runtime.anomaly_runtime.service import (
    compute_anomaly_severity_score,
    matches_known_anomaly_pattern,
)
from virtual_genesis.runtime.verification_runtime.service import verify_output_anomaly_aware
from virtual_genesis.runtime.economy_control.router import choose_tier_anomaly_aware
from virtual_genesis.runtime.economy_control.escalation import should_escalate_anomaly_aware
from virtual_genesis.runtime.pipeline.minimal_run import run_minimal_pipeline


# --- Helpers ---

def _make_candidate(source_type: str = "property_gap", severity: float = 0.6, family: str = "comparison") -> AnomalyCandidate:
    return AnomalyCandidate.create(
        task_family=family,
        source_type=source_type,
        summary=f"test anomaly ({source_type})",
        severity=severity,
    )


def _make_task(family: str = "comparison", difficulty: str = "medium", criticality: str = "medium") -> TaskObject:
    t = TaskObject.create(raw_text="test task")
    t.task_family = family
    t.difficulty_estimate = difficulty
    t.criticality_level = criticality
    return t


def _make_blackboard(task: TaskObject | None = None) -> BlackboardObject:
    task = task or _make_task()
    from virtual_genesis.core.objects.blackboard import BlackboardTaskCore
    task_core = BlackboardTaskCore(
        task_id=task.id,
        task_family=task.task_family,
        criticality_level=task.criticality_level,
        difficulty_estimate=task.difficulty_estimate,
    )
    return BlackboardObject.create(task_ref=task.id, task_core=task_core)


def _make_memory_pack() -> BlackboardMemoryPack:
    return BlackboardMemoryPack()


# --- Tests for compute_anomaly_severity_score ---

class TestComputeAnomalySeverityScore:
    def test_empty_candidates_returns_zero(self):
        assert compute_anomaly_severity_score([]) == 0.0

    def test_single_candidate_returns_positive(self):
        candidates = [_make_candidate(severity=0.5)]
        score = compute_anomaly_severity_score(candidates)
        assert 0.0 < score <= 1.0

    def test_more_candidates_higher_score(self):
        few = [_make_candidate(severity=0.5)]
        many = [_make_candidate(severity=0.5) for _ in range(4)]
        assert compute_anomaly_severity_score(many) > compute_anomaly_severity_score(few)

    def test_higher_severity_higher_score(self):
        low = [_make_candidate(severity=0.3)]
        high = [_make_candidate(severity=0.9)]
        assert compute_anomaly_severity_score(high) > compute_anomaly_severity_score(low)

    def test_diverse_source_types_higher_score(self):
        same = [_make_candidate(source_type="property_gap", severity=0.5) for _ in range(3)]
        diverse = [
            _make_candidate(source_type="property_gap", severity=0.5),
            _make_candidate(source_type="shortcut_pattern", severity=0.5),
            _make_candidate(source_type="contradiction_pattern", severity=0.5),
        ]
        assert compute_anomaly_severity_score(diverse) > compute_anomaly_severity_score(same)

    def test_score_capped_at_one(self):
        extreme = [_make_candidate(source_type=f"type_{i}", severity=1.0) for i in range(10)]
        score = compute_anomaly_severity_score(extreme)
        assert score <= 1.0

    def test_score_never_negative(self):
        candidates = [_make_candidate(severity=0.0)]
        score = compute_anomaly_severity_score(candidates)
        assert score >= 0.0


# --- Tests for matches_known_anomaly_pattern ---

class TestMatchesKnownAnomalyPattern:
    def test_property_gap_and_shortcut_cooccurrence(self):
        task_result = {
            "task": {"task_family": "comparison"},
            "blackboard": {
                "verification_state": {
                    "property_checks": {"explicit comparison": False},
                    "shortcut_checks": {"generic preference without evidence": True},
                    "verification_summary": {"good_enough": False},
                },
                "contradictions": [],
            },
        }
        assert matches_known_anomaly_pattern(task_result) is True

    def test_repeated_family_failures(self):
        task_result = {
            "task": {"task_family": "comparison"},
            "blackboard": {
                "verification_state": {
                    "property_checks": {},
                    "shortcut_checks": {},
                    "verification_summary": {"good_enough": True},
                },
                "contradictions": [],
            },
        }
        previous = [
            _make_candidate(family="comparison"),
            _make_candidate(family="comparison"),
        ]
        assert matches_known_anomaly_pattern(task_result, previous_candidates=previous) is True

    def test_contradiction_clustering(self):
        task_result = {
            "task": {"task_family": "synthesis"},
            "blackboard": {
                "verification_state": {
                    "property_checks": {},
                    "shortcut_checks": {},
                    "verification_summary": {"good_enough": True},
                },
                "contradictions": [
                    {"contradiction_type": "a", "id": "1"},
                    {"contradiction_type": "b", "id": "2"},
                    {"contradiction_type": "c", "id": "3"},
                ],
            },
        }
        assert matches_known_anomaly_pattern(task_result) is True

    def test_no_pattern_match(self):
        task_result = {
            "task": {"task_family": "comparison"},
            "blackboard": {
                "verification_state": {
                    "property_checks": {"explicit comparison": True},
                    "shortcut_checks": {"generic preference without evidence": False},
                    "verification_summary": {"good_enough": True},
                },
                "contradictions": [],
            },
        }
        assert matches_known_anomaly_pattern(task_result) is False


# --- Tests for verify_output_anomaly_aware ---

class TestVerifyOutputAnomalyAware:
    def test_low_severity_returns_normal_result(self):
        result = verify_output_anomaly_aware(
            "comparison",
            "This option is better supported by evidence and contrast with the alternative",
            anomaly_severity=0.2,
        )
        assert result["anomaly_severity_applied"] == 0.2
        # Should behave like normal verify_output
        assert "verification_summary" in result

    def test_high_severity_enables_strict_mode(self):
        result = verify_output_anomaly_aware(
            "comparison",
            "This option is better supported by evidence and contrast with the alternative",
            anomaly_severity=0.8,
        )
        assert result["anomaly_severity_applied"] == 0.8
        assert result["evidence_checks"].get("strict_mode") is True
        assert result["verification_summary"].get("anomaly_strict_mode") is True

    def test_high_severity_stricter_pass_threshold(self):
        # Text with only 1 primary marker should fail in strict mode
        # "supported by" is 1 marker for comparison family
        text_one_marker = "This is supported by the data"
        normal = verify_output_anomaly_aware("comparison", text_one_marker, anomaly_severity=0.3)
        strict = verify_output_anomaly_aware("comparison", text_one_marker, anomaly_severity=0.8)
        # Normal should pass (1 marker is enough), strict should fail (needs 2)
        assert normal["verification_summary"]["good_enough"] is True
        assert strict["verification_summary"]["good_enough"] is False

    def test_high_severity_passes_with_multiple_markers(self):
        # Text with 2+ primary markers should pass even in strict mode
        text_multi = "This is supported by contrast and the difference is grounded by evidence"
        result = verify_output_anomaly_aware("comparison", text_multi, anomaly_severity=0.8)
        assert result["verification_summary"]["good_enough"] is True


# --- Tests for choose_tier_anomaly_aware ---

class TestChooseTierAnomalyAware:
    def test_zero_severity_no_change(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        decision = choose_tier_anomaly_aware(task, bb, mp, anomaly_severity=0.0)
        # With low difficulty procedure and no ambiguity, original would pick tier_0
        assert decision.chosen_tier == "tier_0"

    def test_medium_severity_prevents_tier_0(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        decision = choose_tier_anomaly_aware(task, bb, mp, anomaly_severity=0.5)
        assert decision.chosen_tier != "tier_0"
        assert decision.chosen_tier in ("tier_1", "tier_2")

    def test_high_severity_forces_tier_2(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        decision = choose_tier_anomaly_aware(task, bb, mp, anomaly_severity=0.8)
        assert decision.chosen_tier == "tier_2"

    def test_severity_noted_in_reason(self):
        task = _make_task(family="procedure", difficulty="low")
        bb = _make_blackboard(task)
        mp = _make_memory_pack()
        decision = choose_tier_anomaly_aware(task, bb, mp, anomaly_severity=0.6)
        assert "anomaly_severity" in decision.decision_reason


# --- Tests for should_escalate_anomaly_aware ---

class TestShouldEscalateAnomalyAware:
    def test_high_severity_forces_escalation(self):
        task = _make_task()
        verification = {"verification_summary": {"good_enough": True}}
        result = should_escalate_anomaly_aware(task, verification, current_tier="tier_1", anomaly_severity=0.7)
        assert result["escalate"] is True
        assert result["target_tier"] == "tier_2"

    def test_high_severity_at_tier_2_no_escalation(self):
        task = _make_task()
        verification = {"verification_summary": {"good_enough": True}}
        result = should_escalate_anomaly_aware(task, verification, current_tier="tier_2", anomaly_severity=0.9)
        assert result["escalate"] is False

    def test_low_severity_uses_normal_logic(self):
        task = _make_task()
        verification = {"verification_summary": {"good_enough": True}}
        result = should_escalate_anomaly_aware(task, verification, current_tier="tier_1", anomaly_severity=0.2)
        # Normal logic: good_enough=True means no escalation
        assert result["escalate"] is False

    def test_low_severity_failed_verification_still_escalates(self):
        task = _make_task()
        verification = {"verification_summary": {"good_enough": False}}
        result = should_escalate_anomaly_aware(task, verification, current_tier="tier_0", anomaly_severity=0.2)
        # Normal logic kicks in: failed verification escalates
        assert result["escalate"] is True

    def test_anomaly_severity_in_result(self):
        task = _make_task()
        verification = {"verification_summary": {"good_enough": True}}
        result = should_escalate_anomaly_aware(task, verification, current_tier="tier_1", anomaly_severity=0.3)
        assert "anomaly_severity" in result


# --- Tests for pipeline integration ---

class TestPipelineAnomalyLeverage:
    def test_pipeline_runs_with_anomaly_leverage_disabled(self):
        result = run_minimal_pipeline("Compare these two options and justify your choice")
        assert "anomaly_candidates" in result
        assert result["use_anomaly_leverage"] is False
        assert result["anomaly_severity"] == 0.0

    def test_pipeline_runs_with_anomaly_leverage_enabled(self):
        result = run_minimal_pipeline(
            "Compare these two options and justify your choice",
            use_anomaly_leverage=True,
        )
        assert "anomaly_candidates" in result
        assert result["use_anomaly_leverage"] is True
        # With empty store, anomaly_severity should be 0
        assert result["anomaly_severity"] == 0.0

    def test_pipeline_anomaly_leverage_with_history(self):
        from virtual_genesis.runtime.memory_os.store import InMemoryMemoryStore
        from virtual_genesis.core.objects.memory import MemoryUnit

        store = InMemoryMemoryStore()
        # Seed store with failed memory entries to trigger anomaly severity
        for i in range(3):
            mem = MemoryUnit.create(summary=f"failed task {i}", memory_type="episodic")
            mem.scope.task_families = ["comparison"]
            mem.meta = {
                "task_family": "comparison",
                "good_enough": False,
                "property_checks": {"explicit comparison": False},
                "shortcut_checks": {"generic preference without evidence": True},
            }
            store.store_memory(mem)

        result = run_minimal_pipeline(
            "Compare these two options and justify your choice",
            store=store,
            use_anomaly_leverage=True,
        )
        assert result["anomaly_severity"] > 0.0
        assert result["use_anomaly_leverage"] is True
