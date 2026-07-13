import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from rie.application.knowledge_governor import (
    ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_ID,
    ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_VERSION,
    GOVERNANCE_RESULT_STATUS_RECORDED,
    GOVERNANCE_RESULT_STATUS_REJECTED,
    KNOWLEDGE_GOVERNANCE_POLICY_ID,
    KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
    KnowledgeGovernanceRequest,
    KnowledgeGovernanceResult,
    govern_knowledge_candidate,
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
from rie.domain.knowledge_governance_decision import (
    AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION,
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KnowledgeGovernanceDecision,
)
from rie.domain.knowledge_review_record import (
    KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
    REVIEW_DECISION_DEFERRED,
    REVIEW_DECISION_PASSED,
    REVIEW_DECISION_REJECTED,
    KnowledgeReviewIdentityInput,
    KnowledgeReviewRecord,
    compute_knowledge_candidate_review_snapshot_digest,
    compute_knowledge_review_record_id,
)


FIXED_TIME = datetime(2026, 7, 13, 11, 45, 30, 654321, tzinfo=timezone.utc)


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
        locator_value=(1,),
        locator_schema_version="1.0.0",
    )


def _candidate(
    *,
    statement: str = "The governed fact.",
    seed: str = "1",
) -> KnowledgeCandidate:
    support = _support(seed)
    identity_input = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement,
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=(support,),
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
    )
    return KnowledgeCandidate(
        knowledge_candidate_id=compute_knowledge_candidate_id(identity_input),
        contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement,
        support=(support,),
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
        conflict_ids=(),
        diagnostics=(),
    )


def _review(
    candidate: KnowledgeCandidate,
    decision: str = REVIEW_DECISION_PASSED,
    *,
    actor: str = "reviewer-a",
    reviewed_at: datetime = FIXED_TIME,
    review_policy_id: str = ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_ID,
    review_policy_version: str = ELIGIBLE_KNOWLEDGE_REVIEW_POLICY_VERSION,
    candidate_id: str | None = None,
    candidate_contract_version: str | None = None,
    candidate_snapshot_digest: str | None = None,
) -> KnowledgeReviewRecord:
    reason_by_decision = {
        REVIEW_DECISION_PASSED: "candidate_review_passed",
        REVIEW_DECISION_REJECTED: "candidate_review_rejected",
        REVIEW_DECISION_DEFERRED: "candidate_review_deferred",
    }
    identity_input = KnowledgeReviewIdentityInput(
        review_record_contract_version=KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
        knowledge_candidate_id=(
            candidate_id or candidate.knowledge_candidate_id
        ),
        knowledge_candidate_contract_version=(
            candidate_contract_version or candidate.contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            candidate_snapshot_digest
            or compute_knowledge_candidate_review_snapshot_digest(candidate)
        ),
        review_decision=decision,
        reason_codes=(reason_by_decision[decision],),
        reviewed_evidence_ids=tuple(
            support.evidence_id for support in candidate.support
        ),
        reviewed_acceptance_record_ids=tuple(
            acceptance_id
            for support in candidate.support
            for acceptance_id in support.acceptance_record_ids
        ),
        reviewed_acceptance_review_record_ids=tuple(
            review_id
            for support in candidate.support
            for review_id in support.acceptance_review_record_ids
        ),
        reviewed_by=actor,
        reviewed_at=reviewed_at,
        review_policy_id=review_policy_id,
        review_policy_version=review_policy_version,
    )
    return KnowledgeReviewRecord(
        knowledge_review_record_id=compute_knowledge_review_record_id(
            identity_input
        ),
        contract_version=identity_input.review_record_contract_version,
        knowledge_candidate_id=identity_input.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity_input.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity_input.knowledge_candidate_snapshot_digest
        ),
        review_decision=identity_input.review_decision,
        reason_codes=identity_input.reason_codes,
        reviewed_evidence_ids=identity_input.reviewed_evidence_ids,
        reviewed_acceptance_record_ids=(
            identity_input.reviewed_acceptance_record_ids
        ),
        reviewed_acceptance_review_record_ids=(
            identity_input.reviewed_acceptance_review_record_ids
        ),
        reviewed_by=identity_input.reviewed_by,
        reviewed_at=identity_input.reviewed_at,
        review_policy_id=identity_input.review_policy_id,
        review_policy_version=identity_input.review_policy_version,
        diagnostics=(),
    )


