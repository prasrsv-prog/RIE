from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
import inspect

import pytest

import rie.infrastructure.in_memory_evidence_repository as adapter_module
from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceDiagnostic,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.infrastructure.in_memory_evidence_repository import (
    InMemoryEvidenceRepository,
)
from rie.interfaces.evidence_repository import (
    EvidenceRepository,
    EvidenceWriteRequest,
)


FIXED_TIME = datetime(
    2026,
    7,
    12,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


def _build_request(
    *,
    fact_suffix: str = "base",
    accepted_by: str = "reviewer",
    acceptance_reason: str = "approved",
    review_record_id: str = "review-1",
    accepted_at: datetime = FIXED_TIME,
    evidence_diagnostics: tuple[EvidenceDiagnostic, ...] = (),
    acceptance_diagnostics: tuple[
        AcceptanceDiagnostic,
        ...,
    ] = (),
) -> EvidenceWriteRequest:
    candidate_digest = f"candidate-{fact_suffix}"
    payload_digest = f"payload-{fact_suffix}"
    source_digest = f"source-{fact_suffix}"
    producer_output_digest = f"producer-{fact_suffix}"

    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version="1.0.0",
        candidate_snapshot_digest=candidate_digest,
        candidate_source_id="source-1",
        candidate_producer_name="producer",
        candidate_producer_version="1.0.0",
        candidate_payload_digest=payload_digest,
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id="source-1",
        source_path="official/source.pdf",
        source_type="pdf",
        document_classification="brand_knowledge_spec",
        authority_status="source_of_truth_candidate",
        lifecycle_status="locked",
        evidence_eligibility="eligible",
        source_content_digest=source_digest,
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name="producer",
        producer_version="1.0.0",
        producer_kind="deterministic",
        producer_contract_version="1.0.0",
    )
    factual_payload = EvidencePayload(
        payload_type="text",
        payload_schema_version="1.0.0",
        payload=(("text", "fact"),),
        payload_digest=payload_digest,
        locator=EvidenceLocator(
            locator_type="page",
            locator_value=1,
            locator_schema_version="1.0.0",
        ),
    )
    provenance = EvidenceProvenance(
        collection_id="collection-1",
        producer_output_digest=producer_output_digest,
        lineage=("candidate-1",),
        observed_at=FIXED_TIME,
        source_registry_version="1.0.0",
    )
    eligibility_result = AcceptedEligibilityResult(
        decision="eligible",
        policy_id="eligibility-policy",
        policy_version="1.0.0",
        candidate_snapshot_digest=candidate_digest,
        source_id="source-1",
        reason_codes=("eligible",),
        evaluated_at=FIXED_TIME,
        evaluated_by="reviewer",
        diagnostics=(),
    )
    provisional_materialization = EvidenceMaterializationRecord(
        materializer_id="materializer",
        materializer_version="1.0.0",
        materialized_at=accepted_at,
        acceptance_record_id=f"ar1_{'0' * 64}",
        accepted_by=accepted_by,
        acceptance_reason=acceptance_reason,
        review_record_id=review_record_id,
        identity_policy_id="rcis-evidence-identity",
        identity_policy_version="1.0.0",
    )
    provisional_evidence = AcceptedEvidence(
        evidence_id=f"ev1_{'0' * 64}",
        contract_version="1.0.0",
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=provisional_materialization,
        diagnostics=evidence_diagnostics,
    )
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(
            provisional_evidence
        )
    )
    provisional_acceptance = AcceptanceRecord(
        acceptance_record_id=f"ar1_{'0' * 64}",
        contract_version="1.0.0",
        evidence_id=evidence_identity.evidence_id,
        accepted_by=accepted_by,
        acceptance_reason=acceptance_reason,
        review_record_id=review_record_id,
        accepted_at=accepted_at,
        acceptance_policy_id="acceptance-policy",
        acceptance_policy_version="1.0.0",
        evidence_identity_policy_id="rcis-evidence-identity",
        evidence_identity_policy_version="1.0.0",
        materializer_id="materializer",
        materializer_version="1.0.0",
        diagnostics=acceptance_diagnostics,
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(
            provisional_acceptance
        )
    )
    materialization = replace(
        provisional_materialization,
        acceptance_record_id=(
            acceptance_identity.acceptance_record_id
        ),
    )
    accepted_evidence = replace(
        provisional_evidence,
        evidence_id=evidence_identity.evidence_id,
        materialization_record=materialization,
    )
    acceptance_record = replace(
        provisional_acceptance,
        acceptance_record_id=(
            acceptance_identity.acceptance_record_id
        ),
    )
    return EvidenceWriteRequest(
        accepted_evidence=accepted_evidence,
        canonical_evidence_bytes_digest=(
            evidence_identity.digest_hex
        ),
        acceptance_record=acceptance_record,
        canonical_acceptance_bytes_digest=(
            acceptance_identity.digest_hex
        ),
        repository_contract_version="1.0.0",
        expected_identity_policy_id="rcis-evidence-identity",
        expected_identity_policy_version="1.0.0",
    )


