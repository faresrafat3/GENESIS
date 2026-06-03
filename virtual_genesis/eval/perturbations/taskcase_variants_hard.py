from __future__ import annotations

from typing import Iterable, List

from ...core.objects.task_case import TaskCase
from .taskcase_variants import clone_case, inject_brevity_lure, inject_light_overlap, lexical_soften, tighten_contract


def build_harder_levels(case: TaskCase) -> list[TaskCase]:
    levels: list[TaskCase] = []

    l0 = lexical_soften(case)
    l0.tags.append("hard_curriculum_level_0")
    l0.meta["curriculum_level"] = 0
    levels.append(l0)

    l1 = inject_brevity_lure(l0)
    l1.tags.append("hard_curriculum_level_1")
    l1.meta["curriculum_level"] = 1
    levels.append(l1)

    extra_prop = "evidence-grounded conclusion" if case.expected_primary_family != "procedure" else "stable structured layout"
    l2 = tighten_contract(l1, extra_property=extra_prop)
    l2.tags.append("hard_curriculum_level_2")
    l2.meta["curriculum_level"] = 2
    levels.append(l2)

    overlap_target = "procedure" if case.expected_primary_family != "procedure" else "comparison"
    l3 = inject_light_overlap(l2, overlap_target)
    l3.tags.append("hard_curriculum_level_3")
    l3.meta["curriculum_level"] = 3
    levels.append(l3)

    return levels


def build_harder_curriculum_from_cases(cases: Iterable[TaskCase], limit_per_case: int = 4) -> List[TaskCase]:
    all_cases: List[TaskCase] = []
    for case in cases:
        all_cases.extend(build_harder_levels(case)[:limit_per_case])
    return all_cases
