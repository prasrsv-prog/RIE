"""Side-effect-free pairwise Knowledge conflict assessment recording."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_conflict_assessment_record import (
    ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
    ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
    ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
    ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP,
    KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION,
    KnowledgeConflictAssessmentRecord,
    KnowledgeConflictDiagnostic,
    KnowledgeConflictIdentityInput,
    compute_knowledge_conflict_assessment_record_id,
    knowledge_conflict_participant_from_candidate,
    verify_knowledge_conflict_candidate_identity,
)


KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID = (
    "rcis-knowledge-pairwise-conflict-assessment"
)
KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION = "1.0.0"

CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED = "recorded"
CONFLICT_ASSESSMENT_RESULT_STATUS_REJECTED = "rejected"

_REQUIRED_OUTCOME_REASONS = {
    ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED: "semantic_conflict_identified",
    ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT: (
        "semantic_equivalence_identified"
    ),
    ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED: (
        "pairwise_no_conflict_identified"
    ),
    ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED: "semantic_assessment_deferred",
}

_REJECTION_MESSAGES = {
    "unsupported_conflict_assessment_policy": (
        "The conflict assessment application policy is unsupported."
    ),
    "unsupported_conflict_assessment_outcome": (
        "The requested conflict assessment outcome is unsupported."
    ),
    "missing_required_conflict_assessment_reason": (
        "The required conflict assessment reason is missing."
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


def _require_participants(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("participants must be a tuple")
    if len(value) != 2:
        raise ValueError("participants must contain exactly two candidates")
    candidate_ids: list[str] = []
    for index, candidate in enumerate(value):
        if type(candidate) is not KnowledgeCandidate:
            raise ValueError(
                f"participants[{index}] must be an exact KnowledgeCandidate"
            )
        candidate_ids.append(
            verify_knowledge_conflict_candidate_identity(candidate)
        )
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("participants must contain unique candidate IDs")
    if candidate_ids != sorted(candidate_ids):
        raise ValueError("participants must be ordered by candidate ID")


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgeConflictDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgeConflictDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgeConflictAssessmentRequest:
    participants: tuple[KnowledgeCandidate, ...]
    assessment_outcome: str
    reason_codes: tuple[str, ...]
    assessed_by: str
    assessed_at: datetime
    assessment_policy_id: str
    assessment_policy_version: str

    def __post_init__(self) -> None:
        _require_participants(self.participants)
        for field_name in (
            "assessment_outcome",
            "assessed_by",
            "assessment_policy_id",
            "assessment_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=False,
        )
        _require_aware_datetime(self.assessed_at, "assessed_at")


@dataclass(frozen=True)
class KnowledgeConflictAssessmentResult:
    result_status: str
    conflict_assessment_record: KnowledgeConflictAssessmentRecord | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgeConflictDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED,
            CONFLICT_ASSESSMENT_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported conflict assessment result status")
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=True,
        )
        _require_diagnostics(self.diagnostics)
        if self.result_status == CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED:
            if (
                type(self.conflict_assessment_record)
                is not KnowledgeConflictAssessmentRecord
            ):
                raise ValueError(
                    "recorded result requires an exact conflict assessment record"
                )
            if self.reason_codes:
                raise ValueError("recorded result must not have reason codes")
        else:
            if self.conflict_assessment_record is not None:
                raise ValueError(
                    "rejected result must not have a conflict assessment record"
                )
            if len(self.reason_codes) != 1:
                raise ValueError(
                    "rejected result requires exactly one reason code"
                )


def _rejected(reason_code: str) -> KnowledgeConflictAssessmentResult:
    return KnowledgeConflictAssessmentResult(
        result_status=CONFLICT_ASSESSMENT_RESULT_STATUS_REJECTED,
        conflict_assessment_record=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgeConflictDiagnostic(
                code=reason_code,
                severity="warning",
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_conflict_assessor",
            ),
        ),
    )


def assess_knowledge_candidate_conflict(
    request: KnowledgeConflictAssessmentRequest,
) -> KnowledgeConflictAssessmentResult:
    if type(request) is not KnowledgeConflictAssessmentRequest:
        raise ValueError(
            "request must be an exact KnowledgeConflictAssessmentRequest"
        )

    _require_participants(request.participants)

    if (
        request.assessment_policy_id
        != KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID
        or request.assessment_policy_version
        != KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION
    ):
        return _rejected("unsupported_conflict_assessment_policy")

    required_reason = _REQUIRED_OUTCOME_REASONS.get(
        request.assessment_outcome
    )
    if required_reason is None:
        return _rejected("unsupported_conflict_assessment_outcome")

    if required_reason not in request.reason_codes:
        return _rejected("missing_required_conflict_assessment_reason")

    participants = tuple(
        knowledge_conflict_participant_from_candidate(candidate)
        for candidate in request.participants
    )
    identity_input = KnowledgeConflictIdentityInput(
        conflict_assessment_record_contract_version=(
            KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION
        ),
        participants=participants,
        assessment_scope=(
            ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
        ),
        assessment_outcome=request.assessment_outcome,
        reason_codes=request.reason_codes,
        assessed_by=request.assessed_by,
        assessed_at=request.assessed_at,
        assessment_policy_id=request.assessment_policy_id,
        assessment_policy_version=request.assessment_policy_version,
    )
    record = KnowledgeConflictAssessmentRecord(
        knowledge_conflict_assessment_record_id=(
            compute_knowledge_conflict_assessment_record_id(identity_input)
        ),
        contract_version=(
            KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION
        ),
        participants=participants,
        assessment_scope=(
            ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
        ),
        assessment_outcome=request.assessment_outcome,
        reason_codes=request.reason_codes,
        assessed_by=request.assessed_by,
        assessed_at=request.assessed_at,
        assessment_policy_id=request.assessment_policy_id,
        assessment_policy_version=request.assessment_policy_version,
        diagnostics=(),
    )
    return KnowledgeConflictAssessmentResult(
        result_status=CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED,
        conflict_assessment_record=record,
        reason_codes=(),
        diagnostics=(),
    )
