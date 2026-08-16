"""Deterministic governed RSV knowledge to canonical prompt-input materialization."""

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from rie.domain.governed_knowledge import GovernedKnowledge

from .constraint_binding import AssetRecord, ConstraintRecord, KnowledgeRecord
from .ingestion_manifest import IngestionManifestRecord
from .product_catalog import ProductCatalog, ProductCatalogContractError


class GovernedPromptInputMaterializationContractError(ValueError):
    """Raised when explicit bridge inputs violate the bounded contract."""


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise GovernedPromptInputMaterializationContractError(
            f"{field_name} must be a string"
        )
    normalized = value.strip()
    if not normalized:
        raise GovernedPromptInputMaterializationContractError(
            f"{field_name} must not be empty"
        )
    return normalized


def _optional_text(value: Optional[str], field_name: str) -> Optional[str]:
    if value is None:
        return None
    return _required_text(value, field_name)


@dataclass(frozen=True)
class GovernedKnowledgePromptInputMappingRecord:
    governed_knowledge_id: str
    knowledge_id: str
    product_id: str
    variant_id: Optional[str]
    source_id: str
    source_asset_id: str
    knowledge_type: str
    subject: str
    property: str

    def __post_init__(self) -> None:
        for field_name in (
            "governed_knowledge_id",
            "knowledge_id",
            "product_id",
            "source_id",
            "source_asset_id",
            "knowledge_type",
            "subject",
            "property",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "variant_id",
            _optional_text(self.variant_id, "variant_id"),
        )


@dataclass(frozen=True)
class PromptConstraintMaterializationSpec:
    constraint_id: str
    product_id: str
    variant_id: Optional[str]
    constraint_type: str
    rule: str
    source_knowledge_id_or_asset_id: str
    status: str = "active"

    def __post_init__(self) -> None:
        for field_name in (
            "constraint_id",
            "product_id",
            "constraint_type",
            "rule",
            "source_knowledge_id_or_asset_id",
            "status",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "variant_id",
            _optional_text(self.variant_id, "variant_id"),
        )


@dataclass(frozen=True)
class GovernedPromptInputMaterializationResult:
    knowledge_records: Tuple[KnowledgeRecord, ...]
    asset_records: Tuple[AssetRecord, ...]
    constraint_records: Tuple[ConstraintRecord, ...]
    missing_mappings: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    materialization_status: str


def _scope_compatible(
    source_variant_id: Optional[str],
    target_variant_id: Optional[str],
) -> bool:
    return (
        source_variant_id is None
        or source_variant_id == target_variant_id
    )


def _require_catalog_scope(
    catalog: ProductCatalog,
    product_id: str,
    variant_id: Optional[str],
) -> None:
    try:
        catalog.require_variant(product_id, variant_id)
    except ProductCatalogContractError as exc:
        raise GovernedPromptInputMaterializationContractError(str(exc)) from exc


def _asset_id(record: IngestionManifestRecord) -> str:
    return f"asset-{record.source_sha256}"


def _failed(
    *,
    missing_mappings: Tuple[str, ...] = (),
    conflicts: Tuple[str, ...] = (),
) -> GovernedPromptInputMaterializationResult:
    return GovernedPromptInputMaterializationResult(
        knowledge_records=(),
        asset_records=(),
        constraint_records=(),
        missing_mappings=tuple(sorted(set(missing_mappings))),
        conflicts=tuple(sorted(set(conflicts))),
        materialization_status="FAILED",
    )


