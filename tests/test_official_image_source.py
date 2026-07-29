from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from rie.official_source.official_image_source import (
    AdmissionStatus,
    AuthorityClass,
    LifecycleState,
    OfficialImageSource,
    RightsStatus,
    SourceKind,
)


VALID_SHA256 = "a" * 64
VALID_TIME = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def make_source(**overrides: object) -> OfficialImageSource:
    values: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": "repository://assets/controlled/image-001.png",
        "source_kind": SourceKind.REPOSITORY_ASSET,
        "content_sha256": VALID_SHA256,
        "byte_length": 1234,
        "authority_class": AuthorityClass.OFFICIAL_INTERNAL,
        "rights_status": RightsStatus.OWNED,
        "lifecycle_state": LifecycleState.CANDIDATE,
        "admission_status": AdmissionStatus.PENDING,
        "provenance_parent_id": None,
        "registered_at_utc": VALID_TIME,
        "registered_by": "operator-001",
    }
    values.update(overrides)
    return OfficialImageSource(**values)  # type: ignore[arg-type]


def test_constructs_valid_root_candidate() -> None:
    source = make_source()

    assert source.source_id == "image-source-001"
    assert source.provenance_parent_id is None


def test_required_field_order_is_exact() -> None:
    assert OfficialImageSource.required_field_names() == (
        "source_id",
        "source_locator",
        "source_kind",
        "content_sha256",
        "byte_length",
        "authority_class",
        "rights_status",
        "lifecycle_state",
        "admission_status",
        "provenance_parent_id",
        "registered_at_utc",
        "registered_by",
    )


def test_dataclass_has_exactly_twelve_fields() -> None:
    assert len(fields(OfficialImageSource)) == 12


def test_record_is_immutable() -> None:
    source = make_source()

    with pytest.raises(FrozenInstanceError):
        source.source_id = "changed"  # type: ignore[misc]


def test_source_kind_values_are_exact() -> None:
    assert tuple(item.value for item in SourceKind) == (
        "FILE",
        "REPOSITORY_ASSET",
        "CONTROLLED_EXTERNAL_REFERENCE",
    )


def test_authority_values_are_exact() -> None:
    assert tuple(item.value for item in AuthorityClass) == (
        "OFFICIAL_INTERNAL",
        "OFFICIAL_PARTNER",
        "CONTROLLED_EXTERNAL",
    )


def test_rights_values_are_exact() -> None:
    assert tuple(item.value for item in RightsStatus) == (
        "OWNED",
        "LICENSED",
        "APPROVED_INTERNAL_USE",
        "RESTRICTED",
    )


def test_lifecycle_values_are_exact() -> None:
    assert tuple(item.value for item in LifecycleState) == (
        "CANDIDATE",
        "ACTIVE",
        "SUPERSEDED",
        "RETIRED",
        "REVOKED",
    )


def test_admission_values_are_exact() -> None:
    assert tuple(item.value for item in AdmissionStatus) == (
        "PENDING",
        "ACCEPTED",
        "REJECTED",
    )


def test_rejects_non_string_source_id() -> None:
    with pytest.raises(TypeError, match="source_id must be a string"):
        make_source(source_id=123)


def test_rejects_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id must be non-empty"):
        make_source(source_id="")


def test_rejects_source_id_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_source(source_id=" source-001")


def test_rejects_source_id_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_source(source_id="source\n001")


def test_rejects_empty_source_locator() -> None:
    with pytest.raises(ValueError, match="source_locator must be non-empty"):
        make_source(source_locator="")


def test_rejects_untyped_source_kind_string() -> None:
    with pytest.raises(TypeError, match="source_kind must be a SourceKind"):
        make_source(source_kind="FILE")


def test_rejects_non_string_sha256() -> None:
    with pytest.raises(TypeError, match="content_sha256 must be a string"):
        make_source(content_sha256=123)


def test_rejects_short_sha256() -> None:
    with pytest.raises(ValueError, match="exactly 64 lowercase"):
        make_source(content_sha256="a" * 63)


def test_rejects_uppercase_sha256() -> None:
    with pytest.raises(ValueError, match="exactly 64 lowercase"):
        make_source(content_sha256="A" * 64)


def test_rejects_non_hex_sha256() -> None:
    with pytest.raises(ValueError, match="exactly 64 lowercase"):
        make_source(content_sha256="g" * 64)


