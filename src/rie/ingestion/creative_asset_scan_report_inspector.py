from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CreativeAssetReportInspection:
    root: str
    total_files: int
    counts: dict[str, int]
    total_size_by_type: dict[str, int]
    top_largest_files: list[dict[str, Any]]
    utf8_text_files: list[dict[str, Any]]
    pdf_files: list[dict[str, Any]]
    unknown_files: list[dict[str, Any]]
    failed_files: list[dict[str, Any]]


def inspect_report(
    data: dict[str, Any],
    top_limit: int = 10,
) -> CreativeAssetReportInspection:
    items = data["items"]
    counts = data["counts"]

    return CreativeAssetReportInspection(
        root=data["root"],
        total_files=data["total_files"],
        counts=counts,
        total_size_by_type=_total_size_by_type(items, counts),
        top_largest_files=sorted(
            items,
            key=lambda item: item["size"],
            reverse=True,
        )[:top_limit],
        utf8_text_files=_filter_by_type(items, "UTF8_TEXT"),
        pdf_files=_filter_by_type(items, "PDF"),
        unknown_files=_filter_by_type(items, "UNKNOWN"),
        failed_files=[
            item for item in items
            if item["error"] is not None
        ],
    )


def _total_size_by_type(
    items: list[dict[str, Any]],
    counts: dict[str, int],
) -> dict[str, int]:
    totals = {
        asset_type: 0
        for asset_type in counts
    }

    for item in items:
        totals[item["asset_type"]] = totals.get(
            item["asset_type"],
            0,
        ) + item["size"]

    return totals


def _filter_by_type(
    items: list[dict[str, Any]],
    asset_type: str,
) -> list[dict[str, Any]]:
    return [
        item for item in items
        if item["asset_type"] == asset_type
    ]
