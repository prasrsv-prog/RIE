import ast
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import rie.application.governed_knowledge_acceptance_decider as application
from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeDiagnostic,
    GovernedKnowledgeIdentityInput,
    compute_governed_knowledge_id,
)
from rie.domain.knowledge_candidate import KnowledgeEvidenceSupport
import rie.domain.governed_knowledge_acceptance_decision as domain


NOW = datetime(2026, 7, 15, 10, 20, 30, 456789, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


def _governed(
    diagnostics: tuple[GovernedKnowledgeDiagnostic, ...] = (),
) -> GovernedKnowledge:
    support = KnowledgeEvidenceSupport(
        evidence_id="ev1_" + "1" * 64,
        acceptance_record_ids=("ar1_" + "2" * 64,),
        acceptance_review_record_ids=("review-1",),
        source_id="source-1",
        source_content_digest="3" * 64,
        source_authority_status="authoritative",
        source_lifecycle_status="active",
        payload_digest="4" * 64,
        locator_type="text-span",
        locator_value="line-1",
        locator_schema_version="1.0.0",
    )
    identity = GovernedKnowledgeIdentityInput(
        contract_version=GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        knowledge_candidate_id="kc1_" + "5" * 64,
        knowledge_candidate_contract_version="knowledge-candidate-v1",
        knowledge_candidate_snapshot_digest="6" * 64,
        statement_type="fact",
        statement="Governed statement.",
        support=(support,),
        knowledge_promotion_prerequisite_evaluation_id="kpe1_" + "7" * 64,
        knowledge_promotion_prerequisite_evaluation_contract_version="knowledge-promotion-prerequisite-evaluation-v1",
        knowledge_promotion_decision_id="kpd1_" + "8" * 64,
        knowledge_promotion_decision_contract_version="knowledge-promotion-decision-v1",
        promotion_decision_outcome="promotion_authorized_for_future_execution",
        authorization_scope="eligible_for_future_promotion_execution_for_declared_scope",
        knowledge_promotion_execution_id="kpx1_" + "9" * 64,
        knowledge_promotion_execution_contract_version="knowledge-promotion-execution-v1",
        promotion_execution_scope="promotion_execution_for_declared_scope",
        promotion_execution_outcome="promotion_execution_completed_for_declared_scope",
        construction_scope=GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
        construction_reference="construction-run-1",
        reason_codes=(REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,),
        constructed_by="constructor",
        constructed_at=NOW - timedelta(hours=1),
        construction_policy_id="rcis-governed-knowledge-construction",
        construction_policy_version="1.0.0",
    )
    return GovernedKnowledge(
        governed_knowledge_id=compute_governed_knowledge_id(identity),
        contract_version=identity.contract_version,
        knowledge_candidate_id=identity.knowledge_candidate_id,
        knowledge_candidate_contract_version=identity.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=identity.knowledge_candidate_snapshot_digest,
        statement_type=identity.statement_type,
        statement=identity.statement,
        support=identity.support,
        knowledge_promotion_prerequisite_evaluation_id=identity.knowledge_promotion_prerequisite_evaluation_id,
        knowledge_promotion_prerequisite_evaluation_contract_version=identity.knowledge_promotion_prerequisite_evaluation_contract_version,
        knowledge_promotion_decision_id=identity.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=identity.knowledge_promotion_decision_contract_version,
        promotion_decision_outcome=identity.promotion_decision_outcome,
        authorization_scope=identity.authorization_scope,
        knowledge_promotion_execution_id=identity.knowledge_promotion_execution_id,
        knowledge_promotion_execution_contract_version=identity.knowledge_promotion_execution_contract_version,
        promotion_execution_scope=identity.promotion_execution_scope,
        promotion_execution_outcome=identity.promotion_execution_outcome,
        construction_scope=identity.construction_scope,
        construction_reference=identity.construction_reference,
        reason_codes=identity.reason_codes,
        constructed_by=identity.constructed_by,
        constructed_at=identity.constructed_at,
        construction_policy_id=identity.construction_policy_id,
        construction_policy_version=identity.construction_policy_version,
        diagnostics=diagnostics,
    )


def _request(**changes: object) -> application.GovernedKnowledgeAcceptanceDecisionRequest:
    values = {
        "governed_knowledge": _governed(),
        "acceptance_scope": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED,
        "acceptance_scope_reference": "release-scope-2026-07",
        "acceptance_outcome": domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
        "reason_codes": (
            domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE,
        ),
        "decided_by": "acceptance-board",
        "decided_at": NOW,
        "acceptance_policy_id": application.GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_ID,
        "acceptance_policy_version": application.GOVERNED_KNOWLEDGE_ACCEPTANCE_POLICY_VERSION,
    }
    values.update(changes)
    return application.GovernedKnowledgeAcceptanceDecisionRequest(**values)


def _reason(result: application.GovernedKnowledgeAcceptanceDecisionResult) -> str:
    assert result.result_status == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_REJECTED
    assert result.acceptance_decision is None
    return result.reason_codes[0]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_a01_request_field_order_acceptance_reference_and_accepted_record() -> None:
    request = _request()
    before = request.governed_knowledge
    result = application.decide_governed_knowledge_acceptance(request)
    assert [item.name for item in fields(request)] == ["governed_knowledge", "acceptance_scope", "acceptance_scope_reference", "acceptance_outcome", "reason_codes", "decided_by", "decided_at", "acceptance_policy_id", "acceptance_policy_version"]
    assert result.result_status == "recorded"
    assert result.acceptance_decision is not None
    assert result.acceptance_decision.acceptance_scope_reference == "release-scope-2026-07"
    assert request.governed_knowledge == before


def test_a02_rejected_is_recorded_domain_outcome() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="rejected", reason_codes=(domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,)))
    assert result.result_status == "recorded" and result.acceptance_decision is not None
    assert result.acceptance_decision.acceptance_outcome == "rejected"


