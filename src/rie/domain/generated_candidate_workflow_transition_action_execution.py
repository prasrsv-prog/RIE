from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
import hashlib
import json
import re

from rie.domain.evaluate_governed_creative_workflow_transition import (
    GovernedCreativeWorkflowTransitionEvaluation,
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


def _canonicalize(value: object) -> object:
    if is_dataclass(value):
        return {
            field.name: _canonicalize(getattr(value, field.name))
            for field in fields(value)
        }
    if type(value) is datetime:
        return value.isoformat()
    if type(value) is tuple:
        return [_canonicalize(item) for item in value]
    if value is None or type(value) in {str, bool, int, float}:
        return value
    raise ValueError(f"unsupported deterministic projection type: {type(value)!r}")


def derive_workflow_transition_evaluation_sha256(
    evaluation: GovernedCreativeWorkflowTransitionEvaluation,
) -> str:
    if type(evaluation) is not GovernedCreativeWorkflowTransitionEvaluation:
        raise ValueError(
            "evaluation must be an exact GovernedCreativeWorkflowTransitionEvaluation"
        )
    payload = json.dumps(
        _canonicalize(evaluation),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def derive_generated_candidate_workflow_transition_action_execution_id(
    *,
    authorization_id: str,
    decision_id: str,
    evaluation_id: str,
    candidate_id: str,
    candidate_checksum: str,
    requested_next_workflow_state: str,
    workflow_transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> str:
    identity_projection = {
        "authorization_id": _require_sha256(authorization_id, "authorization_id"),
        "decision_id": _require_ascii_nonempty(decision_id, "decision_id"),
        "evaluation_id": _require_ascii_nonempty(evaluation_id, "evaluation_id"),
        "candidate_id": _require_ascii_nonempty(candidate_id, "candidate_id"),
        "candidate_checksum": _require_sha256(
            candidate_checksum,
            "candidate_checksum",
        ),
        "requested_next_workflow_state": _require_ascii_nonempty(
            requested_next_workflow_state,
            "requested_next_workflow_state",
        ),
        "workflow_transition_evaluation_sha256": (
            derive_workflow_transition_evaluation_sha256(
                workflow_transition_evaluation
            )
        ),
        "execution_actor_reference": _require_ascii_nonempty(
            execution_actor_reference,
            "execution_actor_reference",
        ),
        "execution_timestamp": _require_aware_datetime(
            execution_timestamp,
            "execution_timestamp",
        ).isoformat(),
    }
    canonical = json.dumps(
        identity_projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class GeneratedCandidateWorkflowTransitionActionExecution:
    workflow_transition_action_execution_id: str
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
    requested_next_workflow_state: str
    execution_actor_reference: str
    execution_timestamp: datetime
    workflow_transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(
            self.workflow_transition_action_execution_id,
            "workflow_transition_action_execution_id",
        )
        _require_sha256(self.authorization_id, "authorization_id")
        _require_ascii_nonempty(self.decision_id, "decision_id")
        _require_ascii_nonempty(self.evaluation_id, "evaluation_id")
        _require_ascii_nonempty(self.candidate_id, "candidate_id")
        _require_sha256(self.candidate_checksum, "candidate_checksum")
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
        _require_ascii_nonempty(self.instruction_reference, "instruction_reference")
        _require_ascii_nonempty(self.decision_outcome, "decision_outcome")
        if self.requested_action != "WORKFLOW_TRANSITION":
            raise ValueError("requested_action must be WORKFLOW_TRANSITION")
        if self.authorization_outcome != "AUTHORIZED":
            raise ValueError("authorization_outcome must be AUTHORIZED")
        _require_ascii_nonempty(
            self.requested_next_workflow_state,
            "requested_next_workflow_state",
        )
        _require_ascii_nonempty(
            self.execution_actor_reference,
            "execution_actor_reference",
        )
        _require_aware_datetime(self.execution_timestamp, "execution_timestamp")
        if (
            type(self.workflow_transition_evaluation)
            is not GovernedCreativeWorkflowTransitionEvaluation
        ):
            raise ValueError(
                "workflow_transition_evaluation must be an exact "
                "GovernedCreativeWorkflowTransitionEvaluation"
            )

        expected_id = derive_generated_candidate_workflow_transition_action_execution_id(
            authorization_id=self.authorization_id,
            decision_id=self.decision_id,
            evaluation_id=self.evaluation_id,
            candidate_id=self.candidate_id,
            candidate_checksum=self.candidate_checksum,
            requested_next_workflow_state=self.requested_next_workflow_state,
            workflow_transition_evaluation=self.workflow_transition_evaluation,
            execution_actor_reference=self.execution_actor_reference,
            execution_timestamp=self.execution_timestamp,
        )
        if self.workflow_transition_action_execution_id != expected_id:
            raise ValueError("workflow transition action execution identity mismatch")

        evaluation_sha = derive_workflow_transition_evaluation_sha256(
            self.workflow_transition_evaluation
        )
        expected_provenance = (
            f"authorization_sha256:{self.authorization_id}",
            f"decision_id:{self.decision_id}",
            f"candidate_sha256:{self.candidate_checksum}",
            "requested_action:WORKFLOW_TRANSITION",
            f"workflow_transition_evaluation_sha256:{evaluation_sha}",
            (
                "workflow_transition_action_execution_sha256:"
                f"{self.workflow_transition_action_execution_id}"
            ),
        )
        if self.deterministic_provenance != expected_provenance:
            raise ValueError("deterministic_provenance mismatch")
