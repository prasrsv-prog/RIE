from rie.rsv_knowledge import ProductCatalog, ProductRecord, VariantRecord
from rie.rsv_knowledge.constraint_binding import (
    AssetRecord,
    ConstraintRecord,
    KnowledgeRecord,
    bind_canonical_constraints,
)
from rie.rsv_knowledge.grounded_prompt_compiler import compile_grounded_prompt


def build_catalog():
    return ProductCatalog(
        products=[
            ProductRecord(
                product_id="windbreaker",
                canonical_name="Windbreaker",
                brand="RSV",
                status="active",
            )
        ],
        variants=[
            VariantRecord(
                variant_id="windbreaker-bob",
                product_id="windbreaker",
                canonical_name="Windbreaker Motif Black on Black",
                status="active",
            ),
            VariantRecord(
                variant_id="windbreaker-black-glossy",
                product_id="windbreaker",
                canonical_name="Windbreaker Black Glossy",
                status="active",
            ),
        ],
    )


def asset(asset_id, variant_id=None, status="approved"):
    return AssetRecord(
        asset_id=asset_id,
        product_id="windbreaker",
        variant_id=variant_id,
        asset_type="image",
        canonical_path=f"assets/{asset_id}.jpg",
        sha256="a" * 64,
        source="RSV_INTERNAL",
        authority="APPROVED_PRODUCT_REFERENCE",
        version="1",
        status=status,
    )


def knowledge(
    knowledge_id,
    source_asset_id,
    variant_id=None,
    value="canonical product detail",
    status="active",
):
    return KnowledgeRecord(
        knowledge_id=knowledge_id,
        product_id="windbreaker",
        variant_id=variant_id,
        knowledge_type="product_detail",
        subject="helmet",
        property="product_lock",
        value=value,
        source_asset_id=source_asset_id,
        authority="APPROVED_PRODUCT_REFERENCE",
        version="1",
        status=status,
    )


def constraint(
    constraint_id,
    constraint_type,
    rule,
    source_id,
    variant_id=None,
    status="active",
):
    return ConstraintRecord(
        constraint_id=constraint_id,
        product_id="windbreaker",
        variant_id=variant_id,
        constraint_type=constraint_type,
        rule=rule,
        source_knowledge_id_or_asset_id=source_id,
        status=status,
    )


def run_pipeline(
    *,
    variant_id,
    knowledge_records,
    asset_records,
    constraint_records,
    creative_variables,
    requested_output,
):
    binding = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="windbreaker",
        variant_id=variant_id,
        knowledge_records=knowledge_records,
        asset_records=asset_records,
        constraint_records=constraint_records,
    )
    compiled = compile_grounded_prompt(
        binding_result=binding,
        creative_variables=creative_variables,
        requested_output=requested_output,
    )
    return binding, compiled


def test_end_to_end_success_preserves_exact_variant_locks_and_provenance():
    shell_rule = "preserve exact shell geometry"
    logo_rule = "preserve exact RSV logo placement"

    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[
            knowledge(
                "knowledge-shell",
                "asset-product",
                value="shell geometry reference",
            )
        ],
        asset_records=[
            asset("asset-product"),
            asset("asset-logo", "windbreaker-bob"),
        ],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                shell_rule,
                "knowledge-shell",
            ),
            constraint(
                "constraint-logo",
                "logo_placement",
                logo_rule,
                "asset-logo",
                "windbreaker-bob",
            ),
        ],
        creative_variables={
            "background": "clean white studio",
            "camera_angle": "high angle",
        },
        requested_output="premium commercial product image",
    )

    assert binding.binding_status == "PASSED"
    assert compiled.grounding_status == "PASSED"
    assert compiled.product_id == "windbreaker"
    assert compiled.variant_id == "windbreaker-bob"
    assert compiled.used_knowledge_ids == ("knowledge-shell",)
    assert compiled.used_asset_ids == ("asset-logo",)
    assert compiled.missing_knowledge == ()
    assert compiled.conflicts == ()
    assert shell_rule in compiled.prompt_text
    assert logo_rule in compiled.prompt_text
    assert "- background: clean white studio" in compiled.prompt_text
    assert "- camera_angle: high angle" in compiled.prompt_text
    assert compiled.prompt_text.endswith("premium commercial product image")


def test_end_to_end_other_variant_records_do_not_leak():
    other_rule = "other variant visor rule"

    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[
            knowledge(
                "knowledge-bob",
                "asset-bob",
                "windbreaker-bob",
            ),
            knowledge(
                "knowledge-other",
                "asset-other",
                "windbreaker-black-glossy",
            ),
        ],
        asset_records=[
            asset("asset-bob", "windbreaker-bob"),
            asset("asset-other", "windbreaker-black-glossy"),
        ],
        constraint_records=[
            constraint(
                "constraint-bob",
                "shell_geometry",
                "BOB shell lock",
                "knowledge-bob",
                "windbreaker-bob",
            ),
            constraint(
                "constraint-other",
                "visor_geometry",
                other_rule,
                "knowledge-other",
                "windbreaker-black-glossy",
            ),
        ],
        creative_variables={"background": "studio"},
        requested_output="product image",
    )

    assert binding.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in binding.bound_constraints) == (
        "constraint-bob",
    )
    assert binding.used_knowledge_ids == ("knowledge-bob",)
    assert compiled.grounding_status == "PASSED"
    assert other_rule not in compiled.prompt_text
    assert "knowledge-other" not in compiled.used_knowledge_ids


