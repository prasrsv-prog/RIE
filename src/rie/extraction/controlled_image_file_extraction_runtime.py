"""Bounded file-backed runtime for Gate 13 controlled image extraction."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, fields
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Final

from rie.extraction.controlled_image_extraction_orchestrator import (
    ControlledImageExtractionOrchestrationResult,
    run_controlled_image_extraction,
)
from rie.extraction.image_structure_parser import MAX_INPUT_BYTES


CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION: Final = (
    "controlled_image_file_extraction_runtime_v1"
)
CONTROLLED_IMAGE_FILE_EXTRACTION_RESULT_FIELD_ORDER: Final = (
    "runtime_version",
    "status",
    "source_relative_path",
    "source_file_opened",
    "input_sha256",
    "input_byte_length",
    "failure_code",
    "orchestration_result",
)
_SUPPORTED_DECLARATIONS: Final = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
_CONTROLLED_RELATIVE_PATH = re.compile(r"^[^\\\x00-\x1f\x7f]+$")


class ControlledImageFileExtractionRuntimeStatus(str, Enum):
    ORCHESTRATED = "orchestrated"
    FILE_REJECTED = "file_rejected"


class ControlledImageFileExtractionFailureCode(str, Enum):
    SOURCE_ROOT_NOT_ABSOLUTE = "source_root_not_absolute"
    SOURCE_ROOT_NOT_FOUND = "source_root_not_found"
    SOURCE_ROOT_NOT_DIRECTORY = "source_root_not_directory"
    SOURCE_ROOT_SYMLINK_FORBIDDEN = "source_root_symlink_forbidden"
    SOURCE_PATH_ESCAPE_FORBIDDEN = "source_path_escape_forbidden"
    SOURCE_PATH_SYMLINK_FORBIDDEN = "source_path_symlink_forbidden"
    SOURCE_FILE_NOT_FOUND = "source_file_not_found"
    SOURCE_FILE_NOT_REGULAR_FILE = "source_file_not_regular_file"
    SOURCE_FILE_EMPTY = "source_file_empty"
    SOURCE_FILE_OVERSIZED = "source_file_oversized"
    SOURCE_FILE_READ_FAILED = "source_file_read_failed"


@dataclass(frozen=True)
class ControlledImageFileExtractionRuntimeResult:
    runtime_version: str
    status: ControlledImageFileExtractionRuntimeStatus
    source_relative_path: str
    source_file_opened: bool
    input_sha256: str | None
    input_byte_length: int | None
    failure_code: ControlledImageFileExtractionFailureCode | None
    orchestration_result: (
        ControlledImageExtractionOrchestrationResult | None
    )

    def __post_init__(self) -> None:
        if tuple(field.name for field in fields(type(self))) != (
            CONTROLLED_IMAGE_FILE_EXTRACTION_RESULT_FIELD_ORDER
        ):
            raise RuntimeError("file runtime result field order is invalid.")
        if self.runtime_version != (
            CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION
        ):
            raise ValueError("runtime_version is unsupported.")
        if type(self.status) is not (
            ControlledImageFileExtractionRuntimeStatus
        ):
            raise TypeError("status must be exact file runtime status.")
        _require_relative_path(self.source_relative_path)
        if type(self.source_file_opened) is not bool:
            raise TypeError("source_file_opened must be exact bool.")

        if self.status is (
            ControlledImageFileExtractionRuntimeStatus.ORCHESTRATED
        ):
            if not self.source_file_opened:
                raise ValueError(
                    "orchestrated result requires source_file_opened."
                )
            if self.failure_code is not None:
                raise ValueError(
                    "orchestrated result must not contain failure_code."
                )
            if type(self.orchestration_result) is not (
                ControlledImageExtractionOrchestrationResult
            ):
                raise TypeError(
                    "orchestrated result requires exact orchestration result."
                )
            _require_input_metadata(
                self.input_sha256,
                self.input_byte_length,
            )
            if self.orchestration_result.artifact.input_sha256 != (
                self.input_sha256
            ):
                raise ValueError(
                    "orchestration artifact SHA-256 does not match file read."
                )
            if self.orchestration_result.artifact.input_byte_length != (
                self.input_byte_length
            ):
                raise ValueError(
                    "orchestration artifact byte length does not match file read."
                )
            return

        if self.failure_code is None:
            raise ValueError("file_rejected result requires failure_code.")
        if self.orchestration_result is not None:
            raise ValueError(
                "file_rejected result must not contain orchestration_result."
            )
        if self.input_sha256 is not None:
            raise ValueError(
                "file_rejected result must not contain input_sha256."
            )
        if self.input_byte_length is not None:
            raise ValueError(
                "file_rejected result must not contain input_byte_length."
            )


def _require_input_metadata(
    input_sha256: object,
    input_byte_length: object,
) -> None:
    if type(input_sha256) is not str:
        raise TypeError("input_sha256 must be an exact string.")
    if len(input_sha256) != 64 or any(
        character not in "0123456789abcdef"
        for character in input_sha256
    ):
        raise ValueError("input_sha256 must be lowercase SHA-256.")
    if type(input_byte_length) is not int:
        raise TypeError("input_byte_length must be an exact integer.")
    if not (0 < input_byte_length <= MAX_INPUT_BYTES):
        raise ValueError(
            "input_byte_length is outside the file runtime boundary."
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


def _require_relative_path(value: object) -> str:
    if type(value) is not str:
        raise TypeError("source_relative_path must be an exact string.")
    if (
        not value
        or value != value.strip()
        or _CONTROLLED_RELATIVE_PATH.fullmatch(value) is None
    ):
        raise ValueError(
            "source_relative_path must be clean controlled POSIX text."
        )
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(
        part in {"", ".", ".."}
        for part in pure.parts
    ):
        raise ValueError(
            "source_relative_path must be a normalized relative path."
        )
    if pure.as_posix() != value:
        raise ValueError(
            "source_relative_path must use canonical POSIX separators."
        )
    return value


def _file_rejected(
    *,
    source_relative_path: str,
    failure_code: ControlledImageFileExtractionFailureCode,
    source_file_opened: bool = False,
) -> ControlledImageFileExtractionRuntimeResult:
    return ControlledImageFileExtractionRuntimeResult(
        runtime_version=(
            CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION
        ),
        status=(
            ControlledImageFileExtractionRuntimeStatus.FILE_REJECTED
        ),
        source_relative_path=source_relative_path,
        source_file_opened=source_file_opened,
        input_sha256=None,
        input_byte_length=None,
        failure_code=failure_code,
        orchestration_result=None,
    )


def _validate_source_root(
    source_root: Path,
) -> tuple[
    Path | None,
    ControlledImageFileExtractionFailureCode | None,
]:
    if not isinstance(source_root, Path):
        raise TypeError("source_root must be a pathlib.Path.")
    if not source_root.is_absolute():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_ROOT_NOT_ABSOLUTE,
        )
    if source_root.is_symlink():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_ROOT_SYMLINK_FORBIDDEN,
        )
    if not source_root.exists():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_ROOT_NOT_FOUND,
        )
    if not source_root.is_dir():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_ROOT_NOT_DIRECTORY,
        )
    try:
        return (source_root.resolve(strict=True), None)
    except OSError:
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_ROOT_NOT_FOUND,
        )


def _resolve_source_file(
    *,
    resolved_root: Path,
    source_relative_path: str,
) -> tuple[
    Path | None,
    ControlledImageFileExtractionFailureCode | None,
]:
    parts = PurePosixPath(source_relative_path).parts
    candidate = resolved_root.joinpath(*parts)

    current = resolved_root
    for part in parts:
        current = current / part
        if current.is_symlink():
            return (
                None,
                ControlledImageFileExtractionFailureCode
                .SOURCE_PATH_SYMLINK_FORBIDDEN,
            )

    if not candidate.exists():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_FILE_NOT_FOUND,
        )
    if not candidate.is_file():
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_FILE_NOT_REGULAR_FILE,
        )

    try:
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
    except ValueError:
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_PATH_ESCAPE_FORBIDDEN,
        )
    except OSError:
        return (
            None,
            ControlledImageFileExtractionFailureCode
            .SOURCE_FILE_NOT_FOUND,
        )

    return (resolved_candidate, None)


def run_controlled_image_file_extraction(
    *,
    official_source_payload: bytes | None,
    presented_source_id: str,
    presented_source_locator: str,
    source_root: Path,
    source_relative_path: str,
    declared_media_type: str,
    declared_extension: str,
    artifact_root: Path,
) -> ControlledImageFileExtractionRuntimeResult:
    """Read one controlled file and invoke accepted bytes orchestration."""

    source_relative_path = _require_relative_path(
        source_relative_path
    )
    declared_media_type, declared_extension = _require_declaration(
        declared_media_type,
        declared_extension,
    )
    if not isinstance(artifact_root, Path):
        raise TypeError("artifact_root must be a pathlib.Path.")

    resolved_root, root_failure = _validate_source_root(source_root)
    if root_failure is not None:
        return _file_rejected(
            source_relative_path=source_relative_path,
            failure_code=root_failure,
        )
    if resolved_root is None:
        raise RuntimeError("validated source root state is invalid.")

    source_file, source_failure = _resolve_source_file(
        resolved_root=resolved_root,
        source_relative_path=source_relative_path,
    )
    if source_failure is not None:
        return _file_rejected(
            source_relative_path=source_relative_path,
            failure_code=source_failure,
        )
    if source_file is None:
        raise RuntimeError("resolved source file state is invalid.")

    try:
        with open(source_file, "rb") as stream:
            input_bytes = stream.read(MAX_INPUT_BYTES + 1)
    except OSError:
        return _file_rejected(
            source_relative_path=source_relative_path,
            failure_code=(
                ControlledImageFileExtractionFailureCode
                .SOURCE_FILE_READ_FAILED
            ),
        )

    if len(input_bytes) == 0:
        return _file_rejected(
            source_relative_path=source_relative_path,
            source_file_opened=True,
            failure_code=(
                ControlledImageFileExtractionFailureCode
                .SOURCE_FILE_EMPTY
            ),
        )
    if len(input_bytes) > MAX_INPUT_BYTES:
        return _file_rejected(
            source_relative_path=source_relative_path,
            source_file_opened=True,
            failure_code=(
                ControlledImageFileExtractionFailureCode
                .SOURCE_FILE_OVERSIZED
            ),
        )

    input_sha256 = hashlib.sha256(input_bytes).hexdigest()
    orchestration_result = run_controlled_image_extraction(
        official_source_payload=official_source_payload,
        presented_source_id=presented_source_id,
        presented_source_locator=presented_source_locator,
        input_bytes=input_bytes,
        declared_media_type=declared_media_type,
        declared_extension=declared_extension,
        artifact_root=artifact_root,
    )

    return ControlledImageFileExtractionRuntimeResult(
        runtime_version=(
            CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION
        ),
        status=(
            ControlledImageFileExtractionRuntimeStatus.ORCHESTRATED
        ),
        source_relative_path=source_relative_path,
        source_file_opened=True,
        input_sha256=input_sha256,
        input_byte_length=len(input_bytes),
        failure_code=None,
        orchestration_result=orchestration_result,
    )
