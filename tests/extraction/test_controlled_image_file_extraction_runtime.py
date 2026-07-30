from __future__ import annotations

import ast
import builtins
import dataclasses
import hashlib
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

import rie.extraction.controlled_image_file_extraction_runtime as runtime_module
from rie.extraction.controlled_image_extraction_orchestrator import (
    ControlledImageExtractionOrchestrationStatus,
)
from rie.extraction.controlled_image_file_extraction_runtime import (
    CONTROLLED_IMAGE_FILE_EXTRACTION_RESULT_FIELD_ORDER,
    CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION,
    ControlledImageFileExtractionFailureCode,
    ControlledImageFileExtractionRuntimeStatus,
    run_controlled_image_file_extraction,
)
from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifactRejectionCode,
    ImageExtractionArtifactStatus,
)
from rie.extraction.image_structure_parser import MAX_INPUT_BYTES
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


def _write(
    source_root: Path,
    relative_path: str,
    data: bytes = PNG,
) -> Path:
    path = source_root.joinpath(*relative_path.split("/"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _run(
    tmp_path: Path,
    *,
    data: bytes = PNG,
    relative_path: str = "nested/image-001.png",
    source: OfficialImageSource | None = None,
    **changes: object,
):
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    _write(source_root, relative_path, data)
    if source is None:
        source = _source(data)
    values: dict[str, object] = {
        "official_source_payload": encode_official_image_source(source),
        "presented_source_id": source.source_id,
        "presented_source_locator": source.source_locator,
        "source_root": source_root,
        "source_relative_path": relative_path,
        "declared_media_type": "image/png",
        "declared_extension": ".png",
        "artifact_root": artifact_root,
    }
    values.update(changes)
    return run_controlled_image_file_extraction(
        **values  # type: ignore[arg-type]
    )


def test_version_and_result_field_order_are_exact() -> None:
    assert CONTROLLED_IMAGE_FILE_EXTRACTION_RUNTIME_VERSION == (
        "controlled_image_file_extraction_runtime_v1"
    )
    assert CONTROLLED_IMAGE_FILE_EXTRACTION_RESULT_FIELD_ORDER == (
        "runtime_version",
        "status",
        "source_relative_path",
        "source_file_opened",
        "input_sha256",
        "input_byte_length",
        "failure_code",
        "orchestration_result",
    )


def test_successful_file_runtime_orchestrates_and_persists(
    tmp_path: Path,
) -> None:
    result = _run(tmp_path)
    assert result.status is (
        ControlledImageFileExtractionRuntimeStatus.ORCHESTRATED
    )
    assert result.failure_code is None
    assert result.source_file_opened is True
    assert result.orchestration_result is not None
    assert result.orchestration_result.status is (
        ControlledImageExtractionOrchestrationStatus.SUCCEEDED
    )
    assert result.orchestration_result.artifact.extraction_status is (
        ImageExtractionArtifactStatus.SUCCEEDED
    )


def test_result_contains_exact_file_fingerprint_and_length(
    tmp_path: Path,
) -> None:
    result = _run(tmp_path)
    assert result.input_sha256 == hashlib.sha256(PNG).hexdigest()
    assert result.input_byte_length == len(PNG)


def test_nested_relative_path_is_supported(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        relative_path="one/two/three/image.png",
    )
    assert result.source_relative_path == "one/two/three/image.png"
    assert result.status is (
        ControlledImageFileExtractionRuntimeStatus.ORCHESTRATED
    )


def test_source_rejection_is_persisted_without_parser_execution(
    tmp_path: Path,
) -> None:
    source = _source(content_sha256="b" * 64)
    result = _run(tmp_path, source=source)
    assert result.orchestration_result is not None
    assert result.orchestration_result.status is (
        ControlledImageExtractionOrchestrationStatus.REJECTED
    )
    assert result.orchestration_result.parser_executed is False
    assert result.orchestration_result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode.INPUT_SHA256_MISMATCH
    )


def test_parser_rejection_is_persisted(tmp_path: Path) -> None:
    data = b"not-an-image"
    source = _source(data)
    result = _run(
        tmp_path,
        data=data,
        source=source,
        relative_path="synthetic.bin",
        declared_media_type="image/png",
        declared_extension=".png",
    )
    assert result.orchestration_result is not None
    assert result.orchestration_result.parser_executed is True
    assert result.orchestration_result.status is (
        ControlledImageExtractionOrchestrationStatus.REJECTED
    )
    assert result.orchestration_result.artifact.rejection_code is (
        ImageExtractionArtifactRejectionCode.UNSUPPORTED_FORMAT
    )


def test_missing_artifact_root_propagates_persistence_failure(
    tmp_path: Path,
) -> None:
    missing_artifact_root = tmp_path / "missing-artifacts"
    result = _run(
        tmp_path,
        artifact_root=missing_artifact_root,
    )
    assert result.orchestration_result is not None
    assert result.orchestration_result.status is (
        ControlledImageExtractionOrchestrationStatus.PERSISTENCE_FAILED
    )


def test_repeated_identical_file_is_idempotent(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    _write(source_root, "image.png")
    source = _source()
    values = {
        "official_source_payload": encode_official_image_source(source),
        "presented_source_id": source.source_id,
        "presented_source_locator": source.source_locator,
        "source_root": source_root,
        "source_relative_path": "image.png",
        "declared_media_type": "image/png",
        "declared_extension": ".png",
        "artifact_root": artifact_root,
    }
    first = run_controlled_image_file_extraction(**values)
    second = run_controlled_image_file_extraction(**values)
    assert first.orchestration_result is not None
    assert second.orchestration_result is not None
    assert first.orchestration_result.artifact == (
        second.orchestration_result.artifact
    )
    assert second.orchestration_result.persistence_result.status.value == (
        "already_present"
    )


def test_source_file_is_opened_once_and_read_with_limit_plus_sentinel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    path = _write(source_root, "image.png")
    source = _source()
    real_open = builtins.open
    open_paths: list[Path] = []
    read_sizes: list[int] = []

    class TrackingReader:
        def __init__(self, stream: object) -> None:
            self._stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            self._stream.close()  # type: ignore[attr-defined]

        def read(self, size: int = -1) -> bytes:
            read_sizes.append(size)
            return self._stream.read(size)  # type: ignore[attr-defined]

    def tracking_open(value: object, mode: str):
        open_paths.append(Path(value))
        return TrackingReader(real_open(value, mode))

    monkeypatch.setattr(builtins, "open", tracking_open)
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.status is (
        ControlledImageFileExtractionRuntimeStatus.ORCHESTRATED
    )
    assert open_paths == [path.resolve()]
    assert read_sizes == [MAX_INPUT_BYTES + 1]


def test_runtime_passes_exact_read_bytes_to_orchestration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[bytes] = []
    real = runtime_module.run_controlled_image_extraction

    def capture(**kwargs: object):
        captured.append(kwargs["input_bytes"])  # type: ignore[arg-type]
        return real(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(
        runtime_module,
        "run_controlled_image_extraction",
        capture,
    )
    _run(tmp_path)
    assert captured == [PNG]


def test_empty_file_is_controlled_rejection(tmp_path: Path) -> None:
    result = _run(tmp_path, data=b"", source=_source(PNG))
    assert result.status is (
        ControlledImageFileExtractionRuntimeStatus.FILE_REJECTED
    )
    assert result.source_file_opened is True
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_FILE_EMPTY
    )
    assert result.orchestration_result is None


def test_oversized_file_is_controlled_rejection(
    tmp_path: Path,
) -> None:
    data = b"x" * (MAX_INPUT_BYTES + 2)
    result = _run(tmp_path, data=data, source=_source(PNG))
    assert result.source_file_opened is True
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_FILE_OVERSIZED
    )
    assert result.orchestration_result is None


def test_oversized_file_does_not_invoke_orchestration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def forbidden(**kwargs: object):
        nonlocal calls
        calls += 1
        raise AssertionError("orchestration must not run")

    monkeypatch.setattr(
        runtime_module,
        "run_controlled_image_extraction",
        forbidden,
    )
    result = _run(
        tmp_path,
        data=b"x" * (MAX_INPUT_BYTES + 1),
        source=_source(PNG),
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_FILE_OVERSIZED
    )
    assert calls == 0


def test_missing_file_is_controlled_rejection(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    source = _source()
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="missing.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.source_file_opened is False
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_FILE_NOT_FOUND
    )


def test_directory_target_is_controlled_rejection(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    (source_root / "directory.png").mkdir()
    source = _source()
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="directory.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode
        .SOURCE_FILE_NOT_REGULAR_FILE
    )


def test_relative_source_root_is_controlled_rejection() -> None:
    source = _source()
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=Path("relative-root"),
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=Path("relative-artifacts"),
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode
        .SOURCE_ROOT_NOT_ABSOLUTE
    )


