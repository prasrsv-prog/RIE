from pathlib import Path

from rie.interfaces.batch_discovery import BatchDiscovery

from rie.application.asset import Asset
from rie.application.batch import Batch
from rie.application.metadata_extractor import MetadataExtractor
from rie.infrastructure.repository_scanner import RepositoryScanner


class DiscoveryService(BatchDiscovery):

    def __init__(self) -> None:
        self.scanner = RepositoryScanner()
        self.extractor = MetadataExtractor()

    def discover(
        self,
        root: Path,
    ) -> Batch:

        files = self.scanner.scan(root)

        assets: list[Asset] = []

        for file in files:

            metadata = self.extractor.extract(
                extension=file.suffix,
                size=file.stat().st_size,
            )

            assets.append(
                Asset(
                    path=file,
                    filename=file.name,
                    metadata=metadata,
                )
            )

        return Batch(
            name=root.name,
            root=root,
            assets=assets,
        )