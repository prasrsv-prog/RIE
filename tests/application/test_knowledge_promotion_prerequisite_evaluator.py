import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

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
from rie.application.knowledge_promotion_prerequisite_evaluator import (
    KnowledgePromotionPrerequisiteEvaluationRequest,
    KnowledgePromotionPrerequisiteEvaluationResult,
    evaluate_knowledge_promotion_prerequisites,
)
from rie.domain.knowledge_authority_decision import (
    AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    AUTHORITY_DECISION_OUTCOME_DEFERRED,
    AUTHORITY_DECISION_OUTCOME_DENIED,
    AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY,
    INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION,
    KnowledgeAuthorityDecision,
    KnowledgeAuthorityIdentityInput,
    compute_knowledge_authority_decision_id,
)
from rie.domain.knowledge_candidate import (
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    VERBATIM_TEXT_STATEMENT_TYPE,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
)
from rie.domain.knowledge_conflict_assessment_record import (
    ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
    ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
    ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
    ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP,
    KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION,
    KnowledgeConflictAssessmentRecord,
    KnowledgeConflictIdentityInput,
    KnowledgeConflictParticipant,
    compute_knowledge_conflict_assessment_record_id,
    knowledge_conflict_participant_from_candidate,
)
from rie.domain.knowledge_governance_decision import (
    AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION,
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
    KnowledgeGovernanceDecision,
    KnowledgeGovernanceIdentityInput,
    compute_knowledge_governance_candidate_snapshot_digest,
    compute_knowledge_governance_decision_id,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_EVALUATION_SCOPE_POLICY_ID,
    PROMOTION_EVALUATION_SCOPE_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED,
    KnowledgePromotionEvaluationScope,
    KnowledgePromotionEvaluationScopeIdentityInput,
    KnowledgePromotionEvaluationScopePeer,
    KnowledgePromotionPrerequisiteDiagnostic,
    KnowledgePromotionPrerequisiteEvaluation,
    compute_knowledge_promotion_evaluation_scope_id,
)


FIXED_TIME = datetime(2026, 7, 13, 17, 45, 30, 654321, tzinfo=timezone.utc)


def _support(seed: str) -> KnowledgeEvidenceSupport:
    return KnowledgeEvidenceSupport(
        evidence_id="ev1_" + seed * 64,
        acceptance_record_ids=("ar1_" + seed * 64,),
        acceptance_review_record_ids=(f"acceptance-review-{seed}",),
        source_id=f"source-{seed}",
        source_content_digest=seed * 64,
        source_authority_status="official",
        source_lifecycle_status="active",
        payload_digest=("a" if seed == "1" else seed) * 64,
        locator_type="page",
        locator_value=(int(seed, 16),),
        locator_schema_version="1.0.0",
    )


def _candidate(seed: str = "1", statement: str | None = None) -> KnowledgeCandidate:
    support = _support(seed)
    identity = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement or f"Candidate statement {seed}.",
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=(support,),
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
    )
    return KnowledgeCandidate(
        knowledge_candidate_id=compute_knowledge_candidate_id(identity),
        contract_version=identity.candidate_contract_version,
        statement_type=identity.statement_type,
        statement=identity.statement,
        support=identity.support,
        construction_rule_id=identity.construction_rule_id,
        construction_rule_version=identity.construction_rule_version,
        authority_status=identity.authority_status,
        lifecycle_status=identity.lifecycle_status,
        review_status=identity.review_status,
        conflict_status=identity.conflict_status,
        conflict_ids=(),
        diagnostics=(),
    )


def _governance(
    candidate: KnowledgeCandidate,
    decision: str = GOVERNANCE_DECISION_AUTHORIZED,
    *,
    seed: str = "1",
    policy_id: str = KNOWLEDGE_GOVERNANCE_POLICY_ID,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
) -> KnowledgeGovernanceDecision:
    reason = {
        GOVERNANCE_DECISION_AUTHORIZED: "eligible_review_evidence",
        GOVERNANCE_DECISION_DENIED: "review_evidence_rejected",
        GOVERNANCE_DECISION_DEFERRED: "governance_evaluation_deferred",
    }[decision]
    identity = KnowledgeGovernanceIdentityInput(
        governance_decision_contract_version=KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate_contract or candidate.contract_version,
        knowledge_candidate_snapshot_digest=snapshot or compute_knowledge_governance_candidate_snapshot_digest(candidate),
        knowledge_review_record_ids=("kr1_" + seed * 64,),
        authorization_scope=AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION,
        governance_decision=decision,
        reason_codes=(reason,),
        decided_by=f"governance-{seed}",
        decided_at=FIXED_TIME + timedelta(minutes=int(seed, 16)),
        governance_policy_id=policy_id,
        governance_policy_version=KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
    )
    return KnowledgeGovernanceDecision(
        knowledge_governance_decision_id=compute_knowledge_governance_decision_id(identity),
        contract_version=identity.governance_decision_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        knowledge_review_record_ids=identity.knowledge_review_record_ids,
        authorization_scope=identity.authorization_scope,
        governance_decision=identity.governance_decision,
        reason_codes=identity.reason_codes,
        decided_by=identity.decided_by,
        decided_at=identity.decided_at,
        governance_policy_id=identity.governance_policy_id,
        governance_policy_version=identity.governance_policy_version,
        diagnostics=(),
    )


