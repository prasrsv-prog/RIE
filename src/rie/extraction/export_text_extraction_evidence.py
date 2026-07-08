import argparse
from pathlib import Path

from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)
from collection.text_extraction_evidence_collection_serializer import (
    to_json,
)
from collection.text_extraction_evidence_collector import (
    TextExtractionEvidenceCollector,
)
from rie.extraction.text_asset_extraction_report import (
    TextAssetExtractionReport,
)
from rie.extraction.text_asset_extraction_report_serializer import load_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export text extraction evidence from an extraction report.",
    )
    parser.add_argument("report_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    report_path = Path(args.report_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

    if not report_path.exists():
        print(f"Report not found: {report_path}")
        return 1

    if not report_path.is_file():
        print(f"Not a file: {report_path}")
        return 1

    try:
        report = load_json(report_path)
    except Exception as exc:
        print(f"Failed to read extraction report: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    collection = TextExtractionEvidenceCollector.collect(report)

    try:
        output_path.write_text(
            to_json(collection),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write evidence file: {exc}")
        return 1

    print_export_summary(
        report=report,
        collection=collection,
        output_path=output_path,
    )

    return 0


def print_export_summary(
    report: TextAssetExtractionReport,
    collection: TextExtractionEvidenceCollection,
    output_path: Path,
) -> None:
    print("Text Extraction Evidence Export")
    print(f"Root              : {report.root}")
    print(f"Total Extractions : {len(report.extractions)}")
    print(f"Skipped Failed    : {report.failed}")
    print(f"Evidence Count    : {len(collection.evidences)}")
    print(f"Output Path       : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
