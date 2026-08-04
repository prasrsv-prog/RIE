from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rie.domain.creative_workflow_event import ALLOWED_WORKFLOW_STATES
from rie.domain.evaluate_governed_creative_workflow_transition import (
    ALLOWED_TRANSITION_DISPOSITIONS,
    TRANSITION_DISPOSITION_ACCEPTED,
    TRANSITION_DISPOSITION_REJECTED,
    TRANSITION_DISPOSITION_SAFE_STOP,
    GovernedCreativeWorkflowTransitionEvaluation,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.governed_creative_workflow_result import (
    GovernedCreativeWorkflowResult,
)

PROJECT = "project:alpha"
CAMPAIGN = (PROJECT, "campaign:one")
BRIEF = "brief:approved:001"
INSTRUCTION = ("instruction:approved:001", "APPROVED_INSTRUCTION")
ACTOR = ("ACTOR", "actor:operator:001")
CONTRACT = ("GATE_18_CREATIVE_WORKFLOW", "1.0")
FINGERPRINT = "1" * 64
OTHER_FINGERPRINT = "2" * 64
HANDOFF = (PROJECT, CAMPAIGN[1], "handoff:001")
CANDIDATE = (PROJECT, CAMPAIGN[1], "candidate:001")
OPERATOR_DECISION = (
    PROJECT,
    CAMPAIGN[1],
    "operator-decision:accepted:001",
)
GOVERNED_ASSET = (
    PROJECT,
    CAMPAIGN[1],
    "governed-asset:accepted:001",
)
RECOVERY_EVENT = (PROJECT, CAMPAIGN[1], "a" * 64)
TIMESTAMP = datetime(2026, 8, 4, 13, 30, tzinfo=timezone.utc)

VALID_TRANSITIONS = (
    ("REQUESTED", "INPUTS_VALIDATED"),
    ("INPUTS_VALIDATED", "INSTRUCTION_READY"),
    ("INSTRUCTION_READY", "EXTERNAL_HANDOFF_RECORDED"),
    ("INSTRUCTION_READY", "CANDIDATE_PENDING"),
    ("EXTERNAL_HANDOFF_RECORDED", "CANDIDATE_PENDING"),
    ("CANDIDATE_PENDING", "CANDIDATE_ADMITTED"),
    ("CANDIDATE_ADMITTED", "OPERATOR_REVIEW_PENDING"),
    ("OPERATOR_REVIEW_PENDING", "OPERATOR_DECISION_RECORDED"),
    ("OPERATOR_DECISION_RECORDED", "ASSET_ADMISSION_PENDING"),
    ("ASSET_ADMISSION_PENDING", "GOVERNED_ASSET_REFERENCE_RECORDED"),
    ("GOVERNED_ASSET_REFERENCE_RECORDED", "COMPLETED"),
    ("OPERATOR_REVIEW_PENDING", "REJECTED"),
    ("ASSET_ADMISSION_PENDING", "REJECTED"),
)

VALID_TARGETS = {
    "REQUESTED": {"INPUTS_VALIDATED", "SAFE_STOP"},
    "INPUTS_VALIDATED": {"INSTRUCTION_READY", "SAFE_STOP"},
    "INSTRUCTION_READY": {
        "EXTERNAL_HANDOFF_RECORDED",
        "CANDIDATE_PENDING",
        "SAFE_STOP",
    },
    "EXTERNAL_HANDOFF_RECORDED": {"CANDIDATE_PENDING", "SAFE_STOP"},
    "CANDIDATE_PENDING": {"CANDIDATE_ADMITTED", "SAFE_STOP"},
    "CANDIDATE_ADMITTED": {"OPERATOR_REVIEW_PENDING", "SAFE_STOP"},
    "OPERATOR_REVIEW_PENDING": {
        "OPERATOR_DECISION_RECORDED",
        "REJECTED",
        "SAFE_STOP",
    },
    "OPERATOR_DECISION_RECORDED": {
        "ASSET_ADMISSION_PENDING",
        "SAFE_STOP",
    },
    "ASSET_ADMISSION_PENDING": {
        "GOVERNED_ASSET_REFERENCE_RECORDED",
        "REJECTED",
        "SAFE_STOP",
    },
    "GOVERNED_ASSET_REFERENCE_RECORDED": {"COMPLETED", "SAFE_STOP"},
    "COMPLETED": set(),
    "REJECTED": set(),
    "SAFE_STOP": set(),
}

INVALID_TRANSITIONS = tuple(
    (prior, requested)
    for prior in sorted(ALLOWED_WORKFLOW_STATES)
    for requested in sorted(ALLOWED_WORKFLOW_STATES)
    if requested not in VALID_TARGETS[prior]
)


def transition_overrides(
    current_state: str,
    requested_state: str,
) -> dict[str, object]:
    values: dict[str, object] = {}
    if (
        current_state == "INSTRUCTION_READY"
        and requested_state == "EXTERNAL_HANDOFF_RECORDED"
    ):
        values["manual_external_tool_handoff_reference"] = HANDOFF
    if current_state == "EXTERNAL_HANDOFF_RECORDED":
        values["manual_external_tool_handoff_reference"] = HANDOFF
    if current_state in {
        "CANDIDATE_ADMITTED",
        "OPERATOR_REVIEW_PENDING",
        "OPERATOR_DECISION_RECORDED",
        "ASSET_ADMISSION_PENDING",
        "GOVERNED_ASSET_REFERENCE_RECORDED",
    }:
        values["creative_result_candidate_reference"] = CANDIDATE
    if current_state in {
        "OPERATOR_DECISION_RECORDED",
        "ASSET_ADMISSION_PENDING",
        "GOVERNED_ASSET_REFERENCE_RECORDED",
    }:
        values["accepted_operator_decision_reference"] = OPERATOR_DECISION
    if current_state == "GOVERNED_ASSET_REFERENCE_RECORDED":
        values["accepted_governed_asset_reference"] = GOVERNED_ASSET
    if requested_state in {"CANDIDATE_ADMITTED", "OPERATOR_REVIEW_PENDING"}:
        values["creative_result_candidate_reference"] = CANDIDATE
    if requested_state in {
        "OPERATOR_DECISION_RECORDED",
        "ASSET_ADMISSION_PENDING",
    }:
        values["creative_result_candidate_reference"] = CANDIDATE
        values["accepted_operator_decision_reference"] = OPERATOR_DECISION
    if requested_state == "GOVERNED_ASSET_REFERENCE_RECORDED":
        values["creative_result_candidate_reference"] = CANDIDATE
        values["accepted_operator_decision_reference"] = OPERATOR_DECISION
        values["accepted_governed_asset_reference"] = GOVERNED_ASSET
    if requested_state == "COMPLETED":
        values["creative_result_candidate_reference"] = CANDIDATE
        values["accepted_operator_decision_reference"] = OPERATOR_DECISION
        values["accepted_governed_asset_reference"] = GOVERNED_ASSET
    if (
        current_state == "OPERATOR_REVIEW_PENDING"
        and requested_state == "REJECTED"
    ):
        values["reason_codes"] = ("OPERATOR_DECISION_REJECTED",)
    if (
        current_state == "ASSET_ADMISSION_PENDING"
        and requested_state == "REJECTED"
    ):
        values["reason_codes"] = ("ASSET_ADMISSION_REJECTED",)
    return values


def make_evaluation(**overrides: object):
    values: dict[str, object] = {
        "workflow_request_reference": "workflow-request:001",
        "idempotency_key": "idempotency:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN,
        "creative_brief_reference": BRIEF,
        "instruction_reference": INSTRUCTION,
        "current_workflow_state": "REQUESTED",
        "requested_next_workflow_state": "INPUTS_VALIDATED",
        "responsible_actor_or_service_reference": ACTOR,
        "event_timestamp": TIMESTAMP,
        "evidence_references": (
            (PROJECT, CAMPAIGN[1], "evidence:001"),
        ),
        "reason_codes": ("TRANSITION_ACCEPTED",),
        "workflow_contract_reference": CONTRACT,
        "canonical_input_fingerprint": FINGERPRINT,
        "existing_idempotency_fingerprint": None,
        "manual_external_tool_handoff_reference": None,
        "creative_result_candidate_reference": None,
        "accepted_operator_decision_reference": None,
        "accepted_governed_asset_reference": None,
        "recovery_last_accepted_state": None,
        "recovery_last_accepted_event_reference": None,
        "recovery_reason_code": None,
        "authority_bypass_requested": False,
        "prohibited_automation_requested": False,
        "approval_execution_requested": False,
        "asset_admission_execution_requested": False,
        "lifecycle_mutation_requested": False,
        "production_release_requested": False,
    }
    values.update(overrides)
    return evaluate_governed_creative_workflow_transition(**values)


def test_transition_evaluation_is_frozen_and_has_exact_fields():
    assert [field.name for field in fields(
        GovernedCreativeWorkflowTransitionEvaluation
    )] == [
        "disposition",
        "prior_workflow_state",
        "requested_workflow_state",
        "resulting_workflow_state",
        "creative_workflow_event",
        "governed_creative_workflow_result",
        "reason_codes",
        "diagnostics",
    ]
    evaluation = make_evaluation()
    with pytest.raises(FrozenInstanceError):
        evaluation.disposition = "SAFE_STOP"


def test_exact_transition_disposition_vocabulary():
    assert ALLOWED_TRANSITION_DISPOSITIONS == frozenset(
        {"ACCEPTED", "REJECTED", "SAFE_STOP"}
    )


@pytest.mark.parametrize(("current_state", "requested_state"), VALID_TRANSITIONS)
def test_valid_transition_matrix(current_state, requested_state):
    overrides = transition_overrides(current_state, requested_state)
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
        **overrides,
    )
    assert evaluation.prior_workflow_state == current_state
    assert evaluation.requested_workflow_state == requested_state
    assert evaluation.resulting_workflow_state == requested_state
    assert evaluation.creative_workflow_event is not None
    assert (
        evaluation.creative_workflow_event.prior_workflow_state
        == current_state
    )
    assert (
        evaluation.creative_workflow_event.resulting_workflow_state
        == requested_state
    )
    if requested_state == "REJECTED":
        assert evaluation.disposition == TRANSITION_DISPOSITION_REJECTED
        assert isinstance(
            evaluation.governed_creative_workflow_result,
            GovernedCreativeWorkflowResult,
        )
    elif requested_state == "COMPLETED":
        assert evaluation.disposition == TRANSITION_DISPOSITION_ACCEPTED
        assert isinstance(
            evaluation.governed_creative_workflow_result,
            GovernedCreativeWorkflowResult,
        )
    else:
        assert evaluation.disposition == TRANSITION_DISPOSITION_ACCEPTED
        assert evaluation.governed_creative_workflow_result is None


