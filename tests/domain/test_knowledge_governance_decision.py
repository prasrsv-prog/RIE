from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

import rie.domain.knowledge_governance_decision as governance_module
from rie.domain.knowledge_governance_decision import (
    AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION,
    GOVERNANCE_DECISION_AUTHORIZED,
    GOVERNANCE_DECISION_DEFERRED,
    GOVERNANCE_DECISION_DENIED,
    KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION,
    KNOWLEDGE_GOVERNANCE_DECISION_ID_PREFIX,
    KNOWLEDGE_GOVERNANCE_DIGEST_ALGORITHM,
    KNOWLEDGE_GOVERNANCE_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_ID,
    KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_VERSION,
    KnowledgeGovernanceDecision,
    KnowledgeGovernanceDiagnostic,
    KnowledgeGovernanceIdentityInput,
    canonical_knowledge_governance_identity_bytes,
    canonical_knowledge_governance_identity_projection,
    compute_knowledge_governance_candidate_snapshot_digest,
    compute_knowledge_governance_decision_id,
    knowledge_governance_identity_input_from_record,
    verify_knowledge_review_record_identity,
)


FIXED_TIME = datetime(2026, 7, 13, 10, 30, 45, 123456, tzinfo=timezone.utc)
CANDIDATE_ID = "kc1_" + "1" * 64
REVIEW_ID_1 = "kr1_" + "2" * 64
REVIEW_ID_2 = "kr1_" + "3" * 64


def _identity_input(**changes: object) -> KnowledgeGovernanceIdentityInput:
    values: dict[str, object] = {
        "governance_decision_contract_version": (
            KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        ),
        "knowledge_candidate_id": CANDIDATE_ID,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "4" * 64,
        "knowledge_review_record_ids": (REVIEW_ID_1,),
        "authorization_scope": (
            AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        ),
        "governance_decision": GOVERNANCE_DECISION_AUTHORIZED,
        "reason_codes": ("eligible_review_evidence",),
        "decided_by": "governance-actor",
        "decided_at": FIXED_TIME,
        "governance_policy_id": "rcis-knowledge-governance-authorization",
        "governance_policy_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgeGovernanceIdentityInput(**values)


def _record(
    *,
    identity_input: KnowledgeGovernanceIdentityInput | None = None,
    diagnostics: tuple[KnowledgeGovernanceDiagnostic, ...] = (),
    record_id: str | None = None,
) -> KnowledgeGovernanceDecision:
    value = identity_input or _identity_input()
    return KnowledgeGovernanceDecision(
        knowledge_governance_decision_id=(
            compute_knowledge_governance_decision_id(value)
            if record_id is None
            else record_id
        ),
        contract_version=value.governance_decision_contract_version,
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            value.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            value.knowledge_candidate_snapshot_digest
        ),
        knowledge_review_record_ids=value.knowledge_review_record_ids,
        authorization_scope=value.authorization_scope,
        governance_decision=value.governance_decision,
        reason_codes=value.reason_codes,
        decided_by=value.decided_by,
        decided_at=value.decided_at,
        governance_policy_id=value.governance_policy_id,
        governance_policy_version=value.governance_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_contracts_are_frozen_value_equal_and_explicitly_identified() -> None:
    diagnostic = KnowledgeGovernanceDiagnostic(
        "reviewed", "info", "Recorded", "request", "test"
    )
    identity_input = _identity_input()
    record = _record(diagnostics=(diagnostic,))

    assert record == _record(diagnostics=(diagnostic,))
    assert record.knowledge_governance_decision_id.startswith("kg1_")
    with pytest.raises(FrozenInstanceError):
        diagnostic.code = "changed"
    with pytest.raises(FrozenInstanceError):
        identity_input.decided_by = "changed"
    with pytest.raises(FrozenInstanceError):
        record.governance_decision = GOVERNANCE_DECISION_DENIED


def test_d02_domain_constants_are_exact() -> None:
    assert (
        KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        == "knowledge-governance-decision-v1"
    )
    assert KNOWLEDGE_GOVERNANCE_DECISION_ID_PREFIX == "kg1_"
    assert (
        KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_ID
        == "rcis-knowledge-governance-decision-identity"
    )
    assert KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_VERSION == "1.0.0"
    assert (
        KNOWLEDGE_GOVERNANCE_IDENTITY_CANONICALIZATION_CONTRACT
        == "knowledge-governance-decision-json-v1"
    )
    assert KNOWLEDGE_GOVERNANCE_DIGEST_ALGORITHM == "sha256"
    assert (
        AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        == "eligible_for_future_promotion_evaluation"
    )
    assert {
        GOVERNANCE_DECISION_AUTHORIZED,
        GOVERNANCE_DECISION_DENIED,
        GOVERNANCE_DECISION_DEFERRED,
    } == {"authorized", "denied", "deferred"}


@pytest.mark.parametrize(
    "bad_id",
    (
        "",
        "kg1_" + "a" * 63,
        "kg1_" + "A" * 64,
        "kr1_" + "a" * 64,
    ),
)
def test_d03_decision_id_is_strict_and_matches_canonical_content(
    bad_id: str,
) -> None:
    with pytest.raises(ValueError, match="invalid format|non-empty"):
        _record(record_id=bad_id)
    with pytest.raises(ValueError, match="does not match identity"):
        _record(record_id="kg1_" + "0" * 64)


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    (
        ("knowledge_candidate_id", "kc1_" + "A" * 64),
        ("knowledge_candidate_id", "kc1_" + "1" * 63),
        ("knowledge_candidate_contract_version", " "),
        ("knowledge_candidate_snapshot_digest", "a" * 63),
        ("knowledge_candidate_snapshot_digest", "A" * 64),
    ),
)
def test_d04_candidate_identity_and_snapshot_are_strict(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError):
        _identity_input(**{field_name: bad_value})


