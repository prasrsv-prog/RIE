"""Side-effect-free declared-scope promotion-prerequisite evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.application.knowledge_authority_decider import (
    KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID,
    KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION,
)
from rie.application.knowledge_conflict_assessor import (
    KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID,
    KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION,
)
from rie.application.knowledge_governor import (
    KNOWLEDGE_GOVERNANCE_POLICY_ID,
    KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
)
from rie.domain.knowledge_authority_decision import (
    AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    AUTHORITY_DECISION_OUTCOME_DEFERRED,
    AUTHORITY_DECISION_OUTCOME_DENIED,
    INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    KnowledgeAuthorityDecision,
    compute_knowledge_authority_decision_id,
    knowledge_authority_identity_input_from_record,
)
from rie.domain.knowledge_candidate import (
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_conflict_assessment_record import (
    ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
    ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
    ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
    KnowledgeConflictAssessmentRecord,
    KnowledgeConflictParticipant,
    compute_knowledge_conflict_assessment_record_id,
    knowledge_conflict_identity_input_from_record,
)
from rie.domain.knowledge_governance_decision import (
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KnowledgeGovernanceDecision,
    compute_knowledge_governance_decision_id,
    knowledge_governance_identity_input_from_record,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_EVALUATION_SCOPE_POLICY_ID,
    PROMOTION_EVALUATION_SCOPE_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
    KnowledgePromotionEvaluationScope,
    KnowledgePromotionPrerequisiteDiagnostic,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    compute_knowledge_promotion_evaluation_scope_id,
    compute_knowledge_promotion_prerequisite_evaluation_id,
    knowledge_promotion_evaluation_scope_identity_input_from_record,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


_REJECTION_MESSAGES = {
    "unsupported_promotion_prerequisite_evaluation_policy": "The promotion-prerequisite evaluation policy is unsupported.",
    "unsupported_promotion_evaluation_scope_policy": "The declared promotion-evaluation scope policy is unsupported.",
    "scope_candidate_mismatch": "The declared scope references another candidate.",
    "scope_candidate_contract_mismatch": "The declared scope references another candidate contract.",
    "scope_candidate_snapshot_mismatch": "The declared scope references another candidate snapshot.",
    "unsupported_governance_evidence_policy": "At least one governance record uses an unsupported evidence policy.",
    "governance_candidate_mismatch": "At least one governance record references another candidate.",
    "governance_candidate_contract_mismatch": "At least one governance record references another candidate contract.",
    "governance_candidate_snapshot_mismatch": "At least one governance record references another candidate snapshot.",
    "unsupported_conflict_evidence_policy": "At least one conflict record uses an unsupported evidence policy.",
    "conflict_record_outside_declared_scope": "At least one conflict record is outside the declared peer scope.",
    "conflict_participant_contract_mismatch": "At least one conflict participant references another candidate contract.",
    "conflict_participant_snapshot_mismatch": "At least one conflict participant references another candidate snapshot.",
    "unsupported_authority_evidence_policy": "At least one authority record uses an unsupported evidence policy.",
    "authority_candidate_mismatch": "At least one authority record references another candidate.",
    "authority_candidate_contract_mismatch": "At least one authority record references another candidate contract.",
    "authority_candidate_snapshot_mismatch": "At least one authority record references another candidate snapshot.",
    "authority_governance_lineage_mismatch": "At least one authority lineage references governance outside the direct input.",
    "missing_or_mismatched_required_evaluation_reason": "The supplied evaluation reasons do not equal the computed reasons.",
}
if tuple(_REJECTION_MESSAGES) != PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS:
    raise RuntimeError("rejection precedence does not match the domain contract")


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_request_reason_codes(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("reason_codes must be a tuple")
    if not value:
        raise ValueError("reason_codes must not be empty")
    for index, item in enumerate(value):
        _require_string(item, f"reason_codes[{index}]")


def _verified_governance_id(record: KnowledgeGovernanceDecision) -> str:
    expected = compute_knowledge_governance_decision_id(
        knowledge_governance_identity_input_from_record(record)
    )
    if record.knowledge_governance_decision_id != expected:
        raise ValueError("knowledge_governance_decision_id does not match identity")
    return expected


def _verified_conflict_id(record: KnowledgeConflictAssessmentRecord) -> str:
    expected = compute_knowledge_conflict_assessment_record_id(
        knowledge_conflict_identity_input_from_record(record)
    )
    if record.knowledge_conflict_assessment_record_id != expected:
        raise ValueError("knowledge_conflict_assessment_record_id does not match identity")
    return expected


def _verified_authority_id(record: KnowledgeAuthorityDecision) -> str:
    expected = compute_knowledge_authority_decision_id(
        knowledge_authority_identity_input_from_record(record)
    )
    if record.knowledge_authority_decision_id != expected:
        raise ValueError("knowledge_authority_decision_id does not match identity")
    return expected


def _require_record_tuple(
    value: object,
    field_name: str,
    exact_type: type,
    id_getter: object,
    *,
    allow_empty: bool,
) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty")
    record_ids: list[str] = []
    for index, record in enumerate(value):
        if type(record) is not exact_type:
            raise ValueError(
                f"{field_name}[{index}] must be an exact {exact_type.__name__}"
            )
        record_ids.append(id_getter(record))  # type: ignore[operator]
    if len(set(record_ids)) != len(record_ids):
        raise ValueError(f"{field_name} must contain unique IDs")
    if record_ids != sorted(record_ids):
        raise ValueError(f"{field_name} must be ordered by record ID")


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgePromotionPrerequisiteDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionPrerequisiteDiagnostic"
            )


@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluationRequest:
    knowledge_candidate: KnowledgeCandidate
    evaluation_scope: KnowledgePromotionEvaluationScope
    knowledge_governance_decisions: tuple[KnowledgeGovernanceDecision, ...]
    knowledge_conflict_assessment_records: tuple[KnowledgeConflictAssessmentRecord, ...]
    knowledge_authority_decisions: tuple[KnowledgeAuthorityDecision, ...]
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str

    def __post_init__(self) -> None:
        if type(self.knowledge_candidate) is not KnowledgeCandidate:
            raise ValueError("knowledge_candidate must be an exact KnowledgeCandidate")
        expected_candidate_id = compute_knowledge_candidate_id(
            identity_input_from_knowledge_candidate(self.knowledge_candidate)
        )
        if self.knowledge_candidate.knowledge_candidate_id != expected_candidate_id:
            raise ValueError("knowledge_candidate_id does not match identity")
        if type(self.evaluation_scope) is not KnowledgePromotionEvaluationScope:
            raise ValueError("evaluation_scope must be an exact KnowledgePromotionEvaluationScope")
        expected_scope_id = compute_knowledge_promotion_evaluation_scope_id(
            knowledge_promotion_evaluation_scope_identity_input_from_record(self.evaluation_scope)
        )
        if self.evaluation_scope.knowledge_promotion_evaluation_scope_id != expected_scope_id:
            raise ValueError("knowledge_promotion_evaluation_scope_id does not match identity")
        _require_record_tuple(self.knowledge_governance_decisions, "knowledge_governance_decisions", KnowledgeGovernanceDecision, _verified_governance_id, allow_empty=False)
        _require_record_tuple(self.knowledge_conflict_assessment_records, "knowledge_conflict_assessment_records", KnowledgeConflictAssessmentRecord, _verified_conflict_id, allow_empty=True)
        _require_record_tuple(self.knowledge_authority_decisions, "knowledge_authority_decisions", KnowledgeAuthorityDecision, _verified_authority_id, allow_empty=False)
        _require_request_reason_codes(self.reason_codes)
        _require_string(self.evaluated_by, "evaluated_by")
        _require_aware_datetime(self.evaluated_at, "evaluated_at")
        _require_string(self.evaluation_policy_id, "evaluation_policy_id")
        _require_string(self.evaluation_policy_version, "evaluation_policy_version")


@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluationResult:
    result_status: str
    evaluation: KnowledgePromotionPrerequisiteEvaluation | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[KnowledgePromotionPrerequisiteDiagnostic, ...]

    def __post_init__(self) -> None:
        if type(self.result_status) is not str or self.result_status not in (
            PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED,
            PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED,
        ):
            raise ValueError("unsupported promotion-prerequisite result status")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        _require_diagnostics(self.diagnostics)
        if self.result_status == PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED:
            if type(self.evaluation) is not KnowledgePromotionPrerequisiteEvaluation:
                raise ValueError("recorded result requires an exact evaluation")
            self.evaluation.__post_init__()
            if self.reason_codes != () or self.diagnostics != ():
                raise ValueError("recorded result reason codes and diagnostics must be empty")
        else:
            if self.evaluation is not None:
                raise ValueError("rejected result must not contain an evaluation")
            if len(self.reason_codes) != 1 or self.reason_codes[0] not in PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS:
                raise ValueError("rejected result requires one approved reason")
            if len(self.diagnostics) != 1:
                raise ValueError("rejected result requires exactly one diagnostic")
            diagnostic = self.diagnostics[0]
            diagnostic.__post_init__()
            if diagnostic.severity != KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING:
                raise ValueError("rejected diagnostic severity must be warning")
            if diagnostic.code != self.reason_codes[0]:
                raise ValueError("rejected diagnostic code must equal reason")


def _rejected(reason_code: str) -> KnowledgePromotionPrerequisiteEvaluationResult:
    return KnowledgePromotionPrerequisiteEvaluationResult(
        result_status=PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED,
        evaluation=None,
        reason_codes=(reason_code,),
        diagnostics=(
            KnowledgePromotionPrerequisiteDiagnostic(
                code=reason_code,
                severity=KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING,
                message=_REJECTION_MESSAGES[reason_code],
                field="request",
                source="knowledge_promotion_prerequisite_evaluator",
            ),
        ),
    )


def _participant_by_id(
    record: KnowledgeConflictAssessmentRecord,
) -> dict[str, KnowledgeConflictParticipant]:
    return {participant.knowledge_candidate_id: participant for participant in record.participants}


def evaluate_knowledge_promotion_prerequisites(
    request: KnowledgePromotionPrerequisiteEvaluationRequest,
) -> KnowledgePromotionPrerequisiteEvaluationResult:
    if type(request) is not KnowledgePromotionPrerequisiteEvaluationRequest:
        raise ValueError(
            "request must be an exact KnowledgePromotionPrerequisiteEvaluationRequest"
        )
    request.__post_init__()

    candidate = request.knowledge_candidate
    scope = request.evaluation_scope
    governance = request.knowledge_governance_decisions
    conflicts = request.knowledge_conflict_assessment_records
    authorities = request.knowledge_authority_decisions

    if (
        request.evaluation_policy_id != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID
        or request.evaluation_policy_version != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION
    ):
        return _rejected("unsupported_promotion_prerequisite_evaluation_policy")
    if scope.scope_policy_id != PROMOTION_EVALUATION_SCOPE_POLICY_ID or scope.scope_policy_version != PROMOTION_EVALUATION_SCOPE_POLICY_VERSION:
        return _rejected("unsupported_promotion_evaluation_scope_policy")
    if scope.target_knowledge_candidate_id != candidate.knowledge_candidate_id:
        return _rejected("scope_candidate_mismatch")
    if scope.target_knowledge_candidate_contract_version != candidate.contract_version:
        return _rejected("scope_candidate_contract_mismatch")
    candidate_snapshot = compute_knowledge_candidate_review_snapshot_digest(candidate)
    if scope.target_knowledge_candidate_snapshot_digest != candidate_snapshot:
        return _rejected("scope_candidate_snapshot_mismatch")

    if any(record.governance_policy_id != KNOWLEDGE_GOVERNANCE_POLICY_ID or record.governance_policy_version != KNOWLEDGE_GOVERNANCE_POLICY_VERSION for record in governance):
        return _rejected("unsupported_governance_evidence_policy")
    if any(record.knowledge_candidate_id != candidate.knowledge_candidate_id for record in governance):
        return _rejected("governance_candidate_mismatch")
    if any(record.knowledge_candidate_contract_version != candidate.contract_version for record in governance):
        return _rejected("governance_candidate_contract_mismatch")
    if any(record.knowledge_candidate_snapshot_digest != candidate_snapshot for record in governance):
        return _rejected("governance_candidate_snapshot_mismatch")

    if any(record.assessment_policy_id != KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID or record.assessment_policy_version != KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION for record in conflicts):
        return _rejected("unsupported_conflict_evidence_policy")
    peers = {peer.knowledge_candidate_id: peer for peer in scope.peers}
    conflict_peer_ids: dict[str, str] = {}
    for record in conflicts:
        participant_map = _participant_by_id(record)
        participant_ids = set(participant_map)
        if candidate.knowledge_candidate_id not in participant_ids or len(participant_ids) != 2:
            return _rejected("conflict_record_outside_declared_scope")
        peer_ids = participant_ids - {candidate.knowledge_candidate_id}
        peer_id = next(iter(peer_ids))
        if peer_id not in peers:
            return _rejected("conflict_record_outside_declared_scope")
        conflict_peer_ids[record.knowledge_conflict_assessment_record_id] = peer_id
        expected = {
            candidate.knowledge_candidate_id: (candidate.contract_version, candidate_snapshot),
            peer_id: (peers[peer_id].knowledge_candidate_contract_version, peers[peer_id].knowledge_candidate_snapshot_digest),
        }
        if any(participant_map[item].knowledge_candidate_contract_version != expected[item][0] for item in expected):
            return _rejected("conflict_participant_contract_mismatch")
        if any(participant_map[item].knowledge_candidate_snapshot_digest != expected[item][1] for item in expected):
            return _rejected("conflict_participant_snapshot_mismatch")

    if any(record.authority_policy_id != KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID or record.authority_policy_version != KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION for record in authorities):
        return _rejected("unsupported_authority_evidence_policy")
    if any(record.knowledge_candidate_id != candidate.knowledge_candidate_id for record in authorities):
        return _rejected("authority_candidate_mismatch")
    if any(record.knowledge_candidate_contract_version != candidate.contract_version for record in authorities):
        return _rejected("authority_candidate_contract_mismatch")
    if any(record.knowledge_candidate_snapshot_digest != candidate_snapshot for record in authorities):
        return _rejected("authority_candidate_snapshot_mismatch")
    direct_governance_ids = {record.knowledge_governance_decision_id for record in governance}
    if any(not set(record.knowledge_governance_decision_ids).issubset(direct_governance_ids) for record in authorities):
        return _rejected("authority_governance_lineage_mismatch")

    blockers: set[str] = set()
    deferred: set[str] = set()

    governance_values = {record.governance_decision for record in governance}
    if GOVERNANCE_DECISION_AUTHORIZED in governance_values and GOVERNANCE_DECISION_DENIED in governance_values:
        deferred.add(PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY)
    elif GOVERNANCE_DECISION_DENIED in governance_values:
        blockers.add(PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED)
    elif GOVERNANCE_DECISION_DEFERRED in governance_values:
        deferred.add(PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED)

    records_by_peer: dict[str, list[KnowledgeConflictAssessmentRecord]] = {peer_id: [] for peer_id in peers}
    for record in conflicts:
        records_by_peer[conflict_peer_ids[record.knowledge_conflict_assessment_record_id]].append(record)
    if not peers:
        deferred.add(PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY)
    for records in records_by_peer.values():
        if not records:
            deferred.add(PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE)
        elif len(records) > 1:
            deferred.add(PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS)
        else:
            outcome = records[0].assessment_outcome
            if outcome == ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED:
                blockers.add(PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED)
            elif outcome == ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED:
                deferred.add(PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED)
            elif outcome not in (ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED, ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT):
                raise ValueError("unsupported structurally valid conflict outcome")

    contradictory_authority_indexes: set[int] = set()
    for intended_value in (
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    ):
        value_indexes = {
            index
            for index, record in enumerate(authorities)
            if record.intended_authority_value == intended_value
            and record.decision_outcome
            in (AUTHORITY_DECISION_OUTCOME_AUTHORIZED, AUTHORITY_DECISION_OUTCOME_DENIED)
        }
        value_outcomes = {authorities[index].decision_outcome for index in value_indexes}
        if {
            AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
            AUTHORITY_DECISION_OUTCOME_DENIED,
        }.issubset(value_outcomes):
            contradictory_authority_indexes.update(value_indexes)

    incompatible_authorized_indexes = {
        index
        for index, record in enumerate(authorities)
        if record.intended_authority_value
        in (
            INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
            INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        )
        and record.decision_outcome == AUTHORITY_DECISION_OUTCOME_AUTHORIZED
    }
    incompatible_authorized_values = {
        authorities[index].intended_authority_value
        for index in incompatible_authorized_indexes
    }
    if incompatible_authorized_values == {
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    }:
        contradictory_authority_indexes.update(incompatible_authorized_indexes)

    if contradictory_authority_indexes:
        deferred.add(PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY)
    for index, record in enumerate(authorities):
        if index in contradictory_authority_indexes:
            continue
        if record.decision_outcome == AUTHORITY_DECISION_OUTCOME_DEFERRED:
            deferred.add(PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED)
        elif record.intended_authority_value == INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE and record.decision_outcome == AUTHORITY_DECISION_OUTCOME_AUTHORIZED:
            blockers.add(PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE)
        elif record.intended_authority_value == INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE and record.decision_outcome == AUTHORITY_DECISION_OUTCOME_DENIED:
            blockers.add(PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED)
        elif record.intended_authority_value == INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE and record.decision_outcome == AUTHORITY_DECISION_OUTCOME_DENIED:
            deferred.add(PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE)

    if blockers:
        outcome = PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE
        computed_reasons = tuple(sorted(blockers | {PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED}))
    elif deferred:
        outcome = PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
        computed_reasons = tuple(sorted(deferred | {PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED}))
    else:
        outcome = PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
        computed_reasons = (PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,)

    if request.reason_codes != computed_reasons:
        return _rejected("missing_or_mismatched_required_evaluation_reason")

    identity_input = KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=candidate_snapshot,
        knowledge_promotion_evaluation_scope_id=scope.knowledge_promotion_evaluation_scope_id,
        knowledge_governance_decision_ids=tuple(record.knowledge_governance_decision_id for record in governance),
        knowledge_conflict_assessment_record_ids=tuple(record.knowledge_conflict_assessment_record_id for record in conflicts),
        knowledge_authority_decision_ids=tuple(record.knowledge_authority_decision_id for record in authorities),
        evaluation_scope=PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
        completeness_basis=PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
        evaluation_outcome=outcome,
        reason_codes=computed_reasons,
        evaluated_by=request.evaluated_by,
        evaluated_at=request.evaluated_at,
        evaluation_policy_id=request.evaluation_policy_id,
        evaluation_policy_version=request.evaluation_policy_version,
    )
    evaluation = KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=compute_knowledge_promotion_prerequisite_evaluation_id(identity_input),
        contract_version=identity_input.evaluation_record_contract_version,
        knowledge_candidate_id=identity_input.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity_input.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity_input.knowledge_candidate_snapshot_digest,
        knowledge_promotion_evaluation_scope_id=identity_input.knowledge_promotion_evaluation_scope_id,
        knowledge_governance_decision_ids=identity_input.knowledge_governance_decision_ids,
        knowledge_conflict_assessment_record_ids=identity_input.knowledge_conflict_assessment_record_ids,
        knowledge_authority_decision_ids=identity_input.knowledge_authority_decision_ids,
        evaluation_scope=identity_input.evaluation_scope,
        completeness_basis=identity_input.completeness_basis,
        evaluation_outcome=identity_input.evaluation_outcome,
        reason_codes=identity_input.reason_codes,
        evaluated_by=identity_input.evaluated_by,
        evaluated_at=identity_input.evaluated_at,
        evaluation_policy_id=identity_input.evaluation_policy_id,
        evaluation_policy_version=identity_input.evaluation_policy_version,
        diagnostics=(),
    )
    return KnowledgePromotionPrerequisiteEvaluationResult(
        result_status=PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED,
        evaluation=evaluation,
        reason_codes=(),
        diagnostics=(),
    )
