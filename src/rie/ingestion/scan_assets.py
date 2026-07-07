import argparse
from pathlib import Path

from rie.ingestion.creative_asset_batch_scanner import CreativeAssetBatchScanner
from rie.ingestion.creative_asset_scan_report import CreativeAssetScanReport
from rie.ingestion.creative_asset_scan_report_serializer import write_json
from rie.ingestion.creative_asset_type import CreativeAssetType


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan creative assets and report detected file types.",
    )
    parser.add_argument("folder_path")
    parser.add_argument(
        "--recursive",
        action="store_true",
    )
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    folder = Path(args.folder_path)

    if not folder.exists():
        print(f"Folder not found: {folder}")
        return 1

    if not folder.is_dir():
        print(f"Not a folder: {folder}")
        return 1

    report = CreativeAssetBatchScanner(
        recursive=args.recursive,
    ).scan(folder)

    print_report(report)

    if args.output is not None:
        output_path = Path(args.output)

        if not output_path.parent.exists():
            print(f"Output folder not found: {output_path.parent}")
            return 1

        try:
            write_json(report, output_path)
        except OSError as exc:
            print(f"Failed to write report: {exc}")
            return 1

    return 0


def print_report(report: CreativeAssetScanReport) -> None:
    failed = sum(
        item.error is not None
        for item in report.items
    )

    print("Creative Asset Scan Report")
    print(f"Root        : {report.root}")
    print(f"Total Files : {report.total_files}")
    print()
    for asset_type in CreativeAssetType:
        print(f"{asset_type.name:<10} : {report.count_by_type(asset_type)}")
    print(f"Failed     : {failed}")


if __name__ == "__main__":
    raise SystemExit(main())
