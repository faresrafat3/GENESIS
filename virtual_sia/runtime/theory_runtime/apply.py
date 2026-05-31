from __future__ import annotations

from typing import Iterable, List

from ...core.objects.theory import LocalTheoryObject


def select_applicable_theories(task_family: str, theories: Iterable[LocalTheoryObject], limit: int = 1) -> List[LocalTheoryObject]:
    selected: List[LocalTheoryObject] = []
    for theory in theories:
        if task_family in theory.scope.task_families:
            selected.append(theory)
        if len(selected) >= limit:
            break
    return selected


def build_theory_hints(theories: Iterable[LocalTheoryObject]) -> list[str]:
    hints: list[str] = []
    for theory in theories:
        mechanism = theory.mechanism_claims[0] if theory.mechanism_claims else ""
        prescription = theory.prescriptive_implications[0] if theory.prescriptive_implications else ""
        hints.append(f"{theory.name}: {mechanism} {prescription}".strip())
    return hints


def _tokenize(text: str) -> set[str]:
    # NOTE: Known limitation - no stop-word filtering is applied. Common words like
    # "tasks", "with", "will" can cause spurious matches. This is acceptable for the
    # current prototype where the concept set is small and token overlap provides
    # sufficient signal. Full stop-word filtering is deferred to a future cycle.
    return {t.strip('.,:;!?()[]{}').lower() for t in text.split() if t.strip()}


_FAILURE_KEYWORDS = {"fail", "fails", "failure", "absent", "insufficient", "missing", "lack", "unable", "cannot"}
_DIFFICULTY_KEYWORDS = {"difficulty", "difficult", "complex", "complexity", "challenge", "challenging", "hard", "demanding"}


def get_theory_prediction_for_task(
    theory: LocalTheoryObject,
    task_family: str,
    task_text: str,
) -> dict:
    """Generate a prediction for a task based on theory's predictive claims.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 5.33: Popper - Falsifiability (1934)
    ما الذي اخذناه؟
        النظرية العلمية يجب ان تولد تنبؤات قابلة للتكذيب.
        كل نظرية محلية تولد تنبؤا محددا لكل مهمة: هل ستفشل؟ هل ستكون صعبة؟
        هذا التنبؤ قابل للتحقق والتكذيب بعد تنفيذ المهمة.
    ما الذي لم ناخذه الان؟
        الاختبارات المنهجية المتعددة لتكذيب النظرية بشكل كامل.
        لم ناخذ مفهوم الاستبعاد النهائي للنظرية عند التكذيب المتكرر.
    ماذا اصبح عندنا؟
        دالة تولد تنبؤا من كل نظرية محلية: predicts_difficulty و predicts_failure
        مع درجة ثقة مبنية على predictive_value.

    المصدر 5.37: Scientific Realism - Boyd (1983)
    ما الذي اخذناه؟
        النظريات الناجحة تنبؤيا تعكس بنية حقيقية في الواقع.
        كلما نجحت النظرية في التنبؤ، زادت ثقتنا بان ادعاءاتها تعكس واقع المهام.
    ما الذي لم ناخذه الان؟
        الجدل الفلسفي حول الواقعية مقابل الاداتية.
    ماذا اصبح عندنا؟
        confidence التنبؤ مبنية على predictive_value الفعلية للنظرية.
    """
    task_tokens = _tokenize(task_text)
    predicts_difficulty = False
    predicts_failure = False
    relevant_claims: list[str] = []

    for claim in theory.predictive_claims:
        claim_tokens = _tokenize(claim)
        overlap = task_tokens & claim_tokens
        if len(overlap) >= 1:
            relevant_claims.append(claim)
            claim_lower = claim.lower()
            claim_words = _tokenize(claim)
            if claim_words & _FAILURE_KEYWORDS:
                predicts_failure = True
            if claim_words & _DIFFICULTY_KEYWORDS:
                predicts_difficulty = True

    confidence = theory.predictive_value if relevant_claims else 0.0

    return {
        "predicts_difficulty": predicts_difficulty,
        "predicts_failure": predicts_failure,
        "confidence": confidence,
        "relevant_claims": relevant_claims,
    }


