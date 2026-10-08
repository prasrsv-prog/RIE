"""Bounded execution for retrieval-grounded RCIS Intelligence conversational turns."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_retrieval_grounded_conversational_turn_integration import (
    RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
)


RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_EXECUTION_CONTRACT_VERSION: Final[
    str
] = "1.0.0"


@dataclass(frozen=True, slots=True)
class RCISIntelligenceRetrievalGroundedTurnExecutionResult:
    """Immutable execution outcome for one retrieval-grounded conversational turn."""

    contract_version: str
    integration_result: RCISIntelligenceRetrievalGroundedTurnIntegrationResult
    prior_session_state: object | None
    governed_answer: object | None
    next_session_state: object | None
    knowledge_gap: bool
    answer_generated: bool
    session_updated: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_EXECUTION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported retrieval-grounded turn execution contract version"
            )

        if not isinstance(
            self.integration_result,
            RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
        ):
            raise TypeError(
                "integration_result must be "
                "RCISIntelligenceRetrievalGroundedTurnIntegrationResult"
            )

        for field_name, value in (
            ("knowledge_gap", self.knowledge_gap),
            ("answer_generated", self.answer_generated),
            ("session_updated", self.session_updated),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if self.knowledge_gap is not self.integration_result.knowledge_gap:
            raise ValueError(
                "execution knowledge_gap must match integration knowledge_gap"
            )

        if self.knowledge_gap:
            if self.integration_result.answer_generation_allowed:
                raise ValueError(
                    "knowledge gap cannot allow answer generation"
                )
            if self.governed_answer is not None:
                raise ValueError(
                    "governed_answer must be None when knowledge gap is present"
                )
            if self.answer_generated:
                raise ValueError(
                    "answer_generated must be False when knowledge gap is present"
                )
            if self.session_updated:
                raise ValueError(
                    "session_updated must be False when knowledge gap is present"
                )
            if self.next_session_state is not self.prior_session_state:
                raise ValueError(
                    "knowledge gap must preserve prior session state unchanged"
                )
            return

        if not self.integration_result.answer_generation_allowed:
            raise ValueError(
                "non-gap execution requires integration answer generation allowance"
            )
        if self.governed_answer is None:
            raise ValueError(
                "governed_answer is required when knowledge exists"
            )
        if self.next_session_state is None:
            raise ValueError(
                "next_session_state is required when knowledge exists"
            )
        if not self.answer_generated:
            raise ValueError(
                "answer_generated must be True when knowledge exists"
            )
        if not self.session_updated:
            raise ValueError(
                "session_updated must be True when knowledge exists"
            )


class RCISIntelligenceRetrievalGroundedConversationalTurnExecutor:
    """Execute grounded answer generation and bounded session update exactly once."""

    def __init__(
        self,
        *,
        answer_generator: Callable[
            [
                RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
                object | None,
            ],
            object,
        ],
        session_updater: Callable[
            [
                object | None,
                RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
                object,
            ],
            object,
        ],
    ) -> None:
        if not callable(answer_generator):
            raise TypeError("answer_generator must be callable")
        if not callable(session_updater):
            raise TypeError("session_updater must be callable")

        self._answer_generator = answer_generator
        self._session_updater = session_updater

    def execute(
        self,
        *,
        integration_result: RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
        prior_session_state: object | None = None,
    ) -> RCISIntelligenceRetrievalGroundedTurnExecutionResult:
        if not isinstance(
            integration_result,
            RCISIntelligenceRetrievalGroundedTurnIntegrationResult,
        ):
            raise TypeError(
                "integration_result must be "
                "RCISIntelligenceRetrievalGroundedTurnIntegrationResult"
            )

        if integration_result.knowledge_gap:
            if integration_result.answer_generation_allowed:
                raise ValueError(
                    "knowledge gap integration cannot allow answer generation"
                )

            return RCISIntelligenceRetrievalGroundedTurnExecutionResult(
                contract_version=(
                    RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_EXECUTION_CONTRACT_VERSION
                ),
                integration_result=integration_result,
                prior_session_state=prior_session_state,
                governed_answer=None,
                next_session_state=prior_session_state,
                knowledge_gap=True,
                answer_generated=False,
                session_updated=False,
            )

        if not integration_result.answer_generation_allowed:
            raise ValueError(
                "non-gap integration must allow answer generation"
            )
        if integration_result.governed_context is None:
            raise ValueError(
                "non-gap integration must contain governed context"
            )

        governed_answer = self._answer_generator(
            integration_result,
            prior_session_state,
        )

        if governed_answer is None:
            raise ValueError(
                "answer_generator must return governed answer"
            )

        next_session_state = self._session_updater(
            prior_session_state,
            integration_result,
            governed_answer,
        )

        if next_session_state is None:
            raise ValueError(
                "session_updater must return bounded next session state"
            )

        return RCISIntelligenceRetrievalGroundedTurnExecutionResult(
            contract_version=(
                RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_EXECUTION_CONTRACT_VERSION
            ),
            integration_result=integration_result,
            prior_session_state=prior_session_state,
            governed_answer=governed_answer,
            next_session_state=next_session_state,
            knowledge_gap=False,
            answer_generated=True,
            session_updated=True,
        )


__all__ = [
    "RCIS_INTELLIGENCE_RETRIEVAL_GROUNDED_TURN_EXECUTION_CONTRACT_VERSION",
    "RCISIntelligenceRetrievalGroundedConversationalTurnExecutor",
    "RCISIntelligenceRetrievalGroundedTurnExecutionResult",
]
