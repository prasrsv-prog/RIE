import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path

import pytest

import rie.application.governed_knowledge_acceptance_history_interpreter as application
import rie.domain.governed_knowledge_acceptance_history_interpretation as domain
from rie.domain.governed_knowledge import GOVERNED_KNOWLEDGE_CONTRACT_VERSION
from rie.domain.governed_knowledge_acceptance_decision import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
    GovernedKnowledgeAcceptanceDecision,
    GovernedKnowledgeAcceptanceDecisionIdentityInput,
    compute_governed_knowledge_acceptance_decision_id,
)


_GOVERNED_KNOWLEDGE_ID = "gk1_" + "1" * 64
_OTHER_GOVERNED_KNOWLEDGE_ID = "gk1_" + "2" * 64
_SCOPE_REFERENCE = "scope:release"
_REASON_BY_OUTCOME = {
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE
    ),
}


def _decision(
    outcome: str = GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
    *,
    governed_knowledge_id: str = _GOVERNED_KNOWLEDGE_ID,
    governed_knowledge_contract_version: str = GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    acceptance_scope: str = GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
    acceptance_scope_reference: str = _SCOPE_REFERENCE,
    decided_by: str = "actor:1",
    decided_at_minute: int = 1,
    acceptance_policy_id: str = "policy:acceptance",
    acceptance_policy_version: str = "1.0.0",
) -> GovernedKnowledgeAcceptanceDecision:
    identity = GovernedKnowledgeAcceptanceDecisionIdentityInput(
        contract_version=GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION,
        governed_knowledge_id=governed_knowledge_id,
        governed_knowledge_contract_version=governed_knowledge_contract_version,
        acceptance_scope=acceptance_scope,
        acceptance_scope_reference=acceptance_scope_reference,
        acceptance_outcome=outcome,
        reason_codes=(_REASON_BY_OUTCOME[outcome],),
        decided_by=decided_by,
        decided_at=datetime(2026, 7, 15, 8, decided_at_minute, tzinfo=timezone.utc),
        acceptance_policy_id=acceptance_policy_id,
        acceptance_policy_version=acceptance_policy_version,
    )
    return GovernedKnowledgeAcceptanceDecision(
        governed_knowledge_acceptance_decision_id=(
            compute_governed_knowledge_acceptance_decision_id(identity)
        ),
        contract_version=identity.contract_version,
        governed_knowledge_id=identity.governed_knowledge_id,
        governed_knowledge_contract_version=identity.governed_knowledge_contract_version,
        acceptance_scope=identity.acceptance_scope,
        acceptance_scope_reference=identity.acceptance_scope_reference,
        acceptance_outcome=identity.acceptance_outcome,
        reason_codes=identity.reason_codes,
        decided_by=identity.decided_by,
        decided_at=identity.decided_at,
        acceptance_policy_id=identity.acceptance_policy_id,
        acceptance_policy_version=identity.acceptance_policy_version,
        diagnostics=(),
    )


def _ordered(*decisions: GovernedKnowledgeAcceptanceDecision) -> tuple[GovernedKnowledgeAcceptanceDecision, ...]:
    return tuple(
        sorted(
            decisions,
            key=lambda item: item.governed_knowledge_acceptance_decision_id,
        )
    )


def _request(
    decisions: tuple[GovernedKnowledgeAcceptanceDecision, ...] = (),
    **changes: object,
) -> application.GovernedKnowledgeAcceptanceHistoryInterpretationRequest:
    values = {
        "governed_knowledge_id": _GOVERNED_KNOWLEDGE_ID,
        "governed_knowledge_contract_version": GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        "acceptance_scope": GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
        "acceptance_scope_reference": _SCOPE_REFERENCE,
        "acceptance_decisions": decisions,
        "completeness_scope": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY,
        "completeness_reference": "history-snapshot:1",
        "interpretation_policy_id": application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_ID,
        "interpretation_policy_version": application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_VERSION,
    }
    values.update(changes)
    return application.GovernedKnowledgeAcceptanceHistoryInterpretationRequest(**values)


def _interpret(
    *decisions: GovernedKnowledgeAcceptanceDecision,
) -> domain.GovernedKnowledgeAcceptanceHistoryInterpretation:
    result = application.interpret_governed_knowledge_acceptance_history(
        _request(_ordered(*decisions))
    )
    assert result.result_status == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED
    assert result.interpretation is not None
    return result.interpretation


def test_a01_empty_tuple_records_no_decisions() -> None:
    interpretation = _interpret()
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS
    assert interpretation.acceptance_decision_ids == ()


