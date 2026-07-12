"""Deterministic standalone acceptance-record identity contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata

from rie.domain.acceptance_record import AcceptanceRecord


ACCEPTANCE_IDENTITY_POLICY_ID = "rcis-acceptance-record-identity"
ACCEPTANCE_IDENTITY_POLICY_VERSION = "1.0.0"
ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION = (
    "acceptance-json-v1"
)
ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM = "sha256"
ACCEPTANCE_RECORD_ID_PREFIX = "ar1_"

_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


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
class AcceptanceIdentityInput:
    acceptance_record_contract_version: str
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

    def __post_init__(self) -> None:
        _require_pattern(
            self.evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )

        for field_name in (
            "acceptance_record_contract_version",
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


@dataclass(frozen=True)
class AcceptanceIdentityResult:
    acceptance_record_id: str
    digest_algorithm: str
    digest_hex: str
    identity_policy_id: str
    identity_policy_version: str
    canonicalization_contract_version: str
    canonical_byte_length: int

    def __post_init__(self) -> None:
        _require_pattern(
            self.acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_RECORD_ID_PATTERN,
        )
        _require_pattern(
            self.digest_hex,
            "digest_hex",
            _DIGEST_PATTERN,
        )

        expected_record_id = (
            f"{ACCEPTANCE_RECORD_ID_PREFIX}{self.digest_hex}"
        )
        if self.acceptance_record_id != expected_record_id:
            raise ValueError(
                "acceptance_record_id must match digest_hex"
            )

        if self.digest_algorithm != ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM:
            raise ValueError("digest_algorithm must be sha256")
        if self.identity_policy_id != ACCEPTANCE_IDENTITY_POLICY_ID:
            raise ValueError("identity_policy_id mismatch")
        if (
            self.identity_policy_version
            != ACCEPTANCE_IDENTITY_POLICY_VERSION
        ):
            raise ValueError("identity_policy_version mismatch")
        if (
            self.canonicalization_contract_version
            != ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
        ):
            raise ValueError(
                "canonicalization_contract_version mismatch"
            )

        if (
            type(self.canonical_byte_length) is not int
            or self.canonical_byte_length <= 0
        ):
            raise ValueError(
                "canonical_byte_length must be a positive integer"
            )


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_accepted_at(value: datetime) -> str:
    _require_timezone_aware_datetime(value, "accepted_at")
    utc_value = value.astimezone(timezone.utc)
    return utc_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _canonical_acceptance_identity_mapping(
    identity_input: AcceptanceIdentityInput,
) -> dict[str, str]:
    if type(identity_input) is not AcceptanceIdentityInput:
        raise ValueError(
            "identity_input must be an exact AcceptanceIdentityInput"
        )

    return {
        "acceptance_record_contract_version": _normalize_text(
            identity_input.acceptance_record_contract_version
        ),
        "evidence_id": _normalize_text(identity_input.evidence_id),
        "accepted_by": _normalize_text(identity_input.accepted_by),
        "acceptance_reason": _normalize_text(
            identity_input.acceptance_reason
        ),
        "review_record_id": _normalize_text(
            identity_input.review_record_id
        ),
        "accepted_at": _format_accepted_at(identity_input.accepted_at),
        "acceptance_policy_id": _normalize_text(
            identity_input.acceptance_policy_id
        ),
        "acceptance_policy_version": _normalize_text(
            identity_input.acceptance_policy_version
        ),
        "evidence_identity_policy_id": _normalize_text(
            identity_input.evidence_identity_policy_id
        ),
        "evidence_identity_policy_version": _normalize_text(
            identity_input.evidence_identity_policy_version
        ),
        "materializer_id": _normalize_text(
            identity_input.materializer_id
        ),
        "materializer_version": _normalize_text(
            identity_input.materializer_version
        ),
    }


def _canonical_acceptance_identity_bytes(
    identity_input: AcceptanceIdentityInput,
) -> bytes:
    mapping = _canonical_acceptance_identity_mapping(identity_input)
    serialized = json.dumps(
        mapping,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return serialized.encode("utf-8")


def calculate_acceptance_identity(
    identity_input: AcceptanceIdentityInput,
) -> AcceptanceIdentityResult:
    canonical_bytes = _canonical_acceptance_identity_bytes(
        identity_input
    )
    digest_hex = hashlib.sha256(canonical_bytes).hexdigest()

    return AcceptanceIdentityResult(
        acceptance_record_id=(
            f"{ACCEPTANCE_RECORD_ID_PREFIX}{digest_hex}"
        ),
        digest_algorithm=ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM,
        digest_hex=digest_hex,
        identity_policy_id=ACCEPTANCE_IDENTITY_POLICY_ID,
        identity_policy_version=ACCEPTANCE_IDENTITY_POLICY_VERSION,
        canonicalization_contract_version=(
            ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
        ),
        canonical_byte_length=len(canonical_bytes),
    )


def acceptance_identity_input_from_record(
    record: AcceptanceRecord,
) -> AcceptanceIdentityInput:
    if type(record) is not AcceptanceRecord:
        raise ValueError("record must be an exact AcceptanceRecord")

    return AcceptanceIdentityInput(
        acceptance_record_contract_version=record.contract_version,
        evidence_id=record.evidence_id,
        accepted_by=record.accepted_by,
        acceptance_reason=record.acceptance_reason,
        review_record_id=record.review_record_id,
        accepted_at=record.accepted_at,
        acceptance_policy_id=record.acceptance_policy_id,
        acceptance_policy_version=record.acceptance_policy_version,
        evidence_identity_policy_id=(
            record.evidence_identity_policy_id
        ),
        evidence_identity_policy_version=(
            record.evidence_identity_policy_version
        ),
        materializer_id=record.materializer_id,
        materializer_version=record.materializer_version,
    )
