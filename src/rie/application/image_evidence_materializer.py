from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Final

from rie.application.image_evidence_candidate import (
    CONTRACT_NAME as IMAGE_CANDIDATE_CONTRACT_NAME,
    CONTRACT_VERSION as IMAGE_CANDIDATE_CONTRACT_VERSION,
    ImageEvidenceCandidate,
    ImageEvidenceEligibilityDecision,
    ImageEvidenceEligibilityResult,
    ImageEvidenceRelationship,
    ImageEvidenceRelationshipOrigin,
)
from rie.domain.acceptance_identity import (
    ACCEPTANCE_IDENTITY_POLICY_ID,
    ACCEPTANCE_IDENTITY_POLICY_VERSION,
    AcceptanceIdentityResult,
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceDiagnostic,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    EvidenceIdentityResult,
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)


MAPPING_CONTRACT_NAME: Final[str] = (
    "gate_14_image_evidence_acceptance_materialization_and_relationship_identity"
)
MAPPING_CONTRACT_VERSION: Final[str] = "1.0"
SELF_IMAGE_EVIDENCE: Final[str] = "SELF_IMAGE_EVIDENCE"
ACCEPTED_EVIDENCE_CONTRACT_VERSION: Final[str] = "accepted-evidence-v1"
ACCEPTANCE_RECORD_CONTRACT_VERSION: Final[str] = "acceptance-record-v1"
PAYLOAD_TYPE: Final[str] = "image_structural_facts"
PAYLOAD_SCHEMA_VERSION: Final[str] = "1.0"
LOCATOR_TYPE: Final[str] = "image-evidence-binding"
LOCATOR_SCHEMA_VERSION: Final[str] = "1.0"
PRODUCER_NAME: Final[str] = "gate-14-image-evidence-candidate"
PRODUCER_KIND: Final[str] = "image_evidence_candidate"
ELIGIBILITY_POLICY_ID: Final[str] = "gate-14-image-evidence-eligibility"
ELIGIBILITY_POLICY_VERSION: Final[str] = "1.0"
ACCEPTANCE_POLICY_ID: Final[str] = "gate-14-image-evidence-acceptance"
ACCEPTANCE_POLICY_VERSION: Final[str] = "1.0"
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")
_PLACEHOLDER_EVIDENCE_ID: Final[str] = f"ev1_{'0' * 64}"
_PLACEHOLDER_ACCEPTANCE_ID: Final[str] = f"ar1_{'0' * 64}"


class ImageEvidenceMaterializationDecision(str, Enum):
    MATERIALIZED = "MATERIALIZED"
    REJECTED = "REJECTED"
    SAFE_STOP = "SAFE_STOP"


@dataclass(frozen=True, slots=True)
class AcceptedImageEvidenceRelationship:
    relationship_type: str
    origin: ImageEvidenceRelationshipOrigin
    subject_evidence_id: str
    object_evidence_id: str
    provenance_reference: str
    authority_reference: str
    operator_reference: str
    declaration_basis: str


@dataclass(frozen=True, slots=True)
class ImageEvidenceMaterializationRequest:
    eligibility_result: ImageEvidenceEligibilityResult
    accepted_evidence_contract_version: str
    candidate_snapshot_digest: str
    source_snapshot: EvidenceSourceSnapshot
    producer_snapshot: EvidenceProducerSnapshot
    factual_payload: EvidencePayload
    provenance: EvidenceProvenance
    evidence_diagnostics: tuple[EvidenceDiagnostic, ...]
    eligibility_policy_id: str
    eligibility_policy_version: str
    eligibility_evaluated_at: datetime
    eligibility_evaluated_by: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str
    accepted_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str
    materializer_id: str
    materializer_version: str
    acceptance_diagnostics: tuple[AcceptanceDiagnostic, ...]
    automatic_knowledge_promotion_attempted: bool
    automatic_conflict_resolution_attempted: bool
    side_effect_attempted: bool
    image_access_attempted: bool
    semantic_execution_attempted: bool
    real_asset_execution_attempted: bool


