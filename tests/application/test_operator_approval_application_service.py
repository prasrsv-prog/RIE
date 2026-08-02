from dataclasses import FrozenInstanceError, MISSING, asdict, fields

import pytest

from rie.application.operator_approval_application_service import (
    ALLOWED_ASSESSMENT_OUTCOMES,
    ALLOWED_ASSESSMENT_REASON_CODES,
    CONFLICT_CLEAR,
    IDEMPOTENCY_NEW,
    LIFECYCLE_ELIGIBLE,
    OUTCOME_DENIED,
    OUTCOME_ELIGIBLE,
    PROVENANCE_VERIFIED,
    REASON_ACTION_MISMATCH,
    REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH,
    REASON_BLOCKING_CONFLICT_PRESENT,
    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
    REASON_IDEMPOTENCY_NOT_NEW,
    REASON_INVALID_DECISION,
    REASON_INVALID_ROLE_AUTHORITY_EVALUATION,
    REASON_INVALID_TARGET_APPROVAL_CONTEXT,
    REASON_OPERATOR_REFERENCE_MISMATCH,
    REASON_PROVENANCE_NOT_VERIFIED,
    REASON_REASON_REFERENCE_MISMATCH,
    REASON_RIGHTS_NOT_CLEARED,
    REASON_ROLE_AUTHORITY_NOT_ALLOWED,
    REASON_ROLE_REFERENCE_MISMATCH,
    REASON_TARGET_LIFECYCLE_NOT_ELIGIBLE,
    REASON_TARGET_REFERENCE_MISMATCH,
    REASON_TARGET_TYPE_MISMATCH,
    RIGHTS_CLEARED,
    OperatorApprovalExecutionAssessment,
    TargetApprovalContext,
    assess_operator_approval_execution,
)
from rie.domain.operator_approval_decision import (
    ACTION_APPROVE,
    ACTION_REJECT,
    TARGET_TYPE_EVIDENCE,
    TARGET_TYPE_GOVERNED_ASSET_RECORD,
    TARGET_TYPE_INGESTION_JOB,
    TARGET_TYPE_KNOWLEDGE,
    TARGET_TYPE_KNOWLEDGE_CONFLICT,
    TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY,
    TARGET_TYPE_PROMPT_CANDIDATE,
    OperatorApprovalDecision,
)
from rie.domain.operator_role_authority import (
    OUTCOME_ALLOW,
    OUTCOME_DENY,
    OperatorRolePermissionEvaluation,
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


def make_role_evaluation(
    **overrides: object,
) -> OperatorRolePermissionEvaluation:
    values: dict[str, object] = {
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "action": ACTION_APPROVE,
        "outcome": OUTCOME_ALLOW,
        "reason_code": "AUTHORIZED_EXACT_MATCH",
        "permission_reference": "permission-001",
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return OperatorRolePermissionEvaluation(**values)  # type: ignore[arg-type]


def make_target_context(**overrides: object) -> TargetApprovalContext:
    values: dict[str, object] = {
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "lifecycle_state": "CANDIDATE",
        "lifecycle_eligibility": LIFECYCLE_ELIGIBLE,
        "lifecycle_reason_reference": "lifecycle-reason-001",
        "provenance_status": PROVENANCE_VERIFIED,
        "provenance_reference": "provenance-001",
        "rights_status": RIGHTS_CLEARED,
        "rights_reference": "rights-001",
        "idempotency_status": IDEMPOTENCY_NEW,
        "idempotency_reference": "idempotency-001",
        "conflict_status": CONFLICT_CLEAR,
        "conflict_reference": "conflict-001",
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return TargetApprovalContext(**values)  # type: ignore[arg-type]


_MISSING = object()


def assess(
    *,
    decision: object = _MISSING,
    role_evaluation: object = _MISSING,
    target_context: object = _MISSING,
) -> OperatorApprovalExecutionAssessment:
    return assess_operator_approval_execution(
        make_decision() if decision is _MISSING else decision,
        make_role_evaluation() if role_evaluation is _MISSING else role_evaluation,
        make_target_context() if target_context is _MISSING else target_context,
    )


def test_models_have_exact_required_fields() -> None:
    assert tuple(field.name for field in fields(TargetApprovalContext)) == (
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
    assert tuple(
        field.name for field in fields(OperatorApprovalExecutionAssessment)
    ) == (
        "decision_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "outcome",
        "reason_code",
        "reason_reference",
        "audit_context_reference",
        "permission_reference",
        "lifecycle_reason_reference",
        "provenance_reference",
        "rights_reference",
        "idempotency_reference",
        "conflict_reference",
    )
    for model in (TargetApprovalContext, OperatorApprovalExecutionAssessment):
        assert all(field.default is MISSING for field in fields(model))
        assert all(field.default_factory is MISSING for field in fields(model))


@pytest.mark.parametrize(
    "instance",
    [
        make_target_context(),
        assess(),
    ],
)
def test_models_are_immutable(instance: object) -> None:
    with pytest.raises(FrozenInstanceError):
        instance.reason_reference = "changed"  # type: ignore[attr-defined]


def test_exact_outcome_vocabulary() -> None:
    assert ALLOWED_ASSESSMENT_OUTCOMES == {"ELIGIBLE", "DENIED"}


def test_exact_reason_code_vocabulary() -> None:
    assert ALLOWED_ASSESSMENT_REASON_CODES == {
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
    }


@pytest.mark.parametrize(
    "field_name",
    [field.name for field in fields(TargetApprovalContext)],
)
def test_target_context_rejects_non_text(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_target_context(**{field_name: 1})


@pytest.mark.parametrize(
    "field_name",
    [field.name for field in fields(TargetApprovalContext)],
)
@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("", "must not be empty"),
        (" value", "must not contain leading or trailing whitespace"),
        ("value ", "must not contain leading or trailing whitespace"),
        ("value\nx", "must not contain control characters"),
        ("value" + chr(127), "must not contain control characters"),
        ("nilai-" + chr(233), "must contain ASCII text only"),
    ],
)
def test_target_context_rejects_invalid_text(
    field_name: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_target_context(**{field_name: value})


@pytest.mark.parametrize(
    ("target_type", "target_reference"),
    [
        (TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY, "source-001"),
        (TARGET_TYPE_INGESTION_JOB, "job-001"),
        (TARGET_TYPE_EVIDENCE, "evidence-001"),
        (TARGET_TYPE_KNOWLEDGE, "knowledge-001"),
        (TARGET_TYPE_KNOWLEDGE_CONFLICT, "conflict-target-001"),
        (TARGET_TYPE_PROMPT_CANDIDATE, "prompt-001"),
        (TARGET_TYPE_GOVERNED_ASSET_RECORD, "asset-001"),
    ],
)
@pytest.mark.parametrize("action", [ACTION_APPROVE, ACTION_REJECT])
def test_exact_positive_evidence_is_eligible_for_each_supported_tuple(
    target_type: str,
    target_reference: str,
    action: str,
) -> None:
    decision = make_decision(
        target_type=target_type,
        target_reference=target_reference,
        action=action,
    )
    role = make_role_evaluation(target_type=target_type, action=action)
    context = make_target_context(
        target_type=target_type,
        target_reference=target_reference,
    )
    result = assess(
        decision=decision,
        role_evaluation=role,
        target_context=context,
    )
    assert result.outcome == OUTCOME_ELIGIBLE
    assert (
        result.reason_code
        == REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
    )
    assert result.permission_reference == "permission-001"


def test_eligible_assessment_preserves_all_explicit_references() -> None:
    result = assess(
        role_evaluation=make_role_evaluation(
            permission_reference="permission-exact-777"
        ),
        target_context=make_target_context(
            lifecycle_reason_reference="lifecycle-reason-exact",
            provenance_reference="provenance-exact",
            rights_reference="rights-exact",
            idempotency_reference="idempotency-exact",
            conflict_reference="conflict-exact",
        ),
    )
    assert result == OperatorApprovalExecutionAssessment(
        decision_id="decision-001",
        operator_reference="operator-001",
        role_reference="reviewer-role-001",
        target_type=TARGET_TYPE_EVIDENCE,
        target_reference="evidence-001",
        action=ACTION_APPROVE,
        outcome=OUTCOME_ELIGIBLE,
        reason_code=REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
        reason_reference="reason-001",
        audit_context_reference="audit-context-001",
        permission_reference="permission-exact-777",
        lifecycle_reason_reference="lifecycle-reason-exact",
        provenance_reference="provenance-exact",
        rights_reference="rights-exact",
        idempotency_reference="idempotency-exact",
        conflict_reference="conflict-exact",
    )


def test_assessment_is_deterministic_and_serialization_safe() -> None:
    first = assess()
    second = assess()
    assert first == second
    assert asdict(first) == asdict(second)
    assert all(
        value is None or isinstance(value, str)
        for value in asdict(first).values()
    )


@pytest.mark.parametrize(
    ("decision", "expected_reason"),
    [
        (object(), REASON_INVALID_DECISION),
        (None, REASON_INVALID_DECISION),
        (1, REASON_INVALID_DECISION),
    ],
)
def test_invalid_decision_type_denies(
    decision: object,
    expected_reason: str,
) -> None:
    result = assess(decision=decision)
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == expected_reason


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("decision_id", ""),
        ("operator_reference", " operator-001"),
        ("role_reference", "role\n001"),
        ("target_type", "SOURCE"),
        ("target_reference", "target-" + chr(233)),
        ("action", "ACCEPT"),
        ("reason_reference", ""),
        ("audit_context_reference", "audit-context-001 "),
    ],
)
def test_mutated_invalid_decision_denies_first(
    field_name: str,
    value: str,
) -> None:
    decision = make_decision()
    object.__setattr__(decision, field_name, value)
    role = make_role_evaluation(operator_reference="different")
    context = make_target_context(lifecycle_eligibility="BLOCKED")
    result = assess(
        decision=decision,
        role_evaluation=role,
        target_context=context,
    )
    assert result.reason_code == REASON_INVALID_DECISION


@pytest.mark.parametrize("role_evaluation", [object(), None, 1])
def test_invalid_role_evaluation_type_denies(role_evaluation: object) -> None:
    result = assess(role_evaluation=role_evaluation)
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == REASON_INVALID_ROLE_AUTHORITY_EVALUATION


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("operator_reference", ""),
        ("role_reference", " role"),
        ("target_type", "target\n"),
        ("action", "action-" + chr(233)),
        ("outcome", ""),
        ("reason_code", ""),
        ("reason_reference", "reason "),
        ("audit_context_reference", "audit\ncontext"),
        ("permission_reference", ""),
    ],
)
def test_mutated_invalid_role_evaluation_denies_before_identity_checks(
    field_name: str,
    value: str,
) -> None:
    role = make_role_evaluation()
    object.__setattr__(role, field_name, value)
    context = make_target_context(lifecycle_eligibility="BLOCKED")
    result = assess(role_evaluation=role, target_context=context)
    assert result.reason_code == REASON_INVALID_ROLE_AUTHORITY_EVALUATION


