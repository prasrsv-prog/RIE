import ast
import builtins
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import random
import socket
import subprocess
import time
import uuid

import pytest

from evidence.evidence import Evidence as LegacyEvidence
from knowledge.text_knowledge import TextKnowledge
from rie.application import knowledge_reviewer as reviewer_module
from rie.application.evidence_candidate import EvidenceCandidate
from rie.application.knowledge_reviewer import (
    KNOWLEDGE_REVIEW_POLICY_ID,
    KNOWLEDGE_REVIEW_POLICY_VERSION,
    REVIEW_RESULT_STATUS_RECORDED,
    REVIEW_RESULT_STATUS_REJECTED,
    KnowledgeReviewRequest,
    KnowledgeReviewResult,
    review_knowledge_candidate,
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
    KnowledgeDiagnostic,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
)
from rie.domain.knowledge_review_record import (
    REVIEW_DECISION_DEFERRED,
    REVIEW_DECISION_PASSED,
    REVIEW_DECISION_REJECTED,
    KnowledgeReviewRecord,
    compute_knowledge_candidate_review_snapshot_digest,
)


FIXED_TIME = datetime(2026, 7, 13, 9, 15, 30, 654321, tzinfo=timezone.utc)


def _support(
    *,
    seed: str = "1",
    source_authority_status: str = "official",
    source_lifecycle_status: str = "active",
    acceptance_record_ids: tuple[str, ...] | None = None,
    acceptance_review_record_ids: tuple[str, ...] | None = None,
) -> KnowledgeEvidenceSupport:
    return KnowledgeEvidenceSupport(
        evidence_id="ev1_" + seed * 64,
        acceptance_record_ids=(
            acceptance_record_ids or ("ar1_" + seed * 64,)
        ),
        acceptance_review_record_ids=(
            acceptance_review_record_ids or (f"review-{seed}",)
        ),
        source_id=f"source-{seed}",
        source_content_digest=seed * 64,
        source_authority_status=source_authority_status,
        source_lifecycle_status=source_lifecycle_status,
        payload_digest=chr(ord(seed) + 1) * 64,
        locator_type="page",
        locator_value=(int(seed), "paragraph-2"),
        locator_schema_version="1.0.0",
    )


def _candidate(
    *,
    statement: str = "Exact fact",
    support: tuple[KnowledgeEvidenceSupport, ...] | None = None,
    diagnostics: tuple[KnowledgeDiagnostic, ...] = (),
) -> KnowledgeCandidate:
    candidate_support = support or (_support(),)
    identity_input = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement=statement,
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=candidate_support,
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
        support=candidate_support,
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
        conflict_ids=(),
        diagnostics=diagnostics,
    )


def _request(
    candidate: KnowledgeCandidate | None = None,
    **changes: object,
) -> KnowledgeReviewRequest:
    values = {
        "knowledge_candidate": candidate or _candidate(),
        "review_decision": REVIEW_DECISION_PASSED,
        "reason_codes": ("verified",),
        "reviewed_by": "reviewer-1",
        "reviewed_at": FIXED_TIME,
        "review_policy_id": KNOWLEDGE_REVIEW_POLICY_ID,
        "review_policy_version": KNOWLEDGE_REVIEW_POLICY_VERSION,
    }
    values.update(changes)
    return KnowledgeReviewRequest(**values)


def _recorded(request: KnowledgeReviewRequest) -> KnowledgeReviewRecord:
    result = review_knowledge_candidate(request)
    assert result.result_status == REVIEW_RESULT_STATUS_RECORDED
    assert type(result.review_record) is KnowledgeReviewRecord
    assert result.reason_codes == ()
    assert result.diagnostics == ()
    return result.review_record


def _rejection(result: KnowledgeReviewResult) -> str:
    assert result.result_status == REVIEW_RESULT_STATUS_REJECTED
    assert result.review_record is None
    assert len(result.reason_codes) == 1
    assert result.diagnostics[0].code == result.reason_codes[0]
    return result.reason_codes[0]


def test_a01_passed_review_records_one_record_without_candidate_mutation() -> None:
    candidate = _candidate()
    before = repr(candidate)
    request = _request(candidate)
    result = review_knowledge_candidate(request)

    assert result.result_status == "recorded"
    assert type(result.review_record) is KnowledgeReviewRecord
    assert result.review_record.review_decision == REVIEW_DECISION_PASSED
    assert repr(candidate) == before
    assert candidate.authority_status == "unassessed"
    assert candidate.lifecycle_status == "candidate"
    assert candidate.review_status == "pending_review"
    assert candidate.conflict_status == "not_assessed"
    with pytest.raises(FrozenInstanceError):
        request.review_decision = REVIEW_DECISION_REJECTED
    with pytest.raises(FrozenInstanceError):
        result.result_status = REVIEW_RESULT_STATUS_REJECTED


@pytest.mark.parametrize(
    "decision,reasons",
    (
        (REVIEW_DECISION_REJECTED, ("insufficient_support",)),
        (REVIEW_DECISION_DEFERRED, ("conflict_assessment_required",)),
    ),
)
def test_a02_rejected_and_deferred_decisions_record_exact_reasons(
    decision: str,
    reasons: tuple[str, ...],
) -> None:
    record = _recorded(
        _request(review_decision=decision, reason_codes=reasons)
    )
    assert record.review_decision == decision
    assert record.reason_codes == reasons


