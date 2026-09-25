"""Canonical single-file persistence backend for the Gate 15 asset library."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final

from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights

from .governed_asset_library_repository_contract import (
    GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
    GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
    GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION,
    GovernedAssetLibraryPersistenceSnapshot,
    GovernedAssetLibraryRepositoryIssue,
    GovernedAssetLibraryRepositoryLookupResult,
    GovernedAssetLibraryRepositoryWriteRequest,
    GovernedAssetLibraryRepositoryWriteResult,
)


GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION: Final[str] = (
    "rcis-gate15-governed-asset-library-json-file-v1"
)

_ASSET_KEYS: Final[frozenset[str]] = frozenset(
    {
        "asset_record_id",
        "provenance_reference",
        "usage_rights_reference",
        "version_identity",
        "lifecycle_state",
        "use_eligibility",
    }
)
_RIGHTS_KEYS: Final[frozenset[str]] = frozenset(
    {
        "rights_record_id",
        "rights_holder_reference",
        "permitted_use_scope",
        "restriction_scope",
        "validity_state",
        "use_authorization",
    }
)
_SNAPSHOT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract_version",
        "snapshot_digest",
        "asset_records",
        "usage_rights_records",
    }
)
_TOP_LEVEL_KEYS: Final[frozenset[str]] = frozenset(
    {"format_version", "snapshot"}
)


def _issue(code: str, message: str) -> GovernedAssetLibraryRepositoryIssue:
    return GovernedAssetLibraryRepositoryIssue(code=code, message=message)


def _asset_dict(record: GovernedAssetRecord) -> dict[str, str]:
    return {
        "asset_record_id": record.asset_record_id,
        "provenance_reference": record.provenance_reference,
        "usage_rights_reference": record.usage_rights_reference,
        "version_identity": record.version_identity,
        "lifecycle_state": record.lifecycle_state,
        "use_eligibility": record.use_eligibility,
    }


def _rights_dict(record: GovernedAssetUsageRights) -> dict[str, str]:
    return {
        "rights_record_id": record.rights_record_id,
        "rights_holder_reference": record.rights_holder_reference,
        "permitted_use_scope": record.permitted_use_scope,
        "restriction_scope": record.restriction_scope,
        "validity_state": record.validity_state,
        "use_authorization": record.use_authorization,
    }


def _canonical_file_bytes(
    snapshot: GovernedAssetLibraryPersistenceSnapshot,
) -> bytes:
    snapshot.__post_init__()
    payload = {
        "format_version": GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION,
        "snapshot": {
            "contract_version": snapshot.contract_version,
            "snapshot_digest": snapshot.snapshot_digest,
            "asset_records": [_asset_dict(item) for item in snapshot.asset_records],
            "usage_rights_records": [
                _rights_dict(item) for item in snapshot.usage_rights_records
            ],
        },
    }
    return (
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        + b"\n"
    )


def _exact_object(value: object, keys: frozenset[str], label: str) -> dict:
    if type(value) is not dict or frozenset(value.keys()) != keys:
        raise ValueError(f"{label} does not match exact contract")
    return value


def _exact_array(value: object, label: str) -> list:
    if type(value) is not list:
        raise ValueError(f"{label} must be an exact JSON array")
    return value


def _decode_snapshot(raw: bytes) -> GovernedAssetLibraryPersistenceSnapshot:
    try:
        payload = json.loads(raw.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("persisted payload is not valid canonical JSON") from exc

    top = _exact_object(payload, _TOP_LEVEL_KEYS, "top-level payload")
    if top["format_version"] != GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION:
        raise ValueError("unsupported file format")

    data = _exact_object(top["snapshot"], _SNAPSHOT_KEYS, "snapshot")
    if data["contract_version"] != GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION:
        raise ValueError("unsupported snapshot contract")

    assets = []
    for item in _exact_array(data["asset_records"], "asset_records"):
        item = _exact_object(item, _ASSET_KEYS, "asset record")
        assets.append(
            GovernedAssetRecord(
                asset_record_id=item["asset_record_id"],
                provenance_reference=item["provenance_reference"],
                usage_rights_reference=item["usage_rights_reference"],
                version_identity=item["version_identity"],
                lifecycle_state=item["lifecycle_state"],
                use_eligibility=item["use_eligibility"],
            )
        )

    rights = []
    for item in _exact_array(data["usage_rights_records"], "usage_rights_records"):
        item = _exact_object(item, _RIGHTS_KEYS, "usage-rights record")
        rights.append(
            GovernedAssetUsageRights(
                rights_record_id=item["rights_record_id"],
                rights_holder_reference=item["rights_holder_reference"],
                permitted_use_scope=item["permitted_use_scope"],
                restriction_scope=item["restriction_scope"],
                validity_state=item["validity_state"],
                use_authorization=item["use_authorization"],
            )
        )

    snapshot = GovernedAssetLibraryPersistenceSnapshot(
        contract_version=data["contract_version"],
        snapshot_digest=data["snapshot_digest"],
        asset_records=tuple(assets),
        usage_rights_records=tuple(rights),
    )
    if raw != _canonical_file_bytes(snapshot):
        raise ValueError("persisted payload is not exact canonical bytes")
    return snapshot


class JsonFileGovernedAssetLibraryRepository:
    """One canonical local file containing one exact governed registry snapshot."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def load_snapshot(self) -> GovernedAssetLibraryRepositoryLookupResult:
        if not self._path.exists():
            return GovernedAssetLibraryRepositoryLookupResult(
                contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
                status="not_found",
                snapshot=None,
                issue=None,
            )
        if not self._path.is_file():
            return self._rejected_lookup(
                "repository_path_invalid",
                "Governed asset library repository path is not a file.",
            )
        try:
            snapshot = _decode_snapshot(self._path.read_bytes())
        except (OSError, TypeError, ValueError):
            return self._rejected_lookup(
                "invalid_persisted_payload",
                "Persisted governed asset library payload failed exact validation.",
            )
        return GovernedAssetLibraryRepositoryLookupResult(
            contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
            status="found",
            snapshot=snapshot,
            issue=None,
        )

    def persist_snapshot(
        self,
        request: GovernedAssetLibraryRepositoryWriteRequest,
    ) -> GovernedAssetLibraryRepositoryWriteResult:
        if type(request) is not GovernedAssetLibraryRepositoryWriteRequest:
            return self._rejected_write(
                "invalid_write_request",
                "Write request must use the exact governed asset library contract.",
            )
        try:
            request.__post_init__()
            desired = _canonical_file_bytes(request.snapshot)
        except (TypeError, ValueError):
            return self._rejected_write(
                "invalid_snapshot",
                "Governed asset library snapshot failed exact validation.",
            )

        parent = self._path.parent
        if not parent.exists() or not parent.is_dir():
            return self._rejected_write(
                "repository_parent_missing",
                "Governed asset library repository parent directory is missing.",
            )

        if self._path.exists():
            current = self.load_snapshot()
            if current.status == "rejected":
                return self._rejected_write(
                    "existing_payload_invalid",
                    "Existing governed asset library payload failed exact validation.",
                )
            if current.status == "found":
                assert current.snapshot is not None
                if current.snapshot.snapshot_digest == request.snapshot.snapshot_digest:
                    return GovernedAssetLibraryRepositoryWriteResult(
                        contract_version=(
                            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
                        ),
                        status="unchanged",
                        mutation_performed=False,
                        snapshot_digest=request.snapshot.snapshot_digest,
                        issue=None,
                    )

        temp_path = self._path.with_name(self._path.name + ".rcis-tmp")
        if temp_path.exists():
            return self._rejected_write(
                "temporary_path_exists",
                "Governed asset library temporary repository path already exists.",
            )
        try:
            temp_path.write_bytes(desired)
            os.replace(temp_path, self._path)
        except OSError:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            return self._rejected_write(
                "repository_write_failed",
                "Governed asset library repository write failed.",
            )

        return GovernedAssetLibraryRepositoryWriteResult(
            contract_version=GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
            status="written",
            mutation_performed=True,
            snapshot_digest=request.snapshot.snapshot_digest,
            issue=None,
        )

    @staticmethod
    def _rejected_lookup(
        code: str,
        message: str,
    ) -> GovernedAssetLibraryRepositoryLookupResult:
        return GovernedAssetLibraryRepositoryLookupResult(
            contract_version=GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION,
            status="rejected",
            snapshot=None,
            issue=_issue(code, message),
        )

    @staticmethod
    def _rejected_write(
        code: str,
        message: str,
    ) -> GovernedAssetLibraryRepositoryWriteResult:
        return GovernedAssetLibraryRepositoryWriteResult(
            contract_version=GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
            status="rejected",
            mutation_performed=False,
            snapshot_digest=None,
            issue=_issue(code, message),
        )


__all__ = (
    "GOVERNED_ASSET_LIBRARY_JSON_FILE_FORMAT_VERSION",
    "JsonFileGovernedAssetLibraryRepository",
)
