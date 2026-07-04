from pathlib import Path

from rie.application.metadata import Metadata

from src.analysis.asset_analysis import AssetAnalysis
from src.analysis.size_class import SizeClass
from src.analysis.statistics_collector import StatisticsCollector
from src.evidence.evidence import Evidence


def test_should_collect_repository_statistics():

    evidences = [
        Evidence(
            asset_path=Path("a.jpg"),
            filename="a.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=100,
                category="image",
            ),
            analysis=AssetAnalysis(size_class=SizeClass.SMALL),
        ),
        Evidence(
            asset_path=Path("b.jpg"),
            filename="b.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=100,
                category="image",
            ),
            analysis=AssetAnalysis(size_class=SizeClass.SMALL),
        ),
        Evidence(
            asset_path=Path("c.jpg"),
            filename="c.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=100,
                category="image",
            ),
            analysis=AssetAnalysis(size_class=SizeClass.MEDIUM),
        ),
        Evidence(
            asset_path=Path("d.jpg"),
            filename="d.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=100,
                category="image",
            ),
            analysis=AssetAnalysis(size_class=SizeClass.LARGE),
        ),
    ]

    statistics = StatisticsCollector.collect(evidences)

    assert statistics.total_assets == 4
    assert statistics.small_assets == 2
    assert statistics.medium_assets == 1
    assert statistics.large_assets == 1