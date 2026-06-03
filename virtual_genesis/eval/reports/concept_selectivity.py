from __future__ import annotations

from typing import Any, Dict, List


def generate_concept_selectivity_report(task_results: List[dict]) -> Dict[str, Any]:
    total = len(task_results)
    selected_tasks = 0
    total_selected = 0
    total_candidates_seen = 0
    total_selected_score = 0.0

    for run in task_results:
        pack_meta = run['blackboard']['retrieved_memory_pack'].get('meta', {}) or {}
        decisions = pack_meta.get('concept_activation_decisions', []) or []
        total_candidates_seen += len(decisions)
        selected = [d for d in decisions if d.get('selected')]
        if selected:
            selected_tasks += 1
            total_selected += len(selected)
            total_selected_score += sum(d.get('activation_score', 0) for d in selected)

    return {
        'task_count': total,
        'tasks_with_selected_concepts': selected_tasks,
        'concept_activation_rate': (selected_tasks / total) if total else 0.0,
        'avg_selected_concepts_per_task': (total_selected / total) if total else 0.0,
        'avg_candidate_count_per_task': (total_candidates_seen / total) if total else 0.0,
        'avg_selected_activation_score': (total_selected_score / total_selected) if total_selected else 0.0,
    }
