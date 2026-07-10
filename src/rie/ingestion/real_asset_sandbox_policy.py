from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RealAssetSandboxDecision:
    allowed: bool
    reason: str
    root: Path | None
    recursive: bool
    read_only: bool
    allow_real_asset_reads: bool
    allow_mutation: bool


class RealAssetSandboxPolicy:

    @staticmethod
    def evaluate(
        root: Path | None,
        recursive: bool = False,
        read_only: bool = True,
        allow_real_asset_reads: bool = False,
        allow_mutation: bool = False,
    ) -> RealAssetSandboxDecision:
        allowed = False

        if root is None:
            reason = "Explicit sandbox root is required."
        elif read_only is False:
            reason = "Real asset sandbox must be read-only."
        elif allow_mutation is True:
            reason = "Real asset sandbox mutation is forbidden."
        elif allow_real_asset_reads is True:
            reason = "Real asset reads are not approved in PR-016B."
        elif recursive is True:
            reason = "Recursive sandbox scan is not approved in PR-016B."
        else:
            allowed = True
            reason = "Real asset sandbox policy passed."

        return RealAssetSandboxDecision(
            allowed=allowed,
            reason=reason,
            root=root,
            recursive=recursive,
            read_only=read_only,
            allow_real_asset_reads=allow_real_asset_reads,
            allow_mutation=allow_mutation,
        )
