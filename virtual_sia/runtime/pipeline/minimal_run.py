from __future__ import annotations

from ...core.objects.ledger import LedgerEntry
from ...core.objects.memory import MemoryUnit
from ..anomaly_runtime.service import extract_anomaly_candidates, compute_anomaly_severity_score, matches_known_anomaly_pattern
from ..blackboard_core.service import attach_context, close_blackboard, create_blackboard, snapshot_blackboard
from ..concept_engine.registry import InMemoryConceptRegistry
from ..contradiction_runtime.service import detect_contradictions
from ..economy_control.escalation import should_escalate, should_escalate_anomaly_aware
from ..economy_control.ledger import InMemoryLedgerStore
from ..economy_control.router import choose_tier, choose_tier_anomaly_aware, choose_tier_theory_guided
from ..memory_os.retriever import retrieve_memory
from ..memory_os.store import InMemoryMemoryStore
from ..memory_os.forgetting_policy import apply_forgetting_policy
from ..reasoning_runtime.service import run_reasoning
from ..task_ingress.service import ingest_task
from ..theory_runtime.registry import InMemoryTheoryRegistry
from ..theory_runtime.apply import select_applicable_theories, get_theory_prediction_for_task, update_theory_predictive_value, check_theory_explains_contradiction
from ..verification_runtime.service import is_good_enough, verify_output, verify_output_anomaly_aware, verify_output_theory_guided


