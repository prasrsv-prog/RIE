from rie.composition import create_repository_explorer_engine
from rie.core.engine import Engine
from rie.infrastructure.repository_explorer_batch_discovery import (
    RepositoryExplorerBatchDiscovery,
)


def test_create_repository_explorer_engine_wires_repository_explorer_discovery():
    engine = create_repository_explorer_engine()

    assert isinstance(engine, Engine)
    assert isinstance(engine.pipeline.discovery, RepositoryExplorerBatchDiscovery)
    assert engine.pipeline.discovery.explorer is not None
