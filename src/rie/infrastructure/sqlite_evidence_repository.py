"""Durable SQLite Evidence Repository adapter with append-only semantics."""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3

from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence
from rie.domain.evidence_identity import (
    identity_input_from_accepted_evidence,
)
from rie.infrastructure.evidence_repository_serialization import (
    ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID,
    ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID,
    EVIDENCE_PERSISTENCE_CONTRACT_VERSION,
    SerializedAcceptanceRecord,
    SerializedAcceptedEvidenceRecord,
    deserialize_acceptance_record,
    deserialize_accepted_evidence,
    serialize_acceptance_record,
    serialize_accepted_evidence,
)
from rie.interfaces.evidence_repository import (
    AcceptanceRecordListResult,
    AcceptanceRecordLookupResult,
    EvidenceLookupResult,
    EvidenceWriteClassificationResult,
    EvidenceWriteRequest,
    EvidenceWriteResult,
)


SQLITE_EVIDENCE_REPOSITORY_SCHEMA_ID = (
    "rcis-evidence-repository-sqlite"
)
SQLITE_EVIDENCE_REPOSITORY_SCHEMA_VERSION = 1

_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")

_CREATE_ACCEPTED_EVIDENCE_TABLE_SQL = """
CREATE TABLE accepted_evidence_records (
    evidence_id TEXT PRIMARY KEY,
    canonical_identity_digest TEXT NOT NULL,
    persistence_contract_version TEXT NOT NULL,
    payload_schema_id TEXT NOT NULL,
    identity_policy_id TEXT NOT NULL,
    identity_policy_version TEXT NOT NULL,
    payload_bytes_digest TEXT NOT NULL,
    payload_bytes BLOB NOT NULL,

    CHECK (
        length(evidence_id) = 68
        AND substr(evidence_id, 1, 4) = 'ev1_'
        AND substr(evidence_id, 5) NOT GLOB '*[^0-9a-f]*'
    ),
    CHECK (
        length(canonical_identity_digest) = 64
        AND canonical_identity_digest NOT GLOB '*[^0-9a-f]*'
        AND substr(evidence_id, 5) = canonical_identity_digest
    ),
    CHECK (
        length(payload_bytes_digest) = 64
        AND payload_bytes_digest NOT GLOB '*[^0-9a-f]*'
    ),
    CHECK (length(payload_bytes) > 0)
)
""".strip()

_CREATE_ACCEPTANCE_TABLE_SQL = """
CREATE TABLE acceptance_records (
    acceptance_record_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL,
    canonical_identity_digest TEXT NOT NULL,
    persistence_contract_version TEXT NOT NULL,
    payload_schema_id TEXT NOT NULL,
    identity_policy_id TEXT NOT NULL,
    identity_policy_version TEXT NOT NULL,
    payload_bytes_digest TEXT NOT NULL,
    payload_bytes BLOB NOT NULL,

    FOREIGN KEY (evidence_id)
        REFERENCES accepted_evidence_records(evidence_id)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT,

    CHECK (
        length(acceptance_record_id) = 68
        AND substr(acceptance_record_id, 1, 4) = 'ar1_'
        AND substr(acceptance_record_id, 5)
            NOT GLOB '*[^0-9a-f]*'
    ),
    CHECK (
        length(evidence_id) = 68
        AND substr(evidence_id, 1, 4) = 'ev1_'
        AND substr(evidence_id, 5) NOT GLOB '*[^0-9a-f]*'
    ),
    CHECK (
        length(canonical_identity_digest) = 64
        AND canonical_identity_digest NOT GLOB '*[^0-9a-f]*'
        AND substr(acceptance_record_id, 5)
            = canonical_identity_digest
    ),
    CHECK (
        length(payload_bytes_digest) = 64
        AND payload_bytes_digest NOT GLOB '*[^0-9a-f]*'
    ),
    CHECK (length(payload_bytes) > 0)
)
""".strip()

_CREATE_ACCEPTANCE_INDEX_SQL = """
CREATE INDEX acceptance_records_by_evidence
ON acceptance_records(evidence_id, acceptance_record_id)
""".strip()