@pytest.mark.parametrize("target_context", [object(), None, 1])
def test_invalid_target_context_type_denies(target_context: object) -> None:
    result = assess(target_context=target_context)
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == REASON_INVALID_TARGET_APPROVAL_CONTEXT


def test_mutated_invalid_target_context_denies_before_identity_checks() -> None:
    context = make_target_context()
    object.__setattr__(context, "target_reference", "")
    role = make_role_evaluation(operator_reference="different")
    result = assess(role_evaluation=role, target_context=context)
    assert result.reason_code == REASON_INVALID_TARGET_APPROVAL_CONTEXT


@pytest.mark.parametrize(
    ("role_overrides", "reason_code"),
    [
        (
            {"operator_reference": "operator-other"},
            REASON_OPERATOR_REFERENCE_MISMATCH,
        ),
        ({"role_reference": "role-other"}, REASON_ROLE_REFERENCE_MISMATCH),
        ({"action": ACTION_REJECT}, REASON_ACTION_MISMATCH),
        (
            {"target_type": TARGET_TYPE_GOVERNED_ASSET_RECORD},
            REASON_TARGET_TYPE_MISMATCH,
        ),
        (
            {"reason_reference": "reason-other"},
            REASON_REASON_REFERENCE_MISMATCH,
        ),
        (
            {"audit_context_reference": "audit-other"},
            REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH,
        ),
    ],
)
def test_decision_to_role_mismatch_reasons_are_exact(
    role_overrides: dict[str, object],
    reason_code: str,
) -> None:
    result = assess(role_evaluation=make_role_evaluation(**role_overrides))
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == reason_code


