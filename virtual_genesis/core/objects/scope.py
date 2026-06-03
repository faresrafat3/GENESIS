from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class Scope:
    task_families: List[str] = field(default_factory=list)
    positive_conditions: List[str] = field(default_factory=list)
    negative_conditions: List[str] = field(default_factory=list)
    ambiguity_zone: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
