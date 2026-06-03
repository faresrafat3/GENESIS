"""Tests for the adversarial validation harness (strict scoring).

No real API calls are made; all LLM interaction is bypassed by calling the
pure scorer directly with synthetic responses.
"""
from __future__ import annotations

from virtual_genesis.eval.task_sets.adversarial_hard_cases import (
    ADVERSARIAL_HARD_CASES,
    get_adversarial_cases,
)
from virtual_genesis.eval.runners.run_adversarial_llm_eval import score_strict, _aggregate


def _task(task_id: str) -> dict:
    return next(t for t in ADVERSARIAL_HARD_CASES if t["id"] == task_id)


# --------------------------------------------------------------- task set sanity
class TestAdversarialTaskSet:
    def test_has_six_cases(self):
        assert len(ADVERSARIAL_HARD_CASES) == 6

    def test_three_families_covered(self):
        fams = {t["family"] for t in ADVERSARIAL_HARD_CASES}
        assert fams == {"comparison", "synthesis", "procedure"}

    def test_every_case_has_strict_failure_markers(self):
        for t in ADVERSARIAL_HARD_CASES:
            assert t["strict_failure_markers"], f"{t['id']} missing strict markers"

    def test_every_case_has_hints(self):
        for t in ADVERSARIAL_HARD_CASES:
            assert t["concept_hints"] and t["theory_hints"]

    def test_getter_returns_same(self):
        assert get_adversarial_cases() is ADVERSARIAL_HARD_CASES


# --------------------------------------------------------------- comparison
class TestComparisonScoring:
    def test_preference_shortcut_fails(self):
        task = _task("adv-cmp-1")
        resp = "I'd personally prefer PostgreSQL, it just feels right for most startups."
        sc = score_strict(resp, task)
        assert sc["shortcut_taken"] is True
        assert sc["good_enough"] is False

    def test_evidence_backed_passes(self):
        task = _task("adv-cmp-1")
        resp = (
            "PostgreSQL provides ACID transactional guarantees and strong schema "
            "consistency, whereas MongoDB offers schema flexibility and higher write "
            "throughput. Because the startup needs transactional integrity, the decisive "
            "difference is the transaction guarantee."
        )
        sc = score_strict(resp, task)
        assert sc["shortcut_taken"] is False
        assert sc["evidence_explicit"] is True
        assert sc["good_enough"] is True

    def test_verdict_only_fails(self):
        task = _task("adv-cmp-2")
        resp = "GraphQL is better overall, hands down."
        sc = score_strict(resp, task)
        assert sc["good_enough"] is False


# --------------------------------------------------------------- synthesis
class TestSynthesisScoring:
    def test_smoothed_causation_fails(self):
        task = _task("adv-syn-1")
        resp = "In summary, the config push caused the CPU spike which led to the complaints."
        sc = score_strict(resp, task)
        assert sc["shortcut_taken"] is True
        assert sc["good_enough"] is False

    def test_labeled_fact_inference_passes(self):
        task = _task("adv-syn-1")
        resp = (
            "Observed: CPU hit 95% at 14:02; a config push landed at 14:00; complaints "
            "started at 14:10. Inference: the timing suggests the config push is a likely "
            "trigger, but this remains unresolved without a rollback test."
        )
        sc = score_strict(resp, task)
        assert sc["evidence_explicit"] is True
        assert sc["good_enough"] is True

    def test_conflict_smoothing_fails(self):
        task = _task("adv-syn-2")
        resp = "Overall the takeaway is that it was likely a mix of both factors."
        sc = score_strict(resp, task)
        assert sc["good_enough"] is False


# --------------------------------------------------------------- procedure
class TestProcedureScoring:
    def test_prose_fails(self):
        task = _task("adv-prc-1")
        resp = "Here's what happened: at 09:12 a SEV2 hit auth-service and it's mitigated now."
        sc = score_strict(resp, task)
        assert sc["shortcut_taken"] is True
        assert sc["good_enough"] is False

    def test_labeled_fields_pass(self):
        task = _task("adv-prc-1")
        resp = (
            "timestamp: 09:12\nseverity: SEV2\nservice: auth-service\n"
            "status: mitigated\nowner: Lina"
        )
        sc = score_strict(resp, task)
        assert sc["structure_explicit"] is True
        assert sc["good_enough"] is True

    def test_numbered_ordered_steps_pass(self):
        task = _task("adv-prc-2")
        resp = "1. drain traffic\n2. restart the node\n3. verify health\n4. page on-call if red"
        sc = score_strict(resp, task)
        assert sc["structure_explicit"] is True
        assert sc["good_enough"] is True


# --------------------------------------------------------------- error + aggregate
class TestErrorAndAggregate:
    def test_llm_error_is_not_good(self):
        task = _task("adv-cmp-1")
        sc = score_strict("[LLM_ERROR] URLError: timeout", task)
        assert sc["error"] is True
        assert sc["good_enough"] is False

    def test_aggregate_computes_rates(self):
        runs = [
            {"conditions": {
                "A_raw": {"score": {"good_enough": False, "shortcut_taken": True, "evidence_explicit": False}},
                "B_concept": {"score": {"good_enough": True, "shortcut_taken": False, "evidence_explicit": True}},
                "C_concept_theory": {"score": {"good_enough": True, "shortcut_taken": False, "evidence_explicit": True}},
            }},
        ]
        agg = _aggregate(runs)
        assert agg["A_raw"]["success_rate"] == 0.0
        assert agg["B_concept"]["success_rate"] == 1.0
        assert agg["C_concept_theory"]["success_rate"] == 1.0
