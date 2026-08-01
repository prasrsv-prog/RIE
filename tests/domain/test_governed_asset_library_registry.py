from dataclasses import FrozenInstanceError, fields

import pytest

from rie.domain.governed_asset_library_registry import (
    NOT_FOUND,
    GovernedAssetLibraryRegistry,
)
from rie.domain.governed_asset_record import (
    LIFECYCLE_STATE_ACTIVE,
    USE_ELIGIBILITY_ELIGIBLE,
    GovernedAssetRecord,
)
from rie.domain.governed_asset_usage_rights import (
    USE_AUTHORIZATION_AUTHORIZED,
    VALIDITY_STATE_ACTIVE,
    GovernedAssetUsageRights,
)


def make_rights(
    rights_record_id: str = "rights-001",
    permitted_use_scope: str = "campaign",
) -> GovernedAssetUsageRights:
    return GovernedAssetUsageRights(
        rights_record_id=rights_record_id,
        rights_holder_reference="holder-001",
        permitted_use_scope=permitted_use_scope,
        restriction_scope="restricted-use",
        validity_state=VALIDITY_STATE_ACTIVE,
        use_authorization=USE_AUTHORIZATION_AUTHORIZED,
    )


def make_asset(
    asset_record_id: str = "asset-001",
    usage_rights_reference: str = "rights-001",
    version_identity: str = "version-001",
) -> GovernedAssetRecord:
    return GovernedAssetRecord(
        asset_record_id=asset_record_id,
        provenance_reference="source-001",
        usage_rights_reference=usage_rights_reference,
        version_identity=version_identity,
        lifecycle_state=LIFECYCLE_STATE_ACTIVE,
        use_eligibility=USE_ELIGIBILITY_ELIGIBLE,
    )


def make_registry() -> GovernedAssetLibraryRegistry:
    return GovernedAssetLibraryRegistry(
        asset_records=(make_asset(),),
        usage_rights_records=(make_rights(),),
    )


def test_registry_exposes_exact_public_collections() -> None:
    names = [item.name for item in fields(GovernedAssetLibraryRegistry)]
    assert names[:2] == ["asset_records", "usage_rights_records"]


def test_empty_registry_is_valid() -> None:
    registry = GovernedAssetLibraryRegistry((), ())
    assert registry.asset_records == ()
    assert registry.usage_rights_records == ()


def test_registry_retains_exact_record_tuples() -> None:
    asset = make_asset()
    rights = make_rights()
    registry = GovernedAssetLibraryRegistry((asset,), (rights,))
    assert registry.asset_records == (asset,)
    assert registry.usage_rights_records == (rights,)


def test_registry_is_frozen() -> None:
    registry = make_registry()
    with pytest.raises(FrozenInstanceError):
        registry.asset_records = ()  # type: ignore[misc]


def test_asset_collection_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="asset_records must be a tuple"):
        GovernedAssetLibraryRegistry([], ())  # type: ignore[arg-type]


def test_rights_collection_must_be_tuple() -> None:
    with pytest.raises(TypeError, match="usage_rights_records must be a tuple"):
        GovernedAssetLibraryRegistry((), [])  # type: ignore[arg-type]


def test_asset_collection_rejects_wrong_member_type() -> None:
    with pytest.raises(TypeError, match="GovernedAssetRecord"):
        GovernedAssetLibraryRegistry((object(),), ())  # type: ignore[arg-type]


def test_rights_collection_rejects_wrong_member_type() -> None:
    with pytest.raises(TypeError, match="GovernedAssetUsageRights"):
        GovernedAssetLibraryRegistry((), (object(),))  # type: ignore[arg-type]


def test_duplicate_identical_asset_id_is_rejected() -> None:
    asset = make_asset()
    with pytest.raises(ValueError, match="duplicate asset_record_id"):
        GovernedAssetLibraryRegistry((asset, asset), (make_rights(),))


def test_duplicate_different_asset_record_is_rejected() -> None:
    first = make_asset()
    second = make_asset(version_identity="version-002")
    with pytest.raises(ValueError, match="duplicate asset_record_id"):
        GovernedAssetLibraryRegistry((first, second), (make_rights(),))


def test_duplicate_identical_rights_id_is_rejected() -> None:
    rights = make_rights()
    with pytest.raises(ValueError, match="duplicate rights_record_id"):
        GovernedAssetLibraryRegistry((), (rights, rights))


def test_duplicate_different_rights_record_is_rejected() -> None:
    first = make_rights()
    second = make_rights(permitted_use_scope="editorial")
    with pytest.raises(ValueError, match="duplicate rights_record_id"):
        GovernedAssetLibraryRegistry((), (first, second))


def test_missing_usage_rights_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="missing usage_rights_reference"):
        GovernedAssetLibraryRegistry((make_asset(),), ())


