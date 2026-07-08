from dataclasses import dataclass
from typing import Any


ALLOWED_RECORD_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "evidence_index",
}

FORBIDDEN_RECORD_FIELDS = {
    "knowledge_type",
    "summary",
    "category",
    "label",
    "metadata",
    "confidence",
    "embedding",
    "prompt",
    "analysis",
    "size_class",
    "checksum",
    "artifact_id",
}


@dataclass(frozen=True)
class TextKnowledgeArtifactInspection:
    total_knowledge_items: int
    total_content_characters: int
    empty_content_count: int
    invalid_record_count: int
    forbidden_field_count: int


def inspect_artifact(
    artifact: Any,
) -> TextKnowledgeArtifactInspection:
    if not isinstance(artifact, dict):
        raise ValueError("Knowledge artifact must be an object.")

    if "knowledge_items" not in artifact:
        raise ValueError("Knowledge artifact must contain knowledge_items.")

    knowledge_items = artifact["knowledge_items"]

    if not isinstance(knowledge_items, list):
        raise ValueError("Knowledge artifact knowledge_items must be a list.")

    total_content_characters = 0
    empty_content_count = 0
    invalid_record_count = 0
    forbidden_field_count = 0

    for knowledge_item in knowledge_items:
        if not isinstance(knowledge_item, dict):
            invalid_record_count += 1
            continue

        content = knowledge_item.get("content")

        if isinstance(content, str):
            total_content_characters += len(content)

            if content == "":
                empty_content_count += 1

        forbidden_field_count += sum(
            field in FORBIDDEN_RECORD_FIELDS
            for field in knowledge_item
        )

        if not _is_valid_knowledge_item(knowledge_item):
            invalid_record_count += 1

    return TextKnowledgeArtifactInspection(
        total_knowledge_items=len(knowledge_items),
        total_content_characters=total_content_characters,
        empty_content_count=empty_content_count,
        invalid_record_count=invalid_record_count,
        forbidden_field_count=forbidden_field_count,
    )


def _is_valid_knowledge_item(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_RECORD_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not isinstance(record["content"], str):
        return False

    size_bytes = record["size_bytes"]
    evidence_index = record["evidence_index"]

    if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
        return False

    return (
        isinstance(evidence_index, int)
        and not isinstance(evidence_index, bool)
    )
