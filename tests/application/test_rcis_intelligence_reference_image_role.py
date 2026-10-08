from dataclasses import FrozenInstanceError

import pytest

from rie.application.rcis_intelligence_reference_image_role import (
    RCISIntelligenceReferenceImageInput,
    RCISIntelligenceReferenceImageRole,
    RCISIntelligenceReferenceImageRoleClassification,
    RCISIntelligenceReferenceImageRoleUnderstander,
    RCISIntelligenceReferenceImageSourceAuthority,
)


def _reference(
    reference_id: str,
    authority: RCISIntelligenceReferenceImageSourceAuthority = (
        RCISIntelligenceReferenceImageSourceAuthority.USER_PROVIDED
    ),
) -> RCISIntelligenceReferenceImageInput:
    return RCISIntelligenceReferenceImageInput(
        reference_id=reference_id,
        source_authority=authority,
        reference_artifact=object(),
    )


def _classification(
    reference: RCISIntelligenceReferenceImageInput,
    *roles: RCISIntelligenceReferenceImageRole,
    artifact: object | None = None,
) -> RCISIntelligenceReferenceImageRoleClassification:
    return RCISIntelligenceReferenceImageRoleClassification(
        reference=reference,
        roles=tuple(roles),
        classifier_artifact=artifact if artifact is not None else object(),
    )


def test_understander_preserves_order_and_calls_classifier_once_per_reference() -> None:
    first = _reference("ref-1")
    second = _reference("ref-2")
    calls = []

    def classifier(reference, utterance, prior_state):
        calls.append((reference, utterance, prior_state))
        return _classification(
            reference,
            RCISIntelligenceReferenceImageRole.COMPOSITION_ONLY,
        )

    prior_state = object()
    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=classifier,
    )

    result = understander.understand(
        user_utterance="Gunakan komposisi dua referensi ini.",
        references=(first, second),
        prior_session_state=prior_state,
    )

    assert calls == [
        (first, "Gunakan komposisi dua referensi ini.", prior_state),
        (second, "Gunakan komposisi dua referensi ini.", prior_state),
    ]
    assert result.classifications[0].reference is first
    assert result.classifications[1].reference is second


def test_multiple_roles_are_allowed_but_must_be_unique() -> None:
    reference = _reference("ref-1")

    classification = _classification(
        reference,
        RCISIntelligenceReferenceImageRole.LIGHTING_ONLY,
        RCISIntelligenceReferenceImageRole.MOOD_STYLE_ONLY,
    )

    assert classification.roles == (
        RCISIntelligenceReferenceImageRole.LIGHTING_ONLY,
        RCISIntelligenceReferenceImageRole.MOOD_STYLE_ONLY,
    )


def test_duplicate_roles_are_rejected() -> None:
    reference = _reference("ref-1")

    with pytest.raises(ValueError, match="roles must be unique"):
        _classification(
            reference,
            RCISIntelligenceReferenceImageRole.SCENE_ONLY,
            RCISIntelligenceReferenceImageRole.SCENE_ONLY,
        )


def test_empty_roles_are_rejected() -> None:
    reference = _reference("ref-1")

    with pytest.raises(ValueError, match="roles must not be empty"):
        _classification(reference)


def test_duplicate_reference_ids_are_rejected_before_classifier() -> None:
    calls = []
    first = _reference("same")
    second = _reference("same")

    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda *args: calls.append(args),
    )

    with pytest.raises(
        ValueError,
        match="references must contain unique reference ids",
    ):
        understander.understand(
            user_utterance="Gunakan referensi.",
            references=(first, second),
        )

    assert calls == []


def test_classifier_must_preserve_exact_reference_object() -> None:
    reference = _reference("ref-1")
    replacement = _reference("ref-1")

    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda *args: _classification(
            replacement,
            RCISIntelligenceReferenceImageRole.BACKGROUND_ONLY,
        ),
    )

    with pytest.raises(
        ValueError,
        match="must preserve exact reference object",
    ):
        understander.understand(
            user_utterance="Gunakan background.",
            references=(reference,),
        )


