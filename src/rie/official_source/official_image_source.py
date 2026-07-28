"""Gate 12 Official Image Source record model.

This module implements deterministic construction validation only.
Persistence, registry integration, parser integration, CLI behavior,
real-asset execution, Gate 13 behavior, and semantic interpretation are
intentionally outside this boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Final


_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


class SourceKind(str, Enum):
    FILE = "FILE"
    REPOSITORY_ASSET = "REPOSITORY_ASSET"
    CONTROLLED_EXTERNAL_REFERENCE = "CONTROLLED_EXTERNAL_REFERENCE"


class AuthorityClass(str, Enum):
    OFFICIAL_INTERNAL = "OFFICIAL_INTERNAL"
    OFFICIAL_PARTNER = "OFFICIAL_PARTNER"
    CONTROLLED_EXTERNAL = "CONTROLLED_EXTERNAL"


class RightsStatus(str, Enum):
    OWNED = "OWNED"
    LICENSED = "LICENSED"
    APPROVED_INTERNAL_USE = "APPROVED_INTERNAL_USE"
    RESTRICTED = "RESTRICTED"


class LifecycleState(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


class AdmissionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class OfficialImageSource:
    """Immutable Gate 12 source record with deterministic construction checks."""

    source_id: str
    source_locator: str
    source_kind: SourceKind
    content_sha256: str
    byte_length: int
    authority_class: AuthorityClass
    rights_status: RightsStatus
    lifecycle_state: LifecycleState
    admission_status: AdmissionStatus
    provenance_parent_id: str | None
    registered_at_utc: datetime
    registered_by: str

    def __post_init__(self) -> None:
        _require_clean_nonempty_text("source_id", self.source_id)
        _require_clean_nonempty_text("source_locator", self.source_locator)
        _require_enum("source_kind", self.source_kind, SourceKind)
        _require_sha256(self.content_sha256)
        _require_positive_byte_length(self.byte_length)
        _require_enum("authority_class", self.authority_class, AuthorityClass)
        _require_enum("rights_status", self.rights_status, RightsStatus)
        _require_enum("lifecycle_state", self.lifecycle_state, LifecycleState)
        _require_enum("admission_status", self.admission_status, AdmissionStatus)
        _require_optional_parent_id(self.source_id, self.provenance_parent_id)
        _require_normalized_utc(self.registered_at_utc)
        _require_clean_nonempty_text("registered_by", self.registered_by)
        _require_state_admission_consistency(
            self.lifecycle_state,
            self.admission_status,
            self.provenance_parent_id,
        )

    @classmethod
    def required_field_names(cls) -> tuple[str, ...]:
        """Return the canonical twelve-field record order."""

        return tuple(field.name for field in fields(cls))


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


def _require_sha256(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError("content_sha256 must be a string")
    if _SHA256_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "content_sha256 must be exactly 64 lowercase hexadecimal characters"
        )


def _require_positive_byte_length(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("byte_length must be an integer")
    if value <= 0:
        raise ValueError("byte_length must be positive")


def _require_optional_parent_id(
    source_id: str,
    provenance_parent_id: object,
) -> None:
    if provenance_parent_id is None:
        return
    _require_clean_nonempty_text("provenance_parent_id", provenance_parent_id)
    if provenance_parent_id == source_id:
        raise ValueError("provenance_parent_id must differ from source_id")


def _require_normalized_utc(value: object) -> None:
    if not isinstance(value, datetime):
        raise TypeError("registered_at_utc must be a datetime")
    if value.tzinfo is not timezone.utc:
        raise ValueError("registered_at_utc must use datetime.timezone.utc")


def _require_state_admission_consistency(
    lifecycle_state: LifecycleState,
    admission_status: AdmissionStatus,
    provenance_parent_id: str | None,
) -> None:
    if lifecycle_state in {LifecycleState.ACTIVE, LifecycleState.SUPERSEDED}:
        if admission_status is not AdmissionStatus.ACCEPTED:
            raise ValueError(
                f"{lifecycle_state.value} requires admission_status ACCEPTED"
            )
    if (
        lifecycle_state is LifecycleState.SUPERSEDED
        and provenance_parent_id is None
    ):
        raise ValueError("SUPERSEDED requires provenance_parent_id")
