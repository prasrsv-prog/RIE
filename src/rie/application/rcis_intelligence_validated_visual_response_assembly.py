from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rie.application.rcis_intelligence_reference_grounded_visual_result_validation import (
    RCISIntelligenceReferenceGroundedVisualResultValidationResult,
)

RCIS_INTELLIGENCE_VALIDATED_VISUAL_RESPONSE_ASSEMBLY_CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class RCISIntelligenceValidatedVisualResponseAssemblyRequest:
    validated_visual_result: RCISIntelligenceReferenceGroundedVisualResultValidationResult
    response_assembly_request_artifact: object


@dataclass(frozen=True, slots=True)
class RCISIntelligenceValidatedVisualResponseAssemblyDecision:
    response_artifact: object
    visual_delivery_artifact: object | None


@dataclass(frozen=True, slots=True)
class RCISIntelligenceValidatedVisualResponseAssemblyResult:
    contract_version: str
    request: RCISIntelligenceValidatedVisualResponseAssemblyRequest
    validated_visual_result: RCISIntelligenceReferenceGroundedVisualResultValidationResult
    visual_generation_result: object
    validation_decision: object
    validation_artifact: object
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
    response_assembly_request_artifact: object
    response_artifact: object
    visual_delivery_artifact: object | None
    accepted: bool
    product_identity_locked: bool
    facts_claims_authoritative_only: bool
    product_visual_grounding_established: bool
    reference_grounding_established: bool
    visual_result_validation_performed: bool
    validated_visual_response_assembly_performed: bool
    rejected_visual_delivery_blocked: bool
    automatic_regeneration_performed: bool
    automatic_provider_model_selection_performed: bool
    tool_provider_invocation_performed: bool
    foundation_model_knowledge_fallback_performed: bool
    retry_loop_performed: bool
    multi_cycle_autonomy_performed: bool


class RCISIntelligenceValidatedVisualResponseAssembler:
    def assemble(
        self,
        *,
        request: RCISIntelligenceValidatedVisualResponseAssemblyRequest,
        assembler: Callable[
            [RCISIntelligenceValidatedVisualResponseAssemblyRequest],
            RCISIntelligenceValidatedVisualResponseAssemblyDecision,
        ],
    ) -> RCISIntelligenceValidatedVisualResponseAssemblyResult:
        if request is None:
            raise ValueError("request is required")

        validation_result = request.validated_visual_result
        if validation_result is None:
            raise ValueError("validated_visual_result is required")

        if request.response_assembly_request_artifact is None:
            raise ValueError("response_assembly_request_artifact is required")

        if assembler is None or not callable(assembler):
            raise ValueError("assembler must be callable")

        if validation_result.product_identity_locked is not True:
            raise ValueError("validated visual result must preserve product identity lock")

        if validation_result.facts_claims_authoritative_only is not True:
            raise ValueError(
                "validated visual result must preserve authoritative-only facts/claims"
            )

        if validation_result.product_visual_grounding_established is not True:
            raise ValueError(
                "validated visual result must preserve product visual grounding"
            )

        if validation_result.reference_grounding_established is not True:
            raise ValueError(
                "validated visual result must preserve reference grounding"
            )

        if validation_result.visual_result_validation_performed is not True:
            raise ValueError("visual result validation must already be performed")

        if not isinstance(validation_result.accepted, bool):
            raise TypeError("validated visual result accepted must be bool")

        if validation_result.reference_role_understanding is None:
            raise ValueError(
                "validated visual result must preserve reference_role_understanding"
            )

        if validation_result.visual_generation_result is None:
            raise ValueError(
                "validated visual result must preserve visual_generation_result"
            )

        if validation_result.visual_generation_response_artifact is None:
            raise ValueError(
                "validated visual result must preserve visual_generation_response_artifact"
            )

        if validation_result.validation_decision is None:
            raise ValueError(
                "validated visual result must preserve validation_decision"
            )

        if validation_result.validation_artifact is None:
            raise ValueError(
                "validated visual result must preserve validation_artifact"
            )

        decision = assembler(request)

        if not isinstance(
            decision,
            RCISIntelligenceValidatedVisualResponseAssemblyDecision,
        ):
            raise TypeError(
                "assembler must return "
                "RCISIntelligenceValidatedVisualResponseAssemblyDecision"
            )

        if decision.response_artifact is None:
            raise ValueError("response_artifact is required")

        if validation_result.accepted:
            if decision.visual_delivery_artifact is None:
                raise ValueError(
                    "accepted validated visual result requires visual_delivery_artifact"
                )
        elif decision.visual_delivery_artifact is not None:
            raise ValueError(
                "rejected validated visual result must not expose visual_delivery_artifact"
            )

        return RCISIntelligenceValidatedVisualResponseAssemblyResult(
            contract_version=(
                RCIS_INTELLIGENCE_VALIDATED_VISUAL_RESPONSE_ASSEMBLY_CONTRACT_VERSION
            ),
            request=request,
            validated_visual_result=validation_result,
            visual_generation_result=validation_result.visual_generation_result,
            validation_decision=validation_result.validation_decision,
            validation_artifact=validation_result.validation_artifact,
            grounded_creative_context=validation_result.grounded_creative_context,
            creative_intent=validation_result.creative_intent,
            reference_role_understanding=(
                validation_result.reference_role_understanding
            ),
            locked_product_id=validation_result.locked_product_id,
            locked_variant_id=validation_result.locked_variant_id,
            authoritative_product_knowledge_artifact=(
                validation_result.authoritative_product_knowledge_artifact
            ),
            brand_context_artifact=validation_result.brand_context_artifact,
            grounding_provenance_artifact=(
                validation_result.grounding_provenance_artifact
            ),
            visual_generation_request_artifact=(
                validation_result.visual_generation_request_artifact
            ),
            visual_generation_response_artifact=(
                validation_result.visual_generation_response_artifact
            ),
            response_assembly_request_artifact=(
                request.response_assembly_request_artifact
            ),
            response_artifact=decision.response_artifact,
            visual_delivery_artifact=decision.visual_delivery_artifact,
            accepted=validation_result.accepted,
            product_identity_locked=True,
            facts_claims_authoritative_only=True,
            product_visual_grounding_established=True,
            reference_grounding_established=True,
            visual_result_validation_performed=True,
            validated_visual_response_assembly_performed=True,
            rejected_visual_delivery_blocked=not validation_result.accepted,
            automatic_regeneration_performed=False,
            automatic_provider_model_selection_performed=False,
            tool_provider_invocation_performed=False,
            foundation_model_knowledge_fallback_performed=False,
            retry_loop_performed=False,
            multi_cycle_autonomy_performed=False,
        )
