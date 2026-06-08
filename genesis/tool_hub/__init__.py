"""
GENESIS Tool Hub
=================
Component: TOOL_HUB
Source: MCP (Model Context Protocol) + MUSE-Autoskill

Clean public API — this is the ONLY import point for orchestrator and agents:

  from genesis.tool_hub import get_tool, invoke, catalog, register_tool

Orchestrator injection:
  Section 3: catalog() → injected in META_AGENT_PROMPT
  Section 5a: agents invoke tools via this interface

Target agent usage:
  from genesis.tool_hub import invoke
  result = invoke("web_search", {"query": "...", "mode": "quick"})

Backward compat:
  from genesis.tools.web_search import web_search  ← STILL WORKS (never remove)
"""

from __future__ import annotations

import logging
from typing import Any

from genesis.tool_hub.registry import ToolRegistry, ToolSpec, ToolResult
from genesis.tool_hub.executor import SandboxExecutor

logger = logging.getLogger(__name__)

# ─── Singleton Registry ────────────────────────────────────────────────────────
_registry = ToolRegistry()

# ─── Auto-register all built-in tools ─────────────────────────────────────────
try:
    from genesis.tool_hub.tools import ALL_TOOLS
    for _tool in ALL_TOOLS:
        _registry.register(_tool)
    logger.info(f"Tool Hub initialized: {len(ALL_TOOLS)} tools registered")
except Exception as _e:
    logger.warning(f"Tool Hub: partial registration ({_e})")

# ─── Public API ───────────────────────────────────────────────────────────────

def get_tool(name: str) -> ToolSpec:
    """Get tool spec by name."""
    return _registry.get(name)


def invoke(name: str, args: dict) -> dict:
    """
    Invoke a tool. Returns result dict.
    Always returns dict (never raises — errors in result["error"]).
    """
    result = _registry.invoke(name, args)
    if result.success:
        return result.result if isinstance(result.result, dict) else {"result": result.result}
    return {"error": result.error, "success": False, "tool": name}


def invoke_full(name: str, args: dict) -> ToolResult:
    """Invoke a tool and get full ToolResult (with metadata)."""
    return _registry.invoke(name, args)


def catalog() -> str:
    """
    Get tool catalog for META_AGENT_PROMPT injection.
    Progressive disclosure: name + description only.
    """
    return _registry.catalog()


def catalog_yaml() -> str:
    """YAML format catalog."""
    return _registry.catalog_yaml()


def register_tool(tool: ToolSpec) -> None:
    """Register a new tool (e.g., from SKILL_ENGINE for skill_use tool)."""
    _registry.register(tool)
    logger.info(f"Tool registered: {tool.name}")


def list_tools() -> list[str]:
    """List all registered tool names."""
    return [t.name for t in _registry.discover()]


def get_stats() -> dict:
    """Get invocation stats for Telemetry Engine."""
    return _registry.get_stats()


# ─── Convenience shortcuts ────────────────────────────────────────────────────

def web_search(query: str, mode: str = "quick", num_results: int = 10) -> dict:
    """Shortcut for web_search tool."""
    return invoke("web_search", {"query": query, "mode": mode, "num_results": num_results})


def extract_keywords(query: str) -> list[str]:
    """Shortcut for extract_keywords tool."""
    result = invoke("extract_keywords", {"query": query})
    return result.get("keywords", [])


def run_code(code: str, timeout_sec: int = 30) -> dict:
    """Shortcut for code_exec tool."""
    return invoke("code_exec", {"code": code, "timeout_sec": timeout_sec})


def llm_call(messages: list, model: str = "", max_tokens: int = 2000) -> str:
    """Shortcut for llm_call tool. Returns content string."""
    args = {"messages": messages, "max_tokens": max_tokens}
    if model:
        args["model"] = model
    result = invoke("llm_call", args)
    return result.get("content", "")


# ─── Re-exports for backward compat awareness ─────────────────────────────────
__all__ = [
    "get_tool", "invoke", "invoke_full", "catalog", "catalog_yaml",
    "register_tool", "list_tools", "get_stats",
    "web_search", "extract_keywords", "run_code", "llm_call",
    "ToolSpec", "ToolResult", "SandboxExecutor",
]
