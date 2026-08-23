from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re

from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_ID_PREFIX,
    EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_ID_PREFIX,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceStructuredMetadataProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION,
    EvidenceRepositoryWriteRequest,
)
from rie.rsv_knowledge.product_variant_identity_bridge import (
    BRIDGE_STATUS_MATERIALIZED,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
    ProductVariantIdentityEvidenceAdmissionRequest,
    materialize_product_variant_identity_evidence_admission,
)


PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION = (
    "product_variant_identity_structured_metadata_evidence_binding_request_contract_v1"
)
PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_RESULT_CONTRACT_VERSION = (
    "product_variant_identity_structured_metadata_evidence_binding_result_contract_v1"
)
PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID = (
    "pilot-phase-a-product-variant-identity-atomic-knowledge-construction-result"
)
PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256 = (
    "33339f9507ba56e095cb1b4a5a0fcf5d029bd184798bf750901c5a951c3ac72e"
)
PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE = "structured_metadata"
PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION = (
    "operator_approved_product_variant_identity_atomic_knowledge"
)
PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS = "operator_approved_derived"
PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS = "locked"
PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON = (
    "exact18_product_variant_identity_atomic_records_are_operator_approved_and_locked_"
    "for_bounded_evidence_materialization"
)
PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID = (
    "rcis-product-variant-structured-metadata-evidence-eligibility"
)
PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION = "1.0.0"
PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION = (
    "phase-a-exact18-109-v1"
)

_EXPECTED_PAYLOAD_KEYS = (
    "atomic_construction_authority_decision_packet_sha256",
    "atomic_knowledge_id",
    "atomic_statement",
    "downstream_binding_policy_decision_packet_sha256",
    "identity_capture_sha256",
    "knowledge_kind",
    "manifest_sha256",
    "product_family",
    "product_id",
    "source_authority",
    "source_relative_paths",
    "source_status",
    "source_type",
    "source_version",
    "variant_id",
    "variant_name_verbatim",
)


def _is_sha256(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _require_text(value: object, label: str) -> None:
    if type(value) is not str or not value:
        raise ValueError(label + " must be non-empty text")


def _require_utc(value: object) -> None:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
        or value.utcoffset().total_seconds() != 0
    ):
        raise ValueError("recorded_at_utc must be timezone-aware UTC")


