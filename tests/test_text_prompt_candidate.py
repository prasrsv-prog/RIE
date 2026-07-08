from dataclasses import fields

from prompting.text_prompt_candidate import TextPromptCandidate


def test_text_prompt_candidate_stores_exact_copied_values():
    candidate = TextPromptCandidate(
        source_path="prompt.dat",
        content="Generate a helmet concept.",
        size_bytes=26,
        evidence_index=2,
        knowledge_index=5,
    )

    assert candidate.source_path == "prompt.dat"
    assert candidate.content == "Generate a helmet concept."
    assert candidate.size_bytes == 26
    assert candidate.evidence_index == 2
    assert candidate.knowledge_index == 5


def test_text_prompt_candidate_exposes_only_boundary_fields():
    candidate = TextPromptCandidate(
        source_path="prompt.dat",
        content="Prompt",
        size_bytes=6,
        evidence_index=0,
        knowledge_index=0,
    )

    assert [field.name for field in fields(candidate)] == [
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
        "knowledge_index",
    ]
