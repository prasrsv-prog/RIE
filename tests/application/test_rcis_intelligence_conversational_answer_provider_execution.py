from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_answer_provenance import (
    RCISIntelligenceAnswerProvenanceBuilder,
)
from rie.application.rcis_intelligence_context_assembly import (
    RCIS_INTELLIGENCE_CONTEXT_CONTRACT_VERSION,
    RCIS_INTELLIGENCE_CONTEXT_SOURCE_BOUNDARIES,
    RCISIntelligenceContext,
)
from rie.application.rcis_intelligence_conversational_answer_generation import (
    RCISIntelligenceConversationalAnswerGenerator,
    RCISIntelligenceConversationalAnswerInput,
)
from rie.application.rcis_intelligence_conversational_answer_provider_execution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION,
    RCISIntelligenceConversationalAnswerProviderExecutionRequest,
    RCISIntelligenceConversationalAnswerProviderExecutionResponse,
    RCISIntelligenceConversationalAnswerProviderRenderer,
)
from rie.application.rcis_intelligence_conversational_entity_resolution import (
    RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
    RCISConversationalEntityResolution,
    RCISConversationalEntityResolutionBasis,
    RCISConversationalEntityResolutionStatus,
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


def _resolution() -> RCISConversationalEntityResolution:
    return RCISConversationalEntityResolution(
        contract_version=RCIS_INTELLIGENCE_CONVERSATIONAL_ENTITY_RESOLUTION_CONTRACT_VERSION,
        status=RCISConversationalEntityResolutionStatus.RESOLVED,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        resolution_basis=RCISConversationalEntityResolutionBasis.EXACT_VARIANT_ID,
    )


def _answer_input() -> RCISIntelligenceConversationalAnswerInput:
    context = _context()
    resolution = _resolution()
    provenance = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=context,
        resolution=resolution,
    )
    return RCISIntelligenceConversationalAnswerInput(
        utterance="Explain this variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )


def _response(
    *,
    provider_id: str = "provider-a",
    model_id: str = "model-a",
    answer_text: str = "Provider-grounded answer.",
) -> RCISIntelligenceConversationalAnswerProviderExecutionResponse:
    return RCISIntelligenceConversationalAnswerProviderExecutionResponse(
        contract_version=(
            RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
        ),
        provider_id=provider_id,
        model_id=model_id,
        answer_text=answer_text,
    )


def test_renderer_exposes_exact_explicit_provider_and_model_identity() -> None:
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=lambda request: _response(),
    )
    assert renderer.provider_id == "provider-a"
    assert renderer.model_id == "model-a"


def test_renderer_builds_exact_request_and_calls_transport_once() -> None:
    calls = []

    def transport(request):
        calls.append(request)
        return _response()

    answer_input = _answer_input()
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=transport,
    )

    result = renderer(answer_input)

    assert result == "Provider-grounded answer."
    assert len(calls) == 1
    request = calls[0]
    assert request.contract_version == (
        RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
    )
    assert request.provider_id == "provider-a"
    assert request.model_id == "model-a"
    assert request.answer_input is answer_input


def test_renderer_is_directly_compatible_with_governed_answer_generator() -> None:
    calls = []

    def transport(request):
        calls.append(request)
        return _response(answer_text="Exact provider response text.")

    context = _context()
    resolution = _resolution()
    provenance = RCISIntelligenceAnswerProvenanceBuilder().build(
        context=context,
        resolution=resolution,
    )
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=transport,
    )

    answer = RCISIntelligenceConversationalAnswerGenerator(renderer).generate(
        utterance="Explain this variant.",
        context=context,
        resolution=resolution,
        provenance=provenance,
    )

    assert answer.answer_text == "Exact provider response text."
    assert answer.provenance is provenance
    assert len(calls) == 1


def test_request_is_frozen() -> None:
    request = RCISIntelligenceConversationalAnswerProviderExecutionRequest(
        contract_version=(
            RCIS_INTELLIGENCE_CONVERSATIONAL_ANSWER_PROVIDER_EXECUTION_CONTRACT_VERSION
        ),
        provider_id="provider-a",
        model_id="model-a",
        answer_input=_answer_input(),
    )

    with pytest.raises(FrozenInstanceError):
        request.provider_id = "changed"  # type: ignore[misc]


def test_response_is_frozen() -> None:
    response = _response()
    with pytest.raises(FrozenInstanceError):
        response.answer_text = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field_name", "provider_id", "model_id"),
    [
        ("provider_id", "", "model-a"),
        ("provider_id", "   ", "model-a"),
        ("model_id", "provider-a", ""),
        ("model_id", "provider-a", "   "),
    ],
)
def test_blank_provider_or_model_identity_is_rejected_before_execution(
    field_name: str,
    provider_id: str,
    model_id: str,
) -> None:
    calls = []

    def transport(request):
        calls.append(request)
        return _response()

    with pytest.raises(ValueError, match=f"{field_name} must not be empty"):
        RCISIntelligenceConversationalAnswerProviderRenderer(
            provider_id=provider_id,
            model_id=model_id,
            transport=transport,
        )

    assert calls == []


def test_non_callable_transport_is_rejected() -> None:
    with pytest.raises(TypeError, match="transport must be callable"):
        RCISIntelligenceConversationalAnswerProviderRenderer(
            provider_id="provider-a",
            model_id="model-a",
            transport=None,  # type: ignore[arg-type]
        )


def test_non_governed_answer_input_is_rejected_before_transport() -> None:
    calls = []

    def transport(request):
        calls.append(request)
        return _response()

    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=transport,
    )

    with pytest.raises(
        TypeError,
        match="answer_input must be RCISIntelligenceConversationalAnswerInput",
    ):
        renderer(object())  # type: ignore[arg-type]

    assert calls == []


def test_transport_must_return_exact_response_type() -> None:
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=lambda request: "not-a-response",  # type: ignore[return-value]
    )

    with pytest.raises(
        TypeError,
        match="transport response must be",
    ):
        renderer(_answer_input())


def test_response_provider_identity_must_match_request() -> None:
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=lambda request: _response(provider_id="other-provider"),
    )

    with pytest.raises(ValueError, match="provider response provider_id mismatch"):
        renderer(_answer_input())


def test_response_model_identity_must_match_request() -> None:
    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=lambda request: _response(model_id="other-model"),
    )

    with pytest.raises(ValueError, match="provider response model_id mismatch"):
        renderer(_answer_input())


@pytest.mark.parametrize("answer_text", ["", "   "])
def test_response_answer_text_must_be_non_empty(answer_text: str) -> None:
    with pytest.raises(ValueError, match="answer_text must not be empty"):
        _response(answer_text=answer_text)


def test_transport_exception_propagates_without_retry() -> None:
    calls = []

    def transport(request):
        calls.append(request)
        raise RuntimeError("provider transport failure")

    renderer = RCISIntelligenceConversationalAnswerProviderRenderer(
        provider_id="provider-a",
        model_id="model-a",
        transport=transport,
    )

    with pytest.raises(RuntimeError, match="provider transport failure"):
        renderer(_answer_input())

    assert len(calls) == 1
