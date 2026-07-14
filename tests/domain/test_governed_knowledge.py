from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CANONICALIZATION_VERSION,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_DIGEST_ALGORITHM,
    GOVERNED_KNOWLEDGE_IDENTITY_POLICY_ID,
    GOVERNED_KNOWLEDGE_IDENTITY_POLICY_VERSION,
    GOVERNED_KNOWLEDGE_ID_PREFIX,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeDiagnostic,
    GovernedKnowledgeIdentityInput,
    canonical_governed_knowledge_identity_bytes,
    canonical_governed_knowledge_identity_projection,
    compute_governed_knowledge_id,
    governed_knowledge_identity_input_from_record,
)
from rie.domain.knowledge_candidate import KnowledgeEvidenceSupport
from rie.domain.knowledge_promotion_decision import (
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
)
from rie.domain.knowledge_promotion_execution import (
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
)


FIXED_TIME = datetime(2026, 7, 15, 9, 30, 15, 654321, tzinfo=timezone.utc)


def _support(seed: str = "1") -> KnowledgeEvidenceSupport:
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
        locator_value=(int(seed, 16),),
        locator_schema_version="1.0.0",
    )


def _identity(**changes: object) -> GovernedKnowledgeIdentityInput:
    values: dict[str, object] = {
        "contract_version": GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        "knowledge_candidate_id": "kc1_" + "1" * 64,
        "knowledge_candidate_contract_version": "knowledge-candidate-v1",
        "knowledge_candidate_snapshot_digest": "2" * 64,
        "statement_type": "verbatim_text_fact",
        "statement": "Governed statement.",
        "support": (_support(),),
        "knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "3" * 64,
        "knowledge_promotion_prerequisite_evaluation_contract_version": (
            "knowledge-promotion-prerequisite-evaluation-v1"
        ),
        "knowledge_promotion_decision_id": "kpd1_" + "4" * 64,
        "knowledge_promotion_decision_contract_version": (
            "knowledge-promotion-decision-v1"
        ),
        "promotion_decision_outcome": PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        "authorization_scope": PROMOTION_DECISION_AUTHORIZATION_SCOPE,
        "knowledge_promotion_execution_id": "kpx1_" + "5" * 64,
        "knowledge_promotion_execution_contract_version": (
            "knowledge-promotion-execution-v1"
        ),
        "promotion_execution_scope": PROMOTION_EXECUTION_SCOPE_DECLARED,
        "promotion_execution_outcome": PROMOTION_EXECUTION_OUTCOME_COMPLETED,
        "construction_scope": GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
        "construction_reference": "construction-reference-1",
        "reason_codes": (REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,),
        "constructed_by": "construction-actor",
        "constructed_at": FIXED_TIME,
        "construction_policy_id": "rcis-governed-knowledge-construction",
        "construction_policy_version": "1.0.0",
    }
    values.update(changes)
    return GovernedKnowledgeIdentityInput(**values)


def _record(identity: GovernedKnowledgeIdentityInput | None = None) -> GovernedKnowledge:
    value = identity or _identity()
    return GovernedKnowledge(
        governed_knowledge_id=compute_governed_knowledge_id(value),
        contract_version=value.contract_version,
        knowledge_candidate_id=value.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            value.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=value.knowledge_candidate_snapshot_digest,
        statement_type=value.statement_type,
        statement=value.statement,
        support=value.support,
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
        knowledge_promotion_execution_id=value.knowledge_promotion_execution_id,
        knowledge_promotion_execution_contract_version=(
            value.knowledge_promotion_execution_contract_version
        ),
        promotion_execution_scope=value.promotion_execution_scope,
        promotion_execution_outcome=value.promotion_execution_outcome,
        construction_scope=value.construction_scope,
        construction_reference=value.construction_reference,
        reason_codes=value.reason_codes,
        constructed_by=value.constructed_by,
        constructed_at=value.constructed_at,
        construction_policy_id=value.construction_policy_id,
        construction_policy_version=value.construction_policy_version,
        diagnostics=(),
    )


