from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

VALIDITY_STATE_UNVERIFIED: Final = "UNVERIFIED"
VALIDITY_STATE_ACTIVE: Final = "ACTIVE"
VALIDITY_STATE_EXPIRED: Final = "EXPIRED"
VALIDITY_STATE_REVOKED: Final = "REVOKED"

USE_AUTHORIZATION_AUTHORIZED: Final = "AUTHORIZED"
USE_AUTHORIZATION_NOT_AUTHORIZED: Final = "NOT_AUTHORIZED"

ValidityState: TypeAlias = Literal[
    "UNVERIFIED",
    "ACTIVE",
    "EXPIRED",
    "REVOKED",
]
UseAuthorization: TypeAlias = Literal[
    "AUTHORIZED",
    "NOT_AUTHORIZED",
]

ALLOWED_VALIDITY_STATES: Final = frozenset(
    {
        VALIDITY_STATE_UNVERIFIED,
        VALIDITY_STATE_ACTIVE,
        VALIDITY_STATE_EXPIRED,
        VALIDITY_STATE_REVOKED,
    }
)
ALLOWED_USE_AUTHORIZATION_DECISIONS: Final = frozenset(
    {
        USE_AUTHORIZATION_AUTHORIZED,
        USE_AUTHORIZATION_NOT_AUTHORIZED,
    }
)

_REQUIRED_TEXT_FIELDS: Final = (
    "rights_record_id",
    "rights_holder_reference",
    "permitted_use_scope",
    "restriction_scope",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")


@dataclass(frozen=True)
class GovernedAssetUsageRights:
    """Minimum immutable Gate 15 governed asset usage-rights record."""

    rights_record_id: str
    rights_holder_reference: str
    permitted_use_scope: str
    restriction_scope: str
    validity_state: ValidityState
    use_authorization: UseAuthorization

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_required_ascii_text(field_name, getattr(self, field_name))

        if self.validity_state not in ALLOWED_VALIDITY_STATES:
            raise ValueError(
                "validity_state must be one of "
                "UNVERIFIED, ACTIVE, EXPIRED, or REVOKED"
            )

        if self.use_authorization not in ALLOWED_USE_AUTHORIZATION_DECISIONS:
            raise ValueError(
                "use_authorization must be AUTHORIZED or NOT_AUTHORIZED"
            )

        if (
            self.use_authorization == USE_AUTHORIZATION_AUTHORIZED
            and self.validity_state != VALIDITY_STATE_ACTIVE
        ):
            raise ValueError(
                "AUTHORIZED is valid only when validity_state is ACTIVE"
            )
