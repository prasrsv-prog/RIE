from dataclasses import FrozenInstanceError
from hashlib import sha256
from io import BytesIO

import pytest
from PIL import Image

from rie.application.governed_reference_derivative_transformer import (
    DERIVATIVE_ACCEPTED_SOURCE_FORMATS,
    DERIVATIVE_CROP_AUTHORIZED,
    DERIVATIVE_FIT_MODE,
    DERIVATIVE_MAX_HEIGHT,
    DERIVATIVE_MAX_WIDTH,
    DERIVATIVE_OUTPUT_MIME,
    DERIVATIVE_RESAMPLING,
    DERIVATIVE_TRANSFORM_ID,
    DERIVATIVE_TRANSFORM_VERSION,
    DERIVATIVE_UPSCALE_AUTHORIZED,
    GovernedReferenceDerivative,
    derive_governed_reference_png,
)


def _image_bytes(
    size: tuple[int, int],
    *,
    mode: str = "RGB",
    image_format: str = "PNG",
) -> bytes:
    color = (25, 50, 75, 200) if mode == "RGBA" else (25, 50, 75)
    image = Image.new(mode, size, color)
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


def _png_bytes(size: tuple[int, int], *, mode: str = "RGB") -> bytes:
    return _image_bytes(size, mode=mode, image_format="PNG")


def _derive(payload: bytes) -> GovernedReferenceDerivative:
    return derive_governed_reference_png(
        source_asset_id="synthetic-asset-1",
        source_path="synthetic/product.png",
        source_sha256=sha256(payload).hexdigest(),
        source_bytes=len(payload),
        payload=payload,
    )


def _decode_output(result: GovernedReferenceDerivative) -> Image.Image:
    image = Image.open(BytesIO(result.payload))
    image.load()
    return image


def test_large_landscape_is_contained_strictly_below_provider_limit() -> None:
    payload = _png_bytes((1024, 512))
    result = _derive(payload)

    assert result.output_width == 511
    assert result.output_height == 256
    assert result.output_width < 512
    assert result.output_height < 512


def test_large_portrait_is_contained_strictly_below_provider_limit() -> None:
    payload = _png_bytes((512, 1024))
    result = _derive(payload)

    assert result.output_width == 256
    assert result.output_height == 511


def test_small_source_is_not_upscaled() -> None:
    payload = _png_bytes((127, 63))
    result = _derive(payload)

    assert (result.output_width, result.output_height) == (127, 63)
    assert DERIVATIVE_UPSCALE_AUTHORIZED is False


def test_contract_records_exact_source_and_transform_provenance() -> None:
    payload = _png_bytes((800, 600))
    source_sha = sha256(payload).hexdigest()

    result = derive_governed_reference_png(
        source_asset_id="asset-42",
        source_path="FFS21/synthetic.png",
        source_sha256=source_sha,
        source_bytes=len(payload),
        payload=payload,
    )

    assert result.source_asset_id == "asset-42"
    assert result.source_path == "FFS21/synthetic.png"
    assert result.source_sha256 == source_sha
    assert result.source_bytes == len(payload)
    assert (result.source_width, result.source_height) == (800, 600)
    assert result.transform_id == DERIVATIVE_TRANSFORM_ID
    assert result.transform_version == DERIVATIVE_TRANSFORM_VERSION
    assert result.max_width == DERIVATIVE_MAX_WIDTH == 511
    assert result.max_height == DERIVATIVE_MAX_HEIGHT == 511
    assert result.fit_mode == DERIVATIVE_FIT_MODE == "CONTAIN"
    assert result.resampling == DERIVATIVE_RESAMPLING == "LANCZOS"
    assert result.crop_authorized is DERIVATIVE_CROP_AUTHORIZED is False
    assert result.upscale_authorized is DERIVATIVE_UPSCALE_AUTHORIZED is False


def test_output_identity_and_png_mime_are_self_consistent() -> None:
    result = _derive(_png_bytes((900, 700)))

    assert result.output_mime == DERIVATIVE_OUTPUT_MIME == "image/png"
    assert result.output_bytes == len(result.payload)
    assert result.output_sha256 == sha256(result.payload).hexdigest()

    decoded = _decode_output(result)
    assert decoded.format == "PNG"
    assert decoded.size == (result.output_width, result.output_height)


def test_alpha_source_preserves_alpha_capability() -> None:
    result = _derive(_png_bytes((900, 500), mode="RGBA"))

    decoded = _decode_output(result)
    assert decoded.mode == "RGBA"


def test_derivation_is_deterministic_for_identical_input() -> None:
    payload = _png_bytes((1200, 900))

    first = _derive(payload)
    second = _derive(payload)

    assert first == second
    assert first.payload == second.payload


def test_source_payload_is_not_mutated() -> None:
    payload = _png_bytes((1200, 900))
    before = bytes(payload)

    _derive(payload)

    assert payload == before


def test_source_byte_length_mismatch_is_rejected() -> None:
    payload = _png_bytes((32, 32))

    with pytest.raises(ValueError, match="source_bytes"):
        derive_governed_reference_png(
            source_asset_id="a",
            source_path="a.png",
            source_sha256=sha256(payload).hexdigest(),
            source_bytes=len(payload) + 1,
            payload=payload,
        )


def test_source_sha_mismatch_is_rejected() -> None:
    payload = _png_bytes((32, 32))

    with pytest.raises(ValueError, match="source_sha256"):
        derive_governed_reference_png(
            source_asset_id="a",
            source_path="a.png",
            source_sha256="0" * 64,
            source_bytes=len(payload),
            payload=payload,
        )


@pytest.mark.parametrize(
    "payload",
    (
        b"",
        b"not-an-image",
    ),
)
def test_invalid_image_payload_is_rejected(payload: bytes) -> None:
    if not payload:
        with pytest.raises(ValueError, match="payload"):
            derive_governed_reference_png(
                source_asset_id="a",
                source_path="a.png",
                source_sha256=sha256(payload).hexdigest(),
                source_bytes=1,
                payload=payload,
            )
        return

    with pytest.raises(ValueError, match="decodable supported image"):
        derive_governed_reference_png(
            source_asset_id="a",
            source_path="a.png",
            source_sha256=sha256(payload).hexdigest(),
            source_bytes=len(payload),
            payload=payload,
        )


def test_only_png_source_format_is_authorized() -> None:
    payload = _image_bytes((64, 64), image_format="JPEG")

    with pytest.raises(ValueError, match="format is not authorized"):
        _derive(payload)

    assert DERIVATIVE_ACCEPTED_SOURCE_FORMATS == ("PNG",)


def test_result_is_frozen() -> None:
    result = _derive(_png_bytes((64, 64)))

    with pytest.raises(FrozenInstanceError):
        result.output_width = 1
