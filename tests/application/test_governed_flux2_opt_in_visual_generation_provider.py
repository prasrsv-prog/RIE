"""Offline-only governed FLUX.2 composition tests; fake HTTP and temporary rights."""
from __future__ import annotations

import base64
import hashlib
import io

import pytest
from PIL import Image

from rie.application.cloudflare_workers_ai_image_transport import CloudflareWorkersAIHTTPResponse
from rie.application.governed_flux2_opt_in_visual_generation_provider import (
    GovernedFlux2OptInVisualGenerationProvider,
)
from rie.application.governed_visual_reference_read_bridge import (
    GovernedVisualReferenceReadBridge,
    GovernedVisualReferenceReadBridgeContractError,
)
from rie.application.visual_generation_provider import VisualGenerationRequest
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


def _png(width=1024, height=700, rgb=(15, 33, 71)):
    stream = io.BytesIO()
    Image.new("RGB", (width, height), rgb).save(stream, format="PNG")
    return stream.getvalue()


class _Query:
    product_options = ()

    def __init__(self, assets):
        self.assets = {asset.asset_id: (asset, payload) for asset, payload in assets}
        self.read_calls = 0

    def variant_options_for_product(self, product_id):
        return ()

    def list_assets(self, *, product_id, variant_id=None):
        return tuple(asset for asset, _ in self.assets.values() if asset.product_id == product_id)

    def get_asset(self, asset_id):
        return self.assets[asset_id][0]

    def load_preview_bytes(self, asset_id):
        self.read_calls += 1
        return self.assets[asset_id][1]


def _asset(payload, n):
    sha = hashlib.sha256(payload).hexdigest()
    return VisualReferenceAsset(
        reference_id=f"reference-{n}", asset_id=f"asset-{sha}",
        product_id="ffs21", variant_id="ffs21-black-yellow",
        product_label="FFS21", variant_label="Black & Yellow",
        filename=f"reference-{n}.png", source_relative_path=f"FFS21/{n}.png",
        source_type="APPROVED_PRODUCT_PHOTO", authority="RSV_INTERNAL_APPROVED_SOURCE",
        version="2026-08-09", status="APPROVED", sha256=sha, available=True,
    )


def _bridge(tmp_path, pairs, *, rights_state="AUTHORIZED", include_ids=None):
    query = _Query(pairs)
    repo = JsonFileGovernedAssetLibraryRepository(tmp_path / "asset-library.json")
    if include_ids is not None:
        assets = [a for a, _ in pairs if a.asset_id in include_ids]
    else:
        assets = [a for a, _ in pairs]
    if assets:
        records = tuple(GovernedAssetRecord(
            asset_record_id=a.asset_id, provenance_reference=a.reference_id,
            usage_rights_reference="rights-fixture", version_identity=f"sha256:{a.sha256}",
            lifecycle_state="ACTIVE", use_eligibility="ELIGIBLE",
        ) for a in assets)
        rights = (GovernedAssetUsageRights(
            rights_record_id="rights-fixture", rights_holder_reference="offline-fixture-holder",
            permitted_use_scope="creative-reference", restriction_scope="no-redistribution",
            validity_state="ACTIVE", use_authorization=rights_state,
        ),)
        snapshot = build_governed_asset_library_persistence_snapshot(
            asset_records=records, usage_rights_records=rights)
        result = repo.persist_snapshot(GovernedAssetLibraryRepositoryWriteRequest(
            contract_version=GOVERNED_ASSET_LIBRARY_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
            snapshot=snapshot,
        ))
        assert result.status == "written"
    bridge = GovernedVisualReferenceReadBridge(
        visual_reference_query=query, asset_library_repository=repo,
        requested_use_scope="creative-reference", decision_context_reference="c17-offline-test",
    )
    return bridge, query


def _provider(bridge, calls, status=200):
    encoded = base64.b64encode(_png(16, 12)).decode("ascii")
    body = ('{"success":true,"result":{"image":"' + encoded + '"}}').encode("ascii")

    def fake_post(endpoint, headers, multipart):
        calls.append((endpoint, headers, multipart))
        return CloudflareWorkersAIHTTPResponse(status, body if status == 200 else b"{}", "offline-ray")

    return GovernedFlux2OptInVisualGenerationProvider(
        reference_bridge=bridge, account_id="c17-offline", api_token="fake-no-network",
        http_post=fake_post,
    )


