from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from rie.rsv_knowledge.phase_b_grounded_prompt_orchestration import (
    orchestrate_exact18_grounded_prompt_request,
)


REQUEST_FIELD_NAMES = (
    "product_id",
    "variant_id",
    "creative_variables",
    "requested_output",
)

FROZEN_GROUNDED_PROMPT_ORCHESTRATOR = (
    orchestrate_exact18_grounded_prompt_request
)


class GroundedPromptApplicationContractError(ValueError):
    """Fail-closed contract error for the minimum grounded-prompt application layer."""


@dataclass(frozen=True)
class GroundedPromptApplicationRequest:
    product_id: str
    variant_id: str
    creative_variables: Mapping[str, str]
    requested_output: str


def derive_grounded_prompt_application_foundation_dependency_names(
    orchestrator: Callable[..., object],
) -> tuple[str, ...]:
    signature = inspect.signature(orchestrator)
    missing_request_fields = [
        name for name in REQUEST_FIELD_NAMES if name not in signature.parameters
    ]
    if missing_request_fields:
        raise GroundedPromptApplicationContractError(
            "Frozen orchestrator signature missing request fields: "
            + ",".join(missing_request_fields)
        )

    dependency_names: list[str] = []
    for name, parameter in signature.parameters.items():
        if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            raise GroundedPromptApplicationContractError(
                "Unsupported frozen orchestrator parameter kind for " + name
            )
        if name not in REQUEST_FIELD_NAMES:
            dependency_names.append(name)
    return tuple(dependency_names)


def _validate_nonempty_string(field_name: str, value: object) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise GroundedPromptApplicationContractError(
            field_name + " must be a nonempty string"
        )
    return value


def _validated_creative_variables(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        raise GroundedPromptApplicationContractError(
            "creative_variables must be a mapping"
        )
    validated: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or key.strip() == "":
            raise GroundedPromptApplicationContractError(
                "creative_variables keys must be nonempty strings"
            )
        if not isinstance(item, str) or item.strip() == "":
            raise GroundedPromptApplicationContractError(
                "creative_variables values must be nonempty strings"
            )
        validated[key] = item
    return validated


class GroundedPromptApplicationService:
    def __init__(
        self,
        *,
        orchestrator: Callable[..., object],
        foundation_dependencies: Mapping[str, object],
    ) -> None:
        if not callable(orchestrator):
            raise GroundedPromptApplicationContractError(
                "orchestrator must be callable"
            )
        self._orchestrator = orchestrator
        self._required_dependency_names = (
            derive_grounded_prompt_application_foundation_dependency_names(
                orchestrator
            )
        )
        self._foundation_dependencies = self._validate_foundation_dependencies(
            foundation_dependencies
        )

    def _validate_foundation_dependencies(
        self, foundation_dependencies: Mapping[str, object]
    ) -> dict[str, object]:
        if not isinstance(foundation_dependencies, Mapping):
            raise GroundedPromptApplicationContractError(
                "foundation_dependencies must be a mapping"
            )
        provided_keys = tuple(
            sorted(str(key) for key in foundation_dependencies.keys())
        )
        required_keys = tuple(sorted(self._required_dependency_names))
        if provided_keys != required_keys:
            missing = sorted(set(required_keys) - set(provided_keys))
            extra = sorted(set(provided_keys) - set(required_keys))
            problems: list[str] = []
            if missing:
                problems.append("missing=" + ",".join(missing))
            if extra:
                problems.append("extra=" + ",".join(extra))
            raise GroundedPromptApplicationContractError(
                "foundation_dependencies key mismatch: " + ";".join(problems)
            )
        return dict(foundation_dependencies)

    def execute(self, request: GroundedPromptApplicationRequest) -> object:
        if not isinstance(request, GroundedPromptApplicationRequest):
            raise GroundedPromptApplicationContractError(
                "request must be GroundedPromptApplicationRequest"
            )

        product_id = _validate_nonempty_string("product_id", request.product_id)
        variant_id = _validate_nonempty_string("variant_id", request.variant_id)
        requested_output = _validate_nonempty_string(
            "requested_output", request.requested_output
        )
        creative_variables = _validated_creative_variables(
            request.creative_variables
        )

        return self._orchestrator(
            product_id=product_id,
            variant_id=variant_id,
            creative_variables=creative_variables,
            requested_output=requested_output,
            **self._foundation_dependencies,
        )
