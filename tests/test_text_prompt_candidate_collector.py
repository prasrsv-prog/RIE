from prompting.text_prompt_candidate_collection import (
    TextPromptCandidateCollection,
)
from prompting.text_prompt_candidate_collector import (
    TextPromptCandidateCollector,
)


def test_collector_builds_collection_from_text_knowledge_artifact():
    artifact = {
        "knowledge_items": [
            {
                "source_path": "first.dat",
                "content": "First prompt",
                "size_bytes": 12,
                "evidence_index": 0,
            },
            {
                "source_path": "second.dat",
                "content": "Second prompt",
                "size_bytes": 13,
                "evidence_index": 1,
            },
        ],
    }

    collection = TextPromptCandidateCollector.collect(artifact)

    assert isinstance(collection, TextPromptCandidateCollection)
    assert len(collection.prompt_candidates) == 2
    assert collection.prompt_candidates[0].source_path == "first.dat"
    assert collection.prompt_candidates[0].content == "First prompt"
    assert collection.prompt_candidates[0].size_bytes == 12
    assert collection.prompt_candidates[0].evidence_index == 0
    assert collection.prompt_candidates[0].knowledge_index == 0
    assert collection.prompt_candidates[1].source_path == "second.dat"
    assert collection.prompt_candidates[1].knowledge_index == 1


def test_collector_skips_invalid_text_knowledge_records():
    artifact = {
        "knowledge_items": [
            {
                "source_path": "valid-first.dat",
                "content": "First",
                "size_bytes": 5,
                "evidence_index": 0,
            },
            {
                "source_path": "invalid-extra.dat",
                "content": "Invalid",
                "size_bytes": 7,
                "evidence_index": 1,
                "summary": "Do not summarize.",
            },
            "not a record",
            {
                "source_path": "valid-second.dat",
                "content": "Second",
                "size_bytes": 6,
                "evidence_index": 3,
            },
        ],
    }

    collection = TextPromptCandidateCollector.collect(artifact)

    assert len(collection.prompt_candidates) == 2
    assert collection.prompt_candidates[0].source_path == "valid-first.dat"
    assert collection.prompt_candidates[1].source_path == "valid-second.dat"


def test_collector_preserves_original_knowledge_index_positions():
    artifact = {
        "knowledge_items": [
            {
                "source_path": "valid-first.dat",
                "content": "First",
                "size_bytes": 5,
                "evidence_index": 0,
            },
            {
                "source_path": "invalid-extra.dat",
                "content": "Invalid",
                "size_bytes": 7,
                "evidence_index": 1,
                "summary": "Do not summarize.",
            },
            {
                "source_path": "valid-second.dat",
                "content": "Second",
                "size_bytes": 6,
                "evidence_index": 3,
            },
        ],
    }

    collection = TextPromptCandidateCollector.collect(artifact)

    assert [
        candidate.knowledge_index
        for candidate in collection.prompt_candidates
    ] == [
        0,
        2,
    ]


def test_collector_rejects_bool_for_integer_fields():
    artifact = {
        "knowledge_items": [
            {
                "source_path": "valid.dat",
                "content": "Valid",
                "size_bytes": 5,
                "evidence_index": 0,
            },
            {
                "source_path": "bool-size.dat",
                "content": "Invalid",
                "size_bytes": True,
                "evidence_index": 1,
            },
            {
                "source_path": "bool-index.dat",
                "content": "Invalid",
                "size_bytes": 7,
                "evidence_index": False,
            },
        ],
    }

    collection = TextPromptCandidateCollector.collect(artifact)

    assert len(collection.prompt_candidates) == 1
    assert collection.prompt_candidates[0].source_path == "valid.dat"


def test_empty_text_knowledge_artifact_creates_empty_prompt_candidate_collection():
    collection = TextPromptCandidateCollector.collect({"knowledge_items": []})

    assert isinstance(collection, TextPromptCandidateCollection)
    assert collection.prompt_candidates == []


def test_collector_does_not_add_prompt_generation_or_interpretive_fields():
    artifact = {
        "knowledge_items": [
            {
                "source_path": "prompt.dat",
                "content": "Prompt",
                "size_bytes": 6,
                "evidence_index": 0,
            },
        ],
    }

    collection = TextPromptCandidateCollector.collect(artifact)
    candidate = collection.prompt_candidates[0]

    for field in [
        "prompt",
        "final_prompt",
        "instruction",
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
    ]:
        assert not hasattr(candidate, field)
