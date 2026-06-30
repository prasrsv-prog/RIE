from pathlib import Path

from rie.application.asset import Asset
from rie.application.batch import Batch
from rie.infrastructure.repository_scanner import RepositoryScanner


class DiscoveryService:

    def __init__(self) -> None:
        self.scanner = RepositoryScanner()

    def discover(self, root: Path) -> Batch:

        files = self.scanner.scan(root)

        assets: list[Asset] = []

        for file in files:

            assets.append(
                Asset(
                    path=file,
                    filename=file.name,
                    extension=file.suffix,
                    size=file.stat().st_size,
                )
            )

        return Batch(
            name=root.name,
            root=root,
            assets=assets,
        )