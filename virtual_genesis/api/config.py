"""API configuration for Virtual-GENESIS production server."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/owl-alpha"


@dataclass
class APIConfig:
    """Configuration for the GENESIS production API server."""

    model_mapping: Dict[str, str] = field(default_factory=lambda: {
        "tier_0": "openrouter/owl-alpha",
        "tier_1": "openrouter/owl-alpha",
        "tier_2": "openrouter/owl-alpha",
    })
    governance_flags: Dict[str, bool] = field(default_factory=lambda: {
        "use_anomaly_leverage": False,
        "use_theory_leverage": False,
        "use_productive_forgetting": False,
        "use_identity_governance": False,
        "use_paradigm_fork": False,
    })
    memory_limit: int = 100
    decay_rate: float = 0.05
    use_persistence: bool = False
    db_path: str = "./sia_data.db"
    host: str = "127.0.0.1"
    port: int = 8080
