from __future__ import annotations

import ast
import dataclasses
import inspect

import pytest

from rie.extraction.image_extraction_artifact import (
    IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER,
    IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER,
    IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION,
    ImageExtractionArtifact,
    ImageExtractionArtifactContractError,
    ImageExtractionArtifactRejectionCode,
    ImageExtractionArtifactStatus,
    compute_image_extraction_artifact_id,
    image_extraction_artifact_identity_bytes,
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


def _rejected(**changes: object) -> ImageExtractionArtifact:
    values: dict[str, object] = {
        "official_image_source_id": "official-image-source:alpha",
        "input_sha256": SHA,
        "input_byte_length": 128,
        "declared_media_type": "image/png",
        "declared_extension": ".png",
        "parser_id": "rie.image_structure_parser",
        "parser_version": "1",
        "rejection_code":
            ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE,
    }
    values.update(changes)
    return ImageExtractionArtifact.rejected(**values)


def test_schema_and_field_orders_are_exact() -> None:
    assert IMAGE_EXTRACTION_ARTIFACT_SCHEMA_VERSION == (
        "image_extraction_artifact_v1"
    )
    assert tuple(
        field.name for field in dataclasses.fields(ImageExtractionArtifact)
    ) == IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER
    assert IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER == tuple(
        field for field in IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER
        if field != "artifact_id"
    )


@pytest.mark.parametrize(
    ("media_type", "extension", "detected_format"),
    (
        ("image/jpeg", ".jpg", "jpeg"),
        ("image/jpeg", ".jpeg", "jpeg"),
        ("image/png", ".png", "png"),
        ("image/webp", ".webp", "webp"),
    ),
)
def test_supported_success_artifacts(
    media_type: str,
    extension: str,
    detected_format: str,
) -> None:
    artifact = _success(
        declared_media_type=media_type,
        declared_extension=extension,
        detected_format=detected_format,
    )
    assert artifact.extraction_status is (
        ImageExtractionArtifactStatus.SUCCEEDED
    )
    assert artifact.rejection_code is None
    assert len(artifact.artifact_id) == 64


def test_artifact_is_frozen() -> None:
    artifact = _success()
    with pytest.raises(dataclasses.FrozenInstanceError):
        artifact.pixel_width = 9  # type: ignore[misc]


def test_identity_is_deterministic() -> None:
    first = _success()
    second = _success()
    assert first == second
    assert first.artifact_id == second.artifact_id


def test_identity_changes_when_contract_fact_changes() -> None:
    assert _success(pixel_width=16).artifact_id != (
        _success(pixel_width=17).artifact_id
    )


def test_identity_bytes_are_ascii_lf_only_and_stable() -> None:
    artifact = _success()
    values = {
        field: (
            getattr(artifact, field).value
            if isinstance(getattr(artifact, field), ImageExtractionArtifactStatus)
            else getattr(artifact, field)
        )
        for field in IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER
    }
    result = image_extraction_artifact_identity_bytes(values)
    assert result.isascii()
    assert b"\r" not in result
    assert result.endswith(b"\n")
    assert not result.endswith(b"\n\n")
    assert result == image_extraction_artifact_identity_bytes(values)


def test_direct_constructor_rejects_artifact_id_mismatch() -> None:
    artifact = _success()
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="artifact_id",
    ):
        dataclasses.replace(artifact, artifact_id="0" * 64)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("artifact_schema_version", "unknown"),
        ("input_sha256", "A" * 64),
        ("input_byte_length", 0),
        ("input_byte_length", True),
        ("official_image_source_id", ""),
        ("parser_id", ""),
        ("parser_version", ""),
    ),
)
def test_invalid_common_values_are_rejected(
    field: str,
    value: object,
) -> None:
    with pytest.raises((TypeError, ImageExtractionArtifactContractError)):
        _success(**{field: value})


def test_declared_media_type_and_extension_conflict_is_rejected() -> None:
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="extension conflict",
    ):
        _success(
            declared_media_type="image/png",
            declared_extension=".jpg",
            detected_format="jpeg",
        )


def test_declared_and_detected_format_conflict_is_rejected() -> None:
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="detected format conflict",
    ):
        _success(detected_format="jpeg")


@pytest.mark.parametrize(("width", "height"), ((0, 1), (1, 0), (-1, 1)))
def test_invalid_dimensions_are_rejected(width: int, height: int) -> None:
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="dimensions",
    ):
        _success(pixel_width=width, pixel_height=height)


def test_rejected_artifact_has_no_structural_facts() -> None:
    artifact = _rejected()
    assert artifact.extraction_status is (
        ImageExtractionArtifactStatus.REJECTED
    )
    assert artifact.detected_format is None
    assert artifact.pixel_width is None
    assert artifact.pixel_height is None
    assert artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE
    )


def test_rejected_artifact_requires_rejection_code() -> None:
    artifact = _rejected()
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="requires rejection_code",
    ):
        dataclasses.replace(artifact, rejection_code=None)


def test_successful_artifact_forbids_rejection_code() -> None:
    artifact = _success()
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="must not contain rejection_code",
    ):
        dataclasses.replace(
            artifact,
            rejection_code=(
                ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE
            ),
        )


def test_rejected_artifact_forbids_structural_facts() -> None:
    artifact = _rejected()
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="must not contain structural facts",
    ):
        dataclasses.replace(artifact, detected_format="png")


def test_identity_mapping_rejects_wrong_order() -> None:
    artifact = _success()
    reversed_values = {
        field: getattr(artifact, field)
        for field in reversed(
            IMAGE_EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER
        )
    }
    with pytest.raises(
        ImageExtractionArtifactContractError,
        match="field order",
    ):
        image_extraction_artifact_identity_bytes(reversed_values)


def test_compute_identity_matches_factory() -> None:
    artifact = _success()
    computed = compute_image_extraction_artifact_id(
        artifact_schema_version=artifact.artifact_schema_version,
        official_image_source_id=artifact.official_image_source_id,
        input_sha256=artifact.input_sha256,
        input_byte_length=artifact.input_byte_length,
        declared_media_type=artifact.declared_media_type,
        declared_extension=artifact.declared_extension,
        detected_format=artifact.detected_format,
        pixel_width=artifact.pixel_width,
        pixel_height=artifact.pixel_height,
        parser_id=artifact.parser_id,
        parser_version=artifact.parser_version,
        extraction_status=artifact.extraction_status,
        rejection_code=artifact.rejection_code,
    )
    assert computed == artifact.artifact_id


def test_module_has_no_filesystem_network_clock_random_or_model_dependency() -> None:
    import rie.extraction.image_extraction_artifact as module

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
            "os",
            "pathlib",
            "socket",
            "requests",
            "urllib",
            "time",
            "datetime",
            "random",
            "secrets",
            "uuid",
            "PIL",
            "cv2",
            "numpy",
            "torch",
            "tensorflow",
        }
    )
