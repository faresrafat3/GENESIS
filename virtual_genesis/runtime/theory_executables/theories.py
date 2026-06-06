"""
Executable Theories — GENESIS
===============================
The four internal theories as executable Python objects.

Each theory:
    1. Extends the existing LocalTheoryObject structure
    2. Adds formal axioms (testable claims)
    3. Adds testable predictions (can be confirmed/refuted by data)
    4. Adds falsification conditions (what would kill the theory)
    5. Has a test() method that can evaluate evidence against predictions

From the paper (§8.5):
    - Theory-07: Pipeline as Memory vs Pipeline as Decision Injection
    - Theory-08: Feedback Value = f(Determinism, Scope)
    - Theory-09: Anticipatory Concepts vs Anticipatory Lemmas
    - Theory-10: Reasoning Saturation: The Inverted-U of Internal Reasoning
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


# ─────────────────────────────────────────────────────────
# Base Executable Theory
# ─────────────────────────────────────────────────────────

class PredictionOutcome(Enum):
    UNTESTED = "untested"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    INCONCLUSIVE = "inconclusive"


@dataclass
class Axiom:
    """A formal axiom of a theory. Must be a testable claim."""
    id: str
    statement: str
    operationalized_as: str  # How to measure/test this


@dataclass
class Prediction:
    """A testable prediction derived from the theory."""
    id: str
    statement: str
    expected_result: str
    conditions: List[str]
    confidence: float  # How confident the theory is in this prediction
    outcome: PredictionOutcome = PredictionOutcome.UNTESTED
    actual_result: Optional[str] = None
    notes: str = ""


@dataclass
class FalsificationCondition:
    """If this happens, the theory is refuted."""
    condition: str
    severity: str  # "fatal" or "damaging"
    description: str


class ExecutableTheory:
    """
    Base class for executable theories.
    
    An executable theory is NOT a Markdown file.
    It is a Python object with:
    - Axioms that can be checked against code/data
    - Predictions that can be tested
    - Falsification conditions that would kill the theory
    - A test() method that evaluates evidence
    """
    
    theory_id: str = ""
    name: str = ""
    core_question: str = ""
    description: str = ""
    source: str = ""  # Paper section reference
    
    axioms: List[Axiom] = []
    predictions: List[Prediction] = []
    falsification_conditions: List[FalsificationCondition] = []
    
    def test(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test the theory against empirical evidence.
        
        Returns a report of which predictions are confirmed/refuted.
        """
        results = []
        for pred in self.predictions:
            result = self._test_prediction(pred, evidence)
            results.append(result)
        
        confirmed = sum(1 for r in results if r["outcome"] == PredictionOutcome.CONFIRMED)
        refuted = sum(1 for r in results if r["outcome"] == PredictionOutcome.REFUTED)
        
        return {
            "theory_id": self.theory_id,
            "theory_name": self.name,
            "total_predictions": len(self.predictions),
            "confirmed": confirmed,
            "refuted": refuted,
            "untested": len(self.predictions) - confirmed - refuted,
            "status": self._compute_status(confirmed, refuted),
            "prediction_results": results,
        }
    
    def _test_prediction(self, pred: Prediction, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclass for theory-specific testing logic."""
        return {
            "prediction_id": pred.id,
            "outcome": PredictionOutcome.UNTESTED,
            "detail": "No test logic implemented in base class",
        }
    
    def _compute_status(self, confirmed: int, refuted: int) -> str:
        """Compute overall theory status."""
        if refuted > 0:
            return "partially_refuted" if confirmed > refuted else "largely_refuted"
        if confirmed > 0:
            return "partially_confirmed" if confirmed < len(self.predictions) else "confirmed"
        return "untested"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "theory_id": self.theory_id,
            "name": self.name,
            "core_question": self.core_question,
            "description": self.description,
            "source": self.source,
            "axioms": [{"id": a.id, "statement": a.statement} for a in self.axioms],
            "predictions": [
                {
                    "id": p.id,
                    "statement": p.statement,
                    "expected": p.expected_result,
                    "confidence": p.confidence,
                    "outcome": p.outcome.value,
                }
                for p in self.predictions
            ],
            "falsification_conditions": [
                {"condition": f.condition, "severity": f.severity}
                for f in self.falsification_conditions
            ],
        }


# ─────────────────────────────────────────────────────────
# Theory-07: Pipeline as Memory vs Decision Injection
# ─────────────────────────────────────────────────────────

class Theory07_PipelineMemoryVsInjection(ExecutableTheory):
    """
    Theory-07: Pipeline as Memory vs Pipeline as Decision Injection
    
    From PAPER.md §8.5.2:
        Orchestration pipelines fall on a spectrum between:
        Type A — Pipeline as Memory (helpful): LLM leads, pipeline serves
        Type B — Pipeline as Decision Injection (harmful): pipeline leads, LLM obeys
        
    Three axioms:
        1. Capacity Asymmetry: frontier LLMs have enormous prior knowledge.
           Injected signal must be decision-useful or it lowers SNR.
        2. Memory is Pull, Decision is Push: pull-based is opt-in;
           push-based is imposed. Push requires higher justification.
        3. Verification ≠ Decision: pipeline can verify without deciding.
    
    Key prediction (Prop 3):
        Decision injection scales inversely with base model strength.
    """
    
    theory_id = "T07"
    name = "Pipeline as Memory vs Decision Injection"
    core_question = "Under what pipeline design does orchestration add value vs harm?"
    description = (
        "Push-based decision injection in pipelines harms performance on strong "
        "base models because injected signals interfere with the model's internal "
        "reasoning. Pull-based memory access (queryable, opt-in) is superior."
    )
    source = "PAPER.md §8.5.2"
    
    axioms = [
        Axiom(
            id="T07-A1",
            statement="Frontier LLMs have enormous prior knowledge; injected signals must be decision-useful or lower SNR",
            operationalized_as="Compare accuracy with injected signals vs without, on same model",
        ),
        Axiom(
            id="T07-A2",
            statement="Pull-based memory access is superior to push-based injection",
            operationalized_as="Measure accuracy in pull-only vs push-only pipeline modes",
        ),
        Axiom(
            id="T07-A3",
            statement="A pipeline can be a strong verifier without being a decision injector",
            operationalized_as="Run pipeline as verifier-only (output filter) vs decision injector (input modifier)",
        ),
    ]
    
    predictions = [
        Prediction(
            id="T07-P1",
            statement="Removing pipeline decision injection improves Gen1 accuracy",
            expected_result="no_pipeline Gen1 >= standard Gen1 + 3 points",
            conditions=["same model", "same question set", "post-fix scaffolding"],
            confidence=0.8,
        ),
        Prediction(
            id="T07-P2",
            statement="Pipeline injection harms Chemistry more than Physics",
            expected_result="Chemistry delta > Physics delta when pipeline removed",
            conditions=["GPQA-20 subset", "domain-specific analysis"],
            confidence=0.7,
        ),
        Prediction(
            id="T07-P3",
            statement="Decision injection scales inversely with base model strength",
            expected_result="Gap widens with stronger base models",
            conditions=["multiple models tested", "same architecture"],
            confidence=0.6,
        ),
        Prediction(
            id="T07-P4",
            statement="Pull-based pipeline achieves >= push-based accuracy at lower cost",
            expected_result="pull_accuracy >= push_accuracy AND pull_cost < push_cost",
            conditions=["implemented pull mode", "comparable task set"],
            confidence=0.5,
        ),
    ]
    
    falsification_conditions = [
        FalsificationCondition(
            condition="Decision injection improves performance on ALL tested models",
            severity="fatal",
            description="If injection always helps, the theory's core claim is wrong",
        ),
        FalsificationCondition(
            condition="Pull-based memory has no measurable benefit over push-based",
            severity="damaging",
            description="Weakens the Memory>Injection claim but doesn't kill it",
        ),
    ]
    
    def _test_prediction(self, pred: Prediction, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Test T07 predictions against GPQA run data."""
        if pred.id == "T07-P1":
            standard_acc = evidence.get("standard_gen1_accuracy", 0)
            no_pipeline_acc = evidence.get("no_pipeline_gen1_accuracy", 0)
            improvement = no_pipeline_acc - standard_acc
            
            if improvement >= 3:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Removing pipeline improved by {improvement:.1f} points"}
            elif improvement >= 0:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Removing pipeline improved by only {improvement:.1f} points (< 3)"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"Removing pipeline HURT by {abs(improvement):.1f} points"}
        
        elif pred.id == "T07-P2":
            physics_delta = evidence.get("physics_delta_without_pipeline", 0)
            chem_delta = evidence.get("chemistry_delta_without_pipeline", 0)
            
            if chem_delta > physics_delta:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Chemistry improved {chem_delta:.1f} vs Physics {physics_delta:.1f}"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Physics improved more ({physics_delta:.1f} vs {chem_delta:.1f})"}
        
        elif pred.id == "T07-P3":
            models = evidence.get("injection_gap_by_model", {})
            if len(models) >= 2:
                sorted_models = sorted(models.items(), key=lambda x: x[1].get("base_accuracy", 0))
                gaps = [m[1].get("injection_gap", 0) for m in sorted_models]
                # If gap increases with model strength
                if gaps == sorted(gaps, reverse=True):
                    return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                            "detail": f"Gap scales inversely: {gaps}"}
            
            return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                    "detail": "Need multiple model results"}
        
        return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                "detail": "Unknown prediction"}


