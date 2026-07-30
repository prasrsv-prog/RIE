from __future__ import annotations

import ast
import dataclasses
import hashlib
import inspect
from datetime import datetime, timezone

import pytest

from rie.extraction.image_extraction_artifact import (
    ImageExtractionArtifactRejectionCode,
)
from rie.extraction.official_image_source_extraction_integration import (
    OFFICIAL_IMAGE_SOURCE_EXTRACTION_INTEGRATION_VERSION,
    OFFICIAL_IMAGE_SOURCE_EXTRACTION_RESULT_FIELD_ORDER,
    OfficialImageSourceExtractionValidationResult,
    OfficialImageSourceExtractionValidationStatus,
    resolve_and_validate_official_image_source_for_extraction,
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
SHA = hashlib.sha256(PNG).hexdigest()
LOCATOR = "repository://assets/controlled/image-001.png"


def _source(**changes: object) -> OfficialImageSource:
    values: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": LOCATOR,
        "source_kind": SourceKind.REPOSITORY_ASSET,
        "content_sha256": SHA,
        "byte_length": len(PNG),
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


def _validate(
    source: OfficialImageSource | None = None,
    **changes: object,
) -> OfficialImageSourceExtractionValidationResult:
    if source is None:
        source = _source()
    values: dict[str, object] = {
        "official_source_payload": encode_official_image_source(source),
        "presented_source_id": source.source_id,
        "presented_source_locator": source.source_locator,
        "input_bytes": PNG,
        "declared_media_type": "image/png",
        "declared_extension": ".png",
    }
    values.update(changes)
    return resolve_and_validate_official_image_source_for_extraction(
        **values  # type: ignore[arg-type]
    )


def test_version_and_result_field_order_are_exact() -> None:
    assert OFFICIAL_IMAGE_SOURCE_EXTRACTION_INTEGRATION_VERSION == (
        "official_image_source_extraction_integration_v1"
    )
    assert OFFICIAL_IMAGE_SOURCE_EXTRACTION_RESULT_FIELD_ORDER == (
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


def test_accepts_internal_owned_active_source() -> None:
    result = _validate()
    assert result.status is (
        OfficialImageSourceExtractionValidationStatus.ACCEPTED
    )
    assert result.official_source == _source()
    assert result.rejection_code is None


def test_accepts_partner_licensed_file_source() -> None:
    source = _source(
        source_kind=SourceKind.FILE,
        authority_class=AuthorityClass.OFFICIAL_PARTNER,
        rights_status=RightsStatus.LICENSED,
        source_locator="file://controlled/image-001.png",
    )
    result = _validate(source)
    assert result.status is (
        OfficialImageSourceExtractionValidationStatus.ACCEPTED
    )


def test_accepts_controlled_external_reference() -> None:
    source = _source(
        source_kind=SourceKind.CONTROLLED_EXTERNAL_REFERENCE,
        authority_class=AuthorityClass.CONTROLLED_EXTERNAL,
        rights_status=RightsStatus.APPROVED_INTERNAL_USE,
        source_locator="https://controlled.example/image-001",
    )
    result = _validate(source)
    assert result.status is (
        OfficialImageSourceExtractionValidationStatus.ACCEPTED
    )


def test_result_is_frozen() -> None:
    result = _validate()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = (  # type: ignore[misc]
            OfficialImageSourceExtractionValidationStatus.REJECTED
        )


def test_result_contains_exact_computed_input_metadata() -> None:
    result = _validate()
    assert result.input_sha256 == SHA
    assert result.input_byte_length == len(PNG)


def test_identical_inputs_are_deterministic() -> None:
    assert _validate() == _validate()


def test_missing_source_payload_is_controlled_rejection() -> None:
    result = _validate(official_source_payload=None)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .OFFICIAL_IMAGE_SOURCE_MISSING
    )


def test_invalid_source_payload_is_controlled_rejection() -> None:
    result = _validate(official_source_payload=b"invalid")
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .OFFICIAL_IMAGE_SOURCE_NOT_ACCEPTED
    )


@pytest.mark.parametrize(
    "admission_status",
    (AdmissionStatus.PENDING, AdmissionStatus.REJECTED),
)
def test_nonaccepted_source_is_rejected(
    admission_status: AdmissionStatus,
) -> None:
    source = _source(
        lifecycle_state=LifecycleState.CANDIDATE,
        admission_status=admission_status,
    )
    result = _validate(source)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .OFFICIAL_IMAGE_SOURCE_NOT_ACCEPTED
    )


def test_source_id_mismatch_is_rejected() -> None:
    result = _validate(presented_source_id="image-source-other")
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode.SOURCE_ID_MISMATCH
    )


def test_source_reference_mismatch_is_rejected() -> None:
    result = _validate(
        presented_source_locator=(
            "repository://assets/controlled/other.png"
        )
    )
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .SOURCE_REFERENCE_MISMATCH
    )


def test_input_sha256_mismatch_is_rejected() -> None:
    source = _source(content_sha256="b" * 64)
    result = _validate(source)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .INPUT_SHA256_MISMATCH
    )


def test_input_byte_length_mismatch_is_rejected() -> None:
    source = _source(byte_length=len(PNG) + 1)
    result = _validate(source)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .INPUT_BYTE_LENGTH_MISMATCH
    )


