import ast
from dataclasses import FrozenInstanceError, asdict, fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from knowledge.text_knowledge import TextKnowledge
from prompting.text_prompt_candidate import TextPromptCandidate
from rie.application.knowledge_promotion_executor import (
    KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID,
    KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON,
    PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH,
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED,
    PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED,
    PROMOTION_EXECUTION_REJECTION_REASONS,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY,
    PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY,
    PROMOTION_EXECUTION_RESULT_STATUS_RECORDED,
    PROMOTION_EXECUTION_RESULT_STATUS_REJECTED,
    KnowledgePromotionExecutionRequest,
    KnowledgePromotionExecutionResult,
    record_knowledge_promotion_execution,
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
    PROMOTION_DECISION_OUTCOME_DEFERRED,
    PROMOTION_DECISION_OUTCOME_DENIED,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    KnowledgePromotionDecision,
    KnowledgePromotionDecisionIdentityInput,
    compute_knowledge_promotion_decision_id,
)
from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
    KnowledgePromotionExecutionDiagnostic,
    KnowledgePromotionExecutionRecord,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    compute_knowledge_promotion_prerequisite_evaluation_id,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


FIXED_TIME = datetime(2026, 7, 14, 11, 45, 15, 654321, tzinfo=timezone.utc)
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
        statement=f"Promotion execution candidate {seed}.",
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
    identity = KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=(candidate_contract or candidate.contract_version),
        knowledge_candidate_snapshot_digest=(
            snapshot or compute_knowledge_candidate_review_snapshot_digest(candidate)
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
        reason_codes=(PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,),
        evaluated_by="evaluation-actor",
        evaluated_at=FIXED_TIME - timedelta(hours=2),
        evaluation_policy_id=policy_id,
        evaluation_policy_version=policy_version,
    )
    return KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=(
            compute_knowledge_promotion_prerequisite_evaluation_id(identity)
        ),
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


def _decision_reason(outcome: str) -> str:
    if outcome == PROMOTION_DECISION_OUTCOME_AUTHORIZED:
        return PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION
    if outcome == PROMOTION_DECISION_OUTCOME_DENIED:
        return PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION
    return PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION


