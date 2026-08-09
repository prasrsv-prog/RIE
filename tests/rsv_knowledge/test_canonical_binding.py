import pytest

from rie.rsv_knowledge import (
    CanonicalBinding,
    CanonicalBindingContractError,
    ProductCatalog,
    ProductRecord,
    VariantRecord,
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
            )
        ],
    )


def test_binding_accepts_explicit_ids_and_valid_variant_scope():
    binding = CanonicalBinding(
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        asset_ids=("asset-left-profile",),
        knowledge_ids=("knowledge-shell-geometry",),
        constraint_ids=("constraint-logo-placement",),
    )

    assert binding.validate_against(build_catalog()) is binding
    assert binding.scope_key == ("windbreaker", "windbreaker-bob")


def test_binding_requires_at_least_one_explicit_reference():
    with pytest.raises(CanonicalBindingContractError, match="at least one"):
        CanonicalBinding(
            product_id="windbreaker",
            variant_id=None,
        )


def test_binding_rejects_duplicate_reference_ids():
    with pytest.raises(CanonicalBindingContractError, match="duplicates"):
        CanonicalBinding(
            product_id="windbreaker",
            variant_id=None,
            asset_ids=("asset-a", "asset-a"),
        )


def test_binding_fails_closed_on_unknown_variant():
    binding = CanonicalBinding(
        product_id="windbreaker",
        variant_id="unknown-variant",
        asset_ids=("asset-a",),
    )

    with pytest.raises(CanonicalBindingContractError, match="unknown variant_id"):
        binding.validate_against(build_catalog())