@pytest.mark.parametrize(
    "current_state",
    tuple(
        state
        for state in sorted(ALLOWED_WORKFLOW_STATES)
        if state not in {"COMPLETED", "REJECTED", "SAFE_STOP"}
    ),
)
def test_explicit_safe_stop_transition_from_every_nonterminal_state(
    current_state,
):
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state="SAFE_STOP",
        reason_codes=("SAFE_STOP_REQUIRED",),
        **transition_overrides(current_state, "SAFE_STOP"),
    )
    assert evaluation.disposition == TRANSITION_DISPOSITION_SAFE_STOP
    assert evaluation.resulting_workflow_state == "SAFE_STOP"
    assert evaluation.creative_workflow_event is not None
    assert isinstance(
        evaluation.governed_creative_workflow_result,
        GovernedCreativeWorkflowResult,
    )
    assert (
        evaluation.governed_creative_workflow_result.final_workflow_state
        == "SAFE_STOP"
    )


@pytest.mark.parametrize(("current_state", "requested_state"), INVALID_TRANSITIONS)
def test_invalid_transition_matrix_fails_closed(current_state, requested_state):
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
        **transition_overrides(current_state, requested_state),
    )
    assert evaluation.disposition == TRANSITION_DISPOSITION_SAFE_STOP
    assert evaluation.resulting_workflow_state == current_state
    assert evaluation.creative_workflow_event is None
    assert evaluation.governed_creative_workflow_result is None
    assert evaluation.reason_codes == (
        "INVALID_STATE_TRANSITION",
        "SAFE_STOP_REQUIRED",
    )


