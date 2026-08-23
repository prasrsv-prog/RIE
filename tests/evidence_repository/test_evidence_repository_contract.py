
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

# PR-086K-D39 synthetic v2 repository compatibility fixture.
def _pr086k_d39_v2_collection():
    import hashlib as _d39_hashlib

    from rie.evidence_materialization.evidence_materialization_canonicalization import (
        derive_evidence_collection_id as _d39_derive_collection_id,
        derive_evidence_eligibility_snapshot_digest as _d39_derive_snapshot_digest,
        derive_traceable_evidence_id as _d39_derive_evidence_id,
    )
    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION as _D39_COLLECTION_V2,
        EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION as _D39_SNAPSHOT_V1,
        TRACEABLE_EVIDENCE_CONTENT_TYPE as _D39_CONTENT_TYPE,
        TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION as _D39_TRACEABLE_V2,
        EvidenceCollection as _D39_EvidenceCollection,
        EvidenceEligibilitySnapshot as _D39_Snapshot,
        TraceableEvidence as _D39_TraceableEvidence,
        TraceableEvidenceOcrRemediationProvenance as _D39_OcrProvenance,
        TraceableEvidenceProvenance as _D39_Provenance,
    )

    snapshot = _D39_Snapshot(
        contract_version=_D39_SNAPSHOT_V1,
        source_id="d39-source",
        source_path="synthetic-d39.pdf",
        source_checksum="a" * 64,
        source_type="pdf",
        document_classification="product_manual",
        authority_status="approved",
        lifecycle_status="locked",
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="D39 synthetic eligible source.",
        policy_id="d39-synthetic-policy",
        policy_version="1.0.0",
        registry_version="d39-registry-v1",
    )
    provenance = _D39_Provenance(
        artifact_contract_version="extraction_artifact_contract_v2",
        artifact_id="b" * 64,
        upstream_contract_version="controlled_pdf_text_extraction_result_v1",
        job_id="d39-job",
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="bounded_local_ocr",
        extraction_status="completed",
        execution_report_location="report://d39",
    )
    ocr = _D39_OcrProvenance(
        producer_operation_id=(
            "PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_"
            "EXTRACTION_EXECUTION"
        ),
        producer_artifact_path=(
            r"C:\Users\Kreatif Kris\Downloads\RCIS-RSV-Real-Asset-Pilot-01-"
            r"Intake\pilot-bounded-pdf-image-text-extraction-state\ocr-"
            r"extraction-index.json"
        ),
        producer_artifact_sha256=(
            "d509a7d6337f332038e9a37a42b0855b68762b7cfd15cbd1a34190ba74382ee4"
        ),
        producer_artifact_set_digest=(
            "a36604df0195d6a213a5bbd8e69c1e1726f56f64f8d280935c8b57681fd43264"
        ),
        extraction_method="bounded_local_ocr",
    )

    content = "D39 synthetic repository v2 evidence"
    evidence_values = {
        "contract_version": _D39_TRACEABLE_V2,
        "evidence_id": "evm1_" + "0" * 64,
        "content_type": _D39_CONTENT_TYPE,
        "content": content,
        "content_digest": _d39_hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "warnings": (),
        "provenance": provenance,
        "eligibility_snapshot_digest": _d39_derive_snapshot_digest(snapshot),
    }
    provisional_evidence = object.__new__(_D39_TraceableEvidence)
    for _name, _value in evidence_values.items():
        object.__setattr__(provisional_evidence, _name, _value)
    object.__setattr__(
        provisional_evidence,
        "ocr_remediation_provenance",
        ocr,
    )
    evidence_values["evidence_id"] = _d39_derive_evidence_id(
        provisional_evidence
    )
    evidence = _D39_TraceableEvidence(
        **evidence_values,
        ocr_remediation_provenance=ocr,
    )

    collection_values = {
        "contract_version": _D39_COLLECTION_V2,
        "collection_id": "evc1_" + "0" * 64,
        "artifact_contract_version": provenance.artifact_contract_version,
        "artifact_id": provenance.artifact_id,
        "upstream_contract_version": provenance.upstream_contract_version,
        "job_id": provenance.job_id,
        "source_id": snapshot.source_id,
        "source_path": snapshot.source_path,
        "source_checksum": snapshot.source_checksum,
        "eligibility_snapshot": snapshot,
        "evidence_items": (evidence,),
    }
    provisional_collection = object.__new__(_D39_EvidenceCollection)
    for _name, _value in collection_values.items():
        object.__setattr__(provisional_collection, _name, _value)
    collection_values["collection_id"] = _d39_derive_collection_id(
        provisional_collection
    )
    return _D39_EvidenceCollection(**collection_values)

