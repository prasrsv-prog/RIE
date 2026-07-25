from __future__ import annotations

from dataclasses import FrozenInstanceError
from hashlib import sha256

import pytest

from rie.extraction.image_structure_parser import (
    MAX_INPUT_BYTES,
    PARSER_ID,
    PARSER_VERSION,
    ImageStructureResult,
    inspect_image_structure_bytes,
)


def _png(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
    )


def _jpeg(width: int, height: int, marker: int = 0xC0) -> bytes:
    sof_payload = (
        b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x01\x01\x11\x00"
    )
    sof_segment = (
        b"\xff"
        + bytes([marker])
        + (len(sof_payload) + 2).to_bytes(2, "big")
        + sof_payload
    )
    return b"\xff\xd8" + sof_segment + b"\xff\xd9"


def _webp(chunk_type: bytes, payload: bytes) -> bytes:
    chunk = chunk_type + len(payload).to_bytes(4, "little") + payload
    riff_size = len(b"WEBP") + len(chunk)
    return b"RIFF" + riff_size.to_bytes(4, "little") + b"WEBP" + chunk


def _vp8(width: int, height: int) -> bytes:
    payload = (
        b"\x10\x00\x00"
        + b"\x9d\x01\x2a"
        + width.to_bytes(2, "little")
        + height.to_bytes(2, "little")
    )
    return _webp(b"VP8 ", payload)


def _vp8l(width: int, height: int) -> bytes:
    packed = (width - 1) | ((height - 1) << 14)
    payload = b"\x2f" + packed.to_bytes(4, "little")
    return _webp(b"VP8L", payload)


def _vp8x(width: int, height: int) -> bytes:
    payload = (
        b"\x00\x00\x00\x00"
        + (width - 1).to_bytes(3, "little")
        + (height - 1).to_bytes(3, "little")
    )
    return _webp(b"VP8X", payload)


def test_result_contract_is_frozen() -> None:
    result = inspect_image_structure_bytes(_png(7, 9))

    assert isinstance(result, ImageStructureResult)
    assert result.parser_id == PARSER_ID
    assert result.parser_version == PARSER_VERSION

    with pytest.raises(FrozenInstanceError):
        result.width = 8  # type: ignore[misc]


def test_accepts_valid_png_ihdr_dimensions() -> None:
    data = _png(640, 480)
    result = inspect_image_structure_bytes(data)

    assert result.status == "ACCEPTED"
    assert result.image_format == "PNG"
    assert (result.width, result.height) == (640, 480)
    assert result.input_sha256 == sha256(data).hexdigest()
    assert result.input_byte_length == len(data)
    assert result.rejection_reason is None


def test_rejects_truncated_png() -> None:
    result = inspect_image_structure_bytes(b"\x89PNG\r\n\x1a\n")

    assert result.status == "REJECTED"
    assert result.image_format == "PNG"
    assert result.rejection_reason == "TRUNCATED_PNG"


def test_rejects_malformed_png_ihdr() -> None:
    data = b"\x89PNG\r\n\x1a\n" + (12).to_bytes(4, "big") + b"JHDR" + b"\x00" * 8
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.rejection_reason == "MALFORMED_PNG"


def test_rejects_zero_png_dimension() -> None:
    result = inspect_image_structure_bytes(_png(0, 480))

    assert result.status == "REJECTED"
    assert result.rejection_reason == "ZERO_DIMENSION"


def test_accepts_baseline_jpeg_sof_dimensions() -> None:
    result = inspect_image_structure_bytes(_jpeg(1024, 768, 0xC0))

    assert result.status == "ACCEPTED"
    assert result.image_format == "JPEG"
    assert (result.width, result.height) == (1024, 768)


def test_accepts_progressive_jpeg_sof_dimensions() -> None:
    result = inspect_image_structure_bytes(_jpeg(320, 240, 0xC2))

    assert result.status == "ACCEPTED"
    assert result.image_format == "JPEG"
    assert (result.width, result.height) == (320, 240)


def test_rejects_truncated_jpeg_segment() -> None:
    data = b"\xff\xd8\xff\xe0\x00\x10\x00"
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.image_format == "JPEG"
    assert result.rejection_reason == "TRUNCATED_JPEG"


def test_rejects_jpeg_without_accepted_sof() -> None:
    data = b"\xff\xd8\xff\xda\x00\x02\xff\xd9"
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.image_format == "JPEG"
    assert result.rejection_reason == "JPEG_SOF_NOT_FOUND"


def test_rejects_zero_jpeg_dimension() -> None:
    result = inspect_image_structure_bytes(_jpeg(0, 240, 0xC0))

    assert result.status == "REJECTED"
    assert result.rejection_reason == "ZERO_DIMENSION"


def test_accepts_webp_vp8_dimensions() -> None:
    result = inspect_image_structure_bytes(_vp8(800, 600))

    assert result.status == "ACCEPTED"
    assert result.image_format == "WEBP"
    assert (result.width, result.height) == (800, 600)


def test_accepts_webp_vp8l_dimensions() -> None:
    result = inspect_image_structure_bytes(_vp8l(511, 257))

    assert result.status == "ACCEPTED"
    assert result.image_format == "WEBP"
    assert (result.width, result.height) == (511, 257)


def test_accepts_webp_vp8x_dimensions() -> None:
    result = inspect_image_structure_bytes(_vp8x(1920, 1080))

    assert result.status == "ACCEPTED"
    assert result.image_format == "WEBP"
    assert (result.width, result.height) == (1920, 1080)


def test_rejects_malformed_webp_signature() -> None:
    data = b"RIFF" + (12).to_bytes(4, "little") + b"NOPE" + b"VP8 " + b"\x00" * 4
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.image_format == "WEBP"
    assert result.rejection_reason == "MALFORMED_WEBP"


def test_rejects_truncated_webp_payload() -> None:
    data = b"RIFF" + (22).to_bytes(4, "little") + b"WEBP" + b"VP8 " + (10).to_bytes(4, "little") + b"\x00"
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.rejection_reason == "TRUNCATED_WEBP"


def test_rejects_unsupported_webp_chunk() -> None:
    result = inspect_image_structure_bytes(_webp(b"ANIM", b"\x00" * 6))

    assert result.status == "REJECTED"
    assert result.rejection_reason == "UNSUPPORTED_WEBP_CHUNK"


def test_rejects_unsupported_signature() -> None:
    data = b"not-an-image"
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.image_format is None
    assert result.rejection_reason == "UNSUPPORTED_SIGNATURE"
    assert result.input_sha256 == sha256(data).hexdigest()


def test_rejects_oversized_input_before_format_inspection() -> None:
    data = b"\x89PNG\r\n\x1a\n" + b"\x00" * MAX_INPUT_BYTES
    result = inspect_image_structure_bytes(data)

    assert result.status == "REJECTED"
    assert result.image_format is None
    assert result.rejection_reason == "OVERSIZED_INPUT"


def test_repeated_accepted_result_is_deterministic() -> None:
    data = _vp8x(300, 200)

    assert inspect_image_structure_bytes(data) == inspect_image_structure_bytes(data)


def test_repeated_rejected_result_is_deterministic() -> None:
    data = b"unsupported"

    assert inspect_image_structure_bytes(data) == inspect_image_structure_bytes(data)


def test_rejects_non_bytes_input() -> None:
    with pytest.raises(TypeError, match="data must be bytes"):
        inspect_image_structure_bytes(bytearray(b"PNG"))  # type: ignore[arg-type]
