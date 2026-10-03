from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from rie.application.execute_generated_candidate_workflow_transition_action import (
    execute_generated_candidate_workflow_transition_action,
)
from rie.domain.evaluate_governed_creative_workflow_transition import (
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)


PROJECT = "project:alpha"
CAMPAIGN_ID = "campaign:one"
CAMPAIGN = (PROJECT, CAMPAIGN_ID)
INSTRUCTION_ID = "instruction:approved:001"
INSTRUCTION = (INSTRUCTION_ID, "APPROVED_INSTRUCTION")
ACTOR_ID = "actor:service:001"
ACTOR = ("ACTOR", ACTOR_ID)
TIMESTAMP = datetime(2026, 10, 3, 1, 0, tzinfo=timezone.utc)


def make_authorization(**overrides):
    values = {
        "authorization_id": "a" * 64,
        "decision_id": "d" * 64,
        "evaluation_id": "evaluation:001",
        "candidate_id": "candidate:001",
        "workflow_request_reference": "workflow-request:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN_ID,
        "creative_brief_reference": "brief:approved:001",
        "instruction_reference": INSTRUCTION_ID,
        "candidate_checksum": "b" * 64,
        "artifact_type": "image/png",
        "decision_outcome": "ACCEPTED",
        "requested_action": "WORKFLOW_TRANSITION",
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence:authorization:001",
        "authorization_actor_reference": "actor:governance:001",
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


def make_kwargs(**overrides):
    values = {
        "idempotency_key": "idempotency:001",
        "campaign_context_reference": CAMPAIGN,
        "instruction_reference": INSTRUCTION,
        "current_workflow_state": "REQUESTED",
        "requested_next_workflow_state": "INPUTS_VALIDATED",
        "responsible_actor_or_service_reference": ACTOR,
        "evidence_references": ((PROJECT, CAMPAIGN_ID, "evidence:001"),),
        "reason_codes": ("TRANSITION_ACCEPTED",),
        "workflow_contract_reference": ("GATE_18_CREATIVE_WORKFLOW", "1.0"),
        "canonical_input_fingerprint": "1" * 64,
        "execution_actor_reference": ACTOR_ID,
        "execution_timestamp": TIMESTAMP,
    }
    values.update(overrides)
    return values


def test_authorized_workflow_transition_executes_evaluator_once_and_binds_authorization():
    calls = []

    def spy(**kwargs):
        calls.append(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    authorization = make_authorization()
    result = execute_generated_candidate_workflow_transition_action(
        authorization,
        workflow_transition_evaluator=spy,
        **make_kwargs(),
    )

    assert len(calls) == 1
    assert (
        PROJECT,
        CAMPAIGN_ID,
        f"authorization_sha256:{authorization.authorization_id}",
    ) in calls[0]["evidence_references"]
    assert result.authorization_id == authorization.authorization_id
    assert result.requested_next_workflow_state == "INPUTS_VALIDATED"


def test_prohibited_execution_and_mutation_flags_are_all_false():
    captured = {}

    def spy(**kwargs):
        captured.update(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    execute_generated_candidate_workflow_transition_action(
        make_authorization(),
        workflow_transition_evaluator=spy,
        **make_kwargs(),
    )

    for name in (
        "authority_bypass_requested",
        "prohibited_automation_requested",
        "approval_execution_requested",
        "asset_admission_execution_requested",
        "lifecycle_mutation_requested",
        "production_release_requested",
    ):
        assert captured[name] is False


def test_execution_is_deterministic_for_identical_exact_inputs():
    first = execute_generated_candidate_workflow_transition_action(
        make_authorization(),
        **make_kwargs(),
    )
    second = execute_generated_candidate_workflow_transition_action(
        make_authorization(),
        **make_kwargs(),
    )
    assert (
        first.workflow_transition_action_execution_id
        == second.workflow_transition_action_execution_id
    )
    assert first.deterministic_provenance == second.deterministic_provenance


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("requested_action", "ASSET_ADMISSION", "requested_action"),
        ("authorization_outcome", "DENIED", "outcome"),
    ),
)
def test_wrong_authorization_surface_fails_before_evaluator(field, value, message):
    calls = []

    def spy(**kwargs):
        calls.append(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    authorization = make_authorization(**{field: value})
    with pytest.raises(ValueError, match=message):
        execute_generated_candidate_workflow_transition_action(
            authorization,
            workflow_transition_evaluator=spy,
            **make_kwargs(),
        )
    assert calls == []


def test_tampered_authorization_provenance_fails_before_evaluator():
    calls = []

    def spy(**kwargs):
        calls.append(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    authorization = replace(
        make_authorization(),
        deterministic_provenance=("tampered",),
    )
    with pytest.raises(ValueError, match="provenance"):
        execute_generated_candidate_workflow_transition_action(
            authorization,
            workflow_transition_evaluator=spy,
            **make_kwargs(),
        )
    assert calls == []


def test_campaign_binding_mismatch_fails_before_evaluator():
    with pytest.raises(ValueError, match="campaign identity"):
        execute_generated_candidate_workflow_transition_action(
            make_authorization(),
            **make_kwargs(
                campaign_context_reference=(PROJECT, "campaign:other"),
            ),
        )


def test_instruction_binding_mismatch_fails_before_evaluator():
    with pytest.raises(ValueError, match="instruction identity"):
        execute_generated_candidate_workflow_transition_action(
            make_authorization(),
            **make_kwargs(
                instruction_reference=("instruction:other", "APPROVED_INSTRUCTION"),
            ),
        )


def test_execution_actor_binding_mismatch_fails_before_evaluator():
    with pytest.raises(ValueError, match="responsible actor identity"):
        execute_generated_candidate_workflow_transition_action(
            make_authorization(),
            **make_kwargs(execution_actor_reference="actor:other"),
        )


def test_naive_execution_timestamp_fails_before_evaluator():
    with pytest.raises(ValueError, match="timezone-aware"):
        execute_generated_candidate_workflow_transition_action(
            make_authorization(),
            **make_kwargs(execution_timestamp=datetime(2026, 10, 3, 1, 0)),
        )


def test_evaluator_must_return_exact_evaluation_type():
    def invalid_evaluator(**kwargs):
        return object()

    with pytest.raises(ValueError, match="must return an exact"):
        execute_generated_candidate_workflow_transition_action(
            make_authorization(),
            workflow_transition_evaluator=invalid_evaluator,
            **make_kwargs(),
        )


def test_execution_does_not_mutate_authorization():
    authorization = make_authorization()
    before = authorization
    execute_generated_candidate_workflow_transition_action(
        authorization,
        **make_kwargs(),
    )
    assert authorization == before
