from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Final

from rie.application.image_evidence_candidate import (
    ImageEvidenceRelationshipOrigin,
)
from rie.application.image_evidence_materializer import (
    AcceptedImageEvidenceRelationship,
    ImageEvidenceMaterializationDecision,
    ImageEvidenceMaterializationResult,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence
from rie.domain.knowledge_candidate import (
    IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)

_CONSTRUCTION_RULE_ID: Final[str] = (
    "rcis-accepted-image-structural-fact-selection"
)
_CONSTRUCTION_RULE_VERSION: Final[str] = "1.0.0"
_CONSTRUCTOR_ID: Final[str] = (
    "gate-14-image-evidence-to-knowledge-candidate-constructor"
)
_CONSTRUCTOR_VERSION: Final[str] = "1.0"
_IMAGE_PAYLOAD_TYPE: Final[str] = "image_structural_facts"
_IMAGE_PAYLOAD_SCHEMA_VERSION: Final[str] = "1.0"


class ImageKnowledgeConstructionDecision(str, Enum):
    CONSTRUCTED = "CONSTRUCTED"
    REJECTED = "REJECTED"
    SAFE_STOP = "SAFE_STOP"


@dataclass(frozen=True, slots=True)
class ImageKnowledgeRelationshipSupport:
    knowledge_candidate_id: str
    evidence_id: str
    acceptance_record_id: str
    relationship_type: str
    relationship_origin: ImageEvidenceRelationshipOrigin
    subject_evidence_id: str
    object_evidence_id: str
    provenance_reference: str
    authority_reference: str
    operator_reference: str
    declaration_basis: str
    source_id: str
    source_content_digest: str
    payload_digest: str
    source_lineage: tuple[str, ...]
    evidence_materializer_id: str
    evidence_materializer_version: str


@dataclass(frozen=True, slots=True)
class ImageKnowledgeConstructionRequest:
    materialization_result: ImageEvidenceMaterializationResult
    factual_field_name: str
    statement: str
    construction_rule_id: str
    construction_rule_version: str
    constructor_id: str
    constructor_version: str
    constructed_at: datetime
    automatic_promotion_attempted: bool
    automatic_conflict_resolution_attempted: bool
    knowledge_approval_attempted: bool
    persistence_attempted: bool
    side_effect_attempted: bool
    image_access_attempted: bool
    semantic_execution_attempted: bool
    real_asset_execution_attempted: bool


@dataclass(frozen=True, slots=True)
class ImageKnowledgeConstructionResult:
    decision: ImageKnowledgeConstructionDecision
    knowledge_candidate: KnowledgeCandidate | None
    relationship_support: ImageKnowledgeRelationshipSupport | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[str, ...]

    def __post_init__(self) -> None:
        complete = (
            self.knowledge_candidate is not None
            and self.relationship_support is not None
        )
        empty = (
            self.knowledge_candidate is None
            and self.relationship_support is None
        )
        if self.decision is ImageKnowledgeConstructionDecision.CONSTRUCTED:
            if not complete or self.reason_codes:
                raise ValueError(
                    "CONSTRUCTED requires both outputs and no reasons"
                )
        elif not empty:
            raise ValueError("REJECTED and SAFE_STOP require zero outputs")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")


def _blank(value: object) -> bool:
    return type(value) is not str or not value.strip()


def _timezone_aware(value: object) -> bool:
    return (
        type(value) is datetime
        and value.tzinfo is not None
        and value.utcoffset() is not None
    )


def _empty_result(
    decision: ImageKnowledgeConstructionDecision,
    *reason_codes: str,
) -> ImageKnowledgeConstructionResult:
    return ImageKnowledgeConstructionResult(
        decision=decision,
        knowledge_candidate=None,
        relationship_support=None,
        reason_codes=tuple(reason_codes),
        diagnostics=tuple(reason_codes),
    )


def _materialized_outputs(
    result: ImageEvidenceMaterializationResult,
) -> tuple[
    AcceptedEvidence,
    AcceptanceRecord,
    AcceptedImageEvidenceRelationship,
] | None:
    if (
        result.decision
        is not ImageEvidenceMaterializationDecision.MATERIALIZED
    ):
        return None
    if result.reason_codes or result.diagnostics:
        return None
    if (
        type(result.accepted_evidence) is not AcceptedEvidence
        or type(result.acceptance_record) is not AcceptanceRecord
        or type(result.accepted_relationship)
        is not AcceptedImageEvidenceRelationship
    ):
        return None
    return (
        result.accepted_evidence,
        result.acceptance_record,
        result.accepted_relationship,
    )


def _selected_field_value(
    accepted_evidence: AcceptedEvidence,
    field_name: str,
) -> tuple[str | None, str | None]:
    payload = accepted_evidence.factual_payload.payload
    if type(payload) is not tuple or not payload:
        return None, "FACTUAL_PAYLOAD_MAPPING_INVALID"

    matches: list[object] = []
    names: list[str] = []
    for item in payload:
        if (
            type(item) is not tuple
            or len(item) != 2
            or type(item[0]) is not str
        ):
            return None, "FACTUAL_PAYLOAD_MAPPING_INVALID"
        names.append(item[0])
        if item[0] == field_name:
            matches.append(item[1])

    if len(set(names)) != len(names) or names != sorted(names):
        return None, "FACTUAL_PAYLOAD_MAPPING_INVALID"
    if not matches:
        return None, "FACTUAL_FIELD_NOT_FOUND"
    if len(matches) != 1:
        return None, "FACTUAL_FIELD_AMBIGUOUS"

    selected = matches[0]
    if type(selected) is not str or not selected.strip():
        return None, "FACTUAL_FIELD_VALUE_INVALID"
    return selected, None


def construct_image_knowledge_candidate(
    request: object,
) -> ImageKnowledgeConstructionResult:
    if type(request) is not ImageKnowledgeConstructionRequest:
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "REQUEST_INVALID",
        )

    prohibited_flags = (
        request.automatic_promotion_attempted,
        request.automatic_conflict_resolution_attempted,
        request.knowledge_approval_attempted,
        request.persistence_attempted,
        request.side_effect_attempted,
        request.image_access_attempted,
        request.semantic_execution_attempted,
        request.real_asset_execution_attempted,
    )
    if any(type(value) is not bool for value in prohibited_flags):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "PROHIBITED_ATTEMPT_FLAG_INVALID",
        )
    if any(prohibited_flags):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "PROHIBITED_OPERATION_ATTEMPTED",
        )

    if type(request.materialization_result) is not ImageEvidenceMaterializationResult:
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "MATERIALIZATION_RESULT_INVALID",
        )

    outputs = _materialized_outputs(request.materialization_result)
    if outputs is None:
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "MATERIALIZATION_RESULT_NOT_MATERIALIZED",
        )

    accepted_evidence, acceptance_record, relationship = outputs

    if (
        accepted_evidence.evidence_id != acceptance_record.evidence_id
        or accepted_evidence.materialization_record.acceptance_record_id
        != acceptance_record.acceptance_record_id
        or relationship.object_evidence_id != accepted_evidence.evidence_id
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "MATERIALIZED_IDENTITY_LINK_MISMATCH",
        )

    if type(relationship.origin) is not ImageEvidenceRelationshipOrigin:
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "RELATIONSHIP_ORIGIN_INVALID",
        )
    if (
        _blank(relationship.relationship_type)
        or _blank(relationship.subject_evidence_id)
        or _blank(relationship.object_evidence_id)
        or _blank(relationship.provenance_reference)
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "RELATIONSHIP_INCOMPLETE",
        )
    if (
        relationship.origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED
        and _blank(relationship.authority_reference)
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "SOURCE_BACKED_AUTHORITY_REFERENCE_MISSING",
        )
    if (
        relationship.origin
        is ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
        and (
            _blank(relationship.operator_reference)
            or _blank(relationship.declaration_basis)
        )
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "OPERATOR_DECLARATION_INCOMPLETE",
        )

    payload = accepted_evidence.factual_payload
    if (
        payload.payload_type != _IMAGE_PAYLOAD_TYPE
        or payload.payload_schema_version != _IMAGE_PAYLOAD_SCHEMA_VERSION
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "UNSUPPORTED_IMAGE_FACTUAL_PAYLOAD",
        )

    explicit_strings = (
        request.factual_field_name,
        request.statement,
        request.construction_rule_id,
        request.construction_rule_version,
        request.constructor_id,
        request.constructor_version,
    )
    if any(_blank(value) for value in explicit_strings):
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "EXPLICIT_CONSTRUCTION_INPUT_INCOMPLETE",
        )
    if not _timezone_aware(request.constructed_at):
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "TIMEZONE_AWARE_CONSTRUCTION_TIME_REQUIRED",
        )
    if (
        request.construction_rule_id != _CONSTRUCTION_RULE_ID
        or request.construction_rule_version != _CONSTRUCTION_RULE_VERSION
        or request.constructor_id != _CONSTRUCTOR_ID
        or request.constructor_version != _CONSTRUCTOR_VERSION
    ):
        return _empty_result(
            ImageKnowledgeConstructionDecision.REJECTED,
            "UNSUPPORTED_CONSTRUCTION_RULE_OR_CONSTRUCTOR",
        )

    selected_value, field_error = _selected_field_value(
        accepted_evidence,
        request.factual_field_name,
    )
    if field_error is not None:
        decision = (
            ImageKnowledgeConstructionDecision.REJECTED
            if field_error == "FACTUAL_FIELD_NOT_FOUND"
            else ImageKnowledgeConstructionDecision.SAFE_STOP
        )
        return _empty_result(decision, field_error)
    if request.statement != selected_value:
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "STATEMENT_SELECTION_MISMATCH",
        )

    try:
        evidence_support = KnowledgeEvidenceSupport(
            evidence_id=accepted_evidence.evidence_id,
            acceptance_record_ids=(
                acceptance_record.acceptance_record_id,
            ),
            acceptance_review_record_ids=(
                acceptance_record.review_record_id,
            ),
            source_id=accepted_evidence.source_snapshot.source_id,
            source_content_digest=(
                accepted_evidence.source_snapshot.source_content_digest
            ),
            source_authority_status=(
                accepted_evidence.source_snapshot.authority_status
            ),
            source_lifecycle_status=(
                accepted_evidence.source_snapshot.lifecycle_status
            ),
            payload_digest=payload.payload_digest,
            locator_type=payload.locator.locator_type,
            locator_value=payload.locator.locator_value,
            locator_schema_version=payload.locator.locator_schema_version,
        )
        identity_input = KnowledgeCandidateIdentityInput(
            candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
            statement_type=IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
            statement=request.statement,
            construction_rule_id=request.construction_rule_id,
            construction_rule_version=request.construction_rule_version,
            support=(evidence_support,),
            authority_status=INITIAL_AUTHORITY_STATUS,
            lifecycle_status=INITIAL_LIFECYCLE_STATUS,
            review_status=INITIAL_REVIEW_STATUS,
            conflict_status=INITIAL_CONFLICT_STATUS,
        )
        candidate_id = compute_knowledge_candidate_id(identity_input)
        knowledge_candidate = KnowledgeCandidate(
            knowledge_candidate_id=candidate_id,
            contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
            statement_type=IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
            statement=request.statement,
            support=(evidence_support,),
            construction_rule_id=request.construction_rule_id,
            construction_rule_version=request.construction_rule_version,
            authority_status=INITIAL_AUTHORITY_STATUS,
            lifecycle_status=INITIAL_LIFECYCLE_STATUS,
            review_status=INITIAL_REVIEW_STATUS,
            conflict_status=INITIAL_CONFLICT_STATUS,
            conflict_ids=(),
            diagnostics=(),
        )
        if compute_knowledge_candidate_id(
            identity_input_from_knowledge_candidate(knowledge_candidate)
        ) != knowledge_candidate.knowledge_candidate_id:
            return _empty_result(
                ImageKnowledgeConstructionDecision.SAFE_STOP,
                "KNOWLEDGE_CANDIDATE_IDENTITY_RECOMPUTATION_MISMATCH",
            )
        relationship_support = ImageKnowledgeRelationshipSupport(
            knowledge_candidate_id=knowledge_candidate.knowledge_candidate_id,
            evidence_id=accepted_evidence.evidence_id,
            acceptance_record_id=acceptance_record.acceptance_record_id,
            relationship_type=relationship.relationship_type,
            relationship_origin=relationship.origin,
            subject_evidence_id=relationship.subject_evidence_id,
            object_evidence_id=relationship.object_evidence_id,
            provenance_reference=relationship.provenance_reference,
            authority_reference=relationship.authority_reference,
            operator_reference=relationship.operator_reference,
            declaration_basis=relationship.declaration_basis,
            source_id=accepted_evidence.source_snapshot.source_id,
            source_content_digest=(
                accepted_evidence.source_snapshot.source_content_digest
            ),
            payload_digest=payload.payload_digest,
            source_lineage=accepted_evidence.provenance.lineage,
            evidence_materializer_id=(
                accepted_evidence.materialization_record.materializer_id
            ),
            evidence_materializer_version=(
                accepted_evidence.materialization_record.materializer_version
            ),
        )
    except (TypeError, ValueError):
        return _empty_result(
            ImageKnowledgeConstructionDecision.SAFE_STOP,
            "DOMAIN_CONSTRUCTION_SAFE_STOP",
        )

    return ImageKnowledgeConstructionResult(
        decision=ImageKnowledgeConstructionDecision.CONSTRUCTED,
        knowledge_candidate=knowledge_candidate,
        relationship_support=relationship_support,
        reason_codes=(),
        diagnostics=(),
    )
