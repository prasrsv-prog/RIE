from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final, Literal, TypeAlias

INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final = "PROMPT_CANDIDATE"
INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION: Final = "APPROVED_INSTRUCTION"

InstructionAuthorityState: TypeAlias = Literal[
    "PROMPT_CANDIDATE",
    "APPROVED_INSTRUCTION",
]
FinalWorkflowState: TypeAlias = Literal[
    "COMPLETED",
    "REJECTED",
    "SAFE_STOP",
]
CampaignContextReference: TypeAlias = tuple[str, str]
InstructionReference: TypeAlias = tuple[str, InstructionAuthorityState]
BoundReference: TypeAlias = tuple[str, str, str]
DiagnosticEntry: TypeAlias = tuple[str, str]
WorkflowContractReference: TypeAlias = tuple[str, str]

ALLOWED_INSTRUCTION_AUTHORITY_STATES: Final = frozenset(
    {
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    }
)
ALLOWED_FINAL_WORKFLOW_STATES: Final = frozenset(
    {
        "COMPLETED",
        "REJECTED",
        "SAFE_STOP",
    }
)
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_DETERMINISTIC_CODE_PATTERN: Final = re.compile(r"^[A-Z][A-Z0-9_]*$")
_FORBIDDEN_SECRET_MARKERS: Final = (
    "access_token",
    "api_key",
    "authorization:",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
)
_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES: Final = (
    "memory:",
    "mutable:",
    "object:",
    "session:",
    "temp:",
)
_REQUIRED_TEXT_FIELDS: Final = (
    "workflow_request_reference",
    "idempotency_key",
    "project_context_reference",
    "creative_brief_reference",
)