def _scope(
    target: KnowledgeCandidate,
    peers: tuple[KnowledgeCandidate, ...],
    *,
    policy_id: str = PROMOTION_EVALUATION_SCOPE_POLICY_ID,
    policy_version: str = PROMOTION_EVALUATION_SCOPE_POLICY_VERSION,
    target_id: str | None = None,
    target_contract: str | None = None,
    target_snapshot: str | None = None,
) -> KnowledgePromotionEvaluationScope:
    scope_peers = tuple(
        sorted(
            (
                KnowledgePromotionEvaluationScopePeer(
                    knowledge_candidate_id=peer.knowledge_candidate_id,
                    knowledge_candidate_contract_version=peer.contract_version,
                    knowledge_candidate_snapshot_digest=compute_knowledge_governance_candidate_snapshot_digest(peer),
                )
                for peer in peers
            ),
            key=lambda value: value.knowledge_candidate_id,
        )
    )
    identity = KnowledgePromotionEvaluationScopeIdentityInput(
        scope_contract_version=KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION,
        target_knowledge_candidate_id=target_id or target.knowledge_candidate_id,
        target_knowledge_candidate_contract_version=target_contract or target.contract_version,
        target_knowledge_candidate_snapshot_digest=target_snapshot or compute_knowledge_governance_candidate_snapshot_digest(target),
        peers=scope_peers,
        completeness_qualifier=PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE,
        scoped_by="scope-actor",
        reason_codes=("declared_scope_selected",),
        scoped_at=FIXED_TIME,
        scope_policy_id=policy_id,
        scope_policy_version=policy_version,
    )
    return KnowledgePromotionEvaluationScope(
        knowledge_promotion_evaluation_scope_id=compute_knowledge_promotion_evaluation_scope_id(identity),
        contract_version=identity.scope_contract_version,
        target_knowledge_candidate_id=identity.target_knowledge_candidate_id,
        target_knowledge_candidate_contract_version=identity.target_knowledge_candidate_contract_version,
        target_knowledge_candidate_snapshot_digest=identity.target_knowledge_candidate_snapshot_digest,
        peers=identity.peers,
        completeness_qualifier=identity.completeness_qualifier,
        scoped_by=identity.scoped_by,
        reason_codes=identity.reason_codes,
        scoped_at=identity.scoped_at,
        scope_policy_id=identity.scope_policy_id,
        scope_policy_version=identity.scope_policy_version,
    )


def _conflict(
    target: KnowledgeCandidate,
    peer: KnowledgeCandidate,
    outcome: str = ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
    *,
    seed: str = "1",
    policy_id: str = KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID,
    participant_override: KnowledgeConflictParticipant | None = None,
) -> KnowledgeConflictAssessmentRecord:
    participants = list(
        sorted(
            (knowledge_conflict_participant_from_candidate(target), knowledge_conflict_participant_from_candidate(peer)),
            key=lambda item: item.knowledge_candidate_id,
        )
    )
    if participant_override is not None:
        index = next(i for i, item in enumerate(participants) if item.knowledge_candidate_id == participant_override.knowledge_candidate_id)
        participants[index] = participant_override
    reasons = {
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED: ("pairwise_no_conflict_identified",),
        ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT: ("semantic_equivalence_identified",),
        ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED: ("semantic_conflict_identified",),
        ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED: ("semantic_assessment_deferred",),
    }[outcome]
    identity = KnowledgeConflictIdentityInput(
        conflict_assessment_record_contract_version=KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION,
        participants=tuple(participants),
        assessment_scope=ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP,
        assessment_outcome=outcome,
        reason_codes=reasons,
        assessed_by=f"conflict-{seed}",
        assessed_at=FIXED_TIME + timedelta(minutes=int(seed, 16)),
        assessment_policy_id=policy_id,
        assessment_policy_version=KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION,
    )
    return KnowledgeConflictAssessmentRecord(
        knowledge_conflict_assessment_record_id=compute_knowledge_conflict_assessment_record_id(identity),
        contract_version=identity.conflict_assessment_record_contract_version,
        participants=identity.participants,
        assessment_scope=identity.assessment_scope,
        assessment_outcome=identity.assessment_outcome,
        reason_codes=identity.reason_codes,
        assessed_by=identity.assessed_by,
        assessed_at=identity.assessed_at,
        assessment_policy_id=identity.assessment_policy_id,
        assessment_policy_version=identity.assessment_policy_version,
        diagnostics=(),
    )


def _authority(
    candidate: KnowledgeCandidate,
    governance: tuple[KnowledgeGovernanceDecision, ...],
    *,
    intended: str = INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    outcome: str = AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    seed: str = "1",
    policy_id: str = KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
) -> KnowledgeAuthorityDecision:
    governance_ids = tuple(sorted(record.knowledge_governance_decision_id for record in governance))
    reason = {
        AUTHORITY_DECISION_OUTCOME_AUTHORIZED: "intended_knowledge_authority_authorized",
        AUTHORITY_DECISION_OUTCOME_DENIED: "intended_knowledge_authority_denied",
        AUTHORITY_DECISION_OUTCOME_DEFERRED: "intended_knowledge_authority_deferred",
    }[outcome]
    identity = KnowledgeAuthorityIdentityInput(
        authority_decision_record_contract_version=KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate_contract or candidate.contract_version,
        knowledge_candidate_snapshot_digest=snapshot or compute_knowledge_governance_candidate_snapshot_digest(candidate),
        knowledge_governance_decision_ids=governance_ids,
        authority_scope=AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY,
        intended_authority_value=intended,
        decision_outcome=outcome,
        reason_codes=(reason,),
        decided_by=f"authority-{seed}",
        decided_at=FIXED_TIME + timedelta(hours=1, minutes=int(seed, 16)),
        authority_policy_id=policy_id,
        authority_policy_version=KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION,
    )
    return KnowledgeAuthorityDecision(
        knowledge_authority_decision_id=compute_knowledge_authority_decision_id(identity),
        contract_version=identity.authority_decision_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        knowledge_governance_decision_ids=identity.knowledge_governance_decision_ids,
        authority_scope=identity.authority_scope,
        intended_authority_value=identity.intended_authority_value,
        decision_outcome=identity.decision_outcome,
        reason_codes=identity.reason_codes,
        decided_by=identity.decided_by,
        decided_at=identity.decided_at,
        authority_policy_id=identity.authority_policy_id,
        authority_policy_version=identity.authority_policy_version,
        diagnostics=(),
    )