@dataclass(frozen=True, slots=True)
class ImageEvidenceMaterializationResult:
    decision: ImageEvidenceMaterializationDecision
    accepted_evidence: AcceptedEvidence | None
    acceptance_record: AcceptanceRecord | None
    accepted_relationship: AcceptedImageEvidenceRelationship | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        materialized = (
            self.accepted_evidence is not None
            and self.acceptance_record is not None
            and self.accepted_relationship is not None
        )
        empty = (
            self.accepted_evidence is None
            and self.acceptance_record is None
            and self.accepted_relationship is None
        )
        if self.decision is ImageEvidenceMaterializationDecision.MATERIALIZED:
            if not materialized or self.reason_codes:
                raise ValueError("MATERIALIZED requires all outputs and no reasons")
        elif not empty:
            raise ValueError("REJECTED and SAFE_STOP require zero outputs")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")


def _blank(value: object) -> bool:
    return type(value) is not str or not value.strip()


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in _HEX_DIGITS for character in value)
    )


def _is_ev1(value: object) -> bool:
    return (
        type(value) is str
        and value.startswith("ev1_")
        and _is_sha256(value[4:])
    )


def _timezone_aware(value: object) -> bool:
    return (
        type(value) is datetime
        and value.tzinfo is not None
        and value.utcoffset() is not None
    )


def _empty_result(
    decision: ImageEvidenceMaterializationDecision,
    *reason_codes: str,
) -> ImageEvidenceMaterializationResult:
    return ImageEvidenceMaterializationResult(
        decision=decision,
        accepted_evidence=None,
        acceptance_record=None,
        accepted_relationship=None,
        reason_codes=tuple(reason_codes),
        diagnostics=tuple(reason_codes),
    )


def _binding_value(value: str) -> str:
    return value if value.strip() else "NONE"


def _expected_locator_value(
    candidate: ImageEvidenceCandidate,
    relationship: ImageEvidenceRelationship,
) -> tuple[str, ...]:
    origin = relationship.origin
    origin_value = origin.value if isinstance(origin, Enum) else str(origin)
    return (
        "source_revision",
        candidate.source_revision,
        "artifact_id",
        candidate.artifact_id,
        "artifact_version",
        candidate.artifact_version,
        "artifact_checksum",
        candidate.artifact_checksum,
        "relationship_type",
        relationship.relationship_type,
        "relationship_origin",
        origin_value,
        "relationship_subject",
        relationship.subject_evidence_id,
        "relationship_object",
        SELF_IMAGE_EVIDENCE,
        "relationship_provenance",
        relationship.provenance_reference,
        "authority_reference",
        _binding_value(relationship.authority_reference),
        "operator_reference",
        _binding_value(relationship.operator_reference),
        "declaration_basis",
        _binding_value(relationship.declaration_basis),
    )


def _required_lineage(
    candidate: ImageEvidenceCandidate,
    relationship: ImageEvidenceRelationship,
) -> tuple[str, ...]:
    origin = relationship.origin
    origin_value = origin.value if isinstance(origin, Enum) else str(origin)
    return (
        f"source_revision:{candidate.source_revision}",
        f"rights_state:{candidate.rights_state}",
        f"artifact_id:{candidate.artifact_id}",
        f"artifact_version:{candidate.artifact_version}",
        f"artifact_checksum:{candidate.artifact_checksum}",
        f"relationship_type:{relationship.relationship_type}",
        f"relationship_origin:{origin_value}",
        f"relationship_subject:{relationship.subject_evidence_id}",
        f"relationship_object:{SELF_IMAGE_EVIDENCE}",
        f"relationship_provenance:{relationship.provenance_reference}",
        f"authority_reference:{relationship.authority_reference}",
        f"operator_reference:{relationship.operator_reference}",
        f"declaration_basis:{relationship.declaration_basis}",
        f"mapping_contract:{MAPPING_CONTRACT_NAME}",
        f"mapping_version:{MAPPING_CONTRACT_VERSION}",
    )


def _identity_result_valid(result: object) -> bool:
    return (
        type(result) is EvidenceIdentityResult
        and result.identity_policy_id == EVIDENCE_IDENTITY_POLICY_ID
        and result.identity_policy_version == EVIDENCE_IDENTITY_POLICY_VERSION
        and _is_ev1(result.evidence_id)
    )


