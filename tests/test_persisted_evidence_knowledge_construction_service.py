from dataclasses import fields, replace
from datetime import datetime, timezone
import hashlib

import pytest

from rie.application.knowledge_constructor import (
    VERBATIM_TEXT_RULE_ID,
    VERBATIM_TEXT_RULE_VERSION,
    KnowledgeConstructionRequest,
)
from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
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
from rie.domain.evidence_identity import (
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_CONTRACT_VERSION,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_ISSUE_MESSAGES,
    EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
    EvidenceRepositoryAuditRecord,
    EvidenceRepositoryIssue,
    EvidenceRepositoryLookupResult,
    EvidenceRepositoryRevision,
)
from rie.persisted_evidence_knowledge_construction import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PersistedEvidenceKnowledgeConstructionRequest,
    construct_knowledge_from_persisted_evidence,
)
from rie.persisted_evidence_knowledge_construction import (
    persisted_evidence_knowledge_construction_service as service_module,
)


FIXED_TIME = datetime(2026, 7, 21, 4, 0, tzinfo=timezone.utc)


def _unchecked(contract_type: type[object], **values: object) -> object:
    instance = object.__new__(contract_type)
    for field in fields(contract_type):
        object.__setattr__(instance, field.name, values[field.name])
    return instance


def _snapshot(**changes: object) -> EvidenceEligibilitySnapshot:
    values: dict[str, object] = {
        "contract_version": EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        "source_id": "source-1",
        "source_path": "official/source-1.pdf",
        "source_checksum": "a" * 64,
        "source_type": "pdf",
        "document_classification": "brand_knowledge_spec",
        "authority_status": "official",
        "lifecycle_status": "active",
        "evidence_eligibility": "eligible",
        "evidence_collection_allowed": True,
        "requires_review": False,
        "reason": "eligible official source",
        "policy_id": "evidence-eligibility-policy",
        "policy_version": "1.0.0",
        "registry_version": "1.0.0",
    }
    values.update(changes)
    return EvidenceEligibilitySnapshot(**values)


def _unchecked_snapshot(**changes: object) -> EvidenceEligibilitySnapshot:
    valid = _snapshot()
    values = {
        field.name: getattr(valid, field.name)
        for field in fields(EvidenceEligibilitySnapshot)
    }
    values.update(changes)
    return _unchecked(EvidenceEligibilitySnapshot, **values)


def _provenance(
    snapshot: EvidenceEligibilitySnapshot,
    *,
    page_index: int = 0,
) -> TraceableEvidenceProvenance:
    return TraceableEvidenceProvenance(
        artifact_contract_version="extraction_artifact_contract_v1",
        artifact_id="b" * 64,
        upstream_contract_version="controlled_pdf_text_extraction_result_v1",
        job_id="job-1",
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        page_index=page_index,
        page_number=page_index + 1,
        extraction_index=page_index,
        extraction_method="embedded_text",
        extraction_status="completed",
        execution_report_location="report://job-1",
    )


def _traceable(
    snapshot: EvidenceEligibilitySnapshot,
    *,
    content: str = "Exact Fact",
    page_index: int = 0,
) -> TraceableEvidence:
    content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    values = {
        "contract_version": TRACEABLE_EVIDENCE_CONTRACT_VERSION,
        "evidence_id": "evm1_" + "0" * 64,
        "content_type": TRACEABLE_EVIDENCE_CONTENT_TYPE,
        "content": content,
        "content_digest": content_digest,
        "warnings": (),
        "provenance": _provenance(snapshot, page_index=page_index),
        "eligibility_snapshot_digest": (
            derive_evidence_eligibility_snapshot_digest(snapshot)
        ),
    }
    provisional = _unchecked(TraceableEvidence, **values)
    values["evidence_id"] = derive_traceable_evidence_id(provisional)
    return TraceableEvidence(**values)


