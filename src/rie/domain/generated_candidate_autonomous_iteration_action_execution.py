from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_SECRET_MARKERS = (
    "api_key",
    "authorization:",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
    "access_token",
)
_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES = (
    "memory:",
    "mutable:",
    "object:",
    "session:",
    "temp:",
)


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


def _require_exact_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an exact int")
    return value


def _require_immutable_reference(value: object, name: str) -> str:
    text = _require_ascii_nonempty(value, name)
    lowered = text.lower()
    if lowered.startswith(_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES):
        raise ValueError(f"{name} must be an immutable reference")
    if any(marker in lowered for marker in _FORBIDDEN_SECRET_MARKERS):
        raise ValueError(f"{name} must not contain secret material")
    return text


def _canonical_sha256(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def derive_autonomous_iteration_control_sha256(
    *,
    iteration_plan_reference: str,
    current_iteration_index: int,
    maximum_iteration_count: int,
    next_step_reference: str,
) -> str:
    plan_reference = _require_immutable_reference(
        iteration_plan_reference,
        "iteration_plan_reference",
    )
    current_index = _require_exact_int(
        current_iteration_index,
        "current_iteration_index",
    )
    maximum_count = _require_exact_int(
        maximum_iteration_count,
        "maximum_iteration_count",
    )
    next_reference = _require_immutable_reference(
        next_step_reference,
        "next_step_reference",
    )

    if current_index < 0:
        raise ValueError("current_iteration_index must be non-negative")
    if maximum_count <= 0:
        raise ValueError("maximum_iteration_count must be positive")
    if current_index >= maximum_count:
        raise ValueError(
            "current_iteration_index must be less than maximum_iteration_count"
        )

    return _canonical_sha256(
        {
            "iteration_plan_reference": plan_reference,
            "current_iteration_index": current_index,
            "maximum_iteration_count": maximum_count,
            "next_step_reference": next_reference,
        }
    )


def derive_generated_candidate_autonomous_iteration_action_execution_id(
    *,
    authorization_id: str,
    decision_id: str,
    evaluation_id: str,
    candidate_id: str,
    candidate_checksum: str,
    iteration_control_sha256: str,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> str:
    _require_sha256(authorization_id, "authorization_id")
    _require_ascii_nonempty(decision_id, "decision_id")
    _require_ascii_nonempty(evaluation_id, "evaluation_id")
    _require_ascii_nonempty(candidate_id, "candidate_id")
    _require_sha256(candidate_checksum, "candidate_checksum")
    _require_sha256(iteration_control_sha256, "iteration_control_sha256")
    actor_reference = _require_immutable_reference(
        execution_actor_reference,
        "execution_actor_reference",
    )
    timestamp = _require_aware_datetime(execution_timestamp, "execution_timestamp")

    return _canonical_sha256(
        {
            "authorization_id": authorization_id,
            "decision_id": decision_id,
            "evaluation_id": evaluation_id,
            "candidate_id": candidate_id,
            "candidate_checksum": candidate_checksum,
            "iteration_control_sha256": iteration_control_sha256,
            "execution_actor_reference": actor_reference,
            "execution_timestamp": timestamp.isoformat(),
        }
    )


@dataclass(frozen=True)
class GeneratedCandidateAutonomousIterationActionExecution:
    autonomous_iteration_action_execution_id: str
    authorization_id: str
    decision_id: str
    evaluation_id: str
    candidate_id: str
    candidate_checksum: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: str
    creative_brief_reference: str
    instruction_reference: str
    decision_outcome: str
    requested_action: str
    authorization_outcome: str
    iteration_plan_reference: str
    current_iteration_index: int
    maximum_iteration_count: int
    next_step_reference: str
    iteration_control_sha256: str
    execution_actor_reference: str
    execution_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(
            self.autonomous_iteration_action_execution_id,
            "autonomous_iteration_action_execution_id",
        )
        _require_sha256(self.authorization_id, "authorization_id")
        _require_ascii_nonempty(self.decision_id, "decision_id")
        _require_ascii_nonempty(self.evaluation_id, "evaluation_id")
        _require_ascii_nonempty(self.candidate_id, "candidate_id")
        _require_sha256(self.candidate_checksum, "candidate_checksum")
        _require_immutable_reference(
            self.workflow_request_reference,
            "workflow_request_reference",
        )
        _require_immutable_reference(
            self.project_context_reference,
            "project_context_reference",
        )
        _require_immutable_reference(
            self.campaign_context_reference,
            "campaign_context_reference",
        )
        _require_immutable_reference(
            self.creative_brief_reference,
            "creative_brief_reference",
        )
        _require_immutable_reference(
            self.instruction_reference,
            "instruction_reference",
        )
        _require_ascii_nonempty(self.decision_outcome, "decision_outcome")

        if self.requested_action != "AUTONOMOUS_ITERATION":
            raise ValueError("requested_action must be AUTONOMOUS_ITERATION")
        if self.authorization_outcome != "AUTHORIZED":
            raise ValueError("authorization_outcome must be AUTHORIZED")

        derived_control_sha = derive_autonomous_iteration_control_sha256(
            iteration_plan_reference=self.iteration_plan_reference,
            current_iteration_index=self.current_iteration_index,
            maximum_iteration_count=self.maximum_iteration_count,
            next_step_reference=self.next_step_reference,
        )
        if self.iteration_control_sha256 != derived_control_sha:
            raise ValueError("iteration_control_sha256 mismatch")

        _require_immutable_reference(
            self.execution_actor_reference,
            "execution_actor_reference",
        )
        _require_aware_datetime(self.execution_timestamp, "execution_timestamp")

        expected_id = (
            derive_generated_candidate_autonomous_iteration_action_execution_id(
                authorization_id=self.authorization_id,
                decision_id=self.decision_id,
                evaluation_id=self.evaluation_id,
                candidate_id=self.candidate_id,
                candidate_checksum=self.candidate_checksum,
                iteration_control_sha256=self.iteration_control_sha256,
                execution_actor_reference=self.execution_actor_reference,
                execution_timestamp=self.execution_timestamp,
            )
        )
        if self.autonomous_iteration_action_execution_id != expected_id:
            raise ValueError("autonomous iteration action execution identity mismatch")

        expected_provenance = (
            f"authorization_sha256:{self.authorization_id}",
            f"decision_id:{self.decision_id}",
            f"candidate_sha256:{self.candidate_checksum}",
            "requested_action:AUTONOMOUS_ITERATION",
            f"iteration_control_sha256:{self.iteration_control_sha256}",
            (
                "autonomous_iteration_action_execution_sha256:"
                f"{self.autonomous_iteration_action_execution_id}"
            ),
        )
        if self.deterministic_provenance != expected_provenance:
            raise ValueError("deterministic_provenance mismatch")


__all__ = [
    "GeneratedCandidateAutonomousIterationActionExecution",
    "derive_autonomous_iteration_control_sha256",
    "derive_generated_candidate_autonomous_iteration_action_execution_id",
]
