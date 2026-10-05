from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

from rie.application.authorize_generated_candidate_decision_action import (
    authorize_generated_candidate_decision_action,
)
from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderTransport,
    VisualGenerationExecutionConfig,
    VisualReferenceResolver,
)
from rie.application.decide_generated_candidate import decide_generated_candidate
from rie.application.evaluate_generated_candidate import (
    evaluate_generated_candidate,
)
from rie.application.execute_generated_candidate_asset_admission import (
    execute_generated_candidate_asset_admission,
)
from rie.application.execute_generated_candidate_autonomous_iteration_action import (
    execute_generated_candidate_autonomous_iteration_action,
)
from rie.application.execute_generated_candidate_retry_regeneration_action import (
    execute_generated_candidate_retry_regeneration_action,
)
from rie.application.execute_generated_candidate_workflow_transition_action import (
    execute_generated_candidate_workflow_transition_action,
)
from rie.application.execute_visual_generation_with_provider_response_capture import (
    execute_visual_generation_with_provider_response_capture,
)
from rie.application.generated_output_creative_result_candidate_bridge import (
    bridge_generated_output_to_creative_result_candidate,
)
from rie.application.visual_generation_provider import VisualGenerationRequest
from rie.domain.autonomous_creative_generator_single_cycle_result import (
    AutonomousCreativeGeneratorSingleCycleResult,
    BRANCH_OUTCOME_NO_ACTION,
    derive_autonomous_creative_generator_single_cycle_id,
)
from rie.domain.creative_workflow_event import (
    EvidenceReference,
    InstructionReference,
    ResponsibleActorOrServiceReference,
    WorkflowContractReference,
    WorkflowState,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    REQUESTED_ACTION_ASSET_ADMISSION,
    REQUESTED_ACTION_AUTONOMOUS_ITERATION,
    REQUESTED_ACTION_RETRY_REGENERATION,
    REQUESTED_ACTION_WORKFLOW_TRANSITION,
)
from rie.domain.generated_candidate_evaluation import (
    GeneratedCandidateCriterionResult,
)
from rie.domain.governed_creative_workflow_result import BoundReference


@dataclass(frozen=True, slots=True)
class AssetAdmissionActionInputs:
    admitted_asset_reference: str
    execution_actor_reference: str
    execution_timestamp: datetime


@dataclass(frozen=True, slots=True)
class RetryRegenerationActionInputs:
    retry_request: VisualGenerationRequest
    execution_config: VisualGenerationExecutionConfig
    reference_resolver: VisualReferenceResolver
    transport: ProviderTransport
    execution_actor_reference: str
    execution_timestamp: datetime


@dataclass(frozen=True, slots=True)
class WorkflowTransitionActionInputs:
    idempotency_key: str
    campaign_context_reference: tuple[str, str]
    instruction_reference: InstructionReference
    current_workflow_state: WorkflowState
    requested_next_workflow_state: WorkflowState
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference
    evidence_references: tuple[EvidenceReference, ...]
    reason_codes: tuple[str, ...]
    workflow_contract_reference: WorkflowContractReference
    canonical_input_fingerprint: str
    execution_actor_reference: str
    execution_timestamp: datetime
    existing_idempotency_fingerprint: str | None = None
    manual_external_tool_handoff_reference: BoundReference | None = None
    creative_result_candidate_reference: BoundReference | None = None
    accepted_operator_decision_reference: BoundReference | None = None
    accepted_governed_asset_reference: BoundReference | None = None
    recovery_last_accepted_state: WorkflowState | None = None
    recovery_last_accepted_event_reference: BoundReference | None = None
    recovery_reason_code: str | None = None


@dataclass(frozen=True, slots=True)
class AutonomousIterationActionInputs:
    iteration_plan_reference: str
    current_iteration_index: int
    maximum_iteration_count: int
    next_step_reference: str
    execution_actor_reference: str
    execution_timestamp: datetime


ActionInputs = (
    AssetAdmissionActionInputs
    | RetryRegenerationActionInputs
    | WorkflowTransitionActionInputs
    | AutonomousIterationActionInputs
)


