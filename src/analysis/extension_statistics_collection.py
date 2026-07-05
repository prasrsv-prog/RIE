from dataclasses import dataclass

from .extension_statistics import ExtensionStatistics


@dataclass(frozen=True)
class ExtensionStatisticsCollection:
    extensions: list[ExtensionStatistics]