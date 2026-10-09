from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_brand_product_grounded_creative_context import (
    RCISIntelligenceBrandProductGroundedCreativeContextBuilder,
    RCISIntelligenceBrandProductGroundedCreativeContextRequest,
)
from rie.application.rcis_intelligence_creative_intent import (
    RCISIntelligenceBrandGuidanceMode,
    RCISIntelligenceCreativeFreedom,
    RCISIntelligenceCreativeIntentBuilder,
    RCISIntelligenceCreativeIntentRequest,
)
from rie.application.rcis_intelligence_product_variant_lock import (
    RCISIntelligenceProductVariantIdentityResolution,
    RCISIntelligenceProductVariantLocker,
    RCISIntelligenceProductVariantLockRequest,
)
from rie.application.rcis_intelligence_reference_image_role import (
    RCISIntelligenceReferenceImageInput,
    RCISIntelligenceReferenceImageRole,
    RCISIntelligenceReferenceImageRoleClassification,
    RCISIntelligenceReferenceImageRoleUnderstander,
    RCISIntelligenceReferenceImageSourceAuthority,
)


def _lock(*, variant_id: str | None = "variant-1"):
    lock_request = RCISIntelligenceProductVariantLockRequest(
        user_utterance="Buat visual produk ini.",
        product_id="product-1",
        variant_id=variant_id,
    )
    resolution = RCISIntelligenceProductVariantIdentityResolution(
        product_id="product-1",
        variant_id=variant_id,
        authoritative_identity_artifact=object(),
    )
    return RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    ).lock(request=lock_request)


def _reference_roles():
    reference = RCISIntelligenceReferenceImageInput(
        reference_id="ref-1",
        source_authority=(
            RCISIntelligenceReferenceImageSourceAuthority.USER_PROVIDED
        ),
        reference_artifact=object(),
    )

    def classifier(actual_reference, *args):
        return RCISIntelligenceReferenceImageRoleClassification(
            reference=actual_reference,
            roles=(
                RCISIntelligenceReferenceImageRole.COMPOSITION_ONLY,
                RCISIntelligenceReferenceImageRole.LIGHTING_ONLY,
            ),
            classifier_artifact=object(),
        )

    return RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=classifier,
    ).understand(
        user_utterance="Gunakan komposisi dan lighting dari referensi.",
        references=(reference,),
    )


def _creative_intent(
    *,
    variant_id: str | None = "variant-1",
    brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
    reference_role_understanding=None,
):
    request = RCISIntelligenceCreativeIntentRequest(
        objective="Buat key visual launch yang premium.",
        user_creative_direction="Gunakan nuansa cyberpunk yang elegan.",
        brand_guidance_mode=brand_guidance_mode,
        creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
        product_variant_lock=_lock(variant_id=variant_id),
        reference_role_understanding=reference_role_understanding,
        ignore_from_reference=("teks promosi referensi",),
    )
    return RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )


def _request(
    *,
    creative_intent=None,
    product_knowledge=None,
    brand_context=None,
    provenance=None,
):
    intent = (
        creative_intent
        if creative_intent is not None
        else _creative_intent()
    )
    if product_knowledge is None:
        product_knowledge = object()
    if provenance is None:
        provenance = object()
    if (
        brand_context is None
        and intent.brand_guidance_mode
        is not RCISIntelligenceBrandGuidanceMode.FREE
    ):
        brand_context = object()

    return RCISIntelligenceBrandProductGroundedCreativeContextRequest(
        creative_intent=intent,
        authoritative_product_knowledge_artifact=product_knowledge,
        grounding_provenance_artifact=provenance,
        brand_context_artifact=brand_context,
    )


def test_builder_preserves_exact_locked_product_and_variant() -> None:
    intent = _creative_intent()
    request = _request(creative_intent=intent)

    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=request,
    )

    assert result.request is request
    assert result.creative_intent is intent
    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id == "variant-1"
    assert result.product_identity_locked is True


def test_product_only_lock_remains_without_variant_inference() -> None:
    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(
            creative_intent=_creative_intent(variant_id=None),
        ),
    )

    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id is None


