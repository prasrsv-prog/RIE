from datetime import datetime, timezone

import pytest

from rie.application.authorize_generated_candidate_decision_action import (
    authorize_generated_candidate_decision_action,
)
from rie.domain.generated_candidate_decision import GeneratedCandidateDecision


FIXED_TIME = datetime(2026, 10, 1, 3, 0, tzinfo=timezone.utc)


def _decision(*, decision_outcome="ACCEPTED", provenance=None):
    decision = object.__new__(GeneratedCandidateDecision)
    fields = {
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
        "decision_outcome": decision_outcome,
        "deterministic_provenance": provenance
        if provenance is not None
        else (
            "candidate_sha256:" + ("b" * 64),
            "evaluation_id:evaluation-1",
            "decision_sha256:" + ("c" * 64),
        ),
    }
    for name, value in fields.items():
        object.__setattr__(decision, name, value)
    return decision


def _authorize(decision=None, **overrides):
    values = {
        "requested_action": "ASSET_ADMISSION",
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence-1",
        "authorization_actor_reference": "actor-1",
        "authorization_timestamp": FIXED_TIME,
    }
    values.update(overrides)
    return authorize_generated_candidate_decision_action(
        _decision() if decision is None else decision,
        **values,
    )


def test_authorizes_only_evidence_for_explicit_requested_action():
    record = _authorize()
    assert record.requested_action == "ASSET_ADMISSION"
    assert record.authorization_outcome == "AUTHORIZED"
    assert record.decision_outcome == "ACCEPTED"


def test_rejected_decision_does_not_implicitly_choose_retry():
    record = _authorize(
        _decision(decision_outcome="REJECTED"),
        requested_action="WORKFLOW_TRANSITION",
        authorization_outcome="DENIED",
    )
    assert record.decision_outcome == "REJECTED"
    assert record.requested_action == "WORKFLOW_TRANSITION"
    assert record.authorization_outcome == "DENIED"


def test_same_inputs_produce_same_authorization_id():
    first = _authorize()
    second = _authorize()
    assert first.authorization_id == second.authorization_id
    assert first.deterministic_provenance == second.deterministic_provenance


def test_requested_action_changes_authorization_identity():
    first = _authorize(requested_action="ASSET_ADMISSION")
    second = _authorize(requested_action="WORKFLOW_TRANSITION")
    assert first.authorization_id != second.authorization_id


def test_authorization_outcome_changes_authorization_identity():
    first = _authorize(authorization_outcome="AUTHORIZED")
    second = _authorize(authorization_outcome="DENIED")
    assert first.authorization_id != second.authorization_id


def test_rejects_non_decision_input():
    with pytest.raises(ValueError):
        authorize_generated_candidate_decision_action(
            object(),
            requested_action="ASSET_ADMISSION",
            authorization_outcome="AUTHORIZED",
            authorization_reason_evidence_reference="evidence-1",
            authorization_actor_reference="actor-1",
            authorization_timestamp=FIXED_TIME,
        )


def test_rejects_naive_authorization_timestamp():
    with pytest.raises(ValueError):
        _authorize(
            authorization_timestamp=datetime(2026, 10, 1, 3, 0)
        )


def test_rejects_duplicate_upstream_decision_provenance():
    with pytest.raises(ValueError):
        _authorize(
            _decision(provenance=("same", "same"))
        )


def test_authorization_provenance_binds_candidate_evaluation_decision_action_and_record():
    record = _authorize(requested_action="AUTONOMOUS_ITERATION")
    assert record.deterministic_provenance == (
        "candidate_sha256:" + ("b" * 64),
        "evaluation_id:evaluation-1",
        "decision_id:decision-1",
        "requested_action:AUTONOMOUS_ITERATION",
        "authorization_sha256:" + record.authorization_id,
    )
