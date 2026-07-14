import ast
from dataclasses import FrozenInstanceError, asdict, fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from rie.application.governed_knowledge_constructor import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_CONSTRUCTION_REASON,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_EXECUTION_REASON,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EXECUTION_MISMATCH,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_NOT_SATISFIED,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_NOT_AUTHORIZED,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_DECISION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EVALUATION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_REJECTED,
    GovernedKnowledgeConstructionRequest,
    GovernedKnowledgeConstructionResult,
    construct_governed_knowledge,
)
from rie.application.knowledge_promotion_executor import (
    KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID,
    KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION,
)
from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeDiagnostic,
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
    KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    PROMOTION_DECISION_OUTCOME_DENIED,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    KnowledgePromotionDecision,
    KnowledgePromotionDecisionIdentityInput,
    compute_knowledge_promotion_decision_id,
)
from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
    KnowledgePromotionExecutionIdentityInput,
    KnowledgePromotionExecutionRecord,
    compute_knowledge_promotion_execution_id,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    compute_knowledge_promotion_prerequisite_evaluation_id,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


FIXED_TIME = datetime(2026, 7, 15, 12, 30, 15, 654321, tzinfo=timezone.utc)
DECISION_POLICY_ID = "rcis-knowledge-promotion-decision"
DECISION_POLICY_VERSION = "1.0.0"


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
        statement=f"Governed construction candidate {seed}.",
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


def _evaluation(
    candidate: KnowledgeCandidate,
    *,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
    outcome: str = PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    policy_id: str = KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    policy_version: str = KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
) -> KnowledgePromotionPrerequisiteEvaluation:
    reason = (
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED
        if outcome
        == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
        else PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED
    )
    identity = KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate_contract or candidate.contract_version,
        knowledge_candidate_snapshot_digest=snapshot or compute_knowledge_candidate_review_snapshot_digest(candidate),
        knowledge_promotion_evaluation_scope_id="kps1_" + "2" * 64,
        knowledge_governance_decision_ids=("kg1_" + "3" * 64,),
        knowledge_conflict_assessment_record_ids=("kcf1_" + "4" * 64,),
        knowledge_authority_decision_ids=("ka1_" + "5" * 64,),
        evaluation_scope=PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
        completeness_basis=PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
        evaluation_outcome=outcome,
        reason_codes=(reason,),
        evaluated_by="evaluation-actor",
        evaluated_at=FIXED_TIME - timedelta(hours=3),
        evaluation_policy_id=policy_id,
        evaluation_policy_version=policy_version,
    )
    return KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=compute_knowledge_promotion_prerequisite_evaluation_id(identity),
        contract_version=identity.evaluation_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        knowledge_promotion_evaluation_scope_id=identity.knowledge_promotion_evaluation_scope_id,
        knowledge_governance_decision_ids=identity.knowledge_governance_decision_ids,
        knowledge_conflict_assessment_record_ids=identity.knowledge_conflict_assessment_record_ids,
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


def _decision(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    *,
    outcome: str = PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
    evaluation_id: str | None = None,
    evaluation_contract: str | None = None,
    evaluation_outcome: str | None = None,
    authorization_scope: str = PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    policy_id: str = DECISION_POLICY_ID,
    policy_version: str = DECISION_POLICY_VERSION,
) -> KnowledgePromotionDecision:
    reason = (
        PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION
        if outcome == PROMOTION_DECISION_OUTCOME_AUTHORIZED
        else PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION
    )
    identity = KnowledgePromotionDecisionIdentityInput(
        decision_record_contract_version=KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate_contract or candidate.contract_version,
        knowledge_candidate_snapshot_digest=snapshot or compute_knowledge_candidate_review_snapshot_digest(candidate),
        knowledge_promotion_prerequisite_evaluation_id=evaluation_id or evaluation.knowledge_promotion_prerequisite_evaluation_id,
        knowledge_promotion_prerequisite_evaluation_contract_version=evaluation_contract or evaluation.contract_version,
        promotion_prerequisite_evaluation_outcome=evaluation_outcome or evaluation.evaluation_outcome,
        authorization_scope=authorization_scope,
        promotion_decision=outcome,
        reason_codes=(reason,),
        decided_by="decision-actor",
        decided_at=FIXED_TIME - timedelta(hours=2),
        decision_policy_id=policy_id,
        decision_policy_version=policy_version,
    )
    return KnowledgePromotionDecision(
        knowledge_promotion_decision_id=compute_knowledge_promotion_decision_id(identity),
        contract_version=identity.decision_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        knowledge_promotion_prerequisite_evaluation_id=identity.knowledge_promotion_prerequisite_evaluation_id,
        knowledge_promotion_prerequisite_evaluation_contract_version=identity.knowledge_promotion_prerequisite_evaluation_contract_version,
        promotion_prerequisite_evaluation_outcome=identity.promotion_prerequisite_evaluation_outcome,
        authorization_scope=identity.authorization_scope,
        promotion_decision=identity.promotion_decision,
        reason_codes=identity.reason_codes,
        decided_by=identity.decided_by,
        decided_at=identity.decided_at,
        decision_policy_id=identity.decision_policy_id,
        decision_policy_version=identity.decision_policy_version,
        diagnostics=(),
    )


