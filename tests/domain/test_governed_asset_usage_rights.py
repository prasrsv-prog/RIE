from dataclasses import FrozenInstanceError, fields

import pytest

from rie.domain.governed_asset_usage_rights import (
    ALLOWED_USE_AUTHORIZATION_DECISIONS,
    ALLOWED_VALIDITY_STATES,
    USE_AUTHORIZATION_AUTHORIZED,
    USE_AUTHORIZATION_NOT_AUTHORIZED,
    VALIDITY_STATE_ACTIVE,
    VALIDITY_STATE_EXPIRED,
    VALIDITY_STATE_REVOKED,
    VALIDITY_STATE_UNVERIFIED,
    GovernedAssetUsageRights,
)


def make_rights(**overrides: object) -> GovernedAssetUsageRights:
    values: dict[str, object] = {
        "rights_record_id": "rights-record-001",
        "rights_holder_reference": "rights-holder-001",
        "permitted_use_scope": "marketing-use",
        "restriction_scope": "no-resale",
        "validity_state": VALIDITY_STATE_UNVERIFIED,
        "use_authorization": USE_AUTHORIZATION_NOT_AUTHORIZED,
    }
    values.update(overrides)
    return GovernedAssetUsageRights(**values)  # type: ignore[arg-type]


def test_contract_has_exactly_six_fields_without_defaults() -> None:
    model_fields = fields(GovernedAssetUsageRights)

    assert tuple(field.name for field in model_fields) == (
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
        "validity_state",
        "use_authorization",
    )
    assert all(field.default is field.default_factory for field in model_fields)


def test_allowed_value_sets_are_exact() -> None:
    assert ALLOWED_VALIDITY_STATES == {
        "UNVERIFIED",
        "ACTIVE",
        "EXPIRED",
        "REVOKED",
    }
    assert ALLOWED_USE_AUTHORIZATION_DECISIONS == {
        "AUTHORIZED",
        "NOT_AUTHORIZED",
    }


def test_exported_constants_match_contract() -> None:
    assert (
        VALIDITY_STATE_UNVERIFIED,
        VALIDITY_STATE_ACTIVE,
        VALIDITY_STATE_EXPIRED,
        VALIDITY_STATE_REVOKED,
    ) == ("UNVERIFIED", "ACTIVE", "EXPIRED", "REVOKED")
    assert (
        USE_AUTHORIZATION_AUTHORIZED,
        USE_AUTHORIZATION_NOT_AUTHORIZED,
    ) == ("AUTHORIZED", "NOT_AUTHORIZED")


def test_record_is_immutable() -> None:
    record = make_rights()

    with pytest.raises(FrozenInstanceError):
        record.rights_record_id = "changed"  # type: ignore[misc]


def test_active_record_may_be_authorized() -> None:
    record = make_rights(
        validity_state=VALIDITY_STATE_ACTIVE,
        use_authorization=USE_AUTHORIZATION_AUTHORIZED,
    )

    assert record.use_authorization == USE_AUTHORIZATION_AUTHORIZED


def test_active_record_may_remain_not_authorized() -> None:
    record = make_rights(validity_state=VALIDITY_STATE_ACTIVE)

    assert record.use_authorization == USE_AUTHORIZATION_NOT_AUTHORIZED


@pytest.mark.parametrize(
    "validity_state",
    [
        VALIDITY_STATE_UNVERIFIED,
        VALIDITY_STATE_EXPIRED,
        VALIDITY_STATE_REVOKED,
    ],
)
def test_non_active_records_are_valid_when_not_authorized(
    validity_state: str,
) -> None:
    record = make_rights(validity_state=validity_state)

    assert record.use_authorization == USE_AUTHORIZATION_NOT_AUTHORIZED


@pytest.mark.parametrize(
    "validity_state",
    [
        VALIDITY_STATE_UNVERIFIED,
        VALIDITY_STATE_EXPIRED,
        VALIDITY_STATE_REVOKED,
    ],
)
def test_non_active_records_cannot_be_authorized(
    validity_state: str,
) -> None:
    with pytest.raises(ValueError, match="only when"):
        make_rights(
            validity_state=validity_state,
            use_authorization=USE_AUTHORIZATION_AUTHORIZED,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
    ],
)
@pytest.mark.parametrize("invalid_value", ["", "   "])
def test_required_text_fields_reject_empty_values(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_rights(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
    ],
)
def test_required_text_fields_reject_non_ascii(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_rights(**{field_name: "non-ascii-\u00e9"})


@pytest.mark.parametrize(
    "field_name",
    [
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
    ],
)
def test_required_text_fields_reject_non_text(
    field_name: str,
) -> None:
    with pytest.raises(TypeError, match="must be text"):
        make_rights(**{field_name: 123})


@pytest.mark.parametrize("invalid_state", ["active", "SUSPENDED"])
def test_validity_state_rejects_values_outside_exact_contract(
    invalid_state: str,
) -> None:
    with pytest.raises(ValueError, match="validity_state"):
        make_rights(validity_state=invalid_state)


@pytest.mark.parametrize(
    "invalid_authorization",
    ["authorized", "UNKNOWN"],
)
def test_use_authorization_rejects_values_outside_exact_contract(
    invalid_authorization: str,
) -> None:
    with pytest.raises(ValueError, match="use_authorization"):
        make_rights(use_authorization=invalid_authorization)