def _decision(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    outcome: str = PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    *,
    candidate_id: str | None = None,
    candidate_contract: str | None = None,
    snapshot: str | None = None,
    evaluation_id: str | None = None,
    evaluation_contract: str | None = None,
    evaluation_outcome: str | None = None,
    policy_id: str = DECISION_POLICY_ID,
    policy_version: str = DECISION_POLICY_VERSION,
) -> KnowledgePromotionDecision:
    identity = KnowledgePromotionDecisionIdentityInput(
        decision_record_contract_version=KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
        knowledge_candidate_id=candidate_id or candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=(candidate_contract or candidate.contract_version),
        knowledge_candidate_snapshot_digest=(
            snapshot or compute_knowledge_candidate_review_snapshot_digest(candidate)
        ),
        knowledge_promotion_prerequisite_evaluation_id=(
            evaluation_id or evaluation.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            evaluation_contract or evaluation.contract_version
        ),
        promotion_prerequisite_evaluation_outcome=(
            evaluation_outcome or evaluation.evaluation_outcome
        ),
        authorization_scope=PROMOTION_DECISION_AUTHORIZATION_SCOPE,
        promotion_decision=outcome,
        reason_codes=(_decision_reason(outcome),),
        decided_by="decision-actor",
        decided_at=FIXED_TIME - timedelta(hours=1),
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


def _request(
    candidate: KnowledgeCandidate,
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
    decision: KnowledgePromotionDecision,
    *,
    scope: str = PROMOTION_EXECUTION_SCOPE_DECLARED,
    outcome: str = PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    reference: str = "execution-reference-1",
    reasons: tuple[str, ...] | None = None,
    actor: str = "execution-actor",
    executed_at: datetime = FIXED_TIME,
    policy_id: str = KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID,
    policy_version: str = KNOWLEDGE_PROMOTION_EXECUTION_POLICY_VERSION,
) -> KnowledgePromotionExecutionRequest:
    return KnowledgePromotionExecutionRequest(
        knowledge_candidate=candidate,
        promotion_prerequisite_evaluation=evaluation,
        promotion_decision=decision,
        execution_scope=scope,
        execution_outcome=outcome,
        execution_reference=reference,
        reason_codes=(reasons if reasons is not None else (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,)),
        executed_by=actor,
        executed_at=executed_at,
        execution_policy_id=policy_id,
        execution_policy_version=policy_version,
    )


def _bundle() -> tuple[KnowledgeCandidate, KnowledgePromotionPrerequisiteEvaluation, KnowledgePromotionDecision]:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    return candidate, evaluation, _decision(candidate, evaluation)


def _recorded(request: KnowledgePromotionExecutionRequest) -> KnowledgePromotionExecutionRecord:
    result = record_knowledge_promotion_execution(request)
    assert result.result_status == PROMOTION_EXECUTION_RESULT_STATUS_RECORDED
    assert type(result.promotion_execution_record) is KnowledgePromotionExecutionRecord
    assert result.reason_codes == () and result.diagnostics == ()
    return result.promotion_execution_record


def _rejected(request: KnowledgePromotionExecutionRequest, reason: str) -> KnowledgePromotionExecutionResult:
    result = record_knowledge_promotion_execution(request)
    assert result.result_status == PROMOTION_EXECUTION_RESULT_STATUS_REJECTED
    assert result.promotion_execution_record is None
    assert result.reason_codes == (reason,)
    assert len(result.diagnostics) == 1 and result.diagnostics[0].code == reason
    return result


def test_a01_authorized_matching_decision_records_exact_completed_lineage() -> None:
    candidate, evaluation, decision = _bundle()
    record = _recorded(_request(candidate, evaluation, decision))
    assert record.knowledge_candidate_id == candidate.knowledge_candidate_id
    assert record.knowledge_promotion_prerequisite_evaluation_id == evaluation.knowledge_promotion_prerequisite_evaluation_id
    assert record.knowledge_promotion_decision_id == decision.knowledge_promotion_decision_id
    assert record.execution_scope == PROMOTION_EXECUTION_SCOPE_DECLARED
    assert record.execution_outcome == PROMOTION_EXECUTION_OUTCOME_COMPLETED
    assert record.reason_codes == (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,)


def test_a02_authorization_never_automatically_invokes_or_records_execution() -> None:
    candidate, evaluation, decision = _bundle()
    assert decision.promotion_decision == PROMOTION_DECISION_OUTCOME_AUTHORIZED
    assert not hasattr(decision, "knowledge_promotion_execution_id")
    assert [item.name for item in fields(KnowledgePromotionExecutionRequest)][0:3] == [
        "knowledge_candidate", "promotion_prerequisite_evaluation", "promotion_decision"
    ]


def test_a03_denied_decision_rejects_without_execution_event() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_NOT_AUTHORIZED)


def test_a04_deferred_decision_rejects_without_attempt_or_completion() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DEFERRED)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_PROMOTION_DECISION_DEFERRED)


def test_a05_unsupported_execution_policy_id_version_or_both_reject_first() -> None:
    candidate, evaluation, decision = _bundle()
    for policy_id, version in (("other", "1.0.0"), (KNOWLEDGE_PROMOTION_EXECUTION_POLICY_ID, "2.0.0"), ("other", "2.0.0")):
        request = _request(candidate, evaluation, decision, policy_id=policy_id, policy_version=version, outcome="other", scope="other")
        _rejected(request, PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY)


def test_a06_unsupported_execution_outcome_rejects_after_policy() -> None:
    candidate, evaluation, decision = _bundle()
    _rejected(_request(candidate, evaluation, decision, outcome="other_outcome", scope="other_scope"), PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME)


def test_a07_unsupported_execution_scope_rejects_after_outcome() -> None:
    candidate, evaluation, decision = _bundle()
    _rejected(_request(candidate, evaluation, decision, scope="other_scope"), PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_SCOPE)


def test_a08_unsupported_decision_policy_rejects_explicitly() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, policy_id="other-policy")
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PROMOTION_DECISION_POLICY)


