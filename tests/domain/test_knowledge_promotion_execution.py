from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_PROMOTION_EXECUTION_DIGEST_ALGORITHM,
    KNOWLEDGE_PROMOTION_EXECUTION_ID_PREFIX,
    KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_ID,
    KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_VERSION,
    PROMOTION_EXECUTION_CONTROLLED_REASONS,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
    KnowledgePromotionExecutionDiagnostic,
    KnowledgePromotionExecutionIdentityInput,
    KnowledgePromotionExecutionRecord,
    canonical_knowledge_promotion_execution_identity_bytes,
    canonical_knowledge_promotion_execution_identity_projection,
    compute_knowledge_promotion_execution_id,
    knowledge_promotion_execution_identity_input_from_record,
)


FIXED_TIME = datetime(2026, 7, 14, 10, 30, 45, 123456, tzinfo=timezone.utc)


def _identity(**changes: object) -> KnowledgePromotionExecutionIdentityInput:
    values: dict[str, object] = {
        "execution_record_contract_version": (
            KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION
        ),
        "knowledge_candidate_id": "kc1_" + "1" * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "2" * 64,
        "knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "3" * 64,
        "knowledge_promotion_prerequisite_evaluation_contract_version": (
            "knowledge-promotion-prerequisite-evaluation-v1"
        ),
        "knowledge_promotion_decision_id": "kpd1_" + "4" * 64,
        "knowledge_promotion_decision_contract_version": (
            "knowledge-promotion-decision-v1"
        ),
        "promotion_decision_outcome": (
            "promotion_authorized_for_future_execution"
        ),
        "authorization_scope": (
            "eligible_for_future_promotion_execution_for_declared_scope"
        ),
        "execution_scope": PROMOTION_EXECUTION_SCOPE_DECLARED,
        "execution_outcome": PROMOTION_EXECUTION_OUTCOME_COMPLETED,
        "execution_reference": "execution-reference-1",
        "reason_codes": (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,),
        "executed_by": "execution-actor",
        "executed_at": FIXED_TIME,
        "execution_policy_id": "rcis-knowledge-promotion-execution",
        "execution_policy_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgePromotionExecutionIdentityInput(**values)  # type: ignore[arg-type]


def _diagnostic(
    severity: str = KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO,
) -> KnowledgePromotionExecutionDiagnostic:
    return KnowledgePromotionExecutionDiagnostic(
        code="execution_note",
        severity=severity,
        message="Execution note.",
        field="execution_outcome",
        source="domain-test",
    )


def _record(
    identity: KnowledgePromotionExecutionIdentityInput | None = None,
    *,
    execution_id: str | None = None,
    diagnostics: tuple[KnowledgePromotionExecutionDiagnostic, ...] = (),
) -> KnowledgePromotionExecutionRecord:
    value = identity or _identity()
    return KnowledgePromotionExecutionRecord(
        knowledge_promotion_execution_id=(
            execution_id or compute_knowledge_promotion_execution_id(value)
        ),
        contract_version=value.execution_record_contract_version,
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            value.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            value.knowledge_candidate_snapshot_digest
        ),
        knowledge_promotion_prerequisite_evaluation_id=(
            value.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            value.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        knowledge_promotion_decision_id=value.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=(
            value.knowledge_promotion_decision_contract_version
        ),
        promotion_decision_outcome=value.promotion_decision_outcome,
        authorization_scope=value.authorization_scope,
        execution_scope=value.execution_scope,
        execution_outcome=value.execution_outcome,
        execution_reference=value.execution_reference,
        reason_codes=value.reason_codes,
        executed_by=value.executed_by,
        executed_at=value.executed_at,
        execution_policy_id=value.execution_policy_id,
        execution_policy_version=value.execution_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_exact_frozen_dataclasses_and_field_order() -> None:
    assert [item.name for item in fields(KnowledgePromotionExecutionDiagnostic)] == [
        "code", "severity", "message", "field", "source"
    ]
    assert [item.name for item in fields(KnowledgePromotionExecutionIdentityInput)] == [
        "execution_record_contract_version", "knowledge_candidate_id",
        "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest",
        "knowledge_promotion_prerequisite_evaluation_id",
        "knowledge_promotion_prerequisite_evaluation_contract_version",
        "knowledge_promotion_decision_id", "knowledge_promotion_decision_contract_version",
        "promotion_decision_outcome", "authorization_scope", "execution_scope",
        "execution_outcome", "execution_reference", "reason_codes", "executed_by",
        "executed_at", "execution_policy_id", "execution_policy_version",
    ]
    assert [item.name for item in fields(KnowledgePromotionExecutionRecord)] == [
        "knowledge_promotion_execution_id", "contract_version", "knowledge_candidate_id",
        "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest",
        "knowledge_promotion_prerequisite_evaluation_id",
        "knowledge_promotion_prerequisite_evaluation_contract_version",
        "knowledge_promotion_decision_id", "knowledge_promotion_decision_contract_version",
        "promotion_decision_outcome", "authorization_scope", "execution_scope",
        "execution_outcome", "execution_reference", "reason_codes", "executed_by",
        "executed_at", "execution_policy_id", "execution_policy_version", "diagnostics",
    ]
    assert _identity() == _identity() and _record() == _record()
    with pytest.raises(FrozenInstanceError):
        _record().executed_by = "changed"  # type: ignore[misc]


def test_d02_exact_public_constants_and_vocabularies() -> None:
    assert KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION == "knowledge-promotion-execution-v1"
    assert KNOWLEDGE_PROMOTION_EXECUTION_ID_PREFIX == "kpx1_"
    assert KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_ID == "rcis-knowledge-promotion-execution-identity"
    assert KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_VERSION == "1.0.0"
    assert KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_CANONICALIZATION_CONTRACT == "knowledge-promotion-execution-json-v1"
    assert KNOWLEDGE_PROMOTION_EXECUTION_DIGEST_ALGORITHM == "sha256"
    assert PROMOTION_EXECUTION_SCOPE_DECLARED == "promotion_execution_for_declared_scope"
    assert PROMOTION_EXECUTION_OUTCOME_COMPLETED == "promotion_execution_completed_for_declared_scope"
    assert PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION == "authorized_promotion_execution_completed_for_declared_scope"
    assert PROMOTION_EXECUTION_CONTROLLED_REASONS == (PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,)
    assert (KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO, KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING) == ("info", "warning")


def test_d03_kpx1_is_strict_and_matches_canonical_content() -> None:
    identity = _identity()
    value = compute_knowledge_promotion_execution_id(identity)
    assert value.startswith("kpx1_") and len(value) == 69
    assert value[5:] == hashlib.sha256(canonical_knowledge_promotion_execution_identity_bytes(identity)).hexdigest()
    with pytest.raises(ValueError):
        _record(execution_id="kpx1_" + "A" * 64)
    with pytest.raises(ValueError):
        _record(execution_id="kpx1_" + "0" * 64)


def test_d04_candidate_lineage_is_strict_and_required() -> None:
    for changes in (
        {"knowledge_candidate_id": "kc1_" + "A" * 64},
        {"knowledge_candidate_contract_version": " "},
        {"knowledge_candidate_snapshot_digest": "g" * 64},
        {"knowledge_candidate_snapshot_digest": "1" * 63},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d05_prerequisite_evaluation_lineage_is_strict_and_required() -> None:
    for changes in (
        {"knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "A" * 64},
        {"knowledge_promotion_prerequisite_evaluation_contract_version": ""},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d06_promotion_decision_lineage_is_strict_and_required() -> None:
    for changes in (
        {"knowledge_promotion_decision_id": "kpd1_" + "z" * 64},
        {"knowledge_promotion_decision_contract_version": " "},
        {"promotion_decision_outcome": ""},
        {"authorization_scope": " "},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d07_execution_scope_and_outcome_are_exact_record_controls() -> None:
    with pytest.raises(ValueError):
        _identity(execution_scope="another_scope")
    with pytest.raises(ValueError):
        _identity(execution_outcome="another_outcome")


def test_d08_reference_actor_policy_and_reasons_are_exact_nonempty_values() -> None:
    for changes in (
        {"execution_reference": " "}, {"execution_reference": 1},
        {"executed_by": ""}, {"execution_policy_id": " "},
        {"execution_policy_version": 1}, {"reason_codes": ["reason"]},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d09_reason_tuple_is_nonempty_unique_and_lexically_ordered() -> None:
    for value in ((), ("reason", "reason"), ("z_reason", "a_reason"), ("",)):
        with pytest.raises(ValueError):
            _identity(reason_codes=value)
    assert _identity(reason_codes=("a_reason", "z_reason")).reason_codes == ("a_reason", "z_reason")


def test_d10_executed_at_is_exact_aware_and_canonical_utc_microseconds() -> None:
    with pytest.raises(ValueError):
        _identity(executed_at=datetime(2026, 7, 14))
    with pytest.raises(ValueError):
        _identity(executed_at="2026-07-14T00:00:00Z")
    local = FIXED_TIME.astimezone(timezone(timedelta(hours=7)))
    projection = canonical_knowledge_promotion_execution_identity_projection(_identity(executed_at=local))
    assert projection["executed_at"] == "2026-07-14T10:30:45.123456Z"


def test_d11_diagnostics_are_exact_frozen_info_or_warning() -> None:
    assert _diagnostic().severity == "info"
    assert _diagnostic("warning").severity == "warning"
    with pytest.raises(ValueError):
        _diagnostic("error")
    with pytest.raises(ValueError):
        _record(diagnostics=({"code": "x"},))  # type: ignore[arg-type]
    with pytest.raises(FrozenInstanceError):
        _diagnostic().message = "changed"  # type: ignore[misc]


def test_d12_canonical_identity_is_nfc_utf8_sorted_compact_finite_and_sha256() -> None:
    identity = _identity(executed_by="Cafe\u0301")
    projection = canonical_knowledge_promotion_execution_identity_projection(identity)
    raw = canonical_knowledge_promotion_execution_identity_bytes(identity)
    assert projection["executed_by"] == "Caf\u00e9"
    assert raw == json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert b" " not in raw and b"NaN" not in raw and b"Infinity" not in raw
    assert compute_knowledge_promotion_execution_id(identity) == "kpx1_" + hashlib.sha256(raw).hexdigest()


def test_d13_exact_replay_has_identical_bytes_and_kpx1() -> None:
    first = _identity()
    second = _identity()
    assert canonical_knowledge_promotion_execution_identity_bytes(first) == canonical_knowledge_promotion_execution_identity_bytes(second)
    assert compute_knowledge_promotion_execution_id(first) == compute_knowledge_promotion_execution_id(second)
    assert _record(first) == _record(second)


def test_d14_candidate_material_changes_identity() -> None:
    baseline = compute_knowledge_promotion_execution_id(_identity())
    for changes in (
        {"knowledge_candidate_id": "kc1_" + "5" * 64},
        {"knowledge_candidate_contract_version": "knowledge-candidate-v2"},
        {"knowledge_candidate_snapshot_digest": "6" * 64},
    ):
        assert compute_knowledge_promotion_execution_id(_identity(**changes)) != baseline


def test_d15_evaluation_material_changes_identity() -> None:
    baseline = compute_knowledge_promotion_execution_id(_identity())
    for changes in (
        {"knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "7" * 64},
        {"knowledge_promotion_prerequisite_evaluation_contract_version": "evaluation-v2"},
    ):
        assert compute_knowledge_promotion_execution_id(_identity(**changes)) != baseline


def test_d16_decision_material_changes_identity() -> None:
    baseline = compute_knowledge_promotion_execution_id(_identity())
    for changes in (
        {"knowledge_promotion_decision_id": "kpd1_" + "8" * 64},
        {"knowledge_promotion_decision_contract_version": "decision-v2"},
        {"promotion_decision_outcome": "promotion_denied"},
        {"authorization_scope": "another_authorization_scope"},
    ):
        assert compute_knowledge_promotion_execution_id(_identity(**changes)) != baseline


def test_d17_other_material_changes_identity_or_fail_closed() -> None:
    baseline = compute_knowledge_promotion_execution_id(_identity())
    changes = (
        {"execution_reference": "execution-reference-2"}, {"reason_codes": ("another_reason",)},
        {"executed_by": "another-actor"}, {"executed_at": FIXED_TIME + timedelta(seconds=1)},
        {"execution_policy_id": "another-policy"}, {"execution_policy_version": "2.0.0"},
    )
    for change in changes:
        assert compute_knowledge_promotion_execution_id(_identity(**change)) != baseline
    with pytest.raises(ValueError):
        _identity(execution_record_contract_version="knowledge-promotion-execution-v2")
    with pytest.raises(ValueError):
        _identity(execution_scope="another_scope")


def test_d18_diagnostics_and_forbidden_future_metadata_are_outside_identity() -> None:
    identity = _identity()
    assert _record(identity).knowledge_promotion_execution_id == _record(identity, diagnostics=(_diagnostic(),)).knowledge_promotion_execution_id
    names = {item.name for item in fields(KnowledgePromotionExecutionRecord)}
    forbidden = {"repository", "persistence", "governed_knowledge_id", "lifecycle_status", "acceptance_status", "authorization_consumed", "duplicate_prevented"}
    assert names.isdisjoint(forbidden)
    assert "diagnostics" not in canonical_knowledge_promotion_execution_identity_projection(identity)


def test_d19_projection_and_identity_helpers_reject_wrong_exact_and_duck_types() -> None:
    class Duck:
        pass

    class IdentitySubclass(KnowledgePromotionExecutionIdentityInput):
        pass

    identity = _identity()
    subclass = IdentitySubclass(**{item.name: getattr(identity, item.name) for item in fields(identity)})
    for value in ({}, Duck(), subclass):
        with pytest.raises(ValueError):
            canonical_knowledge_promotion_execution_identity_projection(value)  # type: ignore[arg-type]
    for value in ({}, Duck(), identity):
        with pytest.raises(ValueError):
            knowledge_promotion_execution_identity_input_from_record(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        _record(execution_id="kpx1_" + "0" * 64)


def test_d20_record_identity_extraction_round_trips_and_coexistence_is_unranked() -> None:
    first = _record(_identity(execution_reference="execution-reference-1"))
    second = _record(_identity(execution_reference="execution-reference-2"))
    extracted = knowledge_promotion_execution_identity_input_from_record(first)
    assert extracted == _identity(execution_reference="execution-reference-1")
    assert compute_knowledge_promotion_execution_id(extracted) == first.knowledge_promotion_execution_id
    assert first.knowledge_promotion_execution_id != second.knowledge_promotion_execution_id
    assert [first, second] == [first, second] and [second, first] == [second, first]
