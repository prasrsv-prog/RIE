from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from rie.domain.knowledge_conflict_assessment_record import (
    ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
    ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
    ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
    ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP,
    KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_ID_PREFIX,
    KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_CONFLICT_DIGEST_ALGORITHM,
    KNOWLEDGE_CONFLICT_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_CONFLICT_IDENTITY_POLICY_ID,
    KNOWLEDGE_CONFLICT_IDENTITY_POLICY_VERSION,
    KnowledgeConflictAssessmentRecord,
    KnowledgeConflictDiagnostic,
    KnowledgeConflictIdentityInput,
    KnowledgeConflictParticipant,
    canonical_knowledge_conflict_identity_bytes,
    canonical_knowledge_conflict_identity_projection,
    compute_knowledge_conflict_assessment_record_id,
    compute_knowledge_conflict_candidate_snapshot_digest,
    knowledge_conflict_identity_input_from_record,
    knowledge_conflict_participant_from_candidate,
    verify_knowledge_conflict_candidate_identity,
)


FIXED_TIME = datetime(2026, 7, 13, 10, 30, 45, 123456, tzinfo=timezone.utc)
CANDIDATE_ID_1 = "kc1_" + "1" * 64
CANDIDATE_ID_2 = "kc1_" + "2" * 64


def _participant(
    candidate_id: str = CANDIDATE_ID_1,
    *,
    contract_version: str = "knowledge-candidate-v1",
    snapshot_digest: str = "3" * 64,
) -> KnowledgeConflictParticipant:
    return KnowledgeConflictParticipant(
        knowledge_candidate_id=candidate_id,
        knowledge_candidate_contract_version=contract_version,
        knowledge_candidate_snapshot_digest=snapshot_digest,
    )


def _participants() -> tuple[KnowledgeConflictParticipant, ...]:
    return (
        _participant(CANDIDATE_ID_1, snapshot_digest="3" * 64),
        _participant(CANDIDATE_ID_2, snapshot_digest="4" * 64),
    )