def _ordered(records: tuple[object, ...], attribute: str) -> tuple[object, ...]:
    return tuple(sorted(records, key=lambda item: getattr(item, attribute)))


def _request(
    candidate: KnowledgeCandidate,
    scope: KnowledgePromotionEvaluationScope,
    governance: tuple[KnowledgeGovernanceDecision, ...],
    conflicts: tuple[KnowledgeConflictAssessmentRecord, ...],
    authorities: tuple[KnowledgeAuthorityDecision, ...],
    reasons: tuple[str, ...],
    *,
    policy_id: str = KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
) -> KnowledgePromotionPrerequisiteEvaluationRequest:
    return KnowledgePromotionPrerequisiteEvaluationRequest(
        knowledge_candidate=candidate,
        evaluation_scope=scope,
        knowledge_governance_decisions=_ordered(governance, "knowledge_governance_decision_id"),  # type: ignore[arg-type]
        knowledge_conflict_assessment_records=_ordered(conflicts, "knowledge_conflict_assessment_record_id"),  # type: ignore[arg-type]
        knowledge_authority_decisions=_ordered(authorities, "knowledge_authority_decision_id"),  # type: ignore[arg-type]
        reason_codes=reasons,
        evaluated_by="evaluation-actor",
        evaluated_at=FIXED_TIME + timedelta(hours=2),
        evaluation_policy_id=policy_id,
        evaluation_policy_version=KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    )


def _base() -> tuple[KnowledgeCandidate, KnowledgeCandidate, KnowledgeGovernanceDecision, KnowledgePromotionEvaluationScope, KnowledgeConflictAssessmentRecord, KnowledgeAuthorityDecision]:
    candidate, peer = _candidate("1"), _candidate("2")
    governance = _governance(candidate)
    return candidate, peer, governance, _scope(candidate, (peer,)), _conflict(candidate, peer), _authority(candidate, (governance,))


def _recorded(request: KnowledgePromotionPrerequisiteEvaluationRequest) -> KnowledgePromotionPrerequisiteEvaluation:
    result = evaluate_knowledge_promotion_prerequisites(request)
    assert result.result_status == PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED
    assert type(result.evaluation) is KnowledgePromotionPrerequisiteEvaluation
    assert result.reason_codes == () and result.diagnostics == ()
    return result.evaluation


def _rejected(request: KnowledgePromotionPrerequisiteEvaluationRequest, reason: str) -> KnowledgePromotionPrerequisiteEvaluationResult:
    result = evaluate_knowledge_promotion_prerequisites(request)
    assert result.result_status == PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED
    assert result.evaluation is None and result.reason_codes == (reason,)
    assert len(result.diagnostics) == 1 and result.diagnostics[0].code == reason
    return result


def test_a01_complete_compatible_scope_is_satisfied_without_mutation() -> None:
    candidate, peer, governance, scope, conflict, authority = _base()
    request = _request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))
    before = (candidate, peer, governance, scope, conflict, authority, request)
    evaluation = _recorded(request)
    assert evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
    assert before == (candidate, peer, governance, scope, conflict, authority, request)


def test_a02_empty_peer_scope_is_deferred_and_never_positive() -> None:
    candidate = _candidate("1"); governance = _governance(candidate); scope = _scope(candidate, ()); authority = _authority(candidate, (governance,))
    reasons = ("declared_peer_scope_empty", "declared_scope_prerequisites_deferred")
    evaluation = _recorded(_request(candidate, scope, (governance,), (), (authority,), reasons))
    assert evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE


def test_a03_missing_declared_peer_assessment_is_deferred() -> None:
    candidate, peer, governance, scope, _, authority = _base()
    reasons = ("declared_scope_conflict_coverage_incomplete", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (), (authority,), reasons)).reason_codes == reasons


def test_a04_exactly_one_non_conflict_assessment_per_peer_is_positive() -> None:
    candidate, peer, governance, scope, _, authority = _base()
    conflict = _conflict(candidate, peer, ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT)
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE


def test_a05_one_conflict_identified_is_not_satisfied_without_resolution() -> None:
    candidate, peer, governance, scope, _, authority = _base(); conflict = _conflict(candidate, peer, ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED)
    reasons = ("declared_scope_conflict_identified", "declared_scope_prerequisites_not_satisfied")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), reasons)).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE


def test_a06_one_deferred_assessment_is_deferred() -> None:
    candidate, peer, governance, scope, _, authority = _base(); conflict = _conflict(candidate, peer, ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED)
    reasons = ("declared_scope_conflict_evidence_deferred", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), reasons)).reason_codes == reasons


def test_a07_distinct_same_pair_records_defer_even_with_conflict() -> None:
    candidate, peer, governance, scope, _, authority = _base(); conflicts = (_conflict(candidate, peer, seed="1"), _conflict(candidate, peer, ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED, seed="2"))
    reasons = ("declared_scope_conflict_evidence_ambiguous", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), conflicts, (authority,), reasons)).reason_codes == reasons


def test_a08_incompatible_same_pair_outcomes_defer_as_ambiguity() -> None:
    candidate, peer, governance, scope, _, authority = _base(); conflicts = (_conflict(candidate, peer, ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT, seed="1"), _conflict(candidate, peer, ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED, seed="2"))
    reasons = ("declared_scope_conflict_evidence_ambiguous", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), conflicts, (authority,), reasons)).reason_codes == reasons


def test_a09_extra_scope_conflict_rejects_at_precedence() -> None:
    candidate, peer, governance, scope, _, authority = _base(); outside = _candidate("3")
    _rejected(_request(candidate, scope, (governance,), (_conflict(candidate, outside),), (authority,), ("declared_scope_prerequisites_satisfied",)), "conflict_record_outside_declared_scope")


