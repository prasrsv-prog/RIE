import json
from pathlib import Path
from typing import Any

from rie.extraction.text_asset_extraction import TextAssetExtraction
from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport


def load_json(path: Path) -> TextAssetExtractionReport:
    return from_dict(json.loads(path.read_text(encoding="utf-8")))


def from_dict(data: dict[str, Any]) -> TextAssetExtractionReport:
    if not isinstance(data, dict):
        raise ValueError("Extraction report data must be an object.")

    root = _required(data, "root")
    total_text_assets = _required(data, "total_text_assets")
    extractions = _required(data, "extractions")

    if not isinstance(root, str):
        raise ValueError("Extraction report root must be a string.")

    if not isinstance(total_text_assets, int):
        raise ValueError(
            "Extraction report total_text_assets must be an integer."
        )

    if not isinstance(extractions, list):
        raise ValueError("Extraction report extractions must be a list.")

    return TextAssetExtractionReport(
        root=root,
        total_text_assets=total_text_assets,
        extractions=[
            _extraction_from_dict(extraction)
            for extraction in extractions
        ],
    )


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


def _extraction_from_dict(data: Any) -> TextAssetExtraction:
    if not isinstance(data, dict):
        raise ValueError("Text extraction data must be an object.")

    path = _required(data, "path")
    size = _required(data, "size")
    content = _required(data, "content")
    error = data.get("error")

    if not isinstance(path, str):
        raise ValueError("Text extraction path must be a string.")

    if not isinstance(size, int):
        raise ValueError("Text extraction size must be an integer.")

    if not isinstance(content, str):
        raise ValueError("Text extraction content must be a string.")

    if error is not None and not isinstance(error, str):
        raise ValueError("Text extraction error must be a string or null.")

    return TextAssetExtraction(
        path=Path(path),
        size=size,
        content=content,
        error=error,
    )


def _required(data: dict[str, Any], key: str) -> Any:
    try:
        return data[key]
    except KeyError as exc:
        raise ValueError(
            f"Missing extraction report field: {key}"
        ) from exc
