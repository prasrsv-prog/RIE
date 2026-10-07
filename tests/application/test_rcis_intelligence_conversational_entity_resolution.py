from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
    RCISConversationalEntityResolver,
)


def _context() -> RCISIntelligenceContext:
    return RCISIntelligenceContext(
        contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        product_context=object(),
        visual_reference_assets=(),
        source_boundaries=RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    )


def test_resolve_signature_requires_named_utterance_and_context() -> None:
    parameters = inspect.signature(RCISConversationalEntityResolver.resolve).parameters

    assert parameters["utterance"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["context"].kind is inspect.Parameter.KEYWORD_ONLY


def test_exact_product_id_resolves_product_only() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Tell me about sv300.",
        context=_context(),
    )

    assert result.contract_version == RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION
    assert result.status is RCISConversationalEntityResolutionStatus.RESOLVED
    assert result.product_id == "sv300"
    assert result.variant_id is None
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID


def test_exact_variant_id_resolves_governed_product_and_variant() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Use sv300-white-glossy for this request.",
        context=_context(),
    )

    assert result.status is RCISConversationalEntityResolutionStatus.RESOLVED
    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID


def test_exact_product_and_variant_ids_are_recorded_as_combined_basis() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="For sv300, use sv300-white-glossy.",
        context=_context(),
    )

    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_AND_VARIANT_ID


def test_current_product_deictic_resolves_only_product() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="What is special about this product?",
        context=_context(),
    )

    assert result.product_id == "sv300"
    assert result.variant_id is None
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.CURRENT_PRODUCT_DEICTIC


def test_current_variant_deictic_resolves_product_and_variant() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Use the current variant.",
        context=_context(),
    )

    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.CURRENT_VARIANT_DEICTIC


def test_unsupported_pronoun_remains_unresolved() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Use it for the next step.",
        context=_context(),
    )

    assert result.status is RCISConversationalEntityResolutionStatus.UNRESOLVED
    assert result.product_id is None
    assert result.variant_id is None
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE


def test_partial_identifier_does_not_resolve() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Use sv300-white.",
        context=_context(),
    )

    assert result.status is RCISConversationalEntityResolutionStatus.UNRESOLVED


def test_identifier_matching_is_case_sensitive_and_does_not_guess() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="Use SV300-WHITE-GLOSSY.",
        context=_context(),
    )

    assert result.status is RCISConversationalEntityResolutionStatus.UNRESOLVED


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_is_rejected(utterance: str) -> None:
    with pytest.raises(ValueError, match="utterance must not be empty"):
        RCISConversationalEntityResolver().resolve(
            utterance=utterance,
            context=_context(),
        )


def test_non_string_utterance_is_rejected() -> None:
    with pytest.raises(TypeError, match="utterance must be str"):
        RCISConversationalEntityResolver().resolve(
            utterance=None,  # type: ignore[arg-type]
            context=_context(),
        )


def test_non_governed_context_is_rejected() -> None:
    with pytest.raises(TypeError, match="context must be RCISIntelligenceContext"):
        RCISConversationalEntityResolver().resolve(
            utterance="this product",
            context=object(),  # type: ignore[arg-type]
        )


def test_resolution_result_is_frozen() -> None:
    result = RCISConversationalEntityResolver().resolve(
        utterance="this product",
        context=_context(),
    )

    with pytest.raises(FrozenInstanceError):
        result.product_id = "other"  # type: ignore[misc]
