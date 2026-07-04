"""
RCIS Intelligence Engine
Core Engine
"""

from rie.application.discovery_service import DiscoveryService

from rie.core.pipeline import Pipeline
from rie.core.state import EngineState

from src.analyzer.repository_analyzer import RepositoryAnalyzer
from src.analysis.statistics_collector import StatisticsCollector
from src.collection.evidence_collector import EvidenceCollector
from src.report.repository_report_presenter import RepositoryReportPresenter


class Engine:

    def __init__(self) -> None:

        self.state = EngineState()

        discovery = DiscoveryService()

        evidence_collector = EvidenceCollector()

        statistics_collector = StatisticsCollector()

        analyzer = RepositoryAnalyzer(
            discovery=discovery,
            evidence_collector=evidence_collector,
            statistics_collector=statistics_collector,
        )

        presenter = RepositoryReportPresenter()

        self.pipeline = Pipeline(
            analyzer=analyzer,
            presenter=presenter,
        )

        self.name = "RCIS Intelligence Engine"
        self.version = "0.1.0"
        self.status = "Development"

    def run(self) -> None:

        self.state.running = True

        print(f"Running : {self.state.running}")

        print("=" * 50)
        print(self.name)
        print(f"Version : {self.version}")
        print(f"Status  : {self.status}")
        print("=" * 50)

        self.pipeline.execute()

        print(f"Processed : {self.state.processed}")
        print(f"Failed    : {self.state.failed}")

        self.state.running = False

        print(f"Running : {self.state.running}")