from dataclasses import FrozenInstanceError, MISSING, fields
from datetime import datetime, timezone

import pytest

from rie.domain.governed_creative_workflow_request import (
    ALLOWED_INSTRUCTION_AUTHORITY_STATES,
    INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
    GovernedCreativeWorkflowRequest,
)


def make_request(**overrides: object) -> GovernedCreativeWorkflowRequest:
    values: dict[str, object] = {
        "workflow_request_id": "workflow-request-001",
        "idempotency_key": "project-001:campaign-001:request-001",
        "project_context_reference": "project-001",
        "campaign_context_reference": ("project-001", "campaign-001"),
        "creative_brief_reference": "brief-001",
        "approved_knowledge_references": ("knowledge-001",),
        "governed_asset_references": ("asset-001",),
        "instruction_reference": (
            "instruction-001",
            INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        ),
        "requesting_actor_reference": "actor-001",
        "request_timestamp": datetime(
            2026,
            8,
            3,
            13,
            45,
            tzinfo=timezone.utc,
        ),
        "workflow_contract_reference": (
            "GOVERNED_CREATIVE_WORKFLOW",
            "1.0",
        ),
        "requested_output_purpose_code": "CAMPAIGN_CREATIVE",
        "requested_review_policy_reference": "review-policy-001",
        "manual_external_tool_handoff_declared": False,
    }
    values.update(overrides)
    return GovernedCreativeWorkflowRequest(**values)  # type: ignore[arg-type]


def test_contract_has_exactly_fourteen_required_fields() -> None:
    model_fields = fields(GovernedCreativeWorkflowRequest)

    assert tuple(field.name for field in model_fields) == (
        "workflow_request_id",
        "idempotency_key",
        "project_context_reference",
        "campaign_context_reference",
        "creative_brief_reference",
        "approved_knowledge_references",
        "governed_asset_references",
        "instruction_reference",
        "requesting_actor_reference",
        "request_timestamp",
        "workflow_contract_reference",
        "requested_output_purpose_code",
        "requested_review_policy_reference",
        "manual_external_tool_handoff_declared",
    )
    assert all(field.default is MISSING for field in model_fields)
    assert all(field.default_factory is MISSING for field in model_fields)


def test_instruction_authority_states_are_exact() -> None:
    assert ALLOWED_INSTRUCTION_AUTHORITY_STATES == {
        "PROMPT_CANDIDATE",
        "APPROVED_INSTRUCTION",
    }


@pytest.mark.parametrize(
    "authority_state",
    [
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    ],
)
def test_each_instruction_authority_state_is_accepted(
    authority_state: str,
) -> None:
    request = make_request(
        instruction_reference=("instruction-001", authority_state)
    )

    assert request.instruction_reference[1] == authority_state


@pytest.mark.parametrize("declared", [False, True])
def test_optional_manual_handoff_declaration_is_explicit_boolean(
    declared: bool,
) -> None:
    request = make_request(
        manual_external_tool_handoff_declared=declared,
    )

    assert request.manual_external_tool_handoff_declared is declared


def test_request_is_immutable() -> None:
    request = make_request()

    with pytest.raises(FrozenInstanceError):
        request.idempotency_key = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_id",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
        "requesting_actor_reference",
        "requested_output_purpose_code",
        "requested_review_policy_reference",
    ],
)
def test_required_text_fields_reject_non_text(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be text$"):
        make_request(**{field_name: 1})


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_id",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
        "requesting_actor_reference",
        "requested_output_purpose_code",
        "requested_review_policy_reference",
    ],
)
@pytest.mark.parametrize("value", ["", "   "])
def test_required_text_fields_reject_empty_text(
    field_name: str,
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must not be empty$",
    ):
        make_request(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_id",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
        "requesting_actor_reference",
        "requested_output_purpose_code",
        "requested_review_policy_reference",
    ],
)
def test_required_text_fields_reject_non_ascii(field_name: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must contain ASCII text only$",
    ):
        make_request(**{field_name: "value-" + chr(233)})


