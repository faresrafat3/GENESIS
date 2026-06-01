from __future__ import annotations

from typing import Dict, List
from collections import defaultdict

from ...core.objects.memory import MemoryUnit


class InMemoryMemoryStore:
    def __init__(self) -> None:
        self._items: Dict[str, MemoryUnit] = {}
        self._tick: int = 0
        self._last_decay_tick: int = -1
        # Memory clusters for consolidation support
        self._family_clusters: Dict[str, List[str]] = defaultdict(list)
        self._type_clusters: Dict[str, List[str]] = defaultdict(list)

    def store_memory(self, unit: MemoryUnit) -> MemoryUnit:
        self._tick += 1
        unit.last_accessed = self._tick
        self._items[unit.id] = unit
        # Update clusters
        self._update_clusters(unit)
        return unit

    def _update_clusters(self, unit: MemoryUnit) -> None:
        """Update clustering indices for memory unit."""
        # Remove from old clusters if exists
        self._remove_from_clusters(unit.id)
        # Add to new clusters
        for family in unit.scope.task_families:
            self._family_clusters[family].append(unit.id)
        self._type_clusters[unit.memory_type].append(unit.id)

    def _remove_from_clusters(self, memory_id: str) -> None:
        """Remove memory from all cluster indices."""
        mem = self._items.get(memory_id)
        if mem:
            for family in mem.scope.task_families:
                if family in self._family_clusters and memory_id in self._family_clusters[family]:
                    self._family_clusters[family].remove(memory_id)
            if mem.memory_type in self._type_clusters and memory_id in self._type_clusters[mem.memory_type]:
                self._type_clusters[mem.memory_type].remove(memory_id)

    def get(self, memory_id: str) -> MemoryUnit | None:
        return self._items.get(memory_id)

    def all(self) -> list[MemoryUnit]:
        return list(self._items.values())

    def count(self) -> int:
        """Return total number of stored memories (all statuses)."""
        return len(self._items)

    def active_count(self) -> int:
        """Return number of active memories."""
        return sum(1 for m in self._items.values() if m.memory_status == "active")

    def apply_decay(self, decay_rate: float = 0.05) -> None:
        """Reduce decay_score for all active memories based on staleness.
        
        Skips if already applied at the current tick to prevent compounding.
        """
        if self._tick == self._last_decay_tick:
            return
        for mem in self._items.values():
            if mem.memory_status != "active":
                continue
            staleness = (self._tick - mem.last_accessed) * decay_rate
            mem.decay_score = max(0.0, min(1.0, mem.decay_score - staleness))
        self._last_decay_tick = self._tick

    def archive_memory(self, memory_id: str) -> None:
        """Set memory_status to 'archived'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "archived"
            self._remove_from_clusters(memory_id)

    def deprecate_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deprecated'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "deprecated"
            self._remove_from_clusters(memory_id)

    def delete_memory(self, memory_id: str) -> None:
        """Set memory_status to 'deleted'."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.memory_status = "deleted"
            self._remove_from_clusters(memory_id)

    def get_active_memories(self) -> list[MemoryUnit]:
        """Return only memories with status 'active'."""
        return [m for m in self._items.values() if m.memory_status == "active"]

    def get_by_type(self, memory_type: str, active_only: bool = True) -> list[MemoryUnit]:
        """Return memories filtered by type.

        Parameters
        ----------
        memory_type : str
            One of 'episodic', 'semantic', 'procedural', 'negative'.
        active_only : bool
            If True, return only active memories.
        """
        items = self._items.values()
        if active_only:
            items = (m for m in items if m.memory_status == "active")
        return [m for m in items if m.memory_type == memory_type]

    def get_by_family(self, family: str, active_only: bool = True) -> list[MemoryUnit]:
        """Return memories for a specific task family."""
        if active_only:
            memory_ids = self._family_clusters.get(family, [])
            return [self._items[mid] for mid in memory_ids 
                   if self._items[mid].memory_status == "active"]
        else:
            return [m for m in self._items.values() 
                   if family in m.scope.task_families]

    def get_cluster_size(self, family: str = None, memory_type: str = None) -> int:
        """Get size of a memory cluster by family or type."""
        if family:
            return len(self._family_clusters.get(family, []))
        elif memory_type:
            return len(self._type_clusters.get(memory_type, []))
        return 0

    def record_access(self, memory_id: str, tick: int | None = None) -> None:
        """Update last_accessed and increment access_count."""
        mem = self._items.get(memory_id)
        if mem is not None:
            mem.last_accessed = tick if tick is not None else self._tick
            mem.access_count += 1

    def find_similar(
        self,
        target: MemoryUnit,
        same_family: bool = True,
        same_type: bool = True,
        active_only: bool = True,
    ) -> list[MemoryUnit]:
        """Find memories similar to *target* for consolidation candidates.

        Similarity is defined by overlapping task families and/or matching
        memory type.  This is intentionally lightweight (no embedding) to
        keep the consolidation pass fast.

        Parameters
        ----------
        target : MemoryUnit
            The reference memory to compare against.
        same_family : bool
            Require at least one overlapping task family.
        same_type : bool
            Require matching memory_type.
        active_only : bool
            If True, only consider active memories.
        """
        result: list[MemoryUnit] = []
        target_families = set(target.scope.task_families)

        for mem in self._items.values():
            if mem.id == target.id:
                continue
            if active_only and mem.memory_status != "active":
                continue
            if same_type and mem.memory_type != target.memory_type:
                continue
            if same_family and target_families:
                if not target_families.intersection(mem.scope.task_families):
                    continue
            result.append(mem)

        return result

    def find_similar_with_utility(
        self,
        target: MemoryUnit,
        utility_scores: Dict[str, float],
        same_family: bool = True,
        same_type: bool = True,
        active_only: bool = True,
        limit: int = 5,
    ) -> list[MemoryUnit]:
        """Find similar memories prioritized by utility score."""
        similar = self.find_similar(target, same_family, same_type, active_only)
        # Sort by utility score (highest first)
        similar.sort(key=lambda m: utility_scores.get(m.id, 0.0), reverse=True)
        return similar[:limit]

    def boost_salience(self, memory_id: str, amount: float = 0.1) -> None:
        """Increase salience of a memory (e.g. after repeated failure on same topic)."""
        mem = self._items.get(memory_id)
        if mem is not None:
            current = mem.salience if mem.salience is not None else 0.5
            mem.salience = min(1.0, current + amount)

    def get_memories_for_consolidation(
        self,
        family: str = None,
        memory_type: str = None,
        min_cluster_size: int = 2,
    ) -> list[List[MemoryUnit]]:
        """Get groups of memories that could be consolidated."""
        clusters = []
        
        if family:
            cluster_ids = self._family_clusters.get(family, [])
            if len(cluster_ids) >= min_cluster_size:
                cluster = [self._items[mid] for mid in cluster_ids 
                          if self._items[mid].memory_status == "active"]
                if len(cluster) >= min_cluster_size:
                    clusters.append(cluster)
        elif memory_type:
            cluster_ids = self._type_clusters.get(memory_type, [])
            if len(cluster_ids) >= min_cluster_size:
                cluster = [self._items[mid] for mid in cluster_ids 
                          if self._items[mid].memory_status == "active"]
                if len(cluster) >= min_cluster_size:
                    clusters.append(cluster)
        else:
            # Get all clusters that meet minimum size
            for fam, ids in self._family_clusters.items():
                if len(ids) >= min_cluster_size:
                    cluster = [self._items[mid] for mid in ids 
                              if self._items[mid].memory_status == "active"]
                    if len(cluster) >= min_cluster_size:
                        clusters.append(cluster)
        
        return clusters

    def update_clusters_for_existing_memories(self) -> None:
        """Rebuild cluster indices for all existing memories."""
        self._family_clusters.clear()
        self._type_clusters.clear()
        for mem in self._items.values():
            for family in mem.scope.task_families:
                self._family_clusters[family].append(mem.id)
            self._type_clusters[mem.memory_type].append(mem.id)