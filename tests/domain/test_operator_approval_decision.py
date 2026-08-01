from dataclasses import FrozenInstanceError, MISSING, fields

import pytest

from rie.domain.operator_approval_decision import (
    ACTION_APPROVE,
    ACTION_REJECT,
    ALLOWED_ACTIONS,
    ALLOWED_TARGET_TYPES,
    TARGET_TYPE_EVIDENCE,
    TARGET_TYPE_GOVERNED_ASSET_RECORD,
    TARGET_TYPE_INGESTION_JOB,
    TARGET_TYPE_KNOWLEDGE,
    TARGET_TYPE_KNOWLEDGE_CONFLICT,
    TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY,
    TARGET_TYPE_PROMPT_CANDIDATE,
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


def test_contract_has_exactly_eight_required_fields() -> None:
    model_fields = fields(OperatorApprovalDecision)

    assert tuple(field.name for field in model_fields) == (
        "decision_id",
        "operator_reference",
        "role_reference",
        "target_type",
        "target_reference",
        "action",
        "reason_reference",
        "audit_context_reference",
    )
    assert all(field.default is MISSING for field in model_fields)
    assert all(field.default_factory is MISSING for field in model_fields)


def test_allowed_actions_are_exact() -> None:
    assert ALLOWED_ACTIONS == {"APPROVE", "REJECT"}


def test_allowed_target_types_are_exact() -> None:
    assert ALLOWED_TARGET_TYPES == {
        "OFFICIAL_SOURCE_REGISTRY_ENTRY",
        "INGESTION_JOB",
        "EVIDENCE",
        "KNOWLEDGE",
        "KNOWLEDGE_CONFLICT",
        "PROMPT_CANDIDATE",
        "GOVERNED_ASSET_RECORD",
    }


@pytest.mark.parametrize(
    "target_type",
    [
        TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY,
        TARGET_TYPE_INGESTION_JOB,
        TARGET_TYPE_EVIDENCE,
        TARGET_TYPE_KNOWLEDGE,
        TARGET_TYPE_KNOWLEDGE_CONFLICT,
        TARGET_TYPE_PROMPT_CANDIDATE,
        TARGET_TYPE_GOVERNED_ASSET_RECORD,
    ],
)
@pytest.mark.parametrize("action", [ACTION_APPROVE, ACTION_REJECT])
def test_each_exact_target_type_accepts_each_exact_action(
    target_type: str,
    action: str,
) -> None:
    decision = make_decision(target_type=target_type, action=action)

    assert decision.target_type == target_type
    assert decision.action == action


def test_decision_is_immutable() -> None:
    decision = make_decision()

    with pytest.raises(FrozenInstanceError):
        decision.action = ACTION_REJECT  # type: ignore[misc]


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
def test_required_fields_reject_non_text(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_decision(**{field_name: 1})


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
@pytest.mark.parametrize("value", ["", "   "])
def test_required_fields_reject_empty_text(
    field_name: str,
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must not be empty$",
    ):
        make_decision(**{field_name: value})


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
def test_required_fields_reject_non_ascii_text(field_name: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must contain ASCII text only$",
    ):
        make_decision(**{field_name: "nilai-" + chr(233)})


@pytest.mark.parametrize(
    "target_type",
    [
        "SOURCE",
        "ASSET",
        "evidence",
        "UNKNOWN",
    ],
)
def test_unsupported_target_type_fails_closed(target_type: str) -> None:
    with pytest.raises(ValueError, match=r"^target_type must be one of "):
        make_decision(target_type=target_type)


@pytest.mark.parametrize(
    "action",
    [
        "ACCEPT",
        "DENY",
        "approve",
        "PENDING",
    ],
)
def test_unsupported_action_fails_closed(action: str) -> None:
    with pytest.raises(ValueError, match=r"^action must be APPROVE or REJECT$"):
        make_decision(action=action)


def test_approval_and_rejection_both_require_reason_reference() -> None:
    for action in (ACTION_APPROVE, ACTION_REJECT):
        with pytest.raises(
            ValueError,
            match=r"^reason_reference must not be empty$",
        ):
            make_decision(action=action, reason_reference="")


def test_approval_and_rejection_both_require_audit_context_reference() -> None:
    for action in (ACTION_APPROVE, ACTION_REJECT):
        with pytest.raises(
            ValueError,
            match=r"^audit_context_reference must not be empty$",
        ):
            make_decision(
                action=action,
                audit_context_reference="",
            )