def test_a03_deferred_is_recorded_with_required_reason() -> None:
    reason = domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="deferred", reason_codes=(reason,)))
    assert result.result_status == "recorded" and result.acceptance_decision is not None
    assert result.acceptance_decision.reason_codes == (reason,)


def test_a04_exact_upstream_gk_identity_is_recomputed() -> None:
    governed = _governed()
    object.__setattr__(governed, "governed_knowledge_id", "gk1_" + "0" * 64)
    with pytest.raises(ValueError):
        _request(governed_knowledge=governed)


def test_a05_construction_diagnostics_do_not_change_acceptance_identity() -> None:
    diagnostic = GovernedKnowledgeDiagnostic("construction-info", "info", "message", "field", "source")
    plain = application.decide_governed_knowledge_acceptance(_request(governed_knowledge=_governed()))
    detailed = application.decide_governed_knowledge_acceptance(_request(governed_knowledge=_governed((diagnostic,))))
    assert plain.acceptance_decision is not None and detailed.acceptance_decision is not None
    assert plain.acceptance_decision.governed_knowledge_acceptance_decision_id == detailed.acceptance_decision.governed_knowledge_acceptance_decision_id


def test_a06_unsupported_policy_rejects_first() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_policy_id="other", acceptance_scope="other", acceptance_outcome="other", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY


def test_a07_unsupported_scope_rejects_and_opaque_reference_needs_no_lookup() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_scope="other", acceptance_scope_reference="not-a-registry-key"))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE


def test_a08_unsupported_outcome_rejects_after_scope() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="approved"))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME


def test_a09_accepted_missing_required_reason_rejects() -> None:
    assert _reason(application.decide_governed_knowledge_acceptance(_request(reason_codes=("other",)))) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON


def test_a10_rejected_missing_required_reason_rejects() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="rejected", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON


def test_a11_deferred_missing_required_reason_rejects() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="deferred", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_MISSING_REQUIRED_REASON


def test_a12_combined_failures_return_only_first_rejection() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_scope="other", acceptance_outcome="other", reason_codes=("other",)))
    assert result.reason_codes == (application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE,)
    assert len(result.diagnostics) == 1


def test_a13_policy_precedence_dominates_later_failures() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_policy_version="2", acceptance_scope="other", acceptance_outcome="other", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_POLICY


def test_a14_scope_precedence_dominates_outcome_and_reason() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_scope="other", acceptance_outcome="other", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_SCOPE


def test_a15_outcome_precedence_dominates_missing_reason() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="other", reason_codes=("other",)))
    assert _reason(result) == application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_UNSUPPORTED_OUTCOME


