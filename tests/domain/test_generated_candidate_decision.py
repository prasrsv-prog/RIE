from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.domain.generated_candidate_decision import (
    ACCEPTED,
    DEFERRED,
    REJECTED,
    GeneratedCandidateDecision,
)


FIXED_TIME = datetime(2026, 9, 30, 10, 0, tzinfo=timezone.utc)


def _decision(**overrides: object) -> GeneratedCandidateDecision:
    values: dict[str, object] = {
        "decision_id": "a" * 64,
        "evaluation_id": "evaluation-1",
        "candidate_id": "candidate-1",
        "workflow_request_reference": "workflow-1",
        "project_context_reference": "project-1",
        "campaign_context_reference": "campaign-1",
        "creative_brief_reference": "brief-1",
        "instruction_reference": "instruction-1",
        "candidate_checksum": "b" * 64,
        "artifact_type": "IMAGE",
        "evaluation_aggregate_outcome": "passed",
        "decision_outcome": ACCEPTED,
        "decision_reason_evidence_reference": "evidence:review-1",
        "decision_actor_reference": "actor:reviewer-1",
        "decision_timestamp": FIXED_TIME,
        "deterministic_provenance": (
            "candidate:candidate-1",
            "evaluation:evaluation-1",
            "decision_sha256:" + "a" * 64,
        ),
    }
    values.update(overrides)
    return GeneratedCandidateDecision(**values)


@pytest.mark.parametrize("outcome", [ACCEPTED, REJECTED, DEFERRED])
def test_controlled_decision_outcomes_are_accepted(outcome: str) -> None:
    assert _decision(decision_outcome=outcome).decision_outcome == outcome


def test_uncontrolled_decision_outcome_fails_closed() -> None:
    with pytest.raises(ValueError, match="decision_outcome"):
        _decision(decision_outcome="APPROVED")


def test_invalid_candidate_checksum_fails_closed() -> None:
    with pytest.raises(ValueError, match="candidate_checksum"):
        _decision(candidate_checksum="ABC")


def test_timezone_naive_decision_timestamp_fails_closed() -> None:
    with pytest.raises(ValueError, match="decision_timestamp"):
        _decision(decision_timestamp=datetime(2026, 9, 30, 10, 0))


def test_decision_record_is_immutable() -> None:
    decision = _decision()
    with pytest.raises(FrozenInstanceError):
        decision.decision_outcome = REJECTED  # type: ignore[misc]
