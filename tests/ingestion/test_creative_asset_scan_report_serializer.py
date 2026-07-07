import json

from rie.ingestion.creative_asset_scan_item import CreativeAssetScanItem
from rie.ingestion.creative_asset_scan_report import CreativeAssetScanReport
from rie.ingestion.creative_asset_scan_report_serializer import to_dict
from rie.ingestion.creative_asset_scan_report_serializer import write_json
from rie.ingestion.creative_asset_type import CreativeAssetType


def test_to_dict_serializes_scan_report(tmp_path):
    png = tmp_path / "image.dat"
    text = tmp_path / "prompt.dat"

    report = CreativeAssetScanReport(
        root=tmp_path,
        items=[
            CreativeAssetScanItem(
                path=png,
                asset_type=CreativeAssetType.PNG,
                size=123,
            ),
            CreativeAssetScanItem(
                path=text,
                asset_type=CreativeAssetType.UTF8_TEXT,
                size=45,
                error="read warning",
            ),
        ],
    )

    result = to_dict(report)

    assert result["root"] == str(tmp_path)
    assert result["total_files"] == 2
    assert result["counts"] == {
        "PNG": 1,
        "JPEG": 0,
        "PDF": 0,
        "WEBP": 0,
        "TIFF": 0,
        "MP4": 0,
        "ZIP_CONTAINER": 0,
        "UTF8_TEXT": 1,
        "UNKNOWN": 0,
    }
    assert result["failed"] == 1
    assert result["items"] == [
        {
            "path": str(png),
            "asset_type": "PNG",
            "size": 123,
            "error": None,
        },
        {
            "path": str(text),
            "asset_type": "UTF8_TEXT",
            "size": 45,
            "error": "read warning",
        },
    ]


def test_write_json_writes_valid_json(tmp_path):
    report = CreativeAssetScanReport(
        root=tmp_path,
        items=[
            CreativeAssetScanItem(
                path=tmp_path / "document.dat",
                asset_type=CreativeAssetType.PDF,
                size=456,
            ),
        ],
    )
    output_path = tmp_path / "report.json"

    write_json(report, output_path)

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["root"] == str(tmp_path)
    assert data["total_files"] == 1
    assert data["counts"]["PDF"] == 1
    assert data["items"][0]["asset_type"] == "PDF"
