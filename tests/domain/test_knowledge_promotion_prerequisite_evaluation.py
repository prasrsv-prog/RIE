from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import unicodedata

import pytest

from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_DIGEST_ALGORITHM,
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_ID_PREFIX,
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_ID,
    KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO,
    KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_DIGEST_ALGORITHM,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_ID_PREFIX,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_VERSION,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_EVALUATION_SCOPE_POLICY_ID,
    PROMOTION_EVALUATION_SCOPE_POLICY_VERSION,
    PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED,
    PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED,
    PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
    PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE,
    PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED,
    PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
    KnowledgePromotionEvaluationScope,
    KnowledgePromotionEvaluationScopeIdentityInput,
    KnowledgePromotionEvaluationScopePeer,
    KnowledgePromotionPrerequisiteDiagnostic,
    KnowledgePromotionPrerequisiteEvaluation,
    KnowledgePromotionPrerequisiteIdentityInput,
    canonical_knowledge_promotion_evaluation_scope_identity_bytes,
    canonical_knowledge_promotion_evaluation_scope_identity_projection,
    canonical_knowledge_promotion_prerequisite_identity_bytes,
    canonical_knowledge_promotion_prerequisite_identity_projection,
    compute_knowledge_promotion_evaluation_scope_id,
    compute_knowledge_promotion_prerequisite_evaluation_id,
    knowledge_promotion_evaluation_scope_identity_input_from_record,
    knowledge_promotion_prerequisite_identity_input_from_record,
)


FIXED_TIME = datetime(2026, 7, 13, 16, 30, 45, 123456, tzinfo=timezone.utc)


def _peer(seed: str = "2", **changes: object) -> KnowledgePromotionEvaluationScopePeer:
    values: dict[str, object] = {
        "knowledge_candidate_id": "kc1_" + seed * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": seed * 64,
    }
    values.update(changes)
    return KnowledgePromotionEvaluationScopePeer(**values)  # type: ignore[arg-type]


def _scope_identity(**changes: object) -> KnowledgePromotionEvaluationScopeIdentityInput:
    values: dict[str, object] = {
        "scope_contract_version": KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION,
        "target_knowledge_candidate_id": "kc1_" + "1" * 64,
        "target_knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "target_knowledge_candidate_snapshot_digest": "1" * 64,
        "peers": (_peer(),),
        "completeness_qualifier": PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE,
        "scoped_by": "scope-actor",
        "reason_codes": ("declared_scope_selected",),
        "scoped_at": FIXED_TIME,
        "scope_policy_id": PROMOTION_EVALUATION_SCOPE_POLICY_ID,
        "scope_policy_version": PROMOTION_EVALUATION_SCOPE_POLICY_VERSION,
    }
    values.update(changes)
    return KnowledgePromotionEvaluationScopeIdentityInput(**values)  # type: ignore[arg-type]


def _scope(identity: KnowledgePromotionEvaluationScopeIdentityInput | None = None, *, scope_id: str | None = None) -> KnowledgePromotionEvaluationScope:
    value = identity or _scope_identity()
    return KnowledgePromotionEvaluationScope(
        knowledge_promotion_evaluation_scope_id=scope_id or compute_knowledge_promotion_evaluation_scope_id(value),
        contract_version=value.scope_contract_version,
        target_knowledge_candidate_id=value.target_knowledge_candidate_id,
        target_knowledge_candidate_contract_version=value.target_knowledge_candidate_contract_version,
        target_knowledge_candidate_snapshot_digest=value.target_knowledge_candidate_snapshot_digest,
        peers=value.peers,
        completeness_qualifier=value.completeness_qualifier,
        scoped_by=value.scoped_by,
        reason_codes=value.reason_codes,
        scoped_at=value.scoped_at,
        scope_policy_id=value.scope_policy_id,
        scope_policy_version=value.scope_policy_version,
    )