def test_a09_unsupported_evaluation_policy_rejects_explicitly() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate, policy_version="2.0.0")
    decision = _decision(candidate, evaluation)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_PREREQUISITE_EVALUATION_POLICY)


def test_a10_evaluation_candidate_id_mismatch_rejects() -> None:
    candidate = _candidate(); other = _candidate("2")
    evaluation = _evaluation(candidate, candidate_id=other.knowledge_candidate_id)
    decision = _decision(candidate, evaluation)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH)


def test_a11_decision_candidate_id_mismatch_follows_evaluation_check() -> None:
    candidate = _candidate(); other = _candidate("2"); evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, candidate_id=other.knowledge_candidate_id)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_CANDIDATE_MISMATCH)


def test_a12_candidate_contract_mismatch_uses_exact_internal_order() -> None:
    candidate = _candidate()
    evaluation_first = _evaluation(candidate, candidate_contract="candidate-contract-other")
    decision_first = _decision(candidate, evaluation_first, candidate_contract="decision-contract-other")
    _rejected(_request(candidate, evaluation_first, decision_first), PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH)
    evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, candidate_contract="decision-contract-other")
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_CANDIDATE_CONTRACT_MISMATCH)


def test_a13_candidate_snapshot_mismatch_uses_exact_internal_order() -> None:
    candidate = _candidate()
    evaluation_first = _evaluation(candidate, snapshot="a" * 64)
    decision_first = _decision(candidate, evaluation_first, snapshot="b" * 64)
    _rejected(_request(candidate, evaluation_first, decision_first), PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH)
    evaluation = _evaluation(candidate)
    decision = _decision(candidate, evaluation, snapshot="b" * 64)
    _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_CANDIDATE_SNAPSHOT_MISMATCH)


def test_a14_decision_evaluation_mismatch_uses_id_contract_outcome_order() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate)
    variants = (
        _decision(candidate, evaluation, evaluation_id="kpe1_" + "9" * 64),
        _decision(candidate, evaluation, evaluation_contract="evaluation-contract-other"),
        _decision(candidate, evaluation, evaluation_outcome=PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE),
    )
    for decision in variants:
        _rejected(_request(candidate, evaluation, decision), PROMOTION_EXECUTION_REJECTION_PREREQUISITE_EVALUATION_MISMATCH)


def test_a15_broken_upstream_identities_raise_value_error_before_policy() -> None:
    candidate, evaluation, decision = _bundle()
    for value, field_name in (
        (candidate, "knowledge_candidate_id"),
        (evaluation, "knowledge_promotion_prerequisite_evaluation_id"),
        (decision, "knowledge_promotion_decision_id"),
    ):
        original = getattr(value, field_name)
        object.__setattr__(value, field_name, original[:-1] + ("0" if original[-1] != "0" else "1"))
        with pytest.raises(ValueError):
            _request(candidate, evaluation, decision, policy_id="other-policy")
        object.__setattr__(value, field_name, original)


def test_a16_broken_decision_authorization_scope_or_identity_raises_value_error() -> None:
    candidate, evaluation, decision = _bundle()
    original_scope = decision.authorization_scope
    object.__setattr__(decision, "authorization_scope", "other_scope")
    with pytest.raises(ValueError):
        _request(candidate, evaluation, decision)
    object.__setattr__(decision, "authorization_scope", original_scope)
    object.__setattr__(decision, "knowledge_promotion_decision_id", "kpd1_" + "0" * 64)
    with pytest.raises(ValueError):
        _request(candidate, evaluation, decision)


def test_a17_missing_required_reason_rejects_without_insertion_or_repair() -> None:
    candidate, evaluation, decision = _bundle()
    reasons = ("caller_reason",)
    request = _request(candidate, evaluation, decision, reasons=reasons)
    _rejected(request, PROMOTION_EXECUTION_REJECTION_MISSING_REQUIRED_REASON)
    assert request.reason_codes is reasons and request.reason_codes == ("caller_reason",)


