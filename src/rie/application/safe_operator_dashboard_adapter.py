from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Final, Literal, TypeAlias

from rie.application.operator_approval_application_service import (
    ALLOWED_ASSESSMENT_OUTCOMES,
    OUTCOME_DENIED,
    OUTCOME_ELIGIBLE,
    OperatorApprovalExecutionAssessment,
    TargetApprovalContext,
    assess_operator_approval_execution,
)
from rie.domain.operator_approval_audit_history import (
    OperatorApprovalAuditHistory,
    OperatorApprovalAuditRecord,
)
from rie.domain.operator_approval_decision import OperatorApprovalDecision
from rie.domain.operator_role_authority import (
    ALLOWED_OUTCOMES,
    OUTCOME_ALLOW,
    OUTCOME_DENY,
    REASON_AUTHORIZED_EXACT_MATCH,
    OperatorRoleBinding,
    OperatorRolePermissionEvaluation,
    RoleActionTargetPermission,
    evaluate_operator_role_permission,
)

STATUS_READY: Final = "READY"
STATUS_DENIED: Final = "DENIED"
STATUS_INVALID: Final = "INVALID"

ERROR_REQUEST_INVALID: Final = "REQUEST_INVALID"
ERROR_ROLE_AUTHORITY_DENIED: Final = "ROLE_AUTHORITY_DENIED"
ERROR_ROLE_AUTHORITY_RESULT_INVALID: Final = (
    "ROLE_AUTHORITY_RESULT_INVALID"
)
ERROR_APPROVAL_ASSESSMENT_DENIED: Final = "APPROVAL_ASSESSMENT_DENIED"
ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID: Final = (
    "APPROVAL_ASSESSMENT_RESULT_INVALID"
)
ERROR_AUDIT_HISTORY_INVALID: Final = "AUDIT_HISTORY_INVALID"
ERROR_DEPENDENCY_FAILURE: Final = "DEPENDENCY_FAILURE"
ERROR_INTERNAL_FAILURE: Final = "INTERNAL_FAILURE"

DashboardStatus: TypeAlias = Literal["READY", "DENIED", "INVALID"]
DashboardErrorCode: TypeAlias = Literal[
    "REQUEST_INVALID",
    "ROLE_AUTHORITY_DENIED",
    "ROLE_AUTHORITY_RESULT_INVALID",
    "APPROVAL_ASSESSMENT_DENIED",
    "APPROVAL_ASSESSMENT_RESULT_INVALID",
    "AUDIT_HISTORY_INVALID",
    "DEPENDENCY_FAILURE",
    "INTERNAL_FAILURE",
]

ALLOWED_DASHBOARD_STATUSES: Final = frozenset(
    {STATUS_READY, STATUS_DENIED, STATUS_INVALID}
)
ALLOWED_DASHBOARD_ERROR_CODES: Final = frozenset(
    {
        ERROR_REQUEST_INVALID,
        ERROR_ROLE_AUTHORITY_DENIED,
        ERROR_ROLE_AUTHORITY_RESULT_INVALID,
        ERROR_APPROVAL_ASSESSMENT_DENIED,
        ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID,
        ERROR_AUDIT_HISTORY_INVALID,
        ERROR_DEPENDENCY_FAILURE,
        ERROR_INTERNAL_FAILURE,
    }
)

RoleAuthorityEvaluator: TypeAlias = Callable[..., object]
ApprovalAssessmentAssessor: TypeAlias = Callable[..., object]


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


def _validate_optional_ascii_text(field_name: str, value: object) -> None:
    if value is not None:
        _validate_required_ascii_text(field_name, value)


def _validate_audit_limit(value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("audit_limit must be an integer")
    if value < 1 or value > 100:
        raise ValueError("audit_limit must be from 1 through 100")


@dataclass(frozen=True)
class SafeOperatorDashboardRequest:
    """Immutable caller-supplied dashboard projection request."""

    request_id: str
    operator_reference: str
    role_reference: str
    target_type: str
    target_reference: str
    action: str
    reason_reference: str
    audit_context_reference: str
    audit_limit: int

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )
        _validate_audit_limit(self.audit_limit)


@dataclass(frozen=True)
class SafeOperatorDashboardProjection:
    """Immutable read-only projection of accepted dependency results."""

    request_id: str
    operator_reference: str
    role_reference: str
    permission_reference: str | None
    target_type: str
    target_reference: str
    action: str
    assessment_outcome: str
    assessment_reason_code: str
    reason_reference: str
    audit_context_reference: str
    matching_audit_records: tuple[OperatorApprovalAuditRecord, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "assessment_outcome",
            "assessment_reason_code",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )
        _validate_optional_ascii_text(
            "permission_reference",
            self.permission_reference,
        )
        if self.assessment_outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
            raise ValueError("assessment_outcome is not supported")
        if not isinstance(self.matching_audit_records, tuple):
            raise TypeError("matching_audit_records must be a tuple")
        if any(
            not isinstance(record, OperatorApprovalAuditRecord)
            for record in self.matching_audit_records
        ):
            raise TypeError(
                "matching_audit_records must contain "
                "OperatorApprovalAuditRecord values"
            )


