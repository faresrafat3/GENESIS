from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...core.objects.ledger import LedgerEntry


@dataclass
class BudgetState:
    """Tracks cumulative cognitive budget consumption.

    Parameters:
        daily_budget: maximum estimated cognitive cost allowed per period.
        current_period: logical period identifier (e.g., date string).
        consumed: cumulative estimated cost consumed in current period.
    """
    daily_budget: float = 1.0
    current_period: str = "default"
    consumed: float = 0.0


class InMemoryLedgerStore:
    def __init__(self, budget_state: Optional[BudgetState] = None) -> None:
        self._entries: Dict[str, LedgerEntry] = {}
        self._budget_state = budget_state or BudgetState()

    @property
    def budget_state(self) -> BudgetState:
        return self._budget_state

    def record_cognitive_spend(self, entry: LedgerEntry) -> LedgerEntry:
        self._entries[entry.id] = entry
        cost = entry.estimated_cost or 0.0
        self._budget_state.consumed += cost
        return entry

    def all(self) -> List[LedgerEntry]:
        return list(self._entries.values())

    def check_budget(
        self,
        estimated_cost: float,
        criticality: str = "medium",
    ) -> Dict[str, Any]:
        """Check whether a new spend fits within the budget.

        High-criticality tasks are exempt from budget caps since the cost of
        failure outweighs the cognitive budget constraint.
        """
        if criticality == "high":
            return {"allowed": True, "reason": "high criticality overrides budget cap", "remaining": self.remaining()}

        remaining = self.remaining()
        allowed = remaining >= estimated_cost
        reason = "within budget" if allowed else "budget exhausted"
        return {"allowed": allowed, "reason": reason, "remaining": remaining}

    def value_aware_budget_check(
        self,
        estimated_cost: float,
        expected_gain: float,
        criticality: str = "medium",
        min_roi_threshold: float = 2.0,
    ) -> Dict[str, Any]:
        """Check budget with value-aware logic.

        Considers the expected gain vs. cost ratio. A task with high expected gain
        relative to cost is allowed even when budget is tight (but not fully exhausted),
        while low-value tasks are rejected earlier to preserve budget for better opportunities.

        High-criticality tasks always pass.
        """
        if criticality == "high":
            return {
                "allowed": True,
                "reason": "high criticality overrides budget cap",
                "remaining": self.remaining(),
                "effective_roi": float("inf"),
            }

        remaining = self.remaining()

        # Fully exhausted
        if remaining < estimated_cost:
            return {
                "allowed": False,
                "reason": "budget exhausted",
                "remaining": remaining,
                "effective_roi": 0.0,
            }

        # Compute effective ROI of this task
        effective_roi = (expected_gain / estimated_cost) if estimated_cost > 0 else float("inf")

        # If budget is getting low (< 20% remaining), only allow high-ROI tasks
        budget_ratio = remaining / self._budget_state.daily_budget if self._budget_state.daily_budget > 0 else 1.0
        if budget_ratio < 0.2 and effective_roi < min_roi_threshold:
            return {
                "allowed": False,
                "reason": f"budget low ({budget_ratio:.0%} remaining); task ROI {effective_roi:.1f}x below threshold {min_roi_threshold:.1f}x",
                "remaining": remaining,
                "effective_roi": effective_roi,
            }

        return {
            "allowed": True,
            "reason": "within budget",
            "remaining": remaining,
            "effective_roi": effective_roi,
        }

    def remaining(self) -> float:
        """Return remaining cognitive budget for the current period."""
        return max(0.0, self._budget_state.daily_budget - self._budget_state.consumed)

    def entries_for_task(self, task_ref: str) -> List[LedgerEntry]:
        """Return all ledger entries associated with a specific task."""
        return [e for e in self._entries.values() if e.task_ref == task_ref]

    def compute_roi(self) -> Dict[str, Any]:
        """Compute aggregate return-on-investment across all recorded entries.

        ROI is defined as (total estimated gain - total actual cost) / total actual cost.
        """
        entries = self.all()
        if not entries:
            return {"roi": 0.0, "total_gain": 0.0, "total_cost": 0.0, "entry_count": 0}

        total_gain = 0.0
        total_cost = 0.0
        for e in entries:
            gain = (e.estimated_immediate_gain or 0.0) + (e.estimated_reuse_gain or 0.0)
            cost = (e.actual_cost_profile.estimated_cost_usd if e.actual_cost_profile else 0.0) or (e.estimated_cost or 0.0)
            total_gain += gain
            total_cost += cost

        roi = ((total_gain - total_cost) / total_cost) if total_cost > 0 else float("inf")
        return {
            "roi": roi,
            "total_gain": total_gain,
            "total_cost": total_cost,
            "entry_count": len(entries),
        }

    def tier_summary(self, tier: str) -> Dict[str, Any]:
        """Return aggregate statistics for a specific tier."""
        tier_entries = [e for e in self._entries.values() if e.tier_used == tier]
        if not tier_entries:
            return {"count": 0, "avg_cost": 0.0, "avg_gain": 0.0, "success_rate": 0.0}

        costs = [e.estimated_cost or 0.0 for e in tier_entries]
        gains = [
            (e.estimated_immediate_gain or 0.0) + (e.estimated_reuse_gain or 0.0)
            for e in tier_entries
        ]
        successes = sum(
            1 for e in tier_entries
            if e.actual_immediate_effect and "good_enough=True" in e.actual_immediate_effect
        )

        return {
            "count": len(tier_entries),
            "avg_cost": sum(costs) / len(costs),
            "avg_gain": sum(gains) / len(gains),
            "success_rate": successes / len(tier_entries) if tier_entries else 0.0,
        }

    def cost_effectiveness_by_tier(self) -> Dict[str, Dict[str, Any]]:
        """Compute cost-effectiveness (gain-per-cost) for each tier.

        Returns a dict keyed by tier name with:
          - count: number of entries
          - total_gain: sum of all gains for this tier
          - total_cost: sum of all costs for this tier
          - gain_per_cost: average gain per unit cost (higher is better)
          - efficiency_rank: 1 = most cost-effective
        """
        tier_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "total_gain": 0.0, "total_cost": 0.0})

        for e in self._entries.values():
            tier = e.tier_used or "unknown"
            gain = (e.estimated_immediate_gain or 0.0) + (e.estimated_reuse_gain or 0.0)
            cost = (e.actual_cost_profile.estimated_cost_usd if e.actual_cost_profile else 0.0) or (e.estimated_cost or 0.0)
            tier_stats[tier]["count"] += 1
            tier_stats[tier]["total_gain"] += gain
            tier_stats[tier]["total_cost"] += cost

        result: Dict[str, Dict[str, Any]] = {}
        for tier, stats in tier_stats.items():
            total_cost = stats["total_cost"]
            gain_per_cost = (stats["total_gain"] / total_cost) if total_cost > 0 else float("inf")
            result[tier] = {
                "count": int(stats["count"]),
                "total_gain": stats["total_gain"],
                "total_cost": total_cost,
                "gain_per_cost": gain_per_cost,
            }

        # Rank tiers by gain_per_cost (descending)
        sorted_tiers = sorted(result.keys(), key=lambda t: result[t]["gain_per_cost"], reverse=True)
        for rank, tier in enumerate(sorted_tiers, start=1):
            result[tier]["efficiency_rank"] = rank

        return result

    def difficulty_performance(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by task difficulty level.

        Returns a dict keyed by difficulty ('low', 'medium', 'high', 'unknown') with:
          - count: number of entries at this difficulty
          - avg_gain: average total gain
          - avg_cost: average total cost
          - success_rate: fraction of entries judged good_enough
          - recommended_tier: the tier with best gain-per-cost for this difficulty
        """
        diff_stats: Dict[str, Dict[str, Any]] = {}

        for e in self._entries.values():
            # Extract difficulty from entry metadata if available; fallback to "unknown"
            difficulty = getattr(e, "difficulty", None) or "unknown"
            gain = (e.estimated_immediate_gain or 0.0) + (e.estimated_reuse_gain or 0.0)
            cost = (e.actual_cost_profile.estimated_cost_usd if e.actual_cost_profile else 0.0) or (e.estimated_cost or 0.0)
            success = bool(e.actual_immediate_effect and "good_enough=True" in e.actual_immediate_effect)

            if difficulty not in diff_stats:
                diff_stats[difficulty] = {
                    "count": 0, "total_gain": 0.0, "total_cost": 0.0,
                    "successes": 0, "tier_gains": defaultdict(float),
                    "tier_costs": defaultdict(float),
                }
            ds = diff_stats[difficulty]
            ds["count"] += 1
            ds["total_gain"] += gain
            ds["total_cost"] += cost
            if success:
                ds["successes"] += 1
            tier = e.tier_used or "unknown"
            ds["tier_gains"][tier] += gain
            ds["tier_costs"][tier] += cost

        result: Dict[str, Dict[str, Any]] = {}
        for difficulty, ds in diff_stats.items():
            count = ds["count"]
            # Find recommended tier (best gain-per-cost for this difficulty)
            best_tier = None
            best_gpc = -1.0
            for tier in ds["tier_gains"]:
                tier_cost = ds["tier_costs"][tier]
                tier_gain = ds["tier_gains"][tier]
                gpc = (tier_gain / tier_cost) if tier_cost > 0 else float("inf")
                if gpc > best_gpc:
                    best_gpc = gpc
                    best_tier = tier

            result[difficulty] = {
                "count": count,
                "avg_gain": ds["total_gain"] / count if count > 0 else 0.0,
                "avg_cost": ds["total_cost"] / count if count > 0 else 0.0,
                "success_rate": ds["successes"] / count if count > 0 else 0.0,
                "recommended_tier": best_tier or "tier_1",
            }

        return result
