from __future__ import annotations

from typing import Dict, List

from ...core.objects.theory import LocalTheoryObject


class InMemoryTheoryRegistry:
    def __init__(self) -> None:
        self._theories: Dict[str, LocalTheoryObject] = {}
        self._name_index: Dict[str, str] = {}

    def add_theory(self, theory: LocalTheoryObject) -> LocalTheoryObject:
        existing_id = self._name_index.get(theory.name)
        if existing_id:
            return self._theories[existing_id]
        self._theories[theory.id] = theory
        self._name_index[theory.name] = theory.id
        return theory

    def list_theories(self) -> List[LocalTheoryObject]:
        return list(self._theories.values())
