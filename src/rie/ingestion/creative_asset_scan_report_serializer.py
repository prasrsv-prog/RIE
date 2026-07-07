import json
from pathlib import Path
from typing import Any

from rie.ingestion.creative_asset_scan_report import CreativeAssetScanReport
from rie.ingestion.creative_asset_type import CreativeAssetType


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_dict(report: CreativeAssetScanReport) -> dict[str, Any]:
    failed = sum(
        item.error is not None
        for item in report.items
    )

    return {
        "root": str(report.root),
        "total_files": report.total_files,
        "counts": {
            asset_type.name: report.count_by_type(asset_type)
            for asset_type in CreativeAssetType
        },
        "failed": failed,
        "items": [
            {
                "path": str(item.path),
                "asset_type": item.asset_type.name,
                "size": item.size,
                "error": item.error,
            }
            for item in report.items
        ],
    }


def write_json(
    report: CreativeAssetScanReport,
    output_path: Path,
) -> None:
    output_path.write_text(
        json.dumps(to_dict(report), indent=2),
        encoding="utf-8",
    )
