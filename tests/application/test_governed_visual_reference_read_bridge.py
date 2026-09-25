from __future__ import annotations

import hashlib
from types import SimpleNamespace

import pytest

from rie.application.governed_visual_reference_read_bridge import (
    GovernedVisualReferenceReadBridge,
    GovernedVisualReferenceReadBridgeContractError,
)
from rie.application.visual_reference_asset_query import VisualReferenceAsset
from rie.asset_library_repository.governed_asset_library_repository_contract import (
    GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
    GovernedAssetLibraryRepositoryWriteRequest,
    build_governed_asset_library_persistence_snapshot,
)
from rie.asset_library_repository.json_file_governed_asset_library_repository import (
    JsonFileGovernedAssetLibraryRepository,
)
from rie.domain.governed_asset_record import GovernedAssetRecord
from rie.domain.governed_asset_usage_rights import GovernedAssetUsageRights


def _visual_asset(
    payload: bytes = b"approved-photo",
) -> VisualReferenceAsset:
    digest = hashlib.sha256(payload).hexdigest()
    return VisualReferenceAsset(
        reference_id="reference-1",
        asset_id=f"asset-{digest}",
        product_id="sv300",
        variant_id="sv300-white-glossy",
        product_label="SV300",
        variant_label="White Glossy",
        filename="front.png",
        source_relative_path="SV300/White Glossy/front.png",
        source_type="APPROVED_PRODUCT_PHOTO",
        authority="RSV_INTERNAL_APPROVED_SOURCE",
        version="2026-08-09",
        status="APPROVED",
        sha256=digest,
        available=True,
    )


class _FakeVisualReferenceQuery:
    def __init__(self, asset: VisualReferenceAsset, payload: bytes) -> None:
        self.product_options = (
            SimpleNamespace(product_id="sv300", label="SV300"),
        )
        self._asset = asset
        self._payload = payload
        self.preview_call_count = 0

    def variant_options_for_product(self, product_id: str):
        assert product_id == "sv300"
        return (
            SimpleNamespace(
                variant_id="sv300-white-glossy",
                product_id="sv300",
                label="White Glossy",
            ),
        )

    def list_assets(self, *, product_id: str, variant_id: str | None = None):
        assert product_id == "sv300"
        return (self._asset,)

    def get_asset(self, asset_id: str):
        if asset_id != self._asset.asset_id:
            raise ValueError("unknown asset")
        return self._asset

    def load_preview_bytes(self, asset_id: str):
        assert asset_id == self._asset.asset_id
        self.preview_call_count += 1
        return self._payload


def _rights(
    *,
    use_authorization: str = "AUTHORIZED",
) -> GovernedAssetUsageRights:
    return GovernedAssetUsageRights(
        rights_record_id="rights-reference-1",
        rights_holder_reference="rights-holder-1",
        permitted_use_scope="creative-reference",
        restriction_scope="no-redistribution",
        validity_state="ACTIVE",
        use_authorization=use_authorization,
    )


def _asset_record(
    asset: VisualReferenceAsset,
    *,
    version_identity: str | None = None,
) -> GovernedAssetRecord:
    assert asset.asset_id is not None
    return GovernedAssetRecord(
        asset_record_id=asset.asset_id,
        provenance_reference=asset.reference_id,
        usage_rights_reference="rights-reference-1",
        version_identity=(
            version_identity
            if version_identity is not None
            else f"sha256:{asset.sha256}"
        ),
        lifecycle_state="ACTIVE",
        use_eligibility="ELIGIBLE",
    )


def _persist(
    path,
    *,
    asset: VisualReferenceAsset,
    rights: GovernedAssetUsageRights | None = None,
    version_identity: str | None = None,
) -> None:
    snapshot = build_governed_asset_library_persistence_snapshot(
        asset_records=(
            _asset_record(asset, version_identity=version_identity),
        ),
        usage_rights_records=(rights or _rights(),),
    )
    request = GovernedAssetLibraryRepositoryWriteRequest(
        contract_version=(
            GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION
        ),
        snapshot=snapshot,
    )
    result = JsonFileGovernedAssetLibraryRepository(path).persist_snapshot(request)
    assert result.status == "written"


