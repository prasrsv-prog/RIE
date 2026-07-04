from src.analysis.repository_statistics import RepositoryStatistics
from src.evidence.evidence import Evidence

from src.report.repository_insight import RepositoryInsight


class RepositoryInsightBuilder:

    @staticmethod
    def build(
        evidences: list[Evidence],
        statistics: RepositoryStatistics,
    ) -> RepositoryInsight:

        largest_category = (
            RepositoryInsightBuilder._largest_category(
                evidences
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
        evidences: list[Evidence],
    ) -> str:

        categories: dict[str, int] = {}

        for evidence in evidences:
            category = evidence.metadata.category
            categories[category] = (
                categories.get(category, 0) + 1
            )

        return max(
            categories,
            key=categories.get,
        )

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