def _collection(
    *,
    snapshot: EvidenceEligibilitySnapshot | None = None,
    items: tuple[TraceableEvidence, ...] | None = None,
) -> EvidenceCollection:
    snapshot = snapshot or _snapshot()
    items = items if items is not None else (_traceable(snapshot),)
    first = items[0] if items else None
    provenance = (
        first.provenance
        if first is not None
        else _provenance(snapshot)
    )
    values = {
        "contract_version": EVIDENCE_COLLECTION_CONTRACT_VERSION,
        "collection_id": "evc1_" + "0" * 64,
        "artifact_contract_version": provenance.artifact_contract_version,
        "artifact_id": provenance.artifact_id,
        "upstream_contract_version": provenance.upstream_contract_version,
        "job_id": provenance.job_id,
        "source_id": snapshot.source_id,
        "source_path": snapshot.source_path,
        "source_checksum": snapshot.source_checksum,
        "eligibility_snapshot": snapshot,
        "evidence_items": items,
    }
    provisional = _unchecked(EvidenceCollection, **values)
    values["collection_id"] = derive_evidence_collection_id(provisional)
    return EvidenceCollection(**values)


def _lookup(
    collection: EvidenceCollection,
    *,
    payload_digest: str | None = None,
    revision_id_override: str | None = None,
    audit_source_id: str | None = None,
) -> EvidenceRepositoryLookupResult:
    digest = (
        payload_digest
        if payload_digest is not None
        else calculate_evidence_collection_repository_payload_digest(collection)
    )
    revision_id = revision_id_override or calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    audit_source = audit_source_id or collection.source_id
    audit_id = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=audit_source,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="repository-writer",
        recorded_at_utc=FIXED_TIME,
    )
    revision = EvidenceRepositoryRevision(
        contract_version=EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
        actor_id="repository-writer",
        recorded_at_utc=FIXED_TIME,
        audit_id=audit_id,
    )
    audit = EvidenceRepositoryAuditRecord(
        contract_version=EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
        audit_id=audit_id,
        action="persisted_revision",
        revision_id=revision_id,
        source_id=audit_source,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="repository-writer",
        recorded_at_utc=FIXED_TIME,
    )
    return EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        revision=revision,
        audit_record=audit,
        collection=collection,
        issue=None,
    )


def _accepted_values(
    collection: EvidenceCollection,
    target: TraceableEvidence,
    *,
    evidence_id: str,
    acceptance_record_id: str,
    source_snapshot: EvidenceSourceSnapshot | None = None,
) -> dict[str, object]:
    snapshot = collection.eligibility_snapshot
    candidate_digest = "c" * 64
    source_snapshot = source_snapshot or EvidenceSourceSnapshot(
        source_id=collection.source_id,
        source_path=collection.source_path,
        source_type=snapshot.source_type,
        document_classification=snapshot.document_classification,
        authority_status=snapshot.authority_status,
        lifecycle_status=snapshot.lifecycle_status,
        evidence_eligibility=snapshot.evidence_eligibility,
        source_content_digest=collection.source_checksum,
    )
    return {
        "evidence_id": evidence_id,
        "contract_version": "accepted-evidence-v1",
        "candidate_reference": EvidenceCandidateReference(
            candidate_contract_version="evidence-candidate-v1",
            candidate_snapshot_digest=candidate_digest,
            candidate_source_id=collection.source_id,
            candidate_producer_name="producer",
            candidate_producer_version="1.0.0",
            candidate_payload_digest=target.content_digest,
        ),
        "source_snapshot": source_snapshot,
        "producer_snapshot": EvidenceProducerSnapshot(
            producer_name="producer",
            producer_version="1.0.0",
            producer_kind="deterministic",
            producer_contract_version="1.0.0",
        ),
        "factual_payload": EvidencePayload(
            payload_type="text",
            payload_schema_version="1.0.0",
            payload=(("text", target.content),),
            payload_digest=target.content_digest,
            locator=EvidenceLocator(
                locator_type="page",
                locator_value=(1, "paragraph-1"),
                locator_schema_version="1.0.0",
            ),
        ),
        "provenance": EvidenceProvenance(
            collection_id=collection.collection_id,
            producer_output_digest="d" * 64,
            lineage=("repository", "extraction", "accepted-evidence"),
            observed_at=FIXED_TIME,
            source_registry_version=snapshot.registry_version,
        ),
        "eligibility_result": AcceptedEligibilityResult(
            decision="eligible",
            policy_id="eligibility-policy",
            policy_version="1.0.0",
            candidate_snapshot_digest=candidate_digest,
            source_id=collection.source_id,
            reason_codes=("eligible_source",),
            evaluated_at=FIXED_TIME,
            evaluated_by="reviewer",
            diagnostics=(),
        ),
        "materialization_record": EvidenceMaterializationRecord(
            materializer_id="accepted-evidence-materializer",
            materializer_version="1.0.0",
            materialized_at=FIXED_TIME,
            acceptance_record_id=acceptance_record_id,
            accepted_by="reviewer",
            acceptance_reason="verified fact",
            review_record_id="review-1",
            identity_policy_id="rcis-evidence-identity",
            identity_policy_version="1.0.0",
        ),
        "diagnostics": (),
    }


