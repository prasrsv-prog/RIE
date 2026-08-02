from dataclasses import FrozenInstanceError, MISSING, fields

import pytest

from rie.domain.operator_approval_decision import (
    ACTION_APPROVE,
    ACTION_REJECT,
    TARGET_TYPE_EVIDENCE,
    TARGET_TYPE_GOVERNED_ASSET_RECORD,
    OperatorApprovalDecision,
)
from rie.domain.operator_role_authority import (
    ALLOWED_OUTCOMES,
    ALLOWED_REASON_CODES,
    OUTCOME_ALLOW,
    OUTCOME_DENY,
    REASON_AMBIGUOUS_AUTHORITY_EVIDENCE,
    REASON_AUTHORIZED_EXACT_MATCH,
    REASON_INVALID_INPUT,
    REASON_NO_EXACT_OPERATOR_ROLE_BINDING,
    REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION,
    REASON_OPERATOR_REFERENCE_MISMATCH,
    REASON_ROLE_REFERENCE_MISMATCH,
    REASON_UNSUPPORTED_ACTION,
    REASON_UNSUPPORTED_TARGET_TYPE,
    OperatorRoleBinding,
    OperatorRolePermissionEvaluation,
    RoleActionTargetPermission,
    evaluate_operator_role_permission,
)


def make_decision(**overrides: object) -> OperatorApprovalDecision:
    values: dict[str, object] = {
        "decision_id": "decision-001",
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "action": ACTION_APPROVE,
        "reason_reference": "decision-reason-001",
        "audit_context_reference": "decision-audit-001",
    }
    values.update(overrides)
    return OperatorApprovalDecision(**values)  # type: ignore[arg-type]


def make_binding(**overrides: object) -> OperatorRoleBinding:
    values: dict[str, object] = {
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "binding_reference": "binding-001",
        "reason_reference": "binding-reason-001",
        "audit_context_reference": "binding-audit-001",
    }
    values.update(overrides)
    return OperatorRoleBinding(**values)  # type: ignore[arg-type]


def make_permission(**overrides: object) -> RoleActionTargetPermission:
    values: dict[str, object] = {
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "action": ACTION_APPROVE,
        "permission_reference": "permission-001",
        "reason_reference": "permission-reason-001",
        "audit_context_reference": "permission-audit-001",
    }
    values.update(overrides)
    return RoleActionTargetPermission(**values)  # type: ignore[arg-type]


def evaluate(
    *,
    decision: OperatorApprovalDecision | None = None,
    bindings: tuple[OperatorRoleBinding, ...] | object = None,
    permissions: tuple[RoleActionTargetPermission, ...] | object = None,
) -> OperatorRolePermissionEvaluation:
    if decision is None:
        decision = make_decision()
    if bindings is None:
        bindings = (make_binding(),)
    if permissions is None:
        permissions = (make_permission(),)
    return evaluate_operator_role_permission(
        decision,
        bindings,  # type: ignore[arg-type]
        permissions,  # type: ignore[arg-type]
        reason_reference="evaluation-reason-001",
        audit_context_reference="evaluation-audit-001",
    )


@pytest.mark.parametrize(
    ("model", "expected_names"),
    [
        (
            OperatorRoleBinding,
            (
                "operator_reference",
                "role_reference",
                "binding_reference",
                "reason_reference",
                "audit_context_reference",
            ),
        ),
        (
            RoleActionTargetPermission,
            (
                "role_reference",
                "target_type",
                "action",
                "permission_reference",
                "reason_reference",
                "audit_context_reference",
            ),
        ),
        (
            OperatorRolePermissionEvaluation,
            (
                "operator_reference",
                "role_reference",
                "target_type",
                "action",
                "outcome",
                "reason_code",
                "permission_reference",
                "reason_reference",
                "audit_context_reference",
            ),
        ),
    ],
)
def test_models_have_exact_required_fields(
    model: type[object],
    expected_names: tuple[str, ...],
) -> None:
    model_fields = fields(model)
    assert tuple(field.name for field in model_fields) == expected_names
    assert all(field.default is MISSING for field in model_fields)
    assert all(field.default_factory is MISSING for field in model_fields)


@pytest.mark.parametrize(
    "instance",
    [
        make_binding(),
        make_permission(),
        OperatorRolePermissionEvaluation(
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            target_type=TARGET_TYPE_EVIDENCE,
            action=ACTION_APPROVE,
            outcome=OUTCOME_ALLOW,
            reason_code=REASON_AUTHORIZED_EXACT_MATCH,
            permission_reference="permission-001",
            reason_reference="evaluation-reason-001",
            audit_context_reference="evaluation-audit-001",
        ),
    ],
)
def test_models_are_immutable(instance: object) -> None:
    with pytest.raises(FrozenInstanceError):
        instance.reason_reference = "changed"  # type: ignore[attr-defined]


