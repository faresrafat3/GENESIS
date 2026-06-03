from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Provenance:
    source_kind: str
    timestamp: datetime = field(default_factory=utc_now)
    source_id: Optional[str] = None
    source_ref: Optional[str] = None
    generated_by_run_id: Optional[str] = None
    notes: Optional[str] = None
