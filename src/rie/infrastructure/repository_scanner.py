from pathlib import Path


class RepositoryScanner:

    def scan(self, root: Path) -> list[Path]:

        assets: list[Path] = []

        for file in root.rglob("*"):

            if file.is_file():
                assets.append(file)

        return assets