import argparse
import json
from pathlib import Path

from prompting.text_prompt_candidate_artifact_inspector import (
    TextPromptCandidateArtifactInspection,
)
from prompting.text_prompt_candidate_artifact_inspector import inspect_artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a text prompt candidate artifact.",
    )
    parser.add_argument("prompt_candidates_path")

    args = parser.parse_args(argv)
    prompt_candidates_path = Path(args.prompt_candidates_path)

    if not prompt_candidates_path.exists():
        print(f"Prompt candidate artifact not found: {prompt_candidates_path}")
        return 1

    if not prompt_candidates_path.is_file():
        print(f"Not a file: {prompt_candidates_path}")
        return 1

    try:
        artifact = json.loads(
            prompt_candidates_path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Failed to read prompt candidate artifact: {exc}")
        return 1

    try:
        inspection = inspect_artifact(artifact)
    except ValueError as exc:
        print(f"Malformed prompt candidate artifact: {exc}")
        return 1

    print_inspection(inspection)

    return 0


def print_inspection(
    inspection: TextPromptCandidateArtifactInspection,
) -> None:
    print("Text Prompt Candidate Inspection")
    print(
        "Total Prompt Candidates   : "
        f"{inspection.total_prompt_candidates}"
    )
    print(
        "Total Content Characters  : "
        f"{inspection.total_content_characters}"
    )
    print(
        "Empty Content Candidates  : "
        f"{inspection.empty_content_candidate_count}"
    )
    print(f"Invalid Record Count      : {inspection.invalid_record_count}")
    print(f"Forbidden Field Count     : {inspection.forbidden_field_count}")


if __name__ == "__main__":
    raise SystemExit(main())
