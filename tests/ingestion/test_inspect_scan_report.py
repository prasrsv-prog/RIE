import json

from rie.ingestion.inspect_scan_report import main


def _write_report(path):
    data = {
        "root": "D:\\DAT",
        "total_files": 4,
        "counts": {
            "PNG": 1,
            "JPEG": 1,
            "PDF": 1,
            "UTF8_TEXT": 1,
            "UNKNOWN": 0,
        },
        "failed": 1,
        "items": [
            {
                "path": "D:\\DAT\\image.dat",
                "asset_type": "PNG",
                "size": 100,
                "error": None,
            },
            {
                "path": "D:\\DAT\\photo.dat",
                "asset_type": "JPEG",
                "size": 500,
                "error": None,
            },
            {
                "path": "D:\\DAT\\document.dat",
                "asset_type": "PDF",
                "size": 300,
                "error": "read warning",
            },
            {
                "path": "D:\\DAT\\prompt.dat",
                "asset_type": "UTF8_TEXT",
                "size": 50,
                "error": None,
            },
        ],
    }
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_inspect_scan_report_prints_key_sections(tmp_path, capsys):
    report_path = tmp_path / "report.json"
    _write_report(report_path)

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Creative Asset Scan Report Inspection" in output
    assert "Root        : D:\\DAT" in output
    assert "Total Files : 4" in output
    assert "Counts:" in output
    assert "PNG        : 1" in output
    assert "Total Size by Type:" in output
    assert "JPEG       : 500" in output
    assert "Top Largest Files:" in output
    assert "- JPEG 500 D:\\DAT\\photo.dat" in output
    assert "UTF8_TEXT Files:" in output
    assert "- 50 D:\\DAT\\prompt.dat" in output
    assert "PDF Files:" in output
    assert "- 300 D:\\DAT\\document.dat" in output
    assert "Failed Files:" in output
    assert "- PDF D:\\DAT\\document.dat read warning" in output


def test_inspect_scan_report_returns_error_for_missing_report(tmp_path, capsys):
    report_path = tmp_path / "missing.json"

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Report not found" in output


def test_inspect_scan_report_returns_error_for_directory(tmp_path, capsys):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_scan_report_returns_error_for_invalid_json(tmp_path, capsys):
    report_path = tmp_path / "report.json"
    report_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(report_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read report" in output


def test_inspect_scan_report_top_limits_largest_files(tmp_path, capsys):
    report_path = tmp_path / "report.json"
    _write_report(report_path)

    result = main([
        str(report_path),
        "--top",
        "1",
    ])

    output = capsys.readouterr().out
    assert result == 0
    assert "- JPEG 500 D:\\DAT\\photo.dat" in output
    assert "- PDF 300 D:\\DAT\\document.dat" not in output