def test_a03_review_basis_is_derived_completely_from_candidate_support() -> None:
    first = _support(
        seed="1",
        acceptance_record_ids=("ar1_" + "1" * 64, "ar1_" + "3" * 64),
        acceptance_review_record_ids=("review-1", "review-3"),
    )
    second = _support(
        seed="5",
        acceptance_record_ids=("ar1_" + "5" * 64, "ar1_" + "7" * 64),
        acceptance_review_record_ids=("review-2", "review-4"),
    )
    candidate = _candidate(support=(first, second))
    record = _recorded(_request(candidate))

    assert record.knowledge_candidate_id == candidate.knowledge_candidate_id
    assert record.knowledge_candidate_contract_version == candidate.contract_version
    assert record.knowledge_candidate_snapshot_digest == (
        compute_knowledge_candidate_review_snapshot_digest(candidate)
    )
    assert record.reviewed_evidence_ids == tuple(
        sorted((first.evidence_id, second.evidence_id))
    )
    assert record.reviewed_acceptance_record_ids == tuple(
        sorted(first.acceptance_record_ids + second.acceptance_record_ids)
    )
    assert record.reviewed_acceptance_review_record_ids == tuple(
        sorted(
            first.acceptance_review_record_ids
            + second.acceptance_review_record_ids
        )
    )


def test_a04_actor_policy_timestamp_and_reasons_are_copied_exactly() -> None:
    reviewed_at = FIXED_TIME.astimezone(timezone(timedelta(hours=7)))
    request = _request(
        review_decision=REVIEW_DECISION_DEFERRED,
        reason_codes=("additional_review", "policy_check"),
        reviewed_by="reviewer-27",
        reviewed_at=reviewed_at,
    )
    record = _recorded(request)
    assert record.reviewed_by == request.reviewed_by
    assert record.reviewed_at is reviewed_at
    assert record.review_policy_id == KNOWLEDGE_REVIEW_POLICY_ID
    assert record.review_policy_version == KNOWLEDGE_REVIEW_POLICY_VERSION
    assert record.reason_codes == request.reason_codes


def test_a05_exact_replay_returns_same_record_and_kr1_identity() -> None:
    request = _request()
    first = review_knowledge_candidate(request)
    second = review_knowledge_candidate(request)
    assert first == second
    assert first.review_record.knowledge_review_record_id.startswith("kr1_")
    assert first.review_record.knowledge_review_record_id == (
        second.review_record.knowledge_review_record_id
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"review_decision": REVIEW_DECISION_REJECTED},
        {"reason_codes": ("other_reason",)},
        {"reviewed_by": "reviewer-2"},
        {"reviewed_at": FIXED_TIME + timedelta(seconds=1)},
    ),
)
def test_a06_material_review_change_produces_distinct_identity(
    changes: dict[str, object],
) -> None:
    baseline = _recorded(_request())
    changed = _recorded(_request(**changes))
    assert baseline.knowledge_review_record_id != changed.knowledge_review_record_id


@pytest.mark.parametrize(
    "changes",
    (
        {"review_policy_id": "unsupported-policy"},
        {"review_policy_version": "2.0.0"},
    ),
)
def test_a07_unsupported_policy_returns_explicit_rejection(
    changes: dict[str, str],
) -> None:
    assert _rejection(
        review_knowledge_candidate(_request(**changes))
    ) == "unsupported_review_policy"


def test_a08_unsupported_decision_returns_explicit_rejection() -> None:
    assert _rejection(
        review_knowledge_candidate(_request(review_decision="accepted"))
    ) == "unsupported_review_decision"


@pytest.mark.parametrize(
    "bad_candidate",
    (
        {},
        "kc1_" + "0" * 64,
        Path("candidate.json"),
        object.__new__(EvidenceCandidate),
        object.__new__(AcceptedEvidence),
        object.__new__(LegacyEvidence),
        TextKnowledge("source.txt", "fact", 4, 0),
        object(),
    ),
)
def test_a09_request_requires_exact_candidate_and_rejects_boundary_inputs(
    bad_candidate: object,
) -> None:
    with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
        KnowledgeReviewRequest(
            knowledge_candidate=bad_candidate,
            review_decision=REVIEW_DECISION_PASSED,
            reason_codes=("verified",),
            reviewed_by="reviewer",
            reviewed_at=FIXED_TIME,
            review_policy_id=KNOWLEDGE_REVIEW_POLICY_ID,
            review_policy_version=KNOWLEDGE_REVIEW_POLICY_VERSION,
        )

    class DuckRequest:
        pass

    with pytest.raises(ValueError, match="exact KnowledgeReviewRequest"):
        review_knowledge_candidate(DuckRequest())


