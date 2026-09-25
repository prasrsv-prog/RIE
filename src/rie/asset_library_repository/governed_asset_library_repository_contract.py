"""Fail-closed persistence contract for the Gate 15 governed asset library."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Final, Protocol, runtime_checkable

from rie.domain.governed_asset_library_registry import GovernedAssetLibraryRegistry
from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights


GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION: Final[str] = (
    "rcis-gate15-governed-asset-library-snapshot-v1"
)
GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION: Final[str] = (
    "rcis-gate15-governed-asset-library-write-request-v1"
)
GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION: Final[str] = (
    "rcis-gate15-governed-asset-library-write-result-v1"
)
GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION: Final[str] = (
    "rcis-gate15-governed-asset-library-lookup-result-v1"
)

_WRITE_STATUSES: Final[frozenset[str]] = frozenset(
    {"written", "unchanged", "rejected"}
)
_LOOKUP_STATUSES: Final[frozenset[str]] = frozenset(
    {"found", "not_found", "rejected"}
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _require_text(value: object, name: str) -> str:
    if type(value) is not str or value == "":
        raise ValueError(f"{name} must be a non-empty string")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be ASCII") from exc
    return value


def _require_sha256(value: object, name: str) -> str:
    value = _require_text(value, name)
    if _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
    return value


def _require_exact_tuple(
    value: object,
    *,
    item_type: type,
    name: str,
) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{name} must be an exact tuple")
    for item in value:
        if type(item) is not item_type:
            raise TypeError(
                f"{name} must contain exact {item_type.__name__} values"
            )
    return value


def _asset_projection(record: GovernedAssetRecord) -> dict[str, str]:
    return {
        "asset_record_id": record.asset_record_id,
        "provenance_reference": record.provenance_reference,
        "usage_rights_reference": record.usage_rights_reference,
        "version_identity": record.version_identity,
        "lifecycle_state": record.lifecycle_state,
        "use_eligibility": record.use_eligibility,
    }


def _rights_projection(record: GovernedAssetUsageRights) -> dict[str, str]:
    return {
        "rights_record_id": record.rights_record_id,
        "rights_holder_reference": record.rights_holder_reference,
        "permitted_use_scope": record.permitted_use_scope,
        "restriction_scope": record.restriction_scope,
        "validity_state": record.validity_state,
        "use_authorization": record.use_authorization,
    }


def canonical_governed_asset_library_snapshot_bytes(
    *,
    asset_records: tuple[GovernedAssetRecord, ...],
    usage_rights_records: tuple[GovernedAssetUsageRights, ...],
) -> bytes:
    asset_records = _require_exact_tuple(
        asset_records,
        item_type=GovernedAssetRecord,
        name="asset_records",
    )
    usage_rights_records = _require_exact_tuple(
        usage_rights_records,
        item_type=GovernedAssetUsageRights,
        name="usage_rights_records",
    )

    # Reuse the existing canonical Gate 15 domain registry as the only
    # authority for duplicate/reference integrity.
    GovernedAssetLibraryRegistry(
        asset_records=asset_records,
        usage_rights_records=usage_rights_records,
    )

    payload = {
        "contract_version": GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION,
        "asset_records": [_asset_projection(item) for item in asset_records],
        "usage_rights_records": [
            _rights_projection(item) for item in usage_rights_records
        ],
    }
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def derive_governed_asset_library_snapshot_digest(
    *,
    asset_records: tuple[GovernedAssetRecord, ...],
    usage_rights_records: tuple[GovernedAssetUsageRights, ...],
) -> str:
    return hashlib.sha256(
        canonical_governed_asset_library_snapshot_bytes(
            asset_records=asset_records,
            usage_rights_records=usage_rights_records,
        )
    ).hexdigest()


@dataclass(frozen=True)
class GovernedAssetLibraryPersistenceSnapshot:
    contract_version: str
    snapshot_digest: str
    asset_records: tuple[GovernedAssetRecord, ...]
    usage_rights_records: tuple[GovernedAssetUsageRights, ...]

    def __post_init__(self) -> None:
        if self.contract_version != GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION:
            raise ValueError("unsupported governed asset library snapshot contract")
        _require_sha256(self.snapshot_digest, "snapshot_digest")
        expected = derive_governed_asset_library_snapshot_digest(
            asset_records=self.asset_records,
            usage_rights_records=self.usage_rights_records,
        )
        if self.snapshot_digest != expected:
            raise ValueError("governed asset library snapshot digest mismatch")

    def to_registry(self) -> GovernedAssetLibraryRegistry:
        return GovernedAssetLibraryRegistry(
            asset_records=self.asset_records,
            usage_rights_records=self.usage_rights_records,
        )


def build_governed_asset_library_persistence_snapshot(
    *,
    asset_records: tuple[GovernedAssetRecord, ...],
    usage_rights_records: tuple[GovernedAssetUsageRights, ...],
) -> GovernedAssetLibraryPersistenceSnapshot:
    digest = derive_governed_asset_library_snapshot_digest(
        asset_records=asset_records,
        usage_rights_records=usage_rights_records,
    )
    return GovernedAssetLibraryPersistenceSnapshot(
        contract_version=GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION,
        snapshot_digest=digest,
        asset_records=asset_records,
        usage_rights_records=usage_rights_records,
    )


@dataclass(frozen=True)
class GovernedAssetLibraryRepositoryIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        _require_text(self.code, "code")
        _require_text(self.message, "message")


@dataclass(frozen=True)
class GovernedAssetLibraryRepositoryWriteRequest:
    contract_version: str
    snapshot: GovernedAssetLibraryPersistenceSnapshot

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported governed asset library write request contract")
        if type(self.snapshot) is not GovernedAssetLibraryPersistenceSnapshot:
            raise TypeError(
                "snapshot must be exact GovernedAssetLibraryPersistenceSnapshot"
            )
        self.snapshot.__post_init__()


@dataclass(frozen=True)
class GovernedAssetLibraryRepositoryWriteResult:
    contract_version: str
    status: str
    mutation_performed: bool
    snapshot_digest: str | None
    issue: GovernedAssetLibraryRepositoryIssue | None

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported governed asset library write result contract")
        if self.status not in _WRITE_STATUSES:
            raise ValueError("unsupported governed asset library write status")
        if type(self.mutation_performed) is not bool:
            raise TypeError("mutation_performed must be bool")

        if self.status == "written":
            if not self.mutation_performed:
                raise ValueError("written result requires mutation_performed")
            _require_sha256(self.snapshot_digest, "snapshot_digest")
            if self.issue is not None:
                raise ValueError("written result must not contain issue")
            return

        if self.status == "unchanged":
            if self.mutation_performed:
                raise ValueError("unchanged result must not mutate")
            _require_sha256(self.snapshot_digest, "snapshot_digest")
            if self.issue is not None:
                raise ValueError("unchanged result must not contain issue")
            return

        if self.mutation_performed:
            raise ValueError("rejected result must not mutate")
        if self.snapshot_digest is not None:
            raise ValueError("rejected result must not expose snapshot_digest")
        if type(self.issue) is not GovernedAssetLibraryRepositoryIssue:
            raise TypeError("rejected result requires exact repository issue")


@dataclass(frozen=True)
class GovernedAssetLibraryRepositoryLookupResult:
    contract_version: str
    status: str
    snapshot: GovernedAssetLibraryPersistenceSnapshot | None
    issue: GovernedAssetLibraryRepositoryIssue | None

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported governed asset library lookup result contract")
        if self.status not in _LOOKUP_STATUSES:
            raise ValueError("unsupported governed asset library lookup status")

        if self.status == "found":
            if type(self.snapshot) is not GovernedAssetLibraryPersistenceSnapshot:
                raise TypeError("found result requires exact persistence snapshot")
            self.snapshot.__post_init__()
            if self.issue is not None:
                raise ValueError("found result must not contain issue")
            return

        if self.snapshot is not None:
            raise ValueError(f"{self.status} result must not contain snapshot")
        if self.status == "not_found":
            if self.issue is not None:
                raise ValueError("not_found result must not contain issue")
            return

        if type(self.issue) is not GovernedAssetLibraryRepositoryIssue:
            raise TypeError("rejected lookup requires exact repository issue")


@runtime_checkable
class GovernedAssetLibraryRepository(Protocol):
    def persist_snapshot(
        self,
        request: GovernedAssetLibraryRepositoryWriteRequest,
    ) -> GovernedAssetLibraryRepositoryWriteResult:
        ...

    def load_snapshot(self) -> GovernedAssetLibraryRepositoryLookupResult:
        ...


__all__ = (
    "GOVERNED_ASSET_LIBRARY_LOOKUP_RESULT_CONTRACT_VERSION",
    "GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION",
    "GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION",
    "GOVERNED_ASSET_LIBRARY_SNAPSHOT_CONTRACT_VERSION",
    "GovernedAssetLibraryPersistenceSnapshot",
    "GovernedAssetLibraryRepository",
    "GovernedAssetLibraryRepositoryIssue",
    "GovernedAssetLibraryRepositoryLookupResult",
    "GovernedAssetLibraryRepositoryWriteRequest",
    "GovernedAssetLibraryRepositoryWriteResult",
    "build_governed_asset_library_persistence_snapshot",
    "canonical_governed_asset_library_snapshot_bytes",
    "derive_governed_asset_library_snapshot_digest",
)
