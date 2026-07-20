from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from threading import Lock, RLock
from typing import Final

from rie.evidence_materialization.evidence_materialization_contract import (
    EvidenceCollection,
)

from .evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
    deserialize_evidence_collection_repository_payload,
    serialize_evidence_collection_repository_payload,
)
from .evidence_repository_contract import (
    EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX,
    EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_ISSUE_MESSAGES,
    EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_ID_PREFIX,
    EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
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

_SQLITE_APPLICATION_ID: Final = 0x52434937
_PERSISTED_AUDIT_ACTION: Final = "persisted_revision"

_CREATE_COLLECTION_TABLE_SQL: Final = """
CREATE TABLE evidence_collection_records (
    collection_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    payload_digest TEXT NOT NULL,
    payload_bytes BLOB NOT NULL,
    CHECK (length(collection_id) > 0),
    CHECK (length(source_id) > 0),
    CHECK (length(payload_digest) = 64),
    CHECK (length(payload_bytes) > 0)
)
"""

_CREATE_REVISION_TABLE_SQL: Final = """
CREATE TABLE evidence_revision_records (
    revision_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL,
    collection_id TEXT NOT NULL UNIQUE,
    collection_payload_digest TEXT NOT NULL,
    previous_revision_id TEXT,
    actor_id TEXT NOT NULL,
    recorded_at_utc TEXT NOT NULL,
    audit_id TEXT NOT NULL UNIQUE,
    UNIQUE (source_id, revision_number),
    FOREIGN KEY (collection_id)
        REFERENCES evidence_collection_records(collection_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (previous_revision_id)
        REFERENCES evidence_revision_records(revision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (revision_number > 0),
    CHECK (length(source_id) > 0),
    CHECK (length(collection_payload_digest) = 64),
    CHECK (length(actor_id) > 0)
)
"""

_CREATE_AUDIT_TABLE_SQL: Final = """
CREATE TABLE evidence_audit_records (
    audit_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    revision_id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL,
    collection_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    recorded_at_utc TEXT NOT NULL,
    FOREIGN KEY (revision_id)
        REFERENCES evidence_revision_records(revision_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    FOREIGN KEY (collection_id)
        REFERENCES evidence_collection_records(collection_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CHECK (action = 'persisted_revision'),
    CHECK (revision_number > 0),
    CHECK (length(source_id) > 0),
    CHECK (length(actor_id) > 0)
)
"""

_EXPECTED_TABLES: Final = (
    "evidence_audit_records",
    "evidence_collection_records",
    "evidence_revision_records",
)
_EXPECTED_COLUMNS: Final = {
    "evidence_collection_records": (
        ("collection_id", "TEXT", 0, 1),
        ("source_id", "TEXT", 1, 0),
        ("contract_version", "TEXT", 1, 0),
        ("payload_digest", "TEXT", 1, 0),
        ("payload_bytes", "BLOB", 1, 0),
    ),
    "evidence_revision_records": (
        ("revision_id", "TEXT", 0, 1),
        ("source_id", "TEXT", 1, 0),
        ("revision_number", "INTEGER", 1, 0),
        ("collection_id", "TEXT", 1, 0),
        ("collection_payload_digest", "TEXT", 1, 0),
        ("previous_revision_id", "TEXT", 0, 0),
        ("actor_id", "TEXT", 1, 0),
        ("recorded_at_utc", "TEXT", 1, 0),
        ("audit_id", "TEXT", 1, 0),
    ),
    "evidence_audit_records": (
        ("audit_id", "TEXT", 0, 1),
        ("action", "TEXT", 1, 0),
        ("revision_id", "TEXT", 1, 0),
        ("source_id", "TEXT", 1, 0),
        ("revision_number", "INTEGER", 1, 0),
        ("collection_id", "TEXT", 1, 0),
        ("actor_id", "TEXT", 1, 0),
        ("recorded_at_utc", "TEXT", 1, 0),
    ),
}

_PATH_LOCKS_GUARD = Lock()
_PATH_LOCKS: dict[str, RLock] = {}


class _UnsupportedSchemaError(RuntimeError):
    pass


class _CorruptRepositoryError(RuntimeError):
    pass


def _path_lock(path: Path) -> RLock:
    key = str(path.resolve())
    with _PATH_LOCKS_GUARD:
        lock = _PATH_LOCKS.get(key)
        if lock is None:
            lock = RLock()
            _PATH_LOCKS[key] = lock
        return lock


def _issue(code: str) -> EvidenceRepositoryIssue:
    return EvidenceRepositoryIssue(
        code=code,
        message=EVIDENCE_REPOSITORY_ISSUE_MESSAGES[code],
    )


def _format_utc(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise _CorruptRepositoryError("invalid stored timestamp") from exc
    return parsed.replace(tzinfo=timezone.utc)


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    text = str(exc).lower()
    return "locked" in text or "busy" in text


class SqliteEvidenceCollectionRepository:
    def __init__(self, database_path: str | Path) -> None:
        if isinstance(database_path, Path):
            path = database_path
        elif type(database_path) is str and database_path != "":
            path = Path(database_path)
        else:
            raise ValueError("database_path must be a non-empty path")
        if path.exists() and path.is_dir():
            raise ValueError("database_path must identify a file")
        if not path.parent.exists() or not path.parent.is_dir():
            raise ValueError("database_path parent must exist")
        self._database_path = path
        self._lock = _path_lock(path)
        with self._lock:
            try:
                with closing(self._connect()) as connection:
                    self._bootstrap_or_validate(connection)
            except sqlite3.OperationalError as exc:
                if _is_busy(exc):
                    raise RuntimeError("repository is busy") from exc
                raise RuntimeError("repository is unavailable") from exc

    def persist(
        self,
        request: EvidenceRepositoryWriteRequest,
    ) -> EvidenceRepositoryWriteResult:
        if type(request) is not EvidenceRepositoryWriteRequest:
            return self._rejected_write("invalid_request")
        try:
            payload_bytes = serialize_evidence_collection_repository_payload(
                request.collection
            )
            payload_digest = (
                calculate_evidence_collection_repository_payload_digest(
                    request.collection
                )
            )
        except (TypeError, ValueError):
            return self._rejected_write("invalid_collection")
        if payload_digest != request.expected_collection_payload_digest:
            return self._rejected_write(
                "collection_payload_digest_mismatch"
            )

        with self._lock:
            connection: sqlite3.Connection | None = None
            try:
                connection = self._connect()
                self._validate_schema(connection)
                connection.execute("BEGIN IMMEDIATE")
                existing = connection.execute(
                    """
                    SELECT collection_id, source_id, contract_version,
                           payload_digest, payload_bytes
                    FROM evidence_collection_records
                    WHERE collection_id = ?
                    """,
                    (request.collection.collection_id,),
                ).fetchone()
                if existing is not None:
                    result = self._existing_result(
                        connection,
                        request,
                        payload_digest,
                        payload_bytes,
                        existing,
                    )
                    connection.rollback()
                    return result

                latest = connection.execute(
                    """
                    SELECT revision_id, revision_number
                    FROM evidence_revision_records
                    WHERE source_id = ?
                    ORDER BY revision_number DESC
                    LIMIT 1
                    """,
                    (request.collection.source_id,),
                ).fetchone()
                if latest is None:
                    revision_number = 1
                    previous_revision_id = None
                else:
                    previous_revision_id = latest[0]
                    revision_number = int(latest[1]) + 1

                revision_id = calculate_evidence_repository_revision_id(
                    source_id=request.collection.source_id,
                    revision_number=revision_number,
                    collection_id=request.collection.collection_id,
                    collection_payload_digest=payload_digest,
                    previous_revision_id=previous_revision_id,
                )
                audit_id = calculate_evidence_repository_audit_id(
                    action=_PERSISTED_AUDIT_ACTION,
                    revision_id=revision_id,
                    source_id=request.collection.source_id,
                    revision_number=revision_number,
                    collection_id=request.collection.collection_id,
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                )
                revision = EvidenceRepositoryRevision(
                    contract_version=EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
                    revision_id=revision_id,
                    source_id=request.collection.source_id,
                    revision_number=revision_number,
                    collection_id=request.collection.collection_id,
                    collection_payload_digest=payload_digest,
                    previous_revision_id=previous_revision_id,
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                    audit_id=audit_id,
                )
                audit = EvidenceRepositoryAuditRecord(
                    contract_version=(
                        EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION
                    ),
                    audit_id=audit_id,
                    action=_PERSISTED_AUDIT_ACTION,
                    revision_id=revision_id,
                    source_id=request.collection.source_id,
                    revision_number=revision_number,
                    collection_id=request.collection.collection_id,
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                )

                connection.execute(
                    """
                    INSERT INTO evidence_collection_records (
                        collection_id,
                        source_id,
                        contract_version,
                        payload_digest,
                        payload_bytes
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        request.collection.collection_id,
                        request.collection.source_id,
                        request.collection.contract_version,
                        payload_digest,
                        payload_bytes,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO evidence_revision_records (
                        revision_id,
                        source_id,
                        revision_number,
                        collection_id,
                        collection_payload_digest,
                        previous_revision_id,
                        actor_id,
                        recorded_at_utc,
                        audit_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        revision.revision_id,
                        revision.source_id,
                        revision.revision_number,
                        revision.collection_id,
                        revision.collection_payload_digest,
                        revision.previous_revision_id,
                        revision.actor_id,
                        _format_utc(revision.recorded_at_utc),
                        revision.audit_id,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO evidence_audit_records (
                        audit_id,
                        action,
                        revision_id,
                        source_id,
                        revision_number,
                        collection_id,
                        actor_id,
                        recorded_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        audit.audit_id,
                        audit.action,
                        audit.revision_id,
                        audit.source_id,
                        audit.revision_number,
                        audit.collection_id,
                        audit.actor_id,
                        _format_utc(audit.recorded_at_utc),
                    ),
                )
                connection.commit()
                return EvidenceRepositoryWriteResult(
                    contract_version=(
                        EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
                    ),
                    status="persisted",
                    mutation_performed=True,
                    revision=revision,
                    audit_record=audit,
                    collection=request.collection,
                    issue=None,
                )
            except sqlite3.OperationalError as exc:
                if connection is not None:
                    connection.rollback()
                return self._rejected_write(
                    "repository_busy" if _is_busy(exc)
                    else "repository_unavailable"
                )
            except _UnsupportedSchemaError:
                if connection is not None:
                    connection.rollback()
                return self._rejected_write("unsupported_schema")
            except (
                _CorruptRepositoryError,
                sqlite3.DatabaseError,
                TypeError,
                ValueError,
            ):
                if connection is not None:
                    connection.rollback()
                return self._rejected_write("repository_corrupt")
            finally:
                if connection is not None:
                    connection.close()

    def get_by_collection_id(
        self,
        collection_id: str,
    ) -> EvidenceRepositoryLookupResult:
        if type(collection_id) is not str or collection_id == "":
            return self._rejected_lookup("invalid_request")
        return self._lookup(
            """
            SELECT revision_id
            FROM evidence_revision_records
            WHERE collection_id = ?
            """,
            (collection_id,),
        )

    def get_by_source_revision(
        self,
        source_id: str,
        revision_number: int,
    ) -> EvidenceRepositoryLookupResult:
        if (
            type(source_id) is not str
            or source_id == ""
            or type(revision_number) is not int
            or revision_number < 1
        ):
            return self._rejected_lookup("invalid_request")
        return self._lookup(
            """
            SELECT revision_id
            FROM evidence_revision_records
            WHERE source_id = ? AND revision_number = ?
            """,
            (source_id, revision_number),
        )

    def list_source_history(
        self,
        source_id: str,
    ) -> EvidenceRepositoryHistoryResult:
        return self._history(source_id)

    def list_source_audit(
        self,
        source_id: str,
    ) -> EvidenceRepositoryHistoryResult:
        return self._history(source_id)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            str(self._database_path),
            timeout=0.0,
            isolation_level=None,
        )
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _bootstrap_or_validate(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        objects = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        application_id = int(
            connection.execute("PRAGMA application_id").fetchone()[0]
        )
        user_version = int(
            connection.execute("PRAGMA user_version").fetchone()[0]
        )
        if not objects and application_id == 0 and user_version == 0:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    f"PRAGMA application_id = {_SQLITE_APPLICATION_ID}"
                )
                connection.execute(
                    "PRAGMA user_version = "
                    f"{SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION}"
                )
                connection.execute(_CREATE_COLLECTION_TABLE_SQL)
                connection.execute(_CREATE_REVISION_TABLE_SQL)
                connection.execute(_CREATE_AUDIT_TABLE_SQL)
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        self._validate_schema(connection)

    def _validate_schema(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        foreign_keys = int(
            connection.execute("PRAGMA foreign_keys").fetchone()[0]
        )
        application_id = int(
            connection.execute("PRAGMA application_id").fetchone()[0]
        )
        user_version = int(
            connection.execute("PRAGMA user_version").fetchone()[0]
        )
        if foreign_keys != 1:
            raise _UnsupportedSchemaError("foreign keys are disabled")
        if application_id != _SQLITE_APPLICATION_ID:
            raise _UnsupportedSchemaError(
                SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID
            )
        if (
            user_version
            != SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION
        ):
            raise _UnsupportedSchemaError("schema version mismatch")

        table_names = tuple(
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()
        )
        if table_names != _EXPECTED_TABLES:
            raise _UnsupportedSchemaError("table set mismatch")

        unexpected_objects = connection.execute(
            """
            SELECT type, name
            FROM sqlite_master
            WHERE (
                type IN ('view', 'trigger')
                OR (type = 'index' AND name NOT LIKE 'sqlite_autoindex_%')
            )
            AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()
        if unexpected_objects:
            raise _UnsupportedSchemaError("unexpected schema object")

        for table_name, expected in _EXPECTED_COLUMNS.items():
            actual = tuple(
                (row[1], row[2], int(row[3]), int(row[5]))
                for row in connection.execute(
                    f"PRAGMA table_info({table_name})"
                ).fetchall()
            )
            if actual != expected:
                raise _UnsupportedSchemaError("column set mismatch")

        if not connection.execute(
            "PRAGMA foreign_key_list(evidence_revision_records)"
        ).fetchall():
            raise _UnsupportedSchemaError("revision foreign keys missing")
        if not connection.execute(
            "PRAGMA foreign_key_list(evidence_audit_records)"
        ).fetchall():
            raise _UnsupportedSchemaError("audit foreign keys missing")

    def _existing_result(
        self,
        connection: sqlite3.Connection,
        request: EvidenceRepositoryWriteRequest,
        payload_digest: str,
        payload_bytes: bytes,
        existing: tuple,
    ) -> EvidenceRepositoryWriteResult:
        if (
            existing[1] != request.collection.source_id
            or existing[2] != request.collection.contract_version
            or existing[3] != payload_digest
            or bytes(existing[4]) != payload_bytes
        ):
            return self._rejected_write("collection_identity_collision")
        lookup = self._load_lookup_by_collection(
            connection,
            request.collection.collection_id,
        )
        if lookup.status != "found":
            raise _CorruptRepositoryError("existing collection has no revision")
        return EvidenceRepositoryWriteResult(
            contract_version=(
                EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
            ),
            status="unchanged_exact_replay",
            mutation_performed=False,
            revision=lookup.revision,
            audit_record=lookup.audit_record,
            collection=lookup.collection,
            issue=None,
        )

    def _lookup(
        self,
        query: str,
        parameters: tuple,
    ) -> EvidenceRepositoryLookupResult:
        with self._lock:
            try:
                with closing(self._connect()) as connection:
                    self._validate_schema(connection)
                    row = connection.execute(query, parameters).fetchone()
                    if row is None:
                        return EvidenceRepositoryLookupResult(
                            contract_version=(
                                EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
                            ),
                            status="not_found",
                            revision=None,
                            audit_record=None,
                            collection=None,
                            issue=None,
                        )
                    return self._load_lookup_by_revision(
                        connection,
                        row[0],
                    )
            except sqlite3.OperationalError as exc:
                return self._rejected_lookup(
                    "repository_busy" if _is_busy(exc)
                    else "repository_unavailable"
                )
            except _UnsupportedSchemaError:
                return self._rejected_lookup("unsupported_schema")
            except (
                _CorruptRepositoryError,
                sqlite3.DatabaseError,
                TypeError,
                ValueError,
            ):
                return self._rejected_lookup("repository_corrupt")

    def _history(
        self,
        source_id: str,
    ) -> EvidenceRepositoryHistoryResult:
        if type(source_id) is not str or source_id == "":
            return self._rejected_history(source_id, "invalid_request")
        with self._lock:
            try:
                with closing(self._connect()) as connection:
                    self._validate_schema(connection)
                    ids = connection.execute(
                        """
                        SELECT revision_id
                        FROM evidence_revision_records
                        WHERE source_id = ?
                        ORDER BY revision_number ASC
                        """,
                        (source_id,),
                    ).fetchall()
                    if not ids:
                        return EvidenceRepositoryHistoryResult(
                            contract_version=(
                                EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
                            ),
                            status="not_found",
                            source_id=source_id,
                            revisions=(),
                            audit_records=(),
                            issue=None,
                        )
                    lookups = tuple(
                        self._load_lookup_by_revision(connection, row[0])
                        for row in ids
                    )
                    return EvidenceRepositoryHistoryResult(
                        contract_version=(
                            EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
                        ),
                        status="found",
                        source_id=source_id,
                        revisions=tuple(
                            item.revision for item in lookups
                            if item.revision is not None
                        ),
                        audit_records=tuple(
                            item.audit_record for item in lookups
                            if item.audit_record is not None
                        ),
                        issue=None,
                    )
            except sqlite3.OperationalError as exc:
                return self._rejected_history(
                    source_id,
                    "repository_busy" if _is_busy(exc)
                    else "repository_unavailable",
                )
            except _UnsupportedSchemaError:
                return self._rejected_history(
                    source_id,
                    "unsupported_schema",
                )
            except (
                _CorruptRepositoryError,
                sqlite3.DatabaseError,
                TypeError,
                ValueError,
            ):
                return self._rejected_history(
                    source_id,
                    "repository_corrupt",
                )

    def _load_lookup_by_collection(
        self,
        connection: sqlite3.Connection,
        collection_id: str,
    ) -> EvidenceRepositoryLookupResult:
        row = connection.execute(
            """
            SELECT revision_id
            FROM evidence_revision_records
            WHERE collection_id = ?
            """,
            (collection_id,),
        ).fetchone()
        if row is None:
            raise _CorruptRepositoryError("collection revision missing")
        return self._load_lookup_by_revision(connection, row[0])

    def _load_lookup_by_revision(
        self,
        connection: sqlite3.Connection,
        revision_id: str,
    ) -> EvidenceRepositoryLookupResult:
        row = connection.execute(
            """
            SELECT
                r.revision_id,
                r.source_id,
                r.revision_number,
                r.collection_id,
                r.collection_payload_digest,
                r.previous_revision_id,
                r.actor_id,
                r.recorded_at_utc,
                r.audit_id,
                c.contract_version,
                c.payload_digest,
                c.payload_bytes,
                a.action,
                a.revision_id,
                a.source_id,
                a.revision_number,
                a.collection_id,
                a.actor_id,
                a.recorded_at_utc
            FROM evidence_revision_records AS r
            JOIN evidence_collection_records AS c
              ON c.collection_id = r.collection_id
            JOIN evidence_audit_records AS a
              ON a.audit_id = r.audit_id
            WHERE r.revision_id = ?
            """,
            (revision_id,),
        ).fetchone()
        if row is None:
            raise _CorruptRepositoryError("revision row missing")

        collection = deserialize_evidence_collection_repository_payload(
            bytes(row[11])
        )
        calculated_digest = (
            calculate_evidence_collection_repository_payload_digest(
                collection
            )
        )
        if (
            row[4] != calculated_digest
            or row[10] != calculated_digest
            or row[3] != collection.collection_id
            or row[1] != collection.source_id
            or row[9] != collection.contract_version
        ):
            raise _CorruptRepositoryError("stored collection mismatch")

        recorded_at = _parse_utc(row[7])
        revision = EvidenceRepositoryRevision(
            contract_version=EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
            revision_id=row[0],
            source_id=row[1],
            revision_number=int(row[2]),
            collection_id=row[3],
            collection_payload_digest=row[4],
            previous_revision_id=row[5],
            actor_id=row[6],
            recorded_at_utc=recorded_at,
            audit_id=row[8],
        )
        expected_revision_id = calculate_evidence_repository_revision_id(
            source_id=revision.source_id,
            revision_number=revision.revision_number,
            collection_id=revision.collection_id,
            collection_payload_digest=revision.collection_payload_digest,
            previous_revision_id=revision.previous_revision_id,
        )
        if revision.revision_id != expected_revision_id:
            raise _CorruptRepositoryError("revision identity mismatch")

        audit_recorded_at = _parse_utc(row[18])
        audit = EvidenceRepositoryAuditRecord(
            contract_version=(
                EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION
            ),
            audit_id=row[8],
            action=row[12],
            revision_id=row[13],
            source_id=row[14],
            revision_number=int(row[15]),
            collection_id=row[16],
            actor_id=row[17],
            recorded_at_utc=audit_recorded_at,
        )
        expected_audit_id = calculate_evidence_repository_audit_id(
            action=audit.action,
            revision_id=audit.revision_id,
            source_id=audit.source_id,
            revision_number=audit.revision_number,
            collection_id=audit.collection_id,
            actor_id=audit.actor_id,
            recorded_at_utc=audit.recorded_at_utc,
        )
        if (
            audit.audit_id != expected_audit_id
            or audit.revision_id != revision.revision_id
            or audit.source_id != revision.source_id
            or audit.revision_number != revision.revision_number
            or audit.collection_id != revision.collection_id
        ):
            raise _CorruptRepositoryError("audit identity mismatch")

        return EvidenceRepositoryLookupResult(
            contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
            status="found",
            revision=revision,
            audit_record=audit,
            collection=collection,
            issue=None,
        )

    @staticmethod
    def _rejected_write(code: str) -> EvidenceRepositoryWriteResult:
        return EvidenceRepositoryWriteResult(
            contract_version=(
                EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            mutation_performed=False,
            revision=None,
            audit_record=None,
            collection=None,
            issue=_issue(code),
        )

    @staticmethod
    def _rejected_lookup(code: str) -> EvidenceRepositoryLookupResult:
        return EvidenceRepositoryLookupResult(
            contract_version=(
                EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            revision=None,
            audit_record=None,
            collection=None,
            issue=_issue(code),
        )

    @staticmethod
    def _rejected_history(
        source_id: object,
        code: str,
    ) -> EvidenceRepositoryHistoryResult:
        safe_source_id = source_id if type(source_id) is str and source_id else "invalid"
        return EvidenceRepositoryHistoryResult(
            contract_version=(
                EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            source_id=safe_source_id,
            revisions=(),
            audit_records=(),
            issue=_issue(code),
        )


__all__ = ("SqliteEvidenceCollectionRepository",)
