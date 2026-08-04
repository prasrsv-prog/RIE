from dataclasses import FrozenInstanceError, MISSING, fields
from datetime import datetime, timezone
from pathlib import Path

import pytest

from rie.domain.creative_workflow_event import (
    ALLOWED_INSTRUCTION_AUTHORITY_STATES,
    ALLOWED_RESPONSIBLE_REFERENCE_KINDS,
    ALLOWED_WORKFLOW_STATES,
    INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
    RESPONSIBLE_REFERENCE_ACCEPTED_SERVICE,
    RESPONSIBLE_REFERENCE_ACTOR,
    CreativeWorkflowEvent,
    derive_creative_workflow_event_id,
)


def make_event(**overrides: object) -> CreativeWorkflowEvent:
    base: dict[str, object] = {
        "workflow_request_reference": "workflow-request-001",
        "idempotency_key": "project-001:campaign-001:workflow-001",
        "prior_workflow_state": "CANDIDATE_PENDING",
        "resulting_workflow_state": "CANDIDATE_ADMITTED",
        "project_context_reference": "project-001",
        "campaign_context_reference": ("project-001", "campaign-001"),
        "creative_brief_reference": "brief-001",
        "instruction_reference": (
            "instruction-001",
            INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
        ),
        "responsible_actor_or_service_reference": (
            RESPONSIBLE_REFERENCE_ACTOR,
            "actor-001",
        ),
        "event_timestamp": datetime(
            2026,
            8,
            4,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        "evidence_references": (
            ("project-001", "campaign-001", "candidate-001"),
            ("project-001", "campaign-001", "workflow-request-001"),
        ),
        "reason_codes": ("CANDIDATE_ADMISSION_ACCEPTED",),
        "workflow_contract_reference": (
            "GOVERNED_CREATIVE_WORKFLOW",
            "1.0",
        ),
        "executed_approval_claimed": False,
        "asset_admission_claimed": False,
        "lifecycle_mutation_claimed": False,
        "production_release_claimed": False,
    }
    base.update(overrides)
    if "creative_workflow_event_id" not in overrides:
        base["creative_workflow_event_id"] = (
            derive_creative_workflow_event_id(
                workflow_request_reference=base[
                    "workflow_request_reference"
                ],
                idempotency_key=base["idempotency_key"],
                prior_workflow_state=base["prior_workflow_state"],
                resulting_workflow_state=base["resulting_workflow_state"],
                project_context_reference=base[
                    "project_context_reference"
                ],
                campaign_context_reference=base[
                    "campaign_context_reference"
                ],
                creative_brief_reference=base[
                    "creative_brief_reference"
                ],
                instruction_reference=base["instruction_reference"],
                responsible_actor_or_service_reference=base[
                    "responsible_actor_or_service_reference"
                ],
                event_timestamp=base["event_timestamp"],
                evidence_references=base["evidence_references"],
                reason_codes=base["reason_codes"],
                workflow_contract_reference=base[
                    "workflow_contract_reference"
                ],
            )
        )
    return CreativeWorkflowEvent(**base)


def test_exact_eighteen_fields_and_no_defaults() -> None:
    model_fields = fields(CreativeWorkflowEvent)
    assert tuple(field.name for field in model_fields) == (
        "creative_workflow_event_id",
        "workflow_request_reference",
        "idempotency_key",
        "prior_workflow_state",
        "resulting_workflow_state",
        "project_context_reference",
        "campaign_context_reference",
        "creative_brief_reference",
        "instruction_reference",
        "responsible_actor_or_service_reference",
        "event_timestamp",
        "evidence_references",
        "reason_codes",
        "workflow_contract_reference",
        "executed_approval_claimed",
        "asset_admission_claimed",
        "lifecycle_mutation_claimed",
        "production_release_claimed",
    )
    assert all(field.default is MISSING for field in model_fields)
    assert all(field.default_factory is MISSING for field in model_fields)


def test_event_is_immutable() -> None:
    event = make_event()
    with pytest.raises(FrozenInstanceError):
        event.idempotency_key = "changed"


def test_allowed_workflow_states_are_exact() -> None:
    assert ALLOWED_WORKFLOW_STATES == {
        "REQUESTED",
        "INPUTS_VALIDATED",
        "INSTRUCTION_READY",
        "EXTERNAL_HANDOFF_RECORDED",
        "CANDIDATE_PENDING",
        "CANDIDATE_ADMITTED",
        "OPERATOR_REVIEW_PENDING",
        "OPERATOR_DECISION_RECORDED",
        "ASSET_ADMISSION_PENDING",
        "GOVERNED_ASSET_REFERENCE_RECORDED",
        "COMPLETED",
        "REJECTED",
        "SAFE_STOP",
    }


def test_allowed_instruction_authority_states_are_exact() -> None:
    assert ALLOWED_INSTRUCTION_AUTHORITY_STATES == {
        "PROMPT_CANDIDATE",
        "APPROVED_INSTRUCTION",
    }


def test_allowed_responsible_reference_kinds_are_exact() -> None:
    assert ALLOWED_RESPONSIBLE_REFERENCE_KINDS == {
        "ACTOR",
        "ACCEPTED_SERVICE",
    }


@pytest.mark.parametrize(
    "instruction_state",
    [
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    ],
)
def test_both_instruction_authority_states_are_supported(
    instruction_state: str,
) -> None:
    event = make_event(
        instruction_reference=("instruction-001", instruction_state),
    )
    assert event.instruction_reference[1] == instruction_state


@pytest.mark.parametrize(
    "reference_kind",
    [
        RESPONSIBLE_REFERENCE_ACTOR,
        RESPONSIBLE_REFERENCE_ACCEPTED_SERVICE,
    ],
)
def test_actor_and_accepted_service_references_are_supported(
    reference_kind: str,
) -> None:
    event = make_event(
        responsible_actor_or_service_reference=(
            reference_kind,
            "responsible-001",
        ),
    )
    assert event.responsible_actor_or_service_reference[0] == reference_kind


@pytest.mark.parametrize("prior_state", sorted(ALLOWED_WORKFLOW_STATES))
def test_each_allowed_state_is_accepted_as_prior_state(
    prior_state: str,
) -> None:
    resulting_state = (
        "SAFE_STOP" if prior_state != "SAFE_STOP" else "REQUESTED"
    )
    event = make_event(
        prior_workflow_state=prior_state,
        resulting_workflow_state=resulting_state,
    )
    assert event.prior_workflow_state == prior_state


@pytest.mark.parametrize("resulting_state", sorted(ALLOWED_WORKFLOW_STATES))
def test_each_allowed_state_is_accepted_as_resulting_state(
    resulting_state: str,
) -> None:
    prior_state = (
        "REQUESTED" if resulting_state != "REQUESTED" else "SAFE_STOP"
    )
    event = make_event(
        prior_workflow_state=prior_state,
        resulting_workflow_state=resulting_state,
    )
    assert event.resulting_workflow_state == resulting_state


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ],
)
@pytest.mark.parametrize("invalid_value", ["", "   ", "caf\u00e9"])
def test_required_text_fields_fail_closed(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError):
        make_event(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ],
)
def test_required_text_fields_reject_non_text(field_name: str) -> None:
    with pytest.raises(TypeError):
        make_event(**{field_name: 123})


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ],
)
def test_required_text_fields_reject_control_characters(
    field_name: str,
) -> None:
    with pytest.raises(ValueError):
        make_event(**{field_name: "value\nwith-newline"})


