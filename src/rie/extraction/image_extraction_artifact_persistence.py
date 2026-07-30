"""Canonical persistence bytes for Gate 13 image extraction artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Final

from rie.extraction.image_extraction_artifact import (
    IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER,
    ImageExtractionArtifact,
    ImageExtractionArtifactContractError,
    ImageExtractionArtifactRejectionCode,
    ImageExtractionArtifactStatus,
)


IMAGE_EXTRACTION_ARTIFACT_PERSISTENCE_FORMAT: Final = (
    "image_extraction_artifact_canonical_json_v1"
)
IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES: Final = 65536


class ImageExtractionArtifactPersistenceError(ValueError):
    """Strict canonical artifact persistence contract failure."""


@dataclass(frozen=True)
class CanonicalImageExtractionArtifactPayload:
    payload: bytes
    serialized_sha256: str
    serialized_byte_length: int

    def __post_init__(self) -> None:
        if type(self.payload) is not bytes:
            raise TypeError("payload must be exact bytes.")
        if type(self.serialized_sha256) is not str:
            raise TypeError("serialized_sha256 must be an exact string.")
        if type(self.serialized_byte_length) is not int:
            raise TypeError(
                "serialized_byte_length must be an exact integer."
            )
        if len(self.serialized_sha256) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.serialized_sha256
        ):
            raise ImageExtractionArtifactPersistenceError(
                "serialized_sha256 must be lowercase SHA-256."
            )
        if self.serialized_byte_length != len(self.payload):
            raise ImageExtractionArtifactPersistenceError(
                "serialized_byte_length does not match payload."
            )
        expected_sha256 = hashlib.sha256(self.payload).hexdigest()
        if self.serialized_sha256 != expected_sha256:
            raise ImageExtractionArtifactPersistenceError(
                "serialized_sha256 does not match payload."
            )


def _artifact_mapping(
    artifact: ImageExtractionArtifact,
) -> dict[str, object]:
    if type(artifact) is not ImageExtractionArtifact:
        raise TypeError("artifact must be exact ImageExtractionArtifact.")

    mapping: dict[str, object] = {
        "artifact_schema_version": artifact.artifact_schema_version,
        "artifact_id": artifact.artifact_id,
        "official_image_source_id": artifact.official_image_source_id,
        "input_sha256": artifact.input_sha256,
        "input_byte_length": artifact.input_byte_length,
        "declared_media_type": artifact.declared_media_type,
        "declared_extension": artifact.declared_extension,
        "detected_format": artifact.detected_format,
        "pixel_width": artifact.pixel_width,
        "pixel_height": artifact.pixel_height,
        "parser_id": artifact.parser_id,
        "parser_version": artifact.parser_version,
        "extraction_status": artifact.extraction_status.value,
        "rejection_code": (
            None
            if artifact.rejection_code is None
            else artifact.rejection_code.value
        ),
    }

    if tuple(mapping) != IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER:
        raise RuntimeError("artifact persistence field order is invalid.")

    return mapping


def serialize_image_extraction_artifact(
    artifact: ImageExtractionArtifact,
) -> bytes:
    text = json.dumps(
        _artifact_mapping(artifact),
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    payload = (text + "\n").encode("ascii")

    if (
        len(payload) > IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES
        or b"\r" in payload
        or not payload.endswith(b"\n")
        or payload.endswith(b"\n\n")
    ):
        raise ImageExtractionArtifactPersistenceError(
            "canonical artifact payload is outside persistence boundaries."
        )

    return payload


def canonical_image_extraction_artifact_payload(
    artifact: ImageExtractionArtifact,
) -> CanonicalImageExtractionArtifactPayload:
    payload = serialize_image_extraction_artifact(artifact)
    return CanonicalImageExtractionArtifactPayload(
        payload=payload,
        serialized_sha256=hashlib.sha256(payload).hexdigest(),
        serialized_byte_length=len(payload),
    )


def _reject_duplicate_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}

    for key, value in pairs:
        if key in result:
            raise ImageExtractionArtifactPersistenceError(
                f"duplicate artifact field: {key}"
            )
        result[key] = value

    return result


def _decode_exact_object(payload: bytes) -> dict[str, object]:
    if type(payload) is not bytes:
        raise TypeError("payload must be exact bytes.")
    if not (
        0 < len(payload) <= IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES
    ):
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload length is outside persistence boundaries."
        )
    if payload.startswith(b"\xef\xbb\xbf"):
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload must not contain a BOM."
        )
    if b"\r" in payload:
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload must use LF only."
        )
    if not payload.endswith(b"\n") or payload.endswith(b"\n\n"):
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload must contain exactly one final LF."
        )

    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload must be ASCII."
        ) from exc

    try:
        decoded = json.loads(
            text[:-1],
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ImageExtractionArtifactPersistenceError(
                    f"non-finite JSON value is forbidden: {value}"
                )
            ),
        )
    except ImageExtractionArtifactPersistenceError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ImageExtractionArtifactPersistenceError(
            "serialized payload is not valid canonical artifact JSON."
        ) from exc

    if type(decoded) is not dict:
        raise ImageExtractionArtifactPersistenceError(
            "serialized artifact must be one JSON object."
        )
    if tuple(decoded) != IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER:
        raise ImageExtractionArtifactPersistenceError(
            "serialized artifact field set or order is invalid."
        )

    return decoded


def deserialize_image_extraction_artifact(
    payload: bytes,
) -> ImageExtractionArtifact:
    decoded = _decode_exact_object(payload)

    try:
        status = ImageExtractionArtifactStatus(
            decoded["extraction_status"]
        )
    except (TypeError, ValueError) as exc:
        raise ImageExtractionArtifactPersistenceError(
            "extraction_status is invalid."
        ) from exc

    rejection_value = decoded["rejection_code"]
    if rejection_value is None:
        rejection_code = None
    else:
        try:
            rejection_code = ImageExtractionArtifactRejectionCode(
                rejection_value
            )
        except (TypeError, ValueError) as exc:
            raise ImageExtractionArtifactPersistenceError(
                "rejection_code is invalid."
            ) from exc

    try:
        artifact = ImageExtractionArtifact(
            artifact_schema_version=decoded["artifact_schema_version"],
            artifact_id=decoded["artifact_id"],
            official_image_source_id=decoded[
                "official_image_source_id"
            ],
            input_sha256=decoded["input_sha256"],
            input_byte_length=decoded["input_byte_length"],
            declared_media_type=decoded["declared_media_type"],
            declared_extension=decoded["declared_extension"],
            detected_format=decoded["detected_format"],
            pixel_width=decoded["pixel_width"],
            pixel_height=decoded["pixel_height"],
            parser_id=decoded["parser_id"],
            parser_version=decoded["parser_version"],
            extraction_status=status,
            rejection_code=rejection_code,
        )
    except (
        ImageExtractionArtifactContractError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise ImageExtractionArtifactPersistenceError(
            "serialized artifact violates the artifact model contract."
        ) from exc

    canonical = serialize_image_extraction_artifact(artifact)
    if canonical != payload:
        raise ImageExtractionArtifactPersistenceError(
            "serialized artifact bytes are not canonical."
        )

    return artifact