def _identity_input(**changes: object) -> KnowledgeConflictIdentityInput:
    values: dict[str, object] = {
        "conflict_assessment_record_contract_version": (
            KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION
        ),
        "participants": _participants(),
        "assessment_scope": (
            ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
        ),
        "assessment_outcome": ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
        "reason_codes": ("semantic_conflict_identified",),
        "assessed_by": "conflict-assessor",
        "assessed_at": FIXED_TIME,
        "assessment_policy_id": (
            "rcis-knowledge-pairwise-conflict-assessment"
        ),
        "assessment_policy_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgeConflictIdentityInput(**values)


def _record(
    *,
    identity_input: KnowledgeConflictIdentityInput | None = None,
    diagnostics: tuple[KnowledgeConflictDiagnostic, ...] = (),
    record_id: str | None = None,
) -> KnowledgeConflictAssessmentRecord:
    value = identity_input or _identity_input()
    return KnowledgeConflictAssessmentRecord(
        knowledge_conflict_assessment_record_id=(
            compute_knowledge_conflict_assessment_record_id(value)
            if record_id is None
            else record_id
        ),
        contract_version=(
            value.conflict_assessment_record_contract_version
        ),
        participants=value.participants,
        assessment_scope=value.assessment_scope,
        assessment_outcome=value.assessment_outcome,
        reason_codes=value.reason_codes,
        assessed_by=value.assessed_by,
        assessed_at=value.assessed_at,
        assessment_policy_id=value.assessment_policy_id,
        assessment_policy_version=value.assessment_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_contracts_are_frozen_value_equal_and_explicitly_identified() -> None:
    diagnostic = KnowledgeConflictDiagnostic(
        "recorded", "info", "Recorded", "request", "test"
    )
    participant = _participant()
    identity_input = _identity_input()
    record = _record(diagnostics=(diagnostic,))

    assert diagnostic == KnowledgeConflictDiagnostic(
        "recorded", "info", "Recorded", "request", "test"
    )
    assert participant == _participant()
    assert identity_input == _identity_input()
    assert record == _record(diagnostics=(diagnostic,))
    assert record.knowledge_conflict_assessment_record_id.startswith("kcf1_")
    for instance, field_name in (
        (diagnostic, "code"),
        (participant, "knowledge_candidate_id"),
        (identity_input, "assessed_by"),
        (record, "assessment_outcome"),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, field_name, "changed")


def test_d02_domain_constants_are_exact() -> None:
    assert KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION == (
        "knowledge-conflict-assessment-record-v1"
    )
    assert KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_ID_PREFIX == "kcf1_"
    assert KNOWLEDGE_CONFLICT_IDENTITY_POLICY_ID == (
        "rcis-knowledge-conflict-assessment-record-identity"
    )
    assert KNOWLEDGE_CONFLICT_IDENTITY_POLICY_VERSION == "1.0.0"
    assert KNOWLEDGE_CONFLICT_IDENTITY_CANONICALIZATION_CONTRACT == (
        "knowledge-conflict-assessment-record-json-v1"
    )
    assert KNOWLEDGE_CONFLICT_DIGEST_ALGORITHM == "sha256"
    assert (
        ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
        == "pairwise_knowledge_candidate_semantic_relationship"
    )
    assert {
        ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    } == {
        "conflict_identified",
        "equivalent_statement",
        "no_conflict_identified",
        "assessment_deferred",
    }
    assert {
        KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_WARNING,
    } == {"info", "warning"}


def test_d03_record_id_is_strict_and_matches_canonical_content() -> None:
    for bad_id in (
        "",
        "kcf1_" + "a" * 63,
        "kcf1_" + "A" * 64,
        "kg1_" + "a" * 64,
    ):
        with pytest.raises(ValueError, match="invalid format|non-empty"):
            _record(record_id=bad_id)
    with pytest.raises(ValueError, match="does not match identity"):
        _record(record_id="kcf1_" + "0" * 64)


def test_d04_participant_requires_candidate_identity_contract_and_snapshot() -> None:
    assert _participant().knowledge_candidate_id == CANDIDATE_ID_1
    invalid = (
        {"candidate_id": "kc1_" + "A" * 64},
        {"candidate_id": "kc1_" + "1" * 63},
        {"contract_version": " "},
        {"snapshot_digest": "a" * 63},
        {"snapshot_digest": "A" * 64},
    )
    for changes in invalid:
        with pytest.raises(ValueError):
            _participant(**changes)


def test_d05_participants_are_exact_pair_unique_and_ordered() -> None:
    first, second = _participants()
    for bad_value in (
        [],
        (),
        (first,),
        (first, second, _participant("kc1_" + "5" * 64)),
        (first, first),
        (second, first),
        (first, object()),
    ):
        with pytest.raises(ValueError, match="participants"):
            _identity_input(participants=bad_value)


def test_d06_scope_is_exactly_pairwise_semantic_relationship() -> None:
    assert _record().assessment_scope == (
        "pairwise_knowledge_candidate_semantic_relationship"
    )
    with pytest.raises(ValueError, match="assessment_scope"):
        _identity_input(assessment_scope="global_semantic_relationship")


def test_d07_only_four_assessment_outcomes_are_recordable() -> None:
    outcomes = (
        ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    )
    for outcome in outcomes:
        assert _record(
            identity_input=_identity_input(assessment_outcome=outcome)
        ).assessment_outcome == outcome
    with pytest.raises(ValueError, match="assessment_outcome"):
        _identity_input(assessment_outcome="resolved")


def test_d08_required_strings_reasons_policy_and_aware_time_fail_closed() -> None:
    invalid = (
        ("assessed_by", " "),
        ("assessment_policy_id", ""),
        ("assessment_policy_version", 1),
        ("reason_codes", []),
        ("reason_codes", ()),
        ("reason_codes", ("reason", "reason")),
        ("reason_codes", ("z_reason", "a_reason")),
        ("assessed_at", datetime(2026, 7, 13, 10, 30)),
        ("assessed_at", "2026-07-13T10:30:00Z"),
    )
    for field_name, bad_value in invalid:
        with pytest.raises(ValueError):
            _identity_input(**{field_name: bad_value})


def test_d09_diagnostics_are_exact_immutable_and_outside_identity() -> None:
    info = KnowledgeConflictDiagnostic(
        "note", "info", "Info", "request", "test"
    )
    warning = KnowledgeConflictDiagnostic(
        "note", "warning", "Warning", "request", "test"
    )
    plain = _record()
    diagnosed = _record(diagnostics=(info, warning))
    assert plain.knowledge_conflict_assessment_record_id == (
        diagnosed.knowledge_conflict_assessment_record_id
    )
    assert plain != diagnosed
    with pytest.raises(ValueError, match="severity"):
        KnowledgeConflictDiagnostic("x", "error", "x", "x", "x")
    with pytest.raises(ValueError, match="diagnostics must be a tuple"):
        replace(plain, diagnostics=[info])
    with pytest.raises(ValueError, match="exact KnowledgeConflictDiagnostic"):
        replace(plain, diagnostics=(object(),))


def test_d10_canonical_identity_is_utf8_nfc_sorted_compact_utc_and_sha256() -> None:
    identity_input = _identity_input(
        assessed_by="Cafe\u0301",
        assessed_at=datetime(
            2026,
            7,
            13,
            17,
            30,
            45,
            123456,
            tzinfo=timezone(timedelta(hours=7)),
        ),
    )
    canonical_bytes = canonical_knowledge_conflict_identity_bytes(
        identity_input
    )
    projection = json.loads(canonical_bytes.decode("utf-8"))
    assert projection["assessed_by"] == "Caf\u00e9"
    assert projection["assessed_at"] == "2026-07-13T10:30:45.123456Z"
    assert projection["identity_canonicalization_contract"] == (
        "knowledge-conflict-assessment-record-json-v1"
    )
    assert b": " not in canonical_bytes
    assert canonical_bytes == json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert compute_knowledge_conflict_assessment_record_id(identity_input) == (
        "kcf1_" + hashlib.sha256(canonical_bytes).hexdigest()
    )


def test_d11_exact_replay_returns_identical_bytes_and_identity() -> None:
    first = _identity_input()
    second = _identity_input()
    assert canonical_knowledge_conflict_identity_bytes(first) == (
        canonical_knowledge_conflict_identity_bytes(second)
    )
    assert compute_knowledge_conflict_assessment_record_id(first) == (
        compute_knowledge_conflict_assessment_record_id(second)
    )
    assert _record(identity_input=first) == _record(identity_input=second)


def test_d12_every_material_identity_field_change_changes_identity() -> None:
    baseline = compute_knowledge_conflict_assessment_record_id(_identity_input())
    changes = (
        {"participants": (
            _participant(CANDIDATE_ID_1, snapshot_digest="5" * 64),
            _participant(CANDIDATE_ID_2, snapshot_digest="4" * 64),
        )},
        {"assessment_outcome": ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT},
        {"reason_codes": ("other_reason",)},
        {"assessed_by": "other-actor"},
        {"assessed_at": FIXED_TIME + timedelta(seconds=1)},
        {"assessment_policy_id": "other-policy"},
        {"assessment_policy_version": "2.0.0"},
    )
    for change in changes:
        assert compute_knowledge_conflict_assessment_record_id(
            _identity_input(**change)
        ) != baseline

    scope_changed = _identity_input()
    object.__setattr__(scope_changed, "assessment_scope", "other_scope")
    contract_changed = _identity_input()
    object.__setattr__(
        contract_changed,
        "conflict_assessment_record_contract_version",
        "knowledge-conflict-assessment-record-v2",
    )
    assert compute_knowledge_conflict_assessment_record_id(scope_changed) != baseline
    assert compute_knowledge_conflict_assessment_record_id(contract_changed) != baseline


def test_d13_forbidden_downstream_metadata_is_absent_from_identity() -> None:
    canonical_text = canonical_knowledge_conflict_identity_bytes(
        _identity_input()
    ).decode("utf-8")
    for forbidden in (
        "diagnostics",
        "statement",
        "knowledge_review_record_id",
        "knowledge_governance_decision_id",
        "authority",
        "lifecycle",
        "resolution",
        "winner",
        "source_path",
        "repository",
        "list_position",
        "random",
        "uuid",
        "promotion",
        "acceptance",
        "governed_knowledge",
        "supersession",
        "invalidation",
        "persistence",
    ):
        assert forbidden not in canonical_text


def test_d14_snapshot_identity_participant_and_record_helpers_reject_ducks() -> None:
    class DuckIdentity:
        participants = _participants()

    class DuckCandidate:
        knowledge_candidate_id = CANDIDATE_ID_1

    class DuckRecord:
        contract_version = KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION

    for helper, value in (
        (canonical_knowledge_conflict_identity_projection, DuckIdentity()),
        (canonical_knowledge_conflict_identity_bytes, object()),
        (compute_knowledge_conflict_assessment_record_id, DuckIdentity()),
        (verify_knowledge_conflict_candidate_identity, DuckCandidate()),
        (compute_knowledge_conflict_candidate_snapshot_digest, object()),
        (knowledge_conflict_participant_from_candidate, DuckCandidate()),
        (knowledge_conflict_identity_input_from_record, DuckRecord()),
    ):
        with pytest.raises(ValueError, match="exact"):
            helper(value)


def test_d15_identity_extraction_from_record_round_trips_exactly() -> None:
    identity_input = _identity_input()
    record = _record(identity_input=identity_input)
    extracted = knowledge_conflict_identity_input_from_record(record)
    assert extracted == identity_input
    assert canonical_knowledge_conflict_identity_bytes(extracted) == (
        canonical_knowledge_conflict_identity_bytes(identity_input)
    )
    assert compute_knowledge_conflict_assessment_record_id(extracted) == (
        record.knowledge_conflict_assessment_record_id
    )
