from __future__ import annotations

from typing import Any, Dict

from ...core.objects.task import TaskObject


def should_escalate(task: TaskObject, verification_state: Dict[str, Any], current_tier: str) -> Dict[str, Any]:
    good_enough = bool(verification_state.get("verification_summary", {}).get("good_enough", False))
    if good_enough:
        return {
            "escalate": False,
            "target_tier": None,
            "reason": "verification judged output good enough",
            "expected_value": 0.0,
            "blockers": [],
        }

    if current_tier == "tier_2":
        return {
            "escalate": False,
            "target_tier": None,
            "reason": "already at premium tier",
            "expected_value": 0.0,
            "blockers": ["premium_ceiling_reached"],
        }

    target = "tier_1" if current_tier == "tier_0" else "tier_2"
    reason = "failed verification and higher tier may improve answer quality"
    if task.criticality_level == "high":
        reason += "; task criticality increases escalation value"

    return {
        "escalate": True,
        "target_tier": target,
        "reason": reason,
        "expected_value": 0.5 if target == "tier_1" else 0.75,
        "blockers": [],
    }


def should_escalate_anomaly_aware(
    task: TaskObject,
    verification_state: Dict[str, Any],
    current_tier: str,
    anomaly_severity: float = 0.0,
) -> Dict[str, Any]:
    """Anomaly-aware escalation that lowers escalation threshold when anomaly signals present.

    ## سرقة شرعية (Legitimate Theft)

    المصدر: DevOps Incident Management (PagerDuty/Datadog patterns)
    ما الذي اخذناه؟
        escalation caution under anomaly signals: في انظمة ادارة الحوادث،
        عند وجود اشارات شذوذ يتم خفض عتبة التصعيد واحيانا التصعيد الفوري
        بغض النظر عن نتيجة التحقق المبدئي.
    ما الذي لم ناخذه الان؟
        multi-level runbooks، acknowledgment windows، on-call rotations.
    ماذا اصبح عندنا؟
        اذا كانت شدة الشذوذ > 0.5 والنظام ليس في tier_2 بالفعل،
        يتم التصعيد دائما بغض النظر عن نتيجة التحقق.

    المصدر 6.3: Kuhn - Structure of Scientific Revolutions (1962)
    ما الذي اخذناه؟
        تراكم الشذوذات يجبر على تغيير السلوك. هنا: الشذوذ العالي يجبر
        على التصعيد حتى لو بدا المخرج "جيدا بما يكفي" بالمعايير العادية.
    ما الذي لم ناخذه الان؟
        التغيير الجذري في النموذج (paradigm shift).
    ماذا اصبح عندنا؟
        تصعيد قسري عند severity > 0.5 يعكس ضغط الشذوذ على قرارات النظام.
    """
    if current_tier == "tier_2":
        return {
            "escalate": False,
            "target_tier": None,
            "reason": "already at premium tier; anomaly pressure noted but ceiling reached",
            "expected_value": 0.0,
            "blockers": ["premium_ceiling_reached"],
            "anomaly_severity": anomaly_severity,
        }

    # Anomaly-forced escalation: severity > 0.5 always escalates to tier_2
    if anomaly_severity > 0.5:
        return {
            "escalate": True,
            "target_tier": "tier_2",
            "reason": f"anomaly_severity={anomaly_severity:.2f} exceeds threshold 0.5; forced escalation to tier_2",
            "expected_value": 0.85,
            "blockers": [],
            "anomaly_severity": anomaly_severity,
        }

    # Fall back to normal escalation logic for low anomaly severity
    base_result = should_escalate(task, verification_state, current_tier)
    base_result["anomaly_severity"] = anomaly_severity
    return base_result