def test_decision_to_role_first_failure_order_is_stable() -> None:
    result = assess(
        role_evaluation=make_role_evaluation(
            operator_reference="operator-other",
            role_reference="role-other",
            action=ACTION_REJECT,
            target_type=TARGET_TYPE_GOVERNED_ASSET_RECORD,
            reason_reference="reason-other",
            audit_context_reference="audit-other",
        )
    )
    assert result.reason_code == REASON_OPERATOR_REFERENCE_MISMATCH


@pytest.mark.parametrize(
    ("outcome", "permission_reference"),
    [
        (OUTCOME_DENY, None),
        (OUTCOME_DENY, "permission-001"),
        ("UNKNOWN", "permission-001"),
        (OUTCOME_ALLOW, None),
    ],
)
def test_role_authority_must_be_exact_allow_with_permission_reference(
    outcome: str,
    permission_reference: str | None,
) -> None:
    role = make_role_evaluation()
    object.__setattr__(role, "outcome", outcome)
    object.__setattr__(role, "permission_reference", permission_reference)
    result = assess(role_evaluation=role)
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == REASON_ROLE_AUTHORITY_NOT_ALLOWED


@pytest.mark.parametrize(
    ("context_overrides", "reason_code"),
    [
        (
            {"target_type": TARGET_TYPE_GOVERNED_ASSET_RECORD},
            REASON_TARGET_TYPE_MISMATCH,
        ),
        (
            {"target_reference": "evidence-other"},
            REASON_TARGET_REFERENCE_MISMATCH,
        ),
        (
            {"reason_reference": "reason-other"},
            REASON_REASON_REFERENCE_MISMATCH,
        ),
        (
            {"audit_context_reference": "audit-other"},
            REASON_AUDIT_CONTEXT_REFERENCE_MISMATCH,
        ),
        (
            {"lifecycle_eligibility": "BLOCKED"},
            REASON_TARGET_LIFECYCLE_NOT_ELIGIBLE,
        ),
        (
            {"provenance_status": "UNKNOWN"},
            REASON_PROVENANCE_NOT_VERIFIED,
        ),
        ({"rights_status": "UNCLEARED"}, REASON_RIGHTS_NOT_CLEARED),
        ({"idempotency_status": "EXISTING"}, REASON_IDEMPOTENCY_NOT_NEW),
        ({"conflict_status": "BLOCKED"}, REASON_BLOCKING_CONFLICT_PRESENT),
    ],
)
def test_target_context_failure_reasons_are_exact(
    context_overrides: dict[str, object],
    reason_code: str,
) -> None:
    result = assess(target_context=make_target_context(**context_overrides))
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == reason_code


