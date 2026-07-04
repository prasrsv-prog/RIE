from pathlib import Path

from src.analyzer.repository_analyzer import RepositoryAnalyzer
from src.report.repository_report_presenter import RepositoryReportPresenter


class Pipeline:

    def __init__(
        self,
        analyzer: RepositoryAnalyzer,
        presenter: RepositoryReportPresenter,
    ) -> None:

        self.analyzer = analyzer
        self.presenter = presenter

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

            report = self.analyzer.analyze(folder)

            self.presenter.present(report)