def test_a10_conflict_participant_contract_and_snapshot_mismatches_reject() -> None:
    candidate, peer, governance, scope, _, authority = _base(); participant = knowledge_conflict_participant_from_candidate(peer)
    bad_contract = replace(participant, knowledge_candidate_contract_version="other")
    _rejected(_request(candidate, scope, (governance,), (_conflict(candidate, peer, participant_override=bad_contract),), (authority,), ("declared_scope_prerequisites_satisfied",)), "conflict_participant_contract_mismatch")
    bad_snapshot = replace(participant, knowledge_candidate_snapshot_digest="f" * 64)
    _rejected(_request(candidate, scope, (governance,), (_conflict(candidate, peer, participant_override=bad_snapshot),), (authority,), ("declared_scope_prerequisites_satisfied",)), "conflict_participant_snapshot_mismatch")


def test_a11_all_direct_authorized_governance_satisfies() -> None:
    candidate, _, governance, scope, conflict, authority = _base()
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE


def test_a12_denied_governance_without_authorized_is_not_satisfied() -> None:
    candidate, peer = _candidate("1"), _candidate("2"); governance = _governance(candidate, GOVERNANCE_DECISION_DENIED); authority = _authority(candidate, (governance,)); reasons = ("declared_scope_prerequisites_not_satisfied", "governance_evidence_denied")
    assert _recorded(_request(candidate, _scope(candidate, (peer,)), (governance,), (_conflict(candidate, peer),), (authority,), reasons)).reason_codes == reasons


def test_a13_deferred_governance_is_deferred() -> None:
    candidate, peer = _candidate("1"), _candidate("2"); governance = _governance(candidate, GOVERNANCE_DECISION_DEFERRED); authority = _authority(candidate, (governance,)); reasons = ("declared_scope_prerequisites_deferred", "governance_evidence_deferred")
    assert _recorded(_request(candidate, _scope(candidate, (peer,)), (governance,), (_conflict(candidate, peer),), (authority,), reasons)).reason_codes == reasons


def test_a14_authorized_plus_denied_governance_is_contradictory_deferred() -> None:
    candidate, peer = _candidate("1"), _candidate("2"); first = _governance(candidate, seed="1"); second = _governance(candidate, GOVERNANCE_DECISION_DENIED, seed="2"); authority = _authority(candidate, (first,)); reasons = ("declared_scope_prerequisites_deferred", "governance_evidence_contradictory")
    assert _recorded(_request(candidate, _scope(candidate, (peer,)), (first, second), (_conflict(candidate, peer),), (authority,), reasons)).reason_codes == reasons


def test_a15_governance_identity_policy_lineage_order_and_uniqueness_are_direct() -> None:
    candidate, peer, other = _candidate("1"), _candidate("2"), _candidate("3")
    scope, conflict = _scope(candidate, (peer,)), _conflict(candidate, peer)
    first, second = _governance(candidate, seed="1"), _governance(candidate, seed="2")
    ordered = _ordered((first, second), "knowledge_governance_decision_id")
    authority = _authority(candidate, ordered)  # type: ignore[arg-type]
    request = _request(candidate, scope, ordered, (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))  # type: ignore[arg-type]
    evaluation = _recorded(request)
    assert request.knowledge_governance_decisions == ordered
    assert evaluation.knowledge_governance_decision_ids == tuple(record.knowledge_governance_decision_id for record in ordered)

    for malformed_id in ("kg1_bad", "kg1_" + "f" * 64):
        malformed = replace(first)
        object.__setattr__(malformed, "knowledge_governance_decision_id", malformed_id)
        with pytest.raises(ValueError):
            replace(request, knowledge_governance_decisions=(malformed,))

    unsupported = _governance(candidate, policy_id="unsupported")
    unsupported_authority = _authority(candidate, (unsupported,))
    _rejected(_request(candidate, scope, (unsupported,), (conflict,), (unsupported_authority,), ("declared_scope_prerequisites_satisfied",)), "unsupported_governance_evidence_policy")
    mismatch_cases = (
        (_governance(candidate, candidate_id=other.knowledge_candidate_id), "governance_candidate_mismatch"),
        (_governance(candidate, candidate_contract="other-contract"), "governance_candidate_contract_mismatch"),
        (_governance(candidate, snapshot="f" * 64), "governance_candidate_snapshot_mismatch"),
    )
    for bad, reason in mismatch_cases:
        bad_authority = _authority(candidate, (bad,))
        _rejected(_request(candidate, scope, (bad,), (conflict,), (bad_authority,), ("declared_scope_prerequisites_satisfied",)), reason)
    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=(first, first))
    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=tuple(reversed(ordered)))


def test_a16_consistent_authorized_authoritative_decisions_satisfy() -> None:
    candidate, _, governance, scope, conflict, authority = _base()
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE


def test_a17_authorized_non_authoritative_is_not_satisfied() -> None:
    candidate, peer, governance, scope, conflict, _ = _base(); authority = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE)
    reasons = ("authority_value_not_authoritative", "declared_scope_prerequisites_not_satisfied")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), reasons)).reason_codes == reasons


def test_a18_denied_authoritative_is_not_satisfied_without_opposite_inference() -> None:
    candidate, _, governance, scope, conflict, _ = _base(); authority = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DENIED)
    reasons = ("authoritative_value_denied", "declared_scope_prerequisites_not_satisfied")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), reasons)).reason_codes == reasons


def test_a19_deferred_and_denied_non_authoritative_are_deferred() -> None:
    candidate, _, governance, scope, conflict, _ = _base()
    deferred = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED)
    reasons = ("authority_evidence_deferred", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (deferred,), reasons)).reason_codes == reasons
    denied = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, outcome=AUTHORITY_DECISION_OUTCOME_DENIED)
    reasons = ("authority_evidence_not_affirmative", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (denied,), reasons)).reason_codes == reasons


