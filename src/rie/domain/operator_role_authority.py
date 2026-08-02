from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from rie.domain.operator_approval_decision import (
    ALLOWED_ACTIONS,
    ALLOWED_TARGET_TYPES,
    ApprovalAction,
    ApprovalTargetType,
    OperatorApprovalDecision,
)

OUTCOME_ALLOW: Final = "ALLOW"
OUTCOME_DENY: Final = "DENY"

REASON_AUTHORIZED_EXACT_MATCH: Final = "AUTHORIZED_EXACT_MATCH"
REASON_INVALID_INPUT: Final = "INVALID_INPUT"
REASON_UNSUPPORTED_ACTION: Final = "UNSUPPORTED_ACTION"
REASON_UNSUPPORTED_TARGET_TYPE: Final = "UNSUPPORTED_TARGET_TYPE"
REASON_OPERATOR_REFERENCE_MISMATCH: Final = "OPERATOR_REFERENCE_MISMATCH"
REASON_ROLE_REFERENCE_MISMATCH: Final = "ROLE_REFERENCE_MISMATCH"
REASON_NO_EXACT_OPERATOR_ROLE_BINDING: Final = (
    "NO_EXACT_OPERATOR_ROLE_BINDING"
)
REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION: Final = (
    "NO_EXACT_ROLE_ACTION_TARGET_PERMISSION"
)
REASON_AMBIGUOUS_AUTHORITY_EVIDENCE: Final = (
    "AMBIGUOUS_AUTHORITY_EVIDENCE"
)

AuthorizationOutcome: TypeAlias = Literal["ALLOW", "DENY"]
AuthorizationReasonCode: TypeAlias = Literal[
    "AUTHORIZED_EXACT_MATCH",
    "INVALID_INPUT",
    "UNSUPPORTED_ACTION",
    "UNSUPPORTED_TARGET_TYPE",
    "OPERATOR_REFERENCE_MISMATCH",
    "ROLE_REFERENCE_MISMATCH",
    "NO_EXACT_OPERATOR_ROLE_BINDING",
    "NO_EXACT_ROLE_ACTION_TARGET_PERMISSION",
    "AMBIGUOUS_AUTHORITY_EVIDENCE",
]

