from __future__ import annotations

from rie.domain.governed_asset_library_registry import (
    GovernedAssetLibraryRegistry,
)
from rie.domain.governed_asset_use_eligibility import (
    GovernedAssetUseEligibilityDecision,
)


def evaluate_governed_asset_library_use_eligibility(
    registry: GovernedAssetLibraryRegistry,
    asset_record_id: str,
    requested_use_scope: str,
    decision_context_reference: str,
) -> GovernedAssetUseEligibilityDecision:
    """Resolve exact governed records and construct one immutable decision."""

    if not isinstance(registry, GovernedAssetLibraryRegistry):
        raise TypeError("registry must be a GovernedAssetLibraryRegistry")

    asset_record = registry.get_asset_record(asset_record_id)
    usage_rights_record = registry.resolve_usage_rights(asset_record)

    return GovernedAssetUseEligibilityDecision(
        asset_record=asset_record,
        usage_rights_record=usage_rights_record,
        requested_use_scope=requested_use_scope,
        asset_record_reference=asset_record.asset_record_id,
        usage_rights_record_reference=usage_rights_record.rights_record_id,
        decision_context_reference=decision_context_reference,
    )
