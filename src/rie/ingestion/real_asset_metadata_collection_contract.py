from dataclasses import dataclass

from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundaryResult,
)


@dataclass(frozen=True)
class RealAssetMetadataCollectionDecision:
    allowed: bool
    reason: str
    boundary_allowed: bool
    boundary_reason: str
    mode: str
    allow_filesystem_metadata: bool
    allow_recursive_collection: bool
    allow_content_reads: bool
    allow_mutation: bool


class RealAssetMetadataCollectionContract:
    METADATA_ONLY = "metadata_only"

    @staticmethod
    def evaluate(
        boundary_result: RealAssetMetadataDryRunBoundaryResult,
        allow_filesystem_metadata: bool = False,
        allow_recursive_collection: bool = False,
        allow_content_reads: bool = False,
        allow_mutation: bool = False,
    ) -> RealAssetMetadataCollectionDecision:
        allowed = False

        if boundary_result.allowed is False:
            reason = (
                "Metadata dry-run boundary blocked collection contract."
            )
        elif boundary_result.mode != RealAssetMetadataCollectionContract.METADATA_ONLY:
            reason = "Only metadata_only mode is approved for collection contract."
        elif allow_filesystem_metadata is True:
            reason = (
                "Filesystem metadata collection is not approved in PR-016H."
            )
        elif allow_recursive_collection is True:
            reason = "Recursive collection is not approved in PR-016H."
        elif allow_content_reads is True:
            reason = "Content reads are forbidden."
        elif allow_mutation is True:
            reason = "Metadata collection mutation is forbidden."
        else:
            allowed = True
            reason = (
                "Real asset metadata collection contract passed as "
                "disabled skeleton-only."
            )

        return RealAssetMetadataCollectionDecision(
            allowed=allowed,
            reason=reason,
            boundary_allowed=boundary_result.allowed,
            boundary_reason=boundary_result.reason,
            mode=boundary_result.mode,
            allow_filesystem_metadata=allow_filesystem_metadata,
            allow_recursive_collection=allow_recursive_collection,
            allow_content_reads=allow_content_reads,
            allow_mutation=allow_mutation,
        )