def _execution(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    decision: KnowledgePromotionDecision,
    *,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
    evaluation_id: str | None = None,
    evaluation_contract: str | None = None,
    decision_id: str | None = None,
    decision_contract: str | None = None,
    decision_outcome: str | None = None,
    authorization_scope: str | None = None,
    reasons: tuple[str, ...] | None = None,
    policy_id: str = KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID,
    policy_version: str = KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION,
) -> KnowledgePromotionExecutionRecord:
    identity = KnowledgePromotionExecutionIdentityInput(
        execution_record_contract_version=KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate_contract or candidate.contract_version,
        knowledge_candidate_snapshot_digest=snapshot or compute_knowledge_candidate_review_snapshot_digest(candidate),
        knowledge_promotion_prerequisite_evaluation_id=evaluation_id or evaluation.knowledge_promotion_prerequisite_evaluation_id,
        knowledge_promotion_prerequisite_evaluation_contract_version=evaluation_contract or evaluation.contract_version,
        knowledge_promotion_decision_id=decision_id or decision.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=decision_contract or decision.contract_version,
        promotion_decision_outcome=decision_outcome or decision.promotion_decision,
        authorization_scope=authorization_scope or decision.authorization_scope,
        execution_scope=PROMOTION_EXECUTION_SCOPE_DECLARED,
        execution_outcome=PROMOTION_EXECUTION_OUTCOME_COMPLETED,
        execution_reference="execution-reference-1",
        reason_codes=reasons if reasons is not None else (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,),
        executed_by="execution-actor",
        executed_at=FIXED_TIME - timedelta(hours=1),
        execution_policy_id=policy_id,
        execution_policy_version=policy_version,
    )
    return KnowledgePromotionExecutionRecord(
        knowledge_promotion_execution_id=compute_knowledge_promotion_execution_id(identity),
        contract_version=identity.execution_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        knowledge_promotion_prerequisite_evaluation_id=identity.knowledge_promotion_prerequisite_evaluation_id,
        knowledge_promotion_prerequisite_evaluation_contract_version=identity.knowledge_promotion_prerequisite_evaluation_contract_version,
        knowledge_promotion_decision_id=identity.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=identity.knowledge_promotion_decision_contract_version,
        promotion_decision_outcome=identity.promotion_decision_outcome,
        authorization_scope=identity.authorization_scope,
        execution_scope=identity.execution_scope,
        execution_outcome=identity.execution_outcome,
        execution_reference=identity.execution_reference,
        reason_codes=identity.reason_codes,
        executed_by=identity.executed_by,
        executed_at=identity.executed_at,
        execution_policy_id=identity.execution_policy_id,
        execution_policy_version=identity.execution_policy_version,
        diagnostics=(),
    )


def _bundle() -> tuple[KnowledgeCandidate, KnowledgePromotionPrerequisiteEvaluation, KnowledgePromotionDecision, KnowledgePromotionExecutionRecord]:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation)
    return candidate, evaluation, decision, _execution(candidate, evaluation, decision)


