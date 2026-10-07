"""Minimum governed conversational-answer generation contract for RCIS intelligence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_answer_provenance import (
    RCISIntelligenceAnswerProvenance,
)
from rie.application.rcis_intelligence_context_assembly import RCISIntelligenceContext
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionStatus,
)


RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def _validate_governed_boundaries(
    *,
    context: RCISIntelligenceContext,
    resolution: RCISConversationalEntityResolution,
    provenance: RCISIntelligenceAnswerProvenance,
) -> None:
    if not isinstance(context, RCISIntelligenceContext):
        raise TypeError("context must be RCISIntelligenceContext")
    if not isinstance(resolution, RCISConversationalEntityResolution):
        raise TypeError("resolution must be RCISConversationalEntityResolution")
    if not isinstance(provenance, RCISIntelligenceAnswerProvenance):
        raise TypeError("provenance must be RCISIntelligenceAnswerProvenance")
    if resolution.status is not RCISConversationalEntityResolutionStatus.RESOLVED:
        raise ValueError("resolution must be RESOLVED before answer generation")
    if resolution.product_id != context.product_id:
        raise ValueError("resolved product does not match governed context")
    if resolution.variant_id is not None and resolution.variant_id != context.variant_id:
        raise ValueError("resolved variant does not match governed context")
    if provenance.context_contract_version != context.contract_version:
        raise ValueError("provenance context contract version mismatch")
    if provenance.entity_resolution_contract_version != resolution.contract_version:
        raise ValueError("provenance entity-resolution contract version mismatch")
    if provenance.context_product_id != context.product_id:
        raise ValueError("provenance context product mismatch")
    if provenance.context_variant_id != context.variant_id:
        raise ValueError("provenance context variant mismatch")
    if provenance.resolved_product_id != resolution.product_id:
        raise ValueError("provenance resolved product mismatch")
    if provenance.resolved_variant_id != resolution.variant_id:
        raise ValueError("provenance resolved variant mismatch")
    if provenance.resolution_basis is not resolution.resolution_basis:
        raise ValueError("provenance resolution basis mismatch")
    if provenance.context_source_boundaries != context.source_boundaries:
        raise ValueError("provenance source-boundary mismatch")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalAnswerInput:
    """Immutable input passed to one caller-supplied answer renderer."""

    utterance: str
    context: RCISIntelligenceContext
    resolution: RCISConversationalEntityResolution
    provenance: RCISIntelligenceAnswerProvenance

    def __post_init__(self) -> None:
        _require_non_empty_text(self.utterance, field_name="utterance")
        _validate_governed_boundaries(
            context=self.context,
            resolution=self.resolution,
            provenance=self.provenance,
        )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalAnswer:
    """Immutable generated answer envelope retaining governed provenance."""

    contract_version: str
    answer_text: str
    product_id: str
    variant_id: str | None
    provenance: RCISIntelligenceAnswerProvenance

    def __post_init__(self) -> None:
        if self.contract_version != RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION:
            raise ValueError("unsupported conversational-answer generation contract version")
        _require_non_empty_text(self.answer_text, field_name="answer_text")
        _require_non_empty_text(self.product_id, field_name="product_id")
        if self.variant_id is not None:
            _require_non_empty_text(self.variant_id, field_name="variant_id")
        if not isinstance(self.provenance, RCISIntelligenceAnswerProvenance):
            raise TypeError("provenance must be RCISIntelligenceAnswerProvenance")
        if self.product_id != self.provenance.resolved_product_id:
            raise ValueError("answer product does not match provenance")
        if self.variant_id != self.provenance.resolved_variant_id:
            raise ValueError("answer variant does not match provenance")


class RCISIntelligenceConversationalAnswerGenerator:
    """Invoke exactly one supplied renderer after governed-boundary validation."""

    def __init__(
        self,
        renderer: Callable[[RCISIntelligenceConversationalAnswerInput], str],
    ) -> None:
        if not callable(renderer):
            raise TypeError("renderer must be callable")
        self._renderer = renderer

    def generate(
        self,
        *,
        utterance: str,
        context: RCISIntelligenceContext,
        resolution: RCISConversationalEntityResolution,
        provenance: RCISIntelligenceAnswerProvenance,
    ) -> RCISIntelligenceConversationalAnswer:
        generation_input = RCISIntelligenceConversationalAnswerInput(
            utterance=utterance,
            context=context,
            resolution=resolution,
            provenance=provenance,
        )

        answer_text = self._renderer(generation_input)
        _require_non_empty_text(answer_text, field_name="renderer output")

        return RCISIntelligenceConversationalAnswer(
            contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION,
            answer_text=answer_text,
            product_id=resolution.product_id,
            variant_id=resolution.variant_id,
            provenance=provenance,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION",
    "RCISIntelligenceConversationalAnswer",
    "RCISIntelligenceConversationalAnswerGenerator",
    "RCISIntelligenceConversationalAnswerInput",
]
