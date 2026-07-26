from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from rie.extraction import MAX_INPUT_BYTES, ImageStructureResult
from rie.ingestion.unknown_asset_header_inspector import (
    inspect_controlled_image_structure_bytes,
    inspect_controlled_image_structure_file,
)


def _png(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
    )


def _jpeg(width: int, height: int) -> bytes:
    sof_payload = (
        b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x01\x01\x11\x00"
    )
    sof_segment = (
        b"\xff\xc0"
        + (len(sof_payload) + 2).to_bytes(2, "big")
        + sof_payload
    )
    return b"\xff\xd8" + sof_segment + b"\xff\xd9"


def _webp_vp8x(width: int, height: int) -> bytes:
    payload = (
        b"\x00\x00\x00\x00"
        + (width - 1).to_bytes(3, "little")
        + (height - 1).to_bytes(3, "little")
    )
    chunk = b"VP8X" + len(payload).to_bytes(4, "little") + payload
    riff_size = len(b"WEBP") + len(chunk)
    return (
        b"RIFF"
        + riff_size.to_bytes(4, "little")
        + b"WEBP"
        + chunk
    )


def _write_synthetic(
    tmp_path: Path,
    name: str,
    data: bytes,
) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def _assert_file_equivalent(
    tmp_path: Path,
    name: str,
    data: bytes,
) -> ImageStructureResult:
    path = _write_synthetic(tmp_path, name, data)
    expected = inspect_controlled_image_structure_bytes(
        data[: MAX_INPUT_BYTES + 1],
    )
    actual = inspect_controlled_image_structure_file(path)

    assert actual == expected
    assert type(actual) is type(expected)
    return actual


def test_controlled_image_file_png_equivalence(tmp_path: Path) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "synthetic.png",
        _png(640, 480),
    )
    assert result.status == "ACCEPTED"
    assert result.image_format == "PNG"


def test_controlled_image_file_jpeg_equivalence(tmp_path: Path) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "synthetic.jpg",
        _jpeg(1024, 768),
    )
    assert result.status == "ACCEPTED"
    assert result.image_format == "JPEG"


def test_controlled_image_file_webp_equivalence(tmp_path: Path) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "synthetic.webp",
        _webp_vp8x(1920, 1080),
    )
    assert result.status == "ACCEPTED"
    assert result.image_format == "WEBP"


def test_controlled_image_file_unsupported_equivalence(
    tmp_path: Path,
) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "synthetic.bin",
        b"not-an-image",
    )
    assert result.status == "REJECTED"
    assert result.rejection_reason == "UNSUPPORTED_SIGNATURE"


def test_controlled_image_file_truncated_png_equivalence(
    tmp_path: Path,
) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "truncated.png",
        b"\x89PNG\r\n\x1a\n",
    )
    assert result.status == "REJECTED"
    assert result.rejection_reason == "TRUNCATED_PNG"


def test_controlled_image_file_oversized_reads_limit_plus_sentinel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = b"x" * (MAX_INPUT_BYTES + 2)
    path = _write_synthetic(tmp_path, "oversized.bin", data)
    real_open = builtins.open
    read_sizes: list[int] = []

    class TrackingBinaryReader:
        def __init__(self, file: object) -> None:
            self._file = file

        def __enter__(self) -> TrackingBinaryReader:
            return self

        def __exit__(
            self,
            exc_type: object,
            exc: object,
            traceback: object,
        ) -> None:
            self._file.close()  # type: ignore[attr-defined]

        def read(self, size: int = -1) -> bytes:
            read_sizes.append(size)
            return self._file.read(size)  # type: ignore[attr-defined]

    def tracking_open(path_value: object, mode: str) -> TrackingBinaryReader:
        return TrackingBinaryReader(real_open(path_value, mode))

    monkeypatch.setattr(builtins, "open", tracking_open)

    result = inspect_controlled_image_structure_file(path)

    assert read_sizes == [MAX_INPUT_BYTES + 1]
    assert result == inspect_controlled_image_structure_bytes(
        data[: MAX_INPUT_BYTES + 1],
    )
    assert result.status == "REJECTED"
    assert result.input_byte_length == MAX_INPUT_BYTES + 1
    assert result.rejection_reason == "OVERSIZED_INPUT"


def test_controlled_image_file_empty_equivalence(tmp_path: Path) -> None:
    result = _assert_file_equivalent(
        tmp_path,
        "empty.bin",
        b"",
    )
    assert result.status == "REJECTED"
    assert result.rejection_reason == "UNSUPPORTED_SIGNATURE"


def test_controlled_image_file_repeated_determinism(
    tmp_path: Path,
) -> None:
    data = _webp_vp8x(320, 240)
    path = _write_synthetic(tmp_path, "repeat.webp", data)

    first = inspect_controlled_image_structure_file(path)
    second = inspect_controlled_image_structure_file(path)

    assert first == second
    assert first == inspect_controlled_image_structure_bytes(data)


def test_controlled_image_file_accepts_string_path(
    tmp_path: Path,
) -> None:
    data = _png(32, 16)
    path = _write_synthetic(tmp_path, "string-path.png", data)

    assert inspect_controlled_image_structure_file(str(path)) == (
        inspect_controlled_image_structure_bytes(data)
    )


def test_controlled_image_file_missing_path_propagates_file_not_found(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        inspect_controlled_image_structure_file(missing)


def test_controlled_image_file_directory_propagates_native_os_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(OSError):
        inspect_controlled_image_structure_file(tmp_path)


def test_controlled_image_file_permission_failure_propagates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _write_synthetic(tmp_path, "permission.png", _png(8, 8))
    expected_error = PermissionError("synthetic permission denied")

    def deny_open(*args: object, **kwargs: object) -> object:
        raise expected_error

    monkeypatch.setattr(builtins, "open", deny_open)

    with pytest.raises(PermissionError) as captured:
        inspect_controlled_image_structure_file(path)

    assert captured.value is expected_error


def test_controlled_image_file_non_path_propagates_type_error() -> None:
    with pytest.raises(TypeError):
        inspect_controlled_image_structure_file(
            object(),  # type: ignore[arg-type]
        )
