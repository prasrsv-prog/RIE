from evidence.evidence import Evidence

from .repository_statistics import RepositoryStatistics
from .size_class import SizeClass


class StatisticsCollector:

    @staticmethod
    def collect(
        evidences: list[Evidence],
    ) -> RepositoryStatistics:

        total_assets = len(evidences)

        small_assets = sum(
            evidence.analysis.size_class == SizeClass.SMALL
            for evidence in evidences
        )

        medium_assets = sum(
            evidence.analysis.size_class == SizeClass.MEDIUM
            for evidence in evidences
        )

        large_assets = sum(
            evidence.analysis.size_class == SizeClass.LARGE
            for evidence in evidences
        )

        return RepositoryStatistics(
            total_assets=total_assets,
            small_assets=small_assets,
            medium_assets=medium_assets,
            large_assets=large_assets,
        )