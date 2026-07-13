"""Side-effect-free Knowledge authority decision recording."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.application.knowledge_governor import (
    KNOWLEDGE_GOVERNANCE_POLICY_ID,
    KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
)
from rie.domain.knowledge_authority_decision import (
    AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    AUTHORITY_DECISION_OUTCOME_DEFERRED,
    AUTHORITY_DECISION_OUTCOME_DENIED,
    AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY,
    INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION,
    KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING,
    KnowledgeAuthorityDecision,
    KnowledgeAuthorityDiagnostic,
    KnowledgeAuthorityIdentityInput,
    compute_knowledge_authority_candidate_snapshot_digest,
    compute_knowledge_authority_decision_id,
    verify_knowledge_authority_candidate_identity,
    verify_knowledge_authority_governance_decision_identity,
)
from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_governance_decision import (
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KnowledgeGovernanceDecision,
)


KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID = "rcis-knowledge-authority-decision"
KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION = "1.0.0"

AUTHORITY_DECISION_RESULT_STATUS_RECORDED = "recorded"
AUTHORITY_DECISION_RESULT_STATUS_REJECTED = "rejected"

_SUPPORTED_INTENDED_AUTHORITY_VALUES = frozenset(
    {
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    }
)
_REQUIRED_OUTCOME_REASONS = {
    AUTHORITY_DECISION_OUTCOME_AUTHORIZED: (
        "intended_knowledge_authority_authorized"
    ),
    AUTHORITY_DECISION_OUTCOME_DENIED: "intended_knowledge_authority_denied",
    AUTHORITY_DECISION_OUTCOME_DEFERRED: (
        "intended_knowledge_authority_deferred"
    ),
}
_REJECTION_MESSAGES = {
    "unsupported_authority_policy": (
        "The authority decision application policy is unsupported."
    ),
    "unsupported_authority_value": (
        "The intended governed-Knowledge authority value is unsupported."
    ),
    "unsupported_authority_decision_outcome": (
        "The requested authority decision outcome is unsupported."
    ),
    "unsupported_governance_evidence_policy": (
        "At least one governance record uses an unsupported evidence policy."
    ),
    "governance_candidate_mismatch": (
        "At least one governance record references another candidate."
    ),
    "governance_candidate_contract_mismatch": (
        "At least one governance record references another candidate contract."
    ),
    "governance_candidate_snapshot_mismatch": (
        "At least one governance record references another candidate snapshot."
    ),
    "contradictory_governance_evidence": (
        "The complete governance evidence is contradictory."
    ),
    "ineligible_governance_evidence": (
        "The complete governance evidence is ineligible."
    ),
    "incomplete_governance_evidence": (
        "The complete governance evidence is incomplete."
    ),
    "missing_required_authority_reason": (
        "The required authority decision reason is missing."
    ),
}
_REJECTION_REASONS = frozenset(_REJECTION_MESSAGES)


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


def _require_governance_decisions(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("knowledge_governance_decisions must be a tuple")
    if not value:
        raise ValueError("knowledge_governance_decisions must not be empty")
    record_ids: list[str] = []
    for index, record in enumerate(value):
        if type(record) is not KnowledgeGovernanceDecision:
            raise ValueError(
                f"knowledge_governance_decisions[{index}] must be an exact "
                "KnowledgeGovernanceDecision"
            )
        record_ids.append(
            verify_knowledge_authority_governance_decision_identity(record)
        )
    if len(set(record_ids)) != len(record_ids):
        raise ValueError(
            "knowledge_governance_decisions must contain unique IDs"
        )
    if record_ids != sorted(record_ids):
        raise ValueError(
            "knowledge_governance_decisions must be ordered by governance ID"
        )


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgeAuthorityDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgeAuthorityDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgeAuthorityDecisionRequest:
    knowledge_candidate: KnowledgeCandidate
    knowledge_governance_decisions: tuple[KnowledgeGovernanceDecision, ...]
    intended_authority_value: str
    decision_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    authority_policy_id: str
    authority_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError(
                "knowledge_candidate must be an exact KnowledgeCandidate"
            )
        verify_knowledge_authority_candidate_identity(self.knowledge_candidate)
        _require_governance_decisions(self.knowledge_governance_decisions)
        for field_name in (
            "intended_authority_value",
            "decision_outcome",
            "decided_by",
            "authority_policy_id",
            "authority_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=False,
        )
        _require_aware_datetime(self.decided_at, "decided_at")


@dataclass(frozen=True)
class KnowledgeAuthorityDecisionResult:
    result_status: str
    authority_decision: KnowledgeAuthorityDecision | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgeAuthorityDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            AUTHORITY_DECISION_RESULT_STATUS_RECORDED,
            AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported authority decision result status")
        _require_reason_codes(
            self.reason_codes,
            "reason_codes",
            allow_empty=True,
        )
        _require_diagnostics(self.diagnostics)
        if self.result_status == AUTHORITY_DECISION_RESULT_STATUS_RECORDED:
            if type(self.authority_decision) is not KnowledgeAuthorityDecision:
                raise ValueError(
                    "recorded result requires an exact authority decision"
                )
            if self.reason_codes:
                raise ValueError("recorded result must not have reason codes")
        else:
            if self.authority_decision is not None:
                raise ValueError(
                    "rejected result must not have an authority decision"
                )
            if len(self.reason_codes) != 1:
                raise ValueError(
                    "rejected result requires exactly one reason code"
                )
            if len(self.diagnostics) != 1:
                raise ValueError(
                    "rejected result requires exactly one diagnostic"
                )
            reason_code = self.reason_codes[0]
            diagnostic = self.diagnostics[0]
            if reason_code not in _REJECTION_REASONS:
                raise ValueError("unsupported rejection reason")
            if (
                diagnostic.severity
                != KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING
            ):
                raise ValueError(
                    "rejected result diagnostic severity must be warning"
                )
            if diagnostic.code != reason_code:
                raise ValueError(
                    "rejected result diagnostic code must match reason code"
                )


def _rejected(reason_code: str) -> KnowledgeAuthorityDecisionResult:
    return KnowledgeAuthorityDecisionResult(
        result_status=AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
        authority_decision=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgeAuthorityDiagnostic(
                code=reason_code,
                severity=KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING,
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_authority_decider",
            ),
        ),
    )


def decide_knowledge_authority(
    request: KnowledgeAuthorityDecisionRequest,
) -> KnowledgeAuthorityDecisionResult:
    if type(request) is not KnowledgeAuthorityDecisionRequest:
        raise ValueError(
            "request must be an exact KnowledgeAuthorityDecisionRequest"
        )

    candidate = request.knowledge_candidate
    verify_knowledge_authority_candidate_identity(candidate)
    _require_governance_decisions(request.knowledge_governance_decisions)

    if (
        request.authority_policy_id != KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID
        or request.authority_policy_version
        != KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION
    ):
        return _rejected("unsupported_authority_policy")

    if request.intended_authority_value not in _SUPPORTED_INTENDED_AUTHORITY_VALUES:
        return _rejected("unsupported_authority_value")

    required_reason = _REQUIRED_OUTCOME_REASONS.get(request.decision_outcome)
    if required_reason is None:
        return _rejected("unsupported_authority_decision_outcome")

    if any(
        record.governance_policy_id != KNOWLEDGE_GOVERNANCE_POLICY_ID
        or record.governance_policy_version
        != KNOWLEDGE_GOVERNANCE_POLICY_VERSION
        for record in request.knowledge_governance_decisions
    ):
        return _rejected("unsupported_governance_evidence_policy")

    if any(
        record.knowledge_candidate_id != candidate.knowledge_candidate_id
        for record in request.knowledge_governance_decisions
    ):
        return _rejected("governance_candidate_mismatch")

    if any(
        record.knowledge_candidate_contract_version != candidate.contract_version
        for record in request.knowledge_governance_decisions
    ):
        return _rejected("governance_candidate_contract_mismatch")

    candidate_snapshot_digest = (
        compute_knowledge_authority_candidate_snapshot_digest(candidate)
    )
    if any(
        record.knowledge_candidate_snapshot_digest != candidate_snapshot_digest
        for record in request.knowledge_governance_decisions
    ):
        return _rejected("governance_candidate_snapshot_mismatch")

    governance_decisions = frozenset(
        record.governance_decision
        for record in request.knowledge_governance_decisions
    )
    if (
        GOVERNANCE_DECISION_AUTHORIZED in governance_decisions
        and GOVERNANCE_DECISION_DENIED in governance_decisions
    ):
        return _rejected("contradictory_governance_evidence")
    if governance_decisions == frozenset({GOVERNANCE_DECISION_DENIED}):
        return _rejected("ineligible_governance_evidence")
    if governance_decisions != frozenset({GOVERNANCE_DECISION_AUTHORIZED}):
        return _rejected("incomplete_governance_evidence")

    if required_reason not in request.reason_codes:
        return _rejected("missing_required_authority_reason")

    governance_ids = tuple(
        record.knowledge_governance_decision_id
        for record in request.knowledge_governance_decisions
    )
    identity_input = KnowledgeAuthorityIdentityInput(
        authority_decision_record_contract_version=(
            KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        knowledge_governance_decision_ids=governance_ids,
        authority_scope=(
            AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY
        ),
        intended_authority_value=request.intended_authority_value,
        decision_outcome=request.decision_outcome,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        authority_policy_id=request.authority_policy_id,
        authority_policy_version=request.authority_policy_version,
    )
    record = KnowledgeAuthorityDecision(
        knowledge_authority_decision_id=(
            compute_knowledge_authority_decision_id(identity_input)
        ),
        contract_version=KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot_digest,
        knowledge_governance_decision_ids=governance_ids,
        authority_scope=(
            AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY
        ),
        intended_authority_value=request.intended_authority_value,
        decision_outcome=request.decision_outcome,
        reason_codes=request.reason_codes,
        decided_by=request.decided_by,
        decided_at=request.decided_at,
        authority_policy_id=request.authority_policy_id,
        authority_policy_version=request.authority_policy_version,
        diagnostics=(),
    )
    return KnowledgeAuthorityDecisionResult(
        result_status=AUTHORITY_DECISION_RESULT_STATUS_RECORDED,
        authority_decision=record,
        reason_codes=(),
        diagnostics=(),
    )
