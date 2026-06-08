"""
Tests for genesis/goal_specification.py
Stolen methodology:
  - MA-RAG (arXiv:2505.20096) — Planner/Step Definer
  - Enterprise Deep Research (arXiv:2510.17797) — task annotation
  - HTN Planning — hierarchical decomposition
  - SAGE (arXiv:2602.05975) — keyword precision
"""
import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from genesis.goal_specification import (
    SubGoal,
    GoalSpec,
    run_goal_specification,
    _heuristic_decompose,
    _parse_goal_spec_from_dict,
)


# ─── SubGoal Tests ────────────────────────────────────────────────────────────
class TestSubGoal(unittest.TestCase):
    def _make(self, **kwargs) -> SubGoal:
        defaults = dict(
            id="sg1", description="Find micro-task platforms",
            priority=1, success_criterion="3+ platforms found",
            search_queries=["micro task platforms", "paid micro tasks 2025"],
            keywords=["micro-task", "platform", "payment"],
            domain="web", scope="global", local_filter="",
        )
        defaults.update(kwargs)
        return SubGoal(**defaults)

    def test_basic_fields(self):
        sg = self._make()
        self.assertEqual(sg.id, "sg1")
        self.assertEqual(sg.priority, 1)
        self.assertEqual(sg.domain, "web")

    def test_to_dict(self):
        sg = self._make()
        d = sg.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("search_queries", d)
        self.assertIn("keywords", d)
        self.assertIn("priority", d)

    def test_local_filter(self):
        sg = self._make(local_filter="Egypt", scope="local")
        self.assertEqual(sg.local_filter, "Egypt")
        self.assertEqual(sg.scope, "local")

    def test_is_primary_default_false(self):
        sg = self._make()
        self.assertFalse(sg.is_primary)

    def test_is_primary_true(self):
        sg = self._make(is_primary=True)
        self.assertTrue(sg.is_primary)


