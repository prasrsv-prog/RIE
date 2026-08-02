from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from rie.domain.operator_approval_decision import (
    ALLOWED_ACTIONS,
    ALLOWED_TARGET_TYPES,
    OperatorApprovalDecision,
)
from rie.domain.operator_role_authority import (
    OUTCOME_ALLOW,
    OperatorRolePermissionEvaluation,
)

OUTCOME_ELIGIBLE: Final = "ELIGIBLE"
OUTCOME_DENIED: Final = "DENIED"

REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION: Final = (
    "ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION"
)
REASON_INVALID_DECISION: Final = "INVALID_DECISION"
REASON_INVALID_ROLE_AUTHORITY_EVALUATION: Final = (
    "INVALID_ROLE_AUTHORITY_EVALUATION"
)
REASON_INVALID_TARGET_APPROVAL_CONTEXT: Final = (
    "INVALID_TARGET_APPROVAL_CONTEXT"
)
REASON_OPERATOR_REFERENCE_MISMATCH: Final = "OPERATOR_REFERENCE_MISMATCH"
REASON_ROLE_REFERENCE_MISMATCH: Final = "ROLE_REFERENCE_MISMATCH"
REASON_TARGET_TYPE_MISMATCH: Final = "TARGET_TYPE_MISMATCH"
REASON_TARGET_REFERENCE_MISMATCH: Final = "TARGET_REFERENCE_MISMATCH"
REASON_ACTION_MISMATCH: Final = "ACTION_MISMATCH"
REASON_REASON_REFERENCE_MISMATCH: Final = "REASON_REFERENCE_MISMATCH"
REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH: Final = (
    "AUDIT_CONTEXT_REFERENCE_MISMATCH"
)
REASON_ROLE_AUTHORITY_NOT_ALLOWED: Final = "ROLE_AUTHORITY_NOT_ALLOWED"
REASON_TARGET_LIFECYCLE_NOT_ELIGIBLE: Final = (
    "TARGET_LIFECYCLE_NOT_ELIGIBLE"
)
REASON_PROVENANCE_NOT_VERIFIED: Final = "PROVENANCE_NOT_VERIFIED"
REASON_RIGHTS_NOT_CLEARED: Final = "RIGHTS_NOT_CLEARED"
REASON_IDEMPOTENCY_NOT_NEW: Final = "IDEMPOTENCY_NOT_NEW"
REASON_BLOCKING_CONFLICT_PRESENT: Final = "BLOCKING_CONFLICT_PRESENT"

LIFECYCLE_ELIGIBLE: Final = "ELIGIBLE"
PROVENANCE_VERIFIED: Final = "VERIFIED"
RIGHTS_CLEARED: Final = "CLEARED"
IDEMPOTENCY_NEW: Final = "NEW"
CONFLICT_CLEAR: Final = "CLEAR"

ApprovalExecutionOutcome: TypeAlias = Literal["ELIGIBLE", "DENIED"]
ApprovalExecutionReasonCode: TypeAlias = Literal[
    "ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION",
    "INVALID_DECISION",
    "INVALID_ROLE_AUTHORITY_EVALUATION",
    "INVALID_TARGET_APPROVAL_CONTEXT",
    "OPERATOR_REFERENCE_MISMATCH",
    "ROLE_REFERENCE_MISMATCH",
    "TARGET_TYPE_MISMATCH",
    "TARGET_REFERENCE_MISMATCH",
    "ACTION_MISMATCH",
    "REASON_REFERENCE_MISMATCH",
    "AUDIT_CONTEXT_REFERENCE_MISMATCH",
    "ROLE_AUTHORITY_NOT_ALLOWED",
    "TARGET_LIFECYCLE_NOT_ELIGIBLE",
    "PROVENANCE_NOT_VERIFIED",
    "RIGHTS_NOT_CLEARED",
    "IDEMPOTENCY_NOT_NEW",
    "BLOCKING_CONFLICT_PRESENT",
]