def test_end_to_end_missing_canonical_provenance_fails_closed_without_prompt():
    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[],
        asset_records=[],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve shell",
                "missing-source",
                "windbreaker-bob",
            )
        ],
        creative_variables={"background": "studio"},
        requested_output="product image",
    )

    assert binding.binding_status == "FAILED"
    assert binding.missing_knowledge == ("missing-source",)
    assert compiled.grounding_status == "FAILED"
    assert compiled.prompt_text == ""
    assert compiled.missing_knowledge == ("missing-source",)


def test_end_to_end_conflicting_active_product_locks_fail_closed_without_prompt():
    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[],
        asset_records=[
            asset("asset-a", "windbreaker-bob"),
            asset("asset-b", "windbreaker-bob"),
        ],
        constraint_records=[
            constraint(
                "constraint-shell-a",
                "shell_geometry",
                "preserve shell A",
                "asset-a",
                "windbreaker-bob",
            ),
            constraint(
                "constraint-shell-b",
                "shell_geometry",
                "preserve shell B",
                "asset-b",
                "windbreaker-bob",
            ),
        ],
        creative_variables={},
        requested_output="product image",
    )

    assert binding.binding_status == "FAILED"
    assert binding.conflicts == (
        "shell_geometry:constraint-shell-a|constraint-shell-b",
    )
    assert compiled.grounding_status == "FAILED"
    assert compiled.prompt_text == ""
    assert compiled.conflicts == binding.conflicts


def test_end_to_end_creative_override_of_product_lock_fails_closed():
    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[],
        asset_records=[asset("asset-shell", "windbreaker-bob")],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve exact shell geometry",
                "asset-shell",
                "windbreaker-bob",
            )
        ],
        creative_variables={
            "SHELL_GEOMETRY": "redesign the shell",
            "background": "studio",
        },
        requested_output="product image",
    )

    assert binding.binding_status == "PASSED"
    assert compiled.grounding_status == "FAILED"
    assert compiled.prompt_text == ""
    assert compiled.conflicts == ("creative_override:SHELL_GEOMETRY",)


def test_end_to_end_pipeline_is_deterministic_for_equivalent_input_order():
    knowledge_records = [
        knowledge("knowledge-shell", "asset-shell"),
    ]
    asset_records = [
        asset("asset-logo", "windbreaker-bob"),
        asset("asset-shell"),
    ]
    constraint_records = [
        constraint(
            "constraint-shell",
            "shell_geometry",
            "preserve shell",
            "knowledge-shell",
        ),
        constraint(
            "constraint-logo",
            "logo_placement",
            "preserve logo",
            "asset-logo",
            "windbreaker-bob",
        ),
    ]

    first = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=knowledge_records,
        asset_records=asset_records,
        constraint_records=constraint_records,
        creative_variables={"lighting": "soft", "background": "white"},
        requested_output="product image",
    )
    second = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=list(reversed(knowledge_records)),
        asset_records=list(reversed(asset_records)),
        constraint_records=list(reversed(constraint_records)),
        creative_variables={"background": "white", "lighting": "soft"},
        requested_output="product image",
    )

    assert first == second


def test_end_to_end_final_result_exposes_required_auditability_fields():
    binding, compiled = run_pipeline(
        variant_id=None,
        knowledge_records=[
            knowledge("knowledge-shell", "asset-shell"),
        ],
        asset_records=[asset("asset-shell")],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve exact shell",
                "knowledge-shell",
            ),
        ],
        creative_variables={},
        requested_output="catalog image",
    )

    assert binding.binding_status == "PASSED"
    assert compiled.grounding_status == "PASSED"
    assert compiled.product_id == "windbreaker"
    assert compiled.variant_id is None
    assert compiled.used_knowledge_ids == ("knowledge-shell",)
    assert compiled.used_asset_ids == ()
    assert compiled.missing_knowledge == ()
    assert compiled.conflicts == ()
    assert compiled.prompt_text


def test_end_to_end_does_not_infer_unbound_knowledge_value_into_prompt():
    unbound_value = "invented-looking detail that is not a bound constraint rule"
    explicit_rule = "preserve exact shell geometry"

    binding, compiled = run_pipeline(
        variant_id="windbreaker-bob",
        knowledge_records=[
            knowledge(
                "knowledge-shell",
                "asset-shell",
                value=unbound_value,
            ),
        ],
        asset_records=[asset("asset-shell")],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                explicit_rule,
                "knowledge-shell",
            )
        ],
        creative_variables={"background": "neutral studio"},
        requested_output="product image",
    )

    assert binding.binding_status == "PASSED"
    assert compiled.grounding_status == "PASSED"
    assert explicit_rule in compiled.prompt_text
    assert unbound_value not in compiled.prompt_text
