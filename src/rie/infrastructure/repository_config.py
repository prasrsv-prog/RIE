from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepositoryConfig:

    repository_root: Path = Path("repository")

    knowledge_root: Path = Path("knowledge")

    cache_root: Path = Path("cache")

    logs_root: Path = Path("logs")