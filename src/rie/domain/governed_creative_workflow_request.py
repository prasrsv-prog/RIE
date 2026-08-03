from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final, Literal, TypeAlias

INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final = "PROMPT_CANDIDATE"
INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION: Final = "APPROVED_INSTRUCTION"
InstructionAuthorityState: TypeAlias = Literal[
    "PROMPT_CANDIDATE",
    "APPROVED_INSTRUCTION",
]
InstructionReference: TypeAlias = tuple[str, InstructionAuthorityState]
CampaignContextReference: TypeAlias = tuple[str, str]
WorkflowContractReference: TypeAlias = tuple[str, str]

ALLOWED_INSTRUCTION_AUTHORITY_STATES: Final = frozenset(
    {
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    }
)
_REQUIRED_TEXT_FIELDS: Final = (
    "workflow_request_id",
    "idempotency_key",
    "project_context_reference",
    "creative_brief_reference",
    "requesting_actor_reference",
    "requested_output_purpose_code",
    "requested_review_policy_reference",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")


def _validate_exact_ascii_tuple(
    field_name: str,
    value: object,
    *,
    expected_length: int,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    if len(value) != expected_length:
        raise ValueError(
            f"{field_name} must contain exactly {expected_length} values"
        )
    for index, item in enumerate(value):
        _validate_required_ascii_text(f"{field_name}[{index}]", item)
    return value


def _validate_ascii_reference_tuple(
    field_name: str,
    value: object,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    for index, item in enumerate(value):
        _validate_required_ascii_text(f"{field_name}[{index}]", item)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must not contain duplicate references")
    return value


@dataclass(frozen=True)
class GovernedCreativeWorkflowRequest:
    """Minimum immutable Gate 18 governed creative-workflow request."""

    workflow_request_id: str
    idempotency_key: str
    project_context_reference: str
    campaign_context_reference: CampaignContextReference
    creative_brief_reference: str
    approved_knowledge_references: tuple[str, ...]
    governed_asset_references: tuple[str, ...]
    instruction_reference: InstructionReference
    requesting_actor_reference: str
    request_timestamp: datetime
    workflow_contract_reference: WorkflowContractReference
    requested_output_purpose_code: str
    requested_review_policy_reference: str
    manual_external_tool_handoff_declared: bool

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_required_ascii_text(field_name, getattr(self, field_name))

        campaign_reference = _validate_exact_ascii_tuple(
            "campaign_context_reference",
            self.campaign_context_reference,
            expected_length=2,
        )
        if campaign_reference[0] != self.project_context_reference:
            raise ValueError(
                "campaign_context_reference project binding must match "
                "project_context_reference"
            )

        _validate_ascii_reference_tuple(
            "approved_knowledge_references",
            self.approved_knowledge_references,
        )
        _validate_ascii_reference_tuple(
            "governed_asset_references",
            self.governed_asset_references,
        )

        instruction_reference = _validate_exact_ascii_tuple(
            "instruction_reference",
            self.instruction_reference,
            expected_length=2,
        )
        if instruction_reference[1] not in ALLOWED_INSTRUCTION_AUTHORITY_STATES:
            raise ValueError(
                "instruction_reference authority state must be "
                "PROMPT_CANDIDATE or APPROVED_INSTRUCTION"
            )

        if not isinstance(self.request_timestamp, datetime):
            raise TypeError("request_timestamp must be a datetime")
        if (
            self.request_timestamp.tzinfo is None
            or self.request_timestamp.utcoffset() is None
        ):
            raise ValueError("request_timestamp must be timezone-aware")

        _validate_exact_ascii_tuple(
            "workflow_contract_reference",
            self.workflow_contract_reference,
            expected_length=2,
        )

        if not isinstance(self.manual_external_tool_handoff_declared, bool):
            raise TypeError(
                "manual_external_tool_handoff_declared must be a boolean"
            )
