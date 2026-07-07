from pathlib import Path

from rie.ingestion.creative_asset_type import CreativeAssetType


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
PDF_SIGNATURE = b"%PDF-"
RIFF_SIGNATURE = b"RIFF"
WEBP_SIGNATURE = b"WEBP"
TIFF_LITTLE_ENDIAN_SIGNATURE = b"II*\x00"
TIFF_BIG_ENDIAN_SIGNATURE = b"MM\x00*"
MP4_BRAND_SIGNATURE = b"ftyp"
ZIP_CONTAINER_SIGNATURE = b"PK\x03\x04"


class CreativeAssetTypeDetector:

    @staticmethod
    def detect(path: Path) -> CreativeAssetType:
        content = path.read_bytes()

        if content.startswith(PNG_SIGNATURE):
            return CreativeAssetType.PNG

        if content.startswith(JPEG_SIGNATURE):
            return CreativeAssetType.JPEG

        if content.startswith(PDF_SIGNATURE):
            return CreativeAssetType.PDF

        if content.startswith(RIFF_SIGNATURE) and content[8:12] == WEBP_SIGNATURE:
            return CreativeAssetType.WEBP

        if content.startswith(TIFF_LITTLE_ENDIAN_SIGNATURE):
            return CreativeAssetType.TIFF

        if content.startswith(TIFF_BIG_ENDIAN_SIGNATURE):
            return CreativeAssetType.TIFF

        if content[4:8] == MP4_BRAND_SIGNATURE:
            return CreativeAssetType.MP4

        if content.startswith(ZIP_CONTAINER_SIGNATURE):
            return CreativeAssetType.ZIP_CONTAINER

        if b"\x00" in content:
            return CreativeAssetType.UNKNOWN

        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            return CreativeAssetType.UNKNOWN

        return CreativeAssetType.UTF8_TEXT
