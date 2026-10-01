from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)


FIXED_TIME = datetime(2026, 10, 1, 3, 0, tzinfo=timezone.utc)


def _authorization(**overrides):
    values = {
        "authorization_id": "a" * 64,
        "decision_id": "decision-1",
        "evaluation_id": "evaluation-1",
        "candidate_id": "candidate-1",
        "workflow_request_reference": "workflow-1",
        "project_context_reference": "project-1",
        "campaign_context_reference": "campaign-1",
        "creative_brief_reference": "brief-1",
        "instruction_reference": "instruction-1",
        "candidate_checksum": "b" * 64,
        "artifact_type": "IMAGE",
        "decision_outcome": "ACCEPTED",
        "requested_action": "ASSET_ADMISSION",
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence-1",
        "authorization_actor_reference": "actor-1",
        "authorization_timestamp": FIXED_TIME,
        "deterministic_provenance": (
            "candidate_sha256:" + ("b" * 64),
            "evaluation_id:evaluation-1",
            "decision_id:decision-1",
            "requested_action:ASSET_ADMISSION",
            "authorization_sha256:" + ("a" * 64),
        ),
    }
    values.update(overrides)
    return GeneratedCandidateDecisionActionAuthorization(**values)


def test_valid_authorization_record_is_immutable_evidence():
    record = _authorization()
    assert record.requested_action == "ASSET_ADMISSION"
    assert record.authorization_outcome == "AUTHORIZED"


def test_authorization_record_is_frozen():
    record = _authorization()
    with pytest.raises(FrozenInstanceError):
        record.authorization_outcome = "DENIED"


@pytest.mark.parametrize("requested_action", ["", "ASSET_APPROVAL"])
def test_rejects_unsupported_requested_action(requested_action):
    with pytest.raises(ValueError):
        _authorization(requested_action=requested_action)


@pytest.mark.parametrize("authorization_outcome", ["", "APPROVED"])
def test_rejects_unsupported_authorization_outcome(authorization_outcome):
    with pytest.raises(ValueError):
        _authorization(authorization_outcome=authorization_outcome)


def test_rejects_non_ascii_reason_reference():
    with pytest.raises(ValueError):
        _authorization(authorization_reason_evidence_reference="bukti-é")


def test_rejects_naive_timestamp():
    with pytest.raises(ValueError):
        _authorization(
            authorization_timestamp=datetime(2026, 10, 1, 3, 0)
        )


def test_rejects_duplicate_provenance():
    with pytest.raises(ValueError):
        _authorization(deterministic_provenance=("same", "same"))