def test_a02_accepted_facts_record_accepted_only() -> None:
    interpretation = _interpret(
        _decision(decided_at_minute=1),
        _decision(decided_by="actor:2", decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY


def test_a03_rejected_facts_record_rejected_only() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED, decided_by="actor:2", decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY


def test_a04_deferred_facts_record_deferred_only() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED, decided_by="actor:2", decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY


def test_a05_distinct_same_outcome_decisions_remain_in_ordered_lineage() -> None:
    decisions = _ordered(
        _decision(decided_at_minute=1),
        _decision(decided_by="actor:2", decided_at_minute=2),
        _decision(decided_by="actor:3", decided_at_minute=3),
    )
    interpretation = _interpret(*decisions)
    assert interpretation.acceptance_decision_ids == tuple(
        item.governed_knowledge_acceptance_decision_id for item in decisions
    )


def test_a06_accepted_and_rejected_record_without_winner() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED, decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED
    assert "winner" not in {item.name for item in fields(interpretation)}


def test_a07_accepted_and_deferred_record_exact_composition() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED, decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED


def test_a08_rejected_and_deferred_record_exact_composition() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED, decided_at_minute=2),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED


def test_a09_all_outcomes_record_without_winner() -> None:
    interpretation = _interpret(
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED, decided_at_minute=2),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED, decided_at_minute=3),
    )
    assert interpretation.outcome_composition == domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED
    assert not hasattr(interpretation, "winning_decision_id")


def test_a10_different_actors_and_acceptance_policies_coexist_without_ranking() -> None:
    decisions = _ordered(
        _decision(decided_by="actor:z", acceptance_policy_id="policy:z", acceptance_policy_version="9.0.0"),
        _decision(GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED, decided_by="actor:a", decided_at_minute=2, acceptance_policy_id="policy:a"),
    )
    interpretation = _interpret(*decisions)
    assert interpretation.acceptance_decision_ids == tuple(
        item.governed_knowledge_acceptance_decision_id for item in decisions
    )
    assert not hasattr(interpretation, "actor_rank")
    assert not hasattr(interpretation, "policy_rank")


def test_a11_every_decision_matches_all_four_subject_key_values() -> None:
    decision = _decision()
    interpretation = _interpret(decision)
    assert (
        interpretation.governed_knowledge_id,
        interpretation.governed_knowledge_contract_version,
        interpretation.acceptance_scope,
        interpretation.acceptance_scope_reference,
    ) == (
        decision.governed_knowledge_id,
        decision.governed_knowledge_contract_version,
        decision.acceptance_scope,
        decision.acceptance_scope_reference,
    )


def test_a12_any_subject_mismatch_returns_exact_rejection() -> None:
    cases = (
        (_decision(governed_knowledge_id=_OTHER_GOVERNED_KNOWLEDGE_ID), {}),
        (_decision(), {"governed_knowledge_id": _OTHER_GOVERNED_KNOWLEDGE_ID}),
        (_decision(acceptance_scope_reference="scope:other"), {}),
        (_decision(), {"acceptance_scope_reference": "scope:other"}),
    )
    for decision, request_changes in cases:
        result = application.interpret_governed_knowledge_acceptance_history(
            _request((decision,), **request_changes)
        )
        assert result.reason_codes == (
            application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH,
        )
        assert result.interpretation is None


def test_a13_policy_constants_and_unsupported_policy_rejection_are_exact() -> None:
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_ID == "rcis-governed-knowledge-acceptance-history-interpretation"
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_VERSION == "1.0.0"
    result = application.interpret_governed_knowledge_acceptance_history(
        _request(interpretation_policy_version="2.0.0")
    )
    assert result.reason_codes == (
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY,
    )
    assert result.diagnostics[0].message == "The acceptance-history interpretation policy is unsupported."


def test_a14_result_constants_and_completeness_rejection_are_exact() -> None:
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED == "recorded"
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_REJECTED == "rejected"
    result = application.interpret_governed_knowledge_acceptance_history(
        _request(completeness_scope="other")
    )
    assert result.result_status == "rejected"
    assert result.reason_codes == (
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE,
    )
    assert result.diagnostics[0].message == "The acceptance-history completeness scope is unsupported."


def test_a15_scope_and_subject_rejection_constants_are_exact() -> None:
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE == "unsupported_acceptance_scope"
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH == "acceptance_decision_subject_mismatch"
    scope_result = application.interpret_governed_knowledge_acceptance_history(
        _request(acceptance_scope="other")
    )
    subject_result = application.interpret_governed_knowledge_acceptance_history(
        _request((_decision(acceptance_scope_reference="scope:other"),))
    )
    assert scope_result.reason_codes == ("unsupported_acceptance_scope",)
    assert scope_result.diagnostics[0].message == "The acceptance-history acceptance scope is unsupported."
    assert subject_result.reason_codes == ("acceptance_decision_subject_mismatch",)
    assert subject_result.diagnostics[0].message == "An acceptance decision does not match the requested interpretation subject."