ALLOWED_OUTCOMES: Final = frozenset({OUTCOME_ALLOW, OUTCOME_DENY})
ALLOWED_REASON_CODES: Final = frozenset(
    {
        REASON_AUTHORIZED_EXACT_MATCH,
        REASON_INVALID_INPUT,
        REASON_UNSUPPORTED_ACTION,
        REASON_UNSUPPORTED_TARGET_TYPE,
        REASON_OPERATOR_REFERENCE_MISMATCH,
        REASON_ROLE_REFERENCE_MISMATCH,
        REASON_NO_EXACT_OPERATOR_ROLE_BINDING,
        REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION,
        REASON_AMBIGUOUS_AUTHORITY_EVIDENCE,
    }
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


@dataclass(frozen=True)
class OperatorRoleBinding:
    """Explicit immutable operator-to-role binding evidence."""

    operator_reference: str
    role_reference: str
    binding_reference: str
    reason_reference: str
    audit_context_reference: str

    def __post_init__(self) -> None:
        for field_name in (
            "operator_reference",
            "role_reference",
            "binding_reference",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )


@dataclass(frozen=True)
class RoleActionTargetPermission:
    """Exact immutable role-action-target permission evidence."""

    role_reference: str
    target_type: ApprovalTargetType
    action: ApprovalAction
    permission_reference: str
    reason_reference: str
    audit_context_reference: str

    def __post_init__(self) -> None:
        for field_name in (
            "role_reference",
            "target_type",
            "action",
            "permission_reference",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )

        if self.target_type not in ALLOWED_TARGET_TYPES:
            raise ValueError("target_type is not supported")
        if self.action not in ALLOWED_ACTIONS:
            raise ValueError("action is not supported")


@dataclass(frozen=True)
class OperatorRolePermissionEvaluation:
    """Immutable non-self-executing authorization evaluation result."""

    operator_reference: str
    role_reference: str
    target_type: str
    action: str
    outcome: AuthorizationOutcome
    reason_code: AuthorizationReasonCode
    reason_reference: str
    audit_context_reference: str

    def __post_init__(self) -> None:
        for field_name in (
            "operator_reference",
            "role_reference",
            "target_type",
            "action",
            "outcome",
            "reason_code",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )

        if self.outcome not in ALLOWED_OUTCOMES:
            raise ValueError("outcome must be ALLOW or DENY")
        if self.reason_code not in ALLOWED_REASON_CODES:
            raise ValueError("reason_code is not supported")
        if (
            self.reason_code == REASON_AUTHORIZED_EXACT_MATCH
            and self.outcome != OUTCOME_ALLOW
        ):
            raise ValueError(
                "AUTHORIZED_EXACT_MATCH requires an ALLOW outcome"
            )
        if (
            self.reason_code != REASON_AUTHORIZED_EXACT_MATCH
            and self.outcome != OUTCOME_DENY
        ):
            raise ValueError(
                "all non-authorized reason codes require a DENY outcome"
            )


def _evaluation(
    decision: OperatorApprovalDecision,
    *,
    outcome: AuthorizationOutcome,
    reason_code: AuthorizationReasonCode,
    reason_reference: str,
    audit_context_reference: str,
) -> OperatorRolePermissionEvaluation:
    return OperatorRolePermissionEvaluation(
        operator_reference=decision.operator_reference,
        role_reference=decision.role_reference,
        target_type=decision.target_type,
        action=decision.action,
        outcome=outcome,
        reason_code=reason_code,
        reason_reference=reason_reference,
        audit_context_reference=audit_context_reference,
    )


def evaluate_operator_role_permission(
    decision: OperatorApprovalDecision,
    operator_role_bindings: tuple[OperatorRoleBinding, ...],
    role_action_target_permissions: tuple[RoleActionTargetPermission, ...],
    *,
    reason_reference: str,
    audit_context_reference: str,
) -> OperatorRolePermissionEvaluation:
    """Evaluate one exact approval tuple without executing any mutation."""

    if not isinstance(decision, OperatorApprovalDecision):
        raise TypeError("decision must be an OperatorApprovalDecision")

    for field_name in (
        "operator_reference",
        "role_reference",
        "target_type",
        "action",
        "reason_reference",
        "audit_context_reference",
    ):
        _validate_required_ascii_text(
            f"decision.{field_name}",
            getattr(decision, field_name),
        )
    _validate_required_ascii_text("reason_reference", reason_reference)
    _validate_required_ascii_text(
        "audit_context_reference",
        audit_context_reference,
    )

    if decision.action not in ALLOWED_ACTIONS:
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_UNSUPPORTED_ACTION,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if decision.target_type not in ALLOWED_TARGET_TYPES:
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_UNSUPPORTED_TARGET_TYPE,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )

    if not isinstance(operator_role_bindings, tuple):
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_INVALID_INPUT,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if not isinstance(role_action_target_permissions, tuple):
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_INVALID_INPUT,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if any(
        not isinstance(binding, OperatorRoleBinding)
        for binding in operator_role_bindings
    ):
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_INVALID_INPUT,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if any(
        not isinstance(permission, RoleActionTargetPermission)
        for permission in role_action_target_permissions
    ):
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_INVALID_INPUT,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )

    exact_bindings = tuple(
        binding
        for binding in operator_role_bindings
        if (
            binding.operator_reference == decision.operator_reference
            and binding.role_reference == decision.role_reference
        )
    )
    if len(exact_bindings) > 1:
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_AMBIGUOUS_AUTHORITY_EVIDENCE,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if not exact_bindings:
        if any(
            binding.operator_reference == decision.operator_reference
            for binding in operator_role_bindings
        ):
            reason_code = REASON_ROLE_REFERENCE_MISMATCH
        elif any(
            binding.role_reference == decision.role_reference
            for binding in operator_role_bindings
        ):
            reason_code = REASON_OPERATOR_REFERENCE_MISMATCH
        else:
            reason_code = REASON_NO_EXACT_OPERATOR_ROLE_BINDING
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=reason_code,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )

    exact_permissions = tuple(
        permission
        for permission in role_action_target_permissions
        if (
            permission.role_reference == decision.role_reference
            and permission.target_type == decision.target_type
            and permission.action == decision.action
        )
    )
    if len(exact_permissions) > 1:
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_AMBIGUOUS_AUTHORITY_EVIDENCE,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )
    if not exact_permissions:
        return _evaluation(
            decision,
            outcome=OUTCOME_DENY,
            reason_code=REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION,
            reason_reference=reason_reference,
            audit_context_reference=audit_context_reference,
        )

    return _evaluation(
        decision,
        outcome=OUTCOME_ALLOW,
        reason_code=REASON_AUTHORIZED_EXACT_MATCH,
        reason_reference=reason_reference,
        audit_context_reference=audit_context_reference,
    )
