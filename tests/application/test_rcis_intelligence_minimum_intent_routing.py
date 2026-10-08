from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_minimum_intent_routing import (
    RCISIntelligenceCapabilityRoute,
    RCISIntelligenceIntent,
    RCISIntelligenceIntentClassification,
    RCISIntelligenceMinimumIntentRouter,
)


def _classification(
    intent: RCISIntelligenceIntent,
    artifact: object | None = None,
) -> RCISIntelligenceIntentClassification:
    return RCISIntelligenceIntentClassification(
        intent=intent,
        classifier_artifact=artifact if artifact is not None else object(),
    )


def test_information_analysis_routes_to_grounded_text_path() -> None:
    classification = _classification(
        RCISIntelligenceIntent.INFORMATION_ANALYSIS,
    )

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda utterance, prior_state: classification,
    )

    result = router.route(
        user_utterance="Apa keunggulan Product A?",
    )

    assert result.classification is classification
    assert (
        result.route
        is RCISIntelligenceCapabilityRoute.GROUNDED_INFORMATIONAL_TEXT_PATH
    )
    assert result.information_analysis_selected is True
    assert result.visual_creation_selected is False
    assert result.downstream_execution_performed is False


def test_visual_creation_routes_to_visual_creation_path() -> None:
    classification = _classification(
        RCISIntelligenceIntent.VISUAL_CREATION,
    )

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda utterance, prior_state: classification,
    )

    result = router.route(
        user_utterance="Buat visual Product A di studio gelap.",
    )

    assert result.classification is classification
    assert result.route is RCISIntelligenceCapabilityRoute.VISUAL_CREATION_PATH
    assert result.information_analysis_selected is False
    assert result.visual_creation_selected is True
    assert result.downstream_execution_performed is False


def test_classifier_is_invoked_once_with_exact_inputs() -> None:
    calls = []
    prior_state = object()
    artifact = object()
    classification = _classification(
        RCISIntelligenceIntent.INFORMATION_ANALYSIS,
        artifact=artifact,
    )

    def classifier(utterance, received_prior_state):
        calls.append((utterance, received_prior_state))
        return classification

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=classifier,
    )

    result = router.route(
        user_utterance="Bandingkan dua varian.",
        prior_session_state=prior_state,
    )

    assert calls == [("Bandingkan dua varian.", prior_state)]
    assert result.classification.classifier_artifact is artifact


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_rejected_before_classifier(utterance: str) -> None:
    calls = []

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda *args: calls.append(args),
    )

    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        router.route(user_utterance=utterance)

    assert calls == []


def test_classifier_must_return_exact_classification_type() -> None:
    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda utterance, prior_state: object(),
    )

    with pytest.raises(TypeError, match="intent_classifier must return"):
        router.route(user_utterance="Jelaskan Product A.")


def test_classifier_failure_propagates_without_retry() -> None:
    calls = []

    def classifier(utterance, prior_state):
        calls.append((utterance, prior_state))
        raise RuntimeError("classification failure")

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=classifier,
    )

    with pytest.raises(RuntimeError, match="classification failure"):
        router.route(user_utterance="Buat visual produk.")

    assert len(calls) == 1


def test_classification_is_immutable() -> None:
    classification = _classification(
        RCISIntelligenceIntent.INFORMATION_ANALYSIS,
    )

    with pytest.raises(FrozenInstanceError):
        classification.intent = RCISIntelligenceIntent.VISUAL_CREATION  # type: ignore[misc]


def test_routing_result_is_immutable() -> None:
    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda *args: _classification(
            RCISIntelligenceIntent.INFORMATION_ANALYSIS,
        ),
    )

    result = router.route(user_utterance="Jelaskan produk.")

    with pytest.raises(FrozenInstanceError):
        result.visual_creation_selected = True  # type: ignore[misc]


def test_classification_requires_classifier_artifact() -> None:
    with pytest.raises(
        ValueError,
        match="classifier_artifact must not be None",
    ):
        RCISIntelligenceIntentClassification(
            intent=RCISIntelligenceIntent.INFORMATION_ANALYSIS,
            classifier_artifact=None,
        )


def test_classification_requires_exact_intent_enum() -> None:
    with pytest.raises(TypeError, match="intent must be RCISIntelligenceIntent"):
        RCISIntelligenceIntentClassification(
            intent="INFORMATION_ANALYSIS",  # type: ignore[arg-type]
            classifier_artifact=object(),
        )


def test_constructor_requires_callable_classifier() -> None:
    with pytest.raises(TypeError, match="intent_classifier must be callable"):
        RCISIntelligenceMinimumIntentRouter(
            intent_classifier=object(),  # type: ignore[arg-type]
        )


def test_router_does_not_execute_grounded_text_path() -> None:
    calls = []

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda *args: _classification(
            RCISIntelligenceIntent.INFORMATION_ANALYSIS,
        ),
    )

    result = router.route(user_utterance="Apa spesifikasinya?")

    assert calls == []
    assert result.downstream_execution_performed is False


def test_router_does_not_execute_visual_creation_path() -> None:
    calls = []

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda *args: _classification(
            RCISIntelligenceIntent.VISUAL_CREATION,
        ),
    )

    result = router.route(user_utterance="Buat poster produk.")

    assert calls == []
    assert result.downstream_execution_performed is False


def test_explicit_classifier_artifact_identity_is_preserved() -> None:
    artifact = {"source": "explicit-classifier"}
    classification = _classification(
        RCISIntelligenceIntent.VISUAL_CREATION,
        artifact=artifact,
    )

    router = RCISIntelligenceMinimumIntentRouter(
        intent_classifier=lambda *args: classification,
    )

    result = router.route(user_utterance="Buat visual produk.")

    assert result.classification is classification
    assert result.classification.classifier_artifact is artifact