def _record_values(
    evidence_id: str,
    *,
    acceptance_record_id: str,
) -> dict[str, object]:
    return {
        "acceptance_record_id": acceptance_record_id,
        "contract_version": "acceptance-record-v1",
        "evidence_id": evidence_id,
        "accepted_by": "reviewer",
        "acceptance_reason": "verified fact",
        "review_record_id": "review-1",
        "accepted_at": FIXED_TIME,
        "acceptance_policy_id": "acceptance-policy",
        "acceptance_policy_version": "1.0.0",
        "evidence_identity_policy_id": "rcis-evidence-identity",
        "evidence_identity_policy_version": "1.0.0",
        "materializer_id": "accepted-evidence-materializer",
        "materializer_version": "1.0.0",
        "diagnostics": (),
    }


def _accepted_and_record(
    collection: EvidenceCollection,
    target: TraceableEvidence,
    *,
    source_snapshot: EvidenceSourceSnapshot | None = None,
) -> tuple[AcceptedEvidence, AcceptanceRecord]:
    placeholder_evidence_id = "ev1_" + "0" * 64
    placeholder_acceptance_id = "ar1_" + "0" * 64
    provisional = AcceptedEvidence(
        **_accepted_values(
            collection,
            target,
            evidence_id=placeholder_evidence_id,
            acceptance_record_id=placeholder_acceptance_id,
            source_snapshot=source_snapshot,
        )
    )
    evidence_id = calculate_evidence_identity(
        identity_input_from_accepted_evidence(provisional)
    ).evidence_id
    provisional_record = AcceptanceRecord(
        **_record_values(
            evidence_id,
            acceptance_record_id=placeholder_acceptance_id,
        )
    )
    acceptance_id = calculate_acceptance_identity(
        acceptance_identity_input_from_record(provisional_record)
    ).acceptance_record_id
    accepted = AcceptedEvidence(
        **_accepted_values(
            collection,
            target,
            evidence_id=evidence_id,
            acceptance_record_id=acceptance_id,
            source_snapshot=source_snapshot,
        )
    )
    record = AcceptanceRecord(
        **_record_values(
            evidence_id,
            acceptance_record_id=acceptance_id,
        )
    )
    return accepted, record


def _request(
    *,
    collection: EvidenceCollection | None = None,
    lookup: EvidenceRepositoryLookupResult | None = None,
    accepted: AcceptedEvidence | None = None,
    records: tuple[AcceptanceRecord, ...] | None = None,
    construction_rule_id: str = VERBATIM_TEXT_RULE_ID,
) -> PersistedEvidenceKnowledgeConstructionRequest:
    collection = collection or _collection()
    target = collection.evidence_items[0]
    if accepted is None or records is None:
        default_accepted, default_record = _accepted_and_record(
            collection,
            target,
        )
        accepted = accepted or default_accepted
        records = records or (default_record,)
    nested = KnowledgeConstructionRequest(
        accepted_evidence=accepted,
        acceptance_records=records,
        construction_rule_id=construction_rule_id,
        construction_rule_version=VERBATIM_TEXT_RULE_VERSION,
    )
    return PersistedEvidenceKnowledgeConstructionRequest(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ),
        repository_lookup_result=lookup or _lookup(collection),
        target_evidence_id=target.evidence_id,
        knowledge_construction_request=nested,
        compatibility_policy_id=(
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
        ),
        compatibility_policy_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
        ),
    )


