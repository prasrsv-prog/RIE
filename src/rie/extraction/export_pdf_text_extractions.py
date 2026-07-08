import argparse
import json
from pathlib import Path
from typing import Any

from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport
from rie.extraction.pdf_text_extraction_report_serializer import (
    PdfTextExtractionReportSerializer,
)
from rie.extraction.pdf_text_extractor import PdfTextExtractor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export embedded PDF text extraction from a scan report.",
    )
    parser.add_argument("scan_report_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    scan_report_path = Path(args.scan_report_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

    if not scan_report_path.exists():
        print(f"Scan report not found: {scan_report_path}")
        return 1

    if not scan_report_path.is_file():
        print(f"Not a file: {scan_report_path}")
        return 1

    try:
        data = json.loads(scan_report_path.read_text(encoding="utf-8"))
        extraction_input = _pdf_extraction_input(data)
    except json.JSONDecodeError as exc:
        print(f"Failed to read scan report: {exc}")
        return 1
    except ValueError as exc:
        print(f"Malformed scan report: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    report = PdfTextExtractor().extract(extraction_input)

    try:
        output_path.write_text(
            PdfTextExtractionReportSerializer.to_json(report),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write PDF text extraction file: {exc}")
        return 1

    print_export_summary(
        report=report,
        output_path=output_path,
    )

    return 0


def _pdf_extraction_input(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Scan report must be an object.")

    if "items" not in data:
        raise ValueError("Scan report must contain items.")

    items = data["items"]

    if not isinstance(items, list):
        raise ValueError("Scan report items must be a list.")

    root = data.get("root", "")

    if not isinstance(root, str):
        raise ValueError("Scan report root must be a string when present.")

    return {
        "root": root,
        "items": [
            item
            for item in items
            if isinstance(item, dict) and _is_pdf_item(item)
        ],
    }


def _is_pdf_item(item: dict[str, Any]) -> bool:
    asset_type = item.get("asset_type", item.get("kind"))

    if hasattr(asset_type, "name"):
        asset_type = asset_type.name

    return str(asset_type).upper() == "PDF"


def print_export_summary(
    report: PdfTextExtractionReport,
    output_path: Path,
) -> None:
    print("PDF Text Extraction Export")
    print(f"Root                   : {report.root}")
    print(f"Total PDF Assets       : {report.total_pdf_assets}")
    print(f"Total Page Extractions : {report.total_page_extractions}")
    print(f"Failed PDF Assets      : {report.failed_pdf_assets}")
    print(f"Output Path            : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
