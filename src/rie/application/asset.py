from dataclasses import dataclass
from pathlib import Path

from rie.application.metadata import Metadata


@dataclass
class Asset:
    path: Path
    filename: str
    metadata: Metadata