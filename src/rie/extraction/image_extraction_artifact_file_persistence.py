"""Bounded filesystem persistence for Gate 13 image extraction artifacts."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifact,
)
from rie.extraction.image_extraction_artifact_persistence import (
    IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES,
    ImageExtractionArtifactPersistenceError,
    canonical_image_extraction_artifact_payload,
    deserialize_image_extraction_artifact,
)


IMAGE_EXTRACTION_ARTIFACT_FILE_SUFFIX: Final = (
    ".image-extraction-artifact.json"
)
IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX: Final = ".tmp"
_LOWER_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


class ImageExtractionArtifactFileWriteStatus(str, Enum):
    WRITTEN = "written"
    ALREADY_PRESENT = "already_present"
    REJECTED = "rejected"


class ImageExtractionArtifactFileReadStatus(str, Enum):
    LOADED = "loaded"
    REJECTED = "rejected"


class ImageExtractionArtifactFileFailureCode(str, Enum):
    ROOT_NOT_ABSOLUTE = "root_not_absolute"
    ROOT_NOT_FOUND = "root_not_found"
    ROOT_NOT_DIRECTORY = "root_not_directory"
    ROOT_SYMLINK_FORBIDDEN = "root_symlink_forbidden"
    TARGET_NOT_REGULAR_FILE = "target_not_regular_file"
    TEMPORARY_PATH_OCCUPIED = "temporary_path_occupied"
    EXISTING_FILE_INVALID = "existing_file_invalid"
    EXISTING_FILE_MISMATCH = "existing_file_mismatch"
    WRITE_FAILED = "write_failed"
    WRITE_VERIFICATION_FAILED = "write_verification_failed"
    ATOMIC_PUBLISH_FAILED = "atomic_publish_failed"
    TEMPORARY_CLEANUP_FAILED = "temporary_cleanup_failed"
    READ_BACK_FAILED = "read_back_failed"
    READ_BACK_MISMATCH = "read_back_mismatch"
    FILE_NOT_FOUND = "file_not_found"
    READ_FAILED = "read_failed"
    INVALID_ARTIFACT_FILE = "invalid_artifact_file"
    ARTIFACT_ID_MISMATCH = "artifact_id_mismatch"


@dataclass(frozen=True)
class ImageExtractionArtifactFileWriteResult:
    status: ImageExtractionArtifactFileWriteStatus
    artifact_id: str
    relative_filename: str
    serialized_sha256: str | None
    serialized_byte_length: int | None
    failure_code: ImageExtractionArtifactFileFailureCode | None
    rollback_performed: bool

    def __post_init__(self) -> None:
        _require_artifact_id(self.artifact_id)
        expected_filename = image_extraction_artifact_filename(
            self.artifact_id
        )
        if self.relative_filename != expected_filename:
            raise ValueError("relative_filename does not match artifact_id.")
        if type(self.rollback_performed) is not bool:
            raise TypeError("rollback_performed must be exact bool.")

        if self.status is ImageExtractionArtifactFileWriteStatus.REJECTED:
            if self.failure_code is None:
                raise ValueError("rejected write result requires failure_code.")
        else:
            if self.failure_code is not None:
                raise ValueError(
                    "successful write result must not contain failure_code."
                )
            _require_serialized_metadata(
                self.serialized_sha256,
                self.serialized_byte_length,
            )


@dataclass(frozen=True)
class ImageExtractionArtifactFileReadResult:
    status: ImageExtractionArtifactFileReadStatus
    artifact_id: str
    relative_filename: str
    artifact: ImageExtractionArtifact | None
    serialized_sha256: str | None
    serialized_byte_length: int | None
    failure_code: ImageExtractionArtifactFileFailureCode | None

    def __post_init__(self) -> None:
        _require_artifact_id(self.artifact_id)
        expected_filename = image_extraction_artifact_filename(
            self.artifact_id
        )
        if self.relative_filename != expected_filename:
            raise ValueError("relative_filename does not match artifact_id.")

        if self.status is ImageExtractionArtifactFileReadStatus.REJECTED:
            if self.failure_code is None:
                raise ValueError("rejected read result requires failure_code.")
            if self.artifact is not None:
                raise ValueError(
                    "rejected read result must not contain artifact."
                )
        else:
            if self.failure_code is not None:
                raise ValueError(
                    "successful read result must not contain failure_code."
                )
            if type(self.artifact) is not ImageExtractionArtifact:
                raise TypeError(
                    "loaded read result requires exact artifact."
                )
            if self.artifact.artifact_id != self.artifact_id:
                raise ValueError("loaded artifact_id does not match request.")
            _require_serialized_metadata(
                self.serialized_sha256,
                self.serialized_byte_length,
            )


def _require_artifact_id(artifact_id: object) -> str:
    if type(artifact_id) is not str:
        raise TypeError("artifact_id must be an exact string.")
    if _LOWER_HEX_64.fullmatch(artifact_id) is None:
        raise ValueError(
            "artifact_id must contain exactly 64 lowercase hex characters."
        )
    return artifact_id


def _require_serialized_metadata(
    serialized_sha256: object,
    serialized_byte_length: object,
) -> None:
    if type(serialized_sha256) is not str:
        raise TypeError("serialized_sha256 must be an exact string.")
    if _LOWER_HEX_64.fullmatch(serialized_sha256) is None:
        raise ValueError("serialized_sha256 must be lowercase SHA-256.")
    if type(serialized_byte_length) is not int:
        raise TypeError(
            "serialized_byte_length must be an exact integer."
        )
    if not (
        0 < serialized_byte_length <=
        IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES
    ):
        raise ValueError(
            "serialized_byte_length is outside persistence boundaries."
        )


def image_extraction_artifact_filename(artifact_id: str) -> str:
    _require_artifact_id(artifact_id)
    return artifact_id + IMAGE_EXTRACTION_ARTIFACT_FILE_SUFFIX


def _temporary_filename(artifact_id: str) -> str:
    return (
        image_extraction_artifact_filename(artifact_id)
        + IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX
    )


def _validate_root(
    root: Path,
) -> tuple[Path | None, ImageExtractionArtifactFileFailureCode | None]:
    if not isinstance(root, Path):
        raise TypeError("root must be a pathlib.Path.")
    if not root.is_absolute():
        return (
            None,
            ImageExtractionArtifactFileFailureCode.ROOT_NOT_ABSOLUTE,
        )
    if root.is_symlink():
        return (
            None,
            ImageExtractionArtifactFileFailureCode.ROOT_SYMLINK_FORBIDDEN,
        )
    if not root.exists():
        return (
            None,
            ImageExtractionArtifactFileFailureCode.ROOT_NOT_FOUND,
        )
    if not root.is_dir():
        return (
            None,
            ImageExtractionArtifactFileFailureCode.ROOT_NOT_DIRECTORY,
        )
    try:
        return (root.resolve(strict=True), None)
    except OSError:
        return (
            None,
            ImageExtractionArtifactFileFailureCode.ROOT_NOT_FOUND,
        )


def _write_rejected(
    artifact_id: str,
    failure_code: ImageExtractionArtifactFileFailureCode,
    *,
    rollback_performed: bool = False,
) -> ImageExtractionArtifactFileWriteResult:
    return ImageExtractionArtifactFileWriteResult(
        status=ImageExtractionArtifactFileWriteStatus.REJECTED,
        artifact_id=artifact_id,
        relative_filename=image_extraction_artifact_filename(artifact_id),
        serialized_sha256=None,
        serialized_byte_length=None,
        failure_code=failure_code,
        rollback_performed=rollback_performed,
    )


def _read_rejected(
    artifact_id: str,
    failure_code: ImageExtractionArtifactFileFailureCode,
) -> ImageExtractionArtifactFileReadResult:
    return ImageExtractionArtifactFileReadResult(
        status=ImageExtractionArtifactFileReadStatus.REJECTED,
        artifact_id=artifact_id,
        relative_filename=image_extraction_artifact_filename(artifact_id),
        artifact=None,
        serialized_sha256=None,
        serialized_byte_length=None,
        failure_code=failure_code,
    )


def _read_bounded_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        payload = stream.read(
            IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES + 1
        )
    if len(payload) > IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES:
        raise ImageExtractionArtifactPersistenceError(
            "artifact file exceeds serialized byte boundary."
        )
    return payload


def _inspect_existing(
    target: Path,
    artifact: ImageExtractionArtifact,
    expected_payload: bytes,
    expected_sha256: str,
    expected_byte_length: int,
) -> ImageExtractionArtifactFileWriteResult:
    if target.is_symlink() or not target.is_file():
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.TARGET_NOT_REGULAR_FILE,
        )

    try:
        existing_payload = _read_bounded_bytes(target)
        existing_artifact = deserialize_image_extraction_artifact(
            existing_payload
        )
    except (OSError, ImageExtractionArtifactPersistenceError):
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.EXISTING_FILE_INVALID,
        )

    if (
        existing_payload != expected_payload
        or existing_artifact != artifact
    ):
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.EXISTING_FILE_MISMATCH,
        )

    return ImageExtractionArtifactFileWriteResult(
        status=(
            ImageExtractionArtifactFileWriteStatus.ALREADY_PRESENT
        ),
        artifact_id=artifact.artifact_id,
        relative_filename=image_extraction_artifact_filename(
            artifact.artifact_id
        ),
        serialized_sha256=expected_sha256,
        serialized_byte_length=expected_byte_length,
        failure_code=None,
        rollback_performed=False,
    )


def persist_image_extraction_artifact_file(
    root: Path,
    artifact: ImageExtractionArtifact,
) -> ImageExtractionArtifactFileWriteResult:
    if type(artifact) is not ImageExtractionArtifact:
        raise TypeError(
            "artifact must be exact ImageExtractionArtifact."
        )

    canonical = canonical_image_extraction_artifact_payload(artifact)
    validated_root, root_failure = _validate_root(root)
    if root_failure is not None:
        return _write_rejected(artifact.artifact_id, root_failure)
    if validated_root is None:
        raise RuntimeError("validated root state is invalid.")

    target = validated_root / image_extraction_artifact_filename(
        artifact.artifact_id
    )
    temporary = validated_root / _temporary_filename(
        artifact.artifact_id
    )

    if target.exists() or target.is_symlink():
        return _inspect_existing(
            target,
            artifact,
            canonical.payload,
            canonical.serialized_sha256,
            canonical.serialized_byte_length,
        )

    if temporary.exists() or temporary.is_symlink():
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.TEMPORARY_PATH_OCCUPIED,
        )

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    try:
        descriptor = os.open(temporary, flags, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            written = stream.write(canonical.payload)
            stream.flush()
            os.fsync(stream.fileno())
        if written != canonical.serialized_byte_length:
            raise OSError("short artifact persistence write")
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.WRITE_FAILED,
        )

    try:
        temporary_payload = _read_bounded_bytes(temporary)
        temporary_artifact = deserialize_image_extraction_artifact(
            temporary_payload
        )
        if (
            temporary_payload != canonical.payload
            or temporary_artifact != artifact
        ):
            raise ImageExtractionArtifactPersistenceError(
                "temporary artifact verification mismatch."
            )
    except (OSError, ImageExtractionArtifactPersistenceError):
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.WRITE_VERIFICATION_FAILED,
        )

    try:
        os.link(temporary, target)
    except FileExistsError:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            return _write_rejected(
                artifact.artifact_id,
                ImageExtractionArtifactFileFailureCode.TEMPORARY_CLEANUP_FAILED,
            )
        return _inspect_existing(
            target,
            artifact,
            canonical.payload,
            canonical.serialized_sha256,
            canonical.serialized_byte_length,
        )
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.ATOMIC_PUBLISH_FAILED,
        )

    try:
        temporary.unlink()
    except OSError:
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.TEMPORARY_CLEANUP_FAILED,
        )

    try:
        read_back = _read_bounded_bytes(target)
        restored = deserialize_image_extraction_artifact(read_back)
    except (OSError, ImageExtractionArtifactPersistenceError):
        rollback = False
        try:
            target.unlink()
            rollback = True
        except OSError:
            pass
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.READ_BACK_FAILED,
            rollback_performed=rollback,
        )

    if read_back != canonical.payload or restored != artifact:
        rollback = False
        try:
            target.unlink()
            rollback = True
        except OSError:
            pass
        return _write_rejected(
            artifact.artifact_id,
            ImageExtractionArtifactFileFailureCode.READ_BACK_MISMATCH,
            rollback_performed=rollback,
        )

    return ImageExtractionArtifactFileWriteResult(
        status=ImageExtractionArtifactFileWriteStatus.WRITTEN,
        artifact_id=artifact.artifact_id,
        relative_filename=image_extraction_artifact_filename(
            artifact.artifact_id
        ),
        serialized_sha256=canonical.serialized_sha256,
        serialized_byte_length=canonical.serialized_byte_length,
        failure_code=None,
        rollback_performed=False,
    )


def load_image_extraction_artifact_file(
    root: Path,
    artifact_id: str,
) -> ImageExtractionArtifactFileReadResult:
    artifact_id = _require_artifact_id(artifact_id)
    validated_root, root_failure = _validate_root(root)
    if root_failure is not None:
        return _read_rejected(artifact_id, root_failure)
    if validated_root is None:
        raise RuntimeError("validated root state is invalid.")

    target = validated_root / image_extraction_artifact_filename(
        artifact_id
    )

    if not target.exists() and not target.is_symlink():
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.FILE_NOT_FOUND,
        )
    if target.is_symlink() or not target.is_file():
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.TARGET_NOT_REGULAR_FILE,
        )

    try:
        payload = _read_bounded_bytes(target)
    except OSError:
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.READ_FAILED,
        )
    except ImageExtractionArtifactPersistenceError:
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.INVALID_ARTIFACT_FILE,
        )

    try:
        artifact = deserialize_image_extraction_artifact(payload)
    except ImageExtractionArtifactPersistenceError:
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.INVALID_ARTIFACT_FILE,
        )

    if artifact.artifact_id != artifact_id:
        return _read_rejected(
            artifact_id,
            ImageExtractionArtifactFileFailureCode.ARTIFACT_ID_MISMATCH,
        )

    return ImageExtractionArtifactFileReadResult(
        status=ImageExtractionArtifactFileReadStatus.LOADED,
        artifact_id=artifact_id,
        relative_filename=image_extraction_artifact_filename(artifact_id),
        artifact=artifact,
        serialized_sha256=hashlib.sha256(payload).hexdigest(),
        serialized_byte_length=len(payload),
        failure_code=None,
    )
