from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionAssetError,
)
from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport


def test_pdf_text_extraction_report_calculates_total_pdf_assets():
    report = PdfTextExtractionReport(
        root="D:\\SPEC",
        page_extractions=[
            PdfPageTextExtraction(
                source_path="D:\\SPEC\\first.pdf",
                size_bytes=100,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="First page",
                warnings=[],
            ),
            PdfPageTextExtraction(
                source_path="D:\\SPEC\\first.pdf",
                size_bytes=100,
                page_number=2,
                extraction_index=1,
                extraction_method="embedded_text",
                content="Second page",
                warnings=[],
            ),
        ],
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="D:\\SPEC\\broken.pdf",
                size_bytes=200,
                error="Could not read PDF.",
            ),
        ],
    )

    assert report.total_pdf_assets == 2


def test_pdf_text_extraction_report_calculates_total_page_extractions():
    report = PdfTextExtractionReport(
        root="D:\\SPEC",
        page_extractions=[
            PdfPageTextExtraction(
                source_path="D:\\SPEC\\first.pdf",
                size_bytes=100,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="First page",
                warnings=[],
            ),
        ],
        asset_errors=[],
    )

    assert report.total_page_extractions == 1


def test_pdf_text_extraction_report_calculates_failed_pdf_assets():
    report = PdfTextExtractionReport(
        root="D:\\SPEC",
        page_extractions=[],
        asset_errors=[
            PdfTextExtractionAssetError(
                source_path="D:\\SPEC\\broken.pdf",
                size_bytes=200,
                error="Could not read PDF.",
            ),
        ],
    )

    assert report.failed_pdf_assets == 1