def test_missing_source_root_is_controlled_rejection(
    tmp_path: Path,
) -> None:
    source = _source()
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=tmp_path / "missing-source",
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=tmp_path,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_ROOT_NOT_FOUND
    )


def test_source_root_file_is_controlled_rejection(
    tmp_path: Path,
) -> None:
    root_file = tmp_path / "root-file"
    root_file.write_bytes(b"x")
    source = _source()
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=root_file,
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=tmp_path,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode
        .SOURCE_ROOT_NOT_DIRECTORY
    )


def test_file_read_failure_is_controlled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    _write(source_root, "image.png")
    source = _source()

    def deny(*args: object, **kwargs: object):
        raise PermissionError("synthetic denied")

    monkeypatch.setattr(builtins, "open", deny)
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode.SOURCE_FILE_READ_FAILED
    )
    assert result.source_file_opened is False


@pytest.mark.parametrize(
    "relative_path",
    (
        "../escape.png",
        "folder/../escape.png",
        "/absolute.png",
        "folder\\image.png",
        " image.png",
        "image.png ",
        "./image.png",
    ),
)
def test_malformed_relative_path_is_programmer_error(
    tmp_path: Path,
    relative_path: str,
) -> None:
    with pytest.raises(ValueError):
        _run(tmp_path, relative_path=relative_path)


