from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCISIntelligenceConversationalAnswerGenerator,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
)
from rie.application.rcis_intelligence_conversational_session_state import (
    RCISIntelligenceConversationalSessionStateManager,
)
from rie.application.rcis_intelligence_conversational_turn_orchestration import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION,
    RCISIntelligenceConversationalTurnOrchestrator,
)


def _context() -> RCISIntelligenceContext:
    return RCISIntelligenceContext(
        contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        product_context=object(),
        visual_reference_assets=(),
        source_boundaries=RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    )


def _resolution(
    *,
    variant_id: str | None = "sv300-white-glossy",
    basis: RCISConversationalEntityResolutionBasis = RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID,
    status: RCISConversationalEntityResolutionStatus = RCISConversationalEntityResolutionStatus.RESOLVED,
) -> RCISConversationalEntityResolution:
    return RCISConversationalEntityResolution(
        contract_version=(
            RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION
        ),
        status=status,
        product_id=(
            "sv300"
            if status is RCISConversationalEntityResolutionStatus.RESOLVED
            else None
        ),
        variant_id=(
            variant_id
            if status is RCISConversationalEntityResolutionStatus.RESOLVED
            else None
        ),
        resolution_basis=basis,
    )


def _system(
    *,
    resolver,
    max_turns: int = 3,
    rendered_text: str = "Governed answer.",
):
    renderer_calls = []

    def renderer(answer_input):
        renderer_calls.append(answer_input)
        return rendered_text

    answer_generator = RCISIntelligenceConversationalAnswerGenerator(renderer)
    session_manager = RCISIntelligenceConversationalSessionStateManager(
        max_turns=max_turns
    )
    orchestrator = RCISIntelligenceConversationalTurnOrchestrator(
        resolver=resolver,
        answer_generator=answer_generator,
        session_manager=session_manager,
    )
    return orchestrator, session_manager, renderer_calls


def test_execute_composes_exactly_one_governed_turn() -> None:
    resolver_calls = []
    resolution = _resolution()

    def resolver(utterance, context, session_state):
        resolver_calls.append((utterance, context, session_state))
        return resolution

    orchestrator, session_manager, renderer_calls = _system(
        resolver=resolver
    )
    state = session_manager.start(session_id="session-1")
    context = _context()

    result = orchestrator.execute(
        user_utterance="Explain this variant.",
        context=context,
        session_state=state,
    )

    assert result.contract_version == (
        RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION
    )
    assert result.user_utterance == "Explain this variant."
    assert result.resolution is resolution
    assert result.answer.answer_text == "Governed answer."
    assert result.session_state is not state
    assert len(result.session_state.turns) == 1
    assert result.session_state.turns[-1].resolution is resolution
    assert result.session_state.turns[-1].answer is result.answer
    assert len(resolver_calls) == 1
    assert resolver_calls[0] == (
        "Explain this variant.",
        context,
        state,
    )
    assert len(renderer_calls) == 1


def test_previous_session_snapshot_is_unchanged() -> None:
    resolution = _resolution()
    orchestrator, session_manager, _ = _system(
        resolver=lambda utterance, context, session_state: resolution
    )
    state = session_manager.start(session_id="session-1")

    result = orchestrator.execute(
        user_utterance="Explain this variant.",
        context=_context(),
        session_state=state,
    )

    assert state.turns == ()
    assert state.current_product_id is None
    assert state.current_variant_id is None
    assert result.session_state.turns != ()


def test_second_turn_receives_prior_session_and_advances_absolute_index() -> None:
    observed_states = []
    resolution = _resolution()

    def resolver(utterance, context, session_state):
        observed_states.append(session_state)
        return resolution

    orchestrator, session_manager, _ = _system(
        resolver=resolver,
        max_turns=2,
    )
    state0 = session_manager.start(session_id="session-1")

    first = orchestrator.execute(
        user_utterance="First question.",
        context=_context(),
        session_state=state0,
    )
    second = orchestrator.execute(
        user_utterance="Second question.",
        context=_context(),
        session_state=first.session_state,
    )

    assert observed_states == [state0, first.session_state]
    assert [turn.turn_index for turn in second.session_state.turns] == [0, 1]


def test_product_only_resolution_remains_product_only() -> None:
    resolution = _resolution(
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
    )
    orchestrator, session_manager, _ = _system(
        resolver=lambda utterance, context, session_state: resolution
    )

    result = orchestrator.execute(
        user_utterance="Tell me about sv300.",
        context=_context(),
        session_state=session_manager.start(session_id="session-1"),
    )

    assert result.resolution.variant_id is None
    assert result.answer.variant_id is None
    assert result.session_state.current_variant_id is None


