
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

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from datetime import timedelta
import os
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

import pytest

from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
    SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION,
    EvidenceRepositoryWriteRequest,
)
from rie.evidence_repository.sqlite_evidence_collection_repository import (
    SqliteEvidenceCollectionRepository,
)


@contextmanager
def _database_path():
    root = os.environ.get("RCIS_SQLITE_TEST_ROOT")
    if not root:
        raise RuntimeError("RCIS_SQLITE_TEST_ROOT is required")
    with TemporaryDirectory(dir=root) as directory:
        yield Path(directory) / "gate7.sqlite"


def _request(
    collection=None,
    *,
    actor_id: str = "reviewer",
    recorded_at=FIXED_TIME,
):
    value = collection or _collection()
    return EvidenceRepositoryWriteRequest(
        contract_version=EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION,
        collection=value,
        expected_collection_payload_digest=(
            calculate_evidence_collection_repository_payload_digest(value)
        ),
        actor_id=actor_id,
        recorded_at_utc=recorded_at,
    )


def _table_names(path: Path) -> tuple[str, ...]:
    with closing(sqlite3.connect(path)) as connection, connection:
        return tuple(
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
        )


def test_constructor_creates_exact_three_table_schema():
    with _database_path() as path:
        SqliteEvidenceCollectionRepository(path)
        assert _table_names(path) == (
            "evidence_audit_records",
            "evidence_collection_records",
            "evidence_revision_records",
        )
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute("PRAGMA user_version").fetchone()[0] == (
                SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION
            )
            assert connection.execute("PRAGMA application_id").fetchone()[0] != 0


@pytest.mark.parametrize(
    "invalid_path",
    (
        "",
        1,
        None,
    ),
)
def test_constructor_rejects_invalid_path_types(invalid_path):
    with pytest.raises(ValueError):
        SqliteEvidenceCollectionRepository(invalid_path)


def test_constructor_rejects_missing_parent_and_directory():
    with _database_path() as path:
        with pytest.raises(ValueError):
            SqliteEvidenceCollectionRepository(path / "missing" / "repo.sqlite")
        path.mkdir()
        with pytest.raises(ValueError):
            SqliteEvidenceCollectionRepository(path)


def test_new_collection_persists_revision_one_and_exact_audit():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        request = _request()
        result = repository.persist(request)
        assert result.status == "persisted"
        assert result.mutation_performed is True
        assert result.revision.revision_number == 1
        assert result.revision.previous_revision_id is None
        assert result.revision.collection_id == request.collection.collection_id
        assert result.audit_record.action == "persisted_revision"
        assert result.collection == request.collection


def test_exact_replay_returns_original_values_without_mutation():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        request = _request()
        first = repository.persist(request)
        replay = repository.persist(
            _request(
                request.collection,
                actor_id="different-actor",
                recorded_at=FIXED_TIME + timedelta(hours=1),
            )
        )
        assert replay.status == "unchanged_exact_replay"
        assert replay.mutation_performed is False
        assert replay.revision == first.revision
        assert replay.audit_record == first.audit_record
        assert replay.collection == first.collection
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute(
                "SELECT count(*) FROM evidence_revision_records"
            ).fetchone()[0] == 1
            assert connection.execute(
                "SELECT count(*) FROM evidence_audit_records"
            ).fetchone()[0] == 1


def test_new_collection_for_same_source_appends_next_revision():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        first = repository.persist(_request(_collection(content="page one")))
        second = repository.persist(
            _request(
                _collection(
                    content="page two",
                    artifact_id="c" * 64,
                    job_id="job-002",
                ),
                recorded_at=FIXED_TIME + timedelta(hours=1),
            )
        )
        assert first.revision.revision_number == 1
        assert second.revision.revision_number == 2
        assert second.revision.previous_revision_id == first.revision.revision_id


def test_lookup_by_collection_and_source_revision_returns_exact_collection():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        request = _request()
        written = repository.persist(request)
        by_collection = repository.get_by_collection_id(
            request.collection.collection_id
        )
        by_revision = repository.get_by_source_revision(
            request.collection.source_id,
            1,
        )
        assert by_collection.status == "found"
        assert by_revision.status == "found"
        assert by_collection.collection == request.collection
        assert by_revision.revision == written.revision
        assert by_revision.audit_record == written.audit_record


