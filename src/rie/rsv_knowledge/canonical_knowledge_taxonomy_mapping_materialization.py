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

_EXTENSION_ARTIFACT_TYPE = "rcis_authoritative_knowledge_taxonomy_mapping_extension"

_EXTENSION_ROOT_FIELDS = (
    "schema_version",
    "artifact_type",
    "extension_id",
    "extension_role",
    "base_mapping_reference",
    "extension_provenance",
    "scope",
    "canonical_binding",
    "mapping_record_count",
    "mappings",
    "authorization",
)

_EXTENSION_BASE_MAPPING_REFERENCE_FIELDS = (
    "filename",
    "sha256",
    "bytes",
    "lf",
    "mapping_record_count",
    "source_decision_packet_sha256",
)

_EXTENSION_PROVENANCE_FIELDS = (
    "source_decision_packet_filename",
    "source_decision_packet_sha256",
    "governed_repository_sha256",
    "code_checkpoint",
    "source_pr086cg_report_sha256",
)

_EXTENSION_SCOPE_FIELDS = (
    "product_id",
    "variant_id",
    "exact_five_facts_only",
    "corrected_l_excluded",
    "other_products_or_facts_authorized",
)

_EXTENSION_CANONICAL_BINDING_FIELDS = (
    "product_id",
    "variant_id",
    "knowledge_ids",
)

_EXTENSION_AUTHORIZATION_FIELDS = (
    "existing_base_mapping_mutation_authorized",
    "governed_repository_write_authorized",
    "evidence_repository_write_authorized",
    "source_code_mutation_authorized",
    "git_mutation_authorized",
    "network_operation_authorized",
    "semantic_inference_authorized",
)

_CORRECTED_L_SINGLE_RECORD_PRODUCT_ID = "ffs21"
_CORRECTED_L_SINGLE_RECORD_VARIANT_ID = None
_CORRECTED_L_SINGLE_RECORD_GOVERNED_KNOWLEDGE_ID = (
    "gk1_319de8156ac006f0536ed8f2ef43e424aa9f0a5113951063b3d4954a931e7b04"
)
_CORRECTED_L_SINGLE_RECORD_KNOWLEDGE_ID = (
    "knowledge-ffs21-head-circumference-size-l"
)
_CORRECTED_L_SINGLE_RECORD_SOURCE_ID = "pilot-rsv-ffs21-product-manual"
_CORRECTED_L_SINGLE_RECORD_SOURCE_ASSET_ID = (
    "asset-67e7d5f723fd84180bcfcf091dfc16801b3498d95b5caefe8be351aebfc40a82"
)
_CORRECTED_L_SINGLE_RECORD_KNOWLEDGE_TYPE = "product_specification"
_CORRECTED_L_SINGLE_RECORD_SUBJECT = "ffs21"
_CORRECTED_L_SINGLE_RECORD_PROPERTY = "head_circumference_size_l"


def _require_sha256_string(value: object, *, label: str) -> str:
    text = _require_nonempty_string(value, label=label)
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"{label} must be a lowercase sha256 hex string")
    return text


