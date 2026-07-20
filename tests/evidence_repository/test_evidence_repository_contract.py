
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib

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
    EVIDENCE_COLLECTION_ID_PREFIX,
    TRACEABLE_EVIDENCE_ID_PREFIX,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceProvenance,
)


def _snapshot(
    *,
    source_id: str = "source-001",
    source_path: str = "official/specification.pdf",
    source_checksum: str = "a" * 64,
) -> EvidenceEligibilitySnapshot:
    return EvidenceEligibilitySnapshot(
        contract_version=EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        source_type="pdf",
        document_classification="official_source",
        authority_status="official",
        lifecycle_status="active",
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="eligible official source",
        policy_id="official-source-policy",
        policy_version="1",
        registry_version="1",
    )


def _collection(
    content: str = "Exact page text.",
    *,
    artifact_id: str = "b" * 64,
    job_id: str = "job-001",
    source_id: str = "source-001",
    source_path: str = "official/specification.pdf",
    source_checksum: str = "a" * 64,
    warnings: tuple[str, ...] = ("warning-a", "warning-a"),
) -> EvidenceCollection:
    snapshot = _snapshot(
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
    )
    provenance = TraceableEvidenceProvenance(
        artifact_contract_version="extraction_artifact_contract_v1",
        artifact_id=artifact_id,
        upstream_contract_version="pdf_ingestion_orchestrator_result_contract_v1",
        job_id=job_id,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="pdf_text",
        extraction_status="completed",
        execution_report_location="reports/extraction.txt",
    )
    content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    snapshot_digest = derive_evidence_eligibility_snapshot_digest(snapshot)

    unchecked_evidence = object.__new__(TraceableEvidence)
    for name, value in (
        ("contract_version", TRACEABLE_EVIDENCE_CONTRACT_VERSION),
        ("evidence_id", TRACEABLE_EVIDENCE_ID_PREFIX + ("0" * 64)),
        ("content_type", TRACEABLE_EVIDENCE_CONTENT_TYPE),
        ("content", content),
        ("content_digest", content_digest),
        ("warnings", warnings),
        ("provenance", provenance),
        ("eligibility_snapshot_digest", snapshot_digest),
    ):
        object.__setattr__(unchecked_evidence, name, value)

    evidence = TraceableEvidence(
        contract_version=TRACEABLE_EVIDENCE_CONTRACT_VERSION,
        evidence_id=derive_traceable_evidence_id(unchecked_evidence),
        content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
        content=content,
        content_digest=content_digest,
        warnings=warnings,
        provenance=provenance,
        eligibility_snapshot_digest=snapshot_digest,
    )

    unchecked_collection = object.__new__(EvidenceCollection)
    for name, value in (
        ("contract_version", EVIDENCE_COLLECTION_CONTRACT_VERSION),
        ("collection_id", EVIDENCE_COLLECTION_ID_PREFIX + ("0" * 64)),
        ("artifact_contract_version", "extraction_artifact_contract_v1"),
        ("artifact_id", artifact_id),
        (
            "upstream_contract_version",
            "pdf_ingestion_orchestrator_result_contract_v1",
        ),
        ("job_id", job_id),
        ("source_id", source_id),
        ("source_path", source_path),
        ("source_checksum", source_checksum),
        ("eligibility_snapshot", snapshot),
        ("evidence_items", (evidence,)),
    ):
        object.__setattr__(unchecked_collection, name, value)

    return EvidenceCollection(
        contract_version=EVIDENCE_COLLECTION_CONTRACT_VERSION,
        collection_id=derive_evidence_collection_id(unchecked_collection),
        artifact_contract_version="extraction_artifact_contract_v1",
        artifact_id=artifact_id,
        upstream_contract_version="pdf_ingestion_orchestrator_result_contract_v1",
        job_id=job_id,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=(evidence,),
    )


FIXED_TIME = datetime(2026, 7, 20, 12, 34, 56, 123456, tzinfo=timezone.utc)

from dataclasses import FrozenInstanceError, MISSING, fields

import pytest

