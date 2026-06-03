from __future__ import annotations

from ..perturbations.taskcase_variants import build_curriculum_from_cases
from .prototype_v3b_cases import PROTOTYPE_V3B_CASES

PROTOTYPE_V3B_CURRICULUM = build_curriculum_from_cases(PROTOTYPE_V3B_CASES, limit_per_case=4)