def test_a20_multiple_consistent_authority_decisions_coexist_without_winner() -> None:
    candidate, _, governance, scope, conflict, authority = _base(); second = _authority(candidate, (governance,), seed="2")
    evaluation = _recorded(_request(candidate, scope, (governance,), (conflict,), (authority, second), ("declared_scope_prerequisites_satisfied",)))
    assert len(evaluation.knowledge_authority_decision_ids) == 2


def test_a21_same_value_authorized_and_denied_is_contradictory_deferred() -> None:
    candidate, _, governance, scope, conflict, authorized = _base(); denied = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="2")
    reasons = ("authority_evidence_contradictory", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authorized, denied), reasons)).reason_codes == reasons
    non_authorized = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, seed="3")
    non_denied = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="4")
    authoritative_denied = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="5")
    blocker_reasons = ("authoritative_value_denied", "declared_scope_prerequisites_not_satisfied")
    blocker_evaluation = _recorded(_request(candidate, scope, (governance,), (conflict,), (non_authorized, non_denied, authoritative_denied), blocker_reasons))
    assert blocker_evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE
    assert blocker_evaluation.reason_codes == blocker_reasons

    authoritative_authorized = _authority(candidate, (governance,), seed="6")
    authoritative_denied = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="7")
    non_denied = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="8")
    deferred_reasons = ("authority_evidence_contradictory", "authority_evidence_not_affirmative", "declared_scope_prerequisites_deferred")
    deferred_evaluation = _recorded(_request(candidate, scope, (governance,), (conflict,), (authoritative_authorized, authoritative_denied, non_denied), deferred_reasons))
    assert deferred_evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
    assert deferred_evaluation.reason_codes == deferred_reasons


def test_a22_authorized_incompatible_values_are_contradictory_deferred() -> None:
    candidate, _, governance, scope, conflict, authorized = _base(); other = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, seed="2")
    reasons = ("authority_evidence_contradictory", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authorized, other), reasons)).reason_codes == reasons
    additional_deferred = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED, seed="3")
    combined_reasons = ("authority_evidence_contradictory", "authority_evidence_deferred", "declared_scope_prerequisites_deferred")
    evaluation = _recorded(_request(candidate, scope, (governance,), (conflict,), (authorized, other, additional_deferred), combined_reasons))
    assert evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
    assert evaluation.reason_codes == combined_reasons


def test_a23_authority_lineages_are_ordered_subsets_and_missing_ids_reject() -> None:
    candidate, peer = _candidate("1"), _candidate("2"); first = _governance(candidate, seed="1"); second = _governance(candidate, seed="2")
    authorities = (_authority(candidate, (first,), seed="1"), _authority(candidate, (second,), seed="2"))
    assert _recorded(_request(candidate, _scope(candidate, (peer,)), (first, second), (_conflict(candidate, peer),), authorities, ("declared_scope_prerequisites_satisfied",))).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
    missing = _governance(candidate, seed="3"); authority = _authority(candidate, (missing,))
    _rejected(_request(candidate, _scope(candidate, (peer,)), (first, second), (_conflict(candidate, peer),), (authority,), ("declared_scope_prerequisites_satisfied",)), "authority_governance_lineage_mismatch")


def test_a24_actor_timestamp_id_age_and_position_never_select_winners() -> None:
    candidate, peer, governance, scope, _, authority = _base(); conflicts = (_conflict(candidate, peer, seed="1"), _conflict(candidate, peer, ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED, seed="2"))
    reasons = ("declared_scope_conflict_evidence_ambiguous", "declared_scope_prerequisites_deferred")
    assert _recorded(_request(candidate, scope, (governance,), conflicts, (authority,), reasons)).evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE


def test_a25_unsupported_policies_reject_in_exact_precedence() -> None:
    candidate, peer, governance, scope, conflict, authority = _base(); satisfied = ("declared_scope_prerequisites_satisfied",)
    _rejected(_request(candidate, scope, (governance,), (conflict,), (authority,), satisfied, policy_id="unsupported"), "unsupported_promotion_prerequisite_evaluation_policy")
    bad_scope = _scope(candidate, (peer,), policy_id="unsupported")
    _rejected(_request(candidate, bad_scope, (governance,), (conflict,), (authority,), satisfied), "unsupported_promotion_evaluation_scope_policy")
    bad_governance = _governance(candidate, policy_id="unsupported")
    bad_governance_authority = _authority(candidate, (bad_governance,))
    _rejected(_request(candidate, scope, (bad_governance,), (conflict,), (bad_governance_authority,), satisfied), "unsupported_governance_evidence_policy")
    bad_conflict = _conflict(candidate, peer, policy_id="unsupported")
    _rejected(_request(candidate, scope, (governance,), (bad_conflict,), (authority,), satisfied), "unsupported_conflict_evidence_policy")
    bad_authority = _authority(candidate, (governance,), policy_id="unsupported")
    _rejected(_request(candidate, scope, (governance,), (conflict,), (bad_authority,), satisfied), "unsupported_authority_evidence_policy")

    all_bad_authority = _authority(candidate, (bad_governance,), policy_id="unsupported")
    all_bad = _request(candidate, bad_scope, (bad_governance,), (bad_conflict,), (all_bad_authority,), satisfied, policy_id="unsupported")
    _rejected(all_bad, "unsupported_promotion_prerequisite_evaluation_policy")
    _rejected(replace(all_bad, evaluation_policy_id=KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID), "unsupported_promotion_evaluation_scope_policy")
    governance_first = _request(candidate, scope, (bad_governance,), (bad_conflict,), (all_bad_authority,), satisfied)
    _rejected(governance_first, "unsupported_governance_evidence_policy")
    conflict_first = _request(candidate, scope, (governance,), (bad_conflict,), (bad_authority,), satisfied)
    _rejected(conflict_first, "unsupported_conflict_evidence_policy")


