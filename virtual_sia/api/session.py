"""Session management for Virtual-SIA production API."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..core.objects.identity import AgentIdentityObject
from ..runtime.concept_engine.registry import InMemoryConceptRegistry
from ..runtime.economy_control.ledger import InMemoryLedgerStore
from ..runtime.memory_os.forgetting_policy import apply_forgetting_policy
from ..runtime.memory_os.store import InMemoryMemoryStore
from ..runtime.theory_runtime.registry import InMemoryTheoryRegistry


class Session:
    """Represents a single user session with isolated state."""

    def __init__(self) -> None:
        self.id: str = str(uuid.uuid4())
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.state: str = "active"
        self.memory_store: InMemoryMemoryStore = InMemoryMemoryStore()
        self.concept_registry: InMemoryConceptRegistry = InMemoryConceptRegistry()
        self.theory_registry: InMemoryTheoryRegistry = InMemoryTheoryRegistry()
        self.ledger_store: InMemoryLedgerStore = InMemoryLedgerStore()
        self.identity: AgentIdentityObject = AgentIdentityObject.create(
            commitments=["accuracy", "coherence", "ethical_alignment"],
            self_model={"version": "0.1.0", "type": "production_session"},
        )
        self.task_count: int = 0


class SessionManager:
    """Manages session lifecycle: create, get, end."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    def create_session(self) -> Session:
        """Create a new active session."""
        session = Session()
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Retrieve a session by ID."""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> dict:
        """End a session: apply forgetting policy and consolidate."""
        session = self.sessions.get(session_id)
        if session is None:
            return {"error": "session_not_found", "session_id": session_id}

        session.state = "consolidating"

        # Apply forgetting policy for consolidation
        forgetting_report = None
        active_memories = session.memory_store.get_active_memories()
        if len(active_memories) > 0:
            forgetting_report = apply_forgetting_policy(session.memory_store)

        session.state = "closed"

        return {
            "session_id": session.id,
            "state": "closed",
            "task_count": session.task_count,
            "forgetting_report": forgetting_report,
            "total_memories": len(session.memory_store.all()),
            "total_concepts": len(session.concept_registry.list_concepts()),
            "total_theories": len(session.theory_registry.list_theories()),
        }

    def list_active(self) -> list[str]:
        """Return IDs of all active sessions."""
        return [sid for sid, s in self.sessions.items() if s.state == "active"]