def test_identical_inputs_return_identical_event_and_result_data():
    overrides = transition_overrides(
        "GOVERNED_ASSET_REFERENCE_RECORDED",
        "COMPLETED",
    )
    first = make_evaluation(
        current_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        requested_next_workflow_state="COMPLETED",
        **overrides,
    )
    second = make_evaluation(
        current_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        requested_next_workflow_state="COMPLETED",
        **overrides,
    )
    assert first == second
    assert (
        first.creative_workflow_event.creative_workflow_event_id
        == second.creative_workflow_event.creative_workflow_event_id
    )


def test_identical_recorded_idempotency_fingerprint_is_accepted():
    evaluation = make_evaluation(
        existing_idempotency_fingerprint=FINGERPRINT,
    )
    assert evaluation.disposition == TRANSITION_DISPOSITION_ACCEPTED


def test_conflicting_idempotency_fingerprint_fails_closed():
    evaluation = make_evaluation(
        existing_idempotency_fingerprint=OTHER_FINGERPRINT,
    )
    assert evaluation.reason_codes == (
        "IDEMPOTENCY_CONFLICT",
        "SAFE_STOP_REQUIRED",
    )
    assert evaluation.creative_workflow_event is None


@pytest.mark.parametrize(
    "flag",
    (
        "authority_bypass_requested",
        "prohibited_automation_requested",
        "approval_execution_requested",
        "asset_admission_execution_requested",
        "lifecycle_mutation_requested",
        "production_release_requested",
    ),
)
def test_prohibited_execution_and_mutation_requests_fail_closed(flag):
    evaluation = make_evaluation(**{flag: True})
    assert evaluation.disposition == TRANSITION_DISPOSITION_SAFE_STOP
    assert evaluation.creative_workflow_event is None
    assert "SAFE_STOP_REQUIRED" in evaluation.reason_codes


