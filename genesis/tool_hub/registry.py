"""
GENESIS Tool Hub — Registry
============================
Component: TOOL_HUB
Source: MCP (Model Context Protocol, Anthropic/Linux Foundation 2026)
        MUSE-Autoskill (arXiv:2605.27366) — sandbox lifecycle tools concept
        SkillOps (arXiv:2605.13716) — contract-based tool spec (P,O,A,V,F adapted)

Stolen:
  - ToolSpec schema: input_schema + output_schema + preconditions + failure_modes
  - ToolRegistry: dynamic discovery pattern (MCP-inspired)
  - Progressive disclosure: catalog = name+description ONLY in system prompt
  - Tool invocation returns structured ToolResult

Genesis Adaptation:
  - Tools are Python callables (not JSON-RPC like real MCP)
  - Catalog → YAML string injected in META_AGENT_PROMPT
  - Every tool registers cost_per_call_usd for Safety Engine tracking
  - ToolResult includes metadata for Telemetry Engine

Called by:
  - genesis/orchestrator.py Section 3: tool_catalog() → META_AGENT_PROMPT
  - genesis/tool_hub/__init__.py: singleton registry
  - target_agent.py: from genesis.tool_hub import invoke

Calls: individual tool executors in genesis/tool_hub/tools/

Artifact out: none (in-memory registry, catalog.yaml auto-generated)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable

import yaml

logger = logging.getLogger(__name__)


# ─── ToolSpec ─────────────────────────────────────────────────────────────────

@dataclass
class ToolSpec:
    """
    Single tool specification.
    Stolen from: MCP Tool Definition + SkillOps contract (P,O,A,V,F adapted)

    name          → unique identifier
    description   → what it does (ONLY this goes in catalog/system prompt)
    version       → semver
    input_schema  → JSON Schema for args
    output_schema → JSON Schema for result
    preconditions → when tool is applicable (SkillOps P)
    failure_modes → known failure reasons (SkillOps F)
    cost_per_call_usd → for Safety Engine budget tracking
    requires_sandbox  → True = runs in isolated subprocess
    executor      → Python callable that actually runs the tool
    source_project → which paper/project this tool came from
    genesis_role  → why we have this in GENESIS specifically
    """
    name: str
    description: str
    version: str = "1.0.0"
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    cost_per_call_usd: float = 0.0
    requires_sandbox: bool = False
    executor: Callable | None = None
    source_project: str = ""
    genesis_role: str = ""

    def get_catalog_entry(self) -> str:
        """Catalog entry: name + description only (progressive disclosure)."""
        cost = f" [~${self.cost_per_call_usd:.4f}/call]" if self.cost_per_call_usd > 0 else " [free]"
        sandbox = " [sandbox]" if self.requires_sandbox else ""
        return f"  {self.name}: {self.description}{cost}{sandbox}"

    def to_dict_safe(self) -> dict:
        """Serializable dict (excludes executor callable)."""
        d = asdict(self)
        d.pop("executor", None)
        return d


# ─── ToolResult ───────────────────────────────────────────────────────────────

@dataclass
class ToolResult:
    """
    Structured result from tool invocation.
    Includes metadata for Telemetry Engine.
    """
    tool_name: str
    success: bool
    result: Any
    error: str | None = None
    execution_time_ms: float = 0.0
    cost_usd: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "cost_usd": self.cost_usd,
            "metadata": self.metadata,
        }


# ─── ToolRegistry ─────────────────────────────────────────────────────────────

class ToolRegistry:
    """
    Central tool registry.
    Stolen from: MCP Server dynamic discovery pattern.

    Manages: registration, discovery, invocation, catalog generation.
    All tools are Python callables registered at startup.
    """

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}
        self._invocation_count: dict[str, int] = {}
        self._total_cost_usd: float = 0.0

    def register(self, tool: ToolSpec) -> None:
        """Register a tool. Overwrites if same name exists (versioning)."""
        if tool.executor is None:
            raise ValueError(f"Tool '{tool.name}' must have an executor callable")
        self._tools[tool.name] = tool
        self._invocation_count[tool.name] = 0
        logger.debug(f"Tool registered: {tool.name} v{tool.version}")

    def get(self, name: str) -> ToolSpec:
        """Get tool by name. Raises KeyError if not found."""
        if name not in self._tools:
            available = list(self._tools.keys())
            raise KeyError(f"Tool '{name}' not found. Available: {available}")
        return self._tools[name]

    def discover(self) -> list[ToolSpec]:
        """MCP-style: return all registered tools."""
        return list(self._tools.values())

    def catalog(self) -> str:
        """
        Progressive disclosure catalog for system prompt injection.
        Only name + description (not full spec) to save tokens.
        """
        lines = ["AVAILABLE TOOLS (call via invoke('tool_name', {...})):"]
        for tool in sorted(self._tools.values(), key=lambda t: t.name):
            lines.append(tool.get_catalog_entry())
        return "\n".join(lines)

    def catalog_yaml(self) -> str:
        """YAML format of catalog for META_AGENT_PROMPT."""
        tools_data = []
        for tool in sorted(self._tools.values(), key=lambda t: t.name):
            tools_data.append({
                "name": tool.name,
                "description": tool.description,
                "cost": f"${tool.cost_per_call_usd:.4f}/call" if tool.cost_per_call_usd else "free",
                "sandbox": tool.requires_sandbox,
            })
        return yaml.dump({"available_tools": tools_data}, allow_unicode=True, default_flow_style=False)

    def invoke(self, name: str, args: dict) -> ToolResult:
        """
        Invoke a tool by name with args.
        Tracks invocation count and cost for Safety Engine.
        """
        tool = self.get(name)
        start = time.time()

        try:
            result = tool.executor(args)
            elapsed = (time.time() - start) * 1000
            cost = tool.cost_per_call_usd

            self._invocation_count[name] += 1
            self._total_cost_usd += cost

            logger.debug(f"Tool '{name}' succeeded in {elapsed:.1f}ms")
            return ToolResult(
                tool_name=name,
                success=True,
                result=result,
                execution_time_ms=elapsed,
                cost_usd=cost,
                metadata={"invocation_count": self._invocation_count[name]},
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"Tool '{name}' failed: {e}")
            return ToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=elapsed,
            )

    def get_stats(self) -> dict:
        """Stats for Telemetry Engine."""
        return {
            "total_tools": len(self._tools),
            "invocations": dict(self._invocation_count),
            "total_cost_usd": round(self._total_cost_usd, 6),
        }
