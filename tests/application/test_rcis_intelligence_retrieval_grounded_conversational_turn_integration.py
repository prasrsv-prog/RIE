from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_conversational_retrieval import (
    RCISIntelligenceConversationalRetrievedRecord,
    RCISIntelligenceConversationalRetriever,
)
from rie.application.rcis_intelligence_retrieval_grounded_conversational_turn_integration import (
    RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator,
    RCISIntelligenceRetrievalGroundedResolvedEntity,
)


def _record(
    *,
    record_id: str = "knowledge-1",
    product_id: str = "product-a",
    variant_id: str | None = None,
    rank: int = 0,
) -> RCISIntelligenceConversationalRetrievedRecord:
    return RCISIntelligenceConversationalRetrievedRecord(
        record_id=record_id,
        source_kind="product_knowledge",
        source_ref=f"knowledge:{record_id}",
        product_id=product_id,
        variant_id=variant_id,
        relevance_rank=rank,
        payload={"statement": "authoritative"},
    )


def _resolved(
    *,
    resolution: object | None = None,
    product_id: str = "product-a",
    variant_id: str | None = None,
) -> RCISIntelligenceRetrievalGroundedResolvedEntity:
    return RCISIntelligenceRetrievalGroundedResolvedEntity(
        resolution=resolution if resolution is not None else object(),
        product_id=product_id,
        variant_id=variant_id,
    )


def test_prepare_orders_resolve_retrieve_assemble_once() -> None:
    events = []
    resolution_object = object()
    resolved = _resolved(resolution=resolution_object)
    governed_context = object()

    def resolver(utterance, prior_state):
        events.append(("resolve", utterance, prior_state))
        return resolved

    def backend(request):
        events.append(
            (
                "retrieve",
                request.user_utterance,
                request.product_id,
                request.variant_id,
            )
        )
        return (_record(),)

    retriever = RCISIntelligenceConversationalRetriever(backend)

    def assembler(utterance, resolved_entity, retrieval_result, prior_state):
        events.append(
            (
                "assemble",
                utterance,
                resolved_entity,
                retrieval_result,
                prior_state,
            )
        )
        return governed_context

    prior_state = object()
    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=resolver,
        retriever=retriever,
        context_assembler=assembler,
    )

    result = integrator.prepare(
        user_utterance="Apa keunggulan Product A?",
        prior_session_state=prior_state,
        max_records=4,
    )

    assert [event[0] for event in events] == [
        "resolve",
        "retrieve",
        "assemble",
    ]
    assert result.resolved_entity is resolved
    assert result.resolved_entity.resolution is resolution_object
    assert result.governed_context is governed_context
    assert result.knowledge_gap is False
    assert result.answer_generation_allowed is True
    assert result.retrieval_result.request.max_records == 4


def test_exact_variant_scope_flows_from_resolution_into_retrieval() -> None:
    requests = []
    resolved = _resolved(variant_id="variant-black")

    def backend(request):
        requests.append(request)
        return (
            _record(record_id="product", rank=0),
            _record(
                record_id="variant",
                variant_id="variant-black",
                rank=1,
            ),
        )

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: resolved,
        retriever=RCISIntelligenceConversationalRetriever(backend),
        context_assembler=lambda *args: object(),
    )

    result = integrator.prepare(
        user_utterance="Bagaimana variant hitam?",
    )

    assert len(requests) == 1
    assert requests[0].product_id == "product-a"
    assert requests[0].variant_id == "variant-black"
    assert result.retrieval_result.request.variant_id == "variant-black"


def test_knowledge_gap_blocks_context_assembly_and_answer_generation() -> None:
    assembler_calls = []

    def assembler(*args):
        assembler_calls.append(args)
        return object()

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: _resolved(),
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: ()
        ),
        context_assembler=assembler,
    )

    result = integrator.prepare(
        user_utterance="Apakah Product A waterproof?",
    )

    assert assembler_calls == []
    assert result.retrieval_result.records == ()
    assert result.knowledge_gap is True
    assert result.answer_generation_allowed is False
    assert result.governed_context is None


