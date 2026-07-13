"""Deterministic AcceptedEvidence-to-KnowledgeCandidate construction."""

from __future__ import annotations

from dataclasses import dataclass

from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence
from rie.domain.knowledge_candidate import (
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    VERBATIM_TEXT_STATEMENT_TYPE,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeDiagnostic,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
)


VERBATIM_TEXT_RULE_ID = "rcis-accepted-text-verbatim"
VERBATIM_TEXT_RULE_VERSION = "1.0.0"
SUPPORTED_TEXT_PAYLOAD_SCHEMA_VERSION = "1.0.0"

CONSTRUCTION_DECISION_CONSTRUCTED = "constructed"
CONSTRUCTION_DECISION_REJECTED = "rejected"


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True)
class KnowledgeConstructionRequest:
    accepted_evidence: AcceptedEvidence
    acceptance_records: tuple[AcceptanceRecord, ...]
    construction_rule_id: str
    construction_rule_version: str

    def __post_init__(self) -> None:
        if type(self.accepted_evidence) is not AcceptedEvidence:
            raise ValueError("accepted_evidence must be an exact AcceptedEvidence")
        if type(self.acceptance_records) is not tuple:
            raise ValueError("acceptance_records must be a tuple")
        if not self.acceptance_records:
            raise ValueError("acceptance_records must not be empty")
        for index, record in enumerate(self.acceptance_records):
            if type(record) is not AcceptanceRecord:
                raise ValueError(
                    f"acceptance_records[{index}] must be an exact AcceptanceRecord"
                )
        _require_string(self.construction_rule_id, "construction_rule_id")
        _require_string(
            self.construction_rule_version,
            "construction_rule_version",
        )


@dataclass(frozen=True)
class KnowledgeConstructionResult:
    decision: str
    knowledge_candidate: KnowledgeCandidate | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgeDiagnostic, ...]

    def __post_init__(self) -> None:
        if self.decision not in (
            CONSTRUCTION_DECISION_CONSTRUCTED,
            CONSTRUCTION_DECISION_REJECTED,
        ):
            raise ValueError("unsupported construction decision")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        for index, reason_code in enumerate(self.reason_codes):
            _require_string(reason_code, f"reason_codes[{index}]")
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")
        for index, diagnostic in enumerate(self.diagnostics):
            if type(diagnostic) is not KnowledgeDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact KnowledgeDiagnostic"
                )

        if self.decision == CONSTRUCTION_DECISION_CONSTRUCTED:
            if type(self.knowledge_candidate) is not KnowledgeCandidate:
                raise ValueError("constructed result requires a candidate")
            if self.reason_codes:
                raise ValueError("constructed result must not have reason codes")
        else:
            if self.knowledge_candidate is not None:
                raise ValueError("rejected result must not have a candidate")
            if not self.reason_codes:
                raise ValueError("rejected result requires reason codes")


_REJECTION_MESSAGES = {
    "unsupported_construction_rule": "The construction rule is unsupported.",
    "duplicate_acceptance_record_id": "Acceptance record IDs are duplicated.",
    "acceptance_record_evidence_id_mismatch": (
        "An acceptance record references another Evidence ID."
    ),
    "missing_materialization_acceptance_record": (
        "The materialization acceptance record is missing."
    ),
    "materialization_acceptance_mismatch": (
        "Materialization and acceptance governance do not match."
    ),
    "ineligible_accepted_evidence": "The accepted Evidence is not eligible.",
    "unsupported_payload_type": "The factual payload type is unsupported.",
    "unsupported_payload_schema": "The factual payload schema is unsupported.",
    "unsupported_payload_shape": "The factual payload shape is unsupported.",
    "missing_text": "The factual payload has no text entry.",
    "non_string_text": "The factual payload text is not a string.",
    "empty_text": "The factual payload text is empty.",
    "invalid_support_provenance": "The support provenance is invalid.",
}


def _rejected(reason_code: str) -> KnowledgeConstructionResult:
    return KnowledgeConstructionResult(
        decision=CONSTRUCTION_DECISION_REJECTED,
        knowledge_candidate=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgeDiagnostic(
                code=reason_code,
                severity="warning",
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_constructor",
            ),
        ),
    )


