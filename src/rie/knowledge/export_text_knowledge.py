import argparse
import json
from pathlib import Path

from knowledge.text_knowledge_collection import TextKnowledgeCollection
from knowledge.text_knowledge_collection_serializer import to_json
from knowledge.text_knowledge_collector import TextKnowledgeCollector


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export text knowledge from a text evidence artifact.",
    )
    parser.add_argument("evidence_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    evidence_path = Path(args.evidence_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

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
        collection = TextKnowledgeCollector.collect(artifact)
    except ValueError as exc:
        print(f"Malformed evidence artifact: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    try:
        output_path.write_text(
            to_json(collection),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write knowledge file: {exc}")
        return 1

    print_export_summary(
        total_evidence_records=len(artifact["evidences"]),
        collection=collection,
        output_path=output_path,
    )

    return 0


def print_export_summary(
    total_evidence_records: int,
    collection: TextKnowledgeCollection,
    output_path: Path,
) -> None:
    exported_knowledge_items = len(collection.knowledge_items)

    print("Text Knowledge Export")
    print(f"Total Evidence Records  : {total_evidence_records}")
    print(f"Exported Knowledge Items: {exported_knowledge_items}")
    print(
        "Skipped Invalid Records : "
        f"{total_evidence_records - exported_knowledge_items}"
    )
    print(f"Output Path             : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