def test_a16_rejection_tuple_and_first_applicable_precedence_are_exact() -> None:
    expected = (
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY,
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE,
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE,
        application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH,
    )
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_REASONS == expected
    mismatch = _decision(acceptance_scope_reference="scope:other")
    requests = (
        _request((mismatch,), interpretation_policy_id="other", completeness_scope="other", acceptance_scope="other"),
        _request((mismatch,), completeness_scope="other", acceptance_scope="other"),
        _request((mismatch,), acceptance_scope="other"),
        _request((mismatch,)),
    )
    for request, reason in zip(requests, expected, strict=True):
        result = application.interpret_governed_knowledge_acceptance_history(request)
        assert result.reason_codes == (reason,)
        assert result.diagnostics[0].code == reason
        assert result.diagnostics[0].severity == "warning"
        assert result.diagnostics[0].field == "request"
        assert result.diagnostics[0].source == "governed_knowledge_acceptance_history_interpreter"


def test_a17_malformed_material_raises_before_policy_evaluation() -> None:
    malformed_values = (
        {"governed_knowledge_id": "bad"},
        {"governed_knowledge_contract_version": "other"},
        {"acceptance_scope_reference": " "},
        {"acceptance_decisions": []},
        {"completeness_reference": ""},
        {"interpretation_policy_id": " "},
    )
    for changes in malformed_values:
        changes["interpretation_policy_version"] = "unsupported"
        with pytest.raises(ValueError):
            _request(**changes)
    decision = _decision()
    with pytest.raises(ValueError):
        _request((decision, decision))
    first = _decision(decided_at_minute=1)
    second = _decision(decided_at_minute=2)
    ordered = _ordered(first, second)
    with pytest.raises(ValueError):
        _request(tuple(reversed(ordered)))
    broken = _decision()
    object.__setattr__(broken, "governed_knowledge_acceptance_decision_id", "gka1_" + "0" * 64)
    with pytest.raises(ValueError):
        _request((broken,), interpretation_policy_id="unsupported")
    with pytest.raises(ValueError):
        application.interpret_governed_knowledge_acceptance_history(object())  # type: ignore[arg-type]


def test_a18_replay_is_stable_and_material_request_changes_change_identity() -> None:
    baseline_request = _request()
    replay = application.interpret_governed_knowledge_acceptance_history(baseline_request)
    repeated = application.interpret_governed_knowledge_acceptance_history(_request())
    assert replay == repeated
    assert replay.interpretation is not None
    variants = (
        _request(governed_knowledge_id=_OTHER_GOVERNED_KNOWLEDGE_ID),
        _request(acceptance_scope_reference="scope:other"),
        _request(completeness_reference="history-snapshot:2"),
    )
    variant_ids = set()
    for request in variants:
        result = application.interpret_governed_knowledge_acceptance_history(request)
        assert result.interpretation is not None
        variant_ids.add(result.interpretation.governed_knowledge_acceptance_history_interpretation_id)
    assert replay.interpretation.governed_knowledge_acceptance_history_interpretation_id not in variant_ids
    assert len(variant_ids) == len(variants)


def test_a19_inputs_and_results_are_immutable_without_current_state() -> None:
    decision = _decision()
    request = _request((decision,))
    result = application.interpret_governed_knowledge_acceptance_history(request)
    assert request.acceptance_decisions == (decision,)
    assert result.interpretation is not None
    forbidden = {"current_acceptance_state", "lifecycle_status", "winner"}
    assert forbidden.isdisjoint({item.name for item in fields(result.interpretation)})
    for value in (request, result, result.interpretation):
        with pytest.raises(FrozenInstanceError):
            value.changed = True  # type: ignore[attr-defined]


def test_a20_production_has_no_forbidden_dependencies_side_effects_or_extra_constants() -> None:
    expected_constants = {
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_ID": "rcis-governed-knowledge-acceptance-history-interpretation",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_POLICY_VERSION": "1.0.0",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_RECORDED": "recorded",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_RESULT_REJECTED": "rejected",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_POLICY": "unsupported_interpretation_policy",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_COMPLETENESS_SCOPE": "unsupported_completeness_scope",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_UNSUPPORTED_ACCEPTANCE_SCOPE": "unsupported_acceptance_scope",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_SUBJECT_MISMATCH": "acceptance_decision_subject_mismatch",
        "GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_REJECTION_REASONS": (
            "unsupported_interpretation_policy",
            "unsupported_completeness_scope",
            "unsupported_acceptance_scope",
            "acceptance_decision_subject_mismatch",
        ),
    }
    actual_constants = {
        name: value
        for name, value in vars(application).items()
        if name.isupper() and not name.startswith("_")
    }
    assert actual_constants == expected_constants
    public_defined = {
        name
        for name, value in vars(application).items()
        if not name.startswith("_")
        and (inspect.isclass(value) or inspect.isfunction(value))
        and getattr(value, "__module__", None) == application.__name__
    }
    assert public_defined == {
        "GovernedKnowledgeAcceptanceHistoryInterpretationRequest",
        "GovernedKnowledgeAcceptanceHistoryInterpretationResult",
        "interpret_governed_knowledge_acceptance_history",
    }
    source_path = Path(application.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    forbidden = {
        "pathlib", "os", "sqlite3", "subprocess", "socket", "requests",
        "httpx", "uuid", "random", "logging", "time", "prompting", "knowledge",
    }
    assert forbidden.isdisjoint(imported_roots)
