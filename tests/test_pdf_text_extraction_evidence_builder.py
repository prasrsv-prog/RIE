import pytest

from evidence.pdf_text_extraction_evidence_builder import (
    PdfTextExtractionEvidenceBuilder,
)


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


def test_builder_preserves_pdf_page_extraction_values():
    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(
            source_path="helmet-spec.pdf",
            size_bytes=4096,
            page_number=3,
            extraction_index=7,
            extraction_method="embedded_text",
            content="Shell construction",
            warnings=["No embedded text found."],
        ),
        evidence_index=2,
    )

    assert evidence.source_path == "helmet-spec.pdf"
    assert evidence.size_bytes == 4096
    assert evidence.page_number == 3
    assert evidence.extraction_index == 7
    assert evidence.extraction_method == "embedded_text"
    assert evidence.content == "Shell construction"
    assert evidence.warnings == ["No embedded text found."]
    assert evidence.evidence_index == 2


def test_builder_preserves_content_exactly():
    content = "  Raw PDF content with spacing.  "

    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(content=content),
        evidence_index=0,
    )

    assert evidence.content == content


def test_builder_preserves_non_ascii_content():
    content = "Caf\u00e9 racer helm"

    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(content=content),
        evidence_index=0,
    )

    assert evidence.content == content


def test_builder_preserves_newline_content():
    content = "Line one\nLine two\n"

    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(content=content),
        evidence_index=0,
    )

    assert evidence.content == content


def test_builder_preserves_empty_content():
    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(content=""),
        evidence_index=0,
    )

    assert evidence.content == ""


def test_builder_preserves_warnings():
    warnings = [
        "No embedded text found.",
        "Failed to extract embedded text from page.",
    ]

    evidence = PdfTextExtractionEvidenceBuilder.build(
        _valid_page(warnings=warnings),
        evidence_index=0,
    )

    assert evidence.warnings == warnings


def test_builder_rejects_missing_required_fields():
    page = _valid_page()
    del page["warnings"]

    with pytest.raises(ValueError, match="exactly"):
        PdfTextExtractionEvidenceBuilder.build(page, evidence_index=0)


def test_builder_rejects_extra_fields():
    with pytest.raises(ValueError, match="exactly"):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(prompt="Do not promote this."),
            evidence_index=0,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_path", 123),
        ("content", 123),
        ("extraction_method", 123),
    ],
)
def test_builder_rejects_wrong_field_types(field, value):
    with pytest.raises(ValueError):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(**{field: value}),
            evidence_index=0,
        )


@pytest.mark.parametrize(
    "field",
    [
        "size_bytes",
        "page_number",
        "extraction_index",
    ],
)
def test_builder_rejects_bool_integer_fields(field):
    with pytest.raises(ValueError, match="integer"):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(**{field: True}),
            evidence_index=0,
        )


def test_builder_rejects_bool_evidence_index():
    with pytest.raises(ValueError, match="Evidence index"):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(),
            evidence_index=False,
        )


def test_builder_rejects_invalid_warnings_list():
    with pytest.raises(ValueError, match="warnings"):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(warnings="No embedded text found."),
            evidence_index=0,
        )


def test_builder_rejects_warnings_list_with_non_string_item():
    with pytest.raises(ValueError, match="warnings"):
        PdfTextExtractionEvidenceBuilder.build(
            _valid_page(warnings=["Warning", 123]),
            evidence_index=0,
        )
