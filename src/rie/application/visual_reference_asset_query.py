"""Framework-neutral read-only visual-reference asset query for PC4."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rie.application.product_intelligence_query import ProductIntelligenceQuery


class VisualReferenceAssetQueryContractError(ValueError):
    """Fail-closed contract error for visual-reference asset reads."""


@dataclass(frozen=True)
class VisualReferenceAsset:
    reference_id: str
    asset_id: str | None
    product_id: str
    variant_id: str | None
    product_label: str
    variant_label: str
    filename: str
    source_relative_path: str
    source_type: str
    authority: str
    version: str
    status: str
    sha256: str
    available: bool


_EXPECTED_MANIFEST_FIELDS = (
    "SOURCE_RELATIVE_PATH",
    "PRODUCT_FAMILY",
    "VARIANT_NAME",
    "SOURCE_TYPE",
    "AUTHORITY",
    "VERSION",
    "STATUS",
    "NOTES",
)
_PRODUCT_LEVEL_VARIANT = "<PRODUCT_LEVEL>"
_APPROVED_PRODUCT_PHOTO = "APPROVED_PRODUCT_PHOTO"
_APPROVED_STATUS = "APPROVED"


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise VisualReferenceAssetQueryContractError(
            f"{field_name} must be a nonempty string"
        )
    return value.strip()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _reference_id(source_relative_path: str) -> str:
    digest = hashlib.sha256(source_relative_path.encode("utf-8")).hexdigest()
    return f"reference-{digest}"


class VisualReferenceAssetQuery:
    """Read approved product photos through an application-facing PC4 boundary."""

    def __init__(
        self,
        *,
        intake_root: str | Path,
        product_intelligence_query: Any,
    ) -> None:
        if not isinstance(intake_root, (str, Path)):
            raise VisualReferenceAssetQueryContractError(
                "intake_root must be str or Path"
            )
        root = Path(intake_root).resolve()
        if not root.is_dir():
            raise VisualReferenceAssetQueryContractError(
                "intake_root must identify an existing directory"
            )
        for method_name in ("list_products", "list_variants"):
            if not callable(getattr(product_intelligence_query, method_name, None)):
                raise VisualReferenceAssetQueryContractError(
                    "product_intelligence_query must expose list_products and "
                    "list_variants"
                )

        self._root = root
        self._product_intelligence_query = product_intelligence_query
        self._products = tuple(product_intelligence_query.list_products())
        self._products_by_id = {
            _required_text(item.product_id, "product_id"): item
            for item in self._products
        }
        self._product_ids_by_label = self._unique_label_index(
            self._products,
            id_field="product_id",
            label_field="label",
            label="product",
        )
        self._variants_by_product: dict[str, tuple[Any, ...]] = {}
        self._variant_ids_by_product_label: dict[str, dict[str, str]] = {}
        for product_id in self._products_by_id:
            variants = tuple(product_intelligence_query.list_variants(product_id))
            self._variants_by_product[product_id] = variants
            self._variant_ids_by_product_label[product_id] = self._unique_label_index(
                variants,
                id_field="variant_id",
                label_field="label",
                label=f"variant for {product_id}",
            )

        self._assets = self._load_manifest_assets()
        self._assets_by_id = {
            item.asset_id: item
            for item in self._assets
            if item.asset_id is not None
        }
        if len(self._assets_by_id) != sum(
            1 for item in self._assets if item.asset_id is not None
        ):
            raise VisualReferenceAssetQueryContractError(
                "approved product photo asset IDs must be unique"
            )

    @classmethod
    def from_intake_root(
        cls,
        *,
        intake_root: str | Path,
    ) -> "VisualReferenceAssetQuery":
        product_query = ProductIntelligenceQuery.from_intake_root(
            intake_root=intake_root
        )
        return cls(
            intake_root=intake_root,
            product_intelligence_query=product_query,
        )

    @staticmethod
    def _unique_label_index(
        values: tuple[Any, ...],
        *,
        id_field: str,
        label_field: str,
        label: str,
    ) -> dict[str, str]:
        output: dict[str, str] = {}
        for item in values:
            item_id = _required_text(getattr(item, id_field, None), id_field)
            display_label = _required_text(
                getattr(item, label_field, None),
                label_field,
            )
            if display_label in output:
                raise VisualReferenceAssetQueryContractError(
                    f"duplicate {label} presentation label: {display_label}"
                )
            output[display_label] = item_id
        return output

    @property
    def product_options(self) -> tuple[Any, ...]:
        return self._products

    def variant_options_for_product(self, product_id: str) -> tuple[Any, ...]:
        product_id = _required_text(product_id, "product_id")
        if product_id not in self._products_by_id:
            raise VisualReferenceAssetQueryContractError(
                f"unknown active product_id: {product_id}"
            )
        return self._variants_by_product[product_id]

    def list_assets(
        self,
        *,
        product_id: str,
        variant_id: str | None = None,
    ) -> tuple[VisualReferenceAsset, ...]:
        product_id = _required_text(product_id, "product_id")
        if product_id not in self._products_by_id:
            raise VisualReferenceAssetQueryContractError(
                f"unknown active product_id: {product_id}"
            )
        if variant_id is not None:
            variant_id = _required_text(variant_id, "variant_id")
            valid_ids = {
                _required_text(item.variant_id, "variant_id")
                for item in self._variants_by_product[product_id]
            }
            if variant_id not in valid_ids:
                raise VisualReferenceAssetQueryContractError(
                    f"unknown active variant_id for {product_id}: {variant_id}"
                )

        return tuple(
            item
            for item in self._assets
            if item.product_id == product_id
            and (
                variant_id is None
                or item.variant_id is None
                or item.variant_id == variant_id
            )
        )

    def get_asset(self, asset_id: str) -> VisualReferenceAsset:
        asset_id = _required_text(asset_id, "asset_id")
        if asset_id not in self._assets_by_id:
            raise VisualReferenceAssetQueryContractError(
                f"unknown available asset_id: {asset_id}"
            )
        return self._assets_by_id[asset_id]

    def load_preview_bytes(self, asset_id: str) -> bytes:
        asset = self.get_asset(asset_id)
        path = self._resolve_source_path(asset.source_relative_path)
        if not path.is_file():
            raise VisualReferenceAssetQueryContractError(
                f"visual reference asset is unavailable: {asset_id}"
            )
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != asset.sha256:
            raise VisualReferenceAssetQueryContractError(
                f"visual reference asset content drift: {asset_id}"
            )
        return payload

    def _resolve_source_path(self, source_relative_path: str) -> Path:
        relative = Path(_required_text(source_relative_path, "SOURCE_RELATIVE_PATH"))
        if relative.is_absolute():
            raise VisualReferenceAssetQueryContractError(
                "SOURCE_RELATIVE_PATH must be relative"
            )
        resolved = (self._root / relative).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError as exc:
            raise VisualReferenceAssetQueryContractError(
                "SOURCE_RELATIVE_PATH escapes intake_root"
            ) from exc
        return resolved

    def _load_manifest_assets(self) -> tuple[VisualReferenceAsset, ...]:
        manifest_path = self._root / "pilot-source-intake-manifest.tsv"
        if not manifest_path.is_file():
            raise VisualReferenceAssetQueryContractError(
                "pilot-source-intake-manifest.tsv is required"
            )

        with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            fields = tuple(reader.fieldnames or ())
            if fields != _EXPECTED_MANIFEST_FIELDS:
                raise VisualReferenceAssetQueryContractError(
                    "pilot source manifest field contract mismatch"
                )
            rows = tuple(reader)

        output: list[VisualReferenceAsset] = []
        seen_references: set[str] = set()
        for index, row in enumerate(rows, start=2):
            source_type = _required_text(row.get("SOURCE_TYPE"), "SOURCE_TYPE")
            if source_type != _APPROVED_PRODUCT_PHOTO:
                continue
            status = _required_text(row.get("STATUS"), "STATUS")
            if status != _APPROVED_STATUS:
                continue

            source_relative_path = _required_text(
                row.get("SOURCE_RELATIVE_PATH"),
                "SOURCE_RELATIVE_PATH",
            )
            reference_id = _reference_id(source_relative_path)
            if reference_id in seen_references:
                raise VisualReferenceAssetQueryContractError(
                    f"duplicate visual reference path at manifest line {index}"
                )
            seen_references.add(reference_id)

            product_label = _required_text(
                row.get("PRODUCT_FAMILY"),
                "PRODUCT_FAMILY",
            )
            if product_label not in self._product_ids_by_label:
                raise VisualReferenceAssetQueryContractError(
                    f"unknown product label in visual reference manifest: {product_label}"
                )
            product_id = self._product_ids_by_label[product_label]

            variant_label = _required_text(row.get("VARIANT_NAME"), "VARIANT_NAME")
            if variant_label == _PRODUCT_LEVEL_VARIANT:
                variant_id = None
            else:
                variant_index = self._variant_ids_by_product_label[product_id]
                if variant_label not in variant_index:
                    raise VisualReferenceAssetQueryContractError(
                        "unknown variant label in visual reference manifest: "
                        f"{product_label} / {variant_label}"
                    )
                variant_id = variant_index[variant_label]

            path = self._resolve_source_path(source_relative_path)
            available = path.is_file()
            source_sha256 = _sha256_file(path) if available else ""
            asset_id = f"asset-{source_sha256}" if available else None

            output.append(
                VisualReferenceAsset(
                    reference_id=reference_id,
                    asset_id=asset_id,
                    product_id=product_id,
                    variant_id=variant_id,
                    product_label=product_label,
                    variant_label=variant_label,
                    filename=Path(source_relative_path).name,
                    source_relative_path=source_relative_path,
                    source_type=source_type,
                    authority=_required_text(row.get("AUTHORITY"), "AUTHORITY"),
                    version=_required_text(row.get("VERSION"), "VERSION"),
                    status=status,
                    sha256=source_sha256,
                    available=available,
                )
            )

        return tuple(
            sorted(
                output,
                key=lambda item: (
                    item.product_id,
                    item.variant_id or "",
                    item.source_relative_path.casefold(),
                ),
            )
        )
