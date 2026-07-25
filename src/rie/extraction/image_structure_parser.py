from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Final


PARSER_ID: Final[str] = "rie.image-structure.stdlib"
PARSER_VERSION: Final[str] = "1"
MAX_INPUT_BYTES: Final[int] = 1_048_576

_STATUS_ACCEPTED: Final[str] = "ACCEPTED"
_STATUS_REJECTED: Final[str] = "REJECTED"

_PNG_SIGNATURE: Final[bytes] = b"\x89PNG\r\n\x1a\n"
_JPEG_SOF_MARKERS: Final[frozenset[int]] = frozenset(
    {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
)
_JPEG_STANDALONE_MARKERS: Final[frozenset[int]] = frozenset(
    {0x01, 0xD8, 0xD9, *range(0xD0, 0xD8)}
)


@dataclass(frozen=True, slots=True)
class ImageStructureResult:
    status: str
    image_format: str | None
    width: int | None
    height: int | None
    parser_id: str
    parser_version: str
    input_sha256: str
    input_byte_length: int
    rejection_reason: str | None


def inspect_image_structure_bytes(data: bytes) -> ImageStructureResult:
    """Inspect bounded image structure without file I/O or pixel decoding."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")

    fingerprint = sha256(data).hexdigest()
    byte_length = len(data)

    if byte_length > MAX_INPUT_BYTES:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            reason="OVERSIZED_INPUT",
        )

    if data.startswith(_PNG_SIGNATURE):
        return _inspect_png(data, fingerprint, byte_length)

    if data.startswith(b"\xff\xd8"):
        return _inspect_jpeg(data, fingerprint, byte_length)

    if data.startswith(b"RIFF") or data[8:12] == b"WEBP":
        return _inspect_webp(data, fingerprint, byte_length)

    return _rejected(
        fingerprint=fingerprint,
        byte_length=byte_length,
        reason="UNSUPPORTED_SIGNATURE",
    )


def _accepted(
    *,
    fingerprint: str,
    byte_length: int,
    image_format: str,
    width: int,
    height: int,
) -> ImageStructureResult:
    return ImageStructureResult(
        status=_STATUS_ACCEPTED,
        image_format=image_format,
        width=width,
        height=height,
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        input_sha256=fingerprint,
        input_byte_length=byte_length,
        rejection_reason=None,
    )


def _rejected(
    *,
    fingerprint: str,
    byte_length: int,
    reason: str,
    image_format: str | None = None,
) -> ImageStructureResult:
    return ImageStructureResult(
        status=_STATUS_REJECTED,
        image_format=image_format,
        width=None,
        height=None,
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        input_sha256=fingerprint,
        input_byte_length=byte_length,
        rejection_reason=reason,
    )


def _inspect_png(
    data: bytes,
    fingerprint: str,
    byte_length: int,
) -> ImageStructureResult:
    if len(data) < 24:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="PNG",
            reason="TRUNCATED_PNG",
        )

    ihdr_length = int.from_bytes(data[8:12], "big")
    chunk_type = data[12:16]

    if ihdr_length != 13 or chunk_type != b"IHDR":
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="PNG",
            reason="MALFORMED_PNG",
        )

    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")

    if width == 0 or height == 0:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="PNG",
            reason="ZERO_DIMENSION",
        )

    return _accepted(
        fingerprint=fingerprint,
        byte_length=byte_length,
        image_format="PNG",
        width=width,
        height=height,
    )


def _inspect_jpeg(
    data: bytes,
    fingerprint: str,
    byte_length: int,
) -> ImageStructureResult:
    offset = 2

    while offset < len(data):
        if data[offset] != 0xFF:
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="MALFORMED_JPEG",
            )

        while offset < len(data) and data[offset] == 0xFF:
            offset += 1

        if offset >= len(data):
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="TRUNCATED_JPEG",
            )

        marker = data[offset]
        offset += 1

        if marker == 0x00:
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="MALFORMED_JPEG",
            )

        if marker in _JPEG_STANDALONE_MARKERS:
            if marker == 0xD9:
                break
            continue

        if offset + 2 > len(data):
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="TRUNCATED_JPEG",
            )

        segment_length = int.from_bytes(data[offset : offset + 2], "big")

        if segment_length < 2:
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="MALFORMED_JPEG",
            )

        segment_end = offset + segment_length

        if segment_end > len(data):
            return _rejected(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                reason="TRUNCATED_JPEG",
            )

        if marker in _JPEG_SOF_MARKERS:
            if segment_length < 7:
                return _rejected(
                    fingerprint=fingerprint,
                    byte_length=byte_length,
                    image_format="JPEG",
                    reason="MALFORMED_JPEG",
                )

            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")

            if width == 0 or height == 0:
                return _rejected(
                    fingerprint=fingerprint,
                    byte_length=byte_length,
                    image_format="JPEG",
                    reason="ZERO_DIMENSION",
                )

            return _accepted(
                fingerprint=fingerprint,
                byte_length=byte_length,
                image_format="JPEG",
                width=width,
                height=height,
            )

        if marker == 0xDA:
            break

        offset = segment_end

    return _rejected(
        fingerprint=fingerprint,
        byte_length=byte_length,
        image_format="JPEG",
        reason="JPEG_SOF_NOT_FOUND",
    )


def _inspect_webp(
    data: bytes,
    fingerprint: str,
    byte_length: int,
) -> ImageStructureResult:
    if len(data) < 20:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="TRUNCATED_WEBP",
        )

    if data[0:4] != b"RIFF" or data[8:12] != b"WEBP":
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="MALFORMED_WEBP",
        )

    riff_size = int.from_bytes(data[4:8], "little")
    declared_total = riff_size + 8

    if declared_total > len(data) or declared_total < 20:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="TRUNCATED_WEBP",
        )

    chunk_type = data[12:16]
    chunk_size = int.from_bytes(data[16:20], "little")
    payload_end = 20 + chunk_size

    if payload_end > declared_total or payload_end > len(data):
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="TRUNCATED_WEBP",
        )

    payload = data[20:payload_end]

    if chunk_type == b"VP8 ":
        dimensions = _parse_vp8_dimensions(payload)
    elif chunk_type == b"VP8L":
        dimensions = _parse_vp8l_dimensions(payload)
    elif chunk_type == b"VP8X":
        dimensions = _parse_vp8x_dimensions(payload)
    else:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="UNSUPPORTED_WEBP_CHUNK",
        )

    if dimensions is None:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="MALFORMED_WEBP",
        )

    width, height = dimensions

    if width == 0 or height == 0:
        return _rejected(
            fingerprint=fingerprint,
            byte_length=byte_length,
            image_format="WEBP",
            reason="ZERO_DIMENSION",
        )

    return _accepted(
        fingerprint=fingerprint,
        byte_length=byte_length,
        image_format="WEBP",
        width=width,
        height=height,
    )


def _parse_vp8_dimensions(payload: bytes) -> tuple[int, int] | None:
    if len(payload) < 10 or payload[3:6] != b"\x9d\x01\x2a":
        return None

    width = int.from_bytes(payload[6:8], "little") & 0x3FFF
    height = int.from_bytes(payload[8:10], "little") & 0x3FFF
    return width, height


def _parse_vp8l_dimensions(payload: bytes) -> tuple[int, int] | None:
    if len(payload) < 5 or payload[0] != 0x2F:
        return None

    packed = int.from_bytes(payload[1:5], "little")
    width = (packed & 0x3FFF) + 1
    height = ((packed >> 14) & 0x3FFF) + 1
    return width, height


def _parse_vp8x_dimensions(payload: bytes) -> tuple[int, int] | None:
    if len(payload) < 10:
        return None

    width = int.from_bytes(payload[4:7], "little") + 1
    height = int.from_bytes(payload[7:10], "little") + 1
    return width, height