def test_missing_and_invalid_lookups_are_controlled():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        assert repository.get_by_collection_id("missing").status == "not_found"
        assert repository.get_by_source_revision("missing", 1).status == "not_found"
        assert repository.get_by_collection_id("").status == "rejected"
        assert repository.get_by_source_revision("", 0).status == "rejected"


def test_source_history_and_audit_are_revision_ordered():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        for index in range(3):
            repository.persist(
                _request(
                    _collection(
                        content=f"page {index}",
                        artifact_id=f"{index + 1:064x}",
                        job_id=f"job-{index}",
                    ),
                    recorded_at=FIXED_TIME + timedelta(hours=index),
                )
            )
        history = repository.list_source_history("source-001")
        audit = repository.list_source_audit("source-001")
        assert history.status == "found"
        assert tuple(item.revision_number for item in history.revisions) == (
            1,
            2,
            3,
        )
        assert tuple(item.revision_number for item in audit.audit_records) == (
            1,
            2,
            3,
        )


def test_empty_source_history_is_not_found():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        result = repository.list_source_history("missing")
        assert result.status == "not_found"
        assert result.revisions == ()
        assert result.audit_records == ()


def test_reopen_preserves_exact_round_trip():
    with _database_path() as path:
        request = _request()
        first_repository = SqliteEvidenceCollectionRepository(path)
        written = first_repository.persist(request)
        reopened = SqliteEvidenceCollectionRepository(path)
        found = reopened.get_by_collection_id(request.collection.collection_id)
        assert found.status == "found"
        assert found.collection == request.collection
        assert found.revision == written.revision
        assert found.audit_record == written.audit_record


def test_payload_digest_mismatch_is_rejected_before_mutation():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        valid = _request()
        forged = replace(
            valid,
            expected_collection_payload_digest="f" * 64,
        )
        result = repository.persist(forged)
        assert result.status == "rejected"
        assert result.issue.code == "collection_payload_digest_mismatch"
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute(
                "SELECT count(*) FROM evidence_collection_records"
            ).fetchone()[0] == 0


def test_collection_identity_collision_is_rejected_without_new_revision():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        request = _request()
        repository.persist(request)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                """
                UPDATE evidence_collection_records
                SET payload_digest = ?
                WHERE collection_id = ?
                """,
                ("f" * 64, request.collection.collection_id),
            )
            connection.commit()
        result = repository.persist(request)
        assert result.status == "rejected"
        assert result.issue.code == "collection_identity_collision"
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute(
                "SELECT count(*) FROM evidence_revision_records"
            ).fetchone()[0] == 1


def test_corrupt_payload_fails_closed_without_content_echo():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        request = _request()
        repository.persist(request)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                """
                UPDATE evidence_collection_records
                SET payload_bytes = ?
                WHERE collection_id = ?
                """,
                (b"{}", request.collection.collection_id),
            )
            connection.commit()
        result = repository.get_by_collection_id(request.collection.collection_id)
        assert result.status == "rejected"
        assert result.issue.code == "repository_corrupt"
        assert "Exact page text" not in result.issue.message


def test_incompatible_schema_version_fails_closed():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("PRAGMA user_version = 99")
        result = repository.get_by_collection_id("missing")
        assert result.status == "rejected"
        assert result.issue.code == "unsupported_schema"


def test_unexpected_schema_object_fails_closed():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        with closing(sqlite3.connect(path)) as connection, connection:
            connection.execute(
                "CREATE VIEW unexpected_object AS SELECT 1 AS value"
            )
        result = repository.get_by_collection_id("missing")
        assert result.status == "rejected"
        assert result.issue.code == "unsupported_schema"


