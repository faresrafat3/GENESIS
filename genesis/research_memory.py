#!/usr/bin/env python3
"""
GENESIS Research Memory Module — Phase 4: Cross-Run Knowledge Accumulation
Inspired by ByteDance's "AutoResearch-2" (May 2026)

A persistent, searchable memory that accumulates across GENESIS runs:
- Past experiments and their results
- Successful agent patterns
- Discovered failure modes and fixes
- Cross-task concept reuse

This enables GENESIS to IMPROVE ACROSS RUNS — not just within a single run.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class ResearchEntry:
    """A single entry in the research memory."""
    id: str
    timestamp: str
    run_id: str
    generation: int
    entry_type: str  # "experiment", "pattern", "failure", "concept", "insight"
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    success: bool = False
    score: float = 0.0  # normalized 0-1


@dataclass
class ResearchMemory:
    """Persistent cross-run research memory."""
    entries: List[ResearchEntry] = field(default_factory=list)
    total_runs: int = 0
    total_experiments: int = 0
    successful_patterns: List[str] = field(default_factory=list)
    known_failures: List[str] = field(default_factory=list)
    concepts_catalog: Dict[str, int] = field(default_factory=dict)  # concept → use count


# ── Memory Store ────────────────────────────────────────────────────────────

class ResearchMemoryStore:
    """Persistent store for cross-run research memory."""
    
    def __init__(self, storage_path: str | None = None):
        if storage_path is None:
            storage_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "research_memory.json"
            )
        self.storage_path = storage_path
        self.memory = self._load()
    
    def _load(self) -> ResearchMemory:
        """Load memory from disk or create new."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                entries = [ResearchEntry(**e) for e in data.get("entries", [])]
                mem = ResearchMemory(
                    entries=entries,
                    total_runs=data.get("total_runs", 0),
                    total_experiments=data.get("total_experiments", 0),
                    successful_patterns=data.get("successful_patterns", []),
                    known_failures=data.get("known_failures", []),
                    concepts_catalog=data.get("concepts_catalog", {}),
                )
                return mem
            except Exception:
                pass
        return ResearchMemory()
    
    def _save(self):
        """Persist memory to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump({
                "entries": [asdict(e) for e in self.memory.entries],
                "total_runs": self.memory.total_runs,
                "total_experiments": self.memory.total_experiments,
                "successful_patterns": self.memory.successful_patterns,
                "known_failures": self.memory.known_failures,
                "concepts_catalog": self.memory.concepts_catalog,
            }, f, indent=2, ensure_ascii=False)
    
    def add_entry(
        self,
        run_id: str,
        generation: int,
        entry_type: str,
        summary: str,
        details: Dict[str, Any] | None = None,
        tags: List[str] | None = None,
        success: bool = False,
        score: float = 0.0,
    ) -> ResearchEntry:
        """Add a research entry to memory."""
        entry = ResearchEntry(
            id=f"entry_{int(time.time() * 1000)}_{len(self.memory.entries)}",
            timestamp=datetime.now().isoformat(),
            run_id=run_id,
            generation=generation,
            entry_type=entry_type,
            summary=summary,
            details=details or {},
            tags=tags or [],
            success=success,
            score=score,
        )
        self.memory.entries.append(entry)
        self.memory.total_experiments += 1
        
        # Update catalogs
        if success and summary not in self.memory.successful_patterns:
            self.memory.successful_patterns.append(summary)
        if not success and summary not in self.memory.known_failures:
            self.memory.known_failures.append(summary)
        
        self._save()
        return entry
    
    def record_run_completion(
        self,
        run_id: str,
        total_generations: int,
        best_score: float,
        improvements: List[str] | None = None,
    ):
        """Record completion of a full GENESIS run."""
        self.memory.total_runs += 1
        
        self.add_entry(
            run_id=run_id,
            generation=total_generations,
            entry_type="experiment",
            summary=f"GENESIS Run {run_id} completed: {total_generations} generations, best score {best_score:.1%}",
            details={
                "total_generations": total_generations,
                "best_score": best_score,
                "improvements": improvements or [],
            },
            success=best_score >= 0.7,
            score=best_score,
        )
    
    def search(
        self,
        query: str = "",
        entry_type: str | None = None,
        min_score: float = 0.0,
        success_only: bool = False,
        max_results: int = 10,
    ) -> List[ResearchEntry]:
        """Search research memory with simple keyword matching."""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory.entries:
            # Filter by type
            if entry_type and entry.entry_type != entry_type:
                continue
            # Filter by score
            if entry.score < min_score:
                continue
            # Filter by success
            if success_only and not entry.success:
                continue
            # Keyword match
            if query_lower:
                searchable = entry.summary.lower() + " " + " ".join(entry.tags).lower()
                if query_lower not in searchable:
                    continue
            results.append(entry)
        
        # Sort by score descending
        results.sort(key=lambda e: e.score, reverse=True)
        return results[:max_results]
    
    def get_insights_for_task(self, task_text: str, max_insights: int = 5) -> str:
        """Get relevant insights from research memory for a new task."""
        # Extract keywords from task
        keywords = task_text.lower().split()[:20]
        
        insights = []
        for kw in keywords:
            matches = self.search(query=kw, max_results=2)
            for m in matches:
                if m.summary not in [i.summary for i in insights]:
                    insights.append(m)
        
        if not insights:
            return "No relevant research memory found."
        
        # Format insights
        parts = ["## Research Memory Insights\n"]
        for i, entry in enumerate(insights[:max_insights]):
            icon = "✅" if entry.success else "❌"
            parts.append(f"{icon} **{entry.entry_type}**: {entry.summary}")
            if entry.tags:
                parts.append(f"   Tags: {', '.join(entry.tags)}")
        
        return "\n".join(parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get research memory statistics."""
        return {
            "total_runs": self.memory.total_runs,
            "total_experiments": self.memory.total_experiments,
            "successful_patterns": len(self.memory.successful_patterns),
            "known_failures": len(self.memory.known_failures),
            "concepts": len(self.memory.concepts_catalog),
            "success_rate": (
                sum(1 for e in self.memory.entries if e.success) / max(len(self.memory.entries), 1)
            ),
            "avg_score": (
                sum(e.score for e in self.memory.entries) / max(len(self.memory.entries), 1)
            ),
        }


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GENESIS Research Memory")
    parser.add_argument("--add", action="store_true", help="Add an entry")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    parser.add_argument("--run-id", type=str, default="test", help="Run ID")
    parser.add_argument("--gen", type=int, default=1, help="Generation")
    parser.add_argument("--type", type=str, default="insight", help="Entry type")
    parser.add_argument("--summary", type=str, default="", help="Summary")
    parser.add_argument("--success", action="store_true", help="Was it successful?")
    parser.add_argument("--score", type=float, default=0.5, help="Score (0-1)")
    
    args = parser.parse_args()
    store = ResearchMemoryStore()
    
    if args.add:
        entry = store.add_entry(
            run_id=args.run_id,
            generation=args.gen,
            entry_type=args.type,
            summary=args.summary or f"Test entry for {args.run_id}",
            success=args.success,
            score=args.score,
        )
        print(f"Added: {entry.id}")
    
    elif args.search:
        results = store.search(query=args.search)
        for r in results:
            print(f"[{r.entry_type}] {r.summary} (score: {r.score:.2f})")
    
    elif args.stats:
        stats = store.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        # Demo
        store.add_entry("demo", 1, "pattern", "Using sys.executable consistently avoids venv issues", 
                       tags=["python", "subprocess", "fix"], success=True, score=0.95)
        store.add_entry("demo", 1, "failure", "IsADirectoryError when reading directory as file",
                       tags=["io", "bug", "fix-applied"], success=False, score=0.3)
        
        results = store.search(query="executable")
        print(f"Found {len(results)} results for 'executable'")
        for r in results:
            print(f"  {r.summary}")
        
        stats = store.get_stats()
        print(f"\nStats: {stats['total_experiments']} experiments, {stats['success_rate']:.0%} success rate")