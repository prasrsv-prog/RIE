from __future__ import annotations

from datetime import datetime
import hashlib
import json

from rie.domain.generated_candidate_decision import (
    DECISION_OUTCOMES,
    GeneratedCandidateDecision,
)
from rie.domain.generated_candidate_evaluation import GeneratedCandidateEvaluation


_REQUIRED_EVALUATION_FIELDS = (
    "evaluation_id",
    "candidate_id",
    "workflow_request_reference",
    "project_context_reference",
    "campaign_context_reference",
    "creative_brief_reference",
    "instruction_reference",
    "candidate_checksum",
    "artifact_type",
    "aggregate_outcome",
    "deterministic_provenance",
)


def _evaluation_value(evaluation: GeneratedCandidateEvaluation, name: str) -> object:
    if not hasattr(evaluation, name):
        raise ValueError(f"evaluation missing required field: {name}")
    return getattr(evaluation, name)


def _canonical_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise ValueError("decision_timestamp must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("decision_timestamp must be timezone-aware")
    return value.isoformat()


def decide_generated_candidate(
    *,
    evaluation: GeneratedCandidateEvaluation,
    decision_outcome: str,
    decision_reason_evidence_reference: str,
    decision_actor_reference: str,
    decision_timestamp: datetime,
) -> GeneratedCandidateDecision:
    if type(evaluation) is not GeneratedCandidateEvaluation:
        raise ValueError("exact GeneratedCandidateEvaluation is required")
    for field_name in _REQUIRED_EVALUATION_FIELDS:
        _evaluation_value(evaluation, field_name)
    if decision_outcome not in DECISION_OUTCOMES:
        raise ValueError("decision_outcome is uncontrolled")
    if not isinstance(decision_reason_evidence_reference, str):
        raise ValueError("decision_reason_evidence_reference must be a string")
    if not isinstance(decision_actor_reference, str):
        raise ValueError("decision_actor_reference must be a string")

    evaluation_provenance = _evaluation_value(
        evaluation, "deterministic_provenance"
    )
    if not isinstance(evaluation_provenance, tuple) or not evaluation_provenance:
        raise ValueError("evaluation deterministic_provenance must be nonempty")

    timestamp_text = _canonical_timestamp(decision_timestamp)
    identity_payload = {
        "artifact_type": _evaluation_value(evaluation, "artifact_type"),
        "campaign_context_reference": _evaluation_value(
            evaluation, "campaign_context_reference"
        ),
        "candidate_checksum": _evaluation_value(evaluation, "candidate_checksum"),
        "candidate_id": _evaluation_value(evaluation, "candidate_id"),
        "creative_brief_reference": _evaluation_value(
            evaluation, "creative_brief_reference"
        ),
        "decision_actor_reference": decision_actor_reference,
        "decision_outcome": decision_outcome,
        "decision_reason_evidence_reference": decision_reason_evidence_reference,
        "decision_timestamp": timestamp_text,
        "evaluation_aggregate_outcome": _evaluation_value(
            evaluation, "aggregate_outcome"
        ),
        "evaluation_deterministic_provenance": list(evaluation_provenance),
        "evaluation_id": _evaluation_value(evaluation, "evaluation_id"),
        "instruction_reference": _evaluation_value(
            evaluation, "instruction_reference"
        ),
        "project_context_reference": _evaluation_value(
            evaluation, "project_context_reference"
        ),
        "workflow_request_reference": _evaluation_value(
            evaluation, "workflow_request_reference"
        ),
    }
    canonical = json.dumps(
        identity_payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    decision_id = hashlib.sha256(canonical).hexdigest()

    provenance = (
        f"candidate:{identity_payload['candidate_id']}",
        f"evaluation:{identity_payload['evaluation_id']}",
        f"decision_sha256:{decision_id}",
    )

    return GeneratedCandidateDecision(
        decision_id=decision_id,
        evaluation_id=identity_payload["evaluation_id"],
        candidate_id=identity_payload["candidate_id"],
        workflow_request_reference=identity_payload[
            "workflow_request_reference"
        ],
        project_context_reference=identity_payload[
            "project_context_reference"
        ],
        campaign_context_reference=identity_payload[
            "campaign_context_reference"
        ],
        creative_brief_reference=identity_payload["creative_brief_reference"],
        instruction_reference=identity_payload["instruction_reference"],
        candidate_checksum=identity_payload["candidate_checksum"],
        artifact_type=identity_payload["artifact_type"],
        evaluation_aggregate_outcome=identity_payload[
            "evaluation_aggregate_outcome"
        ],
        decision_outcome=decision_outcome,
        decision_reason_evidence_reference=decision_reason_evidence_reference,
        decision_actor_reference=decision_actor_reference,
        decision_timestamp=decision_timestamp,
        deterministic_provenance=provenance,
    )