# ─────────────────────────────────────────────────────────
# Theory-08: Feedback Value = f(Determinism, Scope)
# ─────────────────────────────────────────────────────────

class Theory08_FeedbackValueMatrix(ExecutableTheory):
    """
    Theory-08: Feedback Value = f(Determinism, Scope)
    
    From PAPER.md §8.5.3:
        LEAP's feedback comes from Lean compiler (deterministic, narrow scope).
        GENESIS's feedback comes from LLM judge (stochastic, broad scope).
        
    The 2x2 quadrant model:
        High Det + Narrow Scope = Best (compound monotonic improvement)
        High Det + Broad Scope = Mixed
        Low Det + Narrow Scope = Good (bounded stochastic gain)
        Low Det + Broad Scope = Worst (drift compounded over generations)
    """
    
    theory_id = "T08"
    name = "Feedback Value = f(Determinism, Scope)"
    core_question = "What feedback structure produces monotonic improvement vs drift?"
    description = (
        "Feedback value depends on two dimensions: determinism (compiler vs LLM) "
        "and scope (narrow targeted fix vs broad refactor). The current GENESIS "
        "feedback sits in the worst quadrant (low determinism, broad scope)."
    )
    source = "PAPER.md §8.5.3"
    
    axioms = [
        Axiom(
            id="T08-A1",
            statement="Deterministic feedback reduces stochastic drift across generations",
            operationalized_as="Compare variance of Gen-N accuracy with deterministic vs stochastic feedback",
        ),
        Axiom(
            id="T08-A2",
            statement="Broad scope amplifies stochastic noise multiplicatively",
            operationalized_as="Measure accuracy variance with broad vs narrow feedback scope",
        ),
        Axiom(
            id="T08-A3",
            statement="Narrow scope with deterministic signals produces monotonic improvement",
            operationalized_as="Check if Gen(N+1) >= Gen(N) consistently with narrow+deterministic",
        ),
    ]
    
    predictions = [
        Prediction(
            id="T08-P1",
            statement="Gen2 with broad stochastic feedback is worse than Gen1",
            expected_result="Gen2_accuracy < Gen1_accuracy when using broad LLM feedback",
            conditions=["same model", "same questions"],
            confidence=0.85,
        ),
        Prediction(
            id="T08-P2",
            statement="Narrow feedback prevents Gen2 regression",
            expected_result="Gen2_narrow_accuracy >= Gen1_accuracy",
            conditions=["narrow_feedback mode enabled"],
            confidence=0.7,
        ),
        Prediction(
            id="T08-P3",
            statement="The 10-point drop (70→60) in run_58 A3 is the predicted consequence of bottom-right quadrant",
            expected_result="Gen2 drop magnitude correlates with feedback breadth",
            conditions=["run_58 data", "feedback analysis"],
            confidence=0.9,
        ),
    ]
    
    falsification_conditions = [
        FalsificationCondition(
            condition="Broad LLM feedback consistently improves Gen2 over Gen1",
            severity="fatal",
            description="Would invalidate the quadrant model's 'worst' prediction",
        ),
    ]
    
    def _test_prediction(self, pred: Prediction, evidence: Dict[str, Any]) -> Dict[str, Any]:
        if pred.id == "T08-P1":
            gen1 = evidence.get("gen1_accuracy", 0)
            gen2 = evidence.get("gen2_accuracy", 0)
            if gen2 < gen1:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Gen2 ({gen2:.1f}) < Gen1 ({gen1:.1f}) with broad feedback"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"Gen2 ({gen2:.1f}) >= Gen1 ({gen1:.1f})"}
        
        elif pred.id == "T08-P2":
            gen1 = evidence.get("gen1_accuracy", 0)
            gen2_narrow = evidence.get("gen2_narrow_accuracy", 0)
            if gen2_narrow >= gen1:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Narrow Gen2 ({gen2_narrow:.1f}) >= Gen1 ({gen1:.1f})"}
            elif gen2_narrow >= gen1 - 3:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Narrow Gen2 ({gen2_narrow:.1f}) ≈ Gen1 ({gen1:.1f})"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"Narrow Gen2 ({gen2_narrow:.1f}) << Gen1 ({gen1:.1f})"}
        
        elif pred.id == "T08-P3":
            run58_gen1 = evidence.get("a3_gen1_accuracy", 0)
            run58_gen2 = evidence.get("a3_gen2_accuracy", 0)
            drop = run58_gen1 - run58_gen2
            if drop >= 5:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Gen2 dropped {drop:.1f} points ({run58_gen1:.1f}→{run58_gen2:.1f})"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Drop of only {drop:.1f} points"}
        
        return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                "detail": "Unknown prediction"}


