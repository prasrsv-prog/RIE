from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryStatistics:
    total_assets: int
    small_assets: int
    medium_assets: int
    large_assets: int