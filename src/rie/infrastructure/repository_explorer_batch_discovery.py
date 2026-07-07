from pathlib import Path
from typing import Protocol

from repository_explorer import RepositoryExploration

from rie.application.asset import Asset
from rie.application.batch import Batch
from rie.application.metadata_extractor import MetadataExtractor
from rie.interfaces.batch_discovery import BatchDiscovery


class _RepositoryExplorerLike(Protocol):

    def explore(self, repository_path: Path) -> RepositoryExploration:
        ...


class RepositoryExplorerBatchDiscovery(BatchDiscovery):

    def __init__(
        self,
        explorer: _RepositoryExplorerLike,
        extractor: MetadataExtractor | None = None,
    ) -> None:
        self.explorer = explorer
        self.extractor = extractor or MetadataExtractor()

    def discover(self, root: Path) -> Batch:

        exploration = self.explorer.explore(root)
        assets: list[Asset] = []

        for node in exploration.snapshot.repository_nodes:

            if node.is_directory:
                continue

            asset_path = self._asset_path(root, node.path)

            metadata = self.extractor.extract(
                extension=asset_path.suffix,
                size=asset_path.stat().st_size,
            )

            assets.append(
                Asset(
                    path=asset_path,
                    filename=asset_path.name,
                    metadata=metadata,
                )
            )

        return Batch(
            name=root.name,
            root=root,
            assets=assets,
        )

    def _asset_path(self, root: Path, node_path: Path) -> Path:
        if node_path.is_absolute():
            return node_path

        return root / node_path
