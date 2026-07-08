from pathlib import Path

from rie.extraction.pdf_text_extractor import PdfTextExtractor


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


class FakePage:

    def __init__(
        self,
        content,
    ):
        self.content = content

    def extract_text(self):
        if isinstance(self.content, Exception):
            raise self.content

        return self.content


class FakeReader:

    def __init__(
        self,
        pages,
    ):
        self.pages = pages


def _artifact(root, items):
    return {
        "root": str(root),
        "items": items,
    }


def test_extractor_creates_page_level_extraction_records(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
            {
                "path": str(tmp_path / "image.png"),
                "asset_type": "PNG",
                "size": 200,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage("Page one text"),
            FakePage("Page two text"),
        ])
    )

    report = extractor.extract(data)

    assert report.root == str(tmp_path)
    assert report.total_pdf_assets == 1
    assert report.total_page_extractions == 2
    assert report.failed_pdf_assets == 0
    assert [
        extraction.content
        for extraction in report.page_extractions
    ] == [
        "Page one text",
        "Page two text",
    ]


def test_extractor_uses_one_based_page_numbers(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage("First"),
            FakePage("Second"),
        ])
    )

    report = extractor.extract(data)

    assert [
        extraction.page_number
        for extraction in report.page_extractions
    ] == [1, 2]


def test_extraction_index_is_zero_based(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage("First"),
            FakePage("Second"),
        ])
    )

    report = extractor.extract(data)

    assert [
        extraction.extraction_index
        for extraction in report.page_extractions
    ] == [0, 1]


def test_extraction_index_preserves_page_extraction_order(tmp_path):
    first_pdf = tmp_path / "first.pdf"
    second_pdf = tmp_path / "second.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(first_pdf),
                "asset_type": "PDF",
                "size": 100,
            },
            {
                "path": str(second_pdf),
                "asset_type": "PDF",
                "size": 200,
            },
        ],
    )

    def reader_factory(path: Path):
        if path == first_pdf:
            return FakeReader([
                FakePage("First A"),
                FakePage("First B"),
            ])

        return FakeReader([
            FakePage("Second A"),
        ])

    report = PdfTextExtractor(reader_factory=reader_factory).extract(data)

    assert [
        (
            extraction.source_path,
            extraction.content,
            extraction.extraction_index,
        )
        for extraction in report.page_extractions
    ] == [
        (str(first_pdf), "First A", 0),
        (str(first_pdf), "First B", 1),
        (str(second_pdf), "Second A", 2),
    ]


def test_extraction_method_is_embedded_text(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage("Text"),
        ])
    )

    report = extractor.extract(data)

    assert report.page_extractions[0].extraction_method == "embedded_text"


def test_empty_page_content_is_allowed(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage(None),
        ])
    )

    report = extractor.extract(data)

    assert report.page_extractions[0].content == ""
    assert report.page_extractions[0].warnings == [
        "No embedded text found.",
    ]


def test_unreadable_pdf_asset_creates_asset_error_and_does_not_crash(
    tmp_path,
):
    pdf_path = tmp_path / "broken.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )

    def reader_factory(path):
        raise OSError("cannot read pdf")

    report = PdfTextExtractor(reader_factory=reader_factory).extract(data)

    assert report.page_extractions == []
    assert report.failed_pdf_assets == 1
    assert report.asset_errors[0].source_path == str(pdf_path)
    assert report.asset_errors[0].size_bytes == 100
    assert report.asset_errors[0].error == "cannot read pdf"


def test_extractor_accepts_source_path_and_size_bytes_records(tmp_path):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "source_path": str(pdf_path),
                "asset_type": "PDF",
                "size_bytes": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage("Text"),
        ])
    )

    report = extractor.extract(data)

    assert report.page_extractions[0].source_path == str(pdf_path)
    assert report.page_extractions[0].size_bytes == 100


def test_extractor_does_not_add_forbidden_product_or_prompt_fields(
    tmp_path,
):
    pdf_path = tmp_path / "spec.pdf"
    data = _artifact(
        tmp_path,
        [
            {
                "path": str(pdf_path),
                "asset_type": "PDF",
                "size": 100,
            },
        ],
    )
    extractor = PdfTextExtractor(
        reader_factory=lambda path: FakeReader([
            FakePage(
                "Raw PDF text may mention prompt, summary, or helmet_model."
            ),
        ])
    )

    report = extractor.extract(data)
    extraction_fields = set(report.page_extractions[0].__dataclass_fields__)
    report_fields = set(report.__dataclass_fields__)

    assert not extraction_fields.intersection(FORBIDDEN_FIELDS)
    assert not report_fields.intersection(FORBIDDEN_FIELDS)