def _evaluation_identity(**changes: object) -> KnowledgePromotionPrerequisiteIdentityInput:
    values: dict[str, object] = {
        "evaluation_record_contract_version": KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
        "knowledge_candidate_id": "kc1_" + "1" * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "1" * 64,
        "knowledge_promotion_evaluation_scope_id": _scope().knowledge_promotion_evaluation_scope_id,
        "knowledge_governance_decision_ids": ("kg1_" + "3" * 64,),
        "knowledge_conflict_assessment_record_ids": ("kcf1_" + "4" * 64,),
        "knowledge_authority_decision_ids": ("ka1_" + "5" * 64,),
        "evaluation_scope": PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE,
        "completeness_basis": PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY,
        "evaluation_outcome": PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
        "reason_codes": (PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,),
        "evaluated_by": "evaluation-actor",
        "evaluated_at": FIXED_TIME,
        "evaluation_policy_id": KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID,
        "evaluation_policy_version": KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION,
    }
    values.update(changes)
    return KnowledgePromotionPrerequisiteIdentityInput(**values)  # type: ignore[arg-type]


def _evaluation(identity: KnowledgePromotionPrerequisiteIdentityInput | None = None, *, diagnostics: tuple[KnowledgePromotionPrerequisiteDiagnostic, ...] = (), evaluation_id: str | None = None) -> KnowledgePromotionPrerequisiteEvaluation:
    value = identity or _evaluation_identity()
    return KnowledgePromotionPrerequisiteEvaluation(
        knowledge_promotion_prerequisite_evaluation_id=evaluation_id or compute_knowledge_promotion_prerequisite_evaluation_id(value),
        contract_version=value.evaluation_record_contract_version,
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=value.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=value.knowledge_candidate_snapshot_digest,
        knowledge_promotion_evaluation_scope_id=value.knowledge_promotion_evaluation_scope_id,
        knowledge_governance_decision_ids=value.knowledge_governance_decision_ids,
        knowledge_conflict_assessment_record_ids=value.knowledge_conflict_assessment_record_ids,
        knowledge_authority_decision_ids=value.knowledge_authority_decision_ids,
        evaluation_scope=value.evaluation_scope,
        completeness_basis=value.completeness_basis,
        evaluation_outcome=value.evaluation_outcome,
        reason_codes=value.reason_codes,
        evaluated_by=value.evaluated_by,
        evaluated_at=value.evaluated_at,
        evaluation_policy_id=value.evaluation_policy_id,
        evaluation_policy_version=value.evaluation_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_six_exact_frozen_domain_contracts_and_fields() -> None:
    expected = {
        KnowledgePromotionEvaluationScopePeer: ("knowledge_candidate_id", "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest"),
        KnowledgePromotionEvaluationScopeIdentityInput: ("scope_contract_version", "target_knowledge_candidate_id", "target_knowledge_candidate_contract_version", "target_knowledge_candidate_snapshot_digest", "peers", "completeness_qualifier", "scoped_by", "reason_codes", "scoped_at", "scope_policy_id", "scope_policy_version"),
        KnowledgePromotionEvaluationScope: ("knowledge_promotion_evaluation_scope_id", "contract_version", "target_knowledge_candidate_id", "target_knowledge_candidate_contract_version", "target_knowledge_candidate_snapshot_digest", "peers", "completeness_qualifier", "scoped_by", "reason_codes", "scoped_at", "scope_policy_id", "scope_policy_version"),
        KnowledgePromotionPrerequisiteDiagnostic: ("code", "severity", "message", "field", "source"),
        KnowledgePromotionPrerequisiteIdentityInput: ("evaluation_record_contract_version", "knowledge_candidate_id", "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest", "knowledge_promotion_evaluation_scope_id", "knowledge_governance_decision_ids", "knowledge_conflict_assessment_record_ids", "knowledge_authority_decision_ids", "evaluation_scope", "completeness_basis", "evaluation_outcome", "reason_codes", "evaluated_by", "evaluated_at", "evaluation_policy_id", "evaluation_policy_version"),
        KnowledgePromotionPrerequisiteEvaluation: ("knowledge_promotion_prerequisite_evaluation_id", "contract_version", "knowledge_candidate_id", "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest", "knowledge_promotion_evaluation_scope_id", "knowledge_governance_decision_ids", "knowledge_conflict_assessment_record_ids", "knowledge_authority_decision_ids", "evaluation_scope", "completeness_basis", "evaluation_outcome", "reason_codes", "evaluated_by", "evaluated_at", "evaluation_policy_id", "evaluation_policy_version", "diagnostics"),
    }
    values = (_peer(), _scope_identity(), _scope(), KnowledgePromotionPrerequisiteDiagnostic("note", "info", "message", "field", "test"), _evaluation_identity(), _evaluation())
    for value in values:
        assert tuple(field.name for field in fields(type(value))) == expected[type(value)]
        assert value == replace(value)
        with pytest.raises(FrozenInstanceError):
            setattr(value, fields(type(value))[0].name, "changed")
    assert "diagnostics" not in expected[KnowledgePromotionEvaluationScope]


def test_d02_all_public_constants_and_vocabularies_are_exact() -> None:
    assert (KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION, KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_ID_PREFIX, KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_ID, KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_VERSION, KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_CANONICALIZATION_CONTRACT, KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_DIGEST_ALGORITHM) == ("knowledge-promotion-evaluation-scope-v1", "kps1_", "rcis-knowledge-promotion-evaluation-scope-identity", "1.0.0", "knowledge-promotion-evaluation-scope-json-v1", "sha256")
    assert (KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_ID_PREFIX, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_ID, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_VERSION, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_CANONICALIZATION_CONTRACT, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_DIGEST_ALGORITHM) == ("knowledge-promotion-prerequisite-evaluation-v1", "kpe1_", "rcis-knowledge-promotion-prerequisite-evaluation-identity", "1.0.0", "knowledge-promotion-prerequisite-evaluation-json-v1", "sha256")
    assert (PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE, PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE, PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY) == ("complete_only_for_declared_peer_scope", "candidate_governance_conflict_authority_for_declared_peer_scope", "declared_scope_only")
    assert (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE) == ("prerequisites_satisfied_for_declared_scope", "prerequisites_not_satisfied_for_declared_scope", "prerequisites_deferred_for_declared_scope")
    assert (
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED,
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE,
        PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE,
    ) == (
        "declared_scope_prerequisites_satisfied",
        "declared_scope_prerequisites_not_satisfied",
        "governance_evidence_denied",
        "declared_scope_conflict_identified",
        "authority_value_not_authoritative",
        "authoritative_value_denied",
        "declared_scope_prerequisites_deferred",
        "declared_peer_scope_empty",
        "governance_evidence_deferred",
        "governance_evidence_contradictory",
        "declared_scope_conflict_coverage_incomplete",
        "declared_scope_conflict_evidence_ambiguous",
        "declared_scope_conflict_evidence_deferred",
        "authority_evidence_deferred",
        "authority_evidence_contradictory",
        "authority_evidence_not_affirmative",
    )
    assert (KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO, KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING) == ("info", "warning")
    assert (PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED, PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED) == ("recorded", "rejected")
    assert (KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID, KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION, PROMOTION_EVALUATION_SCOPE_POLICY_ID, PROMOTION_EVALUATION_SCOPE_POLICY_VERSION) == ("rcis-knowledge-promotion-prerequisite-evaluation", "1.0.0", "rcis-declared-knowledge-promotion-evaluation-scope", "1.0.0")
    assert PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS == (
        "unsupported_promotion_prerequisite_evaluation_policy",
        "unsupported_promotion_evaluation_scope_policy",
        "scope_candidate_mismatch",
        "scope_candidate_contract_mismatch",
        "scope_candidate_snapshot_mismatch",
        "unsupported_governance_evidence_policy",
        "governance_candidate_mismatch",
        "governance_candidate_contract_mismatch",
        "governance_candidate_snapshot_mismatch",
        "unsupported_conflict_evidence_policy",
        "conflict_record_outside_declared_scope",
        "conflict_participant_contract_mismatch",
        "conflict_participant_snapshot_mismatch",
        "unsupported_authority_evidence_policy",
        "authority_candidate_mismatch",
        "authority_candidate_contract_mismatch",
        "authority_candidate_snapshot_mismatch",
        "authority_governance_lineage_mismatch",
        "missing_or_mismatched_required_evaluation_reason",
    )


def test_d03_scope_peer_is_strict() -> None:
    for changes in ({"knowledge_candidate_id": "kc1_" + "A" * 64}, {"knowledge_candidate_contract_version": " "}, {"knowledge_candidate_snapshot_digest": "g" * 64}):
        with pytest.raises(ValueError):
            _peer(**changes)


def test_d04_scope_target_identity_contract_and_snapshot_are_strict() -> None:
    for changes in ({"target_knowledge_candidate_id": "kc1_" + "A" * 64}, {"target_knowledge_candidate_contract_version": ""}, {"target_knowledge_candidate_snapshot_digest": "0" * 63}):
        with pytest.raises(ValueError):
            _scope_identity(**changes)


def test_d05_scope_peers_are_exact_unique_ordered_and_exclude_target() -> None:
    assert _scope_identity(peers=()).peers == ()
    first, second = _peer("2"), _peer("3")
    assert _scope_identity(peers=(first, second)).peers == (first, second)
    for peers in ([], (second, first), (first, first), (_peer("1"),), (first, _peer("2", knowledge_candidate_contract_version="other"))):
        with pytest.raises(ValueError):
            _scope_identity(peers=peers)


def test_d06_scope_actor_reasons_time_and_policy_fail_closed() -> None:
    for changes in ({"scoped_by": " "}, {"reason_codes": ()}, {"reason_codes": ("z", "a")}, {"scoped_at": datetime(2026, 7, 13)}, {"scope_policy_id": 1}):
        with pytest.raises(ValueError):
            _scope_identity(**changes)


def test_d07_kps1_is_strict_and_matches_canonical_scope() -> None:
    identity = _scope_identity()
    expected = "kps1_" + hashlib.sha256(canonical_knowledge_promotion_evaluation_scope_identity_bytes(identity)).hexdigest()
    assert compute_knowledge_promotion_evaluation_scope_id(identity) == expected
    assert _scope(identity).knowledge_promotion_evaluation_scope_id == expected
    with pytest.raises(ValueError):
        _scope(identity, scope_id="kps1_" + "f" * 64)


def test_d08_kpe1_is_strict_and_matches_canonical_evaluation() -> None:
    identity = _evaluation_identity()
    expected = "kpe1_" + hashlib.sha256(canonical_knowledge_promotion_prerequisite_identity_bytes(identity)).hexdigest()
    assert compute_knowledge_promotion_prerequisite_evaluation_id(identity) == expected
    assert _evaluation(identity).knowledge_promotion_prerequisite_evaluation_id == expected
    with pytest.raises(ValueError):
        _evaluation(identity, evaluation_id="kpe1_" + "f" * 64)


def test_d09_record_id_tuples_are_exact_unique_ordered_with_exact_emptiness() -> None:
    assert _evaluation_identity(knowledge_conflict_assessment_record_ids=()).knowledge_conflict_assessment_record_ids == ()
    for changes in ({"knowledge_governance_decision_ids": ()}, {"knowledge_governance_decision_ids": []}, {"knowledge_authority_decision_ids": ()}, {"knowledge_conflict_assessment_record_ids": ("kcf1_" + "5" * 64, "kcf1_" + "4" * 64)}, {"knowledge_authority_decision_ids": ("ka1_" + "5" * 64,) * 2}):
        with pytest.raises(ValueError):
            _evaluation_identity(**changes)


def test_d10_scope_completeness_and_three_outcomes_are_exact() -> None:
    outcomes = (
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE, ("declared_scope_prerequisites_satisfied",)),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE, ("declared_scope_prerequisites_not_satisfied", "governance_evidence_denied")),
        (PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE, ("declared_scope_prerequisites_deferred", "governance_evidence_deferred")),
    )
    for outcome, reasons in outcomes:
        assert _evaluation_identity(evaluation_outcome=outcome, reason_codes=reasons).evaluation_outcome == outcome
    with pytest.raises(ValueError):
        _evaluation_identity(evaluation_outcome="promotion_ready")


