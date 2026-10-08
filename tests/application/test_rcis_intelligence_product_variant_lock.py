from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_product_variant_lock import (
    RCISIntelligenceProductVariantIdentityResolution,
    RCISIntelligenceProductVariantLocker,
    RCISIntelligenceProductVariantLockRequest,
)


def _request(
    *,
    product_id: str = "product-1",
    variant_id: str | None = "variant-1",
) -> RCISIntelligenceProductVariantLockRequest:
    return RCISIntelligenceProductVariantLockRequest(
        user_utterance="Buat visual untuk produk ini.",
        product_id=product_id,
        variant_id=variant_id,
    )


def _resolution(
    *,
    product_id: str = "product-1",
    variant_id: str | None = "variant-1",
    artifact: object | None = None,
) -> RCISIntelligenceProductVariantIdentityResolution:
    return RCISIntelligenceProductVariantIdentityResolution(
        product_id=product_id,
        variant_id=variant_id,
        authoritative_identity_artifact=(
            artifact if artifact is not None else object()
        ),
    )


def test_variant_request_locks_exact_product_and_variant() -> None:
    request = _request()
    artifact = object()
    resolution = _resolution(artifact=artifact)
    calls = []

    def resolver(actual_request, prior_state):
        calls.append((actual_request, prior_state))
        return resolution

    prior_state = object()
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=resolver,
    )

    result = locker.lock(
        request=request,
        prior_session_state=prior_state,
    )

    assert calls == [(request, prior_state)]
    assert result.request is request
    assert result.resolution is resolution
    assert result.resolution.authoritative_identity_artifact is artifact
    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id == "variant-1"
    assert result.product_identity_locked is True
    assert result.variant_identity_locked is True


def test_product_only_request_locks_product_without_variant() -> None:
    request = _request(variant_id=None)
    resolution = _resolution(variant_id=None)
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    )

    result = locker.lock(request=request)

    assert result.locked_product_id == "product-1"
    assert result.locked_variant_id is None
    assert result.product_identity_locked is True
    assert result.variant_identity_locked is False


def test_product_only_request_rejects_silent_variant_selection() -> None:
    request = _request(variant_id=None)
    resolution = _resolution(variant_id="variant-inferred")
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    )

    with pytest.raises(
        ValueError,
        match="product-only request must not infer or select a variant",
    ):
        locker.lock(request=request)


def test_product_mismatch_is_rejected() -> None:
    request = _request(product_id="product-1")
    resolution = _resolution(product_id="product-2")
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    )

    with pytest.raises(
        ValueError,
        match="resolved product_id must exactly match requested product_id",
    ):
        locker.lock(request=request)


def test_variant_mismatch_is_rejected() -> None:
    request = _request(variant_id="variant-1")
    resolution = _resolution(variant_id="variant-2")
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    )

    with pytest.raises(
        ValueError,
        match="resolved variant_id must exactly match requested variant_id",
    ):
        locker.lock(request=request)


def test_identity_resolver_invoked_exactly_once() -> None:
    request = _request()
    calls = []

    def resolver(*args):
        calls.append(args)
        return _resolution()

    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=resolver,
    )
    locker.lock(request=request)

    assert len(calls) == 1


def test_resolver_failure_propagates_without_retry() -> None:
    request = _request()
    calls = []

    def resolver(*args):
        calls.append(args)
        raise RuntimeError("identity failure")

    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=resolver,
    )

    with pytest.raises(RuntimeError, match="identity failure"):
        locker.lock(request=request)

    assert len(calls) == 1


def test_resolver_must_return_exact_resolution_type() -> None:
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: object(),
    )

    with pytest.raises(
        TypeError,
        match="identity_resolver must return",
    ):
        locker.lock(request=_request())


def test_constructor_requires_callable_resolver() -> None:
    with pytest.raises(TypeError, match="identity_resolver must be callable"):
        RCISIntelligenceProductVariantLocker(
            identity_resolver=object(),  # type: ignore[arg-type]
        )


def test_lock_requires_exact_request_type_before_resolver() -> None:
    calls = []
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: calls.append(args),
    )

    with pytest.raises(TypeError, match="request must be"):
        locker.lock(request=object())  # type: ignore[arg-type]

    assert calls == []


@pytest.mark.parametrize(
    ("product_id", "variant_id"),
    [
        ("", "variant-1"),
        ("   ", "variant-1"),
        ("product-1", ""),
        ("product-1", "   "),
    ],
)
def test_blank_identity_fields_are_rejected(
    product_id: str,
    variant_id: str | None,
) -> None:
    with pytest.raises(ValueError):
        _request(product_id=product_id, variant_id=variant_id)


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_is_rejected(utterance: str) -> None:
    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        RCISIntelligenceProductVariantLockRequest(
            user_utterance=utterance,
            product_id="product-1",
            variant_id="variant-1",
        )


def test_authoritative_identity_artifact_is_required() -> None:
    with pytest.raises(
        ValueError,
        match="authoritative_identity_artifact must not be None",
    ):
        RCISIntelligenceProductVariantIdentityResolution(
            product_id="product-1",
            variant_id="variant-1",
            authoritative_identity_artifact=None,
        )


def test_request_is_immutable() -> None:
    request = _request()

    with pytest.raises(FrozenInstanceError):
        request.product_id = "changed"  # type: ignore[misc]


def test_resolution_is_immutable() -> None:
    resolution = _resolution()

    with pytest.raises(FrozenInstanceError):
        resolution.variant_id = "changed"  # type: ignore[misc]


def test_result_is_immutable_and_does_not_construct_or_execute() -> None:
    request = _request()
    resolution = _resolution()
    locker = RCISIntelligenceProductVariantLocker(
        identity_resolver=lambda *args: resolution,
    )

    result = locker.lock(request=request)

    assert result.creative_intent_constructed is False
    assert result.downstream_visual_execution_performed is False

    with pytest.raises(FrozenInstanceError):
        result.locked_product_id = "changed"  # type: ignore[misc]
