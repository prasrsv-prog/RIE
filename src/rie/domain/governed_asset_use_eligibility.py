from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from rie.domain.governed_asset_record import (
    LIFECYCLE_STATE_ACTIVE,
    USE_ELIGIBILITY_ELIGIBLE,
    GovernedAssetRecord,
)
from rie.domain.governed_asset_usage_rights import (
    USE_AUTHORIZATION_AUTHORIZED,
    VALIDITY_STATE_ACTIVE,
    GovernedAssetUsageRights,
)

DECISION_ELIGIBLE: Final = "ELIGIBLE"
DECISION_INELIGIBLE: Final = "INELIGIBLE"

DecisionValue: TypeAlias = Literal["ELIGIBLE", "INELIGIBLE"]

ALLOWED_DECISION_VALUES: Final = frozenset(
    {
        DECISION_ELIGIBLE,
        DECISION_INELIGIBLE,
    }
)

_REQUIRED_TEXT_FIELDS: Final = (
    "requested_use_scope",
    "asset_record_reference",
    "usage_rights_record_reference",
    "decision_context_reference",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")


@dataclass(frozen=True)
class GovernedAssetUseEligibilityDecision:
    """Minimum immutable Gate 15 use-eligibility decision."""

    asset_record: GovernedAssetRecord
    usage_rights_record: GovernedAssetUsageRights
    requested_use_scope: str
    asset_record_reference: str
    usage_rights_record_reference: str
    decision_context_reference: str

    def __post_init__(self) -> None:
        if not isinstance(self.asset_record, GovernedAssetRecord):
            raise TypeError("asset_record must be a GovernedAssetRecord")
        if not isinstance(
            self.usage_rights_record,
            GovernedAssetUsageRights,
        ):
            raise TypeError(
                "usage_rights_record must be a GovernedAssetUsageRights"
            )

        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_required_ascii_text(field_name, getattr(self, field_name))

    @property
    def decision_value(self) -> DecisionValue:
        if self.asset_record_reference != self.asset_record.asset_record_id:
            return DECISION_INELIGIBLE

        if (
            self.usage_rights_record_reference
            != self.usage_rights_record.rights_record_id
        ):
            return DECISION_INELIGIBLE

        if (
            self.asset_record.usage_rights_reference
            != self.usage_rights_record_reference
        ):
            return DECISION_INELIGIBLE

        if self.asset_record.lifecycle_state != LIFECYCLE_STATE_ACTIVE:
            return DECISION_INELIGIBLE

        if (
            self.asset_record.use_eligibility
            != USE_ELIGIBILITY_ELIGIBLE
        ):
            return DECISION_INELIGIBLE

        if (
            self.usage_rights_record.validity_state
            != VALIDITY_STATE_ACTIVE
        ):
            return DECISION_INELIGIBLE

        if (
            self.usage_rights_record.use_authorization
            != USE_AUTHORIZATION_AUTHORIZED
        ):
            return DECISION_INELIGIBLE

        if (
            self.requested_use_scope
            != self.usage_rights_record.permitted_use_scope
        ):
            return DECISION_INELIGIBLE

        if (
            self.requested_use_scope
            == self.usage_rights_record.restriction_scope
        ):
            return DECISION_INELIGIBLE

        return DECISION_ELIGIBLE
