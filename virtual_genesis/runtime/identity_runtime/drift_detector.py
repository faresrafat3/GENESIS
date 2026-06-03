from __future__ import annotations

from typing import List


def _tokenize(text: str) -> set[str]:
    return {t.strip('.,:;!?()[]{}').lower() for t in text.split() if t.strip()}


def measure_drift(current_behavior: List[str], commitments: List[str]) -> float:
    """Measure drift between current behavior descriptions and commitments.

    Returns 0.0 (fully aligned) to 1.0 (fully drifted).
    """
    if not commitments:
        return 0.0

    commitment_tokens: set[str] = set()
    for c in commitments:
        commitment_tokens |= _tokenize(c)

    behavior_tokens: set[str] = set()
    for b in current_behavior:
        behavior_tokens |= _tokenize(b)

    if not behavior_tokens:
        return 1.0

    overlap = len(commitment_tokens & behavior_tokens) / max(len(commitment_tokens), 1)
    return 1.0 - overlap
