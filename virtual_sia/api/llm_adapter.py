"""LLM adapter for OpenRouter API with mock fallback."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error


class LLMAdapter:
    """Adapter for LLM calls via OpenRouter with deterministic mock fallback."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")

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

    def _mock_generate(self, prompt: str) -> str:
        """Return a deterministic mock response based on prompt hash."""
        truncated = prompt[:50]
        return f"Mock response for: {truncated}..."

    def _call_openrouter(self, prompt: str, model: str, temperature: float) -> str:
        """Call OpenRouter API and return the response text."""
        url = "https://openrouter.ai/api/v1/chat/completions"
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

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError) as e:
            return f"LLM error: {e}"