@pytest.mark.parametrize(
    "secret_value",
    [
        "secret:abc",
        "password=value",
        "credential-001",
        "api_key=abc",
        "access_token=abc",
        "session_token=abc",
        "private_key=abc",
        "authorization: bearer abc",
    ],
)
def test_required_references_reject_secret_markers(
    secret_value: str,
) -> None:
    with pytest.raises(ValueError):
        make_event(creative_brief_reference=secret_value)


@pytest.mark.parametrize(
    "mutable_reference",
    [
        "memory:object-001",
        "mutable:object-001",
        "object:object-001",
        "session:object-001",
        "temp:object-001",
    ],
)
def test_required_references_reject_mutable_reference_prefixes(
    mutable_reference: str,
) -> None:
    with pytest.raises(ValueError):
        make_event(workflow_request_reference=mutable_reference)


@pytest.mark.parametrize(
    "invalid_campaign",
    [
        ["project-001", "campaign-001"],
        ("project-001",),
        ("project-001", "campaign-001", "extra"),
    ],
)
def test_campaign_reference_shape_fails_closed(
    invalid_campaign: object,
) -> None:
    expected_error = TypeError if isinstance(invalid_campaign, list) else ValueError
    with pytest.raises(expected_error):
        make_event(campaign_context_reference=invalid_campaign)


def test_campaign_reference_must_match_project_context() -> None:
    with pytest.raises(ValueError):
        make_event(
            campaign_context_reference=("project-002", "campaign-001"),
        )


@pytest.mark.parametrize(
    "invalid_instruction",
    [
        ["instruction-001", "APPROVED_INSTRUCTION"],
        ("instruction-001",),
        ("instruction-001", "APPROVED_INSTRUCTION", "extra"),
    ],
)
def test_instruction_reference_shape_fails_closed(
    invalid_instruction: object,
) -> None:
    expected_error = TypeError if isinstance(invalid_instruction, list) else ValueError
    with pytest.raises(expected_error):
        make_event(instruction_reference=invalid_instruction)


