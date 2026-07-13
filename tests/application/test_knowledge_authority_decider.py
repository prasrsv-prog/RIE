import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from rie.application.knowledge_authority_decider import (
    AUTHORITY_DECISION_RESULT_STATUS_RECORDED,
    AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
    KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID,
    KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION,
    KnowledgeAuthorityDecisionRequest,
    KnowledgeAuthorityDecisionResult,
    decide_knowledge_authority,
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
    KnowledgeAuthorityDiagnostic,
    compute_knowledge_authority_candidate_snapshot_digest,
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
    KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
    KnowledgeGovernanceDecision,
    KnowledgeGovernanceIdentityInput,
    compute_knowledge_governance_decision_id,
)


FIXED_TIME = datetime(2026, 7, 13, 15, 45, 30, 654321, tzinfo=timezone.utc)

_APPROVED_REJECTION_REASONS = frozenset(
    {
        "unsupported_authority_policy",
        "unsupported_authority_value",
        "unsupported_authority_decision_outcome",
        "unsupported_governance_evidence_policy",
        "governance_candidate_mismatch",
        "governance_candidate_contract_mismatch",
        "governance_candidate_snapshot_mismatch",
        "contradictory_governance_evidence",
        "ineligible_governance_evidence",
        "incomplete_governance_evidence",
        "missing_required_authority_reason",
    }
)