def test_allowed_outcomes_are_exact() -> None:
    assert ALLOWED_OUTCOMES == {"ALLOW", "DENY"}


def test_allowed_reason_codes_are_exact() -> None:
    assert ALLOWED_REASON_CODES == {
        "AUTHORIZED_EXACT_MATCH",
        "INVALID_INPUT",
        "UNSUPPORTED_ACTION",
        "UNSUPPORTED_TARGET_TYPE",
        "OPERATOR_REFERENCE_MISMATCH",
        "ROLE_REFERENCE_MISMATCH",
        "NO_EXACT_OPERATOR_ROLE_BINDING",
        "NO_EXACT_ROLE_ACTION_TARGET_PERMISSION",
        "AMBIGUOUS_AUTHORITY_EVIDENCE",
    }


@pytest.mark.parametrize(
    ("factory", "field_name"),
    [
        (make_binding, "operator_reference"),
        (make_binding, "role_reference"),
        (make_binding, "binding_reference"),
        (make_binding, "reason_reference"),
        (make_binding, "audit_context_reference"),
        (make_permission, "role_reference"),
        (make_permission, "target_type"),
        (make_permission, "action"),
        (make_permission, "permission_reference"),
        (make_permission, "reason_reference"),
        (make_permission, "audit_context_reference"),
    ],
)
def test_evidence_fields_reject_non_text(
    factory: object,
    field_name: str,
) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        factory(**{field_name: 1})  # type: ignore[operator]


@pytest.mark.parametrize(
    ("factory", "field_name"),
    [
        (make_binding, "operator_reference"),
        (make_binding, "role_reference"),
        (make_binding, "binding_reference"),
        (make_binding, "reason_reference"),
        (make_binding, "audit_context_reference"),
        (make_permission, "role_reference"),
        (make_permission, "target_type"),
        (make_permission, "action"),
        (make_permission, "permission_reference"),
        (make_permission, "reason_reference"),
        (make_permission, "audit_context_reference"),
    ],
)
@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("", "must not be empty"),
        (" value", "must not contain leading or trailing whitespace"),
        ("value ", "must not contain leading or trailing whitespace"),
        ("value\nx", "must not contain control characters"),
        ("nilai-" + chr(233), "must contain ASCII text only"),
    ],
)
def test_evidence_fields_reject_invalid_text(
    factory: object,
    field_name: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        factory(**{field_name: value})  # type: ignore[operator]


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"target_type": "SOURCE"}, "target_type is not supported"),
        ({"action": "ACCEPT"}, "action is not supported"),
    ],
)
def test_permission_rejects_unsupported_vocabulary(
    overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=rf"^{message}$"):
        make_permission(**overrides)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"outcome": "PENDING"}, "outcome must be ALLOW or DENY"),
        ({"reason_code": "UNKNOWN"}, "reason_code is not supported"),
        (
            {
                "outcome": OUTCOME_DENY,
                "reason_code": REASON_AUTHORIZED_EXACT_MATCH,
            },
            "AUTHORIZED_EXACT_MATCH requires an ALLOW outcome",
        ),
        (
            {
                "outcome": OUTCOME_ALLOW,
                "reason_code": REASON_INVALID_INPUT,
            },
            "all non-authorized reason codes require a DENY outcome",
        ),
    ],
)
def test_evaluation_rejects_invalid_outcome_reason_pair(
    overrides: dict[str, object],
    message: str,
) -> None:
    values: dict[str, object] = {
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "action": ACTION_APPROVE,
        "outcome": OUTCOME_ALLOW,
        "reason_code": REASON_AUTHORIZED_EXACT_MATCH,
        "permission_reference": "permission-001",
        "reason_reference": "evaluation-reason-001",
        "audit_context_reference": "evaluation-audit-001",
    }
    values.update(overrides)
    with pytest.raises(ValueError, match=rf"^{message}$"):
        OperatorRolePermissionEvaluation(**values)  # type: ignore[arg-type]


def test_exact_binding_and_permission_allow_submission_only() -> None:
    result = evaluate()
    assert result == OperatorRolePermissionEvaluation(
        operator_reference="operator-001",
        role_reference="reviewer-role-001",
        target_type=TARGET_TYPE_EVIDENCE,
        action=ACTION_APPROVE,
        outcome=OUTCOME_ALLOW,
        reason_code=REASON_AUTHORIZED_EXACT_MATCH,
        permission_reference="permission-001",
        reason_reference="evaluation-reason-001",
        audit_context_reference="evaluation-audit-001",
    )