def test_rejects_boolean_byte_length() -> None:
    with pytest.raises(TypeError, match="byte_length must be an integer"):
        make_source(byte_length=True)


def test_rejects_non_integer_byte_length() -> None:
    with pytest.raises(TypeError, match="byte_length must be an integer"):
        make_source(byte_length=12.5)


def test_rejects_zero_byte_length() -> None:
    with pytest.raises(ValueError, match="byte_length must be positive"):
        make_source(byte_length=0)


def test_rejects_negative_byte_length() -> None:
    with pytest.raises(ValueError, match="byte_length must be positive"):
        make_source(byte_length=-1)


def test_rejects_untyped_authority_string() -> None:
    with pytest.raises(TypeError, match="authority_class must be an AuthorityClass"):
        make_source(authority_class="OFFICIAL_INTERNAL")


def test_rejects_untyped_rights_string() -> None:
    with pytest.raises(TypeError, match="rights_status must be a RightsStatus"):
        make_source(rights_status="OWNED")


def test_rejects_untyped_lifecycle_string() -> None:
    with pytest.raises(TypeError, match="lifecycle_state must be a LifecycleState"):
        make_source(lifecycle_state="CANDIDATE")


def test_rejects_untyped_admission_string() -> None:
    with pytest.raises(TypeError, match="admission_status must be an AdmissionStatus"):
        make_source(admission_status="PENDING")


def test_accepts_non_root_parent_id() -> None:
    source = make_source(provenance_parent_id="image-source-parent")

    assert source.provenance_parent_id == "image-source-parent"


def test_rejects_empty_parent_id() -> None:
    with pytest.raises(ValueError, match="provenance_parent_id must be non-empty"):
        make_source(provenance_parent_id="")


def test_rejects_parent_id_equal_to_source_id() -> None:
    with pytest.raises(ValueError, match="must differ from source_id"):
        make_source(provenance_parent_id="image-source-001")


def test_rejects_naive_registered_time() -> None:
    with pytest.raises(ValueError, match="datetime.timezone.utc"):
        make_source(registered_at_utc=datetime(2026, 7, 28, 12, 0))


def test_rejects_noncanonical_zero_offset_timezone() -> None:
    zero_offset = timezone(timedelta(0), name="UTC+00")

    with pytest.raises(ValueError, match="datetime.timezone.utc"):
        make_source(
            registered_at_utc=datetime(
                2026,
                7,
                28,
                12,
                0,
                tzinfo=zero_offset,
            )
        )


def test_rejects_non_datetime_registered_time() -> None:
    with pytest.raises(TypeError, match="registered_at_utc must be a datetime"):
        make_source(registered_at_utc="2026-07-28T12:00:00Z")


def test_rejects_empty_registered_by() -> None:
    with pytest.raises(ValueError, match="registered_by must be non-empty"):
        make_source(registered_by="")


def test_active_requires_accepted_admission() -> None:
    with pytest.raises(ValueError, match="ACTIVE requires admission_status ACCEPTED"):
        make_source(lifecycle_state=LifecycleState.ACTIVE)


def test_accepts_active_accepted_source() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )

    assert source.lifecycle_state is LifecycleState.ACTIVE


def test_superseded_requires_accepted_admission() -> None:
    with pytest.raises(
        ValueError,
        match="SUPERSEDED requires admission_status ACCEPTED",
    ):
        make_source(
            lifecycle_state=LifecycleState.SUPERSEDED,
            provenance_parent_id="image-source-parent",
        )


def test_superseded_requires_parent_id() -> None:
    with pytest.raises(ValueError, match="SUPERSEDED requires provenance_parent_id"):
        make_source(
            lifecycle_state=LifecycleState.SUPERSEDED,
            admission_status=AdmissionStatus.ACCEPTED,
        )


def test_accepts_superseded_source_with_parent() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.SUPERSEDED,
        admission_status=AdmissionStatus.ACCEPTED,
        provenance_parent_id="image-source-parent",
    )

    assert source.provenance_parent_id == "image-source-parent"


def test_rejected_candidate_is_constructible() -> None:
    source = make_source(admission_status=AdmissionStatus.REJECTED)

    assert source.admission_status is AdmissionStatus.REJECTED

def test_transition_to_rejects_untyped_target_string() -> None:
    source = make_source()

    with pytest.raises(TypeError, match="lifecycle_state must be a LifecycleState"):
        source.transition_to("ACTIVE")  # type: ignore[arg-type]


