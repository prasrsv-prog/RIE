from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.domain.evaluate_governed_creative_workflow_transition import (
    TRANSITION_DISPOSITION_ACCEPTED,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_asset_admission_workflow_transition_consumption import (
    GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption,
    derive_generated_candidate_asset_admission_workflow_transition_consumption_id,
    derive_workflow_transition_evaluation_sha256,
)


PROJECT = "project:001"
CAMPAIGN = (PROJECT, "campaign:001")
ASSET = (PROJECT, CAMPAIGN[1], "asset:generated:001")
NOW = datetime(2026, 10, 2, 6, 0, tzinfo=timezone.utc)


def _evaluation():
    return evaluate_governed_creative_workflow_transition(
        workflow_request_reference="workflow:001",
        idempotency_key="idem:001",
        project_context_reference=PROJECT,
        campaign_context_reference=CAMPAIGN,
        creative_brief_reference="brief:001",
        instruction_reference=("instruction:001", "APPROVED_INSTRUCTION"),
        current_workflow_state="ASSET_ADMISSION_PENDING",
        requested_next_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        responsible_actor_or_service_reference=("ACTOR", "actor:workflow"),
        event_timestamp=NOW,
        evidence_references=((PROJECT, CAMPAIGN[1], "evidence:001"),),
        reason_codes=("ASSET_ADMISSION_EXECUTED",),
        workflow_contract_reference=("GATE_18_CREATIVE_WORKFLOW", "1.0"),
        canonical_input_fingerprint="1" * 64,
        creative_result_candidate_reference=(
            PROJECT,
            CAMPAIGN[1],
            "candidate:001",
        ),
        accepted_operator_decision_reference=(
            PROJECT,
            CAMPAIGN[1],
            "operator-decision:001",
        ),
        accepted_governed_asset_reference=ASSET,
    )


def _record():
    evaluation = _evaluation()
    consumption_id = (
        derive_generated_candidate_asset_admission_workflow_transition_consumption_id(
            asset_admission_execution_id="a" * 64,
            admitted_asset_reference=ASSET[2],
            accepted_governed_asset_reference=ASSET,
            requested_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
            workflow_transition_evaluation=evaluation,
            consumption_actor_reference="actor:consumer",
            consumption_timestamp=NOW,
        )
    )
    evaluation_sha = derive_workflow_transition_evaluation_sha256(evaluation)
    provenance = (
        f"asset_admission_execution_sha256:{'a' * 64}",
        f"admitted_asset_reference:{ASSET[2]}",
        f"workflow_transition_evaluation_sha256:{evaluation_sha}",
        "requested_workflow_state:GOVERNED_ASSET_REFERENCE_RECORDED",
        f"consumption_sha256:{consumption_id}",
    )
    return GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
        consumption_id=consumption_id,
        asset_admission_execution_id="a" * 64,
        admitted_asset_reference=ASSET[2],
        accepted_governed_asset_reference=ASSET,
        requested_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        workflow_transition_evaluation=evaluation,
        consumption_actor_reference="actor:consumer",
        consumption_timestamp=NOW,
        deterministic_provenance=provenance,
    )


def test_valid_consumption_record_is_immutable_and_binds_exact_evaluation():
    record = _record()

    assert record.workflow_transition_evaluation.disposition == (
        TRANSITION_DISPOSITION_ACCEPTED
    )
    assert record.accepted_governed_asset_reference == ASSET
    assert record.workflow_transition_evaluation.requested_workflow_state == (
        "GOVERNED_ASSET_REFERENCE_RECORDED"
    )

    with pytest.raises(FrozenInstanceError):
        record.consumption_id = "b" * 64


def test_consumption_identity_is_deterministic():
    first = _record()
    second = _record()

    assert first.consumption_id == second.consumption_id
    assert first.deterministic_provenance == second.deterministic_provenance


def test_record_rejects_bound_reference_identity_mismatch():
    record = _record()

    with pytest.raises(ValueError, match="identity must match"):
        GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
            consumption_id=record.consumption_id,
            asset_admission_execution_id=record.asset_admission_execution_id,
            admitted_asset_reference=record.admitted_asset_reference,
            accepted_governed_asset_reference=(
                PROJECT,
                CAMPAIGN[1],
                "asset:other",
            ),
            requested_workflow_state=record.requested_workflow_state,
            workflow_transition_evaluation=record.workflow_transition_evaluation,
            consumption_actor_reference=record.consumption_actor_reference,
            consumption_timestamp=record.consumption_timestamp,
            deterministic_provenance=record.deterministic_provenance,
        )


def test_record_rejects_naive_consumption_timestamp():
    record = _record()

    with pytest.raises(ValueError, match="timezone-aware"):
        GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
            consumption_id=record.consumption_id,
            asset_admission_execution_id=record.asset_admission_execution_id,
            admitted_asset_reference=record.admitted_asset_reference,
            accepted_governed_asset_reference=record.accepted_governed_asset_reference,
            requested_workflow_state=record.requested_workflow_state,
            workflow_transition_evaluation=record.workflow_transition_evaluation,
            consumption_actor_reference=record.consumption_actor_reference,
            consumption_timestamp=NOW.replace(tzinfo=None),
            deterministic_provenance=record.deterministic_provenance,
        )


def test_record_rejects_wrong_evaluation_type():
    record = _record()

    with pytest.raises(ValueError, match="exact GovernedCreativeWorkflow"):
        GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
            consumption_id=record.consumption_id,
            asset_admission_execution_id=record.asset_admission_execution_id,
            admitted_asset_reference=record.admitted_asset_reference,
            accepted_governed_asset_reference=record.accepted_governed_asset_reference,
            requested_workflow_state=record.requested_workflow_state,
            workflow_transition_evaluation=object(),
            consumption_actor_reference=record.consumption_actor_reference,
            consumption_timestamp=record.consumption_timestamp,
            deterministic_provenance=record.deterministic_provenance,
        )


def test_record_rejects_tampered_provenance():
    record = _record()

    with pytest.raises(ValueError, match="exact consumption lineage"):
        GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption(
            consumption_id=record.consumption_id,
            asset_admission_execution_id=record.asset_admission_execution_id,
            admitted_asset_reference=record.admitted_asset_reference,
            accepted_governed_asset_reference=record.accepted_governed_asset_reference,
            requested_workflow_state=record.requested_workflow_state,
            workflow_transition_evaluation=record.workflow_transition_evaluation,
            consumption_actor_reference=record.consumption_actor_reference,
            consumption_timestamp=record.consumption_timestamp,
            deterministic_provenance=("tampered",),
        )