def test_instruction_reference_rejects_unknown_authority() -> None:
    with pytest.raises(ValueError):
        make_event(
            instruction_reference=("instruction-001", "UNKNOWN"),
        )


@pytest.mark.parametrize(
    "invalid_responsible_reference",
    [
        ["ACTOR", "actor-001"],
        ("ACTOR",),
        ("ACTOR", "actor-001", "extra"),
    ],
)
def test_responsible_reference_shape_fails_closed(
    invalid_responsible_reference: object,
) -> None:
    expected_error = (
        TypeError
        if isinstance(invalid_responsible_reference, list)
        else ValueError
    )
    with pytest.raises(expected_error):
        make_event(
            responsible_actor_or_service_reference=(
                invalid_responsible_reference
            ),
        )


def test_responsible_reference_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError):
        make_event(
            responsible_actor_or_service_reference=(
                "UNACCEPTED_SERVICE",
                "service-001",
            ),
        )


def test_event_timestamp_must_be_datetime() -> None:
    with pytest.raises(TypeError):
        make_event(
            event_timestamp="2026-08-04T10:30:00+00:00",
            creative_workflow_event_id="0" * 64,
        )


def test_event_timestamp_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError):
        make_event(event_timestamp=datetime(2026, 8, 4, 10, 30))


@pytest.mark.parametrize(
    "invalid_evidence",
    [
        ["project-001", "campaign-001", "evidence-001"],
        (),
    ],
)
def test_evidence_collection_shape_fails_closed(
    invalid_evidence: object,
) -> None:
    expected_error = TypeError if isinstance(invalid_evidence, list) else ValueError
    with pytest.raises(expected_error):
        make_event(evidence_references=invalid_evidence)


@pytest.mark.parametrize(
    "invalid_item",
    [
        ["project-001", "campaign-001", "evidence-001"],
        ("project-001", "campaign-001"),
        ("project-001", "campaign-001", "evidence-001", "extra"),
    ],
)
def test_evidence_item_shape_fails_closed(invalid_item: object) -> None:
    expected_error = TypeError if isinstance(invalid_item, list) else ValueError
    with pytest.raises(expected_error):
        make_event(evidence_references=(invalid_item,))


def test_evidence_references_reject_duplicate_items() -> None:
    item = ("project-001", "campaign-001", "evidence-001")
    with pytest.raises(ValueError):
        make_event(evidence_references=(item, item))


def test_evidence_references_require_deterministic_ordering() -> None:
    with pytest.raises(ValueError):
        make_event(
            evidence_references=(
                ("project-001", "campaign-001", "z-evidence"),
                ("project-001", "campaign-001", "a-evidence"),
            ),
        )


def test_evidence_references_reject_cross_project_binding() -> None:
    with pytest.raises(ValueError):
        make_event(
            evidence_references=(
                ("project-002", "campaign-001", "evidence-001"),
            ),
        )


def test_evidence_references_reject_cross_campaign_binding() -> None:
    with pytest.raises(ValueError):
        make_event(
            evidence_references=(
                ("project-001", "campaign-002", "evidence-001"),
            ),
        )


def test_evidence_references_reject_binary_content() -> None:
    with pytest.raises(TypeError):
        make_event(
            evidence_references=(
                ("project-001", "campaign-001", b"binary"),
            ),
        )


def test_evidence_references_reject_secret_material() -> None:
    with pytest.raises(ValueError):
        make_event(
            evidence_references=(
                ("project-001", "campaign-001", "secret:evidence"),
            ),
        )


def test_evidence_references_reject_mutable_reference() -> None:
    with pytest.raises(ValueError):
        make_event(
            evidence_references=(
                ("project-001", "campaign-001", "memory:evidence"),
            ),
        )


@pytest.mark.parametrize(
    "invalid_reason_codes",
    [
        ["CANDIDATE_ADMISSION_ACCEPTED"],
        (),
        ("lowercase",),
        ("HAS-HYPHEN",),
        ("1STARTS_WITH_NUMBER",),
        ("NON_ASCII_\u00c9",),
    ],
)
def test_reason_code_shape_and_vocabulary_fail_closed(
    invalid_reason_codes: object,
) -> None:
    expected_error = TypeError if isinstance(invalid_reason_codes, list) else ValueError
    with pytest.raises(expected_error):
        make_event(reason_codes=invalid_reason_codes)


def test_reason_codes_reject_duplicates() -> None:
    with pytest.raises(ValueError):
        make_event(reason_codes=("A_REASON", "A_REASON"))


def test_reason_codes_require_deterministic_ordering() -> None:
    with pytest.raises(ValueError):
        make_event(reason_codes=("Z_REASON", "A_REASON"))


