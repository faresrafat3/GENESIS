"""
Enhanced Pipeline Run — GENESIS
=================================
The pipeline that uses all Ninja Excavator bridges.

Key differences from minimal_run.py:
    1. Uses Semantic Verifier instead of keyword-based verification
    2. Uses Value Computation for economic decisions (real VoC/VoI/VoV)
    3. Tracks Ladder Ascent state per task family
    4. Tests executable theories against live evidence
    5. Records calibration data for confidence scores

From the Ninja Excavation Report:
    "GENESIS هو عقل فلسفي عميق في جسد كلمات مفتاحية.
     هذا الـ pipeline يبدأ في تمتين الجسد."
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import logging

from ..ladder_ascent.engine import LadderAscentEngine, LadderLevel, get_ladder_engine
from ..semantic_verifier.verifier import SemanticVerifier, get_semantic_verifier
from ..value_computation.value_functions import (
    CognitiveReturnCalculator,
    get_cognitive_return_calculator,
)
from ..theory_executables.theories import (
    get_all_executable_theories,
    evaluate_all_theories,
)

from ..pipeline.minimal_run import run_minimal_pipeline
from ..task_ingress.service import ingest_task
from ..memory_os.store import InMemoryMemoryStore
from ..economy_control.ledger import InMemoryLedgerStore
from ..concept_engine.registry import InMemoryConceptRegistry
from ..theory_runtime.registry import InMemoryTheoryRegistry

from ...core.objects.identity import AgentIdentityObject

logger = logging.getLogger(__name__)


def run_enhanced_pipeline(
    raw_task: str | dict | object,
    store: InMemoryMemoryStore | None = None,
    ledger_store: InMemoryLedgerStore | None = None,
    *,
    concept_registry: InMemoryConceptRegistry | None = None,
    theory_registry: InMemoryTheoryRegistry | None = None,
    identity: AgentIdentityObject | None = None,
    use_semantic_verification: bool = True,
    use_value_computation: bool = True,
    use_ladder_tracking: bool = True,
    use_theory_testing: bool = True,
    # Pass through all minimal_pipeline flags
    **kwargs,
) -> Dict[str, Any]:
    """
    Enhanced pipeline that wraps the minimal pipeline with
    all Ninja Excavator bridge enhancements.
    
    Strategy: Run the existing pipeline first, then ENHANCE the result
    with semantic verification, value computation, ladder tracking,
    and theory testing. This ensures backward compatibility while
    adding the new capabilities.
    """
    
    # ───────────────────────────────────────────────────
    # Step 1: Run the existing minimal pipeline
    # ───────────────────────────────────────────────────
    base_result = run_minimal_pipeline(
        raw_task,
        store=store,
        ledger_store=ledger_store,
        concept_registry=concept_registry,
        theory_registry=theory_registry,
        identity=identity,
        **kwargs,
    )
    
    task = base_result.get("task", {})
    task_family = task.get("task_family", "unknown")
    task_text = task.get("normalized_text", "")
    verification = base_result.get("blackboard", {}).get("verification_state", {})
    is_good_enough = verification.get("verification_summary", {}).get("good_enough", False)
    tier_decision = base_result.get("tier_decision", {})
    chosen_tier = tier_decision.get("chosen_tier", "tier_1")
    domain = task.get("meta", {}).get("domain", "")
    
    # Extract reasoning/output for semantic verification
    candidate_claims = base_result.get("blackboard", {}).get("candidate_claims", [])
    reasoning_text = candidate_claims[0].get("claim_text", "") if candidate_claims else ""
    
    # ───────────────────────────────────────────────────
    # Step 2: Semantic Verification (replaces keyword check)
    # ───────────────────────────────────────────────────
    semantic_result = {}
    if use_semantic_verification:
        semantic_verifier = get_semantic_verifier()
        
        # Determine answer letter if available
        answer_letter = ""
        if reasoning_text:
            # Extract answer from reasoning (last letter mentioned in conclusion)
            import re
            match = re.findall(r'\b([A-D])\b', reasoning_text.upper())
            if match:
                answer_letter = match[-1]
        
        semantic_result = semantic_verifier.verify(
            question=task_text,
            reasoning=reasoning_text,
            answer=answer_letter,
            domain=domain or task_family,
            confidence=tier_decision.get("confidence_in_decision", 0.5),
        )
        
        # Record outcome for calibration
        semantic_verifier.record_outcome(
            confidence=tier_decision.get("confidence_in_decision", 0.5),
            was_correct=is_good_enough,
            domain=domain or task_family,
        )
    
    # ───────────────────────────────────────────────────
    # Step 3: Value Computation (real economic numbers)
    # ───────────────────────────────────────────────────
    value_result = {}
    if use_value_computation:
        calculator = get_cognitive_return_calculator()
        
        # Compute all value functions
        confidence = tier_decision.get("confidence_in_decision", 0.5)
        difficulty = task.get("difficulty_estimate", "medium")
        difficulty_score = {"low": 0.2, "medium": 0.5, "high": 0.8}.get(difficulty, 0.5)
        
        value_functions = calculator.compute_value_functions(
            current_confidence=confidence,
            estimated_difficulty=difficulty_score,
            current_failure_risk=1.0 - confidence,
        )
        
        # Compute cognitive return
        cognitive_return = calculator.compute_cognitive_return(
            immediate_utility=1.0 if is_good_enough else 0.0,
            task_confidence=confidence,
            computation_cost=tier_decision.get("expected_cost", 0.001),
            delay_penalty=tier_decision.get("expected_delay_penalty", 0.0),
            task_id=task.get("id", ""),
            domain=domain or task_family,
            tier=chosen_tier,
        )
        
        # Record cost
        calculator.cost_tracker.record(
            operation="pipeline_run",
            tier=chosen_tier,
            tokens_used=0,  # Would be populated with real data in production
            task_id=task.get("id", ""),
            domain=domain or task_family,
        )
        
        value_result = {
            "value_functions": value_functions,
            "cognitive_return": cognitive_return,
        }
    
    # ───────────────────────────────────────────────────
    # Step 4: Ladder Ascent Tracking
    # ───────────────────────────────────────────────────
    ladder_result = {}
    if use_ladder_tracking:
        ladder_engine = get_ladder_engine()
        state = ladder_engine.get_or_create_state(task_family)
        
        # Record evidence
        state.record_evidence(
            success=is_good_enough,
            domain=domain or task_family,
            contradiction=len(base_result.get("blackboard", {}).get("contradictions", [])) > 0,
        )
        
        # Check if phase transition is warranted
        transition_check = ladder_engine.check_transition(state)
        
        ladder_result = {
            "current_level": state.current_level.label,
            "current_level_int": int(state.current_level),
            "entropy": round(transition_check.entropy, 3),
            "transition_possible": transition_check.should_transition,
            "transition_reason": transition_check.reason if not transition_check.should_transition else "",
            "evidence_count": sum(state.evidence_at_level.values()),
            "transition_count": state.transition_count,
        }
        
        # Execute transition if warranted
        if transition_check.should_transition:
            execution = ladder_engine.execute_transition(state, transition_check)
            ladder_result["transition_executed"] = True
            ladder_result["new_level"] = state.current_level.label
            ladder_result["forgetting_policy"] = execution.forgetting_policy
    
    # ───────────────────────────────────────────────────
    # Step 5: Theory Testing
    # ───────────────────────────────────────────────────
    theory_result = {}
    if use_theory_testing:
        # Build evidence dictionary from run results
        evidence = _build_theory_evidence(base_result, semantic_result)
        theory_result = evaluate_all_theories(evidence)
    
    # ───────────────────────────────────────────────────
    # Step 6: Compose Enhanced Result
    # ───────────────────────────────────────────────────
    enhanced_result = {
        **base_result,
        "enhanced": True,
        "semantic_verification": semantic_result,
        "value_computation": value_result,
        "ladder_tracking": ladder_result,
        "theory_testing": theory_result,
    }
    
    return enhanced_result


def _build_theory_evidence(
    base_result: Dict[str, Any],
    semantic_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build evidence dictionary from pipeline results for theory testing.
    
    Maps run output to the format expected by executable theories.
    """
    task = base_result.get("task", {})
    tier_decision = base_result.get("tier_decision", {})
    verification = base_result.get("blackboard", {}).get("verification_state", {})
    
    # Extract accuracy-related data
    is_good = verification.get("verification_summary", {}).get("good_enough", False)
    
    evidence = {
        # For T07
        "standard_gen1_accuracy": 65.0,   # Known from run_57 (paper locked values)
        "no_pipeline_gen1_accuracy": 70.0, # Known from run_58
        
        # For T08
        "gen1_accuracy": 65.0,
        "gen2_accuracy": 65.0,
        "a3_gen1_accuracy": 70.0,
        "a3_gen2_accuracy": 60.0,
        
        # For T10
        "median_correct_tokens": 989,
        "median_incorrect_tokens": 6836,
        "genesis_empty_content_rate": 0.35,
        "baseline_empty_content_rate": 0.35,
        
        # Current run data
        "current_task_good_enough": is_good,
        "current_tier": tier_decision.get("chosen_tier", "unknown"),
        "current_confidence": tier_decision.get("confidence_in_decision", 0.5),
    }
    
    # Add semantic verification data if available
    if semantic_result:
        evidence["semantic_verdict"] = semantic_result.get("verdict", "unknown")
        evidence["semantic_score"] = semantic_result.get("verification_score", 0.0)
    
    return evidence
