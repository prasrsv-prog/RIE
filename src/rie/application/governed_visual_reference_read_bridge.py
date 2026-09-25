"""Application-facing governed visual-reference read bridge for Gate 15."""

from __future__ import annotations

import hashlib
from typing import Any, Final

from rie.application.visual_reference_asset_query import (
    VisualReferenceAsset,
)
from rie.asset_library_repository.governed_asset_library_repository_contract import (
    GovernedAssetLibraryRepositoryLookupResult,
)
from rie.domain.evaluate_governed_asset_library_use_eligibility import (
    evaluate_governed_asset_library_use_eligibility,
)
from rie.domain.governed_asset_library_registry import GovernedAssetLibraryRegistry
from rie.domain.governed_asset_use_eligibility import DECISION_ELIGIBLE


VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX: Final[str] = "sha256:"


class GovernedVisualReferenceReadBridgeContractError(ValueError):
    """Fail-closed error for repository-backed visual-reference reads."""


def _required_ascii_text(value: object, field_name: str) -> str:
    if type(value) is not str or value == "" or not value.strip():
        raise GovernedVisualReferenceReadBridgeContractError(
            f"{field_name} must be nonempty text"
        )
    if not value.isascii():
        raise GovernedVisualReferenceReadBridgeContractError(
            f"{field_name} must contain ASCII text only"
        )
    return value


class GovernedVisualReferenceReadBridge:
    """Expose visual references only after exact persisted governance checks."""

    def __init__(
        self,
        *,
        visual_reference_query: Any,
        asset_library_repository: Any,
        requested_use_scope: str,
        decision_context_reference: str,
    ) -> None:
        for method_name in (
            "variant_options_for_product",
            "list_assets",
            "get_asset",
            "load_preview_bytes",
        ):
            if not callable(getattr(visual_reference_query, method_name, None)):
                raise GovernedVisualReferenceReadBridgeContractError(
                    "visual_reference_query does not expose the required read boundary"
                )
        if not hasattr(visual_reference_query, "product_options"):
            raise GovernedVisualReferenceReadBridgeContractError(
                "visual_reference_query must expose product_options"
            )
        if not callable(getattr(asset_library_repository, "load_snapshot", None)):
            raise GovernedVisualReferenceReadBridgeContractError(
                "asset_library_repository must expose load_snapshot"
            )

        self._visual_reference_query = visual_reference_query
        self._repository = asset_library_repository
        self._requested_use_scope = _required_ascii_text(
            requested_use_scope,
            "requested_use_scope",
        )
        self._decision_context_reference = _required_ascii_text(
            decision_context_reference,
            "decision_context_reference",
        )

    @property
    def product_options(self) -> tuple[Any, ...]:
        return tuple(self._visual_reference_query.product_options)

    def variant_options_for_product(self, product_id: str) -> tuple[Any, ...]:
        return tuple(
            self._visual_reference_query.variant_options_for_product(product_id)
        )

    def list_assets(
        self,
        *,
        product_id: str,
        variant_id: str | None = None,
    ) -> tuple[VisualReferenceAsset, ...]:
        registry = self._load_registry()
        output: list[VisualReferenceAsset] = []
        for asset in self._visual_reference_query.list_assets(
            product_id=product_id,
            variant_id=variant_id,
        ):
            if type(asset) is not VisualReferenceAsset:
                raise GovernedVisualReferenceReadBridgeContractError(
                    "visual_reference_query returned an invalid asset value"
                )
            if self._eligible_or_false(asset, registry):
                output.append(asset)
        return tuple(output)

    def get_asset(self, asset_id: str) -> VisualReferenceAsset:
        asset = self._visual_reference_query.get_asset(asset_id)
        if type(asset) is not VisualReferenceAsset:
            raise GovernedVisualReferenceReadBridgeContractError(
                "visual_reference_query returned an invalid asset value"
            )
        registry = self._load_registry()
        self._require_eligible(asset, registry)
        return asset

    def load_preview_bytes(self, asset_id: str) -> bytes:
        asset = self.get_asset(asset_id)
        payload = self._visual_reference_query.load_preview_bytes(asset_id)
        if type(payload) is not bytes:
            raise GovernedVisualReferenceReadBridgeContractError(
                "visual_reference_query returned non-bytes preview content"
            )
        if hashlib.sha256(payload).hexdigest() != asset.sha256:
            raise GovernedVisualReferenceReadBridgeContractError(
                f"visual reference asset content drift: {asset_id}"
            )
        return payload

    def _load_registry(self) -> GovernedAssetLibraryRegistry:
        result = self._repository.load_snapshot()
        if type(result) is not GovernedAssetLibraryRepositoryLookupResult:
            raise GovernedVisualReferenceReadBridgeContractError(
                "asset library repository returned an invalid lookup result"
            )
        try:
            result.__post_init__()
        except (TypeError, ValueError) as exc:
            raise GovernedVisualReferenceReadBridgeContractError(
                "asset library repository result failed exact validation"
            ) from exc

        if result.status != "found" or result.snapshot is None:
            raise GovernedVisualReferenceReadBridgeContractError(
                "governed asset library snapshot is unavailable"
            )
        try:
            return result.snapshot.to_registry()
        except (TypeError, ValueError) as exc:
            raise GovernedVisualReferenceReadBridgeContractError(
                "governed asset library snapshot cannot reconstruct registry"
            ) from exc

    def _eligible_or_false(
        self,
        asset: VisualReferenceAsset,
        registry: GovernedAssetLibraryRegistry,
    ) -> bool:
        try:
            self._require_eligible(asset, registry)
        except GovernedVisualReferenceReadBridgeContractError:
            return False
        return True

    def _require_eligible(
        self,
        asset: VisualReferenceAsset,
        registry: GovernedAssetLibraryRegistry,
    ) -> None:
        if not asset.available or asset.asset_id is None or not asset.sha256:
            raise GovernedVisualReferenceReadBridgeContractError(
                "visual reference asset is unavailable"
            )

        try:
            asset_record = registry.get_asset_record(asset.asset_id)
        except (KeyError, TypeError, ValueError) as exc:
            raise GovernedVisualReferenceReadBridgeContractError(
                f"visual reference asset is not governed: {asset.asset_id}"
            ) from exc

        expected_version_identity = (
            VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX + asset.sha256
        )
        if asset_record.version_identity != expected_version_identity:
            raise GovernedVisualReferenceReadBridgeContractError(
                f"visual reference asset identity drift: {asset.asset_id}"
            )

        try:
            decision = evaluate_governed_asset_library_use_eligibility(
                registry,
                asset.asset_id,
                self._requested_use_scope,
                self._decision_context_reference,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GovernedVisualReferenceReadBridgeContractError(
                f"visual reference asset governance evaluation failed: {asset.asset_id}"
            ) from exc

        if decision.decision_value != DECISION_ELIGIBLE:
            raise GovernedVisualReferenceReadBridgeContractError(
                f"visual reference asset is not eligible for requested use: {asset.asset_id}"
            )


__all__ = (
    "VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX",
    "GovernedVisualReferenceReadBridge",
    "GovernedVisualReferenceReadBridgeContractError",
)
