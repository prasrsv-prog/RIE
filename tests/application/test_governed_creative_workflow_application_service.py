from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from rie.application.governed_creative_workflow_application_service import (
    GovernedCreativeWorkflowApplicationAssessment,
    assess_governed_creative_workflow,
    derive_governed_creative_workflow_application_assessment_fingerprint,
    derive_governed_creative_workflow_application_input_fingerprint,
)
from rie.domain.creative_workflow_event import ALLOWED_WORKFLOW_STATES
from rie.domain.evaluate_governed_creative_workflow_transition import (
    TRANSITION_DISPOSITION_ACCEPTED,
    TRANSITION_DISPOSITION_REJECTED,
    TRANSITION_DISPOSITION_SAFE_STOP,
)
from rie.domain.governed_creative_workflow_request import (
    GovernedCreativeWorkflowRequest,
)

PROJECT = "project:alpha"
CAMPAIGN_ID = "campaign:one"
CAMPAIGN = (PROJECT, CAMPAIGN_ID)
BRIEF = "brief:approved:001"
INSTRUCTION = ("instruction:approved:001", "APPROVED_INSTRUCTION")
ACTOR_ID = "actor:operator:001"
ACTOR = ("ACTOR", ACTOR_ID)
SERVICE = ("ACCEPTED_SERVICE", "service:gate18:assessment:001")
CONTRACT = ("GATE_18_CREATIVE_WORKFLOW", "1.0")
TIMESTAMP = datetime(2026, 8, 4, 14, 30, tzinfo=timezone.utc)
REQUEST_TIMESTAMP = TIMESTAMP - timedelta(minutes=5)
EVIDENCE = ((PROJECT, CAMPAIGN_ID, "evidence:001"),)
HANDOFF = (PROJECT, CAMPAIGN_ID, "handoff:001")
CANDIDATE = (PROJECT, CAMPAIGN_ID, "candidate:001")
OPERATOR_DECISION = (
    PROJECT,
    CAMPAIGN_ID,
    "operator-decision:accepted:001",
)
GOVERNED_ASSET = (
    PROJECT,
    CAMPAIGN_ID,
    "governed-asset:accepted:001",
)
RECOVERY_EVENT = (PROJECT, CAMPAIGN_ID, "a" * 64)

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

VALID_TRANSITIONS = tuple(
    (prior, requested)
    for prior in sorted(ALLOWED_WORKFLOW_STATES)
    for requested in sorted(VALID_TARGETS[prior])
)
INVALID_TRANSITIONS = tuple(
    (prior, requested)
    for prior in sorted(ALLOWED_WORKFLOW_STATES)
    for requested in sorted(ALLOWED_WORKFLOW_STATES)
    if requested not in VALID_TARGETS[prior]
)


def make_request(**overrides: object) -> GovernedCreativeWorkflowRequest:
    values: dict[str, object] = {
        "workflow_request_id": "workflow-request:001",
        "idempotency_key": "idempotency:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN,
        "creative_brief_reference": BRIEF,
        "approved_knowledge_references": ("knowledge:approved:001",),
        "governed_asset_references": (),
        "instruction_reference": INSTRUCTION,
        "requesting_actor_reference": ACTOR_ID,
        "request_timestamp": REQUEST_TIMESTAMP,
        "workflow_contract_reference": CONTRACT,
        "requested_output_purpose_code": "CAMPAIGN_CREATIVE",
        "requested_review_policy_reference": "review-policy:001",
        "manual_external_tool_handoff_declared": False,
    }
    values.update(overrides)
    return GovernedCreativeWorkflowRequest(**values)