def _ordered_reviews(
    *records: KnowledgeReviewRecord,
) -> tuple[KnowledgeReviewRecord, ...]:
    return tuple(sorted(records, key=lambda item: item.knowledge_review_record_id))


def _request(
    *,
    candidate: KnowledgeCandidate | None = None,
    reviews: tuple[KnowledgeReviewRecord, ...] | None = None,
    governance_decision: str = GOVERNANCE_DECISION_AUTHORIZED,
    reason_codes: tuple[str, ...] = ("eligible_review_evidence",),
    decided_by: str = "governance-actor",
    decided_at: datetime = FIXED_TIME + timedelta(hours=1),
    governance_policy_id: str = KNOWLEDGE_GOVERNANCE_POLICY_ID,
    governance_policy_version: str = KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
) -> KnowledgeGovernanceRequest:
    selected_candidate = candidate if candidate is not None else _candidate()
    selected_reviews = (
        reviews if reviews is not None else (_review(selected_candidate),)
    )
    return KnowledgeGovernanceRequest(
        knowledge_candidate=selected_candidate,
        knowledge_review_records=selected_reviews,
        governance_decision=governance_decision,
        reason_codes=reason_codes,
        decided_by=decided_by,
        decided_at=decided_at,
        governance_policy_id=governance_policy_id,
        governance_policy_version=governance_policy_version,
    )


def _recorded(request: KnowledgeGovernanceRequest) -> KnowledgeGovernanceDecision:
    result = govern_knowledge_candidate(request)
    assert result.result_status == GOVERNANCE_RESULT_STATUS_RECORDED
    assert type(result.governance_decision_record) is KnowledgeGovernanceDecision
    assert result.reason_codes == ()
    return result.governance_decision_record


def _rejection(request: KnowledgeGovernanceRequest) -> str:
    result = govern_knowledge_candidate(request)
    assert result.result_status == GOVERNANCE_RESULT_STATUS_REJECTED
    assert result.governance_decision_record is None
    assert len(result.reason_codes) == 1
    return result.reason_codes[0]


def test_a01_passed_review_authorizes_without_mutation() -> None:
    candidate = _candidate()
    review = _review(candidate)
    request = _request(candidate=candidate, reviews=(review,))
    before = (candidate, review, request)

    record = _recorded(request)

    assert record.governance_decision == GOVERNANCE_DECISION_AUTHORIZED
    assert record.reason_codes == ("eligible_review_evidence",)
    assert record.authorization_scope == (
        AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
    )
    assert (candidate, review, request) == before
    assert candidate.authority_status == "unassessed"
    assert candidate.lifecycle_status == "candidate"
    assert candidate.review_status == "pending_review"
    assert candidate.conflict_status == "not_assessed"


def test_a02_multiple_ordered_passed_reviews_are_all_preserved() -> None:
    candidate = _candidate()
    reviews = _ordered_reviews(
        _review(candidate, actor="reviewer-a"),
        _review(candidate, actor="reviewer-b", reviewed_at=FIXED_TIME + timedelta(seconds=1)),
    )
    record = _recorded(_request(candidate=candidate, reviews=reviews))
    assert record.knowledge_review_record_ids == tuple(
        review.knowledge_review_record_id for review in reviews
    )


def test_a03_all_passed_may_defer_with_exact_reason() -> None:
    request = _request(
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("governance_evaluation_deferred",),
    )
    record = _recorded(request)
    assert record.governance_decision == GOVERNANCE_DECISION_DEFERRED


def test_a04_all_passed_cannot_record_denied() -> None:
    request = _request(
        governance_decision=GOVERNANCE_DECISION_DENIED,
        reason_codes=("review_evidence_rejected",),
    )
    assert _rejection(request) == "incompatible_governance_decision"