def test_reject_action_can_be_authorized_exactly() -> None:
    decision = make_decision(action=ACTION_REJECT)
    permission = make_permission(action=ACTION_REJECT)
    result = evaluate(decision=decision, permissions=(permission,))
    assert result.outcome == OUTCOME_ALLOW
    assert result.reason_code == REASON_AUTHORIZED_EXACT_MATCH
    assert result.permission_reference == "permission-001"


def test_evaluator_is_deterministic_for_identical_ordered_inputs() -> None:
    first = evaluate()
    second = evaluate()
    assert first == second


def test_evaluator_does_not_modify_decision_or_evidence() -> None:
    decision = make_decision()
    binding = make_binding()
    permission = make_permission()
    before = (decision, binding, permission)
    evaluate(
        decision=decision,
        bindings=(binding,),
        permissions=(permission,),
    )
    assert (decision, binding, permission) == before


@pytest.mark.parametrize(
    ("bindings", "reason_code"),
    [
        ((), REASON_NO_EXACT_OPERATOR_ROLE_BINDING),
        (
            (make_binding(role_reference="other-role"),),
            REASON_ROLE_REFERENCE_MISMATCH,
        ),
        (
            (make_binding(operator_reference="other-operator"),),
            REASON_OPERATOR_REFERENCE_MISMATCH,
        ),
        (
            (
                make_binding(
                    operator_reference="other-operator",
                    role_reference="other-role",
                ),
            ),
            REASON_NO_EXACT_OPERATOR_ROLE_BINDING,
        ),
    ],
)
def test_binding_failures_deny_by_default(
    bindings: tuple[OperatorRoleBinding, ...],
    reason_code: str,
) -> None:
    result = evaluate(bindings=bindings)
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == reason_code
    assert result.permission_reference is None


@pytest.mark.parametrize(
    "permissions",
    [
        (),
        (make_permission(action=ACTION_REJECT),),
        (
            make_permission(
                target_type=TARGET_TYPE_GOVERNED_ASSET_RECORD,
            ),
        ),
        (make_permission(role_reference="other-role"),),
    ],
)
def test_missing_exact_permission_denies_by_default(
    permissions: tuple[RoleActionTargetPermission, ...],
) -> None:
    result = evaluate(permissions=permissions)
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION
    assert result.permission_reference is None


def test_duplicate_exact_bindings_are_ambiguous() -> None:
    result = evaluate(bindings=(make_binding(), make_binding()))
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_AMBIGUOUS_AUTHORITY_EVIDENCE
    assert result.permission_reference is None


def test_duplicate_exact_permissions_are_ambiguous() -> None:
    result = evaluate(permissions=(make_permission(), make_permission()))
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_AMBIGUOUS_AUTHORITY_EVIDENCE
    assert result.permission_reference is None


@pytest.mark.parametrize(
    ("bindings", "permissions"),
    [
        ([], (make_permission(),)),
        ((make_binding(),), [make_permission()]),
        ((object(),), (make_permission(),)),
        ((make_binding(),), (object(),)),
    ],
)
def test_invalid_evidence_input_denies_with_invalid_input(
    bindings: object,
    permissions: object,
) -> None:
    result = evaluate(bindings=bindings, permissions=permissions)
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_INVALID_INPUT
    assert result.permission_reference is None


def test_non_decision_input_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=r"^decision must be an OperatorApprovalDecision$",
    ):
        evaluate_operator_role_permission(
            object(),  # type: ignore[arg-type]
            (),
            (),
            reason_reference="evaluation-reason-001",
            audit_context_reference="evaluation-audit-001",
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("reason_reference", "", "must not be empty"),
        (
            "reason_reference",
            " reason",
            "must not contain leading or trailing whitespace",
        ),
        (
            "audit_context_reference",
            "audit\ncontext",
            "must not contain control characters",
        ),
        (
            "audit_context_reference",
            "audit-" + chr(233),
            "must contain ASCII text only",
        ),
    ],
)
def test_evaluation_context_references_fail_closed(
    field_name: str,
    value: str,
    message: str,
) -> None:
    kwargs = {
        "reason_reference": "evaluation-reason-001",
        "audit_context_reference": "evaluation-audit-001",
    }
    kwargs[field_name] = value
    with pytest.raises(ValueError, match=message):
        evaluate_operator_role_permission(
            make_decision(),
            (make_binding(),),
            (make_permission(),),
            **kwargs,
        )


def test_mutated_decision_with_unsupported_action_denies() -> None:
    decision = make_decision()
    object.__setattr__(decision, "action", "ACCEPT")
    result = evaluate(decision=decision)
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_UNSUPPORTED_ACTION
    assert result.permission_reference is None