def test_d11_evaluation_reasons_actor_time_and_policy_fail_closed() -> None:
    for changes in ({"reason_codes": ()}, {"reason_codes": ("z", "a")}, {"evaluated_by": ""}, {"evaluated_at": datetime(2026, 7, 13)}, {"evaluation_policy_version": 1}):
        with pytest.raises(ValueError):
            _evaluation_identity(**changes)


def test_d12_diagnostics_are_exact_immutable_and_outside_identity() -> None:
    info = KnowledgePromotionPrerequisiteDiagnostic("info-code", KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO, "message", "field", "test")
    warning = KnowledgePromotionPrerequisiteDiagnostic("warning-code", KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING, "message", "field", "test")
    assert _evaluation(diagnostics=(info, warning)).knowledge_promotion_prerequisite_evaluation_id == _evaluation().knowledge_promotion_prerequisite_evaluation_id
    with pytest.raises(ValueError):
        KnowledgePromotionPrerequisiteDiagnostic("code", "error", "message", "field", "test")
    with pytest.raises(ValueError):
        _evaluation(diagnostics=(object(),))  # type: ignore[arg-type]


def test_d13_scope_canonical_bytes_are_nfc_sorted_compact_finite_and_utc() -> None:
    identity = _scope_identity(scoped_by="Cafe\u0301", scoped_at=datetime(2026, 7, 13, 23, 30, 45, 123456, tzinfo=timezone(timedelta(hours=7))))
    raw = canonical_knowledge_promotion_evaluation_scope_identity_bytes(identity)
    text = raw.decode("utf-8")
    assert text == unicodedata.normalize("NFC", text)
    assert " " not in text and "\\n" not in text
    assert json.loads(text)["scoped_at"] == "2026-07-13T16:30:45.123456Z"


