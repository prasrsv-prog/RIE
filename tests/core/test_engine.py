from pathlib import Path

from rie.application.batch import Batch
from rie.application.discovery_service import DiscoveryService
from rie.core.engine import Engine
from rie.interfaces.batch_discovery import BatchDiscovery


class FakeBatchDiscovery(BatchDiscovery):

    def discover(self, root: Path) -> Batch:
        return Batch(
            name=root.name,
            root=root,
            assets=[],
        )


def test_engine_uses_injected_discovery():
    discovery = FakeBatchDiscovery()

    engine = Engine(discovery=discovery)

    assert engine.pipeline.discovery is discovery


def test_engine_uses_discovery_service_by_default():
    engine = Engine()

    assert isinstance(engine.pipeline.discovery, DiscoveryService)
