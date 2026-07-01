from pathlib import Path

from rie.application.asset import Asset

from src.analysis.asset_analyzer import AssetAnalyzer
from src.analysis.size_class import SizeClass


def test_should_return_medium_analysis_for_5mb_asset():
    asset = Asset(
        path=Path("photo.jpg"),
        filename="photo.jpg",
        extension=".jpg",
        size=5 * 1024 * 1024
    )

    analysis = AssetAnalyzer.analyze(asset)

    assert analysis.size_class == SizeClass.MEDIUM