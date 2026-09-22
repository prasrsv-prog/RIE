from __future__ import annotations

import hashlib
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from rie.application.visual_reference_asset_query import (
    VisualReferenceAssetQuery,
    VisualReferenceAssetQueryContractError,
)


_FIELDS = (
    "SOURCE_RELATIVE_PATH",
    "PRODUCT_FAMILY",
    "VARIANT_NAME",
    "SOURCE_TYPE",
    "AUTHORITY",
    "VERSION",
    "STATUS",
    "NOTES",
)


class _FakeProductQuery:
    def list_products(self):
        return (
            SimpleNamespace(product_id="sv300", label="SV300"),
            SimpleNamespace(product_id="ffs21", label="FFS21"),
        )

    def list_variants(self, product_id: str):
        if product_id == "sv300":
            return (
                SimpleNamespace(
                    variant_id="sv300-white-glossy",
                    product_id="sv300",
                    label="White Glossy",
                ),
                SimpleNamespace(
                    variant_id="sv300-black-glossy",
                    product_id="sv300",
                    label="Black Glossy",
                ),
            )
        return (
            SimpleNamespace(
                variant_id="ffs21-black",
                product_id="ffs21",
                label="Black",
            ),
        )


def _write_manifest(root: Path, rows: tuple[tuple[str, ...], ...]) -> None:
    lines = ["\t".join(_FIELDS)]
    lines.extend("\t".join(row) for row in rows)
    (root / "pilot-source-intake-manifest.tsv").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _photo_row(path: str, variant: str = "White Glossy") -> tuple[str, ...]:
    return (
        path,
        "SV300",
        variant,
        "APPROVED_PRODUCT_PHOTO",
        "RSV_INTERNAL_APPROVED_SOURCE",
        "2026-08-09",
        "APPROVED",
        "",
    )


def test_lists_only_approved_photo_scope_and_uses_content_hash_identity(
    tmp_path: Path,
) -> None:
    variant_photo = tmp_path / "SV300" / "White Glossy" / "front.png"
    variant_photo.parent.mkdir(parents=True)
    variant_photo.write_bytes(b"variant-photo")
    product_photo = tmp_path / "SV300" / "hero.png"
    product_photo.write_bytes(b"product-photo")
    document = tmp_path / "SV300" / "manual.pdf"
    document.write_bytes(b"manual")

    _write_manifest(
        tmp_path,
        (
            _photo_row("SV300/White Glossy/front.png"),
            _photo_row("SV300/hero.png", "<PRODUCT_LEVEL>"),
            (
                "SV300/manual.pdf",
                "SV300",
                "<PRODUCT_LEVEL>",
                "OFFICIAL_PRODUCT_DOCUMENT",
                "RSV_INTERNAL_APPROVED_SOURCE",
                "2026-08-09",
                "APPROVED",
                "Product-level official manual",
            ),
        ),
    )

    query = VisualReferenceAssetQuery(
        intake_root=tmp_path,
        product_intelligence_query=_FakeProductQuery(),
    )
    assets = query.list_assets(
        product_id="sv300",
        variant_id="sv300-white-glossy",
    )

    assert len(assets) == 2
    by_path = {item.source_relative_path: item for item in assets}
    variant = by_path["SV300/White Glossy/front.png"]
    product = by_path["SV300/hero.png"]
    assert variant.variant_id == "sv300-white-glossy"
    assert product.variant_id is None
    assert variant.available
    expected_sha = hashlib.sha256(b"variant-photo").hexdigest()
    assert variant.sha256 == expected_sha
    assert variant.asset_id == f"asset-{expected_sha}"
    assert query.load_preview_bytes(variant.asset_id) == b"variant-photo"