def _request(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    decision: KnowledgePromotionDecision,
    execution: KnowledgePromotionExecutionRecord,
    *,
    scope: str = GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    reference: str = "construction-reference-1",
    reasons: tuple[str, ...] | None = None,
    actor: str = "construction-actor",
    constructed_at: datetime = FIXED_TIME,
    policy_id: str = GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID,
    policy_version: str = GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION,
) -> GovernedKnowledgeConstructionRequest:
    return GovernedKnowledgeConstructionRequest(
        knowledge_candidate=candidate,
        knowledge_promotion_prerequisite_evaluation=evaluation,
        knowledge_promotion_decision=decision,
        knowledge_promotion_execution=execution,
        construction_scope=scope,
        construction_reference=reference,
        reason_codes=reasons if reasons is not None else (REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,),
        constructed_by=actor,
        constructed_at=constructed_at,
        construction_policy_id=policy_id,
        construction_policy_version=policy_version,
    )


def _constructed(request: GovernedKnowledgeConstructionRequest) -> GovernedKnowledge:
    result = construct_governed_knowledge(request)
    assert result.result_status == GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED
    assert type(result.governed_knowledge) is GovernedKnowledge
    assert result.reason_codes == () and result.diagnostics == ()
    return result.governed_knowledge


def _rejected(request: GovernedKnowledgeConstructionRequest, reason: str) -> GovernedKnowledgeConstructionResult:
    result = construct_governed_knowledge(request)
    assert result.result_status == GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_REJECTED
    assert result.governed_knowledge is None
    assert result.reason_codes == (reason,)
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].code == reason
    return result


def test_a01_compatible_lineage_constructs_exact_governed_object() -> None:
    candidate, evaluation, decision, execution = _bundle()
    record = _constructed(_request(candidate, evaluation, decision, execution))
    assert record.knowledge_candidate_id == candidate.knowledge_candidate_id
    assert record.knowledge_promotion_execution_id == execution.knowledge_promotion_execution_id
    assert record.governed_knowledge_id.startswith("gk1_")


def test_a02_phase32_never_automatically_invokes_construction() -> None:
    candidate, evaluation, decision, execution = _bundle()
    assert type(execution) is KnowledgePromotionExecutionRecord
    assert not hasattr(execution, "governed_knowledge_id")
    assert [item.name for item in fields(GovernedKnowledgeConstructionRequest)][:4] == [
        "knowledge_candidate", "knowledge_promotion_prerequisite_evaluation",
        "knowledge_promotion_decision", "knowledge_promotion_execution",
    ]


def test_a03_statement_and_support_are_copied_without_rewrite() -> None:
    candidate, evaluation, decision, execution = _bundle()
    record = _constructed(_request(candidate, evaluation, decision, execution))
    assert record.statement_type == candidate.statement_type
    assert record.statement == candidate.statement
    assert record.support == candidate.support


def test_a04_all_upstream_identities_are_recomputed() -> None:
    candidate, evaluation, decision, execution = _bundle()
    for value in (candidate, evaluation, decision, execution):
        original = next(item for item in fields(value) if item.name.endswith("_id")).name
        before = getattr(value, original)
        object.__setattr__(value, original, before[:-1] + ("0" if before[-1] != "0" else "1"))
        with pytest.raises(ValueError):
            _request(candidate, evaluation, decision, execution)
        object.__setattr__(value, original, before)


def test_a05_unsupported_construction_policy_rejects_first() -> None:
    candidate, evaluation, decision, execution = _bundle()
    request = _request(candidate, evaluation, decision, execution, policy_id="other", scope="other")
    _rejected(request, GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY)


def test_a06_unsupported_construction_scope_rejects_second() -> None:
    candidate, evaluation, decision, execution = _bundle()
    _rejected(_request(candidate, evaluation, decision, execution, scope="other"), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE)


def test_a07_unsupported_evaluation_policy_rejects() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate, policy_id="other")
    decision = _decision(candidate, evaluation); execution = _execution(candidate, evaluation, decision)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EVALUATION_POLICY)


def test_a08_unsupported_decision_policy_rejects() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, policy_id="other"); execution = _execution(candidate, evaluation, decision)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_DECISION_POLICY)


def test_a09_unsupported_execution_policy_rejects() -> None:
    candidate, evaluation, decision, _ = _bundle()
    execution = _execution(candidate, evaluation, decision, policy_id="other")
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY)


def test_a10_non_satisfied_evaluation_cannot_construct() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate, outcome=PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE)
    decision = _decision(candidate, evaluation, outcome=PROMOTION_DECISION_OUTCOME_DENIED)
    execution = _execution(candidate, evaluation, decision)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_NOT_SATISFIED)


def test_a11_non_authorized_decision_cannot_construct() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, outcome=PROMOTION_DECISION_OUTCOME_DENIED)
    execution = _execution(candidate, evaluation, decision)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_NOT_AUTHORIZED)


