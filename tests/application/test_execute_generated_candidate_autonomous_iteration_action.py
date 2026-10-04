from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rie.application.execute_generated_candidate_autonomous_iteration_action import (
    execute_generated_candidate_autonomous_iteration_action,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)


TIMESTAMP = datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc)


def make_authorization(**overrides):
    values = {
        "authorization_id": "a" * 64,
        "decision_id": "decision:1",
        "evaluation_id": "evaluation:1",
        "candidate_id": "candidate:1",
        "workflow_request_reference": "workflow:1",
        "project_context_reference": "project:1",
        "campaign_context_reference": "campaign:1",
        "creative_brief_reference": "brief:1",
        "instruction_reference": "instruction:1",
        "candidate_checksum": "b" * 64,
        "artifact_type": "IMAGE",
        "decision_outcome": "REJECTED",
        "requested_action": "AUTONOMOUS_ITERATION",
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence:iteration:1",
        "authorization_actor_reference": "actor:governance:1",
        "authorization_timestamp": TIMESTAMP,
    }
    values.update(overrides)
    values["deterministic_provenance"] = (
        f"candidate_sha256:{values['candidate_checksum']}",
        f"evaluation_id:{values['evaluation_id']}",
        f"decision_id:{values['decision_id']}",
        f"requested_action:{values['requested_action']}",
        f"authorization_sha256:{values['authorization_id']}",
    )
    return GeneratedCandidateDecisionActionAuthorization(**values)


def execute(**overrides):
    values = {
        "authorization": make_authorization(),
        "iteration_plan_reference": "iteration-plan:1",
        "current_iteration_index": 1,
        "maximum_iteration_count": 3,
        "next_step_reference": "next-step:review:2",
        "execution_actor_reference": "actor:service:iteration",
        "execution_timestamp": TIMESTAMP,
    }
    values.update(overrides)
    return execute_generated_candidate_autonomous_iteration_action(**values)


def test_authorized_autonomous_iteration_materializes_one_exact_bounded_advance():
    result = execute()

    assert result.authorization_id == "a" * 64
    assert result.candidate_id == "candidate:1"
    assert result.requested_action == "AUTONOMOUS_ITERATION"
    assert result.authorization_outcome == "AUTHORIZED"
    assert result.iteration_plan_reference == "iteration-plan:1"
    assert result.current_iteration_index == 1
    assert result.maximum_iteration_count == 3
    assert result.next_step_reference == "next-step:review:2"
    assert len(result.iteration_control_sha256) == 64
    assert len(result.autonomous_iteration_action_execution_id) == 64


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("requested_action", "RETRY_REGENERATION", "requested_action"),
        ("authorization_outcome", "DENIED", "outcome"),
        ("authorization_outcome", "DEFERRED", "outcome"),
    ),
)
def test_wrong_authorization_surface_fails_closed(field, value, message):
    authorization = make_authorization(**{field: value})
    with pytest.raises(ValueError, match=message):
        execute(authorization=authorization)


def test_tampered_authorization_provenance_fails_closed():
    authorization = replace(
        make_authorization(),
        deterministic_provenance=("tampered",),
    )
    with pytest.raises(ValueError, match="provenance"):
        execute(authorization=authorization)


@pytest.mark.parametrize(
    ("current_index", "maximum_count", "message"),
    (
        (-1, 3, "non-negative"),
        (0, 0, "positive"),
        (3, 3, "less than"),
    ),
)
def test_explicit_iteration_bounds_fail_closed(current_index, maximum_count, message):
    with pytest.raises(ValueError, match=message):
        execute(
            current_iteration_index=current_index,
            maximum_iteration_count=maximum_count,
        )


def test_next_step_reference_is_preserved_exactly_and_not_inferred():
    first = execute(next_step_reference="next-step:review:2")
    second = execute(next_step_reference="next-step:manual:2")

    assert first.next_step_reference == "next-step:review:2"
    assert second.next_step_reference == "next-step:manual:2"
    assert first.iteration_control_sha256 != second.iteration_control_sha256
    assert (
        first.autonomous_iteration_action_execution_id
        != second.autonomous_iteration_action_execution_id
    )


def test_iteration_index_is_preserved_exactly_and_not_incremented():
    result = execute(current_iteration_index=1, maximum_iteration_count=3)
    assert result.current_iteration_index == 1
    assert result.maximum_iteration_count == 3


def test_identical_exact_evidence_produces_deterministic_execution_identity():
    first = execute()
    second = execute()

    assert (
        first.autonomous_iteration_action_execution_id
        == second.autonomous_iteration_action_execution_id
    )
    assert first.deterministic_provenance == second.deterministic_provenance


def test_execution_does_not_mutate_authorization():
    authorization = make_authorization()
    before = authorization
    execute(authorization=authorization)
    assert authorization == before


def test_application_surface_has_no_provider_or_downstream_action_execution():
    source_path = Path(__file__).parents[2] / (
        "src/rie/application/"
        "execute_generated_candidate_autonomous_iteration_action.py"
    )
    source = source_path.read_text(encoding="utf-8")

    forbidden = (
        "ConcreteVisualGenerationExecutionAdapter",
        "ProviderTransport",
        "execute_generated_candidate_retry_regeneration_action",
        "execute_generated_candidate_workflow_transition_action",
        "execute_generated_candidate_asset_admission",
        "bridge_generated_output_to_creative_result_candidate",
        "authorize_generated_candidate_decision_action(",
    )
    for token in forbidden:
        assert token not in source


def test_application_surface_has_no_loop_or_recursive_execution():
    source_path = Path(__file__).parents[2] / (
        "src/rie/application/"
        "execute_generated_candidate_autonomous_iteration_action.py"
    )
    source = source_path.read_text(encoding="utf-8")

    assert "\n    for " not in source
    assert "\n    while " not in source
    assert source.count(
        "execute_generated_candidate_autonomous_iteration_action("
    ) == 1


def test_output_is_iteration_evidence_only_not_candidate_or_workflow_mutation():
    result = execute()

    assert not hasattr(result, "creative_result_candidate_id")
    assert not hasattr(result, "workflow_transition_evaluation")
    assert not hasattr(result, "admitted_asset_reference")
