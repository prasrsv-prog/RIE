from typing import Any

from knowledge.official_knowledge_source_item import (
    OfficialKnowledgeSourceItem,
)


SOURCE_ITEMS_KEY = "official_knowledge_source_items"

REQUIRED_FIELDS = (
    "source_path",
    "source_document",
    "title",
    "content",
)

OPTIONAL_FIELDS = (
    "knowledge_id",
    "source_section",
    "source_page",
    "status",
    "governance_level",
    "pdf_evidence_index",
    "extraction_index",
)

OPTIONAL_STRING_FIELDS = (
    "knowledge_id",
    "source_section",
    "status",
    "governance_level",
)

INTEGER_FIELDS = (
    "source_page",
    "pdf_evidence_index",
    "extraction_index",
)

ALLOWED_ITEM_FIELDS = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)

FORBIDDEN_ITEM_FIELDS = {
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


class OfficialKnowledgeSourceInputLoader:

    @staticmethod
    def load(
        source_input: dict[str, Any],
    ) -> list[OfficialKnowledgeSourceItem]:
        if not isinstance(source_input, dict):
            raise ValueError(
                "Official Knowledge source input must be an object."
            )

        if set(source_input) != {SOURCE_ITEMS_KEY}:
            raise ValueError(
                "Official Knowledge source input must contain exactly "
                f"{SOURCE_ITEMS_KEY}."
            )

        source_items = source_input[SOURCE_ITEMS_KEY]

        if not isinstance(source_items, list):
            raise ValueError(
                "Official Knowledge source input "
                f"{SOURCE_ITEMS_KEY} must be a list."
            )

        return [
            _load_item(item, index)
            for index, item in enumerate(source_items)
        ]


def _load_item(
    item: Any,
    index: int,
) -> OfficialKnowledgeSourceItem:
    if not isinstance(item, dict):
        raise ValueError(
            f"Official Knowledge source input item {index} "
            "must be an object."
        )

    _reject_forbidden_fields(item, index)
    _reject_unknown_fields(item, index)
    _validate_required_fields(item, index)
    _validate_optional_string_fields(item, index)
    _validate_integer_fields(item, index)

    return OfficialKnowledgeSourceItem(
        knowledge_id=item.get("knowledge_id"),
        source_path=item["source_path"],
        source_document=item["source_document"],
        source_section=item.get("source_section"),
        source_page=item.get("source_page"),
        title=item["title"],
        content=item["content"],
        status=item.get("status"),
        governance_level=item.get("governance_level"),
        pdf_evidence_index=item.get("pdf_evidence_index"),
        extraction_index=item.get("extraction_index"),
    )


def _reject_forbidden_fields(
    item: dict[str, Any],
    index: int,
) -> None:
    forbidden_fields = sorted(set(item).intersection(FORBIDDEN_ITEM_FIELDS))

    if forbidden_fields:
        raise ValueError(
            f"Official Knowledge source input item {index} "
            f"contains forbidden field: {forbidden_fields[0]}."
        )


def _reject_unknown_fields(
    item: dict[str, Any],
    index: int,
) -> None:
    unknown_fields = sorted(set(item).difference(ALLOWED_ITEM_FIELDS))

    if unknown_fields:
        raise ValueError(
            f"Official Knowledge source input item {index} "
            f"contains unknown field: {unknown_fields[0]}."
        )


def _validate_required_fields(
    item: dict[str, Any],
    index: int,
) -> None:
    for field_name in REQUIRED_FIELDS:
        if field_name not in item:
            raise ValueError(
                f"Official Knowledge source input item {index} "
                f"missing required field: {field_name}."
            )

        value = item[field_name]

        if not isinstance(value, str) or value.strip() == "":
            raise ValueError(
                f"Official Knowledge source input item {index} "
                f"{field_name} must be a non-empty string."
            )


def _validate_optional_string_fields(
    item: dict[str, Any],
    index: int,
) -> None:
    for field_name in OPTIONAL_STRING_FIELDS:
        value = item.get(field_name)

        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"Official Knowledge source input item {index} "
                f"{field_name} must be a string or None."
            )


def _validate_integer_fields(
    item: dict[str, Any],
    index: int,
) -> None:
    for field_name in INTEGER_FIELDS:
        value = item.get(field_name)

        if value is None:
            continue

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(
                f"Official Knowledge source input item {index} "
                f"{field_name} must be an integer or None."
            )
