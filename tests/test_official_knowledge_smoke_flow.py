from dataclasses import replace

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


def test_official_knowledge_end_to_end_smoke_flow():
    first_source_item = OfficialKnowledgeSourceItem(
        knowledge_id="BK-001",
        source_path="docs/example_official_knowledge_base.pdf",
        source_document="Example Official Knowledge Base",
        source_section="Example Section",
        source_page=1,
        title="Example Locked Knowledge",
        content="Example official knowledge content.",
        status="LOCKED",
        governance_level="OFFICIAL SOURCE OF TRUTH",
        pdf_evidence_index=0,
        extraction_index=0,
    )
    second_source_item = OfficialKnowledgeSourceItem(
        knowledge_id=None,
        source_path="docs/example_official_knowledge_base.pdf",
        source_document="Example Official Knowledge Base",
        source_section="Example Section",
        source_page=2,
        title="Example Locked Knowledge Without Governance",
        content="Second example official knowledge content.",
        status=None,
        governance_level=None,
        pdf_evidence_index=1,
        extraction_index=1,
    )
    source_items = [
        first_source_item,
        second_source_item,
    ]
    original_source_items = [
        replace(first_source_item),
        replace(second_source_item),
    ]

    collection = OfficialKnowledgeCollector.collect(source_items)
    artifact = OfficialKnowledgeCollectionSerializer.to_dict(collection)
    inspection = OfficialKnowledgeArtifactInspector.inspect(artifact)

    assert source_items == original_source_items

    assert [
        item.official_knowledge_index
        for item in collection.official_knowledge_items
    ] == [0, 1]

    assert "official_knowledge_items" in artifact
    official_knowledge_items = artifact["official_knowledge_items"]

    assert [
        item["title"]
        for item in official_knowledge_items
    ] == [
        "Example Locked Knowledge",
        "Example Locked Knowledge Without Governance",
    ]
    assert [
        item["official_knowledge_index"]
        for item in official_knowledge_items
    ] == [0, 1]

    assert official_knowledge_items[0]["source_path"] == (
        "docs/example_official_knowledge_base.pdf"
    )
    assert official_knowledge_items[0]["source_document"] == (
        "Example Official Knowledge Base"
    )
    assert official_knowledge_items[0]["source_section"] == (
        "Example Section"
    )
    assert official_knowledge_items[0]["source_page"] == 1
    assert official_knowledge_items[0]["content"] == (
        "Example official knowledge content."
    )

    assert official_knowledge_items[0]["status"] == "LOCKED"
    assert official_knowledge_items[0]["governance_level"] == (
        "OFFICIAL SOURCE OF TRUTH"
    )
    assert official_knowledge_items[1]["status"] is None
    assert official_knowledge_items[1]["governance_level"] is None

    assert inspection.total_official_knowledge_items == 2
    assert inspection.missing_required_traceability_count == 0
    assert inspection.missing_governance_count == 1
    assert inspection.forbidden_field_count == 0
    assert inspection.index_mismatch_count == 0
    assert inspection.is_valid is True

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

    assert not forbidden_fields.intersection(artifact)

    for item in official_knowledge_items:
        assert not forbidden_fields.intersection(item)