def _acceptance_identity_result_valid(result: object) -> bool:
    return (
        type(result) is AcceptanceIdentityResult
        and result.identity_policy_id == ACCEPTANCE_IDENTITY_POLICY_ID
        and result.identity_policy_version == ACCEPTANCE_IDENTITY_POLICY_VERSION
        and type(result.acceptance_record_id) is str
        and result.acceptance_record_id.startswith("ar1_")
        and _is_sha256(result.acceptance_record_id[4:])
    )


def _validate_bridge(
    request: ImageEvidenceMaterializationRequest,
    candidate: ImageEvidenceCandidate,
    relationship: ImageEvidenceRelationship,
) -> tuple[str, ...]:
    reasons: list[str] = []

    if request.accepted_evidence_contract_version != ACCEPTED_EVIDENCE_CONTRACT_VERSION:
        reasons.append("UNSUPPORTED_ACCEPTED_EVIDENCE_CONTRACT_VERSION")
    if not _is_sha256(request.candidate_snapshot_digest):
        reasons.append("INVALID_CANDIDATE_SNAPSHOT_DIGEST")
    if type(request.source_snapshot) is not EvidenceSourceSnapshot:
        reasons.append("SOURCE_SNAPSHOT_INVALID")
    if type(request.producer_snapshot) is not EvidenceProducerSnapshot:
        reasons.append("PRODUCER_SNAPSHOT_INVALID")
    if type(request.factual_payload) is not EvidencePayload:
        reasons.append("FACTUAL_PAYLOAD_INVALID")
    if type(request.provenance) is not EvidenceProvenance:
        reasons.append("PROVENANCE_INVALID")
    if type(request.evidence_diagnostics) is not tuple or any(
        type(item) is not EvidenceDiagnostic
        for item in request.evidence_diagnostics
    ):
        reasons.append("EVIDENCE_DIAGNOSTICS_INVALID")
    if type(request.acceptance_diagnostics) is not tuple or any(
        type(item) is not AcceptanceDiagnostic
        for item in request.acceptance_diagnostics
    ):
        reasons.append("ACCEPTANCE_DIAGNOSTICS_INVALID")

    if reasons:
        return tuple(reasons)

    expected_source_path = (
        f"official-image-source:{candidate.source_id}@{candidate.source_revision}"
    )
    if (
        request.source_snapshot.source_id != candidate.source_id
        or request.source_snapshot.source_path != expected_source_path
        or request.source_snapshot.source_type != "image"
        or request.source_snapshot.document_classification
        != "official_image_source"
        or request.source_snapshot.authority_status
        != candidate.source_authority
        or request.source_snapshot.lifecycle_status
        != candidate.lifecycle_state
        or request.source_snapshot.evidence_eligibility != "eligible"
        or request.source_snapshot.source_content_digest
        != candidate.source_checksum
    ):
        reasons.append("SOURCE_SNAPSHOT_MISMATCH")

    if (
        request.producer_snapshot.producer_name != PRODUCER_NAME
        or request.producer_snapshot.producer_version
        != candidate.contract_version
        or request.producer_snapshot.producer_kind != PRODUCER_KIND
        or request.producer_snapshot.producer_contract_version
        != candidate.contract_name
    ):
        reasons.append("PRODUCER_SNAPSHOT_MISMATCH")

    if (
        request.factual_payload.payload_type != PAYLOAD_TYPE
        or request.factual_payload.payload_schema_version
        != PAYLOAD_SCHEMA_VERSION
        or request.factual_payload.payload
        != candidate.factual_structural_fields
        or not _is_sha256(request.factual_payload.payload_digest)
        or request.factual_payload.locator.locator_type != LOCATOR_TYPE
        or request.factual_payload.locator.locator_schema_version
        != LOCATOR_SCHEMA_VERSION
        or request.factual_payload.locator.locator_value
        != _expected_locator_value(candidate, relationship)
    ):
        reasons.append("FACTUAL_PAYLOAD_MISMATCH")

    if (
        not _is_sha256(request.provenance.producer_output_digest)
        or not _timezone_aware(request.provenance.observed_at)
        or _blank(request.provenance.collection_id)
        or _blank(request.provenance.source_registry_version)
    ):
        reasons.append("PROVENANCE_INVALID")
    else:
        missing_lineage = tuple(
            token
            for token in _required_lineage(candidate, relationship)
            if token not in request.provenance.lineage
        )
        if missing_lineage:
            reasons.append("PROVENANCE_LINEAGE_MISMATCH")

    return tuple(reasons)


