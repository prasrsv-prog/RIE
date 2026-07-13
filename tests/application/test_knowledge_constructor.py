import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from evidence.evidence import Evidence as LegacyEvidence
from knowledge.text_knowledge import TextKnowledge
from rie.application import knowledge_constructor as constructor_module
from rie.application.evidence_candidate import EvidenceCandidate
from rie.application.knowledge_constructor import (
    VERBATIM_TEXT_RULE_ID,
    VERBATIM_TEXT_RULE_VERSION,
    KnowledgeConstructionRequest,
    KnowledgeConstructionResult,
    construct_knowledge_candidate,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)


FIXED_TIME = datetime(2026, 7, 13, 5, 0, tzinfo=timezone.utc)


def _ids(seed: str) -> tuple[str, str]:
    return "ev1_" + seed * 64, "ar1_" + seed * 64


def _accepted_evidence(
    *,
    seed: str = "1",
    text: object = "  Exact Fact\n",
    payload_type: str = "text",
    payload_schema_version: str = "1.0.0",
    payload: object | None = None,
    acceptance_record_id: str | None = None,
) -> AcceptedEvidence:
    evidence_id, default_acceptance_id = _ids(seed)
    acceptance_id = acceptance_record_id or default_acceptance_id
    payload_value = (("text", text),) if payload is None else payload
    source_digest = seed * 64
    payload_digest = chr(ord(seed) + 1) * 64
    candidate_digest = chr(ord(seed) + 2) * 64
    return AcceptedEvidence(
        evidence_id=evidence_id,
        contract_version="accepted-evidence-v1",
        candidate_reference=EvidenceCandidateReference(
            candidate_contract_version="evidence-candidate-v1",
            candidate_snapshot_digest=candidate_digest,
            candidate_source_id=f"source-{seed}",
            candidate_producer_name="producer",
            candidate_producer_version="1.0.0",
            candidate_payload_digest=payload_digest,
        ),
        source_snapshot=EvidenceSourceSnapshot(
            source_id=f"source-{seed}",
            source_path=f"official/source-{seed}.pdf",
            source_type="pdf",
            document_classification="brand_knowledge_spec",
            authority_status="official",
            lifecycle_status="active",
            evidence_eligibility="eligible",
            source_content_digest=source_digest,
        ),
        producer_snapshot=EvidenceProducerSnapshot(
            producer_name="producer",
            producer_version="1.0.0",
            producer_kind="deterministic",
            producer_contract_version="1.0.0",
        ),
        factual_payload=EvidencePayload(
            payload_type=payload_type,
            payload_schema_version=payload_schema_version,
            payload=payload_value,
            payload_digest=payload_digest,
            locator=EvidenceLocator(
                locator_type="page",
                locator_value=(int(seed), "paragraph-2"),
                locator_schema_version="1.0.0",
            ),
        ),
        provenance=EvidenceProvenance(
            collection_id=f"collection-{seed}",
            producer_output_digest=chr(ord(seed) + 3) * 64,
            lineage=("repository", "extraction", "accepted-evidence"),
            observed_at=FIXED_TIME,
            source_registry_version="1.0.0",
        ),
        eligibility_result=AcceptedEligibilityResult(
            decision="eligible",
            policy_id="eligibility-policy",
            policy_version="1.0.0",
            candidate_snapshot_digest=candidate_digest,
            source_id=f"source-{seed}",
            reason_codes=("eligible_source",),
            evaluated_at=FIXED_TIME,
            evaluated_by="reviewer",
            diagnostics=(),
        ),
        materialization_record=EvidenceMaterializationRecord(
            materializer_id="accepted-evidence-materializer",
            materializer_version="1.0.0",
            materialized_at=FIXED_TIME,
            acceptance_record_id=acceptance_id,
            accepted_by="reviewer",
            acceptance_reason="verified fact",
            review_record_id="review-1",
            identity_policy_id="rcis-evidence-identity",
            identity_policy_version="1.0.0",
        ),
        diagnostics=(),
    )


