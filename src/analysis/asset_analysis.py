from dataclasses import dataclass

from .size_class import SizeClass


@dataclass(frozen=True)
class AssetAnalysis:
    size_class: SizeClass