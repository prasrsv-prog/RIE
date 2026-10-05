from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re

from rie.domain.creative_result_candidate import CreativeResultCandidate
from rie.domain.generated_candidate_asset_admission_execution import (
    GeneratedCandidateAssetAdmissionExecution,
)
from rie.domain.generated_candidate_autonomous_iteration_action_execution import (
    GeneratedCandidateAutonomousIterationActionExecution,
)
from rie.domain.generated_candidate_decision import GeneratedCandidateDecision
from rie.domain.generated_candidate_decision_action_authorization import (
    AUTHORIZATION_OUTCOME_AUTHORIZED,
    GeneratedCandidateDecisionActionAuthorization,
)
from rie.domain.generated_candidate_evaluation import GeneratedCandidateEvaluation
from rie.domain.generated_candidate_retry_regeneration_action_execution import (
    GeneratedCandidateRetryRegenerationActionExecution,
)
from rie.domain.generated_candidate_workflow_transition_action_execution import (
    GeneratedCandidateWorkflowTransitionActionExecution,
)


BRANCH_OUTCOME_NO_ACTION = "NO_ACTION"

ActionExecution = (
    GeneratedCandidateAssetAdmissionExecution
    | GeneratedCandidateRetryRegenerationActionExecution
    | GeneratedCandidateWorkflowTransitionActionExecution
    | GeneratedCandidateAutonomousIterationActionExecution
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_AUDIT_MARKERS = (
    "access_token",
    "api_key",
    "authorization:",
    "bearer ",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
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


def _require_reference_tuple(value: object, name: str) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError(f"{name} must be a nonempty exact tuple")
    checked = tuple(
        _require_ascii_nonempty(item, f"{name}[{index}]")
        for index, item in enumerate(value)
    )
    if len(set(checked)) != len(checked):
        raise ValueError(f"{name} must not contain duplicates")
    return checked


def _require_safe_audit_message(value: object) -> str:
    text = _require_ascii_nonempty(value, "provider_audit_message")
    lowered = text.lower()
    if any(marker in lowered for marker in _FORBIDDEN_AUDIT_MARKERS):
        raise ValueError("provider_audit_message must not contain secret material")
    return text


def _action_execution_identity(
    action_execution: ActionExecution | None,
) -> tuple[str, str | None, tuple[str, ...]]:
    if action_execution is None:
        return ("NONE", None, ())

    if type(action_execution) is GeneratedCandidateAssetAdmissionExecution:
        return (
            "ASSET_ADMISSION",
            action_execution.asset_admission_execution_id,
            action_execution.deterministic_provenance,
        )
    if type(action_execution) is GeneratedCandidateRetryRegenerationActionExecution:
        return (
            "RETRY_REGENERATION",
            action_execution.retry_regeneration_action_execution_id,
            action_execution.deterministic_provenance,
        )
    if (
        type(action_execution)
        is GeneratedCandidateWorkflowTransitionActionExecution
    ):
        return (
            "WORKFLOW_TRANSITION",
            action_execution.workflow_transition_action_execution_id,
            action_execution.deterministic_provenance,
        )
    if (
        type(action_execution)
        is GeneratedCandidateAutonomousIterationActionExecution
    ):
        return (
            "AUTONOMOUS_ITERATION",
            action_execution.autonomous_iteration_action_execution_id,
            action_execution.deterministic_provenance,
        )
    raise ValueError("action_execution has an unsupported exact type")


def derive_autonomous_creative_generator_single_cycle_id(
    *,
    initial_generation_request_sha256: str,
    provider_id: str,
    model_id: str,
    provider_execution_status: str,
    provider_execution_reference: str,
    provider_output_refs: tuple[str, ...],
    provider_audit_message: str,
    candidate: CreativeResultCandidate,
    evaluation: GeneratedCandidateEvaluation,
    decision: GeneratedCandidateDecision,
    authorization: GeneratedCandidateDecisionActionAuthorization,
    action_execution: ActionExecution | None,
    branch_outcome: str,
    cycle_actor_reference: str,
    cycle_timestamp: datetime,
) -> str:
    request_sha = _require_sha256(
        initial_generation_request_sha256,
        "initial_generation_request_sha256",
    )
    provider = _require_ascii_nonempty(provider_id, "provider_id")
    model = _require_ascii_nonempty(model_id, "model_id")
    status = _require_ascii_nonempty(
        provider_execution_status,
        "provider_execution_status",
    )
    if status != "SUCCEEDED":
        raise ValueError("provider_execution_status must be SUCCEEDED")

    if type(provider_execution_reference) is not str:
        raise ValueError("provider_execution_reference must be an exact str")
    try:
        provider_execution_reference.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("provider_execution_reference must be ASCII") from exc

    outputs = _require_reference_tuple(provider_output_refs, "provider_output_refs")
    audit = _require_safe_audit_message(provider_audit_message)

    if type(candidate) is not CreativeResultCandidate:
        raise ValueError("candidate must be an exact CreativeResultCandidate")
    if type(evaluation) is not GeneratedCandidateEvaluation:
        raise ValueError("evaluation must be an exact GeneratedCandidateEvaluation")
    if type(decision) is not GeneratedCandidateDecision:
        raise ValueError("decision must be an exact GeneratedCandidateDecision")
    if (
        type(authorization)
        is not GeneratedCandidateDecisionActionAuthorization
    ):
        raise ValueError(
            "authorization must be an exact "
            "GeneratedCandidateDecisionActionAuthorization"
        )

    branch = _require_ascii_nonempty(branch_outcome, "branch_outcome")
    actor = _require_ascii_nonempty(cycle_actor_reference, "cycle_actor_reference")
    timestamp = _require_aware_datetime(cycle_timestamp, "cycle_timestamp")

    action_type, action_id, action_provenance = _action_execution_identity(
        action_execution
    )

    payload = {
        "initial_generation_request_sha256": request_sha,
        "provider_id": provider,
        "model_id": model,
        "provider_execution_status": status,
        "provider_execution_reference": provider_execution_reference,
        "provider_output_refs": list(outputs),
        "provider_audit_message": audit,
        "candidate_id": candidate.creative_result_candidate_id,
        "candidate_checksum": candidate.candidate_content_checksum,
        "candidate_deterministic_provenance": list(
            candidate.deterministic_provenance
        ),
        "evaluation_id": evaluation.evaluation_id,
        "evaluation_aggregate_outcome": evaluation.aggregate_outcome,
        "evaluation_deterministic_provenance": list(
            evaluation.deterministic_provenance
        ),
        "decision_id": decision.decision_id,
        "decision_outcome": decision.decision_outcome,
        "decision_deterministic_provenance": list(
            decision.deterministic_provenance
        ),
        "authorization_id": authorization.authorization_id,
        "requested_action": authorization.requested_action,
        "authorization_outcome": authorization.authorization_outcome,
        "authorization_deterministic_provenance": list(
            authorization.deterministic_provenance
        ),
        "action_execution_type": action_type,
        "action_execution_id": action_id,
        "action_execution_deterministic_provenance": list(action_provenance),
        "branch_outcome": branch,
        "cycle_actor_reference": actor,
        "cycle_timestamp": timestamp.isoformat(),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True, slots=True)
class AutonomousCreativeGeneratorSingleCycleResult:
    cycle_id: str
    initial_generation_request_sha256: str
    provider_id: str
    model_id: str
    provider_execution_status: str
    provider_execution_reference: str
    provider_output_refs: tuple[str, ...]
    provider_audit_message: str
    candidate: CreativeResultCandidate
    evaluation: GeneratedCandidateEvaluation
    decision: GeneratedCandidateDecision
    authorization: GeneratedCandidateDecisionActionAuthorization
    action_execution: ActionExecution | None
    branch_outcome: str
    cycle_actor_reference: str
    cycle_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(self.cycle_id, "cycle_id")
        _require_sha256(
            self.initial_generation_request_sha256,
            "initial_generation_request_sha256",
        )
        _require_ascii_nonempty(self.provider_id, "provider_id")
        _require_ascii_nonempty(self.model_id, "model_id")
        if self.provider_execution_status != "SUCCEEDED":
            raise ValueError("provider_execution_status must be SUCCEEDED")
        if type(self.provider_execution_reference) is not str:
            raise ValueError("provider_execution_reference must be an exact str")
        try:
            self.provider_execution_reference.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ValueError("provider_execution_reference must be ASCII") from exc
        _require_reference_tuple(self.provider_output_refs, "provider_output_refs")
        _require_safe_audit_message(self.provider_audit_message)
        _require_ascii_nonempty(self.branch_outcome, "branch_outcome")
        _require_ascii_nonempty(
            self.cycle_actor_reference,
            "cycle_actor_reference",
        )
        _require_aware_datetime(self.cycle_timestamp, "cycle_timestamp")

        if type(self.candidate) is not CreativeResultCandidate:
            raise ValueError("candidate must be an exact CreativeResultCandidate")
        if type(self.evaluation) is not GeneratedCandidateEvaluation:
            raise ValueError(
                "evaluation must be an exact GeneratedCandidateEvaluation"
            )
        if type(self.decision) is not GeneratedCandidateDecision:
            raise ValueError("decision must be an exact GeneratedCandidateDecision")
        if (
            type(self.authorization)
            is not GeneratedCandidateDecisionActionAuthorization
        ):
            raise ValueError(
                "authorization must be an exact "
                "GeneratedCandidateDecisionActionAuthorization"
            )

        if (
            self.evaluation.creative_result_candidate_id
            != self.candidate.creative_result_candidate_id
        ):
            raise ValueError("evaluation candidate identity mismatch")
        if (
            self.evaluation.candidate_content_checksum
            != self.candidate.candidate_content_checksum
        ):
            raise ValueError("evaluation candidate checksum mismatch")
        if self.decision.evaluation_id != self.evaluation.evaluation_id:
            raise ValueError("decision evaluation identity mismatch")
        if (
            self.decision.candidate_id
            != self.candidate.creative_result_candidate_id
        ):
            raise ValueError("decision candidate identity mismatch")
        if (
            self.decision.candidate_checksum
            != self.candidate.candidate_content_checksum
        ):
            raise ValueError("decision candidate checksum mismatch")
        if self.authorization.decision_id != self.decision.decision_id:
            raise ValueError("authorization decision identity mismatch")
        if self.authorization.evaluation_id != self.evaluation.evaluation_id:
            raise ValueError("authorization evaluation identity mismatch")
        if (
            self.authorization.candidate_id
            != self.candidate.creative_result_candidate_id
        ):
            raise ValueError("authorization candidate identity mismatch")
        if (
            self.authorization.candidate_checksum
            != self.candidate.candidate_content_checksum
        ):
            raise ValueError("authorization candidate checksum mismatch")

        action_type, _, _ = _action_execution_identity(self.action_execution)
        if (
            self.authorization.authorization_outcome
            != AUTHORIZATION_OUTCOME_AUTHORIZED
        ):
            if self.action_execution is not None:
                raise ValueError(
                    "non-AUTHORIZED authorization must not contain action execution"
                )
            if self.branch_outcome != BRANCH_OUTCOME_NO_ACTION:
                raise ValueError(
                    "non-AUTHORIZED authorization requires NO_ACTION branch"
                )
        else:
            if self.action_execution is None:
                raise ValueError(
                    "AUTHORIZED authorization requires one action execution"
                )
            if action_type != self.authorization.requested_action:
                raise ValueError(
                    "action execution type must match requested_action"
                )
            if self.branch_outcome != self.authorization.requested_action:
                raise ValueError(
                    "AUTHORIZED branch_outcome must match requested_action"
                )

            for field_name, expected in (
                ("authorization_id", self.authorization.authorization_id),
                ("decision_id", self.authorization.decision_id),
                ("evaluation_id", self.authorization.evaluation_id),
                ("candidate_id", self.authorization.candidate_id),
                ("candidate_checksum", self.authorization.candidate_checksum),
            ):
                actual = getattr(self.action_execution, field_name, None)
                if actual != expected:
                    raise ValueError(
                        f"action execution {field_name} lineage mismatch"
                    )

        expected_cycle_id = derive_autonomous_creative_generator_single_cycle_id(
            initial_generation_request_sha256=(
                self.initial_generation_request_sha256
            ),
            provider_id=self.provider_id,
            model_id=self.model_id,
            provider_execution_status=self.provider_execution_status,
            provider_execution_reference=self.provider_execution_reference,
            provider_output_refs=self.provider_output_refs,
            provider_audit_message=self.provider_audit_message,
            candidate=self.candidate,
            evaluation=self.evaluation,
            decision=self.decision,
            authorization=self.authorization,
            action_execution=self.action_execution,
            branch_outcome=self.branch_outcome,
            cycle_actor_reference=self.cycle_actor_reference,
            cycle_timestamp=self.cycle_timestamp,
        )
        if self.cycle_id != expected_cycle_id:
            raise ValueError("cycle_id deterministic identity mismatch")

        action_kind, action_id, _ = _action_execution_identity(
            self.action_execution
        )
        expected_provenance = (
            f"initial_generation_request_sha256:{self.initial_generation_request_sha256}",
            f"provider:{self.provider_id}",
            f"model:{self.model_id}",
            f"candidate:{self.candidate.creative_result_candidate_id}",
            f"candidate_sha256:{self.candidate.candidate_content_checksum}",
            f"evaluation:{self.evaluation.evaluation_id}",
            f"decision:{self.decision.decision_id}",
            f"authorization_sha256:{self.authorization.authorization_id}",
            f"branch_outcome:{self.branch_outcome}",
            (
                "action_execution:none"
                if action_id is None
                else f"action_execution:{action_kind}:{action_id}"
            ),
            f"cycle_sha256:{self.cycle_id}",
        )
        if self.deterministic_provenance != expected_provenance:
            raise ValueError("deterministic_provenance mismatch")


__all__ = [
    "ActionExecution",
    "AutonomousCreativeGeneratorSingleCycleResult",
    "BRANCH_OUTCOME_NO_ACTION",
    "derive_autonomous_creative_generator_single_cycle_id",
]
