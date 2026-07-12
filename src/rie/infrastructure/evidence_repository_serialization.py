"""Pure deterministic persistence serialization for evidence repository records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata

from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceDiagnostic,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)


EVIDENCE_PERSISTENCE_CONTRACT_VERSION = "1.0.0"
ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID = "accepted-evidence-json-v1"
ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID = "acceptance-record-json-v1"
PERSISTENCE_DIGEST_ALGORITHM = "sha256"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")
_EVIDENCE_IDENTITY_POLICY_ID = "rcis-evidence-identity"
_EVIDENCE_IDENTITY_POLICY_VERSION = "1.0.0"
_ACCEPTANCE_IDENTITY_POLICY_ID = "rcis-acceptance-record-identity"
_ACCEPTANCE_IDENTITY_POLICY_VERSION = "1.0.0"
_CANONICAL_DATETIME_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
)


@dataclass(frozen=True)
class SerializedAcceptedEvidenceRecord:
    persistence_contract_version: str
    payload_schema_id: str
    evidence_id: str
    identity_policy_id: str
    identity_policy_version: str
    canonical_identity_digest: str
    payload_bytes_digest: str
    payload_bytes: bytes

    def __post_init__(self) -> None:
        _require_exact_string(
            self.persistence_contract_version,
            "persistence_contract_version",
        )
        _require_exact_string(
            self.payload_schema_id,
            "payload_schema_id",
        )
        _require_identifier(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        _require_exact_string(
            self.identity_policy_id,
            "identity_policy_id",
        )
        _require_exact_string(
            self.identity_policy_version,
            "identity_policy_version",
        )
        _require_digest(
            self.canonical_identity_digest,
            "canonical_identity_digest",
        )
        _require_digest(
            self.payload_bytes_digest,
            "payload_bytes_digest",
        )
        if type(self.payload_bytes) is not bytes:
            raise ValueError("payload_bytes must be exact bytes")


@dataclass(frozen=True)
class SerializedAcceptanceRecord:
    persistence_contract_version: str
    payload_schema_id: str
    acceptance_record_id: str
    evidence_id: str
    identity_policy_id: str
    identity_policy_version: str
    canonical_identity_digest: str
    payload_bytes_digest: str
    payload_bytes: bytes

    def __post_init__(self) -> None:
        _require_exact_string(
            self.persistence_contract_version,
            "persistence_contract_version",
        )
        _require_exact_string(
            self.payload_schema_id,
            "payload_schema_id",
        )
        _require_identifier(
            self.acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_ID_PATTERN,
        )
        _require_identifier(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        _require_exact_string(
            self.identity_policy_id,
            "identity_policy_id",
        )
        _require_exact_string(
            self.identity_policy_version,
            "identity_policy_version",
        )
        _require_digest(
            self.canonical_identity_digest,
            "canonical_identity_digest",
        )
        _require_digest(
            self.payload_bytes_digest,
            "payload_bytes_digest",
        )
        if type(self.payload_bytes) is not bytes:
            raise ValueError("payload_bytes must be exact bytes")


def serialize_accepted_evidence(
    accepted_evidence: AcceptedEvidence,
    canonical_identity_digest: str,
) -> SerializedAcceptedEvidenceRecord:
    if type(accepted_evidence) is not AcceptedEvidence:
        raise ValueError(
            "accepted_evidence must be an exact AcceptedEvidence"
        )

    digest = _require_digest(
        canonical_identity_digest,
        "canonical_identity_digest",
    )
    evidence_id = _require_identifier(
        accepted_evidence.evidence_id,
        "accepted_evidence.evidence_id",
        _EVIDENCE_ID_PATTERN,
    )
    _require_identifier_digest_match(
        evidence_id,
        digest,
        "accepted_evidence.evidence_id",
    )

    identity_result = calculate_evidence_identity(
        identity_input_from_accepted_evidence(accepted_evidence)
    )
    _verify_evidence_identity(
        accepted_evidence,
        digest,
        identity_result,
    )

    payload_object = _accepted_evidence_to_object(accepted_evidence)
    payload_bytes = _canonical_json_bytes(payload_object)

    return SerializedAcceptedEvidenceRecord(
        persistence_contract_version=(
            EVIDENCE_PERSISTENCE_CONTRACT_VERSION
        ),
        payload_schema_id=ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID,
        evidence_id=evidence_id,
        identity_policy_id=identity_result.identity_policy_id,
        identity_policy_version=(
            identity_result.identity_policy_version
        ),
        canonical_identity_digest=digest,
        payload_bytes_digest=_sha256(payload_bytes),
        payload_bytes=payload_bytes,
    )


def deserialize_accepted_evidence(
    serialized: SerializedAcceptedEvidenceRecord,
) -> AcceptedEvidence:
    if type(serialized) is not SerializedAcceptedEvidenceRecord:
        raise ValueError(
            "serialized must be an exact "
            "SerializedAcceptedEvidenceRecord"
        )

    _require_supported_metadata(
        serialized.persistence_contract_version,
        serialized.payload_schema_id,
        ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID,
    )
    evidence_id = _require_identifier(
        serialized.evidence_id,
        "serialized.evidence_id",
        _EVIDENCE_ID_PATTERN,
    )
    digest = _require_digest(
        serialized.canonical_identity_digest,
        "serialized.canonical_identity_digest",
    )
    _require_identifier_digest_match(
        evidence_id,
        digest,
        "serialized.evidence_id",
    )
    _require_expected_identity_metadata(
        serialized.identity_policy_id,
        serialized.identity_policy_version,
        _EVIDENCE_IDENTITY_POLICY_ID,
        _EVIDENCE_IDENTITY_POLICY_VERSION,
    )
    _verify_payload_digest(serialized)

    payload_object = _decode_canonical_json(serialized.payload_bytes)
    accepted_evidence = _accepted_evidence_from_object(payload_object)

    if accepted_evidence.evidence_id != evidence_id:
        raise ValueError("serialized evidence_id mismatch")

    identity_result = calculate_evidence_identity(
        identity_input_from_accepted_evidence(accepted_evidence)
    )
    _verify_evidence_identity(
        accepted_evidence,
        digest,
        identity_result,
    )
    _verify_identity_metadata(
        serialized.identity_policy_id,
        serialized.identity_policy_version,
        identity_result.identity_policy_id,
        identity_result.identity_policy_version,
    )
    return accepted_evidence


def serialize_acceptance_record(
    acceptance_record: AcceptanceRecord,
    canonical_identity_digest: str,
) -> SerializedAcceptanceRecord:
    if type(acceptance_record) is not AcceptanceRecord:
        raise ValueError(
            "acceptance_record must be an exact AcceptanceRecord"
        )

    digest = _require_digest(
        canonical_identity_digest,
        "canonical_identity_digest",
    )
    acceptance_record_id = _require_identifier(
        acceptance_record.acceptance_record_id,
        "acceptance_record.acceptance_record_id",
        _ACCEPTANCE_ID_PATTERN,
    )
    evidence_id = _require_identifier(
        acceptance_record.evidence_id,
        "acceptance_record.evidence_id",
        _EVIDENCE_ID_PATTERN,
    )
    _require_identifier_digest_match(
        acceptance_record_id,
        digest,
        "acceptance_record.acceptance_record_id",
    )

    identity_result = calculate_acceptance_identity(
        acceptance_identity_input_from_record(acceptance_record)
    )
    _verify_acceptance_identity(
        acceptance_record,
        digest,
        identity_result,
    )

    payload_object = _acceptance_record_to_object(acceptance_record)
    payload_bytes = _canonical_json_bytes(payload_object)

    return SerializedAcceptanceRecord(
        persistence_contract_version=(
            EVIDENCE_PERSISTENCE_CONTRACT_VERSION
        ),
        payload_schema_id=ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID,
        acceptance_record_id=acceptance_record_id,
        evidence_id=evidence_id,
        identity_policy_id=identity_result.identity_policy_id,
        identity_policy_version=(
            identity_result.identity_policy_version
        ),
        canonical_identity_digest=digest,
        payload_bytes_digest=_sha256(payload_bytes),
        payload_bytes=payload_bytes,
    )


def deserialize_acceptance_record(
    serialized: SerializedAcceptanceRecord,
) -> AcceptanceRecord:
    if type(serialized) is not SerializedAcceptanceRecord:
        raise ValueError(
            "serialized must be an exact "
            "SerializedAcceptanceRecord"
        )

    _require_supported_metadata(
        serialized.persistence_contract_version,
        serialized.payload_schema_id,
        ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID,
    )
    acceptance_record_id = _require_identifier(
        serialized.acceptance_record_id,
        "serialized.acceptance_record_id",
        _ACCEPTANCE_ID_PATTERN,
    )
    evidence_id = _require_identifier(
        serialized.evidence_id,
        "serialized.evidence_id",
        _EVIDENCE_ID_PATTERN,
    )
    digest = _require_digest(
        serialized.canonical_identity_digest,
        "serialized.canonical_identity_digest",
    )
    _require_identifier_digest_match(
        acceptance_record_id,
        digest,
        "serialized.acceptance_record_id",
    )
    _require_expected_identity_metadata(
        serialized.identity_policy_id,
        serialized.identity_policy_version,
        _ACCEPTANCE_IDENTITY_POLICY_ID,
        _ACCEPTANCE_IDENTITY_POLICY_VERSION,
    )
    _verify_payload_digest(serialized)

    payload_object = _decode_canonical_json(serialized.payload_bytes)
    acceptance_record = _acceptance_record_from_object(payload_object)

    if acceptance_record.acceptance_record_id != acceptance_record_id:
        raise ValueError("serialized acceptance_record_id mismatch")
    if acceptance_record.evidence_id != evidence_id:
        raise ValueError("serialized evidence_id mismatch")

    identity_result = calculate_acceptance_identity(
        acceptance_identity_input_from_record(acceptance_record)
    )
    _verify_acceptance_identity(
        acceptance_record,
        digest,
        identity_result,
    )
    _verify_identity_metadata(
        serialized.identity_policy_id,
        serialized.identity_policy_version,
        identity_result.identity_policy_id,
        identity_result.identity_policy_version,
    )
    return acceptance_record


def _require_exact_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value:
        raise ValueError(f"{field_name} must be a non-empty exact string")
    return value


def _require_digest(value: object, field_name: str) -> str:
    if type(value) is not str or _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be lowercase SHA-256")
    return value


def _require_identifier(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")
    return value


def _require_identifier_digest_match(
    identifier: str,
    digest: str,
    field_name: str,
) -> None:
    if identifier[4:] != digest:
        raise ValueError(f"{field_name} digest suffix mismatch")


def _require_supported_metadata(
    contract_version: object,
    payload_schema_id: object,
    expected_schema_id: str,
) -> None:
    if contract_version != EVIDENCE_PERSISTENCE_CONTRACT_VERSION:
        raise ValueError("unsupported persistence contract version")
    if payload_schema_id != expected_schema_id:
        raise ValueError("unsupported payload schema id")


def _require_expected_identity_metadata(
    policy_id: object,
    policy_version: object,
    expected_policy_id: str,
    expected_policy_version: str,
) -> None:
    if policy_id != expected_policy_id:
        raise ValueError("identity policy id mismatch")
    if policy_version != expected_policy_version:
        raise ValueError("identity policy version mismatch")


def _verify_identity_metadata(
    stored_policy_id: str,
    stored_policy_version: str,
    calculated_policy_id: str,
    calculated_policy_version: str,
) -> None:
    if stored_policy_id != calculated_policy_id:
        raise ValueError("identity policy id mismatch")
    if stored_policy_version != calculated_policy_version:
        raise ValueError("identity policy version mismatch")


def _verify_evidence_identity(
    accepted_evidence: AcceptedEvidence,
    digest: str,
    identity_result: object,
) -> None:
    if identity_result.digest_hex != digest:
        raise ValueError("evidence identity digest mismatch")
    if identity_result.evidence_id != accepted_evidence.evidence_id:
        raise ValueError("evidence identity id mismatch")


def _verify_acceptance_identity(
    acceptance_record: AcceptanceRecord,
    digest: str,
    identity_result: object,
) -> None:
    if identity_result.digest_hex != digest:
        raise ValueError("acceptance identity digest mismatch")
    if (
        identity_result.acceptance_record_id
        != acceptance_record.acceptance_record_id
    ):
        raise ValueError("acceptance identity id mismatch")


def _verify_payload_digest(serialized: object) -> None:
    payload_digest = _require_digest(
        serialized.payload_bytes_digest,
        "serialized.payload_bytes_digest",
    )
    if type(serialized.payload_bytes) is not bytes:
        raise ValueError("serialized.payload_bytes must be exact bytes")
    if _sha256(serialized.payload_bytes) != payload_digest:
        raise ValueError("payload bytes digest mismatch")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _normalize_string(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _normalize_json_value(value: object, field_name: str) -> object:
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is str:
        return _normalize_string(value)
    if type(value) in (tuple, list):
        return [
            _normalize_json_value(item, field_name)
            for item in value
        ]
    if type(value) is dict:
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(f"{field_name} has a non-string key")
            normalized_key = _normalize_string(key)
            if normalized_key in normalized:
                raise ValueError(
                    f"{field_name} has duplicate normalized keys"
                )
            normalized[normalized_key] = _normalize_json_value(
                item,
                field_name,
            )
        return normalized
    raise ValueError(f"{field_name} has an unsupported JSON value")


def _restore_json_value(value: object) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return tuple(_restore_json_value(item) for item in value)
    if type(value) is dict:
        return {
            key: _restore_json_value(item)
            for key, item in value.items()
        }
    raise ValueError("payload has an unsupported decoded value")


def _canonical_json_bytes(value: object) -> bytes:
    normalized = _normalize_json_value(value, "payload")
    try:
        text = json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("payload cannot be canonically encoded") from exc
    return text.encode("utf-8")


def _reject_duplicate_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _decode_canonical_json(payload_bytes: bytes) -> object:
    try:
        text = payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("payload bytes are not valid UTF-8") from exc

    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_json_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("payload bytes are not valid JSON") from exc
    except ValueError:
        raise

    if _canonical_json_bytes(value) != payload_bytes:
        raise ValueError("payload bytes are not canonical JSON")
    return value


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"unsupported JSON constant: {value}")


def _format_datetime(value: object, field_name: str) -> str:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    utc_value = value.astimezone(timezone.utc)
    return utc_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_datetime(value: object, field_name: str) -> datetime:
    if (
        type(value) is not str
        or _CANONICAL_DATETIME_PATTERN.fullmatch(value) is None
    ):
        raise ValueError(f"{field_name} is not a canonical datetime")
    try:
        parsed = datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )
    except ValueError as exc:
        raise ValueError(
            f"{field_name} is not a valid datetime"
        ) from exc
    return parsed.replace(tzinfo=timezone.utc)


def _require_object(
    value: object,
    expected_keys: tuple[str, ...],
    field_name: str,
) -> dict[str, object]:
    if type(value) is not dict:
        raise ValueError(f"{field_name} must be an exact object")
    observed_keys = tuple(value.keys())
    if observed_keys != expected_keys:
        raise ValueError(f"{field_name} fields mismatch")
    return value


def _require_array(value: object, field_name: str) -> list[object]:
    if type(value) is not list:
        raise ValueError(f"{field_name} must be an exact array")
    return value


def _require_string_array(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    items = _require_array(value, field_name)
    result: list[str] = []
    for item in items:
        if type(item) is not str:
            raise ValueError(
                f"{field_name} must contain exact strings"
            )
        result.append(item)
    return tuple(result)


def _pairs_to_object(
    pairs: tuple[tuple[str, object], ...],
) -> list[object]:
    result: list[object] = []
    for pair in pairs:
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("payload pair must be an exact two-tuple")
        key, value = pair
        if type(key) is not str:
            raise ValueError("payload pair key must be a string")
        result.append(
            [
                _normalize_string(key),
                _normalize_json_value(value, "factual_payload.payload"),
            ]
        )
    return result


def _pairs_from_object(value: object) -> tuple[tuple[str, object], ...]:
    items = _require_array(value, "factual_payload.payload")
    result: list[tuple[str, object]] = []
    for item in items:
        if type(item) is not list or len(item) != 2:
            raise ValueError(
                "factual_payload.payload item must be a two-element array"
            )
        key, nested_value = item
        if type(key) is not str:
            raise ValueError(
                "factual_payload.payload key must be a string"
            )
        result.append((key, _restore_json_value(nested_value)))
    return tuple(result)


def _evidence_diagnostic_to_object(
    diagnostic: EvidenceDiagnostic,
) -> dict[str, object]:
    if type(diagnostic) is not EvidenceDiagnostic:
        raise ValueError(
            "diagnostic must be an exact EvidenceDiagnostic"
        )
    return {
        "code": diagnostic.code,
        "severity": diagnostic.severity,
        "message": diagnostic.message,
        "field": diagnostic.field,
        "source": diagnostic.source,
    }


def _evidence_diagnostic_from_object(
    value: object,
) -> EvidenceDiagnostic:
    item = _require_object(
        value,
        ("code", "severity", "message", "field", "source"),
        "evidence diagnostic",
    )
    return EvidenceDiagnostic(
        code=item["code"],
        severity=item["severity"],
        message=item["message"],
        field=item["field"],
        source=item["source"],
    )


def _acceptance_diagnostic_to_object(
    diagnostic: AcceptanceDiagnostic,
) -> dict[str, object]:
    if type(diagnostic) is not AcceptanceDiagnostic:
        raise ValueError(
            "diagnostic must be an exact AcceptanceDiagnostic"
        )
    return {
        "code": diagnostic.code,
        "severity": diagnostic.severity,
        "message": diagnostic.message,
        "field": diagnostic.field,
        "source": diagnostic.source,
    }


def _acceptance_diagnostic_from_object(
    value: object,
) -> AcceptanceDiagnostic:
    item = _require_object(
        value,
        ("code", "severity", "message", "field", "source"),
        "acceptance diagnostic",
    )
    return AcceptanceDiagnostic(
        code=item["code"],
        severity=item["severity"],
        message=item["message"],
        field=item["field"],
        source=item["source"],
    )


def _accepted_evidence_to_object(
    accepted_evidence: AcceptedEvidence,
) -> dict[str, object]:
    candidate = accepted_evidence.candidate_reference
    source = accepted_evidence.source_snapshot
    producer = accepted_evidence.producer_snapshot
    payload = accepted_evidence.factual_payload
    locator = payload.locator
    provenance = accepted_evidence.provenance
    eligibility = accepted_evidence.eligibility_result
    materialization = accepted_evidence.materialization_record

    return {
        "evidence_id": accepted_evidence.evidence_id,
        "contract_version": accepted_evidence.contract_version,
        "candidate_reference": {
            "candidate_contract_version": (
                candidate.candidate_contract_version
            ),
            "candidate_snapshot_digest": (
                candidate.candidate_snapshot_digest
            ),
            "candidate_source_id": candidate.candidate_source_id,
            "candidate_producer_name": (
                candidate.candidate_producer_name
            ),
            "candidate_producer_version": (
                candidate.candidate_producer_version
            ),
            "candidate_payload_digest": (
                candidate.candidate_payload_digest
            ),
        },
        "source_snapshot": {
            "source_id": source.source_id,
            "source_path": source.source_path,
            "source_type": source.source_type,
            "document_classification": (
                source.document_classification
            ),
            "authority_status": source.authority_status,
            "lifecycle_status": source.lifecycle_status,
            "evidence_eligibility": source.evidence_eligibility,
            "source_content_digest": source.source_content_digest,
        },
        "producer_snapshot": {
            "producer_name": producer.producer_name,
            "producer_version": producer.producer_version,
            "producer_kind": producer.producer_kind,
            "producer_contract_version": (
                producer.producer_contract_version
            ),
        },
        "factual_payload": {
            "payload_type": payload.payload_type,
            "payload_schema_version": (
                payload.payload_schema_version
            ),
            "payload": _pairs_to_object(payload.payload),
            "payload_digest": payload.payload_digest,
            "locator": {
                "locator_type": locator.locator_type,
                "locator_value": _normalize_json_value(
                    locator.locator_value,
                    "factual_payload.locator.locator_value",
                ),
                "locator_schema_version": (
                    locator.locator_schema_version
                ),
            },
        },
        "provenance": {
            "collection_id": provenance.collection_id,
            "producer_output_digest": (
                provenance.producer_output_digest
            ),
            "lineage": list(provenance.lineage),
            "observed_at": _format_datetime(
                provenance.observed_at,
                "provenance.observed_at",
            ),
            "source_registry_version": (
                provenance.source_registry_version
            ),
        },
        "eligibility_result": {
            "decision": eligibility.decision,
            "policy_id": eligibility.policy_id,
            "policy_version": eligibility.policy_version,
            "candidate_snapshot_digest": (
                eligibility.candidate_snapshot_digest
            ),
            "source_id": eligibility.source_id,
            "reason_codes": list(eligibility.reason_codes),
            "evaluated_at": _format_datetime(
                eligibility.evaluated_at,
                "eligibility_result.evaluated_at",
            ),
            "evaluated_by": eligibility.evaluated_by,
            "diagnostics": [
                _evidence_diagnostic_to_object(diagnostic)
                for diagnostic in eligibility.diagnostics
            ],
        },
        "materialization_record": {
            "materializer_id": materialization.materializer_id,
            "materializer_version": (
                materialization.materializer_version
            ),
            "materialized_at": _format_datetime(
                materialization.materialized_at,
                "materialization_record.materialized_at",
            ),
            "acceptance_record_id": (
                materialization.acceptance_record_id
            ),
            "accepted_by": materialization.accepted_by,
            "acceptance_reason": (
                materialization.acceptance_reason
            ),
            "review_record_id": materialization.review_record_id,
            "identity_policy_id": (
                materialization.identity_policy_id
            ),
            "identity_policy_version": (
                materialization.identity_policy_version
            ),
        },
        "diagnostics": [
            _evidence_diagnostic_to_object(diagnostic)
            for diagnostic in accepted_evidence.diagnostics
        ],
    }


def _accepted_evidence_from_object(
    value: object,
) -> AcceptedEvidence:
    root = _require_object(
        value,
        (
            "evidence_id",
            "contract_version",
            "candidate_reference",
            "source_snapshot",
            "producer_snapshot",
            "factual_payload",
            "provenance",
            "eligibility_result",
            "materialization_record",
            "diagnostics",
        ),
        "accepted evidence",
    )
    candidate = _require_object(
        root["candidate_reference"],
        (
            "candidate_contract_version",
            "candidate_snapshot_digest",
            "candidate_source_id",
            "candidate_producer_name",
            "candidate_producer_version",
            "candidate_payload_digest",
        ),
        "candidate_reference",
    )
    source = _require_object(
        root["source_snapshot"],
        (
            "source_id",
            "source_path",
            "source_type",
            "document_classification",
            "authority_status",
            "lifecycle_status",
            "evidence_eligibility",
            "source_content_digest",
        ),
        "source_snapshot",
    )
    producer = _require_object(
        root["producer_snapshot"],
        (
            "producer_name",
            "producer_version",
            "producer_kind",
            "producer_contract_version",
        ),
        "producer_snapshot",
    )
    payload = _require_object(
        root["factual_payload"],
        (
            "payload_type",
            "payload_schema_version",
            "payload",
            "payload_digest",
            "locator",
        ),
        "factual_payload",
    )
    locator = _require_object(
        payload["locator"],
        (
            "locator_type",
            "locator_value",
            "locator_schema_version",
        ),
        "factual_payload.locator",
    )
    provenance = _require_object(
        root["provenance"],
        (
            "collection_id",
            "producer_output_digest",
            "lineage",
            "observed_at",
            "source_registry_version",
        ),
        "provenance",
    )
    eligibility = _require_object(
        root["eligibility_result"],
        (
            "decision",
            "policy_id",
            "policy_version",
            "candidate_snapshot_digest",
            "source_id",
            "reason_codes",
            "evaluated_at",
            "evaluated_by",
            "diagnostics",
        ),
        "eligibility_result",
    )
    materialization = _require_object(
        root["materialization_record"],
        (
            "materializer_id",
            "materializer_version",
            "materialized_at",
            "acceptance_record_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "identity_policy_id",
            "identity_policy_version",
        ),
        "materialization_record",
    )

    eligibility_diagnostics = tuple(
        _evidence_diagnostic_from_object(item)
        for item in _require_array(
            eligibility["diagnostics"],
            "eligibility_result.diagnostics",
        )
    )
    diagnostics = tuple(
        _evidence_diagnostic_from_object(item)
        for item in _require_array(
            root["diagnostics"],
            "diagnostics",
        )
    )

    try:
        return AcceptedEvidence(
            evidence_id=root["evidence_id"],
            contract_version=root["contract_version"],
            candidate_reference=EvidenceCandidateReference(
                candidate_contract_version=(
                    candidate["candidate_contract_version"]
                ),
                candidate_snapshot_digest=(
                    candidate["candidate_snapshot_digest"]
                ),
                candidate_source_id=(
                    candidate["candidate_source_id"]
                ),
                candidate_producer_name=(
                    candidate["candidate_producer_name"]
                ),
                candidate_producer_version=(
                    candidate["candidate_producer_version"]
                ),
                candidate_payload_digest=(
                    candidate["candidate_payload_digest"]
                ),
            ),
            source_snapshot=EvidenceSourceSnapshot(
                source_id=source["source_id"],
                source_path=source["source_path"],
                source_type=source["source_type"],
                document_classification=(
                    source["document_classification"]
                ),
                authority_status=source["authority_status"],
                lifecycle_status=source["lifecycle_status"],
                evidence_eligibility=(
                    source["evidence_eligibility"]
                ),
                source_content_digest=(
                    source["source_content_digest"]
                ),
            ),
            producer_snapshot=EvidenceProducerSnapshot(
                producer_name=producer["producer_name"],
                producer_version=producer["producer_version"],
                producer_kind=producer["producer_kind"],
                producer_contract_version=(
                    producer["producer_contract_version"]
                ),
            ),
            factual_payload=EvidencePayload(
                payload_type=payload["payload_type"],
                payload_schema_version=(
                    payload["payload_schema_version"]
                ),
                payload=_pairs_from_object(payload["payload"]),
                payload_digest=payload["payload_digest"],
                locator=EvidenceLocator(
                    locator_type=locator["locator_type"],
                    locator_value=_restore_json_value(
                        locator["locator_value"]
                    ),
                    locator_schema_version=(
                        locator["locator_schema_version"]
                    ),
                ),
            ),
            provenance=EvidenceProvenance(
                collection_id=provenance["collection_id"],
                producer_output_digest=(
                    provenance["producer_output_digest"]
                ),
                lineage=_require_string_array(
                    provenance["lineage"],
                    "provenance.lineage",
                ),
                observed_at=_parse_datetime(
                    provenance["observed_at"],
                    "provenance.observed_at",
                ),
                source_registry_version=(
                    provenance["source_registry_version"]
                ),
            ),
            eligibility_result=AcceptedEligibilityResult(
                decision=eligibility["decision"],
                policy_id=eligibility["policy_id"],
                policy_version=eligibility["policy_version"],
                candidate_snapshot_digest=(
                    eligibility["candidate_snapshot_digest"]
                ),
                source_id=eligibility["source_id"],
                reason_codes=_require_string_array(
                    eligibility["reason_codes"],
                    "eligibility_result.reason_codes",
                ),
                evaluated_at=_parse_datetime(
                    eligibility["evaluated_at"],
                    "eligibility_result.evaluated_at",
                ),
                evaluated_by=eligibility["evaluated_by"],
                diagnostics=eligibility_diagnostics,
            ),
            materialization_record=EvidenceMaterializationRecord(
                materializer_id=materialization["materializer_id"],
                materializer_version=(
                    materialization["materializer_version"]
                ),
                materialized_at=_parse_datetime(
                    materialization["materialized_at"],
                    "materialization_record.materialized_at",
                ),
                acceptance_record_id=(
                    materialization["acceptance_record_id"]
                ),
                accepted_by=materialization["accepted_by"],
                acceptance_reason=(
                    materialization["acceptance_reason"]
                ),
                review_record_id=(
                    materialization["review_record_id"]
                ),
                identity_policy_id=(
                    materialization["identity_policy_id"]
                ),
                identity_policy_version=(
                    materialization["identity_policy_version"]
                ),
            ),
            diagnostics=diagnostics,
        )
    except TypeError as exc:
        raise ValueError(
            "accepted evidence reconstruction failed"
        ) from exc


def _acceptance_record_to_object(
    acceptance_record: AcceptanceRecord,
) -> dict[str, object]:
    return {
        "acceptance_record_id": (
            acceptance_record.acceptance_record_id
        ),
        "contract_version": acceptance_record.contract_version,
        "evidence_id": acceptance_record.evidence_id,
        "accepted_by": acceptance_record.accepted_by,
        "acceptance_reason": acceptance_record.acceptance_reason,
        "review_record_id": acceptance_record.review_record_id,
        "accepted_at": _format_datetime(
            acceptance_record.accepted_at,
            "acceptance_record.accepted_at",
        ),
        "acceptance_policy_id": (
            acceptance_record.acceptance_policy_id
        ),
        "acceptance_policy_version": (
            acceptance_record.acceptance_policy_version
        ),
        "evidence_identity_policy_id": (
            acceptance_record.evidence_identity_policy_id
        ),
        "evidence_identity_policy_version": (
            acceptance_record.evidence_identity_policy_version
        ),
        "materializer_id": acceptance_record.materializer_id,
        "materializer_version": (
            acceptance_record.materializer_version
        ),
        "diagnostics": [
            _acceptance_diagnostic_to_object(diagnostic)
            for diagnostic in acceptance_record.diagnostics
        ],
    }


def _acceptance_record_from_object(
    value: object,
) -> AcceptanceRecord:
    root = _require_object(
        value,
        (
            "acceptance_record_id",
            "contract_version",
            "evidence_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "accepted_at",
            "acceptance_policy_id",
            "acceptance_policy_version",
            "evidence_identity_policy_id",
            "evidence_identity_policy_version",
            "materializer_id",
            "materializer_version",
            "diagnostics",
        ),
        "acceptance record",
    )
    diagnostics = tuple(
        _acceptance_diagnostic_from_object(item)
        for item in _require_array(
            root["diagnostics"],
            "acceptance_record.diagnostics",
        )
    )

    try:
        return AcceptanceRecord(
            acceptance_record_id=root["acceptance_record_id"],
            contract_version=root["contract_version"],
            evidence_id=root["evidence_id"],
            accepted_by=root["accepted_by"],
            acceptance_reason=root["acceptance_reason"],
            review_record_id=root["review_record_id"],
            accepted_at=_parse_datetime(
                root["accepted_at"],
                "acceptance_record.accepted_at",
            ),
            acceptance_policy_id=(
                root["acceptance_policy_id"]
            ),
            acceptance_policy_version=(
                root["acceptance_policy_version"]
            ),
            evidence_identity_policy_id=(
                root["evidence_identity_policy_id"]
            ),
            evidence_identity_policy_version=(
                root["evidence_identity_policy_version"]
            ),
            materializer_id=root["materializer_id"],
            materializer_version=root["materializer_version"],
            diagnostics=diagnostics,
        )
    except TypeError as exc:
        raise ValueError(
            "acceptance record reconstruction failed"
        ) from exc
