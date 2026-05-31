"""API configuration for Virtual-SIA production server."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class APIConfig:
    """Configuration for the SIA production API server."""

    model_mapping: Dict[str, str] = field(default_factory=lambda: {
        "tier_0": "nousresearch/nous-capybara-7b:free",
        "tier_1": "openai/gpt-3.5-turbo",
        "tier_2": "openai/gpt-4",
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
    host: str = "127.0.0.1"
    port: int = 8080
