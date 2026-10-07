"""Minimum governed answer-provenance contract for RCIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_context_assembly import RCISIntelligenceContext
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
)


RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_identifier(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceAnswerProvenance:
    """Immutable provenance envelope for a future RCIS intelligence answer."""

    contract_version: str
    context_contract_version: str
    entity_resolution_contract_version: str
    context_product_id: str
    context_variant_id: str
    resolved_product_id: str
    resolved_variant_id: str | None
    resolution_basis: RCISConversationalEntityResolutionBasis
    context_source_boundaries: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.contract_version != RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION:
            raise ValueError("unsupported answer-provenance contract version")
        _require_identifier(self.context_contract_version, field_name="context_contract_version")
        _require_identifier(
            self.entity_resolution_contract_version,
            field_name="entity_resolution_contract_version",
        )
        _require_identifier(self.context_product_id, field_name="context_product_id")
        _require_identifier(self.context_variant_id, field_name="context_variant_id")
        _require_identifier(self.resolved_product_id, field_name="resolved_product_id")
        if self.resolved_variant_id is not None:
            _require_identifier(self.resolved_variant_id, field_name="resolved_variant_id")
        if self.resolved_product_id != self.context_product_id:
            raise ValueError("resolved product must match governed context product")
        if (
            self.resolved_variant_id is not None
            and self.resolved_variant_id != self.context_variant_id
        ):
            raise ValueError("resolved variant must match governed context variant")
        if not isinstance(self.resolution_basis, RCISConversationalEntityResolutionBasis):
            raise TypeError("resolution_basis must be RCISConversationalEntityResolutionBasis")
        if not isinstance(self.context_source_boundaries, tuple):
            raise TypeError("context_source_boundaries must be tuple")
        if not self.context_source_boundaries:
            raise ValueError("context_source_boundaries must not be empty")
        if any(
            not isinstance(boundary, str) or not boundary.strip()
            for boundary in self.context_source_boundaries
        ):
            raise ValueError("context_source_boundaries must contain non-empty strings")


class RCISIntelligenceAnswerProvenanceBuilder:
    """Bind a resolved governed referent to the exact governed context envelope."""

    def build(
        self,
        *,
        context: RCISIntelligenceContext,
        resolution: RCISConversationalEntityResolution,
    ) -> RCISIntelligenceAnswerProvenance:
        if not isinstance(context, RCISIntelligenceContext):
            raise TypeError("context must be RCISIntelligenceContext")
        if not isinstance(resolution, RCISConversationalEntityResolution):
            raise TypeError("resolution must be RCISConversationalEntityResolution")
        if resolution.status is not RCISConversationalEntityResolutionStatus.RESOLVED:
            raise ValueError("resolution must be RESOLVED before provenance can be built")
        if resolution.product_id != context.product_id:
            raise ValueError("resolved product does not match governed context")
        if (
            resolution.variant_id is not None
            and resolution.variant_id != context.variant_id
        ):
            raise ValueError("resolved variant does not match governed context")

        return RCISIntelligenceAnswerProvenance(
            contract_version=RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION,
            context_contract_version=context.contract_version,
            entity_resolution_contract_version=resolution.contract_version,
            context_product_id=context.product_id,
            context_variant_id=context.variant_id,
            resolved_product_id=resolution.product_id,
            resolved_variant_id=resolution.variant_id,
            resolution_basis=resolution.resolution_basis,
            context_source_boundaries=context.source_boundaries,
        )


__all__ = [
    "RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION",
    "RCISIntelligenceAnswerProvenance",
    "RCISIntelligenceAnswerProvenanceBuilder",
]
