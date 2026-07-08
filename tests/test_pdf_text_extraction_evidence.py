from dataclasses import fields

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


def test_pdf_text_extraction_evidence_stores_exact_copied_values():
    evidence = PdfTextExtractionEvidence(
        source_path="spec.pdf",
        content="Raw page text",
        size_bytes=123,
        page_number=2,
        extraction_index=4,
        extraction_method="embedded_text",
        warnings=["No embedded text found."],
        evidence_index=0,
    )

    assert evidence.source_path == "spec.pdf"
    assert evidence.content == "Raw page text"
    assert evidence.size_bytes == 123
    assert evidence.page_number == 2
    assert evidence.extraction_index == 4
    assert evidence.extraction_method == "embedded_text"
    assert evidence.warnings == ["No embedded text found."]
    assert evidence.evidence_index == 0


def test_pdf_text_extraction_evidence_exposes_only_boundary_fields():
    evidence = PdfTextExtractionEvidence(
        source_path="spec.pdf",
        content="Raw prompt and summary words can appear in content.",
        size_bytes=123,
        page_number=1,
        extraction_index=0,
        extraction_method="embedded_text",
        warnings=[],
        evidence_index=0,
    )

    assert [field.name for field in fields(evidence)] == [
        "source_path",
        "content",
        "size_bytes",
        "page_number",
        "extraction_index",
        "extraction_method",
        "warnings",
        "evidence_index",
    ]
    assert not set(evidence.__dataclass_fields__).intersection(
        FORBIDDEN_FIELDS
    )
