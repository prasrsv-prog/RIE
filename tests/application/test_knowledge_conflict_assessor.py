import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from evidence.evidence import Evidence
from knowledge.text_knowledge import TextKnowledge
from prompting.text_prompt_candidate import TextPromptCandidate
from rie.application.knowledge_conflict_assessor import (
    CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED,
    CONFLICT_ASSESSMENT_RESULT_STATUS_REJECTED,
    KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID,
    KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION,
    KnowledgeConflictAssessmentRequest,
    KnowledgeConflictAssessmentResult,
    assess_knowledge_candidate_conflict,
)
from rie.domain.accepted_evidence import AcceptedEvidence
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
    KnowledgeConflictAssessmentRecord,
    compute_knowledge_conflict_candidate_snapshot_digest,
)
from rie.domain.knowledge_governance_decision import KnowledgeGovernanceDecision
from rie.domain.knowledge_review_record import KnowledgeReviewRecord


FIXED_TIME = datetime(2026, 7, 13, 12, 45, 30, 654321, tzinfo=timezone.utc)


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
        locator_value=(int(seed),),
        locator_schema_version="1.0.0",
    )


def _candidate(
    *,
    statement: str,
    seed: str,
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


def _pair() -> tuple[KnowledgeCandidate, ...]:
    candidates = (
        _candidate(statement="The fact is enabled.", seed="1"),
        _candidate(statement="The fact is disabled.", seed="2"),
    )
    return tuple(
        sorted(candidates, key=lambda item: item.knowledge_candidate_id)
    )


def _request(
    *,
    participants: tuple[KnowledgeCandidate, ...] | None = None,
    assessment_outcome: str = ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
    reason_codes: tuple[str, ...] = ("semantic_conflict_identified",),
    assessed_by: str = "conflict-assessor",
    assessed_at: datetime = FIXED_TIME,
    assessment_policy_id: str = KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_ID,
    assessment_policy_version: str = (
        KNOWLEDGE_CONFLICT_ASSESSMENT_POLICY_VERSION
    ),
) -> KnowledgeConflictAssessmentRequest:
    return KnowledgeConflictAssessmentRequest(
        participants=_pair() if participants is None else participants,
        assessment_outcome=assessment_outcome,
        reason_codes=reason_codes,
        assessed_by=assessed_by,
        assessed_at=assessed_at,
        assessment_policy_id=assessment_policy_id,
        assessment_policy_version=assessment_policy_version,
    )


def _recorded(
    request: KnowledgeConflictAssessmentRequest,
) -> KnowledgeConflictAssessmentRecord:
    result = assess_knowledge_candidate_conflict(request)
    assert result.result_status == CONFLICT_ASSESSMENT_RESULT_STATUS_RECORDED
    assert type(result.conflict_assessment_record) is (
        KnowledgeConflictAssessmentRecord
    )
    assert result.reason_codes == ()
    return result.conflict_assessment_record


def _rejected(
    request: KnowledgeConflictAssessmentRequest,
    reason: str,
) -> KnowledgeConflictAssessmentResult:
    result = assess_knowledge_candidate_conflict(request)
    assert result.result_status == CONFLICT_ASSESSMENT_RESULT_STATUS_REJECTED
    assert result.conflict_assessment_record is None
    assert result.reason_codes == (reason,)
    assert len(result.diagnostics) == 1
    return result


def test_a01_pair_records_conflict_with_required_reason_and_no_mutation() -> None:
    pair = _pair()
    request = _request(participants=pair)
    before = (pair, request)
    record = _recorded(request)
    assert record.assessment_outcome == ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED
    assert record.reason_codes == ("semantic_conflict_identified",)
    assert record.assessment_scope == (
        ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
    )
    assert (pair, request) == before


def test_a02_equivalent_statement_requires_its_exact_reason() -> None:
    record = _recorded(
        _request(
            assessment_outcome=ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
            reason_codes=("semantic_equivalence_identified",),
        )
    )
    assert record.assessment_outcome == ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT
    assert record.reason_codes == ("semantic_equivalence_identified",)


def test_a03_no_conflict_is_pair_limited_and_requires_its_reason() -> None:
    record = _recorded(
        _request(
            assessment_outcome=ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
            reason_codes=("pairwise_no_conflict_identified",),
        )
    )
    assert record.assessment_outcome == (
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED
    )
    assert len(record.participants) == 2
    assert "global" not in record.assessment_scope


def test_a04_assessment_deferred_requires_its_exact_reason() -> None:
    record = _recorded(
        _request(
            assessment_outcome=ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
            reason_codes=("semantic_assessment_deferred",),
        )
    )
    assert record.assessment_outcome == ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED
    assert record.reason_codes == ("semantic_assessment_deferred",)


def test_a05_participants_preserve_candidate_identity_contract_and_snapshot() -> None:
    request = _request()
    record = _recorded(request)
    assert tuple(
        participant.knowledge_candidate_id
        for participant in record.participants
    ) == tuple(candidate.knowledge_candidate_id for candidate in request.participants)
    for candidate, participant in zip(request.participants, record.participants):
        assert participant.knowledge_candidate_contract_version == (
            candidate.contract_version
        )
        assert participant.knowledge_candidate_snapshot_digest == (
            compute_knowledge_conflict_candidate_snapshot_digest(candidate)
        )


def test_a06_exact_replay_produces_the_same_record_and_identity() -> None:
    request = _request()
    first = _recorded(request)
    second = _recorded(request)
    assert first == second
    assert first.knowledge_conflict_assessment_record_id == (
        second.knowledge_conflict_assessment_record_id
    )


def test_a07_material_changes_change_identity_without_selecting_a_winner() -> None:
    baseline = _recorded(_request())
    changed_records = (
        _recorded(_request(assessed_by="other-assessor")),
        _recorded(_request(assessed_at=FIXED_TIME + timedelta(seconds=1))),
        _recorded(
            _request(
                reason_codes=(
                    "additional_context",
                    "semantic_conflict_identified",
                )
            )
        ),
        _recorded(
            _request(
                assessment_outcome=ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
                reason_codes=("semantic_equivalence_identified",),
            )
        ),
    )
    assert len(
        {
            baseline.knowledge_conflict_assessment_record_id,
            *(
                record.knowledge_conflict_assessment_record_id
                for record in changed_records
            ),
        }
    ) == 5
    for record in (baseline, *changed_records):
        assert not hasattr(record, "winner")


def test_a08_unsupported_policy_has_first_rejection_precedence() -> None:
    for changes in (
        {"assessment_policy_id": "other-policy"},
        {"assessment_policy_version": "2.0.0"},
        {
            "assessment_policy_id": "other-policy",
            "assessment_policy_version": "2.0.0",
            "assessment_outcome": "other-outcome",
            "reason_codes": ("other_reason",),
        },
    ):
        _rejected(
            _request(**changes),
            "unsupported_conflict_assessment_policy",
        )


def test_a09_unsupported_outcome_precedes_missing_reason() -> None:
    _rejected(
        _request(
            assessment_outcome="other_outcome",
            reason_codes=("other_reason",),
        ),
        "unsupported_conflict_assessment_outcome",
    )


def test_a10_missing_required_reason_rejects_without_repair() -> None:
    request = _request(reason_codes=("caller_reason",))
    original_reasons = request.reason_codes
    result = _rejected(
        request,
        "missing_required_conflict_assessment_reason",
    )
    assert request.reason_codes is original_reasons
    assert request.reason_codes == ("caller_reason",)
    assert result.reason_codes != request.reason_codes


def test_a11_invalid_participant_collections_fail_closed() -> None:
    first, second = _pair()
    third = _candidate(statement="A third fact.", seed="3")
    invalid = (
        (),
        (first,),
        (first, second, third),
        (first, first),
        [first, second],
        (first, object()),
    )
    for participants in invalid:
        with pytest.raises(ValueError, match="participants"):
            _request(participants=participants)


def test_a12_reversed_candidate_order_fails_closed_without_repair() -> None:
    pair = _pair()
    reversed_pair = tuple(reversed(pair))
    with pytest.raises(ValueError, match="ordered by candidate ID"):
        _request(participants=reversed_pair)
    assert reversed_pair == tuple(reversed(pair))


def test_a13_non_candidate_domain_legacy_prompt_and_duck_values_are_rejected() -> None:
    class DuckCandidate:
        knowledge_candidate_id = "kc1_" + "1" * 64

    substitutes = (
        {},
        Path("candidate.json"),
        "kc1_" + "1" * 64,
        object.__new__(Evidence),
        object.__new__(AcceptedEvidence),
        object.__new__(KnowledgeReviewRecord),
        object.__new__(KnowledgeGovernanceDecision),
        TextKnowledge("legacy", "value", 5, 1),
        TextPromptCandidate("legacy", "value", 5, 1, 1),
        DuckCandidate(),
    )
    candidate = _pair()[0]
    for substitute in substitutes:
        with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
            _request(participants=(candidate, substitute))
    with pytest.raises(ValueError, match="exact KnowledgeConflictAssessmentRequest"):
        assess_knowledge_candidate_conflict({})


def test_a14_broken_candidate_identity_fails_before_snapshot_recording() -> None:
    first, second = _pair()
    original_id = first.knowledge_candidate_id
    object.__setattr__(first, "statement", first.statement + " changed")
    with pytest.raises(ValueError, match="does not match identity"):
        _request(participants=(first, second))
    assert first.knowledge_candidate_id == original_id


def test_a15_inputs_and_recorded_or_rejected_results_remain_immutable() -> None:
    pair = _pair()
    reasons = ("semantic_conflict_identified",)
    request = _request(participants=pair, reason_codes=reasons)
    recorded = assess_knowledge_candidate_conflict(request)
    rejected = assess_knowledge_candidate_conflict(
        _request(assessment_policy_id="other-policy")
    )
    with pytest.raises(FrozenInstanceError):
        pair[0].statement = "changed"
    with pytest.raises(FrozenInstanceError):
        request.assessed_by = "changed"
    with pytest.raises(FrozenInstanceError):
        recorded.result_status = "changed"
    with pytest.raises(FrozenInstanceError):
        rejected.reason_codes = ()
    assert request.participants is pair
    assert request.reason_codes is reasons


def test_a16_caller_outcome_is_not_inferred_from_content_authority_time_or_id() -> None:
    pair = _pair()
    conflict = _recorded(_request(participants=pair))
    no_conflict = _recorded(
        _request(
            participants=pair,
            assessment_outcome=ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
            reason_codes=("pairwise_no_conflict_identified",),
            assessed_at=FIXED_TIME + timedelta(hours=1),
        )
    )
    assert conflict.assessment_outcome == ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED
    assert no_conflict.assessment_outcome == (
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED
    )
    assert conflict.participants == no_conflict.participants
    assert all(
        support.source_authority_status == "official"
        for candidate in pair
        for support in candidate.support
    )
    for record in (conflict, no_conflict):
        assert not hasattr(record, "review_decision")
        assert not hasattr(record, "governance_decision")
        assert not hasattr(record, "winner")


def test_a17_recording_creates_no_resolution_or_downstream_result() -> None:
    record = _recorded(_request())
    for forbidden in (
        "conflict_resolution",
        "winner",
        "supersession",
        "invalidation",
        "authority_assignment",
        "lifecycle_transition",
        "acceptance",
        "promotion",
        "governed_knowledge",
        "final_knowledge",
        "repository",
        "persistence",
    ):
        assert not hasattr(record, forbidden)


def test_a18_production_imports_and_runtime_exclude_forbidden_behavior() -> None:
    root = Path(__file__).resolve().parents[2]
    production_paths = (
        root / "src/rie/domain/knowledge_conflict_assessment_record.py",
        root / "src/rie/application/knowledge_conflict_assessor.py",
    )
    import_names: set[str] = set()
    public_application_functions: list[str] = []
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
        if path.name == "knowledge_conflict_assessor.py":
            public_application_functions.extend(
                node.name
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
                and not node.name.startswith("_")
            )

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
        "knowledge_governance_decision",
        "rie.knowledge",
        "knowledge.",
    )
    assert not any(
        forbidden in imported
        for imported in import_names
        for forbidden in forbidden_import_parts
    )
    for forbidden_text in (
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "open(",
        ".read_text(",
        ".write_text(",
        "retry",
        ".statement",
        "embedding",
        "tokenize",
        "knowledge review record",
        "knowledge governance decision",
    ):
        assert forbidden_text not in combined_source
    assert public_application_functions == [
        "assess_knowledge_candidate_conflict"
    ]
    request = _request(assessed_at=FIXED_TIME)
    result = assess_knowledge_candidate_conflict(request)
    assert type(result) is KnowledgeConflictAssessmentResult
    assert result.conflict_assessment_record is not None
    assert result.conflict_assessment_record.assessed_at is FIXED_TIME