def test_d14_evaluation_canonical_bytes_are_nfc_sorted_compact_finite_and_utc() -> None:
    identity = _evaluation_identity(evaluated_by="Cafe\u0301", evaluated_at=datetime(2026, 7, 13, 23, 30, 45, 123456, tzinfo=timezone(timedelta(hours=7))))
    raw = canonical_knowledge_promotion_prerequisite_identity_bytes(identity)
    text = raw.decode("utf-8")
    assert text == unicodedata.normalize("NFC", text)
    assert " " not in text and "\\n" not in text
    assert json.loads(text)["evaluated_at"] == "2026-07-13T16:30:45.123456Z"


def test_d15_exact_scope_and_evaluation_replay_is_stable() -> None:
    assert canonical_knowledge_promotion_evaluation_scope_identity_bytes(_scope_identity()) == canonical_knowledge_promotion_evaluation_scope_identity_bytes(_scope_identity())
    assert compute_knowledge_promotion_evaluation_scope_id(_scope_identity()) == compute_knowledge_promotion_evaluation_scope_id(_scope_identity())
    assert canonical_knowledge_promotion_prerequisite_identity_bytes(_evaluation_identity()) == canonical_knowledge_promotion_prerequisite_identity_bytes(_evaluation_identity())


def test_d16_every_material_scope_field_changes_kps1() -> None:
    base = compute_knowledge_promotion_evaluation_scope_id(_scope_identity())
    changes = ({"target_knowledge_candidate_id": "kc1_" + "6" * 64}, {"target_knowledge_candidate_contract_version": "candidate-v2"}, {"target_knowledge_candidate_snapshot_digest": "6" * 64}, {"peers": (_peer("3"),)}, {"scoped_by": "other"}, {"reason_codes": ("other",)}, {"scoped_at": FIXED_TIME + timedelta(seconds=1)}, {"scope_policy_id": "other-scope-policy"}, {"scope_policy_version": "2.0.0"})
    assert all(compute_knowledge_promotion_evaluation_scope_id(_scope_identity(**change)) != base for change in changes)
    for unsupported in ({"scope_contract_version": "knowledge-promotion-evaluation-scope-v2"}, {"completeness_qualifier": "repository_global"}):
        with pytest.raises(ValueError):
            _scope_identity(**unsupported)


