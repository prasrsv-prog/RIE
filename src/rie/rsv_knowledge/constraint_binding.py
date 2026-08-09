"""Fail-closed canonical constraint binding for grounded RSV product locks."""

from dataclasses import dataclass
import re
from typing import Iterable, Optional, Tuple

from .product_catalog import ProductCatalog, ProductCatalogContractError


_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


class ConstraintBindingContractError(ValueError):
    """Raised when canonical constraint-binding input violates the contract."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ConstraintBindingContractError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ConstraintBindingContractError(f"{field_name} must not be empty")
    return normalized


def _optional_text(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    return _required_text(value, field_name)


@dataclass(frozen=True)
class AssetRecord:
    asset_id: str
    product_id: str
    variant_id: Optional[str]
    asset_type: str
    canonical_path: str
    sha256: str
    source: str
    authority: str
    version: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "asset_id", _required_text(self.asset_id, "asset_id"))
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(self, "variant_id", _optional_text(self.variant_id, "variant_id"))
        object.__setattr__(self, "asset_type", _required_text(self.asset_type, "asset_type"))
        object.__setattr__(
            self,
            "canonical_path",
            _required_text(self.canonical_path, "canonical_path"),
        )
        sha256 = _required_text(self.sha256, "sha256").lower()
        if _SHA256_PATTERN.fullmatch(sha256) is None:
            raise ConstraintBindingContractError(
                "sha256 must contain exactly 64 hexadecimal characters"
            )
        object.__setattr__(self, "sha256", sha256)
        object.__setattr__(self, "source", _required_text(self.source, "source"))
        object.__setattr__(self, "authority", _required_text(self.authority, "authority"))
        object.__setattr__(self, "version", _required_text(self.version, "version"))
        object.__setattr__(self, "status", _required_text(self.status, "status"))


@dataclass(frozen=True)
class KnowledgeRecord:
    knowledge_id: str
    product_id: str
    variant_id: Optional[str]
    knowledge_type: str
    subject: str
    property: str
    value: str
    source_asset_id: str
    authority: str
    version: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "knowledge_id",
            _required_text(self.knowledge_id, "knowledge_id"),
        )
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(self, "variant_id", _optional_text(self.variant_id, "variant_id"))
        object.__setattr__(
            self,
            "knowledge_type",
            _required_text(self.knowledge_type, "knowledge_type"),
        )
        object.__setattr__(self, "subject", _required_text(self.subject, "subject"))
        object.__setattr__(self, "property", _required_text(self.property, "property"))
        object.__setattr__(self, "value", _required_text(self.value, "value"))
        object.__setattr__(
            self,
            "source_asset_id",
            _required_text(self.source_asset_id, "source_asset_id"),
        )
        object.__setattr__(self, "authority", _required_text(self.authority, "authority"))
        object.__setattr__(self, "version", _required_text(self.version, "version"))
        object.__setattr__(self, "status", _required_text(self.status, "status"))


@dataclass(frozen=True)
class ConstraintRecord:
    constraint_id: str
    product_id: str
    variant_id: Optional[str]
    constraint_type: str
    rule: str
    source_knowledge_id_or_asset_id: str
    status: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "constraint_id",
            _required_text(self.constraint_id, "constraint_id"),
        )
        object.__setattr__(self, "product_id", _required_text(self.product_id, "product_id"))
        object.__setattr__(self, "variant_id", _optional_text(self.variant_id, "variant_id"))
        object.__setattr__(
            self,
            "constraint_type",
            _required_text(self.constraint_type, "constraint_type"),
        )
        object.__setattr__(self, "rule", _required_text(self.rule, "rule"))
        object.__setattr__(
            self,
            "source_knowledge_id_or_asset_id",
            _required_text(
                self.source_knowledge_id_or_asset_id,
                "source_knowledge_id_or_asset_id",
            ),
        )
        object.__setattr__(self, "status", _required_text(self.status, "status"))


@dataclass(frozen=True)
class ConstraintBindingResult:
    product_id: str
    variant_id: Optional[str]
    bound_constraints: Tuple[ConstraintRecord, ...]
    used_knowledge_ids: Tuple[str, ...]
    used_asset_ids: Tuple[str, ...]
    missing_knowledge: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    binding_status: str


def _unique_by_id(records: Iterable[object], id_field: str) -> Tuple[object, ...]:
    normalized = tuple(records)
    seen = set()
    for record in normalized:
        record_id = getattr(record, id_field)
        if record_id in seen:
            raise ConstraintBindingContractError(
                f"{id_field} contains duplicates: {record_id}"
            )
        seen.add(record_id)
    return normalized


def _scope_matches(record_variant_id: Optional[str], variant_id: Optional[str]) -> bool:
    if record_variant_id is None:
        return True
    return variant_id is not None and record_variant_id == variant_id


def _validate_record_scope(
    catalog: ProductCatalog,
    product_id: str,
    variant_id: Optional[str],
) -> None:
    try:
        catalog.require_variant(product_id, variant_id)
    except ProductCatalogContractError as exc:
        raise ConstraintBindingContractError(str(exc)) from exc


def bind_canonical_constraints(
    *,
    catalog: ProductCatalog,
    product_id: str,
    variant_id: Optional[str],
    knowledge_records: Iterable[KnowledgeRecord],
    asset_records: Iterable[AssetRecord],
    constraint_records: Iterable[ConstraintRecord],
) -> ConstraintBindingResult:
    """Bind deterministic product locks without inference or cross-variant leakage."""

    if not isinstance(catalog, ProductCatalog):
        raise ConstraintBindingContractError("catalog must be a ProductCatalog")

    product_id = _required_text(product_id, "product_id")
    variant_id = _optional_text(variant_id, "variant_id")
    _validate_record_scope(catalog, product_id, variant_id)

    knowledge = _unique_by_id(knowledge_records, "knowledge_id")
    assets = _unique_by_id(asset_records, "asset_id")
    constraints = _unique_by_id(constraint_records, "constraint_id")

    for record in knowledge:
        if not isinstance(record, KnowledgeRecord):
            raise ConstraintBindingContractError(
                "knowledge_records must contain KnowledgeRecord values"
            )
        _validate_record_scope(catalog, record.product_id, record.variant_id)

    for record in assets:
        if not isinstance(record, AssetRecord):
            raise ConstraintBindingContractError(
                "asset_records must contain AssetRecord values"
            )
        _validate_record_scope(catalog, record.product_id, record.variant_id)

    for record in constraints:
        if not isinstance(record, ConstraintRecord):
            raise ConstraintBindingContractError(
                "constraint_records must contain ConstraintRecord values"
            )
        _validate_record_scope(catalog, record.product_id, record.variant_id)

    applicable_knowledge = {
        record.knowledge_id: record
        for record in knowledge
        if record.status == "active"
        and record.product_id == product_id
        and _scope_matches(record.variant_id, variant_id)
    }
    applicable_assets = {
        record.asset_id: record
        for record in assets
        if record.status == "approved"
        and record.product_id == product_id
        and _scope_matches(record.variant_id, variant_id)
    }

    if set(applicable_knowledge).intersection(applicable_assets):
        raise ConstraintBindingContractError(
            "knowledge_id and asset_id provenance namespaces must not collide"
        )

    applicable_constraints = sorted(
        (
            record
            for record in constraints
            if record.status == "active"
            and record.product_id == product_id
            and _scope_matches(record.variant_id, variant_id)
        ),
        key=lambda record: (record.constraint_type, record.constraint_id),
    )

    missing = []
    used_knowledge = set()
    used_assets = set()

    for constraint in applicable_constraints:
        source_id = constraint.source_knowledge_id_or_asset_id
        if source_id in applicable_knowledge:
            used_knowledge.add(source_id)
        elif source_id in applicable_assets:
            used_assets.add(source_id)
        else:
            missing.append(source_id)

    by_type = {}
    for constraint in applicable_constraints:
        by_type.setdefault(constraint.constraint_type, []).append(constraint)

    conflicts = []
    for constraint_type in sorted(by_type):
        type_records = by_type[constraint_type]
        rules = {record.rule for record in type_records}
        if len(rules) > 1:
            conflicts.append(
                f"{constraint_type}:"
                + "|".join(record.constraint_id for record in type_records)
            )

    missing_tuple = tuple(sorted(set(missing)))
    conflicts_tuple = tuple(conflicts)

    if missing_tuple or conflicts_tuple:
        return ConstraintBindingResult(
            product_id=product_id,
            variant_id=variant_id,
            bound_constraints=(),
            used_knowledge_ids=(),
            used_asset_ids=(),
            missing_knowledge=missing_tuple,
            conflicts=conflicts_tuple,
            binding_status="FAILED",
        )

    return ConstraintBindingResult(
        product_id=product_id,
        variant_id=variant_id,
        bound_constraints=tuple(applicable_constraints),
        used_knowledge_ids=tuple(sorted(used_knowledge)),
        used_asset_ids=tuple(sorted(used_assets)),
        missing_knowledge=(),
        conflicts=(),
        binding_status="PASSED",
    )