def test_nonstring_relative_path_is_programmer_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(TypeError):
        _run(
            tmp_path,
            source_relative_path=object(),
        )


def test_nonpath_source_root_is_programmer_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(TypeError, match="source_root"):
        _run(
            tmp_path,
            source_root="source",  # type: ignore[arg-type]
        )


def test_nonpath_artifact_root_is_programmer_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(TypeError, match="artifact_root"):
        _run(
            tmp_path,
            artifact_root="artifacts",  # type: ignore[arg-type]
        )


def test_invalid_declaration_fails_before_file_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = False

    def forbidden(*args: object, **kwargs: object):
        nonlocal opened
        opened = True
        raise AssertionError("file must not open")

    monkeypatch.setattr(builtins, "open", forbidden)
    with pytest.raises(ValueError):
        _run(
            tmp_path,
            declared_media_type="image/jpeg",
            declared_extension=".png",
        )
    assert opened is False


def test_runtime_result_is_frozen(tmp_path: Path) -> None:
    result = _run(tmp_path)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = (  # type: ignore[misc]
            ControlledImageFileExtractionRuntimeStatus.FILE_REJECTED
        )


def test_runtime_module_has_no_network_decoder_model_or_cli_dependency() -> None:
    source = inspect.getsource(runtime_module)
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
            "http",
            "time",
            "datetime",
            "random",
            "secrets",
            "uuid",
            "tempfile",
            "argparse",
            "click",
            "typer",
            "PIL",
            "cv2",
            "numpy",
            "torch",
            "tensorflow",
        }
    )


def test_source_root_symlink_signal_is_controlled_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    source = _source()
    real_is_symlink = Path.is_symlink

    def mark_root(path: Path) -> bool:
        if path == source_root:
            return True
        return real_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", mark_root)
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode
        .SOURCE_ROOT_SYMLINK_FORBIDDEN
    )


def test_source_path_symlink_signal_is_controlled_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_root = tmp_path / "source"
    artifact_root = tmp_path / "artifacts"
    source_root.mkdir()
    artifact_root.mkdir()
    target = _write(source_root, "nested/image.png")
    source = _source()
    real_is_symlink = Path.is_symlink

    def mark_target(path: Path) -> bool:
        if path == target:
            return True
        return real_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", mark_target)
    result = run_controlled_image_file_extraction(
        official_source_payload=encode_official_image_source(source),
        presented_source_id=source.source_id,
        presented_source_locator=source.source_locator,
        source_root=source_root,
        source_relative_path="nested/image.png",
        declared_media_type="image/png",
        declared_extension=".png",
        artifact_root=artifact_root,
    )
    assert result.failure_code is (
        ControlledImageFileExtractionFailureCode
        .SOURCE_PATH_SYMLINK_FORBIDDEN
    )
