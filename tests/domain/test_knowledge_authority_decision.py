from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import unicodedata

import pytest

from rie.domain.knowledge_authority_decision import (
    AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
    AUTHORITY_DECISION_OUTCOME_DEFERRED,
    AUTHORITY_DECISION_OUTCOME_DENIED,
    AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY,
    INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION,
    KNOWLEDGE_AUTHORITY_DECISION_ID_PREFIX,
    KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_AUTHORITY_DIGEST_ALGORITHM,
    KNOWLEDGE_AUTHORITY_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_ID,
    KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_VERSION,
    KnowledgeAuthorityDecision,
    KnowledgeAuthorityDiagnostic,
    KnowledgeAuthorityIdentityInput,
    canonical_knowledge_authority_identity_bytes,
    canonical_knowledge_authority_identity_projection,
    compute_knowledge_authority_candidate_snapshot_digest,
    compute_knowledge_authority_decision_id,
    knowledge_authority_identity_input_from_record,
    verify_knowledge_authority_candidate_identity,
    verify_knowledge_authority_governance_decision_identity,
)


FIXED_TIME = datetime(2026, 7, 13, 14, 30, 45, 123456, tzinfo=timezone.utc)


def _identity(**changes: object) -> KnowledgeAuthorityIdentityInput:
    values: dict[str, object] = {
        "authority_decision_record_contract_version": (
            KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION
        ),
        "knowledge_candidate_id": "kc1_" + "1" * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "2" * 64,
        "knowledge_governance_decision_ids": ("kg1_" + "3" * 64,),
        "authority_scope": (
            AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY
        ),
        "intended_authority_value": (
            INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE
        ),
        "decision_outcome": AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
        "reason_codes": ("intended_knowledge_authority_authorized",),
        "decided_by": "authority-actor",
        "decided_at": FIXED_TIME,
        "authority_policy_id": "rcis-knowledge-authority-decision",
        "authority_policy_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgeAuthorityIdentityInput(**values)  # type: ignore[arg-type]


def _record(
    identity: KnowledgeAuthorityIdentityInput | None = None,
    *,
    diagnostics: tuple[KnowledgeAuthorityDiagnostic, ...] = (),
    record_id: str | None = None,
) -> KnowledgeAuthorityDecision:
    selected = identity or _identity()
    return KnowledgeAuthorityDecision(
        knowledge_authority_decision_id=(
            record_id or compute_knowledge_authority_decision_id(selected)
        ),
        contract_version=(
            selected.authority_decision_record_contract_version
        ),
        knowledge_candidate_id=selected.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            selected.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            selected.knowledge_candidate_snapshot_digest
        ),
        knowledge_governance_decision_ids=(
            selected.knowledge_governance_decision_ids
        ),
        authority_scope=selected.authority_scope,
        intended_authority_value=selected.intended_authority_value,
        decision_outcome=selected.decision_outcome,
        reason_codes=selected.reason_codes,
        decided_by=selected.decided_by,
        decided_at=selected.decided_at,
        authority_policy_id=selected.authority_policy_id,
        authority_policy_version=selected.authority_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_contracts_are_frozen_value_equal_and_explicitly_identified() -> None:
    diagnostic = KnowledgeAuthorityDiagnostic(
        code="note", severity="info", message="message", field="field", source="test"
    )
    identity = _identity()
    record = _record(identity, diagnostics=(diagnostic,))
    assert diagnostic == replace(diagnostic)
    assert identity == replace(identity)
    assert record == replace(record)
    assert record.knowledge_authority_decision_id.startswith("ka1_")
    for value, field in ((diagnostic, "code"), (identity, "decided_by"), (record, "decided_by")):
        with pytest.raises(FrozenInstanceError):
            setattr(value, field, "changed")


def test_d02_domain_constants_are_exact() -> None:
    assert KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION == "knowledge-authority-decision-v1"
    assert KNOWLEDGE_AUTHORITY_DECISION_ID_PREFIX == "ka1_"
    assert KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_ID == "rcis-knowledge-authority-decision-identity"
    assert KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_VERSION == "1.0.0"
    assert KNOWLEDGE_AUTHORITY_IDENTITY_CANONICALIZATION_CONTRACT == "knowledge-authority-decision-json-v1"
    assert KNOWLEDGE_AUTHORITY_DIGEST_ALGORITHM == "sha256"
    assert AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY == "intended_future_governed_knowledge_authority"
    assert INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE == "authoritative_for_governed_knowledge"
    assert INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE == "non_authoritative_for_governed_knowledge"
    assert {AUTHORITY_DECISION_OUTCOME_AUTHORIZED, AUTHORITY_DECISION_OUTCOME_DENIED, AUTHORITY_DECISION_OUTCOME_DEFERRED} == {
        "authority_value_authorized", "authority_value_denied", "authority_value_deferred"
    }
    assert {KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_INFO, KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING} == {"info", "warning"}


def test_d03_record_id_is_strict_and_matches_canonical_content() -> None:
    identity = _identity()
    expected = "ka1_" + hashlib.sha256(
        canonical_knowledge_authority_identity_bytes(identity)
    ).hexdigest()
    assert compute_knowledge_authority_decision_id(identity) == expected
    assert _record(identity).knowledge_authority_decision_id == expected
    for bad_id in ("ka1_" + "A" * 64, "ka1_" + "1" * 63, "kg1_" + "1" * 64):
        with pytest.raises(ValueError):
            _record(identity, record_id=bad_id)
    with pytest.raises(ValueError, match="does not match identity"):
        _record(identity, record_id="ka1_" + "f" * 64)


def test_d04_candidate_identity_contract_and_snapshot_are_strict() -> None:
    for changes in (
        {"knowledge_candidate_id": "kc1_" + "A" * 64},
        {"knowledge_candidate_contract_version": " "},
        {"knowledge_candidate_snapshot_digest": "g" * 64},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d05_governance_ids_are_exact_nonempty_unique_and_ordered() -> None:
    first = "kg1_" + "1" * 64
    second = "kg1_" + "2" * 64
    assert _identity(knowledge_governance_decision_ids=(first, second)).knowledge_governance_decision_ids == (first, second)
    for value in ([], (), (first, first), (second, first), ("kg1_" + "A" * 64,)):
        with pytest.raises(ValueError):
            _identity(knowledge_governance_decision_ids=value)


def test_d06_authority_scope_and_both_values_are_exact() -> None:
    for value in (
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    ):
        assert _identity(intended_authority_value=value).intended_authority_value == value
    with pytest.raises(ValueError):
        _identity(authority_scope="source_authority")
    with pytest.raises(ValueError):
        _identity(intended_authority_value="official")


def test_d07_only_three_authority_decision_outcomes_are_recordable() -> None:
    for outcome in (
        AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
        AUTHORITY_DECISION_OUTCOME_DENIED,
        AUTHORITY_DECISION_OUTCOME_DEFERRED,
    ):
        assert _identity(decision_outcome=outcome).decision_outcome == outcome
    with pytest.raises(ValueError):
        _identity(decision_outcome="promoted")


def test_d08_required_strings_reasons_policy_and_aware_time_fail_closed() -> None:
    for changes in (
        {"decided_by": " "},
        {"authority_policy_id": ""},
        {"authority_policy_version": 1},
        {"reason_codes": []},
        {"reason_codes": ()},
        {"reason_codes": ("reason", "reason")},
        {"reason_codes": ("z", "a")},
        {"decided_at": datetime(2026, 7, 13)},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d09_diagnostics_are_exact_immutable_and_outside_identity() -> None:
    info = KnowledgeAuthorityDiagnostic("info-code", "info", "message", "field", "test")
    warning = KnowledgeAuthorityDiagnostic("warning-code", "warning", "message", "field", "test")
    plain = _record()
    diagnosed = _record(diagnostics=(info, warning))
    assert plain.knowledge_authority_decision_id == diagnosed.knowledge_authority_decision_id
    with pytest.raises(ValueError):
        KnowledgeAuthorityDiagnostic("code", "error", "message", "field", "test")
    with pytest.raises(ValueError):
        _record(diagnostics=(object(),))  # type: ignore[arg-type]


def test_d10_canonical_identity_is_utf8_nfc_sorted_compact_utc_and_sha256() -> None:
    decomposed = "Cafe\u0301 actor"
    identity = _identity(
        decided_by=decomposed,
        decided_at=datetime(2026, 7, 13, 21, 30, 45, 123456, tzinfo=timezone(timedelta(hours=7))),
    )
    raw = canonical_knowledge_authority_identity_bytes(identity)
    projection = json.loads(raw.decode("utf-8"))
    assert projection["decided_by"] == unicodedata.normalize("NFC", decomposed)
    assert projection["decided_at"] == "2026-07-13T14:30:45.123456Z"
    assert raw == json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert compute_knowledge_authority_decision_id(identity) == "ka1_" + hashlib.sha256(raw).hexdigest()


def test_d11_exact_replay_returns_identical_bytes_and_identity() -> None:
    left = _identity()
    right = _identity()
    assert canonical_knowledge_authority_identity_bytes(left) == canonical_knowledge_authority_identity_bytes(right)
    assert compute_knowledge_authority_decision_id(left) == compute_knowledge_authority_decision_id(right)
    assert _record(left) == _record(right)


def test_d12_every_material_identity_field_change_changes_or_fails_closed() -> None:
    baseline = _identity()
    baseline_id = compute_knowledge_authority_decision_id(baseline)
    changes = (
        {"knowledge_candidate_id": "kc1_" + "4" * 64},
        {"knowledge_candidate_contract_version": "knowledge-candidate-v2"},
        {"knowledge_candidate_snapshot_digest": "5" * 64},
        {"knowledge_governance_decision_ids": ("kg1_" + "6" * 64,)},
        {"intended_authority_value": INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE},
        {"decision_outcome": AUTHORITY_DECISION_OUTCOME_DENIED},
        {"reason_codes": ("intended_knowledge_authority_authorized", "secondary")},
        {"decided_by": "another-actor"},
        {"decided_at": FIXED_TIME + timedelta(seconds=1)},
        {"authority_policy_id": "another-policy"},
        {"authority_policy_version": "2.0.0"},
    )
    assert all(compute_knowledge_authority_decision_id(_identity(**change)) != baseline_id for change in changes)
    with pytest.raises(ValueError):
        _identity(authority_decision_record_contract_version="knowledge-authority-decision-v2")


def test_d13_forbidden_downstream_metadata_is_absent_from_identity() -> None:
    projection = canonical_knowledge_authority_identity_projection(_identity())
    forbidden = {
        "diagnostics", "knowledge_review_record_ids", "conflict_ids", "source_path",
        "promotion_result", "governed_knowledge_id", "lifecycle_status", "acceptance",
        "repository", "persistence", "winner", "supersession", "invalidation",
    }
    assert forbidden.isdisjoint(projection)
    assert "statement" not in projection


def test_d14_candidate_snapshot_governance_and_identity_helpers_reject_ducks() -> None:
    class Duck:
        knowledge_candidate_id = "kc1_" + "1" * 64
        knowledge_governance_decision_id = "kg1_" + "2" * 64

    for function, value in (
        (verify_knowledge_authority_candidate_identity, Duck()),
        (compute_knowledge_authority_candidate_snapshot_digest, Duck()),
        (verify_knowledge_authority_governance_decision_identity, Duck()),
        (canonical_knowledge_authority_identity_projection, Duck()),
        (canonical_knowledge_authority_identity_bytes, Duck()),
        (compute_knowledge_authority_decision_id, Duck()),
        (knowledge_authority_identity_input_from_record, Duck()),
    ):
        with pytest.raises(ValueError):
            function(value)  # type: ignore[arg-type]


def test_d15_identity_extraction_from_record_round_trips_exactly() -> None:
    identity = _identity()
    record = _record(identity)
    extracted = knowledge_authority_identity_input_from_record(record)
    assert extracted == identity
    assert compute_knowledge_authority_decision_id(extracted) == record.knowledge_authority_decision_id
