from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import json

import pytest

import rie.domain.governed_knowledge_acceptance_history_interpretation as domain
from rie.domain.governed_knowledge import GOVERNED_KNOWLEDGE_CONTRACT_VERSION
from rie.domain.governed_knowledge_acceptance_decision import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
)


_GOVERNED_KNOWLEDGE_ID = "gk1_" + "1" * 64
_DECISION_ID_1 = "gka1_" + "1" * 64
_DECISION_ID_2 = "gka1_" + "2" * 64


def _identity(**changes: object) -> domain.GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
    values = {
        "contract_version": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION,
        "governed_knowledge_id": _GOVERNED_KNOWLEDGE_ID,
        "governed_knowledge_contract_version": GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        "acceptance_scope": "governed_knowledge_acceptance_for_declared_scope",
        "acceptance_scope_reference": "scope:release",
        "acceptance_decision_contract_version": GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
        "acceptance_decision_ids": (_DECISION_ID_1,),
        "completeness_scope": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY,
        "completeness_reference": "history-snapshot:1",
        "outcome_composition": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY,
        "interpretation_policy_id": "rcis-governed-knowledge-acceptance-history-interpretation",
        "interpretation_policy_version": "1.0.0",
    }
    values.update(changes)
    return domain.GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput(**values)


def _record(
    identity_input: domain.GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput | None = None,
    diagnostics: tuple[domain.GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic, ...] = (),
) -> domain.GovernedKnowledgeAcceptanceHistoryInterpretation:
    identity_input = identity_input or _identity()
    return domain.GovernedKnowledgeAcceptanceHistoryInterpretation(
        governed_knowledge_acceptance_history_interpretation_id=(
            domain.compute_governed_knowledge_acceptance_history_interpretation_id(
                identity_input
            )
        ),
        contract_version=identity_input.contract_version,
        governed_knowledge_id=identity_input.governed_knowledge_id,
        governed_knowledge_contract_version=identity_input.governed_knowledge_contract_version,
        acceptance_scope=identity_input.acceptance_scope,
        acceptance_scope_reference=identity_input.acceptance_scope_reference,
        acceptance_decision_contract_version=identity_input.acceptance_decision_contract_version,
        acceptance_decision_ids=identity_input.acceptance_decision_ids,
        completeness_scope=identity_input.completeness_scope,
        completeness_reference=identity_input.completeness_reference,
        outcome_composition=identity_input.outcome_composition,
        interpretation_policy_id=identity_input.interpretation_policy_id,
        interpretation_policy_version=identity_input.interpretation_policy_version,
        diagnostics=diagnostics,
    )


def test_d01_records_are_frozen_and_value_equal() -> None:
    diagnostic = domain.GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic(
        code="notice", severity="info", message="message", field="request", source="test"
    )
    identity = _identity()
    record = _record(identity, (diagnostic,))
    assert diagnostic == replace(diagnostic)
    assert identity == replace(identity)
    assert record == replace(record)
    for value in (diagnostic, identity, record):
        with pytest.raises(FrozenInstanceError):
            value.code = "changed"  # type: ignore[attr-defined]


def test_d02_public_domain_constants_are_exact_and_complete() -> None:
    expected = {
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION": "governed-knowledge-acceptance-history-interpretation-v1",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_ID_PREFIX": "gkai1_",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_POLICY_ID": "rcis-governed-knowledge-acceptance-history-interpretation-identity",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_POLICY_VERSION": "1.0.0",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_CANONICALIZATION_CONTRACT": "rcis-governed-knowledge-acceptance-history-interpretation-canonical-json-v1",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIGEST_ALGORITHM": "sha256",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY": "caller_asserted_complete_bounded_subject_history",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS": "no_decisions",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY": "accepted_only",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY": "rejected_only",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY": "deferred_only",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED": "accepted_and_rejected",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED": "accepted_and_deferred",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED": "rejected_and_deferred",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED": "accepted_rejected_and_deferred",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_INFO": "info",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_WARNING": "warning",
    }
    actual = {
        name: value
        for name, value in vars(domain).items()
        if name.isupper() and not name.startswith("_")
    }
    assert actual == expected


