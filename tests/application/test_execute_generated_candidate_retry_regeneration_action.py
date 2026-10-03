from dataclasses import replace
from datetime import datetime, timezone

import pytest

from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderExecutionResponse,
    ResolvedVisualReference,
    VisualGenerationExecutionConfig,
)
from rie.application.execute_generated_candidate_retry_regeneration_action import (
    execute_generated_candidate_retry_regeneration_action,
)
from rie.application.visual_generation_provider import VisualGenerationRequest
from rie.domain.generated_candidate_decision_action_authorization import (
    GeneratedCandidateDecisionActionAuthorization,
)


TIMESTAMP = datetime(2026, 10, 3, 13, 0, tzinfo=timezone.utc)


class Resolver:
    def __init__(self):
        self.calls = []

    def resolve(self, asset_id):
        self.calls.append(asset_id)
        return ResolvedVisualReference(
            requested_asset_id=asset_id,
            resolved_asset_id=asset_id,
            provider_media_ref=f"media:{asset_id}",
            use_eligible=True,
        )


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
        "requested_action": "RETRY_REGENERATION",
        "authorization_outcome": "AUTHORIZED",
        "authorization_reason_evidence_reference": "evidence:retry:1",
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


def make_request():
    return VisualGenerationRequest(
        grounded_prompt="retry grounded prompt",
        selected_reference_asset_ids=("asset:1", "asset:2"),
    )


def make_config():
    return VisualGenerationExecutionConfig(
        provider_id="explicit-provider",
        model_id="explicit-model",
    )


def make_transport(calls, *, diagnostic="completed"):
    def transport(payload):
        calls.append(payload)
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=("provider-output:retry:1",),
            provider_execution_ref="execution:retry:1",
            diagnostic_message=diagnostic,
        )
    return transport


def execute(*, authorization=None, request=None, config=None, resolver=None, transport=None):
    calls = []
    resolver = Resolver() if resolver is None else resolver
    transport = make_transport(calls) if transport is None else transport
    result = execute_generated_candidate_retry_regeneration_action(
        make_authorization() if authorization is None else authorization,
        retry_request=make_request() if request is None else request,
        execution_config=make_config() if config is None else config,
        reference_resolver=resolver,
        transport=transport,
        execution_actor_reference="actor:service:retry",
        execution_timestamp=TIMESTAMP,
    )
    return result, resolver, calls


def test_authorized_retry_executes_exactly_one_provider_attempt_and_binds_lineage():
    result, resolver, calls = execute()

    assert resolver.calls == ["asset:1", "asset:2"]
    assert len(calls) == 1
    assert calls[0] == {
        "provider_id": "explicit-provider",
        "model_id": "explicit-model",
        "grounded_prompt": "retry grounded prompt",
        "reference_media_refs": ("media:asset:1", "media:asset:2"),
    }
    assert result.authorization_id == "a" * 64
    assert result.candidate_id == "candidate:1"
    assert result.requested_action == "RETRY_REGENERATION"
    assert result.authorization_outcome == "AUTHORIZED"
    assert result.provider_output_refs == ("provider-output:retry:1",)
    assert result.selected_reference_asset_ids == ("asset:1", "asset:2")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("requested_action", "AUTONOMOUS_ITERATION", "requested_action"),
        ("authorization_outcome", "DENIED", "outcome"),
    ),
)
def test_wrong_authorization_surface_fails_before_provider(field, value, message):
    calls = []
    resolver = Resolver()
    authorization = make_authorization(**{field: value})
    with pytest.raises(ValueError, match=message):
        execute_generated_candidate_retry_regeneration_action(
            authorization,
            retry_request=make_request(),
            execution_config=make_config(),
            reference_resolver=resolver,
            transport=make_transport(calls),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert calls == []
    assert resolver.calls == []


def test_tampered_authorization_provenance_fails_before_provider():
    calls = []
    resolver = Resolver()
    authorization = replace(
        make_authorization(),
        deterministic_provenance=("tampered",),
    )
    with pytest.raises(ValueError, match="provenance"):
        execute_generated_candidate_retry_regeneration_action(
            authorization,
            retry_request=make_request(),
            execution_config=make_config(),
            reference_resolver=resolver,
            transport=make_transport(calls),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert calls == []
    assert resolver.calls == []


def test_retry_request_must_be_exact_visual_generation_request():
    calls = []
    resolver = Resolver()
    with pytest.raises(ValueError, match="VisualGenerationRequest"):
        execute_generated_candidate_retry_regeneration_action(
            make_authorization(),
            retry_request=object(),
            execution_config=make_config(),
            reference_resolver=resolver,
            transport=make_transport(calls),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert calls == []


def test_execution_config_must_be_exact_visual_generation_execution_config():
    calls = []
    resolver = Resolver()
    with pytest.raises(ValueError, match="VisualGenerationExecutionConfig"):
        execute_generated_candidate_retry_regeneration_action(
            make_authorization(),
            retry_request=make_request(),
            execution_config=object(),
            reference_resolver=resolver,
            transport=make_transport(calls),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert calls == []


def test_reference_resolution_failure_fails_closed_before_transport():
    class FailingResolver:
        def resolve(self, asset_id):
            raise ValueError("reference unavailable")

    calls = []
    with pytest.raises(ValueError, match="reference unavailable"):
        execute_generated_candidate_retry_regeneration_action(
            make_authorization(),
            retry_request=make_request(),
            execution_config=make_config(),
            reference_resolver=FailingResolver(),
            transport=make_transport(calls),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert calls == []


def test_transport_failure_is_not_retried_or_fallbacked():
    calls = []

    def failing_transport(payload):
        calls.append(payload)
        raise RuntimeError("provider failed")

    with pytest.raises(RuntimeError, match="provider failed"):
        execute_generated_candidate_retry_regeneration_action(
            make_authorization(),
            retry_request=make_request(),
            execution_config=make_config(),
            reference_resolver=Resolver(),
            transport=failing_transport,
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert len(calls) == 1


def test_secret_material_in_provider_audit_is_rejected_after_single_attempt():
    calls = []
    with pytest.raises(ValueError, match="secret material"):
        execute_generated_candidate_retry_regeneration_action(
            make_authorization(),
            retry_request=make_request(),
            execution_config=make_config(),
            reference_resolver=Resolver(),
            transport=make_transport(calls, diagnostic="authorization: hidden"),
            execution_actor_reference="actor:service:retry",
            execution_timestamp=TIMESTAMP,
        )
    assert len(calls) == 1


def test_identical_exact_evidence_produces_deterministic_execution_identity():
    first, _, _ = execute()
    second, _, _ = execute()
    assert (
        first.retry_regeneration_action_execution_id
        == second.retry_regeneration_action_execution_id
    )
    assert first.deterministic_provenance == second.deterministic_provenance


def test_execution_does_not_mutate_authorization():
    authorization = make_authorization()
    before = authorization
    execute(authorization=authorization)
    assert authorization == before


def test_provider_output_remains_execution_evidence_not_candidate_ingestion():
    result, _, _ = execute()
    assert result.provider_output_refs == ("provider-output:retry:1",)
    assert not hasattr(result, "creative_result_candidate_id")
    assert not hasattr(result, "authority_state")
