import argparse
from pathlib import Path

from rie.ingestion.creative_asset_scan_report_serializer import load_json
from rie.ingestion.unknown_asset_header_inspector import (
    UnknownAssetHeaderInspection,
)
from rie.ingestion.unknown_asset_header_inspector import inspect_unknown_assets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect UNKNOWN creative asset file headers.",
    )
    parser.add_argument("report_path")
    parser.add_argument(
        "--bytes",
        type=int,
        default=32,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=40,
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

    inspections = inspect_unknown_assets(
        data,
        header_bytes=args.bytes,
        limit=args.limit,
    )
    print_unknown_asset_inspections(inspections)

    return 0


def print_unknown_asset_inspections(
    inspections: list[UnknownAssetHeaderInspection],
) -> None:
    print("UNKNOWN Asset Header Inspection")
    print(f"Total UNKNOWN : {len(inspections)}")
    print()

    for inspection in inspections:
        print(f"- {inspection.path}")
        print(f"  Size         : {inspection.size}")
        print(f"  Header HEX   : {inspection.header_hex}")
        print(f"  Header ASCII : {inspection.header_ascii}")
        print(f"  Candidate    : {inspection.candidate}")

        if inspection.error is not None:
            print(f"  Error        : {inspection.error}")


if __name__ == "__main__":
    raise SystemExit(main())