_INSERT_EVIDENCE_SQL = """
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
""".strip()

_INSERT_ACCEPTANCE_SQL = """
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
""".strip()

_EXPECTED_SCHEMA_OBJECTS = {
    (
        "table",
        "accepted_evidence_records",
        "accepted_evidence_records",
    ): _CREATE_ACCEPTED_EVIDENCE_TABLE_SQL,
    (
        "table",
        "acceptance_records",
        "acceptance_records",
    ): _CREATE_ACCEPTANCE_TABLE_SQL,
    (
        "index",
        "acceptance_records_by_evidence",
        "acceptance_records",
    ): _CREATE_ACCEPTANCE_INDEX_SQL,
}

_EXPECTED_EVIDENCE_COLUMNS = (
    ("evidence_id", "TEXT", 0, 1),
    ("canonical_identity_digest", "TEXT", 1, 0),
    ("persistence_contract_version", "TEXT", 1, 0),
    ("payload_schema_id", "TEXT", 1, 0),
    ("identity_policy_id", "TEXT", 1, 0),
    ("identity_policy_version", "TEXT", 1, 0),
    ("payload_bytes_digest", "TEXT", 1, 0),
    ("payload_bytes", "BLOB", 1, 0),
)

_EXPECTED_ACCEPTANCE_COLUMNS = (
    ("acceptance_record_id", "TEXT", 0, 1),
    ("evidence_id", "TEXT", 1, 0),
    ("canonical_identity_digest", "TEXT", 1, 0),
    ("persistence_contract_version", "TEXT", 1, 0),
    ("payload_schema_id", "TEXT", 1, 0),
    ("identity_policy_id", "TEXT", 1, 0),
    ("identity_policy_version", "TEXT", 1, 0),
    ("payload_bytes_digest", "TEXT", 1, 0),
    ("payload_bytes", "BLOB", 1, 0),
)


@dataclass(frozen=True)
class _EvidenceEntry:
    accepted_evidence: AcceptedEvidence
    canonical_digest: str
    identity_projection: object


@dataclass(frozen=True)
class _AcceptanceEntry:
    acceptance_record: AcceptanceRecord
    canonical_digest: str
    identity_projection: object


def _normalize_sql(value: str) -> str:
    return " ".join(value.strip().rstrip(";").split()).lower()


