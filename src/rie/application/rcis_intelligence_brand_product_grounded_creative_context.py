"""Minimum governed brand/product-grounded creative-context contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_creative_intent import (
    RCISIntelligenceBrandGuidanceMode,
    RCISIntelligenceCreativeFreedom,
    RCISIntelligenceCreativeIntent,
)
from rie.application.rcis_intelligence_reference_image_role import (
    RCISIntelligenceReferenceImageRoleUnderstandingResult,
)


RCIS_INTELLIGENCE_BRAND_PRODUCT_GROUNDED_CREATIVE_CONTEXT_CONTRACT_VERSION: Final[
    str
] = "1.0.0"


def _require_artifact(value: object | None, *, field_name: str) -> object:
    if value is None:
        raise ValueError(f"{field_name} must not be None")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceBrandProductGroundedCreativeContextRequest:
    """Caller-supplied governed grounding inputs over an immutable Creative Intent."""

    creative_intent: RCISIntelligenceCreativeIntent
    authoritative_product_knowledge_artifact: object
    grounding_provenance_artifact: object
    brand_context_artifact: object | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.creative_intent,
            RCISIntelligenceCreativeIntent,
        ):
            raise TypeError(
                "creative_intent must be RCISIntelligenceCreativeIntent"
            )

        if not self.creative_intent.product_identity_locked:
            raise ValueError(
                "grounded creative context requires locked product identity"
            )

        if not self.creative_intent.facts_claims_authoritative_only:
            raise ValueError(
                "grounded creative context requires authoritative-only facts "
                "and claims"
            )

        _require_artifact(
            self.authoritative_product_knowledge_artifact,
            field_name="authoritative_product_knowledge_artifact",
        )
        _require_artifact(
            self.grounding_provenance_artifact,
            field_name="grounding_provenance_artifact",
        )

        if (
            self.creative_intent.brand_guidance_mode
            is not RCISIntelligenceBrandGuidanceMode.FREE
            and self.brand_context_artifact is None
        ):
            raise ValueError(
                "brand_context_artifact is required unless brand guidance is FREE"
            )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceBrandProductGroundedCreativeContext:
    """Immutable grounded context for downstream visual generation."""

    contract_version: str
    request: RCISIntelligenceBrandProductGroundedCreativeContextRequest
    creative_intent: RCISIntelligenceCreativeIntent
    locked_product_id: str
    locked_variant_id: str | None
    authoritative_product_knowledge_artifact: object
    brand_context_artifact: object | None
    grounding_provenance_artifact: object
    reference_role_understanding: (
        RCISIntelligenceReferenceImageRoleUnderstandingResult | None
    )
    brand_guidance_mode: RCISIntelligenceBrandGuidanceMode
    creative_freedom: RCISIntelligenceCreativeFreedom
    product_identity_locked: bool
    facts_claims_authoritative_only: bool
    product_visual_grounding_established: bool
    brand_context_grounded: bool
    image_analysis_performed: bool
    downstream_visual_generation_performed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_BRAND_PRODUCT_GROUNDED_CREATIVE_CONTEXT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported grounded creative-context contract version")

        if not isinstance(
            self.request,
            RCISIntelligenceBrandProductGroundedCreativeContextRequest,
        ):
            raise TypeError(
                "request must be "
                "RCISIntelligenceBrandProductGroundedCreativeContextRequest"
            )
        if not isinstance(
            self.creative_intent,
            RCISIntelligenceCreativeIntent,
        ):
            raise TypeError(
                "creative_intent must be RCISIntelligenceCreativeIntent"
            )

        if self.creative_intent is not self.request.creative_intent:
            raise ValueError(
                "creative_intent must preserve exact request object identity"
            )

        if self.locked_product_id != self.creative_intent.locked_product_id:
            raise ValueError(
                "locked_product_id must match creative intent exactly"
            )
        if self.locked_variant_id != self.creative_intent.locked_variant_id:
            raise ValueError(
                "locked_variant_id must match creative intent exactly"
            )

        _require_artifact(
            self.authoritative_product_knowledge_artifact,
            field_name="authoritative_product_knowledge_artifact",
        )
        _require_artifact(
            self.grounding_provenance_artifact,
            field_name="grounding_provenance_artifact",
        )

        if (
            self.authoritative_product_knowledge_artifact
            is not self.request.authoritative_product_knowledge_artifact
        ):
            raise ValueError(
                "authoritative product knowledge artifact identity must be preserved"
            )
        if (
            self.brand_context_artifact
            is not self.request.brand_context_artifact
        ):
            raise ValueError(
                "brand context artifact identity must be preserved"
            )
        if (
            self.grounding_provenance_artifact
            is not self.request.grounding_provenance_artifact
        ):
            raise ValueError(
                "grounding provenance artifact identity must be preserved"
            )

        if (
            self.reference_role_understanding
            is not self.creative_intent.reference_role_understanding
        ):
            raise ValueError(
                "reference-role understanding identity must be preserved"
            )

        if self.brand_guidance_mode is not self.creative_intent.brand_guidance_mode:
            raise ValueError(
                "brand guidance mode must match creative intent"
            )
        if self.creative_freedom is not self.creative_intent.creative_freedom:
            raise ValueError(
                "creative freedom must match creative intent"
            )

        for field_name, value in (
            ("product_identity_locked", self.product_identity_locked),
            (
                "facts_claims_authoritative_only",
                self.facts_claims_authoritative_only,
            ),
            (
                "product_visual_grounding_established",
                self.product_visual_grounding_established,
            ),
            ("brand_context_grounded", self.brand_context_grounded),
            ("image_analysis_performed", self.image_analysis_performed),
            (
                "downstream_visual_generation_performed",
                self.downstream_visual_generation_performed,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if not self.product_identity_locked:
            raise ValueError("product identity lock must remain hard")
        if not self.facts_claims_authoritative_only:
            raise ValueError(
                "facts and claims must remain authoritative-only"
            )
        if not self.product_visual_grounding_established:
            raise ValueError(
                "authoritative product visual grounding must be established"
            )

        expected_brand_grounded = self.brand_context_artifact is not None
        if self.brand_context_grounded is not expected_brand_grounded:
            raise ValueError(
                "brand_context_grounded must match brand_context_artifact presence"
            )

        if (
            self.brand_guidance_mode is not RCISIntelligenceBrandGuidanceMode.FREE
            and not self.brand_context_grounded
        ):
            raise ValueError(
                "non-FREE brand guidance requires grounded brand context"
            )

        if self.image_analysis_performed:
            raise ValueError(
                "grounded creative-context contract must not perform image analysis"
            )
        if self.downstream_visual_generation_performed:
            raise ValueError(
                "grounded creative-context contract must not execute visual generation"
            )


class RCISIntelligenceBrandProductGroundedCreativeContextBuilder:
    """Assemble explicit governed grounding without model/provider execution."""

    def build(
        self,
        *,
        request: RCISIntelligenceBrandProductGroundedCreativeContextRequest,
    ) -> RCISIntelligenceBrandProductGroundedCreativeContext:
        if not isinstance(
            request,
            RCISIntelligenceBrandProductGroundedCreativeContextRequest,
        ):
            raise TypeError(
                "request must be "
                "RCISIntelligenceBrandProductGroundedCreativeContextRequest"
            )

        creative_intent = request.creative_intent

        return RCISIntelligenceBrandProductGroundedCreativeContext(
            contract_version=(
                RCIS_INTELLIGENCE_BRAND_PRODUCT_GROUNDED_CREATIVE_CONTEXT_CONTRACT_VERSION
            ),
            request=request,
            creative_intent=creative_intent,
            locked_product_id=creative_intent.locked_product_id,
            locked_variant_id=creative_intent.locked_variant_id,
            authoritative_product_knowledge_artifact=(
                request.authoritative_product_knowledge_artifact
            ),
            brand_context_artifact=request.brand_context_artifact,
            grounding_provenance_artifact=request.grounding_provenance_artifact,
            reference_role_understanding=(
                creative_intent.reference_role_understanding
            ),
            brand_guidance_mode=creative_intent.brand_guidance_mode,
            creative_freedom=creative_intent.creative_freedom,
            product_identity_locked=True,
            facts_claims_authoritative_only=True,
            product_visual_grounding_established=True,
            brand_context_grounded=request.brand_context_artifact is not None,
            image_analysis_performed=False,
            downstream_visual_generation_performed=False,
        )


__all__ = [
    "RCIS_INTELLIGENCE_BRAND_PRODUCT_GROUNDED_CREATIVE_CONTEXT_CONTRACT_VERSION",
    "RCISIntelligenceBrandProductGroundedCreativeContext",
    "RCISIntelligenceBrandProductGroundedCreativeContextBuilder",
    "RCISIntelligenceBrandProductGroundedCreativeContextRequest",
]