def test_a16_well_formed_unsupported_values_return_results() -> None:
    results = (
        application.decide_governed_knowledge_acceptance(_request(acceptance_policy_id="other")),
        application.decide_governed_knowledge_acceptance(_request(acceptance_scope="other")),
        application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="other")),
    )
    assert all(item.result_status == "rejected" for item in results)


def test_a17_malformed_request_material_raises_before_evaluation() -> None:
    malformed = ({"acceptance_scope_reference": " "}, {"acceptance_scope_reference": 1}, {"reason_codes": []}, {"reason_codes": ("z", "a")}, {"decided_at": datetime(2026, 1, 1)}, {"acceptance_policy_id": ""})
    for changes in malformed:
        with pytest.raises(ValueError):
            _request(**changes)


def test_a18_broken_governed_identity_or_contract_raises() -> None:
    broken_id = _governed()
    object.__setattr__(broken_id, "governed_knowledge_id", "gk1_" + "0" * 64)
    broken_contract = _governed()
    object.__setattr__(broken_contract, "contract_version", "other")
    for value in (broken_id, broken_contract):
        with pytest.raises(ValueError):
            _request(governed_knowledge=value)


def test_a19_raw_ids_paths_wrong_objects_subclasses_and_ducks_fail() -> None:
    class GovernedSubclass(GovernedKnowledge):
        pass
    class Duck:
        governed_knowledge_id = _governed().governed_knowledge_id
    governed = _governed()
    subclass = object.__new__(GovernedSubclass)
    for item in fields(governed):
        object.__setattr__(
            subclass,
            item.name,
            getattr(governed, item.name),
        )
    for value in ({}, governed.governed_knowledge_id, Path("x"), object(), subclass, Duck()):
        with pytest.raises(ValueError):
            _request(governed_knowledge=value)
    with pytest.raises(ValueError):
        application.decide_governed_knowledge_acceptance({})  # type: ignore[arg-type]


def test_a20_reason_values_remain_unchanged_and_collections_fail_closed() -> None:
    reasons = ("additional", domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE)
    request = _request(reason_codes=reasons)
    result = application.decide_governed_knowledge_acceptance(request)
    assert request.reason_codes is reasons
    assert result.acceptance_decision is not None and result.acceptance_decision.reason_codes == reasons
    for bad in (("z", "a"), ("a", "a"), ["a"]):
        with pytest.raises(ValueError):
            _request(reason_codes=bad)


def test_a21_caller_time_preserved_without_clock_uuid_or_randomness() -> None:
    result = application.decide_governed_knowledge_acceptance(_request(decided_at=NOW))
    assert result.acceptance_decision is not None and result.acceptance_decision.decided_at is NOW
    source = (ROOT / "src/rie/application/governed_knowledge_acceptance_decider.py").read_text(encoding="utf-8-sig")
    assert all(token not in source for token in ("datetime.now", "utcnow", "uuid", "random", "secrets"))


def test_a22_exact_result_names_constants_and_recorded_invariants() -> None:
    result = application.decide_governed_knowledge_acceptance(_request())
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_RECORDED == "recorded"
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_RESULT_REJECTED == "rejected"
    assert [item.name for item in fields(result)] == ["result_status", "acceptance_decision", "reason_codes", "diagnostics"]
    assert result.reason_codes == () and result.diagnostics == ()
    assert result.acceptance_decision is not None and result.acceptance_decision.diagnostics == ()
    with pytest.raises(ValueError):
        replace(result, reason_codes=("x",))


def test_a23_exact_rejection_constants_tuple_and_diagnostic_invariants() -> None:
    expected = ("unsupported_acceptance_policy", "unsupported_acceptance_scope", "unsupported_acceptance_outcome", "missing_required_acceptance_reason")
    assert application.GOVERNED_KNOWLEDGE_ACCEPTANCE_REJECTION_REASONS == expected
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_policy_id="other"))
    diagnostic = result.diagnostics[0]
    assert (diagnostic.code, diagnostic.severity, diagnostic.message, diagnostic.field, diagnostic.source) == (expected[0], "warning", "The governed-Knowledge acceptance policy is unsupported.", "request", "governed_knowledge_acceptance_decider")
    with pytest.raises(ValueError):
        replace(result, diagnostics=())


