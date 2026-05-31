"""LLM adapter for OpenRouter API with mock fallback and cost tracking."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Dict


class LLMAdapter:
    """Adapter for LLM calls via OpenRouter with deterministic mock fallback."""

    ESTIMATED_COST_PER_CALL = 0.001

    def __init__(self, api_key: str | None = None, use_config_fallback: bool = False) -> None:
        if api_key:
            self.api_key = api_key
        elif os.environ.get("OPENROUTER_API_KEY"):
            self.api_key = os.environ["OPENROUTER_API_KEY"]
        elif use_config_fallback:
            from .config import OPENROUTER_API_KEY as CONFIG_KEY
            self.api_key = CONFIG_KEY
        else:
            self.api_key = None
        self._call_count: int = 0
        self._total_cost_estimate: float = 0.0
        self._per_model_calls: Dict[str, int] = {}

    def generate(self, prompt: str, model_tier: str = "tier_1", temperature: float = 0.7) -> str:
        """Generate a response for the given prompt.

        When api_key is set, calls OpenRouter API.
        When no api_key, returns a deterministic mock response.
        """
        if not self.api_key:
            return self._mock_generate(prompt)

        from .config import APIConfig
        config = APIConfig()
        model = config.model_mapping.get(model_tier, config.model_mapping["tier_1"])
        return self._call_openrouter(prompt, model, temperature)

    def generate_with_tracking(
        self, prompt: str, model_tier: str = "tier_1", temperature: float = 0.7
    ) -> tuple[str, dict]:
        """Generate a response and return (response_text, cost_info).

        Tracks call count and estimated cost per model.
        """
        from .config import APIConfig
        config = APIConfig()
        model = config.model_mapping.get(model_tier, config.model_mapping["tier_1"])

        response = self.generate(prompt, model_tier, temperature)

        # Track cost
        self._call_count += 1
        self._total_cost_estimate += self.ESTIMATED_COST_PER_CALL
        self._per_model_calls[model] = self._per_model_calls.get(model, 0) + 1

        cost_info = {
            "model": model,
            "estimated_cost": self.ESTIMATED_COST_PER_CALL,
            "cumulative_cost": self._total_cost_estimate,
            "call_number": self._call_count,
        }
        return response, cost_info

    def get_cost_report(self) -> dict:
        """Return summary of API usage and estimated costs."""
        return {
            "total_calls": self._call_count,
            "total_cost_estimate": self._total_cost_estimate,
            "per_model_calls": dict(self._per_model_calls),
        }

    def _mock_generate(self, prompt: str) -> str:
        """Return a deterministic mock response based on prompt hash."""
        truncated = prompt[:50]
        return f"Mock response for: {truncated}..."

    def _call_openrouter(self, prompt: str, model: str, temperature: float) -> str:
        """Call OpenRouter API and return the response text."""
        from .config import OPENROUTER_BASE_URL
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://virtual-sia.dev",
            "X-Title": "Virtual-SIA",
        }
        payload = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }).encode("utf-8")

        req = urllib.request.Request(
            OPENROUTER_BASE_URL, data=payload, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError) as e:
            return f"LLM error: {e}"