def materialize_image_evidence_candidate(
    request: object,
) -> ImageEvidenceMaterializationResult:
    if type(request) is not ImageEvidenceMaterializationRequest:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "REQUEST_INVALID",
        )

    prohibited_flags = (
        request.automatic_knowledge_promotion_attempted,
        request.automatic_conflict_resolution_attempted,
        request.side_effect_attempted,
        request.image_access_attempted,
        request.semantic_execution_attempted,
        request.real_asset_execution_attempted,
    )
    if any(type(value) is not bool for value in prohibited_flags):
        return _empty_result(
            ImageEvidenceMaterializationDecision.SAFE_STOP,
            "PROHIBITED_ATTEMPT_FLAG_INVALID",
        )
    if any(prohibited_flags):
        return _empty_result(
            ImageEvidenceMaterializationDecision.SAFE_STOP,
            "PROHIBITED_OPERATION_ATTEMPTED",
        )

    if type(request.eligibility_result) is not ImageEvidenceEligibilityResult:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "ELIGIBILITY_RESULT_INVALID",
        )
    if (
        request.eligibility_result.decision
        is not ImageEvidenceEligibilityDecision.ELIGIBLE
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "ELIGIBILITY_NOT_ELIGIBLE",
        )

    candidate = request.eligibility_result.candidate
    if type(candidate) is not ImageEvidenceCandidate:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "CANDIDATE_MISSING_OR_INVALID",
        )
    if (
        candidate.contract_name != IMAGE_CANDIDATE_CONTRACT_NAME
        or candidate.contract_version != IMAGE_CANDIDATE_CONTRACT_VERSION
        or candidate.eligibility_decision
        is not ImageEvidenceEligibilityDecision.ELIGIBLE
        or candidate.eligibility_reasons
        != request.eligibility_result.reasons
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "CANDIDATE_CONTRACT_OR_ELIGIBILITY_MISMATCH",
        )

    required_candidate_strings = (
        candidate.source_id,
        candidate.source_revision,
        candidate.source_authority,
        candidate.rights_state,
        candidate.lifecycle_state,
        candidate.artifact_id,
        candidate.artifact_version,
    )
    if any(_blank(value) for value in required_candidate_strings) or not all(
        _is_sha256(value)
        for value in (
            candidate.source_checksum,
            candidate.artifact_checksum,
        )
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "CANDIDATE_IDENTITY_INCOMPLETE",
        )
    if (
        type(candidate.factual_structural_fields) is not tuple
        or not candidate.factual_structural_fields
        or candidate.factual_structural_fields
        != tuple(sorted(candidate.factual_structural_fields))
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "FACTUAL_STRUCTURAL_FIELDS_INVALID",
        )

    relationship = candidate.relationship
    if type(relationship) is not ImageEvidenceRelationship:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "RELATIONSHIP_REQUIRED",
        )
    if relationship.synthetic is not True:
        return _empty_result(
            ImageEvidenceMaterializationDecision.SAFE_STOP,
            "REAL_ASSET_RELATIONSHIP_PROHIBITED",
        )
    if type(relationship.origin) is not ImageEvidenceRelationshipOrigin:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "RELATIONSHIP_ORIGIN_INVALID",
        )
    if (
        _blank(relationship.relationship_type)
        or not _is_ev1(relationship.subject_evidence_id)
        or _blank(relationship.provenance_reference)
        or relationship.object_evidence_id != SELF_IMAGE_EVIDENCE
        and not _is_ev1(relationship.object_evidence_id)
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "RELATIONSHIP_INVALID",
        )
    if relationship.origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED:
        if _blank(relationship.authority_reference):
            return _empty_result(
                ImageEvidenceMaterializationDecision.REJECTED,
                "SOURCE_BACKED_AUTHORITY_REFERENCE_MISSING",
            )
    elif (
        _blank(relationship.operator_reference)
        or _blank(relationship.declaration_basis)
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "OPERATOR_DECLARATION_INCOMPLETE",
        )

    explicit_strings = (
        request.eligibility_policy_id,
        request.eligibility_policy_version,
        request.eligibility_evaluated_by,
        request.accepted_by,
        request.acceptance_reason,
        request.review_record_id,
        request.acceptance_policy_id,
        request.acceptance_policy_version,
        request.materializer_id,
        request.materializer_version,
    )
    if any(_blank(value) for value in explicit_strings):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "EXPLICIT_ACCEPTANCE_INPUT_INCOMPLETE",
        )
    if (
        not _timezone_aware(request.eligibility_evaluated_at)
        or not _timezone_aware(request.accepted_at)
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "TIMEZONE_AWARE_TIMESTAMP_REQUIRED",
        )
    if (
        request.eligibility_policy_id != ELIGIBILITY_POLICY_ID
        or request.eligibility_policy_version != ELIGIBILITY_POLICY_VERSION
        or request.acceptance_policy_id != ACCEPTANCE_POLICY_ID
        or request.acceptance_policy_version != ACCEPTANCE_POLICY_VERSION
        or request.materializer_id != MAPPING_CONTRACT_NAME
        or request.materializer_version != MAPPING_CONTRACT_VERSION
    ):
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            "UNSUPPORTED_POLICY_OR_MATERIALIZER",
        )

    bridge_reasons = _validate_bridge(request, candidate, relationship)
    if bridge_reasons:
        return _empty_result(
            ImageEvidenceMaterializationDecision.REJECTED,
            *bridge_reasons,
        )

    try:
        candidate_reference = EvidenceCandidateReference(
            candidate_contract_version=candidate.contract_version,
            candidate_snapshot_digest=request.candidate_snapshot_digest,
            candidate_source_id=candidate.source_id,
            candidate_producer_name=request.producer_snapshot.producer_name,
            candidate_producer_version=request.producer_snapshot.producer_version,
            candidate_payload_digest=request.factual_payload.payload_digest,
        )
        accepted_eligibility = AcceptedEligibilityResult(
            decision="eligible",
            policy_id=request.eligibility_policy_id,
            policy_version=request.eligibility_policy_version,
            candidate_snapshot_digest=request.candidate_snapshot_digest,
            source_id=candidate.source_id,
            reason_codes=request.eligibility_result.reasons,
            evaluated_at=request.eligibility_evaluated_at,
            evaluated_by=request.eligibility_evaluated_by,
            diagnostics=request.evidence_diagnostics,
        )
        provisional_materialization = EvidenceMaterializationRecord(
            materializer_id=request.materializer_id,
            materializer_version=request.materializer_version,
            materialized_at=request.accepted_at,
            acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_ID,
            accepted_by=request.accepted_by,
            acceptance_reason=request.acceptance_reason,
            review_record_id=request.review_record_id,
            identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
            identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        )
        provisional_evidence = AcceptedEvidence(
            evidence_id=_PLACEHOLDER_EVIDENCE_ID,
            contract_version=request.accepted_evidence_contract_version,
            candidate_reference=candidate_reference,
            source_snapshot=request.source_snapshot,
            producer_snapshot=request.producer_snapshot,
            factual_payload=request.factual_payload,
            provenance=request.provenance,
            eligibility_result=accepted_eligibility,
            materialization_record=provisional_materialization,
            diagnostics=request.evidence_diagnostics,
        )
        evidence_identity = calculate_evidence_identity(
            identity_input_from_accepted_evidence(provisional_evidence)
        )
        if not _identity_result_valid(evidence_identity):
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "EVIDENCE_IDENTITY_RESULT_INVALID",
            )
        evidence_id = evidence_identity.evidence_id
        if (
            relationship.object_evidence_id != SELF_IMAGE_EVIDENCE
            and relationship.object_evidence_id != evidence_id
        ):
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "RELATIONSHIP_OBJECT_IDENTITY_MISMATCH",
            )

        provisional_acceptance = AcceptanceRecord(
            acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_ID,
            contract_version=ACCEPTANCE_RECORD_CONTRACT_VERSION,
            evidence_id=evidence_id,
            accepted_by=request.accepted_by,
            acceptance_reason=request.acceptance_reason,
            review_record_id=request.review_record_id,
            accepted_at=request.accepted_at,
            acceptance_policy_id=request.acceptance_policy_id,
            acceptance_policy_version=request.acceptance_policy_version,
            evidence_identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
            evidence_identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
            materializer_id=request.materializer_id,
            materializer_version=request.materializer_version,
            diagnostics=request.acceptance_diagnostics,
        )
        acceptance_identity = calculate_acceptance_identity(
            acceptance_identity_input_from_record(provisional_acceptance)
        )
        if not _acceptance_identity_result_valid(acceptance_identity):
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "ACCEPTANCE_IDENTITY_RESULT_INVALID",
            )

        acceptance_record = AcceptanceRecord(
            acceptance_record_id=acceptance_identity.acceptance_record_id,
            contract_version=ACCEPTANCE_RECORD_CONTRACT_VERSION,
            evidence_id=evidence_id,
            accepted_by=request.accepted_by,
            acceptance_reason=request.acceptance_reason,
            review_record_id=request.review_record_id,
            accepted_at=request.accepted_at,
            acceptance_policy_id=request.acceptance_policy_id,
            acceptance_policy_version=request.acceptance_policy_version,
            evidence_identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
            evidence_identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
            materializer_id=request.materializer_id,
            materializer_version=request.materializer_version,
            diagnostics=request.acceptance_diagnostics,
        )
        materialization_record = EvidenceMaterializationRecord(
            materializer_id=request.materializer_id,
            materializer_version=request.materializer_version,
            materialized_at=request.accepted_at,
            acceptance_record_id=acceptance_record.acceptance_record_id,
            accepted_by=request.accepted_by,
            acceptance_reason=request.acceptance_reason,
            review_record_id=request.review_record_id,
            identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
            identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        )
        accepted_evidence = AcceptedEvidence(
            evidence_id=evidence_id,
            contract_version=request.accepted_evidence_contract_version,
            candidate_reference=candidate_reference,
            source_snapshot=request.source_snapshot,
            producer_snapshot=request.producer_snapshot,
            factual_payload=request.factual_payload,
            provenance=request.provenance,
            eligibility_result=accepted_eligibility,
            materialization_record=materialization_record,
            diagnostics=request.evidence_diagnostics,
        )
        recomputed_evidence = calculate_evidence_identity(
            identity_input_from_accepted_evidence(accepted_evidence)
        )
        recomputed_acceptance = calculate_acceptance_identity(
            acceptance_identity_input_from_record(acceptance_record)
        )
        if (
            not _identity_result_valid(recomputed_evidence)
            or recomputed_evidence != evidence_identity
        ):
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "EVIDENCE_IDENTITY_RECOMPUTATION_MISMATCH",
            )
        if (
            not _acceptance_identity_result_valid(recomputed_acceptance)
            or recomputed_acceptance != acceptance_identity
        ):
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "ACCEPTANCE_IDENTITY_RECOMPUTATION_MISMATCH",
            )
        if acceptance_record.evidence_id != accepted_evidence.evidence_id:
            return _empty_result(
                ImageEvidenceMaterializationDecision.SAFE_STOP,
                "ACCEPTED_OUTPUT_EVIDENCE_ID_MISMATCH",
            )

        accepted_relationship = AcceptedImageEvidenceRelationship(
            relationship_type=relationship.relationship_type,
            origin=relationship.origin,
            subject_evidence_id=relationship.subject_evidence_id,
            object_evidence_id=evidence_id,
            provenance_reference=relationship.provenance_reference,
            authority_reference=relationship.authority_reference,
            operator_reference=relationship.operator_reference,
            declaration_basis=relationship.declaration_basis,
        )
    except (TypeError, ValueError):
        return _empty_result(
            ImageEvidenceMaterializationDecision.SAFE_STOP,
            "DOMAIN_CONSTRUCTION_SAFE_STOP",
        )

    return ImageEvidenceMaterializationResult(
        decision=ImageEvidenceMaterializationDecision.MATERIALIZED,
        accepted_evidence=accepted_evidence,
        acceptance_record=acceptance_record,
        accepted_relationship=accepted_relationship,
        reason_codes=(),
        diagnostics=(),
    )