@pytest.mark.parametrize(
    ("current_state", "requested_state", "expected_code", "base_overrides"),
    (
        (
            "INSTRUCTION_READY",
            "EXTERNAL_HANDOFF_RECORDED",
            "HANDOFF_RECORD_INVALID",
            {},
        ),
        (
            "EXTERNAL_HANDOFF_RECORDED",
            "CANDIDATE_PENDING",
            "HANDOFF_RECORD_INVALID",
            {},
        ),
        (
            "CANDIDATE_PENDING",
            "CANDIDATE_ADMITTED",
            "CANDIDATE_PROVENANCE_INVALID",
            {},
        ),
        (
            "CANDIDATE_ADMITTED",
            "OPERATOR_REVIEW_PENDING",
            "CANDIDATE_PROVENANCE_INVALID",
            {},
        ),
        (
            "OPERATOR_REVIEW_PENDING",
            "OPERATOR_DECISION_RECORDED",
            "OPERATOR_REVIEW_REQUIRED",
            {"creative_result_candidate_reference": CANDIDATE},
        ),
        (
            "OPERATOR_DECISION_RECORDED",
            "ASSET_ADMISSION_PENDING",
            "OPERATOR_REVIEW_REQUIRED",
            {"creative_result_candidate_reference": CANDIDATE},
        ),
        (
            "ASSET_ADMISSION_PENDING",
            "GOVERNED_ASSET_REFERENCE_RECORDED",
            "ASSET_ADMISSION_REQUIRED",
            {
                "creative_result_candidate_reference": CANDIDATE,
                "accepted_operator_decision_reference": OPERATOR_DECISION,
            },
        ),
        (
            "GOVERNED_ASSET_REFERENCE_RECORDED",
            "COMPLETED",
            "ASSET_ADMISSION_REQUIRED",
            {
                "creative_result_candidate_reference": CANDIDATE,
                "accepted_operator_decision_reference": OPERATOR_DECISION,
            },
        ),
    ),
)
def test_missing_transition_preconditions_fail_closed(
    current_state,
    requested_state,
    expected_code,
    base_overrides,
):
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
        **base_overrides,
    )
    assert expected_code in evaluation.reason_codes
    assert evaluation.creative_workflow_event is None


def test_declared_handoff_cannot_skip_handoff_record_state():
    evaluation = make_evaluation(
        current_workflow_state="INSTRUCTION_READY",
        requested_next_workflow_state="CANDIDATE_PENDING",
        manual_external_tool_handoff_reference=HANDOFF,
    )
    assert "HANDOFF_RECORD_INVALID" in evaluation.reason_codes


@pytest.mark.parametrize(
    ("current_state", "reason_code"),
    (
        ("OPERATOR_REVIEW_PENDING", "OPERATOR_DECISION_REJECTED"),
        ("ASSET_ADMISSION_PENDING", "ASSET_ADMISSION_REJECTED"),
    ),
)
def test_rejected_transition_requires_exact_reason(
    current_state,
    reason_code,
):
    overrides = transition_overrides(current_state, "REJECTED")
    overrides.pop("reason_codes", None)
    without_reason = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state="REJECTED",
        **overrides,
    )
    assert reason_code in without_reason.reason_codes
    assert without_reason.creative_workflow_event is None