@pytest.mark.parametrize(
    "invalid_contract",
    [
        ["GOVERNED_CREATIVE_WORKFLOW", "1.0"],
        ("GOVERNED_CREATIVE_WORKFLOW",),
        ("GOVERNED_CREATIVE_WORKFLOW", "1.0", "extra"),
    ],
)
def test_contract_reference_shape_fails_closed(
    invalid_contract: object,
) -> None:
    expected_error = TypeError if isinstance(invalid_contract, list) else ValueError
    with pytest.raises(expected_error):
        make_event(workflow_contract_reference=invalid_contract)


@pytest.mark.parametrize(
    "claim_field",
    [
        "executed_approval_claimed",
        "asset_admission_claimed",
        "lifecycle_mutation_claimed",
        "production_release_claimed",
    ],
)
def test_authority_claims_must_remain_false(claim_field: str) -> None:
    with pytest.raises(ValueError):
        make_event(**{claim_field: True})


@pytest.mark.parametrize(
    "claim_field",
    [
        "executed_approval_claimed",
        "asset_admission_claimed",
        "lifecycle_mutation_claimed",
        "production_release_claimed",
    ],
)
def test_authority_claims_must_be_boolean(claim_field: str) -> None:
    with pytest.raises(TypeError):
        make_event(**{claim_field: 0})


@pytest.mark.parametrize(
    "invalid_event_id",
    [
        "",
        "0" * 63,
        "G" * 64,
        "A" * 64,
    ],
)
def test_event_identity_requires_lowercase_sha256(
    invalid_event_id: str,
) -> None:
    with pytest.raises(ValueError):
        make_event(creative_workflow_event_id=invalid_event_id)


def test_event_identity_rejects_non_text() -> None:
    with pytest.raises(TypeError):
        make_event(creative_workflow_event_id=123)


def test_event_identity_rejects_mismatched_deterministic_value() -> None:
    with pytest.raises(ValueError):
        make_event(creative_workflow_event_id="0" * 64)


def test_identical_inputs_return_identical_event_identity() -> None:
    assert make_event().creative_workflow_event_id == (
        make_event().creative_workflow_event_id
    )


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    [
        ("workflow_request_reference", "workflow-request-002"),
        ("idempotency_key", "project-001:campaign-001:workflow-002"),
        ("prior_workflow_state", "INPUTS_VALIDATED"),
        ("resulting_workflow_state", "OPERATOR_REVIEW_PENDING"),
        ("creative_brief_reference", "brief-002"),
        (
            "instruction_reference",
            ("instruction-002", "APPROVED_INSTRUCTION"),
        ),
        (
            "responsible_actor_or_service_reference",
            ("ACCEPTED_SERVICE", "service-001"),
        ),
        (
            "event_timestamp",
            datetime(2026, 8, 4, 10, 31, tzinfo=timezone.utc),
        ),
        (
            "reason_codes",
            ("CANDIDATE_ADMISSION_ACCEPTED", "EVIDENCE_VALIDATED"),
        ),
        (
            "workflow_contract_reference",
            ("GOVERNED_CREATIVE_WORKFLOW", "1.1"),
        ),
    ],
)
def test_canonical_input_changes_event_identity(
    field_name: str,
    changed_value: object,
) -> None:
    original = make_event()
    changed = make_event(**{field_name: changed_value})
    assert changed.creative_workflow_event_id != (
        original.creative_workflow_event_id
    )


def test_coordinated_project_context_change_changes_event_identity() -> None:
    original = make_event()
    changed = make_event(
        project_context_reference="project-002",
        campaign_context_reference=("project-002", "campaign-001"),
        evidence_references=(
            ("project-002", "campaign-001", "candidate-001"),
            ("project-002", "campaign-001", "workflow-request-001"),
        ),
    )
    assert changed.creative_workflow_event_id != (
        original.creative_workflow_event_id
    )


def test_prior_and_resulting_states_must_differ() -> None:
    with pytest.raises(ValueError):
        make_event(
            prior_workflow_state="CANDIDATE_ADMITTED",
            resulting_workflow_state="CANDIDATE_ADMITTED",
        )


@pytest.mark.parametrize(
    "field_name",
    ["prior_workflow_state", "resulting_workflow_state"],
)
def test_workflow_states_reject_unknown_value(field_name: str) -> None:
    with pytest.raises(ValueError):
        make_event(**{field_name: "UNKNOWN"})


def test_model_source_has_no_ambient_clock_random_or_persistence_imports() -> None:
    source_text = Path(
        "src/rie/domain/creative_workflow_event.py"
    ).read_text(encoding="ascii")
    forbidden_imports = (
        "import os",
        "import random",
        "import time",
        "import uuid",
        "from os",
        "from random",
        "from time",
        "from uuid",
        "sqlite",
        "sqlalchemy",
        "requests",
    )
    assert not any(item in source_text for item in forbidden_imports)
