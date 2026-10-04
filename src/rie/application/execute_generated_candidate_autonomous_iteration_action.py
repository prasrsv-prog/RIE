from __future__ import annotations

from datetime import datetime

from rie.domain.generated_candidate_autonomous_iteration_action_execution import (
    GeneratedCandidateAutonomousIterationActionExecution,
    derive_autonomous_iteration_control_sha256,
    derive_generated_candidate_autonomous_iteration_action_execution_id,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    REQUESTED_ACTION_AUTONOMOUS_ITERATION,
    GeneratedCandidateDecisionActionAuthorization,
)


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


def execute_generated_candidate_autonomous_iteration_action(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    *,
    iteration_plan_reference: str,
    current_iteration_index: int,
    maximum_iteration_count: int,
    next_step_reference: str,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> GeneratedCandidateAutonomousIterationActionExecution:
    if type(authorization) is not GeneratedCandidateDecisionActionAuthorization:
        raise ValueError(
            "authorization must be an exact "
            "GeneratedCandidateDecisionActionAuthorization"
        )
    if authorization.requested_action != REQUESTED_ACTION_AUTONOMOUS_ITERATION:
        raise ValueError("requested_action must be AUTONOMOUS_ITERATION")
    if authorization.authorization_outcome != AUTHORIZATION_OUTCOME_AUTHORIZED:
        raise ValueError("authorization outcome must be AUTHORIZED")

    _require_authorization_provenance(authorization)

    control_sha = derive_autonomous_iteration_control_sha256(
        iteration_plan_reference=iteration_plan_reference,
        current_iteration_index=current_iteration_index,
        maximum_iteration_count=maximum_iteration_count,
        next_step_reference=next_step_reference,
    )

    execution_id = (
        derive_generated_candidate_autonomous_iteration_action_execution_id(
            authorization_id=authorization.authorization_id,
            decision_id=authorization.decision_id,
            evaluation_id=authorization.evaluation_id,
            candidate_id=authorization.candidate_id,
            candidate_checksum=authorization.candidate_checksum,
            iteration_control_sha256=control_sha,
            execution_actor_reference=execution_actor_reference,
            execution_timestamp=execution_timestamp,
        )
    )

    provenance = (
        f"authorization_sha256:{authorization.authorization_id}",
        f"decision_id:{authorization.decision_id}",
        f"candidate_sha256:{authorization.candidate_checksum}",
        "requested_action:AUTONOMOUS_ITERATION",
        f"iteration_control_sha256:{control_sha}",
        f"autonomous_iteration_action_execution_sha256:{execution_id}",
    )

    return GeneratedCandidateAutonomousIterationActionExecution(
        autonomous_iteration_action_execution_id=execution_id,
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
        iteration_plan_reference=iteration_plan_reference,
        current_iteration_index=current_iteration_index,
        maximum_iteration_count=maximum_iteration_count,
        next_step_reference=next_step_reference,
        iteration_control_sha256=control_sha,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
        deterministic_provenance=provenance,
    )


__all__ = ["execute_generated_candidate_autonomous_iteration_action"]
