import argparse
import json
from pathlib import Path

from knowledge.official_knowledge_collection import OfficialKnowledgeCollection
from knowledge.official_knowledge_collection_serializer import (
    OfficialKnowledgeCollectionSerializer,
)
from knowledge.official_knowledge_collector import OfficialKnowledgeCollector
from knowledge.official_knowledge_source_input_loader import (
    OfficialKnowledgeSourceInputLoader,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export Official Knowledge from curated source input JSON."
        ),
    )
    parser.add_argument("source_input_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    source_input_path = Path(args.source_input_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

    if not source_input_path.exists():
        print(
            "Official Knowledge source input not found: "
            f"{source_input_path}"
        )
        return 1

    if not source_input_path.is_file():
        print(f"Not a file: {source_input_path}")
        return 1

    try:
        source_input = json.loads(
            source_input_path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Failed to read Official Knowledge source input: {exc}")
        return 1

    try:
        source_items = OfficialKnowledgeSourceInputLoader.load(source_input)
    except ValueError as exc:
        print(f"Malformed Official Knowledge source input: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    collection = OfficialKnowledgeCollector.collect(source_items)

    try:
        output_path.write_text(
            OfficialKnowledgeCollectionSerializer.to_json(collection),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write Official Knowledge file: {exc}")
        return 1

    print_export_summary(
        total_source_items=len(source_items),
        collection=collection,
        output_path=output_path,
    )

    return 0


def print_export_summary(
    total_source_items: int,
    collection: OfficialKnowledgeCollection,
    output_path: Path,
) -> None:
    exported_official_knowledge_items = len(
        collection.official_knowledge_items
    )

    print("Official Knowledge Export")
    print(f"Total Source Items              : {total_source_items}")
    print(
        "Exported Official Knowledge Items: "
        f"{exported_official_knowledge_items}"
    )
    print(f"Output Path                     : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
