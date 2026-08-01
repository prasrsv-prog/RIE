from dataclasses import FrozenInstanceError, MISSING, fields

import pytest

from rie.domain.governed_asset_record import (
    LIFECYCLE_STATE_ACTIVE,
    LIFECYCLE_STATE_CANDIDATE,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_SUPERSEDED,
    USE_ELIGIBILITY_ELIGIBLE,
    USE_ELIGIBILITY_INELIGIBLE,
    GovernedAssetRecord,
)
from rie.domain.governed_asset_usage_rights import (
    USE_AUTHORIZATION_AUTHORIZED,
    USE_AUTHORIZATION_NOT_AUTHORIZED,
    VALIDITY_STATE_ACTIVE,
    VALIDITY_STATE_EXPIRED,
    VALIDITY_STATE_REVOKED,
    VALIDITY_STATE_UNVERIFIED,
    GovernedAssetUsageRights,
)
from rie.domain.governed_asset_use_eligibility import (
    ALLOWED_DECISION_VALUES,
    DECISION_ELIGIBLE,
    DECISION_INELIGIBLE,
    GovernedAssetUseEligibilityDecision,
)


def make_asset(**overrides: object) -> GovernedAssetRecord:
    values: dict[str, object] = {
        "asset_record_id": "asset-record-001",
        "provenance_reference": "provenance-001",
        "usage_rights_reference": "rights-record-001",
        "version_identity": "asset-version-001",
        "lifecycle_state": LIFECYCLE_STATE_ACTIVE,
        "use_eligibility": USE_ELIGIBILITY_ELIGIBLE,
    }
    values.update(overrides)
    return GovernedAssetRecord(**values)  # type: ignore[arg-type]


def make_rights(**overrides: object) -> GovernedAssetUsageRights:
    values: dict[str, object] = {
        "rights_record_id": "rights-record-001",
        "rights_holder_reference": "rights-holder-001",
        "permitted_use_scope": "marketing-use",
        "restriction_scope": "no-resale",
        "validity_state": VALIDITY_STATE_ACTIVE,
        "use_authorization": USE_AUTHORIZATION_AUTHORIZED,
    }
    values.update(overrides)
    return GovernedAssetUsageRights(**values)  # type: ignore[arg-type]


def make_decision(**overrides: object) -> GovernedAssetUseEligibilityDecision:
    values: dict[str, object] = {
        "asset_record": make_asset(),
        "usage_rights_record": make_rights(),
        "requested_use_scope": "marketing-use",
        "asset_record_reference": "asset-record-001",
        "usage_rights_record_reference": "rights-record-001",
        "decision_context_reference": "decision-context-001",
    }
    values.update(overrides)
    return GovernedAssetUseEligibilityDecision(
        **values
    )  # type: ignore[arg-type]


def test_contract_has_exactly_six_input_fields_without_defaults() -> None:
    model_fields = fields(GovernedAssetUseEligibilityDecision)

    assert tuple(field.name for field in model_fields) == (
        "asset_record",
        "usage_rights_record",
        "requested_use_scope",
        "asset_record_reference",
        "usage_rights_record_reference",
        "decision_context_reference",
    )
    assert all(
        field.default is MISSING and field.default_factory is MISSING
        for field in model_fields
    )


def test_decision_values_are_exact() -> None:
    assert ALLOWED_DECISION_VALUES == {"ELIGIBLE", "INELIGIBLE"}
    assert (DECISION_ELIGIBLE, DECISION_INELIGIBLE) == (
        "ELIGIBLE",
        "INELIGIBLE",
    )


def test_decision_is_immutable() -> None:
    decision = make_decision()

    with pytest.raises(FrozenInstanceError):
        decision.requested_use_scope = "changed"  # type: ignore[misc]


def test_all_required_predicates_produce_eligible() -> None:
    decision = make_decision()

    assert decision.decision_value == DECISION_ELIGIBLE


@pytest.mark.parametrize("invalid_value", ["", "   "])
@pytest.mark.parametrize(
    "field_name",
    [
        "requested_use_scope",
        "asset_record_reference",
        "usage_rights_record_reference",
        "decision_context_reference",
    ],
)
def test_required_text_inputs_reject_empty_values(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_decision(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "requested_use_scope",
        "asset_record_reference",
        "usage_rights_record_reference",
        "decision_context_reference",
    ],
)
def test_required_text_inputs_reject_non_ascii(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_decision(**{field_name: "non-ascii-\u00e9"})


@pytest.mark.parametrize(
    "field_name",
    [
        "requested_use_scope",
        "asset_record_reference",
        "usage_rights_record_reference",
        "decision_context_reference",
    ],
)
def test_required_text_inputs_reject_non_text(
    field_name: str,
) -> None:
    with pytest.raises(TypeError, match="must be text"):
        make_decision(**{field_name: 123})


def test_asset_record_requires_exact_domain_type() -> None:
    with pytest.raises(TypeError, match="GovernedAssetRecord"):
        make_decision(asset_record=object())


def test_usage_rights_record_requires_exact_domain_type() -> None:
    with pytest.raises(TypeError, match="GovernedAssetUsageRights"):
        make_decision(usage_rights_record=object())


def test_asset_record_reference_mismatch_is_ineligible() -> None:
    decision = make_decision(asset_record_reference="asset-record-other")

    assert decision.decision_value == DECISION_INELIGIBLE


def test_usage_rights_record_reference_mismatch_is_ineligible() -> None:
    decision = make_decision(
        usage_rights_record_reference="rights-record-other"
    )

    assert decision.decision_value == DECISION_INELIGIBLE


def test_asset_to_rights_reference_mismatch_is_ineligible() -> None:
    decision = make_decision(
        asset_record=make_asset(
            usage_rights_reference="rights-record-other"
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE


@pytest.mark.parametrize(
    "lifecycle_state",
    [
        LIFECYCLE_STATE_CANDIDATE,
        LIFECYCLE_STATE_DEPRECATED,
        LIFECYCLE_STATE_SUPERSEDED,
    ],
)
def test_non_active_asset_is_ineligible(
    lifecycle_state: str,
) -> None:
    decision = make_decision(
        asset_record=make_asset(
            lifecycle_state=lifecycle_state,
            use_eligibility=USE_ELIGIBILITY_INELIGIBLE,
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE


def test_stored_asset_ineligibility_is_ineligible() -> None:
    decision = make_decision(
        asset_record=make_asset(
            use_eligibility=USE_ELIGIBILITY_INELIGIBLE
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE


@pytest.mark.parametrize(
    "validity_state",
    [
        VALIDITY_STATE_UNVERIFIED,
        VALIDITY_STATE_EXPIRED,
        VALIDITY_STATE_REVOKED,
    ],
)
def test_non_active_rights_are_ineligible(
    validity_state: str,
) -> None:
    decision = make_decision(
        usage_rights_record=make_rights(
            validity_state=validity_state,
            use_authorization=USE_AUTHORIZATION_NOT_AUTHORIZED,
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE


def test_not_authorized_rights_are_ineligible() -> None:
    decision = make_decision(
        usage_rights_record=make_rights(
            use_authorization=USE_AUTHORIZATION_NOT_AUTHORIZED
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE


def test_requested_use_outside_permitted_scope_is_ineligible() -> None:
    decision = make_decision(requested_use_scope="editorial-use")

    assert decision.decision_value == DECISION_INELIGIBLE


def test_requested_use_blocked_by_restriction_is_ineligible() -> None:
    decision = make_decision(
        usage_rights_record=make_rights(
            restriction_scope="marketing-use"
        )
    )

    assert decision.decision_value == DECISION_INELIGIBLE
