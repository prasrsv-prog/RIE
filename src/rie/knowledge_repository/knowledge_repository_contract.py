from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Final

from rie.application.governed_knowledge_constructor import (
    GovernedKnowledgeConstructionResult,
)
from rie.domain.governed_knowledge import GovernedKnowledge
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result import (
    GovernedKnowledgeLifecycleAssertionInterpretationResult,
)

KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION: Final = (
    "knowledge_repository_initial_write_request_contract_v1"
)
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION: Final = (
    "knowledge_repository_lifecycle_transition_request_contract_v1"
)
KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION: Final = (
    "knowledge_repository_lineage_record_contract_v1"
)
KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION: Final = (
    "knowledge_repository_revision_contract_v1"
)
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_RECORD_CONTRACT_VERSION: Final = (
    "knowledge_repository_lifecycle_transition_record_contract_v1"
)
KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION: Final = (
    "knowledge_repository_audit_record_contract_v1"
)
KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION: Final = (
    "knowledge_repository_write_result_contract_v1"
)
KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION: Final = (
    "knowledge_repository_lookup_result_contract_v1"
)
KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION: Final = (
    "knowledge_repository_history_result_contract_v1"
)
KNOWLEDGE_REPOSITORY_ISSUE_CONTRACT_VERSION: Final = (
    "knowledge_repository_issue_contract_v1"
)

KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION: Final = (
    "knowledge_repository_payload_json_v1"
)
KNOWLEDGE_REPOSITORY_LINEAGE_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "knowledge_repository_lineage_identity_json_v1"
)
KNOWLEDGE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "knowledge_repository_revision_identity_json_v1"
)
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "knowledge_repository_lifecycle_transition_identity_json_v1"
)
KNOWLEDGE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "knowledge_repository_audit_identity_json_v1"
)

KNOWLEDGE_REPOSITORY_POLICY_ID: Final = "rcis-governed-knowledge-repository"
KNOWLEDGE_REPOSITORY_POLICY_VERSION: Final = "1.0.0"
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID: Final = (
    "rcis-governed-knowledge-lifecycle-transition"
)
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION: Final = "1.0.0"
KNOWLEDGE_REPOSITORY_DIGEST_ALGORITHM: Final = "sha256"

KNOWLEDGE_REPOSITORY_LINEAGE_ID_PREFIX: Final = "gkrl1_"
KNOWLEDGE_REPOSITORY_REVISION_ID_PREFIX: Final = "gkr1_"
KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_ID_PREFIX: Final = "gkrt1_"
KNOWLEDGE_REPOSITORY_AUDIT_ID_PREFIX: Final = "gkra1_"

SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID: Final = (
    "rcis-gate9-governed-knowledge-repository-sqlite"
)
SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION: Final = 1

