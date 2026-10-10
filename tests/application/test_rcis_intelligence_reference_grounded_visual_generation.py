import pytest

from rie.application.rcis_intelligence_brand_product_grounded_creative_context import (
    RCISIntelligenceBrandProductGroundedCreativeContext,
)
from rie.application.rcis_intelligence_reference_grounded_visual_generation import (
    RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_GENERATION_CONTRACT_VERSION,
    RCISIntelligenceReferenceGroundedVisualGenerationExecutor,
    RCISIntelligenceReferenceGroundedVisualGenerationRequest,
)


def _context(**overrides):
    values = dict(
        contract_version="1.0.0",
        request=object(),
        creative_intent=object(),
        locked_product_id="product-1",
        locked_variant_id="variant-1",
        authoritative_product_knowledge_artifact=object(),
        brand_context_artifact=object(),
        grounding_provenance_artifact=object(),
        reference_role_understanding=object(),
        brand_guidance_mode="BALANCED",
        creative_freedom="BALANCED",
        product_identity_locked=True,
        facts_claims_authoritative_only=True,
        product_visual_grounding_established=True,
        brand_context_grounded=True,
        image_analysis_performed=False,
        downstream_visual_generation_performed=False,
    )
    values.update(overrides)

    context = object.__new__(RCISIntelligenceBrandProductGroundedCreativeContext)
    for name, value in values.items():
        object.__setattr__(context, name, value)
    return context


def _request(context=None, visual_request=None):
    return RCISIntelligenceReferenceGroundedVisualGenerationRequest(
        grounded_creative_context=context if context is not None else _context(),
        visual_generation_request_artifact=(
            visual_request if visual_request is not None else object()
        ),
    )


def test_contract_version_is_1_0_0():
    assert (
        RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_GENERATION_CONTRACT_VERSION
        == "1.0.0"
    )


def test_request_preserves_exact_context_and_visual_request_identity():
    context = _context()
    visual_request = object()

    request = _request(context=context, visual_request=visual_request)

    assert request.grounded_creative_context is context
    assert request.visual_generation_request_artifact is visual_request


def test_execute_preserves_governed_context_identity_and_response_identity():
    context = _context()
    visual_request = object()
    response = object()
    request = _request(context=context, visual_request=visual_request)

    seen = []

    def executor(received):
        seen.append(received)
        return response

    result = RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
        request=request,
        executor=executor,
    )

    assert seen == [request]
    assert result.request is request
    assert result.grounded_creative_context is context
    assert result.creative_intent is context.creative_intent
    assert result.reference_role_understanding is context.reference_role_understanding
    assert result.authoritative_product_knowledge_artifact is (
        context.authoritative_product_knowledge_artifact
    )
    assert result.brand_context_artifact is context.brand_context_artifact
    assert result.grounding_provenance_artifact is context.grounding_provenance_artifact
    assert result.visual_generation_request_artifact is visual_request
    assert result.visual_generation_response_artifact is response


def test_execute_preserves_exact_product_and_variant_identity():
    context = _context(
        locked_product_id="product-exact",
        locked_variant_id="variant-exact",
    )
    request = _request(context=context)

    result = RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
        request=request,
        executor=lambda received: object(),
    )

    assert result.locked_product_id == "product-exact"
    assert result.locked_variant_id == "variant-exact"


def test_execute_does_not_infer_missing_variant_identity():
    context = _context(locked_variant_id=None)
    request = _request(context=context)

    result = RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
        request=request,
        executor=lambda received: object(),
    )

    assert result.locked_variant_id is None


def test_execute_marks_only_reference_grounding_and_not_broader_automation():
    result = RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
        request=_request(),
        executor=lambda received: object(),
    )

    assert result.product_identity_locked is True
    assert result.facts_claims_authoritative_only is True
    assert result.product_visual_grounding_established is True
    assert result.reference_grounding_established is True
    assert result.automatic_provider_model_selection_performed is False
    assert result.foundation_model_knowledge_fallback_performed is False
    assert result.retry_loop_performed is False
    assert result.multi_cycle_autonomy_performed is False


def test_execute_requires_reference_role_understanding():
    context = _context(reference_role_understanding=None)

    with pytest.raises(
        ValueError,
        match="reference_role_understanding is required",
    ):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(context=context),
            executor=lambda received: object(),
        )


def test_execute_requires_product_identity_lock():
    context = _context(product_identity_locked=False)

    with pytest.raises(ValueError, match="product identity lock"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(context=context),
            executor=lambda received: object(),
        )


def test_execute_requires_authoritative_only_facts_and_claims():
    context = _context(facts_claims_authoritative_only=False)

    with pytest.raises(ValueError, match="authoritative-only facts/claims"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(context=context),
            executor=lambda received: object(),
        )


def test_execute_requires_product_visual_grounding():
    context = _context(product_visual_grounding_established=False)

    with pytest.raises(ValueError, match="product visual grounding"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(context=context),
            executor=lambda received: object(),
        )


def test_execute_requires_visual_generation_request_artifact():
    request = RCISIntelligenceReferenceGroundedVisualGenerationRequest(
        grounded_creative_context=_context(),
        visual_generation_request_artifact=None,
    )

    with pytest.raises(ValueError, match="visual_generation_request_artifact"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=request,
            executor=lambda received: object(),
        )


def test_execute_requires_callable_executor():
    with pytest.raises(ValueError, match="executor must be callable"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(),
            executor=None,
        )


def test_execute_rejects_none_executor_response():
    with pytest.raises(ValueError, match="returned no visual generation response artifact"):
        RCISIntelligenceReferenceGroundedVisualGenerationExecutor().execute(
            request=_request(),
            executor=lambda received: None,
        )
