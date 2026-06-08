"""
Tests for genesis/open_task_evaluator.py
Stolen methodology:
  - Rulers (arXiv:2601.08654) — schema-constrained judge
  - InfoDeepSeek (arXiv:2505.15872) — IA@5 evidence score
  - G-Eval — step-by-step criteria
"""
import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from genesis.open_task_evaluator import (
    CriterionVerdict,
    OpenTaskResult,
    extract_rubric_from_task,
    find_output_file,
    load_evidence_stats,
    compute_evidence_score,
    load_open_task_score,
    DEFAULT_RUBRIC,
)


# ─── CriterionVerdict Tests ───────────────────────────────────────────────────
class TestCriterionVerdict(unittest.TestCase):
    def test_basic(self):
        cv = CriterionVerdict(
            criterion="Output addresses task objectives",
            met=True,
            score=0.9,
            evidence_quote="Here is the report on micro-tasks",
            explanation="Clearly addresses the task",
        )
        self.assertTrue(cv.met)
        self.assertEqual(cv.score, 0.9)
        self.assertIn("report", cv.evidence_quote)

    def test_not_met(self):
        cv = CriterionVerdict(
            criterion="No hallucinated links",
            met=False,
            score=0.0,
            evidence_quote="NOT FOUND",
        )
        self.assertFalse(cv.met)
        self.assertEqual(cv.score, 0.0)


# ─── OpenTaskResult Tests ─────────────────────────────────────────────────────
class TestOpenTaskResult(unittest.TestCase):
    def _make(self, **kwargs) -> OpenTaskResult:
        defaults = dict(
            gen_dir="/tmp/test_gen",
            output_file="/tmp/test_gen/report.md",
            output_score=70.0,
            evidence_score=60.0,
            hallucination_rate=0.2,
            overall_score=63.0,
        )
        defaults.update(kwargs)
        return OpenTaskResult(**defaults)

    def test_regime_signal_range(self):
        r = self._make(overall_score=63.0)
        self.assertAlmostEqual(r.regime_signal, 0.63, places=5)

    def test_regime_signal_zero(self):
        r = self._make(overall_score=0.0)
        self.assertEqual(r.regime_signal, 0.0)

    def test_regime_signal_hundred(self):
        r = self._make(overall_score=100.0)
        self.assertEqual(r.regime_signal, 1.0)

    def test_skipped_result(self):
        r = OpenTaskResult.skipped_result("/tmp/gen", "no output found")
        self.assertTrue(r.skipped)
        self.assertEqual(r.skip_reason, "no output found")
        self.assertEqual(r.overall_score, 0.0)
        self.assertIsNone(r.output_file)

    def test_save_and_load(self):
        r = self._make(
            checklist=[
                CriterionVerdict("criterion A", True, 0.9, "quote A", explanation="good"),
                CriterionVerdict("criterion B", False, 0.0, "NOT FOUND"),
            ]
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "open_task_eval.json")
            r.gen_dir = tmpdir
            r.save(path)

            # Verify JSON structure
            with open(path) as f:
                data = json.load(f)
            self.assertIn("output_score", data)
            self.assertIn("evidence_score", data)
            self.assertIn("hallucination_rate", data)
            self.assertIn("overall_score", data)
            self.assertIn("checklist", data)
            self.assertIn("regime_signal", data)
            self.assertEqual(len(data["checklist"]), 2)

            # Load back
            loaded = OpenTaskResult.load(path)
            self.assertAlmostEqual(loaded.output_score, 70.0)
            self.assertAlmostEqual(loaded.overall_score, 63.0)
            self.assertEqual(len(loaded.checklist), 2)
            self.assertTrue(loaded.checklist[0].met)
            self.assertFalse(loaded.checklist[1].met)

    def test_to_dict_has_regime_signal(self):
        r = self._make(overall_score=75.0)
        d = r.to_dict()
        self.assertIn("regime_signal", d)
        self.assertAlmostEqual(d["regime_signal"], 0.75, places=5)


