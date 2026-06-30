from pathlib import Path

from rie.application.discovery_service import DiscoveryService


class Pipeline:

    def __init__(self) -> None:
        self.discovery = DiscoveryService()

    def execute(self) -> None:

        print("Loading configuration...")
        print("Loading repository...")
        print("Discovering assets...")

        repository = Path("repository")

        if not repository.exists():
            print("Repository folder not found.")
            return

        batches = []

        for folder in repository.iterdir():

            if not folder.is_dir():
                continue

            batch = self.discovery.discover(folder)
            batches.append(batch)

        total_assets = sum(len(batch.assets) for batch in batches)

        print()
        print("=" * 50)
        print("Repository Summary")
        print("=" * 50)
        print(f"Batch Found  : {len(batches)}")
        print(f"Assets Found : {total_assets}")

        print()

        for batch in batches:
            print(f"- {batch.name} ({len(batch.assets)} assets)")

        print("=" * 50)