def test_a26_scope_candidate_and_upstream_lineage_mismatches_reject_in_order() -> None:
    candidate, peer, governance, scope, conflict, authority = _base(); other = _candidate("3"); satisfied = ("declared_scope_prerequisites_satisfied",)
    candidate_snapshot = compute_knowledge_governance_candidate_snapshot_digest(candidate)
    scope_cases = (
        (_scope(candidate, (peer,), target_id=other.knowledge_candidate_id, target_snapshot=candidate_snapshot), "scope_candidate_mismatch"),
        (_scope(candidate, (peer,), target_contract="other-contract"), "scope_candidate_contract_mismatch"),
        (_scope(candidate, (peer,), target_snapshot="f" * 64), "scope_candidate_snapshot_mismatch"),
    )
    for bad_scope, reason in scope_cases:
        _rejected(_request(candidate, bad_scope, (governance,), (conflict,), (authority,), satisfied), reason)

    governance_cases = (
        (_governance(candidate, candidate_id=other.knowledge_candidate_id), "governance_candidate_mismatch"),
        (_governance(candidate, candidate_contract="other-contract"), "governance_candidate_contract_mismatch"),
        (_governance(candidate, snapshot="f" * 64), "governance_candidate_snapshot_mismatch"),
    )
    for bad_governance, reason in governance_cases:
        bad_authority = _authority(candidate, (bad_governance,))
        _rejected(_request(candidate, scope, (bad_governance,), (conflict,), (bad_authority,), satisfied), reason)

    outside = _conflict(other, peer)
    _rejected(_request(candidate, scope, (governance,), (outside,), (authority,), satisfied), "conflict_record_outside_declared_scope")
    participant = knowledge_conflict_participant_from_candidate(peer)
    conflict_cases = (
        (_conflict(candidate, peer, participant_override=replace(participant, knowledge_candidate_contract_version="other-contract")), "conflict_participant_contract_mismatch"),
        (_conflict(candidate, peer, participant_override=replace(participant, knowledge_candidate_snapshot_digest="f" * 64)), "conflict_participant_snapshot_mismatch"),
    )
    for bad_conflict, reason in conflict_cases:
        _rejected(_request(candidate, scope, (governance,), (bad_conflict,), (authority,), satisfied), reason)

    authority_cases = (
        (_authority(candidate, (governance,), candidate_id=other.knowledge_candidate_id), "authority_candidate_mismatch"),
        (_authority(candidate, (governance,), candidate_contract="other-contract"), "authority_candidate_contract_mismatch"),
        (_authority(candidate, (governance,), snapshot="f" * 64), "authority_candidate_snapshot_mismatch"),
    )
    for bad_authority, reason in authority_cases:
        _rejected(_request(candidate, scope, (governance,), (conflict,), (bad_authority,), satisfied), reason)


def test_a27_exact_computed_reason_algorithm_rejects_every_mismatch_without_repair() -> None:
    candidate, peer, governance, scope, conflict, authority = _base()
    denied_governance = _governance(candidate, GOVERNANCE_DECISION_DENIED)
    conflict_blocker = _conflict(candidate, peer, ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED)
    non_authoritative_blocker = _authority(candidate, (denied_governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, seed="2")
    authoritative_blocker = _authority(candidate, (denied_governance,), outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="3")
    blocker_reasons = (
        "authoritative_value_denied",
        "authority_value_not_authoritative",
        "declared_scope_conflict_identified",
        "declared_scope_prerequisites_not_satisfied",
        "governance_evidence_denied",
    )
    blocked = _recorded(_request(candidate, scope, (denied_governance,), (conflict_blocker,), (non_authoritative_blocker, authoritative_blocker), blocker_reasons))
    assert blocked.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE
    assert blocked.reason_codes == blocker_reasons

    deferred_governance = _governance(candidate, GOVERNANCE_DECISION_DEFERRED)
    deferred_conflict = _conflict(candidate, peer, ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED)
    deferred_authority = _authority(candidate, (deferred_governance,), outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED)
    deferred_reasons = ("authority_evidence_deferred", "declared_scope_conflict_evidence_deferred", "declared_scope_prerequisites_deferred", "governance_evidence_deferred")
    deferred_evaluation = _recorded(_request(candidate, scope, (deferred_governance,), (deferred_conflict,), (deferred_authority,), deferred_reasons))
    assert deferred_evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
    assert deferred_evaluation.reason_codes == deferred_reasons

    extra_deferred_governance = _governance(candidate, GOVERNANCE_DECISION_DEFERRED, seed="2")
    governance_blocker_reasons = ("declared_scope_prerequisites_not_satisfied", "governance_evidence_denied")
    governance_blocked = _recorded(_request(candidate, scope, (denied_governance, extra_deferred_governance), (conflict,), (_authority(candidate, (denied_governance,), seed="4"),), governance_blocker_reasons))
    assert governance_blocked.reason_codes == governance_blocker_reasons
    assert "governance_evidence_deferred" not in governance_blocked.reason_codes

    affirmative = _authority(candidate, (governance,), seed="5")
    denied_non_authoritative = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="6")
    non_affirmative_reasons = ("authority_evidence_not_affirmative", "declared_scope_prerequisites_deferred")
    non_affirmative = _recorded(_request(candidate, scope, (governance,), (conflict,), (affirmative, denied_non_authoritative), non_affirmative_reasons))
    assert non_affirmative.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE

    deferred_authority = _authority(candidate, (governance,), outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED, seed="7")
    conflict_blocker_reasons = ("declared_scope_conflict_identified", "declared_scope_prerequisites_not_satisfied")
    conflict_blocked = _recorded(_request(candidate, scope, (governance,), (conflict_blocker,), (deferred_authority,), conflict_blocker_reasons))
    assert conflict_blocked.reason_codes == conflict_blocker_reasons
    assert "authority_evidence_deferred" not in conflict_blocked.reason_codes

    mixed_blocked = _recorded(_request(candidate, scope, (denied_governance,), (conflict_blocker,), (non_authoritative_blocker, authoritative_blocker, _authority(candidate, (denied_governance,), outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED, seed="8")), blocker_reasons))
    assert mixed_blocked.reason_codes == blocker_reasons
    assert not {"authority_evidence_deferred", "governance_evidence_deferred"}.intersection(mixed_blocked.reason_codes)

    satisfied_reasons = ("declared_scope_prerequisites_satisfied",)
    assert _recorded(_request(candidate, scope, (governance,), (conflict,), (authority,), satisfied_reasons)).reason_codes == satisfied_reasons

    mismatched_requests = (
        _request(candidate, scope, (governance,), (conflict_blocker,), (authority,), ("declared_scope_prerequisites_not_satisfied",)),
        _request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied", "governance_evidence_deferred")),
        _request(candidate, scope, (governance,), (conflict,), (authority,), ("unknown",)),
        _request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied", "declared_scope_prerequisites_satisfied")),
        _request(candidate, scope, (governance,), (conflict,), (deferred_authority,), ("declared_scope_prerequisites_deferred", "authority_evidence_deferred")),
    )
    supplied_reason_tuples = tuple(request.reason_codes for request in mismatched_requests)
    for request in mismatched_requests:
        _rejected(request, "missing_or_mismatched_required_evaluation_reason")
    assert tuple(request.reason_codes for request in mismatched_requests) == supplied_reason_tuples


