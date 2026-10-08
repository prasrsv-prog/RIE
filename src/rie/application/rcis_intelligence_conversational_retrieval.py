"""Bounded governed conversational retrieval contract for RCIS Intelligence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final


RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalRetrievalRequest:
    """Exact bounded retrieval request for one conversational turn."""

    contract_version: str
    user_utterance: str
    product_id: str
    variant_id: str | None
    max_records: int

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
        ):
            raise ValueError("unsupported conversational retrieval contract version")

        _require_non_empty_text(
            self.user_utterance,
            field_name="user_utterance",
        )
        _require_non_empty_text(self.product_id, field_name="product_id")

        if self.variant_id is not None:
            _require_non_empty_text(self.variant_id, field_name="variant_id")

        if isinstance(self.max_records, bool) or not isinstance(
            self.max_records,
            int,
        ):
            raise TypeError("max_records must be int")
        if self.max_records <= 0:
            raise ValueError("max_records must be positive")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalRetrievedRecord:
    """One exact authoritative record selected by the retrieval backend."""

    record_id: str
    source_kind: str
    source_ref: str
    product_id: str
    variant_id: str | None
    relevance_rank: int
    payload: object

    def __post_init__(self) -> None:
        _require_non_empty_text(self.record_id, field_name="record_id")
        _require_non_empty_text(self.source_kind, field_name="source_kind")
        _require_non_empty_text(self.source_ref, field_name="source_ref")
        _require_non_empty_text(self.product_id, field_name="product_id")

        if self.variant_id is not None:
            _require_non_empty_text(self.variant_id, field_name="variant_id")

        if isinstance(self.relevance_rank, bool) or not isinstance(
            self.relevance_rank,
            int,
        ):
            raise TypeError("relevance_rank must be int")
        if self.relevance_rank < 0:
            raise ValueError("relevance_rank must be non-negative")

        if self.payload is None:
            raise ValueError("payload must not be None")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalRetrievalResult:
    """Immutable retrieval result with explicit knowledge-gap state."""

    contract_version: str
    request: RCISIntelligenceConversationalRetrievalRequest
    records: tuple[RCISIntelligenceConversationalRetrievedRecord, ...]
    knowledge_gap: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
        ):
            raise ValueError("unsupported conversational retrieval contract version")

        if not isinstance(
            self.request,
            RCISIntelligenceConversationalRetrievalRequest,
        ):
            raise TypeError(
                "request must be RCISIntelligenceConversationalRetrievalRequest"
            )
        if not isinstance(self.records, tuple):
            raise TypeError("records must be tuple")
        if not isinstance(self.knowledge_gap, bool):
            raise TypeError("knowledge_gap must be bool")

        if len(self.records) > self.request.max_records:
            raise ValueError("retrieval result exceeds request max_records")

        seen_record_ids: set[str] = set()

        for expected_rank, record in enumerate(self.records):
            if not isinstance(
                record,
                RCISIntelligenceConversationalRetrievedRecord,
            ):
                raise TypeError(
                    "records must contain RCISIntelligenceConversationalRetrievedRecord"
                )

            if record.record_id in seen_record_ids:
                raise ValueError("duplicate retrieval record_id")
            seen_record_ids.add(record.record_id)

            if record.relevance_rank != expected_rank:
                raise ValueError(
                    "retrieval records must preserve consecutive relevance_rank order"
                )

            if record.product_id != self.request.product_id:
                raise ValueError("retrieved record product_id outside request scope")

            if self.request.variant_id is None:
                if record.variant_id is not None:
                    raise ValueError(
                        "product-only retrieval must not include variant-specific record"
                    )
            elif record.variant_id not in (None, self.request.variant_id):
                raise ValueError("retrieved record variant_id outside request scope")

        expected_gap = len(self.records) == 0
        if self.knowledge_gap is not expected_gap:
            raise ValueError("knowledge_gap must exactly reflect empty records")


class RCISIntelligenceConversationalRetriever:
    """Invoke one explicit authoritative retrieval backend exactly once."""

    def __init__(
        self,
        backend: Callable[
            [RCISIntelligenceConversationalRetrievalRequest],
            tuple[RCISIntelligenceConversationalRetrievedRecord, ...],
        ],
    ) -> None:
        if not callable(backend):
            raise TypeError("backend must be callable")
        self._backend = backend

    def retrieve(
        self,
        *,
        user_utterance: str,
        product_id: str,
        variant_id: str | None = None,
        max_records: int = 8,
    ) -> RCISIntelligenceConversationalRetrievalResult:
        request = RCISIntelligenceConversationalRetrievalRequest(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
            ),
            user_utterance=user_utterance,
            product_id=product_id,
            variant_id=variant_id,
            max_records=max_records,
        )

        records = self._backend(request)

        if not isinstance(records, tuple):
            raise TypeError("retrieval backend must return tuple")

        return RCISIntelligenceConversationalRetrievalResult(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
            ),
            request=request,
            records=records,
            knowledge_gap=len(records) == 0,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION",
    "RCISIntelligenceConversationalRetrievedRecord",
    "RCISIntelligenceConversationalRetrievalRequest",
    "RCISIntelligenceConversationalRetrievalResult",
    "RCISIntelligenceConversationalRetriever",
]
