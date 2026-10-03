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
    GovernedCreativeWorkflowTransitionEvaluation,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    REQUESTED_ACTION_WORKFLOW_TRANSITION,
    GeneratedCandidateDecisionActionAuthorization,
)
from rie.domain.generated_candidate_workflow_transition_action_execution import (
    GeneratedCandidateWorkflowTransitionActionExecution,
    derive_generated_candidate_workflow_transition_action_execution_id,
    derive_workflow_transition_evaluation_sha256,
)
from rie.domain.governed_creative_workflow_result import BoundReference


WorkflowTransitionEvaluator = Callable[..., GovernedCreativeWorkflowTransitionEvaluation]


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


def _require_authorization_provenance(
    authorization: GeneratedCandidateDecisionActionAuthorization,
) -> None:
    expected = (
        f"candidate_sha256:{authorization.candidate_checksum}",
        f"evaluation_id:{authorization.evaluation_id}",
        f"decision_id:{authorization.decision_id}",
        f"requested_action:{authorization.requested_action}",
        f"authorization_sha256:{authorization.authorization_id}",
    )
    if authorization.deterministic_provenance != expected:
        raise ValueError("authorization deterministic_provenance mismatch")


def _require_campaign_binding(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    campaign_context_reference: tuple[str, str],
) -> None:
    if type(campaign_context_reference) is not tuple:
        raise ValueError("campaign_context_reference must be an exact tuple")
    if len(campaign_context_reference) != 2:
        raise ValueError("campaign_context_reference must contain exactly two values")
    if campaign_context_reference[0] != authorization.project_context_reference:
        raise ValueError("campaign project binding must match authorization")
    if campaign_context_reference[1] != authorization.campaign_context_reference:
        raise ValueError("campaign identity must match authorization")


def _require_instruction_binding(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    instruction_reference: InstructionReference,
) -> None:
    if type(instruction_reference) is not tuple or len(instruction_reference) != 2:
        raise ValueError("instruction_reference must contain exactly two values")
    if instruction_reference[0] != authorization.instruction_reference:
        raise ValueError("instruction identity must match authorization")


def _require_actor_binding(
    execution_actor_reference: str,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
) -> None:
    if (
        type(responsible_actor_or_service_reference) is not tuple
        or len(responsible_actor_or_service_reference) != 2
    ):
        raise ValueError(
            "responsible_actor_or_service_reference must contain exactly two values"
        )
    if responsible_actor_or_service_reference[1] != execution_actor_reference:
        raise ValueError("responsible actor identity must match execution actor")


