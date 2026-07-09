from collections.abc import Mapping
from typing import Any

from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType


SOURCE_ITEMS_KEY = "official_sources"

REQUIRED_FIELDS = (
    "source_id",
    "source_path",
    "source_type",
    "document_classification",
    "authority_status",
    "lifecycle_status",
    "evidence_eligibility",
)

OPTIONAL_FIELDS = (
    "version",
    "review_notes",
)

REQUIRED_STRING_FIELDS = (
    "source_id",
    "source_path",
)

OPTIONAL_STRING_FIELDS = (
    "version",
    "review_notes",
)

ENUM_FIELDS = (
    ("source_type", SourceType),
    ("document_classification", DocumentClassification),
    ("authority_status", AuthorityStatus),
    ("lifecycle_status", LifecycleStatus),
    ("evidence_eligibility", EvidenceEligibility),
)

ALLOWED_ITEM_FIELDS = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)

FORBIDDEN_ITEM_FIELDS = {
    "content",
    "text",
    "evidence",
    "evidence_index",
    "knowledge",
    "knowledge_id",
    "official_knowledge",
    "official_knowledge_index",
    "product_type",
    "prompt",
    "final_prompt",
    "ai_generated",
}


class OfficialSourceRegistryLoader:

    @staticmethod
    def load_from_mapping(
        data: Mapping[str, Any],
    ) -> list[OfficialSource]:
        if not isinstance(data, Mapping):
            raise TypeError("Official Source registry input must be a mapping.")

        if set(data) != {SOURCE_ITEMS_KEY}:
            raise ValueError(
                "Official Source registry input must contain exactly "
                f"{SOURCE_ITEMS_KEY}."
            )

        source_items = data[SOURCE_ITEMS_KEY]

        if not isinstance(source_items, list):
            raise TypeError(
                "Official Source registry "
                f"{SOURCE_ITEMS_KEY} must be a list."
            )

        sources = []
        seen_source_ids = set()

        for index, item in enumerate(source_items):
            source = _load_item(item, index)

            if source.source_id in seen_source_ids:
                raise ValueError(f"duplicate source_id: {source.source_id}.")

            seen_source_ids.add(source.source_id)
            sources.append(source)

        return sources


def _load_item(
    item: Any,
    index: int,
) -> OfficialSource:
    if not isinstance(item, Mapping):
        raise TypeError(
            f"Official Source registry item {index} must be an object."
        )

    _reject_forbidden_fields(item, index)
    _reject_unknown_fields(item, index)
    _validate_required_fields(item, index)
    _validate_optional_string_fields(item, index)

    enum_values = {
        field_name: _load_enum_value(item, index, field_name, enum_type)
        for field_name, enum_type in ENUM_FIELDS
    }

    return OfficialSource(
        source_id=item["source_id"],
        source_path=item["source_path"],
        source_type=enum_values["source_type"],
        document_classification=enum_values["document_classification"],
        authority_status=enum_values["authority_status"],
        lifecycle_status=enum_values["lifecycle_status"],
        evidence_eligibility=enum_values["evidence_eligibility"],
        version=item.get("version"),
        review_notes=item.get("review_notes"),
    )


def _reject_forbidden_fields(
    item: Mapping[str, Any],
    index: int,
) -> None:
    forbidden_fields = sorted(set(item).intersection(FORBIDDEN_ITEM_FIELDS))

    if forbidden_fields:
        raise ValueError(
            f"Official Source registry item {index} "
            f"contains forbidden field: {forbidden_fields[0]}."
        )


def _reject_unknown_fields(
    item: Mapping[str, Any],
    index: int,
) -> None:
    unknown_fields = sorted(set(item).difference(ALLOWED_ITEM_FIELDS))

    if unknown_fields:
        raise ValueError(
            f"Official Source registry item {index} "
            f"contains unknown field: {unknown_fields[0]}."
        )


def _validate_required_fields(
    item: Mapping[str, Any],
    index: int,
) -> None:
    for field_name in REQUIRED_FIELDS:
        if field_name not in item:
            raise ValueError(
                f"Official Source registry item {index} "
                f"missing required field: {field_name}."
            )

    for field_name in REQUIRED_STRING_FIELDS:
        value = item[field_name]

        if not isinstance(value, str) or value.strip() == "":
            raise ValueError(
                f"Official Source registry item {index} "
                f"{field_name} must be a non-empty string."
            )


def _validate_optional_string_fields(
    item: Mapping[str, Any],
    index: int,
) -> None:
    for field_name in OPTIONAL_STRING_FIELDS:
        value = item.get(field_name)

        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"Official Source registry item {index} "
                f"{field_name} must be a string or None."
            )


def _load_enum_value(
    item: Mapping[str, Any],
    index: int,
    field_name: str,
    enum_type: type[SourceType]
    | type[DocumentClassification]
    | type[AuthorityStatus]
    | type[LifecycleStatus]
    | type[EvidenceEligibility],
) -> (
    SourceType
    | DocumentClassification
    | AuthorityStatus
    | LifecycleStatus
    | EvidenceEligibility
):
    value = item[field_name]

    if not isinstance(value, str):
        raise ValueError(
            f"Official Source registry item {index} "
            f"{field_name} must be an exact enum string value."
        )

    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValueError(
            f"Official Source registry item {index} "
            f"{field_name} has invalid enum value: {value}."
        ) from exc
