from pathlib import Path

from rie.interfaces.batch_discovery import BatchDiscovery

from src.analysis.statistics_collector import StatisticsCollector
from src.collection.evidence_collector import EvidenceCollector
from src.report.repository_report import RepositoryReport


class RepositoryAnalyzer:

    def __init__(
        self,
        discovery: BatchDiscovery,
        evidence_collector: EvidenceCollector,
        statistics_collector: StatisticsCollector,
    ) -> None:

        self.discovery = discovery
        self.evidence_collector = evidence_collector
        self.statistics_collector = statistics_collector

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

        return RepositoryReport(
            evidences=evidences,
            statistics=statistics,
        )