def test_a28_wrong_types_and_inconsistent_result_invariants_raise_value_error() -> None:
    candidate, peer, governance, scope, conflict, authority = _base()
    request = _request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",))
    with pytest.raises(ValueError):
        evaluate_knowledge_promotion_prerequisites(object())  # type: ignore[arg-type]
    class RequestSubclass(KnowledgePromotionPrerequisiteEvaluationRequest):
        pass
    subclass_request = RequestSubclass(**{field.name: getattr(request, field.name) for field in fields(KnowledgePromotionPrerequisiteEvaluationRequest)})
    with pytest.raises(ValueError):
        evaluate_knowledge_promotion_prerequisites(subclass_request)
    class RequestDuck:
        knowledge_candidate = candidate
    with pytest.raises(ValueError):
        evaluate_knowledge_promotion_prerequisites(RequestDuck())  # type: ignore[arg-type]

    malformed_values = (
        ("knowledge_candidate", replace(candidate), "knowledge_candidate_id", "kc1_bad"),
        ("evaluation_scope", replace(scope), "knowledge_promotion_evaluation_scope_id", "kps1_bad"),
        ("knowledge_governance_decisions", replace(governance), "knowledge_governance_decision_id", "kg1_bad"),
        ("knowledge_conflict_assessment_records", replace(conflict), "knowledge_conflict_assessment_record_id", "kcf1_bad"),
        ("knowledge_authority_decisions", replace(authority), "knowledge_authority_decision_id", "ka1_bad"),
    )
    for request_field, malformed, identity_field, invalid_id in malformed_values:
        object.__setattr__(malformed, identity_field, invalid_id)
        replacement = (malformed,) if request_field.endswith("s") else malformed
        with pytest.raises(ValueError):
            replace(request, **{request_field: replacement})

    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=[governance])  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=(governance, governance))
    second_governance = _governance(candidate, seed="2")
    ordered_governance = _ordered((governance, second_governance), "knowledge_governance_decision_id")
    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=tuple(reversed(ordered_governance)))
    with pytest.raises(ValueError):
        replace(request, knowledge_governance_decisions=())
    with pytest.raises(ValueError):
        replace(request, knowledge_authority_decisions=())
    with pytest.raises(ValueError):
        replace(request, evaluated_by=" ")
    with pytest.raises(ValueError):
        replace(request, evaluated_at=datetime(2026, 7, 13))

    with pytest.raises(ValueError):
        KnowledgePromotionPrerequisiteEvaluationResult(PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED, None, (), ())
    arbitrary = KnowledgePromotionPrerequisiteDiagnostic("arbitrary", KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING, "message", "request", "test")
    with pytest.raises(ValueError):
        KnowledgePromotionPrerequisiteEvaluationResult(PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED, None, ("arbitrary",), (arbitrary,))
    reason = "unsupported_promotion_prerequisite_evaluation_policy"
    non_warning = KnowledgePromotionPrerequisiteDiagnostic(reason, KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO, "message", "request", "test")
    with pytest.raises(ValueError):
        KnowledgePromotionPrerequisiteEvaluationResult(PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED, None, (reason,), (non_warning,))
    different_code = KnowledgePromotionPrerequisiteDiagnostic("unsupported_promotion_evaluation_scope_policy", KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING, "message", "request", "test")
    with pytest.raises(ValueError):
        KnowledgePromotionPrerequisiteEvaluationResult(PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED, None, (reason,), (different_code,))


