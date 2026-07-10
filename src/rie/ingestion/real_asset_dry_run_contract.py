from dataclasses import dataclass
from pathlib import Path

from rie.ingestion.real_asset_sandbox_policy import RealAssetSandboxDecision


@dataclass(frozen=True)
class RealAssetDryRunResult:
    allowed: bool
    reason: str
    sandbox_allowed: bool
    sandbox_reason: str
    root: Path | None
    recursive: bool
    read_only: bool
    allow_real_asset_reads: bool
    allow_mutation: bool
    mode: str
    planned_scan_allowed: bool
    planned_real_asset_reads_allowed: bool
    planned_mutation_allowed: bool
    item_count: int


class RealAssetDryRunContract:
    METADATA_ONLY = "metadata_only"
    HEADER_ONLY = "header_only"
    EXTRACTION_PREVIEW = "extraction_preview"

    @staticmethod
    def evaluate(
        sandbox_decision: RealAssetSandboxDecision,
        mode: str = METADATA_ONLY,
        planned_scan_allowed: bool = False,
        planned_real_asset_reads_allowed: bool = False,
        planned_mutation_allowed: bool = False,
    ) -> RealAssetDryRunResult:
        allowed = False

        if sandbox_decision.allowed is False:
            reason = "Sandbox policy blocked dry-run contract."
        elif mode == RealAssetDryRunContract.HEADER_ONLY:
            reason = "Header-only mode is not approved in PR-016D."
        elif mode == RealAssetDryRunContract.EXTRACTION_PREVIEW:
            reason = "Extraction preview mode is not approved in PR-016D."
        elif mode != RealAssetDryRunContract.METADATA_ONLY:
            reason = "Unsupported dry-run mode."
        elif planned_scan_allowed is True:
            reason = "Scan execution is not approved in PR-016D."
        elif planned_real_asset_reads_allowed is True:
            reason = "Real asset reads are not approved in PR-016D."
        elif planned_mutation_allowed is True:
            reason = "Dry-run mutation is forbidden."
        else:
            allowed = True
            reason = "Real asset dry-run contract passed."

        return RealAssetDryRunResult(
            allowed=allowed,
            reason=reason,
            sandbox_allowed=sandbox_decision.allowed,
            sandbox_reason=sandbox_decision.reason,
            root=sandbox_decision.root,
            recursive=sandbox_decision.recursive,
            read_only=sandbox_decision.read_only,
            allow_real_asset_reads=sandbox_decision.allow_real_asset_reads,
            allow_mutation=sandbox_decision.allow_mutation,
            mode=mode,
            planned_scan_allowed=planned_scan_allowed,
            planned_real_asset_reads_allowed=planned_real_asset_reads_allowed,
            planned_mutation_allowed=planned_mutation_allowed,
            item_count=0,
        )
