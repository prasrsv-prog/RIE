from __future__ import annotations

from dataclasses import dataclass, FrozenInstanceError
from datetime import datetime
import re

from rie.domain.generated_candidate_decision import DECISION_OUTCOMES


REQUESTED_ACTION_ASSET_ADMISSION = "ASSET_ADMISSION"
REQUESTED_ACTION_RETRY_REGENERATION = "RETRY_REGENERATION"
REQUESTED_ACTION_WORKFLOW_TRANSITION = "WORKFLOW_TRANSITION"
REQUESTED_ACTION_AUTONOMOUS_ITERATION = "AUTONOMOUS_ITERATION"

REQUESTED_ACTIONS = frozenset(
    {
        REQUESTED_ACTION_ASSET_ADMISSION,
        REQUESTED_ACTION_RETRY_REGENERATION,
        REQUESTED_ACTION_WORKFLOW_TRANSITION,
        REQUESTED_ACTION_AUTONOMOUS_ITERATION,
    }
)

AUTHORIZATION_OUTCOME_AUTHORIZED = "AUTHORIZED"
AUTHORIZATION_OUTCOME_DENIED = "DENIED"
AUTHORIZATION_OUTCOME_DEFERRED = "DEFERRED"

AUTHORIZATION_OUTCOMES = frozenset(
    {
        AUTHORIZATION_OUTCOME_AUTHORIZED,
        AUTHORIZATION_OUTCOME_DENIED,
        AUTHORIZATION_OUTCOME_DEFERRED,
    }
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_ascii_nonempty(value: object, name: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} must be an exact str")
    if not value or value != value.strip():
        raise ValueError(f"{name} must be nonempty with no surrounding whitespace")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be ASCII") from exc
    return value


def _require_sha256(value: object, name: str) -> str:
    text = _require_ascii_nonempty(value, name)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{name} must be a lowercase 64-hex SHA256")
    return text


def _require_aware_datetime(value: object, name: str) -> datetime:
    if type(value) is not datetime:
        raise ValueError(f"{name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _require_provenance(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError("deterministic_provenance must be a nonempty tuple")
    normalized: list[str] = []
    for index, entry in enumerate(value):
        normalized.append(
            _require_ascii_nonempty(
                entry,
                f"deterministic_provenance[{index}]",
            )
        )
    if len(set(normalized)) != len(normalized):
        raise ValueError("deterministic_provenance must not contain duplicates")
    return tuple(normalized)


@dataclass(frozen=True)
class GeneratedCandidateDecisionActionAuthorization:
    authorization_id: str
    decision_id: str
    evaluation_id: str
    candidate_id: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: str
    creative_brief_reference: str
    instruction_reference: str
    candidate_checksum: str
    artifact_type: str
    decision_outcome: str
    requested_action: str
    authorization_outcome: str
    authorization_reason_evidence_reference: str
    authorization_actor_reference: str
    authorization_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(self.authorization_id, "authorization_id")
        _require_ascii_nonempty(self.decision_id, "decision_id")
        _require_ascii_nonempty(self.evaluation_id, "evaluation_id")
        _require_ascii_nonempty(self.candidate_id, "candidate_id")
        _require_ascii_nonempty(
            self.workflow_request_reference,
            "workflow_request_reference",
        )
        _require_ascii_nonempty(
            self.project_context_reference,
            "project_context_reference",
        )
        _require_ascii_nonempty(
            self.campaign_context_reference,
            "campaign_context_reference",
        )
        _require_ascii_nonempty(
            self.creative_brief_reference,
            "creative_brief_reference",
        )
        _require_ascii_nonempty(
            self.instruction_reference,
            "instruction_reference",
        )
        _require_sha256(self.candidate_checksum, "candidate_checksum")
        _require_ascii_nonempty(self.artifact_type, "artifact_type")
        _require_ascii_nonempty(self.decision_outcome, "decision_outcome")
        if self.decision_outcome not in DECISION_OUTCOMES:
            raise ValueError("unsupported decision_outcome")
        _require_ascii_nonempty(self.requested_action, "requested_action")
        if self.requested_action not in REQUESTED_ACTIONS:
            raise ValueError("unsupported requested_action")
        _require_ascii_nonempty(
            self.authorization_outcome,
            "authorization_outcome",
        )
        if self.authorization_outcome not in AUTHORIZATION_OUTCOMES:
            raise ValueError("unsupported authorization_outcome")
        _require_ascii_nonempty(
            self.authorization_reason_evidence_reference,
            "authorization_reason_evidence_reference",
        )
        _require_ascii_nonempty(
            self.authorization_actor_reference,
            "authorization_actor_reference",
        )
        _require_aware_datetime(
            self.authorization_timestamp,
            "authorization_timestamp",
        )
        _require_provenance(self.deterministic_provenance)
