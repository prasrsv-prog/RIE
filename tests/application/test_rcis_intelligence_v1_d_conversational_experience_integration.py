import pytest

from rie.application.rcis_intelligence_validated_visual_response_assembly import (
    RCISIntelligenceValidatedVisualResponseAssemblyResult,
)
from rie.application.rcis_intelligence_v1_d_conversational_experience_integration import (
    RCIS_INTELLIGENCE_V1_D_CONVERSATIONAL_EXPERIENCE_INTEGRATION_CONTRACT_VERSION,
    RCISIntelligenceV1DConversationalExperienceIntegrationDecision,
    RCISIntelligenceV1DConversationalExperienceIntegrationRequest,
    RCISIntelligenceV1DConversationalExperienceIntegrator,
)


def _visual_result(**overrides):
    values = dict(
        contract_version="1.0.0",
        request=object(),
        validated_visual_result=object(),
        visual_generation_result=object(),
        validation_decision=object(),
        validation_artifact=object(),
        grounded_creative_context=object(),
        creative_intent=object(),
        reference_role_understanding=object(),
        locked_product_id="product-1",
        locked_variant_id="variant-1",
        authoritative_product_knowledge_artifact=object(),
        brand_context_artifact=object(),
        grounding_provenance_artifact=object(),
        visual_generation_request_artifact=object(),
        visual_generation_response_artifact=object(),
        response_assembly_request_artifact=object(),
        response_artifact=object(),
        visual_delivery_artifact=object(),
        accepted=True,
        product_identity_locked=True,
        facts_claims_authoritative_only=True,
        product_visual_grounding_established=True,
        reference_grounding_established=True,
        visual_result_validation_performed=True,
        validated_visual_response_assembly_performed=True,
        rejected_visual_delivery_blocked=False,
        automatic_regeneration_performed=False,
        automatic_provider_model_selection_performed=False,
        tool_provider_invocation_performed=False,
        foundation_model_knowledge_fallback_performed=False,
        retry_loop_performed=False,
        multi_cycle_autonomy_performed=False,
    )
    values.update(overrides)

    result = object.__new__(
        RCISIntelligenceValidatedVisualResponseAssemblyResult
    )
    for name, value in values.items():
        object.__setattr__(result, name, value)
    return result


def _text_request():
    return RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="text",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=object(),
        validated_visual_response=None,
    )


def _visual_request(result=None):
    return RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="visual",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=None,
        governed_text_grounding_artifact=None,
        validated_visual_response=result if result is not None else _visual_result(),
    )


def _decision(response=None):
    return RCISIntelligenceV1DConversationalExperienceIntegrationDecision(
        conversation_response_artifact=(
            response if response is not None else object()
        )
    )


def test_contract_version_is_1_0_0():
    assert (
        RCIS_INTELLIGENCE_V1_D_CONVERSATIONAL_EXPERIENCE_INTEGRATION_CONTRACT_VERSION
        == "1.0.0"
    )


def test_text_path_preserves_exact_governed_artifacts_in_one_response():
    request = _text_request()
    response = object()
    seen = []

    result = RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
        request=request,
        assembler=lambda received: (
            seen.append(received) or _decision(response)
        ),
    )

    assert seen == [request]
    assert result.request is request
    assert result.response_kind == "text"
    assert (
        result.conversation_turn_request_artifact
        is request.conversation_turn_request_artifact
    )
    assert (
        result.governed_text_response_artifact
        is request.governed_text_response_artifact
    )
    assert (
        result.governed_text_grounding_artifact
        is request.governed_text_grounding_artifact
    )
    assert result.validated_visual_response is None
    assert result.visual_response_artifact is None
    assert result.visual_delivery_artifact is None
    assert result.conversation_response_artifact is response
    assert result.text_grounding_preserved is True
    assert result.visual_validation_preserved is False


def test_visual_path_preserves_exact_validated_result_and_product_identity():
    visual_result = _visual_result(
        locked_product_id="product-exact",
        locked_variant_id=None,
    )
    request = _visual_request(visual_result)
    response = object()

    result = RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
        request=request,
        assembler=lambda received: _decision(response),
    )

    assert result.response_kind == "visual"
    assert result.validated_visual_response is visual_result
    assert result.visual_response_artifact is visual_result.response_artifact
    assert (
        result.visual_delivery_artifact
        is visual_result.visual_delivery_artifact
    )
    assert result.locked_product_id == "product-exact"
    assert result.locked_variant_id is None
    assert result.conversation_response_artifact is response
    assert result.text_grounding_preserved is False
    assert result.visual_validation_preserved is True
    assert result.product_identity_preserved_without_inference is True


