"""Deterministic fail-closed grounded prompt compilation from canonical product locks."""

from dataclasses import dataclass
from typing import Mapping, Optional, Tuple

from .constraint_binding import ConstraintBindingResult


class GroundedPromptCompilerContractError(ValueError):
    """Raised when grounded prompt compiler input violates the contract."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise GroundedPromptCompilerContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise GroundedPromptCompilerContractError(f"{field_name} must not be empty")
    return normalized


@dataclass(frozen=True)
class GroundedPromptCompileResult:
    prompt_text: str
    product_id: str
    variant_id: Optional[str]
    used_knowledge_ids: Tuple[str, ...]
    used_asset_ids: Tuple[str, ...]
    missing_knowledge: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    grounding_status: str


def _failed_result(
    binding_result: ConstraintBindingResult,
    *,
    conflicts: Tuple[str, ...],
) -> GroundedPromptCompileResult:
    return GroundedPromptCompileResult(
        prompt_text="",
        product_id=binding_result.product_id,
        variant_id=binding_result.variant_id,
        used_knowledge_ids=tuple(binding_result.used_knowledge_ids),
        used_asset_ids=tuple(binding_result.used_asset_ids),
        missing_knowledge=tuple(binding_result.missing_knowledge),
        conflicts=conflicts,
        grounding_status="FAILED",
    )


def compile_grounded_prompt(
    *,
    binding_result: ConstraintBindingResult,
    creative_variables: Mapping[str, str],
    requested_output: str,
) -> GroundedPromptCompileResult:
    """Compile only accepted canonical locks plus explicit creative variables."""

    if not isinstance(binding_result, ConstraintBindingResult):
        raise GroundedPromptCompilerContractError(
            "binding_result must be a ConstraintBindingResult"
        )

    if not isinstance(creative_variables, Mapping):
        raise GroundedPromptCompilerContractError(
            "creative_variables must be a mapping"
        )

    requested_output = _required_text(requested_output, "requested_output")

    normalized_creative = {}
    for raw_key, raw_value in creative_variables.items():
        key = _required_text(raw_key, "creative variable key")
        value = _required_text(raw_value, f"creative variable value for {key}")
        if key in normalized_creative:
            raise GroundedPromptCompilerContractError(
                f"duplicate creative variable key: {key}"
            )
        normalized_creative[key] = value

    inherited_conflicts = tuple(binding_result.conflicts)
    inherited_missing = tuple(binding_result.missing_knowledge)

    if (
        binding_result.binding_status != "PASSED"
        or inherited_missing
        or inherited_conflicts
    ):
        return _failed_result(
            binding_result,
            conflicts=inherited_conflicts,
        )

    constraint_types = {
        constraint.constraint_type.casefold(): constraint.constraint_type
        for constraint in binding_result.bound_constraints
    }

    creative_override_conflicts = tuple(
        f"creative_override:{key}"
        for key in sorted(normalized_creative)
        if key.casefold() in constraint_types
    )

    if creative_override_conflicts:
        return _failed_result(
            binding_result,
            conflicts=creative_override_conflicts,
        )

    ordered_constraints = tuple(
        sorted(
            binding_result.bound_constraints,
            key=lambda item: (item.constraint_type, item.constraint_id),
        )
    )

    prompt_lines = ["PRODUCT LOCKS:"]
    if ordered_constraints:
        for constraint in ordered_constraints:
            prompt_lines.append(
                f"- {constraint.constraint_type}: {constraint.rule}"
            )
    else:
        prompt_lines.append("- <NONE>")

    prompt_lines.append("CREATIVE VARIABLES:")
    if normalized_creative:
        for key in sorted(normalized_creative):
            prompt_lines.append(f"- {key}: {normalized_creative[key]}")
    else:
        prompt_lines.append("- <NONE>")

    prompt_lines.append("REQUESTED OUTPUT:")
    prompt_lines.append(requested_output)

    return GroundedPromptCompileResult(
        prompt_text="\n".join(prompt_lines),
        product_id=binding_result.product_id,
        variant_id=binding_result.variant_id,
        used_knowledge_ids=tuple(binding_result.used_knowledge_ids),
        used_asset_ids=tuple(binding_result.used_asset_ids),
        missing_knowledge=(),
        conflicts=(),
        grounding_status="PASSED",
    )
