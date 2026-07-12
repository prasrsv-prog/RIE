"""Immutable application-facing EvidenceRepository interface contracts."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol

from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence


EVIDENCE_REPOSITORY_CONTRACT_VERSION = "1.0.0"

_LOOKUP_STATUSES = frozenset({"found", "not_found", "failed"})
_CLASSIFICATIONS = frozenset(
    {
        "new_evidence",
        "exact_replay",
        "governance_replay",
        "same_fact_new_acceptance",
        "identity_collision",
        "acceptance_collision",
        "semantic_duplicate_candidate",
        "conflicting_evidence_candidate",
        "superseding_evidence_candidate",
        "rejected",
    }
)
_WRITE_STATUSES = frozenset(
    {
        "inserted_new_evidence",
        "appended_acceptance_record",
        "unchanged_exact_replay",
        "unchanged_governance_replay",
        "rejected_identity_collision",
        "rejected_acceptance_collision",
        "rejected_invalid_request",
        "failed_repository_operation",
    }
)
_WRITE_STATUS_RULES = {
    "inserted_new_evidence": ("new_evidence", True),
    "appended_acceptance_record": (
        "same_fact_new_acceptance",
        True,
    ),
    "unchanged_exact_replay": ("exact_replay", False),
    "unchanged_governance_replay": (
        "governance_replay",
        False,
    ),
    "rejected_identity_collision": (
        "identity_collision",
        False,
    ),
    "rejected_acceptance_collision": (
        "acceptance_collision",
        False,
    ),
    "rejected_invalid_request": ("rejected", False),
}

_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(
    r"^ar1_[0-9a-f]{64}$"
)
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_non_empty_string(
    value: object,
    field_name: str,
) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> None:
    _require_non_empty_string(value, field_name)
    if pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")


def _require_optional_digest(
    value: object,
    field_name: str,
) -> None:
    if value is not None:
        _require_pattern(value, field_name, _DIGEST_PATTERN)


def _require_string_tuple(
    value: object,
    field_name: str,
) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")

    for index, item in enumerate(value):
        _require_non_empty_string(
            item,
            f"{field_name}[{index}]",
        )


def _require_unique_sorted_strings(
    value: tuple[str, ...],
    field_name: str,
) -> None:
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if value != tuple(sorted(value)):
        raise ValueError(
            f"{field_name} must be lexicographically ordered"
        )


def _require_reason_and_diagnostic_tuples(
    reason_codes: object,
    diagnostics: object,
) -> None:
    _require_string_tuple(reason_codes, "reason_codes")
    _require_string_tuple(diagnostics, "diagnostics")


@dataclass(frozen=True)
class EvidenceWriteRequest:
    accepted_evidence: AcceptedEvidence
    canonical_evidence_bytes_digest: str
    acceptance_record: AcceptanceRecord
    canonical_acceptance_bytes_digest: str
    repository_contract_version: str
    expected_identity_policy_id: str
    expected_identity_policy_version: str

    def __post_init__(self) -> None:
        if type(self.accepted_evidence) is not AcceptedEvidence:
            raise ValueError(
                "accepted_evidence must be an exact AcceptedEvidence"
            )
        if type(self.acceptance_record) is not AcceptanceRecord:
            raise ValueError(
                "acceptance_record must be an exact AcceptanceRecord"
            )

        _require_pattern(
            self.canonical_evidence_bytes_digest,
            "canonical_evidence_bytes_digest",
            _DIGEST_PATTERN,
        )
        _require_pattern(
            self.canonical_acceptance_bytes_digest,
            "canonical_acceptance_bytes_digest",
            _DIGEST_PATTERN,
        )
        _require_non_empty_string(
            self.repository_contract_version,
            "repository_contract_version",
        )
        _require_non_empty_string(
            self.expected_identity_policy_id,
            "expected_identity_policy_id",
        )
        _require_non_empty_string(
            self.expected_identity_policy_version,
            "expected_identity_policy_version",
        )

        if (
            self.repository_contract_version
            != EVIDENCE_REPOSITORY_CONTRACT_VERSION
        ):
            raise ValueError("repository_contract_version mismatch")

        if (
            self.canonical_evidence_bytes_digest
            != self.accepted_evidence.evidence_id.removeprefix(
                "ev1_"
            )
        ):
            raise ValueError(
                "canonical_evidence_bytes_digest mismatch"
            )

        if (
            self.canonical_acceptance_bytes_digest
            != self.acceptance_record.acceptance_record_id.removeprefix(
                "ar1_"
            )
        ):
            raise ValueError(
                "canonical_acceptance_bytes_digest mismatch"
            )

        if (
            self.acceptance_record.evidence_id
            != self.accepted_evidence.evidence_id
        ):
            raise ValueError("acceptance_record evidence_id mismatch")

        materialization = self.accepted_evidence.materialization_record

        if (
            self.expected_identity_policy_id
            != materialization.identity_policy_id
        ):
            raise ValueError("expected_identity_policy_id mismatch")
        if (
            self.expected_identity_policy_version
            != materialization.identity_policy_version
        ):
            raise ValueError(
                "expected_identity_policy_version mismatch"
            )
        if (
            self.acceptance_record.evidence_identity_policy_id
            != self.expected_identity_policy_id
        ):
            raise ValueError(
                "acceptance_record evidence identity policy mismatch"
            )
        if (
            self.acceptance_record.evidence_identity_policy_version
            != self.expected_identity_policy_version
        ):
            raise ValueError(
                "acceptance_record evidence identity policy version mismatch"
            )

        compatibility_pairs = (
            (
                self.acceptance_record.acceptance_record_id,
                materialization.acceptance_record_id,
                "acceptance_record_id",
            ),
            (
                self.acceptance_record.accepted_by,
                materialization.accepted_by,
                "accepted_by",
            ),
            (
                self.acceptance_record.acceptance_reason,
                materialization.acceptance_reason,
                "acceptance_reason",
            ),
            (
                self.acceptance_record.review_record_id,
                materialization.review_record_id,
                "review_record_id",
            ),
            (
                self.acceptance_record.materializer_id,
                materialization.materializer_id,
                "materializer_id",
            ),
            (
                self.acceptance_record.materializer_version,
                materialization.materializer_version,
                "materializer_version",
            ),
            (
                self.acceptance_record.accepted_at,
                materialization.materialized_at,
                "accepted_at",
            ),
        )

        for observed, expected, field_name in compatibility_pairs:
            if observed != expected:
                raise ValueError(
                    f"materialization compatibility mismatch: {field_name}"
                )


@dataclass(frozen=True)
class EvidenceLookupResult:
    status: str
    accepted_evidence: AcceptedEvidence | None
    canonical_evidence_bytes_digest: str | None
    acceptance_record_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in _LOOKUP_STATUSES:
            raise ValueError("unsupported lookup status")

        _require_string_tuple(
            self.acceptance_record_ids,
            "acceptance_record_ids",
        )
        for index, record_id in enumerate(
            self.acceptance_record_ids
        ):
            _require_pattern(
                record_id,
                f"acceptance_record_ids[{index}]",
                _ACCEPTANCE_RECORD_ID_PATTERN,
            )
        _require_unique_sorted_strings(
            self.acceptance_record_ids,
            "acceptance_record_ids",
        )
        _require_reason_and_diagnostic_tuples(
            self.reason_codes,
            self.diagnostics,
        )

        if self.status == "found":
            if type(self.accepted_evidence) is not AcceptedEvidence:
                raise ValueError(
                    "found result requires exact AcceptedEvidence"
                )
            _require_pattern(
                self.canonical_evidence_bytes_digest,
                "canonical_evidence_bytes_digest",
                _DIGEST_PATTERN,
            )
            if (
                self.canonical_evidence_bytes_digest
                != self.accepted_evidence.evidence_id.removeprefix(
                    "ev1_"
                )
            ):
                raise ValueError(
                    "canonical_evidence_bytes_digest mismatch"
                )
            if not self.acceptance_record_ids:
                raise ValueError(
                    "found result requires acceptance_record_ids"
                )
        else:
            if self.accepted_evidence is not None:
                raise ValueError(
                    "non-found result must not contain accepted_evidence"
                )
            if self.canonical_evidence_bytes_digest is not None:
                raise ValueError(
                    "non-found result must not contain evidence digest"
                )
            if self.acceptance_record_ids:
                raise ValueError(
                    "non-found result must have empty acceptance_record_ids"
                )


@dataclass(frozen=True)
class AcceptanceRecordLookupResult:
    status: str
    acceptance_record: AcceptanceRecord | None
    canonical_acceptance_bytes_digest: str | None
    evidence_id: str | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in _LOOKUP_STATUSES:
            raise ValueError("unsupported lookup status")

        _require_reason_and_diagnostic_tuples(
            self.reason_codes,
            self.diagnostics,
        )

        if self.status == "found":
            if type(self.acceptance_record) is not AcceptanceRecord:
                raise ValueError(
                    "found result requires exact AcceptanceRecord"
                )
            _require_pattern(
                self.canonical_acceptance_bytes_digest,
                "canonical_acceptance_bytes_digest",
                _DIGEST_PATTERN,
            )
            _require_pattern(
                self.evidence_id,
                "evidence_id",
                _EVIDENCE_ID_PATTERN,
            )
            if (
                self.canonical_acceptance_bytes_digest
                != self.acceptance_record.acceptance_record_id.removeprefix(
                    "ar1_"
                )
            ):
                raise ValueError(
                    "canonical_acceptance_bytes_digest mismatch"
                )
            if self.evidence_id != self.acceptance_record.evidence_id:
                raise ValueError("evidence_id mismatch")
        else:
            if self.acceptance_record is not None:
                raise ValueError(
                    "non-found result must not contain acceptance_record"
                )
            if self.canonical_acceptance_bytes_digest is not None:
                raise ValueError(
                    "non-found result must not contain acceptance digest"
                )
            if self.evidence_id is not None:
                raise ValueError(
                    "non-found result must not contain evidence_id"
                )


@dataclass(frozen=True)
class AcceptanceRecordListResult:
    status: str
    evidence_id: str
    acceptance_records: tuple[AcceptanceRecord, ...]
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in _LOOKUP_STATUSES:
            raise ValueError("unsupported lookup status")

        _require_pattern(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        if type(self.acceptance_records) is not tuple:
            raise ValueError("acceptance_records must be a tuple")

        record_ids: list[str] = []
        for index, record in enumerate(self.acceptance_records):
            if type(record) is not AcceptanceRecord:
                raise ValueError(
                    f"acceptance_records[{index}] must be exact"
                )
            if record.evidence_id != self.evidence_id:
                raise ValueError(
                    "acceptance record evidence_id mismatch"
                )
            record_ids.append(record.acceptance_record_id)

        if len(set(record_ids)) != len(record_ids):
            raise ValueError(
                "acceptance_records must contain unique records"
            )
        if record_ids != sorted(record_ids):
            raise ValueError(
                "acceptance_records must be ordered by ID"
            )

        _require_reason_and_diagnostic_tuples(
            self.reason_codes,
            self.diagnostics,
        )

        if self.status == "found":
            if not self.acceptance_records:
                raise ValueError(
                    "found result requires acceptance_records"
                )
        elif self.acceptance_records:
            raise ValueError(
                "non-found result must have empty acceptance_records"
            )


@dataclass(frozen=True)
class EvidenceWriteClassificationResult:
    classification: str
    evidence_id: str
    acceptance_record_id: str
    existing_evidence_digest: str | None
    existing_acceptance_digest: str | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.classification not in _CLASSIFICATIONS:
            raise ValueError("unsupported classification")

        _require_pattern(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        _require_pattern(
            self.acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_RECORD_ID_PATTERN,
        )
        _require_optional_digest(
            self.existing_evidence_digest,
            "existing_evidence_digest",
        )
        _require_optional_digest(
            self.existing_acceptance_digest,
            "existing_acceptance_digest",
        )
        _require_reason_and_diagnostic_tuples(
            self.reason_codes,
            self.diagnostics,
        )


@dataclass(frozen=True)
class EvidenceWriteResult:
    status: str
    classification: str
    evidence_id: str
    acceptance_record_id: str
    mutation_performed: bool
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in _WRITE_STATUSES:
            raise ValueError("unsupported write status")
        if self.classification not in _CLASSIFICATIONS:
            raise ValueError("unsupported classification")

        _require_pattern(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        _require_pattern(
            self.acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_RECORD_ID_PATTERN,
        )
        if type(self.mutation_performed) is not bool:
            raise ValueError("mutation_performed must be a bool")
        _require_reason_and_diagnostic_tuples(
            self.reason_codes,
            self.diagnostics,
        )

        if self.status == "failed_repository_operation":
            if self.mutation_performed:
                raise ValueError(
                    "failed repository operation cannot mutate"
                )
            return

        expected_classification, expected_mutation = (
            _WRITE_STATUS_RULES[self.status]
        )
        if self.classification != expected_classification:
            raise ValueError(
                "write status classification mismatch"
            )
        if self.mutation_performed is not expected_mutation:
            raise ValueError("write status mutation mismatch")


class EvidenceRepository(Protocol):
    def get_evidence(
        self,
        evidence_id: str,
    ) -> EvidenceLookupResult:
        ...

    def get_acceptance_record(
        self,
        acceptance_record_id: str,
    ) -> AcceptanceRecordLookupResult:
        ...

    def list_acceptance_records(
        self,
        evidence_id: str,
    ) -> AcceptanceRecordListResult:
        ...

    def classify_write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult:
        ...

    def write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteResult:
        ...
