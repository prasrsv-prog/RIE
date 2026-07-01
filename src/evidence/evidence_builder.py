from rie.application.asset import Asset

from src.analysis.asset_analyzer import AssetAnalyzer

from .evidence import Evidence


class EvidenceBuilder:

    @staticmethod
    def build(
        asset: Asset
    ) -> Evidence:
        
        analysis = AssetAnalyzer.analyze(asset)

        return Evidence(
            asset_path=asset.path,
            filename=asset.filename,
            analysis=analysis
        )