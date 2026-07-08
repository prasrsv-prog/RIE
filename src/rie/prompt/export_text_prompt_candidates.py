import argparse
import json
from pathlib import Path

from prompting.text_prompt_candidate_collection import (
    TextPromptCandidateCollection,
)
from prompting.text_prompt_candidate_collection_serializer import (
    TextPromptCandidateCollectionSerializer,
)
from prompting.text_prompt_candidate_collector import (
    TextPromptCandidateCollector,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export text prompt candidates from a text knowledge artifact."
        ),
    )
    parser.add_argument("knowledge_path")
    parser.add_argument("--output")

    args = parser.parse_args(argv)
    knowledge_path = Path(args.knowledge_path)

    if args.output is None:
        print("Output path required: --output")
        return 1

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
        collection = TextPromptCandidateCollector.collect(artifact)
    except ValueError as exc:
        print(f"Malformed knowledge artifact: {exc}")
        return 1

    output_path = Path(args.output)

    if not output_path.parent.exists():
        print(f"Output folder not found: {output_path.parent}")
        return 1

    try:
        output_path.write_text(
            TextPromptCandidateCollectionSerializer.to_json(collection),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Failed to write prompt candidates file: {exc}")
        return 1

    print_export_summary(
        total_knowledge_items=len(artifact["knowledge_items"]),
        collection=collection,
        output_path=output_path,
    )

    return 0


def print_export_summary(
    total_knowledge_items: int,
    collection: TextPromptCandidateCollection,
    output_path: Path,
) -> None:
    exported_prompt_candidates = len(collection.prompt_candidates)

    print("Text Prompt Candidate Export")
    print(f"Total Knowledge Items       : {total_knowledge_items}")
    print(f"Exported Prompt Candidates : {exported_prompt_candidates}")
    print(
        "Skipped Invalid Records    : "
        f"{total_knowledge_items - exported_prompt_candidates}"
    )
    print(f"Output Path                : {output_path}")


if __name__ == "__main__":
    raise SystemExit(main())
