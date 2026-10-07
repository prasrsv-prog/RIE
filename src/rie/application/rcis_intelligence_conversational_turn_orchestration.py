"""Minimum governed single-turn orchestration contract for RCIS intelligence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_answer_provenance import (
    RCISIntelligenceAnswerProvenanceBuilder,
)
from rie.application.rcis_intelligence_context_assembly import (
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCISIntelligenceConversationalAnswer,
    RCISIntelligenceConversationalAnswerGenerator,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionStatus,
)
from rie.application.rcis_intelligence_conversational_session_state import (
    RCISIntelligenceConversationalSessionState,
    RCISIntelligenceConversationalSessionStateManager,
)


RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalTurnResult:
    """Immutable exact result of one governed conversational turn."""

    contract_version: str
    user_utterance: str
    resolution: RCISConversationalEntityResolution
    answer: RCISIntelligenceConversationalAnswer
    session_state: RCISIntelligenceConversationalSessionState

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported conversational-turn orchestration contract version")
        _require_non_empty_text(self.user_utterance, field_name="user_utterance")

        if not isinstance(self.resolution, RCISConversationalEntityResolution):
            raise TypeError(
                "resolution must be RCISConversationalEntityResolution"
            )
        if (
            self.resolution.status
            is not RCISConversationalEntityResolutionStatus.RESOLVED
        ):
            raise ValueError("turn result resolution must be RESOLVED")

        if not isinstance(self.answer, RCISIntelligenceConversationalAnswer):
            raise TypeError("answer must be RCISIntelligenceConversationalAnswer")
        if not isinstance(
            self.session_state,
            RCISIntelligenceConversationalSessionState,
        ):
            raise TypeError(
                "session_state must be RCISIntelligenceConversationalSessionState"
            )

        if self.answer.product_id != self.resolution.product_id:
            raise ValueError("turn result answer product mismatch")
        if self.answer.variant_id != self.resolution.variant_id:
            raise ValueError("turn result answer variant mismatch")
        if self.session_state.current_product_id != self.resolution.product_id:
            raise ValueError("turn result session product mismatch")
        if self.session_state.current_variant_id != self.resolution.variant_id:
            raise ValueError("turn result session variant mismatch")
        if not self.session_state.turns:
            raise ValueError("turn result session must contain appended turn")

        latest_turn = self.session_state.turns[-1]
        if latest_turn.user_utterance != self.user_utterance:
            raise ValueError("turn result latest utterance mismatch")
        if latest_turn.resolution is not self.resolution:
            raise ValueError("turn result latest resolution mismatch")
        if latest_turn.answer is not self.answer:
            raise ValueError("turn result latest answer mismatch")


class RCISIntelligenceConversationalTurnOrchestrator:
    """Compose exactly one governed resolution, answer, and session append."""

    def __init__(
        self,
        *,
        resolver: Callable[
            [
                str,
                RCISIntelligenceContext,
                RCISIntelligenceConversationalSessionState,
            ],
            RCISConversationalEntityResolution,
        ],
        answer_generator: RCISIntelligenceConversationalAnswerGenerator,
        session_manager: RCISIntelligenceConversationalSessionStateManager,
    ) -> None:
        if not callable(resolver):
            raise TypeError("resolver must be callable")
        if not isinstance(
            answer_generator,
            RCISIntelligenceConversationalAnswerGenerator,
        ):
            raise TypeError(
                "answer_generator must be RCISIntelligenceConversationalAnswerGenerator"
            )
        if not isinstance(
            session_manager,
            RCISIntelligenceConversationalSessionStateManager,
        ):
            raise TypeError(
                "session_manager must be RCISIntelligenceConversationalSessionStateManager"
            )

        self._resolver = resolver
        self._answer_generator = answer_generator
        self._session_manager = session_manager
        self._provenance_builder = RCISIntelligenceAnswerProvenanceBuilder()

    def execute(
        self,
        *,
        user_utterance: str,
        context: RCISIntelligenceContext,
        session_state: RCISIntelligenceConversationalSessionState,
    ) -> RCISIntelligenceConversationalTurnResult:
        utterance = _require_non_empty_text(
            user_utterance,
            field_name="user_utterance",
        )
        if not isinstance(context, RCISIntelligenceContext):
            raise TypeError("context must be RCISIntelligenceContext")
        if not isinstance(
            session_state,
            RCISIntelligenceConversationalSessionState,
        ):
            raise TypeError(
                "session_state must be RCISIntelligenceConversationalSessionState"
            )
        if session_state.max_turns != self._session_manager.max_turns:
            raise ValueError(
                "session_state max_turns does not match session_manager max_turns"
            )

        resolution = self._resolver(
            utterance,
            context,
            session_state,
        )
        if not isinstance(resolution, RCISConversationalEntityResolution):
            raise TypeError(
                "resolver must return RCISConversationalEntityResolution"
            )
        if (
            resolution.status
            is not RCISConversationalEntityResolutionStatus.RESOLVED
        ):
            raise ValueError("resolver result must be RESOLVED")

        provenance = self._provenance_builder.build(
            context=context,
            resolution=resolution,
        )

        answer = self._answer_generator.generate(
            utterance=utterance,
            context=context,
            resolution=resolution,
            provenance=provenance,
        )

        updated_state = self._session_manager.append_turn(
            state=session_state,
            user_utterance=utterance,
            resolution=resolution,
            answer=answer,
        )

        return RCISIntelligenceConversationalTurnResult(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION
            ),
            user_utterance=utterance,
            resolution=resolution,
            answer=answer,
            session_state=updated_state,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_TURN_ORCHESTRATION_CONTRACT_VERSION",
    "RCISIntelligenceConversationalTurnOrchestrator",
    "RCISIntelligenceConversationalTurnResult",
]