def _support(
    seed: str = "1",
    *,
    source_authority_status: str = "official",
) -> KnowledgeEvidenceSupport:
    return KnowledgeEvidenceSupport(
        evidence_id="ev1_" + seed * 64,
        acceptance_record_ids=("ar1_" + seed * 64,),
        acceptance_review_record_ids=(f"acceptance-review-{seed}",),
        source_id=f"source-{seed}",
        source_content_digest=seed * 64,
        source_authority_status=source_authority_status,
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
    source_authority_status: str = "official",
) -> KnowledgeCandidate:
    support = _support(
        seed,
        source_authority_status=source_authority_status,
    )
    identity = KnowledgeCandidateIdentityInput(
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
        knowledge_candidate_id=compute_knowledge_candidate_id(identity),
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


def _governance(
    candidate: KnowledgeCandidate,
    decision: str = GOVERNANCE_DECISION_AUTHORIZED,
    *,
    seed: str = "1",
    candidate_id: str | None = None,
    candidate_contract_version: str | None = None,
    candidate_snapshot_digest: str | None = None,
    governance_policy_id: str = KNOWLEDGE_GOVERNANCE_POLICY_ID,
    governance_policy_version: str = KNOWLEDGE_GOVERNANCE_POLICY_VERSION,
) -> KnowledgeGovernanceDecision:
    required_reason = {
        GOVERNANCE_DECISION_AUTHORIZED: "eligible_review_evidence",
        GOVERNANCE_DECISION_DENIED: "review_evidence_rejected",
        GOVERNANCE_DECISION_DEFERRED: "governance_evaluation_deferred",
    }[decision]
    identity = KnowledgeGovernanceIdentityInput(
        governance_decision_contract_version=(
            KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=(
            candidate.knowledge_candidate_id
            if candidate_id is None
            else candidate_id
        ),
        knowledge_candidate_contract_version=(
            candidate.contract_version
            if candidate_contract_version is None
            else candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            compute_knowledge_authority_candidate_snapshot_digest(candidate)
            if candidate_snapshot_digest is None
            else candidate_snapshot_digest
        ),
        knowledge_review_record_ids=("kr1_" + seed * 64,),
        authorization_scope=(
            AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        ),
        governance_decision=decision,
        reason_codes=(required_reason,),
        decided_by=f"governance-actor-{seed}",
        decided_at=FIXED_TIME + timedelta(minutes=int(seed, 16)),
        governance_policy_id=governance_policy_id,
        governance_policy_version=governance_policy_version,
    )
    return KnowledgeGovernanceDecision(
        knowledge_governance_decision_id=(
            compute_knowledge_governance_decision_id(identity)
        ),
        contract_version=identity.governance_decision_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity.knowledge_candidate_snapshot_digest
        ),
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


def _ordered(
    *records: KnowledgeGovernanceDecision,
) -> tuple[KnowledgeGovernanceDecision, ...]:
    return tuple(
        sorted(records, key=lambda item: item.knowledge_governance_decision_id)
    )


def _request(
    *,
    candidate: KnowledgeCandidate | None = None,
    governance: tuple[KnowledgeGovernanceDecision, ...] | None = None,
    intended_authority_value: str = (
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE
    ),
    decision_outcome: str = AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    reason_codes: tuple[str, ...] | None = None,
    decided_by: str = "authority-actor",
    decided_at: datetime = FIXED_TIME + timedelta(hours=2),
    authority_policy_id: str = KNOWLEDGE_AUTHORITY_DECISION_POLICY_ID,
    authority_policy_version: str = KNOWLEDGE_AUTHORITY_DECISION_POLICY_VERSION,
) -> KnowledgeAuthorityDecisionRequest:
    selected_candidate = candidate if candidate is not None else _candidate()
    selected_governance = (
        governance
        if governance is not None
        else (_governance(selected_candidate),)
    )
    required_reason = {
        AUTHORITY_DECISION_OUTCOME_AUTHORIZED: (
            "intended_knowledge_authority_authorized"
        ),
        AUTHORITY_DECISION_OUTCOME_DENIED: (
            "intended_knowledge_authority_denied"
        ),
        AUTHORITY_DECISION_OUTCOME_DEFERRED: (
            "intended_knowledge_authority_deferred"
        ),
    }.get(decision_outcome, "caller_supplied_reason")
    return KnowledgeAuthorityDecisionRequest(
        knowledge_candidate=selected_candidate,
        knowledge_governance_decisions=selected_governance,
        intended_authority_value=intended_authority_value,
        decision_outcome=decision_outcome,
        reason_codes=(required_reason,) if reason_codes is None else reason_codes,
        decided_by=decided_by,
        decided_at=decided_at,
        authority_policy_id=authority_policy_id,
        authority_policy_version=authority_policy_version,
    )


def _recorded(request: KnowledgeAuthorityDecisionRequest) -> KnowledgeAuthorityDecision:
    result = decide_knowledge_authority(request)
    assert result.result_status == AUTHORITY_DECISION_RESULT_STATUS_RECORDED
    assert type(result.authority_decision) is KnowledgeAuthorityDecision
    assert result.reason_codes == ()
    assert result.diagnostics == ()
    return result.authority_decision


def _rejection(request: KnowledgeAuthorityDecisionRequest) -> str:
    result = decide_knowledge_authority(request)
    assert result.result_status == AUTHORITY_DECISION_RESULT_STATUS_REJECTED
    assert result.authority_decision is None
    assert len(result.reason_codes) == 1
    assert result.reason_codes[0] in _APPROVED_REJECTION_REASONS
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0].severity == "warning"
    assert result.diagnostics[0].code == result.reason_codes[0]
    return result.reason_codes[0]


def test_a01_all_authorized_records_authorized_outcome_without_mutation() -> None:
    request = _request()
    candidate_before = repr(request.knowledge_candidate)
    governance_before = repr(request.knowledge_governance_decisions)
    record = _recorded(request)
    assert record.decision_outcome == AUTHORITY_DECISION_OUTCOME_AUTHORIZED
    assert repr(request.knowledge_candidate) == candidate_before
    assert repr(request.knowledge_governance_decisions) == governance_before
    assert request.knowledge_candidate.authority_status == "unassessed"


def test_a02_denied_outcome_requires_and_preserves_exact_reason() -> None:
    request = _request(decision_outcome=AUTHORITY_DECISION_OUTCOME_DENIED)
    record = _recorded(request)
    assert record.decision_outcome == AUTHORITY_DECISION_OUTCOME_DENIED
    assert record.reason_codes == ("intended_knowledge_authority_denied",)


def test_a03_deferred_outcome_requires_reason_and_creates_no_readiness() -> None:
    request = _request(decision_outcome=AUTHORITY_DECISION_OUTCOME_DEFERRED)
    record = _recorded(request)
    assert record.decision_outcome == AUTHORITY_DECISION_OUTCOME_DEFERRED
    assert record.reason_codes == ("intended_knowledge_authority_deferred",)
    assert not hasattr(record, "promotion_prerequisite_result")
    assert not hasattr(record, "promotion_ready")


def test_a04_both_values_are_caller_selected_and_never_source_derived() -> None:
    records = []
    for index, (source_value, intended_value) in enumerate(
        (
            ("draft", INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE),
            ("official", INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE),
        ),
        start=1,
    ):
        candidate = _candidate(seed=str(index), source_authority_status=source_value)
        record = _recorded(
            _request(candidate=candidate, intended_authority_value=intended_value)
        )
        records.append(record)
    assert [item.intended_authority_value for item in records] == [
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    ]


def test_a05_record_preserves_candidate_identity_contract_and_snapshot() -> None:
    request = _request()
    record = _recorded(request)
    candidate = request.knowledge_candidate
    assert record.knowledge_candidate_id == candidate.knowledge_candidate_id
    assert record.knowledge_candidate_contract_version == candidate.contract_version
    assert record.knowledge_candidate_snapshot_digest == compute_knowledge_authority_candidate_snapshot_digest(candidate)


def test_a06_multiple_governance_records_are_ordered_valid_and_preserved() -> None:
    candidate = _candidate()
    governance = _ordered(
        _governance(candidate, seed="1"),
        _governance(candidate, seed="2"),
    )
    record = _recorded(_request(candidate=candidate, governance=governance))
    assert record.knowledge_governance_decision_ids == tuple(
        item.knowledge_governance_decision_id for item in governance
    )


def test_a07_exact_replay_produces_same_record_and_identity() -> None:
    request = _request()
    first = _recorded(request)
    second = _recorded(request)
    assert first == second
    assert first.knowledge_authority_decision_id == second.knowledge_authority_decision_id


def test_a08_material_request_changes_change_identity_without_override() -> None:
    baseline_request = _request()
    baseline = _recorded(baseline_request)
    changed_requests = (
        _request(intended_authority_value=INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE),
        _request(decision_outcome=AUTHORITY_DECISION_OUTCOME_DENIED),
        _request(reason_codes=("additional_reason", "intended_knowledge_authority_authorized")),
        _request(decided_by="other-authority-actor"),
        _request(decided_at=baseline_request.decided_at + timedelta(seconds=1)),
    )
    identities = {_recorded(item).knowledge_authority_decision_id for item in changed_requests}
    assert baseline.knowledge_authority_decision_id not in identities
    assert len(identities) == len(changed_requests)


def test_a09_unsupported_authority_policy_has_first_precedence() -> None:
    candidate = _candidate()
    governance = (_governance(candidate, GOVERNANCE_DECISION_DENIED, governance_policy_id="other-governance-policy"),)
    request = _request(
        candidate=candidate,
        governance=governance,
        intended_authority_value="other-value",
        decision_outcome="other-outcome",
        authority_policy_id="other-authority-policy",
    )
    assert _rejection(request) == "unsupported_authority_policy"


def test_a10_unsupported_value_precedes_outcome_and_lineage() -> None:
    candidate = _candidate()
    governance = (_governance(candidate, governance_policy_id="other-governance-policy"),)
    request = _request(
        candidate=candidate,
        governance=governance,
        intended_authority_value="other-value",
        decision_outcome="other-outcome",
    )
    assert _rejection(request) == "unsupported_authority_value"


def test_a11_unsupported_outcome_precedes_lineage_and_missing_reason() -> None:
    candidate = _candidate()
    governance = (_governance(candidate, governance_policy_id="other-governance-policy"),)
    request = _request(
        candidate=candidate,
        governance=governance,
        decision_outcome="other-outcome",
        reason_codes=("unrelated_reason",),
    )
    assert _rejection(request) == "unsupported_authority_decision_outcome"


def test_a12_unsupported_governance_evidence_policy_rejects() -> None:
    candidate = _candidate()
    governance = (_governance(candidate, governance_policy_version="2.0.0"),)
    assert _rejection(_request(candidate=candidate, governance=governance)) == "unsupported_governance_evidence_policy"


def test_a13_candidate_id_contract_and_snapshot_mismatch_precedence() -> None:
    candidate = _candidate()
    bad_id = _governance(
        candidate,
        candidate_id="kc1_" + "f" * 64,
        candidate_contract_version="knowledge-candidate-v2",
        candidate_snapshot_digest="f" * 64,
    )
    bad_contract = _governance(
        candidate,
        candidate_contract_version="knowledge-candidate-v2",
        candidate_snapshot_digest="f" * 64,
    )
    bad_snapshot = _governance(candidate, candidate_snapshot_digest="f" * 64)
    assert _rejection(_request(candidate=candidate, governance=(bad_id,))) == "governance_candidate_mismatch"
    assert _rejection(_request(candidate=candidate, governance=(bad_contract,))) == "governance_candidate_contract_mismatch"
    assert _rejection(_request(candidate=candidate, governance=(bad_snapshot,))) == "governance_candidate_snapshot_mismatch"


def test_a14_authorized_plus_denied_is_contradictory() -> None:
    candidate = _candidate()
    governance = _ordered(
        _governance(candidate, GOVERNANCE_DECISION_AUTHORIZED, seed="1"),
        _governance(candidate, GOVERNANCE_DECISION_DENIED, seed="2"),
    )
    assert _rejection(_request(candidate=candidate, governance=governance)) == "contradictory_governance_evidence"


def test_a15_denied_only_is_ineligible() -> None:
    candidate = _candidate()
    governance = (_governance(candidate, GOVERNANCE_DECISION_DENIED),)
    assert _rejection(_request(candidate=candidate, governance=governance)) == "ineligible_governance_evidence"


def test_a16_deferred_and_mixed_noncontradictory_sets_are_incomplete() -> None:
    candidate = _candidate()
    compositions = (
        (_governance(candidate, GOVERNANCE_DECISION_DEFERRED, seed="1"),),
        _ordered(
            _governance(candidate, GOVERNANCE_DECISION_AUTHORIZED, seed="1"),
            _governance(candidate, GOVERNANCE_DECISION_DEFERRED, seed="2"),
        ),
        _ordered(
            _governance(candidate, GOVERNANCE_DECISION_DENIED, seed="1"),
            _governance(candidate, GOVERNANCE_DECISION_DEFERRED, seed="2"),
        ),
    )
    for governance in compositions:
        assert _rejection(_request(candidate=candidate, governance=governance)) == "incomplete_governance_evidence"


def test_a17_missing_required_reason_rejects_without_repair() -> None:
    request = _request(reason_codes=("caller_reason",))
    before = request.reason_codes
    assert _rejection(request) == "missing_required_authority_reason"
    assert request.reason_codes == before


def test_a18_malformed_collections_substitutes_and_identities_fail_closed() -> None:
    candidate = _candidate()
    governance = _governance(candidate)
    invalid_governance_values = ([], (), (governance, governance), ("kg1_" + "1" * 64,), ({"id": "value"},), (Path("candidate"),))
    for value in invalid_governance_values:
        with pytest.raises(ValueError):
            _request(candidate=candidate, governance=value)  # type: ignore[arg-type]
    second = _governance(candidate, seed="2")
    ordered = _ordered(governance, second)
    with pytest.raises(ValueError):
        _request(candidate=candidate, governance=tuple(reversed(ordered)))
    with pytest.raises(ValueError):
        _request(reason_codes=[])  # type: ignore[arg-type]
    broken_candidate = _candidate()
    object.__setattr__(broken_candidate, "knowledge_candidate_id", "kc1_" + "f" * 64)
    with pytest.raises(ValueError):
        _request(candidate=broken_candidate)
    broken_governance = _governance(candidate)
    object.__setattr__(broken_governance, "knowledge_governance_decision_id", "kg1_" + "f" * 64)
    with pytest.raises(ValueError):
        _request(candidate=candidate, governance=(broken_governance,))
    with pytest.raises(ValueError):
        decide_knowledge_authority(object())  # type: ignore[arg-type]
    arbitrary_reason = KnowledgeAuthorityDiagnostic(
        code="arbitrary_reason",
        severity="warning",
        message="message",
        field="request",
        source="test",
    )
    with pytest.raises(ValueError, match="unsupported rejection reason"):
        KnowledgeAuthorityDecisionResult(
            result_status=AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
            authority_decision=None,
            reason_codes=("arbitrary_reason",),
            diagnostics=(arbitrary_reason,),
        )
    info_diagnostic = KnowledgeAuthorityDiagnostic(
        code="unsupported_authority_policy",
        severity="info",
        message="message",
        field="request",
        source="test",
    )
    with pytest.raises(ValueError, match="severity must be warning"):
        KnowledgeAuthorityDecisionResult(
            result_status=AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
            authority_decision=None,
            reason_codes=("unsupported_authority_policy",),
            diagnostics=(info_diagnostic,),
        )
    mismatched_diagnostic = KnowledgeAuthorityDiagnostic(
        code="unsupported_authority_value",
        severity="warning",
        message="message",
        field="request",
        source="test",
    )
    with pytest.raises(ValueError, match="code must match reason code"):
        KnowledgeAuthorityDecisionResult(
            result_status=AUTHORITY_DECISION_RESULT_STATUS_REJECTED,
            authority_decision=None,
            reason_codes=("unsupported_authority_policy",),
            diagnostics=(mismatched_diagnostic,),
        )


def test_a19_inputs_results_are_frozen_and_no_source_or_semantic_inference_occurs() -> None:
    first_candidate = _candidate(statement="Statement alpha.", source_authority_status="draft")
    second_candidate = _candidate(statement="Contradictory statement beta.", seed="2", source_authority_status="official")
    first_request = _request(candidate=first_candidate)
    second_request = _request(candidate=second_candidate)
    first_result = decide_knowledge_authority(first_request)
    second_result = decide_knowledge_authority(second_request)
    assert first_result.result_status == second_result.result_status == AUTHORITY_DECISION_RESULT_STATUS_RECORDED
    assert first_result.authority_decision is not None
    assert second_result.authority_decision is not None
    assert first_result.authority_decision.intended_authority_value == second_result.authority_decision.intended_authority_value
    for value, field in ((first_request, "decided_by"), (first_result, "result_status"), (first_candidate, "authority_status")):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, "changed")