def test_a12_candidate_id_mismatch_rejects() -> None:
    candidate = _candidate(); other = _candidate("2"); evaluation = _evaluation(other)
    decision = _decision(other, evaluation); execution = _execution(other, evaluation, decision)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_MISMATCH)


def test_a13_candidate_contract_mismatch_follows_id() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate, candidate_contract="other-contract")
    decision = _decision(candidate, evaluation, candidate_contract="other-contract")
    execution = _execution(candidate, evaluation, decision, candidate_contract="other-contract")
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH)


def test_a14_candidate_snapshot_mismatch_follows_contract() -> None:
    candidate = _candidate(); snapshot = "f" * 64; evaluation = _evaluation(candidate, snapshot=snapshot)
    decision = _decision(candidate, evaluation, snapshot=snapshot); execution = _execution(candidate, evaluation, decision, snapshot=snapshot)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH)


def test_a15_evaluation_mismatch_uses_exact_internal_precedence() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, evaluation_id="kpe1_" + "f" * 64)
    execution = _execution(candidate, evaluation, decision, evaluation_id=decision.knowledge_promotion_prerequisite_evaluation_id)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EVALUATION_MISMATCH)


def test_a16_decision_mismatch_uses_exact_internal_precedence() -> None:
    candidate, evaluation, decision, _ = _bundle()
    execution = _execution(candidate, evaluation, decision, decision_id="kpd1_" + "f" * 64)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_DECISION_MISMATCH)


def test_a17_execution_mismatch_follows_decision_compatibility() -> None:
    candidate, evaluation, decision, _ = _bundle()
    execution = _execution(candidate, evaluation, decision, evaluation_id="kpe1_" + "f" * 64)
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_EXECUTION_MISMATCH)


def test_a18_missing_phase32_completion_reason_rejects() -> None:
    candidate, evaluation, decision, _ = _bundle()
    execution = _execution(candidate, evaluation, decision, reasons=("other",))
    _rejected(_request(candidate, evaluation, decision, execution), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_EXECUTION_REASON)


def test_a19_missing_phase33_construction_reason_rejects() -> None:
    candidate, evaluation, decision, execution = _bundle()
    _rejected(_request(candidate, evaluation, decision, execution, reasons=("other",)), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_MISSING_CONSTRUCTION_REASON)


def test_a20_combined_failures_return_only_first_rejection() -> None:
    candidate, evaluation, decision, execution = _bundle()
    result = _rejected(
        _request(candidate, evaluation, decision, execution, policy_id="other", scope="other", reasons=("other",)),
        GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_POLICY,
    )
    assert len(result.reason_codes) == 1


def test_a21_broken_identities_and_wrong_exact_objects_raise_value_error_first() -> None:
    candidate, evaluation, decision, execution = _bundle()
    original = candidate.knowledge_candidate_id
    object.__setattr__(candidate, "knowledge_candidate_id", "kc1_" + "0" * 64)
    with pytest.raises(ValueError):
        _request(candidate, evaluation, decision, execution)
    object.__setattr__(candidate, "knowledge_candidate_id", original)
    class Duck:
        pass
    with pytest.raises(ValueError):
        construct_governed_knowledge(Duck())  # type: ignore[arg-type]


def test_a22_constructed_result_invariants_are_exact() -> None:
    candidate, evaluation, decision, execution = _bundle()
    record = _constructed(_request(candidate, evaluation, decision, execution))
    result = GovernedKnowledgeConstructionResult("constructed", record, (), ())
    assert result.governed_knowledge is record
    with pytest.raises(ValueError):
        GovernedKnowledgeConstructionResult("constructed", None, (), ())


def test_a23_rejected_result_and_diagnostic_invariants_are_exact() -> None:
    candidate, evaluation, decision, execution = _bundle()
    result = _rejected(_request(candidate, evaluation, decision, execution, scope="other"), GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_UNSUPPORTED_CONSTRUCTION_SCOPE)
    diagnostic = result.diagnostics[0]
    assert type(diagnostic) is GovernedKnowledgeDiagnostic
    assert diagnostic.severity == "warning" and diagnostic.field == "request"
    assert diagnostic.source == "governed_knowledge_constructor"
    with pytest.raises(ValueError):
        GovernedKnowledgeConstructionResult("rejected", None, ("other",), ())


