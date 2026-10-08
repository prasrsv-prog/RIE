from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_conversational_retrieval import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION,
    RCISIntelligenceConversationalRetrievedRecord,
    RCISIntelligenceConversationalRetrievalRequest,
    RCISIntelligenceConversationalRetrievalResult,
    RCISIntelligenceConversationalRetriever,
)


def _record(
    *,
    record_id: str,
    rank: int,
    product_id: str = "product-a",
    variant_id: str | None = None,
    payload: object | None = None,
) -> RCISIntelligenceConversationalRetrievedRecord:
    return RCISIntelligenceConversationalRetrievedRecord(
        record_id=record_id,
        source_kind="product_knowledge",
        source_ref=f"knowledge:{record_id}",
        product_id=product_id,
        variant_id=variant_id,
        relevance_rank=rank,
        payload=payload if payload is not None else object(),
    )


def test_retrieve_invokes_backend_once_and_preserves_exact_order() -> None:
    calls = []
    records = (
        _record(record_id="k1", rank=0),
        _record(record_id="k2", rank=1),
    )

    def backend(request):
        calls.append(request)
        return records

    retriever = RCISIntelligenceConversationalRetriever(backend)
    result = retriever.retrieve(
        user_utterance="Apa keunggulan Product A?",
        product_id="product-a",
        max_records=4,
    )

    assert len(calls) == 1
    assert calls[0] is result.request
    assert result.records is records
    assert result.knowledge_gap is False
    assert [record.record_id for record in result.records] == ["k1", "k2"]


def test_variant_retrieval_accepts_product_and_matching_variant_records() -> None:
    records = (
        _record(record_id="product", rank=0),
        _record(
            record_id="variant",
            rank=1,
            variant_id="variant-black",
        ),
    )
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: records
    )

    result = retriever.retrieve(
        user_utterance="Bagaimana variant hitam?",
        product_id="product-a",
        variant_id="variant-black",
    )

    assert result.records == records
    assert result.request.variant_id == "variant-black"


def test_product_only_retrieval_rejects_variant_specific_record() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(
                record_id="variant",
                rank=0,
                variant_id="variant-black",
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="product-only retrieval must not include variant-specific record",
    ):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )


def test_wrong_product_scope_is_rejected() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(
                record_id="wrong-product",
                rank=0,
                product_id="product-b",
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="retrieved record product_id outside request scope",
    ):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )


def test_wrong_variant_scope_is_rejected() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(
                record_id="wrong-variant",
                rank=0,
                variant_id="variant-red",
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="retrieved record variant_id outside request scope",
    ):
        retriever.retrieve(
            user_utterance="Jelaskan variant hitam.",
            product_id="product-a",
            variant_id="variant-black",
        )


def test_empty_result_sets_explicit_knowledge_gap() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: ()
    )

    result = retriever.retrieve(
        user_utterance="Apakah produk ini waterproof?",
        product_id="product-a",
    )

    assert result.records == ()
    assert result.knowledge_gap is True


def test_backend_must_return_tuple() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: []
    )

    with pytest.raises(TypeError, match="retrieval backend must return tuple"):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )


def test_result_rejects_more_records_than_maximum() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(record_id="k1", rank=0),
            _record(record_id="k2", rank=1),
        )
    )

    with pytest.raises(
        ValueError,
        match="retrieval result exceeds request max_records",
    ):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
            max_records=1,
        )


def test_result_requires_consecutive_rank_order() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(record_id="k1", rank=1),
        )
    )

    with pytest.raises(
        ValueError,
        match="consecutive relevance_rank order",
    ):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )


def test_result_rejects_duplicate_record_ids() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: (
            _record(record_id="same", rank=0),
            _record(record_id="same", rank=1),
        )
    )

    with pytest.raises(ValueError, match="duplicate retrieval record_id"):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )


def test_backend_exception_propagates_without_retry() -> None:
    calls = []

    def backend(request):
        calls.append(request)
        raise RuntimeError("retrieval failure")

    retriever = RCISIntelligenceConversationalRetriever(backend)

    with pytest.raises(RuntimeError, match="retrieval failure"):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
        )

    assert len(calls) == 1


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_rejected_before_backend(utterance: str) -> None:
    calls = []

    def backend(request):
        calls.append(request)
        return ()

    retriever = RCISIntelligenceConversationalRetriever(backend)

    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        retriever.retrieve(
            user_utterance=utterance,
            product_id="product-a",
        )

    assert calls == []


@pytest.mark.parametrize("max_records", [0, -1])
def test_non_positive_max_records_rejected(max_records: int) -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: ()
    )

    with pytest.raises(ValueError, match="max_records must be positive"):
        retriever.retrieve(
            user_utterance="Jelaskan Product A.",
            product_id="product-a",
            max_records=max_records,
        )


def test_request_and_result_are_immutable() -> None:
    retriever = RCISIntelligenceConversationalRetriever(
        lambda request: ()
    )
    result = retriever.retrieve(
        user_utterance="Jelaskan Product A.",
        product_id="product-a",
    )

    with pytest.raises(FrozenInstanceError):
        result.request.product_id = "changed"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.knowledge_gap = False  # type: ignore[misc]


def test_manual_result_must_match_knowledge_gap_to_empty_records() -> None:
    request = RCISIntelligenceConversationalRetrievalRequest(
        contract_version=(
            RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
        ),
        user_utterance="Jelaskan Product A.",
        product_id="product-a",
        variant_id=None,
        max_records=8,
    )

    with pytest.raises(
        ValueError,
        match="knowledge_gap must exactly reflect empty records",
    ):
        RCISIntelligenceConversationalRetrievalResult(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_RETRIEVAL_CONTRACT_VERSION
            ),
            request=request,
            records=(),
            knowledge_gap=False,
        )