@pytest.mark.parametrize(
    ("current_state", "reason_code"),
    (
        ("OPERATOR_REVIEW_PENDING", "OPERATOR_DECISION_REJECTED"),
        ("ASSET_ADMISSION_PENDING", "ASSET_ADMISSION_REJECTED"),
    ),
)
def test_rejected_transition_must_not_fabricate_accepted_references(
    current_state,
    reason_code,
):
    overrides = transition_overrides(current_state, "REJECTED")
    overrides.pop("reason_codes", None)
    if current_state == "OPERATOR_REVIEW_PENDING":
        overrides["accepted_operator_decision_reference"] = OPERATOR_DECISION
    else:
        overrides["accepted_governed_asset_reference"] = GOVERNED_ASSET
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state="REJECTED",
        reason_codes=(reason_code,),
        **overrides,
    )
    assert "AUTHORITY_BYPASS_ATTEMPT" in evaluation.reason_codes
    assert evaluation.creative_workflow_event is None


def test_valid_recovery_requires_exact_state_event_and_reason():
    evaluation = make_evaluation(
        current_workflow_state="INPUTS_VALIDATED",
        requested_next_workflow_state="INSTRUCTION_READY",
        evidence_references=(RECOVERY_EVENT,),
        recovery_last_accepted_state="INPUTS_VALIDATED",
        recovery_last_accepted_event_reference=RECOVERY_EVENT,
        recovery_reason_code="RECOVERY_RESUMED",
    )
    assert evaluation.disposition == TRANSITION_DISPOSITION_ACCEPTED


@pytest.mark.parametrize(
    "overrides",
    (
        {"recovery_last_accepted_state": "REQUESTED"},
        {"recovery_last_accepted_event_reference": RECOVERY_EVENT},
        {"recovery_reason_code": "RECOVERY_RESUMED"},
        {
            "recovery_last_accepted_state": "INPUTS_VALIDATED",
            "recovery_last_accepted_event_reference": RECOVERY_EVENT,
            "recovery_reason_code": None,
        },
        {
            "recovery_last_accepted_state": "INPUTS_VALIDATED",
            "recovery_last_accepted_event_reference": RECOVERY_EVENT,
            "recovery_reason_code": "recovery",
        },
    ),
)
def test_invalid_or_partial_recovery_evidence_fails_closed(overrides):
    values = {
        "current_workflow_state": "INPUTS_VALIDATED",
        "requested_next_workflow_state": "INSTRUCTION_READY",
    }
    values.update(overrides)
    evaluation = make_evaluation(**values)
    assert "RECOVERY_EVIDENCE_INVALID" in evaluation.reason_codes
    assert evaluation.creative_workflow_event is None


@pytest.mark.parametrize(
    "field_name",
    (
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_operator_decision_reference",
        "accepted_governed_asset_reference",
    ),
)
@pytest.mark.parametrize(
    "reference",
    (
        ("project:other", CAMPAIGN[1], "reference:001"),
        (PROJECT, "campaign:other", "reference:001"),
    ),
)
def test_cross_context_downstream_references_fail_closed(
    field_name,
    reference,
):
    evaluation = make_evaluation(**{field_name: reference})
    assert "CAMPAIGN_CONTEXT_MISMATCH" in evaluation.reason_codes
    assert evaluation.creative_workflow_event is None


def test_campaign_project_mismatch_fails_closed():
    evaluation = make_evaluation(
        campaign_context_reference=("project:other", CAMPAIGN[1]),
    )
    assert "PROJECT_CONTEXT_MISMATCH" in evaluation.reason_codes


@pytest.mark.parametrize(
    "field_name",
    (
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "",
        " ",
        "secret:value",
        "mutable:value",
        "contains\nnewline",
        "non-ascii-\u00e9",
    ),
)
def test_required_reference_text_rejects_invalid_values(
    field_name,
    invalid_value,
):
    with pytest.raises((TypeError, ValueError)):
        make_evaluation(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "invalid_fingerprint",
    (
        "",
        "a" * 63,
        "A" * 64,
        "g" * 64,
    ),
)
def test_canonical_input_fingerprint_requires_lowercase_sha256(
    invalid_fingerprint,
):
    with pytest.raises(ValueError):
        make_evaluation(canonical_input_fingerprint=invalid_fingerprint)