def test_transition_to_rejects_candidate_no_op() -> None:
    source = make_source()

    with pytest.raises(
        ValueError,
        match="CANDIDATE -> CANDIDATE is not allowed",
    ):
        source.transition_to(LifecycleState.CANDIDATE)


def test_transition_to_active_returns_new_immutable_record() -> None:
    source = make_source(admission_status=AdmissionStatus.ACCEPTED)

    transitioned = source.transition_to(LifecycleState.ACTIVE)

    assert transitioned is not source
    assert source.lifecycle_state is LifecycleState.CANDIDATE
    assert transitioned.lifecycle_state is LifecycleState.ACTIVE
    assert transitioned.source_id == source.source_id
    assert transitioned.content_sha256 == source.content_sha256


def test_transition_to_active_rejects_pending_candidate() -> None:
    source = make_source(admission_status=AdmissionStatus.PENDING)

    with pytest.raises(
        ValueError,
        match="ACTIVE requires admission_status ACCEPTED",
    ):
        source.transition_to(LifecycleState.ACTIVE)


def test_transition_to_active_rejects_rejected_candidate() -> None:
    source = make_source(admission_status=AdmissionStatus.REJECTED)

    with pytest.raises(
        ValueError,
        match="ACTIVE requires admission_status ACCEPTED",
    ):
        source.transition_to(LifecycleState.ACTIVE)


def test_transition_candidate_to_retired() -> None:
    source = make_source()

    transitioned = source.transition_to(LifecycleState.RETIRED)

    assert transitioned.lifecycle_state is LifecycleState.RETIRED
    assert transitioned.admission_status is AdmissionStatus.PENDING


def test_transition_candidate_to_revoked() -> None:
    source = make_source(admission_status=AdmissionStatus.REJECTED)

    transitioned = source.transition_to(LifecycleState.REVOKED)

    assert transitioned.lifecycle_state is LifecycleState.REVOKED
    assert transitioned.admission_status is AdmissionStatus.REJECTED


def test_transition_candidate_to_superseded_is_rejected() -> None:
    source = make_source(
        admission_status=AdmissionStatus.ACCEPTED,
        provenance_parent_id="image-source-parent",
    )

    with pytest.raises(
        ValueError,
        match="CANDIDATE -> SUPERSEDED is not allowed",
    ):
        source.transition_to(LifecycleState.SUPERSEDED)


def test_transition_active_to_superseded_with_parent() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
        provenance_parent_id="image-source-parent",
    )

    transitioned = source.transition_to(LifecycleState.SUPERSEDED)

    assert transitioned.lifecycle_state is LifecycleState.SUPERSEDED
    assert transitioned.provenance_parent_id == "image-source-parent"


def test_transition_active_to_superseded_requires_parent() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )

    with pytest.raises(
        ValueError,
        match="SUPERSEDED requires provenance_parent_id",
    ):
        source.transition_to(LifecycleState.SUPERSEDED)


def test_transition_active_to_retired() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )

    transitioned = source.transition_to(LifecycleState.RETIRED)

    assert transitioned.lifecycle_state is LifecycleState.RETIRED


def test_transition_active_to_revoked() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )

    transitioned = source.transition_to(LifecycleState.REVOKED)

    assert transitioned.lifecycle_state is LifecycleState.REVOKED


def test_transition_active_to_candidate_is_rejected() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )

    with pytest.raises(
        ValueError,
        match="ACTIVE -> CANDIDATE is not allowed",
    ):
        source.transition_to(LifecycleState.CANDIDATE)


def test_transition_superseded_is_terminal() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.SUPERSEDED,
        admission_status=AdmissionStatus.ACCEPTED,
        provenance_parent_id="image-source-parent",
    )

    with pytest.raises(
        ValueError,
        match="SUPERSEDED -> RETIRED is not allowed",
    ):
        source.transition_to(LifecycleState.RETIRED)


def test_transition_retired_is_terminal() -> None:
    source = make_source(lifecycle_state=LifecycleState.RETIRED)

    with pytest.raises(
        ValueError,
        match="RETIRED -> REVOKED is not allowed",
    ):
        source.transition_to(LifecycleState.REVOKED)


def test_transition_revoked_is_terminal() -> None:
    source = make_source(lifecycle_state=LifecycleState.REVOKED)

    with pytest.raises(
        ValueError,
        match="REVOKED -> RETIRED is not allowed",
    ):
        source.transition_to(LifecycleState.RETIRED)
