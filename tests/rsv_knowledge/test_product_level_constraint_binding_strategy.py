"""Targeted proof for native product-level constraint binding semantics."""

from rie.rsv_knowledge import ProductCatalog, ProductRecord, VariantRecord
from rie.rsv_knowledge.constraint_binding import (
    AssetRecord,
    ConstraintRecord,
    bind_canonical_constraints,
)


def catalog():
    return ProductCatalog(
        products=[
            ProductRecord("product-a", "Product A", "RSV", "active"),
            ProductRecord("product-b", "Product B", "RSV", "active"),
        ],
        variants=[
            VariantRecord("product-a-v1", "product-a", "Product A V1", "active"),
            VariantRecord("product-a-v2", "product-a", "Product A V2", "active"),
            VariantRecord("product-b-v1", "product-b", "Product B V1", "active"),
        ],
    )


def asset(asset_id, product_id, variant_id=None):
    return AssetRecord(
        asset_id=asset_id,
        product_id=product_id,
        variant_id=variant_id,
        asset_type="synthetic-proof",
        canonical_path=f"synthetic/{asset_id}",
        sha256="a" * 64,
        source="SYNTHETIC_TEST_ONLY",
        authority="SYNTHETIC_TEST_ONLY",
        version="1",
        status="approved",
    )


def constraint(
    constraint_id,
    product_id,
    constraint_type,
    rule,
    source_id,
    variant_id=None,
):
    return ConstraintRecord(
        constraint_id=constraint_id,
        product_id=product_id,
        variant_id=variant_id,
        constraint_type=constraint_type,
        rule=rule,
        source_knowledge_id_or_asset_id=source_id,
        status="active",
    )


def test_product_level_constraint_binds_to_each_variant_of_same_product():
    source = asset("asset-product-a", "product-a")
    lock = constraint(
        "constraint-product-a-material",
        "product-a",
        "helmet_body_material",
        "preserve synthetic material",
        source.asset_id,
    )

    first = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[source],
        constraint_records=[lock],
    )
    second = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v2",
        knowledge_records=[],
        asset_records=[source],
        constraint_records=[lock],
    )

    assert first.binding_status == "PASSED"
    assert second.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in first.bound_constraints) == (
        "constraint-product-a-material",
    )
    assert tuple(item.constraint_id for item in second.bound_constraints) == (
        "constraint-product-a-material",
    )
    assert first.used_asset_ids == ("asset-product-a",)
    assert second.used_asset_ids == ("asset-product-a",)


def test_product_level_constraint_does_not_bind_cross_product():
    source_a = asset("asset-product-a", "product-a")
    source_b = asset("asset-product-b", "product-b")
    product_b_lock = constraint(
        "constraint-product-b-material",
        "product-b",
        "helmet_body_material",
        "preserve synthetic product B material",
        source_b.asset_id,
    )

    result = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[source_a, source_b],
        constraint_records=[product_b_lock],
    )

    assert result.binding_status == "PASSED"
    assert result.bound_constraints == ()
    assert result.used_asset_ids == ()
    assert result.conflicts == ()


def test_variant_level_constraint_remains_sibling_variant_isolated():
    source = asset("asset-product-a-v1", "product-a", "product-a-v1")
    variant_lock = constraint(
        "constraint-product-a-v1-logo",
        "product-a",
        "logo_placement",
        "preserve synthetic V1 logo placement",
        source.asset_id,
        "product-a-v1",
    )

    matching = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[source],
        constraint_records=[variant_lock],
    )
    sibling = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v2",
        knowledge_records=[],
        asset_records=[source],
        constraint_records=[variant_lock],
    )

    assert matching.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in matching.bound_constraints) == (
        "constraint-product-a-v1-logo",
    )
    assert sibling.binding_status == "PASSED"
    assert sibling.bound_constraints == ()
    assert sibling.used_asset_ids == ()


def test_product_and_variant_constraints_coexist_deterministically():
    product_source = asset("asset-product-a", "product-a")
    variant_source = asset("asset-product-a-v1", "product-a", "product-a-v1")
    product_lock = constraint(
        "constraint-product-a-material",
        "product-a",
        "helmet_body_material",
        "preserve synthetic material",
        product_source.asset_id,
    )
    variant_lock = constraint(
        "constraint-product-a-v1-logo",
        "product-a",
        "logo_placement",
        "preserve synthetic V1 logo placement",
        variant_source.asset_id,
        "product-a-v1",
    )

    first = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[variant_source, product_source],
        constraint_records=[variant_lock, product_lock],
    )
    second = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[product_source, variant_source],
        constraint_records=[product_lock, variant_lock],
    )

    assert first == second
    assert first.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in first.bound_constraints) == (
        "constraint-product-a-material",
        "constraint-product-a-v1-logo",
    )
    assert first.used_asset_ids == (
        "asset-product-a",
        "asset-product-a-v1",
    )


def test_product_and_variant_same_type_different_rules_fail_closed_without_precedence():
    product_source = asset("asset-product-a", "product-a")
    variant_source = asset("asset-product-a-v1", "product-a", "product-a-v1")
    product_lock = constraint(
        "constraint-product-a-material",
        "product-a",
        "helmet_body_material",
        "preserve synthetic product material",
        product_source.asset_id,
    )
    variant_lock = constraint(
        "constraint-product-a-v1-material",
        "product-a",
        "helmet_body_material",
        "preserve different synthetic variant material",
        variant_source.asset_id,
        "product-a-v1",
    )

    result = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id="product-a-v1",
        knowledge_records=[],
        asset_records=[product_source, variant_source],
        constraint_records=[variant_lock, product_lock],
    )

    assert result.binding_status == "FAILED"
    assert result.bound_constraints == ()
    assert result.used_asset_ids == ()
    assert result.conflicts == (
        "helmet_body_material:"
        "constraint-product-a-material|constraint-product-a-v1-material",
    )


def test_product_level_request_binds_product_scope_and_excludes_variant_scope():
    product_source = asset("asset-product-a", "product-a")
    variant_source = asset("asset-product-a-v1", "product-a", "product-a-v1")
    product_lock = constraint(
        "constraint-product-a-material",
        "product-a",
        "helmet_body_material",
        "preserve synthetic material",
        product_source.asset_id,
    )
    variant_lock = constraint(
        "constraint-product-a-v1-logo",
        "product-a",
        "logo_placement",
        "preserve synthetic V1 logo placement",
        variant_source.asset_id,
        "product-a-v1",
    )

    result = bind_canonical_constraints(
        catalog=catalog(),
        product_id="product-a",
        variant_id=None,
        knowledge_records=[],
        asset_records=[product_source, variant_source],
        constraint_records=[product_lock, variant_lock],
    )

    assert result.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in result.bound_constraints) == (
        "constraint-product-a-material",
    )
    assert result.used_asset_ids == ("asset-product-a",)
