import argparse
from pathlib import Path

from rie.ingestion.creative_asset_scan_report_inspector import (
    CreativeAssetReportInspection,
)
from rie.ingestion.creative_asset_scan_report_inspector import inspect_report
from rie.ingestion.creative_asset_scan_report_serializer import load_json
from rie.ingestion.creative_asset_type import CreativeAssetType


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a creative asset scan report.",
    )
    parser.add_argument("report_path")
    parser.add_argument(
        "--top",
        type=int,
        default=10,
    )

    args = parser.parse_args(argv)
    report_path = Path(args.report_path)

    if not report_path.exists():
        print(f"Report not found: {report_path}")
        return 1

    if not report_path.is_file():
        print(f"Not a file: {report_path}")
        return 1

    try:
        data = load_json(report_path)
    except Exception as exc:
        print(f"Failed to read report: {exc}")
        return 1

    inspection = inspect_report(
        data,
        top_limit=args.top,
    )
    print_inspection(inspection)

    return 0


def print_inspection(inspection: CreativeAssetReportInspection) -> None:
    print("Creative Asset Scan Report Inspection")
    print(f"Root        : {inspection.root}")
    print(f"Total Files : {inspection.total_files}")
    print()
    print("Counts:")
    _print_counts(inspection.counts)
    print()
    print("Total Size by Type:")
    _print_counts(inspection.total_size_by_type)
    print()
    print("Top Largest Files:")
    _print_item_lines(
        inspection.top_largest_files,
        include_asset_type=True,
    )
    print()
    print("UTF8_TEXT Files:")
    _print_item_lines(inspection.utf8_text_files)
    print()
    print("PDF Files:")
    _print_item_lines(inspection.pdf_files)
    print()
    print("UNKNOWN Files:")
    _print_item_lines(inspection.unknown_files)
    print()
    print("Failed Files:")
    _print_failed_files(inspection.failed_files)


def _print_counts(counts: dict[str, int]) -> None:
    for asset_type in CreativeAssetType:
        print(f"{asset_type.name:<10} : {counts.get(asset_type.name, 0)}")


def _print_item_lines(
    items: list[dict],
    include_asset_type: bool = False,
) -> None:
    for item in items:
        if include_asset_type:
            print(f"- {item['asset_type']} {item['size']} {item['path']}")
        else:
            print(f"- {item['size']} {item['path']}")


def _print_failed_files(items: list[dict]) -> None:
    for item in items:
        print(
            f"- {item['asset_type']} "
            f"{item['path']} "
            f"{item['error']}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
