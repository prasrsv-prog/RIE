import json

from rie.extraction.inspect_text_extraction_evidence import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_inspect_text_extraction_evidence_prints_summary(tmp_path, capsys):
    evidence_path = tmp_path / "text-evidence.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "first.dat",
                    "content": "First",
                    "size_bytes": 5,
                },
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                },
            ],
        },
    )

    result = main([str(evidence_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Text Extraction Evidence Inspection" in output
    assert "Total Evidences          : 2" in output
    assert "Total Content Characters : 5" in output
    assert "Empty Content Count      : 1" in output
    assert "Invalid Record Count     : 0" in output
    assert "Forbidden Field Count    : 0" in output


def test_inspect_text_extraction_evidence_returns_error_for_missing_file(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "missing.json"

    result = main([str(evidence_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Evidence artifact not found" in output


def test_inspect_text_extraction_evidence_returns_error_for_directory(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_text_extraction_evidence_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    evidence_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(evidence_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read evidence artifact" in output


def test_inspect_text_extraction_evidence_returns_error_for_malformed_artifact(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    _write_artifact(
        evidence_path,
        {
            "items": [],
        },
    )

    result = main([str(evidence_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed evidence artifact" in output


def test_inspect_text_extraction_evidence_returns_zero_for_invalid_records_after_readable_artifact(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "summary.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "summary": "No summary belongs here.",
                },
                "not a record",
            ],
        },
    )

    result = main([str(evidence_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Evidences          : 2" in output
    assert "Invalid Record Count     : 2" in output
    assert "Forbidden Field Count    : 1" in output