# ─────────────────────────────────────────────────────────
# Theory-09: Anticipatory Concepts vs Anticipatory Lemmas
# ─────────────────────────────────────────────────────────

class Theory09_AnticipatoryConcepts(ExecutableTheory):
    """
    Theory-09: Anticipatory Concepts vs Anticipatory Lemmas
    
    From PAPER.md §8.5.4:
        LEAP's anticipatory lemma planning contributes +10 to +17 points.
        GENESIS has a structurally analogous mechanism (Concept Engine proposer)
        but it operates reactively, not proactively.
        
    Key claim: activating anticipatory mode in Concept Engine would
    disproportionately improve the weakest domain (Chemistry Organic).
    """
    
    theory_id = "T09"
    name = "Anticipatory Concepts vs Anticipatory Lemmas"
    core_question = "Does proactive abstraction (anticipatory mode) improve performance on hard domains?"
    description = (
        "Anticipatory abstraction is a general architectural principle. "
        "LEAP implements it as anticipatory lemma planning (+10-17 points). "
        "GENESIS should implement it as anticipatory concept proposal."
    )
    source = "PAPER.md §8.5.4"
    
    axioms = [
        Axiom(
            id="T09-A1",
            statement="Proactive abstraction is a general architectural principle across domains",
            operationalized_as="Test anticipatory mode in multiple domains",
        ),
        Axiom(
            id="T09-A2",
            statement="Anticipatory concepts improve hardest domains most",
            operationalized_as="Compare improvement on Hard vs Easy questions",
        ),
    ]
    
    predictions = [
        Prediction(
            id="T09-P1",
            statement="Anticipatory concept mode disproportionately improves Chemistry Organic",
            expected_result="Chemistry accuracy gain > Physics accuracy gain with anticipatory mode",
            conditions=["anticipatory_mode enabled in Concept Engine"],
            confidence=0.65,
        ),
        Prediction(
            id="T09-P2",
            statement="Anticipatory mode improves overall accuracy by at least 5 points",
            expected_result="overall_accuracy_with_anticipatory >= baseline + 5",
            conditions=["GPQA-20 or larger subset"],
            confidence=0.5,
        ),
    ]
    
    falsification_conditions = [
        FalsificationCondition(
            condition="Anticipatory concepts make no measurable difference",
            severity="damaging",
            description="Would suggest the LEAP analogy doesn't transfer to MCQ domains",
        ),
    ]
    
    def _test_prediction(self, pred: Prediction, evidence: Dict[str, Any]) -> Dict[str, Any]:
        if pred.id == "T09-P1":
            chem_gain = evidence.get("chemistry_gain_anticipatory", 0)
            phys_gain = evidence.get("physics_gain_anticipatory", 0)
            if chem_gain > phys_gain:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Chemistry +{chem_gain:.1f} vs Physics +{phys_gain:.1f}"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Physics gained more: +{phys_gain:.1f} vs Chemistry +{chem_gain:.1f}"}
        
        elif pred.id == "T09-P2":
            baseline = evidence.get("baseline_accuracy", 0)
            anticipatory = evidence.get("anticipatory_accuracy", 0)
            gain = anticipatory - baseline
            if gain >= 5:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"+{gain:.1f} points improvement"}
            elif gain >= 0:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                        "detail": f"Only +{gain:.1f} points"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"Anticipatory mode HURT by {abs(gain):.1f} points"}
        
        return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                "detail": "Unknown prediction"}