def update_theory_predictive_value(theory: LocalTheoryObject, prediction_correct: bool) -> None:
    """Update a theory's predictive value using Laplace smoothing after observing prediction outcome.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 5.34: Bayesian Epistemology - Howson & Urbach (1989)
    ما الذي اخذناه؟
        التحديث البايزي للمعتقدات: بعد كل ملاحظة، يتم تحديث درجة الثقة
        في النظرية بناء على نسبة التنبؤات الصحيحة.
        استخدمنا Laplace smoothing لتجنب القيم المتطرفة (0 او 1) في البداية.
    ما الذي لم ناخذه الان؟
        التحديث البايزي الكامل مع prior distributions واحتمالات شرطية.
        لم ناخذ التفريق بين انواع مختلفة من التنبؤات.
    ماذا اصبح عندنا؟
        دالة تحديث بسيطة: predictive_value = (correct + 1) / (total + 2)
        تبدا من 0.5 وتتحرك تدريجيا حسب الاداء التنبؤي الفعلي.
    """
    theory.prediction_count += 1
    if prediction_correct:
        theory.correct_predictions += 1
    theory.predictive_value = (theory.correct_predictions + 1) / (theory.prediction_count + 2)


def check_theory_explains_contradiction(theory: LocalTheoryObject, contradiction: dict) -> bool:
    """Check whether a theory's predictive claims can explain a detected contradiction.

    ## سرقة شرعية (Legitimate Theft)

    المصدر 6.2: Lakatos - Methodology of Scientific Research Programmes (1978)
    ما الذي اخذناه؟
        النظرية القوية تستطيع استيعاب الشذوذات وتفسيرها ضمن اطارها.
        اذا كانت ادعاءات النظرية التنبؤية تتداخل مع محتوى التناقض،
        فالنظرية تملك قوة تفسيرية لهذا التناقض.
    ما الذي لم ناخذه الان؟
        التفريق الكامل بين التعديلات التقدمية والتراجعية للنظرية.
        لم ناخذ مفهوم الحزام الواقي والنواة الصلبة بالكامل.
    ماذا اصبح عندنا؟
        فحص تداخل: اذا تقاطعت رموز ادعاءات النظرية مع محتوى التناقض
        (عتبة 2 رموز)، تزداد القوة التفسيرية بمقدار 0.1.

    المصدر 6.3: Kuhn - Structure of Scientific Revolutions (1962)
    ما الذي اخذناه؟
        النظرية السائدة (paradigm) تفسر الشذوذات طالما لم تتراكم بما يكفي
        لاحداث ثورة. النظرية التي تفسر التناقضات تتعزز قوتها.
    ما الذي لم ناخذه الان؟
        مفهوم الثورة العلمية الكاملة واستبدال النظرية.
    ماذا اصبح عندنا؟
        تعزيز explanatory_power عند التفسير الناجح (حد اقصى 1.0).
    """
    # Check scope match
    task_family = contradiction.get("task_family", "")
    if task_family and task_family not in theory.scope.task_families:
        return False

    # Collect contradiction content tokens
    content_parts = []
    for key in ("summary", "description", "content", "claim_text", "reason"):
        val = contradiction.get(key, "")
        if val:
            content_parts.append(str(val))
    contradiction_tokens = _tokenize(" ".join(content_parts))

    # Check overlap with predictive claims
    theory_tokens: set[str] = set()
    for claim in theory.predictive_claims:
        theory_tokens |= _tokenize(claim)

    overlap = contradiction_tokens & theory_tokens
    if len(overlap) >= 2:
        theory.explanatory_power = min(1.0, theory.explanatory_power + 0.1)
        return True

    return False