def test_context_assembler_cannot_return_none_when_knowledge_exists() -> None:
    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: _resolved(),
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: (_record(),)
        ),
        context_assembler=lambda *args: None,
    )

    with pytest.raises(
        ValueError,
        match="context_assembler must return governed context",
    ):
        integrator.prepare(
            user_utterance="Jelaskan Product A.",
        )


def test_entity_resolver_must_return_exact_bridge_type() -> None:
    backend_calls = []

    def backend(request):
        backend_calls.append(request)
        return ()

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: object(),
        retriever=RCISIntelligenceConversationalRetriever(backend),
        context_assembler=lambda *args: object(),
    )

    with pytest.raises(
        TypeError,
        match="entity_resolver must return",
    ):
        integrator.prepare(
            user_utterance="Jelaskan Product A.",
        )

    assert backend_calls == []


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_rejected_before_any_component_call(
    utterance: str,
) -> None:
    events = []

    def resolver(user_utterance, prior_state):
        events.append("resolve")
        return _resolved()

    def backend(request):
        events.append("retrieve")
        return ()

    def assembler(*args):
        events.append("assemble")
        return object()

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=resolver,
        retriever=RCISIntelligenceConversationalRetriever(backend),
        context_assembler=assembler,
    )

    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        integrator.prepare(user_utterance=utterance)

    assert events == []


@pytest.mark.parametrize("max_records", [0, -1])
def test_non_positive_max_records_rejected_before_resolution(
    max_records: int,
) -> None:
    resolver_calls = []

    def resolver(utterance, prior_state):
        resolver_calls.append(utterance)
        return _resolved()

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=resolver,
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: ()
        ),
        context_assembler=lambda *args: object(),
    )

    with pytest.raises(ValueError, match="max_records must be positive"):
        integrator.prepare(
            user_utterance="Jelaskan Product A.",
            max_records=max_records,
        )

    assert resolver_calls == []


def test_resolver_failure_propagates_without_retry() -> None:
    calls = []

    def resolver(utterance, prior_state):
        calls.append(utterance)
        raise RuntimeError("resolution failure")

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=resolver,
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: ()
        ),
        context_assembler=lambda *args: object(),
    )

    with pytest.raises(RuntimeError, match="resolution failure"):
        integrator.prepare(user_utterance="Jelaskan Product A.")

    assert len(calls) == 1


def test_retrieval_failure_propagates_without_retry_or_assembly() -> None:
    backend_calls = []
    assembler_calls = []

    def backend(request):
        backend_calls.append(request)
        raise RuntimeError("retrieval failure")

    def assembler(*args):
        assembler_calls.append(args)
        return object()

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: _resolved(),
        retriever=RCISIntelligenceConversationalRetriever(backend),
        context_assembler=assembler,
    )

    with pytest.raises(RuntimeError, match="retrieval failure"):
        integrator.prepare(user_utterance="Jelaskan Product A.")

    assert len(backend_calls) == 1
    assert assembler_calls == []


def test_context_assembler_failure_propagates_without_retry() -> None:
    calls = []

    def assembler(*args):
        calls.append(args)
        raise RuntimeError("assembly failure")

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: _resolved(),
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: (_record(),)
        ),
        context_assembler=assembler,
    )

    with pytest.raises(RuntimeError, match="assembly failure"):
        integrator.prepare(user_utterance="Jelaskan Product A.")

    assert len(calls) == 1


def test_resolved_entity_and_result_are_immutable() -> None:
    resolved = _resolved()
    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: resolved,
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: ()
        ),
        context_assembler=lambda *args: object(),
    )

    result = integrator.prepare(user_utterance="Jelaskan Product A.")

    with pytest.raises(FrozenInstanceError):
        resolved.product_id = "changed"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.knowledge_gap = False  # type: ignore[misc]


def test_resolved_entity_rejects_blank_variant() -> None:
    with pytest.raises(ValueError, match="variant_id must not be empty"):
        _resolved(variant_id=" ")


def test_constructor_requires_published_retriever_type() -> None:
    with pytest.raises(
        TypeError,
        match="retriever must be RCISIntelligenceConversationalRetriever",
    ):
        RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
            entity_resolver=lambda utterance, prior_state: _resolved(),
            retriever=object(),  # type: ignore[arg-type]
            context_assembler=lambda *args: object(),
        )