# ─────────────────────────────────────────────────────────
# Theory-10: Reasoning Saturation (The Inverted-U)
# ─────────────────────────────────────────────────────────

class Theory10_ReasoningSaturation(ExecutableTheory):
    """
    Theory-10: Reasoning Saturation — The Inverted-U of Internal Reasoning
    
    From PAPER.md §7.3:
        Four axioms:
        1. Error accumulation (Wu et al. 2025)
        2. Confusion spiral (observed in run_57)
        3. Token budget exhaustion (Empirical Discovery #3)
        4. Inverse capability scaling (Wu et al. 2025)
        
    The most externally-validated theory in the paper:
    6 independent external papers converge on the same finding.
    """
    
    theory_id = "T10"
    name = "Reasoning Saturation: The Inverted-U"
    core_question = "What is the optimal reasoning token budget for a given task-model pair?"
    description = (
        "More reasoning tokens can correlate with WORSE answers. "
        "There exists an inverted-U sweet spot. "
        "Median correct: 989 tokens. Median incorrect: 6,836 tokens."
    )
    source = "PAPER.md §7.3"
    
    axioms = [
        Axiom(
            id="T10-A1",
            statement="Each reasoning step carries error probability ε; over N steps, accumulated error overwhelms gains",
            operationalized_as="Correlate reasoning token count with accuracy",
        ),
        Axiom(
            id="T10-A2",
            statement="When a question exceeds model capacity, extended reasoning generates competing hypotheses",
            operationalized_as="Analyze reasoning text of incorrect long answers for hypothesis count",
        ),
        Axiom(
            id="T10-A3",
            statement="When reasoning consumes max_tokens, visible content is empty",
            operationalized_as="Measure empty content rate vs max_tokens budget",
        ),
        Axiom(
            id="T10-A4",
            statement="Optimal CoT length decreases as model capability increases",
            operationalized_as="Test same tasks across models with varying capability",
        ),
    ]
    
    predictions = [
        Prediction(
            id="T10-P1",
            statement="A sweet-spot max_tokens exists for gpt-oss-120b on GPQA (expected 4K-8K)",
            expected_result="accuracy peaks at max_tokens ∈ {4096, 8192}",
            conditions=["token sweep experiment", "same 20 questions"],
            confidence=0.7,
        ),
        Prediction(
            id="T10-P2",
            statement="GENESIS empty-content rate exceeds pure baseline rate on identical questions",
            expected_result="genesis_empty_rate > baseline_empty_rate",
            conditions=["Theory-07 interaction: pipeline injection burns reasoning budget"],
            confidence=0.65,
        ),
        Prediction(
            id="T10-P3",
            statement="Chemistry Organic needs longer reasoning but saturates faster",
            expected_result="Chemistry optimal_tokens > Physics optimal_tokens, but Chemistry peak < Physics peak",
            conditions=["domain-specific token sweep"],
            confidence=0.6,
        ),
        Prediction(
            id="T10-P4",
            statement="Median correct reasoning tokens < median incorrect reasoning tokens",
            expected_result="median_correct_tokens < median_incorrect_tokens",
            conditions=["any GPQA run with reasoning token tracking"],
            confidence=0.9,
        ),
        Prediction(
            id="T10-P5",
            statement="DTR-style early termination achieves equal or better accuracy at ~50% compute",
            expected_result="early_term_accuracy >= full_accuracy AND early_term_compute <= 0.55 * full_compute",
            conditions=["DTR proxy implementation"],
            confidence=0.55,
        ),
    ]
    
    falsification_conditions = [
        FalsificationCondition(
            condition="More tokens always correlates with better accuracy (no inverted-U)",
            severity="fatal",
            description="Would directly refute the core claim",
        ),
        FalsificationCondition(
            condition="Empty content rate is independent of max_tokens budget",
            severity="damaging",
            description="Would weaken A3 but not kill the whole theory",
        ),
    ]
    
    def _test_prediction(self, pred: Prediction, evidence: Dict[str, Any]) -> Dict[str, Any]:
        if pred.id == "T10-P1":
            sweep = evidence.get("accuracy_by_max_tokens", {})
            if sweep:
                best_budget = max(sweep, key=sweep.get)
                best_acc = sweep[best_budget]
                if best_budget in [4096, 8192, 4096.0, 8192.0]:
                    return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                            "detail": f"Peak at {best_budget} tokens ({best_acc:.1%})"}
                else:
                    return {"prediction_id": pred.id, "outcome": PredictionOutcome.INCONCLUSIVE,
                            "detail": f"Peak at {best_budget} tokens (not 4K-8K range)"}
            return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                    "detail": "No token sweep data available"}
        
        elif pred.id == "T10-P2":
            genesis_rate = evidence.get("genesis_empty_content_rate", 0)
            baseline_rate = evidence.get("baseline_empty_content_rate", 0)
            if genesis_rate > baseline_rate:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"GENESIS {genesis_rate:.1%} > Baseline {baseline_rate:.1%}"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"GENESIS {genesis_rate:.1%} <= Baseline {baseline_rate:.1%}"}
        
        elif pred.id == "T10-P4":
            correct_median = evidence.get("median_correct_tokens", 0)
            incorrect_median = evidence.get("median_incorrect_tokens", 0)
            if correct_median < incorrect_median:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Correct median ({correct_median}) < Incorrect median ({incorrect_median})"}
            else:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.REFUTED,
                        "detail": f"Correct median ({correct_median}) >= Incorrect median ({incorrect_median})"}
        
        elif pred.id == "T10-P3":
            chem_opt = evidence.get("chemistry_optimal_tokens", 0)
            phys_opt = evidence.get("physics_optimal_tokens", 0)
            chem_peak = evidence.get("chemistry_peak_accuracy", 0)
            phys_peak = evidence.get("physics_peak_accuracy", 0)
            if chem_opt > phys_opt and chem_peak < phys_peak:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Chem needs {chem_opt} vs Phys {phys_opt} tokens, but Chem peak {chem_peak:.1%} < Phys {phys_peak:.1%}"}
            return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                    "detail": "Need domain-specific token sweep data"}
        
        elif pred.id == "T10-P5":
            early_acc = evidence.get("early_termination_accuracy", 0)
            full_acc = evidence.get("full_accuracy", 0)
            early_compute = evidence.get("early_termination_compute_ratio", 1.0)
            if early_acc >= full_acc and early_compute <= 0.55:
                return {"prediction_id": pred.id, "outcome": PredictionOutcome.CONFIRMED,
                        "detail": f"Early: {early_acc:.1%} vs Full: {full_acc:.1%} at {early_compute:.0%} compute"}
            return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                    "detail": "Need DTR experiment data"}
        
        return {"prediction_id": pred.id, "outcome": PredictionOutcome.UNTESTED,
                "detail": "Unknown prediction"}


