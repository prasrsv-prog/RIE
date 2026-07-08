from dataclasses import fields

from knowledge.official_knowledge_collection import OfficialKnowledgeCollection
from knowledge.official_knowledge_collector import OfficialKnowledgeCollector
from knowledge.official_knowledge_item import OfficialKnowledgeItem
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


def test_collects_one_source_item_into_one_official_knowledge_item():
    source_item = make_source_item()

    collection = OfficialKnowledgeCollector.collect([source_item])

    assert isinstance(collection, OfficialKnowledgeCollection)
    assert len(collection.official_knowledge_items) == 1
    assert isinstance(
        collection.official_knowledge_items[0],
        OfficialKnowledgeItem,
    )


def test_preserves_all_source_fields_exactly():
    source_item = make_source_item(
        knowledge_id="BK-001",
        source_path="official/example.pdf",
        source_document="Example Official Knowledge Base",
        source_section="Example Section",
        source_page=3,
        title="Example Locked Knowledge",
        content="Example official knowledge content.\nPreserve exactly.",
        status="LOCKED",
        governance_level="OFFICIAL SOURCE OF TRUTH",
        pdf_evidence_index=4,
        extraction_index=5,
    )

    collection = OfficialKnowledgeCollector.collect([source_item])
    item = collection.official_knowledge_items[0]

    assert item.knowledge_id == source_item.knowledge_id
    assert item.source_path == source_item.source_path
    assert item.source_document == source_item.source_document
    assert item.source_section == source_item.source_section
    assert item.source_page == source_item.source_page
    assert item.title == source_item.title
    assert item.content == source_item.content
    assert item.status == source_item.status
    assert item.governance_level == source_item.governance_level
    assert item.pdf_evidence_index == source_item.pdf_evidence_index
    assert item.extraction_index == source_item.extraction_index


def test_official_knowledge_index_starts_at_zero():
    collection = OfficialKnowledgeCollector.collect([make_source_item()])

    assert collection.official_knowledge_items[0].official_knowledge_index == 0


def test_multiple_source_items_preserve_order_and_receive_indexes():
    source_items = [
        make_source_item(knowledge_id="BK-001", title="First"),
        make_source_item(knowledge_id="BK-002", title="Second"),
        make_source_item(knowledge_id="BK-003", title="Third"),
    ]

    collection = OfficialKnowledgeCollector.collect(source_items)

    assert [
        item.title
        for item in collection.official_knowledge_items
    ] == [
        "First",
        "Second",
        "Third",
    ]
    assert [
        item.official_knowledge_index
        for item in collection.official_knowledge_items
    ] == [0, 1, 2]


def test_knowledge_id_remains_none_when_source_knowledge_id_is_none():
    source_item = make_source_item(knowledge_id=None)

    collection = OfficialKnowledgeCollector.collect([source_item])

    assert collection.official_knowledge_items[0].knowledge_id is None


def test_collector_does_not_skip_duplicate_content():
    source_items = [
        make_source_item(knowledge_id="BK-001"),
        make_source_item(knowledge_id="BK-002"),
    ]

    collection = OfficialKnowledgeCollector.collect(source_items)

    assert len(collection.official_knowledge_items) == 2
    assert collection.official_knowledge_items[0].content == (
        collection.official_knowledge_items[1].content
    )
    assert [
        item.official_knowledge_index
        for item in collection.official_knowledge_items
    ] == [0, 1]


def test_empty_source_list_returns_empty_collection():
    collection = OfficialKnowledgeCollector.collect([])

    assert isinstance(collection, OfficialKnowledgeCollection)
    assert collection.official_knowledge_items == []


def test_official_knowledge_item_and_collection_expose_no_forbidden_fields():
    collection = OfficialKnowledgeCollector.collect([make_source_item()])
    item = collection.official_knowledge_items[0]

    assert [field.name for field in fields(item)] == [
        "knowledge_id",
        "source_path",
        "source_document",
        "source_section",
        "source_page",
        "title",
        "content",
        "status",
        "governance_level",
        "pdf_evidence_index",
        "extraction_index",
        "official_knowledge_index",
    ]
    assert [field.name for field in fields(collection)] == [
        "official_knowledge_items",
    ]

    forbidden_fields = [
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
    ]

    for field_name in forbidden_fields:
        assert not hasattr(item, field_name)
        assert not hasattr(collection, field_name)