@pytest.mark.parametrize(
    "bad_ids",
    (
        [],
        (),
        ("kr1_" + "A" * 64,),
        (REVIEW_ID_1, REVIEW_ID_1),
        (REVIEW_ID_2, REVIEW_ID_1),
    ),
)
def test_d05_review_record_ids_are_exact_nonempty_unique_and_ordered(
    bad_ids: object,
) -> None:
    with pytest.raises(ValueError):
        _identity_input(knowledge_review_record_ids=bad_ids)


def test_d06_authorization_scope_is_exact() -> None:
    assert (
        _identity_input().authorization_scope
        == "eligible_for_future_promotion_evaluation"
    )
    with pytest.raises(ValueError, match="unsupported authorization_scope"):
        _identity_input(authorization_scope="promote")


@pytest.mark.parametrize(
    "decision",
    (
        GOVERNANCE_DECISION_AUTHORIZED,
        GOVERNANCE_DECISION_DENIED,
        GOVERNANCE_DECISION_DEFERRED,
    ),
)
def test_d07_only_exact_governance_decisions_are_accepted(
    decision: str,
) -> None:
    assert _identity_input(governance_decision=decision).governance_decision == decision
    with pytest.raises(ValueError, match="unsupported governance_decision"):
        _identity_input(governance_decision="accepted")


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    (
        ("decided_by", " "),
        ("governance_policy_id", ""),
        ("governance_policy_version", 1),
        ("reason_codes", []),
        ("reason_codes", ()),
        ("reason_codes", ("reason", "reason")),
        ("reason_codes", ("z_reason", "a_reason")),
        ("decided_at", datetime(2026, 7, 13, 10, 30)),
        ("decided_at", "2026-07-13T10:30:00Z"),
    ),
)
def test_d08_required_strings_reasons_and_aware_time_fail_closed(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError):
        _identity_input(**{field_name: bad_value})


def test_d09_diagnostics_are_exact_immutable_and_outside_identity() -> None:
    info = KnowledgeGovernanceDiagnostic(
        "note", "info", "Info", "request", "test"
    )
    warning = KnowledgeGovernanceDiagnostic(
        "note", "warning", "Warning", "request", "test"
    )
    plain = _record()
    with_diagnostics = _record(diagnostics=(info, warning))

    assert plain.knowledge_governance_decision_id == (
        with_diagnostics.knowledge_governance_decision_id
    )
    assert plain != with_diagnostics
    with pytest.raises(ValueError, match="severity"):
        KnowledgeGovernanceDiagnostic("x", "error", "x", "x", "x")
    with pytest.raises(ValueError, match="diagnostics must be a tuple"):
        replace(plain, diagnostics=[info])
    with pytest.raises(ValueError, match="exact KnowledgeGovernanceDiagnostic"):
        replace(plain, diagnostics=(object(),))


