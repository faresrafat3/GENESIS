"""Tests for the Virtual-SIA production API."""
from __future__ import annotations

import json
import threading
import time
import urllib.request
import urllib.error


class TestAPI:
    """Integration tests for the SIA HTTP API server."""

    @classmethod
    def setup_class(cls):
        from virtual_sia.api.app import create_app
        from virtual_sia.api.config import APIConfig

        config = APIConfig()
        config.port = 0  # Let OS assign port
        cls.server = create_app(config)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(0.1)

    @classmethod
    def teardown_class(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)

    def _url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _get(self, path: str) -> tuple[int, dict]:
        req = urllib.request.Request(self._url(path))
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def _post(self, path: str, data: dict | None = None) -> tuple[int, dict]:
        body = json.dumps(data or {}).encode("utf-8")
        req = urllib.request.Request(
            self._url(path),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_health_endpoint(self):
        status, data = self._get("/health")
        assert status == 200
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"

    def test_session_start(self):
        status, data = self._post("/session/start")
        assert status == 200
        assert "session_id" in data
        assert "created_at" in data
        assert len(data["session_id"]) > 0

    def test_session_end(self):
        _, start_data = self._post("/session/start")
        session_id = start_data["session_id"]
        status, data = self._post("/session/end", {"session_id": session_id})
        assert status == 200
        assert data["state"] == "closed"
        assert data["session_id"] == session_id

    def test_task_submission(self):
        status, data = self._post("/task", {"text": "What is 2+2?"})
        assert status == 200
        assert "task_family" in data
        assert "good_enough" in data
        assert "tier_used" in data

    def test_task_with_session(self):
        # Start session
        _, start_data = self._post("/session/start")
        session_id = start_data["session_id"]

        # Submit task with session
        status, task_data = self._post("/task", {
            "text": "Analyze this concept",
            "session_id": session_id,
        })
        assert status == 200
        assert task_data["session_id"] == session_id

        # End session
        _, end_data = self._post("/session/end", {"session_id": session_id})
        assert end_data["task_count"] == 1
        assert end_data["state"] == "closed"

    def test_status_endpoint(self):
        status, data = self._get("/status")
        assert status == 200
        assert "active_sessions" in data
        assert "total_sessions" in data
        assert "total_tasks_processed" in data

    def test_mock_llm_adapter(self):
        import os
        from unittest.mock import patch
        from virtual_sia.api.llm_adapter import LLMAdapter

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            adapter = LLMAdapter()  # No API key
            result = adapter.generate("Hello world, this is a test prompt")
            assert isinstance(result, str)
            assert "Mock response for:" in result
            assert "Hello world" in result

    def test_llm_adapter_deterministic(self):
        import os
        from unittest.mock import patch
        from virtual_sia.api.llm_adapter import LLMAdapter

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            adapter = LLMAdapter()
            prompt = "Deterministic test prompt for consistency check"
            result1 = adapter.generate(prompt)
            result2 = adapter.generate(prompt)
            assert result1 == result2
