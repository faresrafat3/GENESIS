"""
Tests for genesis/tool_hub/
Component: TOOL_HUB
Source: MCP + MUSE-Autoskill

Tests cover:
  - ToolSpec: creation, catalog entry, serialization
  - ToolResult: creation, to_dict
  - ToolRegistry: register, get, invoke, catalog, stats
  - SandboxExecutor: create, upload, run, download, close, pytest
  - Tool Hub public API: get_tool, invoke, catalog, shortcuts
  - Built-in tools: web_search, code_exec, llm_call (mocked)
  - Backward compat: old genesis.tools.web_search still works
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from genesis.tool_hub.registry import ToolSpec, ToolResult, ToolRegistry
from genesis.tool_hub.executor import SandboxExecutor, run_code_isolated


# ─── ToolSpec Tests ───────────────────────────────────────────────────────────

class TestToolSpec(unittest.TestCase):
    def _make(self, **kwargs) -> ToolSpec:
        defaults = dict(
            name="test_tool",
            description="A test tool that does things",
            executor=lambda args: {"result": "ok"},
        )
        defaults.update(kwargs)
        return ToolSpec(**defaults)

    def test_basic_fields(self):
        t = self._make()
        self.assertEqual(t.name, "test_tool")
        self.assertEqual(t.version, "1.0.0")
        self.assertFalse(t.requires_sandbox)
        self.assertEqual(t.cost_per_call_usd, 0.0)

    def test_catalog_entry_free(self):
        t = self._make(cost_per_call_usd=0.0)
        entry = t.get_catalog_entry()
        self.assertIn("test_tool", entry)
        self.assertIn("A test tool", entry)
        self.assertIn("free", entry)

    def test_catalog_entry_with_cost(self):
        t = self._make(cost_per_call_usd=0.001)
        entry = t.get_catalog_entry()
        self.assertIn("$0.0010", entry)

    def test_catalog_entry_sandbox(self):
        t = self._make(requires_sandbox=True)
        entry = t.get_catalog_entry()
        self.assertIn("[sandbox]", entry)

    def test_to_dict_safe_no_executor(self):
        t = self._make()
        d = t.to_dict_safe()
        self.assertNotIn("executor", d)
        self.assertIn("name", d)
        self.assertIn("description", d)
        self.assertIsInstance(d, dict)

    def test_to_dict_serializable(self):
        t = self._make(input_schema={"type": "object"})
        d = t.to_dict_safe()
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)

    def test_source_project_field(self):
        t = self._make(source_project="TestProject")
        self.assertEqual(t.source_project, "TestProject")

    def test_genesis_role_field(self):
        t = self._make(genesis_role="Used for testing purposes")
        self.assertEqual(t.genesis_role, "Used for testing purposes")


# ─── ToolResult Tests ─────────────────────────────────────────────────────────

class TestToolResult(unittest.TestCase):
    def test_success_result(self):
        r = ToolResult("test", True, {"data": 42}, execution_time_ms=15.0)
        self.assertTrue(r.success)
        self.assertIsNone(r.error)
        self.assertEqual(r.result["data"], 42)

    def test_failure_result(self):
        r = ToolResult("test", False, None, error="timeout")
        self.assertFalse(r.success)
        self.assertEqual(r.error, "timeout")

    def test_to_dict(self):
        r = ToolResult("test", True, {"x": 1}, execution_time_ms=10.0, cost_usd=0.001)
        d = r.to_dict()
        self.assertEqual(d["tool_name"], "test")
        self.assertTrue(d["success"])
        self.assertAlmostEqual(d["cost_usd"], 0.001)
        self.assertAlmostEqual(d["execution_time_ms"], 10.0)


# ─── ToolRegistry Tests ───────────────────────────────────────────────────────

class TestToolRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = ToolRegistry()
        self.tool_a = ToolSpec(
            name="tool_a", description="Tool A",
            executor=lambda args: {"result": "A_" + args.get("x", "?")}
        )
        self.tool_b = ToolSpec(
            name="tool_b", description="Tool B",
            cost_per_call_usd=0.005,
            executor=lambda args: {"value": args.get("n", 0) * 2}
        )

    def test_register_and_get(self):
        self.reg.register(self.tool_a)
        got = self.reg.get("tool_a")
        self.assertEqual(got.name, "tool_a")

    def test_get_unknown_raises(self):
        with self.assertRaises(KeyError):
            self.reg.get("nonexistent")

    def test_register_requires_executor(self):
        bad = ToolSpec(name="bad", description="no executor")
        with self.assertRaises(ValueError):
            self.reg.register(bad)

    def test_discover_returns_all(self):
        self.reg.register(self.tool_a)
        self.reg.register(self.tool_b)
        tools = self.reg.discover()
        names = [t.name for t in tools]
        self.assertIn("tool_a", names)
        self.assertIn("tool_b", names)

    def test_invoke_success(self):
        self.reg.register(self.tool_a)
        result = self.reg.invoke("tool_a", {"x": "hello"})
        self.assertTrue(result.success)
        self.assertEqual(result.result["result"], "A_hello")

    def test_invoke_failure(self):
        def failing(args): raise RuntimeError("boom")
        bad = ToolSpec(name="bad", description="fails", executor=failing)
        self.reg.register(bad)
        result = self.reg.invoke("bad", {})
        self.assertFalse(result.success)
        self.assertIn("boom", result.error)

    def test_catalog_contains_all_tools(self):
        self.reg.register(self.tool_a)
        self.reg.register(self.tool_b)
        catalog = self.reg.catalog()
        self.assertIn("tool_a", catalog)
        self.assertIn("tool_b", catalog)
        self.assertIn("Tool A", catalog)

    def test_catalog_has_cost(self):
        self.reg.register(self.tool_b)
        catalog = self.reg.catalog()
        self.assertIn("$0.0050", catalog)

    def test_catalog_yaml_format(self):
        self.reg.register(self.tool_a)
        yaml_str = self.reg.catalog_yaml()
        self.assertIn("tool_a", yaml_str)
        self.assertIn("available_tools", yaml_str)

    def test_cost_tracking(self):
        self.reg.register(self.tool_b)
        self.reg.invoke("tool_b", {"n": 5})
        self.reg.invoke("tool_b", {"n": 3})
        stats = self.reg.get_stats()
        self.assertEqual(stats["invocations"]["tool_b"], 2)
        self.assertAlmostEqual(stats["total_cost_usd"], 0.01, places=4)

    def test_stats_empty(self):
        stats = self.reg.get_stats()
        self.assertEqual(stats["total_tools"], 0)
        self.assertEqual(stats["total_cost_usd"], 0.0)

    def test_overwrite_registration(self):
        self.reg.register(self.tool_a)
        new_a = ToolSpec(
            name="tool_a", description="Updated A",
            executor=lambda args: {"result": "updated"}
        )
        self.reg.register(new_a)
        got = self.reg.get("tool_a")
        self.assertEqual(got.description, "Updated A")


# ─── SandboxExecutor Tests ────────────────────────────────────────────────────

class TestSandboxExecutor(unittest.TestCase):
    def test_create_and_close(self):
        sb = SandboxExecutor()
        sid = sb.create()
        self.assertIsNotNone(sid)
        self.assertIn(sid, sb._sandboxes)
        sb.close(sid)
        self.assertNotIn(sid, sb._sandboxes)

    def test_upload_and_download(self):
        sb = SandboxExecutor()
        sid = sb.create()
        try:
            sb.upload(sid, "test.txt", "hello world")
            content = sb.download(sid, "test.txt")
            self.assertEqual(content, "hello world")
        finally:
            sb.close(sid)

    def test_run_simple_script(self):
        sb = SandboxExecutor(timeout_sec=10)
        sid = sb.create()
        try:
            sb.upload(sid, "script.py", "print('success')")
            result = sb.run(sid, "script.py")
            self.assertTrue(result.success)
            self.assertIn("success", result.stdout)
            self.assertEqual(result.exit_code, 0)
        finally:
            sb.close(sid)

    def test_run_failing_script(self):
        sb = SandboxExecutor(timeout_sec=10)
        sid = sb.create()
        try:
            sb.upload(sid, "fail.py", "raise ValueError('test error')")
            result = sb.run(sid, "fail.py")
            self.assertFalse(result.success)
            self.assertNotEqual(result.exit_code, 0)
        finally:
            sb.close(sid)

    def test_run_timeout(self):
        sb = SandboxExecutor(timeout_sec=1)
        sid = sb.create()
        try:
            sb.upload(sid, "slow.py", "import time; time.sleep(10)")
            result = sb.run(sid, "slow.py")
            self.assertFalse(result.success)
            self.assertIn("imeout", result.stderr)
        finally:
            sb.close(sid, keep=True)  # might already be gone
            try: sb.close(sid)
            except: pass

    def test_run_nonexistent_script(self):
        sb = SandboxExecutor()
        sid = sb.create()
        try:
            result = sb.run(sid, "nonexistent.py")
            self.assertFalse(result.success)
            self.assertIn("not found", result.stderr.lower())
        finally:
            sb.close(sid)

    def test_context_manager(self):
        with SandboxExecutor() as (sid, sb):
            sb.upload(sid, "ctx.py", "print('from context')")
            result = sb.run(sid, "ctx.py")
            self.assertTrue(result.success)
        # Sandbox should be cleaned up
        self.assertNotIn(sid, sb._sandboxes)

    def test_get_path_unknown_raises(self):
        sb = SandboxExecutor()
        with self.assertRaises(KeyError):
            sb._get_path("nonexistent_sandbox")

    def test_upload_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            os.makedirs(os.path.join(tmpdir, "subdir"))
            with open(os.path.join(tmpdir, "file.txt"), "w") as f:
                f.write("test content")

            sb = SandboxExecutor()
            sid = sb.create()
            try:
                sb.upload_dir(sid, tmpdir, "uploaded")
                content = sb.download(sid, "uploaded/file.txt")
                self.assertEqual(content, "test content")
            finally:
                sb.close(sid)


class TestRunCodeIsolated(unittest.TestCase):
    def test_simple_success(self):
        result = run_code_isolated("x = 1 + 1\nprint(x)", timeout_sec=10)
        self.assertTrue(result.success)
        self.assertIn("2", result.stdout)

    def test_failure(self):
        result = run_code_isolated("raise Exception('fail')", timeout_sec=10)
        self.assertFalse(result.success)

    def test_empty_code(self):
        result = run_code_isolated("", timeout_sec=5)
        # Empty script succeeds (exit 0)
        self.assertEqual(result.exit_code, 0)


# ─── Tool Hub Public API Tests ─────────────────────────────────────────────────

class TestToolHubAPI(unittest.TestCase):
    def test_list_tools_nonempty(self):
        from genesis.tool_hub import list_tools
        tools = list_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

    def test_catalog_is_string(self):
        from genesis.tool_hub import catalog
        cat = catalog()
        self.assertIsInstance(cat, str)
        self.assertGreater(len(cat), 0)

    def test_catalog_contains_web_search(self):
        from genesis.tool_hub import catalog
        cat = catalog()
        self.assertIn("web_search", cat)

    def test_get_tool_web_search(self):
        from genesis.tool_hub import get_tool
        tool = get_tool("web_search")
        self.assertEqual(tool.name, "web_search")
        self.assertIsNotNone(tool.executor)

    def test_get_tool_unknown_raises(self):
        from genesis.tool_hub import get_tool
        with self.assertRaises(KeyError):
            get_tool("nonexistent_xyz")

    def test_register_custom_tool(self):
        from genesis.tool_hub import register_tool, get_tool, list_tools
        custom = ToolSpec(
            name="test_custom_unique_xyz",
            description="Custom test tool",
            executor=lambda args: {"custom": True}
        )
        register_tool(custom)
        tools = list_tools()
        self.assertIn("test_custom_unique_xyz", tools)
        got = get_tool("test_custom_unique_xyz")
        self.assertEqual(got.description, "Custom test tool")

    def test_invoke_returns_dict(self):
        from genesis.tool_hub import invoke, register_tool
        reg = ToolSpec(
            name="test_invoke_returns_dict",
            description="Test",
            executor=lambda args: {"answer": args.get("x", 0) * 2}
        )
        register_tool(reg)
        result = invoke("test_invoke_returns_dict", {"x": 5})
        self.assertEqual(result.get("answer"), 10)

    def test_invoke_failure_returns_error_dict(self):
        from genesis.tool_hub import invoke, register_tool
        reg = ToolSpec(
            name="test_invoke_fail_xyz",
            description="Fails",
            executor=lambda args: (_ for _ in ()).throw(RuntimeError("intentional"))
        )
        register_tool(reg)
        result = invoke("test_invoke_fail_xyz", {})
        self.assertIn("error", result)
        self.assertFalse(result.get("success", True))

    def test_get_stats(self):
        from genesis.tool_hub import get_stats
        stats = get_stats()
        self.assertIn("total_tools", stats)
        self.assertIn("total_cost_usd", stats)


# ─── Built-in Tools Tests (mocked) ───────────────────────────────────────────

class TestWebSearchToolMocked(unittest.TestCase):
    @patch("genesis.tools.web_search.httpx.post")
    def test_web_search_via_hub(self, mock_post):
        from genesis.tool_hub import invoke
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "organic": [{"title": "Test", "link": "https://example.com", "snippet": "test"}],
            "news": []
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        os.environ["SERPER_API_KEY"] = "test_key"
        result = invoke("web_search", {"query": "test query", "mode": "quick"})
        self.assertIn("results", result)
        self.assertEqual(result["count"], 1)

    def test_extract_keywords_via_hub(self):
        from genesis.tool_hub import extract_keywords
        keywords = extract_keywords("find micro task platforms Egypt payment")
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

    def test_code_exec_via_hub(self):
        from genesis.tool_hub import run_code
        result = run_code("print('tool hub works')", timeout_sec=10)
        self.assertTrue(result.get("success"))
        self.assertIn("tool hub works", result.get("stdout", ""))


# ─── Backward Compatibility Tests ────────────────────────────────────────────

class TestBackwardCompat(unittest.TestCase):
    def test_old_import_still_works(self):
        """genesis.tools.web_search must NEVER be broken."""
        from genesis.tools.web_search import web_search, EvidenceLog, SearchResult
        self.assertTrue(callable(web_search))
        self.assertTrue(hasattr(EvidenceLog, "add_claim"))

    def test_old_extract_keywords_works(self):
        from genesis.tools.web_search import extract_keywords
        kws = extract_keywords("test query platform search")
        self.assertIsInstance(kws, list)

    def test_old_multi_query_search_signature(self):
        from genesis.tools.web_search import multi_query_search
        self.assertTrue(callable(multi_query_search))


if __name__ == "__main__":
    unittest.main(verbosity=2)
