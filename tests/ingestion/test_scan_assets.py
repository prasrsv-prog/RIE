import json

from rie.ingestion.scan_assets import main


def test_scan_assets_prints_summary_for_valid_folder(tmp_path, capsys):
    folder = tmp_path / "batch"
    folder.mkdir()
    (folder / "image.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    (folder / "prompt.dat").write_text("Generate a prompt.", encoding="utf-8")
    (folder / "unknown.dat").write_bytes(b"\x00\xff")

    result = main([str(folder)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Creative Asset Scan Report" in output
    assert f"Root        : {folder}" in output
    assert "Total Files : 3" in output
    assert "PNG        : 1" in output
    assert "UTF8_TEXT  : 1" in output
    assert "UNKNOWN    : 1" in output
    assert "Failed     : 0" in output


def test_scan_assets_writes_json_report_with_output(tmp_path, capsys):
    folder = tmp_path / "batch"
    folder.mkdir()
    (folder / "image.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    (folder / "prompt.dat").write_text("Generate a prompt.", encoding="utf-8")
    output_path = tmp_path / "report.json"

    result = main([
        str(folder),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Creative Asset Scan Report" in output
    assert "Total Files : 2" in output
    assert data["root"] == str(folder)
    assert data["total_files"] == 2
    assert data["counts"]["PNG"] == 1
    assert data["counts"]["UTF8_TEXT"] == 1
    assert data["failed"] == 0
    assert len(data["items"]) == 2


def test_scan_assets_returns_error_for_missing_folder(tmp_path, capsys):
    folder = tmp_path / "missing"

    result = main([str(folder)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Folder not found" in output


def test_scan_assets_returns_error_for_file_path(tmp_path, capsys):
    file = tmp_path / "asset.dat"
    file.write_text("content", encoding="utf-8")

    result = main([str(file)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a folder" in output


def test_scan_assets_returns_error_for_missing_output_parent(tmp_path, capsys):
    folder = tmp_path / "batch"
    folder.mkdir()
    (folder / "image.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    output_path = tmp_path / "missing" / "report.json"

    result = main([
        str(folder),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Output folder not found" in output


def test_scan_assets_returns_error_for_json_write_failure(
    monkeypatch,
    tmp_path,
    capsys,
):
    folder = tmp_path / "batch"
    folder.mkdir()
    (folder / "image.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")
    output_path = tmp_path / "report.json"

    def fail_write_json(report, output_path):
        raise OSError("cannot write report")

    monkeypatch.setattr(
        "rie.ingestion.scan_assets.write_json",
        fail_write_json,
    )

    result = main([
        str(folder),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to write report: cannot write report" in output


def test_scan_assets_is_non_recursive_by_default(tmp_path, capsys):
    folder = tmp_path / "batch"
    nested = folder / "nested"
    nested.mkdir(parents=True)
    (folder / "top.dat").write_bytes(b"\xff\xd8\xffcontent")
    (nested / "nested.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")

    result = main([str(folder)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Files : 1" in output
    assert "JPEG       : 1" in output
    assert "PNG        : 0" in output


def test_scan_assets_recursive_includes_nested_files(tmp_path, capsys):
    folder = tmp_path / "batch"
    nested = folder / "nested"
    nested.mkdir(parents=True)
    (folder / "top.dat").write_bytes(b"\xff\xd8\xffcontent")
    (nested / "nested.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")

    result = main([
        "--recursive",
        str(folder),
    ])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Files : 2" in output
    assert "JPEG       : 1" in output
    assert "PNG        : 1" in output
