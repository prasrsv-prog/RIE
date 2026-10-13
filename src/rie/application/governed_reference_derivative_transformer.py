"""Deterministic transient provider-reference image normalization.

This module derives an execution-only PNG from one exact governed source image.
It does not persist, promote, or replace governed asset authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import re

from PIL import Image, UnidentifiedImageError


DERIVATIVE_TRANSFORM_ID = "rie.governed-reference.pillow-contain-png"
DERIVATIVE_TRANSFORM_VERSION = "1"
DERIVATIVE_MAX_WIDTH = 511
DERIVATIVE_MAX_HEIGHT = 511
DERIVATIVE_FIT_MODE = "CONTAIN"
DERIVATIVE_RESAMPLING = "LANCZOS"
DERIVATIVE_OUTPUT_MIME = "image/png"
DERIVATIVE_OUTPUT_FORMAT = "PNG"
DERIVATIVE_ACCEPTED_SOURCE_FORMATS = ("PNG",)
DERIVATIVE_MAX_SOURCE_BYTES = 32_000_000
DERIVATIVE_MAX_SOURCE_PIXELS = 40_000_000
DERIVATIVE_CROP_AUTHORIZED = False
DERIVATIVE_UPSCALE_AUTHORIZED = False

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _required_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be non-empty text")
    return value


def _required_sha256(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a lowercase SHA256 hex digest")
    return value


def _target_size(width: int, height: int) -> tuple[int, int]:
    if width <= 0 or height <= 0:
        raise ValueError("source image dimensions must be positive")
    if width <= DERIVATIVE_MAX_WIDTH and height <= DERIVATIVE_MAX_HEIGHT:
        return width, height

    scale = min(
        DERIVATIVE_MAX_WIDTH / width,
        DERIVATIVE_MAX_HEIGHT / height,
    )
    target_width = max(1, round(width * scale))
    target_height = max(1, round(height * scale))

    # Round can theoretically cross the strict bound by one due to binary
    # floating point. Clamp without cropping or changing the chosen fit mode.
    target_width = min(target_width, DERIVATIVE_MAX_WIDTH)
    target_height = min(target_height, DERIVATIVE_MAX_HEIGHT)
    return target_width, target_height


def _normalized_mode(image: Image.Image) -> str:
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        return "RGBA"
    return "RGB"


@dataclass(frozen=True)
class GovernedReferenceDerivative:
    source_asset_id: str
    source_path: str
    source_sha256: str
    source_bytes: int
    source_width: int
    source_height: int
    transform_id: str
    transform_version: str
    max_width: int
    max_height: int
    fit_mode: str
    resampling: str
    crop_authorized: bool
    upscale_authorized: bool
    output_mime: str
    output_width: int
    output_height: int
    output_bytes: int
    output_sha256: str
    payload: bytes

    def __post_init__(self) -> None:
        _required_text(self.source_asset_id, field_name="source_asset_id")
        _required_text(self.source_path, field_name="source_path")
        _required_sha256(self.source_sha256, field_name="source_sha256")
        _required_sha256(self.output_sha256, field_name="output_sha256")

        if not isinstance(self.payload, bytes) or not self.payload:
            raise ValueError("payload must be non-empty bytes")
        if self.source_bytes <= 0 or self.output_bytes <= 0:
            raise ValueError("byte lengths must be positive")
        if self.source_width <= 0 or self.source_height <= 0:
            raise ValueError("source dimensions must be positive")
        if self.output_width <= 0 or self.output_height <= 0:
            raise ValueError("output dimensions must be positive")
        if self.output_width >= 512 or self.output_height >= 512:
            raise ValueError("output dimensions must remain strictly below 512")
        if self.output_width > self.source_width or self.output_height > self.source_height:
            raise ValueError("upscaling is prohibited")
        if self.output_bytes != len(self.payload):
            raise ValueError("output_bytes must match payload length")
        if self.output_sha256 != sha256(self.payload).hexdigest():
            raise ValueError("output_sha256 must match payload")


def derive_governed_reference_png(
    *,
    source_asset_id: str,
    source_path: str,
    source_sha256: str,
    source_bytes: int,
    payload: bytes,
) -> GovernedReferenceDerivative:
    """Derive one deterministic execution-only PNG from exact governed bytes."""

    source_asset_id = _required_text(
        source_asset_id,
        field_name="source_asset_id",
    )
    source_path = _required_text(source_path, field_name="source_path")
    source_sha256 = _required_sha256(
        source_sha256,
        field_name="source_sha256",
    )

    if not isinstance(source_bytes, int) or isinstance(source_bytes, bool):
        raise ValueError("source_bytes must be an integer")
    if source_bytes <= 0:
        raise ValueError("source_bytes must be positive")
    if not isinstance(payload, bytes) or not payload:
        raise ValueError("payload must be non-empty bytes")
    if len(payload) != source_bytes:
        raise ValueError("source_bytes must match payload length")
    if source_bytes > DERIVATIVE_MAX_SOURCE_BYTES:
        raise ValueError("source image exceeds maximum authorized byte length")

    actual_source_sha256 = sha256(payload).hexdigest()
    if actual_source_sha256 != source_sha256:
        raise ValueError("source_sha256 must match payload")

    try:
        with Image.open(BytesIO(payload)) as opened:
            if opened.format not in DERIVATIVE_ACCEPTED_SOURCE_FORMATS:
                raise ValueError("source image format is not authorized")

            source_width, source_height = opened.size
            if source_width * source_height > DERIVATIVE_MAX_SOURCE_PIXELS:
                raise ValueError("source image exceeds maximum authorized pixel count")

            opened.load()
            target_width, target_height = _target_size(
                source_width,
                source_height,
            )

            normalized = opened.convert(_normalized_mode(opened))
            if (target_width, target_height) != normalized.size:
                normalized = normalized.resize(
                    (target_width, target_height),
                    resample=Image.Resampling.LANCZOS,
                )

            output = BytesIO()
            normalized.save(
                output,
                format=DERIVATIVE_OUTPUT_FORMAT,
                optimize=False,
                compress_level=9,
            )
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("payload must be a decodable supported image") from exc

    output_payload = output.getvalue()
    output_sha256 = sha256(output_payload).hexdigest()

    return GovernedReferenceDerivative(
        source_asset_id=source_asset_id,
        source_path=source_path,
        source_sha256=source_sha256,
        source_bytes=source_bytes,
        source_width=source_width,
        source_height=source_height,
        transform_id=DERIVATIVE_TRANSFORM_ID,
        transform_version=DERIVATIVE_TRANSFORM_VERSION,
        max_width=DERIVATIVE_MAX_WIDTH,
        max_height=DERIVATIVE_MAX_HEIGHT,
        fit_mode=DERIVATIVE_FIT_MODE,
        resampling=DERIVATIVE_RESAMPLING,
        crop_authorized=DERIVATIVE_CROP_AUTHORIZED,
        upscale_authorized=DERIVATIVE_UPSCALE_AUTHORIZED,
        output_mime=DERIVATIVE_OUTPUT_MIME,
        output_width=target_width,
        output_height=target_height,
        output_bytes=len(output_payload),
        output_sha256=output_sha256,
        payload=output_payload,
    )


__all__ = [
    "DERIVATIVE_ACCEPTED_SOURCE_FORMATS",
    "DERIVATIVE_CROP_AUTHORIZED",
    "DERIVATIVE_FIT_MODE",
    "DERIVATIVE_MAX_HEIGHT",
    "DERIVATIVE_MAX_SOURCE_BYTES",
    "DERIVATIVE_MAX_SOURCE_PIXELS",
    "DERIVATIVE_MAX_WIDTH",
    "DERIVATIVE_OUTPUT_FORMAT",
    "DERIVATIVE_OUTPUT_MIME",
    "DERIVATIVE_RESAMPLING",
    "DERIVATIVE_TRANSFORM_ID",
    "DERIVATIVE_TRANSFORM_VERSION",
    "DERIVATIVE_UPSCALE_AUTHORIZED",
    "GovernedReferenceDerivative",
    "derive_governed_reference_png",
]
