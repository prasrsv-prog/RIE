from pathlib import Path

from rie.application.batch import Batch
from rie.core.pipeline import Pipeline
from rie.interfaces.batch_discovery import BatchDiscovery


class FakeBatchDiscovery(BatchDiscovery):

    def __init__(self) -> None:
        self.discovered_roots: list[Path] = []

    def discover(self, root: Path) -> Batch:
        self.discovered_roots.append(root)

        return Batch(
            name=root.name,
            root=root,
            assets=[],
        )


def test_pipeline_uses_injected_batch_discovery(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    batch_folder = repository / "batch-a"
    batch_folder.mkdir(parents=True)
    (repository / "ignored-file.txt").write_text("", encoding="utf-8")

    fake_discovery = FakeBatchDiscovery()
    pipeline = Pipeline(discovery=fake_discovery)

    monkeypatch.chdir(tmp_path)

    pipeline.execute()

    assert len(fake_discovery.discovered_roots) == 1
    assert fake_discovery.discovered_roots[0].resolve() == batch_folder
    assert pipeline.discovery is fake_discovery
