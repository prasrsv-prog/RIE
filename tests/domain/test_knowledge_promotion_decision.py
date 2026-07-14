from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from rie.application.knowledge_promotion_decider import (
    KNOWLEDGE_PROMOTION_DECISION_POLICY_ID,
    KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION,
    PROMOTION_DECISION_REJECTION_REASONS,
    PROMOTION_DECISION_RESULT_STATUS_RECORDED,
    PROMOTION_DECISION_RESULT_STATUS_REJECTED,
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
    KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_PROMOTION_DECISION_DIGEST_ALGORITHM,
    KNOWLEDGE_PROMOTION_DECISION_ID_PREFIX,
    KNOWLEDGE_PROMOTION_DECISION_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_ID,
    KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_VERSION,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_CONTROLLED_REASONS,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
    PROMOTION_DECISION_OUTCOME_DEFERRED,
    PROMOTION_DECISION_OUTCOME_DENIED,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    KnowledgePromotionDecision,
    KnowledgePromotionDecisionDiagnostic,
    KnowledgePromotionDecisionIdentityInput,
    canonical_knowledge_promotion_decision_identity_bytes,
    canonical_knowledge_promotion_decision_identity_projection,
    compute_knowledge_promotion_decision_candidate_snapshot_digest,
    compute_knowledge_promotion_decision_id,
    knowledge_promotion_decision_identity_input_from_record,
    verify_knowledge_promotion_decision_candidate_identity,
    verify_knowledge_promotion_prerequisite_evaluation_identity,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    compute_knowledge_promotion_prerequisite_evaluation_id,
)


FIXED_TIME = datetime(2026, 7, 14, 8, 15, 30, 123456, tzinfo=timezone.utc)


def _support() -> KnowledgeEvidenceSupport:
    return KnowledgeEvidenceSupport(
        evidence_id="ev1_" + "1" * 64,
        acceptance_record_ids=("ar1_" + "2" * 64,),
        acceptance_review_record_ids=("acceptance-review-1",),
        source_id="source-1",
        source_content_digest="3" * 64,
        source_authority_status="official",
        source_lifecycle_status="active",
        payload_digest="4" * 64,
        locator_type="page",
        locator_value=(1,),
        locator_schema_version="1.0.0",
    )


def _candidate() -> KnowledgeCandidate:
    identity = KnowledgeCandidateIdentityInput(
        candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement="Promotion decision candidate.",
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=(_support(),),
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


def _evaluation(candidate: KnowledgeCandidate | None = None) -> KnowledgePromotionPrerequisiteEvaluation:
    value = candidate or _candidate()
    identity = KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ),
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=value.contract_version,
        knowledge_candidate_snapshot_digest=(
            compute_knowledge_promotion_decision_candidate_snapshot_digest(value)
        ),
        knowledge_promotion_evaluation_scope_id="kps1_" + "5" * 64,
        knowledge_governance_decision_ids=("kg1_" + "6" * 64,),
        knowledge_conflict_assessment_record_ids=("kcf1_" + "7" * 64,),
        knowledge_authority_decision_ids=("ka1_" + "8" * 64,),
        evaluation_scope=(
            PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE
        ),
        completeness_basis=(
            PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY
        ),
        evaluation_outcome=(
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
        ),
        reason_codes=(
            PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
        ),
        evaluated_by="evaluation-actor",
        evaluated_at=FIXED_TIME - timedelta(hours=1),
        evaluation_policy_id=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID
        ),
        evaluation_policy_version=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION
        ),
    )
    return KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=(
            compute_knowledge_promotion_prerequisite_evaluation_id(identity)
        ),
        contract_version=identity.evaluation_record_contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            identity.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            identity.knowledge_candidate_snapshot_digest
        ),
        knowledge_promotion_evaluation_scope_id=(
            identity.knowledge_promotion_evaluation_scope_id
        ),
        knowledge_governance_decision_ids=(
            identity.knowledge_governance_decision_ids
        ),
        knowledge_conflict_assessment_record_ids=(
            identity.knowledge_conflict_assessment_record_ids
        ),
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


def _identity(**changes: object) -> KnowledgePromotionDecisionIdentityInput:
    values: dict[str, object] = {
        "decision_record_contract_version": KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
        "knowledge_candidate_id": "kc1_" + "1" * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "2" * 64,
        "knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "3" * 64,
        "knowledge_promotion_prerequisite_evaluation_contract_version": (
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ),
        "promotion_prerequisite_evaluation_outcome": (
            PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE
        ),
        "authorization_scope": PROMOTION_DECISION_AUTHORIZATION_SCOPE,
        "promotion_decision": PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        "reason_codes": (
            PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
        ),
        "decided_by": "decision-actor",
        "decided_at": FIXED_TIME,
        "decision_policy_id": KNOWLEDGE_PROMOTION_DECISION_POLICY_ID,
        "decision_policy_version": KNOWLEDGE_PROMOTION_DECISION_POLICY_VERSION,
    }
    values.update(changes)
    return KnowledgePromotionDecisionIdentityInput(**values)  # type: ignore[arg-type]