def test_a05_all_rejected_may_record_denied_with_exact_reason() -> None:
    candidate = _candidate()
    reviews = (_review(candidate, REVIEW_DECISION_REJECTED),)
    request = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DENIED,
        reason_codes=("review_evidence_rejected",),
    )
    assert _recorded(request).governance_decision == GOVERNANCE_DECISION_DENIED


def test_a06_all_rejected_may_record_deferred_with_exact_reason() -> None:
    candidate = _candidate()
    request = _request(
        candidate=candidate,
        reviews=(_review(candidate, REVIEW_DECISION_REJECTED),),
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("governance_evaluation_deferred",),
    )
    assert _recorded(request).governance_decision == GOVERNANCE_DECISION_DEFERRED


def test_a07_all_rejected_cannot_authorize() -> None:
    candidate = _candidate()
    request = _request(
        candidate=candidate,
        reviews=(_review(candidate, REVIEW_DECISION_REJECTED),),
    )
    assert _rejection(request) == "ineligible_review_evidence"


def test_a08_all_deferred_may_only_record_deferred() -> None:
    candidate = _candidate()
    reviews = (_review(candidate, REVIEW_DECISION_DEFERRED),)
    deferred = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("incomplete_review_evidence",),
    )
    assert _recorded(deferred).governance_decision == GOVERNANCE_DECISION_DEFERRED
    for decision in (GOVERNANCE_DECISION_AUTHORIZED, GOVERNANCE_DECISION_DENIED):
        request = _request(
            candidate=candidate,
            reviews=reviews,
            governance_decision=decision,
            reason_codes=("incomplete_review_evidence",),
        )
        assert _rejection(request) == "incomplete_review_evidence"


def test_a09_passed_plus_rejected_may_only_record_contradiction_deferral() -> None:
    candidate = _candidate()
    reviews = _ordered_reviews(
        _review(candidate, REVIEW_DECISION_PASSED),
        _review(candidate, REVIEW_DECISION_REJECTED, actor="reviewer-b"),
    )
    deferred = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("contradictory_review_evidence",),
    )
    assert _recorded(deferred).governance_decision == GOVERNANCE_DECISION_DEFERRED
    for decision in (GOVERNANCE_DECISION_AUTHORIZED, GOVERNANCE_DECISION_DENIED):
        request = _request(
            candidate=candidate,
            reviews=reviews,
            governance_decision=decision,
            reason_codes=("contradictory_review_evidence",),
        )
        assert _rejection(request) == "contradictory_review_evidence"


def test_a10_passed_rejected_deferred_uses_complete_contradiction_matrix() -> None:
    candidate = _candidate()
    reviews = _ordered_reviews(
        _review(candidate, REVIEW_DECISION_PASSED),
        _review(candidate, REVIEW_DECISION_REJECTED, actor="reviewer-b"),
        _review(candidate, REVIEW_DECISION_DEFERRED, actor="reviewer-c"),
    )
    deferred = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("contradictory_review_evidence",),
    )
    assert _recorded(deferred).knowledge_review_record_ids == tuple(
        item.knowledge_review_record_id for item in reviews
    )
    denied = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DENIED,
        reason_codes=("contradictory_review_evidence",),
    )
    assert _rejection(denied) == "contradictory_review_evidence"


def test_a11_passed_plus_deferred_may_only_record_incomplete_deferral() -> None:
    candidate = _candidate()
    reviews = _ordered_reviews(
        _review(candidate, REVIEW_DECISION_PASSED),
        _review(candidate, REVIEW_DECISION_DEFERRED, actor="reviewer-b"),
    )
    deferred = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("incomplete_review_evidence",),
    )
    assert _recorded(deferred).governance_decision == GOVERNANCE_DECISION_DEFERRED
    assert _rejection(_request(candidate=candidate, reviews=reviews)) == (
        "incomplete_review_evidence"
    )


def test_a12_rejected_plus_deferred_cannot_silently_become_denied() -> None:
    candidate = _candidate()
    reviews = _ordered_reviews(
        _review(candidate, REVIEW_DECISION_REJECTED),
        _review(candidate, REVIEW_DECISION_DEFERRED, actor="reviewer-b"),
    )
    deferred = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DEFERRED,
        reason_codes=("incomplete_review_evidence",),
    )
    assert _recorded(deferred).governance_decision == GOVERNANCE_DECISION_DEFERRED
    denied = _request(
        candidate=candidate,
        reviews=reviews,
        governance_decision=GOVERNANCE_DECISION_DENIED,
        reason_codes=("review_evidence_rejected",),
    )
    assert _rejection(denied) == "incomplete_review_evidence"