def _require_positive_integer(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _require_nonnegative_integer(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a nonnegative integer")
    return value


def materialize_canonical_knowledge_taxonomy_mapping_extension_records(
    canonical_mapping_extension_dataset: Mapping[str, object],
) -> tuple[GovernedKnowledgePromptInputMappingRecord, ...]:
    """Validate a provenance-preserving mapping extension and reuse v1 row materialization.

    The caller supplies an already-resolved in-memory extension artifact. This
    adapter validates extension provenance and scope, projects only the explicit
    canonical mapping rows plus their own decision provenance into the existing
    canonical-v1 materializer input contract, and delegates deterministic row
    construction to ``materialize_canonical_knowledge_taxonomy_mapping_records``.

    It performs no filesystem, network, model, semantic, prompt, repository, or
    mutation work.
    """

    if not isinstance(canonical_mapping_extension_dataset, Mapping):
        raise TypeError(
            "canonical_mapping_extension_dataset must be a mapping"
        )

    _require_exact_keys(
        canonical_mapping_extension_dataset,
        _EXTENSION_ROOT_FIELDS,
        label="canonical mapping extension dataset",
    )

    schema_version = canonical_mapping_extension_dataset["schema_version"]
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != _SCHEMA_VERSION
    ):
        raise ValueError(
            "unsupported canonical mapping extension dataset schema_version"
        )

    if (
        canonical_mapping_extension_dataset["artifact_type"]
        != _EXTENSION_ARTIFACT_TYPE
    ):
        raise ValueError(
            "unsupported canonical mapping extension dataset artifact_type"
        )

    _require_nonempty_string(
        canonical_mapping_extension_dataset["extension_id"],
        label="extension_id",
    )
    _require_nonempty_string(
        canonical_mapping_extension_dataset["extension_role"],
        label="extension_role",
    )

    base_reference = canonical_mapping_extension_dataset[
        "base_mapping_reference"
    ]
    if not isinstance(base_reference, Mapping):
        raise ValueError("base_mapping_reference must be a mapping")
    _require_exact_keys(
        base_reference,
        _EXTENSION_BASE_MAPPING_REFERENCE_FIELDS,
        label="base_mapping_reference",
    )
    _require_nonempty_string(
        base_reference["filename"],
        label="base_mapping_reference.filename",
    )
    _require_sha256_string(
        base_reference["sha256"],
        label="base_mapping_reference.sha256",
    )
    _require_positive_integer(
        base_reference["bytes"],
        label="base_mapping_reference.bytes",
    )
    _require_nonnegative_integer(
        base_reference["lf"],
        label="base_mapping_reference.lf",
    )
    _require_positive_integer(
        base_reference["mapping_record_count"],
        label="base_mapping_reference.mapping_record_count",
    )
    _require_sha256_string(
        base_reference["source_decision_packet_sha256"],
        label="base_mapping_reference.source_decision_packet_sha256",
    )

    extension_provenance = canonical_mapping_extension_dataset[
        "extension_provenance"
    ]
    if not isinstance(extension_provenance, Mapping):
        raise ValueError("extension_provenance must be a mapping")
    _require_exact_keys(
        extension_provenance,
        _EXTENSION_PROVENANCE_FIELDS,
        label="extension_provenance",
    )
    _require_nonempty_string(
        extension_provenance["source_decision_packet_filename"],
        label="extension_provenance.source_decision_packet_filename",
    )
    source_decision_packet_sha256 = _require_sha256_string(
        extension_provenance["source_decision_packet_sha256"],
        label="extension_provenance.source_decision_packet_sha256",
    )
    _require_sha256_string(
        extension_provenance["governed_repository_sha256"],
        label="extension_provenance.governed_repository_sha256",
    )
    source_checkpoint = _require_nonempty_string(
        extension_provenance["code_checkpoint"],
        label="extension_provenance.code_checkpoint",
    )
    _require_sha256_string(
        extension_provenance["source_pr086cg_report_sha256"],
        label="extension_provenance.source_pr086cg_report_sha256",
    )

    scope = canonical_mapping_extension_dataset["scope"]
    if not isinstance(scope, Mapping):
        raise ValueError("scope must be a mapping")
    _require_exact_keys(
        scope,
        _EXTENSION_SCOPE_FIELDS,
        label="scope",
    )
    scope_product_id = _require_nonempty_string(
        scope["product_id"],
        label="scope.product_id",
    )
    scope_variant_id = _require_variant_id(scope["variant_id"])
    exact_five_scope_mode = (
        scope["exact_five_facts_only"] is True
        and scope["corrected_l_excluded"] is True
    )
    corrected_l_single_record_scope_mode = (
        scope["exact_five_facts_only"] is False
        and scope["corrected_l_excluded"] is False
    )
    if not (
        exact_five_scope_mode
        or corrected_l_single_record_scope_mode
    ):
        raise ValueError(
            "extension scope mode must be legacy exact-five or exact corrected-L single-record"
        )
    if scope["other_products_or_facts_authorized"] is not False:
        raise ValueError(
            "scope.other_products_or_facts_authorized must be false"
        )
    if corrected_l_single_record_scope_mode:
        if scope_product_id != _CORRECTED_L_SINGLE_RECORD_PRODUCT_ID:
            raise ValueError(
                "corrected-L single-record extension product_id must be ffs21"
            )
        if scope_variant_id is not _CORRECTED_L_SINGLE_RECORD_VARIANT_ID:
            raise ValueError(
                "corrected-L single-record extension variant_id must be null"
            )

    canonical_binding = canonical_mapping_extension_dataset[
        "canonical_binding"
    ]
    if not isinstance(canonical_binding, Mapping):
        raise ValueError("canonical_binding must be a mapping")
    _require_exact_keys(
        canonical_binding,
        _EXTENSION_CANONICAL_BINDING_FIELDS,
        label="canonical_binding",
    )
    binding_product_id = _require_nonempty_string(
        canonical_binding["product_id"],
        label="canonical_binding.product_id",
    )
    binding_variant_id = _require_variant_id(
        canonical_binding["variant_id"]
    )
    if (
        binding_product_id != scope_product_id
        or binding_variant_id != scope_variant_id
    ):
        raise ValueError("canonical_binding scope does not match extension scope")

    binding_knowledge_ids_value = canonical_binding["knowledge_ids"]
    if (
        not isinstance(binding_knowledge_ids_value, Sequence)
        or isinstance(
            binding_knowledge_ids_value,
            (str, bytes, bytearray),
        )
        or not binding_knowledge_ids_value
    ):
        raise ValueError(
            "canonical_binding.knowledge_ids must be a nonempty sequence"
        )
    binding_knowledge_ids = tuple(
        _require_nonempty_string(
            value,
            label=f"canonical_binding.knowledge_ids[{index}]",
        )
        for index, value in enumerate(binding_knowledge_ids_value)
    )
    if len(set(binding_knowledge_ids)) != len(binding_knowledge_ids):
        raise ValueError("duplicate canonical_binding knowledge_id")

    mapping_record_count = _require_positive_integer(
        canonical_mapping_extension_dataset["mapping_record_count"],
        label="mapping_record_count",
    )
    if exact_five_scope_mode:
        if mapping_record_count != 5:
            raise ValueError(
                "exact-five extension mapping_record_count must equal 5"
            )
    else:
        if mapping_record_count != 1:
            raise ValueError(
                "corrected-L single-record extension mapping_record_count must equal 1"
            )

    mappings_value = canonical_mapping_extension_dataset["mappings"]
    if (
        not isinstance(mappings_value, Sequence)
        or isinstance(mappings_value, (str, bytes, bytearray))
        or len(mappings_value) != mapping_record_count
    ):
        raise ValueError(
            "extension mappings must be a sequence matching mapping_record_count"
        )

    authorization = canonical_mapping_extension_dataset["authorization"]
    if not isinstance(authorization, Mapping):
        raise ValueError("authorization must be a mapping")
    _require_exact_keys(
        authorization,
        _EXTENSION_AUTHORIZATION_FIELDS,
        label="authorization",
    )
    if any(authorization[field] is not False for field in _EXTENSION_AUTHORIZATION_FIELDS):
        raise ValueError(
            "extension authorization fields must all be false"
        )

    projected_dataset = {
        "schema_version": _SCHEMA_VERSION,
        "artifact_type": _ARTIFACT_TYPE,
        "source_checkpoint": source_checkpoint,
        "source_decision_packet_sha256": source_decision_packet_sha256,
        "mapping_record_count": mapping_record_count,
        "mappings": mappings_value,
        "authorization": authorization,
    }

    records = materialize_canonical_knowledge_taxonomy_mapping_records(
        projected_dataset
    )

    explicit_knowledge_ids = tuple(
        row["knowledge_id"] for row in mappings_value
    )
    if explicit_knowledge_ids != binding_knowledge_ids:
        raise ValueError(
            "canonical_binding.knowledge_ids does not match extension mappings"
        )

    for index, row in enumerate(mappings_value):
        if row["product_id"] != scope_product_id:
            raise ValueError(
                f"mappings[{index}].product_id does not match extension scope"
            )
        if row["variant_id"] != scope_variant_id:
            raise ValueError(
                f"mappings[{index}].variant_id does not match extension scope"
            )

    if corrected_l_single_record_scope_mode:
        if binding_knowledge_ids != (
            _CORRECTED_L_SINGLE_RECORD_KNOWLEDGE_ID,
        ):
            raise ValueError(
                "corrected-L single-record canonical binding must contain exact corrected-L knowledge_id"
            )
        corrected_row = mappings_value[0]
        expected_corrected_row = {
            "governed_knowledge_id": (
                _CORRECTED_L_SINGLE_RECORD_GOVERNED_KNOWLEDGE_ID
            ),
            "knowledge_id": _CORRECTED_L_SINGLE_RECORD_KNOWLEDGE_ID,
            "product_id": _CORRECTED_L_SINGLE_RECORD_PRODUCT_ID,
            "variant_id": _CORRECTED_L_SINGLE_RECORD_VARIANT_ID,
            "source_id": _CORRECTED_L_SINGLE_RECORD_SOURCE_ID,
            "source_asset_id": _CORRECTED_L_SINGLE_RECORD_SOURCE_ASSET_ID,
            "knowledge_type": _CORRECTED_L_SINGLE_RECORD_KNOWLEDGE_TYPE,
            "subject": _CORRECTED_L_SINGLE_RECORD_SUBJECT,
            "property": _CORRECTED_L_SINGLE_RECORD_PROPERTY,
        }
        if dict(corrected_row) != expected_corrected_row:
            raise ValueError(
                "corrected-L single-record extension mapping must match exact corrected-L mapping row"
            )

    explicit_governed_ids = tuple(
        row["governed_knowledge_id"] for row in mappings_value
    )
    records_by_governed_id = {
        record.governed_knowledge_id: record
        for record in records
    }
    if set(records_by_governed_id) != set(explicit_governed_ids):
        raise ValueError(
            "materialized extension governed_knowledge_id set mismatch"
        )

    return tuple(
        records_by_governed_id[governed_knowledge_id]
        for governed_knowledge_id in explicit_governed_ids
    )
