from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryInsight:
    largest_category: str
    repository_health: str