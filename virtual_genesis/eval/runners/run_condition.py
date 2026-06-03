from __future__ import annotations

from typing import Iterable, List

from ...core.objects.eval import EvaluationResult
from ...runtime.concept_engine.cycle import run_concept_cycle
from ...runtime.concept_engine.registry import InMemoryConceptRegistry
from ...runtime.economy_control.ledger import InMemoryLedgerStore
from ...runtime.memory_os.store import InMemoryMemoryStore
from ...runtime.pipeline.minimal_run import run_minimal_pipeline
from ...runtime.theory_runtime.builder import build_and_register_theories
from ...runtime.theory_runtime.registry import InMemoryTheoryRegistry
from ..reports.anomaly_candidates import generate_anomaly_candidate_report
from ..reports.concept_selectivity import generate_concept_selectivity_report
from ..reports.concept_utility import generate_concept_utility_report
from ..reports.contradiction_analytics import generate_contradiction_analytics
from ..reports.family_breakdown import generate_family_breakdown
from ..reports.premium_roi import generate_premium_roi_report
from ..reports.theory_analytics import generate_theory_analytics
from ..reports.theory_usage import generate_theory_usage_report


CONDITIONS = {
    "baseline_0": {"use_memory": False, "use_economy": False, "forced_tier": "tier_1", "use_concepts": False},
    "baseline_1": {"use_memory": True, "use_economy": False, "forced_tier": "tier_1", "use_concepts": False},
    "baseline_2_premium_always": {"use_memory": True, "use_economy": False, "forced_tier": "tier_2", "use_concepts": False},
    "condition_a_concept_ready": {"use_memory": True, "use_economy": False, "forced_tier": "tier_1", "use_concepts": True},
    "condition_b_economy": {"use_memory": True, "use_economy": True, "forced_tier": None, "use_concepts": False},
    "condition_c_combined": {"use_memory": True, "use_economy": True, "forced_tier": None, "use_concepts": True},
}


def _refresh_theories(task_results: List[dict], concept_registry: InMemoryConceptRegistry, theory_registry: InMemoryTheoryRegistry) -> None:
    family_names = sorted({run.get("task", {}).get("task_family", "unknown") for run in task_results})
    for family in family_names:
        build_and_register_theories(
            task_family=family,
            concepts=concept_registry.list_concepts(),
            contradictions=[c for run in task_results for c in run.get("blackboard", {}).get("contradictions", []) if run.get("task", {}).get("task_family") == family],
            anomaly_candidates=[a for run in task_results for a in run.get("anomaly_candidates", []) if run.get("task", {}).get("task_family") == family],
            registry=theory_registry,
        )


def _warmup_concepts(tasks: List[object], memory_store: InMemoryMemoryStore, ledger_store: InMemoryLedgerStore, concept_registry: InMemoryConceptRegistry, theory_registry: InMemoryTheoryRegistry) -> dict:
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


def run_condition(
    condition_id: str,
    tasks: Iterable[object],
    task_set_ref: str = "local_dev",
    *,
    use_theory_leverage: bool = False,
    use_anomaly_leverage: bool = False,
) -> EvaluationResult:
    config = CONDITIONS[condition_id]
    task_list = list(tasks)
    memory_store = InMemoryMemoryStore()
    ledger_store = InMemoryLedgerStore()
    concept_registry = InMemoryConceptRegistry()
    theory_registry = InMemoryTheoryRegistry()
    result = EvaluationResult.create(condition_id=condition_id, task_set_ref=task_set_ref)

    warmup_summary = None
    if config["use_concepts"]:
        warmup_summary = _warmup_concepts(task_list, memory_store, ledger_store, concept_registry, theory_registry)

    task_results: List[dict] = []
    success_count = 0
    total_cost = 0.0

    for task in task_list:
        run = run_minimal_pipeline(
            task,
            store=memory_store,
            ledger_store=ledger_store,
            use_memory=config["use_memory"],
            use_economy=config["use_economy"],
            forced_tier=config["forced_tier"],
            concept_registry=concept_registry,
            theory_registry=theory_registry,
            use_concepts=config["use_concepts"],
            use_theory_leverage=use_theory_leverage,
            use_anomaly_leverage=use_anomaly_leverage,
        )
        task_results.append(run)
        if config["use_concepts"]:
            run_concept_cycle(memory_store, concept_registry)
            _refresh_theories(task_results, concept_registry, theory_registry)

        good = bool(run["blackboard"]["verification_state"]["verification_summary"]["good_enough"])
        success_count += int(good)
        total_cost += run["ledger"].get("actual_cost_profile", {}).get("estimated_cost_usd", 0.0) or 0.0

    concept_report = generate_concept_utility_report(task_results)
    selectivity_report = generate_concept_selectivity_report(task_results)
    contradiction_report = generate_contradiction_analytics(task_results)
    anomaly_report = generate_anomaly_candidate_report(task_results)
    premium_report = generate_premium_roi_report(task_results)
    family_report = generate_family_breakdown(task_results)
    theory_report = generate_theory_analytics([t.to_dict() for t in theory_registry.list_theories()])
    theory_usage_report = generate_theory_usage_report(task_results)

    result.task_results = task_results
    result.aggregate_metrics = {
        "task_count": len(task_results),
        "success_rate": success_count / len(task_results) if task_results else 0.0,
        "total_estimated_cost": total_cost,
        "avg_estimated_cost": total_cost / len(task_results) if task_results else 0.0,
        "concept_count": len(concept_registry.list_concepts()),
        "concept_activation_rate": concept_report["concept_activation_rate"],
        "premium_run_count": premium_report["premium_run_count"],
        "contradiction_task_rate": contradiction_report["contradiction_task_rate"],
        "anomaly_candidate_task_rate": anomaly_report["anomaly_candidate_task_rate"],
        "theory_count": theory_report["theory_count"],
        "theory_hint_task_rate": theory_usage_report["theory_hint_task_rate"],
    }
    result.meta = {
        "warmup_summary": warmup_summary,
        "concept_report": concept_report,
        "concept_selectivity_report": selectivity_report,
        "contradiction_report": contradiction_report,
        "anomaly_candidate_report": anomaly_report,
        "premium_report": premium_report,
        "family_report": family_report,
        "theory_report": theory_report,
        "theory_usage_report": theory_usage_report,
        "theories": [t.to_dict() for t in theory_registry.list_theories()],
    }
    return result
