from __future__ import annotations

from enum import Enum


class ObjectStatus(str, Enum):
    PROPOSED = "proposed"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    ACTIVE = "active"
    CONTESTED = "contested"
    REVISED = "revised"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class BlackboardState(str, Enum):
    INITIALIZED = "initialized"
    CONTEXTUALIZED = "contextualized"
    ORIENTED = "oriented"
    DELIBERATING = "deliberating"
    VERIFYING = "verifying"
    RESOLVING_CONFLICTS = "resolving_conflicts"
    FINALIZING = "finalizing"
    CLOSED = "closed"
    ARCHIVED = "archived"


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    STRATEGIC = "strategic"
    PROCEDURAL = "procedural"
    ANOMALY = "anomaly"
    NEGATIVE = "negative"
    ARCHIVED = "archived"


class Tier(str, Enum):
    TIER_0 = "tier_0"
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class TaskFamily(str, Enum):
    """Informational enum documenting valid task families.

    The runtime uses string-based classification (FAMILY_KEYWORDS in service.py),
    but this enum provides a canonical reference of supported families.
    """
    COMPARISON = "comparison"
    SYNTHESIS = "synthesis"
    PROCEDURE = "procedure"
    ANALYSIS = "analysis"
    EXTRACTION = "extraction"
    PLANNING = "planning"
    UNKNOWN = "unknown"
