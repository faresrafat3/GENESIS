from __future__ import annotations

from typing import Any, Dict, List

from ...core.objects.anomaly import AnomalyCandidate


def compute_anomaly_severity_score(candidates: List[AnomalyCandidate]) -> float:
    """Compute a composite severity score (0.0-1.0) from a list of AnomalyCandidate objects.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.8: Predictive Processing / Active Inference (Friston, 2010)
    ما الذي اخذناه؟
        anomaly_severity = prediction error signal. كلما زاد عدد الشذوذات وشدتها
        يعني ان النظام يواجه اشارات خطا تنبؤ اقوى تتطلب استجابة اكبر.
    ما الذي لم ناخذه الان؟
        الحلقة الكاملة للتحديث البايزي للنماذج الداخلية.
    ماذا اصبح عندنا؟
        دالة تحسب درجة شدة مركبة من قائمة المرشحين الشاذين.

    المصدر: Anomaly Detection in ML (Chandola, Banerjee, Kumar - ACM Survey 2009)
    ما الذي اخذناه؟
        severity scoring mechanism: الجمع بين عدد الشذوذات، اقصى شدة،
        وتنوع المصادر كمؤشرات على خطورة الوضع.
    ما الذي لم ناخذه الان؟
        خوارزميات الكشف الاحصائي المعقدة (isolation forests, autoencoders).
    ماذا اصبح عندنا؟
        صيغة مركبة بسيطة تعطي وزنا للعدد والشدة والتنوع.
    """
    if not candidates:
        return 0.0

    count_factor = min(len(candidates) / 5.0, 1.0)

    max_severity = max((c.severity or 0.0) for c in candidates)

    source_types = set(c.source_type for c in candidates if c.source_type)
    diversity_factor = min(len(source_types) / 3.0, 1.0)

    composite = (0.4 * max_severity) + (0.35 * count_factor) + (0.25 * diversity_factor)
    return min(max(composite, 0.0), 1.0)


def matches_known_anomaly_pattern(task_result: dict, previous_candidates: List[AnomalyCandidate] | None = None) -> bool:
    """Check if a task_result matches patterns from previously seen anomalies.

    Looks for: property_gap + shortcut_pattern co-occurrence, repeated family failures,
    contradiction clustering.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.3: Kuhn - Structure of Scientific Revolutions (1962)
    ما الذي اخذناه؟
        anomaly -> behavioral influence: الشذوذ المتكرر يكشف نمطا يستدعي
        تغييرا في سلوك النظام، تماما كما تتراكم الشذوذات لتهز النموذج العلمي.
    ما الذي لم ناخذه الان؟
        paradigm shift الكامل - لا يتغير النموذج بالكامل بل يتعدل السلوك فقط.
    ماذا اصبح عندنا؟
        دالة تتعرف على انماط شذوذ معروفة من خلال التحقق من تزامن
        property_gap مع shortcut_pattern ومن تكرار الفشل في نفس العائلة.
    """
    blackboard = task_result.get("blackboard", {})
    verification = blackboard.get("verification_state", {})
    contradictions = blackboard.get("contradictions", []) or []
    task = task_result.get("task", {})
    task_family = task.get("task_family", "unknown")

    property_checks = verification.get("property_checks", {}) or {}
    shortcut_checks = verification.get("shortcut_checks", {}) or {}

    has_property_gap = property_checks and not all(property_checks.values())
    has_shortcut_trigger = any(shortcut_checks.values())

    # Pattern 1: property_gap + shortcut_pattern co-occurrence
    if has_property_gap and has_shortcut_trigger:
        return True

    # Pattern 2: repeated family failures from previous candidates
    if previous_candidates:
        family_failures = [c for c in previous_candidates if c.task_family == task_family]
        if len(family_failures) >= 2:
            return True

    # Pattern 3: contradiction clustering (3+ contradictions in same result)
    if len(contradictions) >= 3:
        return True

    return False


def extract_anomaly_candidates(task_result: dict) -> List[AnomalyCandidate]:
    task = task_result.get("task", {})
    blackboard = task_result.get("blackboard", {})
    verification = blackboard.get("verification_state", {})
    contradictions = blackboard.get("contradictions", []) or []
    task_family = task.get("task_family", "unknown")

    candidates: List[AnomalyCandidate] = []

    property_checks = verification.get("property_checks", {}) or {}
    shortcut_checks = verification.get("shortcut_checks", {}) or {}
    good_enough = bool(verification.get("verification_summary", {}).get("good_enough", False))

    # Candidate A: repeated contract failure signal
    if not good_enough and property_checks and not all(property_checks.values()):
        failed_props = [k for k, v in property_checks.items() if not v]
        candidates.append(
            AnomalyCandidate.create(
                task_family=task_family,
                source_type="property_gap",
                summary=f"Task failed required properties: {failed_props}",
                supporting_refs=failed_props,
                severity=0.6,
                recommended_action="consider concept or theory refinement around required-property failure",
            )
        )

    # Candidate B: shortcut-trigger anomaly
    if any(shortcut_checks.values()):
        hit_shortcuts = [k for k, v in shortcut_checks.items() if v]
        candidates.append(
            AnomalyCandidate.create(
                task_family=task_family,
                source_type="shortcut_pattern",
                summary=f"Forbidden shortcuts triggered: {hit_shortcuts}",
                supporting_refs=hit_shortcuts,
                severity=0.7,
                recommended_action="strengthen anti-shortcut concept leverage or evaluation pressure",
            )
        )

    # Candidate C: contradiction-driven anomaly candidates
    for contradiction in contradictions:
        ctype = contradiction.get("contradiction_type", "unknown")
        if ctype in {"sufficient_evidence_but_failure", "framing_overlap_failure", "framing_mismatch"}:
            candidates.append(
                AnomalyCandidate.create(
                    task_family=task_family,
                    source_type="contradiction_pattern",
                    summary=f"Contradiction-derived anomaly candidate: {ctype}",
                    supporting_refs=[contradiction.get("id", "")],
                    severity=contradiction.get("severity", 0.5),
                    recommended_action="track recurrence across tasks before promoting to anomaly object",
                )
            )

    return candidates
