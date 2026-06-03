from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...core.objects.identity import AgentIdentityObject
from ...runtime.concept_engine.cycle import run_concept_cycle
from ...runtime.concept_engine.registry import InMemoryConceptRegistry
from ...runtime.economy_control.ledger import InMemoryLedgerStore
from ...runtime.memory_os.store import InMemoryMemoryStore
from ...runtime.pipeline.minimal_run import run_minimal_pipeline
from ...runtime.theory_runtime.builder import build_and_register_theories
from ...runtime.theory_runtime.registry import InMemoryTheoryRegistry
from ..reports.integration_summary import generate_integration_summary_report
from ..task_sets.prototype_v3b_curriculum import PROTOTYPE_V3B_CURRICULUM
from ..task_sets.prototype_v6_cases import PROTOTYPE_V6_CASES
from ..task_sets.prototype_v7_broader_domain import PROTOTYPE_V7_BROADER_DOMAIN_CASES


def _make_identity() -> AgentIdentityObject:
    """Create the standard identity object for full integration runs."""
    return AgentIdentityObject.create(
        commitments=["transparency in reasoning", "accuracy", "cognitive economy"],
        self_model={"capability": "reasoning agent", "limitation": "simulated"},
    )


def _refresh_theories(
    task_results: List[dict],
    concept_registry: InMemoryConceptRegistry,
    theory_registry: InMemoryTheoryRegistry,
) -> None:
    """Rebuild theories from accumulated results."""
    family_names = sorted(
        {run.get("task", {}).get("task_family", "unknown") for run in task_results}
    )
    for family in family_names:
        build_and_register_theories(
            task_family=family,
            concepts=concept_registry.list_concepts(),
            contradictions=[
                c
                for run in task_results
                for c in run.get("blackboard", {}).get("contradictions", [])
                if run.get("task", {}).get("task_family") == family
            ],
            anomaly_candidates=[
                a
                for run in task_results
                for a in run.get("anomaly_candidates", [])
                if run.get("task", {}).get("task_family") == family
            ],
            registry=theory_registry,
        )


def _warmup_concepts(
    tasks: List[object],
    memory_store: InMemoryMemoryStore,
    ledger_store: InMemoryLedgerStore,
    concept_registry: InMemoryConceptRegistry,
    theory_registry: InMemoryTheoryRegistry,
) -> dict:
    """Run warmup phase to build concepts before main evaluation."""
    warmup_cost = 0.0
    warmup_runs: List[dict] = []
    for task in tasks:
        run = run_minimal_pipeline(
            task,
            store=memory_store,
            ledger_store=ledger_store,
            use_memory=True,
            use_economy=False,
            forced_tier="tier_1",
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_concepts=False,
        )
        warmup_cost += run["ledger"].get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0
        warmup_runs.append(run)
        run_concept_cycle(memory_store, concept_registry)
        _refresh_theories(warmup_runs, concept_registry, theory_registry)
    return {
        "warmup_task_count": len(tasks),
        "warmup_cost": warmup_cost,
        "concept_count_after_warmup": len(concept_registry.list_concepts()),
        "theory_count_after_warmup": len(theory_registry.list_theories()),
    }


def run_condition_all_flags(
    tasks: List[object],
    identity: AgentIdentityObject | None = None,
) -> Dict[str, Any]:
    """Run tasks with ALL governance flags enabled.

    This is the key difference from the standard run_condition: it passes
    all 5 governance flags (use_anomaly_leverage, use_theory_leverage,
    use_productive_forgetting, use_identity_governance, use_paradigm_fork)
    plus identity object, use_concepts=True, and use_economy=True.
    """
    identity = identity or _make_identity()
    task_list = list(tasks)
    memory_store = InMemoryMemoryStore()
    ledger_store = InMemoryLedgerStore()
    concept_registry = InMemoryConceptRegistry()
    theory_registry = InMemoryTheoryRegistry()

    # Warmup phase to build concepts and theories
    warmup_summary = _warmup_concepts(
        task_list, memory_store, ledger_store, concept_registry, theory_registry
    )

    task_results: List[dict] = []
    success_count = 0
    total_cost = 0.0

    for task in task_list:
        run = run_minimal_pipeline(
            task,
            store=memory_store,
            ledger_store=ledger_store,
            use_memory=True,
            use_economy=True,
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_concepts=True,
            use_anomaly_leverage=True,
            use_theory_leverage=True,
            use_productive_forgetting=True,
            use_identity_governance=True,
            use_paradigm_fork=True,
            identity=identity,
        )
        task_results.append(run)
        run_concept_cycle(memory_store, concept_registry)
        _refresh_theories(task_results, concept_registry, theory_registry)

        good = bool(
            run["blackboard"]["verification_state"]["verification_summary"]["good_enough"]
        )
        success_count += int(good)
        total_cost += run["ledger"].get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    count = len(task_results)
    return {
        "task_results": task_results,
        "aggregate_metrics": {
            "task_count": count,
            "success_rate": success_count / count if count else 0.0,
            "total_estimated_cost": total_cost,
            "avg_estimated_cost": total_cost / count if count else 0.0,
            "concept_count": len(concept_registry.list_concepts()),
            "theory_count": len(theory_registry.list_theories()),
        },
        "warmup_summary": warmup_summary,
    }


