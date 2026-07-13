import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

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
from rie.domain import knowledge_review_record as review_module
from rie.domain.knowledge_review_record import (
    KNOWLEDGE_CANDIDATE_REVIEW_SNAPSHOT_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_REVIEW_DIGEST_ALGORITHM,
    KNOWLEDGE_REVIEW_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_REVIEW_IDENTITY_POLICY_ID,
    KNOWLEDGE_REVIEW_IDENTITY_POLICY_VERSION,
    KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REVIEW_RECORD_ID_PREFIX,
    REVIEW_DECISION_DEFERRED,
    REVIEW_DECISION_PASSED,
    REVIEW_DECISION_REJECTED,
    KnowledgeReviewDiagnostic,
    KnowledgeReviewIdentityInput,
    KnowledgeReviewRecord,
    canonical_knowledge_review_identity_bytes,
    compute_knowledge_candidate_review_snapshot_digest,
    compute_knowledge_review_record_id,
    knowledge_review_identity_input_from_record,
)


FIXED_TIME = datetime(2026, 7, 13, 8, 30, 15, 123456, tzinfo=timezone.utc)


def _support(
    *,
    seed: str = "1",
    source_authority_status: str = "official",
    source_lifecycle_status: str = "active",
    acceptance_review_record_ids: tuple[str, ...] = ("review-1",),
) -> KnowledgeEvidenceSupport:
    return KnowledgeEvidenceSupport(
        evidence_id="ev1_" + seed * 64,
        acceptance_record_ids=("ar1_" + seed * 64,),
        acceptance_review_record_ids=acceptance_review_record_ids,
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


def _identity_input(**changes: object) -> KnowledgeReviewIdentityInput:
    candidate = _candidate()
    values = {
        "review_record_contract_version": (
            KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION
        ),
        "knowledge_candidate_id": candidate.knowledge_candidate_id,
        "knowledge_candidate_contract_version": candidate.contract_version,
        "knowledge_candidate_snapshot_digest": (
            compute_knowledge_candidate_review_snapshot_digest(candidate)
        ),
        "review_decision": REVIEW_DECISION_PASSED,
        "reason_codes": ("verified",),
        "reviewed_evidence_ids": (candidate.support[0].evidence_id,),
        "reviewed_acceptance_record_ids": (
            candidate.support[0].acceptance_record_ids
        ),
        "reviewed_acceptance_review_record_ids": (
            candidate.support[0].acceptance_review_record_ids
        ),
        "reviewed_by": "reviewer-1",
        "reviewed_at": FIXED_TIME,
        "review_policy_id": "rcis-knowledge-candidate-review",
        "review_policy_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgeReviewIdentityInput(**values)


def _record(
    *,
    diagnostics: tuple[KnowledgeReviewDiagnostic, ...] = (),
    **changes: object,
) -> KnowledgeReviewRecord:
    identity_input = _identity_input(**changes)
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
        diagnostics=diagnostics,
    )


def test_d01_contracts_are_frozen_value_equal_and_explicitly_identified() -> None:
    diagnostic = KnowledgeReviewDiagnostic(
        "notice", "info", "Reviewed", "review_decision", "test"
    )
    identity_input = _identity_input()
    record = _record(diagnostics=(diagnostic,))

    assert record == _record(diagnostics=(diagnostic,))
    assert record.knowledge_review_record_id.startswith("kr1_")
    with pytest.raises(FrozenInstanceError):
        diagnostic.code = "changed"
    with pytest.raises(FrozenInstanceError):
        identity_input.reviewed_by = "changed"
    with pytest.raises(FrozenInstanceError):
        record.review_decision = REVIEW_DECISION_REJECTED


def test_d02_identity_and_contract_constants_are_exact() -> None:
    assert KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION == "knowledge-review-record-v1"
    assert (
        KNOWLEDGE_REVIEW_IDENTITY_POLICY_ID
        == "rcis-knowledge-review-record-identity"
    )
    assert KNOWLEDGE_REVIEW_IDENTITY_POLICY_VERSION == "1.0.0"
    assert (
        KNOWLEDGE_REVIEW_IDENTITY_CANONICALIZATION_CONTRACT
        == "knowledge-review-record-json-v1"
    )
    assert (
        KNOWLEDGE_CANDIDATE_REVIEW_SNAPSHOT_CANONICALIZATION_CONTRACT
        == "knowledge-candidate-review-snapshot-json-v1"
    )
    assert KNOWLEDGE_REVIEW_DIGEST_ALGORITHM == "sha256"
    assert KNOWLEDGE_REVIEW_RECORD_ID_PREFIX == "kr1_"
    assert {
        REVIEW_DECISION_PASSED,
        REVIEW_DECISION_REJECTED,
        REVIEW_DECISION_DEFERRED,
    } == {"passed", "rejected", "deferred"}


@pytest.mark.parametrize(
    "bad_id",
    (
        "",
        "kr1_" + "A" * 64,
        "kr1_" + "0" * 63,
        "kc1_" + "0" * 64,
        "kr1_" + "g" * 64,
    ),
)
def test_d03_record_id_is_strict_and_must_match_content(bad_id: str) -> None:
    record = _record()
    with pytest.raises(ValueError, match="knowledge_review_record_id"):
        replace(record, knowledge_review_record_id=bad_id)
    other_shaped_id = "kr1_" + "0" * 64
    if other_shaped_id == record.knowledge_review_record_id:
        other_shaped_id = "kr1_" + "1" * 64
    with pytest.raises(ValueError, match="does not match identity"):
        replace(record, knowledge_review_record_id=other_shaped_id)


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("knowledge_candidate_id", "kc1_" + "A" * 64),
        ("knowledge_candidate_id", "kc1_" + "0" * 63),
        ("knowledge_candidate_snapshot_digest", "A" * 64),
        ("knowledge_candidate_snapshot_digest", "0" * 63),
    ),
)
def test_d04_candidate_id_and_snapshot_digest_are_strict(
    field_name: str,
    bad_value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _identity_input(**{field_name: bad_value})


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("knowledge_candidate_contract_version", " "),
        ("reviewed_by", ""),
        ("review_policy_id", " "),
        ("review_policy_version", None),
        ("reviewed_at", datetime(2026, 7, 13, 8, 30)),
        ("reviewed_at", "2026-07-13T08:30:00Z"),
    ),
)
def test_d05_required_strings_and_exact_aware_datetime_fail_closed(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _identity_input(**{field_name: bad_value})

    class DatetimeSubclass(datetime):
        pass

    with pytest.raises(ValueError, match="reviewed_at"):
        _identity_input(
            reviewed_at=DatetimeSubclass(
                2026, 7, 13, 8, 30, tzinfo=timezone.utc
            )
        )


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("reason_codes", []),
        ("reason_codes", ()),
        ("reason_codes", ("same", "same")),
        ("reason_codes", ("z", "a")),
        ("reviewed_evidence_ids", ()),
        ("reviewed_evidence_ids", ("ev1_" + "A" * 64,)),
        ("reviewed_acceptance_record_ids", ()),
        ("reviewed_acceptance_record_ids", ("ar1_" + "A" * 64,)),
        ("reviewed_acceptance_review_record_ids", ()),
        ("reviewed_acceptance_review_record_ids", ("z", "a")),
    ),
)
def test_d06_review_collections_are_exact_nonempty_unique_and_ordered(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _identity_input(**{field_name: bad_value})


@pytest.mark.parametrize(
    "decision",
    (REVIEW_DECISION_PASSED, REVIEW_DECISION_REJECTED, REVIEW_DECISION_DEFERRED),
)
def test_d07_only_exact_review_decisions_are_accepted(decision: str) -> None:
    assert _record(review_decision=decision).review_decision == decision
    with pytest.raises(ValueError, match="unsupported review_decision"):
        _identity_input(review_decision="accepted")


def test_d08_diagnostics_are_exact_immutable_info_or_warning_members() -> None:
    info = KnowledgeReviewDiagnostic("i", "info", "Info", "field", "test")
    warning = KnowledgeReviewDiagnostic(
        "w", "warning", "Warning", "field", "test"
    )
    assert _record(diagnostics=(info, warning)).diagnostics == (info, warning)
    with pytest.raises(ValueError, match="severity"):
        KnowledgeReviewDiagnostic("x", "error", "Bad", "field", "test")
    with pytest.raises(ValueError, match="non-empty string"):
        KnowledgeReviewDiagnostic(" ", "info", "Bad", "field", "test")
    with pytest.raises(ValueError, match="diagnostics"):
        replace(_record(), diagnostics=[info])
    with pytest.raises(ValueError, match="exact KnowledgeReviewDiagnostic"):
        replace(_record(), diagnostics=(object(),))


def test_d09_candidate_snapshot_contains_every_representation_field() -> None:
    diagnostic = KnowledgeDiagnostic(
        "candidate-note", "warning", "Review this", "statement", "constructor"
    )
    candidate = _candidate(diagnostics=(diagnostic,))
    projection = review_module._knowledge_candidate_review_snapshot_projection(
        candidate
    )

    assert set(projection) == {
        "authority_status",
        "conflict_ids",
        "conflict_status",
        "construction_rule_id",
        "construction_rule_version",
        "contract_version",
        "diagnostics",
        "knowledge_candidate_id",
        "lifecycle_status",
        "review_status",
        "snapshot_canonicalization_contract",
        "statement",
        "statement_type",
        "support",
    }
    assert set(projection["support"][0]) == {
        "acceptance_record_ids",
        "acceptance_review_record_ids",
        "evidence_id",
        "locator_schema_version",
        "locator_type",
        "locator_value",
        "payload_digest",
        "source_authority_status",
        "source_content_digest",
        "source_id",
        "source_lifecycle_status",
    }
    assert projection["diagnostics"] == [
        {
            "code": "candidate-note",
            "field": "statement",
            "message": "Review this",
            "severity": "warning",
            "source": "constructor",
        }
    ]

    baseline = compute_knowledge_candidate_review_snapshot_digest(_candidate())
    diagnostic_changed = compute_knowledge_candidate_review_snapshot_digest(
        candidate
    )
    provenance_changed = compute_knowledge_candidate_review_snapshot_digest(
        _candidate(
            support=(
                _support(
                    source_authority_status="reference",
                    source_lifecycle_status="superseded",
                    acceptance_review_record_ids=("review-2",),
                ),
            )
        )
    )
    assert len({baseline, diagnostic_changed, provenance_changed}) == 3


def test_d10_candidate_snapshot_is_canonical_utf8_nfc_and_nonmutating() -> None:
    decomposed = "Cafe\u0301 fact"
    composed = "Caf\u00e9 fact"
    decomposed_candidate = _candidate(statement=decomposed)
    composed_candidate = _candidate(statement=composed)
    before = repr(decomposed_candidate)
    snapshot_bytes = review_module._canonical_knowledge_candidate_review_snapshot_bytes(
        decomposed_candidate
    )
    decoded = snapshot_bytes.decode("utf-8")

    assert compute_knowledge_candidate_review_snapshot_digest(
        decomposed_candidate
    ) == compute_knowledge_candidate_review_snapshot_digest(composed_candidate)
    assert hashlib.sha256(snapshot_bytes).hexdigest() == (
        compute_knowledge_candidate_review_snapshot_digest(decomposed_candidate)
    )
    assert '"snapshot_canonicalization_contract":' in decoded
    assert ": " not in decoded
    assert ", " not in decoded
    assert json.loads(decoded)["statement"] == composed
    assert repr(decomposed_candidate) == before
    with pytest.raises(ValueError, match="finite floats"):
        review_module._canonicalize(float("nan"))


def test_d11_review_identity_is_canonical_stable_and_sha256_shaped() -> None:
    identity_input = _identity_input()
    canonical_bytes = canonical_knowledge_review_identity_bytes(identity_input)
    record_id = compute_knowledge_review_record_id(identity_input)
    projection = json.loads(canonical_bytes.decode("utf-8"))

    assert record_id == "kr1_" + hashlib.sha256(canonical_bytes).hexdigest()
    assert record_id == compute_knowledge_review_record_id(identity_input)
    assert projection["reviewed_at"] == "2026-07-13T08:30:15.123456Z"
    assert projection["identity_canonicalization_contract"] == (
        KNOWLEDGE_REVIEW_IDENTITY_CANONICALIZATION_CONTRACT
    )
    offset_input = replace(
        identity_input,
        reviewed_at=FIXED_TIME.astimezone(timezone(timedelta(hours=7))),
    )
    assert compute_knowledge_review_record_id(offset_input) == record_id


@pytest.mark.parametrize(
    "changes",
    (
        {"knowledge_candidate_snapshot_digest": "9" * 64},
        {"review_decision": REVIEW_DECISION_REJECTED},
        {"reason_codes": ("other",)},
        {"reviewed_evidence_ids": ("ev1_" + "8" * 64,)},
        {"reviewed_acceptance_record_ids": ("ar1_" + "8" * 64,)},
        {"reviewed_acceptance_review_record_ids": ("review-2",)},
        {"reviewed_by": "reviewer-2"},
        {"reviewed_at": FIXED_TIME + timedelta(seconds=1)},
        {"review_policy_id": "other-policy"},
        {"review_policy_version": "2.0.0"},
    ),
)
def test_d12_material_review_event_changes_alter_record_identity(
    changes: dict[str, object],
) -> None:
    assert compute_knowledge_review_record_id(_identity_input()) != (
        compute_knowledge_review_record_id(_identity_input(**changes))
    )


def test_d13_diagnostics_and_future_metadata_are_outside_identity() -> None:
    diagnostic = KnowledgeReviewDiagnostic(
        "note", "info", "Not identity", "review_decision", "test"
    )
    assert _record().knowledge_review_record_id == (
        _record(diagnostics=(diagnostic,)).knowledge_review_record_id
    )
    canonical_text = canonical_knowledge_review_identity_bytes(
        _identity_input()
    ).decode("utf-8")
    for forbidden in (
        "diagnostics",
        "source_path",
        "repository",
        "promotion",
        "governed_knowledge_id",
        "persistence",
    ):
        assert forbidden not in canonical_text


def test_d14_snapshot_identity_and_record_helpers_reject_duck_types() -> None:
    class DuckCandidate:
        pass

    class DuckIdentity:
        pass

    class DuckRecord:
        pass

    with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
        compute_knowledge_candidate_review_snapshot_digest(DuckCandidate())
    with pytest.raises(ValueError, match="exact KnowledgeReviewIdentityInput"):
        canonical_knowledge_review_identity_bytes(DuckIdentity())
    with pytest.raises(ValueError, match="exact KnowledgeReviewRecord"):
        knowledge_review_identity_input_from_record(DuckRecord())


def test_d15_identity_extraction_round_trips_exactly() -> None:
    record = _record()
    assert knowledge_review_identity_input_from_record(record) == _identity_input()
