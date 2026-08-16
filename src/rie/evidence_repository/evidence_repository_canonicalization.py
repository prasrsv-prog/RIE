from __future__ import annotations

from datetime import datetime
import hashlib
import json
from typing import Any

from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_FIELD_ORDER,
    EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION as _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_FIELD_ORDER,
    TRACEABLE_EVIDENCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION as _TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_OCR_FIELD_ORDER as _TRACEABLE_EVIDENCE_OCR_FIELD_ORDER,
    TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER as _TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceOcrRemediationProvenance as _TraceableEvidenceOcrRemediationProvenance,
    TraceableEvidenceProvenance,
)

from .evidence_repository_contract import (
    EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX,
    EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
)

_COLLECTION_PAYLOAD_FIELD_ORDER = EVIDENCE_COLLECTION_FIELD_ORDER
_REVISION_IDENTITY_FIELD_ORDER = (
    "contract_version",
    "source_id",
    "revision_number",
    "collection_id",
    "collection_payload_digest",
    "previous_revision_id",
)
_AUDIT_IDENTITY_FIELD_ORDER = (
    "contract_version",
    "action",
    "revision_id",
    "source_id",
    "revision_number",
    "collection_id",
    "actor_id",
    "recorded_at_utc",
)


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _eligibility_object(value: EvidenceEligibilitySnapshot) -> dict[str, Any]:
    return {
        name: getattr(value, name)
        for name in EVIDENCE_ELIGIBILITY_FIELD_ORDER
    }


def _provenance_object(value: TraceableEvidenceProvenance) -> dict[str, Any]:
    return {
        name: getattr(value, name)
        for name in TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER
    }


def _evidence_object(value: TraceableEvidence) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in TRACEABLE_EVIDENCE_FIELD_ORDER:
        item = getattr(value, name)
        if name == "warnings":
            item = list(item)
        elif name == "provenance":
            item = _provenance_object(item)
        result[name] = item
    return result


def _collection_object(value: EvidenceCollection) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in _COLLECTION_PAYLOAD_FIELD_ORDER:
        item = getattr(value, name)
        if name == "eligibility_snapshot":
            item = _eligibility_object(item)
        elif name == "evidence_items":
            item = [_evidence_object(entry) for entry in item]
        result[name] = item
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON constants are invalid")


def _object_from_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _require_object(
    value: object,
    expected_fields: tuple[str, ...],
    field_name: str,
) -> dict[str, Any]:
    if type(value) is not dict:
        raise ValueError(f"{field_name} must be an object")
    if tuple(value.keys()) != expected_fields:
        raise ValueError(f"{field_name} fields are invalid")
    return value


def _require_array(value: object, field_name: str) -> list[Any]:
    if type(value) is not list:
        raise ValueError(f"{field_name} must be an array")
    return value


def _format_utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def serialize_evidence_collection_repository_payload(
    collection: EvidenceCollection,
) -> bytes:
    if type(collection) is not EvidenceCollection:
        raise TypeError("collection must be EvidenceCollection")
    if collection.contract_version == _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION:
        return _d39_serialize_evidence_collection_repository_payload_v2(collection)
    if collection.contract_version != EVIDENCE_COLLECTION_CONTRACT_VERSION:
        raise ValueError("unsupported EvidenceCollection contract version")
    if derive_evidence_collection_id(collection) != collection.collection_id:
        raise ValueError("EvidenceCollection identity mismatch")
    for evidence in collection.evidence_items:
        if derive_traceable_evidence_id(evidence) != evidence.evidence_id:
            raise ValueError("TraceableEvidence identity mismatch")
        if _sha256(evidence.content.encode("utf-8")) != evidence.content_digest:
            raise ValueError("TraceableEvidence content digest mismatch")
        expected_snapshot_digest = derive_evidence_eligibility_snapshot_digest(
            collection.eligibility_snapshot
        )
        if evidence.eligibility_snapshot_digest != expected_snapshot_digest:
            raise ValueError("Evidence eligibility snapshot digest mismatch")
    return _canonical_json_bytes(_collection_object(collection))


