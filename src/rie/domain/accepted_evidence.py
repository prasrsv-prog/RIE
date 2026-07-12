"""Immutable accepted-Evidence domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import TypeAlias


ImmutableScalar: TypeAlias = str | int | float | bool | None
ImmutableValue: TypeAlias = (
    ImmutableScalar
    | tuple["ImmutableValue", ...]
    | tuple[tuple[str, "ImmutableValue"], ...]
)
LocatorValue: TypeAlias = str | int | float | bool | tuple["LocatorValue", ...]


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_tuple(value: object, field_name: str) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    return value


def _validate_string_tuple(
    value: object,
    field_name: str,
    *,
    allow_empty: bool,
) -> None:
    items = _require_tuple(value, field_name)
    if not allow_empty and not items:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(items):
        _require_string(item, f"{field_name}[{index}]")


def _validate_immutable_value(value: object, field_name: str) -> None:
    if value is None or type(value) in (str, int, bool):
        return
    if type(value) is float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must contain only finite floats")
        return
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an immutable scalar or tuple")

    mapping_like = bool(value) and all(
        type(item) is tuple
        and len(item) == 2
        and type(item[0]) is str
        for item in value
    )

    if mapping_like:
        keys = tuple(item[0] for item in value)
        for index, key in enumerate(keys):
            _require_string(key, f"{field_name}[{index}].key")
        if len(set(keys)) != len(keys):
            raise ValueError(f"{field_name} mapping keys must be unique")
        if keys != tuple(sorted(keys)):
            raise ValueError(
                f"{field_name} mapping keys must be lexicographically ordered"
            )
        for index, item in enumerate(value):
            _validate_immutable_value(
                item[1],
                f"{field_name}[{index}].value",
            )
        return

    for index, item in enumerate(value):
        _validate_immutable_value(item, f"{field_name}[{index}]")


def _validate_locator_value(value: object, field_name: str) -> None:
    if type(value) is str:
        _require_string(value, field_name)
        return
    if type(value) in (int, bool):
        return
    if type(value) is float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must contain only finite floats")
        return
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an immutable scalar or tuple")
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _validate_locator_value(item, f"{field_name}[{index}]")


def _require_contract(
    value: object,
    expected_type: type[object],
    field_name: str,
) -> None:
    if type(value) is not expected_type:
        raise ValueError(
            f"{field_name} must be an exact {expected_type.__name__}"
        )


@dataclass(frozen=True)
class EvidenceDiagnostic:
    code: str
    severity: str
    message: str
    field: str
    source: str

    def __post_init__(self) -> None:
        _require_string(self.code, "code")
        _require_string(self.severity, "severity")
        _require_string(self.message, "message")
        _require_string(self.field, "field")
        _require_string(self.source, "source")
        if self.severity not in ("info", "warning"):
            raise ValueError("severity must be info or warning")


def _validate_diagnostics(
    value: object,
    field_name: str,
) -> None:
    items = _require_tuple(value, field_name)
    for index, item in enumerate(items):
        _require_contract(
            item,
            EvidenceDiagnostic,
            f"{field_name}[{index}]",
        )


@dataclass(frozen=True)
class EvidenceCandidateReference:
    candidate_contract_version: str
    candidate_snapshot_digest: str
    candidate_source_id: str
    candidate_producer_name: str
    candidate_producer_version: str
    candidate_payload_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "candidate_contract_version",
            "candidate_snapshot_digest",
            "candidate_source_id",
            "candidate_producer_name",
            "candidate_producer_version",
            "candidate_payload_digest",
        ):
            _require_string(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class EvidenceSourceSnapshot:
    source_id: str
    source_path: str
    source_type: str
    document_classification: str
    authority_status: str
    lifecycle_status: str
    evidence_eligibility: str
    source_content_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "source_id",
            "source_path",
            "source_type",
            "document_classification",
            "authority_status",
            "lifecycle_status",
            "evidence_eligibility",
            "source_content_digest",
        ):
            _require_string(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class EvidenceProducerSnapshot:
    producer_name: str
    producer_version: str
    producer_kind: str
    producer_contract_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "producer_name",
            "producer_version",
            "producer_kind",
            "producer_contract_version",
        ):
            _require_string(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class EvidenceLocator:
    locator_type: str
    locator_value: LocatorValue
    locator_schema_version: str

    def __post_init__(self) -> None:
        _require_string(self.locator_type, "locator_type")
        _validate_locator_value(self.locator_value, "locator_value")
        _require_string(
            self.locator_schema_version,
            "locator_schema_version",
        )


@dataclass(frozen=True)
class EvidencePayload:
    payload_type: str
    payload_schema_version: str
    payload: ImmutableValue
    payload_digest: str
    locator: EvidenceLocator

    def __post_init__(self) -> None:
        _require_string(self.payload_type, "payload_type")
        _require_string(
            self.payload_schema_version,
            "payload_schema_version",
        )
        _validate_immutable_value(self.payload, "payload")
        _require_string(self.payload_digest, "payload_digest")
        _require_contract(self.locator, EvidenceLocator, "locator")


@dataclass(frozen=True)
class EvidenceProvenance:
    collection_id: str
    producer_output_digest: str
    lineage: tuple[str, ...]
    observed_at: datetime
    source_registry_version: str

    def __post_init__(self) -> None:
        _require_string(self.collection_id, "collection_id")
        _require_string(
            self.producer_output_digest,
            "producer_output_digest",
        )
        _validate_string_tuple(
            self.lineage,
            "lineage",
            allow_empty=False,
        )
        _require_datetime(self.observed_at, "observed_at")
        _require_string(
            self.source_registry_version,
            "source_registry_version",
        )


@dataclass(frozen=True)
class AcceptedEligibilityResult:
    decision: str
    policy_id: str
    policy_version: str
    candidate_snapshot_digest: str
    source_id: str
    reason_codes: tuple[str, ...]
    evaluated_at: datetime
    evaluated_by: str
    diagnostics: tuple[EvidenceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_string(self.decision, "decision")
        if self.decision != "eligible":
            raise ValueError("decision must be eligible")
        _require_string(self.policy_id, "policy_id")
        _require_string(self.policy_version, "policy_version")
        _require_string(
            self.candidate_snapshot_digest,
            "candidate_snapshot_digest",
        )
        _require_string(self.source_id, "source_id")
        _validate_string_tuple(
            self.reason_codes,
            "reason_codes",
            allow_empty=False,
        )
        _require_datetime(self.evaluated_at, "evaluated_at")
        _require_string(self.evaluated_by, "evaluated_by")
        _validate_diagnostics(self.diagnostics, "diagnostics")


@dataclass(frozen=True)
class EvidenceMaterializationRecord:
    materializer_id: str
    materializer_version: str
    materialized_at: datetime
    acceptance_record_id: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str
    identity_policy_id: str
    identity_policy_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "materializer_id",
            "materializer_version",
            "acceptance_record_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "identity_policy_id",
            "identity_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_datetime(self.materialized_at, "materialized_at")


@dataclass(frozen=True)
class AcceptedEvidence:
    evidence_id: str
    contract_version: str
    candidate_reference: EvidenceCandidateReference
    source_snapshot: EvidenceSourceSnapshot
    producer_snapshot: EvidenceProducerSnapshot
    factual_payload: EvidencePayload
    provenance: EvidenceProvenance
    eligibility_result: AcceptedEligibilityResult
    materialization_record: EvidenceMaterializationRecord
    diagnostics: tuple[EvidenceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_string(self.evidence_id, "evidence_id")
        _require_string(self.contract_version, "contract_version")
        _require_contract(
            self.candidate_reference,
            EvidenceCandidateReference,
            "candidate_reference",
        )
        _require_contract(
            self.source_snapshot,
            EvidenceSourceSnapshot,
            "source_snapshot",
        )
        _require_contract(
            self.producer_snapshot,
            EvidenceProducerSnapshot,
            "producer_snapshot",
        )
        _require_contract(
            self.factual_payload,
            EvidencePayload,
            "factual_payload",
        )
        _require_contract(
            self.provenance,
            EvidenceProvenance,
            "provenance",
        )
        _require_contract(
            self.eligibility_result,
            AcceptedEligibilityResult,
            "eligibility_result",
        )
        _require_contract(
            self.materialization_record,
            EvidenceMaterializationRecord,
            "materialization_record",
        )
        _validate_diagnostics(self.diagnostics, "diagnostics")

        if (
            self.candidate_reference.candidate_source_id
            != self.source_snapshot.source_id
        ):
            raise ValueError(
                "candidate_source_id must match source_snapshot.source_id"
            )
        if (
            self.candidate_reference.candidate_producer_name
            != self.producer_snapshot.producer_name
        ):
            raise ValueError(
                "candidate_producer_name must match "
                "producer_snapshot.producer_name"
            )
        if (
            self.candidate_reference.candidate_producer_version
            != self.producer_snapshot.producer_version
        ):
            raise ValueError(
                "candidate_producer_version must match "
                "producer_snapshot.producer_version"
            )
        if (
            self.candidate_reference.candidate_payload_digest
            != self.factual_payload.payload_digest
        ):
            raise ValueError(
                "candidate_payload_digest must match "
                "factual_payload.payload_digest"
            )
        if (
            self.eligibility_result.candidate_snapshot_digest
            != self.candidate_reference.candidate_snapshot_digest
        ):
            raise ValueError(
                "eligibility candidate_snapshot_digest must match "
                "candidate_reference.candidate_snapshot_digest"
            )
        if (
            self.eligibility_result.source_id
            != self.source_snapshot.source_id
        ):
            raise ValueError(
                "eligibility source_id must match source_snapshot.source_id"
            )
