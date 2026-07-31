from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from rie.application.image_evidence_candidate import (
    AcceptedImageExtractionArtifactBinding,
    ImageEvidenceEligibilityDecision,
    ImageEvidenceRelationship,
    ImageEvidenceRelationshipOrigin,
    OfficialImageSourceRevisionBinding,
    evaluate_image_evidence_candidate,
)


def make_source(**changes: object) -> OfficialImageSourceRevisionBinding:
    source = OfficialImageSourceRevisionBinding(
        source_id="image-source-001",
        source_revision="rev-001",
        source_checksum="a" * 64,
        source_authority="RSV_OFFICIAL",
        authority_valid=True,
        rights_state="AUTHORIZED",
        rights_eligible=True,
        lifecycle_state="ACTIVE",
        lifecycle_eligible=True,
        synthetic=True,
    )
    return replace(source, **changes)


def make_artifact(
    **changes: object,
) -> AcceptedImageExtractionArtifactBinding:
    artifact = AcceptedImageExtractionArtifactBinding(
        artifact_id="image-extraction-001",
        artifact_version="1.0",
        artifact_checksum="b" * 64,
        verified_artifact_checksum="b" * 64,
        bound_source_id="image-source-001",
        bound_source_revision="rev-001",
        bound_source_checksum="a" * 64,
        gate13_accepted=True,
        factual_structural_fields=(
            ("height_px", "1080"),
            ("width_px", "1920"),
            ("media_type", "image/png"),
        ),
        synthetic=True,
    )
    return replace(artifact, **changes)


def source_backed_relationship(
    **changes: object,
) -> ImageEvidenceRelationship:
    relationship = ImageEvidenceRelationship(
        relationship_type="SUPPORTS",
        origin=ImageEvidenceRelationshipOrigin.SOURCE_BACKED,
        subject_evidence_id="text-evidence-001",
        object_evidence_id="image-evidence-001",
        provenance_reference="source-record-001",
        authority_reference="authority-record-001",
    )
    return replace(relationship, **changes)


def operator_declared_relationship(
    **changes: object,
) -> ImageEvidenceRelationship:
    relationship = ImageEvidenceRelationship(
        relationship_type="ILLUSTRATES",
        origin=ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED,
        subject_evidence_id="text-evidence-001",
        object_evidence_id="image-evidence-001",
        provenance_reference="operator-declaration-001",
        operator_reference="operator-001",
        declaration_basis="manual governed review",
    )
    return replace(relationship, **changes)


def test_exact_eligible_source_and_accepted_artifact() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.ELIGIBLE
    assert result.candidate is not None
    assert result.candidate.source_id == "image-source-001"
    assert result.candidate.factual_structural_fields == (
        ("height_px", "1080"),
        ("media_type", "image/png"),
        ("width_px", "1920"),
    )

    with pytest.raises(FrozenInstanceError):
        result.candidate.source_id = "changed"  # type: ignore[misc]


def test_source_backed_relationship_with_complete_provenance() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=source_backed_relationship(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.ELIGIBLE
    assert result.candidate is not None
    assert result.candidate.relationship is not None
    assert (
        result.candidate.relationship.origin
        is ImageEvidenceRelationshipOrigin.SOURCE_BACKED
    )


def test_operator_declared_relationship_with_complete_provenance() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=operator_declared_relationship(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.ELIGIBLE
    assert result.candidate is not None
    assert result.candidate.relationship is not None
    assert (
        result.candidate.relationship.origin
        is ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
    )


def test_identical_inputs_produce_identical_result() -> None:
    first = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=source_backed_relationship(),
    )
    second = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=source_backed_relationship(),
    )

    assert first == second