def test_a24_exact_replay_reconstructs_same_object_and_gk1() -> None:
    bundle = _bundle()
    first = _constructed(_request(*bundle))
    second = _constructed(_request(*bundle))
    assert first == second and first.governed_knowledge_id == second.governed_knowledge_id


def test_a25_materially_distinct_constructions_coexist_without_selection() -> None:
    bundle = _bundle()
    first = _constructed(_request(*bundle))
    second = _constructed(_request(*bundle, reference="construction-reference-2"))
    assert first != second
    assert not hasattr(first, "winner") and not hasattr(second, "supersedes")


def test_a26_inputs_request_result_and_object_are_immutable() -> None:
    bundle = _bundle(); request = _request(*bundle); before = tuple(asdict(item) for item in bundle)
    record = _constructed(request)
    assert before == tuple(asdict(item) for item in bundle)
    with pytest.raises(FrozenInstanceError):
        request.construction_reference = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        record.statement = "changed"  # type: ignore[misc]


def test_a27_no_acceptance_lifecycle_prompt_ai_business_or_creative_result() -> None:
    record = _constructed(_request(*_bundle()))
    forbidden = {"acceptance", "lifecycle", "prompt", "ai", "business_approval", "creative_approval"}
    assert forbidden.isdisjoint({item.name for item in fields(record)})


def test_a28_no_repository_persistence_serialization_transaction_or_layers() -> None:
    paths = (
        Path("src/rie/domain/governed_knowledge.py"),
        Path("src/rie/application/governed_knowledge_constructor.py"),
    )
    forbidden = {"repository", "infrastructure", "interfaces", "sqlite3", "pickle", "requests", "openai"}
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert roots.isdisjoint(forbidden)


def test_a29_no_clock_retry_random_uuid_filesystem_network_process_or_logging() -> None:
    paths = (
        Path("src/rie/domain/governed_knowledge.py"),
        Path("src/rie/application/governed_knowledge_constructor.py"),
    )
    forbidden = {"logging", "random", "uuid", "subprocess", "pathlib", "os", "socket", "time"}
    for path in paths:
        source = path.read_text(encoding="utf-8"); tree = ast.parse(source)
        roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert roots.isdisjoint(forbidden)
        calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        assert calls.isdisjoint({"now", "utcnow", "open", "write_text", "write_bytes", "run", "Popen"})


def test_a30_exact_import_direction_predecessor_non_import_and_package_boundary() -> None:
    predecessor_paths = (
        Path("src/rie/domain/knowledge_candidate.py"),
        Path("src/rie/domain/knowledge_review_record.py"),
        Path("src/rie/domain/knowledge_governance_decision.py"),
        Path("src/rie/domain/knowledge_conflict_assessment_record.py"),
        Path("src/rie/domain/knowledge_authority_decision.py"),
        Path("src/rie/domain/knowledge_promotion_prerequisite_evaluation.py"),
        Path("src/rie/domain/knowledge_promotion_decision.py"),
        Path("src/rie/domain/knowledge_promotion_execution.py"),
        Path("src/rie/application/knowledge_constructor.py"),
        Path("src/rie/application/knowledge_reviewer.py"),
        Path("src/rie/application/knowledge_governor.py"),
        Path("src/rie/application/knowledge_conflict_assessor.py"),
        Path("src/rie/application/knowledge_authority_decider.py"),
        Path("src/rie/application/knowledge_promotion_prerequisite_evaluator.py"),
        Path("src/rie/application/knowledge_promotion_decider.py"),
        Path("src/rie/application/knowledge_promotion_executor.py"),
    )
    forbidden = {
        "rie.domain.governed_knowledge",
        "rie.application.governed_knowledge_constructor",
    }
    def imported_modules(path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        modules = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        modules.update(node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        return modules
    for path in predecessor_paths:
        assert imported_modules(path).isdisjoint(forbidden)
    application_imports = imported_modules(Path("src/rie/application/governed_knowledge_constructor.py"))
    assert "rie.domain.governed_knowledge" in application_imports
    assert not any(name.startswith("rie.application.") for name in application_imports)
    for init in (Path("src/rie/domain/__init__.py"), Path("src/rie/application/__init__.py")):
        assert imported_modules(init).isdisjoint(forbidden)
    assert tuple(GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS) == GOVERNED_KNOWLEDGE_CONSTRUCTION_REJECTION_REASONS
