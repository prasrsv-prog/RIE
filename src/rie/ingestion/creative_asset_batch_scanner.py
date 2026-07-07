from pathlib import Path

from rie.ingestion.creative_asset_scan_item import CreativeAssetScanItem
from rie.ingestion.creative_asset_scan_report import CreativeAssetScanReport
from rie.ingestion.creative_asset_type import CreativeAssetType
from rie.ingestion.creative_asset_type_detector import CreativeAssetTypeDetector


class CreativeAssetBatchScanner:

    def __init__(
        self,
        recursive: bool = False,
    ) -> None:
        self.recursive = recursive

    def scan(self, folder: Path) -> CreativeAssetScanReport:
        items: list[CreativeAssetScanItem] = []

        for path in self._iter_files(folder):
            items.append(
                self._scan_file(path)
            )

        return CreativeAssetScanReport(
            root=folder,
            items=items,
        )

    def _iter_files(self, folder: Path):
        paths = folder.rglob("*") if self.recursive else folder.iterdir()

        for path in paths:
            if path.is_file():
                yield path

    def _scan_file(self, path: Path) -> CreativeAssetScanItem:
        try:
            asset_type = CreativeAssetTypeDetector.detect(path)
            size = path.stat().st_size
            error = None
        except Exception as exc:
            asset_type = CreativeAssetType.UNKNOWN
            size = self._safe_size(path)
            error = str(exc)

        return CreativeAssetScanItem(
            path=path,
            asset_type=asset_type,
            size=size,
            error=error,
        )

    def _safe_size(self, path: Path) -> int:
        try:
            return path.stat().st_size
        except OSError:
            return 0