# ─── GoalSpec Tests ───────────────────────────────────────────────────────────
class TestGoalSpec(unittest.TestCase):
    def _make_spec(self, n_subgoals=3) -> GoalSpec:
        sub_goals = [
            SubGoal(
                id=f"sg{i}", description=f"Sub-goal {i}",
                priority=i, success_criterion=f"Done {i}",
                search_queries=[f"query {i}a", f"query {i}b"],
                keywords=[f"kw{i}a", f"kw{i}b"],
                domain="web", scope="global", local_filter="",
                is_primary=(i == 1),
            )
            for i in range(1, n_subgoals + 1)
        ]
        return GoalSpec(
            task_name="micro_task",
            primary_goal="Find actionable micro-task opportunities",
            success_criteria=["3+ platforms verified", "Egypt availability stated"],
            priority_principle="Global first, then Egypt filter",
            scope="global_then_local",
            local_filter="Egypt",
            sub_goals=sub_goals,
        )

    def test_ordered_sub_goals(self):
        spec = self._make_spec(3)
        # Scramble order
        spec.sub_goals = spec.sub_goals[::-1]
        ordered = spec.ordered_sub_goals
        priorities = [sg.priority for sg in ordered]
        self.assertEqual(priorities, sorted(priorities))

    def test_ordered_single(self):
        spec = self._make_spec(1)
        ordered = spec.ordered_sub_goals
        self.assertEqual(len(ordered), 1)

    def test_to_prompt_section_contains_key_info(self):
        spec = self._make_spec(2)
        section = spec.to_prompt_section()
        self.assertIn("PRIMARY GOAL", section)
        self.assertIn("GLOBAL", section.upper())
        self.assertIn("Egypt", section)
        self.assertIn("SUB-GOALS", section)
        self.assertIn("sg1", section)

    def test_prompt_section_strategy(self):
        spec = self._make_spec(2)
        section = spec.to_prompt_section()
        # Should mention global-first strategy
        self.assertIn("GLOBAL", section.upper())
        self.assertIn("filter", section.lower())

    def test_save_and_load_roundtrip(self):
        spec = self._make_spec(3)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "goal_spec.json")
            spec.save(path)

            # Verify JSON structure
            with open(path) as f:
                data = json.load(f)
            self.assertIn("primary_goal", data)
            self.assertIn("sub_goals", data)
            self.assertEqual(len(data["sub_goals"]), 3)
            self.assertEqual(data["scope"], "global_then_local")
            self.assertEqual(data["local_filter"], "Egypt")

            # Load back
            loaded = GoalSpec.load(path)
            self.assertEqual(loaded.primary_goal, spec.primary_goal)
            self.assertEqual(len(loaded.sub_goals), 3)
            self.assertEqual(loaded.local_filter, "Egypt")
            ordered = loaded.ordered_sub_goals
            self.assertEqual(ordered[0].priority, 1)

    def test_created_at_set(self):
        spec = self._make_spec(1)
        self.assertIsNotNone(spec.created_at)
        self.assertIn("20", spec.created_at)  # year

    def test_success_criteria_list(self):
        spec = self._make_spec(1)
        self.assertIsInstance(spec.success_criteria, list)
        self.assertGreater(len(spec.success_criteria), 0)

    def test_to_dict_serializable(self):
        spec = self._make_spec(2)
        d = spec.to_dict()
        # Must be JSON-serializable
        json_str = json.dumps(d, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        self.assertGreater(len(json_str), 0)


# ─── _heuristic_decompose Tests ──────────────────────────────────────────────
class TestHeuristicDecompose(unittest.TestCase):
    def test_research_task(self):
        task_md = "Find and research micro-task platforms. Search for payment proofs."
        data = _heuristic_decompose(task_md, "micro_task", "Egypt")
        self.assertIn("primary_goal", data)
        self.assertIn("sub_goals", data)
        self.assertGreater(len(data["sub_goals"]), 0)
        self.assertIn("success_criteria", data)

    def test_coding_task(self):
        task_md = "Implement a function to sort data. Write code for the algorithm."
        data = _heuristic_decompose(task_md, "sorting_task", "")
        self.assertIn("sub_goals", data)
        self.assertGreater(len(data["sub_goals"]), 0)

    def test_generic_task(self):
        task_md = "Complete the analysis and provide recommendations."
        data = _heuristic_decompose(task_md, "analysis_task", "")
        self.assertIn("primary_goal", data)
        self.assertIn("sub_goals", data)

    def test_local_filter_in_subgoal(self):
        task_md = "Research opportunities and find relevant information."
        data = _heuristic_decompose(task_md, "test", "Egypt")
        # At least one sub-goal should reference local filter
        all_filters = [sg.get("local_filter", "") for sg in data["sub_goals"]]
        # Egypt should appear somewhere
        self.assertTrue(any("Egypt" in f for f in all_filters if f))

    def test_priority_ordering(self):
        task_md = "Find and research platforms."
        data = _heuristic_decompose(task_md, "test", "")
        priorities = [sg["priority"] for sg in data["sub_goals"]]
        self.assertEqual(priorities, sorted(priorities))

    def test_search_queries_present(self):
        task_md = "Research micro-task platforms."
        data = _heuristic_decompose(task_md, "micro_task", "")
        for sg in data["sub_goals"]:
            self.assertIn("search_queries", sg)
            self.assertIsInstance(sg["search_queries"], list)

    def test_keywords_present(self):
        task_md = "Research micro-task platforms."
        data = _heuristic_decompose(task_md, "micro_task", "")
        for sg in data["sub_goals"]:
            self.assertIn("keywords", sg)
            self.assertIsInstance(sg["keywords"], list)


# ─── _parse_goal_spec_from_dict Tests ────────────────────────────────────────
class TestParseGoalSpecFromDict(unittest.TestCase):
    def _sample_dict(self) -> dict:
        return {
            "primary_goal": "Find the best micro-task opportunities",
            "success_criteria": ["3+ platforms found", "Egypt availability stated"],
            "priority_principle": "Global first, then local",
            "scope": "global_then_local",
            "local_filter": "Egypt",
            "sub_goals": [
                {
                    "id": "sg1", "description": "Find global platforms",
                    "priority": 1, "success_criterion": "3+ found",
                    "search_queries": ["micro task platforms 2025"],
                    "keywords": ["micro-task", "platform"],
                    "domain": "web", "scope": "global",
                    "local_filter": "", "is_primary": True,
                },
                {
                    "id": "sg2", "description": "Verify credibility",
                    "priority": 2, "success_criterion": "each has payment proof",
                    "search_queries": ["platform payment proof"],
                    "keywords": ["payment", "verified"],
                    "domain": "forum", "scope": "global",
                    "local_filter": "", "is_primary": False,
                },
            ]
        }

    def test_basic_parse(self):
        data = self._sample_dict()
        spec = _parse_goal_spec_from_dict(data, "micro_task")
        self.assertEqual(spec.primary_goal, "Find the best micro-task opportunities")
        self.assertEqual(len(spec.sub_goals), 2)
        self.assertEqual(spec.local_filter, "Egypt")

    def test_sub_goals_converted(self):
        data = self._sample_dict()
        spec = _parse_goal_spec_from_dict(data, "test")
        self.assertIsInstance(spec.sub_goals[0], SubGoal)
        self.assertEqual(spec.sub_goals[0].id, "sg1")
        self.assertTrue(spec.sub_goals[0].is_primary)

    def test_max_sub_goals_respected(self):
        data = self._sample_dict()
        # Add many sub-goals
        for i in range(3, 15):
            data["sub_goals"].append({
                "id": f"sg{i}", "description": f"Extra {i}",
                "priority": i, "success_criterion": "done",
                "search_queries": ["q"], "keywords": ["k"],
                "domain": "web", "scope": "global",
                "local_filter": "", "is_primary": False,
            })
        spec = _parse_goal_spec_from_dict(data, "test")
        self.assertLessEqual(len(spec.sub_goals), 6)  # MAX_SUB_GOALS

    def test_max_queries_per_subgoal(self):
        data = self._sample_dict()
        data["sub_goals"][0]["search_queries"] = ["q1", "q2", "q3", "q4", "q5"]
        spec = _parse_goal_spec_from_dict(data, "test")
        self.assertLessEqual(len(spec.sub_goals[0].search_queries), 3)

    def test_max_keywords_per_subgoal(self):
        data = self._sample_dict()
        data["sub_goals"][0]["keywords"] = ["k1", "k2", "k3", "k4", "k5", "k6", "k7"]
        spec = _parse_goal_spec_from_dict(data, "test")
        self.assertLessEqual(len(spec.sub_goals[0].keywords), 5)

    def test_task_name_set(self):
        data = self._sample_dict()
        spec = _parse_goal_spec_from_dict(data, "my_task")
        self.assertEqual(spec.task_name, "my_task")


# ─── run_goal_specification Integration (mocked) ─────────────────────────────
class TestRunGoalSpecification(unittest.TestCase):
    TASK_MD = """# Micro-Task Economy Research
Find micro-task platforms available in Egypt.
## Evaluation Criteria
1. Real platforms with payment proof
2. Egypt availability clearly stated
"""

    def _mock_llm_response(self, data: dict) -> MagicMock:
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.choices[0].message.content = json.dumps(data)
        mock_client.chat.completions.create.return_value = mock_resp
        return mock_client

    def test_runs_with_mocked_llm(self):
        mock_data = {
            "primary_goal": "Find verified micro-task platforms",
            "success_criteria": ["3+ platforms", "Egypt check"],
            "priority_principle": "Global first",
            "scope": "global_then_local",
            "local_filter": "Egypt",
            "sub_goals": [
                {
                    "id": "sg1", "description": "Find platforms globally",
                    "priority": 1, "success_criterion": "3+ found",
                    "search_queries": ["micro task platform 2025"],
                    "keywords": ["micro-task", "platform"],
                    "domain": "web", "scope": "global",
                    "local_filter": "", "is_primary": True,
                }
            ]
        }
        mock_client = self._mock_llm_response(mock_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            spec = run_goal_specification(
                task_md=self.TASK_MD,
                task_name="micro_task",
                run_dir=tmpdir,
                llm_client=mock_client,
                local_filter="Egypt",
            )
            self.assertEqual(spec.primary_goal, "Find verified micro-task platforms")
            self.assertEqual(len(spec.sub_goals), 1)
            self.assertEqual(spec.local_filter, "Egypt")

            # Verify file saved
            spec_path = os.path.join(tmpdir, "goal_spec.json")
            self.assertTrue(os.path.exists(spec_path))

    def test_uses_cache_second_call(self):
        mock_client = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-create cache
            cached_spec = GoalSpec(
                task_name="micro_task",
                primary_goal="Cached primary goal",
                success_criteria=["cached"],
                priority_principle="cached principle",
                scope="global",
                local_filter="Egypt",
                sub_goals=[SubGoal(
                    id="sg1", description="cached sg",
                    priority=1, success_criterion="done",
                    search_queries=["q"], keywords=["k"],
                    domain="web", scope="global", local_filter="",
                )],
            )
            cached_spec.save(os.path.join(tmpdir, "goal_spec.json"))

            spec = run_goal_specification(
                task_md=self.TASK_MD,
                task_name="micro_task",
                run_dir=tmpdir,
                llm_client=mock_client,
                force=False,
            )
            # Should use cache — LLM not called
            mock_client.chat.completions.create.assert_not_called()
            self.assertEqual(spec.primary_goal, "Cached primary goal")

    def test_force_bypasses_cache(self):
        mock_data = {
            "primary_goal": "Fresh goal",
            "success_criteria": ["fresh"],
            "priority_principle": "fresh",
            "scope": "global",
            "local_filter": "",
            "sub_goals": [
                {"id": "sg1", "description": "fresh sg", "priority": 1,
                 "success_criterion": "done", "search_queries": ["q"],
                 "keywords": ["k"], "domain": "web", "scope": "global",
                 "local_filter": "", "is_primary": True}
            ]
        }
        mock_client = self._mock_llm_response(mock_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-create stale cache
            old = GoalSpec(
                task_name="test", primary_goal="Old goal",
                success_criteria=[], priority_principle="old",
                scope="global", local_filter="", sub_goals=[],
            )
            old.save(os.path.join(tmpdir, "goal_spec.json"))

            spec = run_goal_specification(
                task_md=self.TASK_MD,
                task_name="test",
                run_dir=tmpdir,
                llm_client=mock_client,
                force=True,
            )
            # Should use fresh LLM result
            self.assertEqual(spec.primary_goal, "Fresh goal")

    def test_heuristic_fallback_when_llm_fails(self):
        mock_client = MagicMock()
        # LLM returns garbage
        mock_resp = MagicMock()
        mock_resp.choices[0].message.content = "not json at all"
        mock_client.chat.completions.create.return_value = mock_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            spec = run_goal_specification(
                task_md="Research micro-task platforms and find opportunities.",
                task_name="micro_task",
                run_dir=tmpdir,
                llm_client=mock_client,
                local_filter="Egypt",
            )
            # Should fall back to heuristic
            self.assertIsNotNone(spec)
            self.assertGreater(len(spec.sub_goals), 0)
            self.assertEqual(spec.model_used, "heuristic")

    def test_prompt_section_injected(self):
        """GoalSpec.to_prompt_section() returns text with key sections."""
        spec = GoalSpec(
            task_name="test",
            primary_goal="Find opportunities",
            success_criteria=["3+ platforms"],
            priority_principle="Global first",
            scope="global_then_local",
            local_filter="Egypt",
            sub_goals=[SubGoal(
                id="sg1", description="Find global platforms",
                priority=1, success_criterion="done",
                search_queries=["query 1"], keywords=["kw1"],
                domain="web", scope="global", local_filter="Egypt",
            )],
        )
        section = spec.to_prompt_section()
        self.assertIn("PRIMARY GOAL", section)
        self.assertIn("SUB-GOALS", section)
        self.assertIn("sg1", section)
        self.assertIn("Egypt", section)
        self.assertIn("GLOBAL", section.upper())
        self.assertIn("query 1", section)
        self.assertIn("kw1", section)


if __name__ == "__main__":
    unittest.main(verbosity=2)
