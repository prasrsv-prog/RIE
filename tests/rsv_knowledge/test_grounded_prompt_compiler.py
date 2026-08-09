import pytest

from rie.rsv_knowledge.constraint_binding import (
    ConstraintBindingResult,
    ConstraintRecord,
)
from rie.rsv_knowledge.grounded_prompt_compiler import (
    GroundedPromptCompilerContractError,
    compile_grounded_prompt,
)


def constraint(constraint_id, constraint_type, rule, source_id):
    return ConstraintRecord(
        constraint_id=constraint_id,
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        constraint_type=constraint_type,
        rule=rule,
        source_knowledge_id_or_asset_id=source_id,
        status="active",
    )


def passed_binding():
    return ConstraintBindingResult(
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        bound_constraints=(
            constraint(
                "constraint-logo",
                "logo_placement",
                "preserve exact RSV logo placement",
                "asset-logo",
            ),
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve exact shell geometry",
                "knowledge-shell",
            ),
        ),
        used_knowledge_ids=("knowledge-shell",),
        used_asset_ids=("asset-logo",),
        missing_knowledge=(),
        conflicts=(),
        binding_status="PASSED",
    )


def test_compiler_builds_deterministic_prompt_from_product_locks_and_creative_variables():
    result = compile_grounded_prompt(
        binding_result=passed_binding(),
        creative_variables={
            "background": "clean white studio",
            "camera_angle": "high angle",
        },
        requested_output="premium commercial product image",
    )

    assert result.grounding_status == "PASSED"
    assert result.product_id == "windbreaker"
    assert result.variant_id == "windbreaker-bob"
    assert result.used_knowledge_ids == ("knowledge-shell",)
    assert result.used_asset_ids == ("asset-logo",)
    assert result.missing_knowledge == ()
    assert result.conflicts == ()
    assert result.prompt_text == (
        "PRODUCT LOCKS:\n"
        "- logo_placement: preserve exact RSV logo placement\n"
        "- shell_geometry: preserve exact shell geometry\n"
        "CREATIVE VARIABLES:\n"
        "- background: clean white studio\n"
        "- camera_angle: high angle\n"
        "REQUESTED OUTPUT:\n"
        "premium commercial product image"
    )


def test_compiler_fails_closed_for_non_passed_binding_without_prompt_text():
    binding = ConstraintBindingResult(
        product_id="windbreaker",
        variant_id=None,
        bound_constraints=(),
        used_knowledge_ids=(),
        used_asset_ids=(),
        missing_knowledge=("knowledge-shell",),
        conflicts=(),
        binding_status="FAILED",
    )

    result = compile_grounded_prompt(
        binding_result=binding,
        creative_variables={"background": "studio"},
        requested_output="product image",
    )

    assert result.grounding_status == "FAILED"
    assert result.prompt_text == ""
    assert result.missing_knowledge == ("knowledge-shell",)


def test_compiler_fails_closed_when_binding_reports_conflicts():
    binding = ConstraintBindingResult(
        product_id="windbreaker",
        variant_id=None,
        bound_constraints=(),
        used_knowledge_ids=(),
        used_asset_ids=(),
        missing_knowledge=(),
        conflicts=("shell_geometry:constraint-a|constraint-b",),
        binding_status="FAILED",
    )

    result = compile_grounded_prompt(
        binding_result=binding,
        creative_variables={},
        requested_output="product image",
    )

    assert result.grounding_status == "FAILED"
    assert result.prompt_text == ""
    assert result.conflicts == (
        "shell_geometry:constraint-a|constraint-b",
    )


def test_compiler_fails_closed_on_creative_variable_collision_with_product_lock():
    result = compile_grounded_prompt(
        binding_result=passed_binding(),
        creative_variables={
            "shell_geometry": "change the shell shape",
            "background": "studio",
        },
        requested_output="product image",
    )

    assert result.grounding_status == "FAILED"
    assert result.prompt_text == ""
    assert result.conflicts == ("creative_override:shell_geometry",)


def test_compiler_is_deterministic_for_equivalent_creative_variable_order():
    first = compile_grounded_prompt(
        binding_result=passed_binding(),
        creative_variables={
            "lighting": "soft light",
            "background": "white",
        },
        requested_output="product image",
    )
    second = compile_grounded_prompt(
        binding_result=passed_binding(),
        creative_variables={
            "background": "white",
            "lighting": "soft light",
        },
        requested_output="product image",
    )

    assert first == second


def test_compiler_inherits_product_variant_and_provenance_exactly():
    binding = passed_binding()

    result = compile_grounded_prompt(
        binding_result=binding,
        creative_variables={},
        requested_output="catalog image",
    )

    assert result.product_id == binding.product_id
    assert result.variant_id == binding.variant_id
    assert result.used_knowledge_ids == binding.used_knowledge_ids
    assert result.used_asset_ids == binding.used_asset_ids


def test_compiler_preserves_product_lock_rule_verbatim():
    exact_rule = "keep visor line EXACT; do not shorten, widen, or redesign it."
    binding = ConstraintBindingResult(
        product_id="windbreaker",
        variant_id=None,
        bound_constraints=(
            constraint(
                "constraint-visor",
                "visor_geometry",
                exact_rule,
                "knowledge-visor",
            ),
        ),
        used_knowledge_ids=("knowledge-visor",),
        used_asset_ids=(),
        missing_knowledge=(),
        conflicts=(),
        binding_status="PASSED",
    )

    result = compile_grounded_prompt(
        binding_result=binding,
        creative_variables={"background": "dark studio"},
        requested_output="product image",
    )

    assert exact_rule in result.prompt_text


def test_compiler_rejects_invalid_creative_variable_values():
    with pytest.raises(
        GroundedPromptCompilerContractError,
        match="creative variable value",
    ):
        compile_grounded_prompt(
            binding_result=passed_binding(),
            creative_variables={"background": ""},
            requested_output="product image",
        )
