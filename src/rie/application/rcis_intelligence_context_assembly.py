"""Minimum read-only governed RCIS intelligence context assembly boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final


RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION: Final[str] = "1.0.0"
PRODUCT_INTELLIGENCE_CONTEXT_SOURCE: Final[str] = (
    "ProductIntelligenceQuery.get_product_context"
)
VISUAL_REFERENCE_ASSET_SOURCE: Final[str] = "VisualReferenceAssetQuery.list_assets"
RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES: Final[tuple[str, str]] = (
    PRODUCT_INTELLIGENCE_CONTEXT_SOURCE,
    VISUAL_REFERENCE_ASSET_SOURCE,
)


def _require_identifier(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def _require_read_method(boundary: object, *, method_name: str, boundary_name: str) -> None:
    if not callable(getattr(boundary, method_name, None)):
        raise TypeError(f"{boundary_name} must expose {method_name}")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceContext:
    """Immutable read-only assembly of existing governed RCIS intelligence."""

    contract_version: str
    product_id: str
    variant_id: str
    product_context: Any
    visual_reference_assets: tuple[Any, ...]
    source_boundaries: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.contract_version != RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION:
            raise ValueError("unsupported RCIS intelligence context contract version")
        _require_identifier(self.product_id, field_name="product_id")
        _require_identifier(self.variant_id, field_name="variant_id")
        if self.product_context is None:
            raise ValueError("product_context must not be None")
        if not isinstance(self.visual_reference_assets, tuple):
            raise TypeError("visual_reference_assets must be tuple")
        if any(asset is None for asset in self.visual_reference_assets):
            raise ValueError("visual_reference_assets must not contain None")
        if self.source_boundaries != RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES:
            raise ValueError("source_boundaries must match the governed read boundaries")


class RCISIntelligenceContextAssembler:
    """Compose product intelligence and governed visual assets without side effects."""

    def __init__(
        self,
        *,
        product_intelligence_query: object,
        visual_reference_asset_query: object,
    ) -> None:
        _require_read_method(
            product_intelligence_query,
            method_name="get_product_context",
            boundary_name="product_intelligence_query",
        )
        _require_read_method(
            visual_reference_asset_query,
            method_name="list_assets",
            boundary_name="visual_reference_asset_query",
        )
        self._product_intelligence_query = product_intelligence_query
        self._visual_reference_asset_query = visual_reference_asset_query

    def assemble(
        self,
        *,
        product_id: str,
        variant_id: str,
    ) -> RCISIntelligenceContext:
        _require_identifier(product_id, field_name="product_id")
        _require_identifier(variant_id, field_name="variant_id")

        product_context = self._product_intelligence_query.get_product_context(
            product_id=product_id,
            variant_id=variant_id,
        )
        if product_context is None:
            raise TypeError("product_intelligence_query returned no product context")

        visual_reference_assets = tuple(
            self._visual_reference_asset_query.list_assets(
                product_id=product_id,
                variant_id=variant_id,
            )
        )
        if any(asset is None for asset in visual_reference_assets):
            raise TypeError("visual_reference_asset_query returned an invalid asset value")

        return RCISIntelligenceContext(
            contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
            product_id=product_id,
            variant_id=variant_id,
            product_context=product_context,
            visual_reference_assets=visual_reference_assets,
            source_boundaries=RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
        )


__all__ = [
    "PRODUCT_INTELLIGENCE_CONTEXT_SOURCE",
    "RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION",
    "RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES",
    "RCISIntelligenceContext",
    "RCISIntelligenceContextAssembler",
    "VISUAL_REFERENCE_ASSET_SOURCE",
]