KNOWLEDGE_REPOSITORY_WRITE_STATUSES: Final = (
    "persisted_initial",
    "appended_lifecycle_transition",
    "unchanged_exact_replay",
    "rejected",
)
KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES: Final = (
    "found",
    "not_found",
    "rejected",
)
KNOWLEDGE_REPOSITORY_ISSUE_CODES: Final = (
    "invalid_request",
    "unsupported_contract_version",
    "unsupported_repository_policy",
    "unsupported_transition_policy",
    "invalid_governed_knowledge",
    "governed_knowledge_identity_mismatch",
    "invalid_persisted_evidence_knowledge_construction_result",
    "persisted_evidence_knowledge_construction_rejected",
    "missing_persisted_evidence_knowledge_compatibility_record",
    "invalid_gate_8_knowledge_candidate",
    "gate_8_knowledge_candidate_identity_mismatch",
    "governed_knowledge_candidate_lineage_mismatch",
    "invalid_governed_knowledge_construction_result",
    "governed_knowledge_construction_rejected",
    "governed_knowledge_construction_result_mismatch",
    "invalid_lifecycle_interpretation_result",
    "lifecycle_interpretation_subject_mismatch",
    "lifecycle_interpretation_identity_mismatch",
    "lifecycle_transition_no_change",
    "initial_revision_already_bound_to_different_content",
    "expected_prior_revision_not_found",
    "expected_prior_revision_identity_mismatch",
    "expected_prior_revision_number_mismatch",
    "stale_expected_prior_revision",
    "lifecycle_transition_conflict",
    "lineage_record_id_mismatch",
    "revision_id_mismatch",
    "transition_record_id_mismatch",
    "audit_id_mismatch",
    "unsupported_schema",
    "repository_busy",
    "repository_corrupt",
    "repository_unavailable",
    "internal_contract_violation",
)
_ISSUE_MESSAGES = MappingProxyType(
    {
        code: code.replace("_", " ").capitalize() + "."
        for code in KNOWLEDGE_REPOSITORY_ISSUE_CODES
    }
)


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_datetime(value: object, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{field} must be a timezone-aware datetime")
    return value


def _require_unique_strings(value: object, field: str) -> tuple[str, ...]:
    if (
        not isinstance(value, tuple)
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != len(value)
    ):
        raise ValueError(f"{field} must be a tuple of unique non-empty strings")
    return value


@dataclass(frozen=True)
class KnowledgeRepositoryInitialWriteRequest:
    contract_version: str
    governed_knowledge: GovernedKnowledge
    persisted_evidence_knowledge_construction_result: object
    governed_knowledge_construction_result: GovernedKnowledgeConstructionResult
    lifecycle_interpretation_result: (
        GovernedKnowledgeLifecycleAssertionInterpretationResult
    )
    actor_id: str
    recorded_at_utc: datetime
    repository_policy_id: str
    repository_policy_version: str

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        if not isinstance(self.governed_knowledge, GovernedKnowledge):
            raise ValueError("governed_knowledge has an invalid type")
        persisted_result_type = type(
            self.persisted_evidence_knowledge_construction_result
        )
        if (
            persisted_result_type.__module__
            != (
                "rie.persisted_evidence_knowledge_construction."
                "persisted_evidence_knowledge_construction_contract"
            )
            or persisted_result_type.__qualname__
            != "PersistedEvidenceKnowledgeConstructionResult"
        ):
            raise ValueError(
                "persisted_evidence_knowledge_construction_result has an invalid type"
            )
        if not isinstance(
            self.governed_knowledge_construction_result,
            GovernedKnowledgeConstructionResult,
        ):
            raise ValueError(
                "governed_knowledge_construction_result has an invalid type"
            )
        if not isinstance(
            self.lifecycle_interpretation_result,
            GovernedKnowledgeLifecycleAssertionInterpretationResult,
        ):
            raise ValueError("lifecycle_interpretation_result has an invalid type")
        _require_string(self.actor_id, "actor_id")
        _require_datetime(self.recorded_at_utc, "recorded_at_utc")
        _require_string(self.repository_policy_id, "repository_policy_id")
        _require_string(self.repository_policy_version, "repository_policy_version")


@dataclass(frozen=True)
class KnowledgeRepositoryLifecycleTransitionRequest:
    contract_version: str
    governed_knowledge_id: str
    expected_prior_revision_id: str
    expected_prior_revision_number: int
    next_lifecycle_interpretation_result: (
        GovernedKnowledgeLifecycleAssertionInterpretationResult
    )
    transition_reason_codes: tuple[str, ...]
    actor_id: str
    recorded_at_utc: datetime
    transition_policy_id: str
    transition_policy_version: str

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        _require_string(self.governed_knowledge_id, "governed_knowledge_id")
        _require_string(
            self.expected_prior_revision_id, "expected_prior_revision_id"
        )
        if (
            not isinstance(self.expected_prior_revision_number, int)
            or self.expected_prior_revision_number < 1
        ):
            raise ValueError(
                "expected_prior_revision_number must be a positive integer"
            )
        if not isinstance(
            self.next_lifecycle_interpretation_result,
            GovernedKnowledgeLifecycleAssertionInterpretationResult,
        ):
            raise ValueError(
                "next_lifecycle_interpretation_result has an invalid type"
            )
        _require_unique_strings(
            self.transition_reason_codes, "transition_reason_codes"
        )
        _require_string(self.actor_id, "actor_id")
        _require_datetime(self.recorded_at_utc, "recorded_at_utc")
        _require_string(self.transition_policy_id, "transition_policy_id")
        _require_string(self.transition_policy_version, "transition_policy_version")


@dataclass(frozen=True)
class KnowledgeRepositoryLineageRecord:
    contract_version: str
    lineage_record_id: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    persisted_evidence_knowledge_compatibility_record_id: str
    evidence_repository_revision_id: str
    evidence_repository_audit_id: str
    source_id: str
    source_revision_number: int
    traceable_evidence_id: str
    accepted_evidence_id: str
    acceptance_record_ids: tuple[str, ...]
    construction_rule_id: str
    construction_rule_version: str
    governed_knowledge_construction_policy_id: str
    governed_knowledge_construction_policy_version: str
    lineage_policy_id: str
    lineage_policy_version: str

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if name == "source_revision_number":
                if not isinstance(value, int) or value < 1:
                    raise ValueError("source_revision_number must be positive")
            elif name == "acceptance_record_ids":
                _require_unique_strings(value, name)
            else:
                _require_string(value, name)


@dataclass(frozen=True)
class KnowledgeRepositoryRevision:
    contract_version: str
    revision_id: str
    governed_knowledge_id: str
    revision_number: int
    previous_revision_id: str | None
    governed_knowledge_payload_digest: str
    lineage_record_id: str
    lifecycle_interpretation_result_id: str
    lifecycle_interpretation_result_contract_version: str
    lifecycle_interpretation_result_payload_digest: str
    transition_record_id: str | None
    actor_id: str
    recorded_at_utc: datetime
    audit_id: str

    def __post_init__(self) -> None:
        for field in (
            "contract_version",
            "revision_id",
            "governed_knowledge_id",
            "governed_knowledge_payload_digest",
            "lineage_record_id",
            "lifecycle_interpretation_result_id",
            "lifecycle_interpretation_result_contract_version",
            "lifecycle_interpretation_result_payload_digest",
            "actor_id",
            "audit_id",
        ):
            _require_string(getattr(self, field), field)
        if not isinstance(self.revision_number, int) or self.revision_number < 1:
            raise ValueError("revision_number must be positive")
        if self.previous_revision_id is not None:
            _require_string(self.previous_revision_id, "previous_revision_id")
        if self.transition_record_id is not None:
            _require_string(self.transition_record_id, "transition_record_id")
        _require_datetime(self.recorded_at_utc, "recorded_at_utc")


@dataclass(frozen=True)
class KnowledgeRepositoryLifecycleTransitionRecord:
    contract_version: str
    transition_record_id: str
    governed_knowledge_id: str
    from_revision_id: str
    from_revision_number: int
    previous_lifecycle_interpretation_result_id: str
    next_lifecycle_interpretation_result_id: str
    transition_reason_codes: tuple[str, ...]
    actor_id: str
    recorded_at_utc: datetime
    transition_policy_id: str
    transition_policy_version: str

    def __post_init__(self) -> None:
        for field in (
            "contract_version",
            "transition_record_id",
            "governed_knowledge_id",
            "from_revision_id",
            "previous_lifecycle_interpretation_result_id",
            "next_lifecycle_interpretation_result_id",
            "actor_id",
            "transition_policy_id",
            "transition_policy_version",
        ):
            _require_string(getattr(self, field), field)
        if (
            not isinstance(self.from_revision_number, int)
            or self.from_revision_number < 1
        ):
            raise ValueError("from_revision_number must be positive")
        _require_unique_strings(
            self.transition_reason_codes, "transition_reason_codes"
        )
        _require_datetime(self.recorded_at_utc, "recorded_at_utc")


@dataclass(frozen=True)
class KnowledgeRepositoryAuditRecord:
    contract_version: str
    audit_id: str
    action: str
    revision_id: str
    governed_knowledge_id: str
    revision_number: int
    lineage_record_id: str
    transition_record_id: str | None
    actor_id: str
    recorded_at_utc: datetime

    def __post_init__(self) -> None:
        for field in (
            "contract_version",
            "audit_id",
            "action",
            "revision_id",
            "governed_knowledge_id",
            "lineage_record_id",
            "actor_id",
        ):
            _require_string(getattr(self, field), field)
        if not isinstance(self.revision_number, int) or self.revision_number < 1:
            raise ValueError("revision_number must be positive")
        if self.transition_record_id is not None:
            _require_string(self.transition_record_id, "transition_record_id")
        _require_datetime(self.recorded_at_utc, "recorded_at_utc")


@dataclass(frozen=True)
class KnowledgeRepositoryIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.code not in KNOWLEDGE_REPOSITORY_ISSUE_CODES:
            raise ValueError("unsupported issue code")
        _require_string(self.message, "message")


@dataclass(frozen=True)
class KnowledgeRepositoryWriteResult:
    contract_version: str
    status: str
    mutation_performed: bool
    revision: KnowledgeRepositoryRevision | None
    lineage_record: KnowledgeRepositoryLineageRecord | None
    transition_record: KnowledgeRepositoryLifecycleTransitionRecord | None
    audit_record: KnowledgeRepositoryAuditRecord | None
    governed_knowledge: GovernedKnowledge | None
    lifecycle_interpretation_result: (
        GovernedKnowledgeLifecycleAssertionInterpretationResult | None
    )
    issue: KnowledgeRepositoryIssue | None

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        if self.status not in KNOWLEDGE_REPOSITORY_WRITE_STATUSES:
            raise ValueError("unsupported write status")
        if not isinstance(self.mutation_performed, bool):
            raise ValueError("mutation_performed must be bool")
        if self.status == "rejected":
            if self.mutation_performed or self.issue is None:
                raise ValueError("rejected result invariant violated")
            return
        if self.issue is not None:
            raise ValueError("successful result cannot contain issue")
        if any(
            value is None
            for value in (
                self.revision,
                self.lineage_record,
                self.audit_record,
                self.governed_knowledge,
                self.lifecycle_interpretation_result,
            )
        ):
            raise ValueError("successful result payload is incomplete")
        expected = self.status in {
            "persisted_initial",
            "appended_lifecycle_transition",
        }
        if self.mutation_performed is not expected:
            raise ValueError("write mutation invariant violated")


@dataclass(frozen=True)
class KnowledgeRepositoryLookupResult:
    contract_version: str
    status: str
    revision: KnowledgeRepositoryRevision | None
    lineage_record: KnowledgeRepositoryLineageRecord | None
    transition_record: KnowledgeRepositoryLifecycleTransitionRecord | None
    audit_record: KnowledgeRepositoryAuditRecord | None
    governed_knowledge: GovernedKnowledge | None
    lifecycle_interpretation_result: (
        GovernedKnowledgeLifecycleAssertionInterpretationResult | None
    )
    issue: KnowledgeRepositoryIssue | None

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        if self.status not in KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES:
            raise ValueError("unsupported lookup status")
        required_payload = (
            self.revision,
            self.lineage_record,
            self.audit_record,
            self.governed_knowledge,
            self.lifecycle_interpretation_result,
        )
        all_payload = required_payload + (self.transition_record,)
        if self.status == "found":
            if any(value is None for value in required_payload) or self.issue:
                raise ValueError("found lookup invariant violated")
        elif self.status == "not_found":
            if any(value is not None for value in all_payload) or self.issue:
                raise ValueError("not_found lookup invariant violated")
        elif any(value is not None for value in all_payload) or self.issue is None:
            raise ValueError("rejected lookup invariant violated")


@dataclass(frozen=True)
class KnowledgeRepositoryHistoryResult:
    contract_version: str
    status: str
    governed_knowledge_id: str
    governed_knowledge: GovernedKnowledge | None
    lineage_record: KnowledgeRepositoryLineageRecord | None
    revisions: tuple[KnowledgeRepositoryRevision, ...]
    lifecycle_interpretation_results: tuple[
        GovernedKnowledgeLifecycleAssertionInterpretationResult, ...
    ]
    transition_records: tuple[KnowledgeRepositoryLifecycleTransitionRecord, ...]
    audit_records: tuple[KnowledgeRepositoryAuditRecord, ...]
    issue: KnowledgeRepositoryIssue | None

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        _require_string(self.governed_knowledge_id, "governed_knowledge_id")
        if self.status not in KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES:
            raise ValueError("unsupported history status")
        if self.status == "found":
            if (
                self.governed_knowledge is None
                or self.lineage_record is None
                or self.issue is not None
                or not self.revisions
                or len(self.revisions)
                != len(self.lifecycle_interpretation_results)
                or len(self.audit_records) != len(self.revisions)
                or len(self.transition_records) != len(self.revisions) - 1
            ):
                raise ValueError("found history invariant violated")
        elif self.status == "not_found":
            if (
                self.governed_knowledge is not None
                or self.lineage_record is not None
                or self.revisions
                or self.lifecycle_interpretation_results
                or self.transition_records
                or self.audit_records
                or self.issue is not None
            ):
                raise ValueError("not_found history invariant violated")
        elif self.issue is None:
            raise ValueError("rejected history requires issue")


def _issue(code: str) -> KnowledgeRepositoryIssue:
    return KnowledgeRepositoryIssue(code=code, message=_ISSUE_MESSAGES[code])
