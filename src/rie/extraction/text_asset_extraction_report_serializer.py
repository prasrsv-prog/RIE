import json
from pathlib import Path
from typing import Any

from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport


def to_dict(report: TextAssetExtractionReport) -> dict[str, Any]:
    return {
        "root": report.root,
        "total_text_assets": report.total_text_assets,
        "failed": report.failed,
        "extractions": [
            {
                "path": str(extraction.path),
                "size": extraction.size,
                "content": extraction.content,
                "error": extraction.error,
            }
            for extraction in report.extractions
        ],
    }


def write_json(
    report: TextAssetExtractionReport,
    output_path: Path,
) -> None:
    output_path.write_text(
        json.dumps(
            to_dict(report),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
