from dataclasses import dataclass
from pathlib import Path

from rie.application.asset import Asset


@dataclass
class Batch:

    name: str

    root: Path

    assets: list[Asset]