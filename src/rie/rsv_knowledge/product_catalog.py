"""Minimum fail-closed product and variant identity catalog for RSV knowledge."""

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple


class ProductCatalogContractError(ValueError):
    """Raised when product/variant identity violates the bounded contract."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ProductCatalogContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ProductCatalogContractError(f"{field_name} must not be empty")
    return normalized


@dataclass(frozen=True)
class ProductRecord:
    product_id: str
    canonical_name: str
    brand: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(
            self,
            "canonical_name",
            _required_text(self.canonical_name, "canonical_name"),
        )
        object.__setattr__(self, "brand", _required_text(self.brand, "brand"))
        object.__setattr__(self, "status", _required_text(self.status, "status"))


@dataclass(frozen=True)
class VariantRecord:
    variant_id: str
    product_id: str
    canonical_name: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "variant_id", _required_text(self.variant_id, "variant_id"))
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(
            self,
            "canonical_name",
            _required_text(self.canonical_name, "canonical_name"),
        )
        object.__setattr__(self, "status", _required_text(self.status, "status"))


class ProductCatalog:
    """Immutable-in-practice identity catalog with fail-closed resolution."""

    def __init__(
        self,
        products: Iterable[ProductRecord],
        variants: Iterable[VariantRecord],
    ) -> None:
        product_map = {}
        variant_map = {}

        for product in products:
            if not isinstance(product, ProductRecord):
                raise ProductCatalogContractError(
                    "products must contain ProductRecord values"
                )
            if product.product_id in product_map:
                raise ProductCatalogContractError(
                    f"duplicate product_id: {product.product_id}"
                )
            product_map[product.product_id] = product

        for variant in variants:
            if not isinstance(variant, VariantRecord):
                raise ProductCatalogContractError(
                    "variants must contain VariantRecord values"
                )
            if variant.variant_id in variant_map:
                raise ProductCatalogContractError(
                    f"duplicate variant_id: {variant.variant_id}"
                )
            if variant.product_id not in product_map:
                raise ProductCatalogContractError(
                    f"variant references unknown product_id: {variant.product_id}"
                )
            variant_map[variant.variant_id] = variant

        self._products = product_map
        self._variants = variant_map

    @property
    def products(self) -> Tuple[ProductRecord, ...]:
        return tuple(self._products[key] for key in sorted(self._products))

    @property
    def variants(self) -> Tuple[VariantRecord, ...]:
        return tuple(self._variants[key] for key in sorted(self._variants))

    def require_product(self, product_id: str) -> ProductRecord:
        normalized = _required_text(product_id, "product_id")
        try:
            return self._products[normalized]
        except KeyError as exc:
            raise ProductCatalogContractError(
                f"unknown product_id: {normalized}"
            ) from exc

    def require_variant(
        self,
        product_id: str,
        variant_id: Optional[str],
    ) -> Optional[VariantRecord]:
        product = self.require_product(product_id)
        if variant_id is None:
            return None

        normalized_variant_id = _required_text(variant_id, "variant_id")
        try:
            variant = self._variants[normalized_variant_id]
        except KeyError as exc:
            raise ProductCatalogContractError(
                f"unknown variant_id: {normalized_variant_id}"
            ) from exc

        if variant.product_id != product.product_id:
            raise ProductCatalogContractError(
                "variant_id does not belong to requested product_id"
            )
        return variant