def test_result_is_immutable() -> None:
    resolution = _resolution()
    orchestrator, session_manager, _ = _system(
        resolver=lambda utterance, context, session_state: resolution
    )
    result = orchestrator.execute(
        user_utterance="Explain this variant.",
        context=_context(),
        session_state=session_manager.start(session_id="session-1"),
    )

    with pytest.raises(FrozenInstanceError):
        result.user_utterance = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_rejected_before_resolver(utterance: str) -> None:
    resolver_calls = []

    def resolver(user_utterance, context, session_state):
        resolver_calls.append(user_utterance)
        return _resolution()

    orchestrator, session_manager, renderer_calls = _system(
        resolver=resolver
    )

    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        orchestrator.execute(
            user_utterance=utterance,
            context=_context(),
            session_state=session_manager.start(session_id="session-1"),
        )

    assert resolver_calls == []
    assert renderer_calls == []


def test_non_context_rejected_before_resolver() -> None:
    resolver_calls = []

    def resolver(user_utterance, context, session_state):
        resolver_calls.append(user_utterance)
        return _resolution()

    orchestrator, session_manager, renderer_calls = _system(
        resolver=resolver
    )

    with pytest.raises(TypeError, match="context must be RCISIntelligenceContext"):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=object(),  # type: ignore[arg-type]
            session_state=session_manager.start(session_id="session-1"),
        )

    assert resolver_calls == []
    assert renderer_calls == []


def test_non_session_state_rejected_before_resolver() -> None:
    resolver_calls = []

    def resolver(user_utterance, context, session_state):
        resolver_calls.append(user_utterance)
        return _resolution()

    orchestrator, _, renderer_calls = _system(resolver=resolver)

    with pytest.raises(
        TypeError,
        match="session_state must be RCISIntelligenceConversationalSessionState",
    ):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=_context(),
            session_state=object(),  # type: ignore[arg-type]
        )

    assert resolver_calls == []
    assert renderer_calls == []


def test_session_bound_mismatch_rejected_before_resolver() -> None:
    resolver_calls = []

    def resolver(user_utterance, context, session_state):
        resolver_calls.append(user_utterance)
        return _resolution()

    orchestrator, _, renderer_calls = _system(
        resolver=resolver,
        max_turns=3,
    )
    other_manager = RCISIntelligenceConversationalSessionStateManager(
        max_turns=2
    )

    with pytest.raises(
        ValueError,
        match="session_state max_turns does not match session_manager max_turns",
    ):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=_context(),
            session_state=other_manager.start(session_id="session-1"),
        )

    assert resolver_calls == []
    assert renderer_calls == []


def test_resolver_must_be_callable() -> None:
    answer_generator = RCISIntelligenceConversationalAnswerGenerator(
        lambda answer_input: "answer"
    )
    session_manager = RCISIntelligenceConversationalSessionStateManager(
        max_turns=2
    )

    with pytest.raises(TypeError, match="resolver must be callable"):
        RCISIntelligenceConversationalTurnOrchestrator(
            resolver=None,  # type: ignore[arg-type]
            answer_generator=answer_generator,
            session_manager=session_manager,
        )


def test_resolver_must_return_exact_governed_resolution_type() -> None:
    orchestrator, session_manager, renderer_calls = _system(
        resolver=lambda utterance, context, session_state: object()
    )

    with pytest.raises(
        TypeError,
        match="resolver must return RCISConversationalEntityResolution",
    ):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=_context(),
            session_state=session_manager.start(session_id="session-1"),
        )

    assert renderer_calls == []


def test_unresolved_result_stops_before_answer_generation() -> None:
    unresolved = _resolution(
        status=RCISConversationalEntityResolutionStatus.UNRESOLVED,
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE,
    )
    orchestrator, session_manager, renderer_calls = _system(
        resolver=lambda utterance, context, session_state: unresolved
    )

    state = session_manager.start(session_id="session-1")
    with pytest.raises(ValueError, match="resolver result must be RESOLVED"):
        orchestrator.execute(
            user_utterance="What about it?",
            context=_context(),
            session_state=state,
        )

    assert renderer_calls == []
    assert state.turns == ()


def test_resolver_exception_propagates_without_retry_or_session_mutation() -> None:
    resolver_calls = []

    def resolver(utterance, context, session_state):
        resolver_calls.append(utterance)
        raise RuntimeError("resolver failure")

    orchestrator, session_manager, renderer_calls = _system(
        resolver=resolver
    )
    state = session_manager.start(session_id="session-1")

    with pytest.raises(RuntimeError, match="resolver failure"):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=_context(),
            session_state=state,
        )

    assert resolver_calls == ["Explain this."]
    assert renderer_calls == []
    assert state.turns == ()


def test_answer_renderer_exception_propagates_without_session_append() -> None:
    resolution = _resolution()

    def renderer(answer_input):
        raise RuntimeError("renderer failure")

    answer_generator = RCISIntelligenceConversationalAnswerGenerator(renderer)
    session_manager = RCISIntelligenceConversationalSessionStateManager(
        max_turns=2
    )
    orchestrator = RCISIntelligenceConversationalTurnOrchestrator(
        resolver=lambda utterance, context, session_state: resolution,
        answer_generator=answer_generator,
        session_manager=session_manager,
    )
    state = session_manager.start(session_id="session-1")

    with pytest.raises(RuntimeError, match="renderer failure"):
        orchestrator.execute(
            user_utterance="Explain this.",
            context=_context(),
            session_state=state,
        )

    assert state.turns == ()
