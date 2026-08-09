import pytest

from rie.rsv_knowledge import (
    IngestionManifestContractError,
    IngestionManifestRecord,
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


def test_manifest_accepts_explicit_metadata_without_inferring_product_facts():
    record = IngestionManifestRecord(
        source_path=r"D:\RSV\Windbreaker\bob-left.jpg",
        source_sha256="a" * 64,
        product_id="windbreaker",
        variant_id="windbreaker-bob",
        knowledge_type="visual_reference",
        asset_type="image",
        source="RSV_INTERNAL",
        authority="APPROVED_PRODUCT_REFERENCE",
        version="1",
        status="active",
    )

    assert record.validate_against(build_catalog()) is record
    assert record.source_sha256 == "a" * 64
    assert record.canonical_key[0:2] == ("windbreaker", "windbreaker-bob")


def test_manifest_rejects_invalid_sha256():
    with pytest.raises(IngestionManifestContractError, match="64 hexadecimal"):
        IngestionManifestRecord(
            source_path="source.jpg",
            source_sha256="not-a-sha",
            product_id="windbreaker",
            variant_id=None,
            knowledge_type="visual_reference",
            asset_type="image",
            source="RSV_INTERNAL",
            authority="APPROVED_PRODUCT_REFERENCE",
            version="1",
            status="active",
        )


def test_manifest_fails_closed_on_cross_product_variant_binding():
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

    record = IngestionManifestRecord(
        source_path="source.jpg",
        source_sha256="b" * 64,
        product_id="sv300",
        variant_id="windbreaker-bob",
        knowledge_type="visual_reference",
        asset_type="image",
        source="RSV_INTERNAL",
        authority="APPROVED_PRODUCT_REFERENCE",
        version="1",
        status="active",
    )

    with pytest.raises(IngestionManifestContractError, match="does not belong"):
        record.validate_against(catalog)
