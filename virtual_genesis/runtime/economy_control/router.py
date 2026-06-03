from __future__ import annotations

from typing import Any, Dict, Optional

from ...core.objects.blackboard import BlackboardMemoryPack, BlackboardObject
from ...core.objects.decision import TierDecisionObject
from ...core.objects.task import TaskObject


# Difficulty-to-tier mapping table: maps difficulty to the minimum recommended tier.
_DIFFICULTY_TIER_FLOOR: Dict[str, str] = {
    "low": "tier_0",
    "medium": "tier_1",
    "high": "tier_2",
}


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def _estimate_decision_confidence(
    ambiguity: bool,
    difficulty_known: bool,
    concept_support: bool,
    memory_noise_risk: Optional[float],
) -> float:
    """Compute a confidence score (0..1) in the routing decision.

    Higher confidence when:
      - No ambiguity present
      - Difficulty is known (not 'unknown')
      - Concept support is available (reduces uncertainty)
    Lower confidence when:
      - Memory noise risk is high
    """
    base = 0.5
    if not ambiguity:
        base += 0.15
    if difficulty_known:
        base += 0.1
    if concept_support:
        base += 0.1
    if memory_noise_risk is not None and memory_noise_risk > 0.5:
        base -= 0.15
    return _clamp(base)


def _expected_values(
    chosen_tier: str,
    has_concepts: bool,
    ambiguity: bool,
    criticality: str,
) -> Dict[str, float]:
    """Compute expected immediate gain, reuse gain, cost, and delay penalty for a tier.

    Uses a calibrated table updated with empirical reasoning:
      - tier_0: cheap but lower quality; risk of rework on ambiguous tasks
      - tier_1: balanced quality/cost; benefits most from concept support
      - tier_2: premium quality; justified by high difficulty or criticality
    """
    # Base expected immediate gain per tier
    gain_table = {"tier_0": 0.40, "tier_1": 0.70, "tier_2": 0.90}
    # Base expected cost per tier
    cost_table = {"tier_0": 0.000, "tier_1": 0.001, "tier_2": 0.010}

    immediate_gain = gain_table.get(chosen_tier, 0.5)

    # Reuse gain: concept support amplifies reuse gain for tier_1+
    if has_concepts:
        reuse_gain = {"tier_0": 0.15, "tier_1": 0.30, "tier_2": 0.50}.get(chosen_tier, 0.2)
    else:
        reuse_gain = {"tier_0": 0.10, "tier_1": 0.20, "tier_2": 0.40}.get(chosen_tier, 0.15)

    # Cost increases slightly with ambiguity (higher chance of rework)
    base_cost = cost_table.get(chosen_tier, 0.001)
    cost = base_cost * (1.2 if ambiguity else 1.0)

    # Delay penalty: tier_2 has higher latency; ambiguity adds uncertainty cost
    delay_penalty = 0.05 if chosen_tier == "tier_2" else 0.02 if ambiguity else 0.0

    # Criticality boost: high-criticality tasks have higher effective gain (failure cost is worse)
    if criticality == "high":
        immediate_gain = _clamp(immediate_gain + 0.05)
        reuse_gain = _clamp(reuse_gain + 0.05)

    return {
        "expected_immediate_gain": round(immediate_gain, 4),
        "expected_reuse_gain": round(reuse_gain, 4),
        "expected_cost": round(cost, 6),
        "expected_delay_penalty": round(delay_penalty, 4),
    }


