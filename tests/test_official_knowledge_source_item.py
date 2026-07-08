from dataclasses import fields

import pytest

from knowledge.official_knowledge_source_item import (
    OfficialKnowledgeSourceItem,
)


def test_creates_valid_curated_official_knowledge_source_item():
    item = OfficialKnowledgeSourceItem(
        knowledge_id="BK-001",
        source_path="official/example.pdf",
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

    assert item.knowledge_id == "BK-001"
    assert item.source_path == "official/example.pdf"
    assert item.source_document == "Example Official Knowledge Base"
    assert item.source_section == "Example Section"
    assert item.source_page == 1
    assert item.title == "Example Locked Knowledge"
    assert item.content == "Example official knowledge content."
    assert item.status == "LOCKED"
    assert item.governance_level == "OFFICIAL SOURCE OF TRUTH"
    assert item.pdf_evidence_index == 0
    assert item.extraction_index == 0


def test_knowledge_id_can_be_none():
    item = OfficialKnowledgeSourceItem(
        knowledge_id=None,
        source_path="official/example.pdf",
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

    assert item.knowledge_id is None


def test_optional_traceability_fields_can_be_none():
    item = OfficialKnowledgeSourceItem(
        knowledge_id=None,
        source_path="official/example.pdf",
        source_document="Example Official Knowledge Base",
        source_section=None,
        source_page=None,
        title="Example Locked Knowledge",
        content="Example official knowledge content.",
        status=None,
        governance_level=None,
        pdf_evidence_index=None,
        extraction_index=None,
    )

    assert item.source_section is None
    assert item.source_page is None
    assert item.status is None
    assert item.governance_level is None
    assert item.pdf_evidence_index is None
    assert item.extraction_index is None


def test_required_string_fields_cannot_be_empty():
    required_fields = [
        "source_path",
        "source_document",
        "title",
        "content",
    ]

    for field_name in required_fields:
        values = {
            "knowledge_id": None,
            "source_path": "official/example.pdf",
            "source_document": "Example Official Knowledge Base",
            "source_section": None,
            "source_page": None,
            "title": "Example Locked Knowledge",
            "content": "Example official knowledge content.",
            "status": None,
            "governance_level": None,
            "pdf_evidence_index": None,
            "extraction_index": None,
        }
        values[field_name] = ""

        with pytest.raises(ValueError, match=field_name):
            OfficialKnowledgeSourceItem(**values)


def test_official_knowledge_source_item_exposes_no_forbidden_fields():
    item = OfficialKnowledgeSourceItem(
        knowledge_id=None,
        source_path="official/example.pdf",
        source_document="Example Official Knowledge Base",
        source_section=None,
        source_page=None,
        title="Example Locked Knowledge",
        content="Example official knowledge content.",
        status=None,
        governance_level=None,
        pdf_evidence_index=None,
        extraction_index=None,
    )

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
