from .asset_analysis import AssetAnalysis
from .repository_statistics import RepositoryStatistics
from .size_class import SizeClass


class StatisticsCollector:

    @staticmethod
    def collect(
        analyses: list[AssetAnalysis]
    ) -> RepositoryStatistics:
        
        total_assets = len(analyses)
        small_assets = sum(
            analysis.size_class == SizeClass.SMALL
            for analysis in analyses
        )

        medium_assets = sum(
            analysis.size_class == SizeClass.MEDIUM
            for analysis in analyses
        )

        large_assets = sum(
            analysis.size_class == SizeClass.LARGE
            for analysis in analyses
        )

        return RepositoryStatistics(
            total_assets=total_assets,
            small_assets=small_assets,
            medium_assets=medium_assets,
            large_assets=large_assets
        )