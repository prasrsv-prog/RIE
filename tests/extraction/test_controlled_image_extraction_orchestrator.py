from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rie.extraction.controlled_image_extraction_orchestrator import (
    CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_RESULT_FIELD_ORDER,
    CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION,
    ControlledImageExtractionOrchestrationStatus,
    run_controlled_image_extraction,
)
from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifactRejectionCode,
    ImageExtractionArtifactStatus,
)
from rie.extraction.image_extraction_artifact_file_persistence import (
    ImageExtractionArtifactFileFailureCode,
    ImageExtractionArtifactFileWriteStatus,
    load_image_extraction_artifact_file,
)
from rie.extraction.image_structure_parser import (
    PARSER_ID,
    PARSER_VERSION,
    ImageStructureResult,
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
    encode_official_image_source,
)


PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x10"
    b"\x00\x00\x00\x08"
)
JPEG = (
    b"\xff\xd8"
    b"\xff\xc0\x00\x09"
    b"\x08\x00\x08\x00\x10\x01\x01"
)
WEBP = (
    b"RIFF"
    + (22).to_bytes(4, "little")
    + b"WEBP"
    + b"VP8 "
    + (10).to_bytes(4, "little")
    + b"\x00\x00\x00\x9d\x01\x2a"
    + (16).to_bytes(2, "little")
    + (8).to_bytes(2, "little")
)
LOCATOR = "repository://assets/controlled/image-001.png"


def _source(data: bytes = PNG, **changes: object) -> OfficialImageSource:
    values: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": LOCATOR,
        "source_kind": SourceKind.REPOSITORY_ASSET,
        "content_sha256": hashlib.sha256(data).hexdigest(),
        "byte_length": len(data),
        "authority_class": AuthorityClass.OFFICIAL_INTERNAL,
        "rights_status": RightsStatus.OWNED,
        "lifecycle_state": LifecycleState.ACTIVE,
        "admission_status": AdmissionStatus.ACCEPTED,
        "provenance_parent_id": None,
        "registered_at_utc": datetime(
            2026,
            7,
            30,
            5,
            0,
            tzinfo=timezone.utc,
        ),
        "registered_by": "operator-001",
    }
    values.update(changes)
    return OfficialImageSource(**values)  # type: ignore[arg-type]


def _run(
    root: Path,
    *,
    data: bytes = PNG,
    media_type: str = "image/png",
    extension: str = ".png",
    source: OfficialImageSource | None = None,
    payload: bytes | None | object = ...,
):
    if source is None:
        source = _source(data)
    if payload is ...:
        payload = encode_official_image_source(source)
    return run_controlled_image_extraction(
        official_source_payload=payload,  # type: ignore[arg-type]
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        input_bytes=data,
        declared_media_type=media_type,
        declared_extension=extension,
        artifact_root=root,
    )


def _parser_result(
    *,
    data: bytes = PNG,
    status: str = "ACCEPTED",
    image_format: str | None = "PNG",
    width: int | None = 16,
    height: int | None = 8,
    parser_id: str = PARSER_ID,
    parser_version: str = PARSER_VERSION,
    input_sha256: str | None = None,
    input_byte_length: int | None = None,
    rejection_reason: str | None = None,
) -> ImageStructureResult:
    return ImageStructureResult(
        status=status,
        image_format=image_format,
        width=width,
        height=height,
        parser_id=parser_id,
        parser_version=parser_version,
        input_sha256=(
            hashlib.sha256(data).hexdigest()
            if input_sha256 is None
            else input_sha256
        ),
        input_byte_length=(
            len(data)
            if input_byte_length is None
            else input_byte_length
        ),
        rejection_reason=rejection_reason,
    )


def test_version_and_result_order_are_exact() -> None:
    assert CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_VERSION == (
        "controlled_image_extraction_orchestration_v1"
    )
    assert CONTROLLED_IMAGE_EXTRACTION_ORCHESTRATION_RESULT_FIELD_ORDER == (
        "orchestration_version",
        "status",
        "source_validation",
        "parser_executed",
        "parser_result",
        "artifact",
        "persistence_result",
    )