def test_d03_interpretation_id_syntax_and_recomputation_fail_closed() -> None:
    identity = _identity()
    record = _record(identity)
    assert record.governed_knowledge_acceptance_history_interpretation_id.startswith("gkai1_")
    assert len(record.governed_knowledge_acceptance_history_interpretation_id) == 70
    with pytest.raises(ValueError):
        replace(record, governed_knowledge_acceptance_history_interpretation_id="gkai1_" + "A" * 64)
    with pytest.raises(ValueError):
        replace(record, governed_knowledge_acceptance_history_interpretation_id="gkai1_" + "0" * 64)


def test_d04_all_subject_key_fields_are_strict_and_required() -> None:
    class _StringSubclass(str):
        pass

    invalid = (
        ("governed_knowledge_id", "gk1_bad"),
        ("governed_knowledge_contract_version", "other"),
        ("acceptance_scope", ""),
        ("acceptance_scope", " "),
        ("acceptance_scope", "scope:other"),
        ("acceptance_scope_reference", ""),
        ("governed_knowledge_id", _StringSubclass(_GOVERNED_KNOWLEDGE_ID)),
        (
            "governed_knowledge_contract_version",
            _StringSubclass(GOVERNED_KNOWLEDGE_CONTRACT_VERSION),
        ),
        (
            "acceptance_scope",
            _StringSubclass("governed_knowledge_acceptance_for_declared_scope"),
        ),
        ("acceptance_scope_reference", _StringSubclass("scope:release")),
    )
    for field_name, value in invalid:
        with pytest.raises(ValueError):
            _identity(**{field_name: value})


def test_d05_acceptance_decision_contract_and_id_tuple_rules_are_exact() -> None:
    assert _identity(acceptance_decision_ids=()).acceptance_decision_ids == ()
    assert _identity(acceptance_decision_ids=(_DECISION_ID_1, _DECISION_ID_2)).acceptance_decision_ids == (
        _DECISION_ID_1,
        _DECISION_ID_2,
    )
    invalid = (
        {"acceptance_decision_contract_version": "other"},
        {"acceptance_decision_ids": [_DECISION_ID_1]},
        {"acceptance_decision_ids": (_DECISION_ID_1, _DECISION_ID_1)},
        {"acceptance_decision_ids": (_DECISION_ID_2, _DECISION_ID_1)},
        {"acceptance_decision_ids": ("gka1_bad",)},
    )
    for changes in invalid:
        with pytest.raises(ValueError):
            _identity(**changes)


def test_d06_completeness_scope_and_reference_are_identity_material() -> None:
    baseline = _identity()
    changed = replace(baseline, completeness_reference="history-snapshot:2")
    assert domain.compute_governed_knowledge_acceptance_history_interpretation_id(baseline) != (
        domain.compute_governed_knowledge_acceptance_history_interpretation_id(changed)
    )
    with pytest.raises(ValueError):
        replace(baseline, completeness_scope="other")
    with pytest.raises(ValueError):
        replace(baseline, completeness_reference=" ")


def test_d07_exactly_eight_outcome_compositions_are_accepted() -> None:
    values = (
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED,
        domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED,
    )
    assert len(set(values)) == 8
    for value in values:
        assert _identity(outcome_composition=value).outcome_composition == value
    with pytest.raises(ValueError):
        _identity(outcome_composition="current_state")


def test_d08_interpretation_policy_strings_are_strict_identity_material() -> None:
    baseline = _identity()
    changed_id = replace(baseline, interpretation_policy_id="policy:other")
    changed_version = replace(baseline, interpretation_policy_version="2.0.0")
    ids = {
        domain.compute_governed_knowledge_acceptance_history_interpretation_id(item)
        for item in (baseline, changed_id, changed_version)
    }
    assert len(ids) == 3
    for field_name in ("interpretation_policy_id", "interpretation_policy_version"):
        with pytest.raises(ValueError):
            _identity(**{field_name: " "})