def test_pr086k_d39_write_request_accepts_exact_gate6_v2_collection():
    from datetime import datetime as _d39_datetime, timezone as _d39_timezone

    from rie.evidence_repository.evidence_repository_canonicalization import (
        calculate_evidence_collection_repository_payload_digest as _d39_digest,
    )
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION as _D39_REQUEST_V1,
        EvidenceRepositoryWriteRequest as _D39_WriteRequest,
    )

    collection = _pr086k_d39_v2_collection()
    request = _D39_WriteRequest(
        contract_version=_D39_REQUEST_V1,
        collection=collection,
        expected_collection_payload_digest=_d39_digest(collection),
        actor_id="d39-synthetic-operator",
        recorded_at_utc=_d39_datetime(
            2026, 8, 12, 0, 0, 0, tzinfo=_d39_timezone.utc
        ),
    )
    assert request.collection is collection


def test_pr086k_d39_write_request_still_rejects_unknown_collection_version():
    from dataclasses import fields as _d39_fields
    from datetime import datetime as _d39_datetime, timezone as _d39_timezone

    import pytest as _d39_pytest

    from rie.evidence_materialization.evidence_materialization_contract import (
        EvidenceCollection as _D39_EvidenceCollection,
    )
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION as _D39_REQUEST_V1,
        EvidenceRepositoryWriteRequest as _D39_WriteRequest,
    )

    valid = _pr086k_d39_v2_collection()
    invalid = object.__new__(_D39_EvidenceCollection)
    for _field in _d39_fields(_D39_EvidenceCollection):
        object.__setattr__(invalid, _field.name, getattr(valid, _field.name))
    object.__setattr__(invalid, "contract_version", "evidence_collection_contract_v999")

    with _d39_pytest.raises(
        ValueError,
        match="unsupported EvidenceCollection contract version",
    ):
        _D39_WriteRequest(
            contract_version=_D39_REQUEST_V1,
            collection=invalid,
            expected_collection_payload_digest="c" * 64,
            actor_id="d39-synthetic-operator",
            recorded_at_utc=_d39_datetime(
                2026, 8, 12, 0, 0, 0, tzinfo=_d39_timezone.utc
            ),
        )