def test_a18_combined_failures_return_only_first_applicable_rejection() -> None:
    candidate = _candidate(); evaluation = _evaluation(candidate, policy_id="other-evaluation-policy")
    decision = _decision(candidate, evaluation, PROMOTION_DECISION_OUTCOME_DENIED, policy_id="other-decision-policy")
    request = _request(candidate, evaluation, decision, policy_id="other-execution-policy", outcome="other-outcome", scope="other-scope", reasons=("caller_reason",))
    result = _rejected(request, PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_POLICY)
    assert len(result.reason_codes) == 1 and len(result.diagnostics) == 1


def test_a19_recorded_result_invariants_are_exact() -> None:
    candidate, evaluation, decision = _bundle()
    record = _recorded(_request(candidate, evaluation, decision))
    result = KnowledgePromotionExecutionResult("recorded", record, (), ())
    assert result.promotion_execution_record is record and record.diagnostics == ()
    diagnostic = KnowledgePromotionExecutionDiagnostic("note", "info", "Note.", "field", "test")
    with pytest.raises(ValueError):
        KnowledgePromotionExecutionResult("recorded", replace(record, diagnostics=(diagnostic,)), (), ())


def test_a20_rejected_result_invariants_are_exact() -> None:
    candidate, evaluation, decision = _bundle()
    result = _rejected(_request(candidate, evaluation, decision, outcome="other"), PROMOTION_EXECUTION_REJECTION_UNSUPPORTED_EXECUTION_OUTCOME)
    diagnostic = result.diagnostics[0]
    assert diagnostic.severity == "warning" and diagnostic.message and diagnostic.field and diagnostic.source
    with pytest.raises(ValueError):
        KnowledgePromotionExecutionResult("rejected", None, ("unknown",), ())
    with pytest.raises(ValueError):
        KnowledgePromotionExecutionResult("rejected", None, result.reason_codes, (replace(diagnostic, severity="info"),))


def test_a21_exact_replay_reconstructs_equal_record_and_same_kpx1() -> None:
    candidate, evaluation, decision = _bundle(); request = _request(candidate, evaluation, decision)
    first = _recorded(request); second = _recorded(request)
    assert first == second and first.knowledge_promotion_execution_id == second.knowledge_promotion_execution_id


def test_a22_distinct_reference_or_timestamp_changes_execution_identity() -> None:
    candidate, evaluation, decision = _bundle()
    baseline = _recorded(_request(candidate, evaluation, decision))
    by_reference = _recorded(_request(candidate, evaluation, decision, reference="execution-reference-2"))
    by_time = _recorded(_request(candidate, evaluation, decision, executed_at=FIXED_TIME + timedelta(seconds=1)))
    assert len({baseline.knowledge_promotion_execution_id, by_reference.knowledge_promotion_execution_id, by_time.knowledge_promotion_execution_id}) == 3


def test_a23_multiple_records_coexist_without_selection_or_invalidation() -> None:
    candidate, evaluation, decision = _bundle()
    first = _recorded(_request(candidate, evaluation, decision, reference="execution-reference-a"))
    second = _recorded(_request(candidate, evaluation, decision, reference="execution-reference-b"))
    assert [first, second] == [first, second] and [second, first] == [second, first]
    for name in ("winner", "latest", "supersedes", "invalidates", "duplicate_prevented"):
        assert not hasattr(first, name) and not hasattr(second, name)


def test_a24_inputs_request_reason_tuple_and_results_are_frozen_unchanged() -> None:
    candidate, evaluation, decision = _bundle(); reasons = (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,)
    request = _request(candidate, evaluation, decision, reasons=reasons)
    before = (asdict(candidate), asdict(evaluation), asdict(decision), asdict(request))
    result = record_knowledge_promotion_execution(request)
    assert before == (asdict(candidate), asdict(evaluation), asdict(decision), asdict(request))
    assert request.reason_codes is reasons
    with pytest.raises(FrozenInstanceError):
        request.executed_by = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.result_status = "changed"  # type: ignore[misc]