def choose_tier(
    task: TaskObject,
    blackboard: BlackboardObject,
    memory_pack: BlackboardMemoryPack,
    budget_remaining: Optional[float] = None,
) -> TierDecisionObject:
    """Route a task to the appropriate cognitive tier.

    Decision cascade (evaluated in order):
      1. Criticality override: high-criticality + non-trivial difficulty -> tier_2
      2. Difficulty floor: use difficulty_estimate as minimum tier
      3. Ambiguity penalty: ambiguity without concept support avoids tier_0
      4. Memory noise risk: high noise risk avoids tier_0
      5. Budget constraint: if budget is tight, downgrade to cheaper tier (but never below difficulty floor)
      6. Default: tier_1 balanced worker
    """
    reason_parts: list[str] = []
    ambiguity = bool((task.meta or {}).get("family_ambiguity", False))
    difficulty = task.difficulty_estimate  # "low", "medium", "high", "unknown"
    has_concepts = bool(memory_pack.concept_refs)
    noise_risk = memory_pack.memory_noise_risk

    # 1. High criticality + non-trivial difficulty => tier_2
    if task.criticality_level == "high" and difficulty in {"medium", "high"}:
        chosen_tier = "tier_2"
        reason_parts.append("high criticality with non-trivial difficulty")

    # 2. Difficulty floor: use difficulty as primary signal
    elif difficulty == "high":
        chosen_tier = "tier_2"
        reason_parts.append("high difficulty requires premium tier")
    elif difficulty == "low" and task.task_family in {"procedure", "unknown"} and not ambiguity:
        chosen_tier = "tier_0"
        reason_parts.append("low difficulty and low ambiguity task can start cheap")
    elif difficulty == "medium":
        chosen_tier = "tier_1"
        reason_parts.append("medium difficulty balanced tier")

    # 3. Ambiguity without concept support => avoid tier_0 (not enough signal for cheap path)
    elif ambiguity and not has_concepts:
        chosen_tier = "tier_1"
        reason_parts.append("framing ambiguity present without concept support; balanced tier pending evidence")

    # 4. High memory noise risk => avoid tier_0
    elif noise_risk is not None and noise_risk > 0.5:
        chosen_tier = "tier_1"
        reason_parts.append("memory noise risk above threshold; avoid cheap path")

    # 5. Concept support available and difficulty not high => tier_1 is efficient
    elif has_concepts and difficulty != "high":
        chosen_tier = "tier_1"
        reason_parts.append("concept support available, balanced tier sufficient")

    # 6. Default
    else:
        chosen_tier = "tier_1"
        reason_parts.append("default balanced worker tier")

    # Budget-aware downgrade: if budget is tight, downgrade by one tier (but respect difficulty floor)
    if budget_remaining is not None and budget_remaining < 0.005:
        floor = _DIFFICULTY_TIER_FLOOR.get(difficulty, "tier_1")
        tier_order = ["tier_0", "tier_1", "tier_2"]
        current_idx = tier_order.index(chosen_tier)
        floor_idx = tier_order.index(floor)
        if current_idx > floor_idx:
            chosen_tier = tier_order[current_idx - 1]
            reason_parts.append(f"budget constrained (remaining={budget_remaining:.4f}); downgraded one tier")

    # Compute expected values
    ev = _expected_values(chosen_tier, has_concepts, ambiguity, task.criticality_level or "medium")

    # Compute confidence
    confidence = _estimate_decision_confidence(
        ambiguity=ambiguity,
        difficulty_known=(difficulty not in {"unknown", None}),
        concept_support=has_concepts,
        memory_noise_risk=noise_risk,
    )

    # Fallback: the next tier up (tier_2 has no fallback, stays tier_2)
    fallback = {"tier_0": "tier_1", "tier_1": "tier_2", "tier_2": "tier_2"}.get(chosen_tier, "tier_1")

    decision = TierDecisionObject.create(
        task_ref=task.id,
        chosen_tier=chosen_tier,
        reason="; ".join(reason_parts),
    )
    decision.expected_immediate_gain = ev["expected_immediate_gain"]
    decision.expected_reuse_gain = ev["expected_reuse_gain"]
    decision.expected_cost = ev["expected_cost"]
    decision.expected_delay_penalty = ev["expected_delay_penalty"]
    decision.confidence_in_decision = confidence
    decision.fallback_option = fallback
    return decision


