from pathlib import Path

from repository_explorer import RepositoryExploration, RepositoryNode
from repository_explorer.model.repository_directories import RepositoryDirectories
from repository_explorer.model.repository_extensions import RepositoryExtensions
from repository_explorer.model.repository_snapshot import RepositorySnapshot
from repository_explorer.model.repository_statistics import RepositoryStatistics

from rie.infrastructure.repository_explorer_batch_discovery import (
    RepositoryExplorerBatchDiscovery,
)
from rie.interfaces.batch_discovery import BatchDiscovery


class FakeRepositoryExplorer:

    def __init__(self, exploration: RepositoryExploration) -> None:
        self.exploration = exploration
        self.explored_roots: list[Path] = []

    def explore(self, repository_path: Path) -> RepositoryExploration:
        self.explored_roots.append(repository_path)

        return self.exploration


def test_repository_explorer_batch_discovery_maps_exploration_to_batch(tmp_path):
    root = tmp_path / "batch-a"
    image_directory = root / "images"
    image_directory.mkdir(parents=True)

    image_file = image_directory / "photo.jpg"
    image_content = b"image-bytes"
    image_file.write_bytes(image_content)

    exploration = RepositoryExploration(
        snapshot=RepositorySnapshot(
            repository_nodes=[
                RepositoryNode(
                    path=Path("images"),
                    is_directory=True,
                ),
                RepositoryNode(
                    path=Path("images") / "photo.jpg",
                    is_directory=False,
                ),
            ],
        ),
        statistics=RepositoryStatistics(
            total_nodes=2,
            total_files=1,
            total_directories=1,
        ),
        extensions=RepositoryExtensions(
            extensions={
                ".jpg": 1,
            },
        ),
        directories=RepositoryDirectories(
            total_directories=1,
            top_level_directories=[
                "images",
            ],
            maximum_depth=1,
        ),
    )

    fake_explorer = FakeRepositoryExplorer(exploration)
    adapter = RepositoryExplorerBatchDiscovery(explorer=fake_explorer)

    batch = adapter.discover(root)

    assert fake_explorer.explored_roots == [root]
    assert isinstance(adapter, BatchDiscovery)
    assert batch.name == root.name
    assert batch.root == root
    assert len(batch.assets) == 1

    asset = batch.assets[0]
    assert asset.path.resolve() == image_file
    assert asset.filename == "photo.jpg"
    assert asset.metadata.extension == ".jpg"
    assert asset.metadata.size == len(image_content)
    assert asset.metadata.category == "Image"
