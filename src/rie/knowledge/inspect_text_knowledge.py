import argparse
import json
from pathlib import Path

from knowledge.text_knowledge_artifact_inspector import (
    TextKnowledgeArtifactInspection,
)
from knowledge.text_knowledge_artifact_inspector import inspect_artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a text knowledge artifact.",
    )
    parser.add_argument("knowledge_path")

    args = parser.parse_args(argv)
    knowledge_path = Path(args.knowledge_path)

    if not knowledge_path.exists():
        print(f"Knowledge artifact not found: {knowledge_path}")
        return 1

    if not knowledge_path.is_file():
        print(f"Not a file: {knowledge_path}")
        return 1

    try:
        artifact = json.loads(knowledge_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Failed to read knowledge artifact: {exc}")
        return 1

    try:
        inspection = inspect_artifact(artifact)
    except ValueError as exc:
        print(f"Malformed knowledge artifact: {exc}")
        return 1

    print_inspection(inspection)

    return 0


def print_inspection(
    inspection: TextKnowledgeArtifactInspection,
) -> None:
    print("Text Knowledge Inspection")
    print(f"Total Knowledge Items    : {inspection.total_knowledge_items}")
    print(
        "Total Content Characters : "
        f"{inspection.total_content_characters}"
    )
    print(f"Empty Content Count      : {inspection.empty_content_count}")
    print(f"Invalid Record Count     : {inspection.invalid_record_count}")
    print(f"Forbidden Field Count    : {inspection.forbidden_field_count}")


if __name__ == "__main__":
    raise SystemExit(main())
