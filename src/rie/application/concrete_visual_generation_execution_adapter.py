"""Minimum governed concrete visual-generation execution adapter.

This slice executes exactly one explicitly configured provider/model invocation
through injected, auditable dependencies. It performs no provider selection,
fallback, retry, candidate admission, asset admission, or approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class VisualGenerationExecutionConfig:
    provider_id: str
    model_id: str

    def __post_init__(self) -> None:
        _required_text(self.provider_id, "provider_id")
        _required_text(self.model_id, "model_id")


@dataclass(frozen=True, slots=True)
class ResolvedVisualReference:
    requested_asset_id: str
    resolved_asset_id: str
    provider_media_ref: str
    use_eligible: bool

    def __post_init__(self) -> None:
        _required_text(self.requested_asset_id, "requested_asset_id")
        _required_text(self.resolved_asset_id, "resolved_asset_id")
        _required_text(self.provider_media_ref, "provider_media_ref")
        if self.requested_asset_id != self.resolved_asset_id:
            raise ValueError("resolved asset identity must match requested asset identity")
        if self.use_eligible is not True:
            raise ValueError("resolved reference must remain use-eligible")


class VisualReferenceResolver(Protocol):
    def resolve(self, asset_id: str) -> ResolvedVisualReference: ...


@dataclass(frozen=True, slots=True)
class ProviderExecutionResponse:
    execution_status: str
    provider_output_refs: tuple[str, ...]
    provider_execution_ref: str = ""
    diagnostic_message: str = ""

    def __post_init__(self) -> None:
        _required_text(self.execution_status, "execution_status")
        if self.execution_status != "SUCCEEDED":
            raise ValueError("provider execution status must be SUCCEEDED")
        if not isinstance(self.provider_output_refs, tuple):
            raise TypeError("provider_output_refs must be a tuple")
        if not self.provider_output_refs:
            raise ValueError("provider_output_refs must not be empty")
        for ref in self.provider_output_refs:
            _required_text(ref, "provider_output_refs")
        if len(set(self.provider_output_refs)) != len(self.provider_output_refs):
            raise ValueError("provider_output_refs must not contain duplicates")
        if not isinstance(self.provider_execution_ref, str):
            raise TypeError("provider_execution_ref must be a string")
        if not isinstance(self.diagnostic_message, str):
            raise TypeError("diagnostic_message must be a string")


ProviderTransport = Callable[[Mapping[str, object]], ProviderExecutionResponse]


class ConcreteVisualGenerationExecutionAdapter:
    """Execute one request against one explicit provider/model configuration."""

    def __init__(
        self,
        *,
        config: VisualGenerationExecutionConfig,
        reference_resolver: VisualReferenceResolver,
        transport: ProviderTransport,
    ) -> None:
        if not callable(getattr(reference_resolver, "resolve", None)):
            raise TypeError("reference_resolver must expose resolve")
        if not callable(transport):
            raise TypeError("transport must be callable")
        self._config = config
        self._reference_resolver = reference_resolver
        self._transport = transport

    def generate(self, request: VisualGenerationRequest) -> VisualGenerationResult:
        if not isinstance(request, VisualGenerationRequest):
            raise TypeError("request must be VisualGenerationRequest")

        media_refs: list[str] = []
        for asset_id in request.selected_reference_asset_ids:
            resolved = self._reference_resolver.resolve(asset_id)
            if not isinstance(resolved, ResolvedVisualReference):
                raise TypeError("reference resolver returned an invalid result")
            if resolved.requested_asset_id != asset_id:
                raise ValueError("reference resolver changed requested asset identity")
            media_refs.append(resolved.provider_media_ref)

        provider_request: Mapping[str, object] = {
            "provider_id": self._config.provider_id,
            "model_id": self._config.model_id,
            "grounded_prompt": request.grounded_prompt,
            "reference_media_refs": tuple(media_refs),
        }
        response = self._transport(provider_request)
        if not isinstance(response, ProviderExecutionResponse):
            raise TypeError("transport returned an invalid provider response")

        audit = (
            f"provider={self._config.provider_id};"
            f"model={self._config.model_id};"
            f"status={response.execution_status};"
            f"execution_ref={response.provider_execution_ref};"
            f"diagnostic={response.diagnostic_message}"
        )
        return VisualGenerationResult(
            provider_output_refs=response.provider_output_refs,
            message=audit,
        )


__all__ = [
    "ConcreteVisualGenerationExecutionAdapter",
    "ProviderExecutionResponse",
    "ResolvedVisualReference",
    "VisualGenerationExecutionConfig",
    "VisualReferenceResolver",
]
