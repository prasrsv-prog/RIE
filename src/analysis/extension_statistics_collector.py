from src.evidence.evidence import Evidence

from .extension_statistics import ExtensionStatistics
from .extension_statistics_collection import (
    ExtensionStatisticsCollection,
)


class ExtensionStatisticsCollector:

    @staticmethod
    def collect(
        evidences: list[Evidence],
    ) -> ExtensionStatisticsCollection:

        counts: dict[str, int] = {}

        for evidence in evidences:

            extension = evidence.metadata.extension

            counts[extension] = (
                counts.get(extension, 0) + 1
            )

        statistics = [
            ExtensionStatistics(
                extension=extension,
                total_assets=total_assets,
            )
            for extension, total_assets
            in counts.items()
        ]

        return ExtensionStatisticsCollection(
            extensions=statistics,
        )