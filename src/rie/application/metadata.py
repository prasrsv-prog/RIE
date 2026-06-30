from dataclasses import dataclass


@dataclass
class Metadata:
    extension: str
    size: int
    category: str