def _derive_initial_generation_request_sha256(
    request: VisualGenerationRequest,
) -> str:
    if type(request) is not VisualGenerationRequest:
        raise ValueError("request must be an exact VisualGenerationRequest")
    canonical = json.dumps(
        {
            "grounded_prompt": request.grounded_prompt,
            "selected_reference_asset_ids": list(
                request.selected_reference_asset_ids
            ),
        },
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _dispatch_authorized_action(
    *,
    authorization,
    candidate,
    action_inputs: ActionInputs | None,
):
    requested_action = authorization.requested_action

    if requested_action == REQUESTED_ACTION_ASSET_ADMISSION:
        if type(action_inputs) is not AssetAdmissionActionInputs:
            raise ValueError(
                "ASSET_ADMISSION requires exact AssetAdmissionActionInputs"
            )
        return execute_generated_candidate_asset_admission(
            authorization,
            candidate,
            admitted_asset_reference=action_inputs.admitted_asset_reference,
            execution_actor_reference=action_inputs.execution_actor_reference,
            execution_timestamp=action_inputs.execution_timestamp,
        )

    if requested_action == REQUESTED_ACTION_RETRY_REGENERATION:
        if type(action_inputs) is not RetryRegenerationActionInputs:
            raise ValueError(
                "RETRY_REGENERATION requires exact RetryRegenerationActionInputs"
            )
        return execute_generated_candidate_retry_regeneration_action(
            authorization,
            retry_request=action_inputs.retry_request,
            execution_config=action_inputs.execution_config,
            reference_resolver=action_inputs.reference_resolver,
            transport=action_inputs.transport,
            execution_actor_reference=action_inputs.execution_actor_reference,
            execution_timestamp=action_inputs.execution_timestamp,
        )

    if requested_action == REQUESTED_ACTION_WORKFLOW_TRANSITION:
        if type(action_inputs) is not WorkflowTransitionActionInputs:
            raise ValueError(
                "WORKFLOW_TRANSITION requires exact "
                "WorkflowTransitionActionInputs"
            )
        return execute_generated_candidate_workflow_transition_action(
            authorization,
            idempotency_key=action_inputs.idempotency_key,
            campaign_context_reference=(
                action_inputs.campaign_context_reference
            ),
            instruction_reference=action_inputs.instruction_reference,
            current_workflow_state=action_inputs.current_workflow_state,
            requested_next_workflow_state=(
                action_inputs.requested_next_workflow_state
            ),
            responsible_actor_or_service_reference=(
                action_inputs.responsible_actor_or_service_reference
            ),
            evidence_references=action_inputs.evidence_references,
            reason_codes=action_inputs.reason_codes,
            workflow_contract_reference=(
                action_inputs.workflow_contract_reference
            ),
            canonical_input_fingerprint=(
                action_inputs.canonical_input_fingerprint
            ),
            execution_actor_reference=action_inputs.execution_actor_reference,
            execution_timestamp=action_inputs.execution_timestamp,
            existing_idempotency_fingerprint=(
                action_inputs.existing_idempotency_fingerprint
            ),
            manual_external_tool_handoff_reference=(
                action_inputs.manual_external_tool_handoff_reference
            ),
            creative_result_candidate_reference=(
                action_inputs.creative_result_candidate_reference
            ),
            accepted_operator_decision_reference=(
                action_inputs.accepted_operator_decision_reference
            ),
            accepted_governed_asset_reference=(
                action_inputs.accepted_governed_asset_reference
            ),
            recovery_last_accepted_state=(
                action_inputs.recovery_last_accepted_state
            ),
            recovery_last_accepted_event_reference=(
                action_inputs.recovery_last_accepted_event_reference
            ),
            recovery_reason_code=action_inputs.recovery_reason_code,
        )

    if requested_action == REQUESTED_ACTION_AUTONOMOUS_ITERATION:
        if type(action_inputs) is not AutonomousIterationActionInputs:
            raise ValueError(
                "AUTONOMOUS_ITERATION requires exact "
                "AutonomousIterationActionInputs"
            )
        return execute_generated_candidate_autonomous_iteration_action(
            authorization,
            iteration_plan_reference=action_inputs.iteration_plan_reference,
            current_iteration_index=action_inputs.current_iteration_index,
            maximum_iteration_count=action_inputs.maximum_iteration_count,
            next_step_reference=action_inputs.next_step_reference,
            execution_actor_reference=action_inputs.execution_actor_reference,
            execution_timestamp=action_inputs.execution_timestamp,
        )

    raise ValueError("authorization requested_action is unsupported")


def orchestrate_autonomous_creative_generator_single_cycle(
    *,
    request: VisualGenerationRequest,
    execution_config: VisualGenerationExecutionConfig,
    reference_resolver: VisualReferenceResolver,
    transport: ProviderTransport,
    creative_result_candidate_id: str,
    workflow_request_reference: str,
    project_context_reference: str,
    campaign_context_reference: tuple[str, str],
    creative_brief_reference: str,
    instruction_reference: tuple[str, str],
    originating_manual_handoff_reference: str | None,
    candidate_admission_timestamp: datetime,
    candidate_admitting_actor_reference: str,
    generated_output_bytes: bytes | None,
    generated_output_checksum: str | None,
    criterion_results: tuple[GeneratedCandidateCriterionResult, ...],
    evaluator_actor_reference: str,
    evaluation_timestamp: datetime,
    decision_outcome: str,
    decision_reason_evidence_reference: str,
    decision_actor_reference: str,
    decision_timestamp: datetime,
    requested_action: str,
    authorization_outcome: str,
    authorization_reason_evidence_reference: str,
    authorization_actor_reference: str,
    authorization_timestamp: datetime,
    action_inputs: ActionInputs | None,
    cycle_actor_reference: str,
    cycle_timestamp: datetime,
) -> AutonomousCreativeGeneratorSingleCycleResult:
    request_sha = _derive_initial_generation_request_sha256(request)

    captured = execute_visual_generation_with_provider_response_capture(
        request=request,
        execution_config=execution_config,
        reference_resolver=reference_resolver,
        transport=transport,
    )

    candidate = bridge_generated_output_to_creative_result_candidate(
        creative_result_candidate_id=creative_result_candidate_id,
        workflow_request_reference=workflow_request_reference,
        project_context_reference=project_context_reference,
        campaign_context_reference=campaign_context_reference,
        creative_brief_reference=creative_brief_reference,
        instruction_reference=instruction_reference,
        originating_manual_handoff_reference=(
            originating_manual_handoff_reference
        ),
        admission_timestamp=candidate_admission_timestamp,
        admitting_actor_reference=candidate_admitting_actor_reference,
        provider_id=execution_config.provider_id,
        model_id=execution_config.model_id,
        provider_execution_response=captured.provider_execution_response,
        generated_output_bytes=generated_output_bytes,
        generated_output_checksum=generated_output_checksum,
    )

    evaluation = evaluate_generated_candidate(
        candidate=candidate,
        criterion_results=criterion_results,
        evaluator_actor_reference=evaluator_actor_reference,
        evaluation_timestamp=evaluation_timestamp,
    )

    decision = decide_generated_candidate(
        evaluation=evaluation,
        decision_outcome=decision_outcome,
        decision_reason_evidence_reference=decision_reason_evidence_reference,
        decision_actor_reference=decision_actor_reference,
        decision_timestamp=decision_timestamp,
    )

    authorization = authorize_generated_candidate_decision_action(
        decision,
        requested_action=requested_action,
        authorization_outcome=authorization_outcome,
        authorization_reason_evidence_reference=(
            authorization_reason_evidence_reference
        ),
        authorization_actor_reference=authorization_actor_reference,
        authorization_timestamp=authorization_timestamp,
    )

    action_execution = None
    branch_outcome = BRANCH_OUTCOME_NO_ACTION

    if authorization.authorization_outcome == AUTHORIZATION_OUTCOME_AUTHORIZED:
        action_execution = _dispatch_authorized_action(
            authorization=authorization,
            candidate=candidate,
            action_inputs=action_inputs,
        )
        branch_outcome = authorization.requested_action
    elif action_inputs is not None:
        raise ValueError(
            "non-AUTHORIZED authorization requires action_inputs to be None"
        )

    response = captured.provider_execution_response
    audit_message = captured.visual_generation_result.message

    cycle_id = derive_autonomous_creative_generator_single_cycle_id(
        initial_generation_request_sha256=request_sha,
        provider_id=execution_config.provider_id,
        model_id=execution_config.model_id,
        provider_execution_status=response.execution_status,
        provider_execution_reference=response.provider_execution_ref,
        provider_output_refs=response.provider_output_refs,
        provider_audit_message=audit_message,
        candidate=candidate,
        evaluation=evaluation,
        decision=decision,
        authorization=authorization,
        action_execution=action_execution,
        branch_outcome=branch_outcome,
        cycle_actor_reference=cycle_actor_reference,
        cycle_timestamp=cycle_timestamp,
    )

    action_kind = (
        "none"
        if action_execution is None
        else authorization.requested_action
    )
    action_id = None
    if action_execution is not None:
        for field_name in (
            "asset_admission_execution_id",
            "retry_regeneration_action_execution_id",
            "workflow_transition_action_execution_id",
            "autonomous_iteration_action_execution_id",
        ):
            value = getattr(action_execution, field_name, None)
            if value is not None:
                action_id = value
                break
        if action_id is None:
            raise ValueError("action execution identity field is missing")

    provenance = (
        f"initial_generation_request_sha256:{request_sha}",
        f"provider:{execution_config.provider_id}",
        f"model:{execution_config.model_id}",
        f"candidate:{candidate.creative_result_candidate_id}",
        f"candidate_sha256:{candidate.candidate_content_checksum}",
        f"evaluation:{evaluation.evaluation_id}",
        f"decision:{decision.decision_id}",
        f"authorization_sha256:{authorization.authorization_id}",
        f"branch_outcome:{branch_outcome}",
        (
            "action_execution:none"
            if action_id is None
            else f"action_execution:{action_kind}:{action_id}"
        ),
        f"cycle_sha256:{cycle_id}",
    )

    return AutonomousCreativeGeneratorSingleCycleResult(
        cycle_id=cycle_id,
        initial_generation_request_sha256=request_sha,
        provider_id=execution_config.provider_id,
        model_id=execution_config.model_id,
        provider_execution_status=response.execution_status,
        provider_execution_reference=response.provider_execution_ref,
        provider_output_refs=response.provider_output_refs,
        provider_audit_message=audit_message,
        candidate=candidate,
        evaluation=evaluation,
        decision=decision,
        authorization=authorization,
        action_execution=action_execution,
        branch_outcome=branch_outcome,
        cycle_actor_reference=cycle_actor_reference,
        cycle_timestamp=cycle_timestamp,
        deterministic_provenance=provenance,
    )


__all__ = [
    "ActionInputs",
    "AssetAdmissionActionInputs",
    "AutonomousIterationActionInputs",
    "RetryRegenerationActionInputs",
    "WorkflowTransitionActionInputs",
    "orchestrate_autonomous_creative_generator_single_cycle",
]