def run_minimal_pipeline(
    raw_task: str | dict | object,
    store: InMemoryMemoryStore | None = None,
    ledger_store: InMemoryLedgerStore | None = None,
    *,
    use_memory: bool = True,
    use_economy: bool = True,
    forced_tier: str | None = None,
    concept_registry: InMemoryConceptRegistry | None = None,
    theory_registry: InMemoryTheoryRegistry | None = None,
    use_concepts: bool = False,
    use_anomaly_leverage: bool = False,
    use_theory_leverage: bool = False,
    use_productive_forgetting: bool = False,
) -> dict:
    store = store or InMemoryMemoryStore()
    ledger_store = ledger_store or InMemoryLedgerStore()
    concept_registry = concept_registry or InMemoryConceptRegistry()
    theory_registry = theory_registry or InMemoryTheoryRegistry()

    task = ingest_task(raw_task)
    blackboard = create_blackboard(task)
    attach_context(blackboard, user_context_summary="prototype run", tool_availability=["local"], constraints=[])
    ranked_frames = list((task.meta or {}).get("ranked_frames", []))
    secondary_frames = list((task.meta or {}).get("secondary_frames", []))
    task_contract = (task.meta or {}).get("normalized_envelope", {})
    blackboard.situation_model.candidate_frames = ranked_frames
    if (task.meta or {}).get("family_ambiguity"):
        blackboard.situation_model.uncertainties.append("task framing ambiguity detected")

    concept_items = concept_registry.list_concepts() if use_concepts else []
    theory_items = theory_registry.list_theories()
    family_candidates = [task.task_family] + secondary_frames

    # Apply decay if productive forgetting is enabled
    if use_productive_forgetting:
        store.apply_decay(0.05)

    memory_pack = retrieve_memory(
        task.task_family,
        task.normalized_text,
        store.all(),
        budget=3,
        concept_items=concept_items,
        theory_items=theory_items,
        family_candidates=family_candidates,
        task_contract=task_contract,
        active_only=use_productive_forgetting,
    ) if use_memory else retrieve_memory(task.task_family, task.normalized_text, [], budget=0, concept_items=concept_items, theory_items=theory_items, family_candidates=family_candidates, task_contract=task_contract, active_only=use_productive_forgetting)
    blackboard.retrieved_memory_pack = memory_pack

    # Compute anomaly severity from previous anomaly candidates if anomaly leverage is enabled
    anomaly_severity = 0.0
    if use_anomaly_leverage:
        from ...core.objects.anomaly import AnomalyCandidate
        previous_anomaly_candidates: list[AnomalyCandidate] = []
        for mem in store.all():
            mem_meta = mem.meta or {}
            if not mem_meta.get("good_enough", True):
                # Reconstruct lightweight candidates from failed episodic memories
                prop_checks = mem_meta.get("property_checks", {})
                shortcut_checks = mem_meta.get("shortcut_checks", {})
                mem_family = mem_meta.get("task_family", "unknown")
                if prop_checks and not all(prop_checks.values()):
                    previous_anomaly_candidates.append(
                        AnomalyCandidate.create(
                            task_family=mem_family,
                            source_type="property_gap",
                            summary="historical property failure",
                            severity=0.6,
                        )
                    )
                if any(shortcut_checks.values()):
                    previous_anomaly_candidates.append(
                        AnomalyCandidate.create(
                            task_family=mem_family,
                            source_type="shortcut_pattern",
                            summary="historical shortcut trigger",
                            severity=0.7,
                        )
                    )
        anomaly_severity = compute_anomaly_severity_score(previous_anomaly_candidates)

    # Compute theory prediction if theory leverage is enabled
    theory_prediction = None
    active_theory = None
    if use_theory_leverage:
        applicable_theories = select_applicable_theories(task.task_family, theory_items)
        if applicable_theories:
            active_theory = applicable_theories[0]
            theory_prediction = get_theory_prediction_for_task(
                active_theory, task.task_family, task.normalized_text
            )

    if forced_tier is not None:
        tier_decision = choose_tier(task, blackboard, memory_pack)
        tier_decision.chosen_tier = forced_tier
        tier_decision.decision_reason = f"forced tier: {forced_tier}"
    elif use_economy:
        # Theory leverage applies first, then anomaly leverage layers on top
        if use_theory_leverage and theory_prediction and (theory_prediction["predicts_difficulty"] or theory_prediction["predicts_failure"]):
            tier_decision = choose_tier_theory_guided(task, blackboard, memory_pack, theory_prediction=theory_prediction)
            # Layer anomaly on top of theory-guided decision if both are active
            if use_anomaly_leverage and anomaly_severity > 0:
                if anomaly_severity > 0.7:
                    tier_decision.chosen_tier = "tier_2"
                    tier_decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} forces tier_2"
                elif anomaly_severity > 0.4 and tier_decision.chosen_tier == "tier_0":
                    tier_decision.chosen_tier = "tier_1"
                    tier_decision.decision_reason += f"; anomaly_severity={anomaly_severity:.2f} prevents tier_0"
        elif use_anomaly_leverage and anomaly_severity > 0:
            tier_decision = choose_tier_anomaly_aware(task, blackboard, memory_pack, anomaly_severity=anomaly_severity)
        else:
            tier_decision = choose_tier(task, blackboard, memory_pack)
    else:
        tier_decision = choose_tier(task, blackboard, memory_pack)
        tier_decision.chosen_tier = "tier_1"
        tier_decision.decision_reason = "fixed default tier without economy-aware routing"

    reasoning = run_reasoning(
        task.normalized_text,
        task.task_family,
        memory_pack,
        chosen_tier=tier_decision.chosen_tier,
        framing_candidates=family_candidates,
    )
    blackboard.candidate_claims = reasoning["candidate_claims"]

    # Verification: theory-guided first, then anomaly-aware layers on top
    if use_theory_leverage and theory_prediction and (theory_prediction["predicts_difficulty"] or theory_prediction["predicts_failure"]):
        verification = verify_output_theory_guided(
            task.task_family,
            blackboard.candidate_claims[0]["claim_text"],
            theory_prediction=theory_prediction,
            framing_candidates=family_candidates,
            task_contract=task_contract,
        )
        # Layer anomaly-aware on top if both active
        if use_anomaly_leverage and anomaly_severity > 0.5:
            anomaly_verification = verify_output_anomaly_aware(
                task.task_family,
                blackboard.candidate_claims[0]["claim_text"],
                anomaly_severity=anomaly_severity,
                framing_candidates=family_candidates,
                task_contract=task_contract,
            )
            # Take the stricter result
            if not anomaly_verification["verification_summary"]["good_enough"]:
                verification = anomaly_verification
    else:
        verification = verify_output_anomaly_aware(
            task.task_family,
            blackboard.candidate_claims[0]["claim_text"],
            anomaly_severity=anomaly_severity if use_anomaly_leverage else 0.0,
            framing_candidates=family_candidates,
            task_contract=task_contract,
        )
    blackboard.verification_state = verification
    blackboard.contradictions = [c.to_dict() for c in detect_contradictions(task, verification, tier_decision)]

    pre_escalation_snapshot = snapshot_blackboard(blackboard, phase="post_verification", reason="before escalation decision")

    final_tier = tier_decision.chosen_tier
    if use_economy:
        if use_anomaly_leverage and anomaly_severity > 0:
            escalation = should_escalate_anomaly_aware(task, verification, current_tier=final_tier, anomaly_severity=anomaly_severity)
        else:
            escalation = should_escalate(task, verification, current_tier=final_tier)
    else:
        escalation = {
            "escalate": False,
            "target_tier": None,
            "reason": "economy-aware escalation disabled",
            "expected_value": 0.0,
            "blockers": [],
        }

    if escalation["escalate"]:
        final_tier = escalation["target_tier"]
        escalated_reasoning = run_reasoning(
            task.normalized_text,
            task.task_family,
            memory_pack,
            chosen_tier=final_tier,
            framing_candidates=family_candidates,
        )
        blackboard.candidate_claims = escalated_reasoning["candidate_claims"]
        if use_theory_leverage and theory_prediction and (theory_prediction["predicts_difficulty"] or theory_prediction["predicts_failure"]):
            verification = verify_output_theory_guided(
                task.task_family,
                blackboard.candidate_claims[0]["claim_text"],
                theory_prediction=theory_prediction,
                framing_candidates=family_candidates,
                task_contract=task_contract,
            )
            if use_anomaly_leverage and anomaly_severity > 0.5:
                anomaly_verification = verify_output_anomaly_aware(
                    task.task_family,
                    blackboard.candidate_claims[0]["claim_text"],
                    anomaly_severity=anomaly_severity,
                    framing_candidates=family_candidates,
                    task_contract=task_contract,
                )
                if not anomaly_verification["verification_summary"]["good_enough"]:
                    verification = anomaly_verification
        else:
            verification = verify_output_anomaly_aware(
                task.task_family,
                blackboard.candidate_claims[0]["claim_text"],
                anomaly_severity=anomaly_severity if use_anomaly_leverage else 0.0,
                framing_candidates=family_candidates,
                task_contract=task_contract,
            )
        blackboard.verification_state = verification
        blackboard.contradictions = [c.to_dict() for c in detect_contradictions(task, verification, tier_decision)]
        reasoning = escalated_reasoning
        snapshot_blackboard(blackboard, phase="post_escalation", reason=escalation["reason"])

    ledger = LedgerEntry.create(task_ref=task.id, phase="answering", action_type="reasoning_and_verification")
    ledger.tier_used = final_tier
    ledger.estimated_cost = tier_decision.expected_cost
    ledger.estimated_immediate_gain = tier_decision.expected_immediate_gain
    ledger.estimated_reuse_gain = tier_decision.expected_reuse_gain
    ledger.actual_cost_profile = reasoning["cost_profile"]
    ledger.actual_immediate_effect = f"good_enough={is_good_enough(verification)}"
    ledger.notes = tier_decision.decision_reason
    ledger_store.record_cognitive_spend(ledger)

    anomaly_candidates = [a.to_dict() for a in extract_anomaly_candidates({
        "task": task.to_dict(),
        "blackboard": blackboard.to_dict(),
        "ledger": ledger.to_dict(),
    })]

    # Theory leverage post-processing: update predictive value and check contradiction explanations
    if use_theory_leverage and active_theory and theory_prediction:
        # Determine if prediction was correct
        # NOTE: Known simplification for this cycle - both predicts_failure and
        # predicts_difficulty use the same condition (not actual_good_enough) to
        # determine correctness. This conflates severity levels but is intentionally
        # simple for the initial implementation. Full differentiation (e.g. difficulty
        # confirmed by escalation needed vs outright failure) is deferred to a future cycle.
        actual_good_enough = verification["verification_summary"]["good_enough"]
        if theory_prediction["predicts_failure"]:
            prediction_correct = not actual_good_enough
        elif theory_prediction["predicts_difficulty"]:
            prediction_correct = not actual_good_enough
        else:
            prediction_correct = actual_good_enough
        update_theory_predictive_value(active_theory, prediction_correct)

        # Check if theory explains any contradictions
        for contradiction_dict in blackboard.contradictions:
            check_theory_explains_contradiction(active_theory, contradiction_dict)

    episode_memory = MemoryUnit.create(
        summary=f"Task {task.task_family} finished with good_enough={verification['verification_summary']['good_enough']} on {final_tier}",
        memory_type="episodic",
    )
    episode_memory.scope.task_families = [task.task_family]
    episode_memory.meta = {
        "task_family": task.task_family,
        "good_enough": verification["verification_summary"]["good_enough"],
        "tier_used": final_tier,
        "used_memory": use_memory,
        "used_economy": use_economy,
        "used_concepts": use_concepts,
        "use_productive_forgetting": use_productive_forgetting,
        "secondary_frames": secondary_frames,
        "ranked_frames": ranked_frames,
        "required_properties": task_contract.get("required_properties", []),
        "forbidden_shortcuts": task_contract.get("forbidden_shortcuts", []),
        "property_checks": verification.get("property_checks", {}),
        "shortcut_checks": verification.get("shortcut_checks", {}),
    }
    store.store_memory(episode_memory)

    # Apply forgetting policy if enabled and store has enough memories
    forgetting_report = None
    if use_productive_forgetting and len(store.get_active_memories()) > 10:
        forgetting_report = apply_forgetting_policy(store)

    close_blackboard(
        blackboard,
        {
            "task_outcome": verification['verification_summary']['good_enough'],
            "lessons_to_extract": [],
            "candidate_concepts": [],
            "candidate_contradictions": blackboard.contradictions,
            "candidate_anomalies": anomaly_candidates,
        },
    )

    return {
        "task": task.to_dict(),
        "blackboard": blackboard.to_dict(),
        "snapshot": pre_escalation_snapshot.state_copy,
        "tier_decision": tier_decision.to_dict(),
        "escalation": escalation,
        "ledger": ledger.to_dict(),
        "stored_memory": episode_memory.to_dict(),
        "concept_count": len(concept_registry.list_concepts()),
        "used_concepts_count": len(memory_pack.concept_refs),
        "anomaly_candidates": anomaly_candidates,
        "used_theories_count": len(memory_pack.theory_refs),
        "anomaly_severity": anomaly_severity,
        "use_anomaly_leverage": use_anomaly_leverage,
        "use_theory_leverage": use_theory_leverage,
        "theory_prediction": theory_prediction,
        "theory_predictive_value": active_theory.predictive_value if active_theory else None,
        "forgetting_report": forgetting_report,
    }
