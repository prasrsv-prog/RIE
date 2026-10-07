from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_answer_provenance import (
    RCISIntelligenceAnswerProvenanceBuilder,
)
from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION,
    RCISIntelligenceConversationalAnswer,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
)
from rie.application.rcis_intelligence_conversational_session_state import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION,
    RCISIntelligenceConversationalSessionState,
    RCISIntelligenceConversationalSessionStateManager,
    RCISIntelligenceConversationalSessionTurn,
)


def _context(
    *,
    product_id: str = "sv300",
    variant_id: str = "sv300-white-glossy",
) -> RCISIntelligenceContext:
    return RCISIntelligenceContext(
        contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
        product_id=product_id,
        variant_id=variant_id,
        product_context=object(),
        visual_reference_assets=(),
        source_boundaries=RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    )


def _resolution(
    *,
    product_id: str = "sv300",
    variant_id: str | None = "sv300-white-glossy",
    basis: RCISConversationalEntityResolutionBasis = RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID,
    status: RCISConversationalEntityResolutionStatus = RCISConversationalEntityResolutionStatus.RESOLVED,
) -> RCISConversationalEntityResolution:
    return RCISConversationalEntityResolution(
        contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
        status=status,
        product_id=product_id if status is RCISConversationalEntityResolutionStatus.RESOLVED else None,
        variant_id=variant_id if status is RCISConversationalEntityResolutionStatus.RESOLVED else None,
        resolution_basis=basis,
    )


def _answer(
    *,
    resolution: RCISConversationalEntityResolution | None = None,
    context: RCISIntelligenceContext | None = None,
    text: str = "Governed answer.",
) -> RCISIntelligenceConversationalAnswer:
    resolution = _resolution() if resolution is None else resolution
    context = _context() if context is None else context
    provenance = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=context,
        resolution=resolution,
    )
    return RCISIntelligenceConversationalAnswer(
        contract_version=(
            RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION
        ),
        answer_text=text,
        product_id=resolution.product_id,
        variant_id=resolution.variant_id,
        provenance=provenance,
    )


def test_start_creates_empty_immutable_session() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=3)
    state = manager.start(session_id="session-1")

    assert state.contract_version == (
        RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
    )
    assert state.session_id == "session-1"
    assert state.max_turns == 3
    assert state.turns == ()
    assert state.current_product_id is None
    assert state.current_variant_id is None

    with pytest.raises(FrozenInstanceError):
        state.session_id = "changed"  # type: ignore[misc]


def test_append_turn_returns_new_state_and_preserves_original() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=3)
    original = manager.start(session_id="session-1")
    resolution = _resolution()
    answer = _answer(resolution=resolution)

    updated = manager.append_turn(
        state=original,
        user_utterance="Tell me about this variant.",
        resolution=resolution,
        answer=answer,
    )

    assert original.turns == ()
    assert updated is not original
    assert len(updated.turns) == 1
    assert updated.turns[0].turn_index == 0
    assert updated.turns[0].user_utterance == "Tell me about this variant."
    assert updated.turns[0].resolution is resolution
    assert updated.turns[0].answer is answer


def test_current_identity_tracks_latest_governed_resolution() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=3)
    state = manager.start(session_id="session-1")
    resolution = _resolution()
    answer = _answer(resolution=resolution)

    state = manager.append_turn(
        state=state,
        user_utterance="Explain it.",
        resolution=resolution,
        answer=answer,
    )

    assert state.current_product_id == "sv300"
    assert state.current_variant_id == "sv300-white-glossy"


def test_product_only_resolution_preserves_no_variant() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=3)
    state = manager.start(session_id="session-1")
    resolution = _resolution(
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
    )
    answer = _answer(resolution=resolution)

    state = manager.append_turn(
        state=state,
        user_utterance="Tell me about sv300.",
        resolution=resolution,
        answer=answer,
    )

    assert state.current_product_id == "sv300"
    assert state.current_variant_id is None


def test_bounded_history_keeps_latest_turns_with_absolute_consecutive_indexes() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=2)
    state = manager.start(session_id="session-1")

    for index in range(4):
        resolution = _resolution()
        state = manager.append_turn(
            state=state,
            user_utterance=f"Question {index}",
            resolution=resolution,
            answer=_answer(resolution=resolution, text=f"Answer {index}"),
        )

    assert [turn.turn_index for turn in state.turns] == [2, 3]
    assert [turn.user_utterance for turn in state.turns] == [
        "Question 2",
        "Question 3",
    ]