def _with_evidence_diagnostic(
    request: EvidenceWriteRequest,
) -> EvidenceWriteRequest:
    diagnostic = EvidenceDiagnostic(
        code="stored-diagnostic",
        severity="info",
        message="stored diagnostic changed",
        field="diagnostics",
        source="test",
    )
    return replace(
        request,
        accepted_evidence=replace(
            request.accepted_evidence,
            diagnostics=(diagnostic,),
        ),
    )


def _with_acceptance_diagnostic(
    request: EvidenceWriteRequest,
) -> EvidenceWriteRequest:
    diagnostic = AcceptanceDiagnostic(
        code="governance-diagnostic",
        severity="warning",
        message="governance diagnostic changed",
        field="diagnostics",
        source="test",
    )
    return replace(
        request,
        acceptance_record=replace(
            request.acceptance_record,
            diagnostics=(diagnostic,),
        ),
    )


def _factual_projection_collision(
    base: EvidenceWriteRequest,
) -> EvidenceWriteRequest:
    different = _build_request(fact_suffix="different")
    accepted_evidence = replace(
        different.accepted_evidence,
        evidence_id=base.accepted_evidence.evidence_id,
    )
    acceptance_record = replace(
        different.acceptance_record,
        evidence_id=base.accepted_evidence.evidence_id,
    )
    return EvidenceWriteRequest(
        accepted_evidence=accepted_evidence,
        canonical_evidence_bytes_digest=(
            base.canonical_evidence_bytes_digest
        ),
        acceptance_record=acceptance_record,
        canonical_acceptance_bytes_digest=(
            different.canonical_acceptance_bytes_digest
        ),
        repository_contract_version="1.0.0",
        expected_identity_policy_id="rcis-evidence-identity",
        expected_identity_policy_version="1.0.0",
    )


def _acceptance_projection_collision(
    base: EvidenceWriteRequest,
) -> EvidenceWriteRequest:
    different = _build_request(
        accepted_by="other-reviewer",
        acceptance_reason="other-reason",
        review_record_id="review-2",
        accepted_at=FIXED_TIME + timedelta(seconds=1),
    )
    acceptance_record = replace(
        different.acceptance_record,
        acceptance_record_id=(
            base.acceptance_record.acceptance_record_id
        ),
    )
    materialization = replace(
        different.accepted_evidence.materialization_record,
        acceptance_record_id=(
            base.acceptance_record.acceptance_record_id
        ),
    )
    accepted_evidence = replace(
        different.accepted_evidence,
        evidence_id=base.accepted_evidence.evidence_id,
        materialization_record=materialization,
    )
    acceptance_record = replace(
        acceptance_record,
        evidence_id=base.accepted_evidence.evidence_id,
    )
    return EvidenceWriteRequest(
        accepted_evidence=accepted_evidence,
        canonical_evidence_bytes_digest=(
            base.canonical_evidence_bytes_digest
        ),
        acceptance_record=acceptance_record,
        canonical_acceptance_bytes_digest=(
            base.canonical_acceptance_bytes_digest
        ),
        repository_contract_version="1.0.0",
        expected_identity_policy_id="rcis-evidence-identity",
        expected_identity_policy_version="1.0.0",
    )


def _forge_request(
    request: EvidenceWriteRequest,
    **changes: object,
) -> EvidenceWriteRequest:
    forged = object.__new__(EvidenceWriteRequest)
    for field in fields(EvidenceWriteRequest):
        object.__setattr__(
            forged,
            field.name,
            changes.get(
                field.name,
                getattr(request, field.name),
            ),
        )
    return forged


def test_adapter_has_exact_protocol_method_names() -> None:
    public_methods = {
        name
        for name, value in (
            InMemoryEvidenceRepository.__dict__.items()
        )
        if inspect.isfunction(value)
        and not name.startswith("_")
    }

    assert public_methods == {
        "get_evidence",
        "get_acceptance_record",
        "list_acceptance_records",
        "classify_write",
        "write",
    }


def test_adapter_is_structurally_assignable_to_protocol() -> None:
    repository: EvidenceRepository = (
        InMemoryEvidenceRepository()
    )

    assert callable(repository.write)


@pytest.mark.parametrize(
    "method_name",
    (
        "update",
        "delete",
        "replace",
        "upsert",
        "merge",
        "compact",
        "bulk_write",
        "clear",
        "reset",
        "seed",
        "load",
        "dump",
        "export",
    ),
)
def test_adapter_excludes_forbidden_public_methods(
    method_name: str,
) -> None:
    assert not hasattr(
        InMemoryEvidenceRepository,
        method_name,
    )


