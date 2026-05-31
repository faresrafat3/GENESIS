"""Tests for Real LLM evaluation - all HTTP calls are mocked."""
from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch, MagicMock

import pytest


# Mock response that contains keywords to satisfy verification checks
MOCK_LLM_RESPONSE = (
    "Based on the evidence, I observe a clear contrast between the two approaches. "
    "The first option is better supported by grounded observations, while the second "
    "shows difference in its evidence base. The structured layout with labeled field "
    "entries provides a checklist for operator handoff. "
    "This is inferred from the observed patterns and supported by evidence. "
    "The decisive factor is the stronger empirical grounding."
)


def _make_mock_urlopen(response_text: str = MOCK_LLM_RESPONSE):
    """Create a mock urlopen that returns a proper API response."""
    mock_response_data = {
        "choices": [{"message": {"content": response_text}}]
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(mock_response_data).encode("utf-8")
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestLLMAdapterCostTracking:
    """Test cost tracking in LLMAdapter."""

    def test_initial_state_zero_cost(self):
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key="test-key")
        report = adapter.get_cost_report()
        assert report["total_calls"] == 0
        assert report["total_cost_estimate"] == 0.0
        assert report["per_model_calls"] == {}

    @patch("urllib.request.urlopen")
    def test_generate_with_tracking_increments_cost(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen()
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key="test-key")

        response, cost_info = adapter.generate_with_tracking("test prompt")

        assert cost_info["call_number"] == 1
        assert cost_info["estimated_cost"] == 0.001
        assert cost_info["cumulative_cost"] == 0.001
        assert "model" in cost_info

    @patch("urllib.request.urlopen")
    def test_multiple_calls_accumulate_cost(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen()
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key="test-key")

        adapter.generate_with_tracking("prompt 1")
        adapter.generate_with_tracking("prompt 2")
        adapter.generate_with_tracking("prompt 3")

        report = adapter.get_cost_report()
        assert report["total_calls"] == 3
        assert abs(report["total_cost_estimate"] - 0.003) < 1e-9

    @patch("urllib.request.urlopen")
    def test_per_model_calls_tracked(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen()
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key="test-key")

        adapter.generate_with_tracking("p1", model_tier="tier_0")
        adapter.generate_with_tracking("p2", model_tier="tier_1")
        adapter.generate_with_tracking("p3", model_tier="tier_0")

        report = adapter.get_cost_report()
        assert report["per_model_calls"]["openrouter/owl-alpha"] == 3


class TestLLMAdapterAPIKey:
    """Test API key resolution."""

    def test_api_key_from_constructor(self):
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key="custom-key")
        assert adapter.api_key == "custom-key"

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "env-key"})
    def test_api_key_from_env(self):
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(api_key=None)
        assert adapter.api_key == "env-key"

    def test_api_key_from_config_fallback(self):
        from virtual_sia.api.llm_adapter import LLMAdapter
        adapter = LLMAdapter(use_config_fallback=True)
        # In test env without env var, key may be empty string (mock mode)
        assert adapter.api_key is not None


class TestPromptBuilding:
    """Test prompt building functions in llm_reasoning."""

    def test_build_raw_prompt(self):
        from virtual_sia.api.llm_reasoning import build_raw_prompt
        result = build_raw_prompt("Compare A and B")
        assert "## Task" in result
        assert "Compare A and B" in result
        assert "## Instructions" in result
        assert "Relevant Concepts" not in result

    def test_build_augmented_prompt_with_concepts_only(self):
        from virtual_sia.api.llm_reasoning import build_augmented_prompt
        result = build_augmented_prompt(
            "Do the task",
            concept_hints=["Concept 1", "Concept 2"],
        )
        assert "## Relevant Concepts" in result
        assert "- Concept 1" in result
        assert "- Concept 2" in result
        assert "## Task" in result
        assert "Applicable Theories" not in result

    def test_build_augmented_prompt_with_theories(self):
        from virtual_sia.api.llm_reasoning import build_augmented_prompt
        result = build_augmented_prompt(
            "Do the task",
            concept_hints=["C1"],
            theory_hints=["T1", "T2"],
        )
        assert "## Relevant Concepts" in result
        assert "## Applicable Theories" in result
        assert "- T1" in result
        assert "- T2" in result
        assert "## Instructions" in result

    def test_build_augmented_prompt_no_hints_no_instructions(self):
        from virtual_sia.api.llm_reasoning import build_augmented_prompt
        result = build_augmented_prompt("Just the task")
        assert "## Task" in result
        assert "Just the task" in result
        assert "## Instructions" not in result


