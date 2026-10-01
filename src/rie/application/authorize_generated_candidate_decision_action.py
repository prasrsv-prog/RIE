from __future__ import annotations

from datetime import datetime
import hashlib
import json

from rie.domain.generated_candidate_decision import GeneratedCandidateDecision
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOMES,
    REQUESTED_ACTIONS,
    GeneratedCandidateDecisionActionAuthorization,
)


_REQUIRED_DECISION_FIELDS = (
    "decision_id",
    "evaluation_id",
    "candidate_id",
    "workflow_request_reference",
    "project_context_reference",
    "campaign_context_reference",
    "creative_brief_reference",
    "instruction_reference",
    "candidate_checksum",
    "artifact_type",
    "decision_outcome",
    "deterministic_provenance",
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


def _require_aware_datetime(value: object, name: str) -> datetime:
    if type(value) is not datetime:
        raise ValueError(f"{name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _require_decision_field(
    decision: GeneratedCandidateDecision,
    name: str,
) -> object:
    if not hasattr(decision, name):
        raise ValueError(f"decision missing required field: {name}")
    return getattr(decision, name)


def _require_decision_provenance(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError("decision deterministic_provenance must be nonempty tuple")
    normalized: list[str] = []
    for index, entry in enumerate(value):
        normalized.append(
            _require_ascii_nonempty(
                entry,
                f"decision.deterministic_provenance[{index}]",
            )
        )
    if len(set(normalized)) != len(normalized):
        raise ValueError("decision deterministic_provenance must not contain duplicates")
    return tuple(normalized)


def authorize_generated_candidate_decision_action(
    decision: GeneratedCandidateDecision,
    *,
    requested_action: str,
    authorization_outcome: str,
    authorization_reason_evidence_reference: str,
    authorization_actor_reference: str,
    authorization_timestamp: datetime,
) -> GeneratedCandidateDecisionActionAuthorization:
    if type(decision) is not GeneratedCandidateDecision:
        raise ValueError("decision must be an exact GeneratedCandidateDecision")

    values = {
        name: _require_decision_field(decision, name)
        for name in _REQUIRED_DECISION_FIELDS
    }

    requested_action = _require_ascii_nonempty(
        requested_action,
        "requested_action",
    )
    if requested_action not in REQUESTED_ACTIONS:
        raise ValueError("unsupported requested_action")

    authorization_outcome = _require_ascii_nonempty(
        authorization_outcome,
        "authorization_outcome",
    )
    if authorization_outcome not in AUTHORIZATION_OUTCOMES:
        raise ValueError("unsupported authorization_outcome")

    authorization_reason_evidence_reference = _require_ascii_nonempty(
        authorization_reason_evidence_reference,
        "authorization_reason_evidence_reference",
    )
    authorization_actor_reference = _require_ascii_nonempty(
        authorization_actor_reference,
        "authorization_actor_reference",
    )
    authorization_timestamp = _require_aware_datetime(
        authorization_timestamp,
        "authorization_timestamp",
    )
    decision_provenance = _require_decision_provenance(
        values["deterministic_provenance"]
    )

    identity_projection = {
        "decision_id": values["decision_id"],
        "evaluation_id": values["evaluation_id"],
        "candidate_id": values["candidate_id"],
        "workflow_request_reference": values["workflow_request_reference"],
        "project_context_reference": values["project_context_reference"],
        "campaign_context_reference": values["campaign_context_reference"],
        "creative_brief_reference": values["creative_brief_reference"],
        "instruction_reference": values["instruction_reference"],
        "candidate_checksum": values["candidate_checksum"],
        "artifact_type": values["artifact_type"],
        "decision_outcome": values["decision_outcome"],
        "requested_action": requested_action,
        "authorization_outcome": authorization_outcome,
        "authorization_reason_evidence_reference": (
            authorization_reason_evidence_reference
        ),
        "authorization_actor_reference": authorization_actor_reference,
        "authorization_timestamp": authorization_timestamp.isoformat(),
        "decision_deterministic_provenance": list(decision_provenance),
    }
    canonical = json.dumps(
        identity_projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    authorization_id = hashlib.sha256(canonical).hexdigest()

    authorization_provenance = (
        f"candidate_sha256:{values['candidate_checksum']}",
        f"evaluation_id:{values['evaluation_id']}",
        f"decision_id:{values['decision_id']}",
        f"requested_action:{requested_action}",
        f"authorization_sha256:{authorization_id}",
    )

    return GeneratedCandidateDecisionActionAuthorization(
        authorization_id=authorization_id,
        decision_id=values["decision_id"],
        evaluation_id=values["evaluation_id"],
        candidate_id=values["candidate_id"],
        workflow_request_reference=values["workflow_request_reference"],
        project_context_reference=values["project_context_reference"],
        campaign_context_reference=values["campaign_context_reference"],
        creative_brief_reference=values["creative_brief_reference"],
        instruction_reference=values["instruction_reference"],
        candidate_checksum=values["candidate_checksum"],
        artifact_type=values["artifact_type"],
        decision_outcome=values["decision_outcome"],
        requested_action=requested_action,
        authorization_outcome=authorization_outcome,
        authorization_reason_evidence_reference=(
            authorization_reason_evidence_reference
        ),
        authorization_actor_reference=authorization_actor_reference,
        authorization_timestamp=authorization_timestamp,
        deterministic_provenance=authorization_provenance,
    )
