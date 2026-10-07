"""Minimum governed conversational-session state contract for RCIS intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCISIntelligenceConversationalAnswer,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionStatus,
)


RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def _require_max_turns(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("max_turns must be int")
    if value < 1:
        raise ValueError("max_turns must be at least 1")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalSessionTurn:
    """One immutable governed user/assistant turn."""

    turn_index: int
    user_utterance: str
    resolution: RCISConversationalEntityResolution
    answer: RCISIntelligenceConversationalAnswer

    def __post_init__(self) -> None:
        if isinstance(self.turn_index, bool) or not isinstance(self.turn_index, int):
            raise TypeError("turn_index must be int")
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        _require_non_empty_text(self.user_utterance, field_name="user_utterance")

        if not isinstance(self.resolution, RCISConversationalEntityResolution):
            raise TypeError(
                "resolution must be RCISConversationalEntityResolution"
            )
        if (
            self.resolution.status
            is not RCISConversationalEntityResolutionStatus.RESOLVED
        ):
            raise ValueError("session turn resolution must be RESOLVED")

        if not isinstance(self.answer, RCISIntelligenceConversationalAnswer):
            raise TypeError(
                "answer must be RCISIntelligenceConversationalAnswer"
            )
        if self.answer.product_id != self.resolution.product_id:
            raise ValueError("session turn answer product mismatch")
        if self.answer.variant_id != self.resolution.variant_id:
            raise ValueError("session turn answer variant mismatch")
        if (
            self.answer.provenance.entity_resolution_contract_version
            != self.resolution.contract_version
        ):
            raise ValueError("session turn resolution contract mismatch")
        if (
            self.answer.provenance.resolved_product_id
            != self.resolution.product_id
        ):
            raise ValueError("session turn provenance product mismatch")
        if (
            self.answer.provenance.resolved_variant_id
            != self.resolution.variant_id
        ):
            raise ValueError("session turn provenance variant mismatch")
        if (
            self.answer.provenance.resolution_basis
            is not self.resolution.resolution_basis
        ):
            raise ValueError("session turn provenance resolution basis mismatch")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalSessionState:
    """Immutable bounded session snapshot with current governed identity."""

    contract_version: str
    session_id: str
    max_turns: int
    turns: tuple[RCISIntelligenceConversationalSessionTurn, ...]
    current_product_id: str | None
    current_variant_id: str | None

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported conversational-session state contract version")

        _require_non_empty_text(self.session_id, field_name="session_id")
        _require_max_turns(self.max_turns)

        if not isinstance(self.turns, tuple):
            raise TypeError("turns must be tuple")
        if len(self.turns) > self.max_turns:
            raise ValueError("turn history exceeds max_turns")

        for turn in self.turns:
            if not isinstance(turn, RCISIntelligenceConversationalSessionTurn):
                raise TypeError(
                    "turns must contain RCISIntelligenceConversationalSessionTurn"
                )

        for previous, current in zip(self.turns, self.turns[1:]):
            if current.turn_index != previous.turn_index + 1:
                raise ValueError("turn indexes must be strictly consecutive")

        if not self.turns:
            if self.current_product_id is not None:
                raise ValueError("empty session cannot have current_product_id")
            if self.current_variant_id is not None:
                raise ValueError("empty session cannot have current_variant_id")
            return

        latest = self.turns[-1]
        if self.current_product_id != latest.resolution.product_id:
            raise ValueError("current product must match latest governed resolution")
        if self.current_variant_id != latest.resolution.variant_id:
            raise ValueError("current variant must match latest governed resolution")


class RCISIntelligenceConversationalSessionStateManager:
    """Create and append immutable bounded governed session snapshots."""

    def __init__(self, *, max_turns: int) -> None:
        self._max_turns = _require_max_turns(max_turns)

    @property
    def max_turns(self) -> int:
        return self._max_turns

    def start(
        self,
        *,
        session_id: str,
    ) -> RCISIntelligenceConversationalSessionState:
        return RCISIntelligenceConversationalSessionState(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
            ),
            session_id=_require_non_empty_text(
                session_id,
                field_name="session_id",
            ),
            max_turns=self._max_turns,
            turns=(),
            current_product_id=None,
            current_variant_id=None,
        )

    def append_turn(
        self,
        *,
        state: RCISIntelligenceConversationalSessionState,
        user_utterance: str,
        resolution: RCISConversationalEntityResolution,
        answer: RCISIntelligenceConversationalAnswer,
    ) -> RCISIntelligenceConversationalSessionState:
        if not isinstance(state, RCISIntelligenceConversationalSessionState):
            raise TypeError(
                "state must be RCISIntelligenceConversationalSessionState"
            )
        if state.max_turns != self._max_turns:
            raise ValueError("state max_turns does not match manager max_turns")

        next_turn_index = (
            0
            if not state.turns
            else state.turns[-1].turn_index + 1
        )
        new_turn = RCISIntelligenceConversationalSessionTurn(
            turn_index=next_turn_index,
            user_utterance=user_utterance,
            resolution=resolution,
            answer=answer,
        )

        retained_turns = (*state.turns, new_turn)
        if len(retained_turns) > self._max_turns:
            retained_turns = retained_turns[-self._max_turns :]

        return RCISIntelligenceConversationalSessionState(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION
            ),
            session_id=state.session_id,
            max_turns=self._max_turns,
            turns=retained_turns,
            current_product_id=resolution.product_id,
            current_variant_id=resolution.variant_id,
        )


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_SESSION_STATE_CONTRACT_VERSION",
    "RCISIntelligenceConversationalSessionState",
    "RCISIntelligenceConversationalSessionStateManager",
    "RCISIntelligenceConversationalSessionTurn",
]
