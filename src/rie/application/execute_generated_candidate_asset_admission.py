from __future__ import annotations

from datetime import datetime
import hashlib
import json

from rie.domain.creative_result_candidate import (
    CANDIDATE_AUTHORITY_STATE,
    CreativeResultCandidate,
)
from rie.domain.generated_candidate_asset_admission_execution import (
    ADMISSION_OUTCOME_ADMITTED,
    GeneratedCandidateAssetAdmissionExecution,
)
from rie.domain.generated_candidate_decision import ACCEPTED
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    REQUESTED_ACTION_ASSET_ADMISSION,
    GeneratedCandidateDecisionActionAuthorization,
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


def execute_generated_candidate_asset_admission(
    authorization: GeneratedCandidateDecisionActionAuthorization,
    candidate: CreativeResultCandidate,
    *,
    admitted_asset_reference: str,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> GeneratedCandidateAssetAdmissionExecution:
    if type(authorization) is not GeneratedCandidateDecisionActionAuthorization:
        raise ValueError(
            "authorization must be an exact "
            "GeneratedCandidateDecisionActionAuthorization"
        )
    if type(candidate) is not CreativeResultCandidate:
        raise ValueError("candidate must be an exact CreativeResultCandidate")

    if authorization.requested_action != REQUESTED_ACTION_ASSET_ADMISSION:
        raise ValueError("authorization requested_action must be ASSET_ADMISSION")
    if authorization.authorization_outcome != AUTHORIZATION_OUTCOME_AUTHORIZED:
        raise ValueError("authorization outcome must be AUTHORIZED")
    if authorization.decision_outcome != ACCEPTED:
        raise ValueError("bound decision outcome must be ACCEPTED")

    if candidate.authority_state != CANDIDATE_AUTHORITY_STATE:
        raise ValueError("candidate authority_state must remain CANDIDATE")
    if (
        candidate.official_source_claimed
        or candidate.accepted_asset_claimed
        or candidate.approved_asset_claimed
    ):
        raise ValueError("candidate must not already claim elevated asset authority")

    if authorization.candidate_id != candidate.creative_result_candidate_id:
        raise ValueError("authorization candidate identity mismatch")
    if authorization.candidate_checksum != candidate.candidate_content_checksum:
        raise ValueError("authorization candidate checksum mismatch")
    if authorization.workflow_request_reference != candidate.workflow_request_reference:
        raise ValueError("authorization workflow request mismatch")
    if authorization.project_context_reference != candidate.project_context_reference:
        raise ValueError("authorization project context mismatch")
    if authorization.artifact_type != candidate.artifact_type:
        raise ValueError("authorization artifact type mismatch")

    expected_authorization_provenance = (
        f"candidate_sha256:{authorization.candidate_checksum}",
        f"evaluation_id:{authorization.evaluation_id}",
        f"decision_id:{authorization.decision_id}",
        f"requested_action:{REQUESTED_ACTION_ASSET_ADMISSION}",
        f"authorization_sha256:{authorization.authorization_id}",
    )
    if authorization.deterministic_provenance != expected_authorization_provenance:
        raise ValueError("authorization deterministic provenance mismatch")

    admitted_asset_reference = _require_ascii_nonempty(
        admitted_asset_reference,
        "admitted_asset_reference",
    )
    execution_actor_reference = _require_ascii_nonempty(
        execution_actor_reference,
        "execution_actor_reference",
    )
    execution_timestamp = _require_aware_datetime(
        execution_timestamp,
        "execution_timestamp",
    )

    identity_projection = {
        "authorization_id": authorization.authorization_id,
        "decision_id": authorization.decision_id,
        "evaluation_id": authorization.evaluation_id,
        "candidate_id": authorization.candidate_id,
        "candidate_checksum": authorization.candidate_checksum,
        "candidate_deterministic_provenance": list(
            candidate.deterministic_provenance
        ),
        "admitted_asset_reference": admitted_asset_reference,
        "execution_actor_reference": execution_actor_reference,
        "execution_timestamp": execution_timestamp.isoformat(),
        "execution_outcome": ADMISSION_OUTCOME_ADMITTED,
    }
    canonical = json.dumps(
        identity_projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    execution_id = hashlib.sha256(canonical).hexdigest()

    provenance = (
        f"candidate_sha256:{authorization.candidate_checksum}",
        f"evaluation_id:{authorization.evaluation_id}",
        f"decision_id:{authorization.decision_id}",
        f"authorization_sha256:{authorization.authorization_id}",
        f"admitted_asset_reference:{admitted_asset_reference}",
        f"asset_admission_execution_sha256:{execution_id}",
    )

    return GeneratedCandidateAssetAdmissionExecution(
        asset_admission_execution_id=execution_id,
        authorization_id=authorization.authorization_id,
        decision_id=authorization.decision_id,
        evaluation_id=authorization.evaluation_id,
        candidate_id=authorization.candidate_id,
        candidate_checksum=authorization.candidate_checksum,
        admitted_asset_reference=admitted_asset_reference,
        execution_actor_reference=execution_actor_reference,
        execution_timestamp=execution_timestamp,
        execution_outcome=ADMISSION_OUTCOME_ADMITTED,
        deterministic_provenance=provenance,
    )


__all__ = ["execute_generated_candidate_asset_admission"]
