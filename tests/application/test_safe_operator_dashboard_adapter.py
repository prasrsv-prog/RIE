from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path

import pytest

import rie.application.safe_operator_dashboard_adapter as adapter_module
from rie.application.operator_approval_application_service import (
    CONFLICT_CLEAR,
    IDEMPOTENCY_NEW,
    LIFECYCLE_ELIGIBLE,
    OUTCOME_DENIED,
    OUTCOME_ELIGIBLE,
    PROVENANCE_VERIFIED,
    REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION,
    RIGHTS_CLEARED,
    OperatorApprovalExecutionAssessment,
    TargetApprovalContext,
    assess_operator_approval_execution,
)
from rie.application.safe_operator_dashboard_adapter import (
    ALLOWED_DASHBOARD_ERROR_CODES,
    ALLOWED_DASHBOARD_STATUSES,
    ERROR_APPROVAL_ASSESSMENT_DENIED,
    ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID,
    ERROR_AUDIT_HISTORY_INVALID,
    ERROR_DEPENDENCY_FAILURE,
    ERROR_INTERNAL_FAILURE,
    ERROR_REQUEST_INVALID,
    ERROR_ROLE_AUTHORITY_DENIED,
    ERROR_ROLE_AUTHORITY_RESULT_INVALID,
    STATUS_DENIED,
    STATUS_INVALID,
    STATUS_READY,
    SafeOperatorDashboardProjection,
    SafeOperatorDashboardRequest,
    SafeOperatorDashboardResult,
    build_safe_operator_dashboard,
)
from rie.domain.operator_approval_audit_history import (
    OperatorApprovalAuditHistory,
    OperatorApprovalAuditRecord,
)
from rie.domain.operator_approval_decision import (
    ACTION_APPROVE,
    ACTION_REJECT,
    TARGET_TYPE_EVIDENCE,
    OperatorApprovalDecision,
)
from rie.domain.operator_role_authority import (
    OUTCOME_ALLOW,
    OUTCOME_DENY,
    REASON_AUTHORIZED_EXACT_MATCH,
    REASON_NO_EXACT_OPERATOR_ROLE_BINDING,
    OperatorRoleBinding,
    OperatorRolePermissionEvaluation,
    RoleActionTargetPermission,
    evaluate_operator_role_permission,
)


def make_request(**overrides: object) -> SafeOperatorDashboardRequest:
    values: dict[str, object] = {
        "request_id": "dashboard-request-001",
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "target_reference": "evidence-001",
        "action": ACTION_APPROVE,
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
        "audit_limit": 10,
    }
    values.update(overrides)
    return SafeOperatorDashboardRequest(**values)  # type: ignore[arg-type]


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


