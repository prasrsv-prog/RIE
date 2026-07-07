import json

from rie.extraction.text_asset_extraction import TextAssetExtraction
from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport
from rie.extraction.text_asset_extraction_report_serializer import to_dict
from rie.extraction.text_asset_extraction_report_serializer import write_json


def test_to_dict_serializes_text_asset_extraction_report(tmp_path):
    report = TextAssetExtractionReport(
        root=str(tmp_path),
        total_text_assets=2,
        extractions=[
            TextAssetExtraction(
                path=tmp_path / "prompt.dat",
                size=25,
                content="Prompt content",
            ),
            TextAssetExtraction(
                path=tmp_path / "missing.dat",
                size=12,
                content="",
                error="missing file",
            ),
        ],
    )

    result = to_dict(report)

    assert result == {
        "root": str(tmp_path),
        "total_text_assets": 2,
        "failed": 1,
        "extractions": [
            {
                "path": str(tmp_path / "prompt.dat"),
                "size": 25,
                "content": "Prompt content",
                "error": None,
            },
            {
                "path": str(tmp_path / "missing.dat"),
                "size": 12,
                "content": "",
                "error": "missing file",
            },
        ],
    }


def test_write_json_writes_utf8_json_and_preserves_non_ascii_content(tmp_path):
    report = TextAssetExtractionReport(
        root=str(tmp_path),
        total_text_assets=1,
        extractions=[
            TextAssetExtraction(
                path=tmp_path / "prompt.dat",
                size=19,
                content="Helm Café Racer",
            ),
        ],
    )
    output_path = tmp_path / "text-extractions.json"

    write_json(report, output_path)

    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert "Café" in raw_json
    assert data["root"] == str(tmp_path)
    assert data["total_text_assets"] == 1
    assert data["failed"] == 0
    assert data["extractions"][0]["content"] == "Helm Café Racer"