def _canonical_admission_payload_text(
    payload: tuple[tuple[str, object], ...],
) -> str:
    ordered = OrderedDict(payload)
    if tuple(ordered) != _EXPECTED_PAYLOAD_KEYS:
        raise ValueError("admission payload field order mismatch")
    return (
        json.dumps(
            ordered,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def _validate_snapshot(snapshot: EvidenceEligibilitySnapshot) -> None:
    if type(snapshot) is not EvidenceEligibilitySnapshot:
        raise TypeError("eligibility_snapshot must be exact EvidenceEligibilitySnapshot")
    expected = (
        (snapshot.source_id, PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID),
        (snapshot.source_checksum, PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256),
        (snapshot.source_type, PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE),
        (
            snapshot.document_classification,
            PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION,
        ),
        (snapshot.authority_status, PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS),
        (snapshot.lifecycle_status, PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS),
        (snapshot.evidence_eligibility, "eligible"),
        (snapshot.evidence_collection_allowed, True),
        (snapshot.requires_review, False),
        (snapshot.reason, PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON),
        (snapshot.policy_id, PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID),
        (
            snapshot.policy_version,
            PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION,
        ),
        (
            snapshot.registry_version,
            PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION,
        ),
    )
    if any(actual != required for actual, required in expected):
        raise ValueError("eligibility_snapshot is outside the approved exact18/109 pilot scope")


@dataclass(frozen=True)
class ProductVariantIdentityStructuredMetadataEvidenceBindingRequest:
    contract_version: str
    admission_requests: tuple[ProductVariantIdentityEvidenceAdmissionRequest, ...]
    eligibility_snapshot: EvidenceEligibilitySnapshot
    artifact_contract_version: str
    artifact_id: str
    upstream_contract_version: str
    job_id: str
    actor_id: str
    recorded_at_utc: datetime

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported binding request contract version")
        if (
            type(self.admission_requests) is not tuple
            or len(self.admission_requests) != 18
            or any(
                type(value) is not ProductVariantIdentityEvidenceAdmissionRequest
                for value in self.admission_requests
            )
        ):
            raise ValueError("admission_requests must be the exact 18-request tuple")

        _validate_snapshot(self.eligibility_snapshot)
        for value, label in (
            (self.artifact_contract_version, "artifact_contract_version"),
            (self.upstream_contract_version, "upstream_contract_version"),
            (self.job_id, "job_id"),
            (self.actor_id, "actor_id"),
        ):
            _require_text(value, label)
        if not _is_sha256(self.artifact_id):
            raise ValueError("artifact_id must be a SHA256 digest")
        if self.artifact_id != self.eligibility_snapshot.source_checksum:
            raise ValueError("artifact_id must equal the locked source checksum")
        _require_utc(self.recorded_at_utc)

        atomic_ids: list[str] = []
        all_paths: list[str] = []
        for request in self.admission_requests:
            if (
                request.contract_version
                != PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION
            ):
                raise ValueError("admission request contract mismatch")
            if (
                request.image_content_interpretation_attempted
                or request.additional_semantic_inference_attempted
                or request.repository_write_attempted
                or request.network_operation_attempted
            ):
                raise ValueError("admission request contains a forbidden attempted operation")
            unit = request.unit
            if unit.knowledge_kind != "product_variant_identity":
                raise ValueError("admission request knowledge kind mismatch")
            atomic_ids.append(unit.atomic_knowledge_id)
            all_paths.extend(unit.source_relative_paths)

        if len(set(atomic_ids)) != 18:
            raise ValueError("atomic knowledge IDs must be unique across exact18")
        if len(all_paths) != 109 or len(set(all_paths)) != 109:
            raise ValueError("source path scope must be exact109 and unique")


@dataclass(frozen=True)
class ProductVariantIdentityStructuredMetadataEvidenceBindingResult:
    contract_version: str
    collection: EvidenceCollection
    write_request: EvidenceRepositoryWriteRequest
    evidence_items: tuple[TraceableEvidence, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported binding result contract version")
        if type(self.collection) is not EvidenceCollection:
            raise TypeError("collection must be exact EvidenceCollection")
        if type(self.write_request) is not EvidenceRepositoryWriteRequest:
            raise TypeError("write_request must be exact EvidenceRepositoryWriteRequest")
        if (
            type(self.evidence_items) is not tuple
            or len(self.evidence_items) != 18
            or self.collection.evidence_items != self.evidence_items
        ):
            raise ValueError("evidence_items must match the exact18 collection")


def _provisional_evidence(
    *,
    content: str,
    content_digest: str,
    provenance: TraceableEvidenceStructuredMetadataProvenance,
    eligibility_snapshot_digest: str,
) -> TraceableEvidence:
    value = object.__new__(TraceableEvidence)
    object.__setattr__(
        value,
        "contract_version",
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
    )
    object.__setattr__(value, "evidence_id", TRACEABLE_EVIDENCE_ID_PREFIX + ("0" * 64))
    object.__setattr__(
        value,
        "content_type",
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    )
    object.__setattr__(value, "content", content)
    object.__setattr__(value, "content_digest", content_digest)
    object.__setattr__(value, "warnings", ())
    object.__setattr__(value, "provenance", provenance)
    object.__setattr__(
        value,
        "eligibility_snapshot_digest",
        eligibility_snapshot_digest,
    )
    object.__setattr__(value, "ocr_remediation_provenance", None)
    object.__setattr__(value, "atomic_text_derivation_provenance", None)
    return value


def _provisional_collection(
    *,
    request: ProductVariantIdentityStructuredMetadataEvidenceBindingRequest,
    evidence_items: tuple[TraceableEvidence, ...],
) -> EvidenceCollection:
    snapshot = request.eligibility_snapshot
    value = object.__new__(EvidenceCollection)
    object.__setattr__(
        value,
        "contract_version",
        EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
    )
    object.__setattr__(value, "collection_id", EVIDENCE_COLLECTION_ID_PREFIX + ("0" * 64))
    object.__setattr__(
        value,
        "artifact_contract_version",
        request.artifact_contract_version,
    )
    object.__setattr__(value, "artifact_id", request.artifact_id)
    object.__setattr__(
        value,
        "upstream_contract_version",
        request.upstream_contract_version,
    )
    object.__setattr__(value, "job_id", request.job_id)
    object.__setattr__(value, "source_id", snapshot.source_id)
    object.__setattr__(value, "source_path", snapshot.source_path)
    object.__setattr__(value, "source_checksum", snapshot.source_checksum)
    object.__setattr__(value, "eligibility_snapshot", snapshot)
    object.__setattr__(value, "evidence_items", evidence_items)
    return value


def materialize_product_variant_identity_structured_metadata_evidence_binding(
    request: ProductVariantIdentityStructuredMetadataEvidenceBindingRequest,
) -> ProductVariantIdentityStructuredMetadataEvidenceBindingResult:
    if type(request) is not ProductVariantIdentityStructuredMetadataEvidenceBindingRequest:
        raise TypeError(
            "request must be exact "
            "ProductVariantIdentityStructuredMetadataEvidenceBindingRequest"
        )
    request.__post_init__()

    snapshot_digest = derive_evidence_eligibility_snapshot_digest(
        request.eligibility_snapshot
    )
    evidence_items: list[TraceableEvidence] = []
    evidence_ids: set[str] = set()

    for admission_request in request.admission_requests:
        admission_result = materialize_product_variant_identity_evidence_admission(
            admission_request
        )
        if (
            admission_result.status != BRIDGE_STATUS_MATERIALIZED
            or admission_result.reason_codes != ()
        ):
            raise ValueError("bridge admission did not materialize cleanly")
        if (
            admission_result.locator_type
            != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE
            or admission_result.locator_schema_version
            != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION
        ):
            raise ValueError("bridge locator contract mismatch")

        content = _canonical_admission_payload_text(admission_result.payload)
        content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        unit = admission_request.unit
        provenance = TraceableEvidenceStructuredMetadataProvenance(
            contract_version=(
                TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION
            ),
            payload_type=PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
            payload_schema_version=(
                PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION
            ),
            locator_type=admission_result.locator_type,
            locator_value=admission_result.locator_value,
            locator_schema_version=admission_result.locator_schema_version,
            atomic_knowledge_id=unit.atomic_knowledge_id,
            source_relative_paths=unit.source_relative_paths,
            manifest_sha256=unit.manifest_sha256,
            identity_capture_sha256=unit.identity_capture_sha256,
            atomic_construction_authority_decision_packet_sha256=(
                unit.atomic_construction_authority_decision_packet_sha256
            ),
            downstream_binding_policy_decision_packet_sha256=(
                unit.downstream_binding_policy_decision_packet_sha256
            ),
            admission_payload_digest=content_digest,
        )
        provisional = _provisional_evidence(
            content=content,
            content_digest=content_digest,
            provenance=provenance,
            eligibility_snapshot_digest=snapshot_digest,
        )
        evidence_id = derive_traceable_evidence_id(provisional)
        if evidence_id in evidence_ids:
            raise ValueError("derived TraceableEvidence ID collision")
        evidence_ids.add(evidence_id)

        evidence_items.append(
            TraceableEvidence(
                contract_version=(
                    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION
                ),
                evidence_id=evidence_id,
                content_type=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
                content=content,
                content_digest=content_digest,
                warnings=(),
                provenance=provenance,
                eligibility_snapshot_digest=snapshot_digest,
            )
        )

    frozen_items = tuple(evidence_items)
    provisional_collection = _provisional_collection(
        request=request,
        evidence_items=frozen_items,
    )
    collection_id = derive_evidence_collection_id(provisional_collection)
    snapshot = request.eligibility_snapshot
    collection = EvidenceCollection(
        contract_version=EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
        collection_id=collection_id,
        artifact_contract_version=request.artifact_contract_version,
        artifact_id=request.artifact_id,
        upstream_contract_version=request.upstream_contract_version,
        job_id=request.job_id,
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=frozen_items,
    )
    payload_digest = calculate_evidence_collection_repository_payload_digest(
        collection
    )
    write_request = EvidenceRepositoryWriteRequest(
        contract_version=EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION,
        collection=collection,
        expected_collection_payload_digest=payload_digest,
        actor_id=request.actor_id,
        recorded_at_utc=request.recorded_at_utc,
    )
    return ProductVariantIdentityStructuredMetadataEvidenceBindingResult(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_RESULT_CONTRACT_VERSION
        ),
        collection=collection,
        write_request=write_request,
        evidence_items=frozen_items,
    )


__all__ = (
    "PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION",
    "PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_RESULT_CONTRACT_VERSION",
    "PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID",
    "PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256",
    "ProductVariantIdentityStructuredMetadataEvidenceBindingRequest",
    "ProductVariantIdentityStructuredMetadataEvidenceBindingResult",
    "materialize_product_variant_identity_structured_metadata_evidence_binding",
)
