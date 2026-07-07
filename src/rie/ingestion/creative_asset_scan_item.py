from dataclasses import dataclass
from pathlib import Path

from rie.ingestion.creative_asset_type import CreativeAssetType


@dataclass(frozen=True)
class CreativeAssetScanItem:
    path: Path
    asset_type: CreativeAssetType
    size: int
    error: str | None = None
