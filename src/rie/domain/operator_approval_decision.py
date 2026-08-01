from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

ACTION_APPROVE: Final = "APPROVE"
ACTION_REJECT: Final = "REJECT"

TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY: Final = (
    "OFFICIAL_SOURCE_REGISTRY_ENTRY"
)
TARGET_TYPE_INGESTION_JOB: Final = "INGESTION_JOB"
TARGET_TYPE_EVIDENCE: Final = "EVIDENCE"
TARGET_TYPE_KNOWLEDGE: Final = "KNOWLEDGE"
TARGET_TYPE_KNOWLEDGE_CONFLICT: Final = "KNOWLEDGE_CONFLICT"
TARGET_TYPE_PROMPT_CANDIDATE: Final = "PROMPT_CANDIDATE"
TARGET_TYPE_GOVERNED_ASSET_RECORD: Final = "GOVERNED_ASSET_RECORD"

ApprovalAction: TypeAlias = Literal["APPROVE", "REJECT"]
ApprovalTargetType: TypeAlias = Literal[
    "OFFICIAL_SOURCE_REGISTRY_ENTRY",
    "INGESTION_JOB",
    "EVIDENCE",
    "KNOWLEDGE",
    "KNOWLEDGE_CONFLICT",
    "PROMPT_CANDIDATE",
    "GOVERNED_ASSET_RECORD",
]

ALLOWED_ACTIONS: Final = frozenset(
    {
        ACTION_APPROVE,
        ACTION_REJECT,
    }
)
ALLOWED_TARGET_TYPES: Final = frozenset(
    {
        TARGET_TYPE_OFFICIAL_SOURCE_REGISTRY_ENTRY,
        TARGET_TYPE_INGESTION_JOB,
        TARGET_TYPE_EVIDENCE,
        TARGET_TYPE_KNOWLEDGE,
        TARGET_TYPE_KNOWLEDGE_CONFLICT,
        TARGET_TYPE_PROMPT_CANDIDATE,
        TARGET_TYPE_GOVERNED_ASSET_RECORD,
    }
)

_REQUIRED_TEXT_FIELDS: Final = (
    "decision_id",
    "operator_reference",
    "role_reference",
    "target_type",
    "target_reference",
    "action",
    "reason_reference",
    "audit_context_reference",
)


def _validate_required_ascii_text(field_name: str, value: object) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")


@dataclass(frozen=True)
class OperatorApprovalDecision:
    """Minimum immutable Gate 16 operator approval decision."""

    decision_id: str
    operator_reference: str
    role_reference: str
    target_type: ApprovalTargetType
    target_reference: str
    action: ApprovalAction
    reason_reference: str
    audit_context_reference: str

    def __post_init__(self) -> None:
        for field_name in _REQUIRED_TEXT_FIELDS:
            _validate_required_ascii_text(
                field_name,
                getattr(self, field_name),
            )

        if self.target_type not in ALLOWED_TARGET_TYPES:
            raise ValueError(
                "target_type must be one of "
                "OFFICIAL_SOURCE_REGISTRY_ENTRY, INGESTION_JOB, EVIDENCE, "
                "KNOWLEDGE, KNOWLEDGE_CONFLICT, PROMPT_CANDIDATE, or "
                "GOVERNED_ASSET_RECORD"
            )

        if self.action not in ALLOWED_ACTIONS:
            raise ValueError("action must be APPROVE or REJECT")