def test_rejected_visual_path_preserves_rejection_without_delivery():
    visual_result = _visual_result(
        accepted=False,
        visual_delivery_artifact=None,
        rejected_visual_delivery_blocked=True,
    )

    result = RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
        request=_visual_request(visual_result),
        assembler=lambda received: _decision(),
    )

    assert result.validated_visual_response is visual_result
    assert result.visual_delivery_artifact is None
    assert result.visual_validation_preserved is True


def test_integration_sets_bounded_execution_flags():
    result = RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
        request=_text_request(),
        assembler=lambda received: _decision(),
    )

    assert result.one_conversational_experience_integration_performed is True
    assert result.explicit_response_kind_preserved is True
    assert result.automatic_modality_inference_performed is False
    assert result.automatic_provider_model_selection_performed is False
    assert result.provider_invocation_performed is False
    assert result.automatic_regeneration_performed is False
    assert result.retry_loop_performed is False
    assert result.multi_cycle_autonomy_performed is False


def test_invalid_response_kind_is_rejected():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="audio",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=object(),
        validated_visual_response=None,
    )

    with pytest.raises(ValueError, match="response_kind"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


def test_text_requires_response_artifact():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="text",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=None,
        governed_text_grounding_artifact=object(),
        validated_visual_response=None,
    )

    with pytest.raises(ValueError, match="governed_text_response_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


def test_text_requires_grounding_artifact():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="text",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=None,
        validated_visual_response=None,
    )

    with pytest.raises(ValueError, match="governed_text_grounding_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


def test_text_must_not_mix_visual_payload():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="text",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=object(),
        validated_visual_response=_visual_result(),
    )

    with pytest.raises(ValueError, match="must not include validated_visual_response"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


def test_visual_must_not_mix_text_payload():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="visual",
        conversation_turn_request_artifact=object(),
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=None,
        validated_visual_response=_visual_result(),
    )

    with pytest.raises(
        ValueError,
        match="must not include governed_text_response_artifact",
    ):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "validated_visual_response_assembly_performed",
            False,
            "assembly must already be performed",
        ),
        (
            "visual_result_validation_performed",
            False,
            "validation must already be performed",
        ),
        (
            "product_identity_locked",
            False,
            "product identity lock",
        ),
        (
            "response_artifact",
            None,
            "response_artifact",
        ),
    ],
)
def test_visual_requires_upstream_governed_invariants(field, value, message):
    with pytest.raises(ValueError, match=message):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_visual_request(_visual_result(**{field: value})),
            assembler=lambda received: _decision(),
        )


def test_visual_requires_boolean_accepted():
    with pytest.raises(TypeError, match="accepted must be bool"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_visual_request(_visual_result(accepted="yes")),
            assembler=lambda received: _decision(),
        )


def test_accepted_visual_requires_delivery_artifact():
    with pytest.raises(ValueError, match="requires visual_delivery_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_visual_request(
                _visual_result(
                    accepted=True,
                    visual_delivery_artifact=None,
                )
            ),
            assembler=lambda received: _decision(),
        )


def test_rejected_visual_cannot_expose_delivery_artifact():
    with pytest.raises(ValueError, match="must not expose visual_delivery_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_visual_request(
                _visual_result(
                    accepted=False,
                    visual_delivery_artifact=object(),
                )
            ),
            assembler=lambda received: _decision(),
        )


def test_conversation_turn_request_artifact_is_required():
    request = RCISIntelligenceV1DConversationalExperienceIntegrationRequest(
        response_kind="text",
        conversation_turn_request_artifact=None,
        governed_text_response_artifact=object(),
        governed_text_grounding_artifact=object(),
        validated_visual_response=None,
    )

    with pytest.raises(ValueError, match="conversation_turn_request_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=request,
            assembler=lambda received: _decision(),
        )


def test_callable_assembler_is_required():
    with pytest.raises(ValueError, match="assembler must be callable"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_text_request(),
            assembler=None,
        )


def test_exact_decision_type_is_required():
    with pytest.raises(
        TypeError,
        match="RCISIntelligenceV1DConversationalExperienceIntegrationDecision",
    ):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_text_request(),
            assembler=lambda received: object(),
        )


def test_conversation_response_artifact_is_required():
    decision = RCISIntelligenceV1DConversationalExperienceIntegrationDecision(
        conversation_response_artifact=None
    )

    with pytest.raises(ValueError, match="conversation_response_artifact"):
        RCISIntelligenceV1DConversationalExperienceIntegrator().integrate(
            request=_text_request(),
            assembler=lambda received: decision,
        )
