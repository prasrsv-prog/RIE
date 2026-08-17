from __future__ import annotations

from copy import deepcopy

import pytest

from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
    materialize_canonical_knowledge_taxonomy_mapping_records,
)
from rie.rsv_knowledge.governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)


def _row(
    governed_knowledge_id: str,
    knowledge_id: str,
    product_id: str,
) -> dict[str, object]:
    return {
        "governed_knowledge_id": governed_knowledge_id,
        "knowledge_id": knowledge_id,
        "product_id": product_id,
        "variant_id": None,
        "source_id": f"source-{product_id}",
        "source_asset_id": f"asset-{product_id}",
        "knowledge_type": "product_manual",
        "subject": product_id,
        "property": "official_manual_content",
    }


def _dataset() -> dict[str, object]:
    return {
        "schema_version": 1,
        "artifact_type": (
            "pilot_authoritative_knowledge_taxonomy_mapping_canonical_data"
        ),
        "source_checkpoint": "checkpoint",
        "source_decision_packet_sha256": "packet-sha",
        "mapping_record_count": 3,
        "mappings": [
            _row("gk-z", "knowledge-z", "sv300"),
            _row("gk-a", "knowledge-a", "ffs21"),
            _row("gk-m", "knowledge-m", "new-windtail"),
        ],
        "authorization": {
            "external_canonical_mapping_data_materialization_authorized": True,
            "decision_packet_mutation_authorized": False,
            "repository_implementation_authorized": False,
            "canonical_constraint_data_write_authorized": False,
            "concrete_constraint_creation_authorized": False,
            "semantic_inference_authorized": False,
        },
    }


def test_materializes_three_records_deterministically() -> None:
    result = materialize_canonical_knowledge_taxonomy_mapping_records(_dataset())

    assert isinstance(result, tuple)
    assert all(
        isinstance(item, GovernedKnowledgePromptInputMappingRecord)
        for item in result
    )
    assert [item.governed_knowledge_id for item in result] == [
        "gk-a",
        "gk-m",
        "gk-z",
    ]


def test_preserves_every_mapping_field_exactly() -> None:
    dataset = _dataset()
    rows = {
        row["governed_knowledge_id"]: row
        for row in dataset["mappings"]
    }

    result = materialize_canonical_knowledge_taxonomy_mapping_records(dataset)

    for item in result:
        row = rows[item.governed_knowledge_id]
        assert item.knowledge_id == row["knowledge_id"]
        assert item.product_id == row["product_id"]
        assert item.variant_id == row["variant_id"]
        assert item.source_id == row["source_id"]
        assert item.source_asset_id == row["source_asset_id"]
        assert item.knowledge_type == row["knowledge_type"]
        assert item.subject == row["subject"]
        assert item.property == row["property"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", 2),
        ("schema_version", True),
        ("artifact_type", "wrong"),
        ("source_checkpoint", ""),
        ("source_decision_packet_sha256", ""),
        ("mapping_record_count", 0),
        ("mapping_record_count", True),
    ],
)
def test_invalid_metadata_fails_closed(field: str, value: object) -> None:
    dataset = _dataset()
    dataset[field] = value

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_record_count_mismatch_fails_closed() -> None:
    dataset = _dataset()
    dataset["mapping_record_count"] = 2

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_empty_mapping_set_fails_closed() -> None:
    dataset = _dataset()
    dataset["mapping_record_count"] = 0
    dataset["mappings"] = []

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_missing_mapping_field_fails_closed() -> None:
    dataset = _dataset()
    del dataset["mappings"][0]["property"]

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_extra_mapping_field_fails_closed() -> None:
    dataset = _dataset()
    dataset["mappings"][0]["unexpected"] = "value"

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_duplicate_governed_knowledge_id_fails_closed() -> None:
    dataset = _dataset()
    dataset["mappings"][1]["governed_knowledge_id"] = (
        dataset["mappings"][0]["governed_knowledge_id"]
    )

    with pytest.raises(ValueError, match="duplicate governed_knowledge_id"):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_duplicate_knowledge_id_fails_closed() -> None:
    dataset = _dataset()
    dataset["mappings"][1]["knowledge_id"] = (
        dataset["mappings"][0]["knowledge_id"]
    )

    with pytest.raises(ValueError, match="duplicate knowledge_id"):
        materialize_canonical_knowledge_taxonomy_mapping_records(dataset)


