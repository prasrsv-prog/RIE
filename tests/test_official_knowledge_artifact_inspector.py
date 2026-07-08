from copy import deepcopy

from knowledge.official_knowledge_artifact_inspector import (
    OfficialKnowledgeArtifactInspector,
)
from knowledge.official_knowledge_collection_serializer import (
    OfficialKnowledgeCollectionSerializer,
)
from knowledge.official_knowledge_collector import OfficialKnowledgeCollector
from knowledge.official_knowledge_source_item import (
    OfficialKnowledgeSourceItem,
)


def make_source_item(
    *,
    knowledge_id: str | None = "BK-001",
    source_path: str = "official/example.pdf",
    source_document: str = "Example Official Knowledge Base",
    source_section: str | None = "Example Section",
    source_page: int | None = 1,
    title: str = "Example Locked Knowledge",
    content: str = "Example official knowledge content.",
    status: str | None = "LOCKED",
    governance_level: str | None = "OFFICIAL SOURCE OF TRUTH",
    pdf_evidence_index: int | None = 0,
    extraction_index: int | None = 0,
) -> OfficialKnowledgeSourceItem:
    return OfficialKnowledgeSourceItem(
        knowledge_id=knowledge_id,
        source_path=source_path,
        source_document=source_document,
        source_section=source_section,
        source_page=source_page,
        title=title,
        content=content,
        status=status,
        governance_level=governance_level,
        pdf_evidence_index=pdf_evidence_index,
        extraction_index=extraction_index,
    )


def make_artifact(
    source_items: list[OfficialKnowledgeSourceItem] | None = None,
) -> dict:
    if source_items is None:
        source_items = [make_source_item()]

    collection = OfficialKnowledgeCollector.collect(source_items)

    return OfficialKnowledgeCollectionSerializer.to_dict(collection)


def test_inspects_valid_artifact():
    artifact = make_artifact(
        [
            make_source_item(knowledge_id="BK-001", title="First"),
            make_source_item(knowledge_id="BK-002", title="Second"),
        ],
    )

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.total_official_knowledge_items == 2
    assert inspection.missing_required_traceability_count == 0
    assert inspection.missing_governance_count == 0
    assert inspection.forbidden_field_count == 0
    assert inspection.index_mismatch_count == 0
    assert inspection.is_valid is True


def test_empty_official_knowledge_items_list_is_valid():
    inspection = OfficialKnowledgeArtifactInspector.inspect(
        {
            "official_knowledge_items": [],
        },
    )

    assert inspection.total_official_knowledge_items == 0
    assert inspection.is_valid is True


def test_missing_official_knowledge_items_key_is_invalid():
    inspection = OfficialKnowledgeArtifactInspector.inspect({})

    assert inspection.total_official_knowledge_items == 0
    assert inspection.is_valid is False


def test_official_knowledge_items_not_list_is_invalid():
    inspection = OfficialKnowledgeArtifactInspector.inspect(
        {
            "official_knowledge_items": {},
        },
    )

    assert inspection.total_official_knowledge_items == 0
    assert inspection.is_valid is False


def test_missing_or_empty_required_traceability_fields_are_counted():
    artifact = make_artifact(
        [
            make_source_item(knowledge_id="BK-001", title="First"),
            make_source_item(knowledge_id="BK-002", title="Second"),
            make_source_item(knowledge_id="BK-003", title="Third"),
            make_source_item(knowledge_id="BK-004", title="Fourth"),
            make_source_item(knowledge_id="BK-005", title="Fifth"),
        ],
    )
    items = artifact["official_knowledge_items"]
    del items[0]["source_path"]
    items[1]["source_document"] = ""
    items[2]["title"] = None
    items[3]["content"] = "   "
    del items[4]["official_knowledge_index"]

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.total_official_knowledge_items == 5
    assert inspection.missing_required_traceability_count == 5
    assert inspection.index_mismatch_count == 0
    assert inspection.is_valid is False


def test_missing_governance_is_counted_but_does_not_make_artifact_invalid():
    artifact = make_artifact(
        [
            make_source_item(knowledge_id="BK-001", status=None),
            make_source_item(
                knowledge_id="BK-002",
                governance_level="",
            ),
        ],
    )

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.total_official_knowledge_items == 2
    assert inspection.missing_governance_count == 2
    assert inspection.missing_required_traceability_count == 0
    assert inspection.forbidden_field_count == 0
    assert inspection.index_mismatch_count == 0
    assert inspection.is_valid is True


def test_forbidden_fields_are_counted_and_make_artifact_invalid():
    artifact = make_artifact(
        [
            make_source_item(knowledge_id="BK-001", title="First"),
            make_source_item(knowledge_id="BK-002", title="Second"),
        ],
    )
    artifact["official_knowledge_items"][0]["prompt"] = "Do not include."
    artifact["official_knowledge_items"][0]["embedding"] = []
    artifact["official_knowledge_items"][1]["model"] = "Do not include."

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.forbidden_field_count == 3
    assert inspection.is_valid is False


def test_official_knowledge_index_mismatch_is_counted_and_invalid():
    artifact = make_artifact(
        [
            make_source_item(knowledge_id="BK-001", title="First"),
            make_source_item(knowledge_id="BK-002", title="Second"),
        ],
    )
    artifact["official_knowledge_items"][1]["official_knowledge_index"] = 7

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.index_mismatch_count == 1
    assert inspection.is_valid is False


def test_non_dict_item_is_invalid_and_counted_as_missing_traceability():
    artifact = make_artifact()
    artifact["official_knowledge_items"].append("not an item")

    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert inspection.total_official_knowledge_items == 2
    assert inspection.missing_required_traceability_count == 1
    assert inspection.is_valid is False


def test_inspector_does_not_mutate_artifact():
    artifact = make_artifact()
    original_artifact = deepcopy(artifact)

    OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert artifact == original_artifact