@pytest.mark.parametrize(
    "field_name",
    [
        "campaign_context_reference",
        "approved_knowledge_references",
        "governed_asset_references",
        "instruction_reference",
        "workflow_contract_reference",
    ],
)
def test_tuple_fields_reject_non_tuple(field_name: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field_name} must be a tuple$"):
        make_request(**{field_name: []})


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("campaign_context_reference", ("project-001",)),
        (
            "campaign_context_reference",
            ("project-001", "campaign-001", "extra"),
        ),
        ("instruction_reference", ("instruction-001",)),
        (
            "instruction_reference",
            (
                "instruction-001",
                INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
                "extra",
            ),
        ),
        ("workflow_contract_reference", ("GOVERNED_CREATIVE_WORKFLOW",)),
        (
            "workflow_contract_reference",
            ("GOVERNED_CREATIVE_WORKFLOW", "1.0", "extra"),
        ),
    ],
)
def test_exact_tuple_fields_reject_wrong_length(
    field_name: str,
    value: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="must contain exactly 2 values"):
        make_request(**{field_name: value})


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        (
            "campaign_context_reference",
            ("project-001", ""),
        ),
        (
            "instruction_reference",
            ("", INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE),
        ),
        (
            "workflow_contract_reference",
            ("GOVERNED_CREATIVE_WORKFLOW", ""),
        ),
        (
            "approved_knowledge_references",
            ("",),
        ),
        (
            "governed_asset_references",
            ("",),
        ),
    ],
)
def test_tuple_reference_values_reject_empty_text(
    field_name: str,
    value: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_request(**{field_name: value})


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        (
            "campaign_context_reference",
            ("project-001", "campaign-" + chr(233)),
        ),
        (
            "instruction_reference",
            (
                "instruction-" + chr(233),
                INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
            ),
        ),
        (
            "workflow_contract_reference",
            ("GOVERNED_CREATIVE_WORKFLOW", "version-" + chr(233)),
        ),
        (
            "approved_knowledge_references",
            ("knowledge-" + chr(233),),
        ),
        (
            "governed_asset_references",
            ("asset-" + chr(233),),
        ),
    ],
)
def test_tuple_reference_values_reject_non_ascii_text(
    field_name: str,
    value: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="must contain ASCII text only"):
        make_request(**{field_name: value})


def test_campaign_reference_must_bind_to_exact_project() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^campaign_context_reference project binding must match "
            "project_context_reference$"
        ),
    ):
        make_request(
            campaign_context_reference=("project-002", "campaign-001")
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "approved_knowledge_references",
        "governed_asset_references",
    ],
)
def test_reference_collections_allow_empty_tuple(field_name: str) -> None:
    request = make_request(**{field_name: ()})

    assert getattr(request, field_name) == ()


@pytest.mark.parametrize(
    "field_name",
    [
        "approved_knowledge_references",
        "governed_asset_references",
    ],
)
def test_reference_collections_reject_duplicates(field_name: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"^{field_name} must not contain duplicate references$",
    ):
        make_request(**{field_name: ("reference-001", "reference-001")})


@pytest.mark.parametrize(
    "authority_state",
    [
        "APPROVED",
        "PROMPT",
        "prompt_candidate",
        "UNKNOWN",
    ],
)
def test_instruction_reference_rejects_unknown_authority_state(
    authority_state: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^instruction_reference authority state must be "
            "PROMPT_CANDIDATE or APPROVED_INSTRUCTION$"
        ),
    ):
        make_request(
            instruction_reference=("instruction-001", authority_state)
        )


def test_request_timestamp_rejects_non_datetime() -> None:
    with pytest.raises(
        TypeError,
        match="^request_timestamp must be a datetime$",
    ):
        make_request(request_timestamp="2026-08-03T13:45:00+00:00")


def test_request_timestamp_rejects_naive_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="^request_timestamp must be timezone-aware$",
    ):
        make_request(request_timestamp=datetime(2026, 8, 3, 13, 45))


@pytest.mark.parametrize("invalid_value", [0, 1, "False", None])
def test_manual_handoff_declaration_rejects_non_boolean(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "^manual_external_tool_handoff_declared must be a boolean$"
        ),
    ):
        make_request(
            manual_external_tool_handoff_declared=invalid_value,
        )


def test_request_preserves_caller_supplied_timestamp_without_derivation() -> None:
    supplied_timestamp = datetime(
        2026,
        8,
        3,
        20,
        45,
        tzinfo=timezone.utc,
    )

    request = make_request(request_timestamp=supplied_timestamp)

    assert request.request_timestamp is supplied_timestamp


def test_request_preserves_exact_reference_order() -> None:
    knowledge_references = ("knowledge-002", "knowledge-001")
    asset_references = ("asset-002", "asset-001")

    request = make_request(
        approved_knowledge_references=knowledge_references,
        governed_asset_references=asset_references,
    )

    assert request.approved_knowledge_references == knowledge_references
    assert request.governed_asset_references == asset_references
