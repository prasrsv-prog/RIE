from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from types import MappingProxyType
from typing import Final

from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION as _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION as _EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    EvidenceCollection,
)

EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION: Final = (
    "evidence_repository_write_request_contract_v1"
)
EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION: Final = (
    "evidence_repository_write_request_contract_v2"
)
EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION: Final = (
    "evidence_repository_write_result_contract_v1"
)
EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION: Final = (
    "evidence_repository_revision_contract_v1"
)
EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION: Final = (
    "evidence_repository_audit_record_contract_v1"
)
EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION: Final = (
    "evidence_repository_lookup_result_contract_v1"
)
EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION: Final = (
    "evidence_repository_history_result_contract_v1"
)
EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION: Final = (
    "evidence_repository_issue_contract_v1"
)

EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION: Final = (
    "evidence_collection_repository_payload_json_v1"
)
EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "evidence_repository_revision_identity_json_v1"
)
EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "evidence_repository_audit_identity_json_v1"
)
EVIDENCE_REPOSITORY_REVISION_ID_PREFIX: Final = "evr1_"
EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX: Final = "eva1_"

SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID: Final = (
    "rcis-gate7-evidence-repository-sqlite"
)
SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION: Final = 1

EVIDENCE_REPOSITORY_WRITE_STATUSES: Final = (
    "persisted",
    "unchanged_exact_replay",
    "rejected",
)
EVIDENCE_REPOSITORY_LOOKUP_STATUSES: Final = (
    "found",
    "not_found",
    "rejected",
)
EVIDENCE_REPOSITORY_ISSUE_CODES: Final = (
    "invalid_request",
    "unsupported_contract_version",
    "invalid_collection",
    "collection_id_mismatch",
    "collection_payload_digest_mismatch",
    "collection_identity_collision",
    "revision_id_mismatch",
    "audit_id_mismatch",
    "unsupported_schema",
    "repository_busy",
    "repository_corrupt",
    "repository_unavailable",
)
EVIDENCE_REPOSITORY_ISSUE_MESSAGES: Final = MappingProxyType(
    {
        "invalid_request": "The repository request is invalid.",
        "unsupported_contract_version": "The repository contract version is unsupported.",
        "invalid_collection": "The EvidenceCollection is invalid.",
        "collection_id_mismatch": "The EvidenceCollection identity does not match its content.",
        "collection_payload_digest_mismatch": "The collection payload digest does not match.",
        "collection_identity_collision": "The collection identity is already bound to different content.",
        "revision_id_mismatch": "The revision identity does not match its content.",
        "audit_id_mismatch": "The audit identity does not match its content.",
        "unsupported_schema": "The repository schema is unsupported.",
        "repository_busy": "The repository is busy.",
        "repository_corrupt": "The repository content is corrupt.",
        "repository_unavailable": "The repository is unavailable.",
    }
)

_HEX_DIGITS = frozenset("0123456789abcdef")
_PERSISTED_AUDIT_ACTION = "persisted_revision"


