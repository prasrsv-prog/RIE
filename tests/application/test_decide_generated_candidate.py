from datetime import datetime, timedelta, timezone

import pytest

from rie.application.authorize_generated_candidate_decision_action import (
    authorize_generated_candidate_decision_action,
)
from rie.application.decide_generated_candidate import decide_generated_candidate
from rie.domain.generated_candidate_decision import ACCEPTED, DEFERRED, REJECTED
from rie.domain.generated_candidate_evaluation import (
    GeneratedCandidateCriterionResult,
    GeneratedCandidateEvaluation,
)


FIXED_TIME = datetime(2026, 9, 30, 10, 30, tzinfo=timezone.utc)


def _evaluation(
    *,
    aggregate_outcome: str = "passed",
    evaluation_id: str = "e" * 64,
    candidate_id: str = "candidate-1",
    candidate_checksum: str = "b" * 64,
    campaign_context_reference: tuple[str, str] = ("project-1", "campaign-1"),
    instruction_reference: tuple[str, str] = (
        "instruction-1",
        "APPROVED_INSTRUCTION",
    ),
) -> GeneratedCandidateEvaluation:
    criterion = GeneratedCandidateCriterionResult(
        criterion_id="criterion-1",
        outcome=aggregate_outcome,
        reason_evidence_reference="evidence:criterion-1",
    )
    return GeneratedCandidateEvaluation(
        evaluation_id=evaluation_id,
        creative_result_candidate_id=candidate_id,
        workflow_request_reference="workflow-1",
        project_context_reference="project-1",
        campaign_context_reference=campaign_context_reference,
        creative_brief_reference="brief-1",
        instruction_reference=instruction_reference,
        candidate_content_checksum=candidate_checksum,
        artifact_type="IMAGE",
        candidate_deterministic_provenance=(
            "workflow_request:workflow-1",
            "content_sha256:" + candidate_checksum,
        ),
        criterion_results=(criterion,),
        aggregate_outcome=aggregate_outcome,
        evaluator_actor_reference="evaluator-1",
        evaluation_timestamp=datetime(
            2026,
            9,
            30,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        deterministic_provenance=(
            f"candidate:{candidate_id}",
            f"content_sha256:{candidate_checksum}",
            f"evaluation_sha256:{evaluation_id}",
        ),
    )


def _decide(
    *,
    evaluation: GeneratedCandidateEvaluation | object | None = None,
    outcome: str = ACCEPTED,
    reason: str = "evidence:review-1",
    actor: str = "actor:reviewer-1",
    timestamp: datetime = FIXED_TIME,
):
    return decide_generated_candidate(
        evaluation=_evaluation() if evaluation is None else evaluation,  # type: ignore[arg-type]
        decision_outcome=outcome,
        decision_reason_evidence_reference=reason,
        decision_actor_reference=actor,
        decision_timestamp=timestamp,
    )


def test_explicit_decision_preserves_exact_canonical_evaluation_lineage() -> None:
    decision = _decide()
    assert decision.evaluation_id == "e" * 64
    assert decision.candidate_id == "candidate-1"
    assert decision.candidate_checksum == "b" * 64
    assert decision.campaign_context_reference == "campaign-1"
    assert decision.instruction_reference == "instruction-1"
    assert decision.evaluation_aggregate_outcome == "passed"
    assert decision.decision_outcome == ACCEPTED


def test_evaluation_aggregate_does_not_implicitly_map_to_decision() -> None:
    decision = _decide(
        evaluation=_evaluation(aggregate_outcome="passed"),
        outcome=REJECTED,
    )
    assert decision.evaluation_aggregate_outcome == "passed"
    assert decision.decision_outcome == REJECTED


def test_deferred_decision_is_explicit_and_side_effect_free_record() -> None:
    decision = _decide(outcome=DEFERRED)
    assert decision.decision_outcome == DEFERRED
    assert decision.deterministic_provenance[0] == "candidate:candidate-1"


def test_identical_explicit_inputs_have_identical_identity() -> None:
    assert _decide().decision_id == _decide().decision_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("outcome", REJECTED),
        ("reason", "evidence:review-2"),
        ("actor", "actor:reviewer-2"),
        ("timestamp", FIXED_TIME + timedelta(seconds=1)),
    ],
)
def test_identity_changes_when_identity_bearing_input_changes(
    field: str,
    value: object,
) -> None:
    baseline = _decide().decision_id
    kwargs = {field: value}
    assert _decide(**kwargs).decision_id != baseline


def test_canonical_evaluation_identity_fields_change_decision_identity() -> None:
    baseline = _decide().decision_id
    assert _decide(evaluation=_evaluation(candidate_id="candidate-2")).decision_id != baseline
    assert _decide(evaluation=_evaluation(candidate_checksum="c" * 64)).decision_id != baseline
    assert _decide(
        evaluation=_evaluation(
            campaign_context_reference=("project-1", "campaign-2")
        )
    ).decision_id != baseline
    assert _decide(
        evaluation=_evaluation(
            instruction_reference=("instruction-2", "APPROVED_INSTRUCTION")
        )
    ).decision_id != baseline


def test_decision_remains_compatible_with_authorization_boundary() -> None:
    decision = _decide()
    authorization = authorize_generated_candidate_decision_action(
        decision,
        requested_action="ASSET_ADMISSION",
        authorization_outcome="AUTHORIZED",
        authorization_reason_evidence_reference="evidence:authorization-1",
        authorization_actor_reference="actor:authorizer-1",
        authorization_timestamp=datetime(
            2026,
            9,
            30,
            11,
            0,
            tzinfo=timezone.utc,
        ),
    )
    assert authorization.candidate_id == "candidate-1"
    assert authorization.candidate_checksum == "b" * 64
    assert authorization.campaign_context_reference == "campaign-1"
    assert authorization.instruction_reference == "instruction-1"


def test_wrong_evaluation_type_fails_closed() -> None:
    with pytest.raises(ValueError, match="GeneratedCandidateEvaluation"):
        _decide(evaluation=object())


def test_canonical_evaluation_rejects_invalid_campaign_binding() -> None:
    with pytest.raises(ValueError, match="campaign project binding"):
        _evaluation(campaign_context_reference=("other-project", "campaign-1"))


def test_canonical_evaluation_rejects_invalid_instruction_shape() -> None:
    with pytest.raises(ValueError, match="instruction_reference"):
        GeneratedCandidateEvaluation(
            evaluation_id="e" * 64,
            creative_result_candidate_id="candidate-1",
            workflow_request_reference="workflow-1",
            project_context_reference="project-1",
            campaign_context_reference=("project-1", "campaign-1"),
            creative_brief_reference="brief-1",
            instruction_reference=("instruction-1",),  # type: ignore[arg-type]
            candidate_content_checksum="b" * 64,
            artifact_type="IMAGE",
            candidate_deterministic_provenance=("source:1",),
            criterion_results=(
                GeneratedCandidateCriterionResult(
                    "criterion-1",
                    "passed",
                    "evidence:criterion-1",
                ),
            ),
            aggregate_outcome="passed",
            evaluator_actor_reference="evaluator-1",
            evaluation_timestamp=datetime(
                2026,
                9,
                30,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            deterministic_provenance=("evaluation:1",),
        )


def test_timezone_naive_decision_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _decide(timestamp=datetime(2026, 9, 30, 10, 30))
