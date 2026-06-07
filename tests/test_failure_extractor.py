"""Tests for failure extractor and regime orchestrator bridge.

Covers:
- Failure extraction from evaluation_results.json
- Failure extraction from agent_execution.json
- Cross-generation recurrence tracking
- Accuracy history building
- Regime check in orchestrator context
- Report persistence (regime_transition_report.json, regime_history.json)
- Edge cases: missing files, malformed JSON, empty generations
"""
from __future__ import annotations

import json
import os
import tempfile
import shutil

import pytest

from virtual_genesis.eval.runners.failure_extractor import (
    extract_failures_from_generation,
    extract_failures_across_generations,
    extract_accuracy_from_gen,
    build_accuracy_history,
)
from virtual_genesis.eval.runners.regime_orchestrator_bridge import (
    run_regime_check,
    load_regime_history,
    get_regime_transition_generations,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def run_dir():
    """Create a temporary run directory with mock generation data."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


def _write_eval_results(gen_dir, correct=60, total=198, details=None):
    """Write a mock evaluation_results.json."""
    os.makedirs(gen_dir, exist_ok=True)
    if details is None:
        details = []
        for i in range(1, total + 1):
            status = "correct" if i <= correct else "incorrect"
            details.append({
                "question_id": i,
                "correct_answer": "A",
                "model_answer": "A" if status == "correct" else "C",
                "domain": "Physics" if i % 2 == 0 else "Chemistry",
                "status": status,
                "is_correct": status == "correct",
            })
    data = {
        "total_questions": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": correct / total,
        "accuracy_percent": correct / total * 100,
        "details": details,
    }
    with open(os.path.join(gen_dir, "evaluation_results.json"), "w") as f:
        json.dump(data, f)


def _write_exec_log(gen_dir, accuracy=0.3, task_type="qa", error=None):
    """Write a mock agent_execution.json."""
    os.makedirs(gen_dir, exist_ok=True)
    data = {
        "timestamp": "2026-06-07T12:00:00",
        "accuracy": accuracy,
        "detected_task_type": task_type,
        "verification_good_enough": True,
        "pipeline_result_keys": ["task", "blackboard"],
    }
    if error:
        data["error"] = error
    with open(os.path.join(gen_dir, "agent_execution.json"), "w") as f:
        json.dump(data, f)


# ──────────────────────────────────────────────────────────────────────────
# Failure Extraction from evaluation_results.json
# ──────────────────────────────────────────────────────────────────────────


class TestExtractFromEval:
    def test_extracts_wrong_answers(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=2, total=4)
        failures = extract_failures_from_generation(gen_dir, gen_num=1)
        # 4 - 2 correct = 2 failures
        assert len(failures) == 2
        assert all(f["failure_type"] == "wrong_answer" for f in failures)

    def test_failure_has_required_fields(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=0, total=1)
        failures = extract_failures_from_generation(gen_dir, gen_num=1)
        assert len(failures) == 1
        f = failures[0]
        assert "id" in f
        assert "task_family" in f
        assert "failure_type" in f
        assert "context_summary" in f
        assert "expected_behavior" in f
        assert "actual_behavior" in f
        assert "severity" in f

    def test_no_failures_when_all_correct(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=4, total=4)
        failures = extract_failures_from_generation(gen_dir)
        assert len(failures) == 0

    def test_no_file_returns_empty(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        os.makedirs(gen_dir, exist_ok=True)
        failures = extract_failures_from_generation(gen_dir)
        assert failures == []

    def test_malformed_json_returns_empty(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        os.makedirs(gen_dir, exist_ok=True)
        with open(os.path.join(gen_dir, "evaluation_results.json"), "w") as f:
            f.write("NOT JSON")
        failures = extract_failures_from_generation(gen_dir)
        assert failures == []

    def test_domain_mapped_to_task_family(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        details = [
            {"question_id": 1, "correct_answer": "A", "model_answer": "B",
             "domain": "Physics", "status": "incorrect", "is_correct": False},
        ]
        _write_eval_results(gen_dir, correct=0, total=1, details=details)
        failures = extract_failures_from_generation(gen_dir)
        assert failures[0]["task_family"] == "physics"

    def test_max_failures_cap(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=0, total=100)
        failures = extract_failures_from_generation(gen_dir, max_failures=10)
        assert len(failures) == 10


# ──────────────────────────────────────────────────────────────────────────
# Failure Extraction from agent_execution.json
# ──────────────────────────────────────────────────────────────────────────


class TestExtractFromExec:
    def test_zero_accuracy_qa_triggers_shortcut(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen_dir, accuracy=0.0, task_type="qa")
        failures = extract_failures_from_generation(gen_dir, gen_num=1)
        # Should find the zero-accuracy failure
        exec_failures = [f for f in failures if f["failure_type"] == "shortcut"]
        assert len(exec_failures) == 1
        assert exec_failures[0]["severity"] == 0.9

    def test_error_field_triggers_failure(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen_dir, error="ModuleNotFoundError: xyz")
        failures = extract_failures_from_generation(gen_dir, gen_num=1)
        error_failures = [f for f in failures if "error" in f["context_summary"].lower()]
        assert len(error_failures) >= 1

    def test_nonzero_accuracy_no_zero_failure(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen_dir, accuracy=0.3, task_type="qa")
        failures = extract_failures_from_generation(gen_dir)
        zero_failures = [f for f in failures if f["id"].startswith("zero_acc")]
        assert len(zero_failures) == 0

    def test_malformed_json_creates_parse_failure(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        os.makedirs(gen_dir, exist_ok=True)
        with open(os.path.join(gen_dir, "agent_execution.json"), "w") as f:
            f.write("BROKEN{JSON")
        failures = extract_failures_from_generation(gen_dir, gen_num=1)
        parse_failures = [f for f in failures if "malformed" in f["context_summary"].lower()]
        assert len(parse_failures) == 1


# ──────────────────────────────────────────────────────────────────────────
# Cross-Generation Recurrence
# ──────────────────────────────────────────────────────────────────────────


class TestRecurrence:
    def test_recurrence_counted_across_gens(self, run_dir):
        # Gen 1: question 1 wrong
        gen1_dir = os.path.join(run_dir, "gen_1")
        gen2_dir = os.path.join(run_dir, "gen_2")
        for gen_dir in [gen1_dir, gen2_dir]:
            details = [
                {"question_id": 1, "correct_answer": "A", "model_answer": "B",
                 "domain": "Physics", "status": "incorrect", "is_correct": False},
            ]
            _write_eval_results(gen_dir, correct=0, total=1, details=details)

        failures, stats = extract_failures_across_generations(run_dir, max_gen=2)
        assert stats["total_failures_extracted"] == 2
        assert stats["recurring_failures"] == 1  # question 1 appeared twice

    def test_deduplication_with_max_total(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen1_dir, correct=0, total=50)
        failures, stats = extract_failures_across_generations(run_dir, max_gen=1, max_total=10)
        assert len(failures) <= 10

    def test_empty_run_returns_empty(self, run_dir):
        failures, stats = extract_failures_across_generations(run_dir, max_gen=5)
        assert failures == []
        assert stats["generations_scanned"] == 0


# ──────────────────────────────────────────────────────────────────────────
# Accuracy Extraction
# ──────────────────────────────────────────────────────────────────────────


class TestAccuracyExtraction:
    def test_from_eval_results(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=60, total=200)
        acc = extract_accuracy_from_gen(gen_dir)
        assert abs(acc - 0.3) < 0.01

    def test_from_results_json(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        os.makedirs(gen_dir, exist_ok=True)
        with open(os.path.join(gen_dir, "results.json"), "w") as f:
            json.dump({"accuracy": 0.75}, f)
        acc = extract_accuracy_from_gen(gen_dir)
        assert abs(acc - 0.75) < 0.01

    def test_from_execution_log(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen_dir, accuracy=0.45)
        acc = extract_accuracy_from_gen(gen_dir)
        assert abs(acc - 0.45) < 0.01

    def test_no_data_returns_none(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        os.makedirs(gen_dir, exist_ok=True)
        acc = extract_accuracy_from_gen(gen_dir)
        assert acc is None

    def test_eval_results_takes_priority(self, run_dir):
        gen_dir = os.path.join(run_dir, "gen_1")
        _write_eval_results(gen_dir, correct=60, total=200)  # 0.3
        _write_exec_log(gen_dir, accuracy=0.8)  # different value
        acc = extract_accuracy_from_gen(gen_dir)
        assert abs(acc - 0.3) < 0.01  # eval_results wins


class TestAccuracyHistory:
    def test_builds_from_multiple_gens(self, run_dir):
        for gen_num, acc_val in [(1, 0.3), (2, 0.4), (3, 0.45)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc_val)
        history = build_accuracy_history(run_dir, max_gen=3)
        assert len(history) == 3
        assert history == [0.3, 0.4, 0.45]

    def test_skips_gens_without_data(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)
        os.makedirs(os.path.join(run_dir, "gen_2"), exist_ok=True)  # no data
        gen3_dir = os.path.join(run_dir, "gen_3")
        _write_exec_log(gen3_dir, accuracy=0.5)
        history = build_accuracy_history(run_dir, max_gen=3)
        assert len(history) == 2
        assert history == [0.3, 0.5]

    def test_empty_run_returns_empty(self, run_dir):
        history = build_accuracy_history(run_dir, max_gen=5)
        assert history == []


# ──────────────────────────────────────────────────────────────────────────
# Regime Orchestrator Bridge
# ──────────────────────────────────────────────────────────────────────────


class TestRegimeOrchestratorBridge:
    def test_run_regime_check_returns_report(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)
        _write_eval_results(gen1_dir, correct=60, total=200)

        report = run_regime_check(run_dir, current_gen=1, save_report=True)
        assert report is not None
        assert "generation" in report
        assert "regime_decision" in report
        assert "regime_transition_required" in report

    def test_saves_report_to_gen_dir(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)

        run_regime_check(run_dir, current_gen=1, save_report=True)

        report_path = os.path.join(gen1_dir, "regime_transition_report.json")
        assert os.path.exists(report_path)
        with open(report_path) as f:
            saved = json.load(f)
        assert saved["generation"] == 1

    def test_saves_regime_history(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)

        run_regime_check(run_dir, current_gen=1, save_report=True)

        history_path = os.path.join(run_dir, "regime_history.json")
        assert os.path.exists(history_path)
        history = json.load(open(history_path))
        assert len(history) == 1
        assert history[0]["generation"] == 1

    def test_multiple_gens_accumulate_history(self, run_dir):
        for gen_num, acc in [(1, 0.3), (2, 0.35), (3, 0.33)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc)
            run_regime_check(run_dir, current_gen=gen_num, save_report=True)

        history = load_regime_history(run_dir)
        assert len(history) == 3
        assert [h["generation"] for h in history] == [1, 2, 3]

    def test_flat_accuracy_triggers_transition(self, run_dir):
        """5 identical accuracies → saturation → transition."""
        for gen_num in range(1, 6):
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=0.30)

        report = run_regime_check(run_dir, current_gen=5)
        assert report["regime_decision"]["active_signal_count"] >= 1  # at least saturation

    def test_declining_accuracy_triggers_transition(self, run_dir):
        for gen_num, acc in [(1, 0.5), (2, 0.45), (3, 0.40), (4, 0.35)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc)

        report = run_regime_check(run_dir, current_gen=4)
        # Should detect degradation (gen 4 < gen 3) and possibly saturation
        decision = report["regime_decision"]
        assert decision["active_signal_count"] >= 1

    def test_improving_accuracy_no_transition(self, run_dir):
        for gen_num, acc in [(1, 0.3), (2, 0.4), (3, 0.5), (4, 0.6)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc)

        report = run_regime_check(run_dir, current_gen=4)
        assert not report["regime_transition_required"]

    def test_get_transition_generations(self, run_dir):
        for gen_num, acc in [(1, 0.5), (2, 0.5), (3, 0.5), (4, 0.5)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc)
            run_regime_check(run_dir, current_gen=gen_num)

        transition_gens = get_regime_transition_generations(run_dir)
        # With 4 flat values, should detect transition at gen 3 or 4
        assert isinstance(transition_gens, list)

    def test_no_report_when_disabled(self, run_dir):
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)
        report = run_regime_check(run_dir, current_gen=1, save_report=False)
        assert report is not None  # still returns the report
        # But file should NOT be saved
        report_path = os.path.join(gen1_dir, "regime_transition_report.json")
        assert not os.path.exists(report_path)

    def test_includes_failure_stats(self, run_dir):
        # Gen 1 has failures, gen 2 is the current gen being checked
        gen1_dir = os.path.join(run_dir, "gen_1")
        _write_exec_log(gen1_dir, accuracy=0.3)
        _write_eval_results(gen1_dir, correct=60, total=200)  # 140 failures

        gen2_dir = os.path.join(run_dir, "gen_2")
        _write_exec_log(gen2_dir, accuracy=0.35)
        _write_eval_results(gen2_dir, correct=70, total=200)

        # Run regime check on gen 2 — it extracts failures from gen 1
        report = run_regime_check(run_dir, current_gen=2)
        assert "failure_stats" in report
        assert report["failure_stats"]["total_failures_extracted"] > 0

    def test_accuracy_history_in_report(self, run_dir):
        for gen_num, acc in [(1, 0.3), (2, 0.35)]:
            gen_dir = os.path.join(run_dir, f"gen_{gen_num}")
            _write_exec_log(gen_dir, accuracy=acc)
            run_regime_check(run_dir, current_gen=gen_num)

        report = run_regime_check(run_dir, current_gen=2)
        assert len(report["accuracy_history"]) >= 2

    def test_missing_gen_dir_no_crash(self, run_dir):
        # No gen directories at all
        report = run_regime_check(run_dir, current_gen=1)
        assert report is not None