class TestGenerateWithConcepts:
    """Test the generate_with_concepts function with mocked HTTP."""

    @patch("urllib.request.urlopen")
    def test_successful_call(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("Generated text here")
        from virtual_sia.api.llm_reasoning import generate_with_concepts

        result = generate_with_concepts(
            "Test task",
            concept_hints=["hint1"],
            api_key="test-key",
        )
        assert result == "Generated text here"

    @patch("urllib.request.urlopen")
    def test_http_error_returns_error_string(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "http://test", 429, "Rate limited", {}, None
        )
        from virtual_sia.api.llm_reasoning import generate_with_concepts

        result = generate_with_concepts("Test", api_key="key")
        assert "[LLM_ERROR]" in result
        assert "HTTPError" in result

    @patch("urllib.request.urlopen")
    def test_malformed_response_returns_error(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"not_choices": []}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        from virtual_sia.api.llm_reasoning import generate_with_concepts

        result = generate_with_concepts("Test", api_key="key")
        assert "[LLM_ERROR]" in result
        assert "Parse error" in result

    @patch("urllib.request.urlopen")
    def test_request_structure(self, mock_urlopen):
        mock_urlopen.return_value = _make_mock_urlopen("ok")
        from virtual_sia.api.llm_reasoning import generate_with_concepts

        generate_with_concepts("My task", api_key="sk-test-123", model="test-model")

        # Verify the request was made with correct structure
        mock_urlopen.assert_called_once()
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert req.get_header("Authorization") == "Bearer sk-test-123"
        assert req.get_header("Content-type") == "application/json"

        payload = json.loads(req.data)
        assert payload["model"] == "test-model"
        assert payload["messages"][0]["role"] == "user"
        assert "My task" in payload["messages"][0]["content"]


class TestEvalRunnerTaskSelection:
    """Test the eval runner task selection logic."""

    def test_select_eval_tasks_default(self):
        from virtual_sia.eval.runners.run_real_llm_eval import select_eval_tasks
        tasks = select_eval_tasks(count_per_family=2)
        assert len(tasks) == 6
        families = [t.expected_primary_family for t in tasks]
        assert families.count("comparison") == 2
        assert families.count("synthesis") == 2
        assert families.count("procedure") == 2

    def test_select_eval_tasks_one_per_family(self):
        from virtual_sia.eval.runners.run_real_llm_eval import select_eval_tasks
        tasks = select_eval_tasks(count_per_family=1)
        assert len(tasks) == 3


class TestComputeEvalSummary:
    """Test the evaluation summary computation."""

    def test_basic_summary(self):
        from virtual_sia.eval.runners.run_real_llm_eval import compute_eval_summary
        results = [
            {"condition": "A_raw", "task_family": "comparison", "good_enough": True},
            {"condition": "A_raw", "task_family": "synthesis", "good_enough": False},
            {"condition": "B_concept", "task_family": "comparison", "good_enough": True},
            {"condition": "B_concept", "task_family": "synthesis", "good_enough": True},
            {"condition": "C_full", "task_family": "comparison", "good_enough": True},
            {"condition": "C_full", "task_family": "synthesis", "good_enough": True},
        ]
        summary = compute_eval_summary(results)

        assert summary["total_evaluations"] == 6
        assert summary["conditions"]["A_raw"]["success_rate"] == 0.5
        assert summary["conditions"]["B_concept"]["success_rate"] == 1.0
        assert summary["conditions"]["C_full"]["success_rate"] == 1.0
        assert summary["concept_lift"] == 0.5
        assert summary["theory_lift"] == 0.0
        assert summary["total_lift"] == 0.5

    def test_summary_by_family(self):
        from virtual_sia.eval.runners.run_real_llm_eval import compute_eval_summary
        results = [
            {"condition": "A_raw", "task_family": "comparison", "good_enough": True},
            {"condition": "A_raw", "task_family": "synthesis", "good_enough": False},
        ]
        summary = compute_eval_summary(results)
        assert "comparison" in summary["by_family"]
        assert "synthesis" in summary["by_family"]
        assert summary["by_family"]["comparison"]["A_raw"]["success_rate"] == 1.0
        assert summary["by_family"]["synthesis"]["A_raw"]["success_rate"] == 0.0

    def test_empty_results(self):
        from virtual_sia.eval.runners.run_real_llm_eval import compute_eval_summary
        summary = compute_eval_summary([])
        assert summary["total_evaluations"] == 0
        assert summary["concept_lift"] == 0.0


class TestRunSingleCondition:
    """Test run_single_condition with mocked LLM."""

    @patch("virtual_sia.eval.runners.run_real_llm_eval._call_openrouter")
    def test_condition_a_raw(self, mock_call):
        mock_call.return_value = MOCK_LLM_RESPONSE
        from virtual_sia.eval.runners.run_real_llm_eval import run_single_condition, select_eval_tasks

        tasks = select_eval_tasks(count_per_family=1)
        task = tasks[0]  # comparison task

        result = run_single_condition(task, "A_raw", api_key="test")
        assert result["condition"] == "A_raw"
        assert result["task_family"] == "comparison"
        assert "good_enough" in result
        assert "response_preview" in result
        assert result["response_length"] > 0

    @patch("virtual_sia.eval.runners.run_real_llm_eval._call_openrouter")
    def test_condition_c_full_passes_verification(self, mock_call):
        mock_call.return_value = MOCK_LLM_RESPONSE
        from virtual_sia.eval.runners.run_real_llm_eval import run_single_condition, select_eval_tasks

        tasks = select_eval_tasks(count_per_family=1)
        task = tasks[0]  # comparison task

        result = run_single_condition(
            task, "C_full",
            concept_hints=["evidence grounding"],
            theory_hints=["contract compliance"],
            api_key="test",
        )
        assert result["condition"] == "C_full"
        # Mock response has keywords that should pass comparison verification
        assert result["good_enough"] is True

    @patch("virtual_sia.eval.runners.run_real_llm_eval._call_openrouter")
    def test_error_in_llm_returns_error_result(self, mock_call):
        mock_call.return_value = "[LLM_ERROR] HTTPError: 500"
        from virtual_sia.eval.runners.run_real_llm_eval import run_single_condition, select_eval_tasks

        tasks = select_eval_tasks(count_per_family=1)
        task = tasks[0]

        result = run_single_condition(task, "A_raw", api_key="test")
        # Error response is detected and short-circuits verification
        assert result["good_enough"] is False
        assert "error" in result
        assert result["error"] == "[LLM_ERROR] HTTPError: 500"


class TestConfigConstants:
    """Test that config constants are properly set."""

    def test_openrouter_api_key_exists(self):
        from virtual_sia.api.config import OPENROUTER_API_KEY
        # Key is loaded from env var; in test env it may be empty string
        assert isinstance(OPENROUTER_API_KEY, str)

    def test_openrouter_base_url(self):
        from virtual_sia.api.config import OPENROUTER_BASE_URL
        assert "openrouter.ai" in OPENROUTER_BASE_URL

    def test_default_model(self):
        from virtual_sia.api.config import DEFAULT_MODEL
        assert DEFAULT_MODEL == "openrouter/owl-alpha"

    def test_model_mapping_uses_owl_alpha(self):
        from virtual_sia.api.config import APIConfig
        config = APIConfig()
        assert config.model_mapping["tier_0"] == "openrouter/owl-alpha"
        assert config.model_mapping["tier_1"] == "openrouter/owl-alpha"
        assert config.model_mapping["tier_2"] == "openrouter/owl-alpha"
