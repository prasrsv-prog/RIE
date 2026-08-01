from dataclasses import FrozenInstanceError, fields

import pytest

from rie.domain.governed_asset_record import (
    ALLOWED_LIFECYCLE_STATES,
    ALLOWED_USE_ELIGIBILITY_STATES,
    LIFECYCLE_STATE_ACTIVE,
    LIFECYCLE_STATE_CANDIDATE,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_SUPERSEDED,
    USE_ELIGIBILITY_ELIGIBLE,
    USE_ELIGIBILITY_INELIGIBLE,
    GovernedAssetRecord,
)


def make_record(**overrides: object) -> GovernedAssetRecord:
    values: dict[str, object] = {
        "asset_record_id": "asset-record-001",
        "provenance_reference": "provenance-001",
        "usage_rights_reference": "rights-001",
        "version_identity": "asset-version-001",
        "lifecycle_state": LIFECYCLE_STATE_CANDIDATE,
        "use_eligibility": USE_ELIGIBILITY_INELIGIBLE,
    }
    values.update(overrides)
    return GovernedAssetRecord(**values)  # type: ignore[arg-type]


def test_contract_has_exactly_six_fields_without_defaults() -> None:
    model_fields = fields(GovernedAssetRecord)

    assert tuple(field.name for field in model_fields) == (
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
        "lifecycle_state",
        "use_eligibility",
    )
    assert all(field.default is field.default_factory for field in model_fields)


def test_allowed_values_are_exact() -> None:
    assert ALLOWED_LIFECYCLE_STATES == {
        "CANDIDATE",
        "ACTIVE",
        "DEPRECATED",
        "SUPERSEDED",
    }
    assert ALLOWED_USE_ELIGIBILITY_STATES == {"ELIGIBLE", "INELIGIBLE"}


def test_candidate_record_is_valid_and_immutable() -> None:
    record = make_record()

    assert record.lifecycle_state == LIFECYCLE_STATE_CANDIDATE
    with pytest.raises(FrozenInstanceError):
        record.asset_record_id = "changed"  # type: ignore[misc]


def test_active_record_may_be_eligible() -> None:
    record = make_record(
        lifecycle_state=LIFECYCLE_STATE_ACTIVE,
        use_eligibility=USE_ELIGIBILITY_ELIGIBLE,
    )

    assert record.use_eligibility == USE_ELIGIBILITY_ELIGIBLE


def test_active_record_may_remain_ineligible() -> None:
    record = make_record(lifecycle_state=LIFECYCLE_STATE_ACTIVE)

    assert record.use_eligibility == USE_ELIGIBILITY_INELIGIBLE


@pytest.mark.parametrize(
    "lifecycle_state",
    [
        LIFECYCLE_STATE_CANDIDATE,
        LIFECYCLE_STATE_DEPRECATED,
        LIFECYCLE_STATE_SUPERSEDED,
    ],
)
def test_non_active_records_are_valid_when_ineligible(
    lifecycle_state: str,
) -> None:
    record = make_record(lifecycle_state=lifecycle_state)

    assert record.use_eligibility == USE_ELIGIBILITY_INELIGIBLE


@pytest.mark.parametrize(
    "lifecycle_state",
    [
        LIFECYCLE_STATE_CANDIDATE,
        LIFECYCLE_STATE_DEPRECATED,
        LIFECYCLE_STATE_SUPERSEDED,
    ],
)
def test_non_active_records_cannot_be_eligible(
    lifecycle_state: str,
) -> None:
    with pytest.raises(ValueError, match="only when"):
        make_record(
            lifecycle_state=lifecycle_state,
            use_eligibility=USE_ELIGIBILITY_ELIGIBLE,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
    ],
)
@pytest.mark.parametrize("invalid_value", ["", "   "])
def test_required_text_fields_reject_empty_values(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_record(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
    ],
)
def test_required_text_fields_reject_non_ascii(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_record(**{field_name: "non-ascii-\u00e9"})


@pytest.mark.parametrize(
    "field_name",
    [
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
    ],
)
def test_required_text_fields_reject_non_text(
    field_name: str,
) -> None:
    with pytest.raises(TypeError, match="must be text"):
        make_record(**{field_name: 123})


def test_asset_record_and_version_identities_must_be_distinct() -> None:
    with pytest.raises(ValueError, match="distinct"):
        make_record(version_identity="asset-record-001")


@pytest.mark.parametrize("invalid_state", ["candidate", "ARCHIVED"])
def test_lifecycle_state_rejects_values_outside_exact_contract(
    invalid_state: str,
) -> None:
    with pytest.raises(ValueError, match="lifecycle_state"):
        make_record(lifecycle_state=invalid_state)


@pytest.mark.parametrize("invalid_eligibility", ["eligible", "UNKNOWN"])
def test_use_eligibility_rejects_values_outside_exact_contract(
    invalid_eligibility: str,
) -> None:
    with pytest.raises(ValueError, match="use_eligibility"):
        make_record(use_eligibility=invalid_eligibility)