def test_a25_raw_paths_ids_legacy_subclasses_and_duck_inputs_raise_value_error() -> None:
    candidate, evaluation, decision = _bundle()
    for value in ({}, "kc1_" + "1" * 64, Path("candidate.json"), TextKnowledge("x", "y", 1, 0), TextPromptCandidate("x", "y", 1, 0, 0)):
        with pytest.raises(ValueError):
            _request(value, evaluation, decision)  # type: ignore[arg-type]

    class CandidateSubclass(KnowledgeCandidate):
        pass

    subclass = object.__new__(CandidateSubclass)
    for item in fields(candidate):
        object.__setattr__(subclass, item.name, getattr(candidate, item.name))
    with pytest.raises(ValueError):
        _request(subclass, evaluation, decision)

    class Duck:
        pass

    with pytest.raises(ValueError):
        _request(candidate, Duck(), decision)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        record_knowledge_promotion_execution(Duck())  # type: ignore[arg-type]


def test_a26_recording_mutates_no_upstream_object_and_triggers_no_downstream_action() -> None:
    candidate, evaluation, decision = _bundle(); before = (asdict(candidate), asdict(evaluation), asdict(decision))
    record = _recorded(_request(candidate, evaluation, decision))
    assert before == (asdict(candidate), asdict(evaluation), asdict(decision))
    assert record.authorization_scope == decision.authorization_scope
    assert not hasattr(record, "authorization_consumed")


def test_a27_no_governed_knowledge_identity_lifecycle_acceptance_prompt_or_ai_result() -> None:
    candidate, evaluation, decision = _bundle(); record = _recorded(_request(candidate, evaluation, decision))
    names = {item.name for item in fields(record)}
    forbidden = {"governed_knowledge", "governed_knowledge_id", "lifecycle_status", "acceptance_status", "prompt_candidate", "ai_output"}
    assert names.isdisjoint(forbidden)
    source = Path("src/rie/application/knowledge_promotion_executor.py").read_text(encoding="utf-8")
    assert "class GovernedKnowledge" not in source and "TextPromptCandidate" not in source


def test_a28_runtime_has_no_repository_persistence_serialization_transaction_or_layers() -> None:
    paths = (Path("src/rie/domain/knowledge_promotion_execution.py"), Path("src/rie/application/knowledge_promotion_executor.py"))
    forbidden_roots = {"repository", "infrastructure", "interfaces", "sqlite3", "pickle", "requests", "openai"}
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
        roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert roots.isdisjoint(forbidden_roots)


def test_a29_runtime_has_no_clock_retry_random_uuid_filesystem_network_process_or_logging() -> None:
    paths = (Path("src/rie/domain/knowledge_promotion_execution.py"), Path("src/rie/application/knowledge_promotion_executor.py"))
    forbidden = {"logging", "random", "uuid", "subprocess", "pathlib", "os", "socket", "time"}
    for path in paths:
        source = path.read_text(encoding="utf-8"); tree = ast.parse(source)
        roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
        roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert roots.isdisjoint(forbidden)
        assert "datetime.now" not in source and "datetime.utcnow" not in source and "retry" not in source.lower()


def test_a30_import_direction_is_exact_and_earlier_modules_do_not_import_phase32() -> None:
    application = ast.parse(Path("src/rie/application/knowledge_promotion_executor.py").read_text(encoding="utf-8"))
    domain = ast.parse(Path("src/rie/domain/knowledge_promotion_execution.py").read_text(encoding="utf-8"))
    app_modules = {node.module for node in ast.walk(application) if isinstance(node, ast.ImportFrom)}
    domain_modules = {node.module for node in ast.walk(domain) if isinstance(node, ast.ImportFrom)}
    assert {"rie.domain.knowledge_promotion_execution", "rie.domain.knowledge_promotion_decision", "rie.domain.knowledge_promotion_prerequisite_evaluation", "rie.domain.knowledge_candidate", "rie.domain.knowledge_review_record"}.issubset(app_modules)
    assert all(not (name or "").startswith("rie") for name in domain_modules)
    earlier = tuple(Path("src/rie/domain").glob("knowledge_*.py")) + tuple(Path("src/rie/application").glob("knowledge_*.py"))
    for path in earlier:
        if path.name in {"knowledge_promotion_execution.py", "knowledge_promotion_executor.py"}:
            continue
        assert "knowledge_promotion_execution" not in path.read_text(encoding="utf-8")
