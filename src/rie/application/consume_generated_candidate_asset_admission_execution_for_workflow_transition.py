from __future__ import annotations

from datetime import datetime
from typing import Callable

from rie.domain.creative_workflow_event import (
    EvidenceReference,
    InstructionReference,
    ResponsibleActorOrServiceReference,
    WorkflowContractReference,
    WorkflowState,
)
from rie.domain.evaluate_governed_creative_workflow_transition import (
    CampaignContextReference,
    GovernedCreativeWorkflowTransitionEvaluation,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_asset_admission_execution import (
    ADMISSION_OUTCOME_ADMITTED,
    GeneratedCandidateAssetAdmissionExecution,
)
from rie.domain.generated_candidate_asset_admission_workflow_transition_consumption import (
    GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption,
    derive_generated_candidate_asset_admission_workflow_transition_consumption_id,
    derive_workflow_transition_evaluation_sha256,
)
from rie.domain.governed_creative_workflow_result import BoundReference


WorkflowTransitionEvaluator = Callable[
    ...,
    GovernedCreativeWorkflowTransitionEvaluation,
]


def _require_ascii_nonempty(value: object, name: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} must be an exact str")
    if not value or value != value.strip():
        raise ValueError(f"{name} must be nonempty with no surrounding whitespace")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be ASCII") from exc
    return value


def _require_aware_datetime(value: object, name: str) -> datetime:
    if type(value) is not datetime:
        raise ValueError(f"{name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _expected_admission_provenance(
    admission_execution: GeneratedCandidateAssetAdmissionExecution,
) -> tuple[str, ...]:
    return (
        f"candidate_sha256:{admission_execution.candidate_checksum}",
        f"evaluation_id:{admission_execution.evaluation_id}",
        f"decision_id:{admission_execution.decision_id}",
        f"authorization_sha256:{admission_execution.authorization_id}",
        f"admitted_asset_reference:{admission_execution.admitted_asset_reference}",
        (
            "asset_admission_execution_sha256:"
            f"{admission_execution.asset_admission_execution_id}"
        ),
    )


def _bind_admitted_asset_reference(
    *,
    project_context_reference: str,
    campaign_context_reference: CampaignContextReference,
    admitted_asset_reference: str,
    accepted_governed_asset_reference: BoundReference | None,
) -> BoundReference:
    project = _require_ascii_nonempty(
        project_context_reference,
        "project_context_reference",
    )
    if type(campaign_context_reference) is not tuple or len(
        campaign_context_reference
    ) != 2:
        raise ValueError(
            "campaign_context_reference must be an exact two-value tuple"
        )
    campaign_project = _require_ascii_nonempty(
        campaign_context_reference[0],
        "campaign_context_reference[0]",
    )
    campaign = _require_ascii_nonempty(
        campaign_context_reference[1],
        "campaign_context_reference[1]",
    )
    if campaign_project != project:
        raise ValueError(
            "campaign_context_reference project binding must match "
            "project_context_reference"
        )
    admitted = _require_ascii_nonempty(
        admitted_asset_reference,
        "admitted_asset_reference",
    )
    expected: BoundReference = (project, campaign, admitted)

    if (
        accepted_governed_asset_reference is not None
        and accepted_governed_asset_reference != expected
    ):
        raise ValueError(
            "accepted_governed_asset_reference must match the exact admitted "
            "governed asset reference"
        )
    return expected


def consume_generated_candidate_asset_admission_execution_for_workflow_transition(
    admission_execution: GeneratedCandidateAssetAdmissionExecution,
    *,
    workflow_request_reference: str,
    idempotency_key: str,
    project_context_reference: str,
    campaign_context_reference: CampaignContextReference,
    creative_brief_reference: str,
    instruction_reference: InstructionReference,
    current_workflow_state: WorkflowState,
    requested_next_workflow_state: WorkflowState,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    event_timestamp: datetime,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
    canonical_input_fingerprint: str,
    consumption_actor_reference: str,
    consumption_timestamp: datetime,
    existing_idempotency_fingerprint: str | None = None,
    manual_external_tool_handoff_reference: BoundReference | None = None,
    creative_result_candidate_reference: BoundReference | None = None,
    accepted_operator_decision_reference: BoundReference | None = None,
    accepted_governed_asset_reference: BoundReference | None = None,
    recovery_last_accepted_state: WorkflowState | None = None,
    recovery_last_accepted_event_reference: BoundReference | None = None,
    recovery_reason_code: str | None = None,
    workflow_transition_evaluator: WorkflowTransitionEvaluator = (
        evaluate_governed_creative_workflow_transition
    ),
) -> GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption:
    if type(admission_execution) is not GeneratedCandidateAssetAdmissionExecution:
        raise ValueError(
            "admission_execution must be an exact "
            "GeneratedCandidateAssetAdmissionExecution"
        )
    if admission_execution.execution_outcome != ADMISSION_OUTCOME_ADMITTED:
        raise ValueError("admission execution outcome must be exactly ADMITTED")
    if (
        admission_execution.deterministic_provenance
        != _expected_admission_provenance(admission_execution)
    ):
        raise ValueError("admission execution deterministic provenance mismatch")

    requested_state = _require_ascii_nonempty(
        requested_next_workflow_state,
        "requested_next_workflow_state",
    )
    actor = _require_ascii_nonempty(
        consumption_actor_reference,
        "consumption_actor_reference",
    )
    consumed_at = _require_aware_datetime(
        consumption_timestamp,
        "consumption_timestamp",
    )

    bound_asset_reference = _bind_admitted_asset_reference(
        project_context_reference=project_context_reference,
        campaign_context_reference=campaign_context_reference,
        admitted_asset_reference=admission_execution.admitted_asset_reference,
        accepted_governed_asset_reference=accepted_governed_asset_reference,
    )

    evaluation = workflow_transition_evaluator(
        workflow_request_reference=workflow_request_reference,
        idempotency_key=idempotency_key,
        project_context_reference=project_context_reference,
        campaign_context_reference=campaign_context_reference,
        creative_brief_reference=creative_brief_reference,
        instruction_reference=instruction_reference,
        current_workflow_state=current_workflow_state,
        requested_next_workflow_state=requested_next_workflow_state,
        responsible_actor_or_service_reference=(
            responsible_actor_or_service_reference
        ),
        event_timestamp=event_timestamp,
        evidence_references=evidence_references,
        reason_codes=reason_codes,
        workflow_contract_reference=workflow_contract_reference,
        canonical_input_fingerprint=canonical_input_fingerprint,
        existing_idempotency_fingerprint=existing_idempotency_fingerprint,
        manual_external_tool_handoff_reference=(
            manual_external_tool_handoff_reference
        ),
        creative_result_candidate_reference=creative_result_candidate_reference,
        accepted_operator_decision_reference=(
            accepted_operator_decision_reference
        ),
        accepted_governed_asset_reference=bound_asset_reference,
        recovery_last_accepted_state=recovery_last_accepted_state,
        recovery_last_accepted_event_reference=(
            recovery_last_accepted_event_reference
        ),
        recovery_reason_code=recovery_reason_code,
        authority_bypass_requested=False,
        prohibited_automation_requested=False,
        approval_execution_requested=False,
        # The admission already happened. This boundary supplies immutable evidence;
        # it does not ask the Gate 18 evaluator to execute asset admission.
        asset_admission_execution_requested=False,
        lifecycle_mutation_requested=False,
        production_release_requested=False,
    )

    if type(evaluation) is not GovernedCreativeWorkflowTransitionEvaluation:
        raise ValueError(
            "workflow_transition_evaluator must return an exact "
            "GovernedCreativeWorkflowTransitionEvaluation"
        )
    if evaluation.prior_workflow_state != current_workflow_state:
        raise ValueError("workflow evaluation prior state mismatch")
    if evaluation.requested_workflow_state != requested_state:
        raise ValueError("workflow evaluation requested state mismatch")

    consumption_id = (
        derive_generated_candidate_asset_admission_workflow_transition_consumption_id(
            asset_admission_execution_id=(
                admission_execution.asset_admission_execution_id
            ),
            admitted_asset_reference=admission_execution.admitted_asset_reference,
            accepted_governed_asset_reference=bound_asset_reference,
            requested_workflow_state=requested_state,
            workflow_transition_evaluation=evaluation,
            consumption_actor_reference=actor,
            consumption_timestamp=consumed_at,
        )
    )
    evaluation_sha256 = derive_workflow_transition_evaluation_sha256(evaluation)
    provenance = (
        (
            "asset_admission_execution_sha256:"
            f"{admission_execution.asset_admission_execution_id}"
        ),
        f"admitted_asset_reference:{admission_execution.admitted_asset_reference}",
        f"workflow_transition_evaluation_sha256:{evaluation_sha256}",
        f"requested_workflow_state:{requested_state}",
        f"consumption_sha256:{consumption_id}",
    )

    return GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
        consumption_id=consumption_id,
        asset_admission_execution_id=(
            admission_execution.asset_admission_execution_id
        ),
        admitted_asset_reference=admission_execution.admitted_asset_reference,
        accepted_governed_asset_reference=bound_asset_reference,
        requested_workflow_state=requested_state,
        workflow_transition_evaluation=evaluation,
        consumption_actor_reference=actor,
        consumption_timestamp=consumed_at,
        deterministic_provenance=provenance,
    )


__all__ = [
    "consume_generated_candidate_asset_admission_execution_for_workflow_transition",
]
