import json

from rie.extraction.export_text_extraction_evidence import main
from rie.extraction.text_asset_extraction_report_serializer import (
    from_dict,
)
from rie.extraction.text_asset_extraction_report_serializer import (
    load_json,
)


def _write_extraction_report(path, root, extractions):
    path.write_text(
        json.dumps(
            {
                "root": str(root),
                "total_text_assets": len(extractions),
                "failed": sum(
                    extraction.get("error") is not None
                    for extraction in extractions
                ),
                "extractions": extractions,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_from_dict_deserializes_text_asset_extraction_report(tmp_path):
    successful_path = tmp_path / "prompt.dat"
    failed_path = tmp_path / "missing.dat"

    report = from_dict(
        {
            "root": str(tmp_path),
            "total_text_assets": 2,
            "failed": 0,
            "extractions": [
                {
                    "path": str(successful_path),
                    "size": 25,
                    "content": "Prompt content",
                    "error": None,
                },
                {
                    "path": str(failed_path),
                    "size": 0,
                    "content": "",
                    "error": "missing file",
                },
            ],
        }
    )

    assert report.root == str(tmp_path)
    assert report.total_text_assets == 2
    assert report.failed == 1
    assert report.extractions[0].path == successful_path
    assert report.extractions[0].size == 25
    assert report.extractions[0].content == "Prompt content"
    assert report.extractions[0].error is None
    assert report.extractions[1].path == failed_path
    assert report.extractions[1].error == "missing file"


def test_load_json_reads_text_asset_extraction_report(tmp_path):
    report_path = tmp_path / "text-extractions.json"
    text_path = tmp_path / "prompt.dat"
    _write_extraction_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_path),
                "size": 26,
                "content": "Generate a helmet concept.",
                "error": None,
            },
        ],
    )

    report = load_json(report_path)

    assert report.root == str(tmp_path)
    assert report.total_text_assets == 1
    assert report.failed == 0
    assert report.extractions[0].path == text_path
    assert report.extractions[0].content == "Generate a helmet concept."


def test_export_text_extraction_evidence_writes_successful_extractions(
    tmp_path,
    capsys,
):
    first_path = tmp_path / "first.dat"
    second_path = tmp_path / "second.dat"
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "text-evidence.json"
    _write_extraction_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(first_path),
                "size": 12,
                "content": "First prompt",
                "error": None,
            },
            {
                "path": str(second_path),
                "size": 13,
                "content": "Second prompt",
                "error": None,
            },
        ],
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Text Extraction Evidence Export" in output
    assert f"Root              : {tmp_path}" in output
    assert "Total Extractions : 2" in output
    assert "Skipped Failed    : 0" in output
    assert "Evidence Count    : 2" in output
    assert f"Output Path       : {output_path}" in output
    assert data == {
        "evidences": [
            {
                "source_path": str(first_path),
                "content": "First prompt",
                "size_bytes": 12,
            },
            {
                "source_path": str(second_path),
                "content": "Second prompt",
                "size_bytes": 13,
            },
        ],
    }


def test_export_text_extraction_evidence_skips_failed_extractions(
    tmp_path,
    capsys,
):
    successful_path = tmp_path / "prompt.dat"
    failed_path = tmp_path / "missing.dat"
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "text-evidence.json"
    _write_extraction_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(successful_path),
                "size": 11,
                "content": "Prompt text",
                "error": None,
            },
            {
                "path": str(failed_path),
                "size": 0,
                "content": "",
                "error": "missing file",
            },
        ],
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Skipped Failed    : 1" in output
    assert "Evidence Count    : 1" in output
    assert data["evidences"] == [
        {
            "source_path": str(successful_path),
            "content": "Prompt text",
            "size_bytes": 11,
        },
    ]


def test_export_text_extraction_evidence_preserves_non_ascii_content(
    tmp_path,
    capsys,
):
    text_path = tmp_path / "prompt.dat"
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "text-evidence.json"
    content = "Caf\u00e9 racer helm: Rancang konsep."
    _write_extraction_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_path),
                "size": 34,
                "content": content,
                "error": None,
            },
        ],
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert result == 0
    assert content in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert data["evidences"][0]["content"] == content


def test_export_text_extraction_evidence_returns_error_for_missing_report(
    tmp_path,
    capsys,
):
    report_path = tmp_path / "missing.json"
    output_path = tmp_path / "text-evidence.json"

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Report not found" in output


def test_export_text_extraction_evidence_returns_error_for_directory(
    tmp_path,
    capsys,
):
    output_path = tmp_path / "text-evidence.json"

    result = main([
        str(tmp_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_export_text_extraction_evidence_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "text-evidence.json"
    report_path.write_text("{invalid-json", encoding="utf-8")

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read extraction report" in output


def test_export_text_extraction_evidence_returns_error_for_malformed_report(
    tmp_path,
    capsys,
):
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "text-evidence.json"
    report_path.write_text(
        json.dumps(
            {
                "root": str(tmp_path),
                "extractions": [],
            }
        ),
        encoding="utf-8",
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read extraction report" in output


def test_export_text_extraction_evidence_returns_error_for_missing_output_parent(
    tmp_path,
    capsys,
):
    text_path = tmp_path / "prompt.dat"
    report_path = tmp_path / "text-extractions.json"
    output_path = tmp_path / "missing" / "text-evidence.json"
    _write_extraction_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_path),
                "size": 6,
                "content": "Prompt",
                "error": None,
            },
        ],
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Output folder not found" in output
