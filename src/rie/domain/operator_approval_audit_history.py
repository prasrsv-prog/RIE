from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from rie.application.operator_approval_application_service import (
    ALLOWED_ASSESSMENT_OUTCOMES,
    ALLOWED_ASSESSMENT_REASON_CODES,
    OUTCOME_DENIED,
    OUTCOME_ELIGIBLE,
    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
    OperatorApprovalExecutionAssessment,
)
from rie.domain.operator_approval_decision import (
    ALLOWED_ACTIONS,
    ALLOWED_TARGET_TYPES,
    OperatorApprovalDecision,
)

APPEND_OUTCOME_APPENDED: Final = "APPENDED"
APPEND_OUTCOME_EXACT_DUPLICATE: Final = "EXACT_DUPLICATE"
APPEND_OUTCOME_CONFLICT: Final = "CONFLICT"

AuditAppendOutcome: TypeAlias = Literal[
    "APPENDED",
    "EXACT_DUPLICATE",
    "CONFLICT",
]

ALLOWED_AUDIT_APPEND_OUTCOMES: Final = frozenset(
    {
        APPEND_OUTCOME_APPENDED,
        APPEND_OUTCOME_EXACT_DUPLICATE,
        APPEND_OUTCOME_CONFLICT,
    }
)

_RECORD_REQUIRED_FIELDS: Final = (
    "audit_record_id",
    "decision_id",
    "operator_reference",
    "role_reference",
    "target_type",
    "target_reference",
    "action",
    "assessment_outcome",
    "assessment_reason_code",
    "reason_reference",
    "audit_context_reference",
)
_RECORD_OPTIONAL_REFERENCE_FIELDS: Final = (
    "permission_reference",
    "lifecycle_reason_reference",
    "provenance_reference",
    "rights_reference",
    "idempotency_reference",
    "conflict_reference",
)
_DECISION_AGREEMENT_FIELDS: Final = (
    "decision_id",
    "operator_reference",
    "role_reference",
    "target_type",
    "target_reference",
    "action",
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


def _validate_optional_ascii_reference(
    field_name: str,
    value: object,
) -> None:
    if value is not None:
        _validate_required_ascii_text(field_name, value)


def _validate_limit(limit: object) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be from 1 through 100")
    return limit


@dataclass(frozen=True)
class OperatorApprovalAuditRecord:
    """Immutable facts for one approval decision and one assessment."""

    audit_record_id: str
    decision_id: str
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
    lifecycle_reason_reference: str | None
    provenance_reference: str | None
    rights_reference: str | None
    idempotency_reference: str | None
    conflict_reference: str | None

    def __post_init__(self) -> None:
        for field_name in _RECORD_REQUIRED_FIELDS:
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )
        for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
            _validate_optional_ascii_reference(
                field_name,
                getattr(self, field_name),
            )
        if self.target_type not in ALLOWED_TARGET_TYPES:
            raise ValueError("target_type is not supported")
        if self.action not in ALLOWED_ACTIONS:
            raise ValueError("action is not supported")
        if self.assessment_outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
            raise ValueError("assessment_outcome must be ELIGIBLE or DENIED")
        if self.assessment_reason_code not in ALLOWED_ASSESSMENT_REASON_CODES:
            raise ValueError("assessment_reason_code is not supported")
        if self.assessment_outcome == OUTCOME_ELIGIBLE:
            if (
                self.assessment_reason_code
                != REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
            ):
                raise ValueError(
                    "ELIGIBLE requires the exact eligible reason code"
                )
            for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
                _validate_required_ascii_text(
                    field_name,
                    getattr(self, field_name),
                )
        elif (
            self.assessment_reason_code
            == REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ):
            raise ValueError("the eligible reason code requires ELIGIBLE")


