import ast
from dataclasses import FrozenInstanceError, asdict, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from knowledge.text_knowledge import TextKnowledge
from prompting.text_prompt_candidate import TextPromptCandidate
from rie.application.knowledge_promotion_decider import (
    KNOWLEDGE_PROMOTION_DECISION_POLICY_ID,
    KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH,
    PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH,
    PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION,
    PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION,
    PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON,
    PROMOTION_DECISION_REJECTION_REASONS,
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY,
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION,
    PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY,
    PROMOTION_DECISION_RESULT_STATUS_RECORDED,
    PROMOTION_DECISION_RESULT_STATUS_REJECTED,
    KnowledgePromotionDecisionRequest,
    KnowledgePromotionDecisionResult,
    decide_knowledge_promotion,
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
from rie.domain.knowledge_promotion_decision import (
    KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    PROMOTION_DECISION_OUTCOME_DEFERRED,
    PROMOTION_DECISION_OUTCOME_DENIED,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    KnowledgePromotionDecision,
    KnowledgePromotionDecisionDiagnostic,
    compute_knowledge_promotion_decision_candidate_snapshot_digest,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    compute_knowledge_promotion_prerequisite_evaluation_id,
)


FIXED_TIME = datetime(2026, 7, 14, 9, 45, 15, 654321, tzinfo=timezone.utc)


def _support(seed: str = "1") -> KnowledgeEvidenceSupport:
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


def _candidate(seed: str = "1") -> KnowledgeCandidate:
    identity = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=f"Promotion decision candidate {seed}.",
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=(_support(seed),),
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


def _evaluation_reasons(outcome: str) -> tuple[str, ...]:
    if outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE:
        return (PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,)
    if outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE:
        return (
            PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
            PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
        )
    return (
        PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED,
    )


def _evaluation(
    candidate: KnowledgeCandidate,
    outcome: str = PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    *,
    policy_id: str = KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    policy_version: str = KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
) -> KnowledgePromotionPrerequisiteEvaluation:
    identity = KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            candidate_contract or candidate.contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            snapshot
            or compute_knowledge_promotion_decision_candidate_snapshot_digest(candidate)
        ),
        knowledge_promotion_evaluation_scope_id="kps1_" + "2" * 64,
        knowledge_governance_decision_ids=("kg1_" + "3" * 64,),
        knowledge_conflict_assessment_record_ids=("kcf1_" + "4" * 64,),
        knowledge_authority_decision_ids=("ka1_" + "5" * 64,),
        evaluation_scope=(
            PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE
        ),
        completeness_basis=(
            PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY
        ),
        evaluation_outcome=outcome,
        reason_codes=_evaluation_reasons(outcome),
        evaluated_by="evaluation-actor",
        evaluated_at=FIXED_TIME - timedelta(hours=1),
        evaluation_policy_id=policy_id,
        evaluation_policy_version=policy_version,
    )
    return KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=(
            compute_knowledge_promotion_prerequisite_evaluation_id(identity)
        ),
        contract_version=identity.evaluation_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity.knowledge_candidate_snapshot_digest
        ),
        knowledge_promotion_evaluation_scope_id=(
            identity.knowledge_promotion_evaluation_scope_id
        ),
        knowledge_governance_decision_ids=(
            identity.knowledge_governance_decision_ids
        ),
        knowledge_conflict_assessment_record_ids=(
            identity.knowledge_conflict_assessment_record_ids
        ),
        knowledge_authority_decision_ids=identity.knowledge_authority_decision_ids,
        evaluation_scope=identity.evaluation_scope,
        completeness_basis=identity.completeness_basis,
        evaluation_outcome=identity.evaluation_outcome,
        reason_codes=identity.reason_codes,
        evaluated_by=identity.evaluated_by,
        evaluated_at=identity.evaluated_at,
        evaluation_policy_id=identity.evaluation_policy_id,
        evaluation_policy_version=identity.evaluation_policy_version,
        diagnostics=(),
    )


def _matrix_reason(outcome: str, decision: str) -> str:
    return {
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_AUTHORIZED): PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DENIED): PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DENIED): PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED): PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
    }.get((outcome, decision), "caller_reason")


def _request(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    decision: str = PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    *,
    reasons: tuple[str, ...] | None = None,
    actor: str = "decision-actor",
    decided_at: datetime = FIXED_TIME,
    policy_id: str = KNOWLEDGE_PROMOTION_DECISION_POLICY_ID,
    policy_version: str = KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION,
) -> KnowledgePromotionDecisionRequest:
    return KnowledgePromotionDecisionRequest(
        knowledge_candidate=candidate,
        promotion_prerequisite_evaluation=evaluation,
        promotion_decision=decision,
        reason_codes=reasons or (_matrix_reason(evaluation.evaluation_outcome, decision),),
        decided_by=actor,
        decided_at=decided_at,
        decision_policy_id=policy_id,
        decision_policy_version=policy_version,
    )