def _materialization_matches(
    accepted_evidence: AcceptedEvidence,
    record: AcceptanceRecord,
) -> bool:
    materialization = accepted_evidence.materialization_record
    return (
        record.accepted_by == materialization.accepted_by
        and record.acceptance_reason == materialization.acceptance_reason
        and record.review_record_id == materialization.review_record_id
        and record.materializer_id == materialization.materializer_id
        and record.materializer_version == materialization.materializer_version
        and record.accepted_at == materialization.materialized_at
    )


def _extract_text(accepted_evidence: AcceptedEvidence) -> tuple[str | None, str | None]:
    payload_contract = accepted_evidence.factual_payload
    if payload_contract.payload_type != "text":
        return None, "unsupported_payload_type"
    if (
        payload_contract.payload_schema_version
        != SUPPORTED_TEXT_PAYLOAD_SCHEMA_VERSION
    ):
        return None, "unsupported_payload_schema"

    payload = payload_contract.payload
    if type(payload) is not tuple or len(payload) != 1:
        return None, "unsupported_payload_shape"
    entry = payload[0]
    if type(entry) is not tuple or len(entry) != 2:
        return None, "unsupported_payload_shape"
    if entry[0] != "text":
        return None, "missing_text"
    if type(entry[1]) is not str:
        return None, "non_string_text"
    if not entry[1].strip():
        return None, "empty_text"
    return entry[1], None


def construct_knowledge_candidate(
    request: KnowledgeConstructionRequest,
) -> KnowledgeConstructionResult:
    if type(request) is not KnowledgeConstructionRequest:
        raise ValueError("request must be an exact KnowledgeConstructionRequest")

    if (
        request.construction_rule_id != VERBATIM_TEXT_RULE_ID
        or request.construction_rule_version != VERBATIM_TEXT_RULE_VERSION
    ):
        return _rejected("unsupported_construction_rule")

    evidence = request.accepted_evidence
    record_ids = tuple(
        record.acceptance_record_id for record in request.acceptance_records
    )
    if len(set(record_ids)) != len(record_ids):
        return _rejected("duplicate_acceptance_record_id")
    if any(
        record.evidence_id != evidence.evidence_id
        for record in request.acceptance_records
    ):
        return _rejected("acceptance_record_evidence_id_mismatch")

    materialization_record_id = (
        evidence.materialization_record.acceptance_record_id
    )
    matching_records = tuple(
        record
        for record in request.acceptance_records
        if record.acceptance_record_id == materialization_record_id
    )
    if not matching_records:
        return _rejected("missing_materialization_acceptance_record")
    if not _materialization_matches(evidence, matching_records[0]):
        return _rejected("materialization_acceptance_mismatch")
    if evidence.eligibility_result.decision != "eligible":
        return _rejected("ineligible_accepted_evidence")

    statement, rejection = _extract_text(evidence)
    if rejection is not None:
        return _rejected(rejection)
    assert statement is not None

    try:
        support = KnowledgeEvidenceSupport(
            evidence_id=evidence.evidence_id,
            acceptance_record_ids=tuple(sorted(record_ids)),
            acceptance_review_record_ids=tuple(
                sorted(
                    {
                        record.review_record_id
                        for record in request.acceptance_records
                    }
                )
            ),
            source_id=evidence.source_snapshot.source_id,
            source_content_digest=(
                evidence.source_snapshot.source_content_digest
            ),
            source_authority_status=(
                evidence.source_snapshot.authority_status
            ),
            source_lifecycle_status=(
                evidence.source_snapshot.lifecycle_status
            ),
            payload_digest=evidence.factual_payload.payload_digest,
            locator_type=evidence.factual_payload.locator.locator_type,
            locator_value=evidence.factual_payload.locator.locator_value,
            locator_schema_version=(
                evidence.factual_payload.locator.locator_schema_version
            ),
        )
    except ValueError:
        return _rejected("invalid_support_provenance")

    identity_input = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement,
        construction_rule_id=request.construction_rule_id,
        construction_rule_version=request.construction_rule_version,
        support=(support,),
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
    )
    candidate = KnowledgeCandidate(
        knowledge_candidate_id=compute_knowledge_candidate_id(identity_input),
        contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement,
        support=(support,),
        construction_rule_id=request.construction_rule_id,
        construction_rule_version=request.construction_rule_version,
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
        conflict_ids=(),
        diagnostics=(),
    )
    return KnowledgeConstructionResult(
        decision=CONSTRUCTION_DECISION_CONSTRUCTED,
        knowledge_candidate=candidate,
        reason_codes=(),
        diagnostics=(),
    )
