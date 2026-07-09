import argparse
import json
from pathlib import Path

from knowledge.official_knowledge_artifact_inspector import (
    OfficialKnowledgeArtifactInspection,
)
from knowledge.official_knowledge_artifact_inspector import (
    OfficialKnowledgeArtifactInspector,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an Official Knowledge artifact.",
    )
    parser.add_argument("official_knowledge_path")

    args = parser.parse_args(argv)
    official_knowledge_path = Path(args.official_knowledge_path)

    if not official_knowledge_path.exists():
        print(
            "Official Knowledge artifact not found: "
            f"{official_knowledge_path}"
        )
        return 1

    if not official_knowledge_path.is_file():
        print(f"Not a file: {official_knowledge_path}")
        return 1

    try:
        artifact = json.loads(
            official_knowledge_path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        print(f"Failed to read Official Knowledge artifact: {exc}")
        return 1

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)
    print_inspection(inspection)

    if inspection.is_valid:
        return 0

    return 1


def print_inspection(
    inspection: OfficialKnowledgeArtifactInspection,
) -> None:
    print("Official Knowledge Inspection")
    print(
        "total_official_knowledge_items: "
        f"{inspection.total_official_knowledge_items}"
    )
    print(
        "missing_required_traceability_count: "
        f"{inspection.missing_required_traceability_count}"
    )
    print(
        "missing_governance_count: "
        f"{inspection.missing_governance_count}"
    )
    print(f"forbidden_field_count: {inspection.forbidden_field_count}")
    print(f"index_mismatch_count: {inspection.index_mismatch_count}")
    print(f"is_valid: {_format_bool(inspection.is_valid)}")


def _format_bool(value: bool) -> str:
    if value:
        return "true"

    return "false"


if __name__ == "__main__":
    raise SystemExit(main())
