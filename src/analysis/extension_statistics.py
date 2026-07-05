from dataclasses import dataclass


@dataclass(frozen=True)
class ExtensionStatistics:
    extension: str
    total_assets: int