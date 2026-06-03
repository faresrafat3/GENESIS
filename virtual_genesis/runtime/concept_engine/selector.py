from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from ...core.objects.memory import MemoryUnit


def build_contrastive_groups(memories: List[MemoryUnit]) -> List[dict]:
    groups: List[dict] = []

    # Family-level contrastive groups
    grouped: Dict[str, Dict[str, List[MemoryUnit]]] = defaultdict(lambda: {"success": [], "failure": []})
    for mem in memories:
        family = mem.meta.get("task_family", "unknown") if mem.meta else "unknown"
        good = bool(mem.meta.get("good_enough", False)) if mem.meta else False
        grouped[family]["success" if good else "failure"].append(mem)

    for family, buckets in grouped.items():
        if buckets["success"] and buckets["failure"]:
            groups.append(
                {
                    "group_type": "family_contrast",
                    "family": family,
                    "successes": buckets["success"],
                    "failures": buckets["failure"],
                    "property_name": None,
                    "shortcut_name": None,
                }
            )

    # Property-oriented groups
    prop_groups: Dict[tuple[str, str], Dict[str, List[MemoryUnit]]] = defaultdict(lambda: {"success": [], "failure": []})
    for mem in memories:
        meta = mem.meta or {}
        family = meta.get("task_family", "unknown")
        props = meta.get("required_properties", []) or []
        prop_checks = meta.get("property_checks", {}) or {}
        for prop in props:
            passed = bool(prop_checks.get(prop, False))
            prop_groups[(family, prop)]["success" if passed else "failure"].append(mem)

    for (family, prop), buckets in prop_groups.items():
        if (buckets["success"] and buckets["failure"]) or len(buckets["failure"]) >= 2:
            groups.append(
                {
                    "group_type": "property_gap",
                    "family": family,
                    "successes": buckets["success"],
                    "failures": buckets["failure"],
                    "property_name": prop,
                    "shortcut_name": None,
                }
            )

    # Shortcut-oriented groups
    shortcut_groups: Dict[tuple[str, str], Dict[str, List[MemoryUnit]]] = defaultdict(lambda: {"success": [], "failure": []})
    for mem in memories:
        meta = mem.meta or {}
        family = meta.get("task_family", "unknown")
        shortcuts = meta.get("forbidden_shortcuts", []) or []
        shortcut_checks = meta.get("shortcut_checks", {}) or {}
        for shortcut in shortcuts:
            violated = bool(shortcut_checks.get(shortcut, False))
            shortcut_groups[(family, shortcut)]["failure" if violated else "success"].append(mem)

    for (family, shortcut), buckets in shortcut_groups.items():
        if (buckets["success"] and buckets["failure"]) or len(buckets["failure"]) >= 2:
            groups.append(
                {
                    "group_type": "shortcut_gap",
                    "family": family,
                    "successes": buckets["success"],
                    "failures": buckets["failure"],
                    "property_name": None,
                    "shortcut_name": shortcut,
                }
            )

    return groups
