import json

from rie.extraction.inspect_pdf_text_extractions import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data),
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


def _valid_asset_error(**overrides):
    asset_error = {
        "source_path": "broken.pdf",
        "size_bytes": 321,
        "error": "Cannot read PDF.",
    }
    asset_error.update(overrides)
    return asset_error


def _valid_artifact(**overrides):
    artifact = {
        "root": "D:\\SPEC",
        "total_pdf_assets": 1,
        "total_page_extractions": 1,
        "failed_pdf_assets": 0,
        "page_extractions": [
            _valid_page(),
        ],
        "asset_errors": [],
    }
    artifact.update(overrides)
    return artifact


def test_inspect_pdf_text_extractions_valid_artifact_returns_zero(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    capsys.readouterr()
    assert result == 0


def test_inspect_pdf_text_extractions_prints_total_pdf_assets(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(total_pdf_assets=2),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "PDF Text Extraction Inspection" in output
    assert "Total PDF Assets                   : 2" in output


def test_inspect_pdf_text_extractions_prints_total_page_extractions(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(total_page_extractions=3),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Page Extractions             : 3" in output


def test_inspect_pdf_text_extractions_prints_failed_pdf_assets(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(failed_pdf_assets=1),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Failed PDF Assets                  : 1" in output


def test_inspect_pdf_text_extractions_prints_empty_content_page_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(page_extractions=[_valid_page(content="")]),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Empty Content Page Count           : 1" in output


def test_inspect_pdf_text_extractions_prints_page_warning_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            page_extractions=[
                _valid_page(
                    warnings=[
                        "No embedded text found.",
                        "Page warning.",
                    ],
                ),
            ],
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Page Warning Count                 : 2" in output


def test_inspect_pdf_text_extractions_prints_asset_error_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            asset_errors=[_valid_asset_error()],
            failed_pdf_assets=1,
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Asset Error Count                  : 1" in output


def test_inspect_pdf_text_extractions_prints_invalid_page_record_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            page_extractions=[_valid_page(source_path=123)],
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Page Extraction Records    : 1" in output


def test_inspect_pdf_text_extractions_prints_invalid_asset_error_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            asset_errors=[_valid_asset_error(error=123)],
            failed_pdf_assets=1,
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Asset Error Records        : 1" in output


def test_inspect_pdf_text_extractions_prints_forbidden_field_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            page_extractions=[
                _valid_page(prompt="Do not write prompts here."),
            ],
            asset_errors=[
                _valid_asset_error(summary="Do not summarize."),
            ],
            failed_pdf_assets=1,
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Forbidden Field Count              : 2" in output


def test_inspect_pdf_text_extractions_readable_artifact_with_invalid_records_returns_zero(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            page_extractions=[
                _valid_page(prompt="Do not write prompts here."),
                "not a page",
            ],
            asset_errors=[
                _valid_asset_error(error=123),
                "not an asset error",
            ],
            failed_pdf_assets=2,
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Page Extraction Records    : 2" in output
    assert "Invalid Asset Error Records        : 2" in output
    assert "Forbidden Field Count              : 1" in output


def test_inspect_pdf_text_extractions_missing_input_file_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "missing.json"

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "PDF text extraction artifact not found" in output


def test_inspect_pdf_text_extractions_directory_input_returns_one(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_pdf_text_extractions_invalid_json_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    artifact_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read PDF text extraction artifact" in output


def test_inspect_pdf_text_extractions_top_level_list_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(artifact_path, [])

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output


def test_inspect_pdf_text_extractions_missing_required_top_level_key_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    artifact = _valid_artifact()
    del artifact["asset_errors"]
    _write_artifact(artifact_path, artifact)

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output


def test_inspect_pdf_text_extractions_extra_top_level_key_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(extra="field"),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output


def test_inspect_pdf_text_extractions_page_extractions_not_list_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(page_extractions={}),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output


def test_inspect_pdf_text_extractions_asset_errors_not_list_returns_one(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-extractions.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(asset_errors={}),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text extraction artifact" in output
