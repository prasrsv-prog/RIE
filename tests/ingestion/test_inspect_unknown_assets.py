import json

from rie.ingestion.inspect_unknown_assets import main


def _write_report(path, items):
    path.write_text(
        json.dumps(
            {
                "items": items,
            }
        ),
        encoding="utf-8",
    )


def test_inspect_unknown_assets_prints_header_details(tmp_path, capsys):
    unknown = tmp_path / "unknown.dat"
    unknown.write_bytes(b"PK\x03\x04content")
    report = tmp_path / "report.json"
    _write_report(
        report,
        [
            {
                "path": str(unknown),
                "asset_type": "UNKNOWN",
                "size": unknown.stat().st_size,
                "error": None,
            },
        ],
    )

    result = main([str(report)])

    output = capsys.readouterr().out
    assert result == 0
    assert "UNKNOWN Asset Header Inspection" in output
    assert "Total UNKNOWN : 1" in output
    assert str(unknown) in output
    assert "Header HEX   : 50 4b 03 04" in output
    assert "Header ASCII : PK.." in output
    assert "Candidate    : ZIP_CONTAINER" in output


def test_inspect_unknown_assets_bytes_changes_header_length(tmp_path, capsys):
    unknown = tmp_path / "unknown.dat"
    unknown.write_bytes(b"PK\x03\x04content")
    report = tmp_path / "report.json"
    _write_report(
        report,
        [
            {
                "path": str(unknown),
                "asset_type": "UNKNOWN",
                "size": unknown.stat().st_size,
                "error": None,
            },
        ],
    )

    result = main([
        str(report),
        "--bytes",
        "2",
    ])

    output = capsys.readouterr().out
    assert result == 0
    assert "Header HEX   : 50 4b" in output
    assert "Header ASCII : PK" in output


def test_inspect_unknown_assets_limit_limits_printed_items(tmp_path, capsys):
    first = tmp_path / "first.dat"
    second = tmp_path / "second.dat"
    first.write_bytes(b"PK\x03\x04content")
    second.write_bytes(b"\x1f\x8bcontent")
    report = tmp_path / "report.json"
    _write_report(
        report,
        [
            {
                "path": str(first),
                "asset_type": "UNKNOWN",
                "size": first.stat().st_size,
                "error": None,
            },
            {
                "path": str(second),
                "asset_type": "UNKNOWN",
                "size": second.stat().st_size,
                "error": None,
            },
        ],
    )

    result = main([
        str(report),
        "--limit",
        "1",
    ])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total UNKNOWN : 1" in output
    assert str(first) in output
    assert str(second) not in output


def test_inspect_unknown_assets_returns_error_for_missing_report(
    tmp_path,
    capsys,
):
    report = tmp_path / "missing.json"

    result = main([str(report)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Report not found" in output


def test_inspect_unknown_assets_returns_error_for_directory(tmp_path, capsys):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_unknown_assets_returns_error_for_invalid_json(tmp_path, capsys):
    report = tmp_path / "report.json"
    report.write_text("{invalid-json", encoding="utf-8")

    result = main([str(report)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read report" in output
