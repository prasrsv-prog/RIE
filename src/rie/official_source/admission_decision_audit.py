"""Gate 12 admission-decision audit evidence model.

This module implements deterministic construction and source-linkage
validation only. Persistence, registry integration, parser integration,
CLI behavior, admission workflow orchestration, real-asset execution,
Gate 13 behavior, and semantic interpretation are outside this boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Final

from .official_image_source import AdmissionStatus, OfficialImageSource


class AdmissionDecisionReasonCode(str, Enum):
    ACCEPTED_VALIDATED = "ACCEPTED_VALIDATED"
    REJECTED_IDENTITY_INVALID = "REJECTED_IDENTITY_INVALID"
    REJECTED_AUTHORITY_INVALID = "REJECTED_AUTHORITY_INVALID"
    REJECTED_RIGHTS_INVALID = "REJECTED_RIGHTS_INVALID"
    REJECTED_CHECKSUM_INVALID = "REJECTED_CHECKSUM_INVALID"
    REJECTED_BYTE_LENGTH_INVALID = "REJECTED_BYTE_LENGTH_INVALID"
    REJECTED_PROVENANCE_INVALID = "REJECTED_PROVENANCE_INVALID"
    REJECTED_OTHER_CONTRACT_VIOLATION = (
        "REJECTED_OTHER_CONTRACT_VIOLATION"
    )


_REJECTION_REASON_CODES: Final[frozenset[AdmissionDecisionReasonCode]] = (
    frozenset(
        {
            AdmissionDecisionReasonCode.REJECTED_IDENTITY_INVALID,
            AdmissionDecisionReasonCode.REJECTED_AUTHORITY_INVALID,
            AdmissionDecisionReasonCode.REJECTED_RIGHTS_INVALID,
            AdmissionDecisionReasonCode.REJECTED_CHECKSUM_INVALID,
            AdmissionDecisionReasonCode.REJECTED_BYTE_LENGTH_INVALID,
            AdmissionDecisionReasonCode.REJECTED_PROVENANCE_INVALID,
            AdmissionDecisionReasonCode.REJECTED_OTHER_CONTRACT_VIOLATION,
        }
    )
)


@dataclass(frozen=True, slots=True)
class AdmissionDecisionAudit:
    """Immutable audit evidence for one terminal admission decision."""

    decision_id: str
    source_id: str
    prior_admission_status: AdmissionStatus
    resulting_admission_status: AdmissionStatus
    reason_code: AdmissionDecisionReasonCode
    reason_detail: str
    evidence_reference: str
    decided_at_utc: datetime
    decided_by: str

    def __post_init__(self) -> None:
        _require_clean_nonempty_text("decision_id", self.decision_id)
        _require_clean_nonempty_text("source_id", self.source_id)
        _require_enum(
            "prior_admission_status",
            self.prior_admission_status,
            AdmissionStatus,
        )
        _require_enum(
            "resulting_admission_status",
            self.resulting_admission_status,
            AdmissionStatus,
        )
        _require_enum("reason_code", self.reason_code, AdmissionDecisionReasonCode)
        _require_clean_nonempty_text("reason_detail", self.reason_detail)
        _require_clean_nonempty_text(
            "evidence_reference",
            self.evidence_reference,
        )
        _require_normalized_utc(self.decided_at_utc)
        _require_clean_nonempty_text("decided_by", self.decided_by)
        _require_admission_result_consistency(
            self.prior_admission_status,
            self.resulting_admission_status,
            self.reason_code,
        )

    @classmethod
    def required_field_names(cls) -> tuple[str, ...]:
        """Return the canonical nine-field audit record order."""

        return tuple(field.name for field in fields(cls))

    def require_source_linkage(self, source: OfficialImageSource) -> None:
        """Reject a governed source whose identity does not match this audit."""

        if not isinstance(source, OfficialImageSource):
            raise TypeError("source must be an OfficialImageSource")
        if source.source_id != self.source_id:
            raise ValueError("audit source_id does not match governed source_id")


def _require_clean_nonempty_text(name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value:
        raise ValueError(f"{name} must be non-empty")
    if value != value.strip():
        raise ValueError(f"{name} must not contain surrounding whitespace")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{name} must not contain control characters")


def _require_enum(name: str, value: object, enum_type: type[Enum]) -> None:
    if not isinstance(value, enum_type):
        article = "an" if enum_type.__name__[0].lower() in "aeiou" else "a"
        raise TypeError(f"{name} must be {article} {enum_type.__name__}")


def _require_normalized_utc(value: object) -> None:
    if not isinstance(value, datetime):
        raise TypeError("decided_at_utc must be a datetime")
    if value.tzinfo is not timezone.utc:
        raise ValueError("decided_at_utc must use datetime.timezone.utc")


def _require_admission_result_consistency(
    prior_status: AdmissionStatus,
    resulting_status: AdmissionStatus,
    reason_code: AdmissionDecisionReasonCode,
) -> None:
    if prior_status is not AdmissionStatus.PENDING:
        raise ValueError("prior_admission_status must be PENDING")
    if resulting_status not in {
        AdmissionStatus.ACCEPTED,
        AdmissionStatus.REJECTED,
    }:
        raise ValueError(
            "resulting_admission_status must be ACCEPTED or REJECTED"
        )
    if resulting_status is AdmissionStatus.ACCEPTED:
        if reason_code is not AdmissionDecisionReasonCode.ACCEPTED_VALIDATED:
            raise ValueError(
                "ACCEPTED requires reason_code ACCEPTED_VALIDATED"
            )
        return
    if reason_code not in _REJECTION_REASON_CODES:
        raise ValueError("REJECTED requires a REJECTED reason_code")
