"""Minimum governed conversational entity-resolution contract for RCIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Final

from rie.application.rcis_intelligence_context_assembly import RCISIntelligenceContext


RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION: Final[str] = "1.0.0"


class RCISConversationalEntityResolutionStatus(str, Enum):
    """Outcome of resolving a conversational referent against governed context."""

    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"


class RCISConversationalEntityResolutionBasis(str, Enum):
    """Deterministic basis for a governed conversational resolution."""

    EXACT_PRODUCT_ID = "EXACT_PRODUCT_ID"
    EXACT_VARIANT_ID = "EXACT_VARIANT_ID"
    EXACT_PRODUCT_AND_VARIANT_ID = "EXACT_PRODUCT_AND_VARIANT_ID"
    CURRENT_PRODUCT_DEICTIC = "CURRENT_PRODUCT_DEICTIC"
    CURRENT_VARIANT_DEICTIC = "CURRENT_VARIANT_DEICTIC"
    NO_GROUNDED_REFERENCE = "NO_GROUNDED_REFERENCE"


@dataclass(frozen=True, slots=True)
class RCISConversationalEntityResolution:
    """Immutable result of resolving a conversational referent."""

    contract_version: str
    status: RCISConversationalEntityResolutionStatus
    product_id: str | None
    variant_id: str | None
    resolution_basis: RCISConversationalEntityResolutionBasis

    def __post_init__(self) -> None:
        if self.contract_version != RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION:
            raise ValueError("unsupported conversational entity-resolution contract version")
        if self.status is RCISConversationalEntityResolutionStatus.RESOLVED:
            if self.product_id is None:
                raise ValueError("resolved entity must include product_id")
        elif self.product_id is not None or self.variant_id is not None:
            raise ValueError("unresolved entity must not expose governed identifiers")


_PRODUCT_DEICTIC = re.compile(r"\b(?:this|current)\s+product\b", re.IGNORECASE)
_VARIANT_DEICTIC = re.compile(r"\b(?:this|current)\s+variant\b", re.IGNORECASE)


def _contains_exact_identifier(utterance: str, identifier: str) -> bool:
    pattern = re.compile(
        rf"(?<![A-Za-z0-9_-]){re.escape(identifier)}(?![A-Za-z0-9_-])"
    )
    return pattern.search(utterance) is not None


class RCISConversationalEntityResolver:
    """Resolve only referents provable from the supplied governed RCIS context."""

    def resolve(
        self,
        *,
        utterance: str,
        context: RCISIntelligenceContext,
    ) -> RCISConversationalEntityResolution:
        if not isinstance(utterance, str):
            raise TypeError("utterance must be str")
        if not utterance.strip():
            raise ValueError("utterance must not be empty")
        if not isinstance(context, RCISIntelligenceContext):
            raise TypeError("context must be RCISIntelligenceContext")

        product_id = context.product_id
        variant_id = context.variant_id
        product_exact = _contains_exact_identifier(utterance, product_id)
        variant_exact = _contains_exact_identifier(utterance, variant_id)

        if product_exact and variant_exact:
            return self._resolved(
                product_id=product_id,
                variant_id=variant_id,
                basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_AND_VARIANT_ID,
            )

        if variant_exact:
            return self._resolved(
                product_id=product_id,
                variant_id=variant_id,
                basis=RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID,
            )

        if _VARIANT_DEICTIC.search(utterance):
            return self._resolved(
                product_id=product_id,
                variant_id=variant_id,
                basis=RCISConversationalEntityResolutionBasis.CURRENT_VARIANT_DEICTIC,
            )

        if product_exact:
            return self._resolved(
                product_id=product_id,
                variant_id=None,
                basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
            )

        if _PRODUCT_DEICTIC.search(utterance):
            return self._resolved(
                product_id=product_id,
                variant_id=None,
                basis=RCISConversationalEntityResolutionBasis.CURRENT_PRODUCT_DEICTIC,
            )

        return RCISConversationalEntityResolution(
            contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
            status=RCISConversationalEntityResolutionStatus.UNRESOLVED,
            product_id=None,
            variant_id=None,
            resolution_basis=RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE,
        )

    @staticmethod
    def _resolved(
        *,
        product_id: str,
        variant_id: str | None,
        basis: RCISConversationalEntityResolutionBasis,
    ) -> RCISConversationalEntityResolution:
        return RCISConversationalEntityResolution(
            contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
            status=RCISConversationalEntityResolutionStatus.RESOLVED,
            product_id=product_id,
            variant_id=variant_id,
            resolution_basis=basis,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION",
    "RCISConversationalEntityResolution",
    "RCISConversationalEntityResolutionBasis",
    "RCISConversationalEntityResolutionStatus",
    "RCISConversationalEntityResolver",
]