def test_missing_governed_snapshot_blocks_before_any_source_bytes_or_http(tmp_path):
    raw = _png()
    a = _asset(raw, 1)
    bridge, query = _bridge(tmp_path, ((a, raw),), include_ids=set())
    calls = []
    with pytest.raises(GovernedVisualReferenceReadBridgeContractError, match="snapshot"):
        _provider(bridge, calls).generate(VisualGenerationRequest("Test", (a.asset_id,)))
    assert query.read_calls == 0 and calls == []


def test_unauthorized_rights_blocks_before_any_source_bytes_or_http(tmp_path):
    raw = _png()
    a = _asset(raw, 1)
    bridge, query = _bridge(tmp_path, ((a, raw),), rights_state="NOT_AUTHORIZED")
    calls = []
    with pytest.raises(GovernedVisualReferenceReadBridgeContractError, match="not eligible"):
        _provider(bridge, calls).generate(VisualGenerationRequest("Test", (a.asset_id,)))
    assert query.read_calls == 0 and calls == []


def test_second_reference_unauthorized_blocks_before_first_source_is_read(tmp_path):
    raw1, raw2 = _png(rgb=(1,2,3)), _png(rgb=(3,2,1))
    a1, a2 = _asset(raw1, 1), _asset(raw2, 2)
    bridge, query = _bridge(tmp_path, ((a1, raw1), (a2, raw2)), include_ids={a1.asset_id})
    calls = []
    with pytest.raises(GovernedVisualReferenceReadBridgeContractError, match="is not governed"):
        _provider(bridge, calls).generate(VisualGenerationRequest("Test", (a1.asset_id, a2.asset_id)))
    assert query.read_calls == 0 and calls == []


@pytest.mark.parametrize("count", [1,2,3,4])
def test_exact_governed_order_and_multipart_without_network(tmp_path, count):
    pairs = tuple((_asset(p, i), p) for i, p in enumerate((_png(rgb=(n+1, n+2, n+3)) for n in range(count)), 1))
    bridge, query = _bridge(tmp_path, pairs)
    calls = []
    ids = tuple(asset.asset_id for asset, _ in pairs)
    response = _provider(bridge, calls).generate(VisualGenerationRequest("Exact grounded helmet prompt", ids))
    assert len(calls) == 1 and query.read_calls == count
    endpoint, headers, multipart = calls[0]
    assert endpoint.endswith("/ai/run/@cf/black-forest-labs/flux-2-klein-4b")
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=rcis-")
    assert [multipart.index(f'name="input_image_{i}"'.encode()) for i in range(count)] == sorted(
        multipart.index(f'name="input_image_{i}"'.encode()) for i in range(count))
    assert multipart.count(b"Content-Type: image/png") == count
    assert response.provider_output_refs[0].startswith("data:image/png;base64,")


def test_http_429_is_not_retried(tmp_path):
    raw = _png()
    a = _asset(raw, 1)
    bridge, _ = _bridge(tmp_path, ((a, raw),))
    calls = []
    with pytest.raises(RuntimeError, match="HTTP 429"):
        _provider(bridge, calls, status=429).generate(VisualGenerationRequest("Test", (a.asset_id,)))
    assert len(calls) == 1


def test_no_implicit_no_reference_mode(tmp_path):
    bridge, query = _bridge(tmp_path, ())
    calls = []
    with pytest.raises(ValueError, match="1 to 4"):
        _provider(bridge, calls).generate(VisualGenerationRequest("Test", ()))
    assert query.read_calls == 0 and calls == []


def test_plain_manifest_query_cannot_bypass_governed_bridge(tmp_path):
    raw = _png()
    a = _asset(raw, 1)
    query = _Query(((a, raw),))
    calls = []
    with pytest.raises(TypeError, match="exact governed visual reference read bridge"):
        _provider(query, calls)
    assert query.read_calls == 0 and calls == []


def test_missing_explicit_http_hook_is_rejected_before_reads(tmp_path):
    raw = _png()
    a = _asset(raw, 1)
    bridge, query = _bridge(tmp_path, ((a, raw),))
    with pytest.raises(TypeError, match="explicit HTTP callable"):
        GovernedFlux2OptInVisualGenerationProvider(
            reference_bridge=bridge, account_id="fixture", api_token="fixture",
            http_post=None,
        )
    assert query.read_calls == 0
