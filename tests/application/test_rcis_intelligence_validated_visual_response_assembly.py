import pytest

from rie.application.rcis_intelligence_reference_grounded_visual_result_validation import (
    RCISIntelligenceReferenceGroundedVisualResultValidationResult,
)
from rie.application.rcis_intelligence_validated_visual_response_assembly import (
    RCIS_INTELLIGENCE_VALIDATED_VISUAL_RESPONSE_ASSEMBLY_CONTRACT_VERSION,
    RCISIntelligenceValidatedVisualResponseAssembler,
    RCISIntelligenceValidatedVisualResponseAssemblyDecision,
    RCISIntelligenceValidatedVisualResponseAssemblyRequest,
)


def _validation_result(**overrides):
    values = dict(
        contract_version="1.0.0",
        request=object(),
        visual_generation_result=object(),
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
        validation_request_artifact=object(),
        validation_decision=object(),
        validation_artifact=object(),
        accepted=True,
        product_identity_locked=True,
        facts_claims_authoritative_only=True,
        product_visual_grounding_established=True,
        reference_grounding_established=True,
        visual_result_validation_performed=True,
        automatic_regeneration_performed=False,
        automatic_provider_model_selection_performed=False,
        foundation_model_knowledge_fallback_performed=False,
        retry_loop_performed=False,
        multi_cycle_autonomy_performed=False,
    )
    values.update(overrides)

    result = object.__new__(
        RCISIntelligenceReferenceGroundedVisualResultValidationResult
    )
    for name, value in values.items():
        object.__setattr__(result, name, value)
    return result


def _request(result=None, assembly_request=None):
    return RCISIntelligenceValidatedVisualResponseAssemblyRequest(
        validated_visual_result=result if result is not None else _validation_result(),
        response_assembly_request_artifact=(
            assembly_request if assembly_request is not None else object()
        ),
    )


def _decision(*, response_artifact=None, visual_delivery_artifact=None):
    return RCISIntelligenceValidatedVisualResponseAssemblyDecision(
        response_artifact=(
            response_artifact if response_artifact is not None else object()
        ),
        visual_delivery_artifact=visual_delivery_artifact,
    )


def test_contract_version_is_1_0_0():
    assert (
        RCIS_INTELLIGENCE_VALIDATED_VISUAL_RESPONSE_ASSEMBLY_CONTRACT_VERSION
        == "1.0.0"
    )


def test_request_preserves_exact_validation_result_and_assembly_request():
    validation_result = _validation_result()
    assembly_request = object()

    request = _request(
        result=validation_result,
        assembly_request=assembly_request,
    )

    assert request.validated_visual_result is validation_result
    assert request.response_assembly_request_artifact is assembly_request


def test_accepted_result_preserves_exact_governed_identity_chain():
    validation_result = _validation_result(
        accepted=True,
        locked_product_id="product-exact",
        locked_variant_id=None,
    )
    assembly_request = object()
    response_artifact = object()
    delivery_artifact = object()
    request = _request(
        result=validation_result,
        assembly_request=assembly_request,
    )
    seen = []

    def assembler(received):
        seen.append(received)
        return _decision(
            response_artifact=response_artifact,
            visual_delivery_artifact=delivery_artifact,
        )

    result = RCISIntelligenceValidatedVisualResponseAssembler().assemble(
        request=request,
        assembler=assembler,
    )

    assert seen == [request]
    assert result.request is request
    assert result.validated_visual_result is validation_result
    assert result.visual_generation_result is validation_result.visual_generation_result
    assert result.validation_decision is validation_result.validation_decision
    assert result.validation_artifact is validation_result.validation_artifact
    assert result.grounded_creative_context is validation_result.grounded_creative_context
    assert result.creative_intent is validation_result.creative_intent
    assert (
        result.reference_role_understanding
        is validation_result.reference_role_understanding
    )
    assert result.locked_product_id == "product-exact"
    assert result.locked_variant_id is None
    assert (
        result.authoritative_product_knowledge_artifact
        is validation_result.authoritative_product_knowledge_artifact
    )
    assert result.brand_context_artifact is validation_result.brand_context_artifact
    assert (
        result.grounding_provenance_artifact
        is validation_result.grounding_provenance_artifact
    )
    assert (
        result.visual_generation_request_artifact
        is validation_result.visual_generation_request_artifact
    )
    assert (
        result.visual_generation_response_artifact
        is validation_result.visual_generation_response_artifact
    )
    assert result.response_assembly_request_artifact is assembly_request
    assert result.response_artifact is response_artifact
    assert result.visual_delivery_artifact is delivery_artifact


