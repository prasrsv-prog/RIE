import pytest

from rie.rsv_knowledge import ProductCatalog, ProductRecord, VariantRecord
from rie.rsv_knowledge.constraint_binding import (
    AssetRecord,
    ConstraintBindingContractError,
    ConstraintRecord,
    KnowledgeRecord,
    bind_canonical_constraints,
)


def build_catalog():
    return ProductCatalog(
        products=[ProductRecord("windbreaker", "Windbreaker", "RSV", "active")],
        variants=[
            VariantRecord(
                "windbreaker-bob",
                "windbreaker",
                "Windbreaker Motif Black on Black",
                "active",
            ),
            VariantRecord(
                "windbreaker-black-glossy",
                "windbreaker",
                "Windbreaker Black Glossy",
                "active",
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


def knowledge(knowledge_id, source_asset_id, variant_id=None, status="active"):
    return KnowledgeRecord(
        knowledge_id=knowledge_id,
        product_id="windbreaker",
        variant_id=variant_id,
        knowledge_type="product_detail",
        subject="helmet",
        property="shell",
        value="locked-detail",
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


def test_binding_applies_product_and_exact_variant_constraints_with_provenance():
    result = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        knowledge_records=[
            knowledge("knowledge-shell", "asset-product"),
            knowledge("knowledge-other", "asset-other", "windbreaker-black-glossy"),
        ],
        asset_records=[
            asset("asset-product"),
            asset("asset-variant", "windbreaker-bob"),
            asset("asset-other", "windbreaker-black-glossy"),
        ],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve exact shell geometry",
                "knowledge-shell",
            ),
            constraint(
                "constraint-logo",
                "logo_placement",
                "preserve exact RSV logo placement",
                "asset-variant",
                "windbreaker-bob",
            ),
            constraint(
                "constraint-other",
                "visor",
                "other variant only",
                "knowledge-other",
                "windbreaker-black-glossy",
            ),
        ],
    )

    assert result.binding_status == "PASSED"
    assert tuple(item.constraint_id for item in result.bound_constraints) == (
        "constraint-logo",
        "constraint-shell",
    )
    assert result.used_knowledge_ids == ("knowledge-shell",)
    assert result.used_asset_ids == ("asset-variant",)
    assert result.missing_knowledge == ()
    assert result.conflicts == ()


def test_binding_is_deterministic_for_identical_canonical_inputs():
    catalog = build_catalog()
    assets = [asset("asset-b"), asset("asset-a")]
    constraints = [
        constraint("constraint-b", "visor", "preserve visor", "asset-b"),
        constraint("constraint-a", "logo", "preserve logo", "asset-a"),
    ]

    first = bind_canonical_constraints(
        catalog=catalog,
        product_id="windbreaker",
        variant_id=None,
        knowledge_records=[],
        asset_records=assets,
        constraint_records=constraints,
    )
    second = bind_canonical_constraints(
        catalog=catalog,
        product_id="windbreaker",
        variant_id=None,
        knowledge_records=[],
        asset_records=list(reversed(assets)),
        constraint_records=list(reversed(constraints)),
    )

    assert first == second


def test_binding_fails_closed_when_constraint_provenance_is_missing():
    result = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="windbreaker",
        variant_id=None,
        knowledge_records=[],
        asset_records=[],
        constraint_records=[
            constraint(
                "constraint-shell",
                "shell_geometry",
                "preserve shell",
                "missing-knowledge",
            )
        ],
    )

    assert result.binding_status == "FAILED"
    assert result.bound_constraints == ()
    assert result.used_knowledge_ids == ()
    assert result.used_asset_ids == ()
    assert result.missing_knowledge == ("missing-knowledge",)


def test_binding_fails_closed_on_conflicting_active_product_locks():
    result = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="windbreaker",
        variant_id=None,
        knowledge_records=[],
        asset_records=[asset("asset-a"), asset("asset-b")],
        constraint_records=[
            constraint(
                "constraint-shell-a",
                "shell_geometry",
                "preserve shell A",
                "asset-a",
            ),
            constraint(
                "constraint-shell-b",
                "shell_geometry",
                "preserve shell B",
                "asset-b",
            ),
        ],
    )

    assert result.binding_status == "FAILED"
    assert result.bound_constraints == ()
    assert result.conflicts == (
        "shell_geometry:constraint-shell-a|constraint-shell-b",
    )


def test_binding_does_not_leak_other_variant_constraints():
    result = bind_canonical_constraints(
        catalog=build_catalog(),
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        knowledge_records=[
            knowledge(
                "knowledge-other",
                "asset-other",
                "windbreaker-black-glossy",
            )
        ],
        asset_records=[
            asset("asset-other", "windbreaker-black-glossy"),
        ],
        constraint_records=[
            constraint(
                "constraint-other",
                "visor",
                "other variant only",
                "knowledge-other",
                "windbreaker-black-glossy",
            )
        ],
    )

    assert result.binding_status == "PASSED"
    assert result.bound_constraints == ()
    assert result.used_knowledge_ids == ()


def test_binding_rejects_duplicate_canonical_record_ids():
    duplicate = asset("asset-a")

    with pytest.raises(ConstraintBindingContractError, match="duplicates"):
        bind_canonical_constraints(
            catalog=build_catalog(),
            product_id="windbreaker",
            variant_id=None,
            knowledge_records=[],
            asset_records=[duplicate, duplicate],
            constraint_records=[],
        )


def test_binding_fails_closed_on_unknown_requested_variant():
    with pytest.raises(ConstraintBindingContractError, match="unknown variant_id"):
        bind_canonical_constraints(
            catalog=build_catalog(),
            product_id="windbreaker",
            variant_id="unknown-variant",
            knowledge_records=[],
            asset_records=[],
            constraint_records=[],
        )