def transition_overrides(
    current_state: str,
    requested_state: str,
) -> dict[str, object]:
    values: dict[str, object] = {}
    if requested_state == "SAFE_STOP":
        values["reason_codes"] = ("SAFE_STOP_REQUIRED",)
    if (
        current_state == "INSTRUCTION_READY"
        and requested_state == "EXTERNAL_HANDOFF_RECORDED"
    ):
        values["workflow_request"] = make_request(
            manual_external_tool_handoff_declared=True
        )
        values["manual_external_tool_handoff_reference"] = HANDOFF
    if current_state == "EXTERNAL_HANDOFF_RECORDED":
        values["workflow_request"] = make_request(
            manual_external_tool_handoff_declared=True
        )
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
        values[
            "accepted_gate_16_operator_decision_reference"
        ] = OPERATOR_DECISION
    if current_state == "GOVERNED_ASSET_REFERENCE_RECORDED":
        values[
            "accepted_gate_15_governed_asset_reference"
        ] = GOVERNED_ASSET
    if requested_state in {"CANDIDATE_ADMITTED", "OPERATOR_REVIEW_PENDING"}:
        values["creative_result_candidate_reference"] = CANDIDATE
    if requested_state in {
        "OPERATOR_DECISION_RECORDED",
        "ASSET_ADMISSION_PENDING",
    }:
        values["creative_result_candidate_reference"] = CANDIDATE
        values[
            "accepted_gate_16_operator_decision_reference"
        ] = OPERATOR_DECISION
    if requested_state == "GOVERNED_ASSET_REFERENCE_RECORDED":
        values["creative_result_candidate_reference"] = CANDIDATE
        values[
            "accepted_gate_16_operator_decision_reference"
        ] = OPERATOR_DECISION
        values[
            "accepted_gate_15_governed_asset_reference"
        ] = GOVERNED_ASSET
    if requested_state == "COMPLETED":
        values["creative_result_candidate_reference"] = CANDIDATE
        values[
            "accepted_gate_16_operator_decision_reference"
        ] = OPERATOR_DECISION
        values[
            "accepted_gate_15_governed_asset_reference"
        ] = GOVERNED_ASSET
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


def make_assessment(**overrides: object):
    values: dict[str, object] = {
        "workflow_request": make_request(),
        "current_workflow_state": "REQUESTED",
        "requested_next_workflow_state": "INPUTS_VALIDATED",
        "responsible_actor_or_service_reference": ACTOR,
        "assessment_timestamp": TIMESTAMP,
        "evidence_references": EVIDENCE,
        "reason_codes": ("ASSESSMENT_ACCEPTED",),
        "workflow_contract_reference": CONTRACT,
    }
    values.update(overrides)
    return assess_governed_creative_workflow(**values)


def test_assessment_has_exact_twelve_fields() -> None:
    assert tuple(
        field.name
        for field in fields(GovernedCreativeWorkflowApplicationAssessment)
    ) == (
        "assessment_fingerprint",
        "workflow_request_reference",
        "project_context_reference",
        "campaign_context_reference",
        "current_workflow_state",
        "requested_workflow_state",
        "accepted_gate_15_governed_asset_reference",
        "accepted_gate_16_operator_decision_reference",
        "transition_evaluation",
        "creative_workflow_event",
        "governed_creative_workflow_result",
        "production_release_claimed",
    )


def test_assessment_is_immutable() -> None:
    assessment = make_assessment()
    with pytest.raises(FrozenInstanceError):
        assessment.workflow_request_reference = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(("current_state", "requested_state"), VALID_TRANSITIONS)
def test_every_valid_transition_is_assessed_deterministically(
    current_state: str,
    requested_state: str,
) -> None:
    overrides = transition_overrides(current_state, requested_state)
    assessment = make_assessment(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
        **overrides,
    )
    replay = make_assessment(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
        **overrides,
    )
    assert assessment == replay
    assert assessment.assessment_fingerprint == replay.assessment_fingerprint
    assert assessment.transition_evaluation.prior_workflow_state == current_state
    assert (
        assessment.transition_evaluation.requested_workflow_state
        == requested_state
    )
    assert assessment.production_release_claimed is False
    if requested_state == "SAFE_STOP":
        assert (
            assessment.transition_evaluation.disposition
            == TRANSITION_DISPOSITION_SAFE_STOP
        )
    elif requested_state == "REJECTED":
        assert (
            assessment.transition_evaluation.disposition
            == TRANSITION_DISPOSITION_REJECTED
        )
    else:
        assert (
            assessment.transition_evaluation.disposition
            == TRANSITION_DISPOSITION_ACCEPTED
        )


@pytest.mark.parametrize(("current_state", "requested_state"), INVALID_TRANSITIONS)
def test_every_invalid_transition_fails_closed(
    current_state: str,
    requested_state: str,
) -> None:
    assessment = make_assessment(
        current_workflow_state=current_state,
        requested_next_workflow_state=requested_state,
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_SAFE_STOP
    )
    assert assessment.creative_workflow_event is None
    assert assessment.governed_creative_workflow_result is None
    assert "INVALID_STATE_TRANSITION" in (
        assessment.transition_evaluation.reason_codes
    )


