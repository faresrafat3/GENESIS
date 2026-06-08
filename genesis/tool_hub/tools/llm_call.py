"""
GENESIS Tool Hub — LLM Call Tool
==================================
Component: TOOL_HUB.tools.llm_call
Source: genesis/util.py + tools/api_key_pool.py (wraps existing)

Genesis Role:
  - Agents can call LLM via tool interface (consistent with other tools)
  - Automatic key rotation via APIKeyPool
  - Cost tracking per call for Safety Engine

Called by: genesis/tool_hub/__init__.py (auto-registration)
"""

from __future__ import annotations

import logging
import os

from genesis.tool_hub.registry import ToolSpec

logger = logging.getLogger(__name__)


def _execute_llm_call(args: dict) -> dict:
    """
    Call LLM with automatic key rotation.
    Args: {messages: list, model: str, max_tokens: int, temperature: float}
    Returns: {content: str, model: str, usage: dict}
    """
    import openai
    import httpx

    messages = args.get("messages", [])
    model = args.get("model", os.getenv("TASK_MODEL", "openai/gpt-oss-20b:free"))
    max_tokens = args.get("max_tokens", 2000)
    temperature = args.get("temperature", 0.1)

    if not messages:
        return {"error": "messages required", "content": ""}

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key:
        return {"error": "No API key (OPENAI_API_KEY)", "content": ""}

    try:
        http_client = httpx.Client(headers={"Accept-Encoding": "identity"}, timeout=120)
        client = openai.OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        }
        return {"content": content, "model": model, "usage": usage}

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return {"error": str(e), "content": ""}


LLM_CALL_TOOL = ToolSpec(
    name="llm_call",
    description="Call LLM with automatic OpenRouter key rotation",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "messages": {"type": "array", "description": "Chat messages list"},
            "model": {"type": "string", "default": "openai/gpt-oss-20b:free"},
            "max_tokens": {"type": "integer", "default": 2000},
            "temperature": {"type": "number", "default": 0.1},
        },
        "required": ["messages"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "model": {"type": "string"},
            "usage": {"type": "object"},
        },
    },
    preconditions=["OPENAI_API_KEY available"],
    failure_modes=["Rate limit", "Model unavailable", "No API key"],
    cost_per_call_usd=0.0,  # free tier
    requires_sandbox=False,
    executor=_execute_llm_call,
    source_project="genesis/util.py + api_key_pool.py",
    genesis_role="Secondary LLM calls within agent execution loop",
)

ALL_TOOLS = [LLM_CALL_TOOL]
