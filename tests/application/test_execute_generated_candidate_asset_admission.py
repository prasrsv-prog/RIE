from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from rie.application.execute_generated_candidate_asset_admission import (
    execute_generated_candidate_asset_admission,
)
from rie.domain.creative_result_candidate import (
    CANDIDATE_AUTHORITY_STATE,
    CreativeResultCandidate,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)


FIXED_TIME = datetime(2026, 10, 1, 6, 30, tzinfo=timezone.utc)


def _candidate(**overrides):
    values = {
        "creative_result_candidate_id": "candidate-1",
        "workflow_request_reference": "workflow-1",
        "project_context_reference": "project-1",
        "campaign_context_reference": ("project-1", "campaign-1"),
        "creative_brief_reference": "brief-1",
        "instruction_reference": ("instruction-1", "APPROVED_INSTRUCTION"),
        "originating_manual_handoff_reference": None,
        "candidate_content_checksum": "b" * 64,
        "artifact_type": "IMAGE",
        "admission_timestamp": datetime(2026, 9, 30, 8, 0, tzinfo=timezone.utc),
        "admitting_actor_reference": "service-1",
        "deterministic_provenance": (
            "workflow_request:workflow-1",
            "content_sha256:" + "b" * 64,
        ),
        "authority_state": CANDIDATE_AUTHORITY_STATE,
        "official_source_claimed": False,
        "accepted_asset_claimed": False,
        "approved_asset_claimed": False,
    }
    values.update(overrides)
    return CreativeResultCandidate(**values)


def _authorization(**overrides):
    authorization_id = overrides.pop("authorization_id", "a" * 64)
    candidate_checksum = overrides.pop("candidate_checksum", "b" * 64)
    evaluation_id = overrides.pop("evaluation_id", "evaluation-1")
    decision_id = overrides.pop("decision_id", "d" * 64)
    requested_action = overrides.pop("requested_action", "ASSET_ADMISSION")
    values = {
        "authorization_id": authorization_id,
        "decision_id": decision_id,
        "evaluation_id": evaluation_id,
        "candidate_id": "candidate-1",
        "workflow_request_reference": "workflow-1",
        "project_context_reference": "project-1",
        "campaign_context_reference": "campaign-1",
        "creative_brief_reference": "brief-1",
        "instruction_reference": "instruction-1",
        "candidate_checksum": candidate_checksum,
        "artifact_type": "IMAGE",
        "decision_outcome": "ACCEPTED",
        "requested_action": requested_action,
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence-1",
        "authorization_actor_reference": "authorizer-1",
        "authorization_timestamp": datetime(
            2026, 10, 1, 5, 30, tzinfo=timezone.utc
        ),
        "deterministic_provenance": (
            f"candidate_sha256:{candidate_checksum}",
            f"evaluation_id:{evaluation_id}",
            f"decision_id:{decision_id}",
            f"requested_action:{requested_action}",
            f"authorization_sha256:{authorization_id}",
        ),
    }
    values.update(overrides)
    return GeneratedCandidateDecisionActionAuthorization(**values)


def _execute(authorization=None, candidate=None, **overrides):
    values = {
        "admitted_asset_reference": "asset-1",
        "execution_actor_reference": "asset-service-1",
        "execution_timestamp": FIXED_TIME,
    }
    values.update(overrides)
    return execute_generated_candidate_asset_admission(
        _authorization() if authorization is None else authorization,
        _candidate() if candidate is None else candidate,
        **values,
    )


def test_authorized_accepted_candidate_constructs_exact_admission_record():
    record = _execute()
    assert record.authorization_id == "a" * 64
    assert record.decision_id == "d" * 64
    assert record.evaluation_id == "evaluation-1"
    assert record.candidate_id == "candidate-1"
    assert record.candidate_checksum == "b" * 64
    assert record.admitted_asset_reference == "asset-1"
    assert record.execution_outcome == "ADMITTED"


def test_same_inputs_produce_same_deterministic_execution_identity():
    assert (
        _execute().asset_admission_execution_id
        == _execute().asset_admission_execution_id
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("admitted_asset_reference", "asset-2"),
        ("execution_actor_reference", "asset-service-2"),
        ("execution_timestamp", FIXED_TIME + timedelta(seconds=1)),
    ],
)
def test_explicit_execution_input_changes_identity(field, value):
    baseline = _execute().asset_admission_execution_id
    assert _execute(**{field: value}).asset_admission_execution_id != baseline


def test_wrong_authorization_type_fails_closed():
    with pytest.raises(ValueError, match="GeneratedCandidateDecisionActionAuthorization"):
        _execute(authorization=object())


def test_wrong_candidate_type_fails_closed():
    with pytest.raises(ValueError, match="CreativeResultCandidate"):
        _execute(candidate=object())


def test_non_asset_admission_authorization_fails_closed():
    with pytest.raises(ValueError, match="ASSET_ADMISSION"):
        _execute(
            authorization=_authorization(
                requested_action="WORKFLOW_TRANSITION"
            )
        )


def test_non_authorized_outcome_fails_closed():
    with pytest.raises(ValueError, match="AUTHORIZED"):
        _execute(
            authorization=_authorization(
                authorization_outcome="DENIED"
            )
        )


def test_non_accepted_decision_fails_closed():
    with pytest.raises(ValueError, match="ACCEPTED"):
        _execute(
            authorization=_authorization(
                decision_outcome="REJECTED"
            )
        )


def test_candidate_identity_mismatch_fails_closed():
    with pytest.raises(ValueError, match="candidate identity"):
        _execute(candidate=_candidate(creative_result_candidate_id="candidate-2"))


def test_candidate_checksum_mismatch_fails_closed():
    with pytest.raises(ValueError, match="checksum"):
        _execute(candidate=_candidate(candidate_content_checksum="c" * 64))


def test_workflow_project_or_artifact_mismatch_fails_closed():
    with pytest.raises(ValueError, match="workflow request"):
        _execute(candidate=_candidate(workflow_request_reference="workflow-2"))
    with pytest.raises(ValueError, match="project context"):
        _execute(
            candidate=_candidate(
                project_context_reference="project-2",
                campaign_context_reference=("project-2", "campaign-1"),
            )
        )
    with pytest.raises(ValueError, match="artifact type"):
        _execute(candidate=_candidate(artifact_type="VIDEO"))


def test_authorization_lineage_provenance_mismatch_fails_closed():
    authorization = _authorization(
        deterministic_provenance=(
            "candidate_sha256:" + "b" * 64,
            "evaluation_id:evaluation-1",
            "decision_id:" + "d" * 64,
            "requested_action:ASSET_ADMISSION",
            "authorization_sha256:" + "f" * 64,
        )
    )
    with pytest.raises(ValueError, match="provenance"):
        _execute(authorization=authorization)


def test_timezone_naive_execution_timestamp_fails_closed():
    with pytest.raises(ValueError, match="timezone-aware"):
        _execute(execution_timestamp=datetime(2026, 10, 1, 6, 30))


def test_execution_does_not_mutate_candidate_or_authorization():
    authorization = _authorization()
    candidate = _candidate()
    record = _execute(authorization=authorization, candidate=candidate)
    assert candidate.authority_state == "CANDIDATE"
    assert candidate.accepted_asset_claimed is False
    assert authorization.requested_action == "ASSET_ADMISSION"
    with pytest.raises(FrozenInstanceError):
        record.execution_outcome = "OTHER"
