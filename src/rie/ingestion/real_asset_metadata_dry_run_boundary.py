from dataclasses import dataclass

from rie.ingestion.real_asset_dry_run_contract import RealAssetDryRunResult


@dataclass(frozen=True)
class RealAssetMetadataDryRunItem:
    path: str
    relative_path: str
    exists: bool
    is_file: bool
    size: int
    suffix: str
    error: str | None


@dataclass(frozen=True)
class RealAssetMetadataDryRunBoundaryResult:
    allowed: bool
    reason: str
    dry_run_allowed: bool
    dry_run_reason: str
    mode: str
    item_count: int
    items: tuple[RealAssetMetadataDryRunItem, ...]


class RealAssetMetadataDryRunBoundary:
    METADATA_ONLY = "metadata_only"

    @staticmethod
    def evaluate(
        dry_run_result: RealAssetDryRunResult,
        items: tuple[RealAssetMetadataDryRunItem, ...] = (),
    ) -> RealAssetMetadataDryRunBoundaryResult:
        allowed = False

        if dry_run_result.allowed is False:
            reason = "Dry-run contract blocked metadata boundary."
        elif dry_run_result.mode != RealAssetMetadataDryRunBoundary.METADATA_ONLY:
            reason = "Only metadata_only mode is approved for metadata boundary."
        elif any(item.size < 0 for item in items):
            reason = "Metadata item negative size is invalid."
        elif any(not item.path for item in items):
            reason = "Metadata item path is required."
        elif any(not item.relative_path for item in items):
            reason = "Metadata item relative_path is required."
        else:
            allowed = True
            reason = "Real asset metadata-only boundary passed."

        return RealAssetMetadataDryRunBoundaryResult(
            allowed=allowed,
            reason=reason,
            dry_run_allowed=dry_run_result.allowed,
            dry_run_reason=dry_run_result.reason,
            mode=dry_run_result.mode,
            item_count=len(items),
            items=items,
        )
