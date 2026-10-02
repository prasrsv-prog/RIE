from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re

from rie.domain.evaluate_governed_creative_workflow_transition import (
    GovernedCreativeWorkflowTransitionEvaluation,
)
from rie.domain.governed_creative_workflow_result import BoundReference


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


def _require_bound_reference(
    value: object,
    name: str,
) -> BoundReference:
    if type(value) is not tuple or len(value) != 3:
        raise ValueError(f"{name} must be an exact three-value tuple")
    normalized = tuple(
        _require_ascii_nonempty(item, f"{name}[{index}]")
        for index, item in enumerate(value)
    )
    return normalized  # type: ignore[return-value]


def derive_workflow_transition_evaluation_sha256(
    evaluation: GovernedCreativeWorkflowTransitionEvaluation,
) -> str:
    if type(evaluation) is not GovernedCreativeWorkflowTransitionEvaluation:
        raise ValueError(
            "evaluation must be an exact GovernedCreativeWorkflowTransitionEvaluation"
        )

    event_id = None
    if evaluation.creative_workflow_event is not None:
        event_id = evaluation.creative_workflow_event.creative_workflow_event_id

    result_event_reference = None
    if evaluation.governed_creative_workflow_result is not None:
        result_event_reference = list(
            evaluation.governed_creative_workflow_result.last_accepted_event_reference
        )

    projection = {
        "disposition": evaluation.disposition,
        "prior_workflow_state": evaluation.prior_workflow_state,
        "requested_workflow_state": evaluation.requested_workflow_state,
        "resulting_workflow_state": evaluation.resulting_workflow_state,
        "creative_workflow_event_id": event_id,
        "governed_result_last_event_reference": result_event_reference,
        "reason_codes": list(evaluation.reason_codes),
        "diagnostics": [list(item) for item in evaluation.diagnostics],
    }
    canonical = json.dumps(
        projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def derive_generated_candidate_asset_admission_workflow_transition_consumption_id(
    *,
    asset_admission_execution_id: str,
    admitted_asset_reference: str,
    accepted_governed_asset_reference: BoundReference,
    requested_workflow_state: str,
    workflow_transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation,
    consumption_actor_reference: str,
    consumption_timestamp: datetime,
) -> str:
    execution_id = _require_sha256(
        asset_admission_execution_id,
        "asset_admission_execution_id",
    )
    admitted_reference = _require_ascii_nonempty(
        admitted_asset_reference,
        "admitted_asset_reference",
    )
    bound_reference = _require_bound_reference(
        accepted_governed_asset_reference,
        "accepted_governed_asset_reference",
    )
    if bound_reference[2] != admitted_reference:
        raise ValueError(
            "accepted_governed_asset_reference identity must match "
            "admitted_asset_reference"
        )
    requested_state = _require_ascii_nonempty(
        requested_workflow_state,
        "requested_workflow_state",
    )
    actor = _require_ascii_nonempty(
        consumption_actor_reference,
        "consumption_actor_reference",
    )
    timestamp = _require_aware_datetime(
        consumption_timestamp,
        "consumption_timestamp",
    )
    evaluation_sha256 = derive_workflow_transition_evaluation_sha256(
        workflow_transition_evaluation
    )

    projection = {
        "asset_admission_execution_id": execution_id,
        "admitted_asset_reference": admitted_reference,
        "accepted_governed_asset_reference": list(bound_reference),
        "requested_workflow_state": requested_state,
        "workflow_transition_evaluation_sha256": evaluation_sha256,
        "consumption_actor_reference": actor,
        "consumption_timestamp": timestamp.isoformat(),
    }
    canonical = json.dumps(
        projection,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption:
    consumption_id: str
    asset_admission_execution_id: str
    admitted_asset_reference: str
    accepted_governed_asset_reference: BoundReference
    requested_workflow_state: str
    workflow_transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation
    consumption_actor_reference: str
    consumption_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(self.consumption_id, "consumption_id")
        _require_sha256(
            self.asset_admission_execution_id,
            "asset_admission_execution_id",
        )
        admitted_reference = _require_ascii_nonempty(
            self.admitted_asset_reference,
            "admitted_asset_reference",
        )
        bound_reference = _require_bound_reference(
            self.accepted_governed_asset_reference,
            "accepted_governed_asset_reference",
        )
        if bound_reference[2] != admitted_reference:
            raise ValueError(
                "accepted_governed_asset_reference identity must match "
                "admitted_asset_reference"
            )
        requested_state = _require_ascii_nonempty(
            self.requested_workflow_state,
            "requested_workflow_state",
        )
        if (
            type(self.workflow_transition_evaluation)
            is not GovernedCreativeWorkflowTransitionEvaluation
        ):
            raise ValueError(
                "workflow_transition_evaluation must be an exact "
                "GovernedCreativeWorkflowTransitionEvaluation"
            )
        if (
            self.workflow_transition_evaluation.requested_workflow_state
            != requested_state
        ):
            raise ValueError(
                "workflow_transition_evaluation requested state must match "
                "requested_workflow_state"
            )
        _require_ascii_nonempty(
            self.consumption_actor_reference,
            "consumption_actor_reference",
        )
        _require_aware_datetime(
            self.consumption_timestamp,
            "consumption_timestamp",
        )

        expected_id = (
            derive_generated_candidate_asset_admission_workflow_transition_consumption_id(
                asset_admission_execution_id=self.asset_admission_execution_id,
                admitted_asset_reference=self.admitted_asset_reference,
                accepted_governed_asset_reference=self.accepted_governed_asset_reference,
                requested_workflow_state=self.requested_workflow_state,
                workflow_transition_evaluation=self.workflow_transition_evaluation,
                consumption_actor_reference=self.consumption_actor_reference,
                consumption_timestamp=self.consumption_timestamp,
            )
        )
        if self.consumption_id != expected_id:
            raise ValueError("consumption_id must match deterministic inputs")

        if type(self.deterministic_provenance) is not tuple:
            raise ValueError("deterministic_provenance must be an exact tuple")
        evaluation_sha256 = derive_workflow_transition_evaluation_sha256(
            self.workflow_transition_evaluation
        )
        expected_provenance = (
            f"asset_admission_execution_sha256:{self.asset_admission_execution_id}",
            f"admitted_asset_reference:{self.admitted_asset_reference}",
            f"workflow_transition_evaluation_sha256:{evaluation_sha256}",
            f"requested_workflow_state:{self.requested_workflow_state}",
            f"consumption_sha256:{self.consumption_id}",
        )
        if self.deterministic_provenance != expected_provenance:
            raise ValueError(
                "deterministic_provenance must match exact consumption lineage"
            )


__all__ = [
    "GeneratedCandidateAssetAdmissionWorkflowTransitionConsumption",
    "derive_generated_candidate_asset_admission_workflow_transition_consumption_id",
    "derive_workflow_transition_evaluation_sha256",
]