@pytest.mark.parametrize(
    ("lookup_name", "identifier"),
    (
        ("get_evidence", f"ev1_{'1' * 64}"),
        ("get_acceptance_record", f"ar1_{'2' * 64}"),
        ("list_acceptance_records", f"ev1_{'3' * 64}"),
    ),
)
def test_empty_repository_returns_not_found(
    lookup_name: str,
    identifier: str,
) -> None:
    repository = InMemoryEvidenceRepository()

    result = getattr(repository, lookup_name)(identifier)

    assert result.status == "not_found"


@pytest.mark.parametrize(
    ("lookup_name", "identifier"),
    (
        ("get_evidence", "invalid"),
        ("get_acceptance_record", "invalid"),
        ("list_acceptance_records", "invalid"),
    ),
)
def test_lookup_rejects_invalid_identifiers_before_state_access(
    lookup_name: str,
    identifier: str,
) -> None:
    repository = InMemoryEvidenceRepository()

    with pytest.raises(ValueError, match="invalid format"):
        getattr(repository, lookup_name)(identifier)


def test_new_evidence_write_inserts_fact_and_acceptance() -> None:
    repository = InMemoryEvidenceRepository()
    request = _build_request()

    result = repository.write(request)

    assert result.status == "inserted_new_evidence"
    assert result.classification == "new_evidence"
    assert result.mutation_performed is True
    assert (
        repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).accepted_evidence
        == request.accepted_evidence
    )
    assert (
        repository.get_acceptance_record(
            request.acceptance_record.acceptance_record_id
        ).acceptance_record
        == request.acceptance_record
    )


def test_retrieval_preserves_canonical_digests() -> None:
    repository = InMemoryEvidenceRepository()
    request = _build_request()
    repository.write(request)

    evidence = repository.get_evidence(
        request.accepted_evidence.evidence_id
    )
    acceptance = repository.get_acceptance_record(
        request.acceptance_record.acceptance_record_id
    )

    assert (
        evidence.canonical_evidence_bytes_digest
        == request.canonical_evidence_bytes_digest
    )
    assert (
        acceptance.canonical_acceptance_bytes_digest
        == request.canonical_acceptance_bytes_digest
    )


def test_same_fact_new_acceptance_appends_without_replacing_fact() -> None:
    repository = InMemoryEvidenceRepository()
    first = _build_request()
    second = _build_request(
        accepted_by="second-reviewer",
        acceptance_reason="second approval",
        review_record_id="review-2",
        accepted_at=FIXED_TIME + timedelta(seconds=1),
    )
    repository.write(first)

    result = repository.write(second)
    evidence = repository.get_evidence(
        first.accepted_evidence.evidence_id
    )

    assert result.status == "appended_acceptance_record"
    assert result.classification == "same_fact_new_acceptance"
    assert result.mutation_performed is True
    assert evidence.accepted_evidence == first.accepted_evidence


def test_acceptance_records_are_returned_in_lexicographic_order() -> None:
    repository = InMemoryEvidenceRepository()
    requests = (
        _build_request(
            accepted_by="reviewer-c",
            review_record_id="review-c",
            accepted_at=FIXED_TIME + timedelta(seconds=3),
        ),
        _build_request(
            accepted_by="reviewer-a",
            review_record_id="review-a",
            accepted_at=FIXED_TIME + timedelta(seconds=1),
        ),
        _build_request(
            accepted_by="reviewer-b",
            review_record_id="review-b",
            accepted_at=FIXED_TIME + timedelta(seconds=2),
        ),
    )
    for request in requests:
        repository.write(request)

    result = repository.list_acceptance_records(
        requests[0].accepted_evidence.evidence_id
    )
    record_ids = tuple(
        record.acceptance_record_id
        for record in result.acceptance_records
    )

    assert result.status == "found"
    assert record_ids == tuple(sorted(record_ids))


def test_exact_replay_does_not_mutate() -> None:
    repository = InMemoryEvidenceRepository()
    request = _build_request()
    repository.write(request)

    result = repository.write(request)

    assert result.status == "unchanged_exact_replay"
    assert result.classification == "exact_replay"
    assert result.mutation_performed is False


@pytest.mark.parametrize(
    "governance_variant",
    (
        _with_evidence_diagnostic,
        _with_acceptance_diagnostic,
    ),
)
def test_governance_replay_is_limited_to_identity_exclusions(
    governance_variant: object,
) -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)

    result = repository.write(governance_variant(base))

    assert result.status == "unchanged_governance_replay"
    assert result.classification == "governance_replay"
    assert result.mutation_performed is False


def test_classify_write_performs_no_mutation() -> None:
    repository = InMemoryEvidenceRepository()
    request = _build_request()

    classification = repository.classify_write(request)

    assert classification.classification == "new_evidence"
    assert (
        repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status
        == "not_found"
    )


