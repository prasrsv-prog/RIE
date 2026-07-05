from src.analysis.category_statistics_collection import (
    CategoryStatisticsCollection,
)
from src.analysis.category_statistics_collector import (
    CategoryStatisticsCollector,
)
from src.analysis.extension_statistics_collection import (
    ExtensionStatisticsCollection,
)
from src.analysis.extension_statistics_collector import (
    ExtensionStatisticsCollector,
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

        extension_statistics = (
            ExtensionStatisticsCollector.collect(
                evidences
            )
        )

        largest_category = (
            RepositoryInsightBuilder._largest_category(
                category_statistics
            )
        )

        most_common_extension = (
            RepositoryInsightBuilder._most_common_extension(
                extension_statistics
            )
        )

        repository_health = (
            RepositoryInsightBuilder._repository_health(
                statistics
            )
        )

        return RepositoryInsight(
            largest_category=largest_category,
            most_common_extension=most_common_extension,
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
    def _most_common_extension(
        extension_statistics: ExtensionStatisticsCollection,
    ) -> str:

        largest = max(
            extension_statistics.extensions,
            key=lambda item: item.total_assets,
        )

        return largest.extension

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