def _bridge(path, query) -> GovernedVisualReferenceReadBridge:
    return GovernedVisualReferenceReadBridge(
        visual_reference_query=query,
        asset_library_repository=JsonFileGovernedAssetLibraryRepository(path),
        requested_use_scope="creative-reference",
        decision_context_reference="visual-reference-selection",
    )


def test_repository_backed_bridge_lists_gets_and_loads_only_governed_asset(
    tmp_path,
) -> None:
    payload = b"approved-photo"
    asset = _visual_asset(payload)
    query = _FakeVisualReferenceQuery(asset, payload)
    path = tmp_path / "asset-library.json"
    _persist(path, asset=asset)

    bridge = _bridge(path, query)

    assert bridge.product_options == query.product_options
    assert bridge.variant_options_for_product("sv300")[0].variant_id == (
        "sv300-white-glossy"
    )
    assert bridge.list_assets(
        product_id="sv300",
        variant_id="sv300-white-glossy",
    ) == (asset,)
    assert bridge.get_asset(asset.asset_id) == asset
    assert query.preview_call_count == 0
    assert bridge.load_preview_bytes(asset.asset_id) == payload
    assert query.preview_call_count == 1


def test_missing_repository_fails_closed(tmp_path) -> None:
    payload = b"approved-photo"
    asset = _visual_asset(payload)
    query = _FakeVisualReferenceQuery(asset, payload)

    bridge = _bridge(tmp_path / "missing.json", query)

    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="snapshot is unavailable",
    ):
        bridge.list_assets(product_id="sv300")


def test_visual_asset_absent_from_governed_registry_is_not_selectable(
    tmp_path,
) -> None:
    payload = b"approved-photo"
    visual_asset = _visual_asset(payload)
    other_payload = b"other"
    other_asset = _visual_asset(other_payload)
    path = tmp_path / "asset-library.json"
    _persist(path, asset=other_asset)
    query = _FakeVisualReferenceQuery(visual_asset, payload)
    bridge = _bridge(path, query)

    assert bridge.list_assets(product_id="sv300") == ()
    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="is not governed",
    ):
        bridge.get_asset(visual_asset.asset_id)


def test_identity_drift_is_not_selectable(tmp_path) -> None:
    payload = b"approved-photo"
    asset = _visual_asset(payload)
    path = tmp_path / "asset-library.json"
    _persist(path, asset=asset, version_identity="sha256:" + ("0" * 64))
    bridge = _bridge(path, _FakeVisualReferenceQuery(asset, payload))

    assert bridge.list_assets(product_id="sv300") == ()
    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="identity drift",
    ):
        bridge.get_asset(asset.asset_id)


def test_unauthorized_rights_are_not_selectable(tmp_path) -> None:
    payload = b"approved-photo"
    asset = _visual_asset(payload)
    path = tmp_path / "asset-library.json"
    _persist(path, asset=asset, rights=_rights(use_authorization="NOT_AUTHORIZED"))
    bridge = _bridge(path, _FakeVisualReferenceQuery(asset, payload))

    assert bridge.list_assets(product_id="sv300") == ()
    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="not eligible",
    ):
        bridge.get_asset(asset.asset_id)


def test_corrupt_repository_fails_closed_before_selection(tmp_path) -> None:
    payload = b"approved-photo"
    asset = _visual_asset(payload)
    path = tmp_path / "asset-library.json"
    path.write_text('{"bad":true}\n', encoding="ascii")
    bridge = _bridge(path, _FakeVisualReferenceQuery(asset, payload))

    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="snapshot is unavailable",
    ):
        bridge.list_assets(product_id="sv300")


def test_preview_payload_is_rechecked_at_bridge_boundary(tmp_path) -> None:
    asset_payload = b"approved-photo"
    asset = _visual_asset(asset_payload)
    path = tmp_path / "asset-library.json"
    _persist(path, asset=asset)
    query = _FakeVisualReferenceQuery(asset, b"drifted-preview")
    bridge = _bridge(path, query)

    with pytest.raises(
        GovernedVisualReferenceReadBridgeContractError,
        match="content drift",
    ):
        bridge.load_preview_bytes(asset.asset_id)
