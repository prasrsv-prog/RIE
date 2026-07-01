from rie.application.asset import Asset

from .asset_analysis import AssetAnalysis
from .size_classifier import SizeClassifier


class AssetAnalyzer:

    @staticmethod
    def analyze(asset: Asset) -> AssetAnalysis:
        size_class = SizeClassifier.classify(
            asset.metadata.size
        )

        return AssetAnalysis(
            size_class=size_class
        )