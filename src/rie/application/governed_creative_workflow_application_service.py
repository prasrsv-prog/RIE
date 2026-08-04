from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Final, TypeAlias

from rie.domain.creative_workflow_event import (
    ALLOWED_WORKFLOW_STATES,
    CreativeWorkflowEvent,
    EvidenceReference,
    ResponsibleActorOrServiceReference,
    WorkflowContractReference,
    WorkflowState,
)
from rie.domain.evaluate_governed_creative_workflow_transition import (
    GovernedCreativeWorkflowTransitionEvaluation,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.governed_creative_workflow_request import (
    GovernedCreativeWorkflowRequest,
)
from rie.domain.governed_creative_workflow_result import (
    BoundReference,
    GovernedCreativeWorkflowResult,
)

CampaignContextReference: TypeAlias = tuple[str, str]

_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_SECRET_MARKERS: Final = (
    "access_token",
    "api_key",
    "authorization:",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
)
_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES: Final = (
    "memory:",
    "mutable:",
    "object:",
    "session:",
    "temp:",
)


def _validate_required_ascii_text(field_name: str, value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text")
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    if not value.isascii():
        raise ValueError(f"{field_name} must contain ASCII text only")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{field_name} must not contain control characters")
    return value


def _validate_reference_text(field_name: str, value: object) -> str:
    text = _validate_required_ascii_text(field_name, value)
    lowered = text.lower()
    if any(marker in lowered for marker in _FORBIDDEN_SECRET_MARKERS):
        raise ValueError(f"{field_name} must not contain secret material")
    if lowered.startswith(_FORBIDDEN_MUTABLE_REFERENCE_PREFIXES):
        raise ValueError(f"{field_name} must be an immutable reference")
    return text


def _validate_exact_reference_tuple(
    field_name: str,
    value: object,
    *,
    expected_length: int,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    if len(value) != expected_length:
        raise ValueError(
            f"{field_name} must contain exactly {expected_length} values"
        )
    return tuple(
        _validate_reference_text(f"{field_name}[{index}]", item)
        for index, item in enumerate(value)
    )


def _validate_optional_bound_reference(
    field_name: str,
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
) -> BoundReference | None:
    if value is None:
        return None
    validated = _validate_exact_reference_tuple(
        field_name,
        value,
        expected_length=3,
    )
    if validated[0] != project_reference:
        raise ValueError(
            f"{field_name} project binding must match workflow project"
        )
    if validated[1] != campaign_reference:
        raise ValueError(
            f"{field_name} campaign binding must match workflow campaign"
        )
    return validated


def _canonicalize(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canonicalize(item) for item in value]
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _canonicalize(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonicalize(getattr(value, field.name))
            for field in fields(value)
        }
    if value is None or isinstance(value, (bool, int, str)):
        return value
    raise TypeError(
        f"unsupported canonical application-assessment value: "
        f"{type(value).__name__}"
    )


def derive_governed_creative_workflow_application_input_fingerprint(
    *,
    workflow_request: GovernedCreativeWorkflowRequest,
    current_workflow_state: WorkflowState,
    requested_next_workflow_state: WorkflowState,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    assessment_timestamp: datetime,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
    manual_external_tool_handoff_reference: BoundReference | None,
    creative_result_candidate_reference: BoundReference | None,
    accepted_gate_16_operator_decision_reference: BoundReference | None,
    accepted_gate_15_governed_asset_reference: BoundReference | None,
    recovery_last_accepted_state: WorkflowState | None,
    recovery_last_accepted_event_reference: BoundReference | None,
    recovery_reason_code: str | None,
) -> str:
    """Derive one deterministic fingerprint from explicit assessment inputs."""

    payload = {
        "accepted_gate_15_governed_asset_reference": (
            accepted_gate_15_governed_asset_reference
        ),
        "accepted_gate_16_operator_decision_reference": (
            accepted_gate_16_operator_decision_reference
        ),
        "assessment_timestamp": assessment_timestamp,
        "creative_result_candidate_reference": (
            creative_result_candidate_reference
        ),
        "current_workflow_state": current_workflow_state,
        "evidence_references": evidence_references,
        "manual_external_tool_handoff_reference": (
            manual_external_tool_handoff_reference
        ),
        "reason_codes": reason_codes,
        "recovery_last_accepted_event_reference": (
            recovery_last_accepted_event_reference
        ),
        "recovery_last_accepted_state": recovery_last_accepted_state,
        "recovery_reason_code": recovery_reason_code,
        "requested_next_workflow_state": requested_next_workflow_state,
        "responsible_actor_or_service_reference": (
            responsible_actor_or_service_reference
        ),
        "workflow_contract_reference": workflow_contract_reference,
        "workflow_request": workflow_request,
    }
    canonical_bytes = json.dumps(
        _canonicalize(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(canonical_bytes).hexdigest()


def derive_governed_creative_workflow_application_assessment_fingerprint(
    *,
    canonical_input_fingerprint: str,
    transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation,
    accepted_gate_15_governed_asset_reference: BoundReference | None,
    accepted_gate_16_operator_decision_reference: BoundReference | None,
) -> str:
    """Derive one deterministic fingerprint for the immutable assessment."""

    if _SHA256_PATTERN.fullmatch(canonical_input_fingerprint) is None:
        raise ValueError(
            "canonical_input_fingerprint must be a lowercase SHA256 value"
        )
    payload = {
        "accepted_gate_15_governed_asset_reference": (
            accepted_gate_15_governed_asset_reference
        ),
        "accepted_gate_16_operator_decision_reference": (
            accepted_gate_16_operator_decision_reference
        ),
        "canonical_input_fingerprint": canonical_input_fingerprint,
        "transition_evaluation": transition_evaluation,
    }
    canonical_bytes = json.dumps(
        _canonicalize(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(canonical_bytes).hexdigest()


@dataclass(frozen=True)
class GovernedCreativeWorkflowApplicationAssessment:
    """Immutable stateless Gate 18 application-service assessment."""

    assessment_fingerprint: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: CampaignContextReference
    current_workflow_state: WorkflowState
    requested_workflow_state: WorkflowState
    accepted_gate_15_governed_asset_reference: BoundReference | None
    accepted_gate_16_operator_decision_reference: BoundReference | None
    transition_evaluation: GovernedCreativeWorkflowTransitionEvaluation
    creative_workflow_event: CreativeWorkflowEvent | None
    governed_creative_workflow_result: GovernedCreativeWorkflowResult | None
    production_release_claimed: bool

    def __post_init__(self) -> None:
        if _SHA256_PATTERN.fullmatch(self.assessment_fingerprint) is None:
            raise ValueError(
                "assessment_fingerprint must be a lowercase SHA256 value"
            )
        _validate_reference_text(
            "workflow_request_reference",
            self.workflow_request_reference,
        )
        project_reference = _validate_reference_text(
            "project_context_reference",
            self.project_context_reference,
        )
        campaign_reference = _validate_exact_reference_tuple(
            "campaign_context_reference",
            self.campaign_context_reference,
            expected_length=2,
        )
        if campaign_reference[0] != project_reference:
            raise ValueError(
                "campaign_context_reference project binding must match "
                "project_context_reference"
            )
        if self.current_workflow_state not in ALLOWED_WORKFLOW_STATES:
            raise ValueError("current_workflow_state is unsupported")
        if self.requested_workflow_state not in ALLOWED_WORKFLOW_STATES:
            raise ValueError("requested_workflow_state is unsupported")

        _validate_optional_bound_reference(
            "accepted_gate_15_governed_asset_reference",
            self.accepted_gate_15_governed_asset_reference,
            project_reference=project_reference,
            campaign_reference=campaign_reference[1],
        )
        _validate_optional_bound_reference(
            "accepted_gate_16_operator_decision_reference",
            self.accepted_gate_16_operator_decision_reference,
            project_reference=project_reference,
            campaign_reference=campaign_reference[1],
        )

        if not isinstance(
            self.transition_evaluation,
            GovernedCreativeWorkflowTransitionEvaluation,
        ):
            raise TypeError(
                "transition_evaluation must be a "
                "GovernedCreativeWorkflowTransitionEvaluation"
            )
        if (
            self.transition_evaluation.prior_workflow_state
            != self.current_workflow_state
        ):
            raise ValueError(
                "transition_evaluation prior state must match assessment"
            )
        if (
            self.transition_evaluation.requested_workflow_state
            != self.requested_workflow_state
        ):
            raise ValueError(
                "transition_evaluation requested state must match assessment"
            )
        if (
            self.creative_workflow_event
            != self.transition_evaluation.creative_workflow_event
        ):
            raise ValueError(
                "creative_workflow_event must match transition evaluation"
            )
        if (
            self.governed_creative_workflow_result
            != self.transition_evaluation.governed_creative_workflow_result
        ):
            raise ValueError(
                "governed_creative_workflow_result must match transition "
                "evaluation"
            )
        if not isinstance(self.production_release_claimed, bool):
            raise TypeError("production_release_claimed must be a boolean")
        if self.production_release_claimed:
            raise ValueError(
                "application assessment must not claim production release"
            )


def assess_governed_creative_workflow(
    *,
    workflow_request: GovernedCreativeWorkflowRequest,
    current_workflow_state: WorkflowState,
    requested_next_workflow_state: WorkflowState,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    assessment_timestamp: datetime,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
    manual_external_tool_handoff_reference: BoundReference | None = None,
    creative_result_candidate_reference: BoundReference | None = None,
    accepted_gate_16_operator_decision_reference: BoundReference | None = None,
    accepted_gate_15_governed_asset_reference: BoundReference | None = None,
    existing_idempotency_fingerprint: str | None = None,
    recovery_last_accepted_state: WorkflowState | None = None,
    recovery_last_accepted_event_reference: BoundReference | None = None,
    recovery_reason_code: str | None = None,
) -> GovernedCreativeWorkflowApplicationAssessment:
    """Assess one Gate 18 transition without executing external authority."""

    if not isinstance(workflow_request, GovernedCreativeWorkflowRequest):
        raise TypeError(
            "workflow_request must be a GovernedCreativeWorkflowRequest"
        )
    if current_workflow_state not in ALLOWED_WORKFLOW_STATES:
        raise ValueError("current_workflow_state is unsupported")
    if requested_next_workflow_state not in ALLOWED_WORKFLOW_STATES:
        raise ValueError("requested_next_workflow_state is unsupported")
    if not isinstance(assessment_timestamp, datetime):
        raise TypeError("assessment_timestamp must be a datetime")
    if (
        assessment_timestamp.tzinfo is None
        or assessment_timestamp.utcoffset() is None
    ):
        raise ValueError("assessment_timestamp must be timezone-aware")
    if assessment_timestamp < workflow_request.request_timestamp:
        raise ValueError(
            "assessment_timestamp must not precede request_timestamp"
        )

    contract_reference = _validate_exact_reference_tuple(
        "workflow_contract_reference",
        workflow_contract_reference,
        expected_length=2,
    )
    if contract_reference != workflow_request.workflow_contract_reference:
        raise ValueError(
            "workflow_contract_reference must match workflow request"
        )

    responsible_reference = _validate_exact_reference_tuple(
        "responsible_actor_or_service_reference",
        responsible_actor_or_service_reference,
        expected_length=2,
    )
    if responsible_reference[0] not in {"ACTOR", "ACCEPTED_SERVICE"}:
        raise ValueError(
            "responsible reference kind must be ACTOR or ACCEPTED_SERVICE"
        )
    if (
        responsible_reference[0] == "ACTOR"
        and responsible_reference[1]
        != workflow_request.requesting_actor_reference
    ):
        raise ValueError(
            "ACTOR responsibility must match requesting_actor_reference"
        )

    campaign_id = workflow_request.campaign_context_reference[1]
    handoff_reference = _validate_optional_bound_reference(
        "manual_external_tool_handoff_reference",
        manual_external_tool_handoff_reference,
        project_reference=workflow_request.project_context_reference,
        campaign_reference=campaign_id,
    )
    if (
        handoff_reference is not None
        and not workflow_request.manual_external_tool_handoff_declared
    ):
        raise ValueError(
            "manual handoff reference requires a declared external handoff"
        )
    candidate_reference = _validate_optional_bound_reference(
        "creative_result_candidate_reference",
        creative_result_candidate_reference,
        project_reference=workflow_request.project_context_reference,
        campaign_reference=campaign_id,
    )
    operator_reference = _validate_optional_bound_reference(
        "accepted_gate_16_operator_decision_reference",
        accepted_gate_16_operator_decision_reference,
        project_reference=workflow_request.project_context_reference,
        campaign_reference=campaign_id,
    )
    asset_reference = _validate_optional_bound_reference(
        "accepted_gate_15_governed_asset_reference",
        accepted_gate_15_governed_asset_reference,
        project_reference=workflow_request.project_context_reference,
        campaign_reference=campaign_id,
    )
    recovery_event_reference = _validate_optional_bound_reference(
        "recovery_last_accepted_event_reference",
        recovery_last_accepted_event_reference,
        project_reference=workflow_request.project_context_reference,
        campaign_reference=campaign_id,
    )

    canonical_input_fingerprint = (
        derive_governed_creative_workflow_application_input_fingerprint(
            workflow_request=workflow_request,
            current_workflow_state=current_workflow_state,
            requested_next_workflow_state=requested_next_workflow_state,
            responsible_actor_or_service_reference=responsible_reference,
            assessment_timestamp=assessment_timestamp,
            evidence_references=evidence_references,
            reason_codes=reason_codes,
            workflow_contract_reference=contract_reference,
            manual_external_tool_handoff_reference=handoff_reference,
            creative_result_candidate_reference=candidate_reference,
            accepted_gate_16_operator_decision_reference=operator_reference,
            accepted_gate_15_governed_asset_reference=asset_reference,
            recovery_last_accepted_state=recovery_last_accepted_state,
            recovery_last_accepted_event_reference=recovery_event_reference,
            recovery_reason_code=recovery_reason_code,
        )
    )

    evaluation = evaluate_governed_creative_workflow_transition(
        workflow_request_reference=workflow_request.workflow_request_id,
        idempotency_key=workflow_request.idempotency_key,
        project_context_reference=workflow_request.project_context_reference,
        campaign_context_reference=(
            workflow_request.campaign_context_reference
        ),
        creative_brief_reference=workflow_request.creative_brief_reference,
        instruction_reference=workflow_request.instruction_reference,
        current_workflow_state=current_workflow_state,
        requested_next_workflow_state=requested_next_workflow_state,
        responsible_actor_or_service_reference=responsible_reference,
        event_timestamp=assessment_timestamp,
        evidence_references=evidence_references,
        reason_codes=reason_codes,
        workflow_contract_reference=contract_reference,
        canonical_input_fingerprint=canonical_input_fingerprint,
        existing_idempotency_fingerprint=existing_idempotency_fingerprint,
        manual_external_tool_handoff_reference=handoff_reference,
        creative_result_candidate_reference=candidate_reference,
        accepted_operator_decision_reference=operator_reference,
        accepted_governed_asset_reference=asset_reference,
        recovery_last_accepted_state=recovery_last_accepted_state,
        recovery_last_accepted_event_reference=recovery_event_reference,
        recovery_reason_code=recovery_reason_code,
        authority_bypass_requested=False,
        prohibited_automation_requested=False,
        approval_execution_requested=False,
        asset_admission_execution_requested=False,
        lifecycle_mutation_requested=False,
        production_release_requested=False,
    )

    assessment_fingerprint = (
        derive_governed_creative_workflow_application_assessment_fingerprint(
            canonical_input_fingerprint=canonical_input_fingerprint,
            transition_evaluation=evaluation,
            accepted_gate_15_governed_asset_reference=asset_reference,
            accepted_gate_16_operator_decision_reference=operator_reference,
        )
    )
    return GovernedCreativeWorkflowApplicationAssessment(
        assessment_fingerprint=assessment_fingerprint,
        workflow_request_reference=workflow_request.workflow_request_id,
        project_context_reference=workflow_request.project_context_reference,
        campaign_context_reference=(
            workflow_request.campaign_context_reference
        ),
        current_workflow_state=current_workflow_state,
        requested_workflow_state=requested_next_workflow_state,
        accepted_gate_15_governed_asset_reference=asset_reference,
        accepted_gate_16_operator_decision_reference=operator_reference,
        transition_evaluation=evaluation,
        creative_workflow_event=evaluation.creative_workflow_event,
        governed_creative_workflow_result=(
            evaluation.governed_creative_workflow_result
        ),
        production_release_claimed=False,
    )