def test_event_timestamp_must_be_timezone_aware():
    with pytest.raises(ValueError):
        make_evaluation(event_timestamp=datetime(2026, 8, 4, 13, 30))


@pytest.mark.parametrize(
    "invalid_reasons",
    (
        (),
        ("B_CODE", "A_CODE"),
        ("DUPLICATE", "DUPLICATE"),
        ("lowercase",),
    ),
)
def test_reason_codes_require_nonempty_unique_deterministic_order(
    invalid_reasons,
):
    with pytest.raises(ValueError):
        make_evaluation(reason_codes=invalid_reasons)


@pytest.mark.parametrize(
    "invalid_evidence",
    (
        (),
        (
            (PROJECT, CAMPAIGN[1], "z"),
            (PROJECT, CAMPAIGN[1], "a"),
        ),
        (
            (PROJECT, CAMPAIGN[1], "duplicate"),
            (PROJECT, CAMPAIGN[1], "duplicate"),
        ),
        (("project:other", CAMPAIGN[1], "evidence"),),
        ((PROJECT, "campaign:other", "evidence"),),
    ),
)
def test_evidence_references_fail_closed_for_invalid_boundary(
    invalid_evidence,
):
    with pytest.raises((TypeError, ValueError)):
        make_evaluation(evidence_references=invalid_evidence)


def test_completed_result_contains_exact_required_references():
    overrides = transition_overrides(
        "GOVERNED_ASSET_REFERENCE_RECORDED",
        "COMPLETED",
    )
    evaluation = make_evaluation(
        current_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        requested_next_workflow_state="COMPLETED",
        **overrides,
    )
    result = evaluation.governed_creative_workflow_result
    assert result is not None
    assert result.accepted_operator_decision_reference == OPERATOR_DECISION
    assert result.accepted_governed_asset_reference == GOVERNED_ASSET
    assert result.production_release_claimed is False


@pytest.mark.parametrize(
    ("current_state", "reason_code"),
    (
        ("OPERATOR_REVIEW_PENDING", "OPERATOR_DECISION_REJECTED"),
        ("ASSET_ADMISSION_PENDING", "ASSET_ADMISSION_REJECTED"),
    ),
)
def test_rejected_result_does_not_fabricate_downstream_references(
    current_state,
    reason_code,
):
    overrides = transition_overrides(current_state, "REJECTED")
    overrides.pop("reason_codes", None)
    evaluation = make_evaluation(
        current_workflow_state=current_state,
        requested_next_workflow_state="REJECTED",
        reason_codes=(reason_code,),
        **overrides,
    )
    result = evaluation.governed_creative_workflow_result
    assert result is not None
    assert result.accepted_operator_decision_reference is None
    assert result.accepted_governed_asset_reference is None
    assert result.production_release_claimed is False


def test_audit_event_never_claims_executed_authority_or_release():
    evaluation = make_evaluation()
    event = evaluation.creative_workflow_event
    assert event is not None
    assert event.executed_approval_claimed is False
    assert event.asset_admission_claimed is False
    assert event.lifecycle_mutation_claimed is False
    assert event.production_release_claimed is False


def test_no_duplicate_audit_event_identity_for_identical_replay_inputs():
    first = make_evaluation(existing_idempotency_fingerprint=FINGERPRINT)
    second = make_evaluation(existing_idempotency_fingerprint=FINGERPRINT)
    assert (
        first.creative_workflow_event.creative_workflow_event_id
        == second.creative_workflow_event.creative_workflow_event_id
    )


def test_source_contains_no_ambient_or_side_effect_dependencies():
    source_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "domain"
        / "evaluate_governed_creative_workflow_transition.py"
    )
    source = source_path.read_text(encoding="ascii")
    forbidden = (
        "import os",
        "import random",
        "import secrets",
        "import socket",
        "import subprocess",
        "requests.",
        "urllib.",
        "datetime.now",
        "datetime.utcnow",
        "Path(",
        "open(",
        "sqlite",
        "sqlalchemy",
        "model.generate",
        "inference",
        "embedding",
        "vector",
        "ontology",
        "knowledge_graph",
    )
    for marker in forbidden:
        assert marker not in source


def test_targeted_test_file_is_the_only_test_boundary():
    assert Path(__file__).name == (
        "test_evaluate_governed_creative_workflow_transition.py"
    )
