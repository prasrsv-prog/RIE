"""Side-effect-free KnowledgeCandidate review-record construction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_review_record import (
    KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
    REVIEW_DECISION_DEFERRED,
    REVIEW_DECISION_PASSED,
    REVIEW_DECISION_REJECTED,
    KnowledgeReviewDiagnostic,
    KnowledgeReviewIdentityInput,
    KnowledgeReviewRecord,
    compute_knowledge_candidate_review_snapshot_digest,
    compute_knowledge_review_record_id,
)


KNOWLEDGE_REVIEW_POLICY_ID = "rcis-knowledge-candidate-review"
KNOWLEDGE_REVIEW_POLICY_VERSION = "1.0.0"

REVIEW_RESULT_STATUS_RECORDED = "recorded"
REVIEW_RESULT_STATUS_REJECTED = "rejected"

_SUPPORTED_REVIEW_DECISIONS = frozenset(
    {
        REVIEW_DECISION_PASSED,
        REVIEW_DECISION_REJECTED,
        REVIEW_DECISION_DEFERRED,
    }
)


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


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgeReviewDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgeReviewDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgeReviewRequest:
    knowledge_candidate: KnowledgeCandidate
    review_decision: str
    reason_codes: tuple[str, ...]
    reviewed_by: str
    reviewed_at: datetime
    review_policy_id: str
    review_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        for field_name in (
            "review_decision",
            "reviewed_by",
            "review_policy_id",
            "review_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=False,
        )
        _require_aware_datetime(self.reviewed_at, "reviewed_at")


@dataclass(frozen=True)
class KnowledgeReviewResult:
    result_status: str
    review_record: KnowledgeReviewRecord | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgeReviewDiagnostic, ...]

    def __post_init__(self) -> None:
        if self.result_status not in (
            REVIEW_RESULT_STATUS_RECORDED,
            REVIEW_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported review result status")
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=True,
        )
        _require_diagnostics(self.diagnostics)

        if self.result_status == REVIEW_RESULT_STATUS_RECORDED:
            if type(self.review_record) is not KnowledgeReviewRecord:
                raise ValueError("recorded result requires an exact review record")
            if self.reason_codes:
                raise ValueError("recorded result must not have reason codes")
        else:
            if self.review_record is not None:
                raise ValueError("rejected result must not have a review record")
            if not self.reason_codes:
                raise ValueError("rejected result requires reason codes")


_REJECTION_MESSAGES = {
    "unsupported_review_policy": "The review policy is unsupported.",
    "unsupported_review_decision": "The review decision is unsupported.",
}


def _rejected(reason_code: str) -> KnowledgeReviewResult:
    return KnowledgeReviewResult(
        result_status=REVIEW_RESULT_STATUS_REJECTED,
        review_record=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgeReviewDiagnostic(
                code=reason_code,
                severity="warning",
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_reviewer",
            ),
        ),
    )


def review_knowledge_candidate(
    request: KnowledgeReviewRequest,
) -> KnowledgeReviewResult:
    if type(request) is not KnowledgeReviewRequest:
        raise ValueError("request must be an exact KnowledgeReviewRequest")

    if (
        request.review_policy_id != KNOWLEDGE_REVIEW_POLICY_ID
        or request.review_policy_version != KNOWLEDGE_REVIEW_POLICY_VERSION
    ):
        return _rejected("unsupported_review_policy")
    if request.review_decision not in _SUPPORTED_REVIEW_DECISIONS:
        return _rejected("unsupported_review_decision")

    candidate = request.knowledge_candidate
    reviewed_evidence_ids = tuple(
        sorted({support.evidence_id for support in candidate.support})
    )
    reviewed_acceptance_record_ids = tuple(
        sorted(
            {
                acceptance_record_id
                for support in candidate.support
                for acceptance_record_id in support.acceptance_record_ids
            }
        )
    )
    reviewed_acceptance_review_record_ids = tuple(
        sorted(
            {
                review_record_id
                for support in candidate.support
                for review_record_id in support.acceptance_review_record_ids
            }
        )
    )
    candidate_snapshot_digest = (
        compute_knowledge_candidate_review_snapshot_digest(candidate)
    )

    identity_input = KnowledgeReviewIdentityInput(
        review_record_contract_version=KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        review_decision=request.review_decision,
        reason_codes=request.reason_codes,
        reviewed_evidence_ids=reviewed_evidence_ids,
        reviewed_acceptance_record_ids=reviewed_acceptance_record_ids,
        reviewed_acceptance_review_record_ids=(
            reviewed_acceptance_review_record_ids
        ),
        reviewed_by=request.reviewed_by,
        reviewed_at=request.reviewed_at,
        review_policy_id=request.review_policy_id,
        review_policy_version=request.review_policy_version,
    )
    record = KnowledgeReviewRecord(
        knowledge_review_record_id=compute_knowledge_review_record_id(
            identity_input
        ),
        contract_version=KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        review_decision=request.review_decision,
        reason_codes=request.reason_codes,
        reviewed_evidence_ids=reviewed_evidence_ids,
        reviewed_acceptance_record_ids=reviewed_acceptance_record_ids,
        reviewed_acceptance_review_record_ids=(
            reviewed_acceptance_review_record_ids
        ),
        reviewed_by=request.reviewed_by,
        reviewed_at=request.reviewed_at,
        review_policy_id=request.review_policy_id,
        review_policy_version=request.review_policy_version,
        diagnostics=(),
    )
    return KnowledgeReviewResult(
        result_status=REVIEW_RESULT_STATUS_RECORDED,
        review_record=record,
        reason_codes=(),
        diagnostics=(),
    )
