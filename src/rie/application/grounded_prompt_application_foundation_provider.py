"""Read-only Phase E foundation provider for the frozen RSV pilot state."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Tuple

from rie.evidence_repository.sqlite_evidence_collection_repository import (
    SqliteEvidenceCollectionRepository,
)
from rie.knowledge_repository.sqlite_governed_knowledge_repository import (
    SqliteGovernedKnowledgeRepository,
)
from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
    materialize_canonical_knowledge_taxonomy_mapping_records,
)
from rie.rsv_knowledge.ingestion_manifest import IngestionManifestRecord
from rie.rsv_knowledge.phase_b_exact_six_active_constraint_bridge import (
    EXPECTED_PRODUCT_MANUAL_MAPPINGS,
)
from rie.rsv_knowledge.product_catalog import (
    ProductCatalog,
    ProductRecord,
    VariantRecord,
)


class GroundedPromptApplicationFoundationProviderContractError(ValueError):
    """Raised when the frozen pilot state cannot be assembled exactly."""


@dataclass(frozen=True)
class GroundedPromptApplicationFoundation:
    collection_id: str
    catalog: ProductCatalog
    governed_knowledge: Tuple[object, ...]
    knowledge_mappings: Tuple[object, ...]
    traceable_evidence_items: Tuple[object, ...]
    product_constraint_governed_knowledge: Tuple[object, ...]
    product_constraint_ingestion_manifest_records: Tuple[IngestionManifestRecord, ...]
    product_constraint_knowledge_mappings: Tuple[object, ...]


_COLLECTION_ID = (
    "evc1_06534223733730505e33f7225d3d0507da70157396b5f94944d1e646d1b24f4b"
)
_STRUCTURED_CONTENT_TYPE = "product_variant_identity_structured_metadata"
_PRODUCT_NAMES = {
    "ffs21": "FFS21",
    "new-windtail": "New Windtail",
    "sv300": "SV300",
}
_PRODUCT_COUNTS = {"ffs21": 8, "new-windtail": 5, "sv300": 5}

_ARTIFACTS = (
    (
        "manifest",
        "pilot-source-intake-manifest.tsv",
        "a9ed300c5c76e6593c1cb1070322875962e848976c5f15b28cc58b2e9060412e",
    ),
    (
        "capture",
        "pilot-source-identity-capture.tsv",
        "f08f4ffedde5047cb90965820e1da20068d974ea9de9fd9264b389fc29bc8b0d",
    ),
    (
        "base_mapping",
        "pilot-authoritative-knowledge-taxonomy-mapping-canonical-data.json",
        "33af544399b0190a37bdd23ef5ee87cb53dc40795a4c371fd25aa019d055753b",
    ),
    (
        "exact18_mapping",
        "pilot-product-variant-exact18-canonical-mapping-extension.json",
        "754a9f49fe3fc6bb120c6737046276c1574455077422f41a7a5d420eb2a56782",
    ),
    (
        "evidence_db",
        "pilot-canonical-evidence-repository-v2-state/pilot-evidence-repository-v2.sqlite3",
        "67da57d530be11deaa2b211dedfeeddb60a68e95c7ae30df0d9cdceab8a0c052",
    ),
    (
        "governed_db",
        "pilot-governed-knowledge-repository-state/pilot-governed-knowledge-repository.sqlite3",
        "27521348ecda680f502db0342af97961f1494c586d2fa88e8134074dd7b4149c",
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verified_artifact_paths(intake_root: str | Path) -> dict[str, Path]:
    if not isinstance(intake_root, (str, Path)):
        raise GroundedPromptApplicationFoundationProviderContractError(
            "intake_root must be caller-supplied str or Path."
        )
    root = Path(intake_root)
    if not root.is_dir():
        raise GroundedPromptApplicationFoundationProviderContractError(
            "intake_root must identify the exact frozen pilot intake directory."
        )

    paths: dict[str, Path] = {}
    for key, relative_path, expected_sha256 in _ARTIFACTS:
        path = root / Path(relative_path)
        if not path.is_file():
            raise GroundedPromptApplicationFoundationProviderContractError(
                "required frozen pilot artifact is missing: " + relative_path
            )
        if _sha256(path) != expected_sha256:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "frozen pilot artifact SHA256 mismatch: " + relative_path
            )
        paths[key] = path
    return paths


def _load_json_object(path: Path, label: str) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="ascii"))
    if not isinstance(value, dict):
        raise GroundedPromptApplicationFoundationProviderContractError(
            label + " root must be an object."
        )
    return value


def _materialize_exact18(paths: dict[str, Path]) -> Tuple[object, ...]:
    records = tuple(
        materialize_canonical_knowledge_taxonomy_mapping_records(
            _load_json_object(paths["exact18_mapping"], "exact18 mapping")
        )
    )
    if len(records) != 18:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 mapping count drift."
        )
    governed_ids = tuple(record.governed_knowledge_id for record in records)
    knowledge_ids = tuple(record.knowledge_id for record in records)
    scopes = tuple((record.product_id, record.variant_id) for record in records)
    if len(set(governed_ids)) != 18 or len(set(knowledge_ids)) != 18:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 mapping identity duplication."
        )
    if len(set(scopes)) != 18 or any(variant_id is None for _, variant_id in scopes):
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 mapping scope duplication or null variant."
        )
    counts = dict(Counter(record.product_id for record in records))
    if counts != _PRODUCT_COUNTS:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 mapping product distribution drift."
        )
    return tuple(sorted(records, key=lambda record: (record.product_id, record.variant_id)))


def _read_evidence(
    paths: dict[str, Path],
    exact18_records: Tuple[object, ...],
) -> tuple[Tuple[object, ...], dict[tuple[str, str], dict[str, object]]]:
    repository = SqliteEvidenceCollectionRepository(paths["evidence_db"])
    lookup = repository.get_by_collection_id(_COLLECTION_ID)
    if lookup.status != "found" or lookup.collection is None:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact frozen Evidence collection was not found."
        )

    items = tuple(sorted(lookup.collection.evidence_items, key=lambda item: item.evidence_id))
    if len(items) != 18:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 Evidence item count drift."
        )

    by_scope: dict[tuple[str, str], dict[str, object]] = {}
    for item in items:
        if item.content_type != _STRUCTURED_CONTENT_TYPE:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence content type drift."
            )
        payload = json.loads(item.content)
        if not isinstance(payload, dict):
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence payload root drift."
            )
        product_id = payload.get("product_id")
        variant_id = payload.get("variant_id")
        if not isinstance(product_id, str) or not isinstance(variant_id, str):
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence product/variant identity missing."
            )
        scope = (product_id, variant_id)
        if scope in by_scope:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "duplicate exact18 Evidence scope."
            )
        if payload.get("knowledge_kind") != "product_variant_identity":
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence knowledge kind drift."
            )
        if item.provenance.atomic_knowledge_id != payload.get("atomic_knowledge_id"):
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence atomic knowledge lineage drift."
            )
        by_scope[scope] = payload

    if dict(Counter(scope[0] for scope in by_scope)) != _PRODUCT_COUNTS:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "exact18 Evidence product distribution drift."
        )

    for mapping in exact18_records:
        payload = by_scope.get((mapping.product_id, mapping.variant_id))
        if payload is None:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 mapping has no matching Evidence scope."
            )
        if payload.get("atomic_knowledge_id") != mapping.knowledge_id:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 mapping/Evidence knowledge identity drift."
            )
        variant_name = payload.get("variant_name_verbatim")
        if not isinstance(variant_name, str) or not variant_name.strip():
            raise GroundedPromptApplicationFoundationProviderContractError(
                "exact18 Evidence verbatim variant name missing."
            )

    return items, by_scope


def _build_catalog(
    exact18_records: Tuple[object, ...],
    evidence_by_scope: dict[tuple[str, str], dict[str, object]],
) -> ProductCatalog:
    products = tuple(
        ProductRecord(product_id, _PRODUCT_NAMES[product_id], "RSV", "active")
        for product_id in sorted(_PRODUCT_NAMES)
    )
    variants = tuple(
        VariantRecord(
            mapping.variant_id,
            mapping.product_id,
            evidence_by_scope[(mapping.product_id, mapping.variant_id)][
                "variant_name_verbatim"
            ],
            "active",
        )
        for mapping in exact18_records
    )
    catalog = ProductCatalog(products=products, variants=variants)
    if len(catalog.products) != 3 or len(catalog.variants) != 18:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "frozen pilot ProductCatalog count drift."
        )
    return catalog


def _read_governed(
    repository: SqliteGovernedKnowledgeRepository,
    mappings: Tuple[object, ...],
    *,
    require_support_source: bool,
) -> Tuple[object, ...]:
    values = []
    for mapping in mappings:
        lookup = repository.get_by_governed_knowledge_revision(
            mapping.governed_knowledge_id,
            1,
        )
        if lookup.issue is not None or lookup.governed_knowledge is None:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "GovernedKnowledge exact revision readback failed."
            )
        governed = lookup.governed_knowledge
        if require_support_source:
            support_source_ids = {
                support.source_id
                for support in governed.support
                if hasattr(support, "source_id")
            }
            if mapping.source_id not in support_source_ids:
                raise GroundedPromptApplicationFoundationProviderContractError(
                    "GovernedKnowledge support source identity drift."
                )
        values.append(governed)
    return tuple(values)


def _materialize_product_manual_foundation(
    paths: dict[str, Path],
    governed_repository: SqliteGovernedKnowledgeRepository,
) -> tuple[Tuple[object, ...], Tuple[IngestionManifestRecord, ...], Tuple[object, ...]]:
    mappings = tuple(
        materialize_canonical_knowledge_taxonomy_mapping_records(
            _load_json_object(paths["base_mapping"], "base mapping")
        )
    )
    if len(mappings) != 3:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "product manual mapping count drift."
        )
    mappings = tuple(sorted(mappings, key=lambda record: record.product_id))
    if tuple(record.product_id for record in mappings) != tuple(sorted(_PRODUCT_NAMES)):
        raise GroundedPromptApplicationFoundationProviderContractError(
            "product manual mapping product set drift."
        )

    manifests = []
    for mapping in mappings:
        expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS.get(mapping.product_id)
        if expected is None:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "product manual mapping outside exact pilot scope."
            )
        actual = {
            "governed_knowledge_id": mapping.governed_knowledge_id,
            "knowledge_id": mapping.knowledge_id,
            "source_id": mapping.source_id,
            "source_asset_id": mapping.source_asset_id,
            "knowledge_type": mapping.knowledge_type,
            "subject": mapping.subject,
            "property": mapping.property,
        }
        expected_projection = {
            key: expected[key]
            for key in (
                "governed_knowledge_id",
                "knowledge_id",
                "source_id",
                "source_asset_id",
                "knowledge_type",
                "subject",
                "property",
            )
        }
        if mapping.variant_id is not None or actual != expected_projection:
            raise GroundedPromptApplicationFoundationProviderContractError(
                "product manual mapping identity/provenance drift."
            )
        manifests.append(
            IngestionManifestRecord(
                source_path=expected["source_path"],
                source_sha256=expected["source_sha256"],
                product_id=mapping.product_id,
                variant_id=None,
                knowledge_type="product_manual",
                asset_type="pdf",
                source=expected["source_id"],
                authority="RSV_INTERNAL_APPROVED_SOURCE",
                version="2026-08-09",
                status="active",
            )
        )

    governed = _read_governed(
        governed_repository,
        mappings,
        require_support_source=True,
    )
    return governed, tuple(manifests), mappings


def load_frozen_pilot_grounded_prompt_application_foundation(
    *,
    intake_root: str | Path,
) -> GroundedPromptApplicationFoundation:
    """Load the exact frozen pilot foundation with no semantic selection."""

    try:
        paths = _verified_artifact_paths(intake_root)
        exact18_records = _materialize_exact18(paths)
        evidence_items, evidence_by_scope = _read_evidence(paths, exact18_records)
        catalog = _build_catalog(exact18_records, evidence_by_scope)

        governed_repository = SqliteGovernedKnowledgeRepository(paths["governed_db"])
        identity_governed = _read_governed(
            governed_repository,
            exact18_records,
            require_support_source=False,
        )
        (
            product_constraint_governed,
            product_constraint_manifests,
            product_constraint_mappings,
        ) = _materialize_product_manual_foundation(
            paths,
            governed_repository,
        )

        _verified_artifact_paths(intake_root)

        return GroundedPromptApplicationFoundation(
            collection_id=_COLLECTION_ID,
            catalog=catalog,
            governed_knowledge=identity_governed,
            knowledge_mappings=exact18_records,
            traceable_evidence_items=evidence_items,
            product_constraint_governed_knowledge=product_constraint_governed,
            product_constraint_ingestion_manifest_records=product_constraint_manifests,
            product_constraint_knowledge_mappings=product_constraint_mappings,
        )
    except GroundedPromptApplicationFoundationProviderContractError:
        raise
    except Exception as exc:
        raise GroundedPromptApplicationFoundationProviderContractError(
            "frozen pilot foundation assembly failed: "
            + type(exc).__name__
            + ": "
            + str(exc)
        ) from exc
