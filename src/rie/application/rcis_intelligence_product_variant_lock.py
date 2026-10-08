"""Minimum governed product/variant identity lock for RCIS Intelligence v1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final


RCIS_INTELLIGENCE_PRODUCT_VARIANT_LOCK_CONTRACT_VERSION: Final[str] = "1.0.0"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


def _validate_optional_variant_id(value: str | None) -> str | None:
    if value is None:
        return None
    return _require_non_empty_text(value, field_name="variant_id")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceProductVariantLockRequest:
    """Immutable exact product/variant target requested for visual identity lock."""

    user_utterance: str
    product_id: str
    variant_id: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_text(
            self.user_utterance,
            field_name="user_utterance",
        )
        _require_non_empty_text(
            self.product_id,
            field_name="product_id",
        )
        _validate_optional_variant_id(self.variant_id)


@dataclass(frozen=True, slots=True)
class RCISIntelligenceProductVariantIdentityResolution:
    """Authoritative identity resolution returned by the caller-supplied resolver."""

    product_id: str
    variant_id: str | None
    authoritative_identity_artifact: object

    def __post_init__(self) -> None:
        _require_non_empty_text(
            self.product_id,
            field_name="product_id",
        )
        _validate_optional_variant_id(self.variant_id)
        if self.authoritative_identity_artifact is None:
            raise ValueError(
                "authoritative_identity_artifact must not be None"
            )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceProductVariantLockResult:
    """Immutable exact identity lock without creative or visual execution."""

    contract_version: str
    request: RCISIntelligenceProductVariantLockRequest
    resolution: RCISIntelligenceProductVariantIdentityResolution
    locked_product_id: str
    locked_variant_id: str | None
    product_identity_locked: bool
    variant_identity_locked: bool
    creative_intent_constructed: bool
    downstream_visual_execution_performed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_PRODUCT_VARIANT_LOCK_CONTRACT_VERSION
        ):
            raise ValueError("unsupported product/variant lock contract version")

        if not isinstance(
            self.request,
            RCISIntelligenceProductVariantLockRequest,
        ):
            raise TypeError(
                "request must be RCISIntelligenceProductVariantLockRequest"
            )

        if not isinstance(
            self.resolution,
            RCISIntelligenceProductVariantIdentityResolution,
        ):
            raise TypeError(
                "resolution must be "
                "RCISIntelligenceProductVariantIdentityResolution"
            )

        _require_non_empty_text(
            self.locked_product_id,
            field_name="locked_product_id",
        )
        _validate_optional_variant_id(self.locked_variant_id)

        for field_name, value in (
            ("product_identity_locked", self.product_identity_locked),
            ("variant_identity_locked", self.variant_identity_locked),
            ("creative_intent_constructed", self.creative_intent_constructed),
            (
                "downstream_visual_execution_performed",
                self.downstream_visual_execution_performed,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if not self.product_identity_locked:
            raise ValueError("product identity must be locked")

        expected_variant_locked = self.locked_variant_id is not None
        if self.variant_identity_locked is not expected_variant_locked:
            raise ValueError(
                "variant_identity_locked must match locked_variant_id presence"
            )

        if self.creative_intent_constructed:
            raise ValueError(
                "product/variant lock contract must not construct creative intent"
            )

        if self.downstream_visual_execution_performed:
            raise ValueError(
                "product/variant lock contract must not execute visual generation"
            )


class RCISIntelligenceProductVariantLocker:
    """Resolve and lock one exact product/variant identity boundary."""

    def __init__(
        self,
        *,
        identity_resolver: Callable[
            [
                RCISIntelligenceProductVariantLockRequest,
                object | None,
            ],
            RCISIntelligenceProductVariantIdentityResolution,
        ],
    ) -> None:
        if not callable(identity_resolver):
            raise TypeError("identity_resolver must be callable")
        self._identity_resolver = identity_resolver

    def lock(
        self,
        *,
        request: RCISIntelligenceProductVariantLockRequest,
        prior_session_state: object | None = None,
    ) -> RCISIntelligenceProductVariantLockResult:
        if not isinstance(
            request,
            RCISIntelligenceProductVariantLockRequest,
        ):
            raise TypeError(
                "request must be RCISIntelligenceProductVariantLockRequest"
            )

        resolution = self._identity_resolver(
            request,
            prior_session_state,
        )

        if not isinstance(
            resolution,
            RCISIntelligenceProductVariantIdentityResolution,
        ):
            raise TypeError(
                "identity_resolver must return "
                "RCISIntelligenceProductVariantIdentityResolution"
            )

        if resolution.product_id != request.product_id:
            raise ValueError(
                "resolved product_id must exactly match requested product_id"
            )

        if request.variant_id is None:
            if resolution.variant_id is not None:
                raise ValueError(
                    "product-only request must not infer or select a variant"
                )
        elif resolution.variant_id != request.variant_id:
            raise ValueError(
                "resolved variant_id must exactly match requested variant_id"
            )

        return RCISIntelligenceProductVariantLockResult(
            contract_version=RCIS_INTELLIGENCE_PRODUCT_VARIANT_LOCK_CONTRACT_VERSION,
            request=request,
            resolution=resolution,
            locked_product_id=resolution.product_id,
            locked_variant_id=resolution.variant_id,
            product_identity_locked=True,
            variant_identity_locked=resolution.variant_id is not None,
            creative_intent_constructed=False,
            downstream_visual_execution_performed=False,
        )


__all__ = [
    "RCIS_INTELLIGENCE_PRODUCT_VARIANT_LOCK_CONTRACT_VERSION",
    "RCISIntelligenceProductVariantIdentityResolution",
    "RCISIntelligenceProductVariantLocker",
    "RCISIntelligenceProductVariantLockRequest",
    "RCISIntelligenceProductVariantLockResult",
]
