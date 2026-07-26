from __future__ import annotations

import pytest

import rie.extraction as extraction
from rie.extraction import (
    MAX_INPUT_BYTES,
    PARSER_ID,
    PARSER_VERSION,
    ImageStructureResult,
    inspect_image_structure_bytes,
)
from rie.extraction.image_structure_parser import (
    MAX_INPUT_BYTES as DIRECT_MAX_INPUT_BYTES,
)
from rie.extraction.image_structure_parser import (
    PARSER_ID as DIRECT_PARSER_ID,
)
from rie.extraction.image_structure_parser import (
    PARSER_VERSION as DIRECT_PARSER_VERSION,
)
from rie.extraction.image_structure_parser import (
    ImageStructureResult as DirectImageStructureResult,
)
from rie.extraction.image_structure_parser import (
    inspect_image_structure_bytes as direct_inspect_image_structure_bytes,
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


def _assert_package_and_direct_equivalent(data: bytes) -> None:
    package_result = inspect_image_structure_bytes(data)
    direct_result = direct_inspect_image_structure_bytes(data)

    assert package_result == direct_result
    assert inspect_image_structure_bytes(data) == package_result
    assert direct_inspect_image_structure_bytes(data) == direct_result


def test_package_exports_exact_existing_parser_symbols() -> None:
    assert extraction.ImageStructureResult is DirectImageStructureResult
    assert extraction.inspect_image_structure_bytes is direct_inspect_image_structure_bytes
    assert ImageStructureResult is DirectImageStructureResult
    assert inspect_image_structure_bytes is direct_inspect_image_structure_bytes
    assert MAX_INPUT_BYTES == DIRECT_MAX_INPUT_BYTES
    assert PARSER_ID == DIRECT_PARSER_ID
    assert PARSER_VERSION == DIRECT_PARSER_VERSION


def test_package_export_accepts_png_equivalently() -> None:
    _assert_package_and_direct_equivalent(_png(640, 480))


def test_package_export_accepts_jpeg_equivalently() -> None:
    _assert_package_and_direct_equivalent(_jpeg(1024, 768))


def test_package_export_accepts_webp_equivalently() -> None:
    _assert_package_and_direct_equivalent(_webp_vp8x(1920, 1080))


def test_package_export_rejects_unsupported_bytes_equivalently() -> None:
    data = b"not-an-image"
    _assert_package_and_direct_equivalent(data)

    result = inspect_image_structure_bytes(data)
    assert result.status == "REJECTED"
    assert result.rejection_reason == "UNSUPPORTED_SIGNATURE"


def test_package_export_rejects_truncated_png_equivalently() -> None:
    data = b"\x89PNG\r\n\x1a\n"
    _assert_package_and_direct_equivalent(data)

    result = inspect_image_structure_bytes(data)
    assert result.status == "REJECTED"
    assert result.rejection_reason == "TRUNCATED_PNG"


def test_package_export_rejects_oversized_bytes_equivalently() -> None:
    data = b"x" * (MAX_INPUT_BYTES + 1)
    _assert_package_and_direct_equivalent(data)

    result = inspect_image_structure_bytes(data)
    assert result.status == "REJECTED"
    assert result.rejection_reason == "OVERSIZED_INPUT"


def test_package_export_preserves_non_bytes_type_error() -> None:
    with pytest.raises(TypeError, match="data must be bytes"):
        inspect_image_structure_bytes(bytearray(b"PNG"))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="data must be bytes"):
        direct_inspect_image_structure_bytes(  # type: ignore[arg-type]
            bytearray(b"PNG")
        )