def test_mutated_decision_with_unsupported_target_type_denies() -> None:
    decision = make_decision()
    object.__setattr__(decision, "target_type", "SOURCE")
    result = evaluate(decision=decision)
    assert result.outcome == OUTCOME_DENY
    assert result.reason_code == REASON_UNSUPPORTED_TARGET_TYPE
    assert result.permission_reference is None


def test_allow_does_not_mutate_or_promote_target() -> None:
    result = evaluate()
    assert result.outcome == OUTCOME_ALLOW
    assert not hasattr(result, "target_reference")
    assert not hasattr(result, "executed")
    assert not hasattr(result, "persisted")


def test_allow_preserves_exact_permission_reference_without_substitution() -> None:
    permission = make_permission(permission_reference="permission-exact-777")
    result = evaluate(permissions=(permission,))
    assert result.outcome == OUTCOME_ALLOW
    assert result.permission_reference == "permission-exact-777"


@pytest.mark.parametrize(
    "permissions",
    [
        (),
        (make_permission(action=ACTION_REJECT),),
        (
            make_permission(
                target_type=TARGET_TYPE_GOVERNED_ASSET_RECORD,
            ),
        ),
        (make_permission(role_reference="other-role"),),
    ],
)
def test_no_match_permission_denies_without_reference(
    permissions: tuple[RoleActionTargetPermission, ...],
) -> None:
    result = evaluate(permissions=permissions)
    assert result.outcome == OUTCOME_DENY
    assert result.permission_reference is None



def test_direct_non_authorized_allow_without_permission_reference_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=r"^ALLOW requires a permission reference$",
    ):
        OperatorRolePermissionEvaluation(
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            target_type=TARGET_TYPE_EVIDENCE,
            action=ACTION_APPROVE,
            outcome=OUTCOME_ALLOW,
            reason_code=REASON_INVALID_INPUT,
            permission_reference=None,
            reason_reference="evaluation-reason-001",
            audit_context_reference="evaluation-audit-001",
        )

def test_direct_allow_without_permission_reference_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=r"^AUTHORIZED_EXACT_MATCH requires a permission reference$",
    ):
        OperatorRolePermissionEvaluation(
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            target_type=TARGET_TYPE_EVIDENCE,
            action=ACTION_APPROVE,
            outcome=OUTCOME_ALLOW,
            reason_code=REASON_AUTHORIZED_EXACT_MATCH,
            permission_reference=None,
            reason_reference="evaluation-reason-001",
            audit_context_reference="evaluation-audit-001",
        )


@pytest.mark.parametrize(
    ("permission_reference", "error_type", "message"),
    [
        (1, TypeError, "permission_reference must be text"),
        ("", ValueError, "permission_reference must not be empty"),
        (
            " permission-001",
            ValueError,
            "permission_reference must not contain leading or trailing whitespace",
        ),
        (
            "permission-001 ",
            ValueError,
            "permission_reference must not contain leading or trailing whitespace",
        ),
        (
            "permission\n001",
            ValueError,
            "permission_reference must not contain control characters",
        ),
        (
            "permission-" + chr(233),
            ValueError,
            "permission_reference must contain ASCII text only",
        ),
    ],
)
def test_evaluation_rejects_invalid_permission_reference_text(
    permission_reference: object,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=rf"^{message}$"):
        OperatorRolePermissionEvaluation(
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            target_type=TARGET_TYPE_EVIDENCE,
            action=ACTION_APPROVE,
            outcome=OUTCOME_ALLOW,
            reason_code=REASON_AUTHORIZED_EXACT_MATCH,
            permission_reference=permission_reference,  # type: ignore[arg-type]
            reason_reference="evaluation-reason-001",
            audit_context_reference="evaluation-audit-001",
        )


def test_deny_with_permission_reference_remains_denied() -> None:
    result = OperatorRolePermissionEvaluation(
        operator_reference="operator-001",
        role_reference="reviewer-role-001",
        target_type=TARGET_TYPE_EVIDENCE,
        action=ACTION_APPROVE,
        outcome=OUTCOME_DENY,
        reason_code=REASON_NO_EXACT_ROLE_ACTION_TARGET_PERMISSION,
        permission_reference="permission-001",
        reason_reference="evaluation-reason-001",
        audit_context_reference="evaluation-audit-001",
    )
    assert result.outcome == OUTCOME_DENY
    assert result.permission_reference == "permission-001"


def test_permission_reference_is_immutable() -> None:
    result = evaluate()
    with pytest.raises(FrozenInstanceError):
        result.permission_reference = "changed"  # type: ignore[misc]
