from __future__ import annotations

from typing import Dict, List


class CommitmentLedger:
    def __init__(self) -> None:
        self.active_commitments: List[str] = []
        self.violations: List[Dict] = []
        self.evolutions: List[Dict] = []

    def add_commitment(self, text: str) -> None:
        self.active_commitments.append(text)

    def record_violation(self, commitment: str, decision: str, reason: str) -> None:
        self.violations.append({
            "commitment": commitment,
            "decision": decision,
            "reason": reason,
        })

    def evolve_commitment(self, old: str, new: str, reason: str) -> None:
        if old in self.active_commitments:
            self.active_commitments.remove(old)
        self.active_commitments.append(new)
        self.evolutions.append({
            "old_commitment": old,
            "new_commitment": new,
            "reason": reason,
        })

    def get_active(self) -> List[str]:
        return list(self.active_commitments)

    def get_violations(self) -> List[Dict]:
        return list(self.violations)

    def get_violation_count(self) -> int:
        return len(self.violations)