@dataclass(frozen=True)
class SafeOperatorDashboardResult:
    """Immutable deterministic result of one dashboard projection request."""

    status: DashboardStatus
    projection: SafeOperatorDashboardProjection | None
    error_code: DashboardErrorCode | None

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_DASHBOARD_STATUSES:
            raise ValueError("status is not supported")
        if self.projection is not None and not isinstance(
            self.projection,
            SafeOperatorDashboardProjection,
        ):
            raise TypeError(
                "projection must be a SafeOperatorDashboardProjection or None"
            )
        if (
            self.error_code is not None
            and self.error_code not in ALLOWED_DASHBOARD_ERROR_CODES
        ):
            raise ValueError("error_code is not supported")
        if self.status == STATUS_READY:
            if self.projection is None:
                raise ValueError("READY requires projection")
            if self.projection.assessment_outcome != OUTCOME_ELIGIBLE:
                raise ValueError("READY requires an ELIGIBLE projection")
            if self.error_code is not None:
                raise ValueError("READY requires absent error_code")
        elif self.status == STATUS_DENIED:
            if self.error_code not in {
                ERROR_ROLE_AUTHORITY_DENIED,
                ERROR_APPROVAL_ASSESSMENT_DENIED,
            }:
                raise ValueError("DENIED requires an exact denied error_code")
            if (
                self.projection is not None
                and self.projection.assessment_outcome != OUTCOME_DENIED
            ):
                raise ValueError(
                    "DENIED projection requires DENIED assessment_outcome"
                )
        else:
            if self.projection is not None:
                raise ValueError("INVALID requires absent projection")
            if self.error_code not in ALLOWED_DASHBOARD_ERROR_CODES:
                raise ValueError("INVALID requires error_code")
            if self.error_code in {
                ERROR_ROLE_AUTHORITY_DENIED,
                ERROR_APPROVAL_ASSESSMENT_DENIED,
            }:
                raise ValueError(
                    "INVALID cannot use an exact denied error_code"
                )


def _invalid(error_code: DashboardErrorCode) -> SafeOperatorDashboardResult:
    return SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=error_code,
    )


def _validate_request(request: object) -> bool:
    if not isinstance(request, SafeOperatorDashboardRequest):
        return False
    try:
        for field_name in (
            "request_id",
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "reason_reference",
            "audit_context_reference",
        ):
            _validate_required_ascii_text(
                field_name,
                getattr(request, field_name),
            )
        _validate_audit_limit(request.audit_limit)
    except (AttributeError, TypeError, ValueError):
        return False
    return True


def _decision_agrees_with_request(
    decision: object,
    request: SafeOperatorDashboardRequest,
) -> bool:
    if not isinstance(decision, OperatorApprovalDecision):
        return False
    return all(
        getattr(decision, field_name, None) == getattr(request, field_name)
        for field_name in (
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "reason_reference",
            "audit_context_reference",
        )
    )


def _role_evaluation_is_valid(
    evaluation: object,
    request: SafeOperatorDashboardRequest,
) -> bool:
    if not isinstance(evaluation, OperatorRolePermissionEvaluation):
        return False
    if evaluation.outcome not in ALLOWED_OUTCOMES:
        return False
    if any(
        getattr(evaluation, field_name, None)
        != getattr(request, field_name)
        for field_name in (
            "operator_reference",
            "role_reference",
            "target_type",
            "action",
            "reason_reference",
            "audit_context_reference",
        )
    ):
        return False
    if evaluation.outcome == OUTCOME_ALLOW:
        return (
            evaluation.reason_code == REASON_AUTHORIZED_EXACT_MATCH
            and isinstance(evaluation.permission_reference, str)
            and bool(evaluation.permission_reference)
        )
    return (
        evaluation.outcome == OUTCOME_DENY
        and evaluation.reason_code != REASON_AUTHORIZED_EXACT_MATCH
        and evaluation.permission_reference is None
    )


def _assessment_is_valid(
    assessment: object,
    decision: OperatorApprovalDecision,
    evaluation: OperatorRolePermissionEvaluation,
    request: SafeOperatorDashboardRequest,
) -> bool:
    if not isinstance(assessment, OperatorApprovalExecutionAssessment):
        return False
    if assessment.outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
        return False
    if assessment.decision_id != decision.decision_id:
        return False
    if any(
        getattr(assessment, field_name, None)
        != getattr(request, field_name)
        for field_name in (
            "operator_reference",
            "role_reference",
            "target_type",
            "target_reference",
            "action",
            "reason_reference",
            "audit_context_reference",
        )
    ):
        return False
    if assessment.outcome == OUTCOME_ELIGIBLE:
        return (
            evaluation.outcome == OUTCOME_ALLOW
            and assessment.permission_reference
            == evaluation.permission_reference
        )
    if assessment.outcome == OUTCOME_DENIED:
        return (
            assessment.permission_reference is None
            or assessment.permission_reference
            == evaluation.permission_reference
        )
    return False