def test_d17_every_material_evaluation_field_changes_kpe1() -> None:
    base = compute_knowledge_promotion_prerequisite_evaluation_id(_evaluation_identity())
    deferred = (
        "declared_scope_prerequisites_deferred",
        "governance_evidence_deferred",
    )
    changes = ({"knowledge_candidate_id": "kc1_" + "6" * 64}, {"knowledge_candidate_contract_version": "candidate-v2"}, {"knowledge_candidate_snapshot_digest": "6" * 64}, {"knowledge_promotion_evaluation_scope_id": "kps1_" + "6" * 64}, {"knowledge_governance_decision_ids": ("kg1_" + "6" * 64,)}, {"knowledge_conflict_assessment_record_ids": ()}, {"knowledge_authority_decision_ids": ("ka1_" + "6" * 64,)}, {"evaluation_outcome": PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE, "reason_codes": deferred}, {"evaluated_by": "other"}, {"evaluated_at": FIXED_TIME + timedelta(seconds=1)}, {"evaluation_policy_id": "other-evaluation-policy"}, {"evaluation_policy_version": "2.0.0"})
    assert all(compute_knowledge_promotion_prerequisite_evaluation_id(_evaluation_identity(**change)) != base for change in changes)
    changed_reason = (
        "authority_evidence_deferred",
        "declared_scope_prerequisites_deferred",
    )
    assert compute_knowledge_promotion_prerequisite_evaluation_id(
        _evaluation_identity(
            evaluation_outcome=PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
            reason_codes=changed_reason,
        )
    ) != compute_knowledge_promotion_prerequisite_evaluation_id(
        _evaluation_identity(
            evaluation_outcome=PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
            reason_codes=deferred,
        )
    )
    for unsupported in ({"evaluation_record_contract_version": "knowledge-promotion-prerequisite-evaluation-v2"}, {"evaluation_scope": "repository_global"}, {"completeness_basis": "repository_global"}):
        with pytest.raises(ValueError):
            _evaluation_identity(**unsupported)


