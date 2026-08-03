from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Final, Literal, TypeAlias

CANDIDATE_AUTHORITY_STATE: Final = "CANDIDATE"
INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final = "PROMPT_CANDIDATE"
INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION: Final = "APPROVED_INSTRUCTION"

CandidateAuthorityState: TypeAlias = Literal["CANDIDATE"]
InstructionAuthorityState: TypeAlias = Literal[
    "PROMPT_CANDIDATE",
    "APPROVED_INSTRUCTION",
]
CampaignContextReference: TypeAlias = tuple[str, str]
InstructionReference: TypeAlias = tuple[str, InstructionAuthorityState]

ALLOWED_INSTRUCTION_AUTHORITY_STATES: Final = frozenset(
    {
        INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        INSTRUCTION_AUTHORITY_APPROVED_INSTRUCTION,
    }
)
ALLOWED_ARTIFACT_TYPES: Final = frozenset(
    {
        "ARCHIVE",
        "AUDIO",
        "DOCUMENT",
        "IMAGE",
        "VIDEO",
    }
)
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_TEXT_FIELDS: Final = (
    "creative_result_candidate_id",
    "workflow_request_reference",
    "project_context_reference",
    "creative_brief_reference",
    "admitting_actor_reference",
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
    *,
    require_non_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    if require_non_empty and not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _validate_required_ascii_text(f"{field_name}[{index}]", item)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must not contain duplicate references")
    return value


@dataclass(frozen=True)
class CreativeResultCandidate:
    """Minimum immutable Gate 18 creative-result candidate admission record."""

    creative_result_candidate_id: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: CampaignContextReference
    creative_brief_reference: str
    instruction_reference: InstructionReference
    originating_manual_handoff_reference: str | None
    candidate_content_checksum: str
    artifact_type: str
    admission_timestamp: datetime
    admitting_actor_reference: str
    deterministic_provenance: tuple[str, ...]
    authority_state: CandidateAuthorityState
    official_source_claimed: bool
    accepted_asset_claimed: bool
    approved_asset_claimed: bool

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

        if self.originating_manual_handoff_reference is not None:
            _validate_required_ascii_text(
                "originating_manual_handoff_reference",
                self.originating_manual_handoff_reference,
            )

        if not isinstance(self.candidate_content_checksum, str):
            raise TypeError("candidate_content_checksum must be text")
        if _SHA256_PATTERN.fullmatch(self.candidate_content_checksum) is None:
            raise ValueError(
                "candidate_content_checksum must be a lowercase SHA256 value"
            )

        if not isinstance(self.artifact_type, str):
            raise TypeError("artifact_type must be text")
        if self.artifact_type not in ALLOWED_ARTIFACT_TYPES:
            raise ValueError(
                "artifact_type must be one of ARCHIVE, AUDIO, DOCUMENT, "
                "IMAGE, or VIDEO"
            )

        if not isinstance(self.admission_timestamp, datetime):
            raise TypeError("admission_timestamp must be a datetime")
        if (
            self.admission_timestamp.tzinfo is None
            or self.admission_timestamp.utcoffset() is None
        ):
            raise ValueError("admission_timestamp must be timezone-aware")

        _validate_ascii_reference_tuple(
            "deterministic_provenance",
            self.deterministic_provenance,
            require_non_empty=True,
        )

        if self.authority_state != CANDIDATE_AUTHORITY_STATE:
            raise ValueError("authority_state must be exactly CANDIDATE")

        authority_claims = (
            ("official_source_claimed", self.official_source_claimed),
            ("accepted_asset_claimed", self.accepted_asset_claimed),
            ("approved_asset_claimed", self.approved_asset_claimed),
        )
        for field_name, value in authority_claims:
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean")
            if value:
                raise ValueError(
                    "candidate must not claim official-source, accepted-asset, "
                    "or approved-asset authority"
                )