def test_d01_frozen_dataclasses_exact_fields_equality_and_gk1_identity() -> None:
    expected = [
        "governed_knowledge_id", "contract_version", "knowledge_candidate_id",
        "knowledge_candidate_contract_version", "knowledge_candidate_snapshot_digest",
        "statement_type", "statement", "support",
        "knowledge_promotion_prerequisite_evaluation_id",
        "knowledge_promotion_prerequisite_evaluation_contract_version",
        "knowledge_promotion_decision_id", "knowledge_promotion_decision_contract_version",
        "promotion_decision_outcome", "authorization_scope",
        "knowledge_promotion_execution_id", "knowledge_promotion_execution_contract_version",
        "promotion_execution_scope", "promotion_execution_outcome", "construction_scope",
        "construction_reference", "reason_codes", "constructed_by", "constructed_at",
        "construction_policy_id", "construction_policy_version", "diagnostics",
    ]
    record = _record()
    assert [item.name for item in fields(GovernedKnowledge)] == expected
    assert record == _record() and record.governed_knowledge_id.startswith("gk1_")
    with pytest.raises(FrozenInstanceError):
        record.statement = "changed"  # type: ignore[misc]


def test_d02_public_constants_are_exact() -> None:
    assert GOVERNED_KNOWLEDGE_CONTRACT_VERSION == "governed-knowledge-v1"
    assert GOVERNED_KNOWLEDGE_ID_PREFIX == "gk1_"
    assert GOVERNED_KNOWLEDGE_IDENTITY_POLICY_ID == "rcis-governed-knowledge-identity"
    assert GOVERNED_KNOWLEDGE_IDENTITY_POLICY_VERSION == "1.0.0"
    assert GOVERNED_KNOWLEDGE_CANONICALIZATION_VERSION == "rcis-governed-knowledge-canonical-json-v1"
    assert GOVERNED_KNOWLEDGE_DIGEST_ALGORITHM == "sha256"
    assert GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE == "governed_knowledge_construction_for_declared_scope"
    assert REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON == "governed_knowledge_constructed_from_completed_promotion_execution"


def test_d03_gk1_shape_and_content_identity_match() -> None:
    identity = _identity()
    record = _record(identity)
    assert len(record.governed_knowledge_id) == 68
    assert record.governed_knowledge_id == "gk1_" + hashlib.sha256(
        canonical_governed_knowledge_identity_bytes(identity)
    ).hexdigest()
    with pytest.raises(ValueError):
        replace(record, governed_knowledge_id="gk1_" + "0" * 64)


