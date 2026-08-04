from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Final, Literal, TypeAlias

from rie.domain.creative_workflow_event import (
    ALLOWED_WORKFLOW_STATES,
    CreativeWorkflowEvent,
    EvidenceReference,
    InstructionReference,
    ResponsibleActorOrServiceReference,
    WorkflowContractReference,
    WorkflowState,
    derive_creative_workflow_event_id,
)
from rie.domain.governed_creative_workflow_result import (
    BoundReference,
    GovernedCreativeWorkflowResult,
)

TRANSITION_DISPOSITION_ACCEPTED: Final = "ACCEPTED"
TRANSITION_DISPOSITION_REJECTED: Final = "REJECTED"
TRANSITION_DISPOSITION_SAFE_STOP: Final = "SAFE_STOP"

TransitionDisposition: TypeAlias = Literal[
    "ACCEPTED",
    "REJECTED",
    "SAFE_STOP",
]
CampaignContextReference: TypeAlias = tuple[str, str]
DiagnosticEntry: TypeAlias = tuple[str, str]

ALLOWED_TRANSITION_DISPOSITIONS: Final = frozenset(
    {
        TRANSITION_DISPOSITION_ACCEPTED,
        TRANSITION_DISPOSITION_REJECTED,
        TRANSITION_DISPOSITION_SAFE_STOP,
    }
)
TERMINAL_WORKFLOW_STATES: Final = frozenset(
    {
        "COMPLETED",
        "REJECTED",
        "SAFE_STOP",
    }
)
_ALLOWED_DIRECT_TRANSITIONS: Final = {
    "REQUESTED": frozenset({"INPUTS_VALIDATED", "SAFE_STOP"}),
    "INPUTS_VALIDATED": frozenset({"INSTRUCTION_READY", "SAFE_STOP"}),
    "INSTRUCTION_READY": frozenset(
        {
            "EXTERNAL_HANDOFF_RECORDED",
            "CANDIDATE_PENDING",
            "SAFE_STOP",
        }
    ),
    "EXTERNAL_HANDOFF_RECORDED": frozenset(
        {"CANDIDATE_PENDING", "SAFE_STOP"}
    ),
    "CANDIDATE_PENDING": frozenset({"CANDIDATE_ADMITTED", "SAFE_STOP"}),
    "CANDIDATE_ADMITTED": frozenset(
        {"OPERATOR_REVIEW_PENDING", "SAFE_STOP"}
    ),
    "OPERATOR_REVIEW_PENDING": frozenset(
        {"OPERATOR_DECISION_RECORDED", "REJECTED", "SAFE_STOP"}
    ),
    "OPERATOR_DECISION_RECORDED": frozenset(
        {"ASSET_ADMISSION_PENDING", "SAFE_STOP"}
    ),
    "ASSET_ADMISSION_PENDING": frozenset(
        {
            "GOVERNED_ASSET_REFERENCE_RECORDED",
            "REJECTED",
            "SAFE_STOP",
        }
    ),
    "GOVERNED_ASSET_REFERENCE_RECORDED": frozenset(
        {"COMPLETED", "SAFE_STOP"}
    ),
    "COMPLETED": frozenset(),
    "REJECTED": frozenset(),
    "SAFE_STOP": frozenset(),
}
_SHA256_PATTERN: Final = re.compile(r"^[0-9a-f]{64}$")
_CODE_PATTERN: Final = re.compile(r"^[A-Z][A-Z0-9_]*$")
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
_REQUIRED_TEXT_FIELDS: Final = (
    "workflow_request_reference",
    "idempotency_key",
    "project_context_reference",
    "creative_brief_reference",
    "canonical_input_fingerprint",
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


def _validate_bound_reference(
    field_name: str,
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
    require_sha256_identity: bool,
) -> BoundReference:
    validated = _validate_exact_reference_tuple(
        field_name,
        value,
        expected_length=3,
    )
    if validated[0] != project_reference:
        raise ValueError(
            f"{field_name} project binding must match "
            "project_context_reference"
        )
    if validated[1] != campaign_reference:
        raise ValueError(
            f"{field_name} campaign binding must match "
            "campaign_context_reference"
        )
    if (
        require_sha256_identity
        and _SHA256_PATTERN.fullmatch(validated[2]) is None
    ):
        raise ValueError(
            f"{field_name} identity must be a lowercase SHA256 value"
        )
    return validated


def _validate_optional_bound_reference(
    field_name: str,
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
    require_sha256_identity: bool = False,
) -> BoundReference | None:
    if value is None:
        return None
    return _validate_bound_reference(
        field_name,
        value,
        project_reference=project_reference,
        campaign_reference=campaign_reference,
        require_sha256_identity=require_sha256_identity,
    )


def _validate_sorted_codes(
    field_name: str,
    value: object,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty")
    validated = tuple(
        _validate_required_ascii_text(f"{field_name}[{index}]", item)
        for index, item in enumerate(value)
    )
    if any(_CODE_PATTERN.fullmatch(item) is None for item in validated):
        raise ValueError(
            f"{field_name} must use uppercase deterministic codes"
        )
    if len(set(validated)) != len(validated):
        raise ValueError(f"{field_name} must not contain duplicates")
    if validated != tuple(sorted(validated)):
        raise ValueError(f"{field_name} must use deterministic ordering")
    return validated


def _validate_diagnostics(value: object) -> tuple[DiagnosticEntry, ...]:
    if not isinstance(value, tuple):
        raise TypeError("diagnostics must be a tuple")
    normalized: list[DiagnosticEntry] = []
    for index, item in enumerate(value):
        validated = _validate_exact_reference_tuple(
            f"diagnostics[{index}]",
            item,
            expected_length=2,
        )
        if _CODE_PATTERN.fullmatch(validated[0]) is None:
            raise ValueError(
                "diagnostic codes must use uppercase deterministic codes"
            )
        normalized.append(validated)
    result = tuple(normalized)
    if len(set(result)) != len(result):
        raise ValueError("diagnostics must not contain duplicates")
    if result != tuple(sorted(result)):
        raise ValueError("diagnostics must use deterministic ordering")
    return result


def _validate_evidence_references(
    value: object,
    *,
    project_reference: str,
    campaign_reference: str,
) -> tuple[EvidenceReference, ...]:
    if not isinstance(value, tuple):
        raise TypeError("evidence_references must be a tuple")
    if not value:
        raise ValueError("evidence_references must not be empty")
    normalized = tuple(
        _validate_bound_reference(
            f"evidence_references[{index}]",
            item,
            project_reference=project_reference,
            campaign_reference=campaign_reference,
            require_sha256_identity=False,
        )
        for index, item in enumerate(value)
    )
    if len(set(normalized)) != len(normalized):
        raise ValueError("evidence_references must not contain duplicates")
    if normalized != tuple(sorted(normalized)):
        raise ValueError(
            "evidence_references must use deterministic ordering"
        )
    return normalized


def _safe_stop_evaluation(
    *,
    prior_workflow_state: WorkflowState,
    requested_workflow_state: WorkflowState,
    reason_codes: tuple[str, ...],
    diagnostics: tuple[DiagnosticEntry, ...],
) -> GovernedCreativeWorkflowTransitionEvaluation:
    normalized_codes = tuple(sorted(set(reason_codes) | {"SAFE_STOP_REQUIRED"}))
    normalized_diagnostics = tuple(sorted(set(diagnostics)))
    return GovernedCreativeWorkflowTransitionEvaluation(
        disposition=TRANSITION_DISPOSITION_SAFE_STOP,
        prior_workflow_state=prior_workflow_state,
        requested_workflow_state=requested_workflow_state,
        resulting_workflow_state=prior_workflow_state,
        creative_workflow_event=None,
        governed_creative_workflow_result=None,
        reason_codes=normalized_codes,
        diagnostics=normalized_diagnostics,
    )


@dataclass(frozen=True)
class GovernedCreativeWorkflowTransitionEvaluation:
    """Pure deterministic Gate 18 workflow-transition evaluation."""

    disposition: TransitionDisposition
    prior_workflow_state: WorkflowState
    requested_workflow_state: WorkflowState
    resulting_workflow_state: WorkflowState
    creative_workflow_event: CreativeWorkflowEvent | None
    governed_creative_workflow_result: GovernedCreativeWorkflowResult | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[DiagnosticEntry, ...]

    def __post_init__(self) -> None:
        if self.disposition not in ALLOWED_TRANSITION_DISPOSITIONS:
            raise ValueError("disposition is unsupported")
        for field_name in (
            "prior_workflow_state",
            "requested_workflow_state",
            "resulting_workflow_state",
        ):
            if getattr(self, field_name) not in ALLOWED_WORKFLOW_STATES:
                raise ValueError(f"{field_name} is unsupported")
        _validate_sorted_codes(
            "reason_codes",
            self.reason_codes,
            allow_empty=False,
        )
        _validate_diagnostics(self.diagnostics)

        terminal = self.resulting_workflow_state in TERMINAL_WORKFLOW_STATES
        if self.creative_workflow_event is None:
            if self.governed_creative_workflow_result is not None:
                raise ValueError(
                    "result must not exist without an accepted audit event"
                )
            if self.resulting_workflow_state != self.prior_workflow_state:
                raise ValueError(
                    "non-event evaluation must preserve the prior state"
                )
            if self.disposition != TRANSITION_DISPOSITION_SAFE_STOP:
                raise ValueError(
                    "non-event evaluation must use SAFE_STOP disposition"
                )
            return

        if (
            self.creative_workflow_event.prior_workflow_state
            != self.prior_workflow_state
        ):
            raise ValueError("event prior state must match evaluation")
        if (
            self.creative_workflow_event.resulting_workflow_state
            != self.resulting_workflow_state
        ):
            raise ValueError("event resulting state must match evaluation")
        if self.requested_workflow_state != self.resulting_workflow_state:
            raise ValueError(
                "accepted event must match the requested workflow state"
            )

        if terminal:
            if self.governed_creative_workflow_result is None:
                raise ValueError(
                    "terminal accepted transition requires a workflow result"
                )
            if (
                self.governed_creative_workflow_result.final_workflow_state
                != self.resulting_workflow_state
            ):
                raise ValueError(
                    "result final state must match evaluation"
                )
        elif self.governed_creative_workflow_result is not None:
            raise ValueError(
                "non-terminal transition must not fabricate a final result"
            )

        expected_disposition = {
            "REJECTED": TRANSITION_DISPOSITION_REJECTED,
            "SAFE_STOP": TRANSITION_DISPOSITION_SAFE_STOP,
        }.get(
            self.resulting_workflow_state,
            TRANSITION_DISPOSITION_ACCEPTED,
        )
        if self.disposition != expected_disposition:
            raise ValueError(
                "disposition must match the resulting workflow state"
            )


def evaluate_governed_creative_workflow_transition(
    *,
    workflow_request_reference: str,
    idempotency_key: str,
    project_context_reference: str,
    campaign_context_reference: CampaignContextReference,
    creative_brief_reference: str,
    instruction_reference: InstructionReference,
    current_workflow_state: WorkflowState,
    requested_next_workflow_state: WorkflowState,
    responsible_actor_or_service_reference: ResponsibleActorOrServiceReference,
    event_timestamp: datetime,
    evidence_references: tuple[EvidenceReference, ...],
    reason_codes: tuple[str, ...],
    workflow_contract_reference: WorkflowContractReference,
    canonical_input_fingerprint: str,
    existing_idempotency_fingerprint: str | None = None,
    manual_external_tool_handoff_reference: BoundReference | None = None,
    creative_result_candidate_reference: BoundReference | None = None,
    accepted_operator_decision_reference: BoundReference | None = None,
    accepted_governed_asset_reference: BoundReference | None = None,
    recovery_last_accepted_state: WorkflowState | None = None,
    recovery_last_accepted_event_reference: BoundReference | None = None,
    recovery_reason_code: str | None = None,
    authority_bypass_requested: bool = False,
    prohibited_automation_requested: bool = False,
    approval_execution_requested: bool = False,
    asset_admission_execution_requested: bool = False,
    lifecycle_mutation_requested: bool = False,
    production_release_requested: bool = False,
) -> GovernedCreativeWorkflowTransitionEvaluation:
    """Evaluate one explicit workflow-state transition without side effects."""

    for field_name in _REQUIRED_TEXT_FIELDS:
        value = locals()[field_name]
        _validate_reference_text(field_name, value)

    campaign_reference = _validate_exact_reference_tuple(
        "campaign_context_reference",
        campaign_context_reference,
        expected_length=2,
    )
    if campaign_reference[0] != project_context_reference:
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("PROJECT_CONTEXT_MISMATCH",),
            diagnostics=(
                (
                    "PROJECT_CONTEXT_MISMATCH",
                    "campaign project binding does not match workflow project",
                ),
            ),
        )
    campaign_id = campaign_reference[1]

    _validate_exact_reference_tuple(
        "instruction_reference",
        instruction_reference,
        expected_length=2,
    )
    _validate_exact_reference_tuple(
        "responsible_actor_or_service_reference",
        responsible_actor_or_service_reference,
        expected_length=2,
    )
    _validate_exact_reference_tuple(
        "workflow_contract_reference",
        workflow_contract_reference,
        expected_length=2,
    )
    normalized_evidence = _validate_evidence_references(
        evidence_references,
        project_reference=project_context_reference,
        campaign_reference=campaign_id,
    )
    normalized_reason_codes = _validate_sorted_codes(
        "reason_codes",
        reason_codes,
        allow_empty=False,
    )

    if current_workflow_state not in ALLOWED_WORKFLOW_STATES:
        raise ValueError("current_workflow_state is unsupported")
    if requested_next_workflow_state not in ALLOWED_WORKFLOW_STATES:
        raise ValueError("requested_next_workflow_state is unsupported")
    if not isinstance(event_timestamp, datetime):
        raise TypeError("event_timestamp must be a datetime")
    if event_timestamp.tzinfo is None or event_timestamp.utcoffset() is None:
        raise ValueError("event_timestamp must be timezone-aware")

    if _SHA256_PATTERN.fullmatch(canonical_input_fingerprint) is None:
        raise ValueError(
            "canonical_input_fingerprint must be a lowercase SHA256 value"
        )
    if existing_idempotency_fingerprint is not None:
        if not isinstance(existing_idempotency_fingerprint, str):
            raise TypeError(
                "existing_idempotency_fingerprint must be text or None"
            )
        if _SHA256_PATTERN.fullmatch(existing_idempotency_fingerprint) is None:
            raise ValueError(
                "existing_idempotency_fingerprint must be a lowercase "
                "SHA256 value"
            )
        if existing_idempotency_fingerprint != canonical_input_fingerprint:
            return _safe_stop_evaluation(
                prior_workflow_state=current_workflow_state,
                requested_workflow_state=requested_next_workflow_state,
                reason_codes=("IDEMPOTENCY_CONFLICT",),
                diagnostics=(
                    (
                        "IDEMPOTENCY_CONFLICT",
                        "idempotency key is bound to different canonical inputs",
                    ),
                ),
            )

    prohibited_flags = {
        "APPROVAL_EXECUTION_REQUESTED": approval_execution_requested,
        "ASSET_ADMISSION_EXECUTION_REQUESTED": (
            asset_admission_execution_requested
        ),
        "AUTHORITY_BYPASS_ATTEMPT": authority_bypass_requested,
        "LIFECYCLE_MUTATION_REQUESTED": lifecycle_mutation_requested,
        "PRODUCTION_RELEASE_REQUESTED": production_release_requested,
        "PROHIBITED_AUTOMATION_ATTEMPT": prohibited_automation_requested,
    }
    for field_name, value in prohibited_flags.items():
        if not isinstance(value, bool):
            raise TypeError(f"{field_name.lower()} must be a boolean")
    active_prohibited_codes = tuple(
        sorted(code for code, active in prohibited_flags.items() if active)
    )
    if active_prohibited_codes:
        reason_code = (
            "AUTHORITY_BYPASS_ATTEMPT"
            if authority_bypass_requested
            else "PROHIBITED_AUTOMATION_ATTEMPT"
        )
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=(reason_code,),
            diagnostics=tuple(
                (code, "prohibited execution or mutation request was supplied")
                for code in active_prohibited_codes
            ),
        )

    optional_references = {
        "manual_external_tool_handoff_reference": (
            manual_external_tool_handoff_reference,
            False,
        ),
        "creative_result_candidate_reference": (
            creative_result_candidate_reference,
            False,
        ),
        "accepted_operator_decision_reference": (
            accepted_operator_decision_reference,
            False,
        ),
        "accepted_governed_asset_reference": (
            accepted_governed_asset_reference,
            False,
        ),
        "recovery_last_accepted_event_reference": (
            recovery_last_accepted_event_reference,
            True,
        ),
    }
    validated_references: dict[str, BoundReference | None] = {}
    try:
        for field_name, (
            value,
            require_sha256_identity,
        ) in optional_references.items():
            validated_references[field_name] = (
                _validate_optional_bound_reference(
                    field_name,
                    value,
                    project_reference=project_context_reference,
                    campaign_reference=campaign_id,
                    require_sha256_identity=require_sha256_identity,
                )
            )
    except ValueError as error:
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("CAMPAIGN_CONTEXT_MISMATCH",),
            diagnostics=(
                ("CAMPAIGN_CONTEXT_MISMATCH", str(error)),
            ),
        )

    if recovery_last_accepted_state is not None:
        if recovery_last_accepted_state not in ALLOWED_WORKFLOW_STATES:
            raise ValueError("recovery_last_accepted_state is unsupported")
        recovery_reference = validated_references[
            "recovery_last_accepted_event_reference"
        ]
        recovery_reason = (
            None
            if recovery_reason_code is None
            else _validate_required_ascii_text(
                "recovery_reason_code",
                recovery_reason_code,
            )
        )
        recovery_valid = (
            recovery_last_accepted_state == current_workflow_state
            and recovery_reference is not None
            and recovery_reference in normalized_evidence
            and recovery_reason is not None
            and _CODE_PATTERN.fullmatch(recovery_reason) is not None
        )
        if not recovery_valid:
            return _safe_stop_evaluation(
                prior_workflow_state=current_workflow_state,
                requested_workflow_state=requested_next_workflow_state,
                reason_codes=("RECOVERY_EVIDENCE_INVALID",),
                diagnostics=(
                    (
                        "RECOVERY_EVIDENCE_INVALID",
                        "recovery inputs do not identify the last accepted state",
                    ),
                ),
            )
    elif (
        recovery_last_accepted_event_reference is not None
        or recovery_reason_code is not None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("RECOVERY_EVIDENCE_INVALID",),
            diagnostics=(
                (
                    "RECOVERY_EVIDENCE_INVALID",
                    "partial recovery evidence is not permitted",
                ),
            ),
        )

    allowed_targets = _ALLOWED_DIRECT_TRANSITIONS[current_workflow_state]
    if requested_next_workflow_state not in allowed_targets:
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("INVALID_STATE_TRANSITION",),
            diagnostics=(
                (
                    "INVALID_STATE_TRANSITION",
                    f"{current_workflow_state} cannot transition to "
                    f"{requested_next_workflow_state}",
                ),
            ),
        )

    handoff_reference = validated_references[
        "manual_external_tool_handoff_reference"
    ]
    candidate_reference = validated_references[
        "creative_result_candidate_reference"
    ]
    operator_reference = validated_references[
        "accepted_operator_decision_reference"
    ]
    asset_reference = validated_references[
        "accepted_governed_asset_reference"
    ]

    if (
        current_workflow_state == "EXTERNAL_HANDOFF_RECORDED"
        and handoff_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("HANDOFF_RECORD_INVALID",),
            diagnostics=(
                (
                    "HANDOFF_RECORD_INVALID",
                    "handoff predecessor requires an exact handoff reference",
                ),
            ),
        )

    if (
        current_workflow_state
        in {
            "CANDIDATE_ADMITTED",
            "OPERATOR_REVIEW_PENDING",
            "OPERATOR_DECISION_RECORDED",
            "ASSET_ADMISSION_PENDING",
            "GOVERNED_ASSET_REFERENCE_RECORDED",
        }
        and candidate_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("CANDIDATE_PROVENANCE_INVALID",),
            diagnostics=(
                (
                    "CANDIDATE_PROVENANCE_INVALID",
                    "predecessor state requires an exact candidate reference",
                ),
            ),
        )

    if (
        current_workflow_state
        in {
            "OPERATOR_DECISION_RECORDED",
            "ASSET_ADMISSION_PENDING",
            "GOVERNED_ASSET_REFERENCE_RECORDED",
        }
        and operator_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("OPERATOR_REVIEW_REQUIRED",),
            diagnostics=(
                (
                    "OPERATOR_REVIEW_REQUIRED",
                    "predecessor state requires an accepted decision reference",
                ),
            ),
        )

    if (
        current_workflow_state == "GOVERNED_ASSET_REFERENCE_RECORDED"
        and asset_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("ASSET_ADMISSION_REQUIRED",),
            diagnostics=(
                (
                    "ASSET_ADMISSION_REQUIRED",
                    "predecessor state requires an accepted asset reference",
                ),
            ),
        )

    if (
        current_workflow_state == "INSTRUCTION_READY"
        and requested_next_workflow_state == "EXTERNAL_HANDOFF_RECORDED"
        and handoff_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("HANDOFF_RECORD_INVALID",),
            diagnostics=(
                (
                    "HANDOFF_RECORD_INVALID",
                    "external handoff transition requires a handoff reference",
                ),
            ),
        )

    if (
        current_workflow_state == "INSTRUCTION_READY"
        and requested_next_workflow_state == "CANDIDATE_PENDING"
        and handoff_reference is not None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("HANDOFF_RECORD_INVALID",),
            diagnostics=(
                (
                    "HANDOFF_RECORD_INVALID",
                    "declared handoff must be recorded before candidate pending",
                ),
            ),
        )

    if (
        requested_next_workflow_state
        in {"CANDIDATE_ADMITTED", "OPERATOR_REVIEW_PENDING"}
        and candidate_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("CANDIDATE_PROVENANCE_INVALID",),
            diagnostics=(
                (
                    "CANDIDATE_PROVENANCE_INVALID",
                    "candidate transition requires an exact candidate reference",
                ),
            ),
        )

    if (
        requested_next_workflow_state
        in {"OPERATOR_DECISION_RECORDED", "ASSET_ADMISSION_PENDING"}
        and operator_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("OPERATOR_REVIEW_REQUIRED",),
            diagnostics=(
                (
                    "OPERATOR_REVIEW_REQUIRED",
                    "operator transition requires an accepted decision reference",
                ),
            ),
        )

    if (
        requested_next_workflow_state
        == "GOVERNED_ASSET_REFERENCE_RECORDED"
        and asset_reference is None
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("ASSET_ADMISSION_REQUIRED",),
            diagnostics=(
                (
                    "ASSET_ADMISSION_REQUIRED",
                    "asset transition requires an accepted asset reference",
                ),
            ),
        )

    if requested_next_workflow_state == "COMPLETED":
        if operator_reference is None or asset_reference is None:
            return _safe_stop_evaluation(
                prior_workflow_state=current_workflow_state,
                requested_workflow_state=requested_next_workflow_state,
                reason_codes=("SAFE_STOP_REQUIRED",),
                diagnostics=(
                    (
                        "SAFE_STOP_REQUIRED",
                        "completed transition requires operator and asset references",
                    ),
                ),
            )

    if requested_next_workflow_state == "REJECTED":
        required_rejection_code = (
            "OPERATOR_DECISION_REJECTED"
            if current_workflow_state == "OPERATOR_REVIEW_PENDING"
            else "ASSET_ADMISSION_REJECTED"
        )
        if required_rejection_code not in normalized_reason_codes:
            return _safe_stop_evaluation(
                prior_workflow_state=current_workflow_state,
                requested_workflow_state=requested_next_workflow_state,
                reason_codes=(required_rejection_code,),
                diagnostics=(
                    (
                        required_rejection_code,
                        "rejected transition requires the exact rejection reason",
                    ),
                ),
            )
        fabricated_reference = (
            (
                current_workflow_state == "OPERATOR_REVIEW_PENDING"
                and operator_reference is not None
            )
            or asset_reference is not None
        )
        if fabricated_reference:
            return _safe_stop_evaluation(
                prior_workflow_state=current_workflow_state,
                requested_workflow_state=requested_next_workflow_state,
                reason_codes=("AUTHORITY_BYPASS_ATTEMPT",),
                diagnostics=(
                    (
                        "AUTHORITY_BYPASS_ATTEMPT",
                        "rejected transition must not fabricate accepted references",
                    ),
                ),
            )

    if (
        requested_next_workflow_state == "SAFE_STOP"
        and "SAFE_STOP_REQUIRED" not in normalized_reason_codes
    ):
        return _safe_stop_evaluation(
            prior_workflow_state=current_workflow_state,
            requested_workflow_state=requested_next_workflow_state,
            reason_codes=("SAFE_STOP_REQUIRED",),
            diagnostics=(
                (
                    "SAFE_STOP_REQUIRED",
                    "safe-stop transition requires the exact safe-stop reason",
                ),
            ),
        )

    event_id = derive_creative_workflow_event_id(
        workflow_request_reference=workflow_request_reference,
        idempotency_key=idempotency_key,
        prior_workflow_state=current_workflow_state,
        resulting_workflow_state=requested_next_workflow_state,
        project_context_reference=project_context_reference,
        campaign_context_reference=campaign_reference,
        creative_brief_reference=creative_brief_reference,
        instruction_reference=instruction_reference,
        responsible_actor_or_service_reference=(
            responsible_actor_or_service_reference
        ),
        event_timestamp=event_timestamp,
        evidence_references=normalized_evidence,
        reason_codes=normalized_reason_codes,
        workflow_contract_reference=workflow_contract_reference,
    )
    event = CreativeWorkflowEvent(
        creative_workflow_event_id=event_id,
        workflow_request_reference=workflow_request_reference,
        idempotency_key=idempotency_key,
        prior_workflow_state=current_workflow_state,
        resulting_workflow_state=requested_next_workflow_state,
        project_context_reference=project_context_reference,
        campaign_context_reference=campaign_reference,
        creative_brief_reference=creative_brief_reference,
        instruction_reference=instruction_reference,
        responsible_actor_or_service_reference=(
            responsible_actor_or_service_reference
        ),
        event_timestamp=event_timestamp,
        evidence_references=normalized_evidence,
        reason_codes=normalized_reason_codes,
        workflow_contract_reference=workflow_contract_reference,
        executed_approval_claimed=False,
        asset_admission_claimed=False,
        lifecycle_mutation_claimed=False,
        production_release_claimed=False,
    )

    disposition = {
        "REJECTED": TRANSITION_DISPOSITION_REJECTED,
        "SAFE_STOP": TRANSITION_DISPOSITION_SAFE_STOP,
    }.get(
        requested_next_workflow_state,
        TRANSITION_DISPOSITION_ACCEPTED,
    )
    diagnostics: tuple[DiagnosticEntry, ...] = (
        (
            f"TRANSITION_{disposition}",
            f"{current_workflow_state}->{requested_next_workflow_state}",
        ),
    )
    result: GovernedCreativeWorkflowResult | None = None
    if requested_next_workflow_state in TERMINAL_WORKFLOW_STATES:
        last_event_reference: BoundReference = (
            project_context_reference,
            campaign_id,
            event.creative_workflow_event_id,
        )
        result = GovernedCreativeWorkflowResult(
            workflow_request_reference=workflow_request_reference,
            idempotency_key=idempotency_key,
            project_context_reference=project_context_reference,
            campaign_context_reference=campaign_reference,
            creative_brief_reference=creative_brief_reference,
            instruction_reference=instruction_reference,
            final_workflow_state=requested_next_workflow_state,
            last_accepted_event_reference=last_event_reference,
            manual_external_tool_handoff_reference=handoff_reference,
            creative_result_candidate_reference=candidate_reference,
            accepted_operator_decision_reference=(
                operator_reference
                if requested_next_workflow_state == "COMPLETED"
                else None
            ),
            accepted_governed_asset_reference=(
                asset_reference
                if requested_next_workflow_state == "COMPLETED"
                else None
            ),
            reason_codes=normalized_reason_codes,
            diagnostics=diagnostics,
            workflow_contract_reference=workflow_contract_reference,
            production_release_claimed=False,
        )

    return GovernedCreativeWorkflowTransitionEvaluation(
        disposition=disposition,
        prior_workflow_state=current_workflow_state,
        requested_workflow_state=requested_next_workflow_state,
        resulting_workflow_state=requested_next_workflow_state,
        creative_workflow_event=event,
        governed_creative_workflow_result=result,
        reason_codes=normalized_reason_codes,
        diagnostics=diagnostics,
    )