def execute_generated_candidate_workflow_transition_action(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    *,
    idempotency_key: str,
    campaign_context_reference: tuple[str, str],
    instruction_reference: InstructionReference,
    current_workflow_state: WorkflowState,
    requested_next_workflow_state: WorkflowState,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
    canonical_input_fingerprint: str,
    execution_actor_reference: str,
    execution_timestamp: datetime,
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
) -> GeneratedCandidateWorkflowTransitionActionExecution:
    if type(authorization) is not GeneratedCandidateDecisionActionAuthorization:
        raise ValueError(
            "authorization must be an exact "
            "GeneratedCandidateDecisionActionAuthorization"
        )
    if authorization.requested_action != REQUESTED_ACTION_WORKFLOW_TRANSITION:
        raise ValueError("authorization requested_action must be WORKFLOW_TRANSITION")
    if authorization.authorization_outcome != AUTHORIZATION_OUTCOME_AUTHORIZED:
        raise ValueError("authorization outcome must be AUTHORIZED")

    _require_authorization_provenance(authorization)
    _require_campaign_binding(authorization, campaign_context_reference)
    _require_instruction_binding(authorization, instruction_reference)

    requested_next_workflow_state = _require_ascii_nonempty(
        requested_next_workflow_state,
        "requested_next_workflow_state",
    )
    execution_actor_reference = _require_ascii_nonempty(
        execution_actor_reference,
        "execution_actor_reference",
    )
    execution_timestamp = _require_aware_datetime(
        execution_timestamp,
        "execution_timestamp",
    )
    _require_actor_binding(
        execution_actor_reference,
        responsible_actor_or_service_reference,
    )

    if type(evidence_references) is not tuple:
        raise ValueError("evidence_references must be an exact tuple")

    authorization_evidence: EvidenceReference = (
        authorization.project_context_reference,
        authorization.campaign_context_reference,
        f"authorization_sha256:{authorization.authorization_id}",
    )
    evaluator_evidence = tuple(sorted(set(evidence_references + (authorization_evidence,))))

    evaluation = workflow_transition_evaluator(
        workflow_request_reference=authorization.workflow_request_reference,
        idempotency_key=idempotency_key,
        project_context_reference=authorization.project_context_reference,
        campaign_context_reference=campaign_context_reference,
        creative_brief_reference=authorization.creative_brief_reference,
        instruction_reference=instruction_reference,
        current_workflow_state=current_workflow_state,
        requested_next_workflow_state=requested_next_workflow_state,
        responsible_actor_or_service_reference=responsible_actor_or_service_reference,
        event_timestamp=execution_timestamp,
        evidence_references=evaluator_evidence,
        reason_codes=reason_codes,
        workflow_contract_reference=workflow_contract_reference,
        canonical_input_fingerprint=canonical_input_fingerprint,
        existing_idempotency_fingerprint=existing_idempotency_fingerprint,
        manual_external_tool_handoff_reference=manual_external_tool_handoff_reference,
        creative_result_candidate_reference=creative_result_candidate_reference,
        accepted_operator_decision_reference=accepted_operator_decision_reference,
        accepted_governed_asset_reference=accepted_governed_asset_reference,
        recovery_last_accepted_state=recovery_last_accepted_state,
        recovery_last_accepted_event_reference=recovery_last_accepted_event_reference,
        recovery_reason_code=recovery_reason_code,
        authority_bypass_requested=False,
        prohibited_automation_requested=False,
        approval_execution_requested=False,
        asset_admission_execution_requested=False,
        lifecycle_mutation_requested=False,
        production_release_requested=False,
    )

    if type(evaluation) is not GovernedCreativeWorkflowTransitionEvaluation:
        raise ValueError(
            "workflow transition evaluator must return an exact "
            "GovernedCreativeWorkflowTransitionEvaluation"
        )

    execution_id = derive_generated_candidate_workflow_transition_action_execution_id(
        authorization_id=authorization.authorization_id,
        decision_id=authorization.decision_id,
        evaluation_id=authorization.evaluation_id,
        candidate_id=authorization.candidate_id,
        candidate_checksum=authorization.candidate_checksum,
        requested_next_workflow_state=requested_next_workflow_state,
        workflow_transition_evaluation=evaluation,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
    )
    evaluation_sha = derive_workflow_transition_evaluation_sha256(evaluation)
    provenance = (
        f"authorization_sha256:{authorization.authorization_id}",
        f"decision_id:{authorization.decision_id}",
        f"candidate_sha256:{authorization.candidate_checksum}",
        "requested_action:WORKFLOW_TRANSITION",
        f"workflow_transition_evaluation_sha256:{evaluation_sha}",
        f"workflow_transition_action_execution_sha256:{execution_id}",
    )

    return GeneratedCandidateWorkflowTransitionActionExecution(
        workflow_transition_action_execution_id=execution_id,
        authorization_id=authorization.authorization_id,
        decision_id=authorization.decision_id,
        evaluation_id=authorization.evaluation_id,
        candidate_id=authorization.candidate_id,
        candidate_checksum=authorization.candidate_checksum,
        workflow_request_reference=authorization.workflow_request_reference,
        project_context_reference=authorization.project_context_reference,
        campaign_context_reference=authorization.campaign_context_reference,
        creative_brief_reference=authorization.creative_brief_reference,
        instruction_reference=authorization.instruction_reference,
        decision_outcome=authorization.decision_outcome,
        requested_action=authorization.requested_action,
        authorization_outcome=authorization.authorization_outcome,
        requested_next_workflow_state=requested_next_workflow_state,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
        workflow_transition_evaluation=evaluation,
        deterministic_provenance=provenance,
    )
