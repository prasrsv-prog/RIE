from rie.ingestion.creative_asset_scan_report_inspector import inspect_report


def test_inspect_report_computes_inspection_insights():
    data = {
        "root": "D:\\DAT",
        "total_files": 5,
        "counts": {
            "PNG": 1,
            "JPEG": 1,
            "PDF": 1,
            "UTF8_TEXT": 1,
            "UNKNOWN": 1,
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
                "error": None,
            },
            {
                "path": "D:\\DAT\\prompt.dat",
                "asset_type": "UTF8_TEXT",
                "size": 50,
                "error": None,
            },
            {
                "path": "D:\\DAT\\unknown.dat",
                "asset_type": "UNKNOWN",
                "size": 20,
                "error": "cannot read",
            },
        ],
    }

    inspection = inspect_report(
        data,
        top_limit=2,
    )

    assert inspection.root == "D:\\DAT"
    assert inspection.total_files == 5
    assert inspection.counts == data["counts"]
    assert inspection.total_size_by_type == {
        "PNG": 100,
        "JPEG": 500,
        "PDF": 300,
        "UTF8_TEXT": 50,
        "UNKNOWN": 20,
    }
    assert [
        item["path"]
        for item in inspection.top_largest_files
    ] == [
        "D:\\DAT\\photo.dat",
        "D:\\DAT\\document.dat",
    ]
    assert inspection.utf8_text_files == [data["items"][3]]
    assert inspection.pdf_files == [data["items"][2]]
    assert inspection.unknown_files == [data["items"][4]]
    assert inspection.failed_files == [data["items"][4]]
