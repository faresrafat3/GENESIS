"""Virtual-GENESIS Production API server using stdlib http.server."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .config import APIConfig
from .llm_adapter import LLMAdapter
from .session import SessionManager
from ..runtime.pipeline.minimal_run import run_minimal_pipeline


class SIAHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the GENESIS API."""

    def log_message(self, format, *args):
        """Suppress default stderr logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/status":
            self._handle_status()
        else:
            self._send_json(404, {"error": "not_found", "path": self.path})

    def do_POST(self) -> None:
        """Handle POST requests."""
        if self.path == "/task":
            self._handle_task()
        elif self.path == "/session/start":
            self._handle_session_start()
        elif self.path == "/session/end":
            self._handle_session_end()
        else:
            self._send_json(404, {"error": "not_found", "path": self.path})

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _handle_health(self) -> None:
        self._send_json(200, {"status": "ok", "version": "0.1.0"})

    def _handle_status(self) -> None:
        manager = self.server.session_manager
        with self.server.tasks_lock:
            total = self.server.total_tasks_processed
        self._send_json(200, {
            "active_sessions": len(manager.list_active()),
            "total_sessions": len(manager.sessions),
            "total_tasks_processed": total,
        })

    def _handle_session_start(self) -> None:
        manager = self.server.session_manager
        session = manager.create_session()
        self._send_json(200, {
            "session_id": session.id,
            "created_at": session.created_at,
        })

    def _handle_session_end(self) -> None:
        body = self._read_body()
        if body is None:
            self._send_json(400, {"error": "invalid_json"})
            return
        session_id = body.get("session_id")
        if not session_id:
            self._send_json(400, {"error": "missing_session_id"})
            return
        manager = self.server.session_manager
        result = manager.end_session(session_id)
        if "error" in result:
            self._send_json(404, result)
        else:
            self._send_json(200, result)

    def _handle_task(self) -> None:
        body = self._read_body()
        if body is None:
            self._send_json(400, {"error": "invalid_json"})
            return
        text = body.get("text")
        if not text:
            self._send_json(400, {"error": "missing_text"})
            return

        session_id = body.get("session_id")
        governance_flags = body.get("governance_flags", self.server.config.governance_flags)

        manager = self.server.session_manager
        session = None
        if session_id:
            session = manager.get_session(session_id)
            if session is None:
                self._send_json(404, {"error": "session_not_found", "session_id": session_id})
                return
            # Reject tasks on non-active sessions
            if session.state != "active":
                self._send_json(409, {"error": "session_not_active"})
                return

        # Use session stores or create ephemeral ones
        if session:
            store = session.memory_store
            concept_registry = session.concept_registry
            theory_registry = session.theory_registry
            ledger_store = session.ledger_store
            identity = session.identity
        else:
            from ..runtime.memory_os.store import InMemoryMemoryStore
            from ..runtime.concept_engine.registry import InMemoryConceptRegistry
            from ..runtime.theory_runtime.registry import InMemoryTheoryRegistry
            from ..runtime.economy_control.ledger import InMemoryLedgerStore
            from ..core.objects.identity import AgentIdentityObject
            store = InMemoryMemoryStore()
            concept_registry = InMemoryConceptRegistry()
            theory_registry = InMemoryTheoryRegistry()
            ledger_store = InMemoryLedgerStore()
            identity = AgentIdentityObject.create(
                commitments=["accuracy"],
                self_model={"type": "ephemeral"},
            )

        # Run the pipeline
        result = run_minimal_pipeline(
            raw_task=text,
            store=store,
            ledger_store=ledger_store,
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_memory=True,
            use_economy=True,
            use_concepts=True,
            use_anomaly_leverage=governance_flags.get("use_anomaly_leverage", False),
            use_theory_leverage=governance_flags.get("use_theory_leverage", False),
            use_productive_forgetting=governance_flags.get("use_productive_forgetting", False),
            use_identity_governance=governance_flags.get("use_identity_governance", False),
            use_paradigm_fork=governance_flags.get("use_paradigm_fork", False),
            identity=identity,
        )

        with self.server.tasks_lock:
            self.server.total_tasks_processed += 1
        if session:
            session.task_count += 1

        # Generate LLM response if adapter is available
        llm_response = None
        adapter = self.server.llm_adapter
        if adapter is not None:
            llm_response = adapter.generate(text)

        # Build response summary
        response_data = {
            "task_family": result["task"]["task_family"],
            "good_enough": result["blackboard"]["verification_state"]["verification_summary"]["good_enough"],
            "tier_used": result["tier_decision"]["chosen_tier"],
            "concept_count": result["concept_count"],
            "anomaly_severity": result["anomaly_severity"],
            "session_id": session_id,
            "llm_response": llm_response,
        }
        self._send_json(200, response_data)

    def _send_json(self, status_code: int, data: dict) -> None:
        """Send a JSON response with CORS headers."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict | None:
        """Read and parse JSON request body."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                return {}
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            return None


class SIAServer(HTTPServer):
    """Custom HTTP server with session manager and config."""

    def __init__(self, config: APIConfig, llm_adapter: LLMAdapter | None = None) -> None:
        self.config = config
        self.session_manager = SessionManager()
        self.llm_adapter = llm_adapter or LLMAdapter()
        self.total_tasks_processed = 0
        self.tasks_lock = threading.Lock()
        super().__init__((config.host, config.port), SIAHandler)


def create_app(config: APIConfig | None = None) -> SIAServer:
    """Create and return a configured GENESIS server instance."""
    if config is None:
        config = APIConfig()
    llm_adapter = LLMAdapter()
    return SIAServer(config, llm_adapter)
