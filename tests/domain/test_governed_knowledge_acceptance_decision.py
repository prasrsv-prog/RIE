from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

import rie.domain.governed_knowledge_acceptance_decision as domain


NOW = datetime(2026, 7, 15, 9, 10, 11, 123456, tzinfo=timezone.utc)
GK_ID = "gk1_" + "1" * 64


def _identity(**changes: object) -> domain.GovernedKnowledgeAcceptanceDecisionIdentityInput:
    values = {
        "contract_version": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
        "governed_knowledge_id": GK_ID,
        "governed_knowledge_contract_version": "governed-knowledge-v1",
        "acceptance_scope": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
        "acceptance_scope_reference": "scope-release-2026-07",
        "acceptance_outcome": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
        "reason_codes": (
            domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE,
        ),
        "decided_by": "acceptance-board",
        "decided_at": NOW,
        "acceptance_policy_id": "rcis-governed-knowledge-acceptance-decision",
        "acceptance_policy_version": "1.0.0",
    }
    values.update(changes)
    return domain.GovernedKnowledgeAcceptanceDecisionIdentityInput(**values)


def _decision(
    identity: domain.GovernedKnowledgeAcceptanceDecisionIdentityInput | None = None,
    diagnostics: tuple[domain.GovernedKnowledgeAcceptanceDiagnostic, ...] = (),
) -> domain.GovernedKnowledgeAcceptanceDecision:
    value = identity or _identity()
    return domain.GovernedKnowledgeAcceptanceDecision(
        governed_knowledge_acceptance_decision_id=(
            domain.compute_governed_knowledge_acceptance_decision_id(value)
        ),
        contract_version=value.contract_version,
        governed_knowledge_id=value.governed_knowledge_id,
        governed_knowledge_contract_version=value.governed_knowledge_contract_version,
        acceptance_scope=value.acceptance_scope,
        acceptance_scope_reference=value.acceptance_scope_reference,
        acceptance_outcome=value.acceptance_outcome,
        reason_codes=value.reason_codes,
        decided_by=value.decided_by,
        decided_at=value.decided_at,
        acceptance_policy_id=value.acceptance_policy_id,
        acceptance_policy_version=value.acceptance_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_exact_frozen_types_value_equality_and_field_orders() -> None:
    diagnostic = domain.GovernedKnowledgeAcceptanceDiagnostic(
        "code", "info", "message", "field", "source"
    )
    identity = _identity()
    decision = _decision(identity)
    assert diagnostic == replace(diagnostic)
    assert identity == replace(identity)
    assert decision == replace(decision)
    assert [item.name for item in fields(diagnostic)] == [
        "code", "severity", "message", "field", "source"
    ]
    assert [item.name for item in fields(identity)] == [
        "contract_version", "governed_knowledge_id",
        "governed_knowledge_contract_version", "acceptance_scope",
        "acceptance_scope_reference", "acceptance_outcome", "reason_codes",
        "decided_by", "decided_at", "acceptance_policy_id",
        "acceptance_policy_version",
    ]
    assert [item.name for item in fields(decision)] == [
        "governed_knowledge_acceptance_decision_id", "contract_version",
        "governed_knowledge_id", "governed_knowledge_contract_version",
        "acceptance_scope", "acceptance_scope_reference", "acceptance_outcome",
        "reason_codes", "decided_by", "decided_at", "acceptance_policy_id",
        "acceptance_policy_version", "diagnostics",
    ]
    with pytest.raises(FrozenInstanceError):
        decision.acceptance_scope_reference = "other"  # type: ignore[misc]


def test_d02_exact_public_helpers_and_constants() -> None:
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION == "governed-knowledge-acceptance-decision-v1"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_ID_PREFIX == "gka1_"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_POLICY_ID == "rcis-governed-knowledge-acceptance-decision-identity"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_POLICY_VERSION == "1.0.0"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT == "rcis-governed-knowledge-acceptance-decision-canonical-json-v1"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DIGEST_ALGORITHM == "sha256"
    assert domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED == "governed_knowledge_acceptance_for_declared_scope"
    assert (domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED, domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED, domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED) == ("accepted", "rejected", "deferred")
    assert (domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_INFO, domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_WARNING) == ("info", "warning")
    for name in ("canonical_governed_knowledge_acceptance_decision_identity_projection", "canonical_governed_knowledge_acceptance_decision_identity_bytes", "compute_governed_knowledge_acceptance_decision_id", "governed_knowledge_acceptance_decision_identity_input_from_record"):
        assert callable(getattr(domain, name))


def test_d03_strict_gka_shape_and_canonical_content() -> None:
    identity = _identity()
    expected = domain.compute_governed_knowledge_acceptance_decision_id(identity)
    assert expected.startswith("gka1_") and len(expected) == 69
    with pytest.raises(ValueError):
        replace(_decision(identity), governed_knowledge_acceptance_decision_id="gka1_" + "A" * 64)
    with pytest.raises(ValueError):
        replace(_decision(identity), governed_knowledge_acceptance_decision_id="gka1_" + "0" * 64)


def test_d04_exact_governed_knowledge_lineage() -> None:
    assert _identity().governed_knowledge_id == GK_ID
    with pytest.raises(ValueError):
        _identity(governed_knowledge_id="kc1_" + "1" * 64)
    with pytest.raises(ValueError):
        _identity(governed_knowledge_contract_version="other")


def test_d05_declared_scope_and_opaque_reference_validation() -> None:
    assert _identity(acceptance_scope_reference="opaque://anything").acceptance_scope_reference == "opaque://anything"
    with pytest.raises(ValueError):
        _identity(acceptance_scope="other")
    with pytest.raises(ValueError):
        _identity(acceptance_scope_reference=" ")
    with pytest.raises(ValueError):
        _identity(acceptance_scope_reference=1)


def test_d06_only_three_outcomes_are_recordable() -> None:
    mapping = {
        "accepted": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE,
        "rejected": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,
        "deferred": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE,
    }
    for outcome, reason in mapping.items():
        assert _identity(acceptance_outcome=outcome, reason_codes=(reason,)).acceptance_outcome == outcome
    with pytest.raises(ValueError):
        _identity(acceptance_outcome="approved")


def test_d07_reason_tuple_rules_and_required_mapping() -> None:
    with pytest.raises(ValueError):
        _identity(reason_codes=())
    with pytest.raises(ValueError):
        _identity(reason_codes=[domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE])
    with pytest.raises(ValueError):
        _identity(reason_codes=("z", "a"))
    with pytest.raises(ValueError):
        _identity(reason_codes=("a", "a"))
    with pytest.raises(ValueError):
        _identity(reason_codes=("other",))


def test_d08_actor_policy_and_aware_time_fail_closed() -> None:
    for changes in ({"decided_by": ""}, {"acceptance_policy_id": 1}, {"acceptance_policy_version": " "}, {"decided_at": datetime(2026, 1, 1)}, {"decided_at": "now"}):
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d09_exact_diagnostic_validation() -> None:
    info = domain.GovernedKnowledgeAcceptanceDiagnostic("i", "info", "m", "f", "s")
    warning = domain.GovernedKnowledgeAcceptanceDiagnostic("w", "warning", "m", "f", "s")
    assert _decision(diagnostics=(info, warning)).diagnostics == (info, warning)
    with pytest.raises(ValueError):
        domain.GovernedKnowledgeAcceptanceDiagnostic("x", "error", "m", "f", "s")
    with pytest.raises(ValueError):
        replace(_decision(), diagnostics=(object(),))


def test_d10_canonical_nfc_utf8_sorted_compact_utc_microseconds_sha256() -> None:
    identity = _identity(decided_by="Cafe\u0301", decided_at=datetime(2026, 7, 15, 16, 10, 11, 123456, tzinfo=timezone(timedelta(hours=7))))
    raw = domain.canonical_governed_knowledge_acceptance_decision_identity_bytes(identity)
    text = raw.decode("utf-8")
    assert "Caf\u00e9" in text and "Cafe\u0301" not in text
    assert "2026-07-15T09:10:11.123456Z" in text
    assert b" " not in raw and b"\n" not in raw
    assert list(json.loads(text)) == sorted(json.loads(text))
    assert domain.compute_governed_knowledge_acceptance_decision_id(identity) == "gka1_" + hashlib.sha256(raw).hexdigest()


def test_d11_exact_replay_is_identical() -> None:
    first = _identity()
    second = _identity()
    assert domain.canonical_governed_knowledge_acceptance_decision_identity_bytes(first) == domain.canonical_governed_knowledge_acceptance_decision_identity_bytes(second)
    assert domain.compute_governed_knowledge_acceptance_decision_id(first) == domain.compute_governed_knowledge_acceptance_decision_id(second)


def test_d12_governed_knowledge_identity_changes_acceptance_identity() -> None:
    assert domain.compute_governed_knowledge_acceptance_decision_id(_identity()) != domain.compute_governed_knowledge_acceptance_decision_id(_identity(governed_knowledge_id="gk1_" + "2" * 64))


def test_d13_scope_reference_and_outcome_material() -> None:
    first = domain.compute_governed_knowledge_acceptance_decision_id(_identity())
    second = domain.compute_governed_knowledge_acceptance_decision_id(_identity(acceptance_scope_reference="scope-two"))
    rejected = domain.compute_governed_knowledge_acceptance_decision_id(_identity(acceptance_outcome="rejected", reason_codes=(domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,)))
    assert len({first, second, rejected}) == 3


def test_d14_reason_actor_and_time_change_identity() -> None:
    base = domain.compute_governed_knowledge_acceptance_decision_id(_identity())
    changed = {
        domain.compute_governed_knowledge_acceptance_decision_id(_identity(reason_codes=("additional", domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE))),
        domain.compute_governed_knowledge_acceptance_decision_id(_identity(decided_by="other")),
        domain.compute_governed_knowledge_acceptance_decision_id(_identity(decided_at=NOW + timedelta(seconds=1))),
    }
    assert base not in changed and len(changed) == 3


def test_d15_policy_material_and_contract_fail_closed() -> None:
    base = domain.compute_governed_knowledge_acceptance_decision_id(_identity())
    assert base != domain.compute_governed_knowledge_acceptance_decision_id(_identity(acceptance_policy_version="2.0.0"))
    with pytest.raises(ValueError):
        _identity(contract_version="other")


def test_d16_diagnostics_outside_identity() -> None:
    identity = _identity()
    diagnostic = domain.GovernedKnowledgeAcceptanceDiagnostic("i", "info", "m", "f", "s")
    assert _decision(identity).governed_knowledge_acceptance_decision_id == _decision(identity, (diagnostic,)).governed_knowledge_acceptance_decision_id


def test_d17_future_metadata_absent_from_identity() -> None:
    keys = domain.canonical_governed_knowledge_acceptance_decision_identity_projection(_identity())
    forbidden = ("snapshot_digest", "diagnostics", "lifecycle", "repository", "persistence", "supersession", "effective_current")
    assert all(not any(term in key for term in forbidden) for key in keys)


def test_d18_public_helpers_reject_wrong_subclass_and_duck_types() -> None:
    class IdentitySubclass(domain.GovernedKnowledgeAcceptanceDecisionIdentityInput):
        pass
    class Duck:
        pass
    subclass = IdentitySubclass(**{item.name: getattr(_identity(), item.name) for item in fields(_identity())})
    for function in (domain.canonical_governed_knowledge_acceptance_decision_identity_projection, domain.canonical_governed_knowledge_acceptance_decision_identity_bytes, domain.compute_governed_knowledge_acceptance_decision_id):
        for value in (object(), Duck(), subclass):
            with pytest.raises(ValueError):
                function(value)  # type: ignore[arg-type]
    for value in (object(), Duck()):
        with pytest.raises(ValueError):
            domain.governed_knowledge_acceptance_decision_identity_input_from_record(value)  # type: ignore[arg-type]


def test_d19_identity_extraction_round_trips() -> None:
    identity = _identity()
    assert domain.governed_knowledge_acceptance_decision_identity_input_from_record(_decision(identity)) == identity


def test_d20_distinct_decisions_coexist_without_selection_semantics() -> None:
    accepted = _decision(_identity())
    deferred = _decision(_identity(acceptance_outcome="deferred", reason_codes=(domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE,)))
    assert accepted != deferred
    names = set(domain.GovernedKnowledgeAcceptanceDecision.__dataclass_fields__)
    assert not names.intersection({"rank", "winner", "latest", "supersedes", "invalidates", "effective_current"})
