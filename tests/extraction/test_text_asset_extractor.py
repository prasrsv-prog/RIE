from rie.extraction.text_asset_extractor import TextAssetExtractor


def test_extracts_only_utf8_text_assets_and_preserves_content(tmp_path):
    text_file = tmp_path / "prompt.dat"
    content = "Line 1\nCafé racer helmet prompt\n"
    text_file.write_text(content, encoding="utf-8")

    data = {
        "root": str(tmp_path),
        "items": [
            {
                "path": str(text_file),
                "asset_type": "UTF8_TEXT",
                "size": 32,
                "error": None,
            },
            {
                "path": str(tmp_path / "missing-image.dat"),
                "asset_type": "PNG",
                "size": 999,
                "error": None,
            },
            {
                "path": str(tmp_path / "missing-document.dat"),
                "asset_type": "PDF",
                "size": 888,
                "error": None,
            },
            {
                "path": str(tmp_path / "missing-archive.dat"),
                "asset_type": "ZIP_CONTAINER",
                "size": 777,
                "error": None,
            },
        ],
    }

    report = TextAssetExtractor().extract(data)

    assert report.root == str(tmp_path)
    assert report.total_text_assets == 1
    assert report.failed == 0
    assert len(report.extractions) == 1

    extraction = report.extractions[0]
    assert extraction.path == text_file
    assert extraction.size == 32
    assert extraction.content == content
    assert extraction.error is None


def test_missing_utf8_text_file_becomes_failed_extraction(tmp_path):
    missing_file = tmp_path / "missing-prompt.dat"
    data = {
        "root": str(tmp_path),
        "items": [
            {
                "path": str(missing_file),
                "asset_type": "UTF8_TEXT",
                "size": 12,
                "error": None,
            },
        ],
    }

    report = TextAssetExtractor().extract(data)

    assert report.total_text_assets == 1
    assert report.failed == 1
    assert report.extractions[0].path == missing_file
    assert report.extractions[0].size == 12
    assert report.extractions[0].content == ""
    assert report.extractions[0].error is not None


def test_invalid_utf8_text_file_becomes_failed_extraction(tmp_path):
    invalid_file = tmp_path / "invalid-prompt.dat"
    invalid_file.write_bytes(b"\xff\xfe\xfd")
    data = {
        "root": str(tmp_path),
        "items": [
            {
                "path": str(invalid_file),
                "asset_type": "UTF8_TEXT",
                "size": 3,
                "error": None,
            },
        ],
    }

    report = TextAssetExtractor().extract(data)

    assert report.total_text_assets == 1
    assert report.failed == 1
    assert report.extractions[0].path == invalid_file
    assert report.extractions[0].content == ""
    assert report.extractions[0].error is not None
