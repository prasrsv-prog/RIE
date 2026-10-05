"""Single-call visual-generation compatibility helper.

This helper preserves the exact ProviderExecutionResponse already returned
during one ConcreteVisualGenerationExecutionAdapter invocation. It does not
select providers, retry, admit candidates, persist data, or reconstruct a
provider response from adapter audit text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from rie.application.concrete_visual_generation_execution_adapter import (
    ConcreteVisualGenerationExecutionAdapter,
    ProviderExecutionResponse,
    ProviderTransport,
    VisualGenerationExecutionConfig,
    VisualReferenceResolver,
)
from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)


@dataclass(frozen=True, slots=True)
class CapturedVisualGenerationExecution:
    visual_generation_result: VisualGenerationResult
    provider_execution_response: ProviderExecutionResponse

    def __post_init__(self) -> None:
        if type(self.visual_generation_result) is not VisualGenerationResult:
            raise TypeError(
                "visual_generation_result must be an exact VisualGenerationResult"
            )
        if type(self.provider_execution_response) is not ProviderExecutionResponse:
            raise TypeError(
                "provider_execution_response must be an exact "
                "ProviderExecutionResponse"
            )
        if (
            self.visual_generation_result.provider_output_refs
            != self.provider_execution_response.provider_output_refs
        ):
            raise ValueError(
                "visual generation result and provider response output refs mismatch"
            )


class _SingleCallProviderResponseCapture:
    def __init__(self, transport: ProviderTransport) -> None:
        if not callable(transport):
            raise TypeError("transport must be callable")
        self._transport = transport
        self._call_count = 0
        self._response: ProviderExecutionResponse | None = None

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def response(self) -> ProviderExecutionResponse | None:
        return self._response

    def __call__(self, payload: Mapping[str, object]) -> ProviderExecutionResponse:
        if self._call_count != 0:
            raise RuntimeError("provider transport capture permits exactly one call")

        self._call_count += 1
        response = self._transport(payload)
        if type(response) is not ProviderExecutionResponse:
            raise TypeError(
                "transport must return an exact ProviderExecutionResponse"
            )

        self._response = response
        return response


def execute_visual_generation_with_provider_response_capture(
    *,
    request: VisualGenerationRequest,
    execution_config: VisualGenerationExecutionConfig,
    reference_resolver: VisualReferenceResolver,
    transport: ProviderTransport,
) -> CapturedVisualGenerationExecution:
    if type(request) is not VisualGenerationRequest:
        raise TypeError("request must be an exact VisualGenerationRequest")
    if type(execution_config) is not VisualGenerationExecutionConfig:
        raise TypeError(
            "execution_config must be an exact VisualGenerationExecutionConfig"
        )
    if not callable(getattr(reference_resolver, "resolve", None)):
        raise TypeError("reference_resolver must expose resolve")
    if not callable(transport):
        raise TypeError("transport must be callable")

    capture = _SingleCallProviderResponseCapture(transport)
    adapter = ConcreteVisualGenerationExecutionAdapter(
        config=execution_config,
        reference_resolver=reference_resolver,
        transport=capture,
    )
    result = adapter.generate(request)

    if type(result) is not VisualGenerationResult:
        raise TypeError("adapter must return an exact VisualGenerationResult")
    if capture.call_count != 1:
        raise RuntimeError("exactly one provider transport invocation is required")

    response = capture.response
    if type(response) is not ProviderExecutionResponse:
        raise RuntimeError("exact provider response was not captured")
    if result.provider_output_refs != response.provider_output_refs:
        raise ValueError(
            "visual generation result and captured provider response output refs mismatch"
        )

    return CapturedVisualGenerationExecution(
        visual_generation_result=result,
        provider_execution_response=response,
    )


__all__ = [
    "CapturedVisualGenerationExecution",
    "execute_visual_generation_with_provider_response_capture",
]
