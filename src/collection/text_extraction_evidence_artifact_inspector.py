from dataclasses import dataclass
from typing import Any


ALLOWED_RECORD_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
}

FORBIDDEN_RECORD_FIELDS = {
    "evidence_type",
    "metadata",
    "source_stage",
    "analysis",
    "size_class",
    "category",
    "summary",
    "knowledge",
    "prompt",
    "embedding",
}


@dataclass(frozen=True)
class TextExtractionEvidenceArtifactInspection:
    total_evidences: int
    total_content_characters: int
    empty_content_count: int
    invalid_record_count: int
    forbidden_field_count: int


def inspect_artifact(
    artifact: Any,
) -> TextExtractionEvidenceArtifactInspection:
    if not isinstance(artifact, dict):
        raise ValueError("Evidence artifact must be an object.")

    if "evidences" not in artifact:
        raise ValueError("Evidence artifact must contain evidences.")

    evidences = artifact["evidences"]

    if not isinstance(evidences, list):
        raise ValueError("Evidence artifact evidences must be a list.")

    total_content_characters = 0
    empty_content_count = 0
    invalid_record_count = 0
    forbidden_field_count = 0

    for evidence in evidences:
        if not isinstance(evidence, dict):
            invalid_record_count += 1
            continue

        content = evidence.get("content")

        if isinstance(content, str):
            total_content_characters += len(content)

            if content == "":
                empty_content_count += 1

        forbidden_field_count += sum(
            field in FORBIDDEN_RECORD_FIELDS
            for field in evidence
        )

        if not _is_valid_evidence_record(evidence):
            invalid_record_count += 1

    return TextExtractionEvidenceArtifactInspection(
        total_evidences=len(evidences),
        total_content_characters=total_content_characters,
        empty_content_count=empty_content_count,
        invalid_record_count=invalid_record_count,
        forbidden_field_count=forbidden_field_count,
    )


def _is_valid_evidence_record(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_RECORD_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not isinstance(record["content"], str):
        return False

    size_bytes = record["size_bytes"]

    return isinstance(size_bytes, int) and not isinstance(size_bytes, bool)