def _recorded(request: KnowledgePromotionDecisionRequest) -> KnowledgePromotionDecision:
    result = decide_knowledge_promotion(request)
    assert result.result_status == PROMOTION_DECISION_RESULT_STATUS_RECORDED
    assert type(result.promotion_decision_record) is KnowledgePromotionDecision
    assert result.reason_codes == () and result.diagnostics == ()
    return result.promotion_decision_record


def _rejected(request: KnowledgePromotionDecisionRequest, reason: str) -> KnowledgePromotionDecisionResult:
    result = decide_knowledge_promotion(request)
    assert result.result_status == PROMOTION_DECISION_RESULT_STATUS_REJECTED
    assert result.promotion_decision_record is None
    assert result.reason_codes == (reason,)
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == reason
    return result


def test_a01_satisfied_explicit_authorization_records_future_execution_only() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    record = _recorded(_request(candidate, evaluation))
    assert record.promotion_decision == PROMOTION_DECISION_OUTCOME_AUTHORIZED
    assert record.authorization_scope == PROMOTION_DECISION_AUTHORIZATION_SCOPE
    assert record.reason_codes == (PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,)


def test_a02_satisfied_evaluation_never_auto_authorizes() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    request = _request(candidate, evaluation, reasons=("caller_reason",))
    _rejected(request, PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON)
    assert evaluation.evaluation_outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE


def test_a03_satisfied_evaluation_may_record_explicit_denial() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    record = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED))
    assert record.reason_codes == (PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,)


def test_a04_satisfied_evaluation_may_record_explicit_deferral() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    record = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED))
    assert record.reason_codes == (PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,)


def test_a05_not_satisfied_evaluation_cannot_authorize() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE)
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_INELIGIBLE_PREREQUISITE_EVALUATION)


def test_a06_not_satisfied_evaluation_may_record_denial() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE)
    record = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED))
    assert record.reason_codes == (PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,)


def test_a07_not_satisfied_evaluation_may_record_deferral() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE)
    record = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED))
    assert record.reason_codes == (PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,)


def test_a08_deferred_evaluation_cannot_authorize() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE)
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION)


def test_a09_deferred_evaluation_cannot_deny() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE)
    _rejected(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED), PROMOTION_DECISION_REJECTION_INCOMPLETE_PREREQUISITE_EVALUATION)


def test_a10_deferred_evaluation_may_record_only_explicit_deferral() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE)
    record = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED))
    assert record.reason_codes == (PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,)


def test_a11_unsupported_decision_policy_id_or_version_rejects_first() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, policy_id="other-evaluation-policy")
    for request in (
        _request(candidate, evaluation, "unsupported", policy_id="other-policy"),
        _request(candidate, evaluation, "unsupported", policy_version="2.0.0"),
    ):
        _rejected(request, PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY)


def test_a12_unsupported_decision_precedes_evaluation_checks() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, policy_id="other-evaluation-policy", candidate_id="kc1_" + "f" * 64)
    _rejected(_request(candidate, evaluation, "unsupported"), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION)


def test_a13_unsupported_evaluation_policy_precedes_candidate_checks() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, policy_id="other-evaluation-policy", candidate_id="kc1_" + "f" * 64)
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY)


def test_a14_evaluation_candidate_id_mismatch_rejects() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, candidate_id="kc1_" + "f" * 64)
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH)


def test_a15_evaluation_candidate_contract_mismatch_rejects() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, candidate_contract="knowledge-candidate-v2")
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH)


def test_a16_evaluation_candidate_snapshot_mismatch_rejects() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate, snapshot="f" * 64)
    _rejected(_request(candidate, evaluation), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH)


def test_a17_every_compatible_combination_requires_its_matrix_reason() -> None:
    candidate = _candidate()
    combinations = (
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_AUTHORIZED),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DENIED),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DENIED),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE, PROMOTION_DECISION_OUTCOME_DEFERRED),
    )
    for outcome, decision in combinations:
        evaluation = _evaluation(candidate, outcome)
        _rejected(_request(candidate, evaluation, decision, reasons=("caller_reason",)), PROMOTION_DECISION_REJECTION_MISSING_REQUIRED_PROMOTION_DECISION_REASON)