@dataclass(frozen=True)
class OperatorApprovalAuditHistory:
    """Immutable append-ordered in-memory approval audit history."""

    records: tuple[OperatorApprovalAuditRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple")
        seen_audit_record_ids: set[str] = set()
        seen_decision_context_pairs: set[tuple[str, str]] = set()
        for record in self.records:
            if not isinstance(record, OperatorApprovalAuditRecord):
                raise TypeError(
                    "records must contain OperatorApprovalAuditRecord values"
                )
            _validate_audit_record(record)
            if record.audit_record_id in seen_audit_record_ids:
                raise ValueError("history contains duplicate audit_record_id")
            decision_context_pair = (
                record.decision_id,
                record.audit_context_reference,
            )
            if decision_context_pair in seen_decision_context_pairs:
                raise ValueError(
                    "history contains duplicate decision and audit context"
                )
            seen_audit_record_ids.add(record.audit_record_id)
            seen_decision_context_pairs.add(decision_context_pair)


@dataclass(frozen=True)
class OperatorApprovalAuditAppendResult:
    """Immutable result of one pure audit-history append assessment."""

    outcome: AuditAppendOutcome
    history: OperatorApprovalAuditHistory
    record: OperatorApprovalAuditRecord | None
    conflicting_audit_record_id: str | None

    def __post_init__(self) -> None:
        if self.outcome not in ALLOWED_AUDIT_APPEND_OUTCOMES:
            raise ValueError("outcome is not supported")
        _validate_audit_history(self.history)
        if self.record is not None:
            _validate_audit_record(self.record)
        _validate_optional_ascii_reference(
            "conflicting_audit_record_id",
            self.conflicting_audit_record_id,
        )
        if self.outcome == APPEND_OUTCOME_APPENDED:
            if self.record is None:
                raise ValueError("APPENDED requires record")
            if self.conflicting_audit_record_id is not None:
                raise ValueError(
                    "APPENDED requires absent conflicting_audit_record_id"
                )
            if not self.history.records or self.history.records[-1] != self.record:
                raise ValueError(
                    "APPENDED requires record at the end of history"
                )
        elif self.outcome == APPEND_OUTCOME_EXACT_DUPLICATE:
            if self.record is None:
                raise ValueError("EXACT_DUPLICATE requires record")
            if self.conflicting_audit_record_id is not None:
                raise ValueError(
                    "EXACT_DUPLICATE requires absent conflicting_audit_record_id"
                )
            if self.record not in self.history.records:
                raise ValueError(
                    "EXACT_DUPLICATE requires existing record in history"
                )
        else:
            if self.record is not None:
                raise ValueError("CONFLICT requires absent record")
            if self.conflicting_audit_record_id is None:
                raise ValueError(
                    "CONFLICT requires conflicting_audit_record_id"
                )
            if not any(
                record.audit_record_id == self.conflicting_audit_record_id
                for record in self.history.records
            ):
                raise ValueError(
                    "CONFLICT requires an existing conflicting audit record"
                )


def _validate_decision(decision: object) -> OperatorApprovalDecision:
    if not isinstance(decision, OperatorApprovalDecision):
        raise TypeError("decision must be OperatorApprovalDecision")
    for field_name in _DECISION_AGREEMENT_FIELDS:
        _validate_required_ascii_text(field_name, getattr(decision, field_name))
    if decision.target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError("decision target_type is not supported")
    if decision.action not in ALLOWED_ACTIONS:
        raise ValueError("decision action is not supported")
    return decision


def _validate_assessment(
    assessment: object,
) -> OperatorApprovalExecutionAssessment:
    if not isinstance(assessment, OperatorApprovalExecutionAssessment):
        raise TypeError(
            "assessment must be OperatorApprovalExecutionAssessment"
        )
    for field_name in _DECISION_AGREEMENT_FIELDS:
        _validate_required_ascii_text(
            field_name,
            getattr(assessment, field_name),
        )
    for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
        _validate_optional_ascii_reference(
            field_name,
            getattr(assessment, field_name),
        )
    if assessment.target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError("assessment target_type is not supported")
    if assessment.action not in ALLOWED_ACTIONS:
        raise ValueError("assessment action is not supported")
    if assessment.outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
        raise ValueError("assessment outcome must be ELIGIBLE or DENIED")
    if assessment.reason_code not in ALLOWED_ASSESSMENT_REASON_CODES:
        raise ValueError("assessment reason_code is not supported")
    if assessment.outcome == OUTCOME_ELIGIBLE:
        if (
            assessment.reason_code
            != REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ):
            raise ValueError(
                "ELIGIBLE assessment requires the exact eligible reason code"
            )
        for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
            _validate_required_ascii_text(
                field_name,
                getattr(assessment, field_name),
            )
    elif (
        assessment.reason_code
        == REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
    ):
        raise ValueError("the eligible reason code requires ELIGIBLE assessment")
    return assessment


def _validate_audit_record(
    record: object,
) -> OperatorApprovalAuditRecord:
    if not isinstance(record, OperatorApprovalAuditRecord):
        raise TypeError("record must be OperatorApprovalAuditRecord")
    for field_name in _RECORD_REQUIRED_FIELDS:
        _validate_required_ascii_text(field_name, getattr(record, field_name))
    for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
        _validate_optional_ascii_reference(
            field_name,
            getattr(record, field_name),
        )
    if record.target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError("record target_type is not supported")
    if record.action not in ALLOWED_ACTIONS:
        raise ValueError("record action is not supported")
    if record.assessment_outcome not in ALLOWED_ASSESSMENT_OUTCOMES:
        raise ValueError("record assessment_outcome must be ELIGIBLE or DENIED")
    if record.assessment_reason_code not in ALLOWED_ASSESSMENT_REASON_CODES:
        raise ValueError("record assessment_reason_code is not supported")
    if record.assessment_outcome == OUTCOME_ELIGIBLE:
        if (
            record.assessment_reason_code
            != REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ):
            raise ValueError(
                "ELIGIBLE record requires the exact eligible reason code"
            )
        for field_name in _RECORD_OPTIONAL_REFERENCE_FIELDS:
            _validate_required_ascii_text(
                field_name,
                getattr(record, field_name),
            )
    elif (
        record.assessment_reason_code
        == REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
    ):
        raise ValueError("the eligible reason code requires ELIGIBLE record")
    return record


def _validate_audit_history(
    history: object,
) -> OperatorApprovalAuditHistory:
    if not isinstance(history, OperatorApprovalAuditHistory):
        raise TypeError("history must be OperatorApprovalAuditHistory")
    if not isinstance(history.records, tuple):
        raise TypeError("history records must be a tuple")
    seen_audit_record_ids: set[str] = set()
    seen_decision_context_pairs: set[tuple[str, str]] = set()
    for record in history.records:
        _validate_audit_record(record)
        if record.audit_record_id in seen_audit_record_ids:
            raise ValueError("history contains duplicate audit_record_id")
        decision_context_pair = (
            record.decision_id,
            record.audit_context_reference,
        )
        if decision_context_pair in seen_decision_context_pairs:
            raise ValueError(
                "history contains duplicate decision and audit context"
            )
        seen_audit_record_ids.add(record.audit_record_id)
        seen_decision_context_pairs.add(decision_context_pair)
    return history


def create_operator_approval_audit_record(
    audit_record_id: str,
    decision: OperatorApprovalDecision,
    assessment: OperatorApprovalExecutionAssessment,
) -> OperatorApprovalAuditRecord:
    """Construct one immutable audit record after exact agreement validation."""

    _validate_required_ascii_text("audit_record_id", audit_record_id)
    valid_decision = _validate_decision(decision)
    valid_assessment = _validate_assessment(assessment)
    for field_name in _DECISION_AGREEMENT_FIELDS:
        if getattr(valid_decision, field_name) != getattr(
            valid_assessment,
            field_name,
        ):
            raise ValueError(f"{field_name} must match exactly")
    return OperatorApprovalAuditRecord(
        audit_record_id=audit_record_id,
        decision_id=valid_decision.decision_id,
        operator_reference=valid_decision.operator_reference,
        role_reference=valid_decision.role_reference,
        permission_reference=valid_assessment.permission_reference,
        target_type=valid_decision.target_type,
        target_reference=valid_decision.target_reference,
        action=valid_decision.action,
        assessment_outcome=valid_assessment.outcome,
        assessment_reason_code=valid_assessment.reason_code,
        reason_reference=valid_decision.reason_reference,
        audit_context_reference=valid_decision.audit_context_reference,
        lifecycle_reason_reference=(
            valid_assessment.lifecycle_reason_reference
        ),
        provenance_reference=valid_assessment.provenance_reference,
        rights_reference=valid_assessment.rights_reference,
        idempotency_reference=valid_assessment.idempotency_reference,
        conflict_reference=valid_assessment.conflict_reference,
    )


def append_operator_approval_audit_record(
    history: OperatorApprovalAuditHistory,
    record: OperatorApprovalAuditRecord,
) -> OperatorApprovalAuditAppendResult:
    """Purely assess append, exact duplicate, or conflict."""

    valid_history = _validate_audit_history(history)
    valid_record = _validate_audit_record(record)
    for existing in valid_history.records:
        if existing.audit_record_id == valid_record.audit_record_id:
            if existing == valid_record:
                return OperatorApprovalAuditAppendResult(
                    outcome=APPEND_OUTCOME_EXACT_DUPLICATE,
                    history=valid_history,
                    record=existing,
                    conflicting_audit_record_id=None,
                )
            return OperatorApprovalAuditAppendResult(
                outcome=APPEND_OUTCOME_CONFLICT,
                history=valid_history,
                record=None,
                conflicting_audit_record_id=existing.audit_record_id,
            )
    for existing in valid_history.records:
        if (
            existing.decision_id == valid_record.decision_id
            and existing.audit_context_reference
            == valid_record.audit_context_reference
        ):
            return OperatorApprovalAuditAppendResult(
                outcome=APPEND_OUTCOME_CONFLICT,
                history=valid_history,
                record=None,
                conflicting_audit_record_id=existing.audit_record_id,
            )
    new_history = OperatorApprovalAuditHistory(
        records=valid_history.records + (valid_record,)
    )
    return OperatorApprovalAuditAppendResult(
        outcome=APPEND_OUTCOME_APPENDED,
        history=new_history,
        record=valid_record,
        conflicting_audit_record_id=None,
    )


def find_operator_approval_audit_record(
    history: OperatorApprovalAuditHistory,
    audit_record_id: str,
) -> OperatorApprovalAuditRecord | None:
    """Find zero or one record by exact audit_record_id."""

    valid_history = _validate_audit_history(history)
    _validate_required_ascii_text("audit_record_id", audit_record_id)
    for record in valid_history.records:
        if record.audit_record_id == audit_record_id:
            return record
    return None


def _bounded_records(
    history: OperatorApprovalAuditHistory,
    *,
    limit: int,
    predicate: object,
) -> tuple[OperatorApprovalAuditRecord, ...]:
    valid_history = _validate_audit_history(history)
    valid_limit = _validate_limit(limit)
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    matches: list[OperatorApprovalAuditRecord] = []
    for record in valid_history.records:
        if predicate(record):
            matches.append(record)
            if len(matches) == valid_limit:
                break
    return tuple(matches)


def list_operator_approval_audit_records_by_decision_id(
    history: OperatorApprovalAuditHistory,
    decision_id: str,
    *,
    limit: int,
) -> tuple[OperatorApprovalAuditRecord, ...]:
    """List by exact decision_id in append order."""

    _validate_required_ascii_text("decision_id", decision_id)
    return _bounded_records(
        history,
        limit=limit,
        predicate=lambda record: record.decision_id == decision_id,
    )


def list_operator_approval_audit_records_by_operator_reference(
    history: OperatorApprovalAuditHistory,
    operator_reference: str,
    *,
    limit: int,
) -> tuple[OperatorApprovalAuditRecord, ...]:
    """List by exact operator_reference in append order."""

    _validate_required_ascii_text(
        "operator_reference",
        operator_reference,
    )
    return _bounded_records(
        history,
        limit=limit,
        predicate=(
            lambda record: record.operator_reference == operator_reference
        ),
    )


def list_operator_approval_audit_records_by_target(
    history: OperatorApprovalAuditHistory,
    target_type: str,
    target_reference: str,
    *,
    limit: int,
) -> tuple[OperatorApprovalAuditRecord, ...]:
    """List by exact target type and reference in append order."""

    _validate_required_ascii_text("target_type", target_type)
    _validate_required_ascii_text("target_reference", target_reference)
    if target_type not in ALLOWED_TARGET_TYPES:
        raise ValueError("target_type is not supported")
    return _bounded_records(
        history,
        limit=limit,
        predicate=(
            lambda record: (
                record.target_type == target_type
                and record.target_reference == target_reference
            )
        ),
    )


def list_operator_approval_audit_records_by_audit_context_reference(
    history: OperatorApprovalAuditHistory,
    audit_context_reference: str,
    *,
    limit: int,
) -> tuple[OperatorApprovalAuditRecord, ...]:
    """List by exact audit context in append order."""

    _validate_required_ascii_text(
        "audit_context_reference",
        audit_context_reference,
    )
    return _bounded_records(
        history,
        limit=limit,
        predicate=(
            lambda record: (
                record.audit_context_reference == audit_context_reference
            )
        ),
    )
