from dataclasses import dataclass as _dataclass
import re as _re

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION as _GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
)
from rie.domain.governed_knowledge_acceptance_decision import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION as _ACCEPTANCE_DECISION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED as _OUTCOME_ACCEPTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED as _OUTCOME_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED as _OUTCOME_REJECTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED as _ACCEPTANCE_SCOPE_DECLARED,
    GovernedKnowledgeAcceptanceDecision as _GovernedKnowledgeAcceptanceDecision,
    compute_governed_knowledge_acceptance_decision_id as _compute_acceptance_decision_id,
    governed_knowledge_acceptance_decision_identity_input_from_record as _acceptance_identity_input_from_record,
)
from rie.domain.governed_knowledge_acceptance_history_interpretation import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY as _SUPPORTED_COMPLETENESS_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION as _INTERPRETATION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_WARNING as _WARNING,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED as _COMPOSITION_ACCEPTED_AND_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED as _COMPOSITION_ACCEPTED_AND_REJECTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY as _COMPOSITION_ACCEPTED_ONLY,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED as _COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY as _COMPOSITION_DEFERRED_ONLY,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS as _COMPOSITION_NO_DECISIONS,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED as _COMPOSITION_REJECTED_AND_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY as _COMPOSITION_REJECTED_ONLY,
    GovernedKnowledgeAcceptanceHistoryInterpretation as _Interpretation,
    GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic as _Diagnostic,
    GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput as _IdentityInput,
    compute_governed_knowledge_acceptance_history_interpretation_id as _compute_interpretation_id,
)


GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_ID = (
    "rcis-governed-knowledge-acceptance-history-interpretation"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED = "recorded"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_REJECTED = "rejected"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY = (
    "unsupported_interpretation_policy"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE = (
    "unsupported_completeness_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE = (
    "unsupported_acceptance_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH = (
    "acceptance_decision_subject_mismatch"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_REASONS = (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH,
)


_GOVERNED_KNOWLEDGE_ID_PATTERN = _re.compile(r"^gk1_[0-9a-f]{64}$")
_SOURCE = "governed_knowledge_acceptance_history_interpreter"
_REJECTION_MESSAGES = {
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY: (
        "The acceptance-history interpretation policy is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE: (
        "The acceptance-history completeness scope is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE: (
        "The acceptance-history acceptance scope is unsupported."
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH: (
        "An acceptance decision does not match the requested interpretation subject."
    ),
}
_COMPOSITION_BY_OUTCOMES = {
    frozenset(): _COMPOSITION_NO_DECISIONS,
    frozenset((_OUTCOME_ACCEPTED,)): _COMPOSITION_ACCEPTED_ONLY,
    frozenset((_OUTCOME_REJECTED,)): _COMPOSITION_REJECTED_ONLY,
    frozenset((_OUTCOME_DEFERRED,)): _COMPOSITION_DEFERRED_ONLY,
    frozenset((_OUTCOME_ACCEPTED, _OUTCOME_REJECTED)): _COMPOSITION_ACCEPTED_AND_REJECTED,
    frozenset((_OUTCOME_ACCEPTED, _OUTCOME_DEFERRED)): _COMPOSITION_ACCEPTED_AND_DEFERRED,
    frozenset((_OUTCOME_REJECTED, _OUTCOME_DEFERRED)): _COMPOSITION_REJECTED_AND_DEFERRED,
    frozenset((_OUTCOME_ACCEPTED, _OUTCOME_REJECTED, _OUTCOME_DEFERRED)): (
        _COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED
    ),
}


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _validate_decisions(value: object) -> tuple[_GovernedKnowledgeAcceptanceDecision, ...]:
    if type(value) is not tuple:
        raise ValueError("acceptance_decisions must be a tuple")
    for index, decision in enumerate(value):
        if type(decision) is not _GovernedKnowledgeAcceptanceDecision:
            raise ValueError(
                f"acceptance_decisions[{index}] must be an exact "
                "GovernedKnowledgeAcceptanceDecision"
            )
        for field_name in (
            "governed_knowledge_acceptance_decision_id",
            "contract_version",
            "governed_knowledge_id",
            "governed_knowledge_contract_version",
            "acceptance_scope",
            "acceptance_scope_reference",
            "acceptance_outcome",
            "decided_by",
            "acceptance_policy_id",
            "acceptance_policy_version",
        ):
            _require_string(getattr(decision, field_name), field_name)
        decision.__post_init__()
        expected_id = _compute_acceptance_decision_id(
            _acceptance_identity_input_from_record(decision)
        )
        if decision.governed_knowledge_acceptance_decision_id != expected_id:
            raise ValueError("acceptance decision identity does not match content")
    ids = tuple(
        decision.governed_knowledge_acceptance_decision_id for decision in value
    )
    if len(set(ids)) != len(ids):
        raise ValueError("acceptance_decisions must be unique")
    if tuple(sorted(ids)) != ids:
        raise ValueError("acceptance_decisions must be lexicographically ordered")
    return value  # type: ignore[return-value]


@_dataclass(frozen=True)
class GovernedKnowledgeAcceptanceHistoryInterpretationRequest:
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_decisions: tuple[_GovernedKnowledgeAcceptanceDecision, ...]
    completeness_scope: str
    completeness_reference: str
    interpretation_policy_id: str
    interpretation_policy_version: str

    def __post_init__(self) -> None:
        _require_string(self.governed_knowledge_id, "governed_knowledge_id")
        if _GOVERNED_KNOWLEDGE_ID_PATTERN.fullmatch(self.governed_knowledge_id) is None:
            raise ValueError("governed_knowledge_id has an invalid format")
        _require_string(
            self.governed_knowledge_contract_version,
            "governed_knowledge_contract_version",
        )
        if self.governed_knowledge_contract_version != _GOVERNED_KNOWLEDGE_CONTRACT_VERSION:
            raise ValueError("unsupported governed_knowledge_contract_version")
        _require_string(self.acceptance_scope, "acceptance_scope")
        _require_string(self.acceptance_scope_reference, "acceptance_scope_reference")
        _validate_decisions(self.acceptance_decisions)
        _require_string(self.completeness_scope, "completeness_scope")
        _require_string(self.completeness_reference, "completeness_reference")
        _require_string(self.interpretation_policy_id, "interpretation_policy_id")
        _require_string(
            self.interpretation_policy_version,
            "interpretation_policy_version",
        )


@_dataclass(frozen=True)
class GovernedKnowledgeAcceptanceHistoryInterpretationResult:
    result_status: str
    interpretation: _Interpretation | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[_Diagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED,
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_REJECTED,
        ):
            raise ValueError("unsupported result_status")
        if self.interpretation is not None:
            if type(self.interpretation) is not _Interpretation:
                raise ValueError("interpretation must be an exact interpretation or None")
            self.interpretation.__post_init__()
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        for reason_code in self.reason_codes:
            _require_string(reason_code, "reason_codes")
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("reason_codes must be unique")
        if tuple(sorted(self.reason_codes)) != self.reason_codes:
            raise ValueError("reason_codes must be lexicographically ordered")
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")
        for diagnostic in self.diagnostics:
            if type(diagnostic) is not _Diagnostic:
                raise ValueError("diagnostics must contain exact diagnostics")
            diagnostic.__post_init__()
        if self.result_status == GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED:
            if (
                self.interpretation is None
                or self.reason_codes
                or self.diagnostics
                or self.interpretation.diagnostics
            ):
                raise ValueError("recorded result shape is invalid")
        else:
            if (
                self.interpretation is not None
                or len(self.reason_codes) != 1
                or self.reason_codes[0]
                not in GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_REASONS
                or len(self.diagnostics) != 1
            ):
                raise ValueError("rejected result shape is invalid")
            reason = self.reason_codes[0]
            diagnostic = self.diagnostics[0]
            if (
                diagnostic.code != reason
                or diagnostic.severity != _WARNING
                or diagnostic.message != _REJECTION_MESSAGES[reason]
                or diagnostic.field != "request"
                or diagnostic.source != _SOURCE
            ):
                raise ValueError("rejected diagnostic does not match rejection")


def _rejected(reason_code: str) -> GovernedKnowledgeAcceptanceHistoryInterpretationResult:
    diagnostic = _Diagnostic(
        code=reason_code,
        severity=_WARNING,
        message=_REJECTION_MESSAGES[reason_code],
        field="request",
        source=_SOURCE,
    )
    return GovernedKnowledgeAcceptanceHistoryInterpretationResult(
        result_status=GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_REJECTED,
        interpretation=None,
        reason_codes=(reason_code,),
        diagnostics=(diagnostic,),
    )


def interpret_governed_knowledge_acceptance_history(
    request: GovernedKnowledgeAcceptanceHistoryInterpretationRequest,
) -> GovernedKnowledgeAcceptanceHistoryInterpretationResult:
    if type(request) is not GovernedKnowledgeAcceptanceHistoryInterpretationRequest:
        raise ValueError(
            "request must be an exact "
            "GovernedKnowledgeAcceptanceHistoryInterpretationRequest"
        )
    request.__post_init__()
    if (
        request.interpretation_policy_id
        != GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_ID
        or request.interpretation_policy_version
        != GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_VERSION
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY
        )
    if request.completeness_scope != _SUPPORTED_COMPLETENESS_SCOPE:
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE
        )
    if request.acceptance_scope != _ACCEPTANCE_SCOPE_DECLARED:
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE
        )
    if any(
        decision.governed_knowledge_id != request.governed_knowledge_id
        or decision.governed_knowledge_contract_version
        != request.governed_knowledge_contract_version
        or decision.acceptance_scope != request.acceptance_scope
        or decision.acceptance_scope_reference != request.acceptance_scope_reference
        for decision in request.acceptance_decisions
    ):
        return _rejected(
            GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH
        )
    decision_ids = tuple(
        decision.governed_knowledge_acceptance_decision_id
        for decision in request.acceptance_decisions
    )
    composition = _COMPOSITION_BY_OUTCOMES[
        frozenset(
            decision.acceptance_outcome for decision in request.acceptance_decisions
        )
    ]
    identity_input = _IdentityInput(
        contract_version=_INTERPRETATION_CONTRACT_VERSION,
        governed_knowledge_id=request.governed_knowledge_id,
        governed_knowledge_contract_version=request.governed_knowledge_contract_version,
        acceptance_scope=request.acceptance_scope,
        acceptance_scope_reference=request.acceptance_scope_reference,
        acceptance_decision_contract_version=_ACCEPTANCE_DECISION_CONTRACT_VERSION,
        acceptance_decision_ids=decision_ids,
        completeness_scope=request.completeness_scope,
        completeness_reference=request.completeness_reference,
        outcome_composition=composition,
        interpretation_policy_id=request.interpretation_policy_id,
        interpretation_policy_version=request.interpretation_policy_version,
    )
    interpretation = _Interpretation(
        governed_knowledge_acceptance_history_interpretation_id=(
            _compute_interpretation_id(identity_input)
        ),
        contract_version=identity_input.contract_version,
        governed_knowledge_id=identity_input.governed_knowledge_id,
        governed_knowledge_contract_version=(
            identity_input.governed_knowledge_contract_version
        ),
        acceptance_scope=identity_input.acceptance_scope,
        acceptance_scope_reference=identity_input.acceptance_scope_reference,
        acceptance_decision_contract_version=(
            identity_input.acceptance_decision_contract_version
        ),
        acceptance_decision_ids=identity_input.acceptance_decision_ids,
        completeness_scope=identity_input.completeness_scope,
        completeness_reference=identity_input.completeness_reference,
        outcome_composition=identity_input.outcome_composition,
        interpretation_policy_id=identity_input.interpretation_policy_id,
        interpretation_policy_version=identity_input.interpretation_policy_version,
        diagnostics=(),
    )
    return GovernedKnowledgeAcceptanceHistoryInterpretationResult(
        result_status=GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED,
        interpretation=interpretation,
        reason_codes=(),
        diagnostics=(),
    )
