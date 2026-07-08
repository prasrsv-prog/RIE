import json

from rie.extraction import export_pdf_text_extractions as export_module
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


def _write_scan_report(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def _report(
    root,
    page_extractions=None,
    asset_errors=None,
):
    return PdfTextExtractionReport(
        root=root,
        page_extractions=page_extractions or [],
        asset_errors=asset_errors or [],
    )


def _patch_extractor(monkeypatch, report):
    captured_inputs = []

    class FakePdfTextExtractor:

        def extract(self, data):
            captured_inputs.append(data)
            return report

    monkeypatch.setattr(
        export_module,
        "PdfTextExtractor",
        FakePdfTextExtractor,
    )

    return captured_inputs


def test_export_pdf_text_extractions_exports_valid_scan_report_with_pdf_asset(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    pdf_path = tmp_path / "helmet.pdf"
    report = _report(
        root=str(tmp_path),
        page_extractions=[
            PdfPageTextExtraction(
                source_path=str(pdf_path),
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Helmet specification text",
                warnings=[],
            ),
        ],
    )
    _patch_extractor(monkeypatch, report)
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(pdf_path),
                    "asset_type": "PDF",
                    "size": 123,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "PDF Text Extraction Export" in output
    assert "Total PDF Assets       : 1" in output
    assert "Total Page Extractions : 1" in output
    assert "Failed PDF Assets      : 0" in output
    assert data["page_extractions"][0]["content"] == (
        "Helmet specification text"
    )


def test_export_pdf_text_extractions_creates_output_file(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _patch_extractor(monkeypatch, _report(root=str(tmp_path)))
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    assert result == 0
    assert output_path.exists()


def test_export_pdf_text_extractions_output_contains_exact_top_level_keys(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _patch_extractor(monkeypatch, _report(root=str(tmp_path)))
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert set(data) == {
        "root",
        "total_pdf_assets",
        "total_page_extractions",
        "failed_pdf_assets",
        "page_extractions",
        "asset_errors",
    }


def test_export_pdf_text_extractions_preserves_root(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    root = "D:\\SPEC"
    _patch_extractor(monkeypatch, _report(root=root))
    _write_scan_report(
        scan_report_path,
        {
            "root": root,
            "items": [],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["root"] == root


def test_export_pdf_text_extractions_uses_empty_root_when_missing(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    captured_inputs = _patch_extractor(monkeypatch, _report(root=""))
    _write_scan_report(
        scan_report_path,
        {
            "items": [],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert captured_inputs[0]["root"] == ""
    assert data["root"] == ""


def test_export_pdf_text_extractions_ignores_non_pdf_assets(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    pdf_path = tmp_path / "helmet.pdf"
    captured_inputs = _patch_extractor(monkeypatch, _report(root=str(tmp_path)))
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(tmp_path / "image.png"),
                    "asset_type": "PNG",
                    "size": 999,
                },
                {
                    "path": str(pdf_path),
                    "asset_type": "PDF",
                    "size": 123,
                },
                {
                    "path": str(tmp_path / "prompt.txt"),
                    "asset_type": "UTF8_TEXT",
                    "size": 11,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()

    assert result == 0
    assert captured_inputs[0]["items"] == [
        {
            "path": str(pdf_path),
            "asset_type": "PDF",
            "size": 123,
        },
    ]


def test_export_pdf_text_extractions_with_no_pdf_assets_succeeds_and_exports_empty_report(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _patch_extractor(monkeypatch, _report(root=str(tmp_path)))
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(tmp_path / "image.png"),
                    "asset_type": "PNG",
                    "size": 999,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Total PDF Assets       : 0" in output
    assert data == {
        "root": str(tmp_path),
        "total_pdf_assets": 0,
        "total_page_extractions": 0,
        "failed_pdf_assets": 0,
        "page_extractions": [],
        "asset_errors": [],
    }


def test_export_pdf_text_extractions_preserves_page_level_fields(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    pdf_path = tmp_path / "helmet.pdf"
    report = _report(
        root=str(tmp_path),
        page_extractions=[
            PdfPageTextExtraction(
                source_path=str(pdf_path),
                size_bytes=123,
                page_number=1,
                extraction_index=0,
                extraction_method="embedded_text",
                content="Page one",
                warnings=[],
            ),
            PdfPageTextExtraction(
                source_path=str(pdf_path),
                size_bytes=123,
                page_number=2,
                extraction_index=1,
                extraction_method="embedded_text",
                content="Page two",
                warnings=["No embedded text found."],
            ),
        ],
    )
    _patch_extractor(monkeypatch, report)
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(pdf_path),
                    "asset_type": "PDF",
                    "size": 123,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["page_extractions"] == [
        {
            "source_path": str(pdf_path),
            "size_bytes": 123,
            "page_number": 1,
            "extraction_index": 0,
            "extraction_method": "embedded_text",
            "content": "Page one",
            "warnings": [],
        },
        {
            "source_path": str(pdf_path),
            "size_bytes": 123,
            "page_number": 2,
            "extraction_index": 1,
            "extraction_method": "embedded_text",
            "content": "Page two",
            "warnings": ["No embedded text found."],
        },
    ]


def test_export_pdf_text_extractions_preserves_exact_content(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    content = "  Specification text with surrounding spaces.  "
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
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
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": "spec.pdf",
                    "asset_type": "PDF",
                    "size": 42,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["page_extractions"][0]["content"] == content


def test_export_pdf_text_extractions_preserves_non_ascii_content(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    content = "Caf\u00e9 racer helm: Rancang konsep."
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
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
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": "spec.pdf",
                    "asset_type": "PDF",
                    "size": 34,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert result == 0
    assert content in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert data["page_extractions"][0]["content"] == content


def test_export_pdf_text_extractions_preserves_newline_content(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    content = "Line 1\nLine 2\n"
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
            page_extractions=[
                PdfPageTextExtraction(
                    source_path="spec.pdf",
                    size_bytes=14,
                    page_number=1,
                    extraction_index=0,
                    extraction_method="embedded_text",
                    content=content,
                    warnings=[],
                ),
            ],
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": "spec.pdf",
                    "asset_type": "PDF",
                    "size": 14,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["page_extractions"][0]["content"] == content


def test_export_pdf_text_extractions_preserves_empty_content_and_warnings(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    warnings = ["No embedded text found."]
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
            page_extractions=[
                PdfPageTextExtraction(
                    source_path="empty.pdf",
                    size_bytes=0,
                    page_number=1,
                    extraction_index=0,
                    extraction_method="embedded_text",
                    content="",
                    warnings=warnings,
                ),
            ],
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": "empty.pdf",
                    "asset_type": "PDF",
                    "size": 0,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["page_extractions"][0]["content"] == ""
    assert data["page_extractions"][0]["warnings"] == warnings


def test_export_pdf_text_extractions_failed_pdf_asset_becomes_asset_error_and_returns_zero(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    broken_path = tmp_path / "broken.pdf"
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
            asset_errors=[
                PdfTextExtractionAssetError(
                    source_path=str(broken_path),
                    size_bytes=321,
                    error="Cannot read PDF.",
                ),
            ],
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": str(broken_path),
                    "asset_type": "PDF",
                    "size": 321,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Failed PDF Assets      : 1" in output
    assert data["asset_errors"] == [
        {
            "source_path": str(broken_path),
            "size_bytes": 321,
            "error": "Cannot read PDF.",
        },
    ]


def test_export_pdf_text_extractions_returns_error_for_missing_input_file(
    tmp_path,
    capsys,
):
    scan_report_path = tmp_path / "missing.json"
    output_path = tmp_path / "pdf-text-extractions.json"

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Scan report not found" in output


def test_export_pdf_text_extractions_returns_error_for_directory_input(
    tmp_path,
    capsys,
):
    output_path = tmp_path / "pdf-text-extractions.json"

    result = export_module.main([
        str(tmp_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_export_pdf_text_extractions_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    scan_report_path.write_text("{invalid-json", encoding="utf-8")

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read scan report" in output


def test_export_pdf_text_extractions_returns_error_for_malformed_top_level_artifact(
    tmp_path,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _write_scan_report(scan_report_path, [])

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed scan report" in output


def test_export_pdf_text_extractions_returns_error_for_items_not_list(
    tmp_path,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": {},
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed scan report" in output


def test_export_pdf_text_extractions_output_does_not_include_forbidden_structured_fields(
    tmp_path,
    monkeypatch,
    capsys,
):
    scan_report_path = tmp_path / "creative-asset-scan-report.json"
    output_path = tmp_path / "pdf-text-extractions.json"
    _patch_extractor(
        monkeypatch,
        _report(
            root=str(tmp_path),
            page_extractions=[
                PdfPageTextExtraction(
                    source_path="spec.pdf",
                    size_bytes=123,
                    page_number=1,
                    extraction_index=0,
                    extraction_method="embedded_text",
                    content=(
                        "Raw PDF text may contain prompt, summary, "
                        "and helmet_model."
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
        ),
    )
    _write_scan_report(
        scan_report_path,
        {
            "root": str(tmp_path),
            "items": [
                {
                    "path": "spec.pdf",
                    "asset_type": "PDF",
                    "size": 123,
                },
            ],
        },
    )

    result = export_module.main([
        str(scan_report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert not set(data).intersection(FORBIDDEN_FIELDS)
    assert not set(data["page_extractions"][0]).intersection(
        FORBIDDEN_FIELDS
    )
    assert not set(data["asset_errors"][0]).intersection(FORBIDDEN_FIELDS)
