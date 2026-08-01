from dataclasses import FrozenInstanceError

import pytest

from rie.domain.evaluate_governed_asset_library_use_eligibility import (
    evaluate_governed_asset_library_use_eligibility,
)
from rie.domain.governed_asset_library_registry import (
    NOT_FOUND,
    GovernedAssetLibraryRegistry,
)
from rie.domain.governed_asset_record import (
    LIFECYCLE_STATE_ACTIVE,
    LIFECYCLE_STATE_CANDIDATE,
    USE_ELIGIBILITY_ELIGIBLE,
    USE_ELIGIBILITY_INELIGIBLE,
    GovernedAssetRecord,
)
from rie.domain.governed_asset_usage_rights import (
    USE_AUTHORIZATION_AUTHORIZED,
    USE_AUTHORIZATION_NOT_AUTHORIZED,
    VALIDITY_STATE_ACTIVE,
    VALIDITY_STATE_UNVERIFIED,
    GovernedAssetUsageRights,
)
from rie.domain.governed_asset_use_eligibility import (
    DECISION_ELIGIBLE,
    DECISION_INELIGIBLE,
    GovernedAssetUseEligibilityDecision,
)


def make_rights(
    *,
    rights_record_id: str = "rights-001",
    permitted_use_scope: str = "campaign-web",
    restriction_scope: str = "broadcast-tv",
    validity_state: str = VALIDITY_STATE_ACTIVE,
    use_authorization: str = USE_AUTHORIZATION_AUTHORIZED,
) -> GovernedAssetUsageRights:
    return GovernedAssetUsageRights(
        rights_record_id=rights_record_id,
        rights_holder_reference="holder-001",
        permitted_use_scope=permitted_use_scope,
        restriction_scope=restriction_scope,
        validity_state=validity_state,
        use_authorization=use_authorization,
    )


def make_asset(
    *,
    asset_record_id: str = "asset-001",
    usage_rights_reference: str = "rights-001",
    lifecycle_state: str = LIFECYCLE_STATE_ACTIVE,
    use_eligibility: str = USE_ELIGIBILITY_ELIGIBLE,
) -> GovernedAssetRecord:
    return GovernedAssetRecord(
        asset_record_id=asset_record_id,
        provenance_reference="provenance-001",
        usage_rights_reference=usage_rights_reference,
        version_identity=f"{asset_record_id}-v1",
        lifecycle_state=lifecycle_state,
        use_eligibility=use_eligibility,
    )


def make_registry(
    *,
    asset: GovernedAssetRecord | None = None,
    rights: GovernedAssetUsageRights | None = None,
) -> GovernedAssetLibraryRegistry:
    rights_record = rights or make_rights()
    asset_record = asset or make_asset(
        usage_rights_reference=rights_record.rights_record_id
    )
    return GovernedAssetLibraryRegistry(
        asset_records=(asset_record,),
        usage_rights_records=(rights_record,),
    )


def evaluate(
    registry: GovernedAssetLibraryRegistry | None = None,
    *,
    asset_record_id: str = "asset-001",
    requested_use_scope: str = "campaign-web",
    decision_context_reference: str = "decision-context-001",
) -> GovernedAssetUseEligibilityDecision:
    return evaluate_governed_asset_library_use_eligibility(
        registry or make_registry(),
        asset_record_id,
        requested_use_scope,
        decision_context_reference,
    )


def test_returns_governed_asset_use_eligibility_decision() -> None:
    assert isinstance(evaluate(), GovernedAssetUseEligibilityDecision)


def test_returns_eligible_for_exact_active_authorized_scope() -> None:
    assert evaluate().decision_value == DECISION_ELIGIBLE


def test_returns_registered_asset_record_without_copying() -> None:
    registry = make_registry()
    decision = evaluate(registry)
    assert decision.asset_record is registry.asset_records[0]


def test_returns_registered_rights_record_without_copying() -> None:
    registry = make_registry()
    decision = evaluate(registry)
    assert decision.usage_rights_record is registry.usage_rights_records[0]


def test_constructs_exact_asset_record_reference() -> None:
    decision = evaluate()
    assert decision.asset_record_reference == "asset-001"


def test_constructs_exact_usage_rights_record_reference() -> None:
    decision = evaluate()
    assert decision.usage_rights_record_reference == "rights-001"


def test_preserves_requested_use_scope_exactly() -> None:
    decision = evaluate(requested_use_scope="campaign-web")
    assert decision.requested_use_scope == "campaign-web"


def test_preserves_decision_context_reference_exactly() -> None:
    decision = evaluate(decision_context_reference="context-A")
    assert decision.decision_context_reference == "context-A"


def test_decision_is_frozen() -> None:
    decision = evaluate()
    with pytest.raises(FrozenInstanceError):
        decision.asset_record_reference = "asset-002"  # type: ignore[misc]


def test_rejects_non_registry_input() -> None:
    with pytest.raises(
        TypeError,
        match="registry must be a GovernedAssetLibraryRegistry",
    ):
        evaluate_governed_asset_library_use_eligibility(
            object(),  # type: ignore[arg-type]
            "asset-001",
            "campaign-web",
            "context-001",
        )


