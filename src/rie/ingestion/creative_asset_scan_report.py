from dataclasses import dataclass
from pathlib import Path

from rie.ingestion.creative_asset_scan_item import CreativeAssetScanItem
from rie.ingestion.creative_asset_type import CreativeAssetType


@dataclass(frozen=True)
class CreativeAssetScanReport:
    root: Path
    items: list[CreativeAssetScanItem]

    @property
    def total_files(self) -> int:
        return len(self.items)

    def count_by_type(self, asset_type: CreativeAssetType) -> int:
        return sum(
            item.asset_type == asset_type
            for item in self.items
        )