def _matching_audit_records(
    history: object,
    request: SafeOperatorDashboardRequest,
) -> tuple[OperatorApprovalAuditRecord, ...] | None:
    if not isinstance(history, OperatorApprovalAuditHistory):
        return None
    if not isinstance(history.records, tuple):
        return None
    if any(
        not isinstance(record, OperatorApprovalAuditRecord)
        for record in history.records
    ):
        return None
    matches = tuple(
        record
        for record in history.records
        if (
            record.operator_reference == request.operator_reference
            and record.role_reference == request.role_reference
            and record.target_type == request.target_type
            and record.target_reference == request.target_reference
            and record.action == request.action
        )
    )
    return matches[-request.audit_limit :]


def _projection(
    request: SafeOperatorDashboardRequest,
    assessment: OperatorApprovalExecutionAssessment,
    matching_audit_records: tuple[OperatorApprovalAuditRecord, ...],
) -> SafeOperatorDashboardProjection:
    return SafeOperatorDashboardProjection(
        request_id=request.request_id,
        operator_reference=assessment.operator_reference,
        role_reference=assessment.role_reference,
        permission_reference=assessment.permission_reference,
        target_type=assessment.target_type,
        target_reference=assessment.target_reference,
        action=assessment.action,
        assessment_outcome=assessment.outcome,
        assessment_reason_code=assessment.reason_code,
        reason_reference=assessment.reason_reference,
        audit_context_reference=assessment.audit_context_reference,
        matching_audit_records=matching_audit_records,
    )


def _build_safe_operator_dashboard(
    request: SafeOperatorDashboardRequest,
    decision: OperatorApprovalDecision,
    operator_role_bindings: tuple[OperatorRoleBinding, ...],
    role_action_target_permissions: tuple[RoleActionTargetPermission, ...],
    target_approval_context: TargetApprovalContext,
    audit_history: OperatorApprovalAuditHistory,
    *,
    role_authority_evaluator: RoleAuthorityEvaluator,
    approval_assessor: ApprovalAssessmentAssessor,
) -> SafeOperatorDashboardResult:
    if not _decision_agrees_with_request(decision, request):
        return _invalid(ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID)

    matching_records = _matching_audit_records(audit_history, request)
    if matching_records is None:
        return _invalid(ERROR_AUDIT_HISTORY_INVALID)

    if not callable(role_authority_evaluator) or not callable(
        approval_assessor
    ):
        return _invalid(ERROR_DEPENDENCY_FAILURE)

    try:
        evaluation = role_authority_evaluator(
            decision,
            operator_role_bindings,
            role_action_target_permissions,
            reason_reference=request.reason_reference,
            audit_context_reference=request.audit_context_reference,
        )
    except Exception:
        return _invalid(ERROR_DEPENDENCY_FAILURE)

    if not _role_evaluation_is_valid(evaluation, request):
        return _invalid(ERROR_ROLE_AUTHORITY_RESULT_INVALID)

    if evaluation.outcome == OUTCOME_DENY:
        return SafeOperatorDashboardResult(
            status=STATUS_DENIED,
            projection=None,
            error_code=ERROR_ROLE_AUTHORITY_DENIED,
        )

    try:
        assessment = approval_assessor(
            decision,
            evaluation,
            target_approval_context,
        )
    except Exception:
        return _invalid(ERROR_DEPENDENCY_FAILURE)

    if not _assessment_is_valid(
        assessment,
        decision,
        evaluation,
        request,
    ):
        return _invalid(ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID)

    projection = _projection(request, assessment, matching_records)
    if assessment.outcome == OUTCOME_DENIED:
        return SafeOperatorDashboardResult(
            status=STATUS_DENIED,
            projection=projection,
            error_code=ERROR_APPROVAL_ASSESSMENT_DENIED,
        )
    return SafeOperatorDashboardResult(
        status=STATUS_READY,
        projection=projection,
        error_code=None,
    )


def build_safe_operator_dashboard(
    request: object,
    decision: object,
    operator_role_bindings: object,
    role_action_target_permissions: object,
    target_approval_context: object,
    audit_history: object,
    *,
    role_authority_evaluator: object = evaluate_operator_role_permission,
    approval_assessor: object = assess_operator_approval_execution,
) -> SafeOperatorDashboardResult:
    """Build one pure read-only projection from explicit supplied values."""

    if not _validate_request(request):
        return _invalid(ERROR_REQUEST_INVALID)
    try:
        return _build_safe_operator_dashboard(
            request,
            decision,
            operator_role_bindings,
            role_action_target_permissions,
            target_approval_context,
            audit_history,
            role_authority_evaluator=role_authority_evaluator,
            approval_assessor=approval_assessor,
        )
    except Exception:
        return _invalid(ERROR_INTERNAL_FAILURE)