def test_a20_production_imports_and_runtime_exclude_forbidden_behavior() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = (
        root / "src/rie/domain/knowledge_authority_decision.py",
        root / "src/rie/application/knowledge_authority_decider.py",
    )
    forbidden_modules = {
        "rie.domain.knowledge_conflict_assessment_record", "pathlib", "sqlite3",
        "subprocess", "logging", "random", "uuid", "requests", "openai",
    }
    forbidden_calls = {
        "open", "print", "sleep", "retry", "promote", "persist", "serialize",
        "resolve_conflict", "create_governed_knowledge", "evaluate_promotion_prerequisites",
    }
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = set()
        calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        assert forbidden_modules.isdisjoint(imports)
        assert forbidden_calls.isdisjoint(calls)
    application_tree = ast.parse(paths[1].read_text(encoding="utf-8"))
    public_functions = {
        node.name
        for node in application_tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }
    assert public_functions == {"decide_knowledge_authority"}
    recorded = _recorded(_request())
    for field in (
        "conflict_resolution", "promotion_prerequisite_result", "promotion_result",
        "governed_knowledge", "lifecycle_status", "acceptance", "repository", "persistence",
    ):
        assert not hasattr(recorded, field)
    assert isinstance(
        KnowledgeAuthorityDecisionResult(
            result_status="recorded",
            authority_decision=recorded,
            reason_codes=(),
            diagnostics=(),
        ),
        KnowledgeAuthorityDecisionResult,
    )