def test_restricted_rights_are_rejected() -> None:
    result = _validate(_source(rights_status=RightsStatus.RESTRICTED))
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode.RIGHTS_REJECTED
    )


@pytest.mark.parametrize(
    "lifecycle_state",
    (
        LifecycleState.SUPERSEDED,
        LifecycleState.RETIRED,
        LifecycleState.REVOKED,
    ),
)
def test_nonactive_lifecycle_is_rejected(
    lifecycle_state: LifecycleState,
) -> None:
    source = _source(
        lifecycle_state=lifecycle_state,
        provenance_parent_id=(
            "image-source-parent"
            if lifecycle_state is LifecycleState.SUPERSEDED
            else None
        ),
    )
    result = _validate(source)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .LIFECYCLE_REJECTED
    )


@pytest.mark.parametrize(
    ("source_kind", "authority_class"),
    (
        (
            SourceKind.REPOSITORY_ASSET,
            AuthorityClass.CONTROLLED_EXTERNAL,
        ),
        (
            SourceKind.FILE,
            AuthorityClass.CONTROLLED_EXTERNAL,
        ),
        (
            SourceKind.CONTROLLED_EXTERNAL_REFERENCE,
            AuthorityClass.OFFICIAL_INTERNAL,
        ),
    ),
)
def test_source_kind_authority_mismatch_is_rejected(
    source_kind: SourceKind,
    authority_class: AuthorityClass,
) -> None:
    source = _source(
        source_kind=source_kind,
        authority_class=authority_class,
    )
    result = _validate(source)
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode.AUTHORITY_REJECTED
    )


@pytest.mark.parametrize(
    ("media_type", "extension"),
    (
        ("image/jpeg", ".png"),
        ("image/png", ".gif"),
        ("image/gif", ".gif"),
    ),
)
def test_declared_classification_conflict_is_controlled(
    media_type: str,
    extension: str,
) -> None:
    result = _validate(
        declared_media_type=media_type,
        declared_extension=extension,
    )
    assert result.rejection_code is (
        ImageExtractionArtifactRejectionCode
        .DECLARED_MEDIA_TYPE_EXTENSION_CONFLICT
    )


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("presented_source_id", 1),
        ("presented_source_locator", 1),
        ("input_bytes", bytearray(PNG)),
        ("declared_media_type", 1),
        ("declared_extension", 1),
        ("official_source_payload", bytearray(b"x")),
    ),
)
def test_exact_input_types_are_required(
    name: str,
    value: object,
) -> None:
    with pytest.raises(TypeError):
        _validate(**{name: value})


@pytest.mark.parametrize(
    ("name", "value"),
    (
        ("presented_source_id", ""),
        ("presented_source_id", " source"),
        ("presented_source_id", "source id"),
        ("presented_source_id", "a" * 257),
        ("presented_source_locator", ""),
        ("presented_source_locator", " locator"),
        ("input_bytes", b""),
    ),
)
def test_invalid_required_input_values_are_rejected(
    name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError):
        _validate(**{name: value})


def test_rejected_result_contains_no_accepted_source() -> None:
    result = _validate(official_source_payload=None)
    assert result.status is (
        OfficialImageSourceExtractionValidationStatus.REJECTED
    )
    assert result.official_source is None
    assert result.provenance_reference_id is None


def test_root_source_provenance_is_unambiguous() -> None:
    result = _validate()
    assert result.provenance_reference_id == "image-source-001"


def test_parent_provenance_is_preserved() -> None:
    source = _source(provenance_parent_id="image-source-parent")
    result = _validate(source)
    assert result.provenance_reference_id == "image-source-parent"


def test_accepted_result_rejects_rejection_code() -> None:
    accepted = _validate()
    with pytest.raises(ValueError):
        OfficialImageSourceExtractionValidationResult(
            integration_version=accepted.integration_version,
            status=accepted.status,
            presented_source_id=accepted.presented_source_id,
            presented_source_locator=accepted.presented_source_locator,
            input_sha256=accepted.input_sha256,
            input_byte_length=accepted.input_byte_length,
            declared_media_type=accepted.declared_media_type,
            declared_extension=accepted.declared_extension,
            official_source=accepted.official_source,
            provenance_reference_id=accepted.provenance_reference_id,
            rejection_code=(
                ImageExtractionArtifactRejectionCode.RIGHTS_REJECTED
            ),
        )


def test_rejected_result_requires_rejection_code() -> None:
    rejected = _validate(official_source_payload=None)
    with pytest.raises(TypeError):
        OfficialImageSourceExtractionValidationResult(
            integration_version=rejected.integration_version,
            status=rejected.status,
            presented_source_id=rejected.presented_source_id,
            presented_source_locator=rejected.presented_source_locator,
            input_sha256=rejected.input_sha256,
            input_byte_length=rejected.input_byte_length,
            declared_media_type=rejected.declared_media_type,
            declared_extension=rejected.declared_extension,
            official_source=None,
            provenance_reference_id=None,
            rejection_code=None,
        )


def test_integration_module_does_not_import_parser_filesystem_network_clock_or_model() -> None:
    import rie.extraction.official_image_source_extraction_integration as module

    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    forbidden_fragments = (
        "image_structure_parser",
        "image_extraction_artifact_file_persistence",
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
    )
    assert all(
        not any(fragment in module_name for fragment in forbidden_fragments)
        for module_name in imported_modules
    )
