from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
from pathlib import Path

import pytest

from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifact,
    ImageExtractionArtifactRejectionCode,
)
from rie.extraction.image_extraction_artifact_file_persistence import (
    IMAGE_EXTRACTION_ARTIFACT_FILE_SUFFIX,
    IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX,
    ImageExtractionArtifactFileFailureCode,
    ImageExtractionArtifactFileReadStatus,
    ImageExtractionArtifactFileWriteStatus,
    image_extraction_artifact_filename,
    load_image_extraction_artifact_file,
    persist_image_extraction_artifact_file,
)
from rie.extraction.image_extraction_artifact_persistence import (
    IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES,
    canonical_image_extraction_artifact_payload,
    serialize_image_extraction_artifact,
)


SHA = "a" * 64


def _success(**changes: object) -> ImageExtractionArtifact:
    values: dict[str, object] = {
        "official_image_source_id": "official-image-source:alpha",
        "input_sha256": SHA,
        "input_byte_length": 128,
        "declared_media_type": "image/png",
        "declared_extension": ".png",
        "detected_format": "png",
        "pixel_width": 16,
        "pixel_height": 8,
        "parser_id": "rie.image_structure_parser",
        "parser_version": "1",
    }
    values.update(changes)
    return ImageExtractionArtifact.succeeded(**values)


def _rejected() -> ImageExtractionArtifact:
    return ImageExtractionArtifact.rejected(
        official_image_source_id="official-image-source:alpha",
        input_sha256=SHA,
        input_byte_length=128,
        declared_media_type="image/png",
        declared_extension=".png",
        parser_id="rie.image_structure_parser",
        parser_version="1",
        rejection_code=(
            ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE
        ),
    )


def test_filename_contract_is_exact() -> None:
    assert IMAGE_EXTRACTION_ARTIFACT_FILE_SUFFIX == (
        ".image-extraction-artifact.json"
    )
    assert IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX == ".tmp"
    assert image_extraction_artifact_filename(SHA) == (
        SHA + ".image-extraction-artifact.json"
    )


@pytest.mark.parametrize(
    "artifact_id",
    ("", "A" * 64, "a" * 63, "g" * 64),
)
def test_filename_rejects_invalid_artifact_id(
    artifact_id: str,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        image_extraction_artifact_filename(artifact_id)


def test_persist_writes_exact_canonical_bytes(tmp_path: Path) -> None:
    artifact = _success()
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    target = tmp_path / result.relative_filename
    assert result.status is ImageExtractionArtifactFileWriteStatus.WRITTEN
    assert target.read_bytes() == serialize_image_extraction_artifact(
        artifact
    )


def test_persist_result_metadata_is_exact(tmp_path: Path) -> None:
    artifact = _success()
    canonical = canonical_image_extraction_artifact_payload(artifact)
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert result.serialized_sha256 == canonical.serialized_sha256
    assert (
        result.serialized_byte_length
        == canonical.serialized_byte_length
    )
    assert result.failure_code is None
    assert result.rollback_performed is False


def test_write_result_is_frozen(tmp_path: Path) -> None:
    result = persist_image_extraction_artifact_file(
        tmp_path,
        _success(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.rollback_performed = True  # type: ignore[misc]


def test_load_returns_exact_artifact_and_metadata(tmp_path: Path) -> None:
    artifact = _success()
    write_result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    read_result = load_image_extraction_artifact_file(
        tmp_path,
        artifact.artifact_id,
    )
    target = tmp_path / write_result.relative_filename
    payload = target.read_bytes()
    assert read_result.status is ImageExtractionArtifactFileReadStatus.LOADED
    assert read_result.artifact == artifact
    assert read_result.serialized_sha256 == hashlib.sha256(
        payload
    ).hexdigest()
    assert read_result.serialized_byte_length == len(payload)


def test_read_result_is_frozen(tmp_path: Path) -> None:
    artifact = _success()
    persist_image_extraction_artifact_file(tmp_path, artifact)
    result = load_image_extraction_artifact_file(
        tmp_path,
        artifact.artifact_id,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.artifact = None  # type: ignore[misc]


@pytest.mark.parametrize("artifact", (_success(), _rejected()))
def test_write_read_round_trip(
    tmp_path: Path,
    artifact: ImageExtractionArtifact,
) -> None:
    written = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    loaded = load_image_extraction_artifact_file(
        tmp_path,
        artifact.artifact_id,
    )
    assert written.status is ImageExtractionArtifactFileWriteStatus.WRITTEN
    assert loaded.artifact == artifact


def test_idempotent_existing_exact_file(tmp_path: Path) -> None:
    artifact = _success()
    first = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    second = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert first.status is ImageExtractionArtifactFileWriteStatus.WRITTEN
    assert second.status is (
        ImageExtractionArtifactFileWriteStatus.ALREADY_PRESENT
    )
    assert first.serialized_sha256 == second.serialized_sha256


def test_existing_valid_mismatch_is_not_overwritten(
    tmp_path: Path,
) -> None:
    artifact = _success()
    other = _success(pixel_width=17)
    target = tmp_path / image_extraction_artifact_filename(
        artifact.artifact_id
    )
    other_payload = serialize_image_extraction_artifact(other)
    target.write_bytes(other_payload)
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.EXISTING_FILE_MISMATCH
    )
    assert target.read_bytes() == other_payload


def test_existing_invalid_file_is_not_overwritten(
    tmp_path: Path,
) -> None:
    artifact = _success()
    target = tmp_path / image_extraction_artifact_filename(
        artifact.artifact_id
    )
    target.write_bytes(b"invalid\n")
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.EXISTING_FILE_INVALID
    )
    assert target.read_bytes() == b"invalid\n"


def test_relative_root_is_rejected_without_creation() -> None:
    artifact = _success()
    root = Path("relative-artifact-root")
    result = persist_image_extraction_artifact_file(root, artifact)
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.ROOT_NOT_ABSOLUTE
    )
    assert not root.exists()


def test_missing_root_is_rejected(tmp_path: Path) -> None:
    artifact = _success()
    root = tmp_path / "missing"
    result = persist_image_extraction_artifact_file(root, artifact)
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.ROOT_NOT_FOUND
    )
    assert not root.exists()


