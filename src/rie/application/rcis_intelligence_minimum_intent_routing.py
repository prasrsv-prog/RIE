"""Minimum governed intent routing for RCIS Intelligence v1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Final


RCIS_INTELLIGENCE_MINIMUM_INTENT_ROUTING_CONTRACT_VERSION: Final[str] = "1.0.0"


class RCISIntelligenceIntent(str, Enum):
    """The only two v1 top-level user intent classes."""

    INFORMATION_ANALYSIS = "INFORMATION_ANALYSIS"
    VISUAL_CREATION = "VISUAL_CREATION"


class RCISIntelligenceCapabilityRoute(str, Enum):
    """Bounded route targets selected by the minimum router."""

    GROUNDED_INFORMATIONAL_TEXT_PATH = "GROUNDED_INFORMATIONAL_TEXT_PATH"
    VISUAL_CREATION_PATH = "VISUAL_CREATION_PATH"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceIntentClassification:
    """Explicit caller-supplied classification with preserved provenance artifact."""

    intent: RCISIntelligenceIntent
    classifier_artifact: object

    def __post_init__(self) -> None:
        if not isinstance(self.intent, RCISIntelligenceIntent):
            raise TypeError("intent must be RCISIntelligenceIntent")
        if self.classifier_artifact is None:
            raise ValueError("classifier_artifact must not be None")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceIntentRoutingResult:
    """Immutable routing decision without downstream execution."""

    contract_version: str
    user_utterance: str
    classification: RCISIntelligenceIntentClassification
    route: RCISIntelligenceCapabilityRoute
    information_analysis_selected: bool
    visual_creation_selected: bool
    downstream_execution_performed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_MINIMUM_INTENT_ROUTING_CONTRACT_VERSION
        ):
            raise ValueError("unsupported minimum intent routing contract version")

        _require_non_empty_text(
            self.user_utterance,
            field_name="user_utterance",
        )

        if not isinstance(
            self.classification,
            RCISIntelligenceIntentClassification,
        ):
            raise TypeError(
                "classification must be RCISIntelligenceIntentClassification"
            )

        if not isinstance(self.route, RCISIntelligenceCapabilityRoute):
            raise TypeError("route must be RCISIntelligenceCapabilityRoute")

        for field_name, value in (
            ("information_analysis_selected", self.information_analysis_selected),
            ("visual_creation_selected", self.visual_creation_selected),
            ("downstream_execution_performed", self.downstream_execution_performed),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if self.downstream_execution_performed:
            raise ValueError(
                "minimum intent router must not perform downstream execution"
            )

        if self.classification.intent is RCISIntelligenceIntent.INFORMATION_ANALYSIS:
            if self.route is not RCISIntelligenceCapabilityRoute.GROUNDED_INFORMATIONAL_TEXT_PATH:
                raise ValueError(
                    "information/analysis intent must route to grounded informational text path"
                )
            if not self.information_analysis_selected or self.visual_creation_selected:
                raise ValueError(
                    "information/analysis selection flags are inconsistent"
                )
            return

        if self.classification.intent is RCISIntelligenceIntent.VISUAL_CREATION:
            if self.route is not RCISIntelligenceCapabilityRoute.VISUAL_CREATION_PATH:
                raise ValueError(
                    "visual-creation intent must route to visual creation path"
                )
            if self.information_analysis_selected or not self.visual_creation_selected:
                raise ValueError(
                    "visual-creation selection flags are inconsistent"
                )
            return

        raise ValueError("unsupported intent")


class RCISIntelligenceMinimumIntentRouter:
    """Classify exactly once, then select exactly one bounded v1 capability route."""

    def __init__(
        self,
        *,
        intent_classifier: Callable[
            [str, object | None],
            RCISIntelligenceIntentClassification,
        ],
    ) -> None:
        if not callable(intent_classifier):
            raise TypeError("intent_classifier must be callable")

        self._intent_classifier = intent_classifier

    def route(
        self,
        *,
        user_utterance: str,
        prior_session_state: object | None = None,
    ) -> RCISIntelligenceIntentRoutingResult:
        _require_non_empty_text(
            user_utterance,
            field_name="user_utterance",
        )

        classification = self._intent_classifier(
            user_utterance,
            prior_session_state,
        )

        if not isinstance(
            classification,
            RCISIntelligenceIntentClassification,
        ):
            raise TypeError(
                "intent_classifier must return "
                "RCISIntelligenceIntentClassification"
            )

        if classification.intent is RCISIntelligenceIntent.INFORMATION_ANALYSIS:
            route = RCISIntelligenceCapabilityRoute.GROUNDED_INFORMATIONAL_TEXT_PATH
            information_analysis_selected = True
            visual_creation_selected = False
        elif classification.intent is RCISIntelligenceIntent.VISUAL_CREATION:
            route = RCISIntelligenceCapabilityRoute.VISUAL_CREATION_PATH
            information_analysis_selected = False
            visual_creation_selected = True
        else:
            raise ValueError("unsupported intent")

        return RCISIntelligenceIntentRoutingResult(
            contract_version=RCIS_INTELLIGENCE_MINIMUM_INTENT_ROUTING_CONTRACT_VERSION,
            user_utterance=user_utterance,
            classification=classification,
            route=route,
            information_analysis_selected=information_analysis_selected,
            visual_creation_selected=visual_creation_selected,
            downstream_execution_performed=False,
        )


__all__ = [
    "RCIS_INTELLIGENCE_MINIMUM_INTENT_ROUTING_CONTRACT_VERSION",
    "RCISIntelligenceCapabilityRoute",
    "RCISIntelligenceIntent",
    "RCISIntelligenceIntentClassification",
    "RCISIntelligenceIntentRoutingResult",
    "RCISIntelligenceMinimumIntentRouter",
]