@pytest.mark.parametrize(
    "bad_reasons",
    (
        [],
        (),
        (" ",),
        ("same", "same"),
        ("z", "a"),
        (3,),
    ),
)
def test_a10_reason_codes_fail_closed_without_repair(
    bad_reasons: object,
) -> None:
    with pytest.raises(ValueError, match="reason_codes"):
        _request(reason_codes=bad_reasons)


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("review_decision", " "),
        ("reviewed_by", ""),
        ("review_policy_id", " "),
        ("review_policy_version", None),
        ("reviewed_at", datetime(2026, 7, 13, 9, 15)),
        ("reviewed_at", "2026-07-13T09:15:00Z"),
    ),
)
def test_a11_timestamp_and_required_strings_raise_value_error(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _request(**{field_name: bad_value})

    class DatetimeSubclass(datetime):
        pass

    with pytest.raises(ValueError, match="reviewed_at"):
        _request(
            reviewed_at=DatetimeSubclass(
                2026, 7, 13, 9, 15, tzinfo=timezone.utc
            )
        )


def test_a12_source_governance_never_selects_outcome_or_promotes_candidate() -> None:
    official = _candidate(
        support=(
            _support(
                source_authority_status="official",
                source_lifecycle_status="active",
            ),
        )
    )
    draft = _candidate(
        support=(
            _support(
                source_authority_status="draft",
                source_lifecycle_status="superseded",
            ),
        )
    )
    official_record = _recorded(
        _request(official, review_decision=REVIEW_DECISION_DEFERRED)
    )
    draft_record = _recorded(
        _request(draft, review_decision=REVIEW_DECISION_DEFERRED)
    )

    assert official_record.review_decision == draft_record.review_decision
    for candidate in (official, draft):
        assert candidate.authority_status == "unassessed"
        assert candidate.lifecycle_status == "candidate"
        assert candidate.review_status == "pending_review"
        assert candidate.conflict_status == "not_assessed"


def test_a13_passed_review_creates_no_governance_promotion_or_downstream() -> None:
    record = _recorded(_request())
    for forbidden_attribute in (
        "knowledge",
        "governed_knowledge",
        "accept",
        "promote",
        "assign_authority",
        "transition_lifecycle",
        "resolve_conflict",
        "save",
        "serialize",
        "to_prompt_candidate",
    ):
        assert not hasattr(record, forbidden_attribute)
    assert record.review_decision == "passed"
    assert record.knowledge_candidate_id.startswith("kc1_")


def test_a14_contradictory_records_coexist_without_winner_selection() -> None:
    candidate = _candidate()
    passed = _recorded(
        _request(
            candidate,
            review_decision=REVIEW_DECISION_PASSED,
            reason_codes=("verified",),
        )
    )
    rejected = _recorded(
        _request(
            candidate,
            review_decision=REVIEW_DECISION_REJECTED,
            reason_codes=("insufficient_support",),
        )
    )
    reverse_rejected = _recorded(
        _request(
            candidate,
            review_decision=REVIEW_DECISION_REJECTED,
            reason_codes=("insufficient_support",),
        )
    )
    reverse_passed = _recorded(
        _request(
            candidate,
            review_decision=REVIEW_DECISION_PASSED,
            reason_codes=("verified",),
        )
    )

    assert passed.knowledge_review_record_id != rejected.knowledge_review_record_id
    assert reverse_passed == passed
    assert reverse_rejected == rejected
    assert passed.knowledge_candidate_id == rejected.knowledge_candidate_id


def test_a15_inputs_remain_unchanged_after_recorded_and_rejected_results() -> None:
    recorded_request = _request()
    rejected_request = replace(recorded_request, review_policy_id="unsupported")
    recorded_before = repr(recorded_request)
    rejected_before = repr(rejected_request)

    review_knowledge_candidate(recorded_request)
    review_knowledge_candidate(rejected_request)

    assert repr(recorded_request) == recorded_before
    assert repr(rejected_request) == rejected_before


def test_a16_production_imports_exclude_forbidden_boundaries() -> None:
    source_paths = (
        Path(reviewer_module.__file__),
        Path(reviewer_module.__file__).parents[1]
        / "domain"
        / "knowledge_review_record.py",
    )
    imported_modules = set()
    for source_path in source_paths:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)

    forbidden_prefixes = (
        "rie.interfaces",
        "rie.infrastructure",
        "rie.repositories",
        "pathlib",
        "os",
        "sqlite3",
        "pypdf",
        "requests",
        "socket",
        "subprocess",
        "random",
        "uuid",
        "time",
        "logging",
        "openai",
        "prompting",
        "rie.prompt",
        "rie.knowledge",
        "knowledge",
        "evidence",
    )
    assert not any(
        module == prefix or module.startswith(prefix + ".")
        for module in imported_modules
        for prefix in forbidden_prefixes
    )


def test_a17_review_has_no_filesystem_network_clock_random_or_process_side_effect(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("forbidden side effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(random, "random", forbidden)
    monkeypatch.setattr(uuid, "uuid4", forbidden)
    monkeypatch.setattr(time, "time", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    environment_before = dict(os.environ)

    result = review_knowledge_candidate(_request())

    assert result.result_status == REVIEW_RESULT_STATUS_RECORDED
    assert dict(os.environ) == environment_before
    assert caplog.records == []
