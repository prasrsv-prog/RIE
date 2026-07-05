from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryInsight:
    largest_category: str
    most_common_extension: str
    repository_health: str
    most_common_extension: str