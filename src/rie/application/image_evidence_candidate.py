from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


CONTRACT_NAME: Final[str] = (
    "gate_14_explicit_image_evidence_eligibility_and_provenance_relationship"
)
CONTRACT_VERSION: Final[str] = "1.0"
SUPPORTED_ARTIFACT_VERSIONS: Final[frozenset[str]] = frozenset({"1.0"})


class ImageEvidenceEligibilityDecision(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    SAFE_STOP = "SAFE_STOP"


class ImageEvidenceRelationshipOrigin(str, Enum):
    SOURCE_BACKED = "SOURCE_BACKED"
    OPERATOR_DECLARED = "OPERATOR_DECLARED"


@dataclass(frozen=True, slots=True)
class OfficialImageSourceRevisionBinding:
    source_id: str
    source_revision: str
    source_checksum: str
    source_authority: str
    authority_valid: bool
    rights_state: str
    rights_eligible: bool
    lifecycle_state: str
    lifecycle_eligible: bool
    synthetic: bool = True


@dataclass(frozen=True, slots=True)
class AcceptedImageExtractionArtifactBinding:
    artifact_id: str
    artifact_version: str
    artifact_checksum: str
    verified_artifact_checksum: str
    bound_source_id: str
    bound_source_revision: str
    bound_source_checksum: str
    gate13_accepted: bool
    factual_structural_fields: tuple[tuple[str, str], ...]
    semantic_fields: tuple[tuple[str, str], ...] = ()
    ocr_derived_fields: tuple[tuple[str, str], ...] = ()
    model_derived_fields: tuple[tuple[str, str], ...] = ()
    synthetic: bool = True


@dataclass(frozen=True, slots=True)
class ImageEvidenceRelationship:
    relationship_type: str
    origin: ImageEvidenceRelationshipOrigin | str
    subject_evidence_id: str
    object_evidence_id: str
    provenance_reference: str
    authority_reference: str = ""
    operator_reference: str = ""
    declaration_basis: str = ""
    synthetic: bool = True


@dataclass(frozen=True, slots=True)
class ImageEvidenceCandidate:
    contract_name: str
    contract_version: str
    source_id: str
    source_revision: str
    source_checksum: str
    artifact_id: str
    artifact_version: str
    artifact_checksum: str
    source_authority: str
    rights_state: str
    lifecycle_state: str
    factual_structural_fields: tuple[tuple[str, str], ...]
    relationship: ImageEvidenceRelationship | None
    eligibility_decision: ImageEvidenceEligibilityDecision
    eligibility_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImageEvidenceEligibilityResult:
    decision: ImageEvidenceEligibilityDecision
    candidate: ImageEvidenceCandidate | None
    reasons: tuple[str, ...]


def _is_blank(value: str) -> bool:
    return not isinstance(value, str) or not value.strip()


def _canonicalize_fields(
    fields: tuple[tuple[str, str], ...],
) -> tuple[tuple[tuple[str, str], ...] | None, str | None]:
    canonical: list[tuple[str, str]] = []
    seen_names: set[str] = set()

    for field in fields:
        if not isinstance(field, tuple) or len(field) != 2:
            return None, "MALFORMED_FACTUAL_STRUCTURAL_FIELD"

        name, value = field

        if _is_blank(name):
            return None, "MISSING_FACTUAL_STRUCTURAL_FIELD_NAME"

        if not isinstance(value, str):
            return None, "NON_TEXT_FACTUAL_STRUCTURAL_FIELD_VALUE"

        normalized_name = name.strip()

        if normalized_name in seen_names:
            return None, "DUPLICATE_FACTUAL_STRUCTURAL_FIELD_NAME"

        seen_names.add(normalized_name)
        canonical.append((normalized_name, value))

    return tuple(sorted(canonical)), None


def _validate_relationship(
    relationship: ImageEvidenceRelationship | None,
) -> tuple[str, ...]:
    if relationship is None:
        return ()

    reasons: list[str] = []

    if not relationship.synthetic:
        reasons.append("REAL_ASSET_RELATIONSHIP_INPUT_PROHIBITED")

    if _is_blank(relationship.relationship_type):
        reasons.append("MISSING_RELATIONSHIP_TYPE")

    if _is_blank(relationship.subject_evidence_id):
        reasons.append("MISSING_RELATIONSHIP_SUBJECT")

    if _is_blank(relationship.object_evidence_id):
        reasons.append("MISSING_RELATIONSHIP_OBJECT")

    if _is_blank(relationship.provenance_reference):
        reasons.append("MISSING_RELATIONSHIP_PROVENANCE")

    try:
        origin = ImageEvidenceRelationshipOrigin(relationship.origin)
    except (TypeError, ValueError):
        reasons.append("UNKNOWN_RELATIONSHIP_ORIGIN")
        return tuple(reasons)

    if origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED:
        if _is_blank(relationship.authority_reference):
            reasons.append("MISSING_SOURCE_BACKED_AUTHORITY_REFERENCE")
    elif origin is ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED:
        if _is_blank(relationship.operator_reference):
            reasons.append("MISSING_OPERATOR_REFERENCE")
        if _is_blank(relationship.declaration_basis):
            reasons.append("MISSING_OPERATOR_DECLARATION_BASIS")

    return tuple(reasons)


def evaluate_image_evidence_candidate(
    *,
    source: OfficialImageSourceRevisionBinding,
    artifact: AcceptedImageExtractionArtifactBinding,
    relationship: ImageEvidenceRelationship | None = None,
    automatic_relationship_inference_attempted: bool = False,
    automatic_evidence_to_knowledge_promotion_attempted: bool = False,
    automatic_conflict_resolution_attempted: bool = False,
    real_asset_input_attempted: bool = False,
) -> ImageEvidenceEligibilityResult:
    safe_stop_reasons: list[str] = []
    ineligible_reasons: list[str] = []

    required_source_values = (
        ("source_id", source.source_id),
        ("source_revision", source.source_revision),
        ("source_checksum", source.source_checksum),
        ("source_authority", source.source_authority),
        ("rights_state", source.rights_state),
        ("lifecycle_state", source.lifecycle_state),
    )
    required_artifact_values = (
        ("artifact_id", artifact.artifact_id),
        ("artifact_version", artifact.artifact_version),
        ("artifact_checksum", artifact.artifact_checksum),
        ("verified_artifact_checksum", artifact.verified_artifact_checksum),
        ("bound_source_id", artifact.bound_source_id),
        ("bound_source_revision", artifact.bound_source_revision),
        ("bound_source_checksum", artifact.bound_source_checksum),
    )

    for name, value in required_source_values + required_artifact_values:
        if _is_blank(value):
            safe_stop_reasons.append(f"MISSING_{name.upper()}")

    if not source.synthetic or not artifact.synthetic or real_asset_input_attempted:
        safe_stop_reasons.append("REAL_ASSET_INPUT_PROHIBITED")

    if automatic_relationship_inference_attempted:
        safe_stop_reasons.append("AUTOMATIC_RELATIONSHIP_INFERENCE_PROHIBITED")

    if automatic_evidence_to_knowledge_promotion_attempted:
        safe_stop_reasons.append(
            "AUTOMATIC_EVIDENCE_TO_KNOWLEDGE_PROMOTION_PROHIBITED"
        )

    if automatic_conflict_resolution_attempted:
        safe_stop_reasons.append("AUTOMATIC_CONFLICT_RESOLUTION_PROHIBITED")

    if source.source_id != artifact.bound_source_id:
        safe_stop_reasons.append("SOURCE_ID_MISMATCH")

    if source.source_revision != artifact.bound_source_revision:
        safe_stop_reasons.append("SOURCE_REVISION_MISMATCH")

    if source.source_checksum != artifact.bound_source_checksum:
        safe_stop_reasons.append("SOURCE_CHECKSUM_MISMATCH")

    if artifact.artifact_checksum != artifact.verified_artifact_checksum:
        safe_stop_reasons.append("ARTIFACT_CHECKSUM_MISMATCH")

    if artifact.artifact_version not in SUPPORTED_ARTIFACT_VERSIONS:
        safe_stop_reasons.append("UNSUPPORTED_ARTIFACT_VERSION")

    if artifact.semantic_fields:
        safe_stop_reasons.append("SEMANTIC_FIELD_PROHIBITED")

    if artifact.ocr_derived_fields:
        safe_stop_reasons.append("OCR_DERIVED_FIELD_PROHIBITED")

    if artifact.model_derived_fields:
        safe_stop_reasons.append("MODEL_DERIVED_FIELD_PROHIBITED")

    canonical_fields, field_error = _canonicalize_fields(
        artifact.factual_structural_fields
    )
    if field_error is not None:
        safe_stop_reasons.append(field_error)

    safe_stop_reasons.extend(_validate_relationship(relationship))

    if not source.authority_valid:
        ineligible_reasons.append("SOURCE_AUTHORITY_INVALID")

    if not source.rights_eligible:
        ineligible_reasons.append("RIGHTS_NOT_ELIGIBLE")

    if not source.lifecycle_eligible:
        ineligible_reasons.append("LIFECYCLE_NOT_ELIGIBLE")

    if not artifact.gate13_accepted:
        ineligible_reasons.append("ARTIFACT_NOT_ACCEPTED_UNDER_GATE_13")

    if safe_stop_reasons:
        return ImageEvidenceEligibilityResult(
            decision=ImageEvidenceEligibilityDecision.SAFE_STOP,
            candidate=None,
            reasons=tuple(safe_stop_reasons),
        )

    if ineligible_reasons:
        return ImageEvidenceEligibilityResult(
            decision=ImageEvidenceEligibilityDecision.INELIGIBLE,
            candidate=None,
            reasons=tuple(ineligible_reasons),
        )

    eligibility_reasons = ("ALL_ELIGIBILITY_PRECONDITIONS_SATISFIED",)

    candidate = ImageEvidenceCandidate(
        contract_name=CONTRACT_NAME,
        contract_version=CONTRACT_VERSION,
        source_id=source.source_id,
        source_revision=source.source_revision,
        source_checksum=source.source_checksum,
        artifact_id=artifact.artifact_id,
        artifact_version=artifact.artifact_version,
        artifact_checksum=artifact.artifact_checksum,
        source_authority=source.source_authority,
        rights_state=source.rights_state,
        lifecycle_state=source.lifecycle_state,
        factual_structural_fields=canonical_fields or (),
        relationship=relationship,
        eligibility_decision=ImageEvidenceEligibilityDecision.ELIGIBLE,
        eligibility_reasons=eligibility_reasons,
    )

    return ImageEvidenceEligibilityResult(
        decision=ImageEvidenceEligibilityDecision.ELIGIBLE,
        candidate=candidate,
        reasons=eligibility_reasons,
    )