def deserialize_evidence_collection_repository_payload(
    payload_bytes: bytes,
) -> EvidenceCollection:
    if type(payload_bytes) is not bytes:
        raise TypeError("payload_bytes must be bytes")
    if payload_bytes.startswith(
        b'{"contract_version":"evidence_collection_contract_v2",'
    ):
        return _d39_deserialize_evidence_collection_repository_payload_v2(
            payload_bytes
        )
    try:
        text = payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("payload is not valid UTF-8") from exc
    try:
        raw = json.loads(
            text,
            object_pairs_hook=_object_from_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("payload is not valid canonical JSON") from exc

    collection_data = _require_object(
        raw,
        _COLLECTION_PAYLOAD_FIELD_ORDER,
        "collection",
    )
    snapshot_data = _require_object(
        collection_data["eligibility_snapshot"],
        EVIDENCE_ELIGIBILITY_FIELD_ORDER,
        "eligibility_snapshot",
    )
    evidence_data = _require_array(
        collection_data["evidence_items"],
        "evidence_items",
    )

    snapshot = EvidenceEligibilitySnapshot(**snapshot_data)
    evidence_items: list[TraceableEvidence] = []

    for index, item in enumerate(evidence_data):
        evidence_object = _require_object(
            item,
            TRACEABLE_EVIDENCE_FIELD_ORDER,
            f"evidence_items[{index}]",
        )
        provenance_object = _require_object(
            evidence_object["provenance"],
            TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
            f"evidence_items[{index}].provenance",
        )
        warnings = _require_array(
            evidence_object["warnings"],
            f"evidence_items[{index}].warnings",
        )
        if any(type(value) is not str for value in warnings):
            raise ValueError("evidence warnings must contain strings")
        provenance = TraceableEvidenceProvenance(**provenance_object)
        evidence_items.append(
            TraceableEvidence(
                contract_version=evidence_object["contract_version"],
                evidence_id=evidence_object["evidence_id"],
                content_type=evidence_object["content_type"],
                content=evidence_object["content"],
                content_digest=evidence_object["content_digest"],
                warnings=tuple(warnings),
                provenance=provenance,
                eligibility_snapshot_digest=evidence_object[
                    "eligibility_snapshot_digest"
                ],
            )
        )

    collection = EvidenceCollection(
        contract_version=collection_data["contract_version"],
        collection_id=collection_data["collection_id"],
        artifact_contract_version=collection_data["artifact_contract_version"],
        artifact_id=collection_data["artifact_id"],
        upstream_contract_version=collection_data["upstream_contract_version"],
        job_id=collection_data["job_id"],
        source_id=collection_data["source_id"],
        source_path=collection_data["source_path"],
        source_checksum=collection_data["source_checksum"],
        eligibility_snapshot=snapshot,
        evidence_items=tuple(evidence_items),
    )

    if serialize_evidence_collection_repository_payload(collection) != payload_bytes:
        raise ValueError("payload bytes are not canonical")
    return collection


def calculate_evidence_collection_repository_payload_digest(
    collection: EvidenceCollection,
) -> str:
    return _sha256(serialize_evidence_collection_repository_payload(collection))


def calculate_evidence_repository_revision_id(
    *,
    source_id: str,
    revision_number: int,
    collection_id: str,
    collection_payload_digest: str,
    previous_revision_id: str | None,
) -> str:
    value = {
        "contract_version": (
            EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION
        ),
        "source_id": source_id,
        "revision_number": revision_number,
        "collection_id": collection_id,
        "collection_payload_digest": collection_payload_digest,
        "previous_revision_id": previous_revision_id,
    }
    if tuple(value.keys()) != _REVISION_IDENTITY_FIELD_ORDER:
        raise RuntimeError("revision identity field order mismatch")
    return EVIDENCE_REPOSITORY_REVISION_ID_PREFIX + _sha256(
        _canonical_json_bytes(value)
    )


def calculate_evidence_repository_audit_id(
    *,
    action: str,
    revision_id: str,
    source_id: str,
    revision_number: int,
    collection_id: str,
    actor_id: str,
    recorded_at_utc: datetime,
) -> str:
    value = {
        "contract_version": (
            EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION
        ),
        "action": action,
        "revision_id": revision_id,
        "source_id": source_id,
        "revision_number": revision_number,
        "collection_id": collection_id,
        "actor_id": actor_id,
        "recorded_at_utc": _format_utc(recorded_at_utc),
    }
    if tuple(value.keys()) != _AUDIT_IDENTITY_FIELD_ORDER:
        raise RuntimeError("audit identity field order mismatch")
    return EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX + _sha256(
        _canonical_json_bytes(value)
    )


# PR-086K-D39: minimum private Gate6-v2 repository payload compatibility.
def _d39_require_exact_keys(
    value: object,
    expected: tuple[str, ...],
    label: str,
) -> dict[str, object]:
    if type(value) is not dict:
        raise TypeError(label + " must be object")
    if tuple(value.keys()) != expected:
        raise ValueError(label + " field order mismatch")
    return value


def _d39_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    keys = [key for key, _value in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def _d39_reject_constant(value: str) -> object:
    raise ValueError("non-finite JSON constant is not supported: " + value)


def _d39_eligibility_object(
    snapshot: EvidenceEligibilitySnapshot,
) -> dict[str, object]:
    if type(snapshot) is not EvidenceEligibilitySnapshot:
        raise TypeError("snapshot must be exact EvidenceEligibilitySnapshot")
    payload = {
        "contract_version": snapshot.contract_version,
        "source_id": snapshot.source_id,
        "source_path": snapshot.source_path,
        "source_checksum": snapshot.source_checksum,
        "source_type": snapshot.source_type,
        "document_classification": snapshot.document_classification,
        "authority_status": snapshot.authority_status,
        "lifecycle_status": snapshot.lifecycle_status,
        "evidence_eligibility": snapshot.evidence_eligibility,
        "evidence_collection_allowed": snapshot.evidence_collection_allowed,
        "requires_review": snapshot.requires_review,
        "reason": snapshot.reason,
        "policy_id": snapshot.policy_id,
        "policy_version": snapshot.policy_version,
        "registry_version": snapshot.registry_version,
    }
    if tuple(payload) != EVIDENCE_ELIGIBILITY_FIELD_ORDER:
        raise RuntimeError("eligibility field order is invalid")
    return payload


def _d39_provenance_object(
    provenance: TraceableEvidenceProvenance,
) -> dict[str, object]:
    if type(provenance) is not TraceableEvidenceProvenance:
        raise TypeError("provenance must be exact TraceableEvidenceProvenance")
    payload = {
        "artifact_contract_version": provenance.artifact_contract_version,
        "artifact_id": provenance.artifact_id,
        "upstream_contract_version": provenance.upstream_contract_version,
        "job_id": provenance.job_id,
        "source_id": provenance.source_id,
        "source_path": provenance.source_path,
        "source_checksum": provenance.source_checksum,
        "page_index": provenance.page_index,
        "page_number": provenance.page_number,
        "extraction_index": provenance.extraction_index,
        "extraction_method": provenance.extraction_method,
        "extraction_status": provenance.extraction_status,
        "execution_report_location": provenance.execution_report_location,
    }
    if tuple(payload) != TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER:
        raise RuntimeError("provenance field order is invalid")
    return payload


def _d39_ocr_provenance_object(
    provenance: _TraceableEvidenceOcrRemediationProvenance,
) -> dict[str, object]:
    if type(provenance) is not _TraceableEvidenceOcrRemediationProvenance:
        raise TypeError(
            "ocr_remediation_provenance must be exact "
            "TraceableEvidenceOcrRemediationProvenance"
        )
    payload = {
        "producer_operation_id": provenance.producer_operation_id,
        "producer_artifact_path": provenance.producer_artifact_path,
        "producer_artifact_sha256": provenance.producer_artifact_sha256,
        "producer_artifact_set_digest": provenance.producer_artifact_set_digest,
        "extraction_method": provenance.extraction_method,
    }
    if tuple(payload) != _TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER:
        raise RuntimeError("OCR remediation provenance field order is invalid")
    return payload


def _d39_evidence_object_v2(
    evidence: TraceableEvidence,
) -> dict[str, object]:
    if type(evidence) is not TraceableEvidence:
        raise TypeError("evidence must be exact TraceableEvidence")
    if evidence.contract_version != _TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION:
        raise ValueError("unsupported TraceableEvidence contract version")
    ocr = getattr(evidence, "ocr_remediation_provenance", None)
    payload = {
        "contract_version": evidence.contract_version,
        "evidence_id": evidence.evidence_id,
        "content_type": evidence.content_type,
        "content": evidence.content,
        "content_digest": evidence.content_digest,
        "warnings": list(evidence.warnings),
        "provenance": _d39_provenance_object(evidence.provenance),
        "eligibility_snapshot_digest": evidence.eligibility_snapshot_digest,
        "ocr_remediation_provenance": _d39_ocr_provenance_object(ocr),
    }
    if tuple(payload) != _TRACEABLE_EVIDENCE_OCR_FIELD_ORDER:
        raise RuntimeError("TraceableEvidence v2 field order is invalid")
    return payload


def _d39_collection_object_v2(
    collection: EvidenceCollection,
) -> dict[str, object]:
    payload = {
        "contract_version": collection.contract_version,
        "collection_id": collection.collection_id,
        "artifact_contract_version": collection.artifact_contract_version,
        "artifact_id": collection.artifact_id,
        "upstream_contract_version": collection.upstream_contract_version,
        "job_id": collection.job_id,
        "source_id": collection.source_id,
        "source_path": collection.source_path,
        "source_checksum": collection.source_checksum,
        "eligibility_snapshot": _d39_eligibility_object(
            collection.eligibility_snapshot
        ),
        "evidence_items": [
            _d39_evidence_object_v2(item)
            for item in collection.evidence_items
        ],
    }
    if tuple(payload) != EVIDENCE_COLLECTION_FIELD_ORDER:
        raise RuntimeError("EvidenceCollection v2 field order is invalid")
    return payload


def _d39_serialize_evidence_collection_repository_payload_v2(
    collection: EvidenceCollection,
) -> bytes:
    if type(collection) is not EvidenceCollection:
        raise TypeError("collection must be exact EvidenceCollection")
    collection.__post_init__()
    if collection.contract_version != _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION:
        raise ValueError("unsupported EvidenceCollection contract version")
    if derive_evidence_collection_id(collection) != collection.collection_id:
        raise ValueError("EvidenceCollection identity mismatch")
    expected_snapshot_digest = derive_evidence_eligibility_snapshot_digest(
        collection.eligibility_snapshot
    )
    for evidence in collection.evidence_items:
        evidence.__post_init__()
        if evidence.contract_version != _TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION:
            raise ValueError("unsupported TraceableEvidence contract version")
        if derive_traceable_evidence_id(evidence) != evidence.evidence_id:
            raise ValueError("TraceableEvidence identity mismatch")
        if _sha256(evidence.content.encode("utf-8")) != evidence.content_digest:
            raise ValueError("TraceableEvidence content digest mismatch")
        if evidence.eligibility_snapshot_digest != expected_snapshot_digest:
            raise ValueError("Evidence eligibility snapshot digest mismatch")
        if any(type(warning) is not str for warning in evidence.warnings):
            raise TypeError("evidence warnings must contain strings")
        if type(getattr(evidence, "ocr_remediation_provenance", None)) is not (
            _TraceableEvidenceOcrRemediationProvenance
        ):
            raise ValueError("TraceableEvidence v2 OCR provenance is required")
    return _canonical_json_bytes(_d39_collection_object_v2(collection))


def _d39_deserialize_evidence_collection_repository_payload_v2(
    payload_bytes: bytes,
) -> EvidenceCollection:
    if type(payload_bytes) is not bytes:
        raise TypeError("payload_bytes must be bytes")
    try:
        text = payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("payload must be UTF-8") from exc
    try:
        raw = json.loads(
            text,
            object_pairs_hook=_d39_pairs,
            parse_constant=_d39_reject_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("payload JSON is invalid") from exc

    collection_data = _d39_require_exact_keys(
        raw,
        EVIDENCE_COLLECTION_FIELD_ORDER,
        "EvidenceCollection",
    )
    if collection_data["contract_version"] != _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION:
        raise ValueError("unsupported EvidenceCollection contract version")

    snapshot_data = _d39_require_exact_keys(
        collection_data["eligibility_snapshot"],
        EVIDENCE_ELIGIBILITY_FIELD_ORDER,
        "EvidenceEligibilitySnapshot",
    )
    snapshot = EvidenceEligibilitySnapshot(**snapshot_data)

    evidence_raw = collection_data["evidence_items"]
    if type(evidence_raw) is not list:
        raise TypeError("evidence_items must be array")

    evidence_items = []
    for evidence_value in evidence_raw:
        evidence_data = _d39_require_exact_keys(
            evidence_value,
            _TRACEABLE_EVIDENCE_OCR_FIELD_ORDER,
            "TraceableEvidence",
        )
        if evidence_data["contract_version"] != _TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION:
            raise ValueError("unsupported TraceableEvidence contract version")

        warnings = evidence_data["warnings"]
        if type(warnings) is not list:
            raise TypeError("warnings must be array")
        if any(type(warning) is not str for warning in warnings):
            raise TypeError("evidence warnings must contain strings")

        provenance_data = _d39_require_exact_keys(
            evidence_data["provenance"],
            TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
            "TraceableEvidenceProvenance",
        )
        provenance = TraceableEvidenceProvenance(**provenance_data)

        ocr_data = _d39_require_exact_keys(
            evidence_data["ocr_remediation_provenance"],
            _TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER,
            "TraceableEvidenceOcrRemediationProvenance",
        )
        ocr = _TraceableEvidenceOcrRemediationProvenance(**ocr_data)

        evidence_items.append(
            TraceableEvidence(
                contract_version=evidence_data["contract_version"],
                evidence_id=evidence_data["evidence_id"],
                content_type=evidence_data["content_type"],
                content=evidence_data["content"],
                content_digest=evidence_data["content_digest"],
                warnings=tuple(warnings),
                provenance=provenance,
                eligibility_snapshot_digest=(
                    evidence_data["eligibility_snapshot_digest"]
                ),
                ocr_remediation_provenance=ocr,
            )
        )

    collection = EvidenceCollection(
        contract_version=collection_data["contract_version"],
        collection_id=collection_data["collection_id"],
        artifact_contract_version=collection_data["artifact_contract_version"],
        artifact_id=collection_data["artifact_id"],
        upstream_contract_version=collection_data["upstream_contract_version"],
        job_id=collection_data["job_id"],
        source_id=collection_data["source_id"],
        source_path=collection_data["source_path"],
        source_checksum=collection_data["source_checksum"],
        eligibility_snapshot=snapshot,
        evidence_items=tuple(evidence_items),
    )
    if _d39_serialize_evidence_collection_repository_payload_v2(collection) != payload_bytes:
        raise ValueError("payload is not canonical")
    return collection

__all__ = (
    "serialize_evidence_collection_repository_payload",
    "deserialize_evidence_collection_repository_payload",
    "calculate_evidence_collection_repository_payload_digest",
    "calculate_evidence_repository_revision_id",
    "calculate_evidence_repository_audit_id",
)
