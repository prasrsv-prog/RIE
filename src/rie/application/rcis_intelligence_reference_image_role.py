"""Minimum governed reference-image role understanding for RCIS Intelligence v1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Final


RCIS_INTELLIGENCE_REFERENCE_IMAGE_ROLE_CONTRACT_VERSION: Final[str] = "1.0.0"


class RCISIntelligenceReferenceImageSourceAuthority(str, Enum):
    """Governed provenance class for one reference image."""

    AUTHORITATIVE_RCIS_ASSET = "AUTHORITATIVE_RCIS_ASSET"
    USER_PROVIDED = "USER_PROVIDED"
    APPROVED_COMMERCIAL_USE = "APPROVED_COMMERCIAL_USE"
    EXTERNAL_INSPIRATION_REFERENCE_ONLY = "EXTERNAL_INSPIRATION_REFERENCE_ONLY"


class RCISIntelligenceReferenceImageRole(str, Enum):
    """Bounded visual roles that a reference may contribute."""

    BACKGROUND_ONLY = "BACKGROUND_ONLY"
    COMPOSITION_ONLY = "COMPOSITION_ONLY"
    LIGHTING_ONLY = "LIGHTING_ONLY"
    MOOD_STYLE_ONLY = "MOOD_STYLE_ONLY"
    SCENE_ONLY = "SCENE_ONLY"


def _require_non_empty_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be str")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceImageInput:
    """Immutable reference image plus its explicit provenance class."""

    reference_id: str
    source_authority: RCISIntelligenceReferenceImageSourceAuthority
    reference_artifact: object

    def __post_init__(self) -> None:
        _require_non_empty_text(self.reference_id, field_name="reference_id")
        if not isinstance(
            self.source_authority,
            RCISIntelligenceReferenceImageSourceAuthority,
        ):
            raise TypeError(
                "source_authority must be "
                "RCISIntelligenceReferenceImageSourceAuthority"
            )
        if self.reference_artifact is None:
            raise ValueError("reference_artifact must not be None")

    @property
    def authoritative_for_product_truth(self) -> bool:
        return (
            self.source_authority
            is RCISIntelligenceReferenceImageSourceAuthority.AUTHORITATIVE_RCIS_ASSET
        )


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceImageRoleClassification:
    """Explicit role classification for exactly one supplied reference."""

    reference: RCISIntelligenceReferenceImageInput
    roles: tuple[RCISIntelligenceReferenceImageRole, ...]
    classifier_artifact: object

    def __post_init__(self) -> None:
        if not isinstance(self.reference, RCISIntelligenceReferenceImageInput):
            raise TypeError(
                "reference must be RCISIntelligenceReferenceImageInput"
            )

        if not isinstance(self.roles, tuple):
            raise TypeError("roles must be tuple")
        if not self.roles:
            raise ValueError("roles must not be empty")

        for role in self.roles:
            if not isinstance(role, RCISIntelligenceReferenceImageRole):
                raise TypeError(
                    "roles must contain only RCISIntelligenceReferenceImageRole"
                )

        if len(set(self.roles)) != len(self.roles):
            raise ValueError("roles must be unique")

        if self.classifier_artifact is None:
            raise ValueError("classifier_artifact must not be None")


@dataclass(frozen=True, slots=True)
class RCISIntelligenceReferenceImageRoleUnderstandingResult:
    """Immutable, ordered reference-role understanding without visual execution."""

    contract_version: str
    user_utterance: str
    classifications: tuple[RCISIntelligenceReferenceImageRoleClassification, ...]
    product_variant_lock_performed: bool
    creative_intent_constructed: bool
    downstream_visual_execution_performed: bool

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != RCIS_INTELLIGENCE_REFERENCE_IMAGE_ROLE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported reference-image role contract version")

        _require_non_empty_text(
            self.user_utterance,
            field_name="user_utterance",
        )

        if not isinstance(self.classifications, tuple):
            raise TypeError("classifications must be tuple")
        if not self.classifications:
            raise ValueError("classifications must not be empty")

        reference_ids: list[str] = []
        for classification in self.classifications:
            if not isinstance(
                classification,
                RCISIntelligenceReferenceImageRoleClassification,
            ):
                raise TypeError(
                    "classifications must contain only "
                    "RCISIntelligenceReferenceImageRoleClassification"
                )
            reference_ids.append(classification.reference.reference_id)

        if len(set(reference_ids)) != len(reference_ids):
            raise ValueError(
                "classifications must contain unique reference ids"
            )

        for field_name, value in (
            ("product_variant_lock_performed", self.product_variant_lock_performed),
            ("creative_intent_constructed", self.creative_intent_constructed),
            (
                "downstream_visual_execution_performed",
                self.downstream_visual_execution_performed,
            ),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool")

        if self.product_variant_lock_performed:
            raise ValueError(
                "reference-image role contract must not perform product/variant lock"
            )
        if self.creative_intent_constructed:
            raise ValueError(
                "reference-image role contract must not construct creative intent"
            )
        if self.downstream_visual_execution_performed:
            raise ValueError(
                "reference-image role contract must not execute visual generation"
            )


class RCISIntelligenceReferenceImageRoleUnderstander:
    """Classify each supplied reference exactly once while preserving input order."""

    def __init__(
        self,
        *,
        role_classifier: Callable[
            [
                RCISIntelligenceReferenceImageInput,
                str,
                object | None,
            ],
            RCISIntelligenceReferenceImageRoleClassification,
        ],
    ) -> None:
        if not callable(role_classifier):
            raise TypeError("role_classifier must be callable")
        self._role_classifier = role_classifier

    def understand(
        self,
        *,
        user_utterance: str,
        references: tuple[RCISIntelligenceReferenceImageInput, ...],
        prior_session_state: object | None = None,
    ) -> RCISIntelligenceReferenceImageRoleUnderstandingResult:
        _require_non_empty_text(
            user_utterance,
            field_name="user_utterance",
        )

        if not isinstance(references, tuple):
            raise TypeError("references must be tuple")
        if not references:
            raise ValueError("references must not be empty")

        reference_ids: list[str] = []
        for reference in references:
            if not isinstance(reference, RCISIntelligenceReferenceImageInput):
                raise TypeError(
                    "references must contain only "
                    "RCISIntelligenceReferenceImageInput"
                )
            reference_ids.append(reference.reference_id)

        if len(set(reference_ids)) != len(reference_ids):
            raise ValueError("references must contain unique reference ids")

        classifications: list[
            RCISIntelligenceReferenceImageRoleClassification
        ] = []

        for reference in references:
            classification = self._role_classifier(
                reference,
                user_utterance,
                prior_session_state,
            )

            if not isinstance(
                classification,
                RCISIntelligenceReferenceImageRoleClassification,
            ):
                raise TypeError(
                    "role_classifier must return "
                    "RCISIntelligenceReferenceImageRoleClassification"
                )

            if classification.reference is not reference:
                raise ValueError(
                    "role_classifier must preserve exact reference object"
                )

            classifications.append(classification)

        return RCISIntelligenceReferenceImageRoleUnderstandingResult(
            contract_version=RCIS_INTELLIGENCE_REFERENCE_IMAGE_ROLE_CONTRACT_VERSION,
            user_utterance=user_utterance,
            classifications=tuple(classifications),
            product_variant_lock_performed=False,
            creative_intent_constructed=False,
            downstream_visual_execution_performed=False,
        )


__all__ = [
    "RCIS_INTELLIGENCE_REFERENCE_IMAGE_ROLE_CONTRACT_VERSION",
    "RCISIntelligenceReferenceImageInput",
    "RCISIntelligenceReferenceImageRole",
    "RCISIntelligenceReferenceImageRoleClassification",
    "RCISIntelligenceReferenceImageRoleUnderstander",
    "RCISIntelligenceReferenceImageRoleUnderstandingResult",
    "RCISIntelligenceReferenceImageSourceAuthority",
]
