from datetime import datetime, timedelta, timezone

import pytest

from rie.application.decide_generated_candidate import decide_generated_candidate
from rie.domain.generated_candidate_decision import ACCEPTED, DEFERRED, REJECTED
from rie.domain.generated_candidate_evaluation import GeneratedCandidateEvaluation


FIXED_TIME = datetime(2026, 9, 30, 10, 30, tzinfo=timezone.utc)


def _evaluation(
    *,
    aggregate_outcome: str = "passed",
    evaluation_id: str = "evaluation-1",
) -> GeneratedCandidateEvaluation:
    evaluation = object.__new__(GeneratedCandidateEvaluation)
    values = {
        "evaluation_id": evaluation_id,
        "candidate_id": "candidate-1",
        "workflow_request_reference": "workflow-1",
        "project_context_reference": "project-1",
        "campaign_context_reference": "campaign-1",
        "creative_brief_reference": "brief-1",
        "instruction_reference": "instruction-1",
        "candidate_checksum": "b" * 64,
        "artifact_type": "IMAGE",
        "aggregate_outcome": aggregate_outcome,
        "deterministic_provenance": (
            "candidate:candidate-1",
            "content_sha256:" + "b" * 64,
            "evaluation_sha256:" + "c" * 64,
        ),
    }
    for name, value in values.items():
        object.__setattr__(evaluation, name, value)
    return evaluation


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


def test_explicit_decision_preserves_exact_evaluation_lineage() -> None:
    decision = _decide()
    assert decision.evaluation_id == "evaluation-1"
    assert decision.candidate_id == "candidate-1"
    assert decision.candidate_checksum == "b" * 64
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
    field: str, value: object
) -> None:
    baseline = _decide().decision_id
    kwargs = {field: value}
    assert _decide(**kwargs).decision_id != baseline


def test_wrong_evaluation_type_fails_closed() -> None:
    with pytest.raises(ValueError, match="GeneratedCandidateEvaluation"):
        _decide(evaluation=object())


def test_timezone_naive_decision_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        _decide(timestamp=datetime(2026, 9, 30, 10, 30))
