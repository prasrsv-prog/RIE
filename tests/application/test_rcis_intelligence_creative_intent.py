from dataclasses import FrozenInstanceError

import pytest

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
    request = RCISIntelligenceProductVariantLockRequest(
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
    ).lock(request=request)


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


def _request(
    *,
    brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
    creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
    reference_role_understanding=None,
    ignore_from_reference=(),
):
    return RCISIntelligenceCreativeIntentRequest(
        objective="Buat key visual launch yang premium.",
        user_creative_direction="Gunakan nuansa cyberpunk yang elegan.",
        brand_guidance_mode=brand_guidance_mode,
        creative_freedom=creative_freedom,
        product_variant_lock=_lock(),
        reference_role_understanding=reference_role_understanding,
        ignore_from_reference=ignore_from_reference,
    )


def test_builder_preserves_exact_locked_product_and_variant() -> None:
    request = _request()
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )

    assert result.request is request
    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id == "variant-1"
    assert result.product_identity_locked is True


def test_product_only_lock_is_preserved_without_variant_inference() -> None:
    request = RCISIntelligenceCreativeIntentRequest(
        objective="Buat visual produk.",
        user_creative_direction="Tampilkan produk dengan bersih.",
        brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
        creative_freedom=RCISIntelligenceCreativeFreedom.CONTROLLED,
        product_variant_lock=_lock(variant_id=None),
    )

    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )

    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id is None


def test_reference_role_understanding_identity_is_preserved() -> None:
    roles = _reference_roles()
    request = _request(
        reference_role_understanding=roles,
    )

    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )

    assert result.reference_role_understanding is roles


def test_reference_roles_are_optional() -> None:
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=_request(),
    )

    assert result.reference_role_understanding is None


def test_ignore_from_reference_is_preserved_exactly() -> None:
    ignore = ("logo dari referensi", "teks promosi referensi")
    request = _request(
        reference_role_understanding=_reference_roles(),
        ignore_from_reference=ignore,
    )

    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )

    assert result.ignore_from_reference is ignore


@pytest.mark.parametrize(
    "mode",
    list(RCISIntelligenceBrandGuidanceMode),
)
def test_all_brand_guidance_modes_are_explicitly_supported(mode) -> None:
    request = _request(brand_guidance_mode=mode)
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )
    assert result.brand_guidance_mode is mode


@pytest.mark.parametrize(
    "freedom",
    list(RCISIntelligenceCreativeFreedom),
)
def test_all_creative_freedom_modes_are_supported(freedom) -> None:
    request = _request(creative_freedom=freedom)
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=request,
    )
    assert result.creative_freedom is freedom


def test_facts_and_claims_remain_authoritative_only() -> None:
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=_request(),
    )
    assert result.facts_claims_authoritative_only is True


def test_builder_does_not_perform_product_visual_grounding_or_generation() -> None:
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=_request(),
    )

    assert result.product_visual_grounding_performed is False
    assert result.downstream_visual_generation_performed is False


def test_request_is_immutable() -> None:
    request = _request()

    with pytest.raises(FrozenInstanceError):
        request.objective = "changed"  # type: ignore[misc]


def test_result_is_immutable() -> None:
    result = RCISIntelligenceCreativeIntentBuilder().build(
        request=_request(),
    )

    with pytest.raises(FrozenInstanceError):
        result.locked_product_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("objective", ["", "   "])
def test_blank_objective_is_rejected(objective: str) -> None:
    with pytest.raises(ValueError, match="objective must not be empty"):
        RCISIntelligenceCreativeIntentRequest(
            objective=objective,
            user_creative_direction="Arah kreatif.",
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=_lock(),
        )


@pytest.mark.parametrize("direction", ["", "   "])
def test_blank_user_creative_direction_is_rejected(direction: str) -> None:
    with pytest.raises(
        ValueError,
        match="user_creative_direction must not be empty",
    ):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction=direction,
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=_lock(),
        )


def test_invalid_brand_guidance_mode_is_rejected() -> None:
    with pytest.raises(TypeError, match="brand_guidance_mode must be"):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction="Direction.",
            brand_guidance_mode="BALANCED",  # type: ignore[arg-type]
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=_lock(),
        )


def test_invalid_creative_freedom_is_rejected() -> None:
    with pytest.raises(TypeError, match="creative_freedom must be"):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction="Direction.",
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom="BALANCED",  # type: ignore[arg-type]
            product_variant_lock=_lock(),
        )


def test_invalid_lock_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="product_variant_lock must be"):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction="Direction.",
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=object(),  # type: ignore[arg-type]
        )


def test_invalid_reference_role_understanding_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="reference_role_understanding must be",
    ):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction="Direction.",
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=_lock(),
            reference_role_understanding=object(),  # type: ignore[arg-type]
        )


def test_ignore_from_reference_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="ignore_from_reference must be tuple"):
        RCISIntelligenceCreativeIntentRequest(
            objective="Objective.",
            user_creative_direction="Direction.",
            brand_guidance_mode=RCISIntelligenceBrandGuidanceMode.BALANCED,
            creative_freedom=RCISIntelligenceCreativeFreedom.BALANCED,
            product_variant_lock=_lock(),
            ignore_from_reference=["logo"],  # type: ignore[arg-type]
        )


def test_ignore_from_reference_values_must_be_unique() -> None:
    with pytest.raises(
        ValueError,
        match="ignore_from_reference values must be unique",
    ):
        _request(
            ignore_from_reference=("logo", "logo"),
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_ignore_from_reference_value_is_rejected(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="ignore_from_reference item must not be empty",
    ):
        _request(ignore_from_reference=(value,))


def test_builder_requires_exact_request_type() -> None:
    with pytest.raises(TypeError, match="request must be"):
        RCISIntelligenceCreativeIntentBuilder().build(
            request=object(),  # type: ignore[arg-type]
        )
