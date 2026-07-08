import json

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionAssetError,
)
from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport
from rie.extraction.pdf_text_extraction_report_serializer import (
    PdfTextExtractionReportSerializer,
)


FORBIDDEN_FIELDS = {
    "content_length",
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


def _report(
    page_extractions=None,
    asset_errors=None,
):
    return PdfTextExtractionReport(
        root="D:\\SPEC",
        page_extractions=page_extractions or [],
        asset_errors=asset_errors or [],
    )


def test_serializer_produces_expected_top_level_keys():
    result = PdfTextExtractionReportSerializer.to_dict(_report())

    assert set(result) == {
        "root",
        "total_pdf_assets",
        "total_page_extractions",
        "failed_pdf_assets",
        "page_extractions",
        "asset_errors",
    }


def test_serializer_serializes_empty_report():
    result = PdfTextExtractionReportSerializer.to_dict(_report())

    assert result == {
        "root": "D:\\SPEC",
        "total_pdf_assets": 0,
        "total_page_extractions": 0,
        "failed_pdf_assets": 0,
        "page_extractions": [],
        "asset_errors": [],
    }


def test_serializer_serializes_one_page_extraction_correctly():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="D:\\SPEC\\helmet.pdf",
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Page one",
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result == {
        "root": "D:\\SPEC",
        "total_pdf_assets": 1,
        "total_page_extractions": 1,
        "failed_pdf_assets": 0,
        "page_extractions": [
            {
                "source_path": "D:\\SPEC\\helmet.pdf",
                "size_bytes": 123,
                "page_number": 1,
                "extraction_index": 0,
                "extraction_method": "embedded_text",
                "content": "Page one",
                "warnings": [],
            },
        ],
        "asset_errors": [],
    }


def test_serializer_serializes_multiple_page_extractions_in_order():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="b.pdf",
                size_bytes=2,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Second file",
                warnings=[],
            ),
            PdfPageTextExtraction(
                source_path="a.pdf",
                size_bytes=1,
                page_number=1,
                extraction_index=1,
                extraction_method="embedded_text",
                content="First file",
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["page_extractions"] == [
        {
            "source_path": "b.pdf",
            "size_bytes": 2,
            "page_number": 1,
            "extraction_index": 0,
            "extraction_method": "embedded_text",
            "content": "Second file",
            "warnings": [],
        },
        {
            "source_path": "a.pdf",
            "size_bytes": 1,
            "page_number": 1,
            "extraction_index": 1,
            "extraction_method": "embedded_text",
            "content": "First file",
            "warnings": [],
        },
    ]


def test_serializer_preserves_exact_content():
    content = "  Product table text with surrounding spaces.  "
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=42,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content=content,
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["page_extractions"][0]["content"] == content


def test_serializer_preserves_non_ascii_content():
    content = "Caf\u00e9 racer helm: Rancang konsep."
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=34,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content=content,
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_json(report)

    assert content in result
    assert "Caf\\u00e9" not in result
    assert json.loads(result)["page_extractions"][0]["content"] == content


def test_serializer_preserves_newline_content():
    content = "Line 1\nLine 2\n"
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=14,
                page_number=2,
                extraction_index=0,
                extraction_method="embedded_text",
                content=content,
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_json(report)

    assert json.loads(result)["page_extractions"][0]["content"] == content


def test_serializer_preserves_empty_content():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="empty.pdf",
                size_bytes=0,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="",
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["page_extractions"][0]["content"] == ""


def test_serializer_preserves_warnings():
    warnings = [
        "No embedded text found.",
        "Failed to extract embedded text from image-only page.",
    ]
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="warning.pdf",
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="",
                warnings=warnings,
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["page_extractions"][0]["warnings"] == warnings


def test_serializer_preserves_asset_errors():
    report = _report(
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="broken.pdf",
                size_bytes=321,
                error="Cannot read PDF.",
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["asset_errors"] == [
        {
            "source_path": "broken.pdf",
            "size_bytes": 321,
            "error": "Cannot read PDF.",
        },
    ]


def test_serializer_preserves_total_pdf_assets():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="good.pdf",
                size_bytes=100,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Text",
                warnings=[],
            ),
        ],
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="broken.pdf",
                size_bytes=200,
                error="Cannot read PDF.",
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["total_pdf_assets"] == 2


def test_serializer_preserves_total_page_extractions():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="one.pdf",
                size_bytes=100,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="One",
                warnings=[],
            ),
            PdfPageTextExtraction(
                source_path="one.pdf",
                size_bytes=100,
                page_number=2,
                extraction_index=1,
                extraction_method="embedded_text",
                content="Two",
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["total_page_extractions"] == 2


def test_serializer_preserves_failed_pdf_assets():
    report = _report(
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="broken.pdf",
                size_bytes=200,
                error="Cannot read PDF.",
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)

    assert result["failed_pdf_assets"] == 1


def test_serializer_does_not_include_forbidden_fields():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content=(
                    "Raw PDF text may mention prompt, summary, or "
                    "helmet_model."
                ),
                warnings=[],
            ),
        ],
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="broken.pdf",
                size_bytes=321,
                error="Cannot read PDF.",
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_dict(report)
    page_extraction = result["page_extractions"][0]
    asset_error = result["asset_errors"][0]

    assert not set(result).intersection(FORBIDDEN_FIELDS)
    assert not set(page_extraction).intersection(FORBIDDEN_FIELDS)
    assert not set(asset_error).intersection(FORBIDDEN_FIELDS)
    assert set(page_extraction) == {
        "source_path",
        "size_bytes",
        "page_number",
        "extraction_index",
        "extraction_method",
        "content",
        "warnings",
    }
    assert set(asset_error) == {
        "source_path",
        "size_bytes",
        "error",
    }


def test_to_json_output_is_deterministic():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Text",
                warnings=[],
            ),
        ],
    )

    first = PdfTextExtractionReportSerializer.to_json(report)
    second = PdfTextExtractionReportSerializer.to_json(report)

    assert first == second


def test_to_json_output_can_be_parsed_back_with_json_loads():
    report = _report(
        page_extractions=[
            PdfPageTextExtraction(
                source_path="spec.pdf",
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Text",
                warnings=[],
            ),
        ],
    )

    result = PdfTextExtractionReportSerializer.to_json(report)
    data = json.loads(result)

    assert data["page_extractions"][0]["source_path"] == "spec.pdf"
