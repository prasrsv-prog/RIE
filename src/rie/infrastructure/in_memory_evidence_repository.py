"""Process-local reference adapter for the EvidenceRepository protocol."""

from __future__ import annotations

from dataclasses import dataclass
import re
from threading import RLock
from types import MappingProxyType
from typing import Mapping

from rie.domain.acceptance_identity import (
    AcceptanceIdentityInput,
    acceptance_identity_input_from_record,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence
from rie.domain.evidence_identity import (
    EvidenceIdentityInput,
    identity_input_from_accepted_evidence,
)
from rie.interfaces.evidence_repository import (
    AcceptanceRecordListResult,
    AcceptanceRecordLookupResult,
    EvidenceLookupResult,
    EvidenceRepository,
    EvidenceWriteClassificationResult,
    EvidenceWriteRequest,
    EvidenceWriteResult,
)


_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(
    r"^ar1_[0-9a-f]{64}$"
)


@dataclass(frozen=True)
class _EvidenceEntry:
    accepted_evidence: AcceptedEvidence
    canonical_digest: str
    identity_projection: EvidenceIdentityInput


@dataclass(frozen=True)
class _AcceptanceEntry:
    acceptance_record: AcceptanceRecord
    canonical_digest: str
    identity_projection: AcceptanceIdentityInput


@dataclass(frozen=True)
class _RepositoryState:
    evidence_by_id: Mapping[str, _EvidenceEntry]
    acceptance_by_id: Mapping[str, _AcceptanceEntry]
    acceptance_ids_by_evidence_id: Mapping[str, tuple[str, ...]]


def _freeze_mapping(
    values: Mapping[str, object],
) -> Mapping[str, object]:
    return MappingProxyType(dict(values))


def _empty_state() -> _RepositoryState:
    return _RepositoryState(
        evidence_by_id=_freeze_mapping({}),
        acceptance_by_id=_freeze_mapping({}),
        acceptance_ids_by_evidence_id=_freeze_mapping({}),
    )


def _require_exact_request(request: object) -> EvidenceWriteRequest:
    if type(request) is not EvidenceWriteRequest:
        raise ValueError(
            "request must be an exact EvidenceWriteRequest"
        )
    return request


def _require_identifier(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")
    return value


def _classification_reason(
    classification: str,
) -> str:
    reasons = {
        "new_evidence": "new_evidence",
        "exact_replay": "exact_replay_detected",
        "governance_replay": "governance_replay_detected",
        "same_fact_new_acceptance": "same_fact_new_acceptance",
        "identity_collision": "identity_collision_detected",
        "acceptance_collision": "acceptance_collision_detected",
        "rejected": "request_invalid",
    }
    return reasons[classification]


class InMemoryEvidenceRepository:
    """Volatile append-only reference adapter."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._state = _empty_state()

    def get_evidence(
        self,
        evidence_id: str,
    ) -> EvidenceLookupResult:
        valid_evidence_id = _require_identifier(
            evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )

        with self._lock:
            entry = self._state.evidence_by_id.get(
                valid_evidence_id
            )
            if entry is None:
                return EvidenceLookupResult(
                    status="not_found",
                    accepted_evidence=None,
                    canonical_evidence_bytes_digest=None,
                    acceptance_record_ids=(),
                    reason_codes=("evidence_not_found",),
                    diagnostics=(),
                )

            acceptance_ids = (
                self._state.acceptance_ids_by_evidence_id.get(
                    valid_evidence_id,
                    (),
                )
            )
            return EvidenceLookupResult(
                status="found",
                accepted_evidence=entry.accepted_evidence,
                canonical_evidence_bytes_digest=(
                    entry.canonical_digest
                ),
                acceptance_record_ids=acceptance_ids,
                reason_codes=(),
                diagnostics=(),
            )

    def get_acceptance_record(
        self,
        acceptance_record_id: str,
    ) -> AcceptanceRecordLookupResult:
        valid_acceptance_id = _require_identifier(
            acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_RECORD_ID_PATTERN,
        )

        with self._lock:
            entry = self._state.acceptance_by_id.get(
                valid_acceptance_id
            )
            if entry is None:
                return AcceptanceRecordLookupResult(
                    status="not_found",
                    acceptance_record=None,
                    canonical_acceptance_bytes_digest=None,
                    evidence_id=None,
                    reason_codes=(
                        "acceptance_record_not_found",
                    ),
                    diagnostics=(),
                )

            return AcceptanceRecordLookupResult(
                status="found",
                acceptance_record=entry.acceptance_record,
                canonical_acceptance_bytes_digest=(
                    entry.canonical_digest
                ),
                evidence_id=entry.acceptance_record.evidence_id,
                reason_codes=(),
                diagnostics=(),
            )

    def list_acceptance_records(
        self,
        evidence_id: str,
    ) -> AcceptanceRecordListResult:
        valid_evidence_id = _require_identifier(
            evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )

        with self._lock:
            acceptance_ids = (
                self._state.acceptance_ids_by_evidence_id.get(
                    valid_evidence_id,
                    (),
                )
            )
            if not acceptance_ids:
                return AcceptanceRecordListResult(
                    status="not_found",
                    evidence_id=valid_evidence_id,
                    acceptance_records=(),
                    reason_codes=(
                        "acceptance_record_not_found",
                    ),
                    diagnostics=(),
                )

            records = tuple(
                self._state.acceptance_by_id[
                    acceptance_record_id
                ].acceptance_record
                for acceptance_record_id in acceptance_ids
            )
            return AcceptanceRecordListResult(
                status="found",
                evidence_id=valid_evidence_id,
                acceptance_records=records,
                reason_codes=(),
                diagnostics=(),
            )

    def classify_write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult:
        exact_request = _require_exact_request(request)

        with self._lock:
            return self._classify_locked(exact_request)

    def write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteResult:
        exact_request = _require_exact_request(request)

        with self._lock:
            classification = self._classify_locked(
                exact_request
            )
            if classification.classification == "new_evidence":
                self._state = self._state_with_new_evidence(
                    exact_request
                )
                return self._write_result(
                    classification,
                    "inserted_new_evidence",
                    mutation_performed=True,
                )

            if (
                classification.classification
                == "same_fact_new_acceptance"
            ):
                self._state = (
                    self._state_with_new_acceptance(
                        exact_request
                    )
                )
                return self._write_result(
                    classification,
                    "appended_acceptance_record",
                    mutation_performed=True,
                )

            status_by_classification = {
                "exact_replay": "unchanged_exact_replay",
                "governance_replay": (
                    "unchanged_governance_replay"
                ),
                "identity_collision": (
                    "rejected_identity_collision"
                ),
                "acceptance_collision": (
                    "rejected_acceptance_collision"
                ),
                "rejected": "rejected_invalid_request",
            }
            status = status_by_classification.get(
                classification.classification,
                "rejected_invalid_request",
            )
            controlled_classification = (
                classification.classification
                if classification.classification
                in status_by_classification
                else "rejected"
            )
            controlled_result = (
                classification
                if controlled_classification
                == classification.classification
                else EvidenceWriteClassificationResult(
                    classification=controlled_classification,
                    evidence_id=classification.evidence_id,
                    acceptance_record_id=(
                        classification.acceptance_record_id
                    ),
                    existing_evidence_digest=(
                        classification.existing_evidence_digest
                    ),
                    existing_acceptance_digest=(
                        classification.existing_acceptance_digest
                    ),
                    reason_codes=("request_invalid",),
                    diagnostics=(),
                )
            )
            return self._write_result(
                controlled_result,
                status,
                mutation_performed=False,
            )

    def _classify_locked(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult:
        evidence_id = request.accepted_evidence.evidence_id
        acceptance_record_id = (
            request.acceptance_record.acceptance_record_id
        )
        evidence_entry = self._state.evidence_by_id.get(
            evidence_id
        )
        acceptance_entry = (
            self._state.acceptance_by_id.get(
                acceptance_record_id
            )
        )
        evidence_projection = (
            identity_input_from_accepted_evidence(
                request.accepted_evidence
            )
        )
        acceptance_projection = (
            acceptance_identity_input_from_record(
                request.acceptance_record
            )
        )

        if (
            evidence_entry is not None
            and evidence_entry.canonical_digest
            != request.canonical_evidence_bytes_digest
        ):
            return self._classification_result(
                request,
                "identity_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and evidence_entry.identity_projection
            != evidence_projection
        ):
            return self._classification_result(
                request,
                "identity_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            acceptance_entry is not None
            and acceptance_entry.canonical_digest
            != request.canonical_acceptance_bytes_digest
        ):
            return self._classification_result(
                request,
                "acceptance_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            acceptance_entry is not None
            and acceptance_entry.identity_projection
            != acceptance_projection
        ):
            return self._classification_result(
                request,
                "acceptance_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is None
            and acceptance_entry is None
        ):
            return self._classification_result(
                request,
                "new_evidence",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and acceptance_entry is None
        ):
            return self._classification_result(
                request,
                "same_fact_new_acceptance",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and acceptance_entry is not None
        ):
            if (
                evidence_entry.accepted_evidence
                == request.accepted_evidence
                and acceptance_entry.acceptance_record
                == request.acceptance_record
            ):
                replay_classification = "exact_replay"
            else:
                replay_classification = "governance_replay"

            return self._classification_result(
                request,
                replay_classification,
                evidence_entry,
                acceptance_entry,
            )

        return self._classification_result(
            request,
            "rejected",
            evidence_entry,
            acceptance_entry,
        )

    def _classification_result(
        self,
        request: EvidenceWriteRequest,
        classification: str,
        evidence_entry: _EvidenceEntry | None,
        acceptance_entry: _AcceptanceEntry | None,
    ) -> EvidenceWriteClassificationResult:
        return EvidenceWriteClassificationResult(
            classification=classification,
            evidence_id=request.accepted_evidence.evidence_id,
            acceptance_record_id=(
                request.acceptance_record.acceptance_record_id
            ),
            existing_evidence_digest=(
                evidence_entry.canonical_digest
                if evidence_entry is not None
                else None
            ),
            existing_acceptance_digest=(
                acceptance_entry.canonical_digest
                if acceptance_entry is not None
                else None
            ),
            reason_codes=(
                _classification_reason(classification),
            ),
            diagnostics=(),
        )

    def _state_with_new_evidence(
        self,
        request: EvidenceWriteRequest,
    ) -> _RepositoryState:
        evidence_id = request.accepted_evidence.evidence_id
        acceptance_record_id = (
            request.acceptance_record.acceptance_record_id
        )
        evidence_entries = dict(
            self._state.evidence_by_id
        )
        acceptance_entries = dict(
            self._state.acceptance_by_id
        )
        memberships = dict(
            self._state.acceptance_ids_by_evidence_id
        )

        evidence_entries[evidence_id] = _EvidenceEntry(
            accepted_evidence=request.accepted_evidence,
            canonical_digest=(
                request.canonical_evidence_bytes_digest
            ),
            identity_projection=(
                identity_input_from_accepted_evidence(
                    request.accepted_evidence
                )
            ),
        )
        acceptance_entries[
            acceptance_record_id
        ] = _AcceptanceEntry(
            acceptance_record=request.acceptance_record,
            canonical_digest=(
                request.canonical_acceptance_bytes_digest
            ),
            identity_projection=(
                acceptance_identity_input_from_record(
                    request.acceptance_record
                )
            ),
        )
        memberships[evidence_id] = (
            acceptance_record_id,
        )

        return _RepositoryState(
            evidence_by_id=_freeze_mapping(
                evidence_entries
            ),
            acceptance_by_id=_freeze_mapping(
                acceptance_entries
            ),
            acceptance_ids_by_evidence_id=(
                _freeze_mapping(memberships)
            ),
        )

    def _state_with_new_acceptance(
        self,
        request: EvidenceWriteRequest,
    ) -> _RepositoryState:
        evidence_id = request.accepted_evidence.evidence_id
        acceptance_record_id = (
            request.acceptance_record.acceptance_record_id
        )
        acceptance_entries = dict(
            self._state.acceptance_by_id
        )
        memberships = dict(
            self._state.acceptance_ids_by_evidence_id
        )

        acceptance_entries[
            acceptance_record_id
        ] = _AcceptanceEntry(
            acceptance_record=request.acceptance_record,
            canonical_digest=(
                request.canonical_acceptance_bytes_digest
            ),
            identity_projection=(
                acceptance_identity_input_from_record(
                    request.acceptance_record
                )
            ),
        )
        existing_ids = memberships.get(
            evidence_id,
            (),
        )
        memberships[evidence_id] = tuple(
            sorted(
                (*existing_ids, acceptance_record_id)
            )
        )

        return _RepositoryState(
            evidence_by_id=self._state.evidence_by_id,
            acceptance_by_id=_freeze_mapping(
                acceptance_entries
            ),
            acceptance_ids_by_evidence_id=(
                _freeze_mapping(memberships)
            ),
        )

    def _write_result(
        self,
        classification: EvidenceWriteClassificationResult,
        status: str,
        *,
        mutation_performed: bool,
    ) -> EvidenceWriteResult:
        return EvidenceWriteResult(
            status=status,
            classification=classification.classification,
            evidence_id=classification.evidence_id,
            acceptance_record_id=(
                classification.acceptance_record_id
            ),
            mutation_performed=mutation_performed,
            reason_codes=classification.reason_codes,
            diagnostics=classification.diagnostics,
        )


def _assert_protocol_shape(
    repository: EvidenceRepository,
) -> None:
    del repository