def test_variant_id_string_is_preserved_without_inference() -> None:
    dataset = _dataset()
    dataset["mappings"][0]["variant_id"] = "explicit-variant"

    result = materialize_canonical_knowledge_taxonomy_mapping_records(dataset)

    by_governed_id = {
        item.governed_knowledge_id: item
        for item in result
    }
    assert by_governed_id["gk-z"].variant_id == "explicit-variant"


def test_mapping_rows_are_not_mutated() -> None:
    dataset = _dataset()
    before = deepcopy(dataset)

    materialize_canonical_knowledge_taxonomy_mapping_records(dataset)

    assert dataset == before


def test_dataset_root_missing_or_extra_field_fails_closed() -> None:
    missing = _dataset()
    del missing["authorization"]
    extra = _dataset()
    extra["constraint_specs"] = []

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(missing)
    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_records(extra)

def _extension_dataset() -> dict[str, object]:
    mappings = [
        _row(f"gk-{index}", f"knowledge-{index}", "ffs21")
        for index in range(5)
    ]
    return {
        "schema_version": 1,
        "artifact_type": (
            "rcis_authoritative_knowledge_taxonomy_mapping_extension"
        ),
        "extension_id": "extension-five",
        "extension_role": "provenance-preserving-extension",
        "base_mapping_reference": {
            "filename": "base.json",
            "sha256": "a" * 64,
            "bytes": 100,
            "lf": 1,
            "mapping_record_count": 3,
            "source_decision_packet_sha256": "b" * 64,
        },
        "extension_provenance": {
            "source_decision_packet_filename": "atomic.json",
            "source_decision_packet_sha256": "c" * 64,
            "governed_repository_sha256": "d" * 64,
            "code_checkpoint": "e" * 40,
            "source_pr086cg_report_sha256": "f" * 64,
        },
        "scope": {
            "product_id": "ffs21",
            "variant_id": None,
            "exact_five_facts_only": True,
            "corrected_l_excluded": True,
            "other_products_or_facts_authorized": False,
        },
        "canonical_binding": {
            "product_id": "ffs21",
            "variant_id": None,
            "knowledge_ids": [
                row["knowledge_id"] for row in mappings
            ],
        },
        "mapping_record_count": 5,
        "mappings": mappings,
        "authorization": {
            "existing_base_mapping_mutation_authorized": False,
            "governed_repository_write_authorized": False,
            "evidence_repository_write_authorized": False,
            "source_code_mutation_authorized": False,
            "git_mutation_authorized": False,
            "network_operation_authorized": False,
            "semantic_inference_authorized": False,
        },
    }


def test_existing_v1_materializer_remains_strict_for_extension_shape() -> None:
    with pytest.raises(ValueError, match="fields mismatch"):
        materialize_canonical_knowledge_taxonomy_mapping_records(
            _extension_dataset()
        )


def test_extension_adapter_materializes_five_records_deterministically() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    result = materialize_canonical_knowledge_taxonomy_mapping_extension_records(
        dataset
    )

    assert len(result) == 5
    assert all(
        isinstance(item, GovernedKnowledgePromptInputMappingRecord)
        for item in result
    )
    assert [item.governed_knowledge_id for item in result] == [
        "gk-0",
        "gk-1",
        "gk-2",
        "gk-3",
        "gk-4",
    ]


