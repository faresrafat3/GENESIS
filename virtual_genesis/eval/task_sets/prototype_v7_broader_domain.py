from __future__ import annotations

from typing import List

from ...core.objects.task_case import TaskCase
from ..perturbations.taskcase_variants import build_curriculum_from_cases


def _analysis_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="analysis")
    case.required_properties = ["causal chain identification", "evidence-backed root cause", "mechanism explanation"]
    case.forbidden_shortcuts = ["correlation without causation", "single-factor attribution"]
    case.diagnostic_purpose = ["domain_transfer", "analysis_depth", "causal_reasoning"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


def _extraction_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="extraction")
    case.required_properties = ["complete field extraction", "structured output format", "missing value handling"]
    case.forbidden_shortcuts = ["partial extraction", "unstructured dump"]
    case.diagnostic_purpose = ["domain_transfer", "extraction_completeness", "format_compliance"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


def _planning_case(prompt: str, critical: bool = False) -> TaskCase:
    case = TaskCase.create(prompt, expected_primary_family="planning")
    case.required_properties = ["sequenced steps", "constraint satisfaction", "dependency ordering"]
    case.forbidden_shortcuts = ["unordered list", "constraint ignorance"]
    case.diagnostic_purpose = ["domain_transfer", "planning_coherence", "constraint_handling"]
    case.target_thesis = ["thesis_1", "thesis_2"]
    case.criticality_class = "high" if critical else "medium"
    case.difficulty_class = "hard"
    return case


PROTOTYPE_V7_BROADER_DOMAIN_CASES: List[TaskCase] = [
    # Analysis (6 cases): causal reasoning, root cause analysis, system diagnosis
    _analysis_case(
        "Diagnose the root cause of the recurring system failure in the payment pipeline. Identify the causal chain from the initial trigger to the observable symptoms and explain why previous fixes did not address the underlying mechanism.",
        critical=True,
    ),
    _analysis_case(
        "Analyze why the deployment rollback failed last Thursday. Infer the contributing factors from the logs and explain the causal mechanism that led to data inconsistency.",
    ),
    _analysis_case(
        "Investigate the underlying cause of the latency spikes observed during peak hours. Provide a causal chain linking infrastructure changes to the degraded performance.",
    ),
    _analysis_case(
        "Explain why the automated scaling policy did not prevent the outage. Diagnose the contributing factors and identify which system failure mode was triggered.",
    ),
    _analysis_case(
        "Analyze the root cause of the authentication failures affecting mobile users. Trace the causal chain from the certificate rotation to the downstream impact.",
    ),
    _analysis_case(
        "Investigate why the batch processing job silently dropped records. Infer the mechanism from the available evidence and identify which contributing factor was most significant.",
    ),

    # Extraction (6 cases): pulling structured data from noisy text
    _extraction_case(
        "Extract structured incident data from the following unstructured operator notes. Pull out all relevant fields including timestamp, severity, affected systems, and resolution status. Provide structured output with explicit missing value markers.",
        critical=True,
    ),
    _extraction_case(
        "Identify entities and data points from the raw customer feedback dump. Extract all structured fields: product name, issue category, sentiment, and suggested action. Tabulate the results.",
    ),
    _extraction_case(
        "Parse fields from the mixed-format audit log entries below. Extract structured output containing user ID, action type, resource affected, and timestamp. Handle inconsistent formatting.",
    ),
    _extraction_case(
        "Pull out key information from the vendor contract text. Extract all structured data points including pricing tiers, SLA thresholds, penalty clauses, and renewal dates.",
    ),
    _extraction_case(
        "Extract all compliance-relevant data points from the regulatory filing. Identify entities, deadlines, required actions, and responsible parties. Produce structured output suitable for automated tracking.",
    ),
    _extraction_case(
        "Tabulate the key information from the mixed-language support tickets. Extract structured fields for each ticket: priority, category, assignee, and resolution time. Flag missing values explicitly.",
    ),

    # Planning (6 cases): multi-step plans with constraints
    _planning_case(
        "Plan the migration of the legacy database to the new cloud platform. Sequence the steps to respect data dependencies, minimize downtime constraints, and identify milestones for go/no-go decisions. Prioritize based on risk.",
        critical=True,
    ),
    _planning_case(
        "Create a multi-step deployment plan with rollback checkpoints. Schedule the sequence of service updates respecting inter-service dependencies and the constraint that no more than two services can be offline simultaneously.",
    ),
    _planning_case(
        "Plan the steps to onboard the new monitoring stack. Sequence tasks respecting infrastructure dependencies, timeline constraints from the vendor, and team availability milestones.",
    ),
    _planning_case(
        "Develop a roadmap for the security remediation effort. Prioritize the sequence of fixes based on severity, dependencies between patches, and the constraint that production cannot have more than one maintenance window per week.",
    ),
    _planning_case(
        "Plan the disaster recovery drill schedule for Q3. Sequence the multi-step exercises respecting team dependencies, facility constraints, and regulatory milestones that must be met by specific dates.",
    ),
    _planning_case(
        "Create a prioritized plan for resolving the technical debt backlog. Sequence the refactoring steps to respect code dependencies, minimize merge conflicts, and satisfy the timeline constraint of shipping the feature by month end.",
    ),
]


def build_v7_broader_domain_curriculum() -> List[TaskCase]:
    """Apply the extended 6-level curriculum to all v7 broader domain cases.

    Uses build_curriculum_from_cases with limit_per_case=6 to produce
    the full perturbation curriculum across all difficulty levels.
    """
    return build_curriculum_from_cases(PROTOTYPE_V7_BROADER_DOMAIN_CASES, limit_per_case=6)
