from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rie.application.rcis_intelligence_brand_product_grounded_creative_context import (
    RCISIntelligenceBrandProductGroundedCreativeContext,
)

RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_GENERATION_CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceGroundedVisualGenerationRequest:
    grounded_creative_context: RCISIntelligenceBrandProductGroundedCreativeContext
    visual_generation_request_artifact: object


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceGroundedVisualGenerationResult:
    contract_version: str
    request: RCISIntelligenceReferenceGroundedVisualGenerationRequest
    grounded_creative_context: RCISIntelligenceBrandProductGroundedCreativeContext
    creative_intent: object
    reference_role_understanding: object
    locked_product_id: object
    locked_variant_id: object
    authoritative_product_knowledge_artifact: object
    brand_context_artifact: object
    grounding_provenance_artifact: object
    visual_generation_request_artifact: object
    visual_generation_response_artifact: object
    product_identity_locked: bool
    facts_claims_authoritative_only: bool
    product_visual_grounding_established: bool
    reference_grounding_established: bool
    automatic_provider_model_selection_performed: bool
    foundation_model_knowledge_fallback_performed: bool
    retry_loop_performed: bool
    multi_cycle_autonomy_performed: bool


class RCISIntelligenceReferenceGroundedVisualGenerationExecutor:
    def execute(
        self,
        *,
        request: RCISIntelligenceReferenceGroundedVisualGenerationRequest,
        executor: Callable[
            [RCISIntelligenceReferenceGroundedVisualGenerationRequest],
            object,
        ],
    ) -> RCISIntelligenceReferenceGroundedVisualGenerationResult:
        if request is None:
            raise ValueError("request is required")

        context = request.grounded_creative_context
        if context is None:
            raise ValueError("grounded_creative_context is required")

        if request.visual_generation_request_artifact is None:
            raise ValueError("visual_generation_request_artifact is required")

        if executor is None or not callable(executor):
            raise ValueError("executor must be callable")

        if context.product_identity_locked is not True:
            raise ValueError("grounded creative context must preserve product identity lock")

        if context.facts_claims_authoritative_only is not True:
            raise ValueError(
                "grounded creative context must preserve authoritative-only facts/claims"
            )

        if context.product_visual_grounding_established is not True:
            raise ValueError("product visual grounding must already be established")

        reference_role_understanding = context.reference_role_understanding
        if reference_role_understanding is None:
            raise ValueError(
                "reference_role_understanding is required for reference-grounded visual generation"
            )

        response_artifact = executor(request)

        if response_artifact is None:
            raise ValueError("executor returned no visual generation response artifact")

        return RCISIntelligenceReferenceGroundedVisualGenerationResult(
            contract_version=(
                RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_GENERATION_CONTRACT_VERSION
            ),
            request=request,
            grounded_creative_context=context,
            creative_intent=context.creative_intent,
            reference_role_understanding=reference_role_understanding,
            locked_product_id=context.locked_product_id,
            locked_variant_id=context.locked_variant_id,
            authoritative_product_knowledge_artifact=(
                context.authoritative_product_knowledge_artifact
            ),
            brand_context_artifact=context.brand_context_artifact,
            grounding_provenance_artifact=context.grounding_provenance_artifact,
            visual_generation_request_artifact=(
                request.visual_generation_request_artifact
            ),
            visual_generation_response_artifact=response_artifact,
            product_identity_locked=True,
            facts_claims_authoritative_only=True,
            product_visual_grounding_established=True,
            reference_grounding_established=True,
            automatic_provider_model_selection_performed=False,
            foundation_model_knowledge_fallback_performed=False,
            retry_loop_performed=False,
            multi_cycle_autonomy_performed=False,
        )
