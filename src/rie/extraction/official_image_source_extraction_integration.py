"""Official Image Source integration boundary for Gate 13 extraction."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, fields
from enum import Enum
from typing import Final

from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifactRejectionCode,
)
from rie.official_source.official_image_source import (
    AdmissionStatus,
    AuthorityClass,
    LifecycleState,
    OfficialImageSource,
    RightsStatus,
    SourceKind,
)
from rie.official_source.official_image_source_persistence import (
    decode_official_image_source,
)


OFFICIAL_IMAGE_SOURCE_EXTRACTION_INTEGRATION_VERSION: Final = (
    "official_image_source_extraction_integration_v1"
)
OFFICIAL_IMAGE_SOURCE_EXTRACTION_RESULT_FIELD_ORDER: Final = (
    "integration_version",
    "status",
    "presented_source_id",
    "presented_source_locator",
    "input_sha256",
    "input_byte_length",
    "declared_media_type",
    "declared_extension",
    "official_source",
    "provenance_reference_id",
    "rejection_code",
)

_SUPPORTED_CLASSIFICATIONS: Final = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
_ALLOWED_AUTHORITY_BY_KIND: Final = {
    SourceKind.FILE: frozenset(
        {
            AuthorityClass.OFFICIAL_INTERNAL,
            AuthorityClass.OFFICIAL_PARTNER,
        }
    ),
    SourceKind.REPOSITORY_ASSET: frozenset(
        {
            AuthorityClass.OFFICIAL_INTERNAL,
            AuthorityClass.OFFICIAL_PARTNER,
        }
    ),
    SourceKind.CONTROLLED_EXTERNAL_REFERENCE: frozenset(
        {
            AuthorityClass.OFFICIAL_PARTNER,
            AuthorityClass.CONTROLLED_EXTERNAL,
        }
    ),
}
_ALLOWED_RIGHTS: Final = frozenset(
    {
        RightsStatus.OWNED,
        RightsStatus.LICENSED,
        RightsStatus.APPROVED_INTERNAL_USE,
    }
)
_CONTROLLED_TEXT = re.compile(r"^[^\x00-\x1f\x7f]+$")
_ARTIFACT_SOURCE_ID_TOKEN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,255}$"
)


class OfficialImageSourceExtractionValidationStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class OfficialImageSourceExtractionValidationResult:
    integration_version: str
    status: OfficialImageSourceExtractionValidationStatus
    presented_source_id: str
    presented_source_locator: str
    input_sha256: str
    input_byte_length: int
    declared_media_type: str
    declared_extension: str
    official_source: OfficialImageSource | None
    provenance_reference_id: str | None
    rejection_code: ImageExtractionArtifactRejectionCode | None

    def __post_init__(self) -> None:
        if tuple(field.name for field in fields(type(self))) != (
            OFFICIAL_IMAGE_SOURCE_EXTRACTION_RESULT_FIELD_ORDER
        ):
            raise RuntimeError("integration result field order is invalid.")
        if self.integration_version != (
            OFFICIAL_IMAGE_SOURCE_EXTRACTION_INTEGRATION_VERSION
        ):
            raise ValueError("integration_version is unsupported.")
        if type(self.status) is not (
            OfficialImageSourceExtractionValidationStatus
        ):
            raise TypeError(
                "status must be exact validation status."
            )
        _require_clean_text(
            self.presented_source_id,
            "presented_source_id",
        )
        _require_clean_text(
            self.presented_source_locator,
            "presented_source_locator",
        )
        _require_sha256(self.input_sha256)
        if type(self.input_byte_length) is not int:
            raise TypeError(
                "input_byte_length must be an exact integer."
            )
        if self.input_byte_length <= 0:
            raise ValueError("input_byte_length must be positive.")
        _require_declared_strings(
            self.declared_media_type,
            self.declared_extension,
        )

        if self.status is (
            OfficialImageSourceExtractionValidationStatus.ACCEPTED
        ):
            _require_declared_classification(
                self.declared_media_type,
                self.declared_extension,
            )
            if type(self.official_source) is not OfficialImageSource:
                raise TypeError(
                    "accepted result requires exact OfficialImageSource."
                )
            if self.rejection_code is not None:
                raise ValueError(
                    "accepted result must not contain rejection_code."
                )
            if type(self.provenance_reference_id) is not str:
                raise TypeError(
                    "accepted result requires provenance_reference_id."
                )
            _require_clean_text(
                self.provenance_reference_id,
                "provenance_reference_id",
            )
            if self.official_source.source_id != (
                self.presented_source_id
            ):
                raise ValueError(
                    "accepted source_id does not match presentation."
                )
        else:
            if self.official_source is not None:
                raise ValueError(
                    "rejected result must not contain official_source."
                )
            if self.provenance_reference_id is not None:
                raise ValueError(
                    "rejected result must not contain provenance_reference_id."
                )
            if type(self.rejection_code) is not (
                ImageExtractionArtifactRejectionCode
            ):
                raise TypeError(
                    "rejected result requires exact rejection_code."
                )


def _require_clean_text(value: object, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be an exact string.")
    if (
        not value
        or value != value.strip()
        or _CONTROLLED_TEXT.fullmatch(value) is None
    ):
        raise ValueError(
            f"{name} must be clean non-empty controlled text."
        )
    return value


def _require_source_id(value: object) -> str:
    source_id = _require_clean_text(value, "presented_source_id")
    if _ARTIFACT_SOURCE_ID_TOKEN.fullmatch(source_id) is None:
        raise ValueError(
            "presented_source_id is not artifact-compatible."
        )
    return source_id


def _require_sha256(value: object) -> str:
    if type(value) is not str:
        raise TypeError("input_sha256 must be an exact string.")
    if len(value) != 64 or any(
        character not in "0123456789abcdef"
        for character in value
    ):
        raise ValueError(
            "input_sha256 must be lowercase SHA-256."
        )
    return value


def _require_declared_strings(
    declared_media_type: object,
    declared_extension: object,
) -> None:
    if type(declared_media_type) is not str:
        raise TypeError(
            "declared_media_type must be an exact string."
        )
    if type(declared_extension) is not str:
        raise TypeError(
            "declared_extension must be an exact string."
        )


def _require_declared_classification(
    declared_media_type: object,
    declared_extension: object,
) -> None:
    _require_declared_strings(
        declared_media_type,
        declared_extension,
    )
    expected_media_type = _SUPPORTED_CLASSIFICATIONS.get(
        declared_extension
    )
    if (
        expected_media_type is None
        or declared_media_type != expected_media_type
    ):
        raise ValueError(
            "declared media type and extension conflict."
        )


def _result(
    *,
    status: OfficialImageSourceExtractionValidationStatus,
    presented_source_id: str,
    presented_source_locator: str,
    input_sha256: str,
    input_byte_length: int,
    declared_media_type: str,
    declared_extension: str,
    official_source: OfficialImageSource | None = None,
    provenance_reference_id: str | None = None,
    rejection_code: ImageExtractionArtifactRejectionCode | None = None,
) -> OfficialImageSourceExtractionValidationResult:
    return OfficialImageSourceExtractionValidationResult(
        integration_version=(
            OFFICIAL_IMAGE_SOURCE_EXTRACTION_INTEGRATION_VERSION
        ),
        status=status,
        presented_source_id=presented_source_id,
        presented_source_locator=presented_source_locator,
        input_sha256=input_sha256,
        input_byte_length=input_byte_length,
        declared_media_type=declared_media_type,
        declared_extension=declared_extension,
        official_source=official_source,
        provenance_reference_id=provenance_reference_id,
        rejection_code=rejection_code,
    )


def _rejected(
    *,
    presented_source_id: str,
    presented_source_locator: str,
    input_sha256: str,
    input_byte_length: int,
    declared_media_type: str,
    declared_extension: str,
    rejection_code: ImageExtractionArtifactRejectionCode,
) -> OfficialImageSourceExtractionValidationResult:
    return _result(
        status=(
            OfficialImageSourceExtractionValidationStatus.REJECTED
        ),
        presented_source_id=presented_source_id,
        presented_source_locator=presented_source_locator,
        input_sha256=input_sha256,
        input_byte_length=input_byte_length,
        declared_media_type=declared_media_type,
        declared_extension=declared_extension,
        rejection_code=rejection_code,
    )


def resolve_and_validate_official_image_source_for_extraction(
    *,
    official_source_payload: bytes | None,
    presented_source_id: str,
    presented_source_locator: str,
    input_bytes: bytes,
    declared_media_type: str,
    declared_extension: str,
) -> OfficialImageSourceExtractionValidationResult:
    """Resolve one canonical source record and revalidate governed input."""

    presented_source_id = _require_source_id(
        presented_source_id
    )
    presented_source_locator = _require_clean_text(
        presented_source_locator,
        "presented_source_locator",
    )
    if type(input_bytes) is not bytes:
        raise TypeError("input_bytes must be exact bytes.")
    if len(input_bytes) <= 0:
        raise ValueError("input_bytes must be non-empty.")
    _require_declared_strings(
        declared_media_type,
        declared_extension,
    )

    input_sha256 = hashlib.sha256(input_bytes).hexdigest()
    input_byte_length = len(input_bytes)

    common = {
        "presented_source_id": presented_source_id,
        "presented_source_locator": presented_source_locator,
        "input_sha256": input_sha256,
        "input_byte_length": input_byte_length,
        "declared_media_type": declared_media_type,
        "declared_extension": declared_extension,
    }

    if (
        _SUPPORTED_CLASSIFICATIONS.get(declared_extension)
        != declared_media_type
    ):
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DECLARED_MEDIA_TYPE_EXTENSION_CONFLICT
            ),
        )

    if official_source_payload is None:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .OFFICIAL_IMAGE_SOURCE_MISSING
            ),
        )
    if type(official_source_payload) is not bytes:
        raise TypeError(
            "official_source_payload must be exact bytes or None."
        )

    try:
        source = decode_official_image_source(
            official_source_payload
        )
    except (TypeError, ValueError):
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .OFFICIAL_IMAGE_SOURCE_NOT_ACCEPTED
            ),
        )

    if source.source_id != presented_source_id:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .SOURCE_ID_MISMATCH
            ),
        )
    if source.source_locator != presented_source_locator:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .SOURCE_REFERENCE_MISMATCH
            ),
        )
    if source.admission_status is not AdmissionStatus.ACCEPTED:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .OFFICIAL_IMAGE_SOURCE_NOT_ACCEPTED
            ),
        )
    if source.authority_class not in (
        _ALLOWED_AUTHORITY_BY_KIND[source.source_kind]
    ):
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .AUTHORITY_REJECTED
            ),
        )
    if source.rights_status not in _ALLOWED_RIGHTS:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode.RIGHTS_REJECTED
            ),
        )
    if source.lifecycle_state is not LifecycleState.ACTIVE:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .LIFECYCLE_REJECTED
            ),
        )
    if source.content_sha256 != input_sha256:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .INPUT_SHA256_MISMATCH
            ),
        )
    if source.byte_length != input_byte_length:
        return _rejected(
            **common,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .INPUT_BYTE_LENGTH_MISMATCH
            ),
        )

    provenance_reference_id = (
        source.provenance_parent_id
        if source.provenance_parent_id is not None
        else source.source_id
    )

    return _result(
        **common,
        status=(
            OfficialImageSourceExtractionValidationStatus.ACCEPTED
        ),
        official_source=source,
        provenance_reference_id=provenance_reference_id,
    )
