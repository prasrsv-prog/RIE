from src.analysis.asset_analysis import AssetAnalysis
from src.analysis.size_class import SizeClass
from src.analysis.statistics_collector import StatisticsCollector


def test_should_collect_repository_statistics():

    analyses = [
        AssetAnalysis(size_class=SizeClass.SMALL),
        AssetAnalysis(size_class=SizeClass.SMALL),
        AssetAnalysis(size_class=SizeClass.MEDIUM),
        AssetAnalysis(size_class=SizeClass.LARGE),
    ]

    statistics = StatisticsCollector.collect(analyses)

    assert statistics.total_assets == 4
    assert statistics.small_assets == 2
    assert statistics.medium_assets == 1
    assert statistics.large_assets == 1