def test_result_is_frozen(tmp_path: Path) -> None:
    result = _run(tmp_path)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = (  # type: ignore[misc]
            ControlledImageExtractionOrchestrationStatus.REJECTED
        )


@pytest.mark.parametrize(
    ("data", "media_type", "extension", "expected_format"),
    (
        (PNG, "image/png", ".png", "png"),
        (JPEG, "image/jpeg", ".jpg", "jpeg"),
        (WEBP, "image/webp", ".webp", "webp"),
    ),
)
def test_successful_supported_workflows(
    tmp_path: Path,
    data: bytes,
    media_type: str,
    extension: str,
    expected_format: str,
) -> None:
    result = _run(
        tmp_path,
        data=data,
        media_type=media_type,
        extension=extension,
    )
    assert result.status is (
        ControlledImageExtractionOrchestrationStatus.SUCCEEDED
    )
    assert result.parser_executed is True
    assert result.artifact.extraction_status is (
        ImageExtractionArtifactStatus.SUCCEEDED
    )
    assert result.artifact.detected_format == expected_format
    assert result.persistence_result.status is (
        ImageExtractionArtifactFileWriteStatus.WRITTEN
    )


def test_successful_artifact_has_exact_structural_facts(
    tmp_path: Path,
) -> None:
    result = _run(tmp_path)
    assert result.artifact.pixel_width == 16
    assert result.artifact.pixel_height == 8
    assert result.artifact.parser_id == PARSER_ID
    assert result.artifact.parser_version == PARSER_VERSION


def test_persisted_artifact_loads_back_exactly(tmp_path: Path) -> None:
    result = _run(tmp_path)
    loaded = load_image_extraction_artifact_file(
        tmp_path,
        result.artifact.artifact_id,
    )
    assert loaded.artifact == result.artifact


def test_repeated_workflow_is_idempotent(tmp_path: Path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)
    assert first.artifact == second.artifact
    assert second.persistence_result.status is (
        ImageExtractionArtifactFileWriteStatus.ALREADY_PRESENT
    )


def test_missing_source_rejects_without_parser(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    def forbidden(_: bytes) -> ImageStructureResult:
        raise AssertionError("parser must not execute")

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        forbidden,
    )
    result = _run(tmp_path, payload=None)
    assert result.parser_executed is False
    assert result.parser_result is None
    assert result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .OFFICIAL_IMAGE_SOURCE_MISSING
    )
    assert result.status is (
        ControlledImageExtractionOrchestrationStatus.REJECTED
    )


def test_rejected_source_artifact_is_persisted(tmp_path: Path) -> None:
    result = _run(tmp_path, payload=None)
    loaded = load_image_extraction_artifact_file(
        tmp_path,
        result.artifact.artifact_id,
    )
    assert loaded.artifact == result.artifact


@pytest.mark.parametrize(
    ("reason", "expected_code"),
    (
        (
            "TRUNCATED_PNG",
            ImageExtractionArtifactRejectionCode.MALFORMED_STRUCTURE,
        ),
        (
            "UNSUPPORTED_SIGNATURE",
            ImageExtractionArtifactRejectionCode.UNSUPPORTED_FORMAT,
        ),
        (
            "ZERO_DIMENSION",
            ImageExtractionArtifactRejectionCode.INVALID_DIMENSIONS,
        ),
        (
            "OVERSIZED_INPUT",
            ImageExtractionArtifactRejectionCode.RESOURCE_LIMIT_EXCEEDED,
        ),
        (
            "UNKNOWN_REASON",
            ImageExtractionArtifactRejectionCode
            .DETERMINISTIC_OUTPUT_UNPROVEN,
        ),
    ),
)
def test_parser_rejection_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    reason: str,
    expected_code: ImageExtractionArtifactRejectionCode,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            status="REJECTED",
            image_format=None,
            width=None,
            height=None,
            rejection_reason=reason,
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is expected_code
    assert result.status is (
        ControlledImageExtractionOrchestrationStatus.REJECTED
    )


def test_non_result_parser_is_contract_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda _: object(),
    )
    with pytest.raises(
        TypeError,
        match="non-ImageStructureResult",
    ):
        _run(tmp_path)


def test_detected_format_conflict_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            image_format="JPEG",
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode.DECLARED_FORMAT_CONFLICT
    )


