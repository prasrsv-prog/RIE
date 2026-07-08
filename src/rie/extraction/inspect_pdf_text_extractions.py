import argparse
import json
from pathlib import Path

from rie.extraction.pdf_text_extraction_artifact_inspector import (
    PdfTextExtractionArtifactInspection,
)
from rie.extraction.pdf_text_extraction_artifact_inspector import (
    inspect_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a PDF text extraction artifact.",
    )
    parser.add_argument("pdf_text_extractions_path")

    args = parser.parse_args(argv)
    pdf_text_extractions_path = Path(args.pdf_text_extractions_path)

    if not pdf_text_extractions_path.exists():
        print(
            "PDF text extraction artifact not found: "
            f"{pdf_text_extractions_path}"
        )
        return 1

    if not pdf_text_extractions_path.is_file():
        print(f"Not a file: {pdf_text_extractions_path}")
        return 1

    try:
        artifact = json.loads(
            pdf_text_extractions_path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Failed to read PDF text extraction artifact: {exc}")
        return 1

    try:
        inspection = inspect_artifact(artifact)
    except ValueError as exc:
        print(f"Malformed PDF text extraction artifact: {exc}")
        return 1

    print_inspection(inspection)

    return 0


def print_inspection(
    inspection: PdfTextExtractionArtifactInspection,
) -> None:
    print("PDF Text Extraction Inspection")
    print(f"Total PDF Assets                   : {inspection.total_pdf_assets}")
    print(
        "Total Page Extractions             : "
        f"{inspection.total_page_extractions}"
    )
    print(f"Failed PDF Assets                  : {inspection.failed_pdf_assets}")
    print(
        "Empty Content Page Count           : "
        f"{inspection.empty_content_page_count}"
    )
    print(f"Page Warning Count                 : {inspection.page_warning_count}")
    print(f"Asset Error Count                  : {inspection.asset_error_count}")
    print(
        "Invalid Page Extraction Records    : "
        f"{inspection.invalid_page_extraction_record_count}"
    )
    print(
        "Invalid Asset Error Records        : "
        f"{inspection.invalid_asset_error_record_count}"
    )
    print(f"Forbidden Field Count              : {inspection.forbidden_field_count}")


if __name__ == "__main__":
    raise SystemExit(main())
