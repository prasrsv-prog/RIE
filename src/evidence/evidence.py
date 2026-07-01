from dataclasses import dataclass
from pathlib import Path

from src.analysis.asset_analysis import AssetAnalysis


@dataclass(frozen=True)
class Evidence:
    asset_path: Path

    filename: str

    analysis: AssetAnalysis