def test_d18_forbidden_metadata_is_absent_from_identity() -> None:
    keys = set(canonical_knowledge_promotion_evaluation_scope_identity_projection(_scope_identity())) | set(canonical_knowledge_promotion_prerequisite_identity_projection(_evaluation_identity()))
    forbidden = {"repository", "path", "current_time", "randomness", "uuid", "winner", "resolution", "promotion", "governed_knowledge_id", "lifecycle", "acceptance", "persistence", "diagnostics"}
    assert keys.isdisjoint(forbidden)


def test_d19_identity_helpers_reject_wrong_exact_and_duck_types() -> None:
    class ScopeDuck:
        scope_contract_version = KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION
    for function in (canonical_knowledge_promotion_evaluation_scope_identity_projection, compute_knowledge_promotion_evaluation_scope_id):
        with pytest.raises(ValueError):
            function(ScopeDuck())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        knowledge_promotion_evaluation_scope_identity_input_from_record(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        knowledge_promotion_prerequisite_identity_input_from_record(object())  # type: ignore[arg-type]


def test_d20_identity_extraction_round_trips_exactly() -> None:
    scope_identity = _scope_identity()
    evaluation_identity = _evaluation_identity()
    assert knowledge_promotion_evaluation_scope_identity_input_from_record(_scope(scope_identity)) == scope_identity
    assert knowledge_promotion_prerequisite_identity_input_from_record(_evaluation(evaluation_identity)) == evaluation_identity