def choose_tier_anomaly_aware(
    task: TaskObject,
    blackboard: BlackboardObject,
    memory_pack: BlackboardMemoryPack,
    anomaly_severity: float = 0.0,
    budget_remaining: Optional[float] = None,
) -> TierDecisionObject:
    """Anomaly-aware tier routing that biases toward higher tiers under anomaly pressure.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.12: Ashby - Law of Requisite Variety (1956)
    ما الذي اخذناه؟
        requisite variety: anomaly pressure requires matched response variety.
        عندما يرتفع ضغط الشذوذ، يجب ان يزداد تنوع استجابة النظام.
        الطبقة الاعلى (tier_2) توفر تنوعا اكبر في المعالجة.
    ما الذي لم ناخذه الان؟
        الحساب الكامل لدرجات الحرية المطلوبة في كل طبقة.
    ماذا اصبح عندنا؟
        عندما تتجاوز شدة الشذوذ 0.4، لا يسمح بالطبقة الرخيصة (tier_0).
        عندما تتجاوز 0.7، تفرض الطبقة المتقدمة (tier_2).

    المصدر: DevOps Incident Management (PagerDuty/Datadog patterns)
    ما الذي اخذناه؟
        escalation caution under anomaly signals: في ادارة الحوادث،
        كلما ارتفعت شدة التنبيه يتصاعد مستوى الاستجابة تلقائيا.
    ما الذي لم ناخذه الان؟
        runbooks كاملة وتصعيد متعدد المستويات مع on-call rotations.
    ماذا اصبح عندنا؟
        قاعدتان بسيطتان: severity > 0.4 يمنع tier_0، severity > 0.7 يفرض tier_2.
    """
    decision = choose_tier(task, blackboard, memory_pack, budget_remaining=budget_remaining)

    if anomaly_severity > 0.7:
        decision.chosen_tier = "tier_2"
        decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} forces tier_2"
        ev = _expected_values("tier_2", bool(memory_pack.concept_refs), False, task.criticality_level or "medium")
        decision.expected_cost = ev["expected_cost"]
        decision.expected_immediate_gain = ev["expected_immediate_gain"]
        decision.confidence_in_decision = _clamp(decision.confidence_in_decision + 0.1)
    elif anomaly_severity > 0.4:
        if decision.chosen_tier == "tier_0":
            decision.chosen_tier = "tier_1"
            decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} prevents tier_0"
            ev = _expected_values("tier_1", bool(memory_pack.concept_refs), False, task.criticality_level or "medium")
            decision.expected_cost = ev["expected_cost"]
            decision.expected_immediate_gain = ev["expected_immediate_gain"]

    return decision


def choose_tier_theory_guided(
    task: TaskObject,
    blackboard: BlackboardObject,
    memory_pack: BlackboardMemoryPack,
    theory_prediction: dict,
    budget_remaining: Optional[float] = None,
) -> TierDecisionObject:
    """Theory-guided tier routing that biases toward higher tiers based on theory predictions.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 5.34: Bayesian Epistemology - Howson & Urbach (1989)
    ما الذي اخذناه؟
        القرار البايزي: عندما تتنبا النظرية بالصعوبة او الفشل بثقة كافية،
        يجب تعديل قرار الطبقة ليعكس هذا التنبؤ المسبق (prior).
        الثقة العالية في التنبؤ تعني تعديلا اقوى للقرار.
    ما الذي لم ناخذه الان؟
        الحساب البايزي الكامل مع posterior distribution.
        لم ناخذ التوازن الدقيق بين التكلفة والعائد المتوقع.
    ماذا اصبح عندنا؟
        عند تنبؤ بالصعوبة (confidence >= 0.5): لا يسمح بـ tier_0.
        عند تنبؤ بالفشل (confidence >= 0.6): يفرض tier_2.

    المصدر 5.38: DevOps Runbook Automation - SRE Practices (Google, 2016)
    ما الذي اخذناه؟
        في ادارة الحوادث، التنبؤ بالمشكلة يستدعي تصعيدا استباقيا.
        Runbook يقول: اذا الانذار المبكر يشير الى فشل محتمل، صعد فورا.
    ما الذي لم ناخذه الان؟
        Runbooks كاملة مع خطوات متعددة وتصعيد هرمي.
    ماذا اصبح عندنا؟
        قاعدتان بسيطتان للتصعيد الاستباقي المبني على تنبؤ النظرية.
    """
    decision = choose_tier(task, blackboard, memory_pack, budget_remaining=budget_remaining)

    predicts_failure = theory_prediction.get("predicts_failure", False)
    predicts_difficulty = theory_prediction.get("predicts_difficulty", False)
    confidence = theory_prediction.get("confidence", 0.0)

    if predicts_failure and confidence >= 0.6:
        decision.chosen_tier = "tier_2"
        decision.decision_reason += f"; theory predicts failure (confidence={confidence:.2f}), forcing tier_2"
        ev = _expected_values("tier_2", bool(memory_pack.concept_refs), False, task.criticality_level or "medium")
        decision.expected_cost = ev["expected_cost"]
        decision.expected_immediate_gain = ev["expected_immediate_gain"]
        decision.confidence_in_decision = _clamp(decision.confidence_in_decision + 0.1)
    elif predicts_difficulty and confidence >= 0.5:
        if decision.chosen_tier == "tier_0":
            decision.chosen_tier = "tier_1"
            decision.decision_reason += f"; theory predicts difficulty (confidence={confidence:.2f}), preventing tier_0"
            ev = _expected_values("tier_1", bool(memory_pack.concept_refs), False, task.criticality_level or "medium")
            decision.expected_cost = ev["expected_cost"]
            decision.expected_immediate_gain = ev["expected_immediate_gain"]

    return decision
