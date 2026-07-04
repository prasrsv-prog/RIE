from src.report.repository_report import RepositoryReport


class RepositoryReportPresenter:

    def present(
        self,
        report: RepositoryReport,
    ) -> None:

        statistics = report.statistics

        print()
        print("=" * 50)
        print("Repository Summary")
        print("=" * 50)

        print(f"Total Assets  : {statistics.total_assets}")
        print(f"Small Assets  : {statistics.small_assets}")
        print(f"Medium Assets : {statistics.medium_assets}")
        print(f"Large Assets  : {statistics.large_assets}")

        print("=" * 50)