"""Immutable standalone acceptance-record domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re


_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ALLOWED_DIAGNOSTIC_SEVERITIES = frozenset({"info", "warning"})


def _require_non_empty_string(value: object, field_name: str) -> None:
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


def _require_timezone_aware_datetime(
    value: object,
    field_name: str,
) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class AcceptanceDiagnostic:
    code: str
    severity: str
    message: str
    field: str
    source: str

    def __post_init__(self) -> None:
        for field_name in (
            "code",
            "severity",
            "message",
            "field",
            "source",
        ):
            _require_non_empty_string(
                getattr(self, field_name),
                field_name,
            )

        if self.severity not in _ALLOWED_DIAGNOSTIC_SEVERITIES:
            raise ValueError("severity must be info or warning")


@dataclass(frozen=True)
class AcceptanceRecord:
    acceptance_record_id: str
    contract_version: str
    evidence_id: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str
    accepted_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str
    evidence_identity_policy_id: str
    evidence_identity_policy_version: str
    materializer_id: str
    materializer_version: str
    diagnostics: tuple[AcceptanceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_RECORD_ID_PATTERN,
        )
        _require_pattern(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )

        for field_name in (
            "contract_version",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "acceptance_policy_id",
            "acceptance_policy_version",
            "evidence_identity_policy_id",
            "evidence_identity_policy_version",
            "materializer_id",
            "materializer_version",
        ):
            _require_non_empty_string(
                getattr(self, field_name),
                field_name,
            )

        _require_timezone_aware_datetime(
            self.accepted_at,
            "accepted_at",
        )

        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")

        for index, diagnostic in enumerate(self.diagnostics):
            if type(diagnostic) is not AcceptanceDiagnostic:
                raise ValueError(
                    "diagnostics"
                    f"[{index}] must be an exact AcceptanceDiagnostic"
                )