def _require_string(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be str")
    if not allow_empty and value == "":
        raise ValueError(f"{field_name} must be non-empty")
    return value


def _require_digest(value: object, field_name: str) -> str:
    text = _require_string(value, field_name)
    if len(text) != 64 or any(char not in _HEX_DIGITS for char in text):
        raise ValueError(f"{field_name} must be lowercase sha256")
    return text


def _require_prefixed_digest(value: object, field_name: str, prefix: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith(prefix):
        raise ValueError(f"{field_name} has an invalid prefix")
    _require_digest(text[len(prefix) :], field_name)
    return text


def _require_positive_int(value: object, field_name: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field_name} must be a positive int")
    return value


def _require_utc_datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


def _require_exact_tuple(value: object, field_name: str, item_type: type) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{field_name} must be tuple")
    if any(type(item) is not item_type for item in value):
        raise TypeError(f"{field_name} contains an invalid item")
    return value


def _issue(code: str) -> "EvidenceRepositoryIssue":
    return EvidenceRepositoryIssue(code=code, message=EVIDENCE_REPOSITORY_ISSUE_MESSAGES[code])


@dataclass(frozen=True)
class EvidenceRepositoryIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.code not in EVIDENCE_REPOSITORY_ISSUE_CODES:
            raise ValueError("issue code is invalid")
        if self.message != EVIDENCE_REPOSITORY_ISSUE_MESSAGES[self.code]:
            raise ValueError("issue message is invalid")


@dataclass(frozen=True)
class EvidenceRepositoryWriteRequest:
    contract_version: str
    collection: EvidenceCollection
    expected_collection_payload_digest: str
    actor_id: str
    recorded_at_utc: datetime

    def __post_init__(self) -> None:
        if self.contract_version == EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION:
            accepted_collection_versions = (
                EVIDENCE_COLLECTION_CONTRACT_VERSION,
                _EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION,
            )
        elif (
            self.contract_version
            == EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION
        ):
            accepted_collection_versions = (
                _EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
            )
        else:
            raise ValueError("unsupported write request contract version")

        if type(self.collection) is not EvidenceCollection:
            raise TypeError("collection must be EvidenceCollection")
        if self.collection.contract_version not in accepted_collection_versions:
            raise ValueError("unsupported EvidenceCollection contract version")
        if derive_evidence_collection_id(self.collection) != self.collection.collection_id:
            raise ValueError("EvidenceCollection identity mismatch")
        _require_digest(
            self.expected_collection_payload_digest,
            "expected_collection_payload_digest",
        )
        _require_string(self.actor_id, "actor_id")
        _require_utc_datetime(self.recorded_at_utc, "recorded_at_utc")


@dataclass(frozen=True)
class EvidenceRepositoryRevision:
    contract_version: str
    revision_id: str
    source_id: str
    revision_number: int
    collection_id: str
    collection_payload_digest: str
    previous_revision_id: str | None
    actor_id: str
    recorded_at_utc: datetime
    audit_id: str

    def __post_init__(self) -> None:
        if self.contract_version != EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION:
            raise ValueError("unsupported revision contract version")
        _require_prefixed_digest(
            self.revision_id,
            "revision_id",
            EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
        )
        _require_string(self.source_id, "source_id")
        _require_positive_int(self.revision_number, "revision_number")
        _require_string(self.collection_id, "collection_id")
        _require_digest(self.collection_payload_digest, "collection_payload_digest")
        if self.previous_revision_id is not None:
            _require_prefixed_digest(
                self.previous_revision_id,
                "previous_revision_id",
                EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
            )
        if self.revision_number == 1 and self.previous_revision_id is not None:
            raise ValueError("first revision cannot have a previous revision")
        if self.revision_number > 1 and self.previous_revision_id is None:
            raise ValueError("later revision requires a previous revision")
        _require_string(self.actor_id, "actor_id")
        _require_utc_datetime(self.recorded_at_utc, "recorded_at_utc")
        _require_prefixed_digest(
            self.audit_id,
            "audit_id",
            EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX,
        )


@dataclass(frozen=True)
class EvidenceRepositoryAuditRecord:
    contract_version: str
    audit_id: str
    action: str
    revision_id: str
    source_id: str
    revision_number: int
    collection_id: str
    actor_id: str
    recorded_at_utc: datetime

    def __post_init__(self) -> None:
        if self.contract_version != EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION:
            raise ValueError("unsupported audit contract version")
        _require_prefixed_digest(
            self.audit_id,
            "audit_id",
            EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX,
        )
        if self.action != _PERSISTED_AUDIT_ACTION:
            raise ValueError("audit action is invalid")
        _require_prefixed_digest(
            self.revision_id,
            "revision_id",
            EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
        )
        _require_string(self.source_id, "source_id")
        _require_positive_int(self.revision_number, "revision_number")
        _require_string(self.collection_id, "collection_id")
        _require_string(self.actor_id, "actor_id")
        _require_utc_datetime(self.recorded_at_utc, "recorded_at_utc")


@dataclass(frozen=True)
class EvidenceRepositoryWriteResult:
    contract_version: str
    status: str
    mutation_performed: bool
    revision: EvidenceRepositoryRevision | None
    audit_record: EvidenceRepositoryAuditRecord | None
    collection: EvidenceCollection | None
    issue: EvidenceRepositoryIssue | None

    def __post_init__(self) -> None:
        if self.contract_version != EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION:
            raise ValueError("unsupported write result contract version")
        if self.status not in EVIDENCE_REPOSITORY_WRITE_STATUSES:
            raise ValueError("write status is invalid")
        if type(self.mutation_performed) is not bool:
            raise TypeError("mutation_performed must be bool")
        if self.status == "persisted":
            if not self.mutation_performed:
                raise ValueError("persisted result must mutate")
            self._require_success_shape()
        elif self.status == "unchanged_exact_replay":
            if self.mutation_performed:
                raise ValueError("exact replay must not mutate")
            self._require_success_shape()
        else:
            if self.mutation_performed:
                raise ValueError("rejected result must not mutate")
            if any(value is not None for value in (self.revision, self.audit_record, self.collection)):
                raise ValueError("rejected result cannot contain persisted values")
            if type(self.issue) is not EvidenceRepositoryIssue:
                raise TypeError("rejected result requires an issue")

    def _require_success_shape(self) -> None:
        if type(self.revision) is not EvidenceRepositoryRevision:
            raise TypeError("successful write requires revision")
        if type(self.audit_record) is not EvidenceRepositoryAuditRecord:
            raise TypeError("successful write requires audit record")
        if type(self.collection) is not EvidenceCollection:
            raise TypeError("successful write requires collection")
        if self.issue is not None:
            raise ValueError("successful write cannot contain issue")
        if self.revision.audit_id != self.audit_record.audit_id:
            raise ValueError("revision and audit identity mismatch")
        if self.revision.revision_id != self.audit_record.revision_id:
            raise ValueError("revision and audit revision mismatch")
        if self.revision.collection_id != self.collection.collection_id:
            raise ValueError("revision and collection mismatch")


@dataclass(frozen=True)
class EvidenceRepositoryLookupResult:
    contract_version: str
    status: str
    revision: EvidenceRepositoryRevision | None
    audit_record: EvidenceRepositoryAuditRecord | None
    collection: EvidenceCollection | None
    issue: EvidenceRepositoryIssue | None

    def __post_init__(self) -> None:
        if self.contract_version != EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION:
            raise ValueError("unsupported lookup result contract version")
        if self.status not in EVIDENCE_REPOSITORY_LOOKUP_STATUSES:
            raise ValueError("lookup status is invalid")
        if self.status == "found":
            if type(self.revision) is not EvidenceRepositoryRevision:
                raise TypeError("found lookup requires revision")
            if type(self.audit_record) is not EvidenceRepositoryAuditRecord:
                raise TypeError("found lookup requires audit record")
            if type(self.collection) is not EvidenceCollection:
                raise TypeError("found lookup requires collection")
            if self.issue is not None:
                raise ValueError("found lookup cannot contain issue")
        elif self.status == "not_found":
            if any(value is not None for value in (self.revision, self.audit_record, self.collection, self.issue)):
                raise ValueError("not_found lookup must be empty")
        else:
            if any(value is not None for value in (self.revision, self.audit_record, self.collection)):
                raise ValueError("rejected lookup cannot contain persisted values")
            if type(self.issue) is not EvidenceRepositoryIssue:
                raise TypeError("rejected lookup requires issue")


@dataclass(frozen=True)
class EvidenceRepositoryHistoryResult:
    contract_version: str
    status: str
    source_id: str
    revisions: tuple[EvidenceRepositoryRevision, ...]
    audit_records: tuple[EvidenceRepositoryAuditRecord, ...]
    issue: EvidenceRepositoryIssue | None

    def __post_init__(self) -> None:
        if self.contract_version != EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION:
            raise ValueError("unsupported history result contract version")
        if self.status not in EVIDENCE_REPOSITORY_LOOKUP_STATUSES:
            raise ValueError("history status is invalid")
        _require_string(self.source_id, "source_id")
        _require_exact_tuple(self.revisions, "revisions", EvidenceRepositoryRevision)
        _require_exact_tuple(self.audit_records, "audit_records", EvidenceRepositoryAuditRecord)
        if self.status == "found":
            if not self.revisions or len(self.revisions) != len(self.audit_records):
                raise ValueError("found history requires aligned revisions and audits")
            if self.issue is not None:
                raise ValueError("found history cannot contain issue")
            numbers = tuple(item.revision_number for item in self.revisions)
            if numbers != tuple(range(1, len(numbers) + 1)):
                raise ValueError("history revisions must be consecutive")
        elif self.status == "not_found":
            if self.revisions or self.audit_records or self.issue is not None:
                raise ValueError("not_found history must be empty")
        else:
            if self.revisions or self.audit_records:
                raise ValueError("rejected history must be empty")
            if type(self.issue) is not EvidenceRepositoryIssue:
                raise TypeError("rejected history requires issue")


__all__ = (
    "EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION",
    "EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_ID_PREFIX",
    "EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX",
    "SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID",
    "SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION",
    "EVIDENCE_REPOSITORY_WRITE_STATUSES",
    "EVIDENCE_REPOSITORY_LOOKUP_STATUSES",
    "EVIDENCE_REPOSITORY_ISSUE_CODES",
    "EVIDENCE_REPOSITORY_ISSUE_MESSAGES",
    "EvidenceRepositoryIssue",
    "EvidenceRepositoryWriteRequest",
    "EvidenceRepositoryRevision",
    "EvidenceRepositoryAuditRecord",
    "EvidenceRepositoryWriteResult",
    "EvidenceRepositoryLookupResult",
    "EvidenceRepositoryHistoryResult",
)
