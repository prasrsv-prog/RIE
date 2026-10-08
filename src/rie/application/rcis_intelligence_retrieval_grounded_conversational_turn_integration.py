"""Retrieval-grounded conversational turn integration for RCIS Intelligence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_conversational_retrieval import (
    RCISIntelligenceConversationalRetrievalResult,
    RCISIntelligenceConversationalRetriever,
)


RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_INTEGRATION_CONTRACT_VERSION: Final[
    str
] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceRetrievalGroundedResolvedEntity:
    """Exact entity scope plus the original published resolution object."""

    resolution: object
    product_id: str
    variant_id: str | None

    def __post_init__(self) -> None:
        if self.resolution is None:
            raise ValueError("resolution must not be None")

        _require_non_empty_text(self.product_id, field_name="product_id")

        if self.variant_id is not None:
            _require_non_empty_text(self.variant_id, field_name="variant_id")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceRetrievalGroundedTurnIntegrationResult:
    """Immutable output prepared before conversational answer generation."""

    contract_version: str
    user_utterance: str
    resolved_entity: RCISIntelligenceRetrievalGroundedResolvedEntity
    retrieval_result: RCISIntelligenceConversationalRetrievalResult
    governed_context: object | None
    knowledge_gap: bool
    answer_generation_allowed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_INTEGRATION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported retrieval-grounded turn integration contract version"
            )

        _require_non_empty_text(
            self.user_utterance,
            field_name="user_utterance",
        )

        if not isinstance(
            self.resolved_entity,
            RCISIntelligenceRetrievalGroundedResolvedEntity,
        ):
            raise TypeError(
                "resolved_entity must be "
                "RCISIntelligenceRetrievalGroundedResolvedEntity"
            )

        if not isinstance(
            self.retrieval_result,
            RCISIntelligenceConversationalRetrievalResult,
        ):
            raise TypeError(
                "retrieval_result must be "
                "RCISIntelligenceConversationalRetrievalResult"
            )

        if not isinstance(self.knowledge_gap, bool):
            raise TypeError("knowledge_gap must be bool")
        if not isinstance(self.answer_generation_allowed, bool):
            raise TypeError("answer_generation_allowed must be bool")

        request = self.retrieval_result.request

        if request.user_utterance != self.user_utterance:
            raise ValueError("retrieval utterance must match integration utterance")
        if request.product_id != self.resolved_entity.product_id:
            raise ValueError("retrieval product scope must match resolved entity")
        if request.variant_id != self.resolved_entity.variant_id:
            raise ValueError("retrieval variant scope must match resolved entity")

        if self.knowledge_gap is not self.retrieval_result.knowledge_gap:
            raise ValueError(
                "integration knowledge_gap must match retrieval knowledge_gap"
            )

        expected_allowed = not self.knowledge_gap
        if self.answer_generation_allowed is not expected_allowed:
            raise ValueError(
                "answer_generation_allowed must be the inverse of knowledge_gap"
            )

        if self.knowledge_gap:
            if self.governed_context is not None:
                raise ValueError(
                    "governed_context must be None when authoritative knowledge is absent"
                )
        elif self.governed_context is None:
            raise ValueError(
                "governed_context is required when answer generation is allowed"
            )


class RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator:
    """Resolve exact scope, retrieve authority, then assemble grounded context."""

    def __init__(
        self,
        *,
        entity_resolver: Callable[
            [str, object | None],
            RCISIntelligenceRetrievalGroundedResolvedEntity,
        ],
        retriever: RCISIntelligenceConversationalRetriever,
        context_assembler: Callable[
            [
                str,
                RCISIntelligenceRetrievalGroundedResolvedEntity,
                RCISIntelligenceConversationalRetrievalResult,
                object | None,
            ],
            object,
        ],
    ) -> None:
        if not callable(entity_resolver):
            raise TypeError("entity_resolver must be callable")
        if not isinstance(
            retriever,
            RCISIntelligenceConversationalRetriever,
        ):
            raise TypeError(
                "retriever must be RCISIntelligenceConversationalRetriever"
            )
        if not callable(context_assembler):
            raise TypeError("context_assembler must be callable")

        self._entity_resolver = entity_resolver
        self._retriever = retriever
        self._context_assembler = context_assembler

    def prepare(
        self,
        *,
        user_utterance: str,
        prior_session_state: object | None = None,
        max_records: int = 8,
    ) -> RCISIntelligenceRetrievalGroundedTurnIntegrationResult:
        _require_non_empty_text(
            user_utterance,
            field_name="user_utterance",
        )

        if isinstance(max_records, bool) or not isinstance(max_records, int):
            raise TypeError("max_records must be int")
        if max_records <= 0:
            raise ValueError("max_records must be positive")

        resolved_entity = self._entity_resolver(
            user_utterance,
            prior_session_state,
        )

        if not isinstance(
            resolved_entity,
            RCISIntelligenceRetrievalGroundedResolvedEntity,
        ):
            raise TypeError(
                "entity_resolver must return "
                "RCISIntelligenceRetrievalGroundedResolvedEntity"
            )

        retrieval_result = self._retriever.retrieve(
            user_utterance=user_utterance,
            product_id=resolved_entity.product_id,
            variant_id=resolved_entity.variant_id,
            max_records=max_records,
        )

        if retrieval_result.knowledge_gap:
            return RCISIntelligenceRetrievalGroundedTurnIntegrationResult(
                contract_version=(
                    RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_INTEGRATION_CONTRACT_VERSION
                ),
                user_utterance=user_utterance,
                resolved_entity=resolved_entity,
                retrieval_result=retrieval_result,
                governed_context=None,
                knowledge_gap=True,
                answer_generation_allowed=False,
            )

        governed_context = self._context_assembler(
            user_utterance,
            resolved_entity,
            retrieval_result,
            prior_session_state,
        )

        if governed_context is None:
            raise ValueError(
                "context_assembler must return governed context when knowledge exists"
            )

        return RCISIntelligenceRetrievalGroundedTurnIntegrationResult(
            contract_version=(
                RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_INTEGRATION_CONTRACT_VERSION
            ),
            user_utterance=user_utterance,
            resolved_entity=resolved_entity,
            retrieval_result=retrieval_result,
            governed_context=governed_context,
            knowledge_gap=False,
            answer_generation_allowed=True,
        )


__all__ = [
    "RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_INTEGRATION_CONTRACT_VERSION",
    "RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator",
    "RCISIntelligenceRetrievalGroundedResolvedEntity",
    "RCISIntelligenceRetrievalGroundedTurnIntegrationResult",
]
