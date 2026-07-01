from pathlib import Path

from rie.application.discovery_service import DiscoveryService

from src.report.repository_report import RepositoryReport

from src.collection.evidence_collector import EvidenceCollector

from src.analysis.statistics_collector import StatisticsCollector


class RepositoryAnalyzer:

    @staticmethod
    def analyze(
        repository_path: Path
    ) -> RepositoryReport:
        
        repository = DiscoveryService.discover(
            repository_path
        )
        
        evidences = EvidenceCollector.collect(
            repository.assets
        )

        statistics = StatisticsCollector.collect(
            evidences.evidences
        )
        
        return RepositoryReport(
            evidences=evidences,
            statistics=statistics
        )