def make_binding(**overrides: object) -> OperatorRoleBinding:
    values: dict[str, object] = {
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "binding_reference": "binding-001",
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return OperatorRoleBinding(**values)  # type: ignore[arg-type]


def make_permission(**overrides: object) -> RoleActionTargetPermission:
    values: dict[str, object] = {
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "action": ACTION_APPROVE,
        "permission_reference": "permission-001",
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return RoleActionTargetPermission(**values)  # type: ignore[arg-type]


def make_context(**overrides: object) -> TargetApprovalContext:
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


def make_record(index: int, **overrides: object) -> OperatorApprovalAuditRecord:
    values: dict[str, object] = {
        "audit_record_id": f"audit-record-{index:03d}",
        "decision_id": f"decision-{index:03d}",
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
        "audit_context_reference": f"audit-context-record-{index:03d}",
        "lifecycle_reason_reference": "lifecycle-reason-001",
        "provenance_reference": "provenance-001",
        "rights_reference": "rights-001",
        "idempotency_reference": "idempotency-001",
        "conflict_reference": "conflict-001",
    }
    values.update(overrides)
    return OperatorApprovalAuditRecord(**values)  # type: ignore[arg-type]


def make_history(
    records: tuple[OperatorApprovalAuditRecord, ...] = (),
) -> OperatorApprovalAuditHistory:
    return OperatorApprovalAuditHistory(records=records)


def build(**overrides: object) -> SafeOperatorDashboardResult:
    values: dict[str, object] = {
        "request": make_request(),
        "decision": make_decision(),
        "operator_role_bindings": (make_binding(),),
        "role_action_target_permissions": (make_permission(),),
        "target_approval_context": make_context(),
        "audit_history": make_history(),
    }
    values.update(overrides)
    return build_safe_operator_dashboard(**values)  # type: ignore[arg-type]


def make_allow_evaluation(
    **overrides: object,
) -> OperatorRolePermissionEvaluation:
    values: dict[str, object] = {
        "operator_reference": "operator-001",
        "role_reference": "reviewer-role-001",
        "target_type": TARGET_TYPE_EVIDENCE,
        "action": ACTION_APPROVE,
        "outcome": OUTCOME_ALLOW,
        "reason_code": REASON_AUTHORIZED_EXACT_MATCH,
        "permission_reference": "permission-001",
        "reason_reference": "reason-001",
        "audit_context_reference": "audit-context-001",
    }
    values.update(overrides)
    return OperatorRolePermissionEvaluation(**values)  # type: ignore[arg-type]


def make_eligible_assessment(
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
        "reason_code": (
            REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ),
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


def test_models_have_exact_required_fields() -> None:
    assert tuple(field.name for field in fields(SafeOperatorDashboardRequest)) == (
        "request_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
        "audit_limit",
    )
    assert tuple(
        field.name for field in fields(SafeOperatorDashboardProjection)
    ) == (
        "request_id",
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
        "matching_audit_records",
    )
    assert tuple(field.name for field in fields(SafeOperatorDashboardResult)) == (
        "status",
        "projection",
        "error_code",
    )
    for model in (
        SafeOperatorDashboardRequest,
        SafeOperatorDashboardProjection,
        SafeOperatorDashboardResult,
    ):
        assert all(field.default is MISSING for field in fields(model))
        assert all(field.default_factory is MISSING for field in fields(model))


def test_exact_status_and_error_vocabularies() -> None:
    assert ALLOWED_DASHBOARD_STATUSES == {"READY", "DENIED", "INVALID"}
    assert ALLOWED_DASHBOARD_ERROR_CODES == {
        "REQUEST_INVALID",
        "ROLE_AUTHORITY_DENIED",
        "ROLE_AUTHORITY_RESULT_INVALID",
        "APPROVAL_ASSESSMENT_DENIED",
        "APPROVAL_ASSESSMENT_RESULT_INVALID",
        "AUDIT_HISTORY_INVALID",
        "DEPENDENCY_FAILURE",
        "INTERNAL_FAILURE",
    }


@pytest.mark.parametrize(
    "instance",
    [
        make_request(),
        SafeOperatorDashboardProjection(
            request_id="dashboard-request-001",
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            permission_reference="permission-001",
            target_type=TARGET_TYPE_EVIDENCE,
            target_reference="evidence-001",
            action=ACTION_APPROVE,
            assessment_outcome=OUTCOME_ELIGIBLE,
            assessment_reason_code=(
                REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
            ),
            reason_reference="reason-001",
            audit_context_reference="audit-context-001",
            matching_audit_records=(),
        ),
        SafeOperatorDashboardResult(
            status=STATUS_INVALID,
            projection=None,
            error_code=ERROR_REQUEST_INVALID,
        ),
    ],
)
def test_models_are_immutable(instance: object) -> None:
    with pytest.raises(FrozenInstanceError):
        instance.status = STATUS_READY  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "field_name",
    (
        "request_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    ),
)
def test_request_rejects_non_text(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_request(**{field_name: 1})


@pytest.mark.parametrize(
    "field_name",
    (
        "request_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    ),
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
def test_request_rejects_invalid_text(
    field_name: str,
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        make_request(**{field_name: value})


@pytest.mark.parametrize("value", [True, False, 1.5, "1", None])
def test_request_rejects_non_integer_audit_limit(value: object) -> None:
    with pytest.raises(TypeError, match="audit_limit must be an integer"):
        make_request(audit_limit=value)


@pytest.mark.parametrize("value", [0, -1, 101, 1000])
def test_request_rejects_out_of_range_audit_limit(value: int) -> None:
    with pytest.raises(
        ValueError,
        match="audit_limit must be from 1 through 100",
    ):
        make_request(audit_limit=value)


@pytest.mark.parametrize("value", [1, 100])
def test_request_accepts_audit_limit_boundaries(value: int) -> None:
    assert make_request(audit_limit=value).audit_limit == value


@pytest.mark.parametrize("candidate", [None, object(), "request"])
def test_invalid_request_maps_fail_closed(candidate: object) -> None:
    result = build(request=candidate)
    assert result == SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=ERROR_REQUEST_INVALID,
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    ),
)
def test_decision_request_disagreement_is_invalid(field_name: str) -> None:
    replacement = (
        ACTION_REJECT
        if field_name == "action"
        else (
            "KNOWLEDGE"
            if field_name == "target_type"
            else f"different-{field_name}"
        )
    )
    result = build(decision=make_decision(**{field_name: replacement}))
    assert result.status == STATUS_INVALID
    assert result.projection is None
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID


def test_exact_role_authority_delegation() -> None:
    calls: list[tuple[object, ...]] = []
    decision = make_decision()
    bindings = (make_binding(),)
    permissions = (make_permission(),)

    def evaluator(*args: object, **kwargs: object) -> object:
        calls.append((*args, kwargs))
        return make_allow_evaluation()

    result = build(
        decision=decision,
        operator_role_bindings=bindings,
        role_action_target_permissions=permissions,
        role_authority_evaluator=evaluator,
        approval_assessor=lambda *args: make_eligible_assessment(),
    )
    assert result.status == STATUS_READY
    assert calls == [
        (
            decision,
            bindings,
            permissions,
            {
                "reason_reference": "reason-001",
                "audit_context_reference": "audit-context-001",
            },
        )
    ]


def test_role_authority_deny_maps_without_assessor_execution() -> None:
    assessor_called = False

    def denied_evaluator(*args: object, **kwargs: object) -> object:
        return OperatorRolePermissionEvaluation(
            operator_reference="operator-001",
            role_reference="reviewer-role-001",
            target_type=TARGET_TYPE_EVIDENCE,
            action=ACTION_APPROVE,
            outcome=OUTCOME_DENY,
            reason_code=REASON_NO_EXACT_OPERATOR_ROLE_BINDING,
            permission_reference=None,
            reason_reference="reason-001",
            audit_context_reference="audit-context-001",
        )

    def assessor(*args: object, **kwargs: object) -> object:
        nonlocal assessor_called
        assessor_called = True
        return make_eligible_assessment()

    result = build(
        role_authority_evaluator=denied_evaluator,
        approval_assessor=assessor,
    )
    assert result == SafeOperatorDashboardResult(
        status=STATUS_DENIED,
        projection=None,
        error_code=ERROR_ROLE_AUTHORITY_DENIED,
    )
    assert assessor_called is False


@pytest.mark.parametrize(
    "evaluation",
    [
        None,
        object(),
        "ALLOW",
    ],
)
def test_malformed_role_authority_type_is_invalid(evaluation: object) -> None:
    result = build(role_authority_evaluator=lambda *args, **kwargs: evaluation)
    assert result.error_code == ERROR_ROLE_AUTHORITY_RESULT_INVALID
    assert result.status == STATUS_INVALID


@pytest.mark.parametrize(
    "field_name",
    (
        "operator_reference",
        "role_reference",
        "target_type",
        "action",
        "reason_reference",
        "audit_context_reference",
    ),
)
def test_role_authority_agreement_mismatch_is_invalid(
    field_name: str,
) -> None:
    replacement = (
        ACTION_REJECT
        if field_name == "action"
        else (
            "KNOWLEDGE"
            if field_name == "target_type"
            else f"different-{field_name}"
        )
    )
    evaluation = make_allow_evaluation(**{field_name: replacement})
    result = build(
        role_authority_evaluator=lambda *args, **kwargs: evaluation,
    )
    assert result.status == STATUS_INVALID
    assert result.error_code == ERROR_ROLE_AUTHORITY_RESULT_INVALID


def test_exact_approval_assessment_delegation() -> None:
    calls: list[tuple[object, ...]] = []
    decision = make_decision()
    context = make_context()
    evaluation = make_allow_evaluation()

    def assessor(*args: object) -> object:
        calls.append(args)
        return make_eligible_assessment()

    result = build(
        decision=decision,
        target_approval_context=context,
        role_authority_evaluator=lambda *args, **kwargs: evaluation,
        approval_assessor=assessor,
    )
    assert result.status == STATUS_READY
    assert calls == [(decision, evaluation, context)]


def test_eligible_projection_copies_exact_accepted_facts() -> None:
    record = make_record(1)
    result = build(audit_history=make_history((record,)))
    assert result.status == STATUS_READY
    assert result.error_code is None
    assert result.projection == SafeOperatorDashboardProjection(
        request_id="dashboard-request-001",
        operator_reference="operator-001",
        role_reference="reviewer-role-001",
        permission_reference="permission-001",
        target_type=TARGET_TYPE_EVIDENCE,
        target_reference="evidence-001",
        action=ACTION_APPROVE,
        assessment_outcome=OUTCOME_ELIGIBLE,
        assessment_reason_code=(
            REASON_ELIGIBLE_FOR_SEPARATELY_AUTHORIZED_EXECUTION
        ),
        reason_reference="reason-001",
        audit_context_reference="audit-context-001",
        matching_audit_records=(record,),
    )


def test_denied_assessment_maps_to_denied_projection() -> None:
    denied = assess_operator_approval_execution(
        make_decision(),
        make_allow_evaluation(),
        make_context(lifecycle_eligibility="BLOCKED"),
    )
    assert denied.outcome == OUTCOME_DENIED
    result = build(
        approval_assessor=lambda *args: denied,
    )
    assert result.status == STATUS_DENIED
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_DENIED
    assert result.projection is not None
    assert result.projection.assessment_outcome == OUTCOME_DENIED
    assert result.projection.assessment_reason_code == denied.reason_code


@pytest.mark.parametrize("assessment", [None, object(), "ELIGIBLE"])
def test_malformed_assessment_type_is_invalid(assessment: object) -> None:
    result = build(approval_assessor=lambda *args: assessment)
    assert result.status == STATUS_INVALID
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID


@pytest.mark.parametrize(
    "field_name",
    (
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    ),
)
def test_assessment_agreement_mismatch_is_invalid(field_name: str) -> None:
    replacement = (
        ACTION_REJECT
        if field_name == "action"
        else (
            "KNOWLEDGE"
            if field_name == "target_type"
            else f"different-{field_name}"
        )
    )
    assessment = make_eligible_assessment(**{field_name: replacement})
    result = build(approval_assessor=lambda *args: assessment)
    assert result.status == STATUS_INVALID
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID


def test_assessment_decision_identity_mismatch_is_invalid() -> None:
    assessment = make_eligible_assessment(decision_id="decision-other")
    result = build(approval_assessor=lambda *args: assessment)
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID


def test_permission_reference_disagreement_is_invalid() -> None:
    assessment = make_eligible_assessment(
        permission_reference="permission-other"
    )
    result = build(approval_assessor=lambda *args: assessment)
    assert result.status == STATUS_INVALID
    assert result.projection is None
    assert result.error_code == ERROR_APPROVAL_ASSESSMENT_RESULT_INVALID


@pytest.mark.parametrize("history", [None, object(), ()])
def test_invalid_audit_history_maps_fail_closed(history: object) -> None:
    result = build(audit_history=history)
    assert result == SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=ERROR_AUDIT_HISTORY_INVALID,
    )


def test_audit_limit_one_selects_newest_matching_record() -> None:
    records = tuple(make_record(index) for index in range(1, 4))
    result = build(
        request=make_request(audit_limit=1),
        audit_history=make_history(records),
    )
    assert result.projection is not None
    assert result.projection.matching_audit_records == (records[-1],)


def test_audit_limit_one_hundred_preserves_matching_append_order() -> None:
    records = tuple(make_record(index) for index in range(1, 101))
    result = build(
        request=make_request(audit_limit=100),
        audit_history=make_history(records),
    )
    assert result.projection is not None
    assert result.projection.matching_audit_records == records


def test_exact_matching_record_filtering_and_append_order() -> None:
    records = (
        make_record(1),
        make_record(2, operator_reference="operator-other"),
        make_record(3),
        make_record(4, role_reference="role-other"),
        make_record(5),
        make_record(6, target_type="KNOWLEDGE"),
        make_record(7),
        make_record(8, target_reference="evidence-other"),
        make_record(9),
        make_record(10, action=ACTION_REJECT),
        make_record(11),
    )
    result = build(audit_history=make_history(records))
    assert result.projection is not None
    assert result.projection.matching_audit_records == (
        records[0],
        records[2],
        records[4],
        records[6],
        records[8],
        records[10],
    )


def test_audit_history_is_not_mutated() -> None:
    records = tuple(make_record(index) for index in range(1, 4))
    history = make_history(records)
    before = history.records
    result = build(audit_history=history)
    assert result.status == STATUS_READY
    assert history.records is before
    assert history.records == records


@pytest.mark.parametrize(
    "dependency_name",
    ["role_authority_evaluator", "approval_assessor"],
)
def test_non_callable_dependency_maps_failure(dependency_name: str) -> None:
    result = build(**{dependency_name: None})
    assert result.status == STATUS_INVALID
    assert result.error_code == ERROR_DEPENDENCY_FAILURE


def test_role_authority_exception_maps_dependency_failure() -> None:
    def failing(*args: object, **kwargs: object) -> object:
        raise RuntimeError("secret role failure")

    result = build(role_authority_evaluator=failing)
    assert result == SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=ERROR_DEPENDENCY_FAILURE,
    )


def test_assessor_exception_maps_dependency_failure() -> None:
    def failing(*args: object, **kwargs: object) -> object:
        raise RuntimeError("secret assessment failure")

    result = build(approval_assessor=failing)
    assert result == SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=ERROR_DEPENDENCY_FAILURE,
    )


def test_unexpected_internal_exception_maps_internal_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing(*args: object, **kwargs: object) -> object:
        raise RuntimeError("internal secret")

    monkeypatch.setattr(adapter_module, "_matching_audit_records", failing)
    result = build()
    assert result == SafeOperatorDashboardResult(
        status=STATUS_INVALID,
        projection=None,
        error_code=ERROR_INTERNAL_FAILURE,
    )


def test_equivalent_inputs_produce_equal_results() -> None:
    assert build() == build()


def test_input_values_are_not_mutated() -> None:
    request = make_request()
    decision = make_decision()
    bindings = (make_binding(),)
    permissions = (make_permission(),)
    context = make_context()
    history = make_history((make_record(1),))
    snapshots = (
        request,
        decision,
        bindings,
        permissions,
        context,
        history,
    )
    result = build(
        request=request,
        decision=decision,
        operator_role_bindings=bindings,
        role_action_target_permissions=permissions,
        target_approval_context=context,
        audit_history=history,
    )
    assert result.status == STATUS_READY
    assert snapshots == (
        request,
        decision,
        bindings,
        permissions,
        context,
        history,
    )


def test_adapter_uses_accepted_default_dependencies() -> None:
    assert (
        build_safe_operator_dashboard.__kwdefaults__[
            "role_authority_evaluator"
        ]
        is evaluate_operator_role_permission
    )
    assert (
        build_safe_operator_dashboard.__kwdefaults__["approval_assessor"]
        is assess_operator_approval_execution
    )


def test_source_has_no_io_network_clock_randomness_or_persistence_imports() -> None:
    source_path = Path(adapter_module.__file__)
    assert source_path.as_posix().endswith(
        "src/rie/application/safe_operator_dashboard_adapter.py"
    )
    tree = ast.parse(source_path.read_text(encoding="ascii"))
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported_roots.isdisjoint(
        {
            "asyncio",
            "datetime",
            "http",
            "os",
            "pathlib",
            "random",
            "requests",
            "secrets",
            "socket",
            "sqlite3",
            "subprocess",
            "time",
            "urllib",
            "uuid",
        }
    )


def test_source_contains_no_target_mutation_or_automatic_promotion() -> None:
    source = Path(adapter_module.__file__).read_text(encoding="ascii")
    forbidden_markers = (
        "execute_approval",
        "mutate_target",
        "promote_target",
        "automatic_promotion",
        "repository.save",
        "storage.write",
    )
    assert all(marker not in source for marker in forbidden_markers)