def materialize_governed_prompt_inputs(
    *,
    catalog: ProductCatalog,
    governed_knowledge: Iterable[GovernedKnowledge],
    ingestion_manifest_records: Iterable[IngestionManifestRecord],
    knowledge_mappings: Iterable[GovernedKnowledgePromptInputMappingRecord],
    constraint_specs: Iterable[PromptConstraintMaterializationSpec],
) -> GovernedPromptInputMaterializationResult:
    """Materialize exact canonical prompt inputs without inference or ambient reads."""

    if not isinstance(catalog, ProductCatalog):
        raise GovernedPromptInputMaterializationContractError(
            "catalog must be a ProductCatalog"
        )

    governed_values = tuple(governed_knowledge)
    manifest_values = tuple(ingestion_manifest_records)
    mapping_values = tuple(knowledge_mappings)
    constraint_values = tuple(constraint_specs)

    governed_by_id = {}
    for value in governed_values:
        if type(value) is not GovernedKnowledge:
            raise GovernedPromptInputMaterializationContractError(
                "governed_knowledge must contain exact GovernedKnowledge values"
            )
        if value.governed_knowledge_id in governed_by_id:
            raise GovernedPromptInputMaterializationContractError(
                f"duplicate governed_knowledge_id: {value.governed_knowledge_id}"
            )
        governed_by_id[value.governed_knowledge_id] = value

    assets_by_id = {}
    for record in manifest_values:
        if type(record) is not IngestionManifestRecord:
            raise GovernedPromptInputMaterializationContractError(
                "ingestion_manifest_records must contain exact IngestionManifestRecord values"
            )
        record.validate_against(catalog)
        if record.status != "active":
            continue
        asset = AssetRecord(
            asset_id=_asset_id(record),
            product_id=record.product_id,
            variant_id=record.variant_id,
            asset_type=record.asset_type,
            canonical_path=record.source_path,
            sha256=record.source_sha256,
            source=record.source,
            authority=record.authority,
            version=record.version,
            status="approved",
        )
        if asset.asset_id in assets_by_id:
            raise GovernedPromptInputMaterializationContractError(
                f"duplicate materialized asset_id: {asset.asset_id}"
            )
        assets_by_id[asset.asset_id] = asset

    mappings_by_governed_id = {}
    knowledge_ids = set()
    for mapping in mapping_values:
        if type(mapping) is not GovernedKnowledgePromptInputMappingRecord:
            raise GovernedPromptInputMaterializationContractError(
                "knowledge_mappings must contain exact "
                "GovernedKnowledgePromptInputMappingRecord values"
            )
        if mapping.governed_knowledge_id in mappings_by_governed_id:
            raise GovernedPromptInputMaterializationContractError(
                "duplicate governed knowledge mapping: "
                f"{mapping.governed_knowledge_id}"
            )
        if mapping.knowledge_id in knowledge_ids:
            raise GovernedPromptInputMaterializationContractError(
                f"duplicate knowledge_id: {mapping.knowledge_id}"
            )
        if mapping.governed_knowledge_id not in governed_by_id:
            raise GovernedPromptInputMaterializationContractError(
                "mapping references unknown governed_knowledge_id: "
                f"{mapping.governed_knowledge_id}"
            )
        _require_catalog_scope(catalog, mapping.product_id, mapping.variant_id)
        mappings_by_governed_id[mapping.governed_knowledge_id] = mapping
        knowledge_ids.add(mapping.knowledge_id)

    missing = tuple(
        sorted(set(governed_by_id) - set(mappings_by_governed_id))
    )
    if missing:
        return _failed(missing_mappings=missing)

    knowledge_records = []
    for governed_id in sorted(governed_by_id):
        value = governed_by_id[governed_id]
        mapping = mappings_by_governed_id[governed_id]

        source_asset = assets_by_id.get(mapping.source_asset_id)
        if source_asset is None:
            return _failed(
                conflicts=(
                    f"missing_source_asset:{mapping.knowledge_id}:"
                    f"{mapping.source_asset_id}",
                )
            )
        if source_asset.product_id != mapping.product_id:
            return _failed(
                conflicts=(
                    f"source_asset_product_scope:"
                    f"{mapping.knowledge_id}:{mapping.source_asset_id}",
                )
            )
        if not _scope_compatible(source_asset.variant_id, mapping.variant_id):
            return _failed(
                conflicts=(
                    f"source_asset_variant_scope:"
                    f"{mapping.knowledge_id}:{mapping.source_asset_id}",
                )
            )

        support_source_ids = tuple(
            support.source_id for support in value.support
        )
        if mapping.source_id not in support_source_ids:
            return _failed(
                conflicts=(
                    f"governed_support_source_mismatch:"
                    f"{mapping.knowledge_id}:{mapping.source_id}",
                )
            )

        knowledge_records.append(
            KnowledgeRecord(
                knowledge_id=mapping.knowledge_id,
                product_id=mapping.product_id,
                variant_id=mapping.variant_id,
                knowledge_type=mapping.knowledge_type,
                subject=mapping.subject,
                property=mapping.property,
                value=value.statement,
                source_asset_id=mapping.source_asset_id,
                authority=source_asset.authority,
                version=source_asset.version,
                status="active",
            )
        )

    knowledge_by_id = {
        record.knowledge_id: record for record in knowledge_records
    }

    constraint_ids = set()
    constraint_records = []
    for spec in sorted(
        constraint_values,
        key=lambda item: (item.constraint_type, item.constraint_id),
    ):
        if type(spec) is not PromptConstraintMaterializationSpec:
            raise GovernedPromptInputMaterializationContractError(
                "constraint_specs must contain exact "
                "PromptConstraintMaterializationSpec values"
            )
        if spec.constraint_id in constraint_ids:
            raise GovernedPromptInputMaterializationContractError(
                f"duplicate constraint_id: {spec.constraint_id}"
            )
        constraint_ids.add(spec.constraint_id)
        _require_catalog_scope(catalog, spec.product_id, spec.variant_id)

        source = knowledge_by_id.get(spec.source_knowledge_id_or_asset_id)
        if source is None:
            source = assets_by_id.get(spec.source_knowledge_id_or_asset_id)
        if source is None:
            return _failed(
                conflicts=(
                    f"constraint_source_missing:{spec.constraint_id}:"
                    f"{spec.source_knowledge_id_or_asset_id}",
                )
            )
        if source.product_id != spec.product_id:
            return _failed(
                conflicts=(
                    f"constraint_source_product_scope:{spec.constraint_id}:"
                    f"{spec.source_knowledge_id_or_asset_id}",
                )
            )
        if not _scope_compatible(source.variant_id, spec.variant_id):
            return _failed(
                conflicts=(
                    f"constraint_source_variant_scope:{spec.constraint_id}:"
                    f"{spec.source_knowledge_id_or_asset_id}",
                )
            )

        constraint_records.append(
            ConstraintRecord(
                constraint_id=spec.constraint_id,
                product_id=spec.product_id,
                variant_id=spec.variant_id,
                constraint_type=spec.constraint_type,
                rule=spec.rule,
                source_knowledge_id_or_asset_id=(
                    spec.source_knowledge_id_or_asset_id
                ),
                status=spec.status,
            )
        )

    return GovernedPromptInputMaterializationResult(
        knowledge_records=tuple(
            sorted(knowledge_records, key=lambda item: item.knowledge_id)
        ),
        asset_records=tuple(
            sorted(assets_by_id.values(), key=lambda item: item.asset_id)
        ),
        constraint_records=tuple(
            sorted(
                constraint_records,
                key=lambda item: (item.constraint_type, item.constraint_id),
            )
        ),
        missing_mappings=(),
        conflicts=(),
        materialization_status="PASSED",
    )
