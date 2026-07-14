"""Side-effect-free scope-limited Knowledge promotion decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_promotion_decision import (
    KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    PROMOTION_DECISION_OUTCOME_DEFERRED,
    PROMOTION_DECISION_OUTCOME_DENIED,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    KnowledgePromotionDecision,
    KnowledgePromotionDecisionDiagnostic,
    KnowledgePromotionDecisionIdentityInput,
    compute_knowledge_promotion_decision_candidate_snapshot_digest,
    compute_knowledge_promotion_decision_id,
    verify_knowledge_promotion_decision_candidate_identity,
    verify_knowledge_promotion_prerequisite_evaluation_identity,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    KnowledgePromotionPrerequisiteEvaluation,
)


KNOWLEDGE_PROMOTION_DECISION_POLICY_ID = "rcis-knowledge-promotion-decision"
KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION = "1.0.0"

PROMOTION_DECISION_RESULT_STATUS_RECORDED = "recorded"
PROMOTION_DECISION_RESULT_STATUS_REJECTED = "rejected"

PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY = (
    "unsupported_promotion_decision_policy"
)
PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION = (
    "unsupported_promotion_decision"
)
PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY = (
    "unsupported_prerequisite_evaluation_policy"
)
PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH = (
    "decision_candidate_mismatch"
)
PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH = (
    "decision_candidate_contract_mismatch"
)
PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH = (
    "decision_candidate_snapshot_mismatch"
)
PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION = (
    "ineligible_prerequisite_evaluation"
)
PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION = (
    "incomplete_prerequisite_evaluation"
)
PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON = (
    "missing_required_promotion_decision_reason"
)

PROMOTION_DECISION_REJECTION_REASONS = (
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY,
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION,
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH,
    PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION,
    PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION,
    PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON,
)

_PROMOTION_DECISIONS = frozenset(
    {
        PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        PROMOTION_DECISION_OUTCOME_DENIED,
        PROMOTION_DECISION_OUTCOME_DEFERRED,
    }
)

_REJECTION_MESSAGES = {
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY: (
        "The promotion decision policy is unsupported."
    ),
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION: (
        "The requested promotion decision is unsupported."
    ),
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY: (
        "The prerequisite evaluation policy is unsupported."
    ),
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH: (
        "The prerequisite evaluation references another candidate."
    ),
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH: (
        "The prerequisite evaluation references another candidate contract."
    ),
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH: (
        "The prerequisite evaluation references another candidate snapshot."
    ),
    PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION: (
        "The not-satisfied prerequisite evaluation cannot authorize execution."
    ),
    PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION: (
        "The deferred prerequisite evaluation cannot authorize or deny execution."
    ),
    PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON: (
        "The request omits its required promotion decision reason."
    ),
}
if tuple(_REJECTION_MESSAGES) != PROMOTION_DECISION_REJECTION_REASONS:
    raise RuntimeError("rejection precedence does not match the contract")


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_reason_codes(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("reason_codes must be a tuple")
    if not value:
        raise ValueError("reason_codes must not be empty")
    for index, item in enumerate(value):
        _require_string(item, f"reason_codes[{index}]")
    if len(set(value)) != len(value):
        raise ValueError("reason_codes must contain unique values")
    if value != tuple(sorted(value)):
        raise ValueError("reason_codes must be lexicographically ordered")


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgePromotionDecisionDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionDecisionDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgePromotionDecisionRequest:
    knowledge_candidate: KnowledgeCandidate
    promotion_prerequisite_evaluation: KnowledgePromotionPrerequisiteEvaluation
    promotion_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    decision_policy_id: str
    decision_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        verify_knowledge_promotion_decision_candidate_identity(
            self.knowledge_candidate
        )
        if (
            type(self.promotion_prerequisite_evaluation)
            is not KnowledgePromotionPrerequisiteEvaluation
        ):
            raise ValueError(
                "promotion_prerequisite_evaluation must be an exact "
                "KnowledgePromotionPrerequisiteEvaluation"
            )
        verify_knowledge_promotion_prerequisite_evaluation_identity(
            self.promotion_prerequisite_evaluation
        )
        _require_string(self.promotion_decision, "promotion_decision")
        _require_reason_codes(self.reason_codes)
        _require_string(self.decided_by, "decided_by")
        _require_aware_datetime(self.decided_at, "decided_at")
        _require_string(self.decision_policy_id, "decision_policy_id")
        _require_string(self.decision_policy_version, "decision_policy_version")


@dataclass(frozen=True)
class KnowledgePromotionDecisionResult:
    result_status: str
    promotion_decision_record: KnowledgePromotionDecision | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgePromotionDecisionDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            PROMOTION_DECISION_RESULT_STATUS_RECORDED,
            PROMOTION_DECISION_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported promotion decision result status")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        _require_diagnostics(self.diagnostics)
        if self.result_status == PROMOTION_DECISION_RESULT_STATUS_RECORDED:
            if type(self.promotion_decision_record) is not KnowledgePromotionDecision:
                raise ValueError(
                    "recorded result requires an exact KnowledgePromotionDecision"
                )
            self.promotion_decision_record.__post_init__()
            if self.reason_codes != () or self.diagnostics != ():
                raise ValueError(
                    "recorded result reason codes and diagnostics must be empty"
                )
            if self.promotion_decision_record.diagnostics != ():
                raise ValueError("recorded decision diagnostics must be empty")
        else:
            if self.promotion_decision_record is not None:
                raise ValueError("rejected result must not contain a decision")
            if (
                len(self.reason_codes) != 1
                or self.reason_codes[0] not in PROMOTION_DECISION_REJECTION_REASONS
            ):
                raise ValueError("rejected result requires one approved reason")
            if len(self.diagnostics) != 1:
                raise ValueError("rejected result requires one diagnostic")
            diagnostic = self.diagnostics[0]
            diagnostic.__post_init__()
            if (
                diagnostic.severity
                != KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING
            ):
                raise ValueError("rejected diagnostic severity must be warning")
            if diagnostic.code != self.reason_codes[0]:
                raise ValueError("rejected diagnostic code must equal reason")


def _rejected(reason_code: str) -> KnowledgePromotionDecisionResult:
    return KnowledgePromotionDecisionResult(
        result_status=PROMOTION_DECISION_RESULT_STATUS_REJECTED,
        promotion_decision_record=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgePromotionDecisionDiagnostic(
                code=reason_code,
                severity=(
                    KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING
                ),
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_promotion_decider",
            ),
        ),
    )


def _required_reason(evaluation_outcome: str, decision: str) -> str:
    matrix = {
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        ): PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_DENIED,
        ): PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_DEFERRED,
        ): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_DENIED,
        ): PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_DEFERRED,
        ): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
        (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
            PROMOTION_DECISION_OUTCOME_DEFERRED,
        ): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
    }
    return matrix[(evaluation_outcome, decision)]


def decide_knowledge_promotion(
    request: KnowledgePromotionDecisionRequest,
) -> KnowledgePromotionDecisionResult:
    if type(request) is not KnowledgePromotionDecisionRequest:
        raise ValueError(
            "request must be an exact KnowledgePromotionDecisionRequest"
        )
    request.__post_init__()

    candidate = request.knowledge_candidate
    evaluation = request.promotion_prerequisite_evaluation

    if (
        request.decision_policy_id != KNOWLEDGE_PROMOTION_DECISION_POLICY_ID
        or request.decision_policy_version
        != KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION
    ):
        return _rejected(
            PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY
        )
    if request.promotion_decision not in _PROMOTION_DECISIONS:
        return _rejected(
            PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION
        )
    if (
        evaluation.evaluation_policy_id
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID
        or evaluation.evaluation_policy_version
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION
    ):
        return _rejected(
            PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY
        )
    if evaluation.knowledge_candidate_id != candidate.knowledge_candidate_id:
        return _rejected(
            PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH
        )
    if evaluation.knowledge_candidate_contract_version != candidate.contract_version:
        return _rejected(
            PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH
        )

    candidate_snapshot = (
        compute_knowledge_promotion_decision_candidate_snapshot_digest(candidate)
    )
    if evaluation.knowledge_candidate_snapshot_digest != candidate_snapshot:
        return _rejected(
            PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH
        )
    if (
        evaluation.evaluation_outcome
        == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE
        and request.promotion_decision == PROMOTION_DECISION_OUTCOME_AUTHORIZED
    ):
        return _rejected(
            PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION
        )
    if (
        evaluation.evaluation_outcome
        == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
        and request.promotion_decision
        in (PROMOTION_DECISION_OUTCOME_AUTHORIZED, PROMOTION_DECISION_OUTCOME_DENIED)
    ):
        return _rejected(
            PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION
        )

    required_reason = _required_reason(
        evaluation.evaluation_outcome,
        request.promotion_decision,
    )
    if required_reason not in request.reason_codes:
        return _rejected(
            PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON
        )

    identity_input = KnowledgePromotionDecisionIdentityInput(
        decision_record_contract_version=(
            KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot,
        knowledge_promotion_prerequisite_evaluation_id=(
            evaluation.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            evaluation.contract_version
        ),
        promotion_prerequisite_evaluation_outcome=evaluation.evaluation_outcome,
        authorization_scope=PROMOTION_DECISION_AUTHORIZATION_SCOPE,
        promotion_decision=request.promotion_decision,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        decision_policy_id=request.decision_policy_id,
        decision_policy_version=request.decision_policy_version,
    )
    decision = KnowledgePromotionDecision(
        knowledge_promotion_decision_id=(
            compute_knowledge_promotion_decision_id(identity_input)
        ),
        contract_version=identity_input.decision_record_contract_version,
        knowledge_candidate_id=identity_input.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity_input.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity_input.knowledge_candidate_snapshot_digest
        ),
        knowledge_promotion_prerequisite_evaluation_id=(
            identity_input.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            identity_input.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        promotion_prerequisite_evaluation_outcome=(
            identity_input.promotion_prerequisite_evaluation_outcome
        ),
        authorization_scope=identity_input.authorization_scope,
        promotion_decision=identity_input.promotion_decision,
        reason_codes=identity_input.reason_codes,
        decided_by=identity_input.decided_by,
        decided_at=identity_input.decided_at,
        decision_policy_id=identity_input.decision_policy_id,
        decision_policy_version=identity_input.decision_policy_version,
        diagnostics=(),
    )
    return KnowledgePromotionDecisionResult(
        result_status=PROMOTION_DECISION_RESULT_STATUS_RECORDED,
        promotion_decision_record=decision,
        reason_codes=(),
        diagnostics=(),
    )
