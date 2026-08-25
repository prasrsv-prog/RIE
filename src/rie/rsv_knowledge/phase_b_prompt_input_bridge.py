"""Approved Phase B B1 TraceableEvidence-backed prompt-input bridge.

This surface performs deterministic in-memory adaptation only. It does not read
files, databases, networks, models, or ambient configuration.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable, Tuple

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.evidence_materialization.evidence_materialization_contract import (
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TraceableEvidence,
)

from .governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
    GovernedPromptInputMaterializationResult,
    PromptConstraintMaterializationSpec,
    materialize_governed_prompt_inputs,
)
from .ingestion_manifest import IngestionManifestRecord
from .product_catalog import ProductCatalog


B1_CONSTRAINT_TYPE = "product_variant_identity"
B1_CONSTRAINT_RULE = "preserve exact approved product and variant identity"
B1_BRIDGED_ASSET_TYPE = "structured_evidence"
B1_BRIDGED_ASSET_SOURCE = "pilot-evidence-repository-v2"


class PhaseBPromptInputBridgeContractError(ValueError):
    """Raised when B1 bridge inputs cannot be matched exactly."""


@dataclass(frozen=True)
class PhaseBSourceAssetBridgeRecord:
    original_source_asset_id: str
    bridged_source_asset_id: str
    product_id: str
    variant_id: str
    knowledge_id: str
    traceable_evidence_id: str
    traceable_evidence_content_digest: str
    source_relative_paths: Tuple[str, ...]


@dataclass(frozen=True)
class PhaseBPromptInputBridgeResult:
    bridge_records: Tuple[PhaseBSourceAssetBridgeRecord, ...]
    ingestion_manifest_records: Tuple[IngestionManifestRecord, ...]
    bridged_knowledge_mappings: Tuple[GovernedKnowledgePromptInputMappingRecord, ...]
    constraint_specs: Tuple[PromptConstraintMaterializationSpec, ...]
    prompt_inputs: GovernedPromptInputMaterializationResult


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise PhaseBPromptInputBridgeContractError(f"{label} must be a string")
    normalized = value.strip()
    if not normalized:
        raise PhaseBPromptInputBridgeContractError(f"{label} must not be empty")
    return normalized


def _structured_payload(evidence: TraceableEvidence) -> dict[str, object]:
    if type(evidence) is not TraceableEvidence:
        raise PhaseBPromptInputBridgeContractError(
            "traceable_evidence_items must contain exact TraceableEvidence values"
        )
    if evidence.content_type != TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence content_type is not structured metadata"
        )
    expected_digest = hashlib.sha256(evidence.content.encode("utf-8")).hexdigest()
    if evidence.content_digest != expected_digest:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence content_digest mismatch"
        )
    try:
        payload = json.loads(evidence.content)
    except json.JSONDecodeError as exc:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence content is not valid JSON"
        ) from exc
    if type(payload) is not dict:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence structured payload must be an object"
        )

    required = (
        "knowledge_kind",
        "atomic_knowledge_id",
        "product_id",
        "variant_id",
        "source_relative_paths",
        "source_authority",
        "source_version",
    )
    for key in required:
        if key not in payload:
            raise PhaseBPromptInputBridgeContractError(
                f"TraceableEvidence structured payload missing field: {key}"
            )

    if payload["knowledge_kind"] != "product_variant_identity":
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence knowledge_kind mismatch"
        )

    atomic_id = _required_text(payload["atomic_knowledge_id"], "atomic_knowledge_id")
    product_id = _required_text(payload["product_id"], "product_id")
    variant_id = _required_text(payload["variant_id"], "variant_id")
    source_authority = _required_text(payload["source_authority"], "source_authority")
    source_version = _required_text(payload["source_version"], "source_version")

    raw_paths = payload["source_relative_paths"]
    if not isinstance(raw_paths, list) or not raw_paths:
        raise PhaseBPromptInputBridgeContractError(
            "source_relative_paths must be a non-empty list"
        )
    source_paths = tuple(
        _required_text(value, "source_relative_path") for value in raw_paths
    )
    if len(source_paths) != len(set(source_paths)):
        raise PhaseBPromptInputBridgeContractError(
            "source_relative_paths contains duplicates"
        )

    provenance = evidence.provenance
    if getattr(provenance, "atomic_knowledge_id", None) != atomic_id:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence provenance atomic_knowledge_id mismatch"
        )
    if tuple(getattr(provenance, "source_relative_paths", ())) != source_paths:
        raise PhaseBPromptInputBridgeContractError(
            "TraceableEvidence provenance source_relative_paths mismatch"
        )

    normalized = dict(payload)
    normalized["atomic_knowledge_id"] = atomic_id
    normalized["product_id"] = product_id
    normalized["variant_id"] = variant_id
    normalized["source_authority"] = source_authority
    normalized["source_version"] = source_version
    normalized["source_relative_paths"] = source_paths
    return normalized


def materialize_traceable_evidence_backed_product_variant_prompt_inputs(
    *,
    collection_id: str,
    catalog: ProductCatalog,
    governed_knowledge: Iterable[GovernedKnowledge],
    knowledge_mappings: Iterable[GovernedKnowledgePromptInputMappingRecord],
    traceable_evidence_items: Iterable[TraceableEvidence],
) -> PhaseBPromptInputBridgeResult:
    """Materialize the approved B1 bridge and exact identity constraints."""

    collection_id = _required_text(collection_id, "collection_id")
    if not isinstance(catalog, ProductCatalog):
        raise PhaseBPromptInputBridgeContractError(
            "catalog must be a ProductCatalog"
        )

    governed_values = tuple(governed_knowledge)
    mapping_values = tuple(knowledge_mappings)
    evidence_values = tuple(traceable_evidence_items)

    if not mapping_values:
        raise PhaseBPromptInputBridgeContractError(
            "knowledge_mappings must not be empty"
        )
    if not evidence_values:
        raise PhaseBPromptInputBridgeContractError(
            "traceable_evidence_items must not be empty"
        )

    evidence_index: dict[tuple[str, str, str], list[tuple[TraceableEvidence, dict[str, object]]]] = {}
    for evidence in evidence_values:
        payload = _structured_payload(evidence)
        key = (
            str(payload["product_id"]),
            str(payload["variant_id"]),
            str(payload["atomic_knowledge_id"]),
        )
        evidence_index.setdefault(key, []).append((evidence, payload))

    bridge_records = []
    manifest_records = []
    bridged_mappings = []
    constraint_specs = []

    seen_governed_ids = set()
    seen_knowledge_ids = set()
    seen_constraint_ids = set()
    seen_bridged_asset_ids = set()

    for mapping in sorted(
        mapping_values,
        key=lambda value: (
            value.product_id,
            value.variant_id or "",
            value.knowledge_id,
            value.governed_knowledge_id,
        ),
    ):
        if type(mapping) is not GovernedKnowledgePromptInputMappingRecord:
            raise PhaseBPromptInputBridgeContractError(
                "knowledge_mappings must contain exact "
                "GovernedKnowledgePromptInputMappingRecord values"
            )
        if mapping.governed_knowledge_id in seen_governed_ids:
            raise PhaseBPromptInputBridgeContractError(
                f"duplicate governed_knowledge_id: {mapping.governed_knowledge_id}"
            )
        if mapping.knowledge_id in seen_knowledge_ids:
            raise PhaseBPromptInputBridgeContractError(
                f"duplicate knowledge_id: {mapping.knowledge_id}"
            )
        seen_governed_ids.add(mapping.governed_knowledge_id)
        seen_knowledge_ids.add(mapping.knowledge_id)

        if mapping.variant_id is None:
            raise PhaseBPromptInputBridgeContractError(
                "B1 requires variant-level mappings"
            )
        if mapping.knowledge_type != B1_CONSTRAINT_TYPE:
            raise PhaseBPromptInputBridgeContractError(
                "B1 mapping knowledge_type must be product_variant_identity"
            )

        key = (mapping.product_id, mapping.variant_id, mapping.knowledge_id)
        matches = evidence_index.get(key, [])
        if len(matches) == 0:
            raise PhaseBPromptInputBridgeContractError(
                "zero TraceableEvidence matches for mapping: "
                f"{mapping.knowledge_id}"
            )
        if len(matches) != 1:
            raise PhaseBPromptInputBridgeContractError(
                "multiple TraceableEvidence matches for mapping: "
                f"{mapping.knowledge_id}"
            )

        evidence, payload = matches[0]
        if payload["product_id"] != mapping.product_id:
            raise PhaseBPromptInputBridgeContractError(
                f"product_id mismatch: {mapping.knowledge_id}"
            )
        if payload["variant_id"] != mapping.variant_id:
            raise PhaseBPromptInputBridgeContractError(
                f"variant_id mismatch: {mapping.knowledge_id}"
            )
        if payload["atomic_knowledge_id"] != mapping.knowledge_id:
            raise PhaseBPromptInputBridgeContractError(
                f"atomic_knowledge_id mismatch: {mapping.knowledge_id}"
            )

        source_paths = tuple(payload["source_relative_paths"])
        if not source_paths:
            raise PhaseBPromptInputBridgeContractError(
                f"missing underlying source-relative-path lineage: {mapping.knowledge_id}"
            )

        bridged_asset_id = f"asset-{evidence.content_digest}"
        if bridged_asset_id in seen_bridged_asset_ids:
            raise PhaseBPromptInputBridgeContractError(
                f"bridged source asset collision: {bridged_asset_id}"
            )
        seen_bridged_asset_ids.add(bridged_asset_id)

        locator = (
            "evidence://pilot-evidence-repository-v2/collections/"
            f"{collection_id}/evidence/{evidence.evidence_id}"
        )
        manifest_record = IngestionManifestRecord(
            source_path=locator,
            source_sha256=evidence.content_digest,
            product_id=mapping.product_id,
            variant_id=mapping.variant_id,
            knowledge_type=mapping.knowledge_type,
            asset_type=B1_BRIDGED_ASSET_TYPE,
            source=B1_BRIDGED_ASSET_SOURCE,
            authority=str(payload["source_authority"]),
            version=str(payload["source_version"]),
            status="active",
        )
        manifest_record.validate_against(catalog)

        bridged_mapping = GovernedKnowledgePromptInputMappingRecord(
            governed_knowledge_id=mapping.governed_knowledge_id,
            knowledge_id=mapping.knowledge_id,
            product_id=mapping.product_id,
            variant_id=mapping.variant_id,
            source_id=mapping.source_id,
            source_asset_id=bridged_asset_id,
            knowledge_type=mapping.knowledge_type,
            subject=mapping.subject,
            property=mapping.property,
        )

        constraint_id = (
            f"constraint-{mapping.variant_id}-product-variant-identity"
        )
        if constraint_id in seen_constraint_ids:
            raise PhaseBPromptInputBridgeContractError(
                f"constraint_id collision: {constraint_id}"
            )
        seen_constraint_ids.add(constraint_id)

        constraint_spec = PromptConstraintMaterializationSpec(
            constraint_id=constraint_id,
            product_id=mapping.product_id,
            variant_id=mapping.variant_id,
            constraint_type=B1_CONSTRAINT_TYPE,
            rule=B1_CONSTRAINT_RULE,
            source_knowledge_id_or_asset_id=mapping.knowledge_id,
            status="active",
        )

        bridge_records.append(
            PhaseBSourceAssetBridgeRecord(
                original_source_asset_id=mapping.source_asset_id,
                bridged_source_asset_id=bridged_asset_id,
                product_id=mapping.product_id,
                variant_id=mapping.variant_id,
                knowledge_id=mapping.knowledge_id,
                traceable_evidence_id=evidence.evidence_id,
                traceable_evidence_content_digest=evidence.content_digest,
                source_relative_paths=source_paths,
            )
        )
        manifest_records.append(manifest_record)
        bridged_mappings.append(bridged_mapping)
        constraint_specs.append(constraint_spec)

    prompt_inputs = materialize_governed_prompt_inputs(
        catalog=catalog,
        governed_knowledge=governed_values,
        ingestion_manifest_records=tuple(manifest_records),
        knowledge_mappings=tuple(bridged_mappings),
        constraint_specs=tuple(constraint_specs),
    )
    if prompt_inputs.materialization_status != "PASSED":
        details = "|".join(prompt_inputs.conflicts or prompt_inputs.missing_mappings)
        raise PhaseBPromptInputBridgeContractError(
            "governed prompt-input materialization failed: "
            + (details or "<NO_DETAIL>")
        )

    return PhaseBPromptInputBridgeResult(
        bridge_records=tuple(bridge_records),
        ingestion_manifest_records=tuple(manifest_records),
        bridged_knowledge_mappings=tuple(bridged_mappings),
        constraint_specs=tuple(constraint_specs),
        prompt_inputs=prompt_inputs,
    )