def _acceptance_record(
    evidence: AcceptedEvidence,
    *,
    acceptance_record_id: str | None = None,
    review_record_id: str = "review-1",
    **changes: object,
) -> AcceptanceRecord:
    values = {
        "acceptance_record_id": (
            acceptance_record_id
            or evidence.materialization_record.acceptance_record_id
        ),
        "contract_version": "acceptance-record-v1",
        "evidence_id": evidence.evidence_id,
        "accepted_by": "reviewer",
        "acceptance_reason": "verified fact",
        "review_record_id": review_record_id,
        "accepted_at": FIXED_TIME,
        "acceptance_policy_id": "acceptance-policy",
        "acceptance_policy_version": "1.0.0",
        "evidence_identity_policy_id": "rcis-evidence-identity",
        "evidence_identity_policy_version": "1.0.0",
        "materializer_id": "accepted-evidence-materializer",
        "materializer_version": "1.0.0",
        "diagnostics": (),
    }
    values.update(changes)
    return AcceptanceRecord(**values)


def _request(
    evidence: AcceptedEvidence | None = None,
    records: tuple[AcceptanceRecord, ...] | None = None,
    **changes: object,
) -> KnowledgeConstructionRequest:
    accepted = evidence or _accepted_evidence()
    values = {
        "accepted_evidence": accepted,
        "acceptance_records": records or (_acceptance_record(accepted),),
        "construction_rule_id": VERBATIM_TEXT_RULE_ID,
        "construction_rule_version": VERBATIM_TEXT_RULE_VERSION,
    }
    values.update(changes)
    return KnowledgeConstructionRequest(**values)


def _reason(result: KnowledgeConstructionResult) -> str:
    assert result.decision == "rejected"
    assert result.knowledge_candidate is None
    assert len(result.reason_codes) == 1
    assert result.diagnostics[0].code == result.reason_codes[0]
    return result.reason_codes[0]


def test_constructs_exact_text_candidate_and_preserves_statement() -> None:
    evidence = _accepted_evidence(text="  Exact Fact\n")
    result = construct_knowledge_candidate(_request(evidence))

    assert result.decision == "constructed"
    assert result.reason_codes == ()
    assert result.diagnostics == ()
    assert result.knowledge_candidate is not None
    assert result.knowledge_candidate.statement == "  Exact Fact\n"
    assert result.knowledge_candidate.statement_type == "verbatim_text_fact"


def test_complete_provenance_is_preserved_exactly() -> None:
    evidence = _accepted_evidence()
    second_id = "ar1_" + "9" * 64
    records = (
        _acceptance_record(
            evidence,
            acceptance_record_id=second_id,
            review_record_id="review-2",
        ),
        _acceptance_record(evidence),
    )
    result = construct_knowledge_candidate(_request(evidence, records))
    support = result.knowledge_candidate.support[0]

    assert support.evidence_id == evidence.evidence_id
    assert support.acceptance_record_ids == tuple(
        sorted((evidence.materialization_record.acceptance_record_id, second_id))
    )
    assert support.acceptance_review_record_ids == ("review-1", "review-2")
    assert support.source_id == evidence.source_snapshot.source_id
    assert support.source_content_digest == (
        evidence.source_snapshot.source_content_digest
    )
    assert support.payload_digest == evidence.factual_payload.payload_digest
    assert support.locator_type == evidence.factual_payload.locator.locator_type
    assert support.locator_value == evidence.factual_payload.locator.locator_value
    assert support.locator_schema_version == (
        evidence.factual_payload.locator.locator_schema_version
    )


def test_source_governance_is_provenance_not_candidate_promotion() -> None:
    result = construct_knowledge_candidate(_request())
    candidate = result.knowledge_candidate
    support = candidate.support[0]

    assert support.source_authority_status == "official"
    assert support.source_lifecycle_status == "active"
    assert candidate.authority_status == "unassessed"
    assert candidate.lifecycle_status == "candidate"
    assert candidate.review_status == "pending_review"
    assert candidate.conflict_status == "not_assessed"
    assert candidate.conflict_ids == ()


def test_exact_replay_is_deterministic() -> None:
    request = _request()
    first = construct_knowledge_candidate(request)
    second = construct_knowledge_candidate(request)
    assert first == second
    assert first.knowledge_candidate.knowledge_candidate_id == (
        second.knowledge_candidate.knowledge_candidate_id
    )


