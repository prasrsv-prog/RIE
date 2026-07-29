from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from rie.official_source.admission_decision_audit import (
    AdmissionDecisionAudit,
    AdmissionDecisionReasonCode,
)
from rie.official_source.official_image_source import (
    AdmissionStatus,
    AuthorityClass,
    LifecycleState,
    OfficialImageSource,
    RightsStatus,
    SourceKind,
)


VALID_TIME = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)


def make_audit(**overrides: object) -> AdmissionDecisionAudit:
    values: dict[str, object] = {
        "decision_id": "admission-decision-001",
        "source_id": "image-source-001",
        "prior_admission_status": AdmissionStatus.PENDING,
        "resulting_admission_status": AdmissionStatus.ACCEPTED,
        "reason_code": AdmissionDecisionReasonCode.ACCEPTED_VALIDATED,
        "reason_detail": "All Gate 12 admission checks passed.",
        "evidence_reference": "evidence://gate-12/admission/001",
        "decided_at_utc": VALID_TIME,
        "decided_by": "operator-001",
    }
    values.update(overrides)
    return AdmissionDecisionAudit(**values)  # type: ignore[arg-type]


def make_source(**overrides: object) -> OfficialImageSource:
    values: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": "repository://assets/controlled/image-001.png",
        "source_kind": SourceKind.REPOSITORY_ASSET,
        "content_sha256": "a" * 64,
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


def test_constructs_valid_accepted_audit() -> None:
    audit = make_audit()

    assert audit.resulting_admission_status is AdmissionStatus.ACCEPTED
    assert audit.reason_code is AdmissionDecisionReasonCode.ACCEPTED_VALIDATED


def test_constructs_valid_rejected_audit() -> None:
    audit = make_audit(
        resulting_admission_status=AdmissionStatus.REJECTED,
        reason_code=AdmissionDecisionReasonCode.REJECTED_RIGHTS_INVALID,
    )

    assert audit.resulting_admission_status is AdmissionStatus.REJECTED


def test_required_field_order_is_exact() -> None:
    assert AdmissionDecisionAudit.required_field_names() == (
        "decision_id",
        "source_id",
        "prior_admission_status",
        "resulting_admission_status",
        "reason_code",
        "reason_detail",
        "evidence_reference",
        "decided_at_utc",
        "decided_by",
    )


def test_dataclass_has_exactly_nine_fields() -> None:
    assert len(fields(AdmissionDecisionAudit)) == 9


def test_record_is_immutable() -> None:
    audit = make_audit()

    with pytest.raises(FrozenInstanceError):
        audit.decision_id = "changed"  # type: ignore[misc]


def test_reason_code_values_are_exact() -> None:
    assert tuple(item.value for item in AdmissionDecisionReasonCode) == (
        "ACCEPTED_VALIDATED",
        "REJECTED_IDENTITY_INVALID",
        "REJECTED_AUTHORITY_INVALID",
        "REJECTED_RIGHTS_INVALID",
        "REJECTED_CHECKSUM_INVALID",
        "REJECTED_BYTE_LENGTH_INVALID",
        "REJECTED_PROVENANCE_INVALID",
        "REJECTED_OTHER_CONTRACT_VIOLATION",
    )


def test_rejects_non_string_decision_id() -> None:
    with pytest.raises(TypeError, match="decision_id must be a string"):
        make_audit(decision_id=123)


def test_rejects_empty_decision_id() -> None:
    with pytest.raises(ValueError, match="decision_id must be non-empty"):
        make_audit(decision_id="")


def test_rejects_decision_id_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_audit(decision_id=" decision-001")


def test_rejects_decision_id_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_audit(decision_id="decision\n001")


def test_rejects_non_string_source_id() -> None:
    with pytest.raises(TypeError, match="source_id must be a string"):
        make_audit(source_id=123)


def test_rejects_empty_source_id() -> None:
    with pytest.raises(ValueError, match="source_id must be non-empty"):
        make_audit(source_id="")


def test_rejects_source_id_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_audit(source_id=" image-source-001")


def test_rejects_source_id_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_audit(source_id="image\tsource")


def test_rejects_untyped_prior_status() -> None:
    with pytest.raises(
        TypeError,
        match="prior_admission_status must be an AdmissionStatus",
    ):
        make_audit(prior_admission_status="PENDING")


def test_rejects_non_pending_prior_status() -> None:
    with pytest.raises(
        ValueError,
        match="prior_admission_status must be PENDING",
    ):
        make_audit(prior_admission_status=AdmissionStatus.ACCEPTED)


def test_rejects_untyped_resulting_status() -> None:
    with pytest.raises(
        TypeError,
        match="resulting_admission_status must be an AdmissionStatus",
    ):
        make_audit(resulting_admission_status="ACCEPTED")


