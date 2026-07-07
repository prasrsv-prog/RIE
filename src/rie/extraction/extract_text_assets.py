import argparse
from pathlib import Path

from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport
from rie.extraction.text_asset_extraction_report_serializer import write_json
from rie.extraction.text_asset_extractor import TextAssetExtractor
from rie.ingestion.creative_asset_scan_report_serializer import load_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract UTF8_TEXT creative asset content.",
    )
    parser.add_argument("report_path")
    parser.add_argument("--output")

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

    report = TextAssetExtractor().extract(data)
    print_extraction_report(report)

    if args.output is not None:
        output_path = Path(args.output)

        if not output_path.parent.exists():
            print(f"Output folder not found: {output_path.parent}")
            return 1

        try:
            write_json(report, output_path)
        except OSError as exc:
            print(f"Failed to write extraction report: {exc}")
            return 1

    return 0


def print_extraction_report(report: TextAssetExtractionReport) -> None:
    print("Text Asset Extraction Report")
    print(f"Root              : {report.root}")
    print(f"Total Text Assets : {report.total_text_assets}")
    print(f"Failed            : {report.failed}")
    print()
    print("Extracted Files:")

    for extraction in report.extractions:
        print(f"- {extraction.size} {extraction.path}")

        if extraction.error is not None:
            print(f"  Error: {extraction.error}")


if __name__ == "__main__":
    raise SystemExit(main())
