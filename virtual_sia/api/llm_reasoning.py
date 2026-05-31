"""LLM reasoning with concept and theory augmentation."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Optional


def generate_with_concepts(
    task_text: str,
    concept_hints: list[str] | None = None,
    theory_hints: list[str] | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    """Generate LLM response with optional concept and theory augmentation.

    Builds a structured prompt that includes the task + concept hints + theory hints,
    calls OpenRouter API, and returns the generated response.
    """
    from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL

    resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY
    resolved_model = model or DEFAULT_MODEL

    prompt = build_augmented_prompt(task_text, concept_hints, theory_hints)

    return _call_openrouter(prompt, resolved_model, resolved_key)


def build_augmented_prompt(
    task_text: str,
    concept_hints: list[str] | None = None,
    theory_hints: list[str] | None = None,
) -> str:
    """Build a structured prompt with optional concept and theory augmentation."""
    parts = []

    if concept_hints:
        parts.append("## Relevant Concepts")
        for hint in concept_hints:
            parts.append(f"- {hint}")
        parts.append("")

    if theory_hints:
        parts.append("## Applicable Theories")
        for hint in theory_hints:
            parts.append(f"- {hint}")
        parts.append("")

    parts.append("## Task")
    parts.append(task_text)

    if concept_hints or theory_hints:
        parts.append("")
        parts.append("## Instructions")
        parts.append(
            "Use the concepts and theories above to guide your response. "
            "Ensure your answer satisfies the task requirements while "
            "demonstrating awareness of the relevant concepts."
        )

    return "\n".join(parts)


def build_raw_prompt(task_text: str) -> str:
    """Build a simple prompt without augmentation (for baseline condition)."""
    return (
        f"## Task\n{task_text}\n\n"
        f"## Instructions\n"
        f"Provide a thorough, well-structured response to the task above."
    )


def _call_openrouter(prompt: str, model: str, api_key: str) -> str:
    """Call OpenRouter API and return response text."""
    from .config import OPENROUTER_BASE_URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://virtual-sia.dev",
        "X-Title": "Virtual-SIA-Eval",
    }
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1024,
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_BASE_URL, data=payload, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        return f"[LLM_ERROR] {type(e).__name__}: {e}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"[LLM_ERROR] Parse error: {e}"
