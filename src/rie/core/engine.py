"""
RCIS Intelligence Engine
Core Engine
"""

from rie.application.discovery_service import DiscoveryService
from rie.core.pipeline import Pipeline
from rie.core.state import EngineState
from rie.interfaces.batch_discovery import BatchDiscovery

from analyzer.repository_analyzer import RepositoryAnalyzer
from analysis.statistics_collector import StatisticsCollector
from collection.evidence_collector import EvidenceCollector
from report.repository_insight_builder import RepositoryInsightBuilder
from report.repository_report_presenter import RepositoryReportPresenter


class Engine:

    def __init__(
        self,
        discovery: BatchDiscovery | None = None,
    ) -> None:

        self.state = EngineState()

        discovery = discovery or DiscoveryService()

        evidence_collector = EvidenceCollector()

        statistics_collector = StatisticsCollector()

        insight_builder = RepositoryInsightBuilder()

        analyzer = RepositoryAnalyzer(
            discovery=discovery,
            evidence_collector=evidence_collector,
            statistics_collector=statistics_collector,
            insight_builder=insight_builder,
        )

        presenter = RepositoryReportPresenter()

        self.pipeline = Pipeline(
            analyzer=analyzer,
            presenter=presenter,
            discovery=discovery,
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