def test_grounding_artifact_identities_are_preserved() -> None:
    product_knowledge = object()
    brand_context = object()
    provenance = object()
    request = _request(
        product_knowledge=product_knowledge,
        brand_context=brand_context,
        provenance=provenance,
    )

    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=request,
    )

    assert (
        result.authoritative_product_knowledge_artifact
        is product_knowledge
    )
    assert result.brand_context_artifact is brand_context
    assert result.grounding_provenance_artifact is provenance


def test_reference_role_understanding_identity_is_preserved() -> None:
    roles = _reference_roles()
    intent = _creative_intent(
        reference_role_understanding=roles,
    )

    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(creative_intent=intent),
    )

    assert result.reference_role_understanding is roles


@pytest.mark.parametrize(
    "mode",
    [
        RCISIntelligenceBrandGuidanceMode.STRICT,
        RCISIntelligenceBrandGuidanceMode.BALANCED,
        RCISIntelligenceBrandGuidanceMode.EXPLORATORY,
    ],
)
def test_non_free_brand_guidance_requires_brand_context(mode) -> None:
    intent = _creative_intent(brand_guidance_mode=mode)

    with pytest.raises(
        ValueError,
        match="brand_context_artifact is required",
    ):
        RCISIntelligenceBrandProductGroundedCreativeContextRequest(
            creative_intent=intent,
            authoritative_product_knowledge_artifact=object(),
            grounding_provenance_artifact=object(),
            brand_context_artifact=None,
        )


def test_free_brand_guidance_allows_no_brand_context() -> None:
    intent = _creative_intent(
        brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.FREE,
    )
    request = _request(
        creative_intent=intent,
        brand_context=None,
    )

    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=request,
    )

    assert result.brand_guidance_mode is RCISIntelligenceBrandGuidanceMode.FREE
    assert result.brand_context_artifact is None
    assert result.brand_context_grounded is False


def test_non_free_brand_context_is_grounded() -> None:
    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(),
    )
    assert result.brand_context_grounded is True


def test_product_visual_grounding_is_established() -> None:
    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(),
    )

    assert result.product_visual_grounding_established is True
    assert result.facts_claims_authoritative_only is True


def test_builder_does_not_analyze_images_or_generate_visuals() -> None:
    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(),
    )

    assert result.image_analysis_performed is False
    assert result.downstream_visual_generation_performed is False


def test_request_is_immutable() -> None:
    request = _request()

    with pytest.raises(FrozenInstanceError):
        request.brand_context_artifact = object()  # type: ignore[misc]


def test_result_is_immutable() -> None:
    result = RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
        request=_request(),
    )

    with pytest.raises(FrozenInstanceError):
        result.locked_product_id = "changed"  # type: ignore[misc]


def test_authoritative_product_knowledge_is_required() -> None:
    intent = _creative_intent()

    with pytest.raises(
        ValueError,
        match="authoritative_product_knowledge_artifact must not be None",
    ):
        RCISIntelligenceBrandProductGroundedCreativeContextRequest(
            creative_intent=intent,
            authoritative_product_knowledge_artifact=None,
            grounding_provenance_artifact=object(),
            brand_context_artifact=object(),
        )


def test_grounding_provenance_is_required() -> None:
    intent = _creative_intent()

    with pytest.raises(
        ValueError,
        match="grounding_provenance_artifact must not be None",
    ):
        RCISIntelligenceBrandProductGroundedCreativeContextRequest(
            creative_intent=intent,
            authoritative_product_knowledge_artifact=object(),
            grounding_provenance_artifact=None,
            brand_context_artifact=object(),
        )


def test_invalid_creative_intent_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="creative_intent must be"):
        RCISIntelligenceBrandProductGroundedCreativeContextRequest(
            creative_intent=object(),  # type: ignore[arg-type]
            authoritative_product_knowledge_artifact=object(),
            grounding_provenance_artifact=object(),
            brand_context_artifact=object(),
        )


def test_builder_requires_exact_request_type() -> None:
    with pytest.raises(TypeError, match="request must be"):
        RCISIntelligenceBrandProductGroundedCreativeContextBuilder().build(
            request=object(),  # type: ignore[arg-type]
        )