def test_d04_candidate_lineage_is_strict() -> None:
    for changes in (
        {"knowledge_candidate_id": "bad"},
        {"knowledge_candidate_contract_version": ""},
        {"knowledge_candidate_snapshot_digest": "bad"},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d05_prerequisite_evaluation_lineage_is_strict() -> None:
    with pytest.raises(ValueError):
        _identity(knowledge_promotion_prerequisite_evaluation_id="kpe1_bad")
    with pytest.raises(ValueError):
        _identity(knowledge_promotion_prerequisite_evaluation_contract_version=" ")


def test_d06_decision_lineage_outcome_and_authorization_are_strict() -> None:
    for changes in (
        {"knowledge_promotion_decision_id": "kpd1_bad"},
        {"knowledge_promotion_decision_contract_version": ""},
        {"promotion_decision_outcome": "promotion_denied"},
        {"authorization_scope": "other"},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d07_execution_lineage_scope_and_outcome_are_strict() -> None:
    for changes in (
        {"knowledge_promotion_execution_id": "kpx1_bad"},
        {"knowledge_promotion_execution_contract_version": ""},
        {"promotion_execution_scope": "other"},
        {"promotion_execution_outcome": "other"},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d08_statement_and_exact_ordered_support_are_required() -> None:
    with pytest.raises(ValueError):
        _identity(statement=" ")
    with pytest.raises(ValueError):
        _identity(support=())
    with pytest.raises(ValueError):
        _identity(support=(_support("2"), _support("1")))
    with pytest.raises(ValueError):
        _identity(support=(_support(), object()))


def test_d09_construction_material_is_strict() -> None:
    for changes in (
        {"construction_scope": "other"},
        {"construction_reference": ""},
        {"reason_codes": ()},
        {"reason_codes": ("z", "a")},
        {"reason_codes": ("a", "a")},
        {"reason_codes": ("other",)},
        {"constructed_by": ""},
        {"construction_policy_id": ""},
        {"construction_policy_version": ""},
    ):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d10_time_is_exact_aware_and_canonical_utc_microseconds() -> None:
    with pytest.raises(ValueError):
        _identity(constructed_at=datetime(2026, 7, 15))
    shifted = _identity(constructed_at=FIXED_TIME.astimezone(timezone(timedelta(hours=7))))
    projection = canonical_governed_knowledge_identity_projection(shifted)
    assert projection["constructed_at"] == "2026-07-15T09:30:15.654321Z"


def test_d11_diagnostics_are_exact_frozen_and_outside_identity() -> None:
    diagnostic = GovernedKnowledgeDiagnostic("code", "warning", "message", "field", "source")
    record = replace(_record(), diagnostics=(diagnostic,))
    assert governed_knowledge_identity_input_from_record(record) == _identity()
    with pytest.raises(ValueError):
        replace(record, diagnostics=(object(),))
    with pytest.raises(FrozenInstanceError):
        diagnostic.code = "changed"  # type: ignore[misc]


def test_d12_canonical_identity_is_nfc_utf8_sorted_compact_finite_sha256() -> None:
    decomposed = _identity(statement="Cafe\u0301")
    composed = _identity(statement="Café")
    raw = canonical_governed_knowledge_identity_bytes(decomposed)
    assert raw == canonical_governed_knowledge_identity_bytes(composed)
    assert raw == json.dumps(
        canonical_governed_knowledge_identity_projection(decomposed),
        ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    assert decomposed.statement == "Cafe\u0301"


def test_d13_exact_replay_is_identical() -> None:
    first = _identity()
    second = _identity()
    assert canonical_governed_knowledge_identity_bytes(first) == canonical_governed_knowledge_identity_bytes(second)
    assert compute_governed_knowledge_id(first) == compute_governed_knowledge_id(second)


def test_d14_statement_material_changes_identity() -> None:
    assert compute_governed_knowledge_id(_identity()) != compute_governed_knowledge_id(
        _identity(statement="Another governed statement.")
    )


def test_d15_support_material_changes_identity() -> None:
    assert compute_governed_knowledge_id(_identity()) != compute_governed_knowledge_id(
        _identity(support=(_support("2"),))
    )


def test_d16_each_upstream_lineage_changes_identity() -> None:
    base = compute_governed_knowledge_id(_identity())
    changes = (
        {"knowledge_candidate_id": "kc1_" + "6" * 64},
        {"knowledge_promotion_prerequisite_evaluation_id": "kpe1_" + "6" * 64},
        {"knowledge_promotion_decision_id": "kpd1_" + "6" * 64},
        {"knowledge_promotion_execution_id": "kpx1_" + "6" * 64},
    )
    assert all(compute_governed_knowledge_id(_identity(**item)) != base for item in changes)


def test_d17_construction_event_material_changes_or_fails_closed() -> None:
    base = compute_governed_knowledge_id(_identity())
    for changes in (
        {"construction_reference": "construction-reference-2"},
        {"constructed_by": "another-actor"},
        {"constructed_at": FIXED_TIME + timedelta(seconds=1)},
        {"construction_policy_version": "2.0.0"},
    ):
        assert compute_governed_knowledge_id(_identity(**changes)) != base


def test_d18_forbidden_future_metadata_is_absent_from_identity() -> None:
    projection = canonical_governed_knowledge_identity_projection(_identity())
    forbidden = {"diagnostics", "acceptance", "lifecycle", "repository", "persistence", "prompt", "ai"}
    assert forbidden.isdisjoint(projection)
    assert "diagnostics" not in {item.name for item in fields(GovernedKnowledgeIdentityInput)}


def test_d19_helpers_reject_wrong_exact_and_duck_types() -> None:
    class Duck:
        pass

    for helper in (
        canonical_governed_knowledge_identity_projection,
        canonical_governed_knowledge_identity_bytes,
        compute_governed_knowledge_id,
    ):
        with pytest.raises(ValueError):
            helper(Duck())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        governed_knowledge_identity_input_from_record(Duck())  # type: ignore[arg-type]


def test_d20_identity_round_trip_and_unranked_coexistence() -> None:
    first = _record()
    second = _record(_identity(construction_reference="construction-reference-2"))
    assert governed_knowledge_identity_input_from_record(first) == _identity()
    assert first != second
    assert not hasattr(first, "winner") and not hasattr(first, "supersedes")