def test_rejects_pending_resulting_status() -> None:
    with pytest.raises(
        ValueError,
        match="must be ACCEPTED or REJECTED",
    ):
        make_audit(resulting_admission_status=AdmissionStatus.PENDING)


def test_rejects_untyped_reason_code() -> None:
    with pytest.raises(
        TypeError,
        match="reason_code must be an AdmissionDecisionReasonCode",
    ):
        make_audit(reason_code="ACCEPTED_VALIDATED")


def test_accepted_rejects_rejection_reason_code() -> None:
    with pytest.raises(
        ValueError,
        match="ACCEPTED requires reason_code ACCEPTED_VALIDATED",
    ):
        make_audit(
            reason_code=AdmissionDecisionReasonCode.REJECTED_RIGHTS_INVALID,
        )


def test_rejected_rejects_accepted_reason_code() -> None:
    with pytest.raises(
        ValueError,
        match="REJECTED requires a REJECTED reason_code",
    ):
        make_audit(
            resulting_admission_status=AdmissionStatus.REJECTED,
            reason_code=AdmissionDecisionReasonCode.ACCEPTED_VALIDATED,
        )


def test_rejects_non_string_reason_detail() -> None:
    with pytest.raises(TypeError, match="reason_detail must be a string"):
        make_audit(reason_detail=123)


def test_rejects_empty_reason_detail() -> None:
    with pytest.raises(ValueError, match="reason_detail must be non-empty"):
        make_audit(reason_detail="")


def test_rejects_reason_detail_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_audit(reason_detail=" explanation")


def test_rejects_reason_detail_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_audit(reason_detail="line one\nline two")


def test_rejects_non_string_evidence_reference() -> None:
    with pytest.raises(TypeError, match="evidence_reference must be a string"):
        make_audit(evidence_reference=123)


def test_rejects_empty_evidence_reference() -> None:
    with pytest.raises(
        ValueError,
        match="evidence_reference must be non-empty",
    ):
        make_audit(evidence_reference="")


def test_rejects_evidence_reference_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_audit(evidence_reference=" evidence://001")


def test_rejects_evidence_reference_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_audit(evidence_reference="evidence\n001")


def test_rejects_non_datetime_decided_at() -> None:
    with pytest.raises(TypeError, match="decided_at_utc must be a datetime"):
        make_audit(decided_at_utc="2026-07-29T12:00:00Z")


def test_rejects_naive_decided_at() -> None:
    with pytest.raises(
        ValueError,
        match="must use datetime.timezone.utc",
    ):
        make_audit(decided_at_utc=datetime(2026, 7, 29, 12, 0))


def test_rejects_non_utc_offset_decided_at() -> None:
    offset = timezone(timedelta(hours=7))

    with pytest.raises(
        ValueError,
        match="must use datetime.timezone.utc",
    ):
        make_audit(
            decided_at_utc=datetime(
                2026,
                7,
                29,
                12,
                0,
                tzinfo=offset,
            )
        )


def test_rejects_non_string_decided_by() -> None:
    with pytest.raises(TypeError, match="decided_by must be a string"):
        make_audit(decided_by=123)


def test_rejects_empty_decided_by() -> None:
    with pytest.raises(ValueError, match="decided_by must be non-empty"):
        make_audit(decided_by="")


def test_rejects_decided_by_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        make_audit(decided_by=" operator-001")


def test_rejects_decided_by_control_character() -> None:
    with pytest.raises(ValueError, match="control characters"):
        make_audit(decided_by="operator\n001")


def test_require_source_linkage_accepts_matching_source() -> None:
    audit = make_audit()
    source = make_source()

    assert audit.require_source_linkage(source) is None


def test_require_source_linkage_rejects_wrong_type() -> None:
    audit = make_audit()

    with pytest.raises(TypeError, match="source must be an OfficialImageSource"):
        audit.require_source_linkage("image-source-001")  # type: ignore[arg-type]


def test_require_source_linkage_rejects_mismatch() -> None:
    audit = make_audit()
    source = make_source(source_id="image-source-002")

    with pytest.raises(
        ValueError,
        match="audit source_id does not match governed source_id",
    ):
        audit.require_source_linkage(source)


def test_rejected_identity_reason_is_accepted() -> None:
    audit = make_audit(
        resulting_admission_status=AdmissionStatus.REJECTED,
        reason_code=AdmissionDecisionReasonCode.REJECTED_IDENTITY_INVALID,
    )

    assert audit.reason_code is AdmissionDecisionReasonCode.REJECTED_IDENTITY_INVALID
