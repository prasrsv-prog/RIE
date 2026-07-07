from pathlib import Path

from rie.interfaces.batch_discovery import BatchDiscovery

from analyzer.repository_analyzer import RepositoryAnalyzer
from analysis.statistics_collector import StatisticsCollector
from collection.evidence_collector import EvidenceCollector
from report.repository_insight_builder import RepositoryInsightBuilder
from report.repository_report_presenter import RepositoryReportPresenter


class Pipeline:

    def __init__(
        self,
        analyzer: RepositoryAnalyzer | None = None,
        presenter: RepositoryReportPresenter | None = None,
        discovery: BatchDiscovery | None = None,
    ) -> None:

        self.discovery = discovery

        self.simple_mode = False

        if analyzer is None:

            if discovery is None:
                raise ValueError(
                    "Pipeline requires analyzer or discovery"
                )

            self.simple_mode = True

            analyzer = RepositoryAnalyzer(
                discovery=discovery,
                evidence_collector=EvidenceCollector(),
                statistics_collector=StatisticsCollector(),
                insight_builder=RepositoryInsightBuilder(),
            )

        self.analyzer = analyzer

        self.presenter = (
            presenter
            if presenter is not None
            else RepositoryReportPresenter()
        )


    def execute(self) -> None:

        print("Loading configuration...")
        print("Loading repository...")
        print("Discovering assets...")

        repository = Path("repository")

        if not repository.exists():
            print("Repository folder not found.")
            return


        for folder in repository.iterdir():

            if not folder.is_dir():
                continue


            if self.simple_mode:

                batch = self.discovery.discover(folder)

                print(
                    f"Discovered batch: {batch.name}"
                )

                continue


            report = self.analyzer.analyze(folder)

            self.presenter.present(report)