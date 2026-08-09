import pytest

from rie.rsv_knowledge import (
    ProductCatalog,
    ProductCatalogContractError,
    ProductRecord,
    VariantRecord,
)


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
            )
        ],
    )


def test_catalog_resolves_product_and_owned_variant():
    catalog = build_catalog()

    assert catalog.require_product("windbreaker").canonical_name == "Windbreaker"
    assert (
        catalog.require_variant("windbreaker", "windbreaker-bob").product_id
        == "windbreaker"
    )
    assert catalog.require_variant("windbreaker", None) is None


def test_catalog_fails_closed_on_duplicate_product_id():
    product = ProductRecord("windbreaker", "Windbreaker", "RSV", "active")

    with pytest.raises(ProductCatalogContractError, match="duplicate product_id"):
        ProductCatalog(products=[product, product], variants=[])


def test_catalog_fails_closed_on_unknown_variant_product():
    variant = VariantRecord(
        "windbreaker-bob",
        "unknown-product",
        "Windbreaker Motif Black on Black",
        "active",
    )

    with pytest.raises(ProductCatalogContractError, match="unknown product_id"):
        ProductCatalog(products=[], variants=[variant])


def test_catalog_fails_closed_on_cross_product_variant_resolution():
    catalog = ProductCatalog(
        products=[
            ProductRecord("windbreaker", "Windbreaker", "RSV", "active"),
            ProductRecord("sv300", "SV300", "RSV", "active"),
        ],
        variants=[
            VariantRecord(
                "windbreaker-bob",
                "windbreaker",
                "Windbreaker Motif Black on Black",
                "active",
            )
        ],
    )

    with pytest.raises(ProductCatalogContractError, match="does not belong"):
        catalog.require_variant("sv300", "windbreaker-bob")
