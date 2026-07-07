from pathlib import Path

from rie.application.asset import Asset

from analysis.asset_analyzer import AssetAnalyzer
from analysis.size_class import SizeClass
from rie.application.metadata import Metadata


def test_should_return_medium_analysis_for_5mb_asset():
    asset = Asset(
    path=Path("photo.jpg"),
    filename="photo.jpg",
    metadata=Metadata(
        extension=".jpg",
        size=5 * 1024 * 1024,
        category="image",
    )
)

    analysis = AssetAnalyzer.analyze(asset)

    assert analysis.size_class == SizeClass.MEDIUM