from __future__ import annotations

from typing import Any, Dict, Iterable, Sequence


FAMILY_EVIDENCE_MARKERS = {
    "comparison": [
        "supported by",
        "grounded by",
        "contrast",
        "difference",
        "better supported",
        "decisive",
    ],
    "synthesis": [
        "supported by",
        "grounded by",
        "evidence",
        "merge",
        "integrate",
        "observed",
        "inferred",
    ],
    "procedure": [
        "checklist",
        "labeled",
        "field",
        "structured",
        "layout",
        "operator",
        "handoff",
    ],
}


def _markers_for_family(family: str) -> list[str]:
    return FAMILY_EVIDENCE_MARKERS.get(family, [])


def _markers_for_secondary(families: Sequence[str]) -> list[str]:
    markers: list[str] = []
    for family in families:
        markers.extend(FAMILY_EVIDENCE_MARKERS.get(family, []))
    seen = set()
    dedup = []
    for marker in markers:
        if marker not in seen:
            seen.add(marker)
            dedup.append(marker)
    return dedup


def verify_output(
    task_family: str,
    output_text: str,
    framing_candidates: Iterable[str] | None = None,
    task_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized = output_text.lower()
    schema_ok = isinstance(output_text, str) and len(output_text.strip()) > 0

    candidate_families = list(framing_candidates or [])
    primary_markers = _markers_for_family(task_family)
    secondary_markers = _markers_for_secondary([f for f in candidate_families if f != task_family])

    primary_hit = any(marker in normalized for marker in primary_markers) if primary_markers else len(output_text) > 25
    secondary_hit = any(marker in normalized for marker in secondary_markers) if secondary_markers else False

    required_properties = (task_contract or {}).get("required_properties", [])
    forbidden_shortcuts = (task_contract or {}).get("forbidden_shortcuts", [])

    property_hits = {prop: _property_check(prop, normalized) for prop in required_properties}
    required_ok = all(property_hits.values()) if property_hits else primary_hit

    shortcut_hits = {shortcut: _shortcut_check(shortcut, normalized) for shortcut in forbidden_shortcuts}
    shortcuts_ok = not any(shortcut_hits.values())

    if task_family == "unknown" and not required_properties:
        evidence_ok = len(output_text) > 25
    else:
        evidence_ok = required_ok and primary_hit

    rule_ok = True
    good_enough = schema_ok and evidence_ok and rule_ok and shortcuts_ok
    return {
        "schema_checks": {"passed": schema_ok},
        "evidence_checks": {
            "passed": evidence_ok,
            "primary_hit": primary_hit,
            "secondary_hit": secondary_hit,
            "framing_candidates_used": candidate_families,
        },
        "property_checks": property_hits,
        "shortcut_checks": shortcut_hits,
        "rule_checks": {"passed": rule_ok},
        "verification_summary": {
            "good_enough": good_enough,
            "task_family": task_family,
        },
    }


def _property_check(prop: str, normalized: str) -> bool:
    mapping = {
        "explicit comparison": any(k in normalized for k in ["contrast", "difference", "better", "safer", "stronger"]),
        "evidence-backed choice": any(k in normalized for k in ["supported by", "grounded by", "evidence"]),
        "handoff-usable structure": any(k in normalized for k in ["checklist", "field", "structured", "layout"]),
        "evidence-grounded conclusion": any(k in normalized for k in ["supported by", "grounded by", "evidence"]),
        "fact vs inference separation": any(k in normalized for k in ["observed", "inferred"]),
        "stable structured layout": any(k in normalized for k in ["checklist", "field", "structured", "layout"]),
    }
    return mapping.get(prop, True)


def _shortcut_check(shortcut: str, normalized: str) -> bool:
    if shortcut == "generic preference without evidence":
        return ("better" in normalized or "safer" in normalized) and not any(k in normalized for k in ["supported by", "grounded by", "evidence"])
    if shortcut == "summary without distinction":
        summary_like = any(k in normalized for k in ["summary", "answer", "conclusion"])
        evidence_structure = any(k in normalized for k in ["supported by", "grounded by", "observed", "inferred", "contrast", "difference"])
        return summary_like and not evidence_structure
    if shortcut == "structure without a decision":
        return any(k in normalized for k in ["checklist", "field", "structured"]) and not any(k in normalized for k in ["better", "safer", "stronger", "contrast", "difference"])
    if shortcut == "decision without structure":
        return any(k in normalized for k in ["better", "safer", "stronger"]) and not any(k in normalized for k in ["checklist", "field", "structured", "layout"])
    return False


def is_good_enough(verification_state: Dict[str, Any]) -> bool:
    return bool(verification_state.get("verification_summary", {}).get("good_enough", False))


def verify_output_anomaly_aware(
    task_family: str,
    output_text: str,
    anomaly_severity: float = 0.0,
    framing_candidates: Iterable[str] | None = None,
    task_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Anomaly-aware verification that applies stricter checks when anomaly_severity > 0.5.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.8: Predictive Processing / Active Inference (Friston, 2010)
    ما الذي اخذناه؟
        عندما يرتفع خطا التنبؤ (anomaly_severity)، يجب ان يصبح النظام اكثر
        حذرا ودقة في قبول المخرجات - تماما كما يزيد الدماغ من دقة التحقق
        عند مواجهة مفاجات حسية.
    ما الذي لم ناخذه الان؟
        التحديث الديناميكي المستمر لعتبات القبول بناء على تاريخ كامل.
    ماذا اصبح عندنا؟
        دالة تحقق تشدد معاييرها عند ارتفاع شدة الشذوذ فوق 0.5:
        تتطلب نجاح كل الخصائص، وتطلب ضرب علامتين اوليتين بدلا من واحدة.

    المصدر 6.12: Ashby - Law of Requisite Variety (1956)
    ما الذي اخذناه؟
        anomaly pressure requires matched response variety: ضغط الشذوذ يتطلب
        تنوعا مطابقا في الاستجابة. التشديد هو شكل من اشكال زيادة تنوع الاستجابة.
    ما الذي لم ناخذه الان؟
        الحساب الكامل لتنوع الاستجابة المطلوب.
    ماذا اصبح عندنا؟
        تشديد يتناسب مع شدة الشذوذ المكتشف.
    """
    base_result = verify_output(
        task_family, output_text,
        framing_candidates=framing_candidates,
        task_contract=task_contract,
    )

    if anomaly_severity <= 0.5:
        base_result["anomaly_severity_applied"] = anomaly_severity
        return base_result

    # Stricter mode: anomaly_severity > 0.5
    normalized = output_text.lower()
    property_checks = base_result.get("property_checks", {})
    primary_markers = _markers_for_family(task_family)

    # Require ALL required_properties to pass (no partial credit)
    required_ok = all(property_checks.values()) if property_checks else True

    # Require at least 2 primary_markers to hit instead of 1
    primary_hits_count = sum(1 for marker in primary_markers if marker in normalized) if primary_markers else 0
    strict_primary_hit = primary_hits_count >= 2 if primary_markers else len(output_text) > 50

    # Add extra evidence markers requirement
    candidate_families = list(framing_candidates or [])
    secondary_markers = _markers_for_secondary([f for f in candidate_families if f != task_family])
    secondary_hit = any(marker in normalized for marker in secondary_markers) if secondary_markers else False

    shortcut_checks = base_result.get("shortcut_checks", {})
    shortcuts_ok = not any(shortcut_checks.values())

    schema_ok = base_result["schema_checks"]["passed"]
    strict_evidence_ok = required_ok and strict_primary_hit
    strict_good_enough = schema_ok and strict_evidence_ok and shortcuts_ok

    strict_result = dict(base_result)
    strict_result["evidence_checks"] = {
        "passed": strict_evidence_ok,
        "primary_hit": strict_primary_hit,
        "primary_hits_count": primary_hits_count,
        "secondary_hit": secondary_hit,
        "framing_candidates_used": candidate_families,
        "strict_mode": True,
    }
    strict_result["verification_summary"] = {
        "good_enough": strict_good_enough,
        "task_family": task_family,
        "anomaly_strict_mode": True,
    }
    strict_result["anomaly_severity_applied"] = anomaly_severity
    return strict_result


def verify_output_theory_guided(
    task_family: str,
    output_text: str,
    theory_prediction: dict,
    framing_candidates: Iterable[str] | None = None,
    task_contract: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Theory-guided verification that applies stricter checks when theory predicts failure or difficulty.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.8: Predictive Processing / Active Inference (Friston, 2010)
    ما الذي اخذناه؟
        عندما تتنبا النظرية بالفشل، يرتفع خطا التنبؤ المتوقع.
        النظام يشدد معايير القبول استباقيا بناء على تنبؤ النظرية
        تماما كما يشدد الدماغ التحقق عند توقع مفاجاة.
    ما الذي لم ناخذه الان؟
        التكامل الكامل بين تنبؤ النظرية وتنبؤ الشذوذ في نموذج واحد.
    ماذا اصبح عندنا؟
        دالة تحقق تشدد معاييرها عندما تتنبا النظرية بالفشل:
        تتطلب ضرب علامتين اوليتين ونجاح كل الخصائص.
        عند توقع الصعوبة فقط: تتطلب ضرب علامة ثانوية اضافية.

    المصدر 5.33: Popper - Falsifiability (1934)
    ما الذي اخذناه؟
        التنبؤ الصادر من النظرية يجب ان يؤثر على عملية التحقق.
        اذا تنبات النظرية بالفشل ونجحت المهمة، هذا دليل ضد النظرية.
        اذا تنبات بالفشل وفشلت المهمة فعلا، هذا يعزز النظرية.
    ما الذي لم ناخذه الان؟
        آلية تكذيب النظرية الكامل عند فشل تنبؤاتها المتكرر.
    ماذا اصبح عندنا؟
        تشديد التحقق المبني على تنبؤ النظرية يجعل الفشل اكثر قابلية للاكتشاف.
    """
    base_result = verify_output(
        task_family, output_text,
        framing_candidates=framing_candidates,
        task_contract=task_contract,
    )

    predicts_failure = theory_prediction.get("predicts_failure", False)
    predicts_difficulty = theory_prediction.get("predicts_difficulty", False)

    if not predicts_failure and not predicts_difficulty:
        base_result["theory_guided"] = False
        return base_result

    # Apply stricter checks based on theory prediction
    normalized = output_text.lower()
    property_checks = base_result.get("property_checks", {})
    primary_markers = _markers_for_family(task_family)
    candidate_families = list(framing_candidates or [])
    secondary_markers = _markers_for_secondary([f for f in candidate_families if f != task_family])

    schema_ok = base_result["schema_checks"]["passed"]
    shortcut_checks = base_result.get("shortcut_checks", {})
    shortcuts_ok = not any(shortcut_checks.values())

    if predicts_failure:
        # Strict mode: require 2 primary markers AND all properties
        required_ok = all(property_checks.values()) if property_checks else True
        primary_hits_count = sum(1 for marker in primary_markers if marker in normalized) if primary_markers else 0
        strict_primary_hit = primary_hits_count >= 2 if primary_markers else len(output_text) > 50
        strict_evidence_ok = required_ok and strict_primary_hit
    else:
        # Difficulty mode: base evidence + require secondary marker hit
        primary_hit = base_result["evidence_checks"]["passed"]
        secondary_hit = any(marker in normalized for marker in secondary_markers) if secondary_markers else True
        strict_evidence_ok = primary_hit and secondary_hit
        primary_hits_count = sum(1 for marker in primary_markers if marker in normalized) if primary_markers else 0
        strict_primary_hit = primary_hits_count >= 1 if primary_markers else True

    secondary_hit = any(marker in normalized for marker in secondary_markers) if secondary_markers else False
    strict_good_enough = schema_ok and strict_evidence_ok and shortcuts_ok

    strict_result = dict(base_result)
    strict_result["evidence_checks"] = {
        "passed": strict_evidence_ok,
        "primary_hit": strict_primary_hit,
        "primary_hits_count": primary_hits_count,
        "secondary_hit": secondary_hit,
        "framing_candidates_used": candidate_families,
        "theory_strict_mode": True,
        "theory_predicts_failure": predicts_failure,
        "theory_predicts_difficulty": predicts_difficulty,
    }
    strict_result["verification_summary"] = {
        "good_enough": strict_good_enough,
        "task_family": task_family,
        "theory_guided": True,
    }
    strict_result["theory_guided"] = True
    return strict_result
