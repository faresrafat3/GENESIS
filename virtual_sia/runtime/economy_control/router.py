from __future__ import annotations

from ...core.objects.blackboard import BlackboardMemoryPack, BlackboardObject
from ...core.objects.decision import TierDecisionObject
from ...core.objects.task import TaskObject


def choose_tier(task: TaskObject, blackboard: BlackboardObject, memory_pack: BlackboardMemoryPack) -> TierDecisionObject:
    reason_parts: list[str] = []
    chosen_tier = "tier_1"
    ambiguity = bool((task.meta or {}).get("family_ambiguity", False))

    if task.criticality_level == "high" and task.difficulty_estimate in {"medium", "high"}:
        chosen_tier = "tier_2"
        reason_parts.append("high criticality with non-trivial difficulty")
    elif ambiguity and not memory_pack.concept_refs:
        chosen_tier = "tier_1"
        reason_parts.append("framing ambiguity present; stay in balanced tier pending more evidence")
    elif memory_pack.concept_refs and task.difficulty_estimate != "high":
        chosen_tier = "tier_1"
        reason_parts.append("concept support available, no premium escalation needed initially")
    elif task.difficulty_estimate == "low" and task.task_family in {"procedure", "unknown"} and not ambiguity:
        chosen_tier = "tier_0"
        reason_parts.append("low difficulty and low ambiguity task can start cheap")
    elif memory_pack.memory_noise_risk is not None and memory_pack.memory_noise_risk > 0.5:
        chosen_tier = "tier_1"
        reason_parts.append("avoid cheap path due to memory noise risk")
    else:
        reason_parts.append("default balanced worker tier")

    decision = TierDecisionObject.create(
        task_ref=task.id,
        chosen_tier=chosen_tier,
        reason="; ".join(reason_parts),
    )
    decision.expected_immediate_gain = 0.4 if chosen_tier == "tier_0" else 0.7 if chosen_tier == "tier_1" else 0.9
    decision.expected_reuse_gain = 0.2 if memory_pack.concept_refs else 0.1 if chosen_tier == "tier_0" else 0.25 if chosen_tier == "tier_1" else 0.45
    decision.expected_cost = 0.0 if chosen_tier == "tier_0" else 0.001 if chosen_tier == "tier_1" else 0.01
    decision.expected_delay_penalty = 0.05 if chosen_tier == "tier_2" else (0.02 if ambiguity else 0.0)
    decision.confidence_in_decision = 0.5 if ambiguity else 0.6
    decision.fallback_option = "tier_1" if chosen_tier == "tier_0" else "tier_2"
    return decision


def choose_tier_anomaly_aware(
    task: TaskObject,
    blackboard: BlackboardObject,
    memory_pack: BlackboardMemoryPack,
    anomaly_severity: float = 0.0,
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
    decision = choose_tier(task, blackboard, memory_pack)

    if anomaly_severity > 0.7:
        decision.chosen_tier = "tier_2"
        decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} forces tier_2"
        decision.expected_cost = 0.01
        decision.expected_immediate_gain = 0.9
    elif anomaly_severity > 0.4:
        if decision.chosen_tier == "tier_0":
            decision.chosen_tier = "tier_1"
            decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} prevents tier_0"
            decision.expected_cost = 0.001
            decision.expected_immediate_gain = 0.7

    return decision


def choose_tier_theory_guided(
    task: TaskObject,
    blackboard: BlackboardObject,
    memory_pack: BlackboardMemoryPack,
    theory_prediction: dict,
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
    decision = choose_tier(task, blackboard, memory_pack)

    predicts_failure = theory_prediction.get("predicts_failure", False)
    predicts_difficulty = theory_prediction.get("predicts_difficulty", False)
    confidence = theory_prediction.get("confidence", 0.0)

    if predicts_failure and confidence >= 0.6:
        decision.chosen_tier = "tier_2"
        decision.decision_reason += f"; theory predicts failure (confidence={confidence:.2f}), forcing tier_2"
        decision.expected_cost = 0.01
        decision.expected_immediate_gain = 0.9
    elif predicts_difficulty and confidence >= 0.5:
        if decision.chosen_tier == "tier_0":
            decision.chosen_tier = "tier_1"
            decision.decision_reason += f"; theory predicts difficulty (confidence={confidence:.2f}), preventing tier_0"
            decision.expected_cost = 0.001
            decision.expected_immediate_gain = 0.7

    return decision