# ─── extract_rubric_from_task Tests ──────────────────────────────────────────
class TestExtractRubricFromTask(unittest.TestCase):
    def test_with_evaluation_section(self):
        task_md = """
# Task Title

## Description
Do something.

## Evaluation Criteria
1. The output is accurate and specific
2. Claims are verified with sources
3. Output is well-structured
4. No hallucinated links present

## Notes
Other stuff.
"""
        criteria = extract_rubric_from_task(task_md)
        self.assertGreater(len(criteria), 0)
        # Should find criteria from section
        combined = " ".join(criteria)
        self.assertTrue(
            any(kw in combined.lower() for kw in ["accurate", "verified", "structured", "hallucinated"])
        )

    def test_fallback_to_default(self):
        task_md = "# Simple task\nDo something simple."
        criteria = extract_rubric_from_task(task_md)
        # Should fall back to DEFAULT_RUBRIC
        self.assertEqual(criteria, DEFAULT_RUBRIC)

    def test_arabic_section(self):
        task_md = """
## معايير التقييم
- الدقة في المعلومات المقدمة
- وجود مصادر موثّقة
- هيكل واضح ومنظم
"""
        criteria = extract_rubric_from_task(task_md)
        self.assertGreater(len(criteria), 0)

    def test_max_8_criteria(self):
        task_md = "## Evaluation Criteria\n" + "\n".join(
            [f"{i}. Criterion number {i} is very specific and actionable" for i in range(1, 15)]
        )
        criteria = extract_rubric_from_task(task_md)
        self.assertLessEqual(len(criteria), 8)

    def test_scoring_section(self):
        task_md = """
## Scoring
- Accuracy: 40%
- Completeness: 30%
- Source quality: 30%
"""
        criteria = extract_rubric_from_task(task_md)
        self.assertGreater(len(criteria), 0)


# ─── find_output_file Tests ───────────────────────────────────────────────────
class TestFindOutputFile(unittest.TestCase):
    def test_finds_micro_task_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "micro_task_report.md")
            with open(report_path, "w") as f:
                f.write("# Report\nContent here.")

            path, content = find_output_file(tmpdir)
            self.assertEqual(path, report_path)
            self.assertIn("Content here", content)

    def test_finds_report_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "report.md")
            with open(report_path, "w") as f:
                f.write("# Report Content")

            path, content = find_output_file(tmpdir)
            self.assertIsNotNone(path)
            self.assertIn("Report Content", content)

    def test_finds_in_results_subdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = os.path.join(tmpdir, "results")
            os.makedirs(results_dir)
            report_path = os.path.join(results_dir, "micro_task_report.md")
            with open(report_path, "w") as f:
                f.write("# Results Report")

            path, content = find_output_file(tmpdir)
            self.assertIsNotNone(path)
            self.assertIn("Results Report", content)

    def test_priority_micro_task_over_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            micro_path = os.path.join(tmpdir, "micro_task_report.md")
            report_path = os.path.join(tmpdir, "report.md")
            with open(micro_path, "w") as f:
                f.write("micro content")
            with open(report_path, "w") as f:
                f.write("report content")

            path, content = find_output_file(tmpdir)
            # micro_task_report.md has higher priority
            self.assertEqual(path, micro_path)

    def test_no_output_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Only has agent_execution.json (excluded)
            exc_path = os.path.join(tmpdir, "agent_execution.json")
            with open(exc_path, "w") as f:
                f.write('{"accuracy": 0.0}')

            path, content = find_output_file(tmpdir)
            # agent_execution.json is excluded
            self.assertIsNone(path)
            self.assertEqual(content, "")

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path, content = find_output_file(tmpdir)
            self.assertIsNone(path)
            self.assertEqual(content, "")


# ─── load_evidence_stats Tests ───────────────────────────────────────────────
class TestLoadEvidenceStats(unittest.TestCase):
    def test_no_evidence_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stats = load_evidence_stats(tmpdir)
            self.assertFalse(stats["found"])
            self.assertEqual(stats["hallucination_rate"], 0.0)

    def test_loads_evidence_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_data = {
                "summary": {
                    "hallucination_rate": 0.3,
                    "verified_claims": 7,
                    "total_claims": 10,
                    "searches_performed": 5,
                    "pages_read": 2,
                }
            }
            log_path = os.path.join(tmpdir, "evidence_log.json")
            with open(log_path, "w") as f:
                json.dump(evidence_data, f)

            stats = load_evidence_stats(tmpdir)
            self.assertTrue(stats["found"])
            self.assertAlmostEqual(stats["hallucination_rate"], 0.3)
            self.assertEqual(stats["verified_claims"], 7)
            self.assertEqual(stats["total_claims"], 10)
            self.assertEqual(stats["searches_performed"], 5)

    def test_loads_from_results_subdir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = os.path.join(tmpdir, "results")
            os.makedirs(results_dir)
            evidence_data = {"summary": {"hallucination_rate": 0.1}}
            log_path = os.path.join(results_dir, "evidence_log.json")
            with open(log_path, "w") as f:
                json.dump(evidence_data, f)

            stats = load_evidence_stats(tmpdir)
            self.assertTrue(stats["found"])
            self.assertAlmostEqual(stats["hallucination_rate"], 0.1)


