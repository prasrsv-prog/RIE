import pytest

from rie.application.rcis_intelligence_reference_grounded_visual_generation import (
    RCISIntelligenceReferenceGroundedVisualGenerationResult,
)
from rie.application.rcis_intelligence_reference_grounded_visual_result_validation import (
    RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_RESULT_VALIDATION_CONTRACT_VERSION,
    RCISIntelligenceReferenceGroundedVisualResultValidationDecision,
    RCISIntelligenceReferenceGroundedVisualResultValidationRequest,
    RCISIntelligenceReferenceGroundedVisualResultValidator,
)


def _generation_result(**overrides):
    values = dict(
        contract_version="1.0.0",
        request=object(),
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
        product_identity_locked=True,
        facts_claims_authoritative_only=True,
        product_visual_grounding_established=True,
        reference_grounding_established=True,
        automatic_provider_model_selection_performed=False,
        foundation_model_knowledge_fallback_performed=False,
        retry_loop_performed=False,
        multi_cycle_autonomy_performed=False,
    )
    values.update(overrides)

    result = object.__new__(RCISIntelligenceReferenceGroundedVisualGenerationResult)
    for name, value in values.items():
        object.__setattr__(result, name, value)
    return result


def _request(result=None, validation_request=None):
    return RCISIntelligenceReferenceGroundedVisualResultValidationRequest(
        visual_generation_result=result if result is not None else _generation_result(),
        validation_request_artifact=(
            validation_request if validation_request is not None else object()
        ),
    )


def _decision(*, accepted=True, validation_artifact=None):
    return RCISIntelligenceReferenceGroundedVisualResultValidationDecision(
        accepted=accepted,
        validation_artifact=(
            validation_artifact if validation_artifact is not None else object()
        ),
    )


def test_contract_version_is_1_0_0():
    assert (
        RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_RESULT_VALIDATION_CONTRACT_VERSION
        == "1.0.0"
    )


def test_request_preserves_exact_generation_result_and_validation_request():
    generation_result = _generation_result()
    validation_request = object()

    request = _request(
        result=generation_result,
        validation_request=validation_request,
    )

    assert request.visual_generation_result is generation_result
    assert request.validation_request_artifact is validation_request


def test_validate_preserves_exact_grounding_and_validation_artifact_identity():
    generation_result = _generation_result()
    validation_request = object()
    validation_artifact = object()
    request = _request(
        result=generation_result,
        validation_request=validation_request,
    )
    seen = []

    def validator(received):
        seen.append(received)
        return _decision(
            accepted=True,
            validation_artifact=validation_artifact,
        )

    result = RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
        request=request,
        validator=validator,
    )

    assert seen == [request]
    assert result.request is request
    assert result.visual_generation_result is generation_result
    assert result.grounded_creative_context is generation_result.grounded_creative_context
    assert result.creative_intent is generation_result.creative_intent
    assert (
        result.reference_role_understanding
        is generation_result.reference_role_understanding
    )
    assert result.locked_product_id == generation_result.locked_product_id
    assert result.locked_variant_id == generation_result.locked_variant_id
    assert (
        result.authoritative_product_knowledge_artifact
        is generation_result.authoritative_product_knowledge_artifact
    )
    assert result.brand_context_artifact is generation_result.brand_context_artifact
    assert (
        result.grounding_provenance_artifact
        is generation_result.grounding_provenance_artifact
    )
    assert (
        result.visual_generation_request_artifact
        is generation_result.visual_generation_request_artifact
    )
    assert (
        result.visual_generation_response_artifact
        is generation_result.visual_generation_response_artifact
    )
    assert result.validation_request_artifact is validation_request
    assert result.validation_artifact is validation_artifact


def test_validate_preserves_exact_product_and_variant_identity_without_inference():
    generation_result = _generation_result(
        locked_product_id="product-exact",
        locked_variant_id=None,
    )

    result = RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
        request=_request(result=generation_result),
        validator=lambda received: _decision(),
    )

    assert result.locked_product_id == "product-exact"
    assert result.locked_variant_id is None


def test_rejected_decision_is_returned_without_regeneration_or_retry():
    result = RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
        request=_request(),
        validator=lambda received: _decision(accepted=False),
    )

    assert result.accepted is False
    assert result.visual_result_validation_performed is True
    assert result.automatic_regeneration_performed is False
    assert result.automatic_provider_model_selection_performed is False
    assert result.foundation_model_knowledge_fallback_performed is False
    assert result.retry_loop_performed is False
    assert result.multi_cycle_autonomy_performed is False


def test_accepted_decision_preserves_grounding_flags():
    result = RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
        request=_request(),
        validator=lambda received: _decision(accepted=True),
    )

    assert result.accepted is True
    assert result.product_identity_locked is True
    assert result.facts_claims_authoritative_only is True
    assert result.product_visual_grounding_established is True
    assert result.reference_grounding_established is True


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("product_identity_locked", False, "product identity lock"),
        (
            "facts_claims_authoritative_only",
            False,
            "authoritative-only facts/claims",
        ),
        (
            "product_visual_grounding_established",
            False,
            "product visual grounding",
        ),
        ("reference_grounding_established", False, "reference grounding"),
        (
            "reference_role_understanding",
            None,
            "reference_role_understanding",
        ),
        (
            "visual_generation_response_artifact",
            None,
            "visual_generation_response_artifact",
        ),
    ],
)
def test_validate_requires_published_generation_grounding_invariants(
    field,
    value,
    message,
):
    generation_result = _generation_result(**{field: value})

    with pytest.raises(ValueError, match=message):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=_request(result=generation_result),
            validator=lambda received: _decision(),
        )


def test_validate_requires_validation_request_artifact():
    request = RCISIntelligenceReferenceGroundedVisualResultValidationRequest(
        visual_generation_result=_generation_result(),
        validation_request_artifact=None,
    )

    with pytest.raises(ValueError, match="validation_request_artifact"):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=request,
            validator=lambda received: _decision(),
        )


def test_validate_requires_callable_validator():
    with pytest.raises(ValueError, match="validator must be callable"):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=_request(),
            validator=None,
        )


def test_validate_requires_exact_decision_type():
    with pytest.raises(
        TypeError,
        match="RCISIntelligenceReferenceGroundedVisualResultValidationDecision",
    ):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=_request(),
            validator=lambda received: object(),
        )


def test_validate_requires_boolean_accepted():
    decision = RCISIntelligenceReferenceGroundedVisualResultValidationDecision(
        accepted="yes",
        validation_artifact=object(),
    )

    with pytest.raises(TypeError, match="accepted must be bool"):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=_request(),
            validator=lambda received: decision,
        )


def test_validate_requires_validation_artifact():
    decision = RCISIntelligenceReferenceGroundedVisualResultValidationDecision(
        accepted=True,
        validation_artifact=None,
    )

    with pytest.raises(ValueError, match="validation_artifact"):
        RCISIntelligenceReferenceGroundedVisualResultValidator().validate(
            request=_request(),
            validator=lambda received: decision,
        )