def _unchecked_request(
    base: PersistedEvidenceKnowledgeConstructionRequest,
    **changes: object,
) -> PersistedEvidenceKnowledgeConstructionRequest:
    values = {
        field.name: getattr(base, field.name)
        for field in fields(PersistedEvidenceKnowledgeConstructionRequest)
    }
    values.update(changes)
    return _unchecked(
        PersistedEvidenceKnowledgeConstructionRequest,
        **values,
    )


def _code(result: object) -> str:
    assert result.status == "rejected"
    assert result.issue is not None
    return result.issue.code


def test_valid_request_constructs_evidence_backed_knowledge() -> None:
    request = _request()
    result = construct_knowledge_from_persisted_evidence(request)
    assert result.status == "constructed"
    assert result.mutation_performed is False
    assert result.issue is None
    assert result.compatibility_record is not None
    assert result.knowledge_construction_result is not None
    assert result.knowledge_construction_result.decision == "constructed"
    assert result.knowledge_construction_result.knowledge_candidate.statement == (
        request.repository_lookup_result.collection.evidence_items[0].content
    )
    record = result.compatibility_record
    assert record.repository_revision_id == (
        request.repository_lookup_result.revision.revision_id
    )
    assert record.repository_audit_id == (
        request.repository_lookup_result.audit_record.audit_id
    )
    assert record.traceable_evidence_id == request.target_evidence_id
    assert record.accepted_evidence_id == (
        request.knowledge_construction_request.accepted_evidence.evidence_id
    )


def test_exact_replay_is_deterministic_and_inputs_are_unchanged() -> None:
    request = _request()
    before = repr(request)
    first = construct_knowledge_from_persisted_evidence(request)
    second = construct_knowledge_from_persisted_evidence(request)
    assert first == second
    assert repr(request) == before
    assert first.compatibility_record.compatibility_record_id == (
        second.compatibility_record.compatibility_record_id
    )


def test_invalid_outer_request_is_rejected() -> None:
    assert _code(
        construct_knowledge_from_persisted_evidence(object())
    ) == "invalid_request"


