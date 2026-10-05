from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.domain.autonomous_creative_generator_single_cycle_result import (
    AutonomousCreativeGeneratorSingleCycleResult,
    BRANCH_OUTCOME_NO_ACTION,
    derive_autonomous_creative_generator_single_cycle_id,
)
from rie.domain.creative_result_candidate import CreativeResultCandidate
from rie.domain.generated_candidate_decision import GeneratedCandidateDecision
from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)
from rie.domain.generated_candidate_evaluation import (
    GeneratedCandidateCriterionResult,
    GeneratedCandidateEvaluation,
)


TIME = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)


def _candidate() -> CreativeResultCandidate:
    return CreativeResultCandidate(
        creative_result_candidate_id="candidate:1",
        workflow_request_reference="workflow:1",
        project_context_reference="project:1",
        campaign_context_reference=("project:1", "campaign:1"),
        creative_brief_reference="brief:1",
        instruction_reference=("instruction:1", "APPROVED_INSTRUCTION"),
        originating_manual_handoff_reference=None,
        candidate_content_checksum="b" * 64,
        artifact_type="IMAGE",
        admission_timestamp=TIME,
        admitting_actor_reference="actor:admitter",
        deterministic_provenance=(
            "workflow_request:workflow:1",
            "content_sha256:" + "b" * 64,
        ),
        authority_state="CANDIDATE",
        official_source_claimed=False,
        accepted_asset_claimed=False,
        approved_asset_claimed=False,
    )


def _evaluation(candidate: CreativeResultCandidate) -> GeneratedCandidateEvaluation:
    criterion = GeneratedCandidateCriterionResult(
        criterion_id="criterion:1",
        outcome="passed",
        reason_evidence_reference="evidence:criterion:1",
    )
    return GeneratedCandidateEvaluation(
        evaluation_id="e" * 64,
        creative_result_candidate_id=candidate.creative_result_candidate_id,
        workflow_request_reference=candidate.workflow_request_reference,
        project_context_reference=candidate.project_context_reference,
        campaign_context_reference=candidate.campaign_context_reference,
        creative_brief_reference=candidate.creative_brief_reference,
        instruction_reference=candidate.instruction_reference,
        candidate_content_checksum=candidate.candidate_content_checksum,
        artifact_type=candidate.artifact_type,
        candidate_deterministic_provenance=candidate.deterministic_provenance,
        criterion_results=(criterion,),
        aggregate_outcome="passed",
        evaluator_actor_reference="actor:evaluator",
        evaluation_timestamp=TIME,
        deterministic_provenance=(
            f"candidate:{candidate.creative_result_candidate_id}",
            f"content_sha256:{candidate.candidate_content_checksum}",
            "evaluation_sha256:" + "e" * 64,
        ),
    )


def _decision(
    candidate: CreativeResultCandidate,
    evaluation: GeneratedCandidateEvaluation,
) -> GeneratedCandidateDecision:
    return GeneratedCandidateDecision(
        decision_id="d" * 64,
        evaluation_id=evaluation.evaluation_id,
        candidate_id=candidate.creative_result_candidate_id,
        workflow_request_reference=candidate.workflow_request_reference,
        project_context_reference=candidate.project_context_reference,
        campaign_context_reference=candidate.campaign_context_reference[1],
        creative_brief_reference=candidate.creative_brief_reference,
        instruction_reference=candidate.instruction_reference[0],
        candidate_checksum=candidate.candidate_content_checksum,
        artifact_type=candidate.artifact_type,
        evaluation_aggregate_outcome=evaluation.aggregate_outcome,
        decision_outcome="ACCEPTED",
        decision_reason_evidence_reference="evidence:decision:1",
        decision_actor_reference="actor:decision",
        decision_timestamp=TIME,
        deterministic_provenance=(
            f"candidate:{candidate.creative_result_candidate_id}",
            f"evaluation:{evaluation.evaluation_id}",
            "decision_sha256:" + "d" * 64,
        ),
    )


def _authorization(
    candidate: CreativeResultCandidate,
    evaluation: GeneratedCandidateEvaluation,
    decision: GeneratedCandidateDecision,
) -> GeneratedCandidateDecisionActionAuthorization:
    return GeneratedCandidateDecisionActionAuthorization(
        authorization_id="a" * 64,
        decision_id=decision.decision_id,
        evaluation_id=evaluation.evaluation_id,
        candidate_id=candidate.creative_result_candidate_id,
        workflow_request_reference=candidate.workflow_request_reference,
        project_context_reference=candidate.project_context_reference,
        campaign_context_reference=candidate.campaign_context_reference[1],
        creative_brief_reference=candidate.creative_brief_reference,
        instruction_reference=candidate.instruction_reference[0],
        candidate_checksum=candidate.candidate_content_checksum,
        artifact_type=candidate.artifact_type,
        decision_outcome=decision.decision_outcome,
        requested_action="ASSET_ADMISSION",
        authorization_outcome="DENIED",
        authorization_reason_evidence_reference="evidence:authorization:1",
        authorization_actor_reference="actor:authorization",
        authorization_timestamp=TIME,
        deterministic_provenance=(
            f"candidate_sha256:{candidate.candidate_content_checksum}",
            f"evaluation_id:{evaluation.evaluation_id}",
            f"decision_id:{decision.decision_id}",
            "requested_action:ASSET_ADMISSION",
            "authorization_sha256:" + "a" * 64,
        ),
    )


