from __future__ import annotations

from contextlib import contextmanager
from dataclasses import fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import os
from pathlib import Path
import re
import sqlite3
from tempfile import TemporaryDirectory

import pytest

import rie.infrastructure.sqlite_evidence_repository as adapter_module
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
from rie.infrastructure.sqlite_evidence_repository import (
    SQLITE_EVIDENCE_REPOSITORY_SCHEMA_ID,
    SQLITE_EVIDENCE_REPOSITORY_SCHEMA_VERSION,
    SqliteEvidenceRepository,
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


@contextmanager
def _database_path():
    root = Path(os.environ["RCIS_SQLITE_TEST_ROOT"])
    with TemporaryDirectory(
        prefix="pr024ab-",
        dir=root,
    ) as temporary:
        yield Path(temporary) / "evidence.sqlite3"


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


def test_exact_public_surface() -> None:
    public_methods = {
        name
        for name, value in (
            SqliteEvidenceRepository.__dict__.items()
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
    assert SQLITE_EVIDENCE_REPOSITORY_SCHEMA_ID == (
        "rcis-evidence-repository-sqlite"
    )
    assert SQLITE_EVIDENCE_REPOSITORY_SCHEMA_VERSION == 1


def test_structural_protocol_assignment() -> None:
    with _database_path() as database_path:
        repository: EvidenceRepository = (
            SqliteEvidenceRepository(str(database_path))
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
        "close",
    ),
)
def test_forbidden_public_methods_are_absent(
    method_name: str,
) -> None:
    assert not hasattr(
        SqliteEvidenceRepository,
        method_name,
    )


@pytest.mark.parametrize(
    "invalid_path",
    (
        "",
        "   ",
        ":memory:",
        "file:test.sqlite3?mode=memory&cache=shared",
    ),
)
def test_constructor_rejects_invalid_literal_paths(
    invalid_path: str,
) -> None:
    with pytest.raises(ValueError):
        SqliteEvidenceRepository(invalid_path)


def test_constructor_rejects_missing_parent_and_directory() -> None:
    with _database_path() as database_path:
        missing_parent = (
            database_path.parent
            / "missing"
            / "evidence.sqlite3"
        )
        with pytest.raises(ValueError):
            SqliteEvidenceRepository(str(missing_parent))

        directory_target = database_path.parent / "directory"
        directory_target.mkdir()
        with pytest.raises(ValueError):
            SqliteEvidenceRepository(str(directory_target))


def test_exact_schema_columns_foreign_key_and_user_version() -> None:
    with _database_path() as database_path:
        SqliteEvidenceRepository(str(database_path))
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        try:
            objects = connection.execute(
                """
                SELECT type, name, tbl_name
                FROM sqlite_master
                WHERE name NOT LIKE 'sqlite_autoindex_%'
                ORDER BY type, name
                """
            ).fetchall()
            assert {
                (row["type"], row["name"], row["tbl_name"])
                for row in objects
            } == {
                (
                    "table",
                    "accepted_evidence_records",
                    "accepted_evidence_records",
                ),
                (
                    "table",
                    "acceptance_records",
                    "acceptance_records",
                ),
                (
                    "index",
                    "acceptance_records_by_evidence",
                    "acceptance_records",
                ),
            }
            schema_sql = {
                row["name"]: " ".join(row["sql"].split())
                for row in connection.execute(
                    """
                    SELECT name, sql
                    FROM sqlite_master
                    WHERE sql IS NOT NULL
                    """
                )
            }
            assert (
                "substr(evidence_id, 5) = "
                "canonical_identity_digest"
                in schema_sql["accepted_evidence_records"]
            )
            assert (
                "substr(acceptance_record_id, 5) = "
                "canonical_identity_digest"
                in schema_sql["acceptance_records"]
            )
            assert (
                "length(payload_bytes) > 0"
                in schema_sql["accepted_evidence_records"]
            )
            assert (
                "length(payload_bytes) > 0"
                in schema_sql["acceptance_records"]
            )
            assert connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0] == 1
            assert tuple(
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(accepted_evidence_records)"
                )
            ) == (
                "evidence_id",
                "canonical_identity_digest",
                "persistence_contract_version",
                "payload_schema_id",
                "identity_policy_id",
                "identity_policy_version",
                "payload_bytes_digest",
                "payload_bytes",
            )
            assert tuple(
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(acceptance_records)"
                )
            ) == (
                "acceptance_record_id",
                "evidence_id",
                "canonical_identity_digest",
                "persistence_contract_version",
                "payload_schema_id",
                "identity_policy_id",
                "identity_policy_version",
                "payload_bytes_digest",
                "payload_bytes",
            )
            foreign_keys = connection.execute(
                "PRAGMA foreign_key_list(acceptance_records)"
            ).fetchall()
            assert len(foreign_keys) == 1
            assert foreign_keys[0]["table"] == (
                "accepted_evidence_records"
            )
            assert foreign_keys[0]["from"] == "evidence_id"
            assert foreign_keys[0]["to"] == "evidence_id"
            assert foreign_keys[0]["on_update"] == "RESTRICT"
            assert foreign_keys[0]["on_delete"] == "RESTRICT"
            index_columns = connection.execute(
                """
                PRAGMA index_info(
                    acceptance_records_by_evidence
                )
                """
            ).fetchall()
            assert tuple(
                row["name"] for row in index_columns
            ) == (
                "evidence_id",
                "acceptance_record_id",
            )
        finally:
            connection.close()