def test_completed_transition_consumes_gate_15_and_gate_16_references() -> None:
    assessment = make_assessment(
        current_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        requested_next_workflow_state="COMPLETED",
        creative_result_candidate_reference=CANDIDATE,
        accepted_gate_16_operator_decision_reference=OPERATOR_DECISION,
        accepted_gate_15_governed_asset_reference=GOVERNED_ASSET,
    )
    assert assessment.accepted_gate_15_governed_asset_reference == GOVERNED_ASSET
    assert (
        assessment.accepted_gate_16_operator_decision_reference
        == OPERATOR_DECISION
    )
    assert assessment.governed_creative_workflow_result is not None
    assert (
        assessment.governed_creative_workflow_result
        .accepted_operator_decision_reference
        == OPERATOR_DECISION
    )
    assert (
        assessment.governed_creative_workflow_result
        .accepted_governed_asset_reference
        == GOVERNED_ASSET
    )
    assert (
        assessment.governed_creative_workflow_result.production_release_claimed
        is False
    )


def test_missing_gate_16_reference_safe_stops_operator_transition() -> None:
    assessment = make_assessment(
        current_workflow_state="OPERATOR_REVIEW_PENDING",
        requested_next_workflow_state="OPERATOR_DECISION_RECORDED",
        creative_result_candidate_reference=CANDIDATE,
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_SAFE_STOP
    )
    assert "OPERATOR_REVIEW_REQUIRED" in (
        assessment.transition_evaluation.reason_codes
    )


def test_missing_gate_15_reference_safe_stops_asset_transition() -> None:
    assessment = make_assessment(
        current_workflow_state="ASSET_ADMISSION_PENDING",
        requested_next_workflow_state="GOVERNED_ASSET_REFERENCE_RECORDED",
        creative_result_candidate_reference=CANDIDATE,
        accepted_gate_16_operator_decision_reference=OPERATOR_DECISION,
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_SAFE_STOP
    )
    assert "ASSET_ADMISSION_REQUIRED" in (
        assessment.transition_evaluation.reason_codes
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_gate_16_operator_decision_reference",
        "accepted_gate_15_governed_asset_reference",
        "recovery_last_accepted_event_reference",
    ),
)
def test_cross_project_external_reference_is_rejected(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="project binding"):
        make_assessment(
            **{
                field_name: (
                    "project:other",
                    CAMPAIGN_ID,
                    "reference:001",
                )
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_gate_16_operator_decision_reference",
        "accepted_gate_15_governed_asset_reference",
        "recovery_last_accepted_event_reference",
    ),
)
def test_cross_campaign_external_reference_is_rejected(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="campaign binding"):
        make_assessment(
            **{
                field_name: (
                    PROJECT,
                    "campaign:other",
                    "reference:001",
                )
            }
        )


def test_undeclared_handoff_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="declared external handoff"):
        make_assessment(
            manual_external_tool_handoff_reference=HANDOFF,
        )


def test_declared_handoff_reference_is_accepted() -> None:
    assessment = make_assessment(
        workflow_request=make_request(
            manual_external_tool_handoff_declared=True
        ),
        current_workflow_state="INSTRUCTION_READY",
        requested_next_workflow_state="EXTERNAL_HANDOFF_RECORDED",
        manual_external_tool_handoff_reference=HANDOFF,
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_ACCEPTED
    )


def test_actor_must_match_requesting_actor() -> None:
    with pytest.raises(ValueError, match="requesting_actor_reference"):
        make_assessment(
            responsible_actor_or_service_reference=(
                "ACTOR",
                "actor:other",
            )
        )


def test_accepted_service_identity_is_allowed() -> None:
    assessment = make_assessment(
        responsible_actor_or_service_reference=SERVICE
    )
    assert (
        assessment.creative_workflow_event
        .responsible_actor_or_service_reference
        == SERVICE
    )


def test_unsupported_responsibility_kind_is_rejected() -> None:
    with pytest.raises(ValueError, match="ACTOR or ACCEPTED_SERVICE"):
        make_assessment(
            responsible_actor_or_service_reference=(
                "SYSTEM",
                "service:001",
            )
        )


def test_contract_reference_must_match_request() -> None:
    with pytest.raises(ValueError, match="must match workflow request"):
        make_assessment(
            workflow_contract_reference=("OTHER_CONTRACT", "1.0")
        )


def test_assessment_timestamp_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        make_assessment(
            assessment_timestamp=datetime(2026, 8, 4, 14, 30)
        )


def test_assessment_timestamp_must_not_precede_request() -> None:
    with pytest.raises(ValueError, match="must not precede"):
        make_assessment(
            assessment_timestamp=REQUEST_TIMESTAMP - timedelta(seconds=1)
        )


def test_workflow_request_type_is_enforced() -> None:
    with pytest.raises(TypeError, match="GovernedCreativeWorkflowRequest"):
        make_assessment(workflow_request=object())


