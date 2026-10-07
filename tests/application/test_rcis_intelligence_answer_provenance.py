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
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
)
from rie.application.rcis_intelligence_answer_provenance import (
    RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION,
    RCISIntelligenceAnswerProvenance,
    RCISIntelligenceAnswerProvenanceBuilder,
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


def _resolution(
    *,
    product_id: str = "sv300",
    variant_id: str | None = "sv300-white-glossy",
    status: RCISConversationalEntityResolutionStatus = RCISConversationalEntityResolutionStatus.RESOLVED,
    basis: RCISConversationalEntityResolutionBasis = RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID,
) -> RCISConversationalEntityResolution:
    return RCISConversationalEntityResolution(
        contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
        status=status,
        product_id=product_id if status is RCISConversationalEntityResolutionStatus.RESOLVED else None,
        variant_id=variant_id if status is RCISConversationalEntityResolutionStatus.RESOLVED else None,
        resolution_basis=basis,
    )


def test_build_signature_requires_named_context_and_resolution() -> None:
    parameters = inspect.signature(RCISIntelligenceAnswerProvenanceBuilder.build).parameters
    assert parameters["context"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["resolution"].kind is inspect.Parameter.KEYWORD_ONLY


def test_build_binds_exact_context_and_resolution_contract_versions() -> None:
    result = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=_context(),
        resolution=_resolution(),
    )
    assert result.contract_version == RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION
    assert result.context_contract_version == RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION
    assert (
        result.entity_resolution_contract_version
        == RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION
    )


def test_build_records_context_and_resolved_entity_identity() -> None:
    result = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=_context(),
        resolution=_resolution(),
    )
    assert result.context_product_id == "sv300"
    assert result.context_variant_id == "sv300-white-glossy"
    assert result.resolved_product_id == "sv300"
    assert result.resolved_variant_id == "sv300-white-glossy"
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID


def test_product_only_resolution_is_preserved_without_inventing_variant_resolution() -> None:
    result = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=_context(),
        resolution=_resolution(
            variant_id=None,
            basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
        ),
    )
    assert result.context_variant_id == "sv300-white-glossy"
    assert result.resolved_variant_id is None
    assert result.resolution_basis is RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID


def test_build_preserves_exact_governed_context_source_boundaries() -> None:
    result = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=_context(),
        resolution=_resolution(),
    )
    assert result.context_source_boundaries is RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES


def test_unresolved_reference_cannot_create_answer_provenance() -> None:
    with pytest.raises(ValueError, match="resolution must be RESOLVED"):
        RCISIntelligenceAnswerProvenanceBuilder().build(
            context=_context(),
            resolution=_resolution(
                status=RCISConversationalEntityResolutionStatus.UNRESOLVED,
                product_id="unused",
                variant_id=None,
                basis=RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE,
            ),
        )


def test_mismatched_product_is_rejected() -> None:
    with pytest.raises(ValueError, match="resolved product does not match governed context"):
        RCISIntelligenceAnswerProvenanceBuilder().build(
            context=_context(),
            resolution=_resolution(product_id="other"),
        )


def test_mismatched_variant_is_rejected() -> None:
    with pytest.raises(ValueError, match="resolved variant does not match governed context"):
        RCISIntelligenceAnswerProvenanceBuilder().build(
            context=_context(),
            resolution=_resolution(variant_id="other-variant"),
        )


def test_non_governed_context_is_rejected() -> None:
    with pytest.raises(TypeError, match="context must be RCISIntelligenceContext"):
        RCISIntelligenceAnswerProvenanceBuilder().build(
            context=object(),  # type: ignore[arg-type]
            resolution=_resolution(),
        )


def test_non_governed_resolution_is_rejected() -> None:
    with pytest.raises(TypeError, match="resolution must be RCISConversationalEntityResolution"):
        RCISIntelligenceAnswerProvenanceBuilder().build(
            context=_context(),
            resolution=object(),  # type: ignore[arg-type]
        )


def test_provenance_result_is_frozen() -> None:
    result = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=_context(),
        resolution=_resolution(),
    )
    with pytest.raises(FrozenInstanceError):
        result.resolved_product_id = "other"  # type: ignore[misc]


def test_direct_contract_rejects_mismatched_resolved_identity() -> None:
    with pytest.raises(ValueError, match="resolved product must match governed context product"):
        RCISIntelligenceAnswerProvenance(
            contract_version=RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION,
            context_contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
            entity_resolution_contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
            context_product_id="sv300",
            context_variant_id="sv300-white-glossy",
            resolved_product_id="other",
            resolved_variant_id=None,
            resolution_basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
            context_source_boundaries=RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
        )
