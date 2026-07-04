from src.report.repository_report import RepositoryReport


class RepositoryReportPresenter:

    @staticmethod
    def present(report: RepositoryReport) -> None:

        statistics = report.statistics
        insight = report.insight

        print()
        print("=" * 50)
        print("Repository Summary")
        print("=" * 50)

        print(f"Total Assets  : {statistics.total_assets}")
        print(f"Small Assets  : {statistics.small_assets}")
        print(f"Medium Assets : {statistics.medium_assets}")
        print(f"Large Assets  : {statistics.large_assets}")

        print()

        print(f"Largest Category : {insight.largest_category}")
        print(f"Repository Health: {insight.repository_health}")

        print("=" * 50)