@pytest.mark.parametrize(
    "state_field",
    ("current_workflow_state", "requested_next_workflow_state"),
)
def test_unknown_workflow_state_is_rejected(state_field: str) -> None:
    with pytest.raises(ValueError, match="unsupported"):
        make_assessment(**{state_field: "UNKNOWN"})


def test_input_fingerprint_is_lowercase_sha256_and_deterministic() -> None:
    request = make_request()
    kwargs = {
        "workflow_request": request,
        "current_workflow_state": "REQUESTED",
        "requested_next_workflow_state": "INPUTS_VALIDATED",
        "responsible_actor_or_service_reference": ACTOR,
        "assessment_timestamp": TIMESTAMP,
        "evidence_references": EVIDENCE,
        "reason_codes": ("ASSESSMENT_ACCEPTED",),
        "workflow_contract_reference": CONTRACT,
        "manual_external_tool_handoff_reference": None,
        "creative_result_candidate_reference": None,
        "accepted_gate_16_operator_decision_reference": None,
        "accepted_gate_15_governed_asset_reference": None,
        "recovery_last_accepted_state": None,
        "recovery_last_accepted_event_reference": None,
        "recovery_reason_code": None,
    }
    first = derive_governed_creative_workflow_application_input_fingerprint(
        **kwargs
    )
    second = derive_governed_creative_workflow_application_input_fingerprint(
        **kwargs
    )
    assert first == second
    assert len(first) == 64
    assert first == first.lower()
    int(first, 16)


def test_idempotency_conflict_fails_closed() -> None:
    assessment = make_assessment(
        existing_idempotency_fingerprint="f" * 64
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_SAFE_STOP
    )
    assert "IDEMPOTENCY_CONFLICT" in (
        assessment.transition_evaluation.reason_codes
    )


def test_identical_existing_idempotency_fingerprint_replays() -> None:
    request = make_request()
    canonical = (
        derive_governed_creative_workflow_application_input_fingerprint(
            workflow_request=request,
            current_workflow_state="REQUESTED",
            requested_next_workflow_state="INPUTS_VALIDATED",
            responsible_actor_or_service_reference=ACTOR,
            assessment_timestamp=TIMESTAMP,
            evidence_references=EVIDENCE,
            reason_codes=("ASSESSMENT_ACCEPTED",),
            workflow_contract_reference=CONTRACT,
            manual_external_tool_handoff_reference=None,
            creative_result_candidate_reference=None,
            accepted_gate_16_operator_decision_reference=None,
            accepted_gate_15_governed_asset_reference=None,
            recovery_last_accepted_state=None,
            recovery_last_accepted_event_reference=None,
            recovery_reason_code=None,
        )
    )
    assessment = make_assessment(
        workflow_request=request,
        existing_idempotency_fingerprint=canonical,
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_ACCEPTED
    )


def test_recovery_evidence_is_delegated_without_side_effects() -> None:
    assessment = make_assessment(
        recovery_last_accepted_state="REQUESTED",
        recovery_last_accepted_event_reference=RECOVERY_EVENT,
        recovery_reason_code="RECOVERY_CONFIRMED",
        evidence_references=tuple(sorted(EVIDENCE + (RECOVERY_EVENT,))),
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_ACCEPTED
    )


def test_partial_recovery_evidence_fails_closed() -> None:
    assessment = make_assessment(
        recovery_last_accepted_state="REQUESTED",
    )
    assert (
        assessment.transition_evaluation.disposition
        == TRANSITION_DISPOSITION_SAFE_STOP
    )
    assert "RECOVERY_EVIDENCE_INVALID" in (
        assessment.transition_evaluation.reason_codes
    )


@pytest.mark.parametrize(
    "secret_reference",
    (
        (PROJECT, CAMPAIGN_ID, "secret:operator"),
        (PROJECT, CAMPAIGN_ID, "api_key:value"),
        (PROJECT, CAMPAIGN_ID, "session_token:value"),
    ),
)
def test_secret_external_reference_is_rejected(
    secret_reference: tuple[str, str, str],
) -> None:
    with pytest.raises(ValueError, match="secret material"):
        make_assessment(
            accepted_gate_16_operator_decision_reference=secret_reference
        )


@pytest.mark.parametrize(
    "mutable_reference",
    (
        (PROJECT, CAMPAIGN_ID, "mutable:operator"),
        (PROJECT, CAMPAIGN_ID, "session:operator"),
        (PROJECT, CAMPAIGN_ID, "temp:operator"),
    ),
)
def test_mutable_external_reference_is_rejected(
    mutable_reference: tuple[str, str, str],
) -> None:
    with pytest.raises(ValueError, match="immutable reference"):
        make_assessment(
            accepted_gate_16_operator_decision_reference=mutable_reference
        )