def test_a13_unsupported_review_policy_rejects_every_complete_tuple() -> None:
    candidate = _candidate()
    unsupported_id = _review(candidate, review_policy_id="other-review-policy")
    unsupported_version = _review(
        candidate,
        actor="reviewer-b",
        review_policy_version="2.0.0",
    )
    eligible = _review(candidate, actor="reviewer-c")
    for reviews in (
        (unsupported_id,),
        (unsupported_version,),
        _ordered_reviews(eligible, unsupported_id),
    ):
        request = _request(candidate=candidate, reviews=reviews)
        assert _rejection(request) == "unsupported_review_evidence_policy"


def test_a14_candidate_snapshot_contract_and_review_identity_must_match() -> None:
    candidate = _candidate()
    cases = (
        (
            _review(candidate, candidate_id="kc1_" + "9" * 64),
            "review_candidate_mismatch",
        ),
        (
            _review(candidate, candidate_contract_version="knowledge-candidate-v2"),
            "review_candidate_contract_mismatch",
        ),
        (
            _review(candidate, candidate_snapshot_digest="9" * 64),
            "review_candidate_snapshot_mismatch",
        ),
    )
    for review, reason in cases:
        assert _rejection(_request(candidate=candidate, reviews=(review,))) == reason

    broken = _review(candidate)
    object.__setattr__(broken, "knowledge_review_record_id", "kr1_" + "0" * 64)
    with pytest.raises(ValueError, match="does not match identity"):
        _request(candidate=candidate, reviews=(broken,))


def test_a15_missing_required_reason_rejects_without_repair() -> None:
    reasons = ("caller_reason",)
    request = _request(reason_codes=reasons)
    assert _rejection(request) == "missing_required_governance_reason"
    assert request.reason_codes is reasons
    assert request.reason_codes == ("caller_reason",)


def test_a16_policy_and_decision_rejections_follow_exact_precedence() -> None:
    candidate = _candidate()
    unsupported_review = _review(candidate, review_policy_id="other-review-policy")
    cases = (
        _request(governance_policy_id="other-governance-policy"),
        _request(governance_policy_version="2.0.0"),
        _request(
            governance_policy_id="other-governance-policy",
            governance_policy_version="2.0.0",
        ),
        _request(governance_decision="accepted"),
    )
    for request in cases[:3]:
        assert _rejection(request) == "unsupported_governance_policy"
    assert _rejection(cases[3]) == "unsupported_governance_decision"

    policy_first = _request(
        candidate=candidate,
        reviews=(unsupported_review,),
        governance_decision="accepted",
        governance_policy_id="other-governance-policy",
    )
    decision_second = _request(
        candidate=candidate,
        reviews=(unsupported_review,),
        governance_decision="accepted",
    )
    assert _rejection(policy_first) == "unsupported_governance_policy"
    assert _rejection(decision_second) == "unsupported_governance_decision"


def test_a17_replay_is_stable_and_material_request_change_changes_identity() -> None:
    request = _request()
    first = _recorded(request)
    second = _recorded(request)
    changed = _recorded(_request(decided_by="other-governance-actor"))
    assert first == second
    assert first.knowledge_governance_decision_id == (
        second.knowledge_governance_decision_id
    )
    assert changed.knowledge_governance_decision_id != (
        first.knowledge_governance_decision_id
    )


