from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from rie.domain.evaluate_governed_creative_workflow_transition import (
    GovernedCreativeWorkflowTransitionEvaluation,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_workflow_transition_action_execution import (
    GeneratedCandidateWorkflowTransitionActionExecution,
    derive_generated_candidate_workflow_transition_action_execution_id,
    derive_workflow_transition_evaluation_sha256,
)


PROJECT = "project:alpha"
CAMPAIGN = (PROJECT, "campaign:one")
TIMESTAMP = datetime(2026, 10, 3, 1, 0, tzinfo=timezone.utc)


def make_evaluation():
    return evaluate_governed_creative_workflow_transition(
        workflow_request_reference="workflow-request:001",
        idempotency_key="idempotency:001",
        project_context_reference=PROJECT,
        campaign_context_reference=CAMPAIGN,
        creative_brief_reference="brief:approved:001",
        instruction_reference=("instruction:approved:001", "APPROVED_INSTRUCTION"),
        current_workflow_state="REQUESTED",
        requested_next_workflow_state="INPUTS_VALIDATED",
        responsible_actor_or_service_reference=("ACTOR", "actor:service:001"),
        event_timestamp=TIMESTAMP,
        evidence_references=((PROJECT, CAMPAIGN[1], "evidence:001"),),
        reason_codes=("TRANSITION_ACCEPTED",),
        workflow_contract_reference=("GATE_18_CREATIVE_WORKFLOW", "1.0"),
        canonical_input_fingerprint="1" * 64,
    )


def make_execution(**overrides):
    evaluation = overrides.pop("workflow_transition_evaluation", make_evaluation())
    values = {
        "authorization_id": "a" * 64,
        "decision_id": "d" * 64,
        "evaluation_id": "evaluation:001",
        "candidate_id": "candidate:001",
        "candidate_checksum": "b" * 64,
        "workflow_request_reference": "workflow-request:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN[1],
        "creative_brief_reference": "brief:approved:001",
        "instruction_reference": "instruction:approved:001",
        "decision_outcome": "ACCEPTED",
        "requested_action": "WORKFLOW_TRANSITION",
        "authorization_outcome": "AUTHORIZED",
        "requested_next_workflow_state": "INPUTS_VALIDATED",
        "execution_actor_reference": "actor:service:001",
        "execution_timestamp": TIMESTAMP,
        "workflow_transition_evaluation": evaluation,
    }
    values.update(overrides)
    execution_id = derive_generated_candidate_workflow_transition_action_execution_id(
        authorization_id=values["authorization_id"],
        decision_id=values["decision_id"],
        evaluation_id=values["evaluation_id"],
        candidate_id=values["candidate_id"],
        candidate_checksum=values["candidate_checksum"],
        requested_next_workflow_state=values["requested_next_workflow_state"],
        workflow_transition_evaluation=values["workflow_transition_evaluation"],
        execution_actor_reference=values["execution_actor_reference"],
        execution_timestamp=values["execution_timestamp"],
    )
    evaluation_sha = derive_workflow_transition_evaluation_sha256(
        values["workflow_transition_evaluation"]
    )
    values["workflow_transition_action_execution_id"] = execution_id
    values["deterministic_provenance"] = (
        f"authorization_sha256:{values['authorization_id']}",
        f"decision_id:{values['decision_id']}",
        f"candidate_sha256:{values['candidate_checksum']}",
        "requested_action:WORKFLOW_TRANSITION",
        f"workflow_transition_evaluation_sha256:{evaluation_sha}",
        f"workflow_transition_action_execution_sha256:{execution_id}",
    )
    return GeneratedCandidateWorkflowTransitionActionExecution(**values)


def test_execution_record_is_frozen_and_has_exact_fields():
    assert [field.name for field in fields(
        GeneratedCandidateWorkflowTransitionActionExecution
    )] == [
        "workflow_transition_action_execution_id",
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
        "requested_next_workflow_state",
        "execution_actor_reference",
        "execution_timestamp",
        "workflow_transition_evaluation",
        "deterministic_provenance",
    ]
    value = make_execution()
    with pytest.raises(FrozenInstanceError):
        value.authorization_id = "c" * 64


def test_evaluation_sha256_is_deterministic():
    first = derive_workflow_transition_evaluation_sha256(make_evaluation())
    second = derive_workflow_transition_evaluation_sha256(make_evaluation())
    assert first == second
    assert len(first) == 64


def test_execution_identity_is_deterministic():
    assert (
        make_execution().workflow_transition_action_execution_id
        == make_execution().workflow_transition_action_execution_id
    )


def test_execution_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        make_execution(execution_timestamp=datetime(2026, 10, 3, 1, 0))


def test_execution_rejects_non_exact_evaluation_type():
    with pytest.raises(ValueError, match="exact GovernedCreativeWorkflowTransitionEvaluation"):
        derive_workflow_transition_evaluation_sha256(object())


def test_execution_rejects_tampered_provenance():
    value = make_execution()
    with pytest.raises(ValueError, match="deterministic_provenance mismatch"):
        GeneratedCandidateWorkflowTransitionActionExecution(
            **{
                **value.__dict__,
                "deterministic_provenance": ("tampered",),
            }
        )