def test_turn_is_immutable() -> None:
    resolution = _resolution()
    turn = RCISIntelligenceConversationalSessionTurn(
        turn_index=0,
        user_utterance="Explain this.",
        resolution=resolution,
        answer=_answer(resolution=resolution),
    )

    with pytest.raises(FrozenInstanceError):
        turn.user_utterance = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("max_turns", [0, -1])
def test_max_turns_must_be_positive(max_turns: int) -> None:
    with pytest.raises(ValueError, match="max_turns must be at least 1"):
        RCISIntelligenceConversationalSessionStateManager(
            max_turns=max_turns
        )


def test_max_turns_rejects_bool() -> None:
    with pytest.raises(TypeError, match="max_turns must be int"):
        RCISIntelligenceConversationalSessionStateManager(
            max_turns=True  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("session_id", ["", "   "])
def test_blank_session_id_is_rejected(session_id: str) -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=2)
    with pytest.raises(ValueError, match="session_id must not be empty"):
        manager.start(session_id=session_id)


def test_unresolved_resolution_is_rejected() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=2)
    state = manager.start(session_id="session-1")
    unresolved = _resolution(
        status=RCISConversationalEntityResolutionStatus.UNRESOLVED,
        product_id="unused",
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE,
    )
    valid_resolution = _resolution()

    with pytest.raises(ValueError, match="session turn resolution must be RESOLVED"):
        manager.append_turn(
            state=state,
            user_utterance="What about it?",
            resolution=unresolved,
            answer=_answer(resolution=valid_resolution),
        )

    assert state.turns == ()


def test_answer_identity_must_match_resolution() -> None:
    manager = RCISIntelligenceConversationalSessionStateManager(max_turns=2)
    state = manager.start(session_id="session-1")
    resolution = _resolution()
    product_only_resolution = _resolution(
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
    )

    with pytest.raises(ValueError, match="session turn answer variant mismatch"):
        manager.append_turn(
            state=state,
            user_utterance="Explain sv300.",
            resolution=product_only_resolution,
            answer=_answer(resolution=resolution),
        )


def test_manager_rejects_state_with_different_bound() -> None:
    first = RCISIntelligenceConversationalSessionStateManager(max_turns=2)
    second = RCISIntelligenceConversationalSessionStateManager(max_turns=3)
    state = first.start(session_id="session-1")
    resolution = _resolution()

    with pytest.raises(
        ValueError,
        match="state max_turns does not match manager max_turns",
    ):
        second.append_turn(
            state=state,
            user_utterance="Explain this.",
            resolution=resolution,
            answer=_answer(resolution=resolution),
        )


def test_session_snapshot_rejects_non_consecutive_turn_indexes() -> None:
    resolution = _resolution()
    answer = _answer(resolution=resolution)
    first = RCISIntelligenceConversationalSessionTurn(
        turn_index=1,
        user_utterance="First",
        resolution=resolution,
        answer=answer,
    )
    third = RCISIntelligenceConversationalSessionTurn(
        turn_index=3,
        user_utterance="Third",
        resolution=resolution,
        answer=answer,
    )

    with pytest.raises(
        ValueError,
        match="turn indexes must be strictly consecutive",
    ):
        RCISIntelligenceConversationalSessionState(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
            ),
            session_id="session-1",
            max_turns=3,
            turns=(first, third),
            current_product_id="sv300",
            current_variant_id="sv300-white-glossy",
        )


def test_session_snapshot_current_identity_must_match_latest_turn() -> None:
    resolution = _resolution()
    turn = RCISIntelligenceConversationalSessionTurn(
        turn_index=0,
        user_utterance="Explain this.",
        resolution=resolution,
        answer=_answer(resolution=resolution),
    )

    with pytest.raises(
        ValueError,
        match="current product must match latest governed resolution",
    ):
        RCISIntelligenceConversationalSessionState(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
            ),
            session_id="session-1",
            max_turns=2,
            turns=(turn,),
            current_product_id="other-product",
            current_variant_id="sv300-white-glossy",
        )