@pytest.mark.parametrize(
    ("change", "expected_code"),
    (
        (
            {"parser_id": "unexpected"},
            ImageExtractionArtifactRejectionCode.PARSER_IDENTITY_MISMATCH,
        ),
        (
            {"parser_version": "unexpected"},
            ImageExtractionArtifactRejectionCode.PARSER_IDENTITY_MISMATCH,
        ),
        (
            {"input_sha256": "b" * 64},
            ImageExtractionArtifactRejectionCode
            .DETERMINISTIC_OUTPUT_UNPROVEN,
        ),
        (
            {"input_byte_length": len(PNG) + 1},
            ImageExtractionArtifactRejectionCode
            .DETERMINISTIC_OUTPUT_UNPROVEN,
        ),
        (
            {"status": "UNKNOWN"},
            ImageExtractionArtifactRejectionCode
            .DETERMINISTIC_OUTPUT_UNPROVEN,
        ),
    ),
)
def test_parser_contract_mismatch_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, object],
    expected_code: ImageExtractionArtifactRejectionCode,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            **change,  # type: ignore[arg-type]
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is expected_code


def test_rejected_parser_with_dimensions_is_unproven(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            status="REJECTED",
            rejection_reason="MALFORMED_PNG",
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .DETERMINISTIC_OUTPUT_UNPROVEN
    )


def test_accepted_parser_with_rejection_reason_is_unproven(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            rejection_reason="IMPOSSIBLE_ACCEPTED_REASON",
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .DETERMINISTIC_OUTPUT_UNPROVEN
    )


def test_invalid_dimensions_are_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        lambda data: _parser_result(
            data=data,
            width=0,
        ),
    )
    result = _run(tmp_path)
    assert result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode.INVALID_DIMENSIONS
    )


def test_persistence_failure_is_propagated(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    result = _run(missing)
    assert result.status is (
        ControlledImageExtractionOrchestrationStatus.PERSISTENCE_FAILED
    )
    assert result.persistence_result.failure_code is (
        ImageExtractionArtifactFileFailureCode.ROOT_NOT_FOUND
    )


def test_parser_executes_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

    calls = 0

    def one_call(data: bytes) -> ImageStructureResult:
        nonlocal calls
        calls += 1
        return _parser_result(data=data)

    monkeypatch.setattr(
        module,
        "inspect_image_structure_bytes",
        one_call,
    )
    _run(tmp_path)
    assert calls == 1


def test_identical_inputs_are_deterministic(tmp_path: Path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)
    assert first.source_validation == second.source_validation
    assert first.parser_result == second.parser_result
    assert first.artifact == second.artifact


@pytest.mark.parametrize(
    ("media_type", "extension"),
    (
        ("image/jpeg", ".png"),
        ("image/png", ".gif"),
        ("image/gif", ".gif"),
    ),
)
def test_incoherent_declaration_is_programmer_error(
    tmp_path: Path,
    media_type: str,
    extension: str,
) -> None:
    with pytest.raises(ValueError, match="coherent supported"):
        _run(
            tmp_path,
            media_type=media_type,
            extension=extension,
        )


def test_artifact_root_requires_path() -> None:
    source = _source()
    with pytest.raises(TypeError, match="pathlib.Path"):
        run_controlled_image_extraction(
            official_source_payload=encode_official_image_source(source),
            presented_source_id=source.source_id,
            presented_source_locator=source.source_locator,
            input_bytes=PNG,
            declared_media_type="image/png",
            declared_extension=".png",
            artifact_root="root",  # type: ignore[arg-type]
        )


def test_module_has_no_registry_cli_network_decoder_ocr_semantic_or_model_dependency() -> None:
    import rie.extraction.controlled_image_extraction_orchestrator as module

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
            "argparse",
            "click",
            "typer",
            "socket",
            "requests",
            "urllib",
            "PIL",
            "cv2",
            "numpy",
            "pytesseract",
            "torch",
            "tensorflow",
            "transformers",
        }
    )
    forbidden_text = (
        "registry",
        "scan",
        "glob",
        "rglob",
        "read_bytes",
        "read_text",
    )
    assert all(token not in source.lower() for token in forbidden_text)
