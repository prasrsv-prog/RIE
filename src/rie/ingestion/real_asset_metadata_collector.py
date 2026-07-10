from dataclasses import dataclass

from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionDecision,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)


@dataclass(frozen=True)
class RealAssetMetadataCollectionRequest:
    decision: RealAssetMetadataCollectionDecision
    items: tuple[RealAssetMetadataDryRunItem, ...] = ()


@dataclass(frozen=True)
class RealAssetMetadataCollectionResult:
    allowed: bool
    reason: str
    item_count: int
    items: tuple[RealAssetMetadataDryRunItem, ...]
    decision_allowed: bool
    decision_reason: str


class RealAssetMetadataCollector:

    @staticmethod
    def collect(
        request: RealAssetMetadataCollectionRequest,
    ) -> RealAssetMetadataCollectionResult:
        if request.decision.allowed is False:
            return RealAssetMetadataCollectionResult(
                allowed=False,
                reason="Metadata collection contract blocked collector.",
                item_count=0,
                items=(),
                decision_allowed=request.decision.allowed,
                decision_reason=request.decision.reason,
            )

        return RealAssetMetadataCollectionResult(
            allowed=True,
            reason=(
                "Real asset metadata collector skeleton passed supplied "
                "metadata items only."
            ),
            item_count=len(request.items),
            items=request.items,
            decision_allowed=request.decision.allowed,
            decision_reason=request.decision.reason,
        )