def test_extension_adapter_preserves_mapping_fields() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    rows = {
        row["governed_knowledge_id"]: row
        for row in dataset["mappings"]
    }
    result = materialize_canonical_knowledge_taxonomy_mapping_extension_records(
        dataset
    )

    for item in result:
        row = rows[item.governed_knowledge_id]
        assert item.knowledge_id == row["knowledge_id"]
        assert item.product_id == row["product_id"]
        assert item.variant_id == row["variant_id"]
        assert item.source_id == row["source_id"]
        assert item.source_asset_id == row["source_asset_id"]
        assert item.knowledge_type == row["knowledge_type"]
        assert item.subject == row["subject"]
        assert item.property == row["property"]


def test_extension_adapter_does_not_mutate_input() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    before = deepcopy(dataset)

    materialize_canonical_knowledge_taxonomy_mapping_extension_records(
        dataset
    )

    assert dataset == before


def test_extension_adapter_rejects_missing_or_extra_root_field() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    missing = _extension_dataset()
    del missing["extension_role"]
    extra = _extension_dataset()
    extra["unexpected"] = "value"

    with pytest.raises(ValueError, match="fields mismatch"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            missing
        )
    with pytest.raises(ValueError, match="fields mismatch"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            extra
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", 2),
        ("artifact_type", "wrong"),
    ],
)
def test_extension_adapter_rejects_invalid_root_contract(
    field: str,
    value: object,
) -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    dataset[field] = value

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            dataset
        )


def test_extension_adapter_rejects_provenance_field_drift() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    del dataset["extension_provenance"]["source_pr086cg_report_sha256"]

    with pytest.raises(ValueError, match="fields mismatch"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            dataset
        )


def test_extension_adapter_rejects_base_reference_field_drift() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    dataset["base_mapping_reference"]["extra"] = "value"

    with pytest.raises(ValueError, match="fields mismatch"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            dataset
        )


def test_extension_adapter_rejects_scope_or_binding_mismatch() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    bad_scope = _extension_dataset()
    bad_scope["scope"]["corrected_l_excluded"] = False
    bad_binding = _extension_dataset()
    bad_binding["canonical_binding"]["knowledge_ids"][0] = "other"

    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            bad_scope
        )
    with pytest.raises(ValueError):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            bad_binding
        )


def test_extension_adapter_rejects_authorization_escalation() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    dataset["authorization"]["git_mutation_authorized"] = True

    with pytest.raises(ValueError, match="authorization"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            dataset
        )


def test_extension_adapter_reuses_existing_duplicate_guards() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    duplicate = _extension_dataset()
    duplicate["mappings"][1]["knowledge_id"] = (
        duplicate["mappings"][0]["knowledge_id"]
    )
    duplicate["canonical_binding"]["knowledge_ids"][1] = (
        duplicate["canonical_binding"]["knowledge_ids"][0]
    )

    with pytest.raises(ValueError, match="duplicate"):
        materialize_canonical_knowledge_taxonomy_mapping_extension_records(
            duplicate
        )

def test_extension_adapter_preserves_nonlexicographic_mapping_order() -> None:
    from rie.rsv_knowledge.canonical_knowledge_taxonomy_mapping_materialization import (
        materialize_canonical_knowledge_taxonomy_mapping_extension_records,
    )

    dataset = _extension_dataset()
    original_mappings = list(dataset["mappings"])
    order = (2, 0, 4, 3, 1)
    dataset["mappings"] = [
        original_mappings[index] for index in order
    ]
    dataset["canonical_binding"]["knowledge_ids"] = [
        row["knowledge_id"] for row in dataset["mappings"]
    ]

    result = materialize_canonical_knowledge_taxonomy_mapping_extension_records(
        dataset
    )

    assert [record.knowledge_id for record in result] == [
        row["knowledge_id"] for row in dataset["mappings"]
    ]
    assert [record.governed_knowledge_id for record in result] == [
        row["governed_knowledge_id"] for row in dataset["mappings"]
    ]
