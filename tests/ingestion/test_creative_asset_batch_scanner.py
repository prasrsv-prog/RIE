from rie.ingestion.creative_asset_batch_scanner import CreativeAssetBatchScanner
from rie.ingestion.creative_asset_type import CreativeAssetType
from rie.ingestion.creative_asset_type_detector import CreativeAssetTypeDetector


def test_scans_direct_files_and_reports_detected_asset_types(tmp_path):
    folder = tmp_path / "batch"
    folder.mkdir()

    png = folder / "png.dat"
    png.write_bytes(b"\x89PNG\r\n\x1a\ncontent")

    jpeg = folder / "jpeg.dat"
    jpeg.write_bytes(b"\xff\xd8\xffcontent")

    pdf = folder / "pdf.dat"
    pdf.write_bytes(b"%PDF-1.7 content")

    text = folder / "prompt.dat"
    text.write_text("Generate a product prompt.", encoding="utf-8")

    unknown = folder / "unknown.dat"
    unknown.write_bytes(b"\x00\xff\xfe")

    misleading_extension = folder / "not-an-image.png"
    misleading_extension.write_bytes(b"\x00not-a-real-png")

    nested_folder = folder / "nested"
    nested_folder.mkdir()
    (nested_folder / "nested.dat").write_bytes(b"\x89PNG\r\n\x1a\ncontent")

    report = CreativeAssetBatchScanner().scan(folder)

    assert report.root == folder
    assert report.total_files == 6
    assert report.count_by_type(CreativeAssetType.PNG) == 1
    assert report.count_by_type(CreativeAssetType.JPEG) == 1
    assert report.count_by_type(CreativeAssetType.PDF) == 1
    assert report.count_by_type(CreativeAssetType.UTF8_TEXT) == 1
    assert report.count_by_type(CreativeAssetType.UNKNOWN) == 2

    scanned_paths = [item.path for item in report.items]
    assert nested_folder / "nested.dat" not in scanned_paths

    png_item = next(item for item in report.items if item.path == png)
    assert png_item.size == png.stat().st_size
    assert png_item.error is None

    misleading_item = next(
        item for item in report.items
        if item.path == misleading_extension
    )
    assert misleading_item.asset_type == CreativeAssetType.UNKNOWN


def test_captures_file_scan_failure(monkeypatch, tmp_path):
    folder = tmp_path / "batch"
    folder.mkdir()
    file = folder / "broken.dat"
    file.write_text("content", encoding="utf-8")

    def fail_detect(path):
        raise OSError("cannot read file")

    monkeypatch.setattr(
        CreativeAssetTypeDetector,
        "detect",
        fail_detect,
    )

    report = CreativeAssetBatchScanner().scan(folder)

    assert report.total_files == 1
    assert report.items[0].path == file
    assert report.items[0].asset_type == CreativeAssetType.UNKNOWN
    assert report.items[0].size == file.stat().st_size
    assert report.items[0].error == "cannot read file"
