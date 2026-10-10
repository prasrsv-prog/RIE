from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rie.application.rcis_intelligence_reference_grounded_visual_generation import (
    RCISIntelligenceReferenceGroundedVisualGenerationResult,
)

RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_RESULT_VALIDATION_CONTRACT_VERSION = (
    "1.0.0"
)


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceGroundedVisualResultValidationRequest:
    visual_generation_result: RCISIntelligenceReferenceGroundedVisualGenerationResult
    validation_request_artifact: object


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceGroundedVisualResultValidationDecision:
    accepted: bool
    validation_artifact: object


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceGroundedVisualResultValidationResult:
    contract_version: str
    request: RCISIntelligenceReferenceGroundedVisualResultValidationRequest
    visual_generation_result: RCISIntelligenceReferenceGroundedVisualGenerationResult
    grounded_creative_context: object
    creative_intent: object
    reference_role_understanding: object
    locked_product_id: object
    locked_variant_id: object
    authoritative_product_knowledge_artifact: object
    brand_context_artifact: object
    grounding_provenance_artifact: object
    visual_generation_request_artifact: object
    visual_generation_response_artifact: object
    validation_request_artifact: object
    validation_decision: RCISIntelligenceReferenceGroundedVisualResultValidationDecision
    validation_artifact: object
    accepted: bool
    product_identity_locked: bool
    facts_claims_authoritative_only: bool
    product_visual_grounding_established: bool
    reference_grounding_established: bool
    visual_result_validation_performed: bool
    automatic_regeneration_performed: bool
    automatic_provider_model_selection_performed: bool
    foundation_model_knowledge_fallback_performed: bool
    retry_loop_performed: bool
    multi_cycle_autonomy_performed: bool


class RCISIntelligenceReferenceGroundedVisualResultValidator:
    def validate(
        self,
        *,
        request: RCISIntelligenceReferenceGroundedVisualResultValidationRequest,
        validator: Callable[
            [RCISIntelligenceReferenceGroundedVisualResultValidationRequest],
            RCISIntelligenceReferenceGroundedVisualResultValidationDecision,
        ],
    ) -> RCISIntelligenceReferenceGroundedVisualResultValidationResult:
        if request is None:
            raise ValueError("request is required")

        generation_result = request.visual_generation_result
        if generation_result is None:
            raise ValueError("visual_generation_result is required")

        if request.validation_request_artifact is None:
            raise ValueError("validation_request_artifact is required")

        if validator is None or not callable(validator):
            raise ValueError("validator must be callable")

        if generation_result.product_identity_locked is not True:
            raise ValueError("visual generation result must preserve product identity lock")

        if generation_result.facts_claims_authoritative_only is not True:
            raise ValueError(
                "visual generation result must preserve authoritative-only facts/claims"
            )

        if generation_result.product_visual_grounding_established is not True:
            raise ValueError(
                "visual generation result must preserve product visual grounding"
            )

        if generation_result.reference_grounding_established is not True:
            raise ValueError(
                "visual generation result must preserve reference grounding"
            )

        if generation_result.reference_role_understanding is None:
            raise ValueError(
                "visual generation result must preserve reference_role_understanding"
            )

        if generation_result.visual_generation_response_artifact is None:
            raise ValueError(
                "visual_generation_response_artifact is required for validation"
            )

        decision = validator(request)

        if not isinstance(
            decision,
            RCISIntelligenceReferenceGroundedVisualResultValidationDecision,
        ):
            raise TypeError(
                "validator must return "
                "RCISIntelligenceReferenceGroundedVisualResultValidationDecision"
            )

        if not isinstance(decision.accepted, bool):
            raise TypeError("validation decision accepted must be bool")

        if decision.validation_artifact is None:
            raise ValueError("validation_artifact is required")

        return RCISIntelligenceReferenceGroundedVisualResultValidationResult(
            contract_version=(
                RCIS_INTELLIGENCE_REFERENCE_GROUNDED_VISUAL_RESULT_VALIDATION_CONTRACT_VERSION
            ),
            request=request,
            visual_generation_result=generation_result,
            grounded_creative_context=generation_result.grounded_creative_context,
            creative_intent=generation_result.creative_intent,
            reference_role_understanding=(
                generation_result.reference_role_understanding
            ),
            locked_product_id=generation_result.locked_product_id,
            locked_variant_id=generation_result.locked_variant_id,
            authoritative_product_knowledge_artifact=(
                generation_result.authoritative_product_knowledge_artifact
            ),
            brand_context_artifact=generation_result.brand_context_artifact,
            grounding_provenance_artifact=(
                generation_result.grounding_provenance_artifact
            ),
            visual_generation_request_artifact=(
                generation_result.visual_generation_request_artifact
            ),
            visual_generation_response_artifact=(
                generation_result.visual_generation_response_artifact
            ),
            validation_request_artifact=request.validation_request_artifact,
            validation_decision=decision,
            validation_artifact=decision.validation_artifact,
            accepted=decision.accepted,
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
