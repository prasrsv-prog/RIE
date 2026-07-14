"""Side-effect-free scope-limited Knowledge promotion execution recording."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.domain.knowledge_candidate import (
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_promotion_decision import (
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    PROMOTION_DECISION_OUTCOME_DEFERRED,
    KnowledgePromotionDecision,
    compute_knowledge_promotion_decision_id,
    knowledge_promotion_decision_identity_input_from_record,
)
from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
    KnowledgePromotionExecutionDiagnostic,
    KnowledgePromotionExecutionIdentityInput,
    KnowledgePromotionExecutionRecord,
    compute_knowledge_promotion_execution_id,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    KnowledgePromotionPrerequisiteEvaluation,
    compute_knowledge_promotion_prerequisite_evaluation_id,
    knowledge_promotion_prerequisite_identity_input_from_record,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID = "rcis-knowledge-promotion-execution"
KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION = "1.0.0"

PROMOTION_EXECUTION_RESULT_STATUS_RECORDED = "recorded"
PROMOTION_EXECUTION_RESULT_STATUS_REJECTED = "rejected"

PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY = (
    "unsupported_promotion_execution_policy"
)
PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME = (
    "unsupported_promotion_execution_outcome"
)
PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE = (
    "unsupported_promotion_execution_scope"
)
PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY = (
    "unsupported_promotion_decision_policy"
)
PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY = (
    "unsupported_prerequisite_evaluation_policy"
)
PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED = (
    "promotion_decision_deferred_for_execution"
)
PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED = (
    "promotion_decision_not_authorized_for_execution"
)
PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH = (
    "execution_candidate_mismatch"
)
PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH = (
    "execution_candidate_contract_mismatch"
)
PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH = (
    "execution_candidate_snapshot_mismatch"
)
PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH = (
    "execution_prerequisite_evaluation_mismatch"
)
PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON = (
    "missing_required_promotion_execution_reason"
)

PROMOTION_EXECUTION_REJECTION_REASONS = (
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY,
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED,
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON,
)

_SUPPORTED_PROMOTION_DECISION_POLICY_ID = "rcis-knowledge-promotion-decision"
_SUPPORTED_PROMOTION_DECISION_POLICY_VERSION = "1.0.0"

_REJECTION_MESSAGES = {
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY: (
        "The promotion execution policy is unsupported."
    ),
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME: (
        "The promotion execution outcome is unsupported."
    ),
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE: (
        "The promotion execution scope is unsupported."
    ),
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY: (
        "The promotion decision policy is unsupported."
    ),
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY: (
        "The prerequisite evaluation policy is unsupported."
    ),
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED: (
        "The promotion decision is deferred and cannot authorize execution."
    ),
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED: (
        "The promotion decision does not authorize execution."
    ),
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH: (
        "The execution lineage references another candidate."
    ),
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH: (
        "The execution lineage references another candidate contract."
    ),
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH: (
        "The execution lineage references another candidate snapshot."
    ),
    PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH: (
        "The promotion decision references another prerequisite evaluation."
    ),
    PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON: (
        "The request omits its required promotion execution reason."
    ),
}
if tuple(_REJECTION_MESSAGES) != PROMOTION_EXECUTION_REJECTION_REASONS:
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
        if type(diagnostic) is not KnowledgePromotionExecutionDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionExecutionDiagnostic"
            )


def _verify_candidate(candidate: KnowledgeCandidate) -> str:
    expected = compute_knowledge_candidate_id(
        identity_input_from_knowledge_candidate(candidate)
    )
    if candidate.knowledge_candidate_id != expected:
        raise ValueError("knowledge_candidate_id does not match identity")
    return expected


def _verify_evaluation(
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
) -> str:
    expected = compute_knowledge_promotion_prerequisite_evaluation_id(
        knowledge_promotion_prerequisite_identity_input_from_record(evaluation)
    )
    if evaluation.knowledge_promotion_prerequisite_evaluation_id != expected:
        raise ValueError(
            "knowledge_promotion_prerequisite_evaluation_id does not match identity"
        )
    return expected


def _verify_decision(decision: KnowledgePromotionDecision) -> str:
    expected = compute_knowledge_promotion_decision_id(
        knowledge_promotion_decision_identity_input_from_record(decision)
    )
    if decision.knowledge_promotion_decision_id != expected:
        raise ValueError("knowledge_promotion_decision_id does not match identity")
    return expected


@dataclass(frozen=True)
class KnowledgePromotionExecutionRequest:
    knowledge_candidate: KnowledgeCandidate
    promotion_prerequisite_evaluation: KnowledgePromotionPrerequisiteEvaluation
    promotion_decision: KnowledgePromotionDecision
    execution_scope: str
    execution_outcome: str
    execution_reference: str
    reason_codes: tuple[str, ...]
    executed_by: str
    executed_at: datetime
    execution_policy_id: str
    execution_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        _verify_candidate(self.knowledge_candidate)
        compute_knowledge_candidate_review_snapshot_digest(
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
        _verify_evaluation(self.promotion_prerequisite_evaluation)
        if type(self.promotion_decision) is not KnowledgePromotionDecision:
            raise ValueError(
                "promotion_decision must be an exact KnowledgePromotionDecision"
            )
        _verify_decision(self.promotion_decision)
        _require_string(self.execution_scope, "execution_scope")
        _require_string(self.execution_outcome, "execution_outcome")
        _require_string(self.execution_reference, "execution_reference")
        _require_reason_codes(self.reason_codes)
        _require_string(self.executed_by, "executed_by")
        _require_aware_datetime(self.executed_at, "executed_at")
        _require_string(self.execution_policy_id, "execution_policy_id")
        _require_string(
            self.execution_policy_version,
            "execution_policy_version",
        )


@dataclass(frozen=True)
class KnowledgePromotionExecutionResult:
    result_status: str
    promotion_execution_record: KnowledgePromotionExecutionRecord | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgePromotionExecutionDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            PROMOTION_EXECUTION_RESULT_STATUS_RECORDED,
            PROMOTION_EXECUTION_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported promotion execution result status")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        _require_diagnostics(self.diagnostics)
        if self.result_status == PROMOTION_EXECUTION_RESULT_STATUS_RECORDED:
            if (
                type(self.promotion_execution_record)
                is not KnowledgePromotionExecutionRecord
            ):
                raise ValueError(
                    "recorded result requires an exact "
                    "KnowledgePromotionExecutionRecord"
                )
            self.promotion_execution_record.__post_init__()
            if self.reason_codes != () or self.diagnostics != ():
                raise ValueError(
                    "recorded result reason codes and diagnostics must be empty"
                )
            if self.promotion_execution_record.diagnostics != ():
                raise ValueError("recorded execution diagnostics must be empty")
        else:
            if self.promotion_execution_record is not None:
                raise ValueError("rejected result must not contain a record")
            if (
                len(self.reason_codes) != 1
                or self.reason_codes[0]
                not in PROMOTION_EXECUTION_REJECTION_REASONS
            ):
                raise ValueError("rejected result requires one approved reason")
            if len(self.diagnostics) != 1:
                raise ValueError("rejected result requires one diagnostic")
            diagnostic = self.diagnostics[0]
            diagnostic.__post_init__()
            if (
                diagnostic.severity
                != KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING
            ):
                raise ValueError("rejected diagnostic severity must be warning")
            if diagnostic.code != self.reason_codes[0]:
                raise ValueError("rejected diagnostic code must equal reason")


def _rejected(reason_code: str) -> KnowledgePromotionExecutionResult:
    return KnowledgePromotionExecutionResult(
        result_status=PROMOTION_EXECUTION_RESULT_STATUS_REJECTED,
        promotion_execution_record=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgePromotionExecutionDiagnostic(
                code=reason_code,
                severity=(
                    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING
                ),
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_promotion_executor",
            ),
        ),
    )


def record_knowledge_promotion_execution(
    request: KnowledgePromotionExecutionRequest,
) -> KnowledgePromotionExecutionResult:
    if type(request) is not KnowledgePromotionExecutionRequest:
        raise ValueError(
            "request must be an exact KnowledgePromotionExecutionRequest"
        )
    request.__post_init__()

    candidate = request.knowledge_candidate
    evaluation = request.promotion_prerequisite_evaluation
    decision = request.promotion_decision

    if (
        request.execution_policy_id != KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID
        or request.execution_policy_version
        != KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION
    ):
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY
        )
    if request.execution_outcome != PROMOTION_EXECUTION_OUTCOME_COMPLETED:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME
        )
    if request.execution_scope != PROMOTION_EXECUTION_SCOPE_DECLARED:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE
        )
    if (
        decision.decision_policy_id != _SUPPORTED_PROMOTION_DECISION_POLICY_ID
        or decision.decision_policy_version
        != _SUPPORTED_PROMOTION_DECISION_POLICY_VERSION
    ):
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY
        )
    if (
        evaluation.evaluation_policy_id
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID
        or evaluation.evaluation_policy_version
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION
    ):
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY
        )
    if decision.promotion_decision == PROMOTION_DECISION_OUTCOME_DEFERRED:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED
        )
    if decision.promotion_decision != PROMOTION_DECISION_OUTCOME_AUTHORIZED:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED
        )
    if evaluation.knowledge_candidate_id != candidate.knowledge_candidate_id:
        return _rejected(PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH)
    if decision.knowledge_candidate_id != candidate.knowledge_candidate_id:
        return _rejected(PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH)
    if evaluation.knowledge_candidate_contract_version != candidate.contract_version:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH
        )
    if decision.knowledge_candidate_contract_version != candidate.contract_version:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH
        )

    candidate_snapshot = compute_knowledge_candidate_review_snapshot_digest(
        candidate
    )
    if evaluation.knowledge_candidate_snapshot_digest != candidate_snapshot:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH
        )
    if decision.knowledge_candidate_snapshot_digest != candidate_snapshot:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH
        )
    if (
        decision.knowledge_promotion_prerequisite_evaluation_id
        != evaluation.knowledge_promotion_prerequisite_evaluation_id
    ):
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH
        )
    if (
        decision.knowledge_promotion_prerequisite_evaluation_contract_version
        != evaluation.contract_version
    ):
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH
        )
    if decision.promotion_prerequisite_evaluation_outcome != evaluation.evaluation_outcome:
        return _rejected(
            PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH
        )
    if PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION not in request.reason_codes:
        return _rejected(PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON)

    identity_input = KnowledgePromotionExecutionIdentityInput(
        execution_record_contract_version=(
            KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION
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
        knowledge_promotion_decision_id=decision.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=decision.contract_version,
        promotion_decision_outcome=decision.promotion_decision,
        authorization_scope=decision.authorization_scope,
        execution_scope=request.execution_scope,
        execution_outcome=request.execution_outcome,
        execution_reference=request.execution_reference,
        reason_codes=request.reason_codes,
        executed_by=request.executed_by,
        executed_at=request.executed_at,
        execution_policy_id=request.execution_policy_id,
        execution_policy_version=request.execution_policy_version,
    )
    record = KnowledgePromotionExecutionRecord(
        knowledge_promotion_execution_id=(
            compute_knowledge_promotion_execution_id(identity_input)
        ),
        contract_version=identity_input.execution_record_contract_version,
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
        knowledge_promotion_decision_id=(
            identity_input.knowledge_promotion_decision_id
        ),
        knowledge_promotion_decision_contract_version=(
            identity_input.knowledge_promotion_decision_contract_version
        ),
        promotion_decision_outcome=identity_input.promotion_decision_outcome,
        authorization_scope=identity_input.authorization_scope,
        execution_scope=identity_input.execution_scope,
        execution_outcome=identity_input.execution_outcome,
        execution_reference=identity_input.execution_reference,
        reason_codes=identity_input.reason_codes,
        executed_by=identity_input.executed_by,
        executed_at=identity_input.executed_at,
        execution_policy_id=identity_input.execution_policy_id,
        execution_policy_version=identity_input.execution_policy_version,
        diagnostics=(),
    )
    return KnowledgePromotionExecutionResult(
        result_status=PROMOTION_EXECUTION_RESULT_STATUS_RECORDED,
        promotion_execution_record=record,
        reason_codes=(),
        diagnostics=(),
    )