# PR-086BL synthetic v3 compatibility fixture.
def _pr086bl_v3_collection(*, reverse=False):
    import hashlib as _bl_hashlib

    from rie.evidence_materialization.evidence_materialization_canonicalization import (
        derive_evidence_collection_id as _bl_derive_collection_id,
        derive_traceable_evidence_id as _bl_derive_evidence_id,
    )
    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION as _BL_COLLECTION_V3,
        TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION as _BL_TRACEABLE_V3,
        TRACEABLE_EVIDENCE_CONTENT_TYPE as _BL_CONTENT_TYPE,
        EvidenceCollection as _BL_Collection,
        TraceableEvidence as _BL_Evidence,
        TraceableEvidenceAtomicTextDerivationProvenance as _BL_AtomicProvenance,
    )

    base = _pr086k_d39_v2_collection()
    parent = base.evidence_items[0]
    items = []

    for content in ("S: 55-56 cm", "M: 57-58 cm"):
        content_digest = _bl_hashlib.sha256(content.encode("utf-8")).hexdigest()
        atomic = _BL_AtomicProvenance(
            contract_version="traceable_evidence_atomic_text_derivation_provenance_v1",
            derivation_type="operator_approved_verbatim_atomic_text",
            parent_traceable_evidence_id=parent.evidence_id,
            parent_content_digest=parent.content_digest,
            source_span_ids=("span-ffs21-0056",),
            operator_decision_packet_sha256="a" * 64,
            atomic_statement_sha256=content_digest,
        )
        values = {
            "contract_version": _BL_TRACEABLE_V3,
            "evidence_id": "evm1_" + "0" * 64,
            "content_type": _BL_CONTENT_TYPE,
            "content": content,
            "content_digest": content_digest,
            "warnings": parent.warnings,
            "provenance": parent.provenance,
            "eligibility_snapshot_digest": parent.eligibility_snapshot_digest,
            "ocr_remediation_provenance": parent.ocr_remediation_provenance,
            "atomic_text_derivation_provenance": atomic,
        }
        provisional = object.__new__(_BL_Evidence)
        for name, value in values.items():
            object.__setattr__(provisional, name, value)
        values["evidence_id"] = _bl_derive_evidence_id(provisional)
        items.append(_BL_Evidence(**values))

    if reverse:
        items.reverse()

    collection_values = {
        "contract_version": _BL_COLLECTION_V3,
        "collection_id": "evc1_" + "0" * 64,
        "artifact_contract_version": base.artifact_contract_version,
        "artifact_id": base.artifact_id,
        "upstream_contract_version": base.upstream_contract_version,
        "job_id": base.job_id,
        "source_id": base.source_id,
        "source_path": base.source_path,
        "source_checksum": base.source_checksum,
        "eligibility_snapshot": base.eligibility_snapshot,
        "evidence_items": tuple(items),
    }
    provisional_collection = object.__new__(_BL_Collection)
    for name, value in collection_values.items():
        object.__setattr__(provisional_collection, name, value)
    collection_values["collection_id"] = _bl_derive_collection_id(
        provisional_collection
    )
    return _BL_Collection(**collection_values)

def test_pr086bl_v3_collection_preserves_duplicate_parent_page_indexes_and_order():
    first = _pr086bl_v3_collection()
    reversed_collection = _pr086bl_v3_collection(reverse=True)
    assert tuple(item.provenance.page_index for item in first.evidence_items) == (0, 0)
    assert tuple(item.provenance.page_number for item in first.evidence_items) == (1, 1)
    assert first.collection_id != reversed_collection.collection_id
    assert tuple(item.content for item in first.evidence_items) == (
        "S: 55-56 cm",
        "M: 57-58 cm",
    )


def test_pr086bl_write_request_v2_accepts_v3_and_v1_rejects_v3():
    from datetime import datetime as _bl_datetime, timezone as _bl_timezone
    import pytest as _bl_pytest

    from rie.evidence_repository.evidence_repository_canonicalization import (
        calculate_evidence_collection_repository_payload_digest as _bl_digest,
    )
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION as _BL_REQUEST_V1,
        EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION as _BL_REQUEST_V2,
        EvidenceRepositoryWriteRequest as _BL_Request,
    )

    collection = _pr086bl_v3_collection()
    kwargs = {
        "collection": collection,
        "expected_collection_payload_digest": _bl_digest(collection),
        "actor_id": "pr086bl-synthetic-operator",
        "recorded_at_utc": _bl_datetime(
            2026, 8, 16, 0, 0, 0, tzinfo=_bl_timezone.utc
        ),
    }
    request = _BL_Request(contract_version=_BL_REQUEST_V2, **kwargs)
    assert request.collection is collection

    with _bl_pytest.raises(
        ValueError,
        match="unsupported EvidenceCollection contract version",
    ):
        _BL_Request(contract_version=_BL_REQUEST_V1, **kwargs)

# PR-086EW write-request v3 additive contract coverage.
def test_pr086ew_write_request_v3_contract_version_is_additive() -> None:
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION,
        EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION,
    )

    assert EVIDENCE_REPOSITORY_WRITE_REQUEST_V2_CONTRACT_VERSION == "evidence_repository_write_request_contract_v2"
    assert EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION == "evidence_repository_write_request_contract_v3"
