import json

from rie.asset_library_repository.governed_asset_library_repository_contract import (
    GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
    GovernedAssetLibraryRepositoryWriteRequest,
    build_governed_asset_library_persistence_snapshot,
)
from rie.asset_library_repository.json_file_governed_asset_library_repository import (
    GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION,
    JsonFileGovernedAssetLibraryRepository,
)
from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights


def _rights() -> GovernedAssetUsageRights:
    return GovernedAssetUsageRights(
        rights_record_id="rights-reference-1",
        rights_holder_reference="rights-holder-1",
        permitted_use_scope="creative-reference",
        restriction_scope="no-redistribution",
        validity_state="ACTIVE",
        use_authorization="AUTHORIZED",
    )


def _asset(
    asset_record_id: str = "asset-reference-1",
    version_identity: str = "version-identity-1",
) -> GovernedAssetRecord:
    return GovernedAssetRecord(
        asset_record_id=asset_record_id,
        provenance_reference="provenance-reference-1",
        usage_rights_reference="rights-reference-1",
        version_identity=version_identity,
        lifecycle_state="ACTIVE",
        use_eligibility="ELIGIBLE",
    )


def _request(
    asset_record_id: str = "asset-reference-1",
    version_identity: str = "version-identity-1",
) -> GovernedAssetLibraryRepositoryWriteRequest:
    snapshot = build_governed_asset_library_persistence_snapshot(
        asset_records=(_asset(asset_record_id, version_identity),),
        usage_rights_records=(_rights(),),
    )
    return GovernedAssetLibraryRepositoryWriteRequest(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION
        ),
        snapshot=snapshot,
    )


def test_missing_repository_returns_not_found(tmp_path) -> None:
    result = JsonFileGovernedAssetLibraryRepository(
        tmp_path / "asset-library.json"
    ).load_snapshot()
    assert result.status == "not_found"
    assert result.snapshot is None
    assert result.issue is None


def test_fresh_repository_instance_reloads_exact_snapshot_and_registry(
    tmp_path,
) -> None:
    path = tmp_path / "asset-library.json"
    request = _request()
    written = JsonFileGovernedAssetLibraryRepository(path).persist_snapshot(request)
    assert written.status == "written"
    assert written.mutation_performed is True

    loaded = JsonFileGovernedAssetLibraryRepository(path).load_snapshot()
    assert loaded.status == "found"
    assert loaded.snapshot == request.snapshot
    assert loaded.snapshot is not request.snapshot

    registry = loaded.snapshot.to_registry()
    assert registry.get_asset_record("asset-reference-1") == request.snapshot.asset_records[0]
    assert registry.resolve_usage_rights("asset-reference-1") == (
        request.snapshot.usage_rights_records[0]
    )


def test_same_snapshot_is_idempotent_without_file_mutation(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    request = _request()
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(request).status == "written"
    before = path.read_bytes()

    second = repository.persist_snapshot(request)

    assert second.status == "unchanged"
    assert second.mutation_performed is False
    assert path.read_bytes() == before


def test_new_valid_snapshot_replaces_previous_snapshot(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(_request()).status == "written"

    replacement = _request("asset-reference-2", "version-identity-2")
    result = repository.persist_snapshot(replacement)

    assert result.status == "written"
    assert result.mutation_performed is True
    loaded = JsonFileGovernedAssetLibraryRepository(path).load_snapshot()
    assert loaded.status == "found"
    assert loaded.snapshot == replacement.snapshot


def test_reformatted_payload_fails_closed_and_is_not_overwritten(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    request = _request()
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(request).status == "written"

    payload = json.loads(path.read_text(encoding="ascii"))
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    tampered = path.read_bytes()

    loaded = JsonFileGovernedAssetLibraryRepository(path).load_snapshot()
    assert loaded.status == "rejected"
    assert loaded.issue.code == "invalid_persisted_payload"

    retry = JsonFileGovernedAssetLibraryRepository(path).persist_snapshot(request)
    assert retry.status == "rejected"
    assert retry.mutation_performed is False
    assert retry.issue.code == "existing_payload_invalid"
    assert path.read_bytes() == tampered


def test_digest_drift_fails_closed(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    request = _request()
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(request).status == "written"

    payload = json.loads(path.read_text(encoding="ascii"))
    payload["snapshot"]["snapshot_digest"] = "0" * 64
    path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="ascii",
    )
    corrupted = path.read_bytes()

    assert JsonFileGovernedAssetLibraryRepository(path).load_snapshot().status == "rejected"
    retry = JsonFileGovernedAssetLibraryRepository(path).persist_snapshot(request)
    assert retry.status == "rejected"
    assert path.read_bytes() == corrupted


def test_unsupported_format_and_extra_field_fail_closed(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    request = _request()
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(request).status == "written"

    payload = json.loads(path.read_text(encoding="ascii"))
    payload["format_version"] = "unsupported"
    path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="ascii",
    )
    assert JsonFileGovernedAssetLibraryRepository(path).load_snapshot().status == "rejected"

    path.unlink()
    assert repository.persist_snapshot(request).status == "written"
    payload = json.loads(path.read_text(encoding="ascii"))
    payload["unexpected"] = "value"
    path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        + "\n",
        encoding="ascii",
    )
    assert JsonFileGovernedAssetLibraryRepository(path).load_snapshot().status == "rejected"


def test_missing_parent_and_existing_temp_path_reject_without_mutation(tmp_path) -> None:
    missing_path = tmp_path / "missing" / "asset-library.json"
    missing = JsonFileGovernedAssetLibraryRepository(missing_path)
    result = missing.persist_snapshot(_request())
    assert result.status == "rejected"
    assert result.issue.code == "repository_parent_missing"
    assert not missing_path.exists()

    path = tmp_path / "asset-library.json"
    temp_path = tmp_path / "asset-library.json.rcis-tmp"
    temp_path.write_text("occupied", encoding="ascii")
    result = JsonFileGovernedAssetLibraryRepository(path).persist_snapshot(_request())
    assert result.status == "rejected"
    assert result.issue.code == "temporary_path_exists"
    assert not path.exists()
    assert temp_path.read_text(encoding="ascii") == "occupied"


def test_persisted_payload_contains_only_governed_metadata_fields(tmp_path) -> None:
    path = tmp_path / "asset-library.json"
    repository = JsonFileGovernedAssetLibraryRepository(path)
    assert repository.persist_snapshot(_request()).status == "written"
    payload = json.loads(path.read_text(encoding="ascii"))

    assert payload["format_version"] == GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION
    assert set(payload["snapshot"]) == {
        "contract_version",
        "snapshot_digest",
        "asset_records",
        "usage_rights_records",
    }
    assert set(payload["snapshot"]["asset_records"][0]) == {
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
        "lifecycle_state",
        "use_eligibility",
    }
    assert set(payload["snapshot"]["usage_rights_records"][0]) == {
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
        "validity_state",
        "use_authorization",
    }
