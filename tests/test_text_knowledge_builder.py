from dataclasses import fields

import pytest

from knowledge.text_knowledge import TextKnowledge
from knowledge.text_knowledge_builder import TextKnowledgeBuilder


def test_builds_text_knowledge_from_valid_evidence_record():
    record = {
        "source_path": "prompt.dat",
        "content": "Generate a helmet concept.",
        "size_bytes": 26,
    }

    knowledge = TextKnowledgeBuilder.build(
        evidence_record=record,
        evidence_index=0,
    )

    assert isinstance(knowledge, TextKnowledge)
    assert knowledge.source_path == "prompt.dat"
    assert knowledge.content == "Generate a helmet concept."
    assert knowledge.size_bytes == 26
    assert knowledge.evidence_index == 0


def test_preserves_content_exactly_including_non_ascii_and_newlines():
    content = "Line 1\nCaf\u00e9 racer helmet\nRancang helm RSV.\n"
    record = {
        "source_path": "prompt.dat",
        "content": content,
        "size_bytes": 44,
    }

    knowledge = TextKnowledgeBuilder.build(
        evidence_record=record,
        evidence_index=3,
    )

    assert knowledge.content == content


def test_preserves_source_path_size_bytes_and_evidence_index():
    record = {
        "source_path": "D:\\PROJECT\\RIE\\prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
    }

    knowledge = TextKnowledgeBuilder.build(
        evidence_record=record,
        evidence_index=7,
    )

    assert knowledge.source_path == "D:\\PROJECT\\RIE\\prompt.dat"
    assert knowledge.size_bytes == 6
    assert knowledge.evidence_index == 7


def test_builder_rejects_missing_required_fields():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
    }

    with pytest.raises(ValueError):
        TextKnowledgeBuilder.build(
            evidence_record=record,
            evidence_index=0,
        )


def test_builder_rejects_extra_fields():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
        "summary": "Do not summarize.",
    }

    with pytest.raises(ValueError):
        TextKnowledgeBuilder.build(
            evidence_record=record,
            evidence_index=0,
        )


def test_builder_rejects_wrong_field_types():
    records = [
        {
            "source_path": 123,
            "content": "Prompt",
            "size_bytes": 6,
        },
        {
            "source_path": "prompt.dat",
            "content": ["Prompt"],
            "size_bytes": 6,
        },
        {
            "source_path": "prompt.dat",
            "content": "Prompt",
            "size_bytes": "6",
        },
    ]

    for record in records:
        with pytest.raises(ValueError):
            TextKnowledgeBuilder.build(
                evidence_record=record,
                evidence_index=0,
            )


def test_builder_rejects_bool_size_bytes():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
        "size_bytes": True,
    }

    with pytest.raises(ValueError):
        TextKnowledgeBuilder.build(
            evidence_record=record,
            evidence_index=0,
        )


def test_text_knowledge_exposes_no_summary_category_embedding_prompt_analysis_or_size_class():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
    }

    knowledge = TextKnowledgeBuilder.build(
        evidence_record=record,
        evidence_index=0,
    )

    assert [field.name for field in fields(knowledge)] == [
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
    ]
    assert not hasattr(knowledge, "summary")
    assert not hasattr(knowledge, "category")
    assert not hasattr(knowledge, "embedding")
    assert not hasattr(knowledge, "prompt")
    assert not hasattr(knowledge, "analysis")
    assert not hasattr(knowledge, "size_class")