def test_target_context_first_failure_order_is_stable() -> None:
    result = assess(
        target_context=make_target_context(
            target_type=TARGET_TYPE_GOVERNED_ASSET_RECORD,
            target_reference="other",
            reason_reference="other",
            audit_context_reference="other",
            lifecycle_eligibility="BLOCKED",
            provenance_status="UNKNOWN",
            rights_status="UNCLEARED",
            idempotency_status="EXISTING",
            conflict_status="BLOCKED",
        )
    )
    assert result.reason_code == REASON_TARGET_TYPE_MISMATCH


def test_role_authority_failure_precedes_target_context_failure() -> None:
    role = make_role_evaluation()
    object.__setattr__(role, "outcome", OUTCOME_DENY)
    object.__setattr__(role, "permission_reference", None)
    result = assess(
        role_evaluation=role,
        target_context=make_target_context(
            lifecycle_eligibility="BLOCKED",
        ),
    )
    assert result.reason_code == REASON_ROLE_AUTHORITY_NOT_ALLOWED


def test_inputs_are_not_modified() -> None:
    decision = make_decision()
    role = make_role_evaluation()
    context = make_target_context()
    before = (asdict(decision), asdict(role), asdict(context))
    assess(
        decision=decision,
        role_evaluation=role,
        target_context=context,
    )
    assert (asdict(decision), asdict(role), asdict(context)) == before


