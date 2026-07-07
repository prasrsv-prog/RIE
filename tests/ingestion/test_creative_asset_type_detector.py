from rie.ingestion.creative_asset_type import CreativeAssetType
from rie.ingestion.creative_asset_type_detector import CreativeAssetTypeDetector


def test_detects_png_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "image.dat"
    path.write_bytes(b"\x89PNG\r\n\x1a\ncontent")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.PNG


def test_detects_jpeg_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "image.dat"
    path.write_bytes(b"\xff\xd8\xffcontent")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.JPEG


def test_detects_pdf_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "document.dat"
    path.write_bytes(b"%PDF-1.7 content")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.PDF


def test_detects_webp_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "image.dat"
    path.write_bytes(b"RIFFxxxxWEBPcontent")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.WEBP


def test_detects_little_endian_tiff_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "image.dat"
    path.write_bytes(b"II*\x00content")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.TIFF


def test_detects_big_endian_tiff_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "image.dat"
    path.write_bytes(b"MM\x00*content")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.TIFF


def test_detects_mp4_mp42_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "video.dat"
    path.write_bytes(b"\x00\x00\x00\x18ftypmp42content")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.MP4


def test_detects_mp4_isom_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "video.dat"
    path.write_bytes(b"\x00\x00\x00\x18ftypisomcontent")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.MP4


def test_detects_zip_container_from_magic_bytes_with_dat_extension(tmp_path):
    path = tmp_path / "archive.dat"
    path.write_bytes(b"PK\x03\x04content")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.ZIP_CONTAINER


def test_detects_utf8_text_with_dat_extension(tmp_path):
    path = tmp_path / "prompt.dat"
    path.write_text("Generate a helmet product concept.", encoding="utf-8")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.UTF8_TEXT


def test_detects_unknown_for_invalid_binary_content(tmp_path):
    path = tmp_path / "asset.dat"
    path.write_bytes(b"\x00\xff\xfe\xfd")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.UNKNOWN


def test_ignores_extension_when_content_is_unknown(tmp_path):
    path = tmp_path / "image.png"
    path.write_bytes(b"\x00not-a-real-png")

    result = CreativeAssetTypeDetector.detect(path)

    assert result == CreativeAssetType.UNKNOWN