from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX,
    EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_ISSUE_CODES,
    EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_ISSUE_MESSAGES,
    EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_LOOKUP_STATUSES,
    EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION,
    EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
    EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_WRITE_STATUSES,
    SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID,
    SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION,
    EvidenceRepositoryAuditRecord,
    EvidenceRepositoryHistoryResult,
    EvidenceRepositoryIssue,
    EvidenceRepositoryLookupResult,
    EvidenceRepositoryRevision,
    EvidenceRepositoryWriteRequest,
    EvidenceRepositoryWriteResult,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
)


def _revision_and_audit():
    collection = _collection()
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    revision_id = calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    audit_id = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="reviewer",
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
        actor_id="reviewer",
        recorded_at_utc=FIXED_TIME,
        audit_id=audit_id,
    )
    audit = EvidenceRepositoryAuditRecord(
        contract_version=EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
        audit_id=audit_id,
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="reviewer",
        recorded_at_utc=FIXED_TIME,
    )
    return collection, revision, audit


def test_exact_version_and_schema_constants():
    assert EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION == (
        "evidence_repository_write_request_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION == (
        "evidence_repository_write_result_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION == (
        "evidence_repository_revision_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION == (
        "evidence_repository_audit_record_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION == (
        "evidence_repository_lookup_result_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION == (
        "evidence_repository_history_result_contract_v1"
    )
    assert EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION == (
        "evidence_repository_issue_contract_v1"
    )
    assert SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID == (
        "rcis-gate7-evidence-repository-sqlite"
    )
    assert SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION == 1


def test_exact_canonicalization_constants_and_prefixes():
    assert EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION == (
        "evidence_collection_repository_payload_json_v1"
    )
    assert EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION == (
        "evidence_repository_revision_identity_json_v1"
    )
    assert EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION == (
        "evidence_repository_audit_identity_json_v1"
    )
    assert EVIDENCE_REPOSITORY_REVISION_ID_PREFIX == "evr1_"
    assert EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX == "eva1_"


def test_exact_statuses_and_issue_code_order():
    assert EVIDENCE_REPOSITORY_WRITE_STATUSES == (
        "persisted",
        "unchanged_exact_replay",
        "rejected",
    )
    assert EVIDENCE_REPOSITORY_LOOKUP_STATUSES == (
        "found",
        "not_found",
        "rejected",
    )
    assert EVIDENCE_REPOSITORY_ISSUE_CODES == (
        "invalid_request",
        "unsupported_contract_version",
        "invalid_collection",
        "collection_id_mismatch",
        "collection_payload_digest_mismatch",
        "collection_identity_collision",
        "revision_id_mismatch",
        "audit_id_mismatch",
        "unsupported_schema",
        "repository_busy",
        "repository_corrupt",
        "repository_unavailable",
    )


def test_issue_messages_are_fixed_and_non_secret():
    assert tuple(EVIDENCE_REPOSITORY_ISSUE_MESSAGES) == (
        EVIDENCE_REPOSITORY_ISSUE_CODES
    )
    for code in EVIDENCE_REPOSITORY_ISSUE_CODES:
        issue = EvidenceRepositoryIssue(
            code=code,
            message=EVIDENCE_REPOSITORY_ISSUE_MESSAGES[code],
        )
        assert issue.code == code
        assert "Exact page text" not in issue.message
        with pytest.raises(FrozenInstanceError):
            issue.message = "changed"


@pytest.mark.parametrize(
    ("contract_type", "expected_fields"),
    (
        (
            EvidenceRepositoryIssue,
            ("code", "message"),
        ),
        (
            EvidenceRepositoryWriteRequest,
            (
                "contract_version",
                "collection",
                "expected_collection_payload_digest",
                "actor_id",
                "recorded_at_utc",
            ),
        ),
        (
            EvidenceRepositoryRevision,
            (
                "contract_version",
                "revision_id",
                "source_id",
                "revision_number",
                "collection_id",
                "collection_payload_digest",
                "previous_revision_id",
                "actor_id",
                "recorded_at_utc",
                "audit_id",
            ),
        ),
        (
            EvidenceRepositoryAuditRecord,
            (
                "contract_version",
                "audit_id",
                "action",
                "revision_id",
                "source_id",
                "revision_number",
                "collection_id",
                "actor_id",
                "recorded_at_utc",
            ),
        ),
        (
            EvidenceRepositoryWriteResult,
            (
                "contract_version",
                "status",
                "mutation_performed",
                "revision",
                "audit_record",
                "collection",
                "issue",
            ),
        ),
        (
            EvidenceRepositoryLookupResult,
            (
                "contract_version",
                "status",
                "revision",
                "audit_record",
                "collection",
                "issue",
            ),
        ),
        (
            EvidenceRepositoryHistoryResult,
            (
                "contract_version",
                "status",
                "source_id",
                "revisions",
                "audit_records",
                "issue",
            ),
        ),
    ),
)
def test_contracts_are_frozen_with_exact_fields_and_no_defaults(
    contract_type,
    expected_fields,
):
    actual = fields(contract_type)
    assert tuple(field.name for field in actual) == expected_fields
    assert all(field.default is MISSING for field in actual)
    assert all(field.default_factory is MISSING for field in actual)


