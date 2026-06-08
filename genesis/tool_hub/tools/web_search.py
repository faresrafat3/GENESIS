"""
GENESIS Tool Hub — Web Search Tool
====================================
Component: TOOL_HUB.tools.web_search
Wraps: genesis/tools/web_search.py (backward compatible — never delete original)

Source: DeepResearcher + A-RAG + SAGE + Rulers (see original for full credits)
Genesis Role: Provides real-time web grounding for agents — fixes hallucination problem

This file registers the web_search tool in TOOL_HUB.
The actual implementation is in genesis/tools/web_search.py.

Called by: genesis/tool_hub/__init__.py (auto-registration)
"""

from __future__ import annotations

import os

from genesis.tool_hub.registry import ToolSpec

# ─── Import the actual implementation (backward compatible) ────────────────────
from genesis.tools.web_search import (  # noqa: F401 (re-export)
    web_search as _web_search_impl,
    extract_keywords as _extract_keywords_impl,
    multi_query_search as _multi_query_search_impl,
    EvidenceLog,
    SearchResult,
)


def _execute_web_search(args: dict) -> dict:
    """
    Executor for web_search tool.
    Args: {query: str, mode: str = "quick", num_results: int = 10}
    Returns: {results: list[dict], count: int}
    """
    query = args.get("query", "")
    mode = args.get("mode", "quick")
    num_results = args.get("num_results", 10)

    if not query:
        return {"error": "query is required", "results": [], "count": 0}

    results = _web_search_impl(query, mode=mode, num_results=num_results)
    return {
        "results": [r.to_dict() for r in results],
        "count": len(results),
        "query": query,
        "mode": mode,
    }


def _execute_extract_keywords(args: dict) -> dict:
    """
    Executor for extract_keywords tool.
    Args: {query: str}
    Returns: {keywords: list[str]}
    """
    query = args.get("query", "")
    keywords = _extract_keywords_impl(query, llm_client=None)
    return {"keywords": keywords, "query": query}


def _execute_multi_query_search(args: dict) -> dict:
    """
    Executor for multi_query_search tool.
    Args: {queries: list[str], mode: str = "quick"}
    Returns: {results: list[dict], count: int}
    """
    queries = args.get("queries", [])
    mode = args.get("mode", "quick")
    num_results = args.get("num_results", 5)

    if not queries:
        return {"error": "queries list is required", "results": [], "count": 0}

    results = _multi_query_search_impl(queries, mode=mode, num_results=num_results)
    return {
        "results": [r.to_dict() for r in results],
        "count": len(results),
        "queries": queries,
    }


# ─── Tool Specifications ──────────────────────────────────────────────────────

WEB_SEARCH_TOOL = ToolSpec(
    name="web_search",
    description="Search web for real-time information. Modes: quick (snippet), deep (snippet+page), read (full URL)",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query or URL (for read mode)"},
            "mode": {"type": "string", "enum": ["quick", "deep", "read"], "default": "quick"},
            "num_results": {"type": "integer", "default": 10, "maximum": 20},
        },
        "required": ["query"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "results": {"type": "array"},
            "count": {"type": "integer"},
        },
    },
    preconditions=["SERPER_API_KEY available in env"],
    failure_modes=[
        "Rate limit (429) → retry with backoff",
        "No API key → returns empty results",
        "No results → broaden query",
    ],
    cost_per_call_usd=0.001,
    requires_sandbox=False,
    executor=_execute_web_search,
    source_project="DeepResearcher+A-RAG+SAGE+Rulers",
    genesis_role="Real-time web grounding to fix hallucination in open tasks",
)

EXTRACT_KEYWORDS_TOOL = ToolSpec(
    name="extract_keywords",
    description="Extract precise search keywords from query (SAGE: BM25 precision insight)",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
    output_schema={
        "type": "object",
        "properties": {"keywords": {"type": "array", "items": {"type": "string"}}},
    },
    preconditions=[],
    failure_modes=["Falls back to simple word split if LLM unavailable"],
    cost_per_call_usd=0.0,
    requires_sandbox=False,
    executor=_execute_extract_keywords,
    source_project="SAGE (arXiv:2602.05975)",
    genesis_role="Improve search precision — shorter queries = better BM25 results",
)

MULTI_QUERY_SEARCH_TOOL = ToolSpec(
    name="multi_query_search",
    description="Search multiple queries simultaneously (DeepResearcher pattern)",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "queries": {"type": "array", "items": {"type": "string"}},
            "mode": {"type": "string", "enum": ["quick", "deep"], "default": "quick"},
            "num_results": {"type": "integer", "default": 5},
        },
        "required": ["queries"],
    },
    output_schema={
        "type": "object",
        "properties": {"results": {"type": "array"}, "count": {"type": "integer"}},
    },
    preconditions=["SERPER_API_KEY available in env"],
    failure_modes=["Rate limit on multiple queries → delays"],
    cost_per_call_usd=0.001,
    requires_sandbox=False,
    executor=_execute_multi_query_search,
    source_project="DeepResearcher (arXiv:2504.03160)",
    genesis_role="Search multiple sub-goals simultaneously for efficiency",
)

# List of all tools in this module (auto-registered by __init__.py)
ALL_TOOLS = [WEB_SEARCH_TOOL, EXTRACT_KEYWORDS_TOOL, MULTI_QUERY_SEARCH_TOOL]
