from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from rie.domain.generated_candidate_retry_regeneration_action_execution import (
    GeneratedCandidateRetryRegenerationActionExecution,
    derive_generated_candidate_retry_regeneration_action_execution_id,
    derive_provider_local_result_sha256,
    derive_retry_generation_request_sha256,
)


TIMESTAMP = datetime(2026, 10, 3, 13, 0, tzinfo=timezone.utc)


def make_execution(**overrides):
    request_sha = derive_retry_generation_request_sha256(
        grounded_prompt="retry prompt",
        selected_reference_asset_ids=("asset:1",),
    )
    result_sha = derive_provider_local_result_sha256(
        provider_output_refs=("output:1",),
        provider_audit_message=(
            "provider=provider-1;model=model-1;status=SUCCEEDED;"
            "execution_ref=exec-1;diagnostic=completed"
        ),
    )
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
        "requested_action": "RETRY_REGENERATION",
        "authorization_outcome": "AUTHORIZED",
        "retry_generation_request_sha256": request_sha,
        "selected_reference_asset_ids": ("asset:1",),
        "provider_id": "provider-1",
        "model_id": "model-1",
        "provider_output_refs": ("output:1",),
        "provider_audit_message": (
            "provider=provider-1;model=model-1;status=SUCCEEDED;"
            "execution_ref=exec-1;diagnostic=completed"
        ),
        "execution_actor_reference": "actor:service:1",
        "execution_timestamp": TIMESTAMP,
    }
    values.update(overrides)
    result_sha = derive_provider_local_result_sha256(
        provider_output_refs=values["provider_output_refs"],
        provider_audit_message=values["provider_audit_message"],
    )
    execution_id = derive_generated_candidate_retry_regeneration_action_execution_id(
        authorization_id=values["authorization_id"],
        decision_id=values["decision_id"],
        evaluation_id=values["evaluation_id"],
        candidate_id=values["candidate_id"],
        candidate_checksum=values["candidate_checksum"],
        retry_generation_request_sha256=values["retry_generation_request_sha256"],
        selected_reference_asset_ids=values["selected_reference_asset_ids"],
        provider_id=values["provider_id"],
        model_id=values["model_id"],
        provider_local_result_sha256=result_sha,
        execution_actor_reference=values["execution_actor_reference"],
        execution_timestamp=values["execution_timestamp"],
    )
    values["retry_regeneration_action_execution_id"] = execution_id
    values["deterministic_provenance"] = (
        f"authorization_sha256:{values['authorization_id']}",
        f"decision_id:{values['decision_id']}",
        f"candidate_sha256:{values['candidate_checksum']}",
        "requested_action:RETRY_REGENERATION",
        (
            "retry_generation_request_sha256:"
            f"{values['retry_generation_request_sha256']}"
        ),
        f"provider:{values['provider_id']}",
        f"model:{values['model_id']}",
        f"provider_local_result_sha256:{result_sha}",
        f"retry_regeneration_action_execution_sha256:{execution_id}",
    )
    return GeneratedCandidateRetryRegenerationActionExecution(**values)


def test_execution_record_is_frozen_and_has_exact_fields():
    assert [field.name for field in fields(
        GeneratedCandidateRetryRegenerationActionExecution
    )] == [
        "retry_regeneration_action_execution_id",
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
        "retry_generation_request_sha256",
        "selected_reference_asset_ids",
        "provider_id",
        "model_id",
        "provider_output_refs",
        "provider_audit_message",
        "execution_actor_reference",
        "execution_timestamp",
        "deterministic_provenance",
    ]
    value = make_execution()
    with pytest.raises(FrozenInstanceError):
        value.authorization_id = "c" * 64


def test_retry_request_fingerprint_is_deterministic():
    first = derive_retry_generation_request_sha256(
        grounded_prompt="retry prompt",
        selected_reference_asset_ids=("asset:1", "asset:2"),
    )
    second = derive_retry_generation_request_sha256(
        grounded_prompt="retry prompt",
        selected_reference_asset_ids=("asset:1", "asset:2"),
    )
    assert first == second
    assert len(first) == 64


def test_provider_local_result_fingerprint_is_deterministic():
    first = derive_provider_local_result_sha256(
        provider_output_refs=("output:1",),
        provider_audit_message="provider=x;model=y;status=SUCCEEDED",
    )
    second = derive_provider_local_result_sha256(
        provider_output_refs=("output:1",),
        provider_audit_message="provider=x;model=y;status=SUCCEEDED",
    )
    assert first == second
    assert len(first) == 64


def test_execution_identity_is_deterministic_for_identical_exact_evidence():
    assert (
        make_execution().retry_regeneration_action_execution_id
        == make_execution().retry_regeneration_action_execution_id
    )


def test_execution_rejects_wrong_action_or_outcome():
    with pytest.raises(ValueError, match="requested_action"):
        make_execution(requested_action="AUTONOMOUS_ITERATION")
    with pytest.raises(ValueError, match="authorization_outcome"):
        make_execution(authorization_outcome="DENIED")


def test_execution_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        make_execution(execution_timestamp=datetime(2026, 10, 3, 13, 0))


def test_provider_audit_rejects_secret_markers():
    with pytest.raises(ValueError, match="secret material"):
        derive_provider_local_result_sha256(
            provider_output_refs=("output:1",),
            provider_audit_message="authorization: Bearer hidden",
        )


def test_execution_rejects_tampered_provenance():
    value = make_execution()
    with pytest.raises(ValueError, match="deterministic_provenance mismatch"):
        GeneratedCandidateRetryRegenerationActionExecution(
            **{
                **value.__dict__,
                "deterministic_provenance": ("tampered",),
            }
        )
