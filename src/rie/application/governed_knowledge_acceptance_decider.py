from dataclasses import dataclass
from datetime import datetime

from rie.domain.governed_knowledge import (
    GovernedKnowledge,
    compute_governed_knowledge_id,
    governed_knowledge_identity_input_from_record,
)
from rie.domain.governed_knowledge_acceptance_decision import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
    GovernedKnowledgeAcceptanceDecision,
    GovernedKnowledgeAcceptanceDecisionIdentityInput,
    GovernedKnowledgeAcceptanceDiagnostic,
    compute_governed_knowledge_acceptance_decision_id,
)


GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_ID = (
    "rcis-governed-knowledge-acceptance-decision"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_RECORDED = "recorded"
GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_REJECTED = "rejected"
GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY = (
    "unsupported_acceptance_policy"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE = (
    "unsupported_acceptance_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME = (
    "unsupported_acceptance_outcome"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON = (
    "missing_required_acceptance_reason"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_REASONS = (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON,
)


_OUTCOMES = frozenset(
    (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED,
    )
)
_REQUIRED_REASON_BY_OUTCOME = {
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE
    ),
}
_DIAGNOSTIC_SOURCE = "governed_knowledge_acceptance_decider"
_REJECTION_MESSAGES = {
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY: (
        "The governed-Knowledge acceptance policy is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE: (
        "The governed-Knowledge acceptance scope is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME: (
        "The governed-Knowledge acceptance outcome is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON: (
        "The request omits the required governed-Knowledge acceptance reason."
    ),
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


def _verify_governed_knowledge(value: object) -> GovernedKnowledge:
    if type(value) is not GovernedKnowledge:
        raise ValueError("governed_knowledge must be an exact GovernedKnowledge")
    value.__post_init__()
    identity_input = governed_knowledge_identity_input_from_record(value)
    if value.governed_knowledge_id != compute_governed_knowledge_id(identity_input):
        raise ValueError("governed_knowledge_id does not match identity")
    return value


@dataclass(frozen=True)
class GovernedKnowledgeAcceptanceDecisionRequest:
    governed_knowledge: GovernedKnowledge
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str

    def __post_init__(self) -> None:
        _verify_governed_knowledge(self.governed_knowledge)
        for field_name in (
            "acceptance_scope",
            "acceptance_scope_reference",
            "acceptance_outcome",
            "decided_by",
            "acceptance_policy_id",
            "acceptance_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        _require_aware_datetime(self.decided_at, "decided_at")


@dataclass(frozen=True)
class GovernedKnowledgeAcceptanceDecisionResult:
    result_status: str
    acceptance_decision: GovernedKnowledgeAcceptanceDecision | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[GovernedKnowledgeAcceptanceDiagnostic, ...]

    def __post_init__(self) -> None:
        if self.result_status == GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_RECORDED:
            if type(self.acceptance_decision) is not GovernedKnowledgeAcceptanceDecision:
                raise ValueError(
                    "recorded result requires an exact "
                    "GovernedKnowledgeAcceptanceDecision"
                )
            if self.reason_codes != () or self.diagnostics != ():
                raise ValueError(
                    "recorded result requires empty reasons and diagnostics"
                )
            if self.acceptance_decision.diagnostics != ():
                raise ValueError("recorded decision requires empty diagnostics")
            return
        if self.result_status == GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_REJECTED:
            if self.acceptance_decision is not None:
                raise ValueError("rejected result requires no acceptance_decision")
            if (
                type(self.reason_codes) is not tuple
                or len(self.reason_codes) != 1
                or self.reason_codes[0]
                not in GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_REASONS
            ):
                raise ValueError("rejected result requires one approved reason")
            if type(self.diagnostics) is not tuple or len(self.diagnostics) != 1:
                raise ValueError("rejected result requires one diagnostic")
            diagnostic = self.diagnostics[0]
            if type(diagnostic) is not GovernedKnowledgeAcceptanceDiagnostic:
                raise ValueError(
                    "rejected result diagnostic must be exact "
                    "GovernedKnowledgeAcceptanceDiagnostic"
                )
            reason = self.reason_codes[0]
            if (
                diagnostic.code != reason
                or diagnostic.severity != "warning"
                or diagnostic.message != _REJECTION_MESSAGES[reason]
                or diagnostic.field != "request"
                or diagnostic.source != _DIAGNOSTIC_SOURCE
            ):
                raise ValueError("rejected result diagnostic does not match reason")
            return
        raise ValueError("unsupported result_status")


def _rejected(reason: str) -> GovernedKnowledgeAcceptanceDecisionResult:
    diagnostic = GovernedKnowledgeAcceptanceDiagnostic(
        code=reason,
        severity="warning",
        message=_REJECTION_MESSAGES[reason],
        field="request",
        source=_DIAGNOSTIC_SOURCE,
    )
    return GovernedKnowledgeAcceptanceDecisionResult(
        result_status=GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_REJECTED,
        acceptance_decision=None,
        reason_codes=(reason,),
        diagnostics=(diagnostic,),
    )


def decide_governed_knowledge_acceptance(
    request: GovernedKnowledgeAcceptanceDecisionRequest,
) -> GovernedKnowledgeAcceptanceDecisionResult:
    if type(request) is not GovernedKnowledgeAcceptanceDecisionRequest:
        raise ValueError(
            "request must be an exact GovernedKnowledgeAcceptanceDecisionRequest"
        )
    request.__post_init__()
    if (
        request.acceptance_policy_id != GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_ID
        or request.acceptance_policy_version
        != GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY
        )
    if request.acceptance_scope != GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED:
        return _rejected(GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE)
    if request.acceptance_outcome not in _OUTCOMES:
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME
        )
    required_reason = _REQUIRED_REASON_BY_OUTCOME[request.acceptance_outcome]
    if required_reason not in request.reason_codes:
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON
        )
    identity_input = GovernedKnowledgeAcceptanceDecisionIdentityInput(
        contract_version=GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
        governed_knowledge_id=request.governed_knowledge.governed_knowledge_id,
        governed_knowledge_contract_version=request.governed_knowledge.contract_version,
        acceptance_scope=request.acceptance_scope,
        acceptance_scope_reference=request.acceptance_scope_reference,
        acceptance_outcome=request.acceptance_outcome,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        acceptance_policy_id=request.acceptance_policy_id,
        acceptance_policy_version=request.acceptance_policy_version,
    )
    decision = GovernedKnowledgeAcceptanceDecision(
        governed_knowledge_acceptance_decision_id=(
            compute_governed_knowledge_acceptance_decision_id(identity_input)
        ),
        contract_version=identity_input.contract_version,
        governed_knowledge_id=identity_input.governed_knowledge_id,
        governed_knowledge_contract_version=(
            identity_input.governed_knowledge_contract_version
        ),
        acceptance_scope=identity_input.acceptance_scope,
        acceptance_scope_reference=identity_input.acceptance_scope_reference,
        acceptance_outcome=identity_input.acceptance_outcome,
        reason_codes=identity_input.reason_codes,
        decided_by=identity_input.decided_by,
        decided_at=identity_input.decided_at,
        acceptance_policy_id=identity_input.acceptance_policy_id,
        acceptance_policy_version=identity_input.acceptance_policy_version,
        diagnostics=(),
    )
    return GovernedKnowledgeAcceptanceDecisionResult(
        result_status=GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_RECORDED,
        acceptance_decision=decision,
        reason_codes=(),
        diagnostics=(),
    )