def test_valid_write_request_preserves_exact_collection_and_time():
    collection = _collection()
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    request = EvidenceRepositoryWriteRequest(
        contract_version=EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
        collection=collection,
        expected_collection_payload_digest=digest,
        actor_id="reviewer",
        recorded_at_utc=FIXED_TIME,
    )
    assert request.collection is collection
    assert request.recorded_at_utc is FIXED_TIME


@pytest.mark.parametrize(
    "bad_time",
    (
        datetime(2026, 7, 20, 12, 0, 0),
        "2026-07-20T12:00:00.000000Z",
    ),
)
def test_write_request_requires_timezone_aware_utc_datetime(bad_time):
    collection = _collection()
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    with pytest.raises((TypeError, ValueError)):
        EvidenceRepositoryWriteRequest(
            contract_version=EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
            collection=collection,
            expected_collection_payload_digest=digest,
            actor_id="reviewer",
            recorded_at_utc=bad_time,
        )


def test_revision_and_audit_contracts_are_consistent():
    collection, revision, audit = _revision_and_audit()
    assert revision.audit_id == audit.audit_id
    assert revision.revision_id == audit.revision_id
    assert revision.collection_id == collection.collection_id


def test_first_revision_rejects_previous_revision():
    collection, revision, _ = _revision_and_audit()
    with pytest.raises(ValueError):
        replace(
            revision,
            previous_revision_id=EVIDENCE_REPOSITORY_REVISION_ID_PREFIX
            + ("1" * 64),
        )


@pytest.mark.parametrize("status", EVIDENCE_REPOSITORY_WRITE_STATUSES[:2])
def test_successful_write_result_shapes(status):
    collection, revision, audit = _revision_and_audit()
    result = EvidenceRepositoryWriteResult(
        contract_version=EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
        status=status,
        mutation_performed=status == "persisted",
        revision=revision,
        audit_record=audit,
        collection=collection,
        issue=None,
    )
    assert result.status == status


def test_rejected_write_result_has_no_partial_values():
    result = EvidenceRepositoryWriteResult(
        contract_version=EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
        status="rejected",
        mutation_performed=False,
        revision=None,
        audit_record=None,
        collection=None,
        issue=EvidenceRepositoryIssue(
            code="invalid_request",
            message=EVIDENCE_REPOSITORY_ISSUE_MESSAGES["invalid_request"],
        ),
    )
    assert result.revision is None
    assert result.audit_record is None
    assert result.collection is None


def test_found_lookup_requires_complete_shape():
    collection, revision, audit = _revision_and_audit()
    found = EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        revision=revision,
        audit_record=audit,
        collection=collection,
        issue=None,
    )
    assert found.collection == collection
    with pytest.raises((TypeError, ValueError)):
        replace(found, collection=None)


def test_not_found_lookup_is_empty():
    result = EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="not_found",
        revision=None,
        audit_record=None,
        collection=None,
        issue=None,
    )
    assert result.status == "not_found"


def test_found_history_requires_consecutive_revisions_and_audits():
    _, revision, audit = _revision_and_audit()
    result = EvidenceRepositoryHistoryResult(
        contract_version=EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION,
        status="found",
        source_id=revision.source_id,
        revisions=(revision,),
        audit_records=(audit,),
        issue=None,
    )
    assert result.revisions == (revision,)
    with pytest.raises(ValueError):
        replace(result, audit_records=())
