"""Side-effect-free Knowledge governance authorization construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_governance_decision import (
    AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION,
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
    KnowledgeGovernanceDecision,
    KnowledgeGovernanceDiagnostic,
    KnowledgeGovernanceIdentityInput,
    compute_knowledge_governance_candidate_snapshot_digest,
    compute_knowledge_governance_decision_id,
    verify_knowledge_review_record_identity,
)
from rie.domain.knowledge_review_record import (
    REVIEW_DECISION_DEFERRED,
    REVIEW_DECISION_PASSED,
    REVIEW_DECISION_REJECTED,
    KnowledgeReviewRecord,
)


KNOWLEDGE_GOVERNANCE_POLICY_ID = "rcis-knowledge-governance-authorization"
KNOWLEDGE_GOVERNANCE_POLICY_VERSION = "1.0.0"

ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_ID = "rcis-knowledge-candidate-review"
ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_VERSION = "1.0.0"

GOVERNANCE_RESULT_STATUS_RECORDED = "recorded"
GOVERNANCE_RESULT_STATUS_REJECTED = "rejected"

_SUPPORTED_GOVERNANCE_DECISIONS = frozenset(
    {
        GOVERNANCE_DECISION_AUTHORIZED,
        GOVERNANCE_DECISION_DENIED,
        GOVERNANCE_DECISION_DEFERRED,
    }
)

_REJECTION_MESSAGES = {
    "unsupported_governance_policy": (
        "The governance application policy is unsupported."
    ),
    "unsupported_governance_decision": (
        "The requested governance decision is unsupported."
    ),
    "unsupported_review_evidence_policy": (
        "At least one review record uses an unsupported evidence policy."
    ),
    "review_candidate_mismatch": (
        "At least one review record references another candidate."
    ),
    "review_candidate_contract_mismatch": (
        "At least one review record references another candidate contract."
    ),
    "review_candidate_snapshot_mismatch": (
        "At least one review record references another candidate snapshot."
    ),
    "ineligible_review_evidence": (
        "The complete review evidence is ineligible for authorization."
    ),
    "contradictory_review_evidence": (
        "The complete review evidence is contradictory."
    ),
    "incomplete_review_evidence": (
        "The complete review evidence is incomplete."
    ),
    "incompatible_governance_decision": (
        "The requested governance decision is incompatible with the evidence."
    ),
    "missing_required_governance_reason": (
        "The required governance reason is missing."
    ),
}


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_reason_codes(
    value: object,
    field_name: str,
    *,
    allow_empty: bool,
) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _require_string(item, f"{field_name}[{index}]")
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if value != tuple(sorted(value)):
        raise ValueError(f"{field_name} must be lexicographically ordered")


def _require_review_records(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("knowledge_review_records must be a tuple")
    if not value:
        raise ValueError("knowledge_review_records must not be empty")
    record_ids: list[str] = []
    for index, record in enumerate(value):
        if type(record) is not KnowledgeReviewRecord:
            raise ValueError(
                f"knowledge_review_records[{index}] must be an exact "
                "KnowledgeReviewRecord"
            )
        record_ids.append(verify_knowledge_review_record_identity(record))
    if len(set(record_ids)) != len(record_ids):
        raise ValueError("knowledge_review_records must contain unique IDs")
    if record_ids != sorted(record_ids):
        raise ValueError(
            "knowledge_review_records must be ordered by review-record ID"
        )


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgeGovernanceDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgeGovernanceDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgeGovernanceRequest:
    knowledge_candidate: KnowledgeCandidate
    knowledge_review_records: tuple[KnowledgeReviewRecord, ...]
    governance_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    governance_policy_id: str
    governance_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        _require_review_records(self.knowledge_review_records)
        for field_name in (
            "governance_decision",
            "decided_by",
            "governance_policy_id",
            "governance_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=False,
        )
        _require_aware_datetime(self.decided_at, "decided_at")


@dataclass(frozen=True)
class KnowledgeGovernanceResult:
    result_status: str
    governance_decision_record: KnowledgeGovernanceDecision | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgeGovernanceDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            GOVERNANCE_RESULT_STATUS_RECORDED,
            GOVERNANCE_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported governance result status")
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=True,
        )
        _require_diagnostics(self.diagnostics)

        if self.result_status == GOVERNANCE_RESULT_STATUS_RECORDED:
            if type(self.governance_decision_record) is not KnowledgeGovernanceDecision:
                raise ValueError(
                    "recorded result requires an exact governance decision"
                )
            if self.reason_codes:
                raise ValueError("recorded result must not have reason codes")
        else:
            if self.governance_decision_record is not None:
                raise ValueError(
                    "rejected result must not have a governance decision"
                )
            if len(self.reason_codes) != 1:
                raise ValueError(
                    "rejected result requires exactly one reason code"
                )


def _rejected(reason_code: str) -> KnowledgeGovernanceResult:
    return KnowledgeGovernanceResult(
        result_status=GOVERNANCE_RESULT_STATUS_REJECTED,
        governance_decision_record=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgeGovernanceDiagnostic(
                code=reason_code,
                severity="warning",
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_governor",
            ),
        ),
    )


def _matrix_outcome(
    review_decisions: frozenset[str],
    requested_decision: str,
) -> tuple[str | None, str | None]:
    if review_decisions == frozenset({REVIEW_DECISION_PASSED}):
        if requested_decision == GOVERNANCE_DECISION_AUTHORIZED:
            return None, "eligible_review_evidence"
        if requested_decision == GOVERNANCE_DECISION_DEFERRED:
            return None, "governance_evaluation_deferred"
        return "incompatible_governance_decision", None

    if review_decisions == frozenset({REVIEW_DECISION_REJECTED}):
        if requested_decision == GOVERNANCE_DECISION_DENIED:
            return None, "review_evidence_rejected"
        if requested_decision == GOVERNANCE_DECISION_DEFERRED:
            return None, "governance_evaluation_deferred"
        return "ineligible_review_evidence", None

    if REVIEW_DECISION_PASSED in review_decisions and REVIEW_DECISION_REJECTED in review_decisions:
        if requested_decision == GOVERNANCE_DECISION_DEFERRED:
            return None, "contradictory_review_evidence"
        return "contradictory_review_evidence", None

    if requested_decision == GOVERNANCE_DECISION_DEFERRED:
        return None, "incomplete_review_evidence"
    return "incomplete_review_evidence", None


def govern_knowledge_candidate(
    request: KnowledgeGovernanceRequest,
) -> KnowledgeGovernanceResult:
    if type(request) is not KnowledgeGovernanceRequest:
        raise ValueError("request must be an exact KnowledgeGovernanceRequest")

    _require_review_records(request.knowledge_review_records)

    if (
        request.governance_policy_id != KNOWLEDGE_GOVERNANCE_POLICY_ID
        or request.governance_policy_version
        != KNOWLEDGE_GOVERNANCE_POLICY_VERSION
    ):
        return _rejected("unsupported_governance_policy")

    if request.governance_decision not in _SUPPORTED_GOVERNANCE_DECISIONS:
        return _rejected("unsupported_governance_decision")

    if any(
        record.review_policy_id != ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_ID
        or record.review_policy_version
        != ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_VERSION
        for record in request.knowledge_review_records
    ):
        return _rejected("unsupported_review_evidence_policy")

    candidate = request.knowledge_candidate
    if any(
        record.knowledge_candidate_id != candidate.knowledge_candidate_id
        for record in request.knowledge_review_records
    ):
        return _rejected("review_candidate_mismatch")

    if any(
        record.knowledge_candidate_contract_version != candidate.contract_version
        for record in request.knowledge_review_records
    ):
        return _rejected("review_candidate_contract_mismatch")

    candidate_snapshot_digest = (
        compute_knowledge_governance_candidate_snapshot_digest(candidate)
    )
    if any(
        record.knowledge_candidate_snapshot_digest != candidate_snapshot_digest
        for record in request.knowledge_review_records
    ):
        return _rejected("review_candidate_snapshot_mismatch")

    review_decisions = frozenset(
        record.review_decision for record in request.knowledge_review_records
    )
    rejection, required_reason = _matrix_outcome(
        review_decisions,
        request.governance_decision,
    )
    if rejection is not None:
        return _rejected(rejection)
    assert required_reason is not None
    if required_reason not in request.reason_codes:
        return _rejected("missing_required_governance_reason")

    review_record_ids = tuple(
        record.knowledge_review_record_id
        for record in request.knowledge_review_records
    )
    identity_input = KnowledgeGovernanceIdentityInput(
        governance_decision_contract_version=(
            KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        knowledge_review_record_ids=review_record_ids,
        authorization_scope=(
            AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        ),
        governance_decision=request.governance_decision,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        governance_policy_id=request.governance_policy_id,
        governance_policy_version=request.governance_policy_version,
    )
    record = KnowledgeGovernanceDecision(
        knowledge_governance_decision_id=(
            compute_knowledge_governance_decision_id(identity_input)
        ),
        contract_version=KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        knowledge_review_record_ids=review_record_ids,
        authorization_scope=(
            AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        ),
        governance_decision=request.governance_decision,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        governance_policy_id=request.governance_policy_id,
        governance_policy_version=request.governance_policy_version,
        diagnostics=(),
    )
    return KnowledgeGovernanceResult(
        result_status=GOVERNANCE_RESULT_STATUS_RECORDED,
        governance_decision_record=record,
        reason_codes=(),
        diagnostics=(),
    )
