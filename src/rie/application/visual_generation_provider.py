"""Side-effect-free PC5 visual-generation provider boundary.

This module defines request/result values and the provider protocol only.
It does not select, construct, connect to, or execute any concrete model,
network service, generator runtime, persistence layer, or governed asset store.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


def _require_non_empty_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _require_reference_tuple(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    for item in value:
        _require_non_empty_text(item, field_name)
    if len(value) != len(set(value)):
        raise ValueError(f"{field_name} must not contain duplicates")
    return value


@dataclass(frozen=True, slots=True)
class VisualGenerationRequest:
    """Exact application request forwarded to an injected visual provider."""

    grounded_prompt: str
    selected_reference_asset_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_text(self.grounded_prompt, "grounded_prompt")
        _require_reference_tuple(
            self.selected_reference_asset_ids,
            "selected_reference_asset_ids",
        )


@dataclass(frozen=True, slots=True)
class VisualGenerationResult:
    """Non-governed provider-local result metadata returned to the shell."""

    provider_output_refs: tuple[str, ...] = ()
    message: str = ""

    def __post_init__(self) -> None:
        _require_reference_tuple(
            self.provider_output_refs,
            "provider_output_refs",
        )
        if not isinstance(self.message, str):
            raise TypeError("message must be a string")


@runtime_checkable
class VisualGenerationProvider(Protocol):
    """Injected PC5 boundary; concrete generator execution is out of scope."""

    def generate(
        self,
        request: VisualGenerationRequest,
    ) -> VisualGenerationResult:
        """Return provider-local result metadata for one explicit request."""
        ...


__all__ = [
    "VisualGenerationProvider",
    "VisualGenerationRequest",
    "VisualGenerationResult",
]
