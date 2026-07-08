import json

from rie.extraction.export_pdf_text_evidence import main


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


PDF_TEXT_EVIDENCE_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "warnings",
    "evidence_index",
}


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
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


def _artifact(page_extractions):
    return {
        "root": "D:\\SPEC",
        "total_pdf_assets": 1,
        "total_page_extractions": len(page_extractions),
        "failed_pdf_assets": 0,
        "page_extractions": page_extractions,
        "asset_errors": [],
    }


def test_export_pdf_text_evidence_writes_valid_artifact(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(
                source_path="helmet-spec.pdf",
                content="Shell construction",
                size_bytes=4096,
                page_number=2,
                extraction_index=7,
                extraction_method="embedded_text",
                warnings=["No embedded text found."],
            ),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert output_path.exists()
    assert "PDF Text Evidence Export" in output
    assert "Total PDF Extraction Pages : 1" in output
    assert "Exported PDF Evidences     : 1" in output
    assert "Skipped Invalid Records    : 0" in output
    assert set(data) == {"pdf_text_evidences"}
    assert data["pdf_text_evidences"] == [
        {
            "source_path": "helmet-spec.pdf",
            "content": "Shell construction",
            "size_bytes": 4096,
            "page_number": 2,
            "extraction_index": 7,
            "extraction_method": "embedded_text",
            "warnings": ["No embedded text found."],
            "evidence_index": 0,
        },
    ]


def test_export_pdf_text_evidence_preserves_content_variants(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    non_ascii_newline_content = "Caf\u00e9 racer helm\nBaris kedua"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(
                source_path="non-ascii.pdf",
                content=non_ascii_newline_content,
                extraction_index=0,
            ),
            _valid_page(
                source_path="empty.pdf",
                content="",
                extraction_index=1,
                warnings=["No embedded text found."],
            ),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert result == 0
    assert "Café racer helm" in raw_json
    assert "Baris kedua" in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert data["pdf_text_evidences"][0]["content"] == (
        non_ascii_newline_content
    )
    assert data["pdf_text_evidences"][1]["content"] == ""
    assert data["pdf_text_evidences"][1]["warnings"] == [
        "No embedded text found.",
    ]


def test_export_pdf_text_evidence_preserves_order_and_evidence_index(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(
                source_path="first.pdf",
                page_number=5,
                extraction_index=10,
            ),
            _valid_page(
                source_path="second.pdf",
                page_number=6,
                extraction_index=11,
            ),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    records = json.loads(
        output_path.read_text(encoding="utf-8")
    )["pdf_text_evidences"]

    assert result == 0
    assert [record["source_path"] for record in records] == [
        "first.pdf",
        "second.pdf",
    ]
    assert [record["page_number"] for record in records] == [5, 6]
    assert [record["extraction_index"] for record in records] == [10, 11]
    assert [record["evidence_index"] for record in records] == [0, 1]


def test_export_pdf_text_evidence_skips_invalid_page_records(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(source_path="first.pdf"),
            _valid_page(size_bytes=True),
            _valid_page(warnings=["Warning", 123]),
            _valid_page(source_path="second.pdf", extraction_index=3),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    records = json.loads(
        output_path.read_text(encoding="utf-8")
    )["pdf_text_evidences"]

    assert result == 0
    assert "Total PDF Extraction Pages : 4" in output
    assert "Exported PDF Evidences     : 2" in output
    assert "Skipped Invalid Records    : 2" in output
    assert [record["source_path"] for record in records] == [
        "first.pdf",
        "second.pdf",
    ]
    assert [record["evidence_index"] for record in records] == [0, 1]


def test_export_pdf_text_evidence_allows_empty_output(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(input_path, _artifact([]))

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data == {"pdf_text_evidences": []}


def test_export_pdf_text_evidence_returns_error_for_missing_input(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "missing.json"
    output_path = tmp_path / "pdf-text-evidence.json"

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "not found" in output


def test_export_pdf_text_evidence_returns_error_for_directory_input(
    tmp_path,
    capsys,
):
    output_path = tmp_path / "pdf-text-evidence.json"

    result = main([
        str(tmp_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_export_pdf_text_evidence_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    input_path.write_text("{invalid-json", encoding="utf-8")

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read PDF text extraction artifact" in output


def test_export_pdf_text_evidence_returns_error_for_malformed_artifact(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(input_path, [])

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output


def test_export_pdf_text_evidence_returns_error_for_missing_page_extractions(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(input_path, {"root": "D:\\SPEC"})

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "page_extractions" in output


def test_export_pdf_text_evidence_returns_error_for_page_extractions_not_list(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(input_path, {"page_extractions": {}})

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "page_extractions" in output


def test_export_pdf_text_evidence_returns_error_for_missing_output_parent(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "missing" / "pdf-text-evidence.json"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Output folder not found" in output


def test_export_pdf_text_evidence_emits_no_forbidden_structured_fields(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        input_path,
        _artifact([
            _valid_page(
                content=(
                    "Raw PDF text may mention prompt, summary, "
                    "or helmet_model."
                ),
            ),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert not set(data).intersection(FORBIDDEN_FIELDS)
    for record in data["pdf_text_evidences"]:
        assert set(record) == PDF_TEXT_EVIDENCE_FIELDS
        assert not set(record).intersection(FORBIDDEN_FIELDS)