def test_case_mismatched_usage_rights_reference_is_rejected() -> None:
    asset = make_asset(usage_rights_reference="RIGHTS-001")
    with pytest.raises(ValueError, match="missing usage_rights_reference"):
        GovernedAssetLibraryRegistry((asset,), (make_rights(),))


def test_exact_asset_retrieval_returns_registered_record() -> None:
    registry = make_registry()
    assert registry.get_asset_record("asset-001") == make_asset()


def test_exact_rights_retrieval_returns_registered_record() -> None:
    registry = make_registry()
    assert registry.get_usage_rights_record("rights-001") == make_rights()


def test_resolve_usage_rights_by_asset_id() -> None:
    registry = make_registry()
    assert registry.resolve_usage_rights("asset-001") == make_rights()


def test_resolve_usage_rights_by_registered_asset_record() -> None:
    asset = make_asset()
    rights = make_rights()
    registry = GovernedAssetLibraryRegistry((asset,), (rights,))
    assert registry.resolve_usage_rights(asset) is rights


def test_asset_not_found_fails_closed() -> None:
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().get_asset_record("asset-missing")


def test_rights_not_found_fails_closed() -> None:
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().get_usage_rights_record("rights-missing")


def test_asset_lookup_is_case_sensitive() -> None:
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().get_asset_record("ASSET-001")


def test_rights_lookup_is_case_sensitive() -> None:
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().get_usage_rights_record("RIGHTS-001")


@pytest.mark.parametrize("value", ["", "   "])
def test_asset_lookup_rejects_empty_text(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_registry().get_asset_record(value)


@pytest.mark.parametrize("value", ["", "   "])
def test_rights_lookup_rejects_empty_text(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_registry().get_usage_rights_record(value)


def test_asset_lookup_rejects_non_ascii_text() -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_registry().get_asset_record("asset-cafe\N{LATIN SMALL LETTER E WITH ACUTE}")


def test_rights_lookup_rejects_non_ascii_text() -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_registry().get_usage_rights_record("rights-cafe\N{LATIN SMALL LETTER E WITH ACUTE}")


def test_asset_lookup_rejects_non_text() -> None:
    with pytest.raises(TypeError, match="must be text"):
        make_registry().get_asset_record(1)  # type: ignore[arg-type]


def test_rights_lookup_rejects_non_text() -> None:
    with pytest.raises(TypeError, match="must be text"):
        make_registry().get_usage_rights_record(1)  # type: ignore[arg-type]


def test_resolution_rejects_wrong_input_type() -> None:
    with pytest.raises(TypeError, match="GovernedAssetRecord or text"):
        make_registry().resolve_usage_rights(object())  # type: ignore[arg-type]


def test_resolution_rejects_unregistered_asset_id() -> None:
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().resolve_usage_rights("asset-missing")


def test_resolution_rejects_unregistered_asset_record() -> None:
    unregistered = make_asset(
        asset_record_id="asset-002",
        version_identity="version-002",
    )
    with pytest.raises(KeyError, match=NOT_FOUND):
        make_registry().resolve_usage_rights(unregistered)


def test_resolution_rejects_mismatched_registered_record() -> None:
    mismatched = make_asset(version_identity="version-002")
    with pytest.raises(ValueError, match="does not match registered record"):
        make_registry().resolve_usage_rights(mismatched)


def test_unreferenced_rights_record_is_allowed() -> None:
    registry = GovernedAssetLibraryRegistry(
        (make_asset(),),
        (make_rights(), make_rights("rights-002")),
    )
    assert registry.get_usage_rights_record("rights-002").rights_record_id == "rights-002"


def test_input_order_does_not_change_exact_asset_retrieval() -> None:
    asset_one = make_asset()
    asset_two = make_asset(
        asset_record_id="asset-002",
        usage_rights_reference="rights-002",
        version_identity="version-002",
    )
    rights_one = make_rights()
    rights_two = make_rights("rights-002")
    first = GovernedAssetLibraryRegistry(
        (asset_one, asset_two),
        (rights_one, rights_two),
    )
    second = GovernedAssetLibraryRegistry(
        (asset_two, asset_one),
        (rights_two, rights_one),
    )
    assert first.get_asset_record("asset-001") == second.get_asset_record("asset-001")


def test_input_order_does_not_change_exact_reference_resolution() -> None:
    asset_one = make_asset()
    asset_two = make_asset(
        asset_record_id="asset-002",
        usage_rights_reference="rights-002",
        version_identity="version-002",
    )
    rights_one = make_rights()
    rights_two = make_rights("rights-002")
    first = GovernedAssetLibraryRegistry(
        (asset_one, asset_two),
        (rights_one, rights_two),
    )
    second = GovernedAssetLibraryRegistry(
        (asset_two, asset_one),
        (rights_two, rights_one),
    )
    assert first.resolve_usage_rights("asset-002") == second.resolve_usage_rights("asset-002")
