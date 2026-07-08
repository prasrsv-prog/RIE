import argparse
import json
from pathlib import Path
from typing import Any

from collection.pdf_text_extraction_evidence_collection import (
    PdfTextExtractionEvidenceCollection,
)
from collection.pdf_text_extraction_evidence_collection_serializer import (
    PdfTextExtractionEvidenceCollectionSerializer,
)
from collection.pdf_text_extraction_evidence_collector import (
    PdfTextExtractionEvidenceCollector,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export PDF text evidence from a PDF text extraction artifact.",
    )
    parser.add_argument("pdf_text_extractions_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    pdf_text_extractions_path = Path(args.pdf_text_extractions_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

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
        _validate_readable_artifact(artifact)
    except json.JSONDecodeError as exc:
        print(f"Failed to read PDF text extraction artifact: {exc}")
        return 1
    except ValueError as exc:
        print(f"Malformed PDF text extraction artifact: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    collection = PdfTextExtractionEvidenceCollector.collect(artifact)

    try:
        output_path.write_text(
            PdfTextExtractionEvidenceCollectionSerializer.to_json(collection),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write PDF text evidence file: {exc}")
        return 1

    print_export_summary(
        artifact=artifact,
        collection=collection,
        output_path=output_path,
    )

    return 0


def _validate_readable_artifact(
    artifact: Any,
) -> None:
    if not isinstance(artifact, dict):
        raise ValueError("PDF text extraction artifact must be an object.")

    if "page_extractions" not in artifact:
        raise ValueError(
            "PDF text extraction artifact must contain page_extractions."
        )

    if not isinstance(artifact["page_extractions"], list):
        raise ValueError(
            "PDF text extraction artifact page_extractions must be a list."
        )


def print_export_summary(
    artifact: dict[str, Any],
    collection: PdfTextExtractionEvidenceCollection,
    output_path: Path,
) -> None:
    total_pages = len(artifact["page_extractions"])
    exported_evidences = len(collection.evidences)

    print("PDF Text Evidence Export")
    print(f"Total PDF Extraction Pages : {total_pages}")
    print(f"Exported PDF Evidences     : {exported_evidences}")
    print(f"Skipped Invalid Records    : {total_pages - exported_evidences}")
    print(f"Output Path                : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
