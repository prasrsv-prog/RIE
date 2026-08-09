"""Minimum RSV canonical product/variant knowledge binding contracts."""

from .canonical_binding import CanonicalBinding, CanonicalBindingContractError
from .ingestion_manifest import IngestionManifestContractError, IngestionManifestRecord
from .product_catalog import (
    ProductCatalog,
    ProductCatalogContractError,
    ProductRecord,
    VariantRecord,
)

__all__ = [
    "CanonicalBinding",
    "CanonicalBindingContractError",
    "IngestionManifestContractError",
    "IngestionManifestRecord",
    "ProductCatalog",
    "ProductCatalogContractError",
    "ProductRecord",
    "VariantRecord",
]