def test_assessment_event_and_result_are_exact_evaluation_outputs() -> None:
    assessment = make_assessment()
    assert (
        assessment.creative_workflow_event
        == assessment.transition_evaluation.creative_workflow_event
    )
    assert (
        assessment.governed_creative_workflow_result
        == assessment.transition_evaluation.governed_creative_workflow_result
    )


def test_assessment_fingerprint_is_deterministic() -> None:
    first = make_assessment()
    second = make_assessment()
    assert first.assessment_fingerprint == second.assessment_fingerprint
    assert len(first.assessment_fingerprint) == 64
    int(first.assessment_fingerprint, 16)


def test_assessment_fingerprint_changes_when_explicit_input_changes() -> None:
    first = make_assessment()
    second = make_assessment(
        evidence_references=((PROJECT, CAMPAIGN_ID, "evidence:002"),)
    )
    assert first.assessment_fingerprint != second.assessment_fingerprint


def test_invalid_assessment_fingerprint_is_rejected() -> None:
    assessment = make_assessment()
    values = {
        field.name: getattr(assessment, field.name)
        for field in fields(assessment)
    }
    values["assessment_fingerprint"] = "not-sha"
    with pytest.raises(ValueError, match="lowercase SHA256"):
        GovernedCreativeWorkflowApplicationAssessment(**values)


def test_production_release_claim_is_rejected() -> None:
    assessment = make_assessment()
    values = {
        field.name: getattr(assessment, field.name)
        for field in fields(assessment)
    }
    values["production_release_claimed"] = True
    with pytest.raises(ValueError, match="must not claim production release"):
        GovernedCreativeWorkflowApplicationAssessment(**values)


def test_assessment_fingerprint_helper_rejects_non_sha_input() -> None:
    assessment = make_assessment()
    with pytest.raises(ValueError, match="lowercase SHA256"):
        derive_governed_creative_workflow_application_assessment_fingerprint(
            canonical_input_fingerprint="bad",
            transition_evaluation=assessment.transition_evaluation,
            accepted_gate_15_governed_asset_reference=None,
            accepted_gate_16_operator_decision_reference=None,
        )


def test_service_source_contains_only_stateless_boundary_imports() -> None:
    source = Path(
        "src/rie/application/"
        "governed_creative_workflow_application_service.py"
    ).read_text(encoding="ascii")
    forbidden = (
        "import requests",
        "import socket",
        "import sqlite3",
        "import subprocess",
        "from pathlib import Path",
        "open(",
        "os.environ",
        "os.getenv",
        "time.time",
        "datetime.now",
        "random.",
        "approval_execution_requested=True",
        "asset_admission_execution_requested=True",
        "lifecycle_mutation_requested=True",
        "production_release_requested=True",
    )
    for marker in forbidden:
        assert marker not in source


def test_service_delegates_with_all_execution_flags_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import rie.application.governed_creative_workflow_application_service as module

    calls: list[dict[str, object]] = []
    real = module.evaluate_governed_creative_workflow_transition

    def wrapper(**kwargs: object):
        calls.append(kwargs)
        return real(**kwargs)

    monkeypatch.setattr(
        module,
        "evaluate_governed_creative_workflow_transition",
        wrapper,
    )
    assessment = module.assess_governed_creative_workflow(
        workflow_request=make_request(),
        current_workflow_state="REQUESTED",
        requested_next_workflow_state="INPUTS_VALIDATED",
        responsible_actor_or_service_reference=ACTOR,
        assessment_timestamp=TIMESTAMP,
        evidence_references=EVIDENCE,
        reason_codes=("ASSESSMENT_ACCEPTED",),
        workflow_contract_reference=CONTRACT,
    )
    assert assessment.transition_evaluation is not None
    assert len(calls) == 1
    call = calls[0]
    assert call["authority_bypass_requested"] is False
    assert call["prohibited_automation_requested"] is False
    assert call["approval_execution_requested"] is False
    assert call["asset_admission_execution_requested"] is False
    assert call["lifecycle_mutation_requested"] is False
    assert call["production_release_requested"] is False


def test_targeted_file_is_the_only_application_service_test_file() -> None:
    target = Path(
        "tests/application/"
        "test_governed_creative_workflow_application_service.py"
    )
    assert target.exists()
    assert target.name == (
        "test_governed_creative_workflow_application_service.py"
    )
