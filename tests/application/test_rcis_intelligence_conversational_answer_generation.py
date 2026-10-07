from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.application.rcis_intelligence_answer_provenance import (
    RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION,
    RCISIntelligenceAnswerProvenance,
    RCISIntelligenceAnswerProvenanceBuilder,
)
from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION,
    RCISIntelligenceConversationalAnswerGenerator,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
)


def _context(
    *,
    product_id: str = "sv300",
    variant_id: str = "sv300-white-glossy",
) -> RCISIntelligenceContext:
    return RCISIntelligenceContext(
        contract_version=RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
        product_id=product_id,
        variant_id=variant_id,
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


def _provenance(
    *,
    context: RCISIntelligenceContext | None = None,
    resolution: RCISConversationalEntityResolution | None = None,
) -> RCISIntelligenceAnswerProvenance:
    context = _context() if context is None else context
    resolution = _resolution() if resolution is None else resolution
    return RCISIntelligenceAnswerProvenanceBuilder().build(
        context=context,
        resolution=resolution,
    )


def test_generate_signature_requires_named_governed_inputs() -> None:
    parameters = inspect.signature(
        RCISIntelligenceConversationalAnswerGenerator.generate
    ).parameters
    assert parameters["utterance"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["context"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["resolution"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["provenance"].kind is inspect.Parameter.KEYWORD_ONLY


def test_generate_invokes_renderer_once_and_preserves_exact_text() -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        return "The governed RCIS answer."

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    result = RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
        utterance="Tell me about this variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    assert len(calls) == 1
    assert calls[0].utterance == "Tell me about this variant."
    assert calls[0].context is context
    assert calls[0].resolution is resolution
    assert calls[0].provenance is provenance
    assert result.answer_text == "The governed RCIS answer."


def test_generated_answer_retains_exact_provenance_and_resolved_identity() -> None:
    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    result = RCISIntelligenceConversationalAnswerGenerator(
        lambda generation_input: "Grounded answer."
    ).generate(
        utterance="Explain the current variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    assert (
        result.contract_version
        == RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_GENERATION_CONTRACT_VERSION
    )
    assert result.product_id == "sv300"
    assert result.variant_id == "sv300-white-glossy"
    assert result.provenance is provenance
    assert provenance.contract_version == RCIS_INTELLIGENCE_ANSWER_PROVENANCE_CONTRACT_VERSION


def test_product_only_resolution_does_not_invent_variant_identity() -> None:
    context = _context()
    resolution = _resolution(
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
    )
    provenance = _provenance(context=context, resolution=resolution)

    result = RCISIntelligenceConversationalAnswerGenerator(
        lambda generation_input: "Product-level answer."
    ).generate(
        utterance="Tell me about sv300.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    assert result.product_id == "sv300"
    assert result.variant_id is None
    assert result.provenance.resolved_variant_id is None


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_is_rejected_before_renderer(utterance: str) -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        return "should not run"

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    with pytest.raises(ValueError, match="utterance must not be empty"):
        RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
            utterance=utterance,
            context=context,
            resolution=resolution,
            provenance=provenance,
        )

    assert calls == []


def test_unresolved_entity_is_rejected_before_renderer() -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        return "should not run"

    context = _context()
    unresolved = _resolution(
        status=RCISConversationalEntityResolutionStatus.UNRESOLVED,
        product_id="unused",
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.NO_GROUNDED_REFERENCE,
    )

    valid_resolution = _resolution()
    provenance = _provenance(context=context, resolution=valid_resolution)

    with pytest.raises(ValueError, match="resolution must be RESOLVED"):
        RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
            utterance="Use it.",
            context=context,
            resolution=unresolved,
            provenance=provenance,
        )

    assert calls == []


def test_mismatched_context_and_provenance_are_rejected_before_renderer() -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        return "should not run"

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)
    other_context = _context(product_id="other-product", variant_id="other-variant")

    with pytest.raises(ValueError, match="resolved product does not match governed context"):
        RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
            utterance="Explain this product.",
            context=other_context,
            resolution=resolution,
            provenance=provenance,
        )

    assert calls == []


def test_mismatched_resolution_and_provenance_are_rejected_before_renderer() -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        return "should not run"

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)
    product_only_resolution = _resolution(
        variant_id=None,
        basis=RCISConversationalEntityResolutionBasis.EXACT_PRODUCT_ID,
    )

    with pytest.raises(ValueError, match="provenance resolved variant mismatch"):
        RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
            utterance="Explain sv300.",
            context=context,
            resolution=product_only_resolution,
            provenance=provenance,
        )

    assert calls == []


def test_renderer_must_return_string() -> None:
    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    with pytest.raises(TypeError, match="renderer output must be str"):
        RCISIntelligenceConversationalAnswerGenerator(
            lambda generation_input: None  # type: ignore[return-value]
        ).generate(
            utterance="Explain this variant.",
            context=context,
            resolution=resolution,
            provenance=provenance,
        )


def test_renderer_must_return_non_empty_text() -> None:
    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    with pytest.raises(ValueError, match="renderer output must not be empty"):
        RCISIntelligenceConversationalAnswerGenerator(
            lambda generation_input: "   "
        ).generate(
            utterance="Explain this variant.",
            context=context,
            resolution=resolution,
            provenance=provenance,
        )


def test_renderer_exception_propagates_without_retry() -> None:
    calls = []

    def renderer(generation_input):
        calls.append(generation_input)
        raise RuntimeError("renderer failure")

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    with pytest.raises(RuntimeError, match="renderer failure"):
        RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
            utterance="Explain this variant.",
            context=context,
            resolution=resolution,
            provenance=provenance,
        )

    assert len(calls) == 1


def test_generated_answer_is_frozen() -> None:
    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    result = RCISIntelligenceConversationalAnswerGenerator(
        lambda generation_input: "Grounded answer."
    ).generate(
        utterance="Explain this variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    with pytest.raises(FrozenInstanceError):
        result.answer_text = "changed"  # type: ignore[misc]


def test_renderer_input_is_frozen() -> None:
    captured = []

    def renderer(generation_input):
        captured.append(generation_input)
        return "Grounded answer."

    context = _context()
    resolution = _resolution()
    provenance = _provenance(context=context, resolution=resolution)

    RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
        utterance="Explain this variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    with pytest.raises(FrozenInstanceError):
        captured[0].utterance = "changed"  # type: ignore[misc]


def test_non_callable_renderer_is_rejected() -> None:
    with pytest.raises(TypeError, match="renderer must be callable"):
        RCISIntelligenceConversationalAnswerGenerator(None)  # type: ignore[arg-type]