def _require_identifier(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")
    return value


def _require_exact_request(request: object) -> EvidenceWriteRequest:
    if type(request) is not EvidenceWriteRequest:
        raise ValueError(
            "request must be an exact EvidenceWriteRequest"
        )
    request.__post_init__()
    return request


def _classification_reason(classification: str) -> str:
    reasons = {
        "new_evidence": "new_evidence",
        "exact_replay": "exact_replay_detected",
        "governance_replay": "governance_replay_detected",
        "same_fact_new_acceptance": "same_fact_new_acceptance",
        "identity_collision": "identity_collision_detected",
        "acceptance_collision": "acceptance_collision_detected",
        "rejected": "request_invalid",
    }
    return reasons[classification]


def _failed_classification(
    request: EvidenceWriteRequest,
) -> EvidenceWriteClassificationResult:
    return EvidenceWriteClassificationResult(
        classification="rejected",
        evidence_id=request.accepted_evidence.evidence_id,
        acceptance_record_id=(
            request.acceptance_record.acceptance_record_id
        ),
        existing_evidence_digest=None,
        existing_acceptance_digest=None,
        reason_codes=("repository_operation_failed",),
        diagnostics=(),
    )


class SqliteEvidenceRepository:
    """Operation-scoped SQLite implementation of EvidenceRepository."""

    def __init__(self, database_path: str) -> None:
        if type(database_path) is not str:
            raise ValueError("database_path must be an exact string")
        if not database_path or not database_path.strip():
            raise ValueError("database_path must not be empty")
        if database_path == ":memory:":
            raise ValueError("in-memory SQLite is not supported")
        if database_path.lower().startswith("file:"):
            raise ValueError("SQLite URI paths are not supported")

        path = Path(database_path)
        parent = path.parent
        if not parent.exists() or not parent.is_dir():
            raise ValueError("database parent directory must exist")
        if path.exists() and path.is_dir():
            raise ValueError("database_path must not be a directory")

        self._database_path = str(path)
        self._bootstrap_or_validate(path.exists())

    def get_evidence(
        self,
        evidence_id: str,
    ) -> EvidenceLookupResult:
        valid_id = _require_identifier(
            evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        try:
            with closing(self._connect()) as connection:
                entry = self._load_evidence_entry(
                    connection,
                    valid_id,
                )
                if entry is None:
                    return EvidenceLookupResult(
                        status="not_found",
                        accepted_evidence=None,
                        canonical_evidence_bytes_digest=None,
                        acceptance_record_ids=(),
                        reason_codes=("evidence_not_found",),
                        diagnostics=(),
                    )

                record_rows = connection.execute(
                    """
                    SELECT acceptance_record_id
                    FROM acceptance_records
                    WHERE evidence_id = ?
                    ORDER BY acceptance_record_id ASC
                    """,
                    (valid_id,),
                ).fetchall()
                record_ids = tuple(
                    row["acceptance_record_id"]
                    for row in record_rows
                )
                if not record_ids:
                    raise ValueError(
                        "stored evidence has no acceptance record"
                    )

                return EvidenceLookupResult(
                    status="found",
                    accepted_evidence=entry.accepted_evidence,
                    canonical_evidence_bytes_digest=(
                        entry.canonical_digest
                    ),
                    acceptance_record_ids=record_ids,
                    reason_codes=(),
                    diagnostics=(),
                )
        except (sqlite3.Error, ValueError):
            return EvidenceLookupResult(
                status="failed",
                accepted_evidence=None,
                canonical_evidence_bytes_digest=None,
                acceptance_record_ids=(),
                reason_codes=("repository_operation_failed",),
                diagnostics=(),
            )

    def get_acceptance_record(
        self,
        acceptance_record_id: str,
    ) -> AcceptanceRecordLookupResult:
        valid_id = _require_identifier(
            acceptance_record_id,
            "acceptance_record_id",
            _ACCEPTANCE_ID_PATTERN,
        )
        try:
            with closing(self._connect()) as connection:
                entry = self._load_acceptance_entry(
                    connection,
                    valid_id,
                )
                if entry is None:
                    return AcceptanceRecordLookupResult(
                        status="not_found",
                        acceptance_record=None,
                        canonical_acceptance_bytes_digest=None,
                        evidence_id=None,
                        reason_codes=(
                            "acceptance_record_not_found",
                        ),
                        diagnostics=(),
                    )

                return AcceptanceRecordLookupResult(
                    status="found",
                    acceptance_record=entry.acceptance_record,
                    canonical_acceptance_bytes_digest=(
                        entry.canonical_digest
                    ),
                    evidence_id=entry.acceptance_record.evidence_id,
                    reason_codes=(),
                    diagnostics=(),
                )
        except (sqlite3.Error, ValueError):
            return AcceptanceRecordLookupResult(
                status="failed",
                acceptance_record=None,
                canonical_acceptance_bytes_digest=None,
                evidence_id=None,
                reason_codes=("repository_operation_failed",),
                diagnostics=(),
            )

    def list_acceptance_records(
        self,
        evidence_id: str,
    ) -> AcceptanceRecordListResult:
        valid_id = _require_identifier(
            evidence_id,
            "evidence_id",
            _EVIDENCE_ID_PATTERN,
        )
        try:
            with closing(self._connect()) as connection:
                rows = connection.execute(
                    """
                    SELECT
                        acceptance_record_id,
                        evidence_id,
                        canonical_identity_digest,
                        persistence_contract_version,
                        payload_schema_id,
                        identity_policy_id,
                        identity_policy_version,
                        payload_bytes_digest,
                        payload_bytes
                    FROM acceptance_records
                    WHERE evidence_id = ?
                    ORDER BY acceptance_record_id ASC
                    """,
                    (valid_id,),
                ).fetchall()

                if not rows:
                    return AcceptanceRecordListResult(
                        status="not_found",
                        evidence_id=valid_id,
                        acceptance_records=(),
                        reason_codes=(
                            "acceptance_record_not_found",
                        ),
                        diagnostics=(),
                    )

                records = tuple(
                    self._acceptance_entry_from_row(
                        row
                    ).acceptance_record
                    for row in rows
                )
                return AcceptanceRecordListResult(
                    status="found",
                    evidence_id=valid_id,
                    acceptance_records=records,
                    reason_codes=(),
                    diagnostics=(),
                )
        except (sqlite3.Error, ValueError):
            return AcceptanceRecordListResult(
                status="failed",
                evidence_id=valid_id,
                acceptance_records=(),
                reason_codes=("repository_operation_failed",),
                diagnostics=(),
            )

    def classify_write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult:
        exact_request = _require_exact_request(request)
        try:
            with closing(self._connect()) as connection:
                return self._classify_connection(
                    connection,
                    exact_request,
                )
        except (sqlite3.Error, ValueError):
            return _failed_classification(exact_request)

    def write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteResult:
        exact_request = _require_exact_request(request)
        connection: sqlite3.Connection | None = None
        classification: (
            EvidenceWriteClassificationResult | None
        ) = None

        try:
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE")
            classification = self._classify_connection(
                connection,
                exact_request,
            )

            if classification.classification == "new_evidence":
                serialized_evidence = serialize_accepted_evidence(
                    exact_request.accepted_evidence,
                    exact_request.canonical_evidence_bytes_digest,
                )
                serialized_acceptance = serialize_acceptance_record(
                    exact_request.acceptance_record,
                    exact_request.canonical_acceptance_bytes_digest,
                )
                connection.execute(
                    _INSERT_EVIDENCE_SQL,
                    self._evidence_insert_values(
                        serialized_evidence
                    ),
                )
                connection.execute(
                    _INSERT_ACCEPTANCE_SQL,
                    self._acceptance_insert_values(
                        serialized_acceptance
                    ),
                )
                connection.commit()
                return self._write_result(
                    classification,
                    "inserted_new_evidence",
                    mutation_performed=True,
                )

            if (
                classification.classification
                == "same_fact_new_acceptance"
            ):
                serialized_acceptance = serialize_acceptance_record(
                    exact_request.acceptance_record,
                    exact_request.canonical_acceptance_bytes_digest,
                )
                connection.execute(
                    _INSERT_ACCEPTANCE_SQL,
                    self._acceptance_insert_values(
                        serialized_acceptance
                    ),
                )
                connection.commit()
                return self._write_result(
                    classification,
                    "appended_acceptance_record",
                    mutation_performed=True,
                )

            connection.rollback()
            status_by_classification = {
                "exact_replay": "unchanged_exact_replay",
                "governance_replay": (
                    "unchanged_governance_replay"
                ),
                "identity_collision": (
                    "rejected_identity_collision"
                ),
                "acceptance_collision": (
                    "rejected_acceptance_collision"
                ),
                "rejected": "rejected_invalid_request",
            }
            status = status_by_classification.get(
                classification.classification,
                "rejected_invalid_request",
            )
            controlled = (
                classification
                if classification.classification
                in status_by_classification
                else self._classification_result(
                    exact_request,
                    "rejected",
                    None,
                    None,
                )
            )
            return self._write_result(
                controlled,
                status,
                mutation_performed=False,
            )
        except ValueError:
            if connection is not None:
                connection.rollback()
            if classification is None:
                failed = _failed_classification(exact_request)
                return self._write_result(
                    failed,
                    "failed_repository_operation",
                    mutation_performed=False,
                    reason_codes=(
                        "repository_operation_failed",
                    ),
                )
            rejected = self._classification_result(
                exact_request,
                "rejected",
                None,
                None,
            )
            return self._write_result(
                rejected,
                "rejected_invalid_request",
                mutation_performed=False,
            )
        except sqlite3.Error:
            if connection is not None:
                connection.rollback()
            failed = (
                classification
                if classification is not None
                else _failed_classification(exact_request)
            )
            return self._write_result(
                failed,
                "failed_repository_operation",
                mutation_performed=False,
                reason_codes=("repository_operation_failed",),
            )
        finally:
            if connection is not None:
                connection.close()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path,
            timeout=0.0,
            isolation_level=None,
            uri=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 0")
        return connection

    def _bootstrap_or_validate(
        self,
        database_existed: bool,
    ) -> None:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            if not database_existed:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    _CREATE_ACCEPTED_EVIDENCE_TABLE_SQL
                )
                connection.execute(_CREATE_ACCEPTANCE_TABLE_SQL)
                connection.execute(_CREATE_ACCEPTANCE_INDEX_SQL)
                connection.execute(
                    "PRAGMA user_version = "
                    f"{SQLITE_EVIDENCE_REPOSITORY_SCHEMA_VERSION}"
                )
                self._validate_schema(connection)
                connection.commit()
            else:
                self._validate_schema(connection)
        except (sqlite3.Error, ValueError):
            if connection is not None:
                connection.rollback()
            raise ValueError(
                "database schema is invalid or unsupported"
            ) from None
        finally:
            if connection is not None:
                connection.close()

    def _validate_schema(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        user_version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]
        if user_version != SQLITE_EVIDENCE_REPOSITORY_SCHEMA_VERSION:
            raise ValueError("unsupported database schema version")

        rows = connection.execute(
            """
            SELECT type, name, tbl_name, sql
            FROM sqlite_master
            WHERE name NOT LIKE 'sqlite_autoindex_%'
            ORDER BY type, name
            """
        ).fetchall()
        observed_keys = {
            (row["type"], row["name"], row["tbl_name"])
            for row in rows
        }
        if observed_keys != set(_EXPECTED_SCHEMA_OBJECTS):
            raise ValueError("unexpected database schema object")

        for row in rows:
            key = (row["type"], row["name"], row["tbl_name"])
            expected_sql = _EXPECTED_SCHEMA_OBJECTS[key]
            if row["sql"] is None or (
                _normalize_sql(row["sql"])
                != _normalize_sql(expected_sql)
            ):
                raise ValueError("database schema SQL mismatch")

        self._validate_table_columns(
            connection,
            "accepted_evidence_records",
            _EXPECTED_EVIDENCE_COLUMNS,
        )
        self._validate_table_columns(
            connection,
            "acceptance_records",
            _EXPECTED_ACCEPTANCE_COLUMNS,
        )

        foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(acceptance_records)"
        ).fetchall()
        if len(foreign_keys) != 1:
            raise ValueError("foreign key count mismatch")
        foreign_key = foreign_keys[0]
        if (
            foreign_key["table"] != "accepted_evidence_records"
            or foreign_key["from"] != "evidence_id"
            or foreign_key["to"] != "evidence_id"
            or foreign_key["on_update"] != "RESTRICT"
            or foreign_key["on_delete"] != "RESTRICT"
        ):
            raise ValueError("foreign key contract mismatch")

        index_columns = connection.execute(
            "PRAGMA index_info(acceptance_records_by_evidence)"
        ).fetchall()
        if tuple(row["name"] for row in index_columns) != (
            "evidence_id",
            "acceptance_record_id",
        ):
            raise ValueError("acceptance index contract mismatch")

    def _validate_table_columns(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        expected: tuple[tuple[str, str, int, int], ...],
    ) -> None:
        rows = connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
        observed = tuple(
            (
                row["name"],
                row["type"],
                row["notnull"],
                row["pk"],
            )
            for row in rows
        )
        if observed != expected:
            raise ValueError("database table column mismatch")

    def _load_evidence_entry(
        self,
        connection: sqlite3.Connection,
        evidence_id: str,
    ) -> _EvidenceEntry | None:
        row = connection.execute(
            """
            SELECT
                evidence_id,
                canonical_identity_digest,
                persistence_contract_version,
                payload_schema_id,
                identity_policy_id,
                identity_policy_version,
                payload_bytes_digest,
                payload_bytes
            FROM accepted_evidence_records
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()
        if row is None:
            return None
        return self._evidence_entry_from_row(row)

    def _load_acceptance_entry(
        self,
        connection: sqlite3.Connection,
        acceptance_record_id: str,
    ) -> _AcceptanceEntry | None:
        row = connection.execute(
            """
            SELECT
                acceptance_record_id,
                evidence_id,
                canonical_identity_digest,
                persistence_contract_version,
                payload_schema_id,
                identity_policy_id,
                identity_policy_version,
                payload_bytes_digest,
                payload_bytes
            FROM acceptance_records
            WHERE acceptance_record_id = ?
            """,
            (acceptance_record_id,),
        ).fetchone()
        if row is None:
            return None
        return self._acceptance_entry_from_row(row)

    def _evidence_entry_from_row(
        self,
        row: sqlite3.Row,
    ) -> _EvidenceEntry:
        serialized = SerializedAcceptedEvidenceRecord(
            persistence_contract_version=(
                row["persistence_contract_version"]
            ),
            payload_schema_id=row["payload_schema_id"],
            evidence_id=row["evidence_id"],
            identity_policy_id=row["identity_policy_id"],
            identity_policy_version=row["identity_policy_version"],
            canonical_identity_digest=(
                row["canonical_identity_digest"]
            ),
            payload_bytes_digest=row["payload_bytes_digest"],
            payload_bytes=bytes(row["payload_bytes"]),
        )
        accepted_evidence = deserialize_accepted_evidence(
            serialized
        )
        return _EvidenceEntry(
            accepted_evidence=accepted_evidence,
            canonical_digest=serialized.canonical_identity_digest,
            identity_projection=(
                identity_input_from_accepted_evidence(
                    accepted_evidence
                )
            ),
        )

    def _acceptance_entry_from_row(
        self,
        row: sqlite3.Row,
    ) -> _AcceptanceEntry:
        serialized = SerializedAcceptanceRecord(
            persistence_contract_version=(
                row["persistence_contract_version"]
            ),
            payload_schema_id=row["payload_schema_id"],
            acceptance_record_id=row["acceptance_record_id"],
            evidence_id=row["evidence_id"],
            identity_policy_id=row["identity_policy_id"],
            identity_policy_version=row["identity_policy_version"],
            canonical_identity_digest=(
                row["canonical_identity_digest"]
            ),
            payload_bytes_digest=row["payload_bytes_digest"],
            payload_bytes=bytes(row["payload_bytes"]),
        )
        acceptance_record = deserialize_acceptance_record(
            serialized
        )
        return _AcceptanceEntry(
            acceptance_record=acceptance_record,
            canonical_digest=serialized.canonical_identity_digest,
            identity_projection=(
                acceptance_identity_input_from_record(
                    acceptance_record
                )
            ),
        )

    def _classify_connection(
        self,
        connection: sqlite3.Connection,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult:
        evidence_entry = self._load_evidence_entry(
            connection,
            request.accepted_evidence.evidence_id,
        )
        acceptance_entry = self._load_acceptance_entry(
            connection,
            request.acceptance_record.acceptance_record_id,
        )
        evidence_projection = identity_input_from_accepted_evidence(
            request.accepted_evidence
        )
        acceptance_projection = (
            acceptance_identity_input_from_record(
                request.acceptance_record
            )
        )

        if (
            evidence_entry is not None
            and evidence_entry.canonical_digest
            != request.canonical_evidence_bytes_digest
        ):
            return self._classification_result(
                request,
                "identity_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and evidence_entry.identity_projection
            != evidence_projection
        ):
            return self._classification_result(
                request,
                "identity_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            acceptance_entry is not None
            and acceptance_entry.canonical_digest
            != request.canonical_acceptance_bytes_digest
        ):
            return self._classification_result(
                request,
                "acceptance_collision",
                evidence_entry,
                acceptance_entry,
            )

        if (
            acceptance_entry is not None
            and acceptance_entry.identity_projection
            != acceptance_projection
        ):
            return self._classification_result(
                request,
                "acceptance_collision",
                evidence_entry,
                acceptance_entry,
            )

        try:
            serialize_accepted_evidence(
                request.accepted_evidence,
                request.canonical_evidence_bytes_digest,
            )
            serialize_acceptance_record(
                request.acceptance_record,
                request.canonical_acceptance_bytes_digest,
            )
        except ValueError:
            return self._classification_result(
                request,
                "rejected",
                evidence_entry,
                acceptance_entry,
            )

        if evidence_entry is None and acceptance_entry is None:
            return self._classification_result(
                request,
                "new_evidence",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and acceptance_entry is None
        ):
            return self._classification_result(
                request,
                "same_fact_new_acceptance",
                evidence_entry,
                acceptance_entry,
            )

        if (
            evidence_entry is not None
            and acceptance_entry is not None
        ):
            if (
                evidence_entry.accepted_evidence
                == request.accepted_evidence
                and acceptance_entry.acceptance_record
                == request.acceptance_record
            ):
                replay_classification = "exact_replay"
            else:
                replay_classification = "governance_replay"

            return self._classification_result(
                request,
                replay_classification,
                evidence_entry,
                acceptance_entry,
            )

        return self._classification_result(
            request,
            "rejected",
            evidence_entry,
            acceptance_entry,
        )

    def _classification_result(
        self,
        request: EvidenceWriteRequest,
        classification: str,
        evidence_entry: _EvidenceEntry | None,
        acceptance_entry: _AcceptanceEntry | None,
    ) -> EvidenceWriteClassificationResult:
        return EvidenceWriteClassificationResult(
            classification=classification,
            evidence_id=request.accepted_evidence.evidence_id,
            acceptance_record_id=(
                request.acceptance_record.acceptance_record_id
            ),
            existing_evidence_digest=(
                evidence_entry.canonical_digest
                if evidence_entry is not None
                else None
            ),
            existing_acceptance_digest=(
                acceptance_entry.canonical_digest
                if acceptance_entry is not None
                else None
            ),
            reason_codes=(
                _classification_reason(classification),
            ),
            diagnostics=(),
        )

    def _evidence_insert_values(
        self,
        serialized: SerializedAcceptedEvidenceRecord,
    ) -> tuple[object, ...]:
        return (
            serialized.evidence_id,
            serialized.canonical_identity_digest,
            serialized.persistence_contract_version,
            serialized.payload_schema_id,
            serialized.identity_policy_id,
            serialized.identity_policy_version,
            serialized.payload_bytes_digest,
            sqlite3.Binary(serialized.payload_bytes),
        )

    def _acceptance_insert_values(
        self,
        serialized: SerializedAcceptanceRecord,
    ) -> tuple[object, ...]:
        return (
            serialized.acceptance_record_id,
            serialized.evidence_id,
            serialized.canonical_identity_digest,
            serialized.persistence_contract_version,
            serialized.payload_schema_id,
            serialized.identity_policy_id,
            serialized.identity_policy_version,
            serialized.payload_bytes_digest,
            sqlite3.Binary(serialized.payload_bytes),
        )

    def _write_result(
        self,
        classification: EvidenceWriteClassificationResult,
        status: str,
        *,
        mutation_performed: bool,
        reason_codes: tuple[str, ...] | None = None,
    ) -> EvidenceWriteResult:
        return EvidenceWriteResult(
            status=status,
            classification=classification.classification,
            evidence_id=classification.evidence_id,
            acceptance_record_id=(
                classification.acceptance_record_id
            ),
            mutation_performed=mutation_performed,
            reason_codes=(
                reason_codes
                if reason_codes is not None
                else classification.reason_codes
            ),
            diagnostics=classification.diagnostics,
        )


def _assert_protocol_shape(
    repository: object,
) -> None:
    del repository
