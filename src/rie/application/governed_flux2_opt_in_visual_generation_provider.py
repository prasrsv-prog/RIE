"""Explicit governed-asset FLUX.2 visual generation composition boundary.

Not wired to the normal shell. Does not discover credentials, select providers,
read a source image before Gate 15 eligibility, retry, persist outputs, or
invoke network unless the caller separately supplies and calls an HTTP hook.
A manifest APPROVED flag never substitutes for governed use eligibility.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Mapping

from rie.application.cloudflare_workers_ai_flux2_reference_transport import (
    GovernedFlux2PNGReference,
    make_cloudflare_workers_ai_flux2_reference_transport,
)
from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
)
from rie.application.concrete_visual_generation_execution_adapter import (
    ConcreteVisualGenerationExecutionAdapter,
    ResolvedVisualReference,
    VisualGenerationExecutionConfig,
)
from rie.application.governed_reference_derivative_transformer import (
    derive_governed_reference_png,
)
from rie.application.governed_visual_reference_read_bridge import (
    GovernedVisualReferenceReadBridge,
)
from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)

_PROVIDER_ID = "cloudflare-workers-ai"
_MODEL_ID = "@cf/black-forest-labs/flux-2-klein-4b"


@dataclass(frozen=True, slots=True)
class _ReferenceResolver:
    media_by_asset_id: Mapping[str, str]

    def resolve(self, asset_id: str) -> ResolvedVisualReference:
        if asset_id not in self.media_by_asset_id:
            raise ValueError("reference was not included in the governed selection")
        return ResolvedVisualReference(
            requested_asset_id=asset_id,
            resolved_asset_id=asset_id,
            provider_media_ref=self.media_by_asset_id[asset_id],
            use_eligible=True,
        )


class GovernedFlux2OptInVisualGenerationProvider:
    """One explicitly invoked request, with all rights checked before image reads.

    The caller must inject a genuine governed read bridge, account/token values,
    and a separately authorized HTTP callable. This class never looks up any of
    them. It is not connected to UI or a provider service automatically.
    """

    def __init__(
        self,
        *,
        reference_bridge: GovernedVisualReferenceReadBridge,
        account_id: str,
        api_token: str,
        http_post: Callable[[str, Mapping[str, str], bytes], CloudflareWorkersAIHTTPResponse],
    ) -> None:
        if type(reference_bridge) is not GovernedVisualReferenceReadBridge:
            raise TypeError("an exact governed visual reference read bridge is required")
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("an explicit account_id is required")
        if not isinstance(api_token, str) or not api_token.strip():
            raise ValueError("an explicit api_token is required")
        if not callable(http_post):
            raise TypeError("an explicit HTTP callable is required")
        self._bridge = reference_bridge
        self._account_id = account_id
        self._api_token = api_token
        self._http_post = http_post

    def generate(self, request: VisualGenerationRequest) -> VisualGenerationResult:
        if type(request) is not VisualGenerationRequest:
            raise TypeError("request must be an exact VisualGenerationRequest")
        asset_ids = request.selected_reference_asset_ids
        if not 1 <= len(asset_ids) <= 4:
            raise ValueError("FLUX.2 requires exactly 1 to 4 governed references")
        if len(set(asset_ids)) != len(asset_ids):
            raise ValueError("governed asset identities must be unique")

        # Phase 1: check ALL governed records and usage rights before ANY original
        # source image bytes or HTTP operation may be reached.
        assets = []
        for asset_id in asset_ids:
            asset = self._bridge.get_asset(asset_id)
            if asset.asset_id != asset_id or not asset.available or not asset.sha256:
                raise ValueError("governed reference asset identity is invalid")
            assets.append(asset)

        # Phase 2: read only use-eligible bytes, rechecking the official bridge
        # digest at each read. Derivatives are private temporary files only.
        with TemporaryDirectory(prefix="rcis-flux2-governed-") as temp_name:
            temp_root = Path(temp_name)
            ordered_refs = []
            resolver_map: dict[str, str] = {}
            for index, asset in enumerate(assets):
                assert asset.asset_id is not None
                original = self._bridge.load_preview_bytes(asset.asset_id)
                derivative = derive_governed_reference_png(
                    source_asset_id=asset.asset_id,
                    source_path=asset.source_relative_path,
                    source_sha256=asset.sha256,
                    source_bytes=len(original),
                    payload=original,
                )
                path = temp_root / f"reference-{index}.png"
                path.write_bytes(derivative.payload)
                media_ref = asset.asset_id
                ordered_refs.append(
                    GovernedFlux2PNGReference(
                        media_ref=media_ref,
                        local_path=str(path),
                        sha256=derivative.output_sha256,
                        byte_count=derivative.output_bytes,
                        width=derivative.output_width,
                        height=derivative.output_height,
                    )
                )
                resolver_map[asset.asset_id] = media_ref

            transport = make_cloudflare_workers_ai_flux2_reference_transport(
                account_id=self._account_id,
                api_token=self._api_token,
                http_post=self._http_post,
                ordered_references=tuple(ordered_refs),
            )
            adapter = ConcreteVisualGenerationExecutionAdapter(
                config=VisualGenerationExecutionConfig(
                    provider_id=_PROVIDER_ID,
                    model_id=_MODEL_ID,
                ),
                reference_resolver=_ReferenceResolver(resolver_map),
                transport=transport,
            )
            return adapter.generate(request)


__all__ = ["GovernedFlux2OptInVisualGenerationProvider"]
