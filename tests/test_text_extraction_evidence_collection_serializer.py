import json

from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)
from collection.text_extraction_evidence_collection_serializer import (
    to_json,
)
from evidence.text_extraction_evidence import TextExtractionEvidence


def test_serializes_empty_text_extraction_evidence_collection():
    collection = TextExtractionEvidenceCollection(evidences=[])

    result = to_json(collection)

    assert json.loads(result) == {
        "evidences": [],
    }


def test_serializes_one_text_extraction_evidence():
    collection = TextExtractionEvidenceCollection(
        evidences=[
            TextExtractionEvidence(
                source_path="D:\\PROJECT\\RIE\\prompt.dat",
                content="Generate a helmet concept.",
                size_bytes=26,
            ),
        ],
    )

    result = to_json(collection)

    assert json.loads(result) == {
        "evidences": [
            {
                "source_path": "D:\\PROJECT\\RIE\\prompt.dat",
                "content": "Generate a helmet concept.",
                "size_bytes": 26,
            },
        ],
    }


def test_serializes_multiple_evidences_deterministically():
    collection = TextExtractionEvidenceCollection(
        evidences=[
            TextExtractionEvidence(
                source_path="b.dat",
                content="Second",
                size_bytes=6,
            ),
            TextExtractionEvidence(
                source_path="a.dat",
                content="First",
                size_bytes=5,
            ),
        ],
    )

    first = to_json(collection)
    second = to_json(collection)

    assert first == second
    assert json.loads(first)["evidences"] == [
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
    ]


def test_preserves_non_ascii_content_with_ensure_ascii_false():
    collection = TextExtractionEvidenceCollection(
        evidences=[
            TextExtractionEvidence(
                source_path="prompt.dat",
                content="Café racer helm: Rancang konsep.",
                size_bytes=34,
            ),
        ],
    )

    result = to_json(collection)

    assert "Café" in result
    assert json.loads(result)["evidences"][0]["content"] == (
        "Café racer helm: Rancang konsep."
    )


def test_serialized_output_contains_only_evidence_fields():
    collection = TextExtractionEvidenceCollection(
        evidences=[
            TextExtractionEvidence(
                source_path="prompt.dat",
                content="Prompt",
                size_bytes=6,
            ),
        ],
    )

    result = to_json(collection)
    data = json.loads(result)

    assert set(data) == {"evidences"}
    assert set(data["evidences"][0]) == {
        "source_path",
        "content",
        "size_bytes",
    }