def _result(**overrides) -> AutonomousCreativeGeneratorSingleCycleResult:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation)
    authorization = _authorization(candidate, evaluation, decision)

    values = dict(
        initial_generation_request_sha256="1" * 64,
        provider_id="provider:1",
        model_id="model:1",
        provider_execution_status="SUCCEEDED",
        provider_execution_reference="provider-execution:1",
        provider_output_refs=("provider-output:1",),
        provider_audit_message=(
            "provider=provider:1;model=model:1;status=SUCCEEDED;"
            "execution_ref=provider-execution:1;diagnostic=completed"
        ),
        candidate=candidate,
        evaluation=evaluation,
        decision=decision,
        authorization=authorization,
        action_execution=None,
        branch_outcome=BRANCH_OUTCOME_NO_ACTION,
        cycle_actor_reference="actor:cycle",
        cycle_timestamp=TIME,
    )
    values.update(overrides)
    cycle_id = derive_autonomous_creative_generator_single_cycle_id(**values)
    provenance = (
        "initial_generation_request_sha256:" + values[
            "initial_generation_request_sha256"
        ],
        "provider:" + values["provider_id"],
        "model:" + values["model_id"],
        f"candidate:{candidate.creative_result_candidate_id}",
        f"candidate_sha256:{candidate.candidate_content_checksum}",
        f"evaluation:{evaluation.evaluation_id}",
        f"decision:{decision.decision_id}",
        f"authorization_sha256:{authorization.authorization_id}",
        f"branch_outcome:{values['branch_outcome']}",
        "action_execution:none",
        f"cycle_sha256:{cycle_id}",
    )
    return AutonomousCreativeGeneratorSingleCycleResult(
        cycle_id=cycle_id,
        deterministic_provenance=provenance,
        **values,
    )


def test_no_action_result_is_exact_immutable_and_deterministic() -> None:
    first = _result()
    second = _result()
    assert first.cycle_id == second.cycle_id
    assert first.action_execution is None
    assert first.branch_outcome == "NO_ACTION"
    with pytest.raises(FrozenInstanceError):
        first.branch_outcome = "OTHER"


def test_wrong_cycle_identity_fails_closed() -> None:
    result = _result()
    with pytest.raises(ValueError, match="cycle_id"):
        AutonomousCreativeGeneratorSingleCycleResult(
            cycle_id="f" * 64,
            initial_generation_request_sha256=(
                result.initial_generation_request_sha256
            ),
            provider_id=result.provider_id,
            model_id=result.model_id,
            provider_execution_status=result.provider_execution_status,
            provider_execution_reference=result.provider_execution_reference,
            provider_output_refs=result.provider_output_refs,
            provider_audit_message=result.provider_audit_message,
            candidate=result.candidate,
            evaluation=result.evaluation,
            decision=result.decision,
            authorization=result.authorization,
            action_execution=result.action_execution,
            branch_outcome=result.branch_outcome,
            cycle_actor_reference=result.cycle_actor_reference,
            cycle_timestamp=result.cycle_timestamp,
            deterministic_provenance=result.deterministic_provenance,
        )


def test_authorized_authorization_requires_exactly_one_action_execution() -> None:
    result = _result()
    authorization = GeneratedCandidateDecisionActionAuthorization(
        authorization_id="c" * 64,
        decision_id=result.decision.decision_id,
        evaluation_id=result.evaluation.evaluation_id,
        candidate_id=result.candidate.creative_result_candidate_id,
        workflow_request_reference=result.candidate.workflow_request_reference,
        project_context_reference=result.candidate.project_context_reference,
        campaign_context_reference=result.candidate.campaign_context_reference[1],
        creative_brief_reference=result.candidate.creative_brief_reference,
        instruction_reference=result.candidate.instruction_reference[0],
        candidate_checksum=result.candidate.candidate_content_checksum,
        artifact_type=result.candidate.artifact_type,
        decision_outcome=result.decision.decision_outcome,
        requested_action="ASSET_ADMISSION",
        authorization_outcome="AUTHORIZED",
        authorization_reason_evidence_reference="evidence:authorization:2",
        authorization_actor_reference="actor:authorization",
        authorization_timestamp=TIME,
        deterministic_provenance=(
            f"candidate_sha256:{result.candidate.candidate_content_checksum}",
            f"evaluation_id:{result.evaluation.evaluation_id}",
            f"decision_id:{result.decision.decision_id}",
            "requested_action:ASSET_ADMISSION",
            "authorization_sha256:" + "c" * 64,
        ),
    )
    with pytest.raises(ValueError, match="requires one action execution"):
        _result(authorization=authorization)


def test_naive_cycle_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _result(cycle_timestamp=datetime(2026, 10, 5, 8, 0))


def test_provider_audit_secret_marker_fails_closed() -> None:
    with pytest.raises(ValueError, match="secret material"):
        _result(provider_audit_message="authorization: hidden")
