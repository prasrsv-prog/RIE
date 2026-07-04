from src.report.repository_insight import RepositoryInsight


class RepositoryInsightBuilder:

    @staticmethod
    def build() -> RepositoryInsight:

        return RepositoryInsight(
            largest_category="Image",
            repository_health="Healthy",
        )