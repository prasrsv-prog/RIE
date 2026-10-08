from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_conversational_retrieval import (
    RCISIntelligenceConversationalRetrievedRecord,
    RCISIntelligenceConversationalRetriever,
)
from rie.application.rcis_intelligence_retrieval_grounded_conversational_turn_execution import (
    RCISIntelligenceRetrievalGroundedConversationalTurnExecutor,
)
from rie.application.rcis_intelligence_retrieval_grounded_conversational_turn_integration import (
    RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator,
    RCISIntelligenceRetrievalGroundedResolvedEntity,
)


def _record() -> RCISIntelligenceConversationalRetrievedRecord:
    return RCISIntelligenceConversationalRetrievedRecord(
        record_id="knowledge-1",
        source_kind="product_knowledge",
        source_ref="knowledge:knowledge-1",
        product_id="product-a",
        variant_id=None,
        relevance_rank=0,
        payload={"statement": "authoritative"},
    )


def _integration(*, knowledge_gap: bool):
    resolved = RCISIntelligenceRetrievalGroundedResolvedEntity(
        resolution=object(),
        product_id="product-a",
        variant_id=None,
    )

    records = () if knowledge_gap else (_record(),)

    integrator = RCISIntelligenceRetrievalGroundedConversationalTurnIntegrator(
        entity_resolver=lambda utterance, prior_state: resolved,
        retriever=RCISIntelligenceConversationalRetriever(
            lambda request: records
        ),
        context_assembler=lambda *args: object(),
    )

    return integrator.prepare(
        user_utterance="Jelaskan Product A.",
        prior_session_state=object(),
    )


def test_successful_execution_orders_answer_then_session_once() -> None:
    events = []
    integration = _integration(knowledge_gap=False)
    prior_state = object()
    answer = object()
    next_state = object()

    def answer_generator(integration_result, prior_session_state):
        events.append(
            ("answer", integration_result, prior_session_state)
        )
        return answer

    def session_updater(
        prior_session_state,
        integration_result,
        governed_answer,
    ):
        events.append(
            (
                "session",
                prior_session_state,
                integration_result,
                governed_answer,
            )
        )
        return next_state

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=answer_generator,
        session_updater=session_updater,
    )

    result = executor.execute(
        integration_result=integration,
        prior_session_state=prior_state,
    )

    assert [event[0] for event in events] == ["answer", "session"]
    assert result.integration_result is integration
    assert result.prior_session_state is prior_state
    assert result.governed_answer is answer
    assert result.next_session_state is next_state
    assert result.knowledge_gap is False
    assert result.answer_generated is True
    assert result.session_updated is True


def test_knowledge_gap_blocks_answer_and_session_and_preserves_state() -> None:
    events = []
    integration = _integration(knowledge_gap=True)
    prior_state = object()

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: events.append("answer"),
        session_updater=lambda *args: events.append("session"),
    )

    result = executor.execute(
        integration_result=integration,
        prior_session_state=prior_state,
    )

    assert events == []
    assert result.governed_answer is None
    assert result.next_session_state is prior_state
    assert result.knowledge_gap is True
    assert result.answer_generated is False
    assert result.session_updated is False


def test_knowledge_gap_with_none_prior_state_remains_none() -> None:
    integration = _integration(knowledge_gap=True)

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: object(),
        session_updater=lambda *args: object(),
    )

    result = executor.execute(
        integration_result=integration,
        prior_session_state=None,
    )

    assert result.next_session_state is None
    assert result.governed_answer is None


def test_answer_generator_must_return_non_none() -> None:
    session_calls = []
    integration = _integration(knowledge_gap=False)

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: None,
        session_updater=lambda *args: session_calls.append(args),
    )

    with pytest.raises(
        ValueError,
        match="answer_generator must return governed answer",
    ):
        executor.execute(integration_result=integration)

    assert session_calls == []


def test_session_updater_must_return_non_none() -> None:
    integration = _integration(knowledge_gap=False)

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: object(),
        session_updater=lambda *args: None,
    )

    with pytest.raises(
        ValueError,
        match="session_updater must return bounded next session state",
    ):
        executor.execute(integration_result=integration)


def test_answer_failure_propagates_without_retry_or_session_update() -> None:
    answer_calls = []
    session_calls = []
    integration = _integration(knowledge_gap=False)

    def answer_generator(*args):
        answer_calls.append(args)
        raise RuntimeError("answer failure")

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=answer_generator,
        session_updater=lambda *args: session_calls.append(args),
    )

    with pytest.raises(RuntimeError, match="answer failure"):
        executor.execute(integration_result=integration)

    assert len(answer_calls) == 1
    assert session_calls == []


def test_session_failure_propagates_without_retry() -> None:
    session_calls = []
    integration = _integration(knowledge_gap=False)

    def session_updater(*args):
        session_calls.append(args)
        raise RuntimeError("session failure")

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: object(),
        session_updater=session_updater,
    )

    with pytest.raises(RuntimeError, match="session failure"):
        executor.execute(integration_result=integration)

    assert len(session_calls) == 1


def test_execution_result_is_immutable() -> None:
    integration = _integration(knowledge_gap=False)
    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: object(),
        session_updater=lambda *args: object(),
    )

    result = executor.execute(integration_result=integration)

    with pytest.raises(FrozenInstanceError):
        result.answer_generated = False  # type: ignore[misc]


def test_execute_rejects_non_integration_result_before_callbacks() -> None:
    events = []
    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: events.append("answer"),
        session_updater=lambda *args: events.append("session"),
    )

    with pytest.raises(
        TypeError,
        match="integration_result must be",
    ):
        executor.execute(
            integration_result=object(),  # type: ignore[arg-type]
        )

    assert events == []


def test_constructor_requires_callable_answer_generator() -> None:
    with pytest.raises(TypeError, match="answer_generator must be callable"):
        RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
            answer_generator=object(),  # type: ignore[arg-type]
            session_updater=lambda *args: object(),
        )


def test_constructor_requires_callable_session_updater() -> None:
    with pytest.raises(TypeError, match="session_updater must be callable"):
        RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
            answer_generator=lambda *args: object(),
            session_updater=object(),  # type: ignore[arg-type]
        )


def test_success_preserves_exact_integration_and_answer_objects() -> None:
    integration = _integration(knowledge_gap=False)
    answer = {"answer": "grounded"}
    next_state = {"turns": 1}

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: answer,
        session_updater=lambda *args: next_state,
    )

    result = executor.execute(integration_result=integration)

    assert result.integration_result is integration
    assert result.governed_answer is answer
    assert result.next_session_state is next_state


def test_answer_generator_receives_prior_state_exactly() -> None:
    integration = _integration(knowledge_gap=False)
    prior_state = object()
    seen = []

    def answer_generator(integration_result, received_prior):
        seen.append((integration_result, received_prior))
        return object()

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=answer_generator,
        session_updater=lambda *args: object(),
    )

    executor.execute(
        integration_result=integration,
        prior_session_state=prior_state,
    )

    assert seen == [(integration, prior_state)]


def test_session_updater_receives_generated_answer_exactly() -> None:
    integration = _integration(knowledge_gap=False)
    answer = object()
    seen = []

    def session_updater(prior_state, integration_result, governed_answer):
        seen.append((prior_state, integration_result, governed_answer))
        return object()

    executor = RCISIntelligenceRetrievalGroundedConversationalTurnExecutor(
        answer_generator=lambda *args: answer,
        session_updater=session_updater,
    )

    executor.execute(integration_result=integration)

    assert len(seen) == 1
    assert seen[0][1] is integration
    assert seen[0][2] is answer
