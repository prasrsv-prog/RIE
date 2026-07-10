from dataclasses import dataclass
from pathlib import Path

from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)


@dataclass(frozen=True)
class RealFilesystemMetadataAdapterRequest:
    root: Path
    max_items: int = 100


@dataclass(frozen=True)
class RealFilesystemMetadataAdapterResult:
    allowed: bool
    reason: str
    root: str
    item_count: int
    items: tuple[RealAssetMetadataDryRunItem, ...]


class RealFilesystemMetadataAdapter:

    @staticmethod
    def collect(
        request: RealFilesystemMetadataAdapterRequest,
    ) -> RealFilesystemMetadataAdapterResult:
        root = request.root

        if request.max_items <= 0:
            return RealFilesystemMetadataAdapterResult(
                allowed=False,
                reason="Positive max_items is required.",
                root=str(root),
                item_count=0,
                items=(),
            )

        if not root.exists():
            return RealFilesystemMetadataAdapterResult(
                allowed=False,
                reason="Explicit root does not exist.",
                root=str(root),
                item_count=0,
                items=(),
            )

        if root.is_file():
            return RealFilesystemMetadataAdapterResult(
                allowed=False,
                reason="Explicit root must be a directory.",
                root=str(root),
                item_count=0,
                items=(),
            )

        try:
            children = tuple(root.iterdir())
        except OSError as exc:
            return RealFilesystemMetadataAdapterResult(
                allowed=False,
                reason=f"Explicit root must be a directory: {exc}",
                root=str(root),
                item_count=0,
                items=(),
            )

        items = tuple(
            RealFilesystemMetadataAdapter._collect_child_metadata(child)
            for child in children[:request.max_items]
        )

        return RealFilesystemMetadataAdapterResult(
            allowed=True,
            reason="Filesystem metadata adapter collected immediate children.",
            root=str(root),
            item_count=len(items),
            items=items,
        )

    @staticmethod
    def _collect_child_metadata(
        child: Path,
    ) -> RealAssetMetadataDryRunItem:
        try:
            is_file = child.is_file()
            size = child.stat().st_size if is_file else 0
            error = None
        except OSError as exc:
            is_file = False
            size = 0
            error = str(exc)

        return RealAssetMetadataDryRunItem(
            path=str(child),
            relative_path=child.name,
            exists=True,
            is_file=is_file,
            size=size,
            suffix=child.suffix,
            error=error,
        )
