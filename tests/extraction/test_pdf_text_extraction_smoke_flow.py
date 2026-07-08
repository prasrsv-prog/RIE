import json

from rie.extraction import export_pdf_text_extractions as export_module
from rie.extraction.inspect_pdf_text_extractions import main as inspect_main
from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionAssetError,
)
from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport


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

TOP_LEVEL_FIELDS = {
    "root",
    "total_pdf_assets",
    "total_page_extractions",
    "failed_pdf_assets",
    "page_extractions",
    "asset_errors",
}

PAGE_EXTRACTION_FIELDS = {
    "source_path",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "content",
    "warnings",
}

ASSET_ERROR_FIELDS = {
    "source_path",
    "size_bytes",
    "error",
}


def test_pdf_text_extraction_artifact_smoke_flow_exports_then_inspects(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    valid_pdf_path = tmp_path / "helmet-spec.pdf"
    failed_pdf_path = tmp_path / "broken-spec.pdf"
    ignored_image_path = tmp_path / "helmet.png"
    normal_content = "Shell construction and visor notes."
    non_ascii_newline_content = "Caf\u00e9 racer helm\nBaris kedua"
    empty_content = ""
    warning = "No embedded text found."
    captured_inputs = []

    class FakePdfTextExtractor:

        def extract(self, data):
            captured_inputs.append(data)
            return PdfTextExtractionReport(
                root=data["root"],
                page_extractions=[
                    PdfPageTextExtraction(
                        source_path=str(valid_pdf_path),
                        size_bytes=4096,
                        page_number=1,
                        extraction_index=0,
                        extraction_method="embedded_text",
                        content=normal_content,
                        warnings=[],
                    ),
                    PdfPageTextExtraction(
                        source_path=str(valid_pdf_path),
                        size_bytes=4096,
                        page_number=2,
                        extraction_index=1,
                        extraction_method="embedded_text",
                        content=non_ascii_newline_content,
                        warnings=[],
                    ),
                    PdfPageTextExtraction(
                        source_path=str(valid_pdf_path),
                        size_bytes=4096,
                        page_number=3,
                        extraction_index=2,
                        extraction_method="embedded_text",
                        content=empty_content,
                        warnings=[warning],
                    ),
                ],
                asset_errors=[
                    PdfTextExtractionAssetError(
                        source_path=str(failed_pdf_path),
                        size_bytes=2048,
                        error="Cannot read PDF.",
                    ),
                ],
            )

    monkeypatch.setattr(
        export_module,
        "PdfTextExtractor",
        FakePdfTextExtractor,
    )
    scan_report_path.write_text(
        json.dumps(
            {
                "root": str(tmp_path),
                "items": [
                    {
                        "path": str(valid_pdf_path),
                        "asset_type": "PDF",
                        "size": 4096,
                    },
                    {
                        "path": str(ignored_image_path),
                        "asset_type": "PNG",
                        "size": 1024,
                    },
                    {
                        "path": str(failed_pdf_path),
                        "asset_type": "PDF",
                        "size": 2048,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    artifact = json.loads(output_path.read_text(encoding="utf-8"))

    assert export_result == 0
    assert output_path.exists()
    assert captured_inputs == [
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(valid_pdf_path),
                    "asset_type": "PDF",
                    "size": 4096,
                },
                {
                    "path": str(failed_pdf_path),
                    "asset_type": "PDF",
                    "size": 2048,
                },
            ],
        },
    ]

    assert set(artifact) == TOP_LEVEL_FIELDS
    assert artifact["root"] == str(tmp_path)
    assert artifact["total_pdf_assets"] == 2
    assert artifact["total_page_extractions"] == 3
    assert artifact["failed_pdf_assets"] == 1
    assert artifact["page_extractions"] == [
        {
            "source_path": str(valid_pdf_path),
            "size_bytes": 4096,
            "page_number": 1,
            "extraction_index": 0,
            "extraction_method": "embedded_text",
            "content": normal_content,
            "warnings": [],
        },
        {
            "source_path": str(valid_pdf_path),
            "size_bytes": 4096,
            "page_number": 2,
            "extraction_index": 1,
            "extraction_method": "embedded_text",
            "content": non_ascii_newline_content,
            "warnings": [],
        },
        {
            "source_path": str(valid_pdf_path),
            "size_bytes": 4096,
            "page_number": 3,
            "extraction_index": 2,
            "extraction_method": "embedded_text",
            "content": empty_content,
            "warnings": [warning],
        },
    ]
    assert artifact["asset_errors"] == [
        {
            "source_path": str(failed_pdf_path),
            "size_bytes": 2048,
            "error": "Cannot read PDF.",
        },
    ]

    for page_extraction in artifact["page_extractions"]:
        assert set(page_extraction) == PAGE_EXTRACTION_FIELDS
        assert not set(page_extraction).intersection(FORBIDDEN_FIELDS)

    for asset_error in artifact["asset_errors"]:
        assert set(asset_error) == ASSET_ERROR_FIELDS
        assert not set(asset_error).intersection(FORBIDDEN_FIELDS)

    assert not set(artifact).intersection(FORBIDDEN_FIELDS)

    inspect_result = inspect_main([str(output_path)])

    inspect_output = capsys.readouterr().out
    assert inspect_result == 0
    assert "Total PDF Assets                   : 2" in inspect_output
    assert "Total Page Extractions             : 3" in inspect_output
    assert "Failed PDF Assets                  : 1" in inspect_output
    assert "Empty Content Page Count           : 1" in inspect_output
    assert "Page Warning Count                 : 1" in inspect_output
    assert "Asset Error Count                  : 1" in inspect_output
    assert "Invalid Page Extraction Records    : 0" in inspect_output
    assert "Invalid Asset Error Records        : 0" in inspect_output
    assert "Forbidden Field Count              : 0" in inspect_output