def test_accepted_result_preserves_grounding_and_bounded_execution_flags():
    result = RCISIntelligenceValidatedVisualResponseAssembler().assemble(
        request=_request(result=_validation_result(accepted=True)),
        assembler=lambda received: _decision(
            visual_delivery_artifact=object(),
        ),
    )

    assert result.accepted is True
    assert result.product_identity_locked is True
    assert result.facts_claims_authoritative_only is True
    assert result.product_visual_grounding_established is True
    assert result.reference_grounding_established is True
    assert result.visual_result_validation_performed is True
    assert result.validated_visual_response_assembly_performed is True
    assert result.rejected_visual_delivery_blocked is False
    assert result.automatic_regeneration_performed is False
    assert result.automatic_provider_model_selection_performed is False
    assert result.tool_provider_invocation_performed is False
    assert result.foundation_model_knowledge_fallback_performed is False
    assert result.retry_loop_performed is False
    assert result.multi_cycle_autonomy_performed is False


def test_rejected_result_allows_response_but_blocks_visual_delivery():
    validation_result = _validation_result(accepted=False)
    response_artifact = object()

    result = RCISIntelligenceValidatedVisualResponseAssembler().assemble(
        request=_request(result=validation_result),
        assembler=lambda received: _decision(
            response_artifact=response_artifact,
            visual_delivery_artifact=None,
        ),
    )

    assert result.accepted is False
    assert result.response_artifact is response_artifact
    assert result.visual_delivery_artifact is None
    assert result.rejected_visual_delivery_blocked is True
    assert result.automatic_regeneration_performed is False
    assert result.retry_loop_performed is False


def test_rejected_result_cannot_expose_visual_delivery_artifact():
    with pytest.raises(ValueError, match="must not expose visual_delivery_artifact"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(result=_validation_result(accepted=False)),
            assembler=lambda received: _decision(
                visual_delivery_artifact=object(),
            ),
        )


def test_accepted_result_requires_visual_delivery_artifact():
    with pytest.raises(ValueError, match="requires visual_delivery_artifact"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(result=_validation_result(accepted=True)),
            assembler=lambda received: _decision(
                visual_delivery_artifact=None,
            ),
        )


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
            "visual_result_validation_performed",
            False,
            "visual result validation",
        ),
        (
            "reference_role_understanding",
            None,
            "reference_role_understanding",
        ),
        (
            "visual_generation_result",
            None,
            "visual_generation_result",
        ),
        (
            "visual_generation_response_artifact",
            None,
            "visual_generation_response_artifact",
        ),
        (
            "validation_decision",
            None,
            "validation_decision",
        ),
        (
            "validation_artifact",
            None,
            "validation_artifact",
        ),
    ],
)
def test_assembly_requires_upstream_validated_visual_invariants(
    field,
    value,
    message,
):
    with pytest.raises(ValueError, match=message):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(result=_validation_result(**{field: value})),
            assembler=lambda received: _decision(
                visual_delivery_artifact=object(),
            ),
        )


def test_assembly_requires_boolean_upstream_accepted():
    with pytest.raises(TypeError, match="accepted must be bool"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(result=_validation_result(accepted="yes")),
            assembler=lambda received: _decision(
                visual_delivery_artifact=object(),
            ),
        )


def test_assembly_requires_response_assembly_request_artifact():
    request = RCISIntelligenceValidatedVisualResponseAssemblyRequest(
        validated_visual_result=_validation_result(),
        response_assembly_request_artifact=None,
    )

    with pytest.raises(ValueError, match="response_assembly_request_artifact"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=request,
            assembler=lambda received: _decision(
                visual_delivery_artifact=object(),
            ),
        )


def test_assembly_requires_callable_assembler():
    with pytest.raises(ValueError, match="assembler must be callable"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(),
            assembler=None,
        )


def test_assembly_requires_exact_decision_type():
    with pytest.raises(
        TypeError,
        match="RCISIntelligenceValidatedVisualResponseAssemblyDecision",
    ):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(),
            assembler=lambda received: object(),
        )


def test_assembly_requires_response_artifact():
    decision = RCISIntelligenceValidatedVisualResponseAssemblyDecision(
        response_artifact=None,
        visual_delivery_artifact=object(),
    )

    with pytest.raises(ValueError, match="response_artifact"):
        RCISIntelligenceValidatedVisualResponseAssembler().assemble(
            request=_request(),
            assembler=lambda received: decision,
        )