def test_schema_enforces_identity_links_and_nonempty_payloads() -> None:
    with _database_path() as database_path:
        SqliteEvidenceRepository(str(database_path))
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            valid_evidence_id = f"ev1_{'a' * 64}"
            valid_acceptance_id = f"ar1_{'d' * 64}"
            evidence_values = (
                valid_evidence_id,
                "a" * 64,
                "1.0.0",
                "accepted-evidence-json-v1",
                "rcis-evidence-identity",
                "1.0.0",
                "c" * 64,
                sqlite3.Binary(b"x"),
            )
            connection.execute(
                """
                INSERT INTO accepted_evidence_records (
                    evidence_id,
                    canonical_identity_digest,
                    persistence_contract_version,
                    payload_schema_id,
                    identity_policy_id,
                    identity_policy_version,
                    payload_bytes_digest,
                    payload_bytes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                evidence_values,
            )

            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO accepted_evidence_records (
                        evidence_id,
                        canonical_identity_digest,
                        persistence_contract_version,
                        payload_schema_id,
                        identity_policy_id,
                        identity_policy_version,
                        payload_bytes_digest,
                        payload_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"ev1_{'b' * 64}",
                        "c" * 64,
                        "1.0.0",
                        "accepted-evidence-json-v1",
                        "rcis-evidence-identity",
                        "1.0.0",
                        "e" * 64,
                        sqlite3.Binary(b"x"),
                    ),
                )

            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO accepted_evidence_records (
                        evidence_id,
                        canonical_identity_digest,
                        persistence_contract_version,
                        payload_schema_id,
                        identity_policy_id,
                        identity_policy_version,
                        payload_bytes_digest,
                        payload_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"ev1_{'f' * 64}",
                        "f" * 64,
                        "1.0.0",
                        "accepted-evidence-json-v1",
                        "rcis-evidence-identity",
                        "1.0.0",
                        "1" * 64,
                        sqlite3.Binary(b""),
                    ),
                )

            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO acceptance_records (
                        acceptance_record_id,
                        evidence_id,
                        canonical_identity_digest,
                        persistence_contract_version,
                        payload_schema_id,
                        identity_policy_id,
                        identity_policy_version,
                        payload_bytes_digest,
                        payload_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        valid_acceptance_id,
                        valid_evidence_id,
                        "e" * 64,
                        "1.0.0",
                        "acceptance-record-json-v1",
                        "rcis-acceptance-record-identity",
                        "1.0.0",
                        "2" * 64,
                        sqlite3.Binary(b"x"),
                    ),
                )

            with pytest.raises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO acceptance_records (
                        acceptance_record_id,
                        evidence_id,
                        canonical_identity_digest,
                        persistence_contract_version,
                        payload_schema_id,
                        identity_policy_id,
                        identity_policy_version,
                        payload_bytes_digest,
                        payload_bytes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        valid_acceptance_id,
                        valid_evidence_id,
                        "d" * 64,
                        "1.0.0",
                        "acceptance-record-json-v1",
                        "rcis-acceptance-record-identity",
                        "1.0.0",
                        "2" * 64,
                        sqlite3.Binary(b""),
                    ),
                )
        finally:
            connection.close()


def test_reopen_preserves_written_records() -> None:
    with _database_path() as database_path:
        request = _build_request()
        first = SqliteEvidenceRepository(str(database_path))
        assert first.write(request).mutation_performed is True

        reopened = SqliteEvidenceRepository(str(database_path))
        assert reopened.get_evidence(
            request.accepted_evidence.evidence_id
        ).accepted_evidence == request.accepted_evidence
        assert reopened.get_acceptance_record(
            request.acceptance_record.acceptance_record_id
        ).acceptance_record == request.acceptance_record


def test_two_adapter_instances_share_sequential_state() -> None:
    with _database_path() as database_path:
        first = SqliteEvidenceRepository(str(database_path))
        second = SqliteEvidenceRepository(str(database_path))
        request = _build_request()

        first.write(request)

        assert second.get_evidence(
            request.accepted_evidence.evidence_id
        ).status == "found"


def test_new_evidence_write_and_all_reads() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()

        result = repository.write(request)
        evidence = repository.get_evidence(
            request.accepted_evidence.evidence_id
        )
        acceptance = repository.get_acceptance_record(
            request.acceptance_record.acceptance_record_id
        )
        acceptance_list = repository.list_acceptance_records(
            request.accepted_evidence.evidence_id
        )

        assert result.status == "inserted_new_evidence"
        assert result.classification == "new_evidence"
        assert result.mutation_performed is True
        assert evidence.accepted_evidence == (
            request.accepted_evidence
        )
        assert acceptance.acceptance_record == (
            request.acceptance_record
        )
        assert acceptance_list.acceptance_records == (
            request.acceptance_record,
        )


def test_same_fact_new_acceptance_appends_only_record() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        first = _build_request()
        second = _build_request(
            accepted_by="reviewer-2",
            review_record_id="review-2",
            accepted_at=FIXED_TIME + timedelta(seconds=1),
        )
        repository.write(first)

        result = repository.write(second)
        evidence = repository.get_evidence(
            first.accepted_evidence.evidence_id
        )
        records = repository.list_acceptance_records(
            first.accepted_evidence.evidence_id
        )

        assert result.status == "appended_acceptance_record"
        assert result.classification == (
            "same_fact_new_acceptance"
        )
        assert result.mutation_performed is True
        assert evidence.accepted_evidence == (
            first.accepted_evidence
        )
        assert set(records.acceptance_records) == {
            first.acceptance_record,
            second.acceptance_record,
        }


def test_exact_replay_is_non_mutating() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        repository.write(request)

        result = repository.write(request)

        assert result.status == "unchanged_exact_replay"
        assert result.classification == "exact_replay"
        assert result.mutation_performed is False


@pytest.mark.parametrize(
    "variant",
    (
        _with_evidence_diagnostic,
        _with_acceptance_diagnostic,
    ),
)
def test_governance_replay_is_non_mutating(
    variant: object,
) -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        repository.write(request)

        result = repository.write(variant(request))

        assert result.status == "unchanged_governance_replay"
        assert result.classification == "governance_replay"
        assert result.mutation_performed is False
        assert repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).accepted_evidence == request.accepted_evidence


def test_factual_identity_collision_is_rejected() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        base = _build_request()
        repository.write(base)

        result = repository.write(
            _factual_projection_collision(base)
        )

        assert result.classification == "identity_collision"
        assert result.status == "rejected_identity_collision"
        assert result.mutation_performed is False


def test_acceptance_identity_collision_is_rejected() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        base = _build_request()
        repository.write(base)

        result = repository.write(
            _acceptance_projection_collision(base)
        )

        assert result.classification == "acceptance_collision"
        assert result.status == "rejected_acceptance_collision"
        assert result.mutation_performed is False


def test_acceptance_records_are_lexicographically_ordered() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
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
        ids = tuple(
            record.acceptance_record_id
            for record in result.acceptance_records
        )

        assert ids == tuple(sorted(ids))


def test_classify_write_is_advisory_and_non_mutating() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()

        classification = repository.classify_write(request)

        assert classification.classification == "new_evidence"
        assert repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status == "not_found"


def test_invalid_request_is_rejected_before_database_open() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        database_path.unlink()

        for method_name in ("classify_write", "write"):
            with pytest.raises(ValueError):
                getattr(repository, method_name)(object())

        assert not database_path.exists()


def test_corrupt_payload_digest_fails_closed() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        repository.write(request)

        connection = sqlite3.connect(database_path)
        try:
            connection.execute(
                """
                UPDATE accepted_evidence_records
                SET payload_bytes_digest = ?
                WHERE evidence_id = ?
                """,
                (
                    "0" * 64,
                    request.accepted_evidence.evidence_id,
                ),
            )
            connection.commit()
        finally:
            connection.close()

        assert repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status == "failed"


def test_corrupt_canonical_payload_bytes_fail_closed() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        repository.write(request)
        corrupt = b"{}"
        digest = hashlib.sha256(corrupt).hexdigest()

        connection = sqlite3.connect(database_path)
        try:
            connection.execute(
                """
                UPDATE accepted_evidence_records
                SET payload_bytes = ?, payload_bytes_digest = ?
                WHERE evidence_id = ?
                """,
                (
                    sqlite3.Binary(corrupt),
                    digest,
                    request.accepted_evidence.evidence_id,
                ),
            )
            connection.commit()
        finally:
            connection.close()

        assert repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status == "failed"


def test_incompatible_schema_version_is_rejected() -> None:
    with _database_path() as database_path:
        SqliteEvidenceRepository(str(database_path))
        connection = sqlite3.connect(database_path)
        try:
            connection.execute("PRAGMA user_version = 2")
        finally:
            connection.close()

        with pytest.raises(ValueError):
            SqliteEvidenceRepository(str(database_path))


def test_unexpected_schema_object_is_rejected() -> None:
    with _database_path() as database_path:
        SqliteEvidenceRepository(str(database_path))
        connection = sqlite3.connect(database_path)
        try:
            connection.execute(
                "CREATE TABLE unexpected_object (value TEXT)"
            )
            connection.commit()
        finally:
            connection.close()

        with pytest.raises(ValueError):
            SqliteEvidenceRepository(str(database_path))


def test_transaction_rolls_back_when_acceptance_insert_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        monkeypatch.setattr(
            adapter_module,
            "_INSERT_ACCEPTANCE_SQL",
            "INSERT INTO absent_table(value) VALUES (?)",
        )

        result = repository.write(request)

        connection = sqlite3.connect(database_path)
        try:
            evidence_count = connection.execute(
                "SELECT count(*) FROM accepted_evidence_records"
            ).fetchone()[0]
            acceptance_count = connection.execute(
                "SELECT count(*) FROM acceptance_records"
            ).fetchone()[0]
        finally:
            connection.close()

        assert result.status == "failed_repository_operation"
        assert result.mutation_performed is False
        assert evidence_count == 0
        assert acceptance_count == 0


def test_busy_lock_returns_failure_without_partial_mutation() -> None:
    with _database_path() as database_path:
        repository = SqliteEvidenceRepository(
            str(database_path)
        )
        request = _build_request()
        lock = sqlite3.connect(
            database_path,
            timeout=0.0,
            isolation_level=None,
        )
        try:
            lock.execute("BEGIN IMMEDIATE")
            result = repository.write(request)
        finally:
            lock.rollback()
            lock.close()

        assert result.status == "failed_repository_operation"
        assert result.mutation_performed is False
        assert repository.get_evidence(
            request.accepted_evidence.evidence_id
        ).status == "not_found"


def test_source_excludes_forbidden_sql_and_cross_domain_behavior() -> None:
    source = inspect.getsource(adapter_module)

    assert "INSERT OR" not in source.upper()
    assert "UPSERT" not in source.upper()
    assert "VACUUM" not in source.upper()
    assert "ATTACH DATABASE" not in source.upper()
    assert "DETACH DATABASE" not in source.upper()
    assert "PRAGMA journal_mode" not in source
    assert "sleep(" not in source
    assert "KnowledgeRepository" not in source
    assert "PromptCandidate" not in source
    assert re.search(
        r"(?i)\b(UPDATE|DELETE|REPLACE)\s+"
        r"(accepted_evidence_records|acceptance_records)\b",
        source,
    ) is None
