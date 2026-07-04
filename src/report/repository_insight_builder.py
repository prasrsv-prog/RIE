from src.analysis.category_statistics_collection import (
    CategoryStatisticsCollection,
)
from src.analysis.category_statistics_collector import (
    CategoryStatisticsCollector,
)
from src.analysis.repository_statistics import RepositoryStatistics
from src.evidence.evidence import Evidence

from src.report.repository_insight import RepositoryInsight


class RepositoryInsightBuilder:

    @staticmethod
    def build(
        evidences: list[Evidence],
        statistics: RepositoryStatistics,
    ) -> RepositoryInsight:

        category_statistics = (
            CategoryStatisticsCollector.collect(
                evidences
            )
        )

        largest_category = (
            RepositoryInsightBuilder._largest_category(
                category_statistics
            )
        )

        repository_health = (
            RepositoryInsightBuilder._repository_health(
                statistics
            )
        )

        return RepositoryInsight(
            largest_category=largest_category,
            repository_health=repository_health,
        )

    @staticmethod
    def _largest_category(
        category_statistics: CategoryStatisticsCollection,
    ) -> str:

        largest = max(
            category_statistics.categories,
            key=lambda item: item.total_assets,
        )

        return largest.category

    @staticmethod
    def _repository_health(
        statistics: RepositoryStatistics,
    ) -> str:

        counts = {
            "Lightweight": statistics.small_assets,
            "Balanced": statistics.medium_assets,
            "Heavy": statistics.large_assets,
        }

        return max(
            counts,
            key=counts.get,
        )