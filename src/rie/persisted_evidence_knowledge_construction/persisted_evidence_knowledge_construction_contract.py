"""Immutable Gate 8 persisted-Evidence Knowledge construction contracts."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Final as _Final

from rie.application.knowledge_constructor import (
    KnowledgeConstructionRequest as _KnowledgeConstructionRequest,
    KnowledgeConstructionResult as _KnowledgeConstructionResult,
)
from rie.evidence_repository.evidence_repository_contract import (
    EvidenceRepositoryLookupResult as _EvidenceRepositoryLookupResult,
)


PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION: _Final = (
    "persisted_evidence_knowledge_construction_request_contract_v1"
)
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION: _Final = (
    "persisted_evidence_knowledge_compatibility_record_contract_v1"
)
PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION: _Final = (
    "persisted_evidence_knowledge_construction_result_contract_v1"
)
PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CONTRACT_VERSION: _Final = (
    "persisted_evidence_knowledge_construction_issue_contract_v1"
)
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_IDENTITY_CANONICALIZATION_VERSION: _Final = (
    "persisted_evidence_knowledge_compatibility_identity_json_v1"
)
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX: _Final = "pekc1_"
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID: _Final = (
    "rcis-persisted-evidence-knowledge-compatibility"
)
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION: _Final = "1.0.0"
PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_DIGEST_ALGORITHM: _Final = "sha256"
PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED: _Final = "constructed"
PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED: _Final = "rejected"
PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES: _Final = (
    "invalid_request",
    "unsupported_contract_version",
    "unsupported_compatibility_policy",
    "invalid_repository_lookup_result",
    "repository_lookup_not_found",
    "repository_lookup_rejected",
    "repository_linkage_mismatch",
    "repository_identity_mismatch",
    "collection_payload_digest_mismatch",
    "target_evidence_not_found",
    "target_evidence_identity_mismatch",
    "ineligible_evidence",
    "accepted_evidence_identity_mismatch",
    "acceptance_record_identity_mismatch",
    "evidence_compatibility_mismatch",
    "knowledge_construction_rejected",
    "internal_contract_violation",
)


_ISSUE_MESSAGES = _MappingProxyType(
    {
        "invalid_request": (
            "The persisted Evidence Knowledge construction request is invalid."
        ),
        "unsupported_contract_version": (
            "The persisted Evidence Knowledge construction contract version "
            "is unsupported."
        ),
        "unsupported_compatibility_policy": (
            "The persisted Evidence Knowledge compatibility policy is unsupported."
        ),
        "invalid_repository_lookup_result": (
            "The resolved Evidence repository lookup result is invalid."
        ),
        "repository_lookup_not_found": (
            "The resolved Evidence repository lookup did not find a revision."
        ),
        "repository_lookup_rejected": (
            "The resolved Evidence repository lookup was rejected."
        ),
        "repository_linkage_mismatch": (
            "The persisted Evidence repository linkage is inconsistent."
        ),
        "repository_identity_mismatch": (
            "A persisted Evidence repository identity does not match its content."
        ),
        "collection_payload_digest_mismatch": (
            "The persisted Evidence collection payload digest does not match."
        ),
        "target_evidence_not_found": (
            "The target TraceableEvidence was not found exactly once."
        ),
        "target_evidence_identity_mismatch": (
            "The target TraceableEvidence identity does not match its content."
        ),
        "ineligible_evidence": (
            "The target TraceableEvidence is not eligible for Knowledge construction."
        ),
        "accepted_evidence_identity_mismatch": (
            "The AcceptedEvidence identity does not match its content."
        ),
        "acceptance_record_identity_mismatch": (
            "An AcceptanceRecord identity or lineage does not match."
        ),
        "evidence_compatibility_mismatch": (
            "The persisted and accepted Evidence values are not compatible."
        ),
        "knowledge_construction_rejected": (
            "The existing Knowledge construction contract rejected the request."
        ),
        "internal_contract_violation": (
            "The persisted Evidence Knowledge construction result violated its contract."
        ),
    }
)

_LOWER_HEX = frozenset("0123456789abcdef")


def _require_string(value: object, field_name: str) -> str:
    if type(value) is not str or value.strip() == "":
        raise ValueError(f"{field_name} must be an exact non-empty string")
    return value


def _require_positive_int(value: object, field_name: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _require_digest(value: object, field_name: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(character not in _LOWER_HEX for character in value)
    ):
        raise ValueError(f"{field_name} must be a lowercase SHA-256 digest")
    return value


def _require_prefixed_digest(
    value: object,
    field_name: str,
    prefix: str,
) -> str:
    if type(value) is not str or not value.startswith(prefix):
        raise ValueError(f"{field_name} has an invalid identifier prefix")
    _require_digest(value[len(prefix):], field_name)
    return value


def _require_acceptance_record_ids(
    value: object,
    *,
    require_sorted: bool,
) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError(
            "acceptance_record_ids must be a non-empty exact tuple"
        )
    for item in value:
        _require_prefixed_digest(
            item,
            "acceptance_record_ids",
            "ar1_",
        )
    if len(set(value)) != len(value):
        raise ValueError("acceptance_record_ids must be unique")
    if require_sorted and value != tuple(sorted(value)):
        raise ValueError(
            "acceptance_record_ids must be in ascending lexical order"
        )
    return value


def _validate_compatibility_identity_values(
    *,
    contract_version: object,
    repository_revision_id: object,
    source_id: object,
    revision_number: object,
    previous_revision_id: object,
    collection_id: object,
    collection_payload_digest: object,
    repository_audit_id: object,
    traceable_evidence_id: object,
    accepted_evidence_id: object,
    acceptance_record_ids: object,
    construction_rule_id: object,
    construction_rule_version: object,
    compatibility_policy_id: object,
    compatibility_policy_version: object,
    require_sorted_acceptance_record_ids: bool,
    require_supported_values: bool,
) -> tuple[str, ...]:
    _require_string(contract_version, "contract_version")
    if (
        require_supported_values
        and contract_version
        != PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION
    ):
        raise ValueError("unsupported compatibility record contract version")
    _require_prefixed_digest(
        repository_revision_id,
        "repository_revision_id",
        "evr1_",
    )
    _require_string(source_id, "source_id")
    _require_positive_int(revision_number, "revision_number")
    if previous_revision_id is not None:
        _require_prefixed_digest(
            previous_revision_id,
            "previous_revision_id",
            "evr1_",
        )
    if revision_number == 1 and previous_revision_id is not None:
        raise ValueError("first revision cannot have a previous revision")
    if revision_number > 1 and previous_revision_id is None:
        raise ValueError("later revision requires a previous revision")
    _require_prefixed_digest(collection_id, "collection_id", "evc1_")
    _require_digest(
        collection_payload_digest,
        "collection_payload_digest",
    )
    _require_prefixed_digest(
        repository_audit_id,
        "repository_audit_id",
        "eva1_",
    )
    _require_prefixed_digest(
        traceable_evidence_id,
        "traceable_evidence_id",
        "evm1_",
    )
    _require_prefixed_digest(
        accepted_evidence_id,
        "accepted_evidence_id",
        "ev1_",
    )
    ids = _require_acceptance_record_ids(
        acceptance_record_ids,
        require_sorted=require_sorted_acceptance_record_ids,
    )
    _require_string(construction_rule_id, "construction_rule_id")
    _require_string(
        construction_rule_version,
        "construction_rule_version",
    )
    _require_string(compatibility_policy_id, "compatibility_policy_id")
    _require_string(
        compatibility_policy_version,
        "compatibility_policy_version",
    )
    if require_supported_values and (
        compatibility_policy_id
        != PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
        or compatibility_policy_version
        != PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
    ):
        raise ValueError("unsupported compatibility policy")
    return ids


@_dataclass(frozen=True)
class PersistedEvidenceKnowledgeConstructionIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.code not in PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES:
            raise ValueError("issue code is invalid")
        if self.message != _ISSUE_MESSAGES[self.code]:
            raise ValueError("issue message is invalid")


@_dataclass(frozen=True)
class PersistedEvidenceKnowledgeConstructionRequest:
    contract_version: str
    repository_lookup_result: _EvidenceRepositoryLookupResult
    target_evidence_id: str
    knowledge_construction_request: _KnowledgeConstructionRequest
    compatibility_policy_id: str
    compatibility_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported request contract version")
        if type(self.repository_lookup_result) is not _EvidenceRepositoryLookupResult:
            raise TypeError(
                "repository_lookup_result must be an exact "
                "EvidenceRepositoryLookupResult"
            )
        try:
            self.repository_lookup_result.__post_init__()
        except Exception as error:
            raise ValueError("repository_lookup_result is invalid") from error
        _require_prefixed_digest(
            self.target_evidence_id,
            "target_evidence_id",
            "evm1_",
        )
        if (
            type(self.knowledge_construction_request)
            is not _KnowledgeConstructionRequest
        ):
            raise TypeError(
                "knowledge_construction_request must be an exact "
                "KnowledgeConstructionRequest"
            )
        try:
            self.knowledge_construction_request.__post_init__()
        except Exception as error:
            raise ValueError(
                "knowledge_construction_request is invalid"
            ) from error
        if (
            self.compatibility_policy_id
            != PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
            or self.compatibility_policy_version
            != PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
        ):
            raise ValueError("unsupported compatibility policy")


@_dataclass(frozen=True)
class PersistedEvidenceKnowledgeCompatibilityRecord:
    contract_version: str
    compatibility_record_id: str
    repository_revision_id: str
    source_id: str
    revision_number: int
    previous_revision_id: str | None
    collection_id: str
    collection_payload_digest: str
    repository_audit_id: str
    traceable_evidence_id: str
    accepted_evidence_id: str
    acceptance_record_ids: tuple[str, ...]
    construction_rule_id: str
    construction_rule_version: str
    compatibility_policy_id: str
    compatibility_policy_version: str

    def __post_init__(self) -> None:
        _require_prefixed_digest(
            self.compatibility_record_id,
            "compatibility_record_id",
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX,
        )
        _validate_compatibility_identity_values(
            contract_version=self.contract_version,
            repository_revision_id=self.repository_revision_id,
            source_id=self.source_id,
            revision_number=self.revision_number,
            previous_revision_id=self.previous_revision_id,
            collection_id=self.collection_id,
            collection_payload_digest=self.collection_payload_digest,
            repository_audit_id=self.repository_audit_id,
            traceable_evidence_id=self.traceable_evidence_id,
            accepted_evidence_id=self.accepted_evidence_id,
            acceptance_record_ids=self.acceptance_record_ids,
            construction_rule_id=self.construction_rule_id,
            construction_rule_version=self.construction_rule_version,
            compatibility_policy_id=self.compatibility_policy_id,
            compatibility_policy_version=self.compatibility_policy_version,
            require_sorted_acceptance_record_ids=True,
            require_supported_values=True,
        )
        from .persisted_evidence_knowledge_construction_canonicalization import (
            derive_persisted_evidence_knowledge_compatibility_record_id,
        )

        expected_id = (
            derive_persisted_evidence_knowledge_compatibility_record_id(
                contract_version=self.contract_version,
                repository_revision_id=self.repository_revision_id,
                source_id=self.source_id,
                revision_number=self.revision_number,
                previous_revision_id=self.previous_revision_id,
                collection_id=self.collection_id,
                collection_payload_digest=self.collection_payload_digest,
                repository_audit_id=self.repository_audit_id,
                traceable_evidence_id=self.traceable_evidence_id,
                accepted_evidence_id=self.accepted_evidence_id,
                acceptance_record_ids=self.acceptance_record_ids,
                construction_rule_id=self.construction_rule_id,
                construction_rule_version=self.construction_rule_version,
                compatibility_policy_id=self.compatibility_policy_id,
                compatibility_policy_version=self.compatibility_policy_version,
            )
        )
        if self.compatibility_record_id != expected_id:
            raise ValueError(
                "compatibility_record_id does not match identity content"
            )


@_dataclass(frozen=True)
class PersistedEvidenceKnowledgeConstructionResult:
    contract_version: str
    status: str
    mutation_performed: bool
    compatibility_record: PersistedEvidenceKnowledgeCompatibilityRecord | None
    knowledge_construction_result: _KnowledgeConstructionResult | None
    issue: PersistedEvidenceKnowledgeConstructionIssue | None

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported result contract version")
        if self.status not in (
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED,
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED,
        ):
            raise ValueError("unsupported construction status")
        if self.mutation_performed is not False:
            raise ValueError("mutation_performed must always be False")

        if (
            self.status
            == PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED
        ):
            if type(self.compatibility_record) is not (
                PersistedEvidenceKnowledgeCompatibilityRecord
            ):
                raise TypeError(
                    "constructed result requires compatibility_record"
                )
            if (
                type(self.knowledge_construction_result)
                is not _KnowledgeConstructionResult
                or self.knowledge_construction_result.decision != "constructed"
            ):
                raise TypeError(
                    "constructed result requires constructed "
                    "knowledge_construction_result"
                )
            if self.issue is not None:
                raise ValueError("constructed result cannot contain issue")
            return

        if type(self.issue) is not PersistedEvidenceKnowledgeConstructionIssue:
            raise TypeError("rejected result requires issue")
        if self.issue.code == "knowledge_construction_rejected":
            if type(self.compatibility_record) is not (
                PersistedEvidenceKnowledgeCompatibilityRecord
            ):
                raise TypeError(
                    "knowledge construction rejection requires "
                    "compatibility_record"
                )
            if (
                type(self.knowledge_construction_result)
                is not _KnowledgeConstructionResult
                or self.knowledge_construction_result.decision != "rejected"
            ):
                raise TypeError(
                    "knowledge construction rejection requires rejected "
                    "knowledge_construction_result"
                )
        elif (
            self.compatibility_record is not None
            or self.knowledge_construction_result is not None
        ):
            raise ValueError(
                "pre-construction rejection cannot contain compatibility "
                "or nested construction result"
            )


def _issue(code: str) -> PersistedEvidenceKnowledgeConstructionIssue:
    return PersistedEvidenceKnowledgeConstructionIssue(
        code=code,
        message=_ISSUE_MESSAGES[code],
    )