@pytest.mark.parametrize("value", [None, 1, (), []])
def test_rejects_non_text_asset_record_id(value: object) -> None:
    with pytest.raises(TypeError, match="asset_record_id must be text"):
        evaluate_governed_asset_library_use_eligibility(
            make_registry(),
            value,  # type: ignore[arg-type]
            "campaign-web",
            "context-001",
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_empty_asset_record_id(value: str) -> None:
    with pytest.raises(ValueError, match="asset_record_id must not be empty"):
        evaluate(asset_record_id=value)


def test_rejects_non_ascii_asset_record_id() -> None:
    with pytest.raises(
        ValueError,
        match="asset_record_id must contain ASCII text only",
    ):
        evaluate(asset_record_id="asset-caf\u00e9")


def test_missing_asset_propagates_exact_not_found() -> None:
    with pytest.raises(KeyError) as error:
        evaluate(asset_record_id="asset-missing")
    assert error.value.args == (NOT_FOUND,)


def test_asset_id_lookup_is_case_sensitive() -> None:
    with pytest.raises(KeyError) as error:
        evaluate(asset_record_id="ASSET-001")
    assert error.value.args == (NOT_FOUND,)


@pytest.mark.parametrize("value", [None, 1, (), []])
def test_rejects_non_text_requested_use_scope(value: object) -> None:
    with pytest.raises(TypeError, match="requested_use_scope must be text"):
        evaluate_governed_asset_library_use_eligibility(
            make_registry(),
            "asset-001",
            value,  # type: ignore[arg-type]
            "context-001",
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_empty_requested_use_scope(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="requested_use_scope must not be empty",
    ):
        evaluate(requested_use_scope=value)


def test_rejects_non_ascii_requested_use_scope() -> None:
    with pytest.raises(
        ValueError,
        match="requested_use_scope must contain ASCII text only",
    ):
        evaluate(requested_use_scope="campa\u00f1a")


@pytest.mark.parametrize("value", [None, 1, (), []])
def test_rejects_non_text_decision_context_reference(value: object) -> None:
    with pytest.raises(
        TypeError,
        match="decision_context_reference must be text",
    ):
        evaluate_governed_asset_library_use_eligibility(
            make_registry(),
            "asset-001",
            "campaign-web",
            value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_empty_decision_context_reference(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="decision_context_reference must not be empty",
    ):
        evaluate(decision_context_reference=value)


def test_rejects_non_ascii_decision_context_reference() -> None:
    with pytest.raises(
        ValueError,
        match="decision_context_reference must contain ASCII text only",
    ):
        evaluate(decision_context_reference="context-caf\u00e9")


def test_scope_mismatch_returns_ineligible_not_construction_failure() -> None:
    decision = evaluate(requested_use_scope="campaign-print")
    assert decision.decision_value == DECISION_INELIGIBLE


def test_restriction_scope_returns_ineligible() -> None:
    registry = make_registry(
        rights=make_rights(
            permitted_use_scope="campaign-web",
            restriction_scope="campaign-web",
        )
    )
    assert evaluate(registry).decision_value == DECISION_INELIGIBLE


def test_candidate_asset_returns_ineligible() -> None:
    registry = make_registry(
        asset=make_asset(
            lifecycle_state=LIFECYCLE_STATE_CANDIDATE,
            use_eligibility=USE_ELIGIBILITY_INELIGIBLE,
        )
    )
    assert evaluate(registry).decision_value == DECISION_INELIGIBLE


def test_stored_ineligible_asset_returns_ineligible() -> None:
    registry = make_registry(
        asset=make_asset(use_eligibility=USE_ELIGIBILITY_INELIGIBLE)
    )
    assert evaluate(registry).decision_value == DECISION_INELIGIBLE


def test_unverified_rights_returns_ineligible() -> None:
    registry = make_registry(
        rights=make_rights(
            validity_state=VALIDITY_STATE_UNVERIFIED,
            use_authorization=USE_AUTHORIZATION_NOT_AUTHORIZED,
        )
    )
    assert evaluate(registry).decision_value == DECISION_INELIGIBLE


def test_not_authorized_rights_returns_ineligible() -> None:
    registry = make_registry(
        rights=make_rights(
            validity_state=VALIDITY_STATE_ACTIVE,
            use_authorization=USE_AUTHORIZATION_NOT_AUTHORIZED,
        )
    )
    assert evaluate(registry).decision_value == DECISION_INELIGIBLE


def test_function_does_not_mutate_registry_collections() -> None:
    registry = make_registry()
    asset_records_before = registry.asset_records
    rights_records_before = registry.usage_rights_records
    evaluate(registry)
    assert registry.asset_records is asset_records_before
    assert registry.usage_rights_records is rights_records_before


def test_repeated_evaluation_is_deterministic() -> None:
    registry = make_registry()
    first = evaluate(registry)
    second = evaluate(registry)
    assert first == second
    assert first.decision_value == second.decision_value


def test_exact_second_asset_is_selected_from_multi_record_registry() -> None:
    rights_a = make_rights(rights_record_id="rights-A")
    rights_b = make_rights(
        rights_record_id="rights-B",
        permitted_use_scope="campaign-print",
    )
    asset_a = make_asset(
        asset_record_id="asset-A",
        usage_rights_reference="rights-A",
    )
    asset_b = make_asset(
        asset_record_id="asset-B",
        usage_rights_reference="rights-B",
    )
    registry = GovernedAssetLibraryRegistry(
        asset_records=(asset_a, asset_b),
        usage_rights_records=(rights_a, rights_b),
    )

    decision = evaluate(
        registry,
        asset_record_id="asset-B",
        requested_use_scope="campaign-print",
    )

    assert decision.asset_record is asset_b
    assert decision.usage_rights_record is rights_b
    assert decision.decision_value == DECISION_ELIGIBLE