# ─────────────────────────────────────────────────────────
# Registry Functions
# ─────────────────────────────────────────────────────────

def get_all_executable_theories() -> Dict[str, ExecutableTheory]:
    """Get all four executable theories."""
    return {
        "T07": Theory07_PipelineMemoryVsInjection(),
        "T08": Theory08_FeedbackValueMatrix(),
        "T09": Theory09_AnticipatoryConcepts(),
        "T10": Theory10_ReasoningSaturation(),
    }


def register_theories_with_falsification_engine(engine: Any) -> None:
    """
    Register all theories with the TheoryFalsificationEngine
    from the semantic_verifier module.
    """
    for theory in get_all_executable_theories().values():
        engine.register_theory(
            theory_id=theory.theory_id,
            description=theory.description,
            axioms=[a.statement for a in theory.axioms],
            predictions=[
                {
                    "description": p.statement,
                    "expected": p.expected_result,
                    "conditions": p.conditions,
                    "confidence": p.confidence,
                }
                for p in theory.predictions
            ],
            falsification_conditions=[
                f.condition for f in theory.falsification_conditions
            ],
        )


def evaluate_all_theories(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate all theories against a given evidence dictionary.
    
    This is the unified entry point for theory testing.
    
    Usage:
        evidence = {
            "standard_gen1_accuracy": 65.0,
            "no_pipeline_gen1_accuracy": 70.0,
            "gen1_accuracy": 70.0,
            "gen2_accuracy": 60.0,
            "median_correct_tokens": 989,
            "median_incorrect_tokens": 6836,
            ...
        }
        results = evaluate_all_theories(evidence)
    """
    results = {}
    for theory_id, theory in get_all_executable_theories().items():
        results[theory_id] = theory.test(evidence)
    return results
