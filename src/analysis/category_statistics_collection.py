from dataclasses import dataclass

from .category_statistics import CategoryStatistics


@dataclass(frozen=True)
class CategoryStatisticsCollection:
    categories: list[CategoryStatistics]