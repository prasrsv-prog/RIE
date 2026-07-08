import json

from collection.pdf_text_extraction_evidence_collection import (
    PdfTextExtractionEvidenceCollection,
)
from collection.pdf_text_extraction_evidence_collection_serializer import (
    PdfTextExtractionEvidenceCollectionSerializer,
)
from evidence.pdf_text_extraction_evidence import PdfTextExtractionEvidence


FORBIDDEN_FIELDS = {
    "product_type",
    "product_category",
    "helmet_model",
    "variant",
    "summary",
    "persona",
    "USP",
    "visual_style",
    "prompt",
    "final_prompt",
    "confidence",
    "embedding",
    "graph",
    "knowledge",
    "analysis",
    "style",
    "tone",
    "creative_direction",
}


def _evidence(**overrides):
    evidence = {
        "source_path": "spec.pdf",
        "content": "Page text",
        "size_bytes": 123,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "embedded_text",
        "warnings": [],
        "evidence_index": 0,
    }
    evidence.update(overrides)
    return PdfTextExtractionEvidence(**evidence)


def test_serializer_produces_top_level_pdf_text_evidences_key():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(evidences=[])
    )

    assert set(data) == {"pdf_text_evidences"}


def test_serializer_serializes_empty_collection():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(evidences=[])
    )

    assert data == {"pdf_text_evidences": []}


def test_serializer_serializes_one_evidence_correctly():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(
                    source_path="helmet-spec.pdf",
                    content="Shell construction",
                    size_bytes=4096,
                    page_number=2,
                    extraction_index=7,
                    extraction_method="embedded_text",
                    warnings=["No embedded text found."],
                    evidence_index=3,
                ),
            ],
        )
    )

    assert data == {
        "pdf_text_evidences": [
            {
                "source_path": "helmet-spec.pdf",
                "content": "Shell construction",
                "size_bytes": 4096,
                "page_number": 2,
                "extraction_index": 7,
                "extraction_method": "embedded_text",
                "warnings": ["No embedded text found."],
                "evidence_index": 3,
            },
        ],
    }


def test_serializer_serializes_multiple_evidences_in_order():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(source_path="first.pdf", evidence_index=0),
                _evidence(source_path="second.pdf", evidence_index=1),
            ],
        )
    )

    assert [
        evidence["source_path"]
        for evidence in data["pdf_text_evidences"]
    ] == [
        "first.pdf",
        "second.pdf",
    ]


def test_serializer_preserves_exact_content():
    content = "  Raw PDF text with spacing.  "

    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(content=content),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["content"] == content


def test_serializer_preserves_non_ascii_content():
    content = "Caf\u00e9 racer helm"

    json_output = PdfTextExtractionEvidenceCollectionSerializer.to_json(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(content=content),
            ],
        )
    )

    assert content in json_output
    assert "\\u00e9" not in json_output
    assert json.loads(json_output)["pdf_text_evidences"][0]["content"] == (
        content
    )


def test_serializer_preserves_newline_content():
    content = "Line one\nLine two\n"

    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(content=content),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["content"] == content


def test_serializer_preserves_empty_content():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(content=""),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["content"] == ""


def test_serializer_preserves_warnings():
    warnings = [
        "No embedded text found.",
        "Failed to extract embedded text from page.",
    ]

    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(warnings=warnings),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["warnings"] == warnings


def test_serializer_preserves_source_path():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(source_path="manual.pdf"),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["source_path"] == "manual.pdf"


def test_serializer_preserves_size_bytes():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(size_bytes=2048),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["size_bytes"] == 2048


def test_serializer_preserves_page_number():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(page_number=4),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["page_number"] == 4


def test_serializer_preserves_extraction_index():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(extraction_index=8),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["extraction_index"] == 8


def test_serializer_preserves_extraction_method():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(extraction_method="embedded_text"),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["extraction_method"] == (
        "embedded_text"
    )


def test_serializer_preserves_evidence_index():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(evidence_index=5),
            ],
        )
    )

    assert data["pdf_text_evidences"][0]["evidence_index"] == 5


def test_serializer_does_not_include_forbidden_fields():
    data = PdfTextExtractionEvidenceCollectionSerializer.to_dict(
        PdfTextExtractionEvidenceCollection(
            evidences=[
                _evidence(
                    content=(
                        "Raw PDF text may mention prompt, summary, "
                        "or helmet_model."
                    ),
                ),
            ],
        )
    )

    assert not set(data).intersection(FORBIDDEN_FIELDS)
    for evidence in data["pdf_text_evidences"]:
        assert not set(evidence).intersection(FORBIDDEN_FIELDS)


def test_to_json_output_is_deterministic():
    collection = PdfTextExtractionEvidenceCollection(
        evidences=[
            _evidence(source_path="first.pdf", evidence_index=0),
            _evidence(source_path="second.pdf", evidence_index=1),
        ],
    )

    first_output = PdfTextExtractionEvidenceCollectionSerializer.to_json(
        collection
    )
    second_output = PdfTextExtractionEvidenceCollectionSerializer.to_json(
        collection
    )

    assert first_output == second_output


def test_to_json_output_can_be_parsed_back_with_json_loads():
    collection = PdfTextExtractionEvidenceCollection(
        evidences=[
            _evidence(content="Page text"),
        ],
    )

    json_output = PdfTextExtractionEvidenceCollectionSerializer.to_json(
        collection
    )

    assert json.loads(json_output) == (
        PdfTextExtractionEvidenceCollectionSerializer.to_dict(collection)
    )
