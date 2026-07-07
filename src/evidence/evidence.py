from dataclasses import dataclass
from pathlib import Path

from rie.application.metadata import Metadata
from analysis.asset_analysis import AssetAnalysis


@dataclass(frozen=True)
class Evidence:
    asset_path: Path
    filename: str
    metadata: Metadata
    analysis: AssetAnalysis