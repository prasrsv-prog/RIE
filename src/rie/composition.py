from repository_explorer import create_repository_explorer

from rie.core.engine import Engine
from rie.infrastructure.repository_explorer_batch_discovery import (
    RepositoryExplorerBatchDiscovery,
)


def create_repository_explorer_engine() -> Engine:
    return Engine(
        discovery=RepositoryExplorerBatchDiscovery(
            explorer=create_repository_explorer(),
        )
    )