def test_a24_exact_replay_returns_equal_decision_and_identity() -> None:
    first = application.decide_governed_knowledge_acceptance(_request())
    second = application.decide_governed_knowledge_acceptance(_request())
    assert first == second
    assert first.acceptance_decision is not None and second.acceptance_decision is not None
    assert first.acceptance_decision.governed_knowledge_acceptance_decision_id == second.acceptance_decision.governed_knowledge_acceptance_decision_id


def test_a25_materially_different_decisions_coexist_without_selection() -> None:
    accepted = application.decide_governed_knowledge_acceptance(_request())
    rejected = application.decide_governed_knowledge_acceptance(_request(acceptance_outcome="rejected", reason_codes=(domain.GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE,)))
    assert accepted.acceptance_decision is not None and rejected.acceptance_decision is not None
    assert accepted.acceptance_decision != rejected.acceptance_decision


def test_a26_all_values_are_immutable_and_input_is_unchanged() -> None:
    request = _request()
    before = request.governed_knowledge
    result = application.decide_governed_knowledge_acceptance(request)
    for value, name in ((request, "decided_by"), (result, "result_status"), (result.acceptance_decision, "decided_by")):
        with pytest.raises(FrozenInstanceError):
            setattr(value, name, "changed")
    assert request.governed_knowledge == before and isinstance(request.reason_codes, tuple)


def test_a27_construction_does_not_import_or_invoke_acceptance() -> None:
    path = ROOT / "src/rie/application/governed_knowledge_constructor.py"
    imports = _imports(path)
    source = path.read_text(encoding="utf-8-sig")
    assert "rie.domain.governed_knowledge_acceptance_decision" not in imports
    assert "governed_knowledge_acceptance" not in source


def test_a28_scope_reference_has_no_lookup_or_stateful_result() -> None:
    source = (ROOT / "src/rie/application/governed_knowledge_acceptance_decider.py").read_text(encoding="utf-8-sig")
    forbidden = ("repository", "persistence", "serialization", "transaction", "lock", "lifecycle", "authorization_consumption", "lookup(")
    assert all(token not in source.lower() for token in forbidden)
    result = application.decide_governed_knowledge_acceptance(_request(acceptance_scope_reference="opaque-value"))
    assert result.acceptance_decision is not None and result.acceptance_decision.acceptance_scope_reference == "opaque-value"


def test_a29_no_external_or_side_effect_behavior() -> None:
    path = ROOT / "src/rie/application/governed_knowledge_acceptance_decider.py"
    imports = _imports(path)
    forbidden_imports = {"logging", "pathlib", "os", "subprocess", "socket", "random", "uuid", "requests", "sqlite3"}
    assert not imports.intersection(forbidden_imports)
    source = path.read_text(encoding="utf-8-sig").lower()
    for token in ("prompt", " ai ", "business", "creative", "callback", "dispatch", "retry"):
        assert token not in source


def test_a30_exact_import_direction_package_non_import_and_four_file_scope() -> None:
    domain_path = ROOT / "src/rie/domain/governed_knowledge_acceptance_decision.py"
    app_path = ROOT / "src/rie/application/governed_knowledge_acceptance_decider.py"
    domain_imports = _imports(domain_path)
    app_imports = _imports(app_path)
    assert domain_imports == {"dataclasses", "datetime", "hashlib", "json", "math", "re", "unicodedata", "rie.domain.governed_knowledge"}
    assert app_imports == {"dataclasses", "datetime", "rie.domain.governed_knowledge", "rie.domain.governed_knowledge_acceptance_decision"}
    assert "rie.application.governed_knowledge_constructor" not in app_imports
    for init in (ROOT / "src/rie/domain/__init__.py", ROOT / "src/rie/application/__init__.py"):
        assert "governed_knowledge_acceptance" not in init.read_text(encoding="utf-8-sig")
    phase34_basenames = {
        "governed_knowledge_acceptance_decider.py",
        "governed_knowledge_acceptance_decision.py",
        "test_governed_knowledge_acceptance_decider.py",
        "test_governed_knowledge_acceptance_decision.py",
    }
    matches = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*.py")
        if path.name in phase34_basenames
    )
    assert matches == [
        "src/rie/application/governed_knowledge_acceptance_decider.py",
        "src/rie/domain/governed_knowledge_acceptance_decision.py",
        "tests/application/test_governed_knowledge_acceptance_decider.py",
        "tests/domain/test_governed_knowledge_acceptance_decision.py",
    ]
