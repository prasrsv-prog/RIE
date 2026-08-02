from dataclasses import FrozenInstanceError, MISSING, asdict, fields

import pytest

from rie.application.operator_approval_application_service import (
    OUTCOME_DENIED,
    OUTCOME_ELIGIBLE,
    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
    REASON_INVALID_DECISION,
    OperatorApprovalExecutionAssessment,
)
from rie.domain.operator_approval_audit_history import (
    ALLOWED_AUDIT_APPEND_OUTCOMES,
    APPEND_OUTCOME_APPENDED,
    APPEND_OUTCOME_CONFLICT,
    APPEND_OUTCOME_EXACT_DUPLICATE,
    OperatorApprovalAuditAppendResult,
    OperatorApprovalAuditHistory,
    OperatorApprovalAuditRecord,
    append_operator_approval_audit_record,
    create_operator_approval_audit_record,
    find_operator_approval_audit_record,
    list_operator_approval_audit_records_by_audit_context_reference,
    list_operator_approval_audit_records_by_decision_id,
    list_operator_approval_audit_records_by_operator_reference,
    list_operator_approval_audit_records_by_target,
)
from rie.domain.operator_approval_decision import (
    ACTION_APPROVE,
    TARGET_TYPE_EVIDENCE,
    OperatorApprovalDecision,
)


