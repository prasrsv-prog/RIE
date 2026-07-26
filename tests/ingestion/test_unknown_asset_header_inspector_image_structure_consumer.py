from __future__ import annotations

import pytest

from rie.extraction import (
    MAX_INPUT_BYTES,
    ImageStructureResult,
    inspect_image_structure_bytes,
)
from rie.ingestion.unknown_asset_header_inspector import (
    inspect_controlled_image_structure_bytes,
)


def _png(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
    )


def _jpeg(width: int, height: int) -> bytes:
    sof_payload = (
        b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x01\x01\x11\x00"
    )
    sof_segment = (
        b"\xff\xc0"
        + (len(sof_payload) + 2).to_bytes(2, "big")
        + sof_payload
    )
    return b"\xff\xd8" + sof_segment + b"\xff\xd9"


def _webp_vp8x(width: int, height: int) -> bytes:
    payload = (
        b"\x00\x00\x00\x00"
        + (width - 1).to_bytes(3, "little")
        + (height - 1).to_bytes(3, "little")
    )
    chunk = b"VP8X" + len(payload).to_bytes(4, "little") + payload
    riff_size = len(b"WEBP") + len(chunk)
    return (
        b"RIFF"
        + riff_size.to_bytes(4, "little")
        + b"WEBP"
        + chunk
    )


def _assert_delegation_equivalent(data: bytes) -> ImageStructureResult:
    direct = inspect_image_structure_bytes(data)
    delegated = inspect_controlled_image_structure_bytes(data)

    assert delegated == direct
    assert type(delegated) is type(direct)
    return delegated


def test_controlled_image_structure_delegation_png_equivalence() -> None:
    _assert_delegation_equivalent(_png(640, 480))


def test_controlled_image_structure_delegation_jpeg_equivalence() -> None:
    _assert_delegation_equivalent(_jpeg(1024, 768))


def test_controlled_image_structure_delegation_webp_equivalence() -> None:
    _assert_delegation_equivalent(_webp_vp8x(1920, 1080))


def test_controlled_image_structure_delegation_unsupported_equivalence() -> None:
    result = _assert_delegation_equivalent(b"not-an-image")
    assert result.status == "REJECTED"


def test_controlled_image_structure_delegation_truncated_png_equivalence() -> None:
    result = _assert_delegation_equivalent(b"\x89PNG\r\n\x1a\n")
    assert result.status == "REJECTED"


def test_controlled_image_structure_delegation_oversized_equivalence() -> None:
    result = _assert_delegation_equivalent(
        b"x" * (MAX_INPUT_BYTES + 1)
    )
    assert result.status == "REJECTED"


def test_controlled_image_structure_delegation_repeated_determinism() -> None:
    data = _webp_vp8x(320, 240)
    first = inspect_controlled_image_structure_bytes(data)
    second = inspect_controlled_image_structure_bytes(data)

    assert first == second
    assert first == inspect_image_structure_bytes(data)


def test_controlled_image_structure_delegation_non_bytes_type_error() -> None:
    with pytest.raises(TypeError) as direct_error:
        inspect_image_structure_bytes("not-bytes")  # type: ignore[arg-type]

    with pytest.raises(TypeError) as delegated_error:
        inspect_controlled_image_structure_bytes(
            "not-bytes",  # type: ignore[arg-type]
        )

    assert type(delegated_error.value) is type(direct_error.value)
    assert str(delegated_error.value) == str(direct_error.value)
