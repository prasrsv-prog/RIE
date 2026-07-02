from pathlib import Path

from rie.interfaces.batch_discovery import BatchDiscovery

from src.analysis.statistics_collector import StatisticsCollector
from src.collection.evidence_collector import EvidenceCollector
from src.report.repository_report import RepositoryReport


class RepositoryAnalyzer:

    def __init__(
        self,
        discovery: BatchDiscovery,
    ) -> None:
        self.discovery = discovery

    def analyze(
        self,
        repository_path: Path,
    ) -> RepositoryReport:

        batch = self.discovery.discover(
            repository_path
        )

        evidences = EvidenceCollector.collect(
            batch.assets
        )

        statistics = StatisticsCollector.collect(
            evidences.evidences
        )

        return RepositoryReport(
            evidences=evidences,
            statistics=statistics,
        )