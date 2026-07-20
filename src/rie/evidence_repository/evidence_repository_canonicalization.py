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
    EVIDENCE_ELIGIBILITY_FIELD_ORDER,
    TRACEABLE_EVIDENCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
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


__all__ = (
    "serialize_evidence_collection_repository_payload",
    "deserialize_evidence_collection_repository_payload",
    "calculate_evidence_collection_repository_payload_digest",
    "calculate_evidence_repository_revision_id",
    "calculate_evidence_repository_audit_id",
)