def test_root_file_is_rejected(tmp_path: Path) -> None:
    artifact = _success()
    root = tmp_path / "not-directory"
    root.write_bytes(b"x")
    result = persist_image_extraction_artifact_file(root, artifact)
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.ROOT_NOT_DIRECTORY
    )


def test_target_directory_is_rejected(tmp_path: Path) -> None:
    artifact = _success()
    target = tmp_path / image_extraction_artifact_filename(
        artifact.artifact_id
    )
    target.mkdir()
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.TARGET_NOT_REGULAR_FILE
    )


def test_temporary_path_occupied_is_rejected(
    tmp_path: Path,
) -> None:
    artifact = _success()
    temporary = tmp_path / (
        image_extraction_artifact_filename(artifact.artifact_id)
        + IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX
    )
    temporary.write_bytes(b"occupied")
    result = persist_image_extraction_artifact_file(
        tmp_path,
        artifact,
    )
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.TEMPORARY_PATH_OCCUPIED
    )
    assert temporary.read_bytes() == b"occupied"


def test_successful_write_removes_temporary_path(
    tmp_path: Path,
) -> None:
    artifact = _success()
    persist_image_extraction_artifact_file(tmp_path, artifact)
    temporary = tmp_path / (
        image_extraction_artifact_filename(artifact.artifact_id)
        + IMAGE_EXTRACTION_ARTIFACT_TEMP_SUFFIX
    )
    assert not temporary.exists()


def test_load_missing_file_returns_controlled_rejection(
    tmp_path: Path,
) -> None:
    result = load_image_extraction_artifact_file(tmp_path, SHA)
    assert result.status is ImageExtractionArtifactFileReadStatus.REJECTED
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.FILE_NOT_FOUND
    )
    assert result.artifact is None


def test_load_invalid_file_returns_controlled_rejection(
    tmp_path: Path,
) -> None:
    target = tmp_path / image_extraction_artifact_filename(SHA)
    target.write_bytes(b"invalid\n")
    result = load_image_extraction_artifact_file(tmp_path, SHA)
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.INVALID_ARTIFACT_FILE
    )


def test_load_oversized_file_returns_controlled_rejection(
    tmp_path: Path,
) -> None:
    target = tmp_path / image_extraction_artifact_filename(SHA)
    target.write_bytes(
        b"x" * (IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES + 1)
    )
    result = load_image_extraction_artifact_file(tmp_path, SHA)
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.INVALID_ARTIFACT_FILE
    )


def test_load_artifact_id_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    artifact = _success()
    requested_id = "b" * 64
    target = tmp_path / image_extraction_artifact_filename(requested_id)
    target.write_bytes(serialize_image_extraction_artifact(artifact))
    result = load_image_extraction_artifact_file(
        tmp_path,
        requested_id,
    )
    assert result.failure_code is (
        ImageExtractionArtifactFileFailureCode.ARTIFACT_ID_MISMATCH
    )


def test_persist_requires_exact_artifact(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="exact ImageExtractionArtifact"):
        persist_image_extraction_artifact_file(
            tmp_path,
            object(),  # type: ignore[arg-type]
        )


def test_root_requires_path_type() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        persist_image_extraction_artifact_file(
            "root",  # type: ignore[arg-type]
            _success(),
        )


def test_load_requires_exact_artifact_id(tmp_path: Path) -> None:
    with pytest.raises((TypeError, ValueError)):
        load_image_extraction_artifact_file(
            tmp_path,
            "A" * 64,
        )


def test_service_does_not_create_nested_directories(
    tmp_path: Path,
) -> None:
    artifact = _success()
    before = tuple(tmp_path.iterdir())
    persist_image_extraction_artifact_file(tmp_path, artifact)
    after = tuple(tmp_path.iterdir())
    assert before == ()
    assert len(after) == 1
    assert after[0].is_file()


def test_service_module_has_no_network_clock_random_decoder_or_model_dependency() -> None:
    import rie.extraction.image_extraction_artifact_file_persistence as module

    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported.isdisjoint(
        {
            "socket",
            "requests",
            "urllib",
            "time",
            "datetime",
            "random",
            "secrets",
            "uuid",
            "tempfile",
            "PIL",
            "cv2",
            "numpy",
            "torch",
            "tensorflow",
        }
    )
