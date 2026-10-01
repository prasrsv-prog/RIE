from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re


ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
DEFERRED = "DEFERRED"
DECISION_OUTCOMES = (ACCEPTED, REJECTED, DEFERRED)
EVALUATION_OUTCOMES = ("passed", "failed", "deferred")

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_ascii_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    if not value or value.strip() != value:
        raise ValueError(f"{field_name} must be nonempty without surrounding whitespace")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{field_name} must be ASCII") from exc
    return value


def _require_sha256(value: object, field_name: str) -> str:
    text = _require_ascii_text(value, field_name)
    if _SHA256_RE.fullmatch(text) is None:
        raise ValueError(f"{field_name} must be an exact lowercase SHA-256")
    return text


def _require_timezone_aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _require_provenance(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple) or not value:
        raise ValueError("deterministic_provenance must be a nonempty tuple")
    checked = tuple(
        _require_ascii_text(entry, "deterministic_provenance entry")
        for entry in value
    )
    if len(set(checked)) != len(checked):
        raise ValueError("deterministic_provenance entries must be unique")
    return checked


@dataclass(frozen=True)
class GeneratedCandidateDecision:
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
    evaluation_aggregate_outcome: str
    decision_outcome: str
    decision_reason_evidence_reference: str
    decision_actor_reference: str
    decision_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(self.decision_id, "decision_id")
        _require_ascii_text(self.evaluation_id, "evaluation_id")
        _require_ascii_text(self.candidate_id, "candidate_id")
        _require_ascii_text(
            self.workflow_request_reference, "workflow_request_reference"
        )
        _require_ascii_text(
            self.project_context_reference, "project_context_reference"
        )
        _require_ascii_text(
            self.campaign_context_reference, "campaign_context_reference"
        )
        _require_ascii_text(
            self.creative_brief_reference, "creative_brief_reference"
        )
        _require_ascii_text(self.instruction_reference, "instruction_reference")
        _require_sha256(self.candidate_checksum, "candidate_checksum")
        _require_ascii_text(self.artifact_type, "artifact_type")
        if self.evaluation_aggregate_outcome not in EVALUATION_OUTCOMES:
            raise ValueError("evaluation_aggregate_outcome is uncontrolled")
        if self.decision_outcome not in DECISION_OUTCOMES:
            raise ValueError("decision_outcome is uncontrolled")
        _require_ascii_text(
            self.decision_reason_evidence_reference,
            "decision_reason_evidence_reference",
        )
        _require_ascii_text(
            self.decision_actor_reference, "decision_actor_reference"
        )
        _require_timezone_aware(self.decision_timestamp, "decision_timestamp")
        _require_provenance(self.deterministic_provenance)
