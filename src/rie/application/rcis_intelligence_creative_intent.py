"""Minimum governed creative-intent contract for RCIS Intelligence v1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from rie.application.rcis_intelligence_product_variant_lock import (
    RCISIntelligenceProductVariantLockResult,
)
from rie.application.rcis_intelligence_reference_image_role import (
    RCISIntelligenceReferenceImageRoleUnderstandingResult,
)


RCIS_INTELLIGENCE_CREATIVE_INTENT_CONTRACT_VERSION: Final[str] = "1.0.0"


class RCISIntelligenceBrandGuidanceMode(str, Enum):
    """How strongly established brand language should guide creative execution."""

    STRICT = "STRICT"
    BALANCED = "BALANCED"
    EXPLORATORY = "EXPLORATORY"
    FREE = "FREE"


class RCISIntelligenceCreativeFreedom(str, Enum):
    """Bounded creative freedom explicitly chosen for the request."""

    CONTROLLED = "CONTROLLED"
    BALANCED = "BALANCED"
    EXPANSIVE = "EXPANSIVE"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def _validate_ignore_from_reference(values: tuple[str, ...]) -> None:
    if not isinstance(values, tuple):
        raise TypeError("ignore_from_reference must be tuple")
    for value in values:
        _require_non_empty_text(
            value,
            field_name="ignore_from_reference item",
        )
    if len(set(values)) != len(values):
        raise ValueError("ignore_from_reference values must be unique")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceCreativeIntentRequest:
    """Immutable explicit creative direction over an already locked product target."""

    objective: str
    user_creative_direction: str
    brand_guidance_mode: RCISIntelligenceBrandGuidanceMode
    creative_freedom: RCISIntelligenceCreativeFreedom
    product_variant_lock: RCISIntelligenceProductVariantLockResult
    reference_role_understanding: (
        RCISIntelligenceReferenceImageRoleUnderstandingResult | None
    ) = None
    ignore_from_reference: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_text(self.objective, field_name="objective")
        _require_non_empty_text(
            self.user_creative_direction,
            field_name="user_creative_direction",
        )

        if not isinstance(
            self.brand_guidance_mode,
            RCISIntelligenceBrandGuidanceMode,
        ):
            raise TypeError(
                "brand_guidance_mode must be RCISIntelligenceBrandGuidanceMode"
            )

        if not isinstance(
            self.creative_freedom,
            RCISIntelligenceCreativeFreedom,
        ):
            raise TypeError(
                "creative_freedom must be RCISIntelligenceCreativeFreedom"
            )

        if not isinstance(
            self.product_variant_lock,
            RCISIntelligenceProductVariantLockResult,
        ):
            raise TypeError(
                "product_variant_lock must be "
                "RCISIntelligenceProductVariantLockResult"
            )

        if not self.product_variant_lock.product_identity_locked:
            raise ValueError(
                "creative intent requires an already locked product identity"
            )

        if (
            self.reference_role_understanding is not None
            and not isinstance(
                self.reference_role_understanding,
                RCISIntelligenceReferenceImageRoleUnderstandingResult,
            )
        ):
            raise TypeError(
                "reference_role_understanding must be "
                "RCISIntelligenceReferenceImageRoleUnderstandingResult or None"
            )

        _validate_ignore_from_reference(self.ignore_from_reference)


@dataclass(frozen=True, slots=True)
class RCISIntelligenceCreativeIntent:
    """Immutable Creative Intent Contract without downstream grounding or generation."""

    contract_version: str
    request: RCISIntelligenceCreativeIntentRequest
    objective: str
    locked_product_id: str
    locked_variant_id: str | None
    reference_role_understanding: (
        RCISIntelligenceReferenceImageRoleUnderstandingResult | None
    )
    ignore_from_reference: tuple[str, ...]
    user_creative_direction: str
    brand_guidance_mode: RCISIntelligenceBrandGuidanceMode
    creative_freedom: RCISIntelligenceCreativeFreedom
    product_identity_locked: bool
    facts_claims_authoritative_only: bool
    product_visual_grounding_performed: bool
    downstream_visual_generation_performed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CREATIVE_INTENT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported creative-intent contract version")

        if not isinstance(
            self.request,
            RCISIntelligenceCreativeIntentRequest,
        ):
            raise TypeError(
                "request must be RCISIntelligenceCreativeIntentRequest"
            )

        _require_non_empty_text(self.objective, field_name="objective")
        _require_non_empty_text(
            self.locked_product_id,
            field_name="locked_product_id",
        )
        if self.locked_variant_id is not None:
            _require_non_empty_text(
                self.locked_variant_id,
                field_name="locked_variant_id",
            )

        if (
            self.reference_role_understanding is not None
            and not isinstance(
                self.reference_role_understanding,
                RCISIntelligenceReferenceImageRoleUnderstandingResult,
            )
        ):
            raise TypeError(
                "reference_role_understanding must be "
                "RCISIntelligenceReferenceImageRoleUnderstandingResult or None"
            )

        _validate_ignore_from_reference(self.ignore_from_reference)
        _require_non_empty_text(
            self.user_creative_direction,
            field_name="user_creative_direction",
        )

        if not isinstance(
            self.brand_guidance_mode,
            RCISIntelligenceBrandGuidanceMode,
        ):
            raise TypeError(
                "brand_guidance_mode must be RCISIntelligenceBrandGuidanceMode"
            )
        if not isinstance(
            self.creative_freedom,
            RCISIntelligenceCreativeFreedom,
        ):
            raise TypeError(
                "creative_freedom must be RCISIntelligenceCreativeFreedom"
            )

        for field_name, value in (
            ("product_identity_locked", self.product_identity_locked),
            (
                "facts_claims_authoritative_only",
                self.facts_claims_authoritative_only,
            ),
            (
                "product_visual_grounding_performed",
                self.product_visual_grounding_performed,
            ),
            (
                "downstream_visual_generation_performed",
                self.downstream_visual_generation_performed,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if not self.product_identity_locked:
            raise ValueError("creative intent must preserve product identity lock")
        if not self.facts_claims_authoritative_only:
            raise ValueError(
                "creative intent must require authoritative-only facts and claims"
            )
        if self.product_visual_grounding_performed:
            raise ValueError(
                "creative-intent contract must not perform product visual grounding"
            )
        if self.downstream_visual_generation_performed:
            raise ValueError(
                "creative-intent contract must not execute visual generation"
            )


class RCISIntelligenceCreativeIntentBuilder:
    """Build one deterministic intent object from explicit governed inputs."""

    def build(
        self,
        *,
        request: RCISIntelligenceCreativeIntentRequest,
    ) -> RCISIntelligenceCreativeIntent:
        if not isinstance(
            request,
            RCISIntelligenceCreativeIntentRequest,
        ):
            raise TypeError(
                "request must be RCISIntelligenceCreativeIntentRequest"
            )

        lock = request.product_variant_lock

        return RCISIntelligenceCreativeIntent(
            contract_version=RCIS_INTELLIGENCE_CREATIVE_INTENT_CONTRACT_VERSION,
            request=request,
            objective=request.objective,
            locked_product_id=lock.locked_product_id,
            locked_variant_id=lock.locked_variant_id,
            reference_role_understanding=request.reference_role_understanding,
            ignore_from_reference=request.ignore_from_reference,
            user_creative_direction=request.user_creative_direction,
            brand_guidance_mode=request.brand_guidance_mode,
            creative_freedom=request.creative_freedom,
            product_identity_locked=True,
            facts_claims_authoritative_only=True,
            product_visual_grounding_performed=False,
            downstream_visual_generation_performed=False,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CREATIVE_INTENT_CONTRACT_VERSION",
    "RCISIntelligenceBrandGuidanceMode",
    "RCISIntelligenceCreativeFreedom",
    "RCISIntelligenceCreativeIntent",
    "RCISIntelligenceCreativeIntentBuilder",
    "RCISIntelligenceCreativeIntentRequest",
]
