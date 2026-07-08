import pytest

from prompting.text_prompt_candidate import TextPromptCandidate
from prompting.text_prompt_candidate_builder import TextPromptCandidateBuilder


def test_builder_preserves_content_exactly():
    record = {
        "source_path": "prompt.dat",
        "content": "Generate a helmet concept.",
        "size_bytes": 26,
        "evidence_index": 4,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=2,
    )

    assert isinstance(candidate, TextPromptCandidate)
    assert candidate.content == "Generate a helmet concept."


def test_builder_preserves_non_ascii_content():
    content = "Caf\u00e9 racer helm: Rancang konsep."
    record = {
        "source_path": "prompt.dat",
        "content": content,
        "size_bytes": 34,
        "evidence_index": 1,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=0,
    )

    assert candidate.content == content


def test_builder_preserves_newline_content():
    content = "Line 1\nLine 2\n"
    record = {
        "source_path": "prompt.dat",
        "content": content,
        "size_bytes": 14,
        "evidence_index": 2,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=1,
    )

    assert candidate.content == content


def test_builder_preserves_empty_content():
    record = {
        "source_path": "empty.dat",
        "content": "",
        "size_bytes": 0,
        "evidence_index": 3,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=2,
    )

    assert candidate.content == ""


def test_builder_copies_source_path_size_bytes_and_evidence_index():
    record = {
        "source_path": "D:\\PROJECT\\RIE\\prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
        "evidence_index": 7,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=4,
    )

    assert candidate.source_path == "D:\\PROJECT\\RIE\\prompt.dat"
    assert candidate.size_bytes == 6
    assert candidate.evidence_index == 7


def test_builder_adds_knowledge_index():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
        "evidence_index": 0,
    }

    candidate = TextPromptCandidateBuilder.build(
        knowledge_record=record,
        knowledge_index=5,
    )

    assert candidate.knowledge_index == 5


def test_builder_rejects_invalid_text_knowledge_records():
    records = [
        "not a record",
        {
            "source_path": "missing-index.dat",
            "content": "Prompt",
            "size_bytes": 6,
        },
        {
            "source_path": "extra-field.dat",
            "content": "Prompt",
            "size_bytes": 6,
            "evidence_index": 0,
            "summary": "Do not summarize.",
        },
        {
            "source_path": 123,
            "content": "Prompt",
            "size_bytes": 6,
            "evidence_index": 0,
        },
        {
            "source_path": "content-list.dat",
            "content": ["Prompt"],
            "size_bytes": 6,
            "evidence_index": 0,
        },
        {
            "source_path": "size-string.dat",
            "content": "Prompt",
            "size_bytes": "6",
            "evidence_index": 0,
        },
        {
            "source_path": "index-string.dat",
            "content": "Prompt",
            "size_bytes": 6,
            "evidence_index": "0",
        },
    ]

    for record in records:
        with pytest.raises(ValueError):
            TextPromptCandidateBuilder.build(
                knowledge_record=record,
                knowledge_index=0,
            )


def test_builder_rejects_bool_integer_fields():
    records = [
        {
            "source_path": "bool-size.dat",
            "content": "Prompt",
            "size_bytes": True,
            "evidence_index": 0,
        },
        {
            "source_path": "bool-index.dat",
            "content": "Prompt",
            "size_bytes": 6,
            "evidence_index": False,
        },
    ]

    for record in records:
        with pytest.raises(ValueError):
            TextPromptCandidateBuilder.build(
                knowledge_record=record,
                knowledge_index=0,
            )


def test_builder_rejects_bool_knowledge_index():
    record = {
        "source_path": "prompt.dat",
        "content": "Prompt",
        "size_bytes": 6,
        "evidence_index": 0,
    }

    with pytest.raises(ValueError):
        TextPromptCandidateBuilder.build(
            knowledge_record=record,
            knowledge_index=True,
        )