def test_acceptance_record_order_does_not_affect_candidate_or_inputs() -> None:
    evidence = _accepted_evidence()
    first_record = _acceptance_record(evidence)
    second_record = _acceptance_record(
        evidence,
        acceptance_record_id="ar1_" + "9" * 64,
        review_record_id="review-2",
    )
    forward_records = (first_record, second_record)
    reverse_records = tuple(reversed(forward_records))

    forward = construct_knowledge_candidate(_request(evidence, forward_records))
    reverse = construct_knowledge_candidate(_request(evidence, reverse_records))

    assert forward.knowledge_candidate == reverse.knowledge_candidate
    assert forward_records == (first_record, second_record)
    assert reverse_records == (second_record, first_record)


def test_missing_materialization_acceptance_record_is_rejected() -> None:
    evidence = _accepted_evidence()
    other = _acceptance_record(
        evidence,
        acceptance_record_id="ar1_" + "9" * 64,
    )
    assert _reason(
        construct_knowledge_candidate(_request(evidence, (other,)))
    ) == "missing_materialization_acceptance_record"


def test_acceptance_record_for_another_evidence_is_rejected() -> None:
    evidence = _accepted_evidence()
    other_evidence_id, _ = _ids("8")
    record = _acceptance_record(evidence, evidence_id=other_evidence_id)
    assert _reason(
        construct_knowledge_candidate(_request(evidence, (record,)))
    ) == "acceptance_record_evidence_id_mismatch"


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("accepted_by", "other-reviewer"),
        ("acceptance_reason", "other reason"),
        ("review_record_id", "review-2"),
        ("materializer_id", "other-materializer"),
        ("materializer_version", "2.0.0"),
        ("accepted_at", datetime(2026, 7, 13, 6, 0, tzinfo=timezone.utc)),
    ),
)
def test_materialization_acceptance_mismatch_is_rejected(
    field_name: str,
    bad_value: object,
) -> None:
    evidence = _accepted_evidence()
    record = _acceptance_record(evidence, **{field_name: bad_value})
    assert _reason(
        construct_knowledge_candidate(_request(evidence, (record,)))
    ) == "materialization_acceptance_mismatch"


def test_duplicate_acceptance_record_id_is_rejected_without_repair() -> None:
    evidence = _accepted_evidence()
    record = _acceptance_record(evidence)
    assert _reason(
        construct_knowledge_candidate(_request(evidence, (record, record)))
    ) == "duplicate_acceptance_record_id"


@pytest.mark.parametrize(
    "request_changes",
    (
        {"construction_rule_id": "unsupported-rule"},
        {"construction_rule_version": "2.0.0"},
    ),
)
def test_unsupported_rule_is_rejected(request_changes: dict[str, str]) -> None:
    assert _reason(
        construct_knowledge_candidate(_request(**request_changes))
    ) == "unsupported_construction_rule"


@pytest.mark.parametrize(
    "evidence,expected_reason",
    (
        (
            _accepted_evidence(payload_type="document_structural_metadata"),
            "unsupported_payload_type",
        ),
        (
            _accepted_evidence(payload_schema_version="2.0.0"),
            "unsupported_payload_schema",
        ),
        (_accepted_evidence(payload=()), "unsupported_payload_shape"),
        (
            _accepted_evidence(payload=(("extra", "x"), ("text", "fact"))),
            "unsupported_payload_shape",
        ),
        (_accepted_evidence(payload=(("other", "fact"),)), "missing_text"),
        (_accepted_evidence(payload=(("text", 3),)), "non_string_text"),
        (_accepted_evidence(payload=(("text", ""),)), "empty_text"),
        (_accepted_evidence(payload=(("text", "   "),)), "empty_text"),
    ),
)
def test_unsupported_payloads_are_explicitly_rejected(
    evidence: AcceptedEvidence,
    expected_reason: str,
) -> None:
    assert _reason(
        construct_knowledge_candidate(_request(evidence))
    ) == expected_reason


@pytest.mark.parametrize(
    "bad_accepted_evidence",
    (
        {},
        "official/source.pdf",
        Path("official/source.pdf"),
        object.__new__(EvidenceCandidate),
        object.__new__(LegacyEvidence),
        TextKnowledge("source.txt", "fact", 4, 0),
        object(),
    ),
)
def test_request_rejects_raw_legacy_path_extraction_and_wrong_inputs(
    bad_accepted_evidence: object,
) -> None:
    evidence = _accepted_evidence()
    with pytest.raises(ValueError, match="exact AcceptedEvidence"):
        KnowledgeConstructionRequest(
            accepted_evidence=bad_accepted_evidence,
            acceptance_records=(_acceptance_record(evidence),),
            construction_rule_id=VERBATIM_TEXT_RULE_ID,
            construction_rule_version=VERBATIM_TEXT_RULE_VERSION,
        )