def test_a18_rejection_precedence_is_exact_with_multiple_conditions() -> None:
    candidate = _candidate()
    mismatched = _evaluation(candidate, policy_id="other-evaluation-policy", candidate_id="kc1_" + "f" * 64)
    requests = (
        (_request(candidate, mismatched, "unsupported", policy_id="other-policy"), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY),
        (_request(candidate, mismatched, "unsupported"), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION),
        (_request(candidate, mismatched), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY),
        (_request(candidate, _evaluation(candidate, candidate_id="kc1_" + "f" * 64, candidate_contract="v2", snapshot="f" * 64)), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_MISMATCH),
        (_request(candidate, _evaluation(candidate, candidate_contract="v2", snapshot="f" * 64)), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_CONTRACT_MISMATCH),
        (_request(candidate, _evaluation(candidate, snapshot="f" * 64)), PROMOTION_DECISION_REJECTION_DECISION_CANDIDATE_SNAPSHOT_MISMATCH),
    )
    for request, reason in requests:
        _rejected(request, reason)
    assert PROMOTION_DECISION_REJECTION_REASONS == tuple(item for item in PROMOTION_DECISION_REJECTION_REASONS)


def test_a19_recorded_result_invariants_are_exact() -> None:
    candidate = _candidate()
    request = _request(candidate, _evaluation(candidate), reasons=("additional_reason", PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION))
    result = decide_knowledge_promotion(request)
    assert type(result) is KnowledgePromotionDecisionResult
    assert result.result_status == "recorded"
    assert type(result.promotion_decision_record) is KnowledgePromotionDecision
    assert result.reason_codes == () and result.diagnostics == ()
    assert result.promotion_decision_record.reason_codes == request.reason_codes
    assert result.promotion_decision_record.diagnostics == ()


def test_a20_rejected_result_invariants_are_exact() -> None:
    candidate = _candidate()
    result = _rejected(_request(candidate, _evaluation(candidate), policy_id="other"), PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY)
    diagnostic = result.diagnostics[0]
    assert type(diagnostic) is KnowledgePromotionDecisionDiagnostic
    assert diagnostic.severity == KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING
    assert diagnostic.message and diagnostic.field and diagnostic.source
    with pytest.raises(ValueError):
        KnowledgePromotionDecisionResult("rejected", _recorded(_request(candidate, _evaluation(candidate))), (PROMOTION_DECISION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY,), (diagnostic,))
    with pytest.raises(ValueError):
        KnowledgePromotionDecisionResult("rejected", None, ("unknown",), (diagnostic,))


def test_a21_replay_is_stable_and_material_changes_change_kpd1() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    request = _request(candidate, evaluation)
    first = _recorded(request)
    second = _recorded(_request(candidate, evaluation))
    assert first == second
    changed = (
        _recorded(_request(candidate, evaluation, actor="other-actor")),
        _recorded(_request(candidate, evaluation, decided_at=FIXED_TIME + timedelta(seconds=1))),
        _recorded(_request(candidate, evaluation, reasons=("additional_reason", PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION))),
    )
    assert all(item.knowledge_promotion_decision_id != first.knowledge_promotion_decision_id for item in changed)


def test_a22_inputs_requests_and_results_are_frozen_and_unchanged() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    request = _request(candidate, evaluation)
    before = (asdict(candidate), asdict(evaluation), asdict(request))
    result = decide_knowledge_promotion(request)
    assert before == (asdict(candidate), asdict(evaluation), asdict(request))
    for value in (candidate, evaluation, request, result, result.promotion_decision_record):
        with pytest.raises(FrozenInstanceError):
            value.changed = True  # type: ignore[union-attr,misc]


def test_a23_authorized_and_denied_decisions_coexist_without_winner() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    authorized = _recorded(_request(candidate, evaluation))
    denied = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED))
    assert authorized.knowledge_promotion_decision_id != denied.knowledge_promotion_decision_id
    assert {authorized.promotion_decision, denied.promotion_decision} == {PROMOTION_DECISION_OUTCOME_AUTHORIZED, PROMOTION_DECISION_OUTCOME_DENIED}


def test_a24_deferred_decisions_coexist_without_supersession() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    first = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED))
    second = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED, actor="second-actor", decided_at=FIXED_TIME + timedelta(minutes=1)))
    assert first != second
    assert not hasattr(first, "supersedes") and not hasattr(second, "invalidates")


