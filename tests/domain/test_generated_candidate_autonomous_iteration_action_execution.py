from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from rie.domain.generated_candidate_autonomous_iteration_action_execution import (
    GeneratedCandidateAutonomousIterationActionExecution,
    derive_autonomous_iteration_control_sha256,
    derive_generated_candidate_autonomous_iteration_action_execution_id,
)


TIMESTAMP = datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc)


def make_execution(**overrides):
    values = {
        "authorization_id": "a" * 64,
        "decision_id": "decision:1",
        "evaluation_id": "evaluation:1",
        "candidate_id": "candidate:1",
        "candidate_checksum": "b" * 64,
        "workflow_request_reference": "workflow:1",
        "project_context_reference": "project:1",
        "campaign_context_reference": "campaign:1",
        "creative_brief_reference": "brief:1",
        "instruction_reference": "instruction:1",
        "decision_outcome": "REJECTED",
        "requested_action": "AUTONOMOUS_ITERATION",
        "authorization_outcome": "AUTHORIZED",
        "iteration_plan_reference": "iteration-plan:1",
        "current_iteration_index": 1,
        "maximum_iteration_count": 3,
        "next_step_reference": "next-step:retry-review:1",
        "execution_actor_reference": "actor:service:iteration",
        "execution_timestamp": TIMESTAMP,
    }
    values.update(overrides)

    control_sha = derive_autonomous_iteration_control_sha256(
        iteration_plan_reference=values["iteration_plan_reference"],
        current_iteration_index=values["current_iteration_index"],
        maximum_iteration_count=values["maximum_iteration_count"],
        next_step_reference=values["next_step_reference"],
    )
    values["iteration_control_sha256"] = control_sha

    execution_id = derive_generated_candidate_autonomous_iteration_action_execution_id(
        authorization_id=values["authorization_id"],
        decision_id=values["decision_id"],
        evaluation_id=values["evaluation_id"],
        candidate_id=values["candidate_id"],
        candidate_checksum=values["candidate_checksum"],
        iteration_control_sha256=control_sha,
        execution_actor_reference=values["execution_actor_reference"],
        execution_timestamp=values["execution_timestamp"],
    )
    values["autonomous_iteration_action_execution_id"] = execution_id
    values["deterministic_provenance"] = (
        f"authorization_sha256:{values['authorization_id']}",
        f"decision_id:{values['decision_id']}",
        f"candidate_sha256:{values['candidate_checksum']}",
        "requested_action:AUTONOMOUS_ITERATION",
        f"iteration_control_sha256:{control_sha}",
        f"autonomous_iteration_action_execution_sha256:{execution_id}",
    )
    return GeneratedCandidateAutonomousIterationActionExecution(**values)


def test_execution_record_is_frozen_and_has_exact_fields():
    assert [field.name for field in fields(
        GeneratedCandidateAutonomousIterationActionExecution
    )] == [
        "autonomous_iteration_action_execution_id",
        "authorization_id",
        "decision_id",
        "evaluation_id",
        "candidate_id",
        "candidate_checksum",
        "workflow_request_reference",
        "project_context_reference",
        "campaign_context_reference",
        "creative_brief_reference",
        "instruction_reference",
        "decision_outcome",
        "requested_action",
        "authorization_outcome",
        "iteration_plan_reference",
        "current_iteration_index",
        "maximum_iteration_count",
        "next_step_reference",
        "iteration_control_sha256",
        "execution_actor_reference",
        "execution_timestamp",
        "deterministic_provenance",
    ]
    value = make_execution()
    with pytest.raises(FrozenInstanceError):
        value.authorization_id = "c" * 64


def test_iteration_control_fingerprint_is_deterministic():
    first = derive_autonomous_iteration_control_sha256(
        iteration_plan_reference="iteration-plan:1",
        current_iteration_index=1,
        maximum_iteration_count=3,
        next_step_reference="next-step:1",
    )
    second = derive_autonomous_iteration_control_sha256(
        iteration_plan_reference="iteration-plan:1",
        current_iteration_index=1,
        maximum_iteration_count=3,
        next_step_reference="next-step:1",
    )
    assert first == second
    assert len(first) == 64


def test_execution_identity_is_deterministic_for_identical_exact_evidence():
    assert (
        make_execution().autonomous_iteration_action_execution_id
        == make_execution().autonomous_iteration_action_execution_id
    )


def test_execution_rejects_wrong_action_or_outcome():
    with pytest.raises(ValueError, match="requested_action"):
        make_execution(requested_action="RETRY_REGENERATION")
    with pytest.raises(ValueError, match="authorization_outcome"):
        make_execution(authorization_outcome="DENIED")


@pytest.mark.parametrize(
    ("current_index", "maximum_count", "message"),
    (
        (-1, 3, "non-negative"),
        (0, 0, "positive"),
        (3, 3, "less than"),
        (4, 3, "less than"),
    ),
)
def test_iteration_bound_fails_closed(current_index, maximum_count, message):
    with pytest.raises(ValueError, match=message):
        derive_autonomous_iteration_control_sha256(
            iteration_plan_reference="iteration-plan:1",
            current_iteration_index=current_index,
            maximum_iteration_count=maximum_count,
            next_step_reference="next-step:1",
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("iteration_plan_reference", "memory:plan", "immutable"),
        ("iteration_plan_reference", "plan api_key hidden", "secret material"),
        ("next_step_reference", "temp:next", "immutable"),
        ("next_step_reference", "authorization: hidden", "secret material"),
    ),
)
def test_iteration_references_reject_mutable_or_secret_material(field, value, message):
    kwargs = {
        "iteration_plan_reference": "iteration-plan:1",
        "current_iteration_index": 0,
        "maximum_iteration_count": 2,
        "next_step_reference": "next-step:1",
    }
    kwargs[field] = value
    with pytest.raises(ValueError, match=message):
        derive_autonomous_iteration_control_sha256(**kwargs)


def test_execution_rejects_secret_bearing_actor_reference():
    with pytest.raises(ValueError, match="secret material"):
        make_execution(execution_actor_reference="actor secret token")


def test_execution_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        make_execution(execution_timestamp=datetime(2026, 10, 3, 15, 0))


def test_execution_rejects_tampered_iteration_control_sha():
    value = make_execution()
    with pytest.raises(ValueError, match="iteration_control_sha256 mismatch"):
        GeneratedCandidateAutonomousIterationActionExecution(
            **{
                **value.__dict__,
                "iteration_control_sha256": "c" * 64,
            }
        )


def test_execution_rejects_tampered_provenance():
    value = make_execution()
    with pytest.raises(ValueError, match="deterministic_provenance mismatch"):
        GeneratedCandidateAutonomousIterationActionExecution(
            **{
                **value.__dict__,
                "deterministic_provenance": ("tampered",),
            }
        )
