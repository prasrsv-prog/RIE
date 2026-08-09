"""Canonical product/variant bindings to approved RCIS asset and knowledge IDs."""

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from .product_catalog import ProductCatalog, ProductCatalogContractError


class CanonicalBindingContractError(ValueError):
    """Raised when a canonical binding violates fail-closed rules."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise CanonicalBindingContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise CanonicalBindingContractError(f"{field_name} must not be empty")
    return normalized


def _optional_text(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    return _required_text(value, field_name)


def _id_tuple(values: Iterable[str], field_name: str) -> Tuple[str, ...]:
    normalized = tuple(_required_text(value, field_name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise CanonicalBindingContractError(f"{field_name} contains duplicates")
    return normalized


@dataclass(frozen=True)
class CanonicalBinding:
    product_id: str
    variant_id: Optional[str]
    asset_ids: Tuple[str, ...] = ()
    knowledge_ids: Tuple[str, ...] = ()
    constraint_ids: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(
            self,
            "variant_id",
            _optional_text(self.variant_id, "variant_id"),
        )
        object.__setattr__(self, "asset_ids", _id_tuple(self.asset_ids, "asset_ids"))
        object.__setattr__(
            self,
            "knowledge_ids",
            _id_tuple(self.knowledge_ids, "knowledge_ids"),
        )
        object.__setattr__(
            self,
            "constraint_ids",
            _id_tuple(self.constraint_ids, "constraint_ids"),
        )

        if not (self.asset_ids or self.knowledge_ids or self.constraint_ids):
            raise CanonicalBindingContractError(
                "canonical binding must reference at least one asset, knowledge, or constraint id"
            )

    def validate_against(self, catalog: ProductCatalog) -> "CanonicalBinding":
        if not isinstance(catalog, ProductCatalog):
            raise CanonicalBindingContractError(
                "catalog must be a ProductCatalog"
            )
        try:
            catalog.require_variant(self.product_id, self.variant_id)
        except ProductCatalogContractError as exc:
            raise CanonicalBindingContractError(str(exc)) from exc
        return self

    @property
    def scope_key(self) -> Tuple[str, Optional[str]]:
        return (self.product_id, self.variant_id)
