"""Explicit deterministic ingestion manifest for canonical RSV source binding."""

from dataclasses import dataclass
import re
from typing import Optional, Tuple

from .product_catalog import ProductCatalog, ProductCatalogContractError


_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


class IngestionManifestContractError(ValueError):
    """Raised when explicit ingestion metadata is incomplete or invalid."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise IngestionManifestContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise IngestionManifestContractError(f"{field_name} must not be empty")
    return normalized


def _optional_text(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    return _required_text(value, field_name)


@dataclass(frozen=True)
class IngestionManifestRecord:
    source_path: str
    source_sha256: str
    product_id: str
    variant_id: Optional[str]
    knowledge_type: str
    asset_type: str
    source: str
    authority: str
    version: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_path",
            _required_text(self.source_path, "source_path"),
        )

        sha256 = _required_text(self.source_sha256, "source_sha256").lower()
        if _SHA256_PATTERN.fullmatch(sha256) is None:
            raise IngestionManifestContractError(
                "source_sha256 must contain exactly 64 hexadecimal characters"
            )
        object.__setattr__(self, "source_sha256", sha256)

        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(
            self,
            "variant_id",
            _optional_text(self.variant_id, "variant_id"),
        )
        object.__setattr__(
            self,
            "knowledge_type",
            _required_text(self.knowledge_type, "knowledge_type"),
        )
        object.__setattr__(self, "asset_type", _required_text(self.asset_type, "asset_type"))
        object.__setattr__(self, "source", _required_text(self.source, "source"))
        object.__setattr__(self, "authority", _required_text(self.authority, "authority"))
        object.__setattr__(self, "version", _required_text(self.version, "version"))
        object.__setattr__(self, "status", _required_text(self.status, "status"))

    def validate_against(self, catalog: ProductCatalog) -> "IngestionManifestRecord":
        if not isinstance(catalog, ProductCatalog):
            raise IngestionManifestContractError(
                "catalog must be a ProductCatalog"
            )
        try:
            catalog.require_variant(self.product_id, self.variant_id)
        except ProductCatalogContractError as exc:
            raise IngestionManifestContractError(str(exc)) from exc
        return self

    @property
    def canonical_key(self) -> Tuple[str, Optional[str], str, str, str]:
        return (
            self.product_id,
            self.variant_id,
            self.source_sha256,
            self.knowledge_type,
            self.asset_type,
        )
