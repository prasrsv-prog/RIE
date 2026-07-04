from dataclasses import dataclass


@dataclass(frozen=True)
class Metadata:
    extension: str
    size: int
    category: str