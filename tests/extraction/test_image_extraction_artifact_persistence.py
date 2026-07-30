from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
import json

import pytest

from rie.extraction.image_extraction_artifact import (
    IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER,
    ImageExtractionArtifact,
    ImageExtractionArtifactRejectionCode,
)
from rie.extraction.image_extraction_artifact_persistence import (
    IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES,
    IMAGE_EXTRACTION_ARTIFACT_PERSISTENCE_FORMAT,
    CanonicalImageExtractionArtifactPayload,
    ImageExtractionArtifactPersistenceError,
    canonical_image_extraction_artifact_payload,
    deserialize_image_extraction_artifact,
    serialize_image_extraction_artifact,
)


SHA = "a" * 64


def _success() -> ImageExtractionArtifact:
    return ImageExtractionArtifact.succeeded(
        official_image_source_id="official-image-source:alpha",
        input_sha256=SHA,
        input_byte_length=128,
        declared_media_type="image/png",
        declared_extension=".png",
        detected_format="png",
        pixel_width=16,
        pixel_height=8,
        parser_id="rie.image_structure_parser",
        parser_version="1",
    )


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


def _decoded(payload: bytes) -> dict[str, object]:
    return json.loads(payload.decode("ascii"))


def _recoded(values: dict[str, object]) -> bytes:
    return (
        json.dumps(
            values,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def test_persistence_format_and_limit_are_exact() -> None:
    assert IMAGE_EXTRACTION_ARTIFACT_PERSISTENCE_FORMAT == (
        "image_extraction_artifact_canonical_json_v1"
    )
    assert IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES == 65536


@pytest.mark.parametrize("artifact", (_success(), _rejected()))
def test_exact_round_trip(
    artifact: ImageExtractionArtifact,
) -> None:
    payload = serialize_image_extraction_artifact(artifact)
    restored = deserialize_image_extraction_artifact(payload)
    assert restored == artifact
    assert serialize_image_extraction_artifact(restored) == payload


@pytest.mark.parametrize("artifact", (_success(), _rejected()))
def test_serialization_is_deterministic(
    artifact: ImageExtractionArtifact,
) -> None:
    assert serialize_image_extraction_artifact(artifact) == (
        serialize_image_extraction_artifact(artifact)
    )


def test_serialized_field_order_is_exact() -> None:
    payload = serialize_image_extraction_artifact(_success())
    assert tuple(_decoded(payload)) == IMAGE_EXTRACTION_ARTIFACT_FIELD_ORDER


def test_serialized_bytes_are_ascii_lf_only_and_compact() -> None:
    payload = serialize_image_extraction_artifact(_success())
    assert payload.isascii()
    assert b"\r" not in payload
    assert payload.endswith(b"\n")
    assert not payload.endswith(b"\n\n")
    assert b": " not in payload
    assert b", " not in payload


def test_payload_metadata_is_exact_and_frozen() -> None:
    artifact = _success()
    payload = serialize_image_extraction_artifact(artifact)
    result = canonical_image_extraction_artifact_payload(artifact)
    assert result.payload == payload
    assert result.serialized_sha256 == hashlib.sha256(payload).hexdigest()
    assert result.serialized_byte_length == len(payload)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.serialized_byte_length = 0  # type: ignore[misc]


def test_payload_metadata_rejects_sha_mismatch() -> None:
    payload = serialize_image_extraction_artifact(_success())
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="serialized_sha256",
    ):
        CanonicalImageExtractionArtifactPayload(
            payload=payload,
            serialized_sha256="0" * 64,
            serialized_byte_length=len(payload),
        )


def test_payload_metadata_rejects_length_mismatch() -> None:
    payload = serialize_image_extraction_artifact(_success())
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="serialized_byte_length",
    ):
        CanonicalImageExtractionArtifactPayload(
            payload=payload,
            serialized_sha256=hashlib.sha256(payload).hexdigest(),
            serialized_byte_length=len(payload) + 1,
        )


def test_serializer_requires_exact_artifact_type() -> None:
    with pytest.raises(TypeError, match="exact ImageExtractionArtifact"):
        serialize_image_extraction_artifact(object())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "payload",
    (
        b"",
        b"{}",
        b"{}\n\n",
        b"{}\r\n",
        b"\xef\xbb\xbf{}\n",
        b"\xff\n",
    ),
)
def test_transport_byte_contract_rejections(payload: bytes) -> None:
    with pytest.raises(ImageExtractionArtifactPersistenceError):
        deserialize_image_extraction_artifact(payload)


def test_oversized_payload_is_rejected() -> None:
    payload = b"{" + (
        b" " * IMAGE_EXTRACTION_ARTIFACT_MAX_SERIALIZED_BYTES
    ) + b"}\n"
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="length",
    ):
        deserialize_image_extraction_artifact(payload)


def test_non_object_json_is_rejected() -> None:
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="one JSON object",
    ):
        deserialize_image_extraction_artifact(b"[]\n")


def test_duplicate_field_is_rejected() -> None:
    payload = serialize_image_extraction_artifact(_success())
    text = payload.decode("ascii")
    duplicated = text.replace(
        '{"artifact_schema_version":',
        '{"artifact_schema_version":"image_extraction_artifact_v1",'
        '"artifact_schema_version":',
        1,
    ).encode("ascii")
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="duplicate artifact field",
    ):
        deserialize_image_extraction_artifact(duplicated)


def test_missing_field_is_rejected() -> None:
    values = _decoded(serialize_image_extraction_artifact(_success()))
    values.pop("parser_version")
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="field set or order",
    ):
        deserialize_image_extraction_artifact(_recoded(values))


def test_unknown_field_is_rejected() -> None:
    values = _decoded(serialize_image_extraction_artifact(_success()))
    values["unknown"] = "value"
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="field set or order",
    ):
        deserialize_image_extraction_artifact(_recoded(values))


def test_reordered_fields_are_rejected() -> None:
    values = _decoded(serialize_image_extraction_artifact(_success()))
    reordered = dict(reversed(tuple(values.items())))
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="field set or order",
    ):
        deserialize_image_extraction_artifact(_recoded(reordered))


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("artifact_schema_version", "unknown"),
        ("artifact_id", "0" * 64),
        ("input_byte_length", True),
        ("extraction_status", "unknown"),
        ("rejection_code", "unknown"),
    ),
)
def test_model_contract_tampering_is_rejected(
    field: str,
    value: object,
) -> None:
    values = _decoded(serialize_image_extraction_artifact(_success()))
    values[field] = value
    with pytest.raises(ImageExtractionArtifactPersistenceError):
        deserialize_image_extraction_artifact(_recoded(values))


def test_non_canonical_whitespace_is_rejected() -> None:
    values = _decoded(serialize_image_extraction_artifact(_success()))
    payload = (
        json.dumps(values, ensure_ascii=True, indent=2) + "\n"
    ).encode("ascii")
    with pytest.raises(
        ImageExtractionArtifactPersistenceError,
        match="not canonical",
    ):
        deserialize_image_extraction_artifact(payload)


def test_persistence_module_has_no_filesystem_network_clock_or_model_dependency() -> None:
    import rie.extraction.image_extraction_artifact_persistence as module

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
