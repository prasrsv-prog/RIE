from rie.ingestion.unknown_asset_header_inspector import guess_candidate
from rie.ingestion.unknown_asset_header_inspector import inspect_unknown_assets


def test_inspect_unknown_assets_reads_header_bytes_and_formats_header(tmp_path):
    file = tmp_path / "unknown.dat"
    file.write_bytes(b"RIFFxxxxWEBPmore-bytes")
    data = {
        "items": [
            {
                "path": str(file),
                "asset_type": "UNKNOWN",
                "size": file.stat().st_size,
                "error": None,
            },
            {
                "path": str(tmp_path / "image.dat"),
                "asset_type": "PNG",
                "size": 10,
                "error": None,
            },
        ],
    }

    inspections = inspect_unknown_assets(
        data,
        header_bytes=12,
    )

    assert len(inspections) == 1
    assert inspections[0].path == str(file)
    assert inspections[0].size == file.stat().st_size
    assert inspections[0].header_hex == "52 49 46 46 78 78 78 78 57 45 42 50"
    assert inspections[0].header_ascii == "RIFFxxxxWEBP"
    assert inspections[0].candidate == "WEBP"
    assert inspections[0].error is None


def test_inspect_unknown_assets_respects_limit(tmp_path):
    first = tmp_path / "first.dat"
    second = tmp_path / "second.dat"
    first.write_bytes(b"PK\x03\x04content")
    second.write_bytes(b"\x1f\x8bcontent")
    data = {
        "items": [
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
    }

    inspections = inspect_unknown_assets(
        data,
        limit=1,
    )

    assert len(inspections) == 1
    assert inspections[0].path == str(first)


def test_inspect_unknown_assets_captures_missing_file_error(tmp_path):
    missing = tmp_path / "missing.dat"
    data = {
        "items": [
            {
                "path": str(missing),
                "asset_type": "UNKNOWN",
                "size": 99,
                "error": None,
            },
        ],
    }

    inspections = inspect_unknown_assets(data)

    assert inspections[0].path == str(missing)
    assert inspections[0].size == 99
    assert inspections[0].header_hex == ""
    assert inspections[0].header_ascii == ""
    assert inspections[0].candidate == "UNKNOWN"
    assert inspections[0].error is not None


def test_guess_candidate_detects_small_candidate_set():
    assert guess_candidate(b"RIFFxxxxWEBPmore") == "WEBP"
    assert guess_candidate(b"RIFFxxxxAVI more") == "RIFF_CONTAINER"
    assert guess_candidate(b"PK\x03\x04content") == "ZIP_CONTAINER"
    assert guess_candidate(b"\x1f\x8bcontent") == "GZIP"
    assert guess_candidate(b"GIF89acontent") == "GIF"
    assert guess_candidate(b" \n {\"key\": true}") == "JSON_TEXT"
    assert guess_candidate(b"\x00\x01\x02") == "UNKNOWN"
