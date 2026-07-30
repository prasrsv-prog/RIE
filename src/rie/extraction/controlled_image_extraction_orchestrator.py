"""Synthetic-only Gate 13 controlled image extraction orchestration."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path
from typing import Final

from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifact,
    ImageExtractionArtifactRejectionCode,
    ImageExtractionArtifactStatus,
)
from rie.extraction.image_extraction_artifact_file_persistence import (
    ImageExtractionArtifactFileWriteResult,
    ImageExtractionArtifactFileWriteStatus,
    persist_image_extraction_artifact_file,
)
from rie.extraction.image_structure_parser import (
    PARSER_ID,
    PARSER_VERSION,
    ImageStructureResult,
    inspect_image_structure_bytes,
)
from rie.extraction.official_image_source_extraction_integration import (
    OfficialImageSourceExtractionValidationResult,
    OfficialImageSourceExtractionValidationStatus,
    resolve_and_validate_official_image_source_for_extraction,
)


CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION: Final = (
    "controlled_image_extraction_orchestration_v1"
)
CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_RESULT_FIELD_ORDER: Final = (
    "orchestration_version",
    "status",
    "source_validation",
    "parser_executed",
    "parser_result",
    "artifact",
    "persistence_result",
)
_SUPPORTED_DECLARATIONS: Final = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
_FORMAT_NORMALIZATION: Final = {
    "JPEG": "jpeg",
    "PNG": "png",
    "WEBP": "webp",
}
_MALFORMED_REASONS: Final = frozenset(
    {
        "TRUNCATED_PNG",
        "MALFORMED_PNG",
        "TRUNCATED_JPEG",
        "MALFORMED_JPEG",
        "JPEG_SOF_NOT_FOUND",
        "TRUNCATED_WEBP",
        "MALFORMED_WEBP",
    }
)


class ControlledImageExtractionOrchestrationStatus(str, Enum):
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"
    PERSISTENCE_FAILED = "persistence_failed"


@dataclass(frozen=True)
class ControlledImageExtractionOrchestrationResult:
    orchestration_version: str
    status: ControlledImageExtractionOrchestrationStatus
    source_validation: OfficialImageSourceExtractionValidationResult
    parser_executed: bool
    parser_result: ImageStructureResult | None
    artifact: ImageExtractionArtifact
    persistence_result: ImageExtractionArtifactFileWriteResult

    def __post_init__(self) -> None:
        if tuple(field.name for field in fields(type(self))) != (
            CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_RESULT_FIELD_ORDER
        ):
            raise RuntimeError("orchestration result field order is invalid.")
        if self.orchestration_version != (
            CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION
        ):
            raise ValueError("orchestration_version is unsupported.")
        if type(self.status) is not (
            ControlledImageExtractionOrchestrationStatus
        ):
            raise TypeError("status must be exact orchestration status.")
        if type(self.source_validation) is not (
            OfficialImageSourceExtractionValidationResult
        ):
            raise TypeError(
                "source_validation must be exact validation result."
            )
        if type(self.parser_executed) is not bool:
            raise TypeError("parser_executed must be exact bool.")
        if self.parser_executed:
            if type(self.parser_result) is not ImageStructureResult:
                raise TypeError(
                    "executed parser requires exact parser result."
                )
        elif self.parser_result is not None:
            raise ValueError(
                "non-executed parser must not contain parser_result."
            )
        if type(self.artifact) is not ImageExtractionArtifact:
            raise TypeError("artifact must be exact ImageExtractionArtifact.")
        if type(self.persistence_result) is not (
            ImageExtractionArtifactFileWriteResult
        ):
            raise TypeError(
                "persistence_result must be exact write result."
            )
        if self.persistence_result.artifact_id != self.artifact.artifact_id:
            raise ValueError(
                "persistence_result artifact_id does not match artifact."
            )

        persistence_succeeded = (
            self.persistence_result.status
            in {
                ImageExtractionArtifactFileWriteStatus.WRITTEN,
                ImageExtractionArtifactFileWriteStatus.ALREADY_PRESENT,
            }
        )

        if self.status is (
            ControlledImageExtractionOrchestrationStatus
            .PERSISTENCE_FAILED
        ):
            if persistence_succeeded:
                raise ValueError(
                    "persistence_failed requires rejected persistence."
                )
            return

        if not persistence_succeeded:
            raise ValueError(
                "non-failed status requires successful persistence."
            )

        if self.status is (
            ControlledImageExtractionOrchestrationStatus.SUCCEEDED
        ):
            if self.artifact.extraction_status is not (
                ImageExtractionArtifactStatus.SUCCEEDED
            ):
                raise ValueError(
                    "succeeded status requires successful artifact."
                )
        elif self.artifact.extraction_status is not (
            ImageExtractionArtifactStatus.REJECTED
        ):
            raise ValueError(
                "rejected status requires rejected artifact."
            )


def _require_declaration(
    declared_media_type: object,
    declared_extension: object,
) -> tuple[str, str]:
    if type(declared_media_type) is not str:
        raise TypeError("declared_media_type must be an exact string.")
    if type(declared_extension) is not str:
        raise TypeError("declared_extension must be an exact string.")
    if (
        _SUPPORTED_DECLARATIONS.get(declared_extension)
        != declared_media_type
    ):
        raise ValueError(
            "declared media type and extension must be one coherent "
            "supported Gate 13 pair."
        )
    return declared_media_type, declared_extension


def _rejected_artifact(
    *,
    source_validation: OfficialImageSourceExtractionValidationResult,
    rejection_code: ImageExtractionArtifactRejectionCode,
) -> ImageExtractionArtifact:
    return ImageExtractionArtifact.rejected(
        official_image_source_id=(
            source_validation.presented_source_id
        ),
        input_sha256=source_validation.input_sha256,
        input_byte_length=source_validation.input_byte_length,
        declared_media_type=source_validation.declared_media_type,
        declared_extension=source_validation.declared_extension,
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
        rejection_code=rejection_code,
    )


def _parser_rejection_code(
    parser_result: ImageStructureResult,
) -> ImageExtractionArtifactRejectionCode:
    reason = parser_result.rejection_reason

    if reason == "OVERSIZED_INPUT":
        return (
            ImageExtractionArtifactRejectionCode
            .RESOURCE_LIMIT_EXCEEDED
        )
    if reason in {
        "UNSUPPORTED_SIGNATURE",
        "UNSUPPORTED_WEBP_CHUNK",
    }:
        return ImageExtractionArtifactRejectionCode.UNSUPPORTED_FORMAT
    if reason == "ZERO_DIMENSION":
        return ImageExtractionArtifactRejectionCode.INVALID_DIMENSIONS
    if reason in _MALFORMED_REASONS:
        return ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE
    return (
        ImageExtractionArtifactRejectionCode
        .DETERMINISTIC_OUTPUT_UNPROVEN
    )


def _artifact_from_parser(
    *,
    source_validation: OfficialImageSourceExtractionValidationResult,
    parser_result: ImageStructureResult,
) -> ImageExtractionArtifact:
    if (
        parser_result.parser_id != PARSER_ID
        or parser_result.parser_version != PARSER_VERSION
    ):
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .PARSER_IDENTITY_MISMATCH
            ),
        )

    if (
        parser_result.input_sha256
        != source_validation.input_sha256
        or parser_result.input_byte_length
        != source_validation.input_byte_length
    ):
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DETERMINISTIC_OUTPUT_UNPROVEN
            ),
        )

    if parser_result.status == "REJECTED":
        if (
            parser_result.width is not None
            or parser_result.height is not None
        ):
            return _rejected_artifact(
                source_validation=source_validation,
                rejection_code=(
                    ImageExtractionArtifactRejectionCode
                    .DETERMINISTIC_OUTPUT_UNPROVEN
                ),
            )
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=_parser_rejection_code(parser_result),
        )

    if parser_result.status != "ACCEPTED":
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DETERMINISTIC_OUTPUT_UNPROVEN
            ),
        )

    if parser_result.rejection_reason is not None:
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DETERMINISTIC_OUTPUT_UNPROVEN
            ),
        )

    detected_format = _FORMAT_NORMALIZATION.get(
        parser_result.image_format
    )
    if detected_format is None:
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DETERMINISTIC_OUTPUT_UNPROVEN
            ),
        )

    expected_format = {
        "image/jpeg": "jpeg",
        "image/png": "png",
        "image/webp": "webp",
    }[source_validation.declared_media_type]

    if detected_format != expected_format:
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .DECLARED_FORMAT_CONFLICT
            ),
        )

    if (
        type(parser_result.width) is not int
        or type(parser_result.height) is not int
        or parser_result.width <= 0
        or parser_result.height <= 0
    ):
        return _rejected_artifact(
            source_validation=source_validation,
            rejection_code=(
                ImageExtractionArtifactRejectionCode
                .INVALID_DIMENSIONS
            ),
        )

    return ImageExtractionArtifact.succeeded(
        official_image_source_id=(
            source_validation.presented_source_id
        ),
        input_sha256=source_validation.input_sha256,
        input_byte_length=source_validation.input_byte_length,
        declared_media_type=source_validation.declared_media_type,
        declared_extension=source_validation.declared_extension,
        detected_format=detected_format,
        pixel_width=parser_result.width,
        pixel_height=parser_result.height,
        parser_id=PARSER_ID,
        parser_version=PARSER_VERSION,
    )


def _status_for(
    artifact: ImageExtractionArtifact,
    persistence_result: ImageExtractionArtifactFileWriteResult,
) -> ControlledImageExtractionOrchestrationStatus:
    if persistence_result.status is (
        ImageExtractionArtifactFileWriteStatus.REJECTED
    ):
        return (
            ControlledImageExtractionOrchestrationStatus
            .PERSISTENCE_FAILED
        )
    if artifact.extraction_status is (
        ImageExtractionArtifactStatus.SUCCEEDED
    ):
        return ControlledImageExtractionOrchestrationStatus.SUCCEEDED
    return ControlledImageExtractionOrchestrationStatus.REJECTED


def run_controlled_image_extraction(
    *,
    official_source_payload: bytes | None,
    presented_source_id: str,
    presented_source_locator: str,
    input_bytes: bytes,
    declared_media_type: str,
    declared_extension: str,
    artifact_root: Path,
) -> ControlledImageExtractionOrchestrationResult:
    """Run one bounded synthetic Gate 13 extraction workflow."""

    declared_media_type, declared_extension = _require_declaration(
        declared_media_type,
        declared_extension,
    )
    if not isinstance(artifact_root, Path):
        raise TypeError("artifact_root must be a pathlib.Path.")

    source_validation = (
        resolve_and_validate_official_image_source_for_extraction(
            official_source_payload=official_source_payload,
            presented_source_id=presented_source_id,
            presented_source_locator=presented_source_locator,
            input_bytes=input_bytes,
            declared_media_type=declared_media_type,
            declared_extension=declared_extension,
        )
    )

    parser_executed = False
    parser_result: ImageStructureResult | None = None

    if source_validation.status is (
        OfficialImageSourceExtractionValidationStatus.ACCEPTED
    ):
        parser_executed = True
        parser_result = inspect_image_structure_bytes(input_bytes)

        if type(parser_result) is not ImageStructureResult:
            raise TypeError(
                "parser returned non-ImageStructureResult."
            )

        artifact = _artifact_from_parser(
            source_validation=source_validation,
            parser_result=parser_result,
        )
    else:
        if source_validation.rejection_code is None:
            raise RuntimeError(
                "rejected source validation lacks rejection_code."
            )
        artifact = _rejected_artifact(
            source_validation=source_validation,
            rejection_code=source_validation.rejection_code,
        )

    persistence_result = persist_image_extraction_artifact_file(
        artifact_root,
        artifact,
    )

    return ControlledImageExtractionOrchestrationResult(
        orchestration_version=(
            CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION
        ),
        status=_status_for(artifact, persistence_result),
        source_validation=source_validation,
        parser_executed=parser_executed,
        parser_result=parser_result,
        artifact=artifact,
        persistence_result=persistence_result,
    )