def _validate_required_ascii_text(field_name: str, value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{field_name} must not contain control characters")
    return value


def _validate_reference_text(field_name: str, value: object) -> str:
    text = _validate_required_ascii_text(field_name, value)
    lowered = text.lower()
    if any(marker in lowered for marker in _FORBIDDEN_SECRET_MARKERS):
        raise ValueError(f"{field_name} must not contain secret material")
    if lowered.startswith(_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES):
        raise ValueError(f"{field_name} must be an immutable reference")
    return text


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
    return tuple(
        _validate_reference_text(f"{field_name}[{index}]", item)
        for index, item in enumerate(value)
    )


def _validate_bound_reference(
    field_name: str,
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
    require_sha256_identity: bool,
) -> BoundReference:
    validated = _validate_exact_ascii_tuple(
        field_name,
        value,
        expected_length=3,
    )
    if validated[0] != project_reference:
        raise ValueError(
            f"{field_name} project binding must match "
            "project_context_reference"
        )
    if validated[1] != campaign_reference:
        raise ValueError(
            f"{field_name} campaign binding must match "
            "campaign_context_reference"
        )
    if (
        require_sha256_identity
        and _SHA256_PATTERN.fullmatch(validated[2]) is None
    ):
        raise ValueError(
            f"{field_name} identity must be a lowercase SHA256 value"
        )
    return validated


def _validate_optional_bound_reference(
    field_name: str,
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
) -> BoundReference | None:
    if value is None:
        return None
    return _validate_bound_reference(
        field_name,
        value,
        project_reference=project_reference,
        campaign_reference=campaign_reference,
        require_sha256_identity=False,
    )


def _validate_reason_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("reason_codes must be a tuple")
    if not value:
        raise ValueError("reason_codes must not be empty")
    validated = tuple(
        _validate_required_ascii_text(f"reason_codes[{index}]", item)
        for index, item in enumerate(value)
    )
    if any(
        _DETERMINISTIC_CODE_PATTERN.fullmatch(item) is None
        for item in validated
    ):
        raise ValueError("reason_codes must use uppercase deterministic codes")
    if len(set(validated)) != len(validated):
        raise ValueError("reason_codes must not contain duplicates")
    if validated != tuple(sorted(validated)):
        raise ValueError("reason_codes must use deterministic ordering")
    return validated


def _validate_diagnostics(value: object) -> tuple[DiagnosticEntry, ...]:
    if not isinstance(value, tuple):
        raise TypeError("diagnostics must be a tuple")
    normalized: list[DiagnosticEntry] = []
    for index, item in enumerate(value):
        validated = _validate_exact_ascii_tuple(
            f"diagnostics[{index}]",
            item,
            expected_length=2,
        )
        if _DETERMINISTIC_CODE_PATTERN.fullmatch(validated[0]) is None:
            raise ValueError(
                "diagnostic codes must use uppercase deterministic codes"
            )
        normalized.append(validated)
    normalized_tuple = tuple(normalized)
    if len(set(normalized_tuple)) != len(normalized_tuple):
        raise ValueError("diagnostics must not contain duplicates")
    if normalized_tuple != tuple(sorted(normalized_tuple)):
        raise ValueError("diagnostics must use deterministic ordering")
    return normalized_tuple


@dataclass(frozen=True)
class GovernedCreativeWorkflowResult:
    """Minimum immutable Gate 18 governed creative-workflow result."""

    workflow_request_reference: str
    idempotency_key: str
    project_context_reference: str
    campaign_context_reference: CampaignContextReference
    creative_brief_reference: str
    instruction_reference: InstructionReference
    final_workflow_state: FinalWorkflowState
    last_accepted_event_reference: BoundReference
    manual_external_tool_handoff_reference: BoundReference | None
    creative_result_candidate_reference: BoundReference | None
    accepted_operator_decision_reference: BoundReference | None
    accepted_governed_asset_reference: BoundReference | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[DiagnosticEntry, ...]
    workflow_contract_reference: WorkflowContractReference
    production_release_claimed: bool

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_reference_text(field_name, getattr(self, field_name))

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

        if self.final_workflow_state not in ALLOWED_FINAL_WORKFLOW_STATES:
            raise ValueError("final_workflow_state is unsupported")

        campaign_id = campaign_reference[1]
        _validate_bound_reference(
            "last_accepted_event_reference",
            self.last_accepted_event_reference,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_id,
            require_sha256_identity=True,
        )
        handoff_reference = _validate_optional_bound_reference(
            "manual_external_tool_handoff_reference",
            self.manual_external_tool_handoff_reference,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_id,
        )
        candidate_reference = _validate_optional_bound_reference(
            "creative_result_candidate_reference",
            self.creative_result_candidate_reference,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_id,
        )
        operator_decision_reference = _validate_optional_bound_reference(
            "accepted_operator_decision_reference",
            self.accepted_operator_decision_reference,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_id,
        )
        governed_asset_reference = _validate_optional_bound_reference(
            "accepted_governed_asset_reference",
            self.accepted_governed_asset_reference,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_id,
        )

        _validate_reason_codes(self.reason_codes)
        _validate_diagnostics(self.diagnostics)
        _validate_exact_ascii_tuple(
            "workflow_contract_reference",
            self.workflow_contract_reference,
            expected_length=2,
        )

        if self.final_workflow_state == "COMPLETED":
            if operator_decision_reference is None:
                raise ValueError(
                    "COMPLETED requires accepted operator decision reference"
                )
            if governed_asset_reference is None:
                raise ValueError(
                    "COMPLETED requires accepted governed asset reference"
                )
        else:
            if operator_decision_reference is not None:
                raise ValueError(
                    "REJECTED and SAFE_STOP must not fabricate "
                    "accepted operator decision reference"
                )
            if governed_asset_reference is not None:
                raise ValueError(
                    "REJECTED and SAFE_STOP must not fabricate "
                    "accepted governed asset reference"
                )

        if handoff_reference is not None and candidate_reference is None:
            if self.final_workflow_state == "COMPLETED":
                raise ValueError(
                    "COMPLETED handoff result requires candidate reference"
                )

        if not isinstance(self.production_release_claimed, bool):
            raise TypeError("production_release_claimed must be a boolean")
        if self.production_release_claimed:
            raise ValueError(
                "production_release_claimed must remain false for a "
                "governed workflow result"
            )