def test_unavailable_photo_is_visible_but_has_no_selectable_asset_id(
    tmp_path: Path,
) -> None:
    _write_manifest(
        tmp_path,
        (_photo_row("SV300/White Glossy/missing.png"),),
    )
    query = VisualReferenceAssetQuery(
        intake_root=tmp_path,
        product_intelligence_query=_FakeProductQuery(),
    )
    asset = query.list_assets(
        product_id="sv300",
        variant_id="sv300-white-glossy",
    )[0]
    assert not asset.available
    assert asset.asset_id is None
    assert asset.sha256 == ""


def test_preview_fails_closed_when_asset_bytes_drift(tmp_path: Path) -> None:
    photo = tmp_path / "SV300" / "White Glossy" / "front.png"
    photo.parent.mkdir(parents=True)
    photo.write_bytes(b"approved-photo")
    _write_manifest(
        tmp_path,
        (_photo_row("SV300/White Glossy/front.png"),),
    )
    query = VisualReferenceAssetQuery(
        intake_root=tmp_path,
        product_intelligence_query=_FakeProductQuery(),
    )
    asset = query.list_assets(
        product_id="sv300",
        variant_id="sv300-white-glossy",
    )[0]
    assert asset.asset_id is not None
    photo.write_bytes(b"changed-photo")
    with pytest.raises(
        VisualReferenceAssetQueryContractError,
        match="content drift",
    ):
        query.load_preview_bytes(asset.asset_id)


def test_unknown_manifest_product_or_variant_fails_closed(tmp_path: Path) -> None:
    photo = tmp_path / "SV300" / "Unknown" / "front.png"
    photo.parent.mkdir(parents=True)
    photo.write_bytes(b"photo")
    _write_manifest(
        tmp_path,
        (_photo_row("SV300/Unknown/front.png", "Unknown"),),
    )
    with pytest.raises(
        VisualReferenceAssetQueryContractError,
        match="unknown variant label",
    ):
        VisualReferenceAssetQuery(
            intake_root=tmp_path,
            product_intelligence_query=_FakeProductQuery(),
        )


def test_manifest_path_escape_is_rejected(tmp_path: Path) -> None:
    _write_manifest(tmp_path, (_photo_row("../outside.png"),))
    with pytest.raises(
        VisualReferenceAssetQueryContractError,
        match="escapes intake_root",
    ):
        VisualReferenceAssetQuery(
            intake_root=tmp_path,
            product_intelligence_query=_FakeProductQuery(),
        )


def test_unknown_product_or_variant_query_fails_closed(tmp_path: Path) -> None:
    _write_manifest(tmp_path, ())
    query = VisualReferenceAssetQuery(
        intake_root=tmp_path,
        product_intelligence_query=_FakeProductQuery(),
    )
    with pytest.raises(VisualReferenceAssetQueryContractError, match="product_id"):
        query.list_assets(product_id="missing")
    with pytest.raises(VisualReferenceAssetQueryContractError, match="variant_id"):
        query.list_assets(product_id="sv300", variant_id="missing")

def test_real_pilot_exposes_exact_approved_photo_set_when_intake_is_available() -> None:
    configured = os.environ.get("RCIS_TEST_INTAKE_ROOT", "").strip()
    if not configured:
        pytest.skip("RCIS_TEST_INTAKE_ROOT is not configured")
    root = Path(configured)
    if not root.is_dir():
        pytest.skip("configured RCIS_TEST_INTAKE_ROOT is unavailable")

    query = VisualReferenceAssetQuery.from_intake_root(intake_root=root)
    by_reference = {}
    for product in query.product_options:
        variants = query.variant_options_for_product(product.product_id)
        for variant in variants:
            for asset in query.list_assets(
                product_id=product.product_id,
                variant_id=variant.variant_id,
            ):
                by_reference.setdefault(asset.reference_id, asset)

    assert len(by_reference) == 109
    assert all(item.source_type == "APPROVED_PRODUCT_PHOTO" for item in by_reference.values())
    assert all(item.status == "APPROVED" for item in by_reference.values())
    assert all(item.available for item in by_reference.values())
    asset_ids = tuple(item.asset_id for item in by_reference.values())
    assert all(asset_ids)
    assert len(asset_ids) == len(set(asset_ids))