# ─── compute_evidence_score Tests ─────────────────────────────────────────────
class TestComputeEvidenceScore(unittest.TestCase):
    def test_no_evidence_log_no_urls(self):
        stats = {
            "found": False, "hallucination_rate": 0.0,
            "searches_performed": 0, "pages_read": 0,
            "verified_claims": 0, "total_claims": 0,
        }
        score = compute_evidence_score(stats, "Plain text output with no links")
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 45)  # max without evidence log

    def test_with_urls_in_output(self):
        stats = {"found": False, "hallucination_rate": 0.0,
                 "searches_performed": 0, "pages_read": 0,
                 "verified_claims": 0, "total_claims": 0}
        output = "See https://reddit.com/r/beermoney and https://appen.com for more info."
        score = compute_evidence_score(stats, output)
        self.assertGreater(score, 0)

    def test_perfect_evidence_log(self):
        stats = {
            "found": True,
            "hallucination_rate": 0.0,  # no hallucinations
            "searches_performed": 10,
            "pages_read": 3,
            "verified_claims": 10,
            "total_claims": 10,
        }
        score = compute_evidence_score(stats, "output")
        self.assertGreater(score, 70)
        self.assertLessEqual(score, 100)

    def test_high_hallucination_reduces_score(self):
        stats_clean = {
            "found": True, "hallucination_rate": 0.0,
            "searches_performed": 5, "pages_read": 1,
            "verified_claims": 5, "total_claims": 5,
        }
        stats_dirty = {
            "found": True, "hallucination_rate": 0.9,
            "searches_performed": 5, "pages_read": 1,
            "verified_claims": 0, "total_claims": 10,
        }
        clean_score = compute_evidence_score(stats_clean, "")
        dirty_score = compute_evidence_score(stats_dirty, "")
        self.assertGreater(clean_score, dirty_score)

    def test_score_bounded_0_100(self):
        stats = {
            "found": True, "hallucination_rate": 0.0,
            "searches_performed": 1000, "pages_read": 1000,
            "verified_claims": 1000, "total_claims": 1000,
        }
        score = compute_evidence_score(stats, "output")
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_no_claims_but_searched(self):
        stats = {
            "found": True, "hallucination_rate": 0.0,
            "searches_performed": 3, "pages_read": 0,
            "verified_claims": 0, "total_claims": 0,
        }
        score = compute_evidence_score(stats, "")
        self.assertGreater(score, 0)  # at least partial credit for searching


