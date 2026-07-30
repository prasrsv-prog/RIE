"""Versioned factual image extraction artifact model for Gate 13."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields
from enum import Enum
from typing import Final, Mapping


IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION: Final = (
    "image_extraction_artifact_v1"
)
IMAGE_EXTRACTION_ARTIFACT_MAX_INPUT_BYTES: Final = (1 << 63) - 1
IMAGE_EXTRACTION_ARTIFACT_MAX_DIMENSION: Final = (1 << 31) - 1

IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER: Final = (
    "artifact_schema_version",
    "artifact_id",
    "official_image_source_id",
    "input_sha256",
    "input_byte_length",
    "declared_media_type",
    "declared_extension",
    "detected_format",
    "pixel_width",
    "pixel_height",
    "parser_id",
    "parser_version",
    "extraction_status",
    "rejection_code",
)

IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER: Final = tuple(
    name for name in IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER
    if name != "artifact_id"
)

SUPPORTED_IMAGE_FORMATS: Final = frozenset({"jpeg", "png", "webp"})
SUPPORTED_MEDIA_TYPES: Final = frozenset(
    {"image/jpeg", "image/png", "image/webp"}
)
SUPPORTED_EXTENSIONS: Final = frozenset({".jpg", ".jpeg", ".png", ".webp"})

_EXTENSION_MEDIA_FORMAT: Final = {
    ".jpg": ("image/jpeg", "jpeg"),
    ".jpeg": ("image/jpeg", "jpeg"),
    ".png": ("image/png", "png"),
    ".webp": ("image/webp", "webp"),
}

_LOWER_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,255}$")


class ImageExtractionArtifactStatus(str, Enum):
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"


class ImageExtractionArtifactRejectionCode(str, Enum):
    OFFICIAL_IMAGE_SOURCE_MISSING = "official_image_source_missing"
    OFFICIAL_IMAGE_SOURCE_NOT_ACCEPTED = (
        "official_image_source_not_accepted"
    )
    AUTHORITY_REJECTED = "authority_rejected"
    RIGHTS_REJECTED = "rights_rejected"
    LIFECYCLE_REJECTED = "lifecycle_rejected"
    SOURCE_ID_MISMATCH = "source_id_mismatch"
    SOURCE_REFERENCE_MISMATCH = "source_reference_mismatch"
    INPUT_SHA256_MISMATCH = "input_sha256_mismatch"
    INPUT_BYTE_LENGTH_MISMATCH = "input_byte_length_mismatch"
    PROVENANCE_MISSING = "provenance_missing"
    DECLARED_MEDIA_TYPE_EXTENSION_CONFLICT = (
        "declared_media_type_extension_conflict"
    )
    DECLARED_FORMAT_CONFLICT = "declared_format_conflict"
    UNSUPPORTED_FORMAT = "unsupported_format"
    MALFORMED_STRUCTURE = "malformed_structure"
    INVALID_DIMENSIONS = "invalid_dimensions"
    RESOURCE_LIMIT_EXCEEDED = "resource_limit_exceeded"
    PARSER_IDENTITY_MISMATCH = "parser_identity_mismatch"
    UNSUPPORTED_SCHEMA_VERSION = "unsupported_schema_version"
    ARTIFACT_CONTRACT_FAILURE = "artifact_contract_failure"
    DETERMINISTIC_OUTPUT_UNPROVEN = "deterministic_output_unproven"


class ImageExtractionArtifactContractError(ValueError):
    """Deterministic Gate 13 artifact model contract failure."""


def _require_exact_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an exact integer.")
    return value


def _require_token(value: object, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be an exact string.")
    if _TOKEN.fullmatch(value) is None:
        raise ImageExtractionArtifactContractError(
            f"{name} must be a non-empty controlled ASCII token."
        )
    return value


def _require_sha256(value: object, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be an exact string.")
    if _LOWER_HEX_64.fullmatch(value) is None:
        raise ImageExtractionArtifactContractError(
            f"{name} must contain exactly 64 lowercase hexadecimal characters."
        )
    return value


def _require_enum(value: object, enum_type: type[Enum], name: str) -> Enum:
    if type(value) is not enum_type:
        raise TypeError(f"{name} must be exact {enum_type.__name__}.")
    return value


def _identity_mapping_from_values(
    *,
    artifact_schema_version: str,
    official_image_source_id: str,
    input_sha256: str,
    input_byte_length: int,
    declared_media_type: str,
    declared_extension: str,
    detected_format: str | None,
    pixel_width: int | None,
    pixel_height: int | None,
    parser_id: str,
    parser_version: str,
    extraction_status: ImageExtractionArtifactStatus,
    rejection_code: ImageExtractionArtifactRejectionCode | None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_schema_version": artifact_schema_version,
        "official_image_source_id": official_image_source_id,
        "input_sha256": input_sha256,
        "input_byte_length": input_byte_length,
        "declared_media_type": declared_media_type,
        "declared_extension": declared_extension,
        "detected_format": detected_format,
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "parser_id": parser_id,
        "parser_version": parser_version,
        "extraction_status": extraction_status.value,
        "rejection_code": (
            None if rejection_code is None else rejection_code.value
        ),
    }
    if tuple(payload) != IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER:
        raise RuntimeError("identity field order is invalid.")
    return payload


def image_extraction_artifact_identity_bytes(
    values: Mapping[str, object],
) -> bytes:
    if type(values) is not dict:
        raise TypeError("values must be an exact dict.")
    if tuple(values) != IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER:
        raise ImageExtractionArtifactContractError(
            "identity mapping field order is invalid."
        )
    text = json.dumps(
        values,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    result = (text + "\n").encode("ascii")
    if (
        b"\r" in result
        or not result.endswith(b"\n")
        or result.endswith(b"\n\n")
    ):
        raise RuntimeError("identity byte encoding is invalid.")
    return result


def compute_image_extraction_artifact_id(
    *,
    artifact_schema_version: str,
    official_image_source_id: str,
    input_sha256: str,
    input_byte_length: int,
    declared_media_type: str,
    declared_extension: str,
    detected_format: str | None,
    pixel_width: int | None,
    pixel_height: int | None,
    parser_id: str,
    parser_version: str,
    extraction_status: ImageExtractionArtifactStatus,
    rejection_code: ImageExtractionArtifactRejectionCode | None,
) -> str:
    payload = _identity_mapping_from_values(
        artifact_schema_version=artifact_schema_version,
        official_image_source_id=official_image_source_id,
        input_sha256=input_sha256,
        input_byte_length=input_byte_length,
        declared_media_type=declared_media_type,
        declared_extension=declared_extension,
        detected_format=detected_format,
        pixel_width=pixel_width,
        pixel_height=pixel_height,
        parser_id=parser_id,
        parser_version=parser_version,
        extraction_status=extraction_status,
        rejection_code=rejection_code,
    )
    return hashlib.sha256(
        image_extraction_artifact_identity_bytes(payload)
    ).hexdigest()


@dataclass(frozen=True)
class ImageExtractionArtifact:
    artifact_schema_version: str
    artifact_id: str
    official_image_source_id: str
    input_sha256: str
    input_byte_length: int
    declared_media_type: str
    declared_extension: str
    detected_format: str | None
    pixel_width: int | None
    pixel_height: int | None
    parser_id: str
    parser_version: str
    extraction_status: ImageExtractionArtifactStatus
    rejection_code: ImageExtractionArtifactRejectionCode | None

    def __post_init__(self) -> None:
        if tuple(field.name for field in fields(type(self))) != (
            IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER
        ):
            raise RuntimeError("artifact field order is invalid.")

        if self.artifact_schema_version != (
            IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION
        ):
            raise ImageExtractionArtifactContractError(
                "artifact_schema_version is unsupported."
            )

        _require_sha256(self.artifact_id, "artifact_id")
        _require_token(
            self.official_image_source_id,
            "official_image_source_id",
        )
        _require_sha256(self.input_sha256, "input_sha256")

        input_byte_length = _require_exact_int(
            self.input_byte_length,
            "input_byte_length",
        )
        if not (
            0 < input_byte_length <=
            IMAGE_EXTRACTION_ARTIFACT_MAX_INPUT_BYTES
        ):
            raise ImageExtractionArtifactContractError(
                "input_byte_length is outside the artifact model boundary."
            )

        if type(self.declared_media_type) is not str:
            raise TypeError("declared_media_type must be an exact string.")
        if self.declared_media_type not in SUPPORTED_MEDIA_TYPES:
            raise ImageExtractionArtifactContractError(
                "declared_media_type is unsupported."
            )

        if type(self.declared_extension) is not str:
            raise TypeError("declared_extension must be an exact string.")
        if self.declared_extension not in SUPPORTED_EXTENSIONS:
            raise ImageExtractionArtifactContractError(
                "declared_extension is unsupported."
            )

        expected_media_type, expected_format = _EXTENSION_MEDIA_FORMAT[
            self.declared_extension
        ]
        if self.declared_media_type != expected_media_type:
            raise ImageExtractionArtifactContractError(
                "declared media type and extension conflict."
            )

        _require_token(self.parser_id, "parser_id")
        _require_token(self.parser_version, "parser_version")
        _require_enum(
            self.extraction_status,
            ImageExtractionArtifactStatus,
            "extraction_status",
        )

        if self.rejection_code is not None:
            _require_enum(
                self.rejection_code,
                ImageExtractionArtifactRejectionCode,
                "rejection_code",
            )

        if self.extraction_status is ImageExtractionArtifactStatus.SUCCEEDED:
            if self.rejection_code is not None:
                raise ImageExtractionArtifactContractError(
                    "successful artifact must not contain rejection_code."
                )
            if type(self.detected_format) is not str:
                raise TypeError(
                    "detected_format must be an exact string on success."
                )
            if self.detected_format not in SUPPORTED_IMAGE_FORMATS:
                raise ImageExtractionArtifactContractError(
                    "detected_format is unsupported."
                )
            if self.detected_format != expected_format:
                raise ImageExtractionArtifactContractError(
                    "declared classification and detected format conflict."
                )
            width = _require_exact_int(self.pixel_width, "pixel_width")
            height = _require_exact_int(self.pixel_height, "pixel_height")
            if not (
                0 < width <= IMAGE_EXTRACTION_ARTIFACT_MAX_DIMENSION
                and 0 < height <= IMAGE_EXTRACTION_ARTIFACT_MAX_DIMENSION
            ):
                raise ImageExtractionArtifactContractError(
                    "pixel dimensions are outside the artifact model boundary."
                )
        else:
            if self.rejection_code is None:
                raise ImageExtractionArtifactContractError(
                    "rejected artifact requires rejection_code."
                )
            if (
                self.detected_format is not None
                or self.pixel_width is not None
                or self.pixel_height is not None
            ):
                raise ImageExtractionArtifactContractError(
                    "rejected artifact must not contain structural facts."
                )

        expected_id = compute_image_extraction_artifact_id(
            artifact_schema_version=self.artifact_schema_version,
            official_image_source_id=self.official_image_source_id,
            input_sha256=self.input_sha256,
            input_byte_length=self.input_byte_length,
            declared_media_type=self.declared_media_type,
            declared_extension=self.declared_extension,
            detected_format=self.detected_format,
            pixel_width=self.pixel_width,
            pixel_height=self.pixel_height,
            parser_id=self.parser_id,
            parser_version=self.parser_version,
            extraction_status=self.extraction_status,
            rejection_code=self.rejection_code,
        )
        if self.artifact_id != expected_id:
            raise ImageExtractionArtifactContractError(
                "artifact_id does not match canonical identity fields."
            )

    @classmethod
    def succeeded(
        cls,
        *,
        official_image_source_id: str,
        input_sha256: str,
        input_byte_length: int,
        declared_media_type: str,
        declared_extension: str,
        detected_format: str,
        pixel_width: int,
        pixel_height: int,
        parser_id: str,
        parser_version: str,
    ) -> "ImageExtractionArtifact":
        values = {
            "artifact_schema_version":
                IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION,
            "official_image_source_id": official_image_source_id,
            "input_sha256": input_sha256,
            "input_byte_length": input_byte_length,
            "declared_media_type": declared_media_type,
            "declared_extension": declared_extension,
            "detected_format": detected_format,
            "pixel_width": pixel_width,
            "pixel_height": pixel_height,
            "parser_id": parser_id,
            "parser_version": parser_version,
            "extraction_status":
                ImageExtractionArtifactStatus.SUCCEEDED,
            "rejection_code": None,
        }
        artifact_id = compute_image_extraction_artifact_id(**values)
        return cls(artifact_id=artifact_id, **values)

    @classmethod
    def rejected(
        cls,
        *,
        official_image_source_id: str,
        input_sha256: str,
        input_byte_length: int,
        declared_media_type: str,
        declared_extension: str,
        parser_id: str,
        parser_version: str,
        rejection_code: ImageExtractionArtifactRejectionCode,
    ) -> "ImageExtractionArtifact":
        values = {
            "artifact_schema_version":
                IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION,
            "official_image_source_id": official_image_source_id,
            "input_sha256": input_sha256,
            "input_byte_length": input_byte_length,
            "declared_media_type": declared_media_type,
            "declared_extension": declared_extension,
            "detected_format": None,
            "pixel_width": None,
            "pixel_height": None,
            "parser_id": parser_id,
            "parser_version": parser_version,
            "extraction_status": ImageExtractionArtifactStatus.REJECTED,
            "rejection_code": rejection_code,
        }
        artifact_id = compute_image_extraction_artifact_id(**values)
        return cls(artifact_id=artifact_id, **values)