def test_unsupported_version_precedes_policy_and_other_failures() -> None:
    base = _request()
    request = _unchecked_request(
        base,
        contract_version="other",
        compatibility_policy_id="other",
        target_evidence_id="bad",
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "unsupported_contract_version"


def test_unsupported_policy_precedes_invalid_nested_request() -> None:
    base = _request()
    request = _unchecked_request(
        base,
        compatibility_policy_id="other",
        target_evidence_id="bad",
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "unsupported_compatibility_policy"


def test_invalid_nested_request_is_rejected() -> None:
    base = _request()
    request = _unchecked_request(base, target_evidence_id="bad")
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "invalid_request"


def test_invalid_repository_lookup_result_is_rejected() -> None:
    base = _request()
    invalid_lookup = _unchecked(
        EvidenceRepositoryLookupResult,
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        revision=None,
        audit_record=None,
        collection=None,
        issue=None,
    )
    request = _unchecked_request(
        base,
        repository_lookup_result=invalid_lookup,
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "invalid_repository_lookup_result"


def test_not_found_lookup_is_explicit() -> None:
    lookup = EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="not_found",
        revision=None,
        audit_record=None,
        collection=None,
        issue=None,
    )
    base = _request()
    request = _unchecked_request(base, repository_lookup_result=lookup)
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "repository_lookup_not_found"


def test_rejected_lookup_is_explicit() -> None:
    issue = EvidenceRepositoryIssue(
        code="repository_unavailable",
        message=EVIDENCE_REPOSITORY_ISSUE_MESSAGES["repository_unavailable"],
    )
    lookup = EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="rejected",
        revision=None,
        audit_record=None,
        collection=None,
        issue=issue,
    )
    base = _request()
    request = _unchecked_request(base, repository_lookup_result=lookup)
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "repository_lookup_rejected"


def test_repository_linkage_mismatch_precedes_identity() -> None:
    collection = _collection()
    lookup = _lookup(collection, audit_source_id="other-source")
    assert _code(
        construct_knowledge_from_persisted_evidence(
            _request(collection=collection, lookup=lookup)
        )
    ) == "repository_linkage_mismatch"


def test_repository_revision_identity_mismatch_is_rejected() -> None:
    collection = _collection()
    lookup = _lookup(
        collection,
        revision_id_override="evr1_" + "f" * 64,
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(
            _request(collection=collection, lookup=lookup)
        )
    ) == "repository_identity_mismatch"


def test_collection_payload_digest_mismatch_is_rejected() -> None:
    collection = _collection()
    lookup = _lookup(collection, payload_digest="f" * 64)
    assert _code(
        construct_knowledge_from_persisted_evidence(
            _request(collection=collection, lookup=lookup)
        )
    ) == "collection_payload_digest_mismatch"


def test_target_evidence_not_found_is_rejected() -> None:
    base = _request()
    request = _unchecked_request(
        base,
        target_evidence_id="evm1_" + "f" * 64,
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "target_evidence_not_found"


def test_target_evidence_identity_mismatch_is_rejected(
    monkeypatch,
) -> None:
    snapshot = _snapshot()
    original = _traceable(snapshot)
    bad_values = {
        field.name: getattr(original, field.name)
        for field in fields(TraceableEvidence)
    }
    bad_values["content"] = "Changed Fact"
    bad_values["content_digest"] = hashlib.sha256(
        b"Changed Fact"
    ).hexdigest()
    bad_target = _unchecked(TraceableEvidence, **bad_values)
    collection = _collection(snapshot=snapshot, items=(bad_target,))
    payload_digest = "f" * 64
    lookup = _lookup(
        collection,
        payload_digest=payload_digest,
    )
    monkeypatch.setattr(
        service_module,
        "_calculate_payload_digest",
        lambda _collection: payload_digest,
    )
    request = _request(
        collection=collection,
        lookup=lookup,
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "target_evidence_identity_mismatch"


def test_ineligible_evidence_is_rejected() -> None:
    snapshot = _unchecked_snapshot(
        evidence_eligibility="not_eligible",
        evidence_collection_allowed=False,
    )
    target = _traceable(snapshot)
    collection = _collection(snapshot=snapshot, items=(target,))
    assert _code(
        construct_knowledge_from_persisted_evidence(
            _request(collection=collection)
        )
    ) == "ineligible_evidence"


def test_accepted_evidence_identity_mismatch_is_rejected() -> None:
    collection = _collection()
    target = collection.evidence_items[0]
    accepted, record = _accepted_and_record(collection, target)
    values = {
        field.name: getattr(accepted, field.name)
        for field in fields(AcceptedEvidence)
    }
    values["evidence_id"] = "ev1_" + "f" * 64
    bad_accepted = AcceptedEvidence(**values)
    request = _request(
        collection=collection,
        accepted=bad_accepted,
        records=(record,),
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "accepted_evidence_identity_mismatch"


def test_acceptance_record_identity_mismatch_is_rejected() -> None:
    collection = _collection()
    target = collection.evidence_items[0]
    accepted, record = _accepted_and_record(collection, target)
    bad_record = replace(
        record,
        acceptance_record_id="ar1_" + "f" * 64,
    )
    request = _request(
        collection=collection,
        accepted=accepted,
        records=(bad_record,),
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(request)
    ) == "acceptance_record_identity_mismatch"


@pytest.mark.parametrize(
    "field_name",
    (
        "source_id",
        "source_path",
        "source_type",
        "document_classification",
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
    ),
)
def test_each_shared_source_anchor_is_checked(field_name: str) -> None:
    collection = _collection()
    target = collection.evidence_items[0]
    accepted, record = _accepted_and_record(collection, target)
    source = accepted.source_snapshot
    changed_source = replace(source, **{field_name: "different"})
    changed_values = {
        field.name: getattr(accepted, field.name)
        for field in fields(AcceptedEvidence)
    }
    changed_values["source_snapshot"] = changed_source
    changed = _unchecked(AcceptedEvidence, **changed_values)
    result = construct_knowledge_from_persisted_evidence(
        _request(
            collection=collection,
            accepted=changed,
            records=(record,),
        )
    )
    expected = (
        "accepted_evidence_identity_mismatch"
        if field_name in ("source_id",)
        else "evidence_compatibility_mismatch"
    )
    assert _code(result) == expected


def test_content_and_payload_digest_compatibility_is_checked() -> None:
    collection = _collection()
    target = collection.evidence_items[0]
    accepted, record = _accepted_and_record(collection, target)
    payload = replace(
        accepted.factual_payload,
        payload=(("text", "different"),),
    )
    values = {
        field.name: getattr(accepted, field.name)
        for field in fields(AcceptedEvidence)
    }
    values["factual_payload"] = payload
    changed = AcceptedEvidence(**values)
    assert _code(
        construct_knowledge_from_persisted_evidence(
            _request(
                collection=collection,
                accepted=changed,
                records=(record,),
            )
        )
    ) == "evidence_compatibility_mismatch"


def test_existing_constructor_rejection_is_preserved() -> None:
    result = construct_knowledge_from_persisted_evidence(
        _request(construction_rule_id="unsupported-rule")
    )
    assert _code(result) == "knowledge_construction_rejected"
    assert result.compatibility_record is not None
    assert result.knowledge_construction_result is not None
    assert result.knowledge_construction_result.decision == "rejected"
    assert result.knowledge_construction_result.reason_codes == (
        "unsupported_construction_rule",
    )
    assert result.knowledge_construction_result.diagnostics[0].code == (
        "unsupported_construction_rule"
    )


def test_existing_constructor_is_called_exactly_once(monkeypatch) -> None:
    calls: list[KnowledgeConstructionRequest] = []
    original = service_module._construct_knowledge_candidate

    def counted(request: KnowledgeConstructionRequest):
        calls.append(request)
        return original(request)

    monkeypatch.setattr(
        service_module,
        "_construct_knowledge_candidate",
        counted,
    )
    request = _request()
    result = construct_knowledge_from_persisted_evidence(request)
    assert result.status == "constructed"
    assert calls == [request.knowledge_construction_request]


def test_internal_constructor_failure_is_closed(monkeypatch) -> None:
    def fail(_request: object) -> object:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(
        service_module,
        "_construct_knowledge_candidate",
        fail,
    )
    assert _code(
        construct_knowledge_from_persisted_evidence(_request())
    ) == "internal_contract_violation"

# PR-086FX-C3-C1-C4 exact18 structured-v4 compatibility extension coverage.
import rie.persisted_evidence_knowledge_construction.persisted_evidence_knowledge_construction_service as persisted_evidence_knowledge_construction_service

def _pr086fx_structured_anchor_fixture():
    import hashlib
    import json
    from types import SimpleNamespace

    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
        TraceableEvidenceStructuredMetadataProvenance,
    )

    exact_ids = (
    "evm1_009c6c903d897e9bd67bef3852e947cb5d5f66ac21672c44ebb30227e3a4c202",
    "evm1_0ad37b5cd8765d292143f98a31a0dcb7b31dced09b7c13e19f4eecd358f784de",
    "evm1_24cd78892b74ca07a87a5e04b141ae056c7c7b287f04367d5fc5fd9afa9a7b26",
    "evm1_2ada2177e9ad3b79e0dca72cc9e4e85fefed8dd713771d20fdf1fea747ad2eb2",
    "evm1_2e10a2610d2e3d07dcfbebcd5baa28ccb7792981beb72643de50e52714ce484a",
    "evm1_2e350a8d1b61ce11ad4d4b25218a0ae5ab8de8f524a9037611cafa0a8c988e6e",
    "evm1_3353406b885d205d9fd0dce93022e93e37a8a805e10df089722f847f6259e8f7",
    "evm1_54956c4f8205ae61a73c041cf75c7237ae593f2249351cfe0de1d2fa4ae50f2e",
    "evm1_6daf9d7af75892b728a8c5fa57b6be68b45327aaccb3a1e0664dd96cd4732bf9",
    "evm1_8088836878d452f73aff7c26ba36b66683144576c3ca804297f361a0449382c1",
    "evm1_95c87a9869239eba36478468f77aa14e1c4f32a228992017b861bbbfe7f0c5a9",
    "evm1_bdd92e5807c49621bde8390393dff1d84d8034dc36516cf8a35b1320c66189dd",
    "evm1_c0275e89aa2619b80cb6a7a2489e8871e9e2199010d1eda8d705645fbfc9a2d4",
    "evm1_cbe10029707a5ae58e0e2211c2c92de3f8f46dffcf1df98564412d50195b1b96",
    "evm1_dd86d5b43d2d0d32e20e60a161f80a09a5f053e1d02e2de4a91b45361c7ae193",
    "evm1_e20d39d207e4d133741c8ce091b43e27e1d3215d2cf6c00ed62049f42529505a",
    "evm1_e5080797d36e0bfd898225ffcc7345a50c3ff092be0f741220ba1c0912e88069",
    "evm1_ee617df3d287341953b5e40556122f0a648b64dacd52dfdf402de489b1003217",
)
    source_paths = ("official/product-variant-1.jpg",)
    payload_object = {
        "atomic_construction_authority_decision_packet_sha256": "c" * 64,
        "atomic_knowledge_id": "atomic-product-variant-1",
        "downstream_binding_policy_decision_packet_sha256": "d" * 64,
        "identity_capture_sha256": "b" * 64,
        "manifest_sha256": "a" * 64,
        "source_relative_paths": list(source_paths),
    }
    content = json.dumps(
        payload_object,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"
    content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    provenance = TraceableEvidenceStructuredMetadataProvenance(
        contract_version=(
            TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION
        ),
        payload_type=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
        payload_schema_version="1.0.0",
        locator_type="atomic_knowledge_id",
        locator_value="atomic-product-variant-1",
        locator_schema_version="1.0.0",
        atomic_knowledge_id="atomic-product-variant-1",
        source_relative_paths=source_paths,
        manifest_sha256="a" * 64,
        identity_capture_sha256="b" * 64,
        atomic_construction_authority_decision_packet_sha256="c" * 64,
        downstream_binding_policy_decision_packet_sha256="d" * 64,
        admission_payload_digest=content_digest,
    )
    target = SimpleNamespace(
        contract_version=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
        evidence_id=exact_ids[0],
        content_type=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
        content=content,
        content_digest=content_digest,
        provenance=provenance,
    )
    evidence_items = (target,) + tuple(
        SimpleNamespace(evidence_id=value) for value in exact_ids[1:]
    )
    snapshot = SimpleNamespace(
        source_id="pilot-rsv-product-variant-source",
        source_path="official/product-variant.json",
        source_checksum="e" * 64,
        source_type="structured_metadata",
        document_classification="official_product_metadata",
        authority_status="authoritative",
        lifecycle_status="active",
        evidence_eligibility="eligible",
        registry_version="registry-v1",
        policy_id="eligibility-policy",
        policy_version="1.0.0",
    )
    collection = SimpleNamespace(
        contract_version=EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
        collection_id=(
            "evc1_06534223733730505e33f7225d3d0507da70157396b5f94944d1e646d1b24f4b"
        ),
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=evidence_items,
    )
    factual_pairs = tuple(
        (
            key,
            tuple(value) if key == "source_relative_paths" else value,
        )
        for key, value in sorted(payload_object.items())
    )
    accepted = SimpleNamespace(
        source_snapshot=SimpleNamespace(
            source_id=snapshot.source_id,
            source_path=snapshot.source_path,
            source_content_digest=snapshot.source_checksum,
            source_type=snapshot.source_type,
            document_classification=snapshot.document_classification,
            authority_status=snapshot.authority_status,
            lifecycle_status=snapshot.lifecycle_status,
            evidence_eligibility=snapshot.evidence_eligibility,
        ),
        factual_payload=SimpleNamespace(
            payload_type=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
            payload_schema_version="1.0.0",
            payload=factual_pairs,
            payload_digest=content_digest,
            locator=SimpleNamespace(
                locator_type=provenance.locator_type,
                locator_value=provenance.locator_value,
                locator_schema_version=provenance.locator_schema_version,
            ),
        ),
        provenance=SimpleNamespace(
            source_registry_version=snapshot.registry_version,
            collection_id=collection.collection_id,
            producer_output_digest=content_digest,
            lineage=(
                target.evidence_id,
                provenance.atomic_knowledge_id,
                provenance.admission_payload_digest,
                provenance.manifest_sha256,
                provenance.identity_capture_sha256,
                provenance.atomic_construction_authority_decision_packet_sha256,
                provenance.downstream_binding_policy_decision_packet_sha256,
                *provenance.source_relative_paths,
            ),
        ),
        candidate_reference=SimpleNamespace(
            candidate_contract_version=target.contract_version,
            candidate_snapshot_digest=content_digest,
            candidate_source_id=collection.source_id,
            candidate_producer_name=provenance.payload_type,
            candidate_producer_version=provenance.payload_schema_version,
            candidate_payload_digest=content_digest,
        ),
        producer_snapshot=SimpleNamespace(
            producer_name=provenance.payload_type,
            producer_version=provenance.payload_schema_version,
            producer_kind=target.content_type,
            producer_contract_version=provenance.contract_version,
        ),
        eligibility_result=SimpleNamespace(
            decision=snapshot.evidence_eligibility,
            policy_id=snapshot.policy_id,
            policy_version=snapshot.policy_version,
            candidate_snapshot_digest=content_digest,
            source_id=collection.source_id,
        ),
    )
    return collection, target, accepted


def test_pr086fx_exact18_structured_v4_route_passes_shared_semantic_compatibility_and_reaches_existing_constructor() -> None:
    import inspect

    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is True
    )
    source = inspect.getsource(
        persisted_evidence_knowledge_construction_service.construct_knowledge_from_persisted_evidence
    )
    compatibility_index = source.index("_shared_semantic_anchors_match(")
    constructor_index = source.index("_construct_nested_candidate(nested)")
    assert compatibility_index < constructor_index


def test_pr086fx_legacy_page_text_route_behavior_is_unchanged() -> None:
    result = construct_knowledge_from_persisted_evidence(_request())
    assert result.status == "constructed"
    assert result.mutation_performed is False
    assert result.issue is None


def test_pr086fx_structured_route_rejects_non_exact18_target() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    collection.collection_id = "evc1_" + ("f" * 64)
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )


def test_pr086fx_structured_route_rejects_payload_type_or_schema_mismatch() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.factual_payload.payload_type = "text"
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.factual_payload.payload_schema_version = "9.9.9"
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )


def test_pr086fx_structured_route_rejects_payload_digest_or_content_projection_mismatch() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.factual_payload.payload_digest = "f" * 64
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.factual_payload.payload = (("atomic_knowledge_id", "different"),)
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )


