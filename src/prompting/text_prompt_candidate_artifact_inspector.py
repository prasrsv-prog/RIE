from dataclasses import dataclass
from typing import Any


ALLOWED_RECORD_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "evidence_index",
    "knowledge_index",
}

FORBIDDEN_RECORD_FIELDS = {
    "prompt",
    "final_prompt",
    "instruction",
    "system_prompt",
    "user_prompt",
    "summary",
    "category",
    "label",
    "metadata",
    "confidence",
    "score",
    "embedding",
    "graph",
    "style",
    "tone",
    "creative_direction",
    "image_generation",
    "video_generation",
    "model",
    "analysis",
}


@dataclass(frozen=True)
class TextPromptCandidateArtifactInspection:
    total_prompt_candidates: int
    total_content_characters: int
    empty_content_candidate_count: int
    invalid_record_count: int
    forbidden_field_count: int


def inspect_artifact(
    artifact: Any,
) -> TextPromptCandidateArtifactInspection:
    if not isinstance(artifact, dict):
        raise ValueError("Prompt candidate artifact must be an object.")

    if "prompt_candidates" not in artifact:
        raise ValueError(
            "Prompt candidate artifact must contain prompt_candidates."
        )

    prompt_candidates = artifact["prompt_candidates"]

    if not isinstance(prompt_candidates, list):
        raise ValueError(
            "Prompt candidate artifact prompt_candidates must be a list."
        )

    total_content_characters = 0
    empty_content_candidate_count = 0
    invalid_record_count = 0
    forbidden_field_count = 0

    for prompt_candidate in prompt_candidates:
        if not isinstance(prompt_candidate, dict):
            invalid_record_count += 1
            continue

        content = prompt_candidate.get("content")

        if isinstance(content, str):
            total_content_characters += len(content)

            if content == "":
                empty_content_candidate_count += 1

        forbidden_field_count += sum(
            field in FORBIDDEN_RECORD_FIELDS
            for field in prompt_candidate
        )

        if not _is_valid_prompt_candidate(prompt_candidate):
            invalid_record_count += 1

    return TextPromptCandidateArtifactInspection(
        total_prompt_candidates=len(prompt_candidates),
        total_content_characters=total_content_characters,
        empty_content_candidate_count=empty_content_candidate_count,
        invalid_record_count=invalid_record_count,
        forbidden_field_count=forbidden_field_count,
    )


def _is_valid_prompt_candidate(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_RECORD_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not isinstance(record["content"], str):
        return False

    size_bytes = record["size_bytes"]
    evidence_index = record["evidence_index"]
    knowledge_index = record["knowledge_index"]

    if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
        return False

    if (
        not isinstance(evidence_index, int)
        or isinstance(evidence_index, bool)
    ):
        return False

    return (
        isinstance(knowledge_index, int)
        and not isinstance(knowledge_index, bool)
    )