def test_d09_diagnostics_are_exact_immutable_and_outside_identity() -> None:
    info = domain.GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic(
        code="info", severity="info", message="message", field="request", source="test"
    )
    warning = replace(info, code="warning", severity="warning")
    baseline = _record(diagnostics=(info,))
    changed = _record(diagnostics=(warning,))
    assert baseline.governed_knowledge_acceptance_history_interpretation_id == changed.governed_knowledge_acceptance_history_interpretation_id
    with pytest.raises(ValueError):
        replace(info, severity="error")
    with pytest.raises(ValueError):
        replace(baseline, diagnostics=(object(),))


def test_d10_canonical_bytes_are_nfc_sorted_compact_utf8_json_and_sha256() -> None:
    identity = _identity(completeness_reference="Cafe\u0301")
    projection = domain.canonical_governed_knowledge_acceptance_history_interpretation_identity_projection(identity)
    canonical = domain.canonical_governed_knowledge_acceptance_history_interpretation_identity_bytes(identity)
    assert projection["completeness_reference"] == "Caf\u00e9"
    assert canonical.decode("utf-8") == json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    expected = "gkai1_" + hashlib.sha256(canonical).hexdigest()
    assert domain.compute_governed_knowledge_acceptance_history_interpretation_id(identity) == expected


def test_d11_exact_replay_has_identical_bytes_and_identity() -> None:
    first = _identity()
    second = _identity()
    assert domain.canonical_governed_knowledge_acceptance_history_interpretation_identity_bytes(first) == domain.canonical_governed_knowledge_acceptance_history_interpretation_identity_bytes(second)
    assert domain.compute_governed_knowledge_acceptance_history_interpretation_id(first) == domain.compute_governed_knowledge_acceptance_history_interpretation_id(second)


def test_d12_every_changeable_material_field_changes_identity() -> None:
    baseline = _identity()
    variants = (
        replace(baseline, governed_knowledge_id="gk1_" + "2" * 64),
        replace(baseline, acceptance_scope_reference="scope:other"),
        replace(baseline, acceptance_decision_ids=(_DECISION_ID_2,)),
        replace(baseline, completeness_reference="history-snapshot:2"),
        replace(
            baseline,
            outcome_composition=domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY,
        ),
        replace(baseline, interpretation_policy_id="policy:other"),
        replace(baseline, interpretation_policy_version="2.0.0"),
    )
    baseline_id = domain.compute_governed_knowledge_acceptance_history_interpretation_id(baseline)
    variant_ids = {
        domain.compute_governed_knowledge_acceptance_history_interpretation_id(item)
        for item in variants
    }
    assert baseline_id not in variant_ids
    assert len(variant_ids) == len(variants)


def test_d13_forbidden_state_and_runtime_material_are_absent() -> None:
    field_names = {item.name for item in fields(domain.GovernedKnowledgeAcceptanceHistoryInterpretation)}
    projection_names = set(
        domain.canonical_governed_knowledge_acceptance_history_interpretation_identity_projection(
            _identity()
        )
    )
    forbidden = {
        "current_acceptance_state",
        "winner",
        "lifecycle_status",
        "repository",
        "persistence",
        "path",
        "runtime",
    }
    assert forbidden.isdisjoint(field_names)
    assert forbidden.isdisjoint(projection_names)


def test_d14_wrong_exact_types_subclasses_and_duck_types_fail_closed() -> None:
    class _IdentitySubclass(domain.GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput):
        pass

    class _Duck:
        contract_version = domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION

    identity = _identity()
    subclass = _IdentitySubclass(**{item.name: getattr(identity, item.name) for item in fields(identity)})
    for value in (object(), _Duck(), subclass):
        with pytest.raises(ValueError):
            domain.compute_governed_knowledge_acceptance_history_interpretation_id(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        domain.governed_knowledge_acceptance_history_interpretation_identity_input_from_record(object())  # type: ignore[arg-type]


def test_d15_identity_extraction_round_trips_exactly() -> None:
    identity = _identity()
    record = _record(identity)
    extracted = domain.governed_knowledge_acceptance_history_interpretation_identity_input_from_record(record)
    assert extracted == identity
    assert domain.compute_governed_knowledge_acceptance_history_interpretation_id(extracted) == record.governed_knowledge_acceptance_history_interpretation_id
