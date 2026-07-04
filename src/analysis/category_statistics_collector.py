from src.evidence.evidence import Evidence

from .category_statistics import CategoryStatistics
from .category_statistics_collection import (
    CategoryStatisticsCollection,
)


class CategoryStatisticsCollector:

    @staticmethod
    def collect(
        evidences: list[Evidence],
    ) -> CategoryStatisticsCollection:

        counts: dict[str, int] = {}

        for evidence in evidences:

            category = evidence.metadata.category

            counts[category] = (
                counts.get(category, 0) + 1
            )

        statistics = [
            CategoryStatistics(
                category=category,
                total_assets=total_assets,
            )
            for category, total_assets
            in counts.items()
        ]

        return CategoryStatisticsCollection(
            categories=statistics,
        )