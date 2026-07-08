import json

from prompting.text_prompt_candidate import TextPromptCandidate
from prompting.text_prompt_candidate_collection import (
    TextPromptCandidateCollection,
)
from prompting.text_prompt_candidate_collection_serializer import (
    TextPromptCandidateCollectionSerializer,
)


def test_serializer_produces_top_level_prompt_candidates_key():
    collection = TextPromptCandidateCollection(prompt_candidates=[])

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result == {
        "prompt_candidates": [],
    }


def test_serializer_serializes_one_candidate_correctly():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="D:\\PROJECT\\RIE\\prompt.dat",
                content="Generate a helmet concept.",
                size_bytes=26,
                evidence_index=2,
                knowledge_index=4,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result == {
        "prompt_candidates": [
            {
                "source_path": "D:\\PROJECT\\RIE\\prompt.dat",
                "content": "Generate a helmet concept.",
                "size_bytes": 26,
                "evidence_index": 2,
                "knowledge_index": 4,
            },
        ],
    }


def test_serializer_serializes_multiple_candidates_in_order():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="b.dat",
                content="Second",
                size_bytes=6,
                evidence_index=1,
                knowledge_index=1,
            ),
            TextPromptCandidate(
                source_path="a.dat",
                content="First",
                size_bytes=5,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result["prompt_candidates"] == [
        {
            "source_path": "b.dat",
            "content": "Second",
            "size_bytes": 6,
            "evidence_index": 1,
            "knowledge_index": 1,
        },
        {
            "source_path": "a.dat",
            "content": "First",
            "size_bytes": 5,
            "evidence_index": 0,
            "knowledge_index": 0,
        },
    ]


def test_serializer_preserves_exact_content():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="  Prompt with surrounding spaces.  ",
                size_bytes=33,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert (
        result["prompt_candidates"][0]["content"]
        == "  Prompt with surrounding spaces.  "
    )


def test_serializer_preserves_non_ascii_content():
    content = "Caf\u00e9 racer helm: Rancang konsep."
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content=content,
                size_bytes=34,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_json(collection)

    assert content in result
    assert "Caf\\u00e9" not in result
    assert json.loads(result)["prompt_candidates"][0]["content"] == content


def test_serializer_preserves_newline_content():
    content = "Line 1\nLine 2\n"
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content=content,
                size_bytes=14,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_json(collection)

    assert json.loads(result)["prompt_candidates"][0]["content"] == content


def test_serializer_preserves_empty_content():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="empty.dat",
                content="",
                size_bytes=0,
                evidence_index=3,
                knowledge_index=5,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result["prompt_candidates"][0]["content"] == ""


def test_serializer_preserves_evidence_index():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=7,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result["prompt_candidates"][0]["evidence_index"] == 7


def test_serializer_preserves_knowledge_index():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=0,
                knowledge_index=9,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)

    assert result["prompt_candidates"][0]["knowledge_index"] == 9


def test_serializer_does_not_include_forbidden_fields():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_dict(collection)
    candidate = result["prompt_candidates"][0]

    assert set(candidate) == {
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
        "knowledge_index",
    }
    assert not any(
        field in candidate
        for field in {
            "prompt",
            "final_prompt",
            "instruction",
            "system_prompt",
            "user_prompt",
            "summary",
            "category",
            "label",
            "metadata",
            "confidence",
            "score",
            "embedding",
            "graph",
            "style",
            "tone",
            "creative_direction",
            "image_generation",
            "video_generation",
            "model",
            "analysis",
        }
    )


def test_to_json_output_is_deterministic():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    first = TextPromptCandidateCollectionSerializer.to_json(collection)
    second = TextPromptCandidateCollectionSerializer.to_json(collection)

    assert first == second


def test_to_json_output_can_be_parsed_back_with_json_loads():
    collection = TextPromptCandidateCollection(
        prompt_candidates=[
            TextPromptCandidate(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=0,
                knowledge_index=0,
            ),
        ],
    )

    result = TextPromptCandidateCollectionSerializer.to_json(collection)
    data = json.loads(result)

    assert data["prompt_candidates"][0]["source_path"] == "prompt.dat"