def test_pr086fx_structured_route_rejects_locator_mismatch() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.factual_payload.locator.locator_value = "different"
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )


def test_pr086fx_structured_route_rejects_lineage_or_payload_provenance_crosscheck_mismatch() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.provenance.lineage = ("different",)
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )


def test_pr086fx_structured_route_rejects_shared_source_anchor_mismatch() -> None:
    collection, target, accepted = _pr086fx_structured_anchor_fixture()
    accepted.source_snapshot.source_path = "different"
    assert (
        persisted_evidence_knowledge_construction_service._shared_semantic_anchors_match(
            collection,
            target,
            accepted,
        )
        is False
    )

# PR-086GF-R2-C2 narrow runtime-dispatch coverage.
def test_pr086gf_r2_product_variant_dispatch_reaches_specialized_bridge_source() -> None:
    import inspect

    source = inspect.getsource(
        persisted_evidence_knowledge_construction_service._construct_product_variant_candidate
    )
    assert "_pvi_materialize_admission(" in source
    assert "_pvi_construct_candidate(" in source
    assert "_KnowledgeConstructionResult(" in source


def test_pr086gf_r2_dispatch_preserves_generic_constructor_fallback_source() -> None:
    import inspect

    source = inspect.getsource(
        persisted_evidence_knowledge_construction_service._construct_nested_candidate
    )
    assert "nested.construction_rule_id == _PVI_RULE_ID" in source
    assert "return _construct_product_variant_candidate(nested)" in source
    assert "return _construct_knowledge_candidate(nested)" in source