def run_condition_concept_only(tasks: List[object]) -> Dict[str, Any]:
    """Run tasks with concept-only configuration (equivalent to condition_a).

    use_concepts=True, use_memory=True, use_economy=False, no governance flags.
    """
    task_list = list(tasks)
    memory_store = InMemoryMemoryStore()
    ledger_store = InMemoryLedgerStore()
    concept_registry = InMemoryConceptRegistry()
    theory_registry = InMemoryTheoryRegistry()

    warmup_summary = _warmup_concepts(
        task_list, memory_store, ledger_store, concept_registry, theory_registry
    )

    task_results: List[dict] = []
    success_count = 0
    total_cost = 0.0

    for task in task_list:
        run = run_minimal_pipeline(
            task,
            store=memory_store,
            ledger_store=ledger_store,
            use_memory=True,
            use_economy=False,
            forced_tier="tier_1",
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_concepts=True,
        )
        task_results.append(run)
        run_concept_cycle(memory_store, concept_registry)
        _refresh_theories(task_results, concept_registry, theory_registry)

        good = bool(
            run["blackboard"]["verification_state"]["verification_summary"]["good_enough"]
        )
        success_count += int(good)
        total_cost += run["ledger"].get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    count = len(task_results)
    return {
        "task_results": task_results,
        "aggregate_metrics": {
            "task_count": count,
            "success_rate": success_count / count if count else 0.0,
            "total_estimated_cost": total_cost,
            "avg_estimated_cost": total_cost / count if count else 0.0,
            "concept_count": len(concept_registry.list_concepts()),
            "theory_count": len(theory_registry.list_theories()),
        },
        "warmup_summary": warmup_summary,
    }


def run_condition_combined_baseline(tasks: List[object]) -> Dict[str, Any]:
    """Run tasks with combined baseline (equivalent to condition_c).

    use_concepts=True, use_economy=True, no governance flags.
    """
    task_list = list(tasks)
    memory_store = InMemoryMemoryStore()
    ledger_store = InMemoryLedgerStore()
    concept_registry = InMemoryConceptRegistry()
    theory_registry = InMemoryTheoryRegistry()

    warmup_summary = _warmup_concepts(
        task_list, memory_store, ledger_store, concept_registry, theory_registry
    )

    task_results: List[dict] = []
    success_count = 0
    total_cost = 0.0

    for task in task_list:
        run = run_minimal_pipeline(
            task,
            store=memory_store,
            ledger_store=ledger_store,
            use_memory=True,
            use_economy=True,
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_concepts=True,
        )
        task_results.append(run)
        run_concept_cycle(memory_store, concept_registry)
        _refresh_theories(task_results, concept_registry, theory_registry)

        good = bool(
            run["blackboard"]["verification_state"]["verification_summary"]["good_enough"]
        )
        success_count += int(good)
        total_cost += run["ledger"].get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    count = len(task_results)
    return {
        "task_results": task_results,
        "aggregate_metrics": {
            "task_count": count,
            "success_rate": success_count / count if count else 0.0,
            "total_estimated_cost": total_cost,
            "avg_estimated_cost": total_cost / count if count else 0.0,
            "concept_count": len(concept_registry.list_concepts()),
            "theory_count": len(theory_registry.list_theories()),
        },
        "warmup_summary": warmup_summary,
    }


def run_full_integration(
    output_path: str = "virtual_genesis/eval/results/full_integration_summary.json",
) -> dict:
    """Run full integration evaluation across all task sets with all governance flags.

    Compares three conditions:
    - all_flags_enabled: all 5 governance flags True + identity + concepts + economy
    - concept_only: use_concepts=True, use_memory=True, use_economy=False
    - combined_baseline: use_concepts=True, use_economy=True

    Runs against v3b curriculum, v6 cases, and v7 broader domain cases.
    Computes interaction effects and outputs JSON summary.
    """
    # Combine all task sets
    all_tasks: List[object] = []
    all_tasks.extend(PROTOTYPE_V3B_CURRICULUM)
    all_tasks.extend(PROTOTYPE_V6_CASES)
    all_tasks.extend(PROTOTYPE_V7_BROADER_DOMAIN_CASES)

    # Run each condition
    all_flags_result = run_condition_all_flags(all_tasks)
    concept_only_result = run_condition_concept_only(all_tasks)
    combined_result = run_condition_combined_baseline(all_tasks)

    # Generate integration summary report
    summary = generate_integration_summary_report(
        all_flags_results=all_flags_result["task_results"],
        concept_only_results=concept_only_result["task_results"],
        combined_results=combined_result["task_results"],
    )

    payload = {
        "task_count": len(all_tasks),
        "task_sets": ["prototype_v3b_curriculum", "prototype_v6_cases", "prototype_v7_broader_domain"],
        "conditions": ["all_flags_enabled", "concept_only", "combined_baseline"],
        "all_flags_metrics": all_flags_result["aggregate_metrics"],
        "concept_only_metrics": concept_only_result["aggregate_metrics"],
        "combined_metrics": combined_result["aggregate_metrics"],
        "integration_summary": summary,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


if __name__ == "__main__":
    payload = run_full_integration()
    print(json.dumps(payload["integration_summary"], indent=2, ensure_ascii=False))