def _record(
    identity: KnowledgePromotionDecisionIdentityInput | None = None,
    *,
    decision_id: str | None = None,
    diagnostics: tuple[KnowledgePromotionDecisionDiagnostic, ...] = (),
) -> KnowledgePromotionDecision:
    value = identity or _identity()
    return KnowledgePromotionDecision(
        knowledge_promotion_decision_id=(
            decision_id or compute_knowledge_promotion_decision_id(value)
        ),
        contract_version=value.decision_record_contract_version,
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            value.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=value.knowledge_candidate_snapshot_digest,
        knowledge_promotion_prerequisite_evaluation_id=(
            value.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            value.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        promotion_prerequisite_evaluation_outcome=(
            value.promotion_prerequisite_evaluation_outcome
        ),
        authorization_scope=value.authorization_scope,
        promotion_decision=value.promotion_decision,
        reason_codes=value.reason_codes,
        decided_by=value.decided_by,
        decided_at=value.decided_at,
        decision_policy_id=value.decision_policy_id,
        decision_policy_version=value.decision_policy_version,
        diagnostics=diagnostics,
    )


def _diagnostic() -> KnowledgePromotionDecisionDiagnostic:
    return KnowledgePromotionDecisionDiagnostic(
        code="decision_note",
        severity=KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO,
        message="Decision note.",
        field="promotion_decision",
        source="domain-test",
    )


def test_d01_exact_frozen_dataclasses_and_field_order() -> None:
    assert [item.name for item in fields(KnowledgePromotionDecisionDiagnostic)] == [
        "code", "severity", "message", "field", "source"
    ]
    assert [item.name for item in fields(KnowledgePromotionDecisionIdentityInput)] == [
        "decision_record_contract_version", "knowledge_candidate_id",
        "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest",
        "knowledge_promotion_prerequisite_evaluation_id",
        "knowledge_promotion_prerequisite_evaluation_contract_version",
        "promotion_prerequisite_evaluation_outcome", "authorization_scope",
        "promotion_decision", "reason_codes", "decided_by", "decided_at",
        "decision_policy_id", "decision_policy_version",
    ]
    assert [item.name for item in fields(KnowledgePromotionDecision)] == [
        "knowledge_promotion_decision_id", "contract_version",
        "knowledge_candidate_id", "knowledge_candidate_contract_version",
        "knowledge_candidate_snapshot_digest",
        "knowledge_promotion_prerequisite_evaluation_id",
        "knowledge_promotion_prerequisite_evaluation_contract_version",
        "promotion_prerequisite_evaluation_outcome", "authorization_scope",
        "promotion_decision", "reason_codes", "decided_by", "decided_at",
        "decision_policy_id", "decision_policy_version", "diagnostics",
    ]
    for value in (_diagnostic(), _identity(), _record()):
        with pytest.raises(FrozenInstanceError):
            value.code = "changed"  # type: ignore[attr-defined,misc]


def test_d02_all_public_constants_are_exact() -> None:
    assert KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION == "knowledge-promotion-decision-v1"
    assert KNOWLEDGE_PROMOTION_DECISION_ID_PREFIX == "kpd1_"
    assert KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_ID == "rcis-knowledge-promotion-decision-identity"
    assert KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_VERSION == "1.0.0"
    assert KNOWLEDGE_PROMOTION_DECISION_IDENTITY_CANONICALIZATION_CONTRACT == "knowledge-promotion-decision-json-v1"
    assert KNOWLEDGE_PROMOTION_DECISION_DIGEST_ALGORITHM == "sha256"
    assert PROMOTION_DECISION_AUTHORIZATION_SCOPE == "eligible_for_future_promotion_execution_for_declared_scope"
    assert (
        PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        PROMOTION_DECISION_OUTCOME_DENIED,
        PROMOTION_DECISION_OUTCOME_DEFERRED,
    ) == (
        "promotion_authorized_for_future_execution",
        "promotion_denied",
        "promotion_decision_deferred",
    )
    assert (
        KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING,
    ) == ("info", "warning")
    assert PROMOTION_DECISION_CONTROLLED_REASONS == (
        "satisfied_evaluation_supports_future_execution_authorization",
        "promotion_denied_despite_satisfied_evaluation",
        "promotion_decision_deferred_despite_satisfied_evaluation",
        "promotion_denied_for_not_satisfied_evaluation",
        "promotion_decision_deferred_for_not_satisfied_evaluation",
        "promotion_decision_deferred_for_deferred_evaluation",
    )
    assert (PROMOTION_DECISION_RESULT_STATUS_RECORDED, PROMOTION_DECISION_RESULT_STATUS_REJECTED) == ("recorded", "rejected")
    assert PROMOTION_DECISION_REJECTION_REASONS == (
        "unsupported_promotion_decision_policy",
        "unsupported_promotion_decision",
        "unsupported_prerequisite_evaluation_policy",
        "decision_candidate_mismatch",
        "decision_candidate_contract_mismatch",
        "decision_candidate_snapshot_mismatch",
        "ineligible_prerequisite_evaluation",
        "incomplete_prerequisite_evaluation",
        "missing_required_promotion_decision_reason",
    )


def test_d03_candidate_identity_contract_and_snapshot_are_strict() -> None:
    for changes in (
        {"knowledge_candidate_id": "kc1_" + "A" * 64},
        {"knowledge_candidate_id": "kc1_" + "1" * 63},
        {"knowledge_candidate_contract_version": " "},
        {"knowledge_candidate_snapshot_digest": "g" * 64},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d04_evaluation_identity_contract_and_outcome_are_strict() -> None:
    for changes in (
        {"knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "A" * 64},
        {"knowledge_promotion_prerequisite_evaluation_contract_version": ""},
        {"promotion_prerequisite_evaluation_outcome": "complete"},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d05_kpd1_is_strict_and_matches_canonical_content() -> None:
    assert len(_record().knowledge_promotion_decision_id) == 69
    for bad_id in ("kpd1_" + "A" * 64, "kpd1_" + "a" * 63, "kg1_" + "a" * 64):
        with pytest.raises(ValueError):
            _record(decision_id=bad_id)
    with pytest.raises(ValueError):
        replace(_record(), decided_by="another-actor")


def test_d06_authorization_scope_is_exact() -> None:
    assert _identity().authorization_scope == PROMOTION_DECISION_AUTHORIZATION_SCOPE
    with pytest.raises(ValueError):
        _identity(authorization_scope="eligible_for_execution")


def test_d07_only_three_decision_outcomes_are_recordable() -> None:
    for outcome in (
        PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        PROMOTION_DECISION_OUTCOME_DENIED,
        PROMOTION_DECISION_OUTCOME_DEFERRED,
    ):
        assert _identity(promotion_decision=outcome).promotion_decision == outcome
    for outcome in ("approved", "promoted", "", 1):
        with pytest.raises(ValueError):
            _identity(promotion_decision=outcome)


def test_d08_reason_tuple_is_exact_nonempty_unique_and_ordered() -> None:
    for reasons in ([], (), ("",), ("b", "a"), ("a", "a"), (1,)):
        with pytest.raises(ValueError):
            _identity(reason_codes=reasons)
    reasons = ("additional_reason", PROMOTION_DECISION_CONTROLLED_REASONS[0])
    assert _identity(reason_codes=reasons).reason_codes == reasons


def test_d09_actor_policy_and_aware_time_fail_closed() -> None:
    for changes in (
        {"decided_by": " "},
        {"decision_policy_id": ""},
        {"decision_policy_version": 1},
        {"decided_at": datetime(2026, 7, 14)},
        {"decided_at": "2026-07-14T00:00:00Z"},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d10_diagnostics_are_exact_frozen_info_or_warning() -> None:
    assert _diagnostic().severity == KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO
    warning = replace(_diagnostic(), severity=KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING)
    assert _record(diagnostics=(warning,)).diagnostics == (warning,)
    with pytest.raises(ValueError):
        replace(_diagnostic(), severity="error")
    with pytest.raises(ValueError):
        _record(diagnostics=(object(),))  # type: ignore[arg-type]


def test_d11_diagnostics_are_outside_identity() -> None:
    plain = _record()
    annotated = _record(diagnostics=(_diagnostic(),))
    assert plain.knowledge_promotion_decision_id == annotated.knowledge_promotion_decision_id
    assert knowledge_promotion_decision_identity_input_from_record(plain) == knowledge_promotion_decision_identity_input_from_record(annotated)


def test_d12_canonical_identity_is_utf8_nfc_sorted_compact_finite_and_utc() -> None:
    identity = _identity(decided_by="Cafe\u0301", decided_at=datetime(2026, 7, 14, 15, 15, 30, 123456, tzinfo=timezone(timedelta(hours=7))))
    encoded = canonical_knowledge_promotion_decision_identity_bytes(identity)
    projection = json.loads(encoded.decode("utf-8"))
    assert projection["decided_by"] == "Caf\u00e9"
    assert projection["decided_at"] == "2026-07-14T08:15:30.123456Z"
    assert encoded == json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    assert compute_knowledge_promotion_decision_id(identity) == "kpd1_" + hashlib.sha256(encoded).hexdigest()


def test_d13_exact_replay_has_identical_bytes_and_kpd1() -> None:
    first = _identity()
    second = _identity()
    assert canonical_knowledge_promotion_decision_identity_bytes(first) == canonical_knowledge_promotion_decision_identity_bytes(second)
    assert compute_knowledge_promotion_decision_id(first) == compute_knowledge_promotion_decision_id(second)
    assert _record(first) == _record(second)


def test_d14_material_candidate_fields_change_identity() -> None:
    baseline = compute_knowledge_promotion_decision_id(_identity())
    changes = (
        {"knowledge_candidate_id": "kc1_" + "9" * 64},
        {"knowledge_candidate_contract_version": "knowledge-candidate-v2"},
        {"knowledge_candidate_snapshot_digest": "9" * 64},
    )
    assert all(compute_knowledge_promotion_decision_id(_identity(**item)) != baseline for item in changes)


def test_d15_material_evaluation_fields_change_identity() -> None:
    baseline = compute_knowledge_promotion_decision_id(_identity())
    changes = (
        {"knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "9" * 64},
        {"knowledge_promotion_prerequisite_evaluation_contract_version": "knowledge-promotion-prerequisite-evaluation-v2"},
        {"promotion_prerequisite_evaluation_outcome": PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE},
    )
    assert all(compute_knowledge_promotion_decision_id(_identity(**item)) != baseline for item in changes)


def test_d16_other_material_fields_change_identity_or_fail_closed() -> None:
    baseline = compute_knowledge_promotion_decision_id(_identity())
    changes = (
        {"promotion_decision": PROMOTION_DECISION_OUTCOME_DENIED},
        {"reason_codes": ("different_reason",)},
        {"decided_by": "other-actor"},
        {"decided_at": FIXED_TIME + timedelta(seconds=1)},
        {"decision_policy_id": "other-policy"},
        {"decision_policy_version": "2.0.0"},
    )
    assert all(compute_knowledge_promotion_decision_id(_identity(**item)) != baseline for item in changes)
    with pytest.raises(ValueError):
        _identity(decision_record_contract_version="knowledge-promotion-decision-v2")


def test_d17_candidate_and_evaluation_identity_verification_fails_closed() -> None:
    candidate = _candidate()
    evaluation = _evaluation(candidate)
    assert verify_knowledge_promotion_decision_candidate_identity(candidate) == candidate.knowledge_candidate_id
    assert verify_knowledge_promotion_prerequisite_evaluation_identity(evaluation) == evaluation.knowledge_promotion_prerequisite_evaluation_id
    object.__setattr__(candidate, "knowledge_candidate_id", "kc1_" + "f" * 64)
    object.__setattr__(evaluation, "knowledge_promotion_prerequisite_evaluation_id", "kpe1_" + "f" * 64)
    with pytest.raises(ValueError):
        verify_knowledge_promotion_decision_candidate_identity(candidate)
    with pytest.raises(ValueError):
        verify_knowledge_promotion_prerequisite_evaluation_identity(evaluation)


def test_d18_identity_helpers_reject_wrong_exact_and_duck_types() -> None:
    class Duck:
        pass

    for value in ({}, Duck(), _record()):
        with pytest.raises(ValueError):
            canonical_knowledge_promotion_decision_identity_projection(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        knowledge_promotion_decision_identity_input_from_record(Duck())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        verify_knowledge_promotion_decision_candidate_identity(Duck())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        verify_knowledge_promotion_prerequisite_evaluation_identity(Duck())  # type: ignore[arg-type]


def test_d19_forbidden_future_metadata_is_absent_from_identity() -> None:
    keys = set(canonical_knowledge_promotion_decision_identity_projection(_identity()))
    forbidden = {
        "repository_path", "filesystem_path", "current_time", "random", "uuid",
        "winner", "latest_record", "execution_result", "governed_knowledge_id",
        "lifecycle_status", "acceptance_status", "persistence_metadata",
        "prompt_candidate", "ai_output", "diagnostics",
    }
    assert keys.isdisjoint(forbidden)


def test_d20_identity_extraction_round_trips_exactly() -> None:
    identity = _identity()
    record = _record(identity)
    extracted = knowledge_promotion_decision_identity_input_from_record(record)
    assert extracted == identity
    assert compute_knowledge_promotion_decision_id(extracted) == record.knowledge_promotion_decision_id
