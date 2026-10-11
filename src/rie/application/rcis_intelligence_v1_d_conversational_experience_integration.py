from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal

from rie.application.rcis_intelligence_validated_visual_response_assembly import (
    RCISIntelligenceValidatedVisualResponseAssemblyResult,
)

RCIS_INTELLIGENCE_V1_D_CONVERSATIONAL_EXPERIENCE_INTEGRATION_CONTRACT_VERSION = (
    "1.0.0"
)

ConversationResponseKind = Literal["text", "visual"]


@dataclass(frozen=True, slots=True)
class RCISIntelligenceV1DConversationalExperienceIntegrationRequest:
    response_kind: ConversationResponseKind
    conversation_turn_request_artifact: object
    governed_text_response_artifact: object | None
    governed_text_grounding_artifact: object | None
    validated_visual_response: (
        RCISIntelligenceValidatedVisualResponseAssemblyResult | None
    )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceV1DConversationalExperienceIntegrationDecision:
    conversation_response_artifact: object


@dataclass(frozen=True, slots=True)
class RCISIntelligenceV1DConversationalExperienceIntegrationResult:
    contract_version: str
    request: RCISIntelligenceV1DConversationalExperienceIntegrationRequest
    response_kind: ConversationResponseKind
    conversation_turn_request_artifact: object
    conversation_response_artifact: object
    governed_text_response_artifact: object | None
    governed_text_grounding_artifact: object | None
    validated_visual_response: (
        RCISIntelligenceValidatedVisualResponseAssemblyResult | None
    )
    visual_response_artifact: object | None
    visual_delivery_artifact: object | None
    locked_product_id: object | None
    locked_variant_id: object | None
    one_conversational_experience_integration_performed: bool
    explicit_response_kind_preserved: bool
    text_grounding_preserved: bool
    visual_validation_preserved: bool
    product_identity_preserved_without_inference: bool
    automatic_modality_inference_performed: bool
    automatic_provider_model_selection_performed: bool
    provider_invocation_performed: bool
    automatic_regeneration_performed: bool
    retry_loop_performed: bool
    multi_cycle_autonomy_performed: bool


class RCISIntelligenceV1DConversationalExperienceIntegrator:
    def integrate(
        self,
        *,
        request: RCISIntelligenceV1DConversationalExperienceIntegrationRequest,
        assembler: Callable[
            [RCISIntelligenceV1DConversationalExperienceIntegrationRequest],
            RCISIntelligenceV1DConversationalExperienceIntegrationDecision,
        ],
    ) -> RCISIntelligenceV1DConversationalExperienceIntegrationResult:
        if request is None:
            raise ValueError("request is required")

        if request.response_kind not in ("text", "visual"):
            raise ValueError("response_kind must be exactly 'text' or 'visual'")

        if request.conversation_turn_request_artifact is None:
            raise ValueError("conversation_turn_request_artifact is required")

        if assembler is None or not callable(assembler):
            raise ValueError("assembler must be callable")

        if request.response_kind == "text":
            if request.governed_text_response_artifact is None:
                raise ValueError(
                    "text response requires governed_text_response_artifact"
                )
            if request.governed_text_grounding_artifact is None:
                raise ValueError(
                    "text response requires governed_text_grounding_artifact"
                )
            if request.validated_visual_response is not None:
                raise ValueError(
                    "text response must not include validated_visual_response"
                )

            visual_response_artifact = None
            visual_delivery_artifact = None
            locked_product_id = None
            locked_variant_id = None
            text_grounding_preserved = True
            visual_validation_preserved = False
            product_identity_preserved_without_inference = True
        else:
            if request.governed_text_response_artifact is not None:
                raise ValueError(
                    "visual response must not include governed_text_response_artifact"
                )
            if request.governed_text_grounding_artifact is not None:
                raise ValueError(
                    "visual response must not include governed_text_grounding_artifact"
                )

            visual_result = request.validated_visual_response
            if visual_result is None:
                raise ValueError(
                    "visual response requires validated_visual_response"
                )

            if (
                visual_result.validated_visual_response_assembly_performed
                is not True
            ):
                raise ValueError(
                    "validated visual response assembly must already be performed"
                )

            if visual_result.visual_result_validation_performed is not True:
                raise ValueError(
                    "visual result validation must already be performed"
                )

            if visual_result.product_identity_locked is not True:
                raise ValueError(
                    "validated visual response must preserve product identity lock"
                )

            if not isinstance(visual_result.accepted, bool):
                raise TypeError("validated visual response accepted must be bool")

            if visual_result.response_artifact is None:
                raise ValueError(
                    "validated visual response must preserve response_artifact"
                )

            if visual_result.accepted:
                if visual_result.visual_delivery_artifact is None:
                    raise ValueError(
                        "accepted validated visual response requires "
                        "visual_delivery_artifact"
                    )
            elif visual_result.visual_delivery_artifact is not None:
                raise ValueError(
                    "rejected validated visual response must not expose "
                    "visual_delivery_artifact"
                )

            visual_response_artifact = visual_result.response_artifact
            visual_delivery_artifact = visual_result.visual_delivery_artifact
            locked_product_id = visual_result.locked_product_id
            locked_variant_id = visual_result.locked_variant_id
            text_grounding_preserved = False
            visual_validation_preserved = True
            product_identity_preserved_without_inference = True

        decision = assembler(request)

        if not isinstance(
            decision,
            RCISIntelligenceV1DConversationalExperienceIntegrationDecision,
        ):
            raise TypeError(
                "assembler must return "
                "RCISIntelligenceV1DConversationalExperienceIntegrationDecision"
            )

        if decision.conversation_response_artifact is None:
            raise ValueError("conversation_response_artifact is required")

        return RCISIntelligenceV1DConversationalExperienceIntegrationResult(
            contract_version=(
                RCIS_INTELLIGENCE_V1_D_CONVERSATIONAL_EXPERIENCE_INTEGRATION_CONTRACT_VERSION
            ),
            request=request,
            response_kind=request.response_kind,
            conversation_turn_request_artifact=(
                request.conversation_turn_request_artifact
            ),
            conversation_response_artifact=(
                decision.conversation_response_artifact
            ),
            governed_text_response_artifact=(
                request.governed_text_response_artifact
            ),
            governed_text_grounding_artifact=(
                request.governed_text_grounding_artifact
            ),
            validated_visual_response=request.validated_visual_response,
            visual_response_artifact=visual_response_artifact,
            visual_delivery_artifact=visual_delivery_artifact,
            locked_product_id=locked_product_id,
            locked_variant_id=locked_variant_id,
            one_conversational_experience_integration_performed=True,
            explicit_response_kind_preserved=True,
            text_grounding_preserved=text_grounding_preserved,
            visual_validation_preserved=visual_validation_preserved,
            product_identity_preserved_without_inference=(
                product_identity_preserved_without_inference
            ),
            automatic_modality_inference_performed=False,
            automatic_provider_model_selection_performed=False,
            provider_invocation_performed=False,
            automatic_regeneration_performed=False,
            retry_loop_performed=False,
            multi_cycle_autonomy_performed=False,
        )
