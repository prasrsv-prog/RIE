from __future__ import annotations

from datetime import datetime

from rie.application.concrete_visual_generation_execution_adapter import (
    ConcreteVisualGenerationExecutionAdapter,
    ProviderTransport,
    VisualGenerationExecutionConfig,
    VisualReferenceResolver,
)
from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    REQUESTED_ACTION_RETRY_REGENERATION,
    GeneratedCandidateDecisionActionAuthorization,
)
from rie.domain.generated_candidate_retry_regeneration_action_execution import (
    GeneratedCandidateRetryRegenerationActionExecution,
    derive_generated_candidate_retry_regeneration_action_execution_id,
    derive_provider_local_result_sha256,
    derive_retry_generation_request_sha256,
)


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


def execute_generated_candidate_retry_regeneration_action(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    *,
    retry_request: VisualGenerationRequest,
    execution_config: VisualGenerationExecutionConfig,
    reference_resolver: VisualReferenceResolver,
    transport: ProviderTransport,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> GeneratedCandidateRetryRegenerationActionExecution:
    if type(authorization) is not GeneratedCandidateDecisionActionAuthorization:
        raise ValueError(
            "authorization must be an exact "
            "GeneratedCandidateDecisionActionAuthorization"
        )
    if authorization.requested_action != REQUESTED_ACTION_RETRY_REGENERATION:
        raise ValueError("requested_action must be RETRY_REGENERATION")
    if authorization.authorization_outcome != AUTHORIZATION_OUTCOME_AUTHORIZED:
        raise ValueError("authorization outcome must be AUTHORIZED")

    _require_authorization_provenance(authorization)

    if type(retry_request) is not VisualGenerationRequest:
        raise ValueError("retry_request must be an exact VisualGenerationRequest")
    if type(execution_config) is not VisualGenerationExecutionConfig:
        raise ValueError(
            "execution_config must be an exact VisualGenerationExecutionConfig"
        )

    execution_actor_reference = _require_ascii_nonempty(
        execution_actor_reference,
        "execution_actor_reference",
    )
    execution_timestamp = _require_aware_datetime(
        execution_timestamp,
        "execution_timestamp",
    )

    request_sha = derive_retry_generation_request_sha256(
        grounded_prompt=retry_request.grounded_prompt,
        selected_reference_asset_ids=retry_request.selected_reference_asset_ids,
    )

    adapter = ConcreteVisualGenerationExecutionAdapter(
        config=execution_config,
        reference_resolver=reference_resolver,
        transport=transport,
    )
    result = adapter.generate(retry_request)

    if type(result) is not VisualGenerationResult:
        raise ValueError("adapter must return an exact VisualGenerationResult")

    result_sha = derive_provider_local_result_sha256(
        provider_output_refs=result.provider_output_refs,
        provider_audit_message=result.message,
    )

    execution_id = derive_generated_candidate_retry_regeneration_action_execution_id(
        authorization_id=authorization.authorization_id,
        decision_id=authorization.decision_id,
        evaluation_id=authorization.evaluation_id,
        candidate_id=authorization.candidate_id,
        candidate_checksum=authorization.candidate_checksum,
        retry_generation_request_sha256=request_sha,
        selected_reference_asset_ids=retry_request.selected_reference_asset_ids,
        provider_id=execution_config.provider_id,
        model_id=execution_config.model_id,
        provider_local_result_sha256=result_sha,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
    )

    deterministic_provenance = (
        f"authorization_sha256:{authorization.authorization_id}",
        f"decision_id:{authorization.decision_id}",
        f"candidate_sha256:{authorization.candidate_checksum}",
        "requested_action:RETRY_REGENERATION",
        f"retry_generation_request_sha256:{request_sha}",
        f"provider:{execution_config.provider_id}",
        f"model:{execution_config.model_id}",
        f"provider_local_result_sha256:{result_sha}",
        f"retry_regeneration_action_execution_sha256:{execution_id}",
    )

    return GeneratedCandidateRetryRegenerationActionExecution(
        retry_regeneration_action_execution_id=execution_id,
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
        retry_generation_request_sha256=request_sha,
        selected_reference_asset_ids=retry_request.selected_reference_asset_ids,
        provider_id=execution_config.provider_id,
        model_id=execution_config.model_id,
        provider_output_refs=result.provider_output_refs,
        provider_audit_message=result.message,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
        deterministic_provenance=deterministic_provenance,
    )


__all__ = ["execute_generated_candidate_retry_regeneration_action"]
