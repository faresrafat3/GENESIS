from __future__ import annotations

from typing import Dict

from ...core.objects.memory import MemoryUnit


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._items: Dict[str, MemoryUnit] = {}
        self._tick: int = 0

    def store_memory(self, unit: MemoryUnit) -> MemoryUnit:
        self._tick += 1
        unit.last_accessed = self._tick
        self._items[unit.id] = unit
        return unit

    def get(self, memory_id: str) -> MemoryUnit | None:
        return self._items.get(memory_id)

    def all(self) -> list[MemoryUnit]:
        return list(self._items.values())

    def apply_decay(self, decay_rate: float = 0.05) -> None:
        """Reduce decay_score for all active memories based on staleness."""
        for mem in self._items.values():
            if mem.memory_status != "active":
                continue
            staleness = (self._tick - mem.last_accessed) * decay_rate
            mem.decay_score = max(0.0, min(1.0, mem.decay_score - staleness))

    def archive_memory(self, memory_id: str) -> None:
        """Set memory_status to 'archived'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "archived"

    def deprecate_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deprecated'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "deprecated"

    def delete_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deleted'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "deleted"

    def get_active_memories(self) -> list[MemoryUnit]:
        """Return only memories with status 'active'."""
        return [m for m in self._items.values() if m.memory_status == "active"]

    def record_access(self, memory_id: str, tick: int | None = None) -> None:
        """Update last_accessed and increment access_count."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.last_accessed = tick if tick is not None else self._tick
            mem.access_count += 1
