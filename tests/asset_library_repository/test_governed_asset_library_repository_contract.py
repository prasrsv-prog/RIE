from dataclasses import FrozenInstanceError
import hashlib
import json

import pytest

from rie.asset_library_repository import (
    GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
    GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
    GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
    GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION,
    GovernedAssetLibraryPersistenceSnapshot,
    GovernedAssetLibraryRepository,
    GovernedAssetLibraryRepositoryIssue,
    GovernedAssetLibraryRepositoryLookupResult,
    GovernedAssetLibraryRepositoryWriteRequest,
    GovernedAssetLibraryRepositoryWriteResult,
    build_governed_asset_library_persistence_snapshot,
    canonical_governed_asset_library_snapshot_bytes,
)
from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights


def _rights(
    rights_record_id: str = "rights-reference-1",
) -> GovernedAssetUsageRights:
    return GovernedAssetUsageRights(
        rights_record_id=rights_record_id,
        rights_holder_reference="rights-holder-1",
        permitted_use_scope="creative-reference",
        restriction_scope="no-redistribution",
        validity_state="ACTIVE",
        use_authorization="AUTHORIZED",
    )


def _asset(
    asset_record_id: str = "asset-reference-1",
    rights_record_id: str = "rights-reference-1",
) -> GovernedAssetRecord:
    return GovernedAssetRecord(
        asset_record_id=asset_record_id,
        provenance_reference="provenance-reference-1",
        usage_rights_reference=rights_record_id,
        version_identity="version-identity-1",
        lifecycle_state="ACTIVE",
        use_eligibility="ELIGIBLE",
    )


def _snapshot() -> GovernedAssetLibraryPersistenceSnapshot:
    return build_governed_asset_library_persistence_snapshot(
        asset_records=(_asset(),),
        usage_rights_records=(_rights(),),
    )


def test_snapshot_is_deterministic_identity_checked_and_reconstructs_registry() -> None:
    first = _snapshot()
    second = _snapshot()

    assert first == second
    assert first.contract_version == GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION
    assert len(first.snapshot_digest) == 64

    payload = canonical_governed_asset_library_snapshot_bytes(
        asset_records=first.asset_records,
        usage_rights_records=first.usage_rights_records,
    )
    assert hashlib.sha256(payload).hexdigest() == first.snapshot_digest

    decoded = json.loads(payload.decode("ascii"))
    assert decoded["asset_records"][0]["asset_record_id"] == "asset-reference-1"
    assert decoded["usage_rights_records"][0]["rights_record_id"] == (
        "rights-reference-1"
    )

    registry = first.to_registry()
    assert registry.get_asset_record("asset-reference-1") == first.asset_records[0]
    assert registry.resolve_usage_rights("asset-reference-1") == (
        first.usage_rights_records[0]
    )


def test_snapshot_rejects_digest_drift_and_broken_reference() -> None:
    valid = _snapshot()
    with pytest.raises(ValueError, match="digest mismatch"):
        GovernedAssetLibraryPersistenceSnapshot(
            contract_version=GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION,
            snapshot_digest="0" * 64,
            asset_records=valid.asset_records,
            usage_rights_records=valid.usage_rights_records,
        )

    with pytest.raises(ValueError):
        build_governed_asset_library_persistence_snapshot(
            asset_records=(_asset(rights_record_id="missing-rights"),),
            usage_rights_records=(_rights(),),
        )


def test_snapshot_rejects_duplicate_asset_and_rights_records() -> None:
    with pytest.raises(ValueError):
        build_governed_asset_library_persistence_snapshot(
            asset_records=(_asset(), _asset()),
            usage_rights_records=(_rights(),),
        )

    with pytest.raises(ValueError):
        build_governed_asset_library_persistence_snapshot(
            asset_records=(_asset(),),
            usage_rights_records=(_rights(), _rights()),
        )


def test_repository_contract_shapes_are_fail_closed() -> None:
    snapshot = _snapshot()
    request = GovernedAssetLibraryRepositoryWriteRequest(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION
        ),
        snapshot=snapshot,
    )
    assert request.snapshot is snapshot

    written = GovernedAssetLibraryRepositoryWriteResult(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
        ),
        status="written",
        mutation_performed=True,
        snapshot_digest=snapshot.snapshot_digest,
        issue=None,
    )
    assert written.mutation_performed is True

    unchanged = GovernedAssetLibraryRepositoryWriteResult(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
        ),
        status="unchanged",
        mutation_performed=False,
        snapshot_digest=snapshot.snapshot_digest,
        issue=None,
    )
    assert unchanged.mutation_performed is False

    issue = GovernedAssetLibraryRepositoryIssue(
        code="invalid_snapshot",
        message="Snapshot failed exact validation.",
    )
    rejected = GovernedAssetLibraryRepositoryWriteResult(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
        ),
        status="rejected",
        mutation_performed=False,
        snapshot_digest=None,
        issue=issue,
    )
    assert rejected.issue is issue

    with pytest.raises(ValueError):
        GovernedAssetLibraryRepositoryWriteResult(
            contract_version=(
                GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            mutation_performed=True,
            snapshot_digest=None,
            issue=issue,
        )


def test_lookup_contract_distinguishes_found_not_found_and_rejected() -> None:
    snapshot = _snapshot()
    found = GovernedAssetLibraryRepositoryLookupResult(
        contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        snapshot=snapshot,
        issue=None,
    )
    assert found.snapshot is snapshot

    not_found = GovernedAssetLibraryRepositoryLookupResult(
        contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="not_found",
        snapshot=None,
        issue=None,
    )
    assert not_found.snapshot is None

    issue = GovernedAssetLibraryRepositoryIssue(
        code="invalid_persisted_payload",
        message="Persisted payload failed exact validation.",
    )
    rejected = GovernedAssetLibraryRepositoryLookupResult(
        contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="rejected",
        snapshot=None,
        issue=issue,
    )
    assert rejected.issue is issue


def test_contract_objects_are_immutable_and_protocol_is_runtime_checkable() -> None:
    snapshot = _snapshot()
    with pytest.raises(FrozenInstanceError):
        snapshot.snapshot_digest = "0" * 64  # type: ignore[misc]

    class RepositoryShape:
        def persist_snapshot(self, request):
            raise NotImplementedError

        def load_snapshot(self):
            raise NotImplementedError

    assert isinstance(RepositoryShape(), GovernedAssetLibraryRepository)
