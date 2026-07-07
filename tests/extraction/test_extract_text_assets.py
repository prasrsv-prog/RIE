import json

from rie.extraction.extract_text_assets import main


def _write_scan_report(path, root, items):
    path.write_text(
        json.dumps(
            {
                "root": str(root),
                "total_files": len(items),
                "counts": {},
                "failed": 0,
                "items": items,
            }
        ),
        encoding="utf-8",
    )


def test_extract_text_assets_prints_summary_for_valid_report(tmp_path, capsys):
    text_file = tmp_path / "prompt.dat"
    text_file.write_text("Generate a helmet concept.", encoding="utf-8")
    report_path = tmp_path / "scan-report.json"
    _write_scan_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_file),
                "asset_type": "UTF8_TEXT",
                "size": 26,
                "error": None,
            },
        ],
    )

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Text Asset Extraction Report" in output
    assert f"Root              : {tmp_path}" in output
    assert "Total Text Assets : 1" in output
    assert "Failed            : 0" in output
    assert f"- 26 {text_file}" in output


def test_extract_text_assets_writes_json_with_output(tmp_path, capsys):
    text_file = tmp_path / "prompt.dat"
    text_file.write_text("Rancang helm Café Racer.", encoding="utf-8")
    report_path = tmp_path / "scan-report.json"
    output_path = tmp_path / "text-extractions.json"
    _write_scan_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_file),
                "asset_type": "UTF8_TEXT",
                "size": 24,
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
    assert "Text Asset Extraction Report" in output
    assert data["root"] == str(tmp_path)
    assert data["total_text_assets"] == 1
    assert data["failed"] == 0
    assert data["extractions"][0]["content"] == "Rancang helm Café Racer."


def test_extract_text_assets_returns_error_for_missing_report(tmp_path, capsys):
    report_path = tmp_path / "missing.json"

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Report not found" in output


def test_extract_text_assets_returns_error_for_directory(tmp_path, capsys):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_extract_text_assets_returns_error_for_invalid_json(tmp_path, capsys):
    report_path = tmp_path / "scan-report.json"
    report_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read report" in output


def test_extract_text_assets_returns_error_for_missing_output_parent(
    tmp_path,
    capsys,
):
    text_file = tmp_path / "prompt.dat"
    text_file.write_text("Prompt", encoding="utf-8")
    report_path = tmp_path / "scan-report.json"
    output_path = tmp_path / "missing" / "text-extractions.json"
    _write_scan_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_file),
                "asset_type": "UTF8_TEXT",
                "size": 6,
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


def test_extract_text_assets_returns_error_for_write_failure(
    monkeypatch,
    tmp_path,
    capsys,
):
    text_file = tmp_path / "prompt.dat"
    text_file.write_text("Prompt", encoding="utf-8")
    report_path = tmp_path / "scan-report.json"
    output_path = tmp_path / "text-extractions.json"
    _write_scan_report(
        report_path,
        tmp_path,
        [
            {
                "path": str(text_file),
                "asset_type": "UTF8_TEXT",
                "size": 6,
                "error": None,
            },
        ],
    )

    def fail_write_json(report, output_path):
        raise OSError("cannot write extraction")

    monkeypatch.setattr(
        "rie.extraction.extract_text_assets.write_json",
        fail_write_json,
    )

    result = main([
        str(report_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert (
        "Failed to write extraction report: cannot write extraction"
        in output
    )