def test_busy_repository_returns_controlled_issue_without_partial_mutation():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        blocker = sqlite3.connect(path, timeout=0.0, isolation_level=None)
        try:
            blocker.execute("BEGIN IMMEDIATE")
            result = repository.persist(_request())
            assert result.status == "rejected"
            assert result.issue.code == "repository_busy"
        finally:
            blocker.rollback()
            blocker.close()
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute(
                "SELECT count(*) FROM evidence_collection_records"
            ).fetchone()[0] == 0
            assert connection.execute(
                "SELECT count(*) FROM evidence_revision_records"
            ).fetchone()[0] == 0
            assert connection.execute(
                "SELECT count(*) FROM evidence_audit_records"
            ).fetchone()[0] == 0


def test_concurrent_exact_writes_commit_once_then_replay():
    with _database_path() as path:
        repositories = (
            SqliteEvidenceCollectionRepository(path),
            SqliteEvidenceCollectionRepository(path),
            SqliteEvidenceCollectionRepository(path),
        )
        request = _request()
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = tuple(
                executor.map(lambda repo: repo.persist(request), repositories)
            )
        assert sum(item.status == "persisted" for item in results) == 1
        assert sum(
            item.status == "unchanged_exact_replay" for item in results
        ) == 2
        with closing(sqlite3.connect(path)) as connection, connection:
            assert connection.execute(
                "SELECT count(*) FROM evidence_revision_records"
            ).fetchone()[0] == 1


def test_concurrent_distinct_writes_use_consecutive_revisions():
    with _database_path() as path:
        repositories = (
            SqliteEvidenceCollectionRepository(path),
            SqliteEvidenceCollectionRepository(path),
        )
        requests = (
            _request(
                _collection(
                    content="first",
                    artifact_id="c" * 64,
                    job_id="job-a",
                )
            ),
            _request(
                _collection(
                    content="second",
                    artifact_id="d" * 64,
                    job_id="job-b",
                ),
                recorded_at=FIXED_TIME + timedelta(hours=1),
            ),
        )
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = tuple(
                executor.map(
                    lambda pair: pair[0].persist(pair[1]),
                    zip(repositories, requests),
                )
            )
        assert {item.status for item in results} == {"persisted"}
        history = repositories[0].list_source_history("source-001")
        assert tuple(item.revision_number for item in history.revisions) == (
            1,
            2,
        )


def test_foreign_keys_are_enabled_for_every_operation_connection():
    with _database_path() as path:
        repository = SqliteEvidenceCollectionRepository(path)
        repository.persist(_request())
        with closing(sqlite3.connect(path)) as connection, connection:
            revision_foreign_keys = connection.execute(
                "PRAGMA foreign_key_list(evidence_revision_records)"
            ).fetchall()
            audit_foreign_keys = connection.execute(
                "PRAGMA foreign_key_list(evidence_audit_records)"
            ).fetchall()
        assert revision_foreign_keys
        assert audit_foreign_keys

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

def test_pr086k_d39_sqlite_persists_and_reopens_exact_gate6_v2_collection(
    tmp_path,
):
    from datetime import datetime as _d39_datetime, timezone as _d39_timezone

    from rie.evidence_repository.evidence_repository_canonicalization import (
        calculate_evidence_collection_repository_payload_digest as _d39_digest,
    )
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION as _D39_REQUEST_V1,
        EvidenceRepositoryWriteRequest as _D39_WriteRequest,
    )
    from rie.evidence_repository.sqlite_evidence_collection_repository import (
        SqliteEvidenceCollectionRepository as _D39_Repository,
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
    path = tmp_path / "pr086k-d39-v2.sqlite3"

    first_repository = _D39_Repository(path)
    first = first_repository.persist(request)
    assert first.status == "persisted"
    assert first.mutation_performed is True

    lookup = first_repository.get_by_collection_id(collection.collection_id)
    assert lookup.status == "found"
    assert lookup.collection == collection
    assert getattr(
        lookup.collection.evidence_items[0],
        "ocr_remediation_provenance",
    ) == getattr(
        collection.evidence_items[0],
        "ocr_remediation_provenance",
    )

    reopened_repository = _D39_Repository(path)
    reopened = reopened_repository.get_by_collection_id(
        collection.collection_id
    )
    assert reopened.status == "found"
    assert reopened.collection == collection
    assert getattr(
        reopened.collection.evidence_items[0],
        "ocr_remediation_provenance",
    ) == getattr(
        collection.evidence_items[0],
        "ocr_remediation_provenance",
    )
