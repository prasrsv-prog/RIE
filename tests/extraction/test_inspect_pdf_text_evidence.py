import json

from rie.extraction.inspect_pdf_text_evidence import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def _valid_evidence(**overrides):
    evidence = {
        "source_path": "spec.pdf",
        "content": "Page text",
        "size_bytes": 123,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "embedded_text",
        "warnings": [],
        "evidence_index": 0,
    }
    evidence.update(overrides)
    return evidence


def _valid_artifact(**overrides):
    artifact = {
        "pdf_text_evidences": [
            _valid_evidence(
                content="First",
                warnings=["No embedded text found."],
            ),
            _valid_evidence(
                content="",
                evidence_index=1,
            ),
        ],
    }
    artifact.update(overrides)
    return artifact


def test_inspect_pdf_text_evidence_valid_artifact_returns_zero(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    capsys.readouterr()
    assert result == 0


def test_inspect_pdf_text_evidence_prints_total_pdf_text_evidences(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total PDF Text Evidences       : 2" in output


def test_inspect_pdf_text_evidence_prints_total_content_characters(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Content Characters       : 5" in output


def test_inspect_pdf_text_evidence_prints_empty_content_evidence_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Empty Content Evidence Count   : 1" in output


def test_inspect_pdf_text_evidence_prints_warning_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, _valid_artifact())

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Warning Count                  : 1" in output


def test_inspect_pdf_text_evidence_prints_invalid_record_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(size_bytes=True),
            ],
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Record Count           : 1" in output


def test_inspect_pdf_text_evidence_prints_forbidden_field_count(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        artifact_path,
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(prompt="Do not write prompts here."),
            ],
        ),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Forbidden Field Count          : 1" in output


def test_inspect_pdf_text_evidence_readable_artifact_with_invalid_records_returns_zero(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        artifact_path,
        {
            "pdf_text_evidences": [
                "not a record",
                _valid_evidence(warnings=["Warning", 123]),
            ],
        },
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Record Count           : 2" in output


def test_inspect_pdf_text_evidence_returns_error_for_missing_input_file(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "missing.json"

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "not found" in output


def test_inspect_pdf_text_evidence_returns_error_for_directory_input(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_pdf_text_evidence_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    artifact_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read PDF text evidence artifact" in output


def test_inspect_pdf_text_evidence_returns_error_for_top_level_list(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, [])

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed PDF text evidence artifact" in output


def test_inspect_pdf_text_evidence_returns_error_for_missing_pdf_text_evidences(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, {})

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "pdf_text_evidences" in output


def test_inspect_pdf_text_evidence_returns_error_for_extra_top_level_key(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(
        artifact_path,
        {
            "pdf_text_evidences": [],
            "extra": "field",
        },
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "exactly" in output


def test_inspect_pdf_text_evidence_returns_error_for_pdf_text_evidences_not_list(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "pdf-text-evidence.json"
    _write_artifact(artifact_path, {"pdf_text_evidences": {}})

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "pdf_text_evidences" in output
