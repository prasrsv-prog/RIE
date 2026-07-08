import pytest

from collection.pdf_text_extraction_evidence_collection import (
    PdfTextExtractionEvidenceCollection,
)
from collection.pdf_text_extraction_evidence_collector import (
    PdfTextExtractionEvidenceCollector,
)


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


def _valid_page(**overrides):
    page = {
        "source_path": "spec.pdf",
        "size_bytes": 123,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "embedded_text",
        "content": "Page text",
        "warnings": [],
    }
    page.update(overrides)
    return page


def _artifact(page_extractions, **overrides):
    artifact = {
        "root": "D:\\SPEC",
        "total_pdf_assets": 1,
        "total_page_extractions": len(page_extractions),
        "failed_pdf_assets": 0,
        "page_extractions": page_extractions,
        "asset_errors": [],
    }
    artifact.update(overrides)
    return artifact


def test_collector_consumes_page_extractions_from_pdf_text_artifact():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(source_path="first.pdf", content="First"),
            _valid_page(source_path="second.pdf", content="Second"),
        ])
    )

    assert isinstance(collection, PdfTextExtractionEvidenceCollection)
    assert len(collection.evidences) == 2
    assert collection.evidences[0].source_path == "first.pdf"
    assert collection.evidences[0].content == "First"
    assert collection.evidences[1].source_path == "second.pdf"
    assert collection.evidences[1].content == "Second"


def test_collector_skips_invalid_page_extraction_records():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(source_path="valid.pdf"),
            _valid_page(source_path=123),
            "not a page extraction",
        ])
    )

    assert len(collection.evidences) == 1
    assert collection.evidences[0].source_path == "valid.pdf"


def test_collector_preserves_evidence_index_positions_for_valid_output_order():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(page_number=9, extraction_index=4),
            _valid_page(source_path=123),
            _valid_page(page_number=10, extraction_index=5),
        ])
    )

    assert [
        evidence.evidence_index
        for evidence in collection.evidences
    ] == [0, 1]


def test_collector_does_not_confuse_page_number_with_evidence_index():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(page_number=8),
        ])
    )

    assert collection.evidences[0].page_number == 8
    assert collection.evidences[0].evidence_index == 0


def test_collector_does_not_confuse_extraction_index_with_evidence_index():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(extraction_index=12),
        ])
    )

    assert collection.evidences[0].extraction_index == 12
    assert collection.evidences[0].evidence_index == 0


@pytest.mark.parametrize(
    "field",
    [
        "size_bytes",
        "page_number",
        "extraction_index",
    ],
)
def test_collector_rejects_bool_for_integer_fields(field):
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(**{field: True}),
        ])
    )

    assert collection.evidences == []


def test_collector_rejects_invalid_warnings_list():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(warnings="No embedded text found."),
        ])
    )

    assert collection.evidences == []


def test_collector_rejects_warnings_list_with_non_string_item():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(warnings=["Warning", 123]),
        ])
    )

    assert collection.evidences == []


def test_collector_ignores_asset_errors_and_does_not_create_evidence():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact(
            [],
            asset_errors=[
                {
                    "source_path": "broken.pdf",
                    "size_bytes": 456,
                    "error": "Cannot read PDF.",
                },
            ],
            failed_pdf_assets=1,
        )
    )

    assert collection.evidences == []


def test_collector_keeps_empty_content_as_valid_evidence():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(
                content="",
                warnings=["No embedded text found."],
            ),
        ])
    )

    assert len(collection.evidences) == 1
    assert collection.evidences[0].content == ""
    assert collection.evidences[0].warnings == ["No embedded text found."]


def test_collector_returns_empty_collection_for_empty_page_extractions():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([])
    )

    assert collection.evidences == []


def test_collector_rejects_non_dict_artifact():
    with pytest.raises(ValueError, match="object"):
        PdfTextExtractionEvidenceCollector.collect([])


def test_collector_rejects_non_list_page_extractions():
    with pytest.raises(ValueError, match="page_extractions"):
        PdfTextExtractionEvidenceCollector.collect(
            _artifact(page_extractions={})
        )


def test_collector_does_not_add_forbidden_product_or_prompt_fields():
    collection = PdfTextExtractionEvidenceCollector.collect(
        _artifact([
            _valid_page(
                content=(
                    "Raw PDF text may mention prompt, summary, "
                    "or helmet_model."
                ),
            ),
        ])
    )

    evidence_fields = set(
        collection.evidences[0].__dataclass_fields__
    )
    assert not evidence_fields.intersection(FORBIDDEN_FIELDS)