def test_write_reclassifies_current_state_under_lock() -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    conflicting = _factual_projection_collision(base)

    before = repository.classify_write(base)
    repository.write(conflicting)
    after = repository.write(base)

    assert before.classification == "new_evidence"
    assert after.classification == "identity_collision"
    assert after.status == "rejected_identity_collision"


def test_factual_projection_collision_is_rejected() -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)

    result = repository.write(
        _factual_projection_collision(base)
    )

    assert result.classification == "identity_collision"
    assert result.status == "rejected_identity_collision"
    assert result.mutation_performed is False


def test_acceptance_projection_collision_is_rejected() -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)

    result = repository.write(
        _acceptance_projection_collision(base)
    )

    assert result.classification == "acceptance_collision"
    assert result.status == "rejected_acceptance_collision"
    assert result.mutation_performed is False


@pytest.mark.parametrize(
    ("field_name", "expected_classification"),
    (
        (
            "canonical_evidence_bytes_digest",
            "identity_collision",
        ),
        (
            "canonical_acceptance_bytes_digest",
            "acceptance_collision",
        ),
    ),
)
def test_stored_digest_collisions_fail_closed(
    field_name: str,
    expected_classification: str,
) -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)
    forged = _forge_request(
        base,
        **{field_name: "f" * 64},
    )

    result = repository.write(forged)

    assert result.classification == expected_classification
    assert result.mutation_performed is False


@pytest.mark.parametrize(
    "conflicting_factory",
    (
        _factual_projection_collision,
        _acceptance_projection_collision,
    ),
)
def test_rejected_write_leaves_no_partial_mutation(
    conflicting_factory: object,
) -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)
    before_evidence = repository.get_evidence(
        base.accepted_evidence.evidence_id
    )
    before_acceptances = repository.list_acceptance_records(
        base.accepted_evidence.evidence_id
    )

    repository.write(conflicting_factory(base))

    assert (
        repository.get_evidence(
            base.accepted_evidence.evidence_id
        )
        == before_evidence
    )
    assert (
        repository.list_acceptance_records(
            base.accepted_evidence.evidence_id
        )
        == before_acceptances
    )


def test_concurrent_identical_writes_commit_once() -> None:
    repository = InMemoryEvidenceRepository()
    request = _build_request()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = tuple(
            executor.map(
                repository.write,
                (request,) * 8,
            )
        )

    statuses = tuple(result.status for result in results)

    assert statuses.count("inserted_new_evidence") == 1
    assert statuses.count("unchanged_exact_replay") == 7


def test_concurrent_conflicting_writes_reject_one_collision() -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    conflicting = _factual_projection_collision(base)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(
            executor.map(
                repository.write,
                (base, conflicting),
            )
        )

    statuses = {result.status for result in results}

    assert statuses == {
        "inserted_new_evidence",
        "rejected_identity_collision",
    }


def test_separate_instances_do_not_share_state() -> None:
    first_repository = InMemoryEvidenceRepository()
    second_repository = InMemoryEvidenceRepository()
    request = _build_request()
    first_repository.write(request)

    assert (
        second_repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status
        == "not_found"
    )


def test_invalid_request_type_is_rejected_before_state_access() -> None:
    repository = InMemoryEvidenceRepository()

    with pytest.raises(ValueError, match="exact EvidenceWriteRequest"):
        repository.write(object())


def test_adapter_never_emits_semantic_candidate_classifications() -> None:
    repository = InMemoryEvidenceRepository()
    base = _build_request()
    repository.write(base)

    classifications = {
        repository.classify_write(
            _factual_projection_collision(base)
        ).classification,
        repository.classify_write(
            _acceptance_projection_collision(base)
        ).classification,
    }

    assert classifications.isdisjoint(
        {
            "semantic_duplicate_candidate",
            "conflicting_evidence_candidate",
            "superseding_evidence_candidate",
        }
    )


def test_adapter_source_has_no_durable_persistence_or_retry_behavior() -> None:
    source = inspect.getsource(adapter_module)
    forbidden_fragments = (
        "pathlib",
        "sqlite3",
        "pickle",
        "shelve",
        "json",
        "requests",
        "httpx",
        "socket",
        "uuid",
        "random",
        "sleep(",
        "retry",
        "Knowledge",
        "PromptCandidate",
        "open(",
    )

    assert all(
        fragment not in source
        for fragment in forbidden_fragments
    )


def test_adapter_has_no_public_state_property() -> None:
    public_names = {
        name
        for name in InMemoryEvidenceRepository.__dict__
        if not name.startswith("_")
    }

    assert public_names == {
        "get_evidence",
        "get_acceptance_record",
        "list_acceptance_records",
        "classify_write",
        "write",
    }