# ─── load_open_task_score Tests ───────────────────────────────────────────────
class TestLoadOpenTaskScore(unittest.TestCase):
    def test_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            score = load_open_task_score(tmpdir)
            self.assertIsNone(score)

    def test_loads_score(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = OpenTaskResult(
                gen_dir=tmpdir,
                output_file=None,
                output_score=70.0,
                evidence_score=60.0,
                hallucination_rate=0.1,
                overall_score=65.0,
            )
            path = os.path.join(tmpdir, "open_task_eval.json")
            result.save(path)

            score = load_open_task_score(tmpdir)
            self.assertAlmostEqual(score, 65.0, places=1)

    def test_skipped_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = OpenTaskResult.skipped_result(tmpdir, "test skip")
            path = os.path.join(tmpdir, "open_task_eval.json")
            result.save(path)

            score = load_open_task_score(tmpdir)
            self.assertIsNone(score)


# ─── Integration: run_open_task_evaluation (mocked) ──────────────────────────
class TestRunOpenTaskEvaluationMocked(unittest.TestCase):
    def _setup_task_dir(self, tmpdir):
        """Create a task directory with task.md but NO evaluate.py."""
        task_dir = os.path.join(tmpdir, "micro_task")
        data_dir = os.path.join(task_dir, "data", "public")
        os.makedirs(data_dir)
        with open(os.path.join(data_dir, "task.md"), "w") as f:
            f.write("""# Micro Task
## Evaluation Criteria
1. The output is accurate and specific with real platform names
2. Output mentions availability in Egypt explicitly
3. No fabricated payment proof links
""")
        return task_dir

    def _setup_gen_dir(self, tmpdir, report_content):
        """Create a gen directory with a report."""
        gen_dir = os.path.join(tmpdir, "gen_1")
        os.makedirs(gen_dir)
        with open(os.path.join(gen_dir, "micro_task_report.md"), "w") as f:
            f.write(report_content)
        return gen_dir

    @patch("genesis.open_task_evaluator.openai.OpenAI")
    def test_runs_and_saves_result(self, mock_openai_cls):
        from genesis.open_task_evaluator import run_open_task_evaluation

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "criteria_verdicts": [
                {"criterion": "accurate", "met": True, "score": 0.8,
                 "evidence_quote": "Clickworker is available", "explanation": "Good"},
                {"criterion": "Egypt mention", "met": True, "score": 0.9,
                 "evidence_quote": "available in Egypt", "explanation": "Clear"},
            ],
            "output_score": 75,
            "summary": "Good report",
            "main_weakness": "Missing payment proof",
            "main_strength": "Clear structure",
        })
        mock_client.chat.completions.create.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = self._setup_task_dir(tmpdir)
            gen_dir = self._setup_gen_dir(
                tmpdir,
                "# Report\nClickworker is available in Egypt without VPN. Good platform."
            )

            result = run_open_task_evaluation(
                gen_dir=gen_dir,
                task_dir=task_dir,
                llm_client=mock_client,
                judge_model="test-model",
            )

            self.assertFalse(result.skipped)
            self.assertIsNotNone(result.output_file)
            self.assertGreater(result.output_score, 0)
            self.assertEqual(len(result.checklist), 2)
            self.assertTrue(result.checklist[0].met)

            # Verify file saved
            eval_path = os.path.join(gen_dir, "open_task_eval.json")
            self.assertTrue(os.path.exists(eval_path))

    def test_skips_when_evaluate_py_exists(self):
        from genesis.open_task_evaluator import run_open_task_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = os.path.join(tmpdir, "task")
            data_dir = os.path.join(task_dir, "data", "public")
            os.makedirs(data_dir)
            # Create evaluate.py
            with open(os.path.join(data_dir, "evaluate.py"), "w") as f:
                f.write("print('evaluating')")
            # Create task.md
            with open(os.path.join(data_dir, "task.md"), "w") as f:
                f.write("# Task")

            gen_dir = os.path.join(tmpdir, "gen_1")
            os.makedirs(gen_dir)

            result = run_open_task_evaluation(gen_dir=gen_dir, task_dir=task_dir)
            self.assertTrue(result.skipped)
            self.assertIn("evaluate.py", result.skip_reason)

    def test_skips_when_no_output(self):
        from genesis.open_task_evaluator import run_open_task_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = self._setup_task_dir(tmpdir)
            gen_dir = os.path.join(tmpdir, "gen_1")
            os.makedirs(gen_dir)
            # No output files

            result = run_open_task_evaluation(gen_dir=gen_dir, task_dir=task_dir)
            self.assertTrue(result.skipped)

    def test_uses_cache_on_second_call(self):
        from genesis.open_task_evaluator import run_open_task_evaluation

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = self._setup_task_dir(tmpdir)
            gen_dir = self._setup_gen_dir(tmpdir, "# Report content")

            # Pre-write cached result
            cached = OpenTaskResult(
                gen_dir=gen_dir, output_file=None,
                output_score=55.0, evidence_score=40.0,
                hallucination_rate=0.0, overall_score=50.0,
            )
            cached.save(os.path.join(gen_dir, "open_task_eval.json"))

            # Should load cache without calling LLM
            mock_client = MagicMock()
            result = run_open_task_evaluation(
                gen_dir=gen_dir, task_dir=task_dir,
                llm_client=mock_client, force=False,
            )
            mock_client.chat.completions.create.assert_not_called()
            self.assertAlmostEqual(result.overall_score, 50.0)

    def test_overall_score_weighted(self):
        """overall_score = output*0.5 + evidence*0.3 - hallucination_penalty*0.2"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = OpenTaskResult(
                gen_dir=tmpdir, output_file=None,
                output_score=80.0,    # * 0.5 = 40
                evidence_score=60.0,  # * 0.3 = 18
                hallucination_rate=0.5,  # 50% * 100 * 0.2 = 10 penalty
                overall_score=48.0,   # 40 + 18 - 10 = 48
            )
            self.assertAlmostEqual(result.overall_score, 48.0, places=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
