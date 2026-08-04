from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Final, Literal, TypeAlias

INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final = "PROMPT_CANDIDATE"
INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION: Final = "APPROVED_INSTRUCTION"
RESPONSIBLE_REFERENCE_ACTOR: Final = "ACTOR"
RESPONSIBLE_REFERENCE_ACCEPTED_SERVICE: Final = "ACCEPTED_SERVICE"

InstructionAuthorityState: TypeAlias = Literal[
    "PROMPT_CANDIDATE",
    "APPROVED_INSTRUCTION",
]
WorkflowState: TypeAlias = Literal[
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
]
ResponsibleReferenceKind: TypeAlias = Literal["ACTOR", "ACCEPTED_SERVICE"]
CampaignContextReference: TypeAlias = tuple[str, str]
InstructionReference: TypeAlias = tuple[str, InstructionAuthorityState]
ResponsibleActorOrServiceReference: TypeAlias = tuple[
    ResponsibleReferenceKind,
    str,
]
EvidenceReference: TypeAlias = tuple[str, str, str]
WorkflowContractReference: TypeAlias = tuple[str, str]

ALLOWED_INSTRUCTION_AUTHORITY_STATES: Final = frozenset(
    {
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    }
)
ALLOWED_WORKFLOW_STATES: Final = frozenset(
    {
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
)
ALLOWED_RESPONSIBLE_REFERENCE_KINDS: Final = frozenset(
    {
        RESPONSIBLE_REFERENCE_ACTOR,
        RESPONSIBLE_REFERENCE_ACCEPTED_SERVICE,
    }
)
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_REASON_CODE_PATTERN: Final = re.compile(r"^[A-Z][A-Z0-9_]*$")
_FORBIDDEN_SECRET_MARKERS: Final = (
    "api_key",
    "authorization:",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
    "access_token",
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
    for index, item in enumerate(value):
        _validate_reference_text(f"{field_name}[{index}]", item)
    return value


def _validate_evidence_references(
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
) -> tuple[EvidenceReference, ...]:
    if not isinstance(value, tuple):
        raise TypeError("evidence_references must be a tuple")
    if not value:
        raise ValueError("evidence_references must not be empty")
    normalized: list[EvidenceReference] = []
    for index, item in enumerate(value):
        if not isinstance(item, tuple):
            raise TypeError(f"evidence_references[{index}] must be a tuple")
        if len(item) != 3:
            raise ValueError(
                f"evidence_references[{index}] must contain exactly 3 values"
            )
        validated = tuple(
            _validate_reference_text(
                f"evidence_references[{index}][{item_index}]",
                item_value,
            )
            for item_index, item_value in enumerate(item)
        )
        if validated[0] != project_reference:
            raise ValueError(
                "evidence reference project binding must match "
                "project_context_reference"
            )
        if validated[1] != campaign_reference:
            raise ValueError(
                "evidence reference campaign binding must match "
                "campaign_context_reference"
            )
        normalized.append(validated)
    normalized_tuple = tuple(normalized)
    if len(set(normalized_tuple)) != len(normalized_tuple):
        raise ValueError("evidence_references must not contain duplicates")
    if normalized_tuple != tuple(sorted(normalized_tuple)):
        raise ValueError("evidence_references must use deterministic ordering")
    return normalized_tuple


def _validate_reason_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("reason_codes must be a tuple")
    if not value:
        raise ValueError("reason_codes must not be empty")
    validated = tuple(
        _validate_required_ascii_text(f"reason_codes[{index}]", item)
        for index, item in enumerate(value)
    )
    if any(_REASON_CODE_PATTERN.fullmatch(item) is None for item in validated):
        raise ValueError("reason_codes must use uppercase deterministic codes")
    if len(set(validated)) != len(validated):
        raise ValueError("reason_codes must not contain duplicates")
    if validated != tuple(sorted(validated)):
        raise ValueError("reason_codes must use deterministic ordering")
    return validated


def derive_creative_workflow_event_id(
    *,
    workflow_request_reference: str,
    idempotency_key: str,
    prior_workflow_state: str,
    resulting_workflow_state: str,
    project_context_reference: str,
    campaign_context_reference: CampaignContextReference,
    creative_brief_reference: str,
    instruction_reference: InstructionReference,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    event_timestamp: datetime,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
) -> str:
    canonical_payload = {
        "campaign_context_reference": list(campaign_context_reference),
        "creative_brief_reference": creative_brief_reference,
        "event_timestamp": event_timestamp.isoformat(),
        "evidence_references": [list(item) for item in evidence_references],
        "idempotency_key": idempotency_key,
        "instruction_reference": list(instruction_reference),
        "prior_workflow_state": prior_workflow_state,
        "project_context_reference": project_context_reference,
        "reason_codes": list(reason_codes),
        "responsible_actor_or_service_reference": list(
            responsible_actor_or_service_reference
        ),
        "resulting_workflow_state": resulting_workflow_state,
        "workflow_contract_reference": list(workflow_contract_reference),
        "workflow_request_reference": workflow_request_reference,
    }
    canonical_bytes = json.dumps(
        canonical_payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(canonical_bytes).hexdigest()


@dataclass(frozen=True)
class CreativeWorkflowEvent:
    """Minimum immutable Gate 18 accepted-transition audit event."""

    creative_workflow_event_id: str
    workflow_request_reference: str
    idempotency_key: str
    prior_workflow_state: WorkflowState
    resulting_workflow_state: WorkflowState
    project_context_reference: str
    campaign_context_reference: CampaignContextReference
    creative_brief_reference: str
    instruction_reference: InstructionReference
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference
    event_timestamp: datetime
    evidence_references: tuple[EvidenceReference, ...]
    reason_codes: tuple[str, ...]
    workflow_contract_reference: WorkflowContractReference
    executed_approval_claimed: bool
    asset_admission_claimed: bool
    lifecycle_mutation_claimed: bool
    production_release_claimed: bool

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_reference_text(field_name, getattr(self, field_name))

        if self.prior_workflow_state not in ALLOWED_WORKFLOW_STATES:
            raise ValueError("prior_workflow_state is unsupported")
        if self.resulting_workflow_state not in ALLOWED_WORKFLOW_STATES:
            raise ValueError("resulting_workflow_state is unsupported")
        if self.prior_workflow_state == self.resulting_workflow_state:
            raise ValueError("workflow event must record a state transition")

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

        responsible_reference = _validate_exact_ascii_tuple(
            "responsible_actor_or_service_reference",
            self.responsible_actor_or_service_reference,
            expected_length=2,
        )
        if responsible_reference[0] not in ALLOWED_RESPONSIBLE_REFERENCE_KINDS:
            raise ValueError(
                "responsible reference kind must be ACTOR or ACCEPTED_SERVICE"
            )

        if not isinstance(self.event_timestamp, datetime):
            raise TypeError("event_timestamp must be a datetime")
        if (
            self.event_timestamp.tzinfo is None
            or self.event_timestamp.utcoffset() is None
        ):
            raise ValueError("event_timestamp must be timezone-aware")

        evidence_references = _validate_evidence_references(
            self.evidence_references,
            project_reference=self.project_context_reference,
            campaign_reference=campaign_reference[1],
        )
        reason_codes = _validate_reason_codes(self.reason_codes)

        _validate_exact_ascii_tuple(
            "workflow_contract_reference",
            self.workflow_contract_reference,
            expected_length=2,
        )

        for field_name in (
            "executed_approval_claimed",
            "asset_admission_claimed",
            "lifecycle_mutation_claimed",
            "production_release_claimed",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean")
            if value:
                raise ValueError(
                    f"{field_name} must remain false for an audit event"
                )

        if not isinstance(self.creative_workflow_event_id, str):
            raise TypeError("creative_workflow_event_id must be text")
        if _SHA256_PATTERN.fullmatch(self.creative_workflow_event_id) is None:
            raise ValueError(
                "creative_workflow_event_id must be a lowercase SHA256 value"
            )

        expected_event_id = derive_creative_workflow_event_id(
            workflow_request_reference=self.workflow_request_reference,
            idempotency_key=self.idempotency_key,
            prior_workflow_state=self.prior_workflow_state,
            resulting_workflow_state=self.resulting_workflow_state,
            project_context_reference=self.project_context_reference,
            campaign_context_reference=campaign_reference,
            creative_brief_reference=self.creative_brief_reference,
            instruction_reference=instruction_reference,
            responsible_actor_or_service_reference=responsible_reference,
            event_timestamp=self.event_timestamp,
            evidence_references=evidence_references,
            reason_codes=reason_codes,
            workflow_contract_reference=self.workflow_contract_reference,
        )
        if self.creative_workflow_event_id != expected_event_id:
            raise ValueError(
                "creative_workflow_event_id must match deterministic event data"
            )