@pytest.mark.parametrize(
    ("source", "artifact", "expected_reason"),
    [
        (
            make_source(source_id="other-source"),
            make_artifact(),
            "SOURCE_ID_MISMATCH",
        ),
        (
            make_source(source_revision="rev-002"),
            make_artifact(),
            "SOURCE_REVISION_MISMATCH",
        ),
        (
            make_source(source_checksum="c" * 64),
            make_artifact(),
            "SOURCE_CHECKSUM_MISMATCH",
        ),
        (
            make_source(),
            make_artifact(verified_artifact_checksum="c" * 64),
            "ARTIFACT_CHECKSUM_MISMATCH",
        ),
        (
            make_source(),
            make_artifact(artifact_version="2.0"),
            "UNSUPPORTED_ARTIFACT_VERSION",
        ),
    ],
)
def test_identity_and_version_fail_closed(
    source: OfficialImageSourceRevisionBinding,
    artifact: AcceptedImageExtractionArtifactBinding,
    expected_reason: str,
) -> None:
    result = evaluate_image_evidence_candidate(
        source=source,
        artifact=artifact,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert result.candidate is None
    assert expected_reason in result.reasons


def test_artifact_not_accepted_under_gate_13_is_ineligible() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(gate13_accepted=False),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.INELIGIBLE
    assert result.reasons == ("ARTIFACT_NOT_ACCEPTED_UNDER_GATE_13",)


def test_invalid_source_authority_is_ineligible() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(authority_valid=False),
        artifact=make_artifact(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.INELIGIBLE
    assert result.reasons == ("SOURCE_AUTHORITY_INVALID",)


def test_rights_not_eligible_is_ineligible() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(rights_eligible=False),
        artifact=make_artifact(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.INELIGIBLE
    assert result.reasons == ("RIGHTS_NOT_ELIGIBLE",)


def test_lifecycle_not_eligible_is_ineligible() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(lifecycle_eligible=False),
        artifact=make_artifact(),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.INELIGIBLE
    assert result.reasons == ("LIFECYCLE_NOT_ELIGIBLE",)


def test_missing_relationship_provenance_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=source_backed_relationship(provenance_reference=""),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert "MISSING_RELATIONSHIP_PROVENANCE" in result.reasons


def test_unknown_relationship_origin_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        relationship=replace(
            source_backed_relationship(),
            origin="AUTOMATIC",
        ),
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert "UNKNOWN_RELATIONSHIP_ORIGIN" in result.reasons


@pytest.mark.parametrize(
    ("artifact", "expected_reason"),
    [
        (
            make_artifact(semantic_fields=(("scene_meaning", "showroom"),)),
            "SEMANTIC_FIELD_PROHIBITED",
        ),
        (
            make_artifact(ocr_derived_fields=(("recognized_text", "RSV"),)),
            "OCR_DERIVED_FIELD_PROHIBITED",
        ),
        (
            make_artifact(model_derived_fields=(("model_label", "helmet"),)),
            "MODEL_DERIVED_FIELD_PROHIBITED",
        ),
    ],
)
def test_derived_fields_fail_closed(
    artifact: AcceptedImageExtractionArtifactBinding,
    expected_reason: str,
) -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=artifact,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert expected_reason in result.reasons


def test_automatic_relationship_inference_attempt_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        automatic_relationship_inference_attempted=True,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert "AUTOMATIC_RELATIONSHIP_INFERENCE_PROHIBITED" in result.reasons


def test_automatic_evidence_to_knowledge_promotion_attempt_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        automatic_evidence_to_knowledge_promotion_attempted=True,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert (
        "AUTOMATIC_EVIDENCE_TO_KNOWLEDGE_PROMOTION_PROHIBITED"
        in result.reasons
    )


def test_automatic_conflict_resolution_attempt_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        automatic_conflict_resolution_attempted=True,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert "AUTOMATIC_CONFLICT_RESOLUTION_PROHIBITED" in result.reasons


def test_real_asset_input_attempt_fails_closed() -> None:
    result = evaluate_image_evidence_candidate(
        source=make_source(),
        artifact=make_artifact(),
        real_asset_input_attempted=True,
    )

    assert result.decision is ImageEvidenceEligibilityDecision.SAFE_STOP
    assert "REAL_ASSET_INPUT_PROHIBITED" in result.reasons