def test_a29_replay_is_stable_material_changes_change_identity_and_inputs_do_not_mutate() -> None:
    candidate, peer, governance, scope, conflict, authority = _base(); request = _request(candidate, scope, (governance,), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",)); before = replace(request)
    upstream_before = (candidate, peer, governance, scope, conflict, authority)
    first, second = _recorded(request), _recorded(request)
    assert first == second and request == before
    other_peer = _candidate("3")
    other_scope = _scope(candidate, (other_peer,))
    other_conflict = _conflict(candidate, other_peer)
    second_governance = _governance(candidate, seed="2")
    second_authority = _authority(candidate, (governance,), seed="2")
    deferred_conflict = _conflict(candidate, peer, ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED)
    non_authoritative_denied = _authority(candidate, (governance,), intended=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE, outcome=AUTHORITY_DECISION_OUTCOME_DENIED, seed="3")
    changed_requests = (
        _request(candidate, other_scope, (governance,), (other_conflict,), (authority,), ("declared_scope_prerequisites_satisfied",)),
        _request(candidate, scope, (governance, second_governance), (conflict,), (authority,), ("declared_scope_prerequisites_satisfied",)),
        _request(candidate, scope, (governance,), (deferred_conflict,), (authority,), ("declared_scope_conflict_evidence_deferred", "declared_scope_prerequisites_deferred")),
        _request(candidate, scope, (governance,), (conflict,), (authority, second_authority), ("declared_scope_prerequisites_satisfied",)),
        replace(request, evaluated_by="other-evaluation-actor"),
        _request(candidate, scope, (governance,), (conflict,), (non_authoritative_denied,), ("authority_evidence_not_affirmative", "declared_scope_prerequisites_deferred")),
        replace(request, evaluated_at=request.evaluated_at + timedelta(seconds=1)),
    )
    changed_evaluations = tuple(_recorded(changed) for changed in changed_requests)
    assert all(evaluation.knowledge_promotion_prerequisite_evaluation_id != first.knowledge_promotion_prerequisite_evaluation_id for evaluation in changed_evaluations)
    assert changed_evaluations[5].evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE
    rejected = _rejected(replace(request, evaluation_policy_id="unsupported"), "unsupported_promotion_prerequisite_evaluation_policy")
    assert rejected.evaluation is None
    assert request == before
    assert (candidate, peer, governance, scope, conflict, authority) == upstream_before


def test_a30_imports_and_runtime_preserve_the_forbidden_boundary() -> None:
    path = Path("src/rie/application/knowledge_promotion_prerequisite_evaluator.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names} | {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    forbidden_top_level_modules = {
        "sqlite3", "requests", "urllib", "http", "socket", "subprocess", "pathlib", "random", "uuid",
    }
    forbidden_import_tokens = {
        "repository", "persistence", "serialization", "database", "network", "retry", "prompt", "ai", "cli", "api", "ui", "dashboard", "interface", "interfaces", "infrastructure", "legacy",
    }

    def is_forbidden_import(module_name: str) -> bool:
        if not isinstance(module_name, str):
            raise TypeError("module_name must be a string")
        components = module_name.lower().split(".")
        tokens = {token for component in components for token in component.split("_")}
        return components[0] in forbidden_top_level_modules or not forbidden_import_tokens.isdisjoint(tokens)

    legitimate_import_examples = (
        "rie.domain.knowledge_candidate",
        "rie.domain.knowledge_promotion_prerequisite_evaluation",
        "rie.application.knowledge_promotion_prerequisite_evaluator",
        "rie.application.knowledge_authority_decider",
        "rie.application.knowledge_conflict_assessor",
        "rie.application.knowledge_governor",
        "rie.domain.knowledge_authority_decision",
        "rie.domain.knowledge_conflict_assessment_record",
        "rie.domain.knowledge_governance_decision",
        "rie.domain.knowledge_review_record",
    )
    forbidden_import_examples = (
        "sqlite3",
        "requests.sessions",
        "urllib.request",
        "http.client",
        "socket",
        "subprocess",
        "pathlib",
        "random",
        "uuid",
        "rie.repository.knowledge_repository",
        "rie.domain.prompt_candidate",
        "rie.application.ai_service",
        "rie.application.retry_policy",
        "rie.interfaces.api",
        "rie.interface.cli",
        "rie.infrastructure.persistence_adapter",
        "rie.domain.database_record",
        "rie.application.network_client",
        "rie.legacy.dashboard_ui",
        "rie.serialization.knowledge_serializer",
    )
    assert "ai" not in "domain".split("_")
    assert "ui" not in "prerequisite".split("_")
    assert "api" not in "application".split("_")
    assert "ui" not in "evaluation".split("_")
    assert "ui" not in "authority".split("_")
    assert "ai" not in "candidate".split("_")
    assert all(not is_forbidden_import(name) for name in legitimate_import_examples)
    assert all(is_forbidden_import(name) for name in forbidden_import_examples)
    assert not any(is_forbidden_import(name) for name in imports)
    calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert calls.isdisjoint({"open", "print", "input", "read_text", "read_bytes", "write_text", "write_bytes", "unlink", "remove", "rename", "replace", "system", "run", "Popen", "urlopen", "request", "socket"})
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"now", "utcnow"} for node in ast.walk(tree))
    assert not any("retry" in name.lower() or name.lower() in {"random", "randint", "randrange", "uuid1", "uuid4"} for name in calls)
    assert not any(isinstance(node, ast.While) for node in ast.walk(tree))

    def root_name(target: ast.expr) -> str | None:
        while isinstance(target, (ast.Attribute, ast.Subscript)):
            target = target.value
        return target.id if isinstance(target, ast.Name) else None

    assignment_targets = [target for node in ast.walk(tree) if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)) for target in ((node.targets if isinstance(node, ast.Assign) else [node.target]))]
    protected_inputs = {"candidate", "scope", "governance", "conflicts", "authorities", "record"}
    assert not any(isinstance(target, (ast.Attribute, ast.Subscript)) and root_name(target) in protected_inputs for target in assignment_targets)
    lowered = source.lower()
    forbidden_runtime_terms = ("repository_global", "repository-global", "global_completeness", "global completeness", "promotion_decision", "execute_promotion", "promote_candidate", "create_governed", "lifecycle_transition", "acceptance", "prompt", "dashboard")
    assert not any(term in lowered for term in forbidden_runtime_terms)
