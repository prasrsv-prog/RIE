from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UnknownAssetHeaderInspection:
    path: str
    size: int
    header_hex: str
    header_ascii: str
    candidate: str
    error: str | None = None


def inspect_unknown_assets(
    data: dict[str, Any],
    header_bytes: int = 32,
    limit: int | None = None,
) -> list[UnknownAssetHeaderInspection]:
    unknown_items = [
        item for item in data["items"]
        if item["asset_type"] == "UNKNOWN"
    ]

    if limit is not None:
        unknown_items = unknown_items[:limit]

    return [
        _inspect_unknown_item(
            item,
            header_bytes,
        )
        for item in unknown_items
    ]


def guess_candidate(header: bytes) -> str:
    if header.startswith(b"RIFF") and b"WEBP" in header[8:16]:
        return "WEBP"

    if header.startswith(b"RIFF"):
        return "RIFF_CONTAINER"

    if header.startswith(b"PK\x03\x04"):
        return "ZIP_CONTAINER"

    if header.startswith(b"\x1f\x8b"):
        return "GZIP"

    if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
        return "GIF"

    stripped = header.lstrip()

    if stripped.startswith(b"{") or stripped.startswith(b"["):
        return "JSON_TEXT"

    return "UNKNOWN"


def _inspect_unknown_item(
    item: dict[str, Any],
    header_bytes: int,
) -> UnknownAssetHeaderInspection:
    path = item["path"]

    try:
        with open(Path(path), "rb") as file:
            header = file.read(header_bytes)
    except OSError as exc:
        return UnknownAssetHeaderInspection(
            path=path,
            size=item["size"],
            header_hex="",
            header_ascii="",
            candidate="UNKNOWN",
            error=str(exc),
        )

    return UnknownAssetHeaderInspection(
        path=path,
        size=item["size"],
        header_hex=header.hex(" "),
        header_ascii=_safe_ascii(header),
        candidate=guess_candidate(header),
    )


def _safe_ascii(header: bytes) -> str:
    return "".join(
        chr(byte) if 32 <= byte <= 126 else "."
        for byte in header
    )
