from __future__ import annotations

from collections.abc import Mapping, Sequence

from .governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)

_SCHEMA_VERSION = 1
_ARTIFACT_TYPE = "pilot_authoritative_knowledge_taxonomy_mapping_canonical_data"

_ROOT_FIELDS = (
    "schema_version",
    "artifact_type",
    "source_checkpoint",
    "source_decision_packet_sha256",
    "mapping_record_count",
    "mappings",
    "authorization",
)

_MAPPING_FIELDS = (
    "governed_knowledge_id",
    "knowledge_id",
    "product_id",
    "variant_id",
    "source_id",
    "source_asset_id",
    "knowledge_type",
    "subject",
    "property",
)


def _require_exact_keys(
    value: Mapping[str, object],
    expected: tuple[str, ...],
    *,
    label: str,
) -> None:
    actual = set(value.keys())
    expected_set = set(expected)
    if actual != expected_set:
        missing = tuple(sorted(expected_set - actual))
        extra = tuple(sorted(actual - expected_set))
        raise ValueError(
            f"{label} fields mismatch: missing={missing}; extra={extra}"
        )


def _require_nonempty_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a nonempty string")
    return value


def _require_variant_id(value: object) -> str | None:
    if value is None:
        return None
    return _require_nonempty_string(value, label="variant_id")


def materialize_canonical_knowledge_taxonomy_mapping_records(
    canonical_mapping_dataset: Mapping[str, object],
) -> tuple[GovernedKnowledgePromptInputMappingRecord, ...]:
    """Materialize exact canonical mapping rows into existing bridge records.

    The caller supplies a pre-resolved in-memory canonical mapping dataset.
    This function performs validation and deterministic record construction
    only. It performs no filesystem, network, model, semantic, constraint,
    prompt-compilation, or bridge-invocation work.
    """

    if not isinstance(canonical_mapping_dataset, Mapping):
        raise TypeError("canonical_mapping_dataset must be a mapping")

    _require_exact_keys(
        canonical_mapping_dataset,
        _ROOT_FIELDS,
        label="canonical mapping dataset",
    )

    schema_version = canonical_mapping_dataset["schema_version"]
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != _SCHEMA_VERSION
    ):
        raise ValueError("unsupported canonical mapping dataset schema_version")

    artifact_type = canonical_mapping_dataset["artifact_type"]
    if artifact_type != _ARTIFACT_TYPE:
        raise ValueError("unsupported canonical mapping dataset artifact_type")

    _require_nonempty_string(
        canonical_mapping_dataset["source_checkpoint"],
        label="source_checkpoint",
    )
    _require_nonempty_string(
        canonical_mapping_dataset["source_decision_packet_sha256"],
        label="source_decision_packet_sha256",
    )

    authorization = canonical_mapping_dataset["authorization"]
    if not isinstance(authorization, Mapping):
        raise ValueError("authorization must be a mapping")

    mapping_record_count = canonical_mapping_dataset["mapping_record_count"]
    if (
        isinstance(mapping_record_count, bool)
        or not isinstance(mapping_record_count, int)
        or mapping_record_count <= 0
    ):
        raise ValueError("mapping_record_count must be a positive integer")

    mappings_value = canonical_mapping_dataset["mappings"]
    if (
        not isinstance(mappings_value, Sequence)
        or isinstance(mappings_value, (str, bytes, bytearray))
    ):
        raise ValueError("mappings must be a sequence")
    if not mappings_value:
        raise ValueError("mappings must not be empty")
    if len(mappings_value) != mapping_record_count:
        raise ValueError("mapping_record_count does not match mappings length")

    normalized_rows: list[dict[str, str | None]] = []
    governed_ids: set[str] = set()
    knowledge_ids: set[str] = set()

    for index, row_value in enumerate(mappings_value):
        if not isinstance(row_value, Mapping):
            raise ValueError(f"mappings[{index}] must be a mapping")

        _require_exact_keys(
            row_value,
            _MAPPING_FIELDS,
            label=f"mappings[{index}]",
        )

        governed_knowledge_id = _require_nonempty_string(
            row_value["governed_knowledge_id"],
            label=f"mappings[{index}].governed_knowledge_id",
        )
        knowledge_id = _require_nonempty_string(
            row_value["knowledge_id"],
            label=f"mappings[{index}].knowledge_id",
        )

        if governed_knowledge_id in governed_ids:
            raise ValueError("duplicate governed_knowledge_id")
        if knowledge_id in knowledge_ids:
            raise ValueError("duplicate knowledge_id")
        governed_ids.add(governed_knowledge_id)
        knowledge_ids.add(knowledge_id)

        normalized_rows.append(
            {
                "governed_knowledge_id": governed_knowledge_id,
                "knowledge_id": knowledge_id,
                "product_id": _require_nonempty_string(
                    row_value["product_id"],
                    label=f"mappings[{index}].product_id",
                ),
                "variant_id": _require_variant_id(row_value["variant_id"]),
                "source_id": _require_nonempty_string(
                    row_value["source_id"],
                    label=f"mappings[{index}].source_id",
                ),
                "source_asset_id": _require_nonempty_string(
                    row_value["source_asset_id"],
                    label=f"mappings[{index}].source_asset_id",
                ),
                "knowledge_type": _require_nonempty_string(
                    row_value["knowledge_type"],
                    label=f"mappings[{index}].knowledge_type",
                ),
                "subject": _require_nonempty_string(
                    row_value["subject"],
                    label=f"mappings[{index}].subject",
                ),
                "property": _require_nonempty_string(
                    row_value["property"],
                    label=f"mappings[{index}].property",
                ),
            }
        )

    normalized_rows.sort(key=lambda row: row["governed_knowledge_id"] or "")

    return tuple(
        GovernedKnowledgePromptInputMappingRecord(
            governed_knowledge_id=row["governed_knowledge_id"],
            knowledge_id=row["knowledge_id"],
            product_id=row["product_id"],
            variant_id=row["variant_id"],
            source_id=row["source_id"],
            source_asset_id=row["source_asset_id"],
            knowledge_type=row["knowledge_type"],
            subject=row["subject"],
            property=row["property"],
        )
        for row in normalized_rows
    )