def test_request_and_constructor_reject_duck_typed_inputs() -> None:
    class DuckAcceptedEvidence:
        evidence_id = _ids("1")[0]

    class DuckRequest:
        pass

    evidence = _accepted_evidence()
    with pytest.raises(ValueError, match="exact AcceptedEvidence"):
        KnowledgeConstructionRequest(
            DuckAcceptedEvidence(),
            (_acceptance_record(evidence),),
            VERBATIM_TEXT_RULE_ID,
            VERBATIM_TEXT_RULE_VERSION,
        )
    with pytest.raises(ValueError, match="exact KnowledgeConstructionRequest"):
        construct_knowledge_candidate(DuckRequest())


@pytest.mark.parametrize(
    "bad_records",
    ([], (), (object(),)),
)
def test_request_requires_non_empty_exact_acceptance_record_tuple(
    bad_records: object,
) -> None:
    evidence = _accepted_evidence()
    with pytest.raises(ValueError, match="acceptance_records"):
        KnowledgeConstructionRequest(
            evidence,
            bad_records,
            VERBATIM_TEXT_RULE_ID,
            VERBATIM_TEXT_RULE_VERSION,
        )


def test_request_and_result_contracts_are_frozen() -> None:
    request = _request()
    result = construct_knowledge_candidate(request)
    with pytest.raises(FrozenInstanceError):
        request.construction_rule_id = "changed"
    with pytest.raises(FrozenInstanceError):
        result.decision = "rejected"


def test_constructor_imports_no_forbidden_boundary() -> None:
    source_path = Path(constructor_module.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    forbidden_prefixes = (
        "rie.interfaces",
        "rie.infrastructure",
        "knowledge",
        "prompting",
        "evidence",
        "collection",
        "pathlib",
        "sqlite3",
        "requests",
        "pypdf",
        "openai",
    )
    assert not any(
        module == prefix or module.startswith(prefix + ".")
        for module in imported_modules
        for prefix in forbidden_prefixes
    )


def test_no_promotion_acceptance_conflict_or_persistence_behavior() -> None:
    result = construct_knowledge_candidate(_request())
    candidate = result.knowledge_candidate
    assert candidate.authority_status == "unassessed"
    assert candidate.lifecycle_status == "candidate"
    assert candidate.review_status == "pending_review"
    assert candidate.conflict_status == "not_assessed"
    assert not hasattr(candidate, "accept")
    assert not hasattr(candidate, "approve")
    assert not hasattr(candidate, "save")
    assert not hasattr(candidate, "to_prompt_candidate")


def test_inputs_are_unchanged_after_construction_and_rejection() -> None:
    valid_request = _request()
    valid_snapshot = repr(valid_request)
    rejected_request = replace(valid_request, construction_rule_id="unsupported")
    rejected_snapshot = repr(rejected_request)

    construct_knowledge_candidate(valid_request)
    construct_knowledge_candidate(rejected_request)

    assert repr(valid_request) == valid_snapshot
    assert repr(rejected_request) == rejected_snapshot


def test_independent_facts_never_select_or_suppress_each_other() -> None:
    first_request = _request(_accepted_evidence(seed="1", text="Fact one"))
    second_request = _request(_accepted_evidence(seed="5", text="Fact two"))

    first = construct_knowledge_candidate(first_request)
    second = construct_knowledge_candidate(second_request)
    reverse_second = construct_knowledge_candidate(second_request)
    reverse_first = construct_knowledge_candidate(first_request)

    assert first.decision == second.decision == "constructed"
    assert first.knowledge_candidate.statement == "Fact one"
    assert second.knowledge_candidate.statement == "Fact two"
    assert first.knowledge_candidate.knowledge_candidate_id != (
        second.knowledge_candidate.knowledge_candidate_id
    )
    assert reverse_first == first
    assert reverse_second == second