def test_d10_canonical_identity_is_utf8_nfc_sorted_compact_utc_and_sha256() -> None:
    identity_input = _identity_input(
        decided_by="Cafe\u0301",
        decided_at=datetime(
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
    canonical_bytes = canonical_knowledge_governance_identity_bytes(
        identity_input
    )
    projection = json.loads(canonical_bytes.decode("utf-8"))

    assert projection["decided_by"] == "Caf\u00e9"
    assert projection["decided_at"] == "2026-07-13T10:30:45.123456Z"
    assert projection["identity_canonicalization_contract"] == (
        "knowledge-governance-decision-json-v1"
    )
    assert b": " not in canonical_bytes
    assert canonical_bytes == json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert compute_knowledge_governance_decision_id(identity_input) == (
        "kg1_" + hashlib.sha256(canonical_bytes).hexdigest()
    )


def test_d11_exact_replay_returns_identical_bytes_and_identity() -> None:
    first = _identity_input()
    second = _identity_input()
    assert canonical_knowledge_governance_identity_bytes(first) == (
        canonical_knowledge_governance_identity_bytes(second)
    )
    assert compute_knowledge_governance_decision_id(first) == (
        compute_knowledge_governance_decision_id(second)
    )
    assert _record(identity_input=first) == _record(identity_input=second)


@pytest.mark.parametrize(
    "changes",
    (
        {"knowledge_candidate_id": "kc1_" + "9" * 64},
        {"knowledge_candidate_contract_version": "knowledge-candidate-v2"},
        {"knowledge_candidate_snapshot_digest": "9" * 64},
        {"knowledge_review_record_ids": (REVIEW_ID_2,)},
        {"governance_decision": GOVERNANCE_DECISION_DENIED},
        {"reason_codes": ("other_reason",)},
        {"decided_by": "other-actor"},
        {"decided_at": FIXED_TIME + timedelta(seconds=1)},
        {"governance_policy_id": "other-policy"},
        {"governance_policy_version": "2.0.0"},
    ),
)
def test_d12_material_identity_field_changes_change_identity(
    changes: dict[str, object],
) -> None:
    assert compute_knowledge_governance_decision_id(_identity_input()) != (
        compute_knowledge_governance_decision_id(_identity_input(**changes))
    )

    scope_changed = _identity_input()
    object.__setattr__(scope_changed, "authorization_scope", "other_scope")
    contract_changed = _identity_input()
    object.__setattr__(
        contract_changed,
        "governance_decision_contract_version",
        "knowledge-governance-decision-v2",
    )
    baseline = compute_knowledge_governance_decision_id(_identity_input())
    assert compute_knowledge_governance_decision_id(scope_changed) != baseline
    assert compute_knowledge_governance_decision_id(contract_changed) != baseline


def test_d13_forbidden_future_metadata_is_absent_from_identity() -> None:
    canonical_text = canonical_knowledge_governance_identity_bytes(
        _identity_input()
    ).decode("utf-8")
    for forbidden in (
        "diagnostics",
        "source_path",
        "raw_asset",
        "repository_location",
        "list_position",
        "current_time",
        "random",
        "uuid",
        "conflict_result",
        "authority_result",
        "lifecycle_result",
        "promotion_metadata",
        "governed_knowledge_id",
        "persistence_metadata",
        "acceptance_metadata",
    ):
        assert forbidden not in canonical_text


def test_d14_identity_snapshot_and_review_helpers_reject_duck_types() -> None:
    class DuckIdentity:
        governance_decision_contract_version = (
            KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        )

    class DuckCandidate:
        knowledge_candidate_id = CANDIDATE_ID

    class DuckReview:
        knowledge_review_record_id = REVIEW_ID_1

    class DuckRecord:
        knowledge_governance_decision_id = "kg1_" + "5" * 64

    with pytest.raises(ValueError, match="exact KnowledgeGovernanceIdentityInput"):
        canonical_knowledge_governance_identity_projection(DuckIdentity())
    with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
        compute_knowledge_governance_candidate_snapshot_digest(DuckCandidate())
    with pytest.raises(ValueError, match="exact KnowledgeReviewRecord"):
        verify_knowledge_review_record_identity(DuckReview())
    with pytest.raises(ValueError, match="exact KnowledgeGovernanceDecision"):
        knowledge_governance_identity_input_from_record(DuckRecord())
    with pytest.raises(ValueError, match="finite"):
        governance_module._canonicalize(float("nan"))


def test_d15_identity_extraction_from_record_round_trips_exactly() -> None:
    identity_input = _identity_input()
    record = _record(identity_input=identity_input)
    assert knowledge_governance_identity_input_from_record(record) == identity_input
    assert compute_knowledge_governance_decision_id(
        knowledge_governance_identity_input_from_record(record)
    ) == record.knowledge_governance_decision_id
