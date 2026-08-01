from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

LIFECYCLE_STATE_CANDIDATE: Final = "CANDIDATE"
LIFECYCLE_STATE_ACTIVE: Final = "ACTIVE"
LIFECYCLE_STATE_DEPRECATED: Final = "DEPRECATED"
LIFECYCLE_STATE_SUPERSEDED: Final = "SUPERSEDED"

USE_ELIGIBILITY_ELIGIBLE: Final = "ELIGIBLE"
USE_ELIGIBILITY_INELIGIBLE: Final = "INELIGIBLE"

LifecycleState: TypeAlias = Literal[
    "CANDIDATE",
    "ACTIVE",
    "DEPRECATED",
    "SUPERSEDED",
]
UseEligibility: TypeAlias = Literal["ELIGIBLE", "INELIGIBLE"]

ALLOWED_LIFECYCLE_STATES: Final = frozenset(
    {
        LIFECYCLE_STATE_CANDIDATE,
        LIFECYCLE_STATE_ACTIVE,
        LIFECYCLE_STATE_DEPRECATED,
        LIFECYCLE_STATE_SUPERSEDED,
    }
)
ALLOWED_USE_ELIGIBILITY_STATES: Final = frozenset(
    {
        USE_ELIGIBILITY_ELIGIBLE,
        USE_ELIGIBILITY_INELIGIBLE,
    }
)

_REQUIRED_TEXT_FIELDS: Final = (
    "asset_record_id",
    "provenance_reference",
    "usage_rights_reference",
    "version_identity",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")


@dataclass(frozen=True)
class GovernedAssetRecord:
    """Minimum immutable Gate 15 governed asset record."""

    asset_record_id: str
    provenance_reference: str
    usage_rights_reference: str
    version_identity: str
    lifecycle_state: LifecycleState
    use_eligibility: UseEligibility

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_required_ascii_text(field_name, getattr(self, field_name))

        if self.asset_record_id == self.version_identity:
            raise ValueError(
                "version_identity must be distinct from asset_record_id"
            )

        if self.lifecycle_state not in ALLOWED_LIFECYCLE_STATES:
            raise ValueError(
                "lifecycle_state must be one of "
                "CANDIDATE, ACTIVE, DEPRECATED, or SUPERSEDED"
            )

        if self.use_eligibility not in ALLOWED_USE_ELIGIBILITY_STATES:
            raise ValueError(
                "use_eligibility must be ELIGIBLE or INELIGIBLE"
            )

        if (
            self.use_eligibility == USE_ELIGIBILITY_ELIGIBLE
            and self.lifecycle_state != LIFECYCLE_STATE_ACTIVE
        ):
            raise ValueError(
                "ELIGIBLE is valid only when lifecycle_state is ACTIVE"
            )
