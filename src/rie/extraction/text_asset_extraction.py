from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TextAssetExtraction:
    path: Path
    size: int
    content: str
    error: str | None = None