def test_a18_raw_paths_ids_wrong_domains_and_duck_types_are_rejected() -> None:
    candidate = _candidate()
    review = _review(candidate)

    for bad_candidate in ({}, Path("candidate"), review, candidate.knowledge_candidate_id):
        with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
            KnowledgeGovernanceRequest(
                knowledge_candidate=bad_candidate,
                knowledge_review_records=(review,),
                governance_decision=GOVERNANCE_DECISION_AUTHORIZED,
                reason_codes=("eligible_review_evidence",),
                decided_by="actor",
                decided_at=FIXED_TIME,
                governance_policy_id=KNOWLEDGE_GOVERNANCE_POLICY_ID,
                governance_policy_version=KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
            )

    for bad_reviews in ([review], (), ({},), (candidate,)):
        with pytest.raises(ValueError):
            _request(candidate=candidate, reviews=bad_reviews)

    class DuckRequest:
        knowledge_candidate = candidate

    for bad_request in ({}, Path("request"), candidate, DuckRequest()):
        with pytest.raises(ValueError, match="exact KnowledgeGovernanceRequest"):
            govern_knowledge_candidate(bad_request)


def test_a19_inputs_requests_results_and_collections_remain_immutable() -> None:
    candidate = _candidate()
    review = _review(candidate)
    reasons = ("eligible_review_evidence",)
    request = _request(candidate=candidate, reviews=(review,), reason_codes=reasons)
    before = (candidate, review, request, reasons)
    recorded = govern_knowledge_candidate(request)
    rejected = govern_knowledge_candidate(
        _request(governance_policy_id="other-policy")
    )
    assert (candidate, review, request, reasons) == before
    with pytest.raises(FrozenInstanceError):
        request.decided_by = "changed"
    with pytest.raises(FrozenInstanceError):
        recorded.result_status = GOVERNANCE_RESULT_STATUS_REJECTED
    with pytest.raises(FrozenInstanceError):
        rejected.reason_codes = ()
    with pytest.raises(ValueError, match="lexicographically ordered"):
        _request(reason_codes=("z_reason", "a_reason"))


def test_a20_records_no_downstream_state_and_never_selects_governance_winner() -> None:
    candidate = _candidate()
    reviews = (_review(candidate),)
    authorized = _recorded(_request(candidate=candidate, reviews=reviews))
    deferred = _recorded(
        _request(
            candidate=candidate,
            reviews=reviews,
            governance_decision=GOVERNANCE_DECISION_DEFERRED,
            reason_codes=("governance_evaluation_deferred",),
        )
    )
    assert authorized.knowledge_governance_decision_id != (
        deferred.knowledge_governance_decision_id
    )
    assert {authorized.governance_decision, deferred.governance_decision} == {
        GOVERNANCE_DECISION_AUTHORIZED,
        GOVERNANCE_DECISION_DEFERRED,
    }
    for record in (authorized, deferred):
        for forbidden in (
            "acceptance",
            "promotion",
            "governed_knowledge",
            "final_knowledge",
            "authority_assignment",
            "lifecycle_transition",
            "conflict_record",
            "repository",
            "persistence",
            "prompt_candidate",
            "ai_result",
        ):
            assert not hasattr(record, forbidden)


def test_a21_production_imports_and_runtime_exclude_forbidden_side_effects() -> None:
    root = Path(__file__).resolve().parents[2]
    production_paths = (
        root / "src/rie/domain/knowledge_governance_decision.py",
        root / "src/rie/application/knowledge_governor.py",
    )
    import_names: set[str] = set()
    combined_source = ""
    for path in production_paths:
        source = path.read_text(encoding="utf-8")
        combined_source += source.lower()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                import_names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                import_names.add(node.module)

    forbidden_import_parts = (
        "interface",
        "infrastructure",
        "repository",
        "database",
        "sqlite",
        "pathlib",
        "os",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "random",
        "uuid",
        "logging",
        "prompt",
        "knowledge_constructor",
        "knowledge_reviewer",
        "rie.knowledge",
        "knowledge.",
    )
    assert not any(
        forbidden in imported
        for imported in import_names
        for forbidden in forbidden_import_parts
    )
    for forbidden_call in (
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "open(",
        ".read_text(",
        ".write_text(",
        "retry",
    ):
        assert forbidden_call not in combined_source

    request = _request(decided_at=FIXED_TIME)
    result = govern_knowledge_candidate(request)
    assert type(result) is KnowledgeGovernanceResult
    assert result.governance_decision_record is not None
    assert result.governance_decision_record.decided_at is FIXED_TIME
