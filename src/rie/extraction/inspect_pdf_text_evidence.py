import argparse
import json
from pathlib import Path

from evidence.pdf_text_extraction_evidence_artifact_inspector import (
    PdfTextExtractionEvidenceArtifactInspection,
)
from evidence.pdf_text_extraction_evidence_artifact_inspector import (
    inspect_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a PDF text evidence artifact.",
    )
    parser.add_argument("pdf_text_evidence_path")

    args = parser.parse_args(argv)
    pdf_text_evidence_path = Path(args.pdf_text_evidence_path)

    if not pdf_text_evidence_path.exists():
        print(f"PDF text evidence artifact not found: {pdf_text_evidence_path}")
        return 1

    if not pdf_text_evidence_path.is_file():
        print(f"Not a file: {pdf_text_evidence_path}")
        return 1

    try:
        artifact = json.loads(
            pdf_text_evidence_path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Failed to read PDF text evidence artifact: {exc}")
        return 1

    try:
        inspection = inspect_artifact(artifact)
    except ValueError as exc:
        print(f"Malformed PDF text evidence artifact: {exc}")
        return 1

    print_inspection(inspection)

    return 0


def print_inspection(
    inspection: PdfTextExtractionEvidenceArtifactInspection,
) -> None:
    print("PDF Text Evidence Inspection")
    print(
        "Total PDF Text Evidences       : "
        f"{inspection.total_pdf_text_evidences}"
    )
    print(
        "Total Content Characters       : "
        f"{inspection.total_content_characters}"
    )
    print(
        "Empty Content Evidence Count   : "
        f"{inspection.empty_content_evidence_count}"
    )
    print(f"Warning Count                  : {inspection.warning_count}")
    print(f"Invalid Record Count           : {inspection.invalid_record_count}")
    print(f"Forbidden Field Count          : {inspection.forbidden_field_count}")


if __name__ == "__main__":
    raise SystemExit(main())
