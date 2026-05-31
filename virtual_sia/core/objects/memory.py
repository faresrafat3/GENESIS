from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .base import BaseObject, make_id
from .scope import Scope


@dataclass(slots=True)
class MemoryUnit(BaseObject):
    memory_type: str = "episodic"
    content_type: str = "episode_summary"
    content_ref: Optional[str] = None
    summary: str = ""
    scope: Scope = field(default_factory=Scope)
    utility_score: Optional[float] = None
    staleness_score: Optional[float] = None
    salience: Optional[float] = None
    identity_relevance: str = "low"
    ownership: str = "task-derived"
    linked_objects: List[str] = field(default_factory=list)
    last_used_at: Optional[datetime] = None
    decay_score: float = 1.0
    last_accessed: int = 0
    access_count: int = 0
    memory_status: str = "active"

    @classmethod
    def create(cls, summary: str, memory_type: str = "episodic") -> "MemoryUnit":
        return cls(
            id=make_id("mem"),
            object_type="memory",
            memory_type=memory_type,
            summary=summary,
        )
