from pathlib import Path

from rie.interfaces.batch_discovery import BatchDiscovery

from analysis.statistics_collector import StatisticsCollector
from collection.evidence_collector import EvidenceCollector
from report.repository_insight_builder import RepositoryInsightBuilder
from report.repository_report import RepositoryReport


class RepositoryAnalyzer:

    def __init__(
        self,
        discovery: BatchDiscovery,
        evidence_collector: EvidenceCollector,
        statistics_collector: StatisticsCollector,
        insight_builder: RepositoryInsightBuilder,
    ) -> None:

        self.discovery = discovery
        self.evidence_collector = evidence_collector
        self.statistics_collector = statistics_collector
        self.insight_builder = insight_builder

    def analyze(
        self,
        repository_path: Path,
    ) -> RepositoryReport:

        batch = self.discovery.discover(
            repository_path
        )

        evidences = self.evidence_collector.collect(
            batch.assets
        )

        statistics = self.statistics_collector.collect(
            evidences.evidences
        )

        insight = self.insight_builder.build(
            evidences.evidences,
            statistics,
        )

        return RepositoryReport(
            evidences=evidences,
            statistics=statistics,
            insight=insight,
        )