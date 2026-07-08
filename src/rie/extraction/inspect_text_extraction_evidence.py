import argparse
import json
from pathlib import Path

from collection.text_extraction_evidence_artifact_inspector import (
    TextExtractionEvidenceArtifactInspection,
)
from collection.text_extraction_evidence_artifact_inspector import (
    inspect_artifact,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a text extraction evidence artifact.",
    )
    parser.add_argument("evidence_path")

    args = parser.parse_args(argv)
    evidence_path = Path(args.evidence_path)

    if not evidence_path.exists():
        print(f"Evidence artifact not found: {evidence_path}")
        return 1

    if not evidence_path.is_file():
        print(f"Not a file: {evidence_path}")
        return 1

    try:
        artifact = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Failed to read evidence artifact: {exc}")
        return 1

    try:
        inspection = inspect_artifact(artifact)
    except ValueError as exc:
        print(f"Malformed evidence artifact: {exc}")
        return 1

    print_inspection(inspection)

    return 0


def print_inspection(
    inspection: TextExtractionEvidenceArtifactInspection,
) -> None:
    print("Text Extraction Evidence Inspection")
    print(f"Total Evidences          : {inspection.total_evidences}")
    print(
        "Total Content Characters : "
        f"{inspection.total_content_characters}"
    )
    print(f"Empty Content Count      : {inspection.empty_content_count}")
    print(f"Invalid Record Count     : {inspection.invalid_record_count}")
    print(f"Forbidden Field Count    : {inspection.forbidden_field_count}")


if __name__ == "__main__":
    raise SystemExit(main())
