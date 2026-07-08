from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction


def test_pdf_page_text_extraction_stores_exact_values():
    extraction = PdfPageTextExtraction(
        source_path="D:\\SPEC\\helmet.pdf",
        size_bytes=123,
        page_number=2,
        extraction_index=1,
        extraction_method="embedded_text",
        content="Line 1\nLine 2",
        warnings=["No embedded text found."],
    )

    assert extraction.source_path == "D:\\SPEC\\helmet.pdf"
    assert extraction.size_bytes == 123
    assert extraction.page_number == 2
    assert extraction.extraction_index == 1
    assert extraction.extraction_method == "embedded_text"
    assert extraction.content == "Line 1\nLine 2"
    assert extraction.warnings == ["No embedded text found."]
