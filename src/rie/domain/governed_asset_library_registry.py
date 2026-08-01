from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, Mapping

from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights

NOT_FOUND: Final = "NOT_FOUND"


def _validate_lookup_id(field_name: str, value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")
    return value


@dataclass(frozen=True)
class GovernedAssetLibraryRegistry:
    """Minimum immutable in-memory exact-reference Gate 15 registry."""

    asset_records: tuple[GovernedAssetRecord, ...]
    usage_rights_records: tuple[GovernedAssetUsageRights, ...]
    _asset_records_by_id: Mapping[str, GovernedAssetRecord] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _usage_rights_records_by_id: Mapping[
        str,
        GovernedAssetUsageRights,
    ] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not isinstance(self.asset_records, tuple):
            raise TypeError("asset_records must be a tuple")
        if not isinstance(self.usage_rights_records, tuple):
            raise TypeError("usage_rights_records must be a tuple")

        asset_records_by_id: dict[str, GovernedAssetRecord] = {}
        for asset_record in self.asset_records:
            if not isinstance(asset_record, GovernedAssetRecord):
                raise TypeError(
                    "asset_records must contain GovernedAssetRecord values"
                )
            if asset_record.asset_record_id in asset_records_by_id:
                raise ValueError("duplicate asset_record_id")
            asset_records_by_id[asset_record.asset_record_id] = asset_record

        usage_rights_records_by_id: dict[
            str,
            GovernedAssetUsageRights,
        ] = {}
        for usage_rights_record in self.usage_rights_records:
            if not isinstance(
                usage_rights_record,
                GovernedAssetUsageRights,
            ):
                raise TypeError(
                    "usage_rights_records must contain "
                    "GovernedAssetUsageRights values"
                )
            if (
                usage_rights_record.rights_record_id
                in usage_rights_records_by_id
            ):
                raise ValueError("duplicate rights_record_id")
            usage_rights_records_by_id[
                usage_rights_record.rights_record_id
            ] = usage_rights_record

        for asset_record in self.asset_records:
            if (
                asset_record.usage_rights_reference
                not in usage_rights_records_by_id
            ):
                raise ValueError("missing usage_rights_reference")

        object.__setattr__(
            self,
            "_asset_records_by_id",
            MappingProxyType(asset_records_by_id),
        )
        object.__setattr__(
            self,
            "_usage_rights_records_by_id",
            MappingProxyType(usage_rights_records_by_id),
        )

    def get_asset_record(self, asset_record_id: str) -> GovernedAssetRecord:
        exact_id = _validate_lookup_id("asset_record_id", asset_record_id)
        try:
            return self._asset_records_by_id[exact_id]
        except KeyError as error:
            raise KeyError(NOT_FOUND) from error

    def get_usage_rights_record(
        self,
        rights_record_id: str,
    ) -> GovernedAssetUsageRights:
        exact_id = _validate_lookup_id("rights_record_id", rights_record_id)
        try:
            return self._usage_rights_records_by_id[exact_id]
        except KeyError as error:
            raise KeyError(NOT_FOUND) from error

    def resolve_usage_rights(
        self,
        asset_record_or_id: GovernedAssetRecord | str,
    ) -> GovernedAssetUsageRights:
        if isinstance(asset_record_or_id, str):
            asset_record = self.get_asset_record(asset_record_or_id)
        elif isinstance(asset_record_or_id, GovernedAssetRecord):
            asset_record = self.get_asset_record(
                asset_record_or_id.asset_record_id
            )
            if asset_record != asset_record_or_id:
                raise ValueError("asset record does not match registered record")
        else:
            raise TypeError(
                "asset_record_or_id must be a GovernedAssetRecord or text"
            )

        return self.get_usage_rights_record(
            asset_record.usage_rights_reference
        )
