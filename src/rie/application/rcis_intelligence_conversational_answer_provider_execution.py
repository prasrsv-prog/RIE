"""Minimum governed provider-execution contract for RCIS conversational answers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCISIntelligenceConversationalAnswerInput,
)


RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalAnswerProviderExecutionRequest:
    """Immutable execution request bound to one explicit provider/model pair."""

    contract_version: str
    provider_id: str
    model_id: str
    answer_input: RCISIntelligenceConversationalAnswerInput

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported provider-execution contract version")
        _require_non_empty_text(self.provider_id, field_name="provider_id")
        _require_non_empty_text(self.model_id, field_name="model_id")
        if not isinstance(
            self.answer_input,
            RCISIntelligenceConversationalAnswerInput,
        ):
            raise TypeError(
                "answer_input must be RCISIntelligenceConversationalAnswerInput"
            )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceConversationalAnswerProviderExecutionResponse:
    """Immutable exact provider/model response used as conversational answer text."""

    contract_version: str
    provider_id: str
    model_id: str
    answer_text: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported provider-execution contract version")
        _require_non_empty_text(self.provider_id, field_name="provider_id")
        _require_non_empty_text(self.model_id, field_name="model_id")
        _require_non_empty_text(self.answer_text, field_name="answer_text")


class RCISIntelligenceConversationalAnswerProviderRenderer:
    """Renderer adapter that performs one explicit provider/model execution."""

    def __init__(
        self,
        *,
        provider_id: str,
        model_id: str,
        transport: Callable[
            [RCISIntelligenceConversationalAnswerProviderExecutionRequest],
            RCISIntelligenceConversationalAnswerProviderExecutionResponse,
        ],
    ) -> None:
        self._provider_id = _require_non_empty_text(
            provider_id,
            field_name="provider_id",
        )
        self._model_id = _require_non_empty_text(
            model_id,
            field_name="model_id",
        )
        if not callable(transport):
            raise TypeError("transport must be callable")
        self._transport = transport

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def model_id(self) -> str:
        return self._model_id

    def __call__(
        self,
        answer_input: RCISIntelligenceConversationalAnswerInput,
    ) -> str:
        if not isinstance(
            answer_input,
            RCISIntelligenceConversationalAnswerInput,
        ):
            raise TypeError(
                "answer_input must be RCISIntelligenceConversationalAnswerInput"
            )

        request = RCISIntelligenceConversationalAnswerProviderExecutionRequest(
            contract_version=(
                RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
            ),
            provider_id=self._provider_id,
            model_id=self._model_id,
            answer_input=answer_input,
        )

        response = self._transport(request)
        if not isinstance(
            response,
            RCISIntelligenceConversationalAnswerProviderExecutionResponse,
        ):
            raise TypeError(
                "transport response must be "
                "RCISIntelligenceConversationalAnswerProviderExecutionResponse"
            )
        if response.provider_id != request.provider_id:
            raise ValueError("provider response provider_id mismatch")
        if response.model_id != request.model_id:
            raise ValueError("provider response model_id mismatch")

        return response.answer_text


__all__ = [
    "RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION",
    "RCISIntelligenceConversationalAnswerProviderExecutionRequest",
    "RCISIntelligenceConversationalAnswerProviderExecutionResponse",
    "RCISIntelligenceConversationalAnswerProviderRenderer",
]
