from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)
from knowledge.text_knowledge_collection import TextKnowledgeCollection
from knowledge.text_knowledge_collector import TextKnowledgeCollector


def test_collector_builds_collection_from_evidence_artifact():
    artifact = {
        "evidences": [
            {
                "source_path": "first.dat",
                "content": "First prompt",
                "size_bytes": 12,
            },
            {
                "source_path": "second.dat",
                "content": "Second prompt",
                "size_bytes": 13,
            },
        ],
    }

    collection = TextKnowledgeCollector.collect(artifact)

    assert isinstance(collection, TextKnowledgeCollection)
    assert len(collection.knowledge_items) == 2
    assert collection.knowledge_items[0].source_path == "first.dat"
    assert collection.knowledge_items[0].content == "First prompt"
    assert collection.knowledge_items[0].size_bytes == 12
    assert collection.knowledge_items[0].evidence_index == 0
    assert collection.knowledge_items[1].source_path == "second.dat"
    assert collection.knowledge_items[1].evidence_index == 1


def test_collector_preserves_evidence_order():
    artifact = {
        "evidences": [
            {
                "source_path": "b.dat",
                "content": "Second",
                "size_bytes": 6,
            },
            {
                "source_path": "a.dat",
                "content": "First",
                "size_bytes": 5,
            },
        ],
    }

    collection = TextKnowledgeCollector.collect(artifact)

    assert [
        knowledge.source_path
        for knowledge in collection.knowledge_items
    ] == [
        "b.dat",
        "a.dat",
    ]


def test_collector_skips_invalid_evidence_records():
    artifact = {
        "evidences": [
            {
                "source_path": "valid-first.dat",
                "content": "First",
                "size_bytes": 5,
            },
            {
                "source_path": "invalid-extra.dat",
                "content": "Invalid",
                "size_bytes": 7,
                "summary": "Do not summarize.",
            },
            "not a record",
            {
                "source_path": "valid-second.dat",
                "content": "Second",
                "size_bytes": 6,
            },
        ],
    }

    collection = TextKnowledgeCollector.collect(artifact)

    assert len(collection.knowledge_items) == 2
    assert collection.knowledge_items[0].source_path == "valid-first.dat"
    assert collection.knowledge_items[0].evidence_index == 0
    assert collection.knowledge_items[1].source_path == "valid-second.dat"
    assert collection.knowledge_items[1].evidence_index == 3


def test_empty_evidence_artifact_creates_empty_knowledge_collection():
    collection = TextKnowledgeCollector.collect({"evidences": []})

    assert isinstance(collection, TextKnowledgeCollection)
    assert collection.knowledge_items == []


def test_text_knowledge_collection_is_distinct_from_evidence_collection():
    collection = TextKnowledgeCollector.collect({"evidences": []})

    assert isinstance(collection, TextKnowledgeCollection)
    assert not isinstance(collection, TextExtractionEvidenceCollection)
