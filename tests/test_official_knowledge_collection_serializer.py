import json

from knowledge.official_knowledge_collection import OfficialKnowledgeCollection
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


def test_serializes_one_official_knowledge_item_to_expected_dict_shape():
    collection = OfficialKnowledgeCollector.collect([make_source_item()])

    serialized = OfficialKnowledgeCollectionSerializer.to_dict(collection)

    assert serialized == {
        "official_knowledge_items": [
            {
                "knowledge_id": "BK-001",
                "source_path": "official/example.pdf",
                "source_document": "Example Official Knowledge Base",
                "source_section": "Example Section",
                "source_page": 1,
                "title": "Example Locked Knowledge",
                "content": "Example official knowledge content.",
                "status": "LOCKED",
                "governance_level": "OFFICIAL SOURCE OF TRUTH",
                "pdf_evidence_index": 0,
                "extraction_index": 0,
                "official_knowledge_index": 0,
            },
        ],
    }


def test_serializes_optional_none_fields_as_none():
    collection = OfficialKnowledgeCollector.collect(
        [
            make_source_item(
                knowledge_id=None,
                source_section=None,
                source_page=None,
                status=None,
                governance_level=None,
                pdf_evidence_index=None,
                extraction_index=None,
            ),
        ],
    )

    serialized_item = (
        OfficialKnowledgeCollectionSerializer.to_dict(collection)[
            "official_knowledge_items"
        ][0]
    )

    assert serialized_item["knowledge_id"] is None
    assert serialized_item["source_section"] is None
    assert serialized_item["source_page"] is None
    assert serialized_item["status"] is None
    assert serialized_item["governance_level"] is None
    assert serialized_item["pdf_evidence_index"] is None
    assert serialized_item["extraction_index"] is None


def test_serializes_multiple_items_preserving_order_and_indexes():
    collection = OfficialKnowledgeCollector.collect(
        [
            make_source_item(knowledge_id="BK-001", title="First"),
            make_source_item(knowledge_id="BK-002", title="Second"),
            make_source_item(knowledge_id="BK-003", title="Third"),
        ],
    )

    serialized_items = OfficialKnowledgeCollectionSerializer.to_dict(
        collection
    )["official_knowledge_items"]

    assert [
        item["title"]
        for item in serialized_items
    ] == [
        "First",
        "Second",
        "Third",
    ]
    assert [
        item["official_knowledge_index"]
        for item in serialized_items
    ] == [0, 1, 2]


def test_serializes_empty_collection():
    collection = OfficialKnowledgeCollection(
        official_knowledge_items=[],
    )

    assert OfficialKnowledgeCollectionSerializer.to_dict(collection) == {
        "official_knowledge_items": [],
    }


def test_serializer_output_includes_no_forbidden_fields():
    collection = OfficialKnowledgeCollector.collect([make_source_item()])

    serialized = OfficialKnowledgeCollectionSerializer.to_dict(collection)

    forbidden_fields = {
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

    assert not forbidden_fields.intersection(serialized)

    for item in serialized["official_knowledge_items"]:
        assert not forbidden_fields.intersection(item)


def test_to_json_preserves_none_as_json_null_and_non_ascii_content():
    collection = OfficialKnowledgeCollector.collect(
        [
            make_source_item(
                knowledge_id=None,
                content="Example official knowledge content with café.",
            ),
        ],
    )

    serialized_json = OfficialKnowledgeCollectionSerializer.to_json(
        collection
    )

    assert '"knowledge_id": null' in serialized_json
    assert "café" in serialized_json
    assert json.loads(serialized_json) == (
        OfficialKnowledgeCollectionSerializer.to_dict(collection)
    )