def test_classifier_failure_propagates_without_retry() -> None:
    reference = _reference("ref-1")
    calls = []

    def classifier(*args):
        calls.append(args)
        raise RuntimeError("role failure")

    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=classifier,
    )

    with pytest.raises(RuntimeError, match="role failure"):
        understander.understand(
            user_utterance="Gunakan referensi.",
            references=(reference,),
        )

    assert len(calls) == 1


def test_external_inspiration_is_not_authoritative_for_product_truth() -> None:
    reference = _reference(
        "external-1",
        RCISIntelligenceReferenceImageSourceAuthority.EXTERNAL_INSPIRATION_REFERENCE_ONLY,
    )

    assert reference.authoritative_for_product_truth is False


def test_authoritative_rcis_asset_is_authoritative_for_product_truth() -> None:
    reference = _reference(
        "asset-1",
        RCISIntelligenceReferenceImageSourceAuthority.AUTHORITATIVE_RCIS_ASSET,
    )

    assert reference.authoritative_for_product_truth is True


@pytest.mark.parametrize(
    "authority",
    [
        RCISIntelligenceReferenceImageSourceAuthority.USER_PROVIDED,
        RCISIntelligenceReferenceImageSourceAuthority.APPROVED_COMMERCIAL_USE,
    ],
)
def test_non_rcis_asset_sources_are_not_product_truth_authority(authority) -> None:
    reference = _reference("ref-1", authority)
    assert reference.authoritative_for_product_truth is False


def test_result_does_not_perform_product_lock_creative_intent_or_visual_execution() -> None:
    reference = _reference("ref-1")

    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda ref, *args: _classification(
            ref,
            RCISIntelligenceReferenceImageRole.SCENE_ONLY,
        ),
    )

    result = understander.understand(
        user_utterance="Gunakan scene referensi.",
        references=(reference,),
    )

    assert result.product_variant_lock_performed is False
    assert result.creative_intent_constructed is False
    assert result.downstream_visual_execution_performed is False


def test_input_is_immutable() -> None:
    reference = _reference("ref-1")

    with pytest.raises(FrozenInstanceError):
        reference.reference_id = "changed"  # type: ignore[misc]


def test_classification_is_immutable() -> None:
    reference = _reference("ref-1")
    classification = _classification(
        reference,
        RCISIntelligenceReferenceImageRole.BACKGROUND_ONLY,
    )

    with pytest.raises(FrozenInstanceError):
        classification.roles = ()  # type: ignore[misc]


def test_result_is_immutable() -> None:
    reference = _reference("ref-1")
    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda ref, *args: _classification(
            ref,
            RCISIntelligenceReferenceImageRole.BACKGROUND_ONLY,
        ),
    )

    result = understander.understand(
        user_utterance="Gunakan background.",
        references=(reference,),
    )

    with pytest.raises(FrozenInstanceError):
        result.creative_intent_constructed = True  # type: ignore[misc]


def test_constructor_requires_callable_classifier() -> None:
    with pytest.raises(TypeError, match="role_classifier must be callable"):
        RCISIntelligenceReferenceImageRoleUnderstander(
            role_classifier=object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("utterance", ["", "   "])
def test_blank_utterance_rejected_before_classifier(utterance: str) -> None:
    calls = []
    reference = _reference("ref-1")

    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda *args: calls.append(args),
    )

    with pytest.raises(ValueError, match="user_utterance must not be empty"):
        understander.understand(
            user_utterance=utterance,
            references=(reference,),
        )

    assert calls == []


def test_empty_reference_tuple_rejected_before_classifier() -> None:
    calls = []
    understander = RCISIntelligenceReferenceImageRoleUnderstander(
        role_classifier=lambda *args: calls.append(args),
    )

    with pytest.raises(ValueError, match="references must not be empty"):
        understander.understand(
            user_utterance="Gunakan referensi.",
            references=(),
        )

    assert calls == []