ALLOWED_ASSESSMENT_OUTCOMES: Final = frozenset(
    {OUTCOME_ELIGIBLE, OUTCOME_DENIED}
)
ALLOWED_ASSESSMENT_REASON_CODES: Final = frozenset(
    {
        REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
        REASON_INVALID_DECISION,
        REASON_INVALID_ROLE_AUTHORITY_EVALUATION,
        REASON_INVALID_TARGET_APPROVAL_CONTEXT,
        REASON_OPERATOR_REFERENCE_MISMATCH,
        REASON_ROLE_REFERENCE_MISMATCH,
        REASON_TARGET_TYPE_MISMATCH,
        REASON_TARGET_REFERENCE_MISMATCH,
        REASON_ACTION_MISMATCH,
        REASON_REASON_REFERENCE_MISMATCH,
        REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH,
        REASON_ROLE_AUTHORITY_NOT_ALLOWED,
        REASON_TARGET_LIFECYCLE_NOT_ELIGIBLE,
        REASON_PROVENANCE_NOT_VERIFIED,
        REASON_RIGHTS_NOT_CLEARED,
        REASON_IDEMPOTENCY_NOT_NEW,
        REASON_BLOCKING_CONFLICT_PRESENT,
    }
)

_TARGET_CONTEXT_FIELDS: Final = (
    "target_type",
    "target_reference",
    "lifecycle_state",
    "lifecycle_eligibility",
    "lifecycle_reason_reference",
    "provenance_status",
    "provenance_reference",
    "rights_status",
    "rights_reference",
    "idempotency_status",
    "idempotency_reference",
    "conflict_status",
    "conflict_reference",
    "reason_reference",
    "audit_context_reference",
)
_DECISION_FIELDS: Final = (
    "decision_id",
    "operator_reference",
    "role_reference",
    "target_type",
    "target_reference",
    "action",
    "reason_reference",
    "audit_context_reference",
)
_ROLE_EVALUATION_FIELDS: Final = (
    "operator_reference",
    "role_reference",
    "target_type",
    "action",
    "outcome",
    "reason_code",
    "reason_reference",
    "audit_context_reference",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")
    if value != value.strip():
        raise ValueError(
            f"{field_name} must not contain leading or trailing whitespace"
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{field_name} must not contain control characters")


def _has_valid_required_text_fields(value: object, fields: tuple[str, ...]) -> bool:
    try:
        for field_name in fields:
            _validate_required_ascii_text(
                field_name,
                getattr(value, field_name),
            )
    except (AttributeError, TypeError, ValueError):
        return False
    return True


@dataclass(frozen=True)
class TargetApprovalContext:
    """Immutable caller-supplied target eligibility evidence."""

    target_type: str
    target_reference: str
    lifecycle_state: str
    lifecycle_eligibility: str
    lifecycle_reason_reference: str
    provenance_status: str
    provenance_reference: str
    rights_status: str
    rights_reference: str
    idempotency_status: str
    idempotency_reference: str
    conflict_status: str
    conflict_reference: str
    reason_reference: str
    audit_context_reference: str

    def __post_init__(self) -> None:
        for field_name in _TARGET_CONTEXT_FIELDS:
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )


@dataclass(frozen=True)
class OperatorApprovalExecutionAssessment:
    """Immutable, non-persistent approval execution eligibility result."""

    decision_id: str
    operator_reference: str
    role_reference: str
    target_type: str
    target_reference: str
    action: str
    outcome: ApprovalExecutionOutcome
    reason_code: ApprovalExecutionReasonCode
    reason_reference: str
    audit_context_reference: str
    permission_reference: str | None
    lifecycle_reason_reference: str | None
    provenance_reference: str | None
    rights_reference: str | None
    idempotency_reference: str | None
    conflict_reference: str | None

    def __post_init__(self) -> None:
        for field_name in (
            "decision_id",
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "reason_reference",
            "audit_context_reference",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise TypeError(f"{field_name} must be text")
        for field_name in (
            "permission_reference",
            "lifecycle_reason_reference",
            "provenance_reference",
            "rights_reference",
            "idempotency_reference",
            "conflict_reference",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _validate_required_ascii_text(field_name, value)
        if self.outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
            raise ValueError("outcome must be ELIGIBLE or DENIED")
        if self.reason_code not in ALLOWED_ASSESSMENT_REASON_CODES:
            raise ValueError("reason_code is not supported")
        if self.outcome == OUTCOME_ELIGIBLE:
            if (
                self.reason_code
                != REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
            ):
                raise ValueError(
                    "ELIGIBLE requires the exact eligible reason code"
                )
            for field_name in (
                "decision_id",
                "operator_reference",
                "role_reference",
                "target_type",
                "target_reference",
                "action",
                "reason_reference",
                "audit_context_reference",
                "permission_reference",
                "lifecycle_reason_reference",
                "provenance_reference",
                "rights_reference",
                "idempotency_reference",
                "conflict_reference",
            ):
                _validate_required_ascii_text(
                    field_name,
                    getattr(self, field_name),
                )
        elif (
            self.reason_code
            == REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ):
            raise ValueError("the eligible reason code requires ELIGIBLE")


def _text_or_empty(value: object, field_name: str) -> str:
    try:
        candidate = getattr(value, field_name)
    except AttributeError:
        return ""
    return candidate if isinstance(candidate, str) else ""


def _optional_reference(value: object, field_name: str) -> str | None:
    try:
        candidate = getattr(value, field_name)
        _validate_required_ascii_text(field_name, candidate)
    except (AttributeError, TypeError, ValueError):
        return None
    return candidate


def _assessment(
    decision: object,
    role_evaluation: object,
    target_context: object,
    *,
    outcome: ApprovalExecutionOutcome,
    reason_code: ApprovalExecutionReasonCode,
) -> OperatorApprovalExecutionAssessment:
    return OperatorApprovalExecutionAssessment(
        decision_id=_text_or_empty(decision, "decision_id"),
        operator_reference=_text_or_empty(decision, "operator_reference"),
        role_reference=_text_or_empty(decision, "role_reference"),
        target_type=_text_or_empty(decision, "target_type"),
        target_reference=_text_or_empty(decision, "target_reference"),
        action=_text_or_empty(decision, "action"),
        outcome=outcome,
        reason_code=reason_code,
        reason_reference=_text_or_empty(decision, "reason_reference"),
        audit_context_reference=_text_or_empty(
            decision,
            "audit_context_reference",
        ),
        permission_reference=_optional_reference(
            role_evaluation,
            "permission_reference",
        ),
        lifecycle_reason_reference=_optional_reference(
            target_context,
            "lifecycle_reason_reference",
        ),
        provenance_reference=_optional_reference(
            target_context,
            "provenance_reference",
        ),
        rights_reference=_optional_reference(
            target_context,
            "rights_reference",
        ),
        idempotency_reference=_optional_reference(
            target_context,
            "idempotency_reference",
        ),
        conflict_reference=_optional_reference(
            target_context,
            "conflict_reference",
        ),
    )


def assess_operator_approval_execution(
    decision: object,
    role_authority_evaluation: object,
    target_approval_context: object,
) -> OperatorApprovalExecutionAssessment:
    """Assess supplied approval evidence without mutation, persistence, or I/O."""

    if (
        not isinstance(decision, OperatorApprovalDecision)
        or not _has_valid_required_text_fields(decision, _DECISION_FIELDS)
        or decision.action not in ALLOWED_ACTIONS
        or decision.target_type not in ALLOWED_TARGET_TYPES
    ):
        return _assessment(
            decision,
            role_authority_evaluation,
            target_approval_context,
            outcome=OUTCOME_DENIED,
            reason_code=REASON_INVALID_DECISION,
        )

    if (
        not isinstance(
            role_authority_evaluation,
            OperatorRolePermissionEvaluation,
        )
        or not _has_valid_required_text_fields(
            role_authority_evaluation,
            _ROLE_EVALUATION_FIELDS,
        )
        or (
            role_authority_evaluation.permission_reference is not None
            and not _has_valid_required_text_fields(
                role_authority_evaluation,
                ("permission_reference",),
            )
        )
    ):
        return _assessment(
            decision,
            role_authority_evaluation,
            target_approval_context,
            outcome=OUTCOME_DENIED,
            reason_code=REASON_INVALID_ROLE_AUTHORITY_EVALUATION,
        )

    if (
        not isinstance(target_approval_context, TargetApprovalContext)
        or not _has_valid_required_text_fields(
            target_approval_context,
            _TARGET_CONTEXT_FIELDS,
        )
    ):
        return _assessment(
            decision,
            role_authority_evaluation,
            target_approval_context,
            outcome=OUTCOME_DENIED,
            reason_code=REASON_INVALID_TARGET_APPROVAL_CONTEXT,
        )

    if (
        decision.operator_reference
        != role_authority_evaluation.operator_reference
    ):
        reason_code = REASON_OPERATOR_REFERENCE_MISMATCH
    elif decision.role_reference != role_authority_evaluation.role_reference:
        reason_code = REASON_ROLE_REFERENCE_MISMATCH
    elif decision.action != role_authority_evaluation.action:
        reason_code = REASON_ACTION_MISMATCH
    elif decision.target_type != role_authority_evaluation.target_type:
        reason_code = REASON_TARGET_TYPE_MISMATCH
    elif decision.reason_reference != role_authority_evaluation.reason_reference:
        reason_code = REASON_REASON_REFERENCE_MISMATCH
    elif (
        decision.audit_context_reference
        != role_authority_evaluation.audit_context_reference
    ):
        reason_code = REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH
    elif (
        role_authority_evaluation.outcome != OUTCOME_ALLOW
        or role_authority_evaluation.permission_reference is None
    ):
        reason_code = REASON_ROLE_AUTHORITY_NOT_ALLOWED
    elif decision.target_type != target_approval_context.target_type:
        reason_code = REASON_TARGET_TYPE_MISMATCH
    elif decision.target_reference != target_approval_context.target_reference:
        reason_code = REASON_TARGET_REFERENCE_MISMATCH
    elif decision.reason_reference != target_approval_context.reason_reference:
        reason_code = REASON_REASON_REFERENCE_MISMATCH
    elif (
        decision.audit_context_reference
        != target_approval_context.audit_context_reference
    ):
        reason_code = REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH
    elif (
        target_approval_context.lifecycle_eligibility
        != LIFECYCLE_ELIGIBLE
    ):
        reason_code = REASON_TARGET_LIFECYCLE_NOT_ELIGIBLE
    elif target_approval_context.provenance_status != PROVENANCE_VERIFIED:
        reason_code = REASON_PROVENANCE_NOT_VERIFIED
    elif target_approval_context.rights_status != RIGHTS_CLEARED:
        reason_code = REASON_RIGHTS_NOT_CLEARED
    elif target_approval_context.idempotency_status != IDEMPOTENCY_NEW:
        reason_code = REASON_IDEMPOTENCY_NOT_NEW
    elif target_approval_context.conflict_status != CONFLICT_CLEAR:
        reason_code = REASON_BLOCKING_CONFLICT_PRESENT
    else:
        return _assessment(
            decision,
            role_authority_evaluation,
            target_approval_context,
            outcome=OUTCOME_ELIGIBLE,
            reason_code=REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
        )

    return _assessment(
        decision,
        role_authority_evaluation,
        target_approval_context,
        outcome=OUTCOME_DENIED,
        reason_code=reason_code,
    )