def test_a25_actor_time_id_age_and_position_never_select_a_winner() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    older = _recorded(_request(candidate, evaluation, actor="z-actor", decided_at=FIXED_TIME - timedelta(days=1)))
    newer = _recorded(_request(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED, actor="a-actor", decided_at=FIXED_TIME + timedelta(days=1)))
    assert [older, newer] == [older, newer]
    assert [newer, older] == [newer, older]
    assert [item.name for item in fields(KnowledgePromotionDecisionRequest)] == ["knowledge_candidate", "promotion_prerequisite_evaluation", "promotion_decision", "reason_codes", "decided_by", "decided_at", "decision_policy_id", "decision_policy_version"]


def test_a26_wrong_raw_legacy_prompt_and_duck_inputs_raise_value_error() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    for value in ({}, "kc1_" + "1" * 64, Path("candidate.json"), TextKnowledge("x", "y", 1, 0), TextPromptCandidate("x", "y", 1, 0, 0)):
        with pytest.raises(ValueError):
            _request(value, evaluation)  # type: ignore[arg-type]
    class Duck:
        pass
    with pytest.raises(ValueError):
        _request(
            candidate,
            Duck(),  # type: ignore[arg-type]
            reasons=("caller_reason",),
        )
    with pytest.raises(ValueError):
        decide_knowledge_promotion(Duck())  # type: ignore[arg-type]


def test_a27_no_clock_retry_random_uuid_logging_process_filesystem_or_network() -> None:
    source = Path("src/rie/application/knowledge_promotion_decider.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {"logging", "random", "uuid", "subprocess", "pathlib", "os", "socket", "time"}
    imported = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    imported.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    assert imported.isdisjoint(forbidden_imports)
    assert "datetime.now" not in source and "datetime.utcnow" not in source
    assert "retry" not in source.lower()


def test_a28_no_execution_mutation_or_governed_knowledge_creation() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    before = (asdict(candidate), asdict(evaluation))
    record = _recorded(_request(candidate, evaluation))
    assert before == (asdict(candidate), asdict(evaluation))
    assert not hasattr(record, "execution_result")
    source = Path("src/rie/application/knowledge_promotion_decider.py").read_text(encoding="utf-8")
    assert "class KnowledgePromotionExecution" not in source
    assert "class GovernedKnowledge" not in source


def test_a29_no_repository_persistence_lifecycle_acceptance_prompt_ai_or_layers() -> None:
    paths = (Path("src/rie/domain/knowledge_promotion_decision.py"), Path("src/rie/application/knowledge_promotion_decider.py"))
    forbidden_roots = {"repository", "infrastructure", "interfaces", "prompting", "knowledge", "sqlite3", "pickle", "requests", "openai"}
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
        roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert roots.isdisjoint(forbidden_roots)


def test_a30_import_direction_is_exact_and_earlier_modules_do_not_import_phase31() -> None:
    application = ast.parse(Path("src/rie/application/knowledge_promotion_decider.py").read_text(encoding="utf-8"))
    domain = ast.parse(Path("src/rie/domain/knowledge_promotion_decision.py").read_text(encoding="utf-8"))
    app_modules = {node.module for node in ast.walk(application) if isinstance(node, ast.ImportFrom)}
    domain_modules = {node.module for node in ast.walk(domain) if isinstance(node, ast.ImportFrom)}
    assert "rie.domain.knowledge_promotion_decision" in app_modules
    assert "rie.domain.knowledge_candidate" in domain_modules
    assert "rie.domain.knowledge_promotion_prerequisite_evaluation" in domain_modules
    earlier_paths = (
        Path("src/rie/domain/knowledge_candidate.py"),
        Path("src/rie/domain/knowledge_review_record.py"),
        Path("src/rie/domain/knowledge_governance_decision.py"),
        Path("src/rie/domain/knowledge_conflict_assessment_record.py"),
        Path("src/rie/domain/knowledge_authority_decision.py"),
        Path(
            "src/rie/domain/"
            "knowledge_promotion_prerequisite_evaluation.py"
        ),
        Path("src/rie/application/knowledge_constructor.py"),
        Path("src/rie/application/knowledge_reviewer.py"),
        Path("src/rie/application/knowledge_governor.py"),
        Path("src/rie/application/knowledge_conflict_assessor.py"),
        Path("src/rie/application/knowledge_authority_decider.py"),
        Path(
            "src/rie/application/"
            "knowledge_promotion_prerequisite_evaluator.py"
        ),
    )
    forbidden_reverse_imports = {
        "rie.domain.knowledge_promotion_decision",
        "rie.application.knowledge_promotion_decider",
    }
    for path in earlier_paths:
        earlier_tree = ast.parse(path.read_text(encoding="utf-8"))
        imported_modules = {
            alias.name
            for node in ast.walk(earlier_tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported_modules.update(
            node.module
            for node in ast.walk(earlier_tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        assert imported_modules.isdisjoint(forbidden_reverse_imports)
