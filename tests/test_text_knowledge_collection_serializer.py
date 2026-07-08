import json

from knowledge.text_knowledge import TextKnowledge
from knowledge.text_knowledge_collection import TextKnowledgeCollection
from knowledge.text_knowledge_collection_serializer import to_json


def test_serializes_empty_text_knowledge_collection():
    collection = TextKnowledgeCollection(knowledge_items=[])

    result = to_json(collection)

    assert json.loads(result) == {
        "knowledge_items": [],
    }


def test_serializes_one_text_knowledge_item():
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="D:\\PROJECT\\RIE\\prompt.dat",
                content="Generate a helmet concept.",
                size_bytes=26,
                evidence_index=0,
            ),
        ],
    )

    result = to_json(collection)

    assert json.loads(result) == {
        "knowledge_items": [
            {
                "source_path": "D:\\PROJECT\\RIE\\prompt.dat",
                "content": "Generate a helmet concept.",
                "size_bytes": 26,
                "evidence_index": 0,
            },
        ],
    }


def test_serializes_multiple_text_knowledge_items_deterministically():
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="b.dat",
                content="Second",
                size_bytes=6,
                evidence_index=1,
            ),
            TextKnowledge(
                source_path="a.dat",
                content="First",
                size_bytes=5,
                evidence_index=0,
            ),
        ],
    )

    first = to_json(collection)
    second = to_json(collection)

    assert first == second
    assert json.loads(first)["knowledge_items"] == [
        {
            "source_path": "b.dat",
            "content": "Second",
            "size_bytes": 6,
            "evidence_index": 1,
        },
        {
            "source_path": "a.dat",
            "content": "First",
            "size_bytes": 5,
            "evidence_index": 0,
        },
    ]


def test_preserves_non_ascii_content_with_ensure_ascii_false():
    content = "Caf\u00e9 racer helm: Rancang konsep."
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="prompt.dat",
                content=content,
                size_bytes=34,
                evidence_index=2,
            ),
        ],
    )

    result = to_json(collection)

    assert content in result
    assert "Caf\\u00e9" not in result
    assert json.loads(result)["knowledge_items"][0]["content"] == content


def test_preserves_newline_content_exactly():
    content = "Line 1\nLine 2\n"
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="prompt.dat",
                content=content,
                size_bytes=14,
                evidence_index=0,
            ),
        ],
    )

    result = to_json(collection)

    assert json.loads(result)["knowledge_items"][0]["content"] == content


def test_preserves_evidence_index():
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=7,
            ),
        ],
    )

    result = to_json(collection)

    assert json.loads(result)["knowledge_items"][0]["evidence_index"] == 7


def test_serialized_output_contains_only_knowledge_fields():
    collection = TextKnowledgeCollection(
        knowledge_items=[
            TextKnowledge(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
                evidence_index=0,
            ),
        ],
    )

    result = to_json(collection)
    data = json.loads(result)

    assert set(data) == {"knowledge_items"}
    assert set(data["knowledge_items"][0]) == {
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
    }
    assert not any(
        field in data["knowledge_items"][0]
        for field in {
            "summary",
            "category",
            "label",
            "embedding",
            "prompt",
            "analysis",
            "size_class",
        }
    )
