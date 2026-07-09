from copy import deepcopy

import pytest

from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType
from official_source.official_source_registry_loader import (
    OfficialSourceRegistryLoader,
)


def _item(**overrides):
    item = {
        "source_id": "SRC-001",
        "source_path": "docs/synthetic-official-source.pdf",
        "source_type": "pdf",
        "document_classification": "project_rulebook",
        "authority_status": "source_of_truth_candidate",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible_with_review",
        "version": "v1.0",
        "review_notes": "Synthetic example only.",
    }
    item.update(overrides)
    return item


def _registry(items):
    return {
        "official_sources": items,
    }


def test_valid_mapping_returns_ordered_official_source_objects():
    sources = OfficialSourceRegistryLoader.load_from_mapping(
        _registry([
            _item(source_id="SRC-001", source_path="docs/source-001.pdf"),
            _item(source_id="SRC-002", source_path="docs/source-002.md"),
        ]),
    )

    assert len(sources) == 2
    assert all(isinstance(source, OfficialSource) for source in sources)
    assert [source.source_id for source in sources] == [
        "SRC-001",
        "SRC-002",
    ]
    assert sources[0].source_path == "docs/source-001.pdf"
    assert sources[0].source_type == SourceType.PDF
    assert sources[0].document_classification == (
        DocumentClassification.PROJECT_RULEBOOK
    )
    assert sources[0].authority_status == (
        AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE
    )
    assert sources[0].lifecycle_status == LifecycleStatus.LOCKED
    assert sources[0].evidence_eligibility == (
        EvidenceEligibility.ELIGIBLE_WITH_REVIEW
    )
    assert sources[0].version == "v1.0"
    assert sources[0].review_notes == "Synthetic example only."


def test_empty_official_sources_returns_empty_list():
    assert OfficialSourceRegistryLoader.load_from_mapping(
        _registry([]),
    ) == []


def test_non_mapping_top_level_input_fails():
    with pytest.raises(TypeError, match="mapping"):
        OfficialSourceRegistryLoader.load_from_mapping([])


def test_missing_top_level_official_sources_fails():
    with pytest.raises(ValueError, match="official_sources"):
        OfficialSourceRegistryLoader.load_from_mapping({})


def test_unknown_top_level_key_fails():
    with pytest.raises(ValueError, match="official_sources"):
        OfficialSourceRegistryLoader.load_from_mapping(
            {
                "official_sources": [],
                "unknown": [],
            },
        )


def test_official_sources_that_is_not_list_fails():
    with pytest.raises(TypeError, match="list"):
        OfficialSourceRegistryLoader.load_from_mapping(
            {
                "official_sources": {},
            },
        )


def test_non_mapping_item_fails():
    with pytest.raises(TypeError, match="object"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry(["not an item"]),
        )


def test_missing_required_fields_fail():
    for field_name in [
        "source_id",
        "source_path",
        "source_type",
        "document_classification",
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
    ]:
        item = _item()
        del item[field_name]

        with pytest.raises(ValueError, match=field_name):
            OfficialSourceRegistryLoader.load_from_mapping(
                _registry([item]),
            )


def test_blank_source_id_fails():
    with pytest.raises(ValueError, match="source_id"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry([_item(source_id="")]),
        )


def test_blank_source_path_fails():
    with pytest.raises(ValueError, match="source_path"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry([_item(source_path="")]),
        )


def test_duplicate_source_id_fails():
    with pytest.raises(ValueError, match="duplicate source_id"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry([
                _item(source_id="SRC-001"),
                _item(source_id="SRC-001"),
            ]),
        )


def test_invalid_enum_string_fails():
    enum_fields = [
        "source_type",
        "document_classification",
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
    ]

    for field_name in enum_fields:
        with pytest.raises(ValueError, match=field_name):
            OfficialSourceRegistryLoader.load_from_mapping(
                _registry([_item(**{field_name: "not_valid"})]),
            )


def test_explicit_unknown_enum_values_pass():
    sources = OfficialSourceRegistryLoader.load_from_mapping(
        _registry([
            _item(
                source_type="unknown",
                document_classification="unknown",
                authority_status="unknown",
                lifecycle_status="unknown",
                evidence_eligibility="unknown",
            ),
        ]),
    )

    assert sources[0].source_type == SourceType.UNKNOWN
    assert sources[0].document_classification == (
        DocumentClassification.UNKNOWN
    )
    assert sources[0].authority_status == AuthorityStatus.UNKNOWN
    assert sources[0].lifecycle_status == LifecycleStatus.UNKNOWN
    assert sources[0].evidence_eligibility == EvidenceEligibility.UNKNOWN


def test_unknown_item_field_fails():
    with pytest.raises(ValueError, match="unknown field"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry([_item(unexpected="Do not accept.")]),
        )


def test_source_local_id_fails_until_supported():
    with pytest.raises(ValueError, match="source_local_id"):
        OfficialSourceRegistryLoader.load_from_mapping(
            _registry([_item(source_local_id="LOCAL-001")]),
        )


def test_forbidden_downstream_fields_fail():
    forbidden_fields = [
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
    ]

    for field_name in forbidden_fields:
        with pytest.raises(ValueError, match="forbidden field"):
            OfficialSourceRegistryLoader.load_from_mapping(
                _registry([_item(**{field_name: "Do not accept."})]),
            )


def test_nonexistent_source_path_passes_as_string_reference():
    sources = OfficialSourceRegistryLoader.load_from_mapping(
        _registry([
            _item(source_path="docs/not-a-real-synthetic-source.pdf"),
        ]),
    )

    assert sources[0].source_path == "docs/not-a-real-synthetic-source.pdf"


def test_deprecated_and_superseded_lifecycle_entries_remain_returned():
    sources = OfficialSourceRegistryLoader.load_from_mapping(
        _registry([
            _item(source_id="SRC-001", lifecycle_status="deprecated"),
            _item(source_id="SRC-002", lifecycle_status="superseded"),
        ]),
    )

    assert [source.lifecycle_status for source in sources] == [
        LifecycleStatus.DEPRECATED,
        LifecycleStatus.SUPERSEDED,
    ]


def test_input_order_is_preserved():
    sources = OfficialSourceRegistryLoader.load_from_mapping(
        _registry([
            _item(source_id="SRC-003"),
            _item(source_id="SRC-001"),
            _item(source_id="SRC-002"),
        ]),
    )

    assert [source.source_id for source in sources] == [
        "SRC-003",
        "SRC-001",
        "SRC-002",
    ]


def test_input_is_not_mutated():
    registry = _registry([_item()])
    original_registry = deepcopy(registry)

    OfficialSourceRegistryLoader.load_from_mapping(registry)

    assert registry == original_registry


def test_test_data_is_synthetic():
    item = _item()

    assert "synthetic" in item["source_path"]
    assert item["review_notes"] == "Synthetic example only."