def test_eligible_result_is_non_executing_and_non_persistent() -> None:
    result = assess()
    for attribute_name in (
        "executed",
        "persisted",
        "mutated",
        "promoted",
        "published",
        "repository",
        "storage",
    ):
        assert not hasattr(result, attribute_name)


@pytest.mark.parametrize(
    ("outcome", "reason_code", "message"),
    [
        (
            OUTCOME_ELIGIBLE,
            REASON_INVALID_DECISION,
            "ELIGIBLE requires the exact eligible reason code",
        ),
        (
            OUTCOME_DENIED,
            REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
            "the eligible reason code requires ELIGIBLE",
        ),
        ("PENDING", REASON_INVALID_DECISION, "outcome must be ELIGIBLE or DENIED"),
        (OUTCOME_DENIED, "UNKNOWN", "reason_code is not supported"),
    ],
)
def test_assessment_rejects_invalid_outcome_reason_pairs(
    outcome: str,
    reason_code: str,
    message: str,
) -> None:
    values = asdict(assess())
    values["outcome"] = outcome
    values["reason_code"] = reason_code
    with pytest.raises(ValueError, match=message):
        OperatorApprovalExecutionAssessment(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    [
        "permission_reference",
        "lifecycle_reason_reference",
        "provenance_reference",
        "rights_reference",
        "idempotency_reference",
        "conflict_reference",
    ],
)
@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("", "must not be empty"),
        (" ref", "must not contain leading or trailing whitespace"),
        ("ref\nx", "must not contain control characters"),
        ("ref-" + chr(233), "must contain ASCII text only"),
    ],
)
def test_assessment_optional_references_reject_invalid_present_values(
    field_name: str,
    value: str,
    message: str,
) -> None:
    values = asdict(assess())
    values[field_name] = value
    with pytest.raises(ValueError, match=message):
        OperatorApprovalExecutionAssessment(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field_name",
    [
        "decision_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    ],
)
def test_eligible_assessment_requires_non_empty_base_fields(
    field_name: str,
) -> None:
    values = asdict(assess())
    values[field_name] = ""
    with pytest.raises(ValueError, match=rf"^{field_name} must not be empty$"):
        OperatorApprovalExecutionAssessment(**values)  # type: ignore[arg-type]


def test_denied_invalid_decision_remains_serialization_safe() -> None:
    result = assess(decision=object())
    assert result.outcome == OUTCOME_DENIED
    assert result.reason_code == REASON_INVALID_DECISION
    assert result.decision_id == ""
    assert result.permission_reference == "permission-001"
    assert asdict(result)["lifecycle_reason_reference"] == "lifecycle-reason-001"
