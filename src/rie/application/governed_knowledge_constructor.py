from dataclasses import dataclass
from datetime import datetime

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeDiagnostic,
    GovernedKnowledgeIdentityInput,
    compute_governed_knowledge_id,
)
from rie.domain.knowledge_candidate import (
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_promotion_decision import (
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    KnowledgePromotionDecision,
    compute_knowledge_promotion_decision_id,
    knowledge_promotion_decision_identity_input_from_record,
)
from rie.domain.knowledge_promotion_execution import (
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
    KnowledgePromotionExecutionRecord,
    compute_knowledge_promotion_execution_id,
    knowledge_promotion_execution_identity_input_from_record,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    KnowledgePromotionPrerequisiteEvaluation,
    compute_knowledge_promotion_prerequisite_evaluation_id,
    knowledge_promotion_prerequisite_identity_input_from_record,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID = (
    "rcis-governed-knowledge-construction"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED = "constructed"
GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_REJECTED = "rejected"

GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY = (
    "unsupported_governed_knowledge_construction_policy"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE = (
    "unsupported_governed_knowledge_construction_scope"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EVALUATION_POLICY = (
    "unsupported_prerequisite_evaluation_policy"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_DECISION_POLICY = (
    "unsupported_promotion_decision_policy"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY = (
    "unsupported_promotion_execution_policy"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_NOT_SATISFIED = (
    "prerequisite_evaluation_not_satisfied_for_construction"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_NOT_AUTHORIZED = (
    "promotion_decision_not_authorized_for_construction"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_MISMATCH = (
    "governed_knowledge_candidate_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH = (
    "governed_knowledge_candidate_contract_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH = (
    "governed_knowledge_candidate_snapshot_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_MISMATCH = (
    "governed_knowledge_prerequisite_evaluation_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_MISMATCH = (
    "governed_knowledge_promotion_decision_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EXECUTION_MISMATCH = (
    "governed_knowledge_promotion_execution_mismatch"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_EXECUTION_REASON = (
    "missing_required_promotion_execution_completion_reason"
)
GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_CONSTRUCTION_REASON = (
    "missing_required_governed_knowledge_construction_reason"
)

GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS = (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EVALUATION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_DECISION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_NOT_SATISFIED,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_NOT_AUTHORIZED,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EXECUTION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_EXECUTION_REASON,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_CONSTRUCTION_REASON,
)


_PROMOTION_DECISION_POLICY_ID = "rcis-knowledge-promotion-decision"
_PROMOTION_DECISION_POLICY_VERSION = "1.0.0"
_PROMOTION_EXECUTION_POLICY_ID = "rcis-knowledge-promotion-execution"
_PROMOTION_EXECUTION_POLICY_VERSION = "1.0.0"
_DIAGNOSTIC_SOURCE = "governed_knowledge_constructor"
_REJECTION_MESSAGES = {
    reason: reason.replace("_", " ")
    for reason in GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS
}


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _require_unique_ordered_strings(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError(f"{field_name} must be a non-empty tuple")
    for item in value:
        _require_string(item, field_name)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if tuple(sorted(value)) != value:
        raise ValueError(f"{field_name} must be lexicographically ordered")
    return value  # type: ignore[return-value]


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _verify_upstream_identities(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    decision: KnowledgePromotionDecision,
    execution: KnowledgePromotionExecutionRecord,
) -> None:
    candidate.__post_init__()
    evaluation.__post_init__()
    decision.__post_init__()
    execution.__post_init__()
    candidate_identity = identity_input_from_knowledge_candidate(candidate)
    if candidate.knowledge_candidate_id != compute_knowledge_candidate_id(
        candidate_identity
    ):
        raise ValueError("knowledge_candidate_id does not match identity")
    evaluation_identity = (
        knowledge_promotion_prerequisite_identity_input_from_record(evaluation)
    )
    if (
        evaluation.knowledge_promotion_prerequisite_evaluation_id
        != compute_knowledge_promotion_prerequisite_evaluation_id(
            evaluation_identity
        )
    ):
        raise ValueError(
            "knowledge_promotion_prerequisite_evaluation_id does not match identity"
        )
    decision_identity = knowledge_promotion_decision_identity_input_from_record(
        decision
    )
    if (
        decision.knowledge_promotion_decision_id
        != compute_knowledge_promotion_decision_id(decision_identity)
    ):
        raise ValueError("knowledge_promotion_decision_id does not match identity")
    execution_identity = knowledge_promotion_execution_identity_input_from_record(
        execution
    )
    if (
        execution.knowledge_promotion_execution_id
        != compute_knowledge_promotion_execution_id(execution_identity)
    ):
        raise ValueError("knowledge_promotion_execution_id does not match identity")


@dataclass(frozen=True)
class GovernedKnowledgeConstructionRequest:
    knowledge_candidate: KnowledgeCandidate
    knowledge_promotion_prerequisite_evaluation: (
        KnowledgePromotionPrerequisiteEvaluation
    )
    knowledge_promotion_decision: KnowledgePromotionDecision
    knowledge_promotion_execution: KnowledgePromotionExecutionRecord
    construction_scope: str
    construction_reference: str
    reason_codes: tuple[str, ...]
    constructed_by: str
    constructed_at: datetime
    construction_policy_id: str
    construction_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        if (
            type(self.knowledge_promotion_prerequisite_evaluation)
            is not KnowledgePromotionPrerequisiteEvaluation
        ):
            raise ValueError(
                "knowledge_promotion_prerequisite_evaluation must be an exact "
                "KnowledgePromotionPrerequisiteEvaluation"
            )
        if type(self.knowledge_promotion_decision) is not KnowledgePromotionDecision:
            raise ValueError(
                "knowledge_promotion_decision must be an exact "
                "KnowledgePromotionDecision"
            )
        if (
            type(self.knowledge_promotion_execution)
            is not KnowledgePromotionExecutionRecord
        ):
            raise ValueError(
                "knowledge_promotion_execution must be an exact "
                "KnowledgePromotionExecutionRecord"
            )
        _verify_upstream_identities(
            self.knowledge_candidate,
            self.knowledge_promotion_prerequisite_evaluation,
            self.knowledge_promotion_decision,
            self.knowledge_promotion_execution,
        )
        for field_name in (
            "construction_scope",
            "construction_reference",
            "constructed_by",
            "construction_policy_id",
            "construction_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        _require_aware_datetime(self.constructed_at, "constructed_at")


@dataclass(frozen=True)
class GovernedKnowledgeConstructionResult:
    result_status: str
    governed_knowledge: GovernedKnowledge | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[GovernedKnowledgeDiagnostic, ...]

    def __post_init__(self) -> None:
        if self.result_status == GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED:
            if type(self.governed_knowledge) is not GovernedKnowledge:
                raise ValueError(
                    "constructed result requires an exact GovernedKnowledge"
                )
            if self.reason_codes != () or self.diagnostics != ():
                raise ValueError(
                    "constructed result requires empty reasons and diagnostics"
                )
            return
        if self.result_status == GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_REJECTED:
            if self.governed_knowledge is not None:
                raise ValueError("rejected result requires no governed_knowledge")
            if (
                type(self.reason_codes) is not tuple
                or len(self.reason_codes) != 1
                or self.reason_codes[0]
                not in GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS
            ):
                raise ValueError("rejected result requires one approved reason")
            if type(self.diagnostics) is not tuple or len(self.diagnostics) != 1:
                raise ValueError("rejected result requires one diagnostic")
            diagnostic = self.diagnostics[0]
            if type(diagnostic) is not GovernedKnowledgeDiagnostic:
                raise ValueError(
                    "rejected result diagnostic must be exact "
                    "GovernedKnowledgeDiagnostic"
                )
            if (
                diagnostic.code != self.reason_codes[0]
                or diagnostic.severity != "warning"
                or diagnostic.message != _REJECTION_MESSAGES[self.reason_codes[0]]
                or diagnostic.field != "request"
                or diagnostic.source != _DIAGNOSTIC_SOURCE
            ):
                raise ValueError("rejected result diagnostic does not match reason")
            return
        raise ValueError("unsupported result_status")


def _rejected(reason: str) -> GovernedKnowledgeConstructionResult:
    diagnostic = GovernedKnowledgeDiagnostic(
        code=reason,
        severity="warning",
        message=_REJECTION_MESSAGES[reason],
        field="request",
        source=_DIAGNOSTIC_SOURCE,
    )
    return GovernedKnowledgeConstructionResult(
        result_status=GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_REJECTED,
        governed_knowledge=None,
        reason_codes=(reason,),
        diagnostics=(diagnostic,),
    )


def construct_governed_knowledge(
    request: GovernedKnowledgeConstructionRequest,
) -> GovernedKnowledgeConstructionResult:
    if type(request) is not GovernedKnowledgeConstructionRequest:
        raise ValueError(
            "request must be an exact GovernedKnowledgeConstructionRequest"
        )
    request.__post_init__()
    candidate = request.knowledge_candidate
    evaluation = request.knowledge_promotion_prerequisite_evaluation
    decision = request.knowledge_promotion_decision
    execution = request.knowledge_promotion_execution

    if (
        request.construction_policy_id
        != GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID
        or request.construction_policy_version
        != GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY
        )
    if request.construction_scope != GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE:
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE
        )
    if (
        evaluation.evaluation_policy_id
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID
        or evaluation.evaluation_policy_version
        != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EVALUATION_POLICY
        )
    if (
        decision.decision_policy_id != _PROMOTION_DECISION_POLICY_ID
        or decision.decision_policy_version != _PROMOTION_DECISION_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_DECISION_POLICY
        )
    if (
        execution.execution_policy_id != _PROMOTION_EXECUTION_POLICY_ID
        or execution.execution_policy_version
        != _PROMOTION_EXECUTION_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY
        )
    if (
        evaluation.evaluation_outcome
        != PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_NOT_SATISFIED
        )
    if (
        decision.promotion_decision != PROMOTION_DECISION_OUTCOME_AUTHORIZED
        or decision.authorization_scope != PROMOTION_DECISION_AUTHORIZATION_SCOPE
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_NOT_AUTHORIZED
        )
    candidate_ids = (
        evaluation.knowledge_candidate_id,
        decision.knowledge_candidate_id,
        execution.knowledge_candidate_id,
    )
    if any(item != candidate.knowledge_candidate_id for item in candidate_ids):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_MISMATCH
        )
    candidate_contracts = (
        evaluation.knowledge_candidate_contract_version,
        decision.knowledge_candidate_contract_version,
        execution.knowledge_candidate_contract_version,
    )
    if any(item != candidate.contract_version for item in candidate_contracts):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH
        )
    candidate_snapshot_digest = (
        compute_knowledge_candidate_review_snapshot_digest(candidate)
    )
    candidate_snapshots = (
        evaluation.knowledge_candidate_snapshot_digest,
        decision.knowledge_candidate_snapshot_digest,
        execution.knowledge_candidate_snapshot_digest,
    )
    if any(item != candidate_snapshot_digest for item in candidate_snapshots):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH
        )
    if (
        decision.knowledge_promotion_prerequisite_evaluation_id
        != evaluation.knowledge_promotion_prerequisite_evaluation_id
        or decision.knowledge_promotion_prerequisite_evaluation_contract_version
        != evaluation.contract_version
        or decision.promotion_prerequisite_evaluation_outcome
        != evaluation.evaluation_outcome
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_MISMATCH
        )
    if (
        execution.knowledge_promotion_decision_id
        != decision.knowledge_promotion_decision_id
        or execution.knowledge_promotion_decision_contract_version
        != decision.contract_version
        or execution.promotion_decision_outcome != decision.promotion_decision
        or execution.authorization_scope != decision.authorization_scope
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_MISMATCH
        )
    if (
        execution.knowledge_promotion_prerequisite_evaluation_id
        != evaluation.knowledge_promotion_prerequisite_evaluation_id
        or execution.knowledge_promotion_prerequisite_evaluation_contract_version
        != evaluation.contract_version
        or execution.execution_scope != PROMOTION_EXECUTION_SCOPE_DECLARED
        or execution.execution_outcome != PROMOTION_EXECUTION_OUTCOME_COMPLETED
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EXECUTION_MISMATCH
        )
    if PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION not in execution.reason_codes:
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_EXECUTION_REASON
        )
    if (
        REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON
        not in request.reason_codes
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_CONSTRUCTION_REASON
        )

    identity_input = GovernedKnowledgeIdentityInput(
        contract_version=GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        statement_type=candidate.statement_type,
        statement=candidate.statement,
        support=candidate.support,
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
        knowledge_promotion_execution_id=(
            execution.knowledge_promotion_execution_id
        ),
        knowledge_promotion_execution_contract_version=execution.contract_version,
        promotion_execution_scope=execution.execution_scope,
        promotion_execution_outcome=execution.execution_outcome,
        construction_scope=request.construction_scope,
        construction_reference=request.construction_reference,
        reason_codes=request.reason_codes,
        constructed_by=request.constructed_by,
        constructed_at=request.constructed_at,
        construction_policy_id=request.construction_policy_id,
        construction_policy_version=request.construction_policy_version,
    )
    governed_knowledge = GovernedKnowledge(
        governed_knowledge_id=compute_governed_knowledge_id(identity_input),
        contract_version=identity_input.contract_version,
        knowledge_candidate_id=identity_input.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity_input.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity_input.knowledge_candidate_snapshot_digest
        ),
        statement_type=identity_input.statement_type,
        statement=identity_input.statement,
        support=identity_input.support,
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
        knowledge_promotion_execution_id=(
            identity_input.knowledge_promotion_execution_id
        ),
        knowledge_promotion_execution_contract_version=(
            identity_input.knowledge_promotion_execution_contract_version
        ),
        promotion_execution_scope=identity_input.promotion_execution_scope,
        promotion_execution_outcome=identity_input.promotion_execution_outcome,
        construction_scope=identity_input.construction_scope,
        construction_reference=identity_input.construction_reference,
        reason_codes=identity_input.reason_codes,
        constructed_by=identity_input.constructed_by,
        constructed_at=identity_input.constructed_at,
        construction_policy_id=identity_input.construction_policy_id,
        construction_policy_version=identity_input.construction_policy_version,
        diagnostics=(),
    )
    return GovernedKnowledgeConstructionResult(
        result_status=GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED,
        governed_knowledge=governed_knowledge,
        reason_codes=(),
        diagnostics=(),
    )
