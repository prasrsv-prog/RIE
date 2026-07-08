from dataclasses import dataclass
from typing import Any


REQUIRED_STRING_FIELDS = {
    "source_path",
    "source_document",
    "title",
    "content",
}

GOVERNANCE_FIELDS = {
    "status",
    "governance_level",
}

FORBIDDEN_RECORD_FIELDS = {
    "prompt",
    "final_prompt",
    "instruction",
    "system_prompt",
    "user_prompt",
    "ai_output",
    "generated_claim",
    "confidence",
    "embedding",
    "graph",
    "score",
    "creative_direction",
    "image_generation",
    "video_generation",
    "summary",
    "category",
    "label",
    "product_type",
    "variant",
    "style",
    "tone",
    "analysis",
    "model",
}


@dataclass(frozen=True)
class OfficialKnowledgeArtifactInspection:
    total_official_knowledge_items: int
    missing_required_traceability_count: int
    missing_governance_count: int
    forbidden_field_count: int
    index_mismatch_count: int
    is_valid: bool


class OfficialKnowledgeArtifactInspector:

    @staticmethod
    def inspect(
        artifact: Any,
    ) -> OfficialKnowledgeArtifactInspection:
        if not isinstance(artifact, dict):
            return _invalid_top_level_inspection()

        official_knowledge_items = artifact.get("official_knowledge_items")

        if not isinstance(official_knowledge_items, list):
            return _invalid_top_level_inspection()

        missing_required_traceability_count = 0
        missing_governance_count = 0
        forbidden_field_count = 0
        index_mismatch_count = 0

        for index, item in enumerate(official_knowledge_items):
            if not isinstance(item, dict):
                missing_required_traceability_count += 1
                continue

            if _has_missing_required_traceability(item):
                missing_required_traceability_count += 1

            if _has_missing_governance(item):
                missing_governance_count += 1

            forbidden_field_count += _count_forbidden_fields(item)

            if _has_index_mismatch(item, index):
                index_mismatch_count += 1

        is_valid = (
            missing_required_traceability_count == 0
            and forbidden_field_count == 0
            and index_mismatch_count == 0
        )

        return OfficialKnowledgeArtifactInspection(
            total_official_knowledge_items=len(official_knowledge_items),
            missing_required_traceability_count=(
                missing_required_traceability_count
            ),
            missing_governance_count=missing_governance_count,
            forbidden_field_count=forbidden_field_count,
            index_mismatch_count=index_mismatch_count,
            is_valid=is_valid,
        )


def _invalid_top_level_inspection() -> OfficialKnowledgeArtifactInspection:
    return OfficialKnowledgeArtifactInspection(
        total_official_knowledge_items=0,
        missing_required_traceability_count=0,
        missing_governance_count=0,
        forbidden_field_count=0,
        index_mismatch_count=0,
        is_valid=False,
    )


def _has_missing_required_traceability(
    item: dict[str, Any],
) -> bool:
    for field_name in REQUIRED_STRING_FIELDS:
        if _is_missing_string(item, field_name):
            return True

    if "official_knowledge_index" not in item:
        return True

    return item["official_knowledge_index"] is None


def _has_missing_governance(
    item: dict[str, Any],
) -> bool:
    return any(
        _is_missing_string(item, field_name)
        for field_name in GOVERNANCE_FIELDS
    )


def _is_missing_string(
    item: dict[str, Any],
    field_name: str,
) -> bool:
    value = item.get(field_name)

    return not isinstance(value, str) or value.strip() == ""


def _count_forbidden_fields(
    item: dict[str, Any],
) -> int:
    return sum(
        field in FORBIDDEN_RECORD_FIELDS
        for field in item
    )


def _has_index_mismatch(
    item: dict[str, Any],
    expected_index: int,
) -> bool:
    index = item.get("official_knowledge_index")

    if index is None:
        return False

    return (
        not isinstance(index, int)
        or isinstance(index, bool)
        or index != expected_index
    )