def make_decision(**overrides: object) -> OperatorApprovalDecision:
    values: dict[str, object] = {
        "decision_id": "decision-001",
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "action": ACTION_APPROVE,
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return OperatorApprovalDecision(**values)  # type: ignore[arg-type]


def make_assessment(
    **overrides: object,
) -> OperatorApprovalExecutionAssessment:
    values: dict[str, object] = {
        "decision_id": "decision-001",
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "action": ACTION_APPROVE,
        "outcome": OUTCOME_ELIGIBLE,
        "reason_code": REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
        "permission_reference": "permission-001",
        "lifecycle_reason_reference": "lifecycle-reason-001",
        "provenance_reference": "provenance-001",
        "rights_reference": "rights-001",
        "idempotency_reference": "idempotency-001",
        "conflict_reference": "conflict-001",
    }
    values.update(overrides)
    return OperatorApprovalExecutionAssessment(**values)  # type: ignore[arg-type]


def make_denied_assessment(
    **overrides: object,
) -> OperatorApprovalExecutionAssessment:
    values: dict[str, object] = {
        "outcome": OUTCOME_DENIED,
        "reason_code": REASON_INVALID_DECISION,
        "permission_reference": None,
        "lifecycle_reason_reference": None,
        "provenance_reference": None,
        "rights_reference": None,
        "idempotency_reference": None,
        "conflict_reference": None,
    }
    values.update(overrides)
    return make_assessment(**values)


def make_record(**overrides: object) -> OperatorApprovalAuditRecord:
    values: dict[str, object] = {
        "audit_record_id": "audit-record-001",
        "decision_id": "decision-001",
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "permission_reference": "permission-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "action": ACTION_APPROVE,
        "assessment_outcome": OUTCOME_ELIGIBLE,
        "assessment_reason_code": (
            REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ),
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
        "lifecycle_reason_reference": "lifecycle-reason-001",
        "provenance_reference": "provenance-001",
        "rights_reference": "rights-001",
        "idempotency_reference": "idempotency-001",
        "conflict_reference": "conflict-001",
    }
    values.update(overrides)
    return OperatorApprovalAuditRecord(**values)  # type: ignore[arg-type]


def make_denied_record(**overrides: object) -> OperatorApprovalAuditRecord:
    values: dict[str, object] = {
        "assessment_outcome": OUTCOME_DENIED,
        "assessment_reason_code": REASON_INVALID_DECISION,
        "permission_reference": None,
        "lifecycle_reason_reference": None,
        "provenance_reference": None,
        "rights_reference": None,
        "idempotency_reference": None,
        "conflict_reference": None,
    }
    values.update(overrides)
    return make_record(**values)


def make_history(
    *records: OperatorApprovalAuditRecord,
) -> OperatorApprovalAuditHistory:
    return OperatorApprovalAuditHistory(records=tuple(records))


RECORD_REQUIRED_FIELDS = (
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
OPTIONAL_REFERENCE_FIELDS = (
    "permission_reference",
    "lifecycle_reason_reference",
    "provenance_reference",
    "rights_reference",
    "idempotency_reference",
    "conflict_reference",
)
AGREEMENT_FIELDS = (
    "decision_id",
    "operator_reference",
    "role_reference",
    "target_type",
    "target_reference",
    "action",
    "reason_reference",
    "audit_context_reference",
)
READ_FUNCTIONS = (
    list_operator_approval_audit_records_by_decision_id,
    list_operator_approval_audit_records_by_operator_reference,
    list_operator_approval_audit_records_by_audit_context_reference,
)


def test_models_have_exact_required_fields() -> None:
    assert tuple(field.name for field in fields(OperatorApprovalAuditRecord)) == (
        "audit_record_id",
        "decision_id",
        "operator_reference",
        "role_reference",
        "permission_reference",
        "target_type",
        "target_reference",
        "action",
        "assessment_outcome",
        "assessment_reason_code",
        "reason_reference",
        "audit_context_reference",
        "lifecycle_reason_reference",
        "provenance_reference",
        "rights_reference",
        "idempotency_reference",
        "conflict_reference",
    )
    assert tuple(field.name for field in fields(OperatorApprovalAuditHistory)) == (
        "records",
    )
    assert tuple(
        field.name for field in fields(OperatorApprovalAuditAppendResult)
    ) == (
        "outcome",
        "history",
        "record",
        "conflicting_audit_record_id",
    )
    for model in (
        OperatorApprovalAuditRecord,
        OperatorApprovalAuditHistory,
        OperatorApprovalAuditAppendResult,
    ):
        assert all(field.default is MISSING for field in fields(model))
        assert all(field.default_factory is MISSING for field in fields(model))


@pytest.mark.parametrize(
    "instance",
    [
        make_record(),
        make_history(make_record()),
        OperatorApprovalAuditAppendResult(
            outcome=APPEND_OUTCOME_EXACT_DUPLICATE,
            history=make_history(make_record()),
            record=make_record(),
            conflicting_audit_record_id=None,
        ),
    ],
)
def test_models_are_immutable(instance: object) -> None:
    with pytest.raises(FrozenInstanceError):
        instance.outcome = "changed"  # type: ignore[attr-defined]


def test_exact_append_outcome_vocabulary() -> None:
    assert ALLOWED_AUDIT_APPEND_OUTCOMES == {
        "APPENDED",
        "EXACT_DUPLICATE",
        "CONFLICT",
    }


@pytest.mark.parametrize("field_name", RECORD_REQUIRED_FIELDS)
def test_record_rejects_non_text_required_field(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_record(**{field_name: 1})


@pytest.mark.parametrize("field_name", RECORD_REQUIRED_FIELDS)
@pytest.mark.parametrize(
    ("invalid_value", "message"),
    [
        ("", "must not be empty"),
        (" nonempty", "must not contain leading or trailing whitespace"),
        ("nonempty ", "must not contain leading or trailing whitespace"),
        ("caf\u00e9", "must contain ASCII text only"),
        ("value\nnext", "must not contain control characters"),
    ],
)
def test_record_rejects_invalid_required_ascii_text(
    field_name: str,
    invalid_value: str,
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        make_record(**{field_name: invalid_value})


@pytest.mark.parametrize("field_name", OPTIONAL_REFERENCE_FIELDS)
def test_record_rejects_non_text_optional_reference(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_denied_record(**{field_name: 1})


@pytest.mark.parametrize("field_name", OPTIONAL_REFERENCE_FIELDS)
@pytest.mark.parametrize(
    ("invalid_value", "message"),
    [
        ("", "must not be empty"),
        (" nonempty", "must not contain leading or trailing whitespace"),
        ("nonempty ", "must not contain leading or trailing whitespace"),
        ("caf\u00e9", "must contain ASCII text only"),
        ("value\tmore", "must not contain control characters"),
    ],
)
def test_record_rejects_invalid_optional_reference(
    field_name: str,
    invalid_value: str,
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        make_denied_record(**{field_name: invalid_value})


@pytest.mark.parametrize("field_name", OPTIONAL_REFERENCE_FIELDS)
def test_eligible_record_requires_every_optional_reference(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=rf"^{field_name} must be text$",
    ):
        make_record(**{field_name: None})


def test_eligible_record_requires_exact_reason_code() -> None:
    with pytest.raises(
        ValueError,
        match="ELIGIBLE requires the exact eligible reason code",
    ):
        make_record(assessment_reason_code=REASON_INVALID_DECISION)


def test_denied_record_rejects_eligible_reason_code() -> None:
    with pytest.raises(
        ValueError,
        match="the eligible reason code requires ELIGIBLE",
    ):
        make_denied_record(
            assessment_reason_code=(
                REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
            )
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("target_type", "UNKNOWN", "target_type is not supported"),
        ("action", "UNKNOWN", "action is not supported"),
        (
            "assessment_outcome",
            "UNKNOWN",
            "assessment_outcome must be ELIGIBLE or DENIED",
        ),
        (
            "assessment_reason_code",
            "UNKNOWN",
            "assessment_reason_code is not supported",
        ),
    ],
)
def test_record_rejects_unsupported_vocabulary(
    field_name: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_record(**{field_name: value})


def test_denied_record_allows_absent_assessment_references() -> None:
    record = make_denied_record()
    assert record.assessment_outcome == OUTCOME_DENIED
    assert all(getattr(record, field_name) is None for field_name in OPTIONAL_REFERENCE_FIELDS)


def test_denied_record_allows_present_valid_assessment_references() -> None:
    record = make_denied_record(
        permission_reference="permission-denied",
        lifecycle_reason_reference="lifecycle-denied",
        provenance_reference="provenance-denied",
        rights_reference="rights-denied",
        idempotency_reference="idempotency-denied",
        conflict_reference="conflict-denied",
    )
    assert record.permission_reference == "permission-denied"


def test_empty_history_is_valid() -> None:
    assert make_history().records == ()


def test_history_rejects_non_tuple_records() -> None:
    with pytest.raises(TypeError, match="records must be a tuple"):
        OperatorApprovalAuditHistory(records=[])  # type: ignore[arg-type]


def test_history_rejects_non_record_member() -> None:
    with pytest.raises(
        TypeError,
        match="records must contain OperatorApprovalAuditRecord values",
    ):
        OperatorApprovalAuditHistory(records=("invalid",))  # type: ignore[arg-type]


def test_history_rejects_duplicate_audit_record_id() -> None:
    first = make_record()
    second = make_record(
        decision_id="decision-002",
        audit_context_reference="audit-context-002",
    )
    with pytest.raises(
        ValueError,
        match="history contains duplicate audit_record_id",
    ):
        make_history(first, second)


def test_history_rejects_duplicate_decision_and_audit_context() -> None:
    first = make_record()
    second = make_record(audit_record_id="audit-record-002")
    with pytest.raises(
        ValueError,
        match="history contains duplicate decision and audit context",
    ):
        make_history(first, second)


@pytest.mark.parametrize(
    ("outcome", "record", "conflict_id", "message"),
    [
        (
            APPEND_OUTCOME_APPENDED,
            None,
            None,
            "APPENDED requires record",
        ),
        (
            APPEND_OUTCOME_APPENDED,
            make_record(),
            "audit-record-001",
            "APPENDED requires absent conflicting_audit_record_id",
        ),
        (
            APPEND_OUTCOME_EXACT_DUPLICATE,
            None,
            None,
            "EXACT_DUPLICATE requires record",
        ),
        (
            APPEND_OUTCOME_EXACT_DUPLICATE,
            make_record(),
            "audit-record-001",
            "EXACT_DUPLICATE requires absent conflicting_audit_record_id",
        ),
        (
            APPEND_OUTCOME_CONFLICT,
            make_record(),
            "audit-record-001",
            "CONFLICT requires absent record",
        ),
        (
            APPEND_OUTCOME_CONFLICT,
            None,
            None,
            "CONFLICT requires conflicting_audit_record_id",
        ),
    ],
)
def test_append_result_rejects_invalid_field_combinations(
    outcome: str,
    record: OperatorApprovalAuditRecord | None,
    conflict_id: str | None,
    message: str,
) -> None:
    history = make_history(make_record())
    with pytest.raises(ValueError, match=message):
        OperatorApprovalAuditAppendResult(
            outcome=outcome,  # type: ignore[arg-type]
            history=history,
            record=record,
            conflicting_audit_record_id=conflict_id,
        )


def test_append_result_rejects_unsupported_outcome() -> None:
    with pytest.raises(ValueError, match="outcome is not supported"):
        OperatorApprovalAuditAppendResult(
            outcome="UNKNOWN",  # type: ignore[arg-type]
            history=make_history(),
            record=None,
            conflicting_audit_record_id=None,
        )


def test_appended_result_requires_record_at_history_end() -> None:
    first = make_record()
    second = make_record(
        audit_record_id="audit-record-002",
        decision_id="decision-002",
        audit_context_reference="audit-context-002",
    )
    with pytest.raises(
        ValueError,
        match="APPENDED requires record at the end of history",
    ):
        OperatorApprovalAuditAppendResult(
            outcome=APPEND_OUTCOME_APPENDED,
            history=make_history(first, second),
            record=first,
            conflicting_audit_record_id=None,
        )


def test_exact_duplicate_result_requires_existing_record() -> None:
    with pytest.raises(
        ValueError,
        match="EXACT_DUPLICATE requires existing record in history",
    ):
        OperatorApprovalAuditAppendResult(
            outcome=APPEND_OUTCOME_EXACT_DUPLICATE,
            history=make_history(),
            record=make_record(),
            conflicting_audit_record_id=None,
        )


def test_conflict_result_requires_existing_conflict_id() -> None:
    with pytest.raises(
        ValueError,
        match="CONFLICT requires an existing conflicting audit record",
    ):
        OperatorApprovalAuditAppendResult(
            outcome=APPEND_OUTCOME_CONFLICT,
            history=make_history(make_record()),
            record=None,
            conflicting_audit_record_id="missing",
        )


@pytest.mark.parametrize(
    ("audit_record_id", "error_type", "message"),
    [
        (1, TypeError, "audit_record_id must be text"),
        ("", ValueError, "audit_record_id must not be empty"),
        (" bad", ValueError, "must not contain leading or trailing whitespace"),
        ("bad ", ValueError, "must not contain leading or trailing whitespace"),
        ("caf\u00e9", ValueError, "must contain ASCII text only"),
        ("bad\nid", ValueError, "must not contain control characters"),
    ],
)
def test_record_constructor_rejects_invalid_audit_record_id(
    audit_record_id: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        create_operator_approval_audit_record(
            audit_record_id,  # type: ignore[arg-type]
            make_decision(),
            make_assessment(),
        )


def test_record_constructor_rejects_invalid_decision_type() -> None:
    with pytest.raises(
        TypeError,
        match="decision must be OperatorApprovalDecision",
    ):
        create_operator_approval_audit_record(
            "audit-record-001",
            object(),  # type: ignore[arg-type]
            make_assessment(),
        )


def test_record_constructor_rejects_invalid_assessment_type() -> None:
    with pytest.raises(
        TypeError,
        match="assessment must be OperatorApprovalExecutionAssessment",
    ):
        create_operator_approval_audit_record(
            "audit-record-001",
            make_decision(),
            object(),  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("field_name", AGREEMENT_FIELDS)
def test_record_constructor_rejects_every_identity_mismatch(
    field_name: str,
) -> None:
    assessment = make_assessment()
    mismatch_value = {
        "target_type": "KNOWLEDGE",
        "action": "REJECT",
    }.get(field_name, f"different-{field_name}")
    object.__setattr__(
        assessment,
        field_name,
        mismatch_value,
    )
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must match exactly$",
    ):
        create_operator_approval_audit_record(
            "audit-record-001",
            make_decision(),
            assessment,
        )


def test_record_constructor_copies_eligible_facts_exactly() -> None:
    decision = make_decision()
    assessment = make_assessment()
    record = create_operator_approval_audit_record(
        "audit-record-explicit",
        decision,
        assessment,
    )
    assert asdict(record) == {
        "audit_record_id": "audit-record-explicit",
        "decision_id": decision.decision_id,
        "operator_reference": decision.operator_reference,
        "role_reference": decision.role_reference,
        "permission_reference": assessment.permission_reference,
        "target_type": decision.target_type,
        "target_reference": decision.target_reference,
        "action": decision.action,
        "assessment_outcome": assessment.outcome,
        "assessment_reason_code": assessment.reason_code,
        "reason_reference": decision.reason_reference,
        "audit_context_reference": decision.audit_context_reference,
        "lifecycle_reason_reference": assessment.lifecycle_reason_reference,
        "provenance_reference": assessment.provenance_reference,
        "rights_reference": assessment.rights_reference,
        "idempotency_reference": assessment.idempotency_reference,
        "conflict_reference": assessment.conflict_reference,
    }


def test_record_constructor_copies_denied_absent_references_exactly() -> None:
    record = create_operator_approval_audit_record(
        "audit-record-denied",
        make_decision(),
        make_denied_assessment(),
    )
    assert record.assessment_outcome == OUTCOME_DENIED
    assert all(getattr(record, field_name) is None for field_name in OPTIONAL_REFERENCE_FIELDS)


@pytest.mark.parametrize("field_name", AGREEMENT_FIELDS)
@pytest.mark.parametrize(
    ("invalid_value", "message"),
    [
        ("", "must not be empty"),
        (" bad", "must not contain leading or trailing whitespace"),
        ("caf\u00e9", "must contain ASCII text only"),
        ("bad\nvalue", "must not contain control characters"),
    ],
)
def test_record_constructor_revalidates_corrupted_decision(
    field_name: str,
    invalid_value: str,
    message: str,
) -> None:
    decision = make_decision()
    object.__setattr__(decision, field_name, invalid_value)
    with pytest.raises(ValueError, match=message):
        create_operator_approval_audit_record(
            "audit-record-001",
            decision,
            make_assessment(),
        )


@pytest.mark.parametrize("field_name", OPTIONAL_REFERENCE_FIELDS)
def test_record_constructor_rejects_corrupted_eligible_missing_reference(
    field_name: str,
) -> None:
    assessment = make_assessment()
    object.__setattr__(assessment, field_name, None)
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        create_operator_approval_audit_record(
            "audit-record-001",
            make_decision(),
            assessment,
        )


def test_append_to_empty_history_returns_appended() -> None:
    record = make_record()
    result = append_operator_approval_audit_record(make_history(), record)
    assert result.outcome == APPEND_OUTCOME_APPENDED
    assert result.history.records == (record,)
    assert result.record is record
    assert result.conflicting_audit_record_id is None


def test_append_preserves_original_history_and_order() -> None:
    first = make_record()
    second = make_record(
        audit_record_id="audit-record-002",
        decision_id="decision-002",
        audit_context_reference="audit-context-002",
    )
    original = make_history(first)
    result = append_operator_approval_audit_record(original, second)
    assert original.records == (first,)
    assert result.history.records == (first, second)
    assert result.history is not original


def test_exact_duplicate_returns_original_history_unchanged() -> None:
    record = make_record()
    history = make_history(record)
    result = append_operator_approval_audit_record(history, make_record())
    assert result.outcome == APPEND_OUTCOME_EXACT_DUPLICATE
    assert result.history is history
    assert result.record is record
    assert result.conflicting_audit_record_id is None


@pytest.mark.parametrize(
    ("field_name", "different_value"),
    [
        ("operator_reference", "operator-002"),
        ("role_reference", "role-002"),
        ("permission_reference", "permission-002"),
        ("target_reference", "evidence-002"),
        ("action", "REJECT"),
        ("assessment_outcome", OUTCOME_DENIED),
        ("reason_reference", "reason-002"),
        ("audit_context_reference", "audit-context-002"),
    ],
)
def test_same_id_with_different_fact_returns_conflict(
    field_name: str,
    different_value: str,
) -> None:
    existing = make_record()
    values: dict[str, object] = {field_name: different_value}
    if field_name == "assessment_outcome":
        values.update(
            {
                "assessment_reason_code": REASON_INVALID_DECISION,
                "permission_reference": None,
                "lifecycle_reason_reference": None,
                "provenance_reference": None,
                "rights_reference": None,
                "idempotency_reference": None,
                "conflict_reference": None,
            }
        )
    candidate = make_record(**values)
    history = make_history(existing)
    result = append_operator_approval_audit_record(history, candidate)
    assert result.outcome == APPEND_OUTCOME_CONFLICT
    assert result.history is history
    assert result.record is None
    assert result.conflicting_audit_record_id == existing.audit_record_id


def test_same_decision_context_under_different_id_returns_conflict() -> None:
    existing = make_record()
    candidate = make_record(audit_record_id="audit-record-002")
    history = make_history(existing)
    result = append_operator_approval_audit_record(history, candidate)
    assert result.outcome == APPEND_OUTCOME_CONFLICT
    assert result.history is history
    assert result.record is None
    assert result.conflicting_audit_record_id == existing.audit_record_id


def test_same_decision_with_different_context_can_append() -> None:
    existing = make_record()
    candidate = make_record(
        audit_record_id="audit-record-002",
        audit_context_reference="audit-context-002",
    )
    result = append_operator_approval_audit_record(
        make_history(existing),
        candidate,
    )
    assert result.outcome == APPEND_OUTCOME_APPENDED
    assert result.history.records == (existing, candidate)


def test_same_context_with_different_decision_can_append() -> None:
    existing = make_record()
    candidate = make_record(
        audit_record_id="audit-record-002",
        decision_id="decision-002",
    )
    result = append_operator_approval_audit_record(
        make_history(existing),
        candidate,
    )
    assert result.outcome == APPEND_OUTCOME_APPENDED
    assert result.history.records == (existing, candidate)


def test_append_revalidates_corrupted_record() -> None:
    record = make_record()
    object.__setattr__(record, "audit_record_id", "")
    with pytest.raises(ValueError, match="audit_record_id must not be empty"):
        append_operator_approval_audit_record(make_history(), record)


def test_append_rejects_invalid_history_type() -> None:
    with pytest.raises(
        TypeError,
        match="history must be OperatorApprovalAuditHistory",
    ):
        append_operator_approval_audit_record(
            object(),  # type: ignore[arg-type]
            make_record(),
        )


def test_append_rejects_invalid_record_type() -> None:
    with pytest.raises(
        TypeError,
        match="record must be OperatorApprovalAuditRecord",
    ):
        append_operator_approval_audit_record(
            make_history(),
            object(),  # type: ignore[arg-type]
        )


def build_read_history() -> OperatorApprovalAuditHistory:
    records = (
        make_record(),
        make_record(
            audit_record_id="audit-record-002",
            decision_id="decision-002",
            operator_reference="operator-001",
            target_reference="evidence-002",
            audit_context_reference="audit-context-002",
        ),
        make_record(
            audit_record_id="audit-record-003",
            decision_id="decision-003",
            operator_reference="operator-002",
            target_reference="evidence-001",
            audit_context_reference="audit-context-003",
        ),
        make_record(
            audit_record_id="audit-record-004",
            decision_id="decision-004",
            operator_reference="operator-001",
            target_reference="evidence-001",
            audit_context_reference="audit-context-004",
        ),
    )
    return make_history(*records)


def test_find_by_exact_audit_record_id_returns_record() -> None:
    history = build_read_history()
    assert (
        find_operator_approval_audit_record(history, "audit-record-003")
        is history.records[2]
    )


def test_find_by_exact_audit_record_id_returns_none() -> None:
    assert (
        find_operator_approval_audit_record(
            build_read_history(),
            "audit-record-missing",
        )
        is None
    )


@pytest.mark.parametrize(
    ("invalid_value", "error_type", "message"),
    [
        (1, TypeError, "audit_record_id must be text"),
        ("", ValueError, "audit_record_id must not be empty"),
        (" bad", ValueError, "must not contain leading or trailing whitespace"),
        ("caf\u00e9", ValueError, "must contain ASCII text only"),
        ("bad\nid", ValueError, "must not contain control characters"),
    ],
)
def test_find_rejects_invalid_id(
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        find_operator_approval_audit_record(
            build_read_history(),
            invalid_value,  # type: ignore[arg-type]
        )


def test_list_by_decision_id_is_exact_and_ordered() -> None:
    history = build_read_history()
    assert list_operator_approval_audit_records_by_decision_id(
        history,
        "decision-002",
        limit=100,
    ) == (history.records[1],)


def test_list_by_operator_reference_preserves_append_order() -> None:
    history = build_read_history()
    assert list_operator_approval_audit_records_by_operator_reference(
        history,
        "operator-001",
        limit=100,
    ) == (
        history.records[0],
        history.records[1],
        history.records[3],
    )


def test_list_by_target_requires_exact_type_and_reference() -> None:
    history = build_read_history()
    assert list_operator_approval_audit_records_by_target(
        history,
        TARGET_TYPE_EVIDENCE,
        "evidence-001",
        limit=100,
    ) == (
        history.records[0],
        history.records[2],
        history.records[3],
    )


def test_list_by_audit_context_is_exact() -> None:
    history = build_read_history()
    assert list_operator_approval_audit_records_by_audit_context_reference(
        history,
        "audit-context-004",
        limit=100,
    ) == (history.records[3],)


@pytest.mark.parametrize("limit", [1, 2, 3])
def test_list_limit_truncates_without_reordering(limit: int) -> None:
    history = build_read_history()
    result = list_operator_approval_audit_records_by_operator_reference(
        history,
        "operator-001",
        limit=limit,
    )
    expected = (
        history.records[0],
        history.records[1],
        history.records[3],
    )[:limit]
    assert result == expected


@pytest.mark.parametrize("limit", [1, 100])
def test_limit_boundaries_are_accepted(limit: int) -> None:
    result = list_operator_approval_audit_records_by_operator_reference(
        build_read_history(),
        "operator-001",
        limit=limit,
    )
    assert len(result) <= limit


@pytest.mark.parametrize(
    ("limit", "error_type", "message"),
    [
        (True, TypeError, "limit must be an integer"),
        (False, TypeError, "limit must be an integer"),
        (1.0, TypeError, "limit must be an integer"),
        ("1", TypeError, "limit must be an integer"),
        (0, ValueError, "limit must be from 1 through 100"),
        (-1, ValueError, "limit must be from 1 through 100"),
        (101, ValueError, "limit must be from 1 through 100"),
    ],
)
def test_reads_reject_invalid_limit(
    limit: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        list_operator_approval_audit_records_by_operator_reference(
            build_read_history(),
            "operator-001",
            limit=limit,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("function", "field_name"),
    [
        (
            list_operator_approval_audit_records_by_decision_id,
            "decision_id",
        ),
        (
            list_operator_approval_audit_records_by_operator_reference,
            "operator_reference",
        ),
        (
            list_operator_approval_audit_records_by_audit_context_reference,
            "audit_context_reference",
        ),
    ],
)
@pytest.mark.parametrize(
    ("invalid_value", "error_type", "message"),
    [
        (1, TypeError, "must be text"),
        ("", ValueError, "must not be empty"),
        (" bad", ValueError, "must not contain leading or trailing whitespace"),
        ("caf\u00e9", ValueError, "must contain ASCII text only"),
        ("bad\nvalue", ValueError, "must not contain control characters"),
    ],
)
def test_single_key_reads_reject_invalid_query(
    function: object,
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=rf"{field_name} {message}"):
        function(  # type: ignore[operator]
            build_read_history(),
            invalid_value,
            limit=10,
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value", "error_type", "message"),
    [
        ("target_type", 1, TypeError, "target_type must be text"),
        ("target_type", "", ValueError, "target_type must not be empty"),
        (
            "target_type",
            "UNKNOWN",
            ValueError,
            "target_type is not supported",
        ),
        (
            "target_reference",
            1,
            TypeError,
            "target_reference must be text",
        ),
        (
            "target_reference",
            "",
            ValueError,
            "target_reference must not be empty",
        ),
        (
            "target_reference",
            " bad",
            ValueError,
            "must not contain leading or trailing whitespace",
        ),
    ],
)
def test_target_read_rejects_invalid_query(
    field_name: str,
    invalid_value: object,
    error_type: type[Exception],
    message: str,
) -> None:
    values: dict[str, object] = {
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
    }
    values[field_name] = invalid_value
    with pytest.raises(error_type, match=message):
        list_operator_approval_audit_records_by_target(
            build_read_history(),
            values["target_type"],  # type: ignore[arg-type]
            values["target_reference"],  # type: ignore[arg-type]
            limit=10,
        )


@pytest.mark.parametrize(
    "reader",
    [
        find_operator_approval_audit_record,
        list_operator_approval_audit_records_by_decision_id,
        list_operator_approval_audit_records_by_operator_reference,
        list_operator_approval_audit_records_by_audit_context_reference,
    ],
)
def test_reads_reject_invalid_history_type(reader: object) -> None:
    with pytest.raises(
        TypeError,
        match="history must be OperatorApprovalAuditHistory",
    ):
        if reader is find_operator_approval_audit_record:
            reader(object(), "audit-record-001")  # type: ignore[operator]
        else:
            reader(object(), "value", limit=10)  # type: ignore[operator]


def test_target_read_rejects_invalid_history_type() -> None:
    with pytest.raises(
        TypeError,
        match="history must be OperatorApprovalAuditHistory",
    ):
        list_operator_approval_audit_records_by_target(
            object(),  # type: ignore[arg-type]
            TARGET_TYPE_EVIDENCE,
            "evidence-001",
            limit=10,
        )


def test_reads_return_tuples_not_mutable_lists() -> None:
    history = build_read_history()
    assert isinstance(
        list_operator_approval_audit_records_by_operator_reference(
            history,
            "operator-001",
            limit=10,
        ),
        tuple,
    )


def test_read_misses_return_empty_tuple() -> None:
    history = build_read_history()
    assert list_operator_approval_audit_records_by_operator_reference(
        history,
        "operator-missing",
        limit=10,
    ) == ()


def test_no_clock_random_network_or_io_imports() -> None:
    import rie.domain.operator_approval_audit_history as module

    source = module.__loader__.get_source(module.__name__)  # type: ignore[union-attr]
    assert source is not None
    prohibited = (
        "datetime",
        "time",
        "random",
        "uuid",
        "pathlib",
        "sqlite",
        "requests",
        "socket",
        "open(",
    )
    assert not any(token in source for token in prohibited)


def test_authority_separations_remain_non_executing() -> None:
    record = create_operator_approval_audit_record(
        "audit-record-001",
        make_decision(),
        make_assessment(),
    )
    result = append_operator_approval_audit_record(make_history(), record)
    assert result.outcome == APPEND_OUTCOME_APPENDED
    assert not hasattr(result, "execute")
    assert not hasattr(result, "promote")
    assert not hasattr(result, "persist")
