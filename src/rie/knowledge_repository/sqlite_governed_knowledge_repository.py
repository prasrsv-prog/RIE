from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sqlite3

from rie.application.governed_knowledge_constructor import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED,
    GovernedKnowledgeConstructionResult,
)
from rie.domain.governed_knowledge import (
    GovernedKnowledge,
    compute_governed_knowledge_id,
    governed_knowledge_identity_input_from_record,
)
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
    GovernedKnowledgeLifecycleAssertionInterpretationResult,
    compute_governed_knowledge_lifecycle_assertion_interpretation_result_id,
    governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record,
)
from rie.domain.knowledge_candidate import (
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)
from .knowledge_repository_canonicalization import (
    calculate_governed_knowledge_repository_payload_digest,
    calculate_knowledge_repository_audit_id,
    calculate_knowledge_repository_lifecycle_transition_record_id,
    calculate_knowledge_repository_lineage_record_id,
    calculate_knowledge_repository_revision_id,
    deserialize_governed_knowledge_repository_payload,
    serialize_governed_knowledge_repository_payload,
)
from .knowledge_repository_contract import (
    KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_POLICY_ID,
    KNOWLEDGE_REPOSITORY_POLICY_VERSION,
    KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION,
    SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID,
    SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION,
    KnowledgeRepositoryAuditRecord,
    KnowledgeRepositoryHistoryResult,
    KnowledgeRepositoryInitialWriteRequest,
    KnowledgeRepositoryLifecycleTransitionRecord,
    KnowledgeRepositoryLifecycleTransitionRequest,
    KnowledgeRepositoryLineageRecord,
    KnowledgeRepositoryLookupResult,
    KnowledgeRepositoryRevision,
    KnowledgeRepositoryWriteResult,
    _issue,
)

_INITIAL_ACTION = "persist_initial_governed_knowledge"
_TRANSITION_ACTION = "append_explicit_lifecycle_transition"
_ALLOWED_LIFECYCLE_STATUSES = {
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
}

_GATE_8_CONTRACT_MODULE = (
    "rie.persisted_evidence_knowledge_construction."
    "persisted_evidence_knowledge_construction_contract"
)
_GATE_8_RESULT_NAME = "PersistedEvidenceKnowledgeConstructionResult"
_GATE_8_COMPATIBILITY_RECORD_NAME = (
    "PersistedEvidenceKnowledgeCompatibilityRecord"
)
_GATE_8_RESULT_CONTRACT_VERSION = (
    "persisted_evidence_knowledge_construction_result_contract_v1"
)
_GATE_8_COMPATIBILITY_RECORD_CONTRACT_VERSION = (
    "persisted_evidence_knowledge_compatibility_record_contract_v1"
)
_GATE_8_CONSTRUCTED_STATUS = "constructed"
_GATE_8_COMPATIBILITY_POLICY_ID = (
    "rcis-persisted-evidence-knowledge-compatibility"
)
_GATE_8_COMPATIBILITY_POLICY_VERSION = "1.0.0"
_GATE_8_COMPATIBILITY_RECORD_ID_PREFIX = "pekc1_"


def _is_exact_gate_8_type(value: object, expected_name: str) -> bool:
    value_type = type(value)
    return (
        value_type.__module__ == _GATE_8_CONTRACT_MODULE
        and value_type.__qualname__ == expected_name
    )


def _derive_gate_8_compatibility_record_id(record: object) -> str:
    identity = {
        "contract_version": record.contract_version,
        "repository_revision_id": record.repository_revision_id,
        "source_id": record.source_id,
        "revision_number": record.revision_number,
        "previous_revision_id": record.previous_revision_id,
        "collection_id": record.collection_id,
        "collection_payload_digest": record.collection_payload_digest,
        "repository_audit_id": record.repository_audit_id,
        "traceable_evidence_id": record.traceable_evidence_id,
        "accepted_evidence_id": record.accepted_evidence_id,
        "acceptance_record_ids": sorted(
            record.acceptance_record_ids
        ),
        "construction_rule_id": record.construction_rule_id,
        "construction_rule_version": record.construction_rule_version,
        "compatibility_policy_id": record.compatibility_policy_id,
        "compatibility_policy_version": (
            record.compatibility_policy_version
        ),
    }
    canonical = json.dumps(
        identity,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return (
        _GATE_8_COMPATIBILITY_RECORD_ID_PREFIX
        + hashlib.sha256(canonical).hexdigest()
    )


class _UnsupportedSchemaError(RuntimeError):
    pass


class SqliteGovernedKnowledgeRepository:
    def __init__(
        self,
        database_path: str | Path,
        *,
        timeout_seconds: float = 5.0,
    ) -> None:
        if not isinstance(database_path, (str, Path)):
            raise TypeError("database_path must be str or Path")
        if (
            not isinstance(timeout_seconds, (int, float))
            or timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be positive")
        self._database_path = Path(database_path)
        self._timeout_seconds = float(timeout_seconds)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path,
            timeout=self._timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "PRAGMA busy_timeout = "
            + str(int(self._timeout_seconds * 1000))
        )
        self._ensure_schema(connection)
        return connection

    @staticmethod
    def _ensure_schema(connection: sqlite3.Connection) -> None:
        existing = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            if not str(row[0]).startswith("sqlite_")
        }
        required = {
            "knowledge_repository_metadata",
            "governed_knowledge_payloads",
            "knowledge_repository_lineage_records",
            "knowledge_repository_lifecycle_results",
            "knowledge_repository_transition_records",
            "knowledge_repository_revisions",
            "knowledge_repository_audit_records",
        }
        if existing and existing != required:
            raise _UnsupportedSchemaError("unsupported non-empty schema")
        if not existing:
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.executescript(
                    """
                    CREATE TABLE knowledge_repository_metadata (
                        schema_id TEXT NOT NULL,
                        schema_version INTEGER NOT NULL
                    );
                    CREATE TABLE governed_knowledge_payloads (
                        governed_knowledge_id TEXT PRIMARY KEY,
                        payload_digest TEXT NOT NULL,
                        payload BLOB NOT NULL
                    );
                    CREATE TABLE knowledge_repository_lineage_records (
                        lineage_record_id TEXT PRIMARY KEY,
                        governed_knowledge_id TEXT NOT NULL UNIQUE,
                        payload BLOB NOT NULL
                    );
                    CREATE TABLE knowledge_repository_lifecycle_results (
                        lifecycle_interpretation_result_id TEXT PRIMARY KEY,
                        governed_knowledge_id TEXT NOT NULL,
                        payload_digest TEXT NOT NULL,
                        payload BLOB NOT NULL
                    );
                    CREATE TABLE knowledge_repository_transition_records (
                        transition_record_id TEXT PRIMARY KEY,
                        governed_knowledge_id TEXT NOT NULL,
                        from_revision_id TEXT NOT NULL UNIQUE,
                        payload BLOB NOT NULL
                    );
                    CREATE TABLE knowledge_repository_revisions (
                        revision_id TEXT PRIMARY KEY,
                        governed_knowledge_id TEXT NOT NULL,
                        revision_number INTEGER NOT NULL,
                        previous_revision_id TEXT UNIQUE,
                        lineage_record_id TEXT NOT NULL,
                        lifecycle_interpretation_result_id TEXT NOT NULL,
                        transition_record_id TEXT,
                        audit_id TEXT NOT NULL UNIQUE,
                        payload BLOB NOT NULL,
                        UNIQUE(governed_knowledge_id, revision_number)
                    );
                    CREATE TABLE knowledge_repository_audit_records (
                        audit_id TEXT PRIMARY KEY,
                        revision_id TEXT NOT NULL UNIQUE,
                        governed_knowledge_id TEXT NOT NULL,
                        payload BLOB NOT NULL
                    );
                    """
                )
                connection.execute(
                    "INSERT INTO knowledge_repository_metadata"
                    "(schema_id, schema_version) VALUES (?, ?)",
                    (
                        SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID,
                        SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION,
                    ),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        row = connection.execute(
            "SELECT schema_id, schema_version "
            "FROM knowledge_repository_metadata"
        ).fetchone()
        if (
            row is None
            or row["schema_id"]
            != SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID
            or row["schema_version"]
            != SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION
        ):
            raise _UnsupportedSchemaError("unsupported schema metadata")

    @staticmethod
    def _map_database_issue(error: BaseException) -> str:
        text = str(error).lower()
        if isinstance(error, _UnsupportedSchemaError):
            return "unsupported_schema"
        if isinstance(error, sqlite3.OperationalError) and (
            "locked" in text or "busy" in text
        ):
            return "repository_busy"
        if isinstance(error, sqlite3.DatabaseError) and (
            "malformed" in text or "not a database" in text
        ):
            return "repository_corrupt"
        return "repository_unavailable"

    @staticmethod
    def _rejected(code: str) -> KnowledgeRepositoryWriteResult:
        return KnowledgeRepositoryWriteResult(
            contract_version=(
                KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            mutation_performed=False,
            revision=None,
            lineage_record=None,
            transition_record=None,
            audit_record=None,
            governed_knowledge=None,
            lifecycle_interpretation_result=None,
            issue=_issue(code),
        )

    @staticmethod
    def _lookup_rejected(code: str) -> KnowledgeRepositoryLookupResult:
        return KnowledgeRepositoryLookupResult(
            contract_version=(
                KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            revision=None,
            lineage_record=None,
            transition_record=None,
            audit_record=None,
            governed_knowledge=None,
            lifecycle_interpretation_result=None,
            issue=_issue(code),
        )

    @staticmethod
    def _history_rejected(
        governed_knowledge_id: str,
        code: str,
    ) -> KnowledgeRepositoryHistoryResult:
        return KnowledgeRepositoryHistoryResult(
            contract_version=(
                KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
            ),
            status="rejected",
            governed_knowledge_id=governed_knowledge_id or "<invalid>",
            governed_knowledge=None,
            lineage_record=None,
            revisions=(),
            lifecycle_interpretation_results=(),
            transition_records=(),
            audit_records=(),
            issue=_issue(code),
        )

    @staticmethod
    def _verify_lifecycle_result(
        result: object,
        governed_knowledge_id: str,
    ) -> str | None:
        if not isinstance(
            result,
            GovernedKnowledgeLifecycleAssertionInterpretationResult,
        ):
            return "invalid_lifecycle_interpretation_result"
        try:
            result.__post_init__()
        except Exception:
            return "invalid_lifecycle_interpretation_result"
        if result.result_status not in _ALLOWED_LIFECYCLE_STATUSES:
            return "invalid_lifecycle_interpretation_result"
        if result.premise.governed_knowledge_id != governed_knowledge_id:
            return "lifecycle_interpretation_subject_mismatch"
        try:
            expected_id = (
                compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
                    governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
                        result
                    )
                )
            )
        except Exception:
            return "invalid_lifecycle_interpretation_result"
        if (
            expected_id
            != result.governed_knowledge_lifecycle_assertion_interpretation_result_id
        ):
            return "lifecycle_interpretation_identity_mismatch"
        return None

    @staticmethod
    def _validate_initial(
        request: object,
    ) -> tuple[str | None, dict[str, object] | None]:
        if not isinstance(
            request,
            KnowledgeRepositoryInitialWriteRequest,
        ):
            return "invalid_request", None
        if (
            request.contract_version
            != KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION
        ):
            return "unsupported_contract_version", None
        if (
            request.repository_policy_id
            != KNOWLEDGE_REPOSITORY_POLICY_ID
            or request.repository_policy_version
            != KNOWLEDGE_REPOSITORY_POLICY_VERSION
        ):
            return "unsupported_repository_policy", None
        try:
            request.__post_init__()
        except Exception:
            return "invalid_request", None

        governed = request.governed_knowledge
        try:
            governed.__post_init__()
            governed_id = compute_governed_knowledge_id(
                governed_knowledge_identity_input_from_record(governed)
            )
        except Exception:
            return "invalid_governed_knowledge", None
        if governed_id != governed.governed_knowledge_id:
            return "governed_knowledge_identity_mismatch", None

        persisted = (
            request.persisted_evidence_knowledge_construction_result
        )
        if not _is_exact_gate_8_type(
            persisted,
            _GATE_8_RESULT_NAME,
        ):
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        try:
            persisted.__post_init__()
        except Exception:
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        if (
            persisted.contract_version
            != _GATE_8_RESULT_CONTRACT_VERSION
        ):
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        if persisted.status != _GATE_8_CONSTRUCTED_STATUS:
            return (
                "persisted_evidence_knowledge_construction_rejected",
                None,
            )
        if persisted.mutation_performed or persisted.issue is not None:
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        compatibility = persisted.compatibility_record
        nested = persisted.knowledge_construction_result
        if compatibility is None:
            return (
                "missing_persisted_evidence_knowledge_compatibility_record",
                None,
            )
        if not _is_exact_gate_8_type(
            compatibility,
            _GATE_8_COMPATIBILITY_RECORD_NAME,
        ):
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        try:
            compatibility.__post_init__()
        except Exception:
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        if (
            compatibility.contract_version
            != _GATE_8_COMPATIBILITY_RECORD_CONTRACT_VERSION
            or compatibility.compatibility_policy_id
            != _GATE_8_COMPATIBILITY_POLICY_ID
            or compatibility.compatibility_policy_version
            != _GATE_8_COMPATIBILITY_POLICY_VERSION
        ):
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        if nested is None or nested.knowledge_candidate is None:
            return "invalid_gate_8_knowledge_candidate", None

        candidate = nested.knowledge_candidate
        try:
            candidate.__post_init__()
            candidate_id = compute_knowledge_candidate_id(
                identity_input_from_knowledge_candidate(candidate)
            )
        except Exception:
            return "invalid_gate_8_knowledge_candidate", None
        if candidate_id != candidate.knowledge_candidate_id:
            return (
                "gate_8_knowledge_candidate_identity_mismatch",
                None,
            )
        snapshot = compute_knowledge_candidate_review_snapshot_digest(
            candidate
        )
        if (
            governed.knowledge_candidate_id
            != candidate.knowledge_candidate_id
            or governed.knowledge_candidate_contract_version
            != candidate.contract_version
            or governed.knowledge_candidate_snapshot_digest != snapshot
        ):
            return (
                "governed_knowledge_candidate_lineage_mismatch",
                None,
            )

        governed_result = (
            request.governed_knowledge_construction_result
        )
        if not isinstance(
            governed_result,
            GovernedKnowledgeConstructionResult,
        ):
            return "invalid_governed_knowledge_construction_result", None
        try:
            governed_result.__post_init__()
        except Exception:
            return "invalid_governed_knowledge_construction_result", None
        if (
            governed_result.result_status
            != GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED
        ):
            return "governed_knowledge_construction_rejected", None
        if governed_result.governed_knowledge != governed:
            return (
                "governed_knowledge_construction_result_mismatch",
                None,
            )

        lifecycle_issue = (
            SqliteGovernedKnowledgeRepository._verify_lifecycle_result(
                request.lifecycle_interpretation_result,
                governed.governed_knowledge_id,
            )
        )
        if lifecycle_issue is not None:
            return lifecycle_issue, None

        try:
            expected_compatibility_id = (
                _derive_gate_8_compatibility_record_id(
                    compatibility
                )
            )
        except Exception:
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )
        if (
            expected_compatibility_id
            != compatibility.compatibility_record_id
        ):
            return (
                "invalid_persisted_evidence_knowledge_construction_result",
                None,
            )

        lineage_kwargs = dict(
            governed_knowledge_id=governed.governed_knowledge_id,
            governed_knowledge_contract_version=(
                governed.contract_version
            ),
            knowledge_candidate_id=candidate.knowledge_candidate_id,
            knowledge_candidate_contract_version=candidate.contract_version,
            knowledge_candidate_snapshot_digest=snapshot,
            persisted_evidence_knowledge_compatibility_record_id=(
                compatibility.compatibility_record_id
            ),
            evidence_repository_revision_id=(
                compatibility.repository_revision_id
            ),
            evidence_repository_audit_id=(
                compatibility.repository_audit_id
            ),
            source_id=compatibility.source_id,
            source_revision_number=compatibility.revision_number,
            traceable_evidence_id=compatibility.traceable_evidence_id,
            accepted_evidence_id=compatibility.accepted_evidence_id,
            acceptance_record_ids=compatibility.acceptance_record_ids,
            construction_rule_id=compatibility.construction_rule_id,
            construction_rule_version=(
                compatibility.construction_rule_version
            ),
            governed_knowledge_construction_policy_id=(
                governed.construction_policy_id
            ),
            governed_knowledge_construction_policy_version=(
                governed.construction_policy_version
            ),
            lineage_policy_id=KNOWLEDGE_REPOSITORY_POLICY_ID,
            lineage_policy_version=(
                KNOWLEDGE_REPOSITORY_POLICY_VERSION
            ),
        )
        lineage = KnowledgeRepositoryLineageRecord(
            contract_version=(
                KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION
            ),
            lineage_record_id=(
                calculate_knowledge_repository_lineage_record_id(
                    **lineage_kwargs
                )
            ),
            **lineage_kwargs,
        )
        lifecycle = request.lifecycle_interpretation_result
        governed_digest = (
            calculate_governed_knowledge_repository_payload_digest(
                governed
            )
        )
        lifecycle_digest = (
            calculate_governed_knowledge_repository_payload_digest(
                lifecycle
            )
        )
        lifecycle_id = (
            lifecycle.governed_knowledge_lifecycle_assertion_interpretation_result_id
        )
        revision_kwargs = dict(
            governed_knowledge_id=governed.governed_knowledge_id,
            revision_number=1,
            previous_revision_id=None,
            governed_knowledge_payload_digest=governed_digest,
            lineage_record_id=lineage.lineage_record_id,
            lifecycle_interpretation_result_id=lifecycle_id,
            lifecycle_interpretation_result_contract_version=(
                lifecycle.contract_version
            ),
            lifecycle_interpretation_result_payload_digest=(
                lifecycle_digest
            ),
            transition_record_id=None,
            actor_id=request.actor_id,
            recorded_at_utc=request.recorded_at_utc,
        )
        revision_id = calculate_knowledge_repository_revision_id(
            **revision_kwargs
        )
        audit_kwargs = dict(
            action=_INITIAL_ACTION,
            revision_id=revision_id,
            governed_knowledge_id=governed.governed_knowledge_id,
            revision_number=1,
            lineage_record_id=lineage.lineage_record_id,
            transition_record_id=None,
            actor_id=request.actor_id,
            recorded_at_utc=request.recorded_at_utc,
        )
        audit_id = calculate_knowledge_repository_audit_id(
            **audit_kwargs
        )
        revision = KnowledgeRepositoryRevision(
            contract_version=(
                KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION
            ),
            revision_id=revision_id,
            audit_id=audit_id,
            **revision_kwargs,
        )
        audit = KnowledgeRepositoryAuditRecord(
            contract_version=(
                KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION
            ),
            audit_id=audit_id,
            **audit_kwargs,
        )
        return None, {
            "governed": governed,
            "lineage": lineage,
            "lifecycle": lifecycle,
            "revision": revision,
            "audit": audit,
        }

    def persist_initial(
        self,
        request: KnowledgeRepositoryInitialWriteRequest,
    ) -> KnowledgeRepositoryWriteResult:
        issue_code, derived = self._validate_initial(request)
        if issue_code is not None or derived is None:
            return self._rejected(
                issue_code or "internal_contract_violation"
            )
        try:
            connection = self._connect()
            try:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute(
                    "SELECT revision_id "
                    "FROM knowledge_repository_revisions "
                    "WHERE governed_knowledge_id = ? "
                    "AND revision_number = 1",
                    (
                        derived[
                            "governed"
                        ].governed_knowledge_id,
                    ),
                ).fetchone()
                if row is not None:
                    existing = self._lookup_by_revision_id(
                        connection,
                        row["revision_id"],
                    )
                    connection.rollback()
                    if (
                        existing.status == "found"
                        and existing.revision == derived["revision"]
                        and existing.lineage_record
                        == derived["lineage"]
                        and existing.audit_record == derived["audit"]
                        and existing.governed_knowledge
                        == derived["governed"]
                        and existing.lifecycle_interpretation_result
                        == derived["lifecycle"]
                    ):
                        return self._write_from_lookup(
                            "unchanged_exact_replay",
                            False,
                            existing,
                        )
                    return self._rejected(
                        "initial_revision_already_bound_to_different_content"
                    )

                governed_payload = (
                    serialize_governed_knowledge_repository_payload(
                        derived["governed"]
                    )
                )
                lifecycle_payload = (
                    serialize_governed_knowledge_repository_payload(
                        derived["lifecycle"]
                    )
                )
                connection.execute(
                    "INSERT INTO governed_knowledge_payloads "
                    "VALUES (?, ?, ?)",
                    (
                        derived[
                            "governed"
                        ].governed_knowledge_id,
                        derived[
                            "revision"
                        ].governed_knowledge_payload_digest,
                        governed_payload,
                    ),
                )
                connection.execute(
                    "INSERT INTO "
                    "knowledge_repository_lineage_records "
                    "VALUES (?, ?, ?)",
                    (
                        derived["lineage"].lineage_record_id,
                        derived[
                            "governed"
                        ].governed_knowledge_id,
                        serialize_governed_knowledge_repository_payload(
                            derived["lineage"]
                        ),
                    ),
                )
                connection.execute(
                    "INSERT INTO "
                    "knowledge_repository_lifecycle_results "
                    "VALUES (?, ?, ?, ?)",
                    (
                        derived[
                            "revision"
                        ].lifecycle_interpretation_result_id,
                        derived[
                            "governed"
                        ].governed_knowledge_id,
                        derived[
                            "revision"
                        ].lifecycle_interpretation_result_payload_digest,
                        lifecycle_payload,
                    ),
                )
                self._insert_revision_and_audit(
                    connection,
                    derived["revision"],
                    derived["audit"],
                )
                connection.commit()
                return KnowledgeRepositoryWriteResult(
                    contract_version=(
                        KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
                    ),
                    status="persisted_initial",
                    mutation_performed=True,
                    revision=derived["revision"],
                    lineage_record=derived["lineage"],
                    transition_record=None,
                    audit_record=derived["audit"],
                    governed_knowledge=derived["governed"],
                    lifecycle_interpretation_result=derived[
                        "lifecycle"
                    ],
                    issue=None,
                )
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()
        except Exception as error:
            return self._rejected(
                self._map_database_issue(error)
            )

    @staticmethod
    def _insert_revision_and_audit(
        connection: sqlite3.Connection,
        revision: KnowledgeRepositoryRevision,
        audit: KnowledgeRepositoryAuditRecord,
    ) -> None:
        connection.execute(
            "INSERT INTO knowledge_repository_revisions "
            "(revision_id, governed_knowledge_id, "
            "revision_number, previous_revision_id, "
            "lineage_record_id, "
            "lifecycle_interpretation_result_id, "
            "transition_record_id, audit_id, payload) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                revision.revision_id,
                revision.governed_knowledge_id,
                revision.revision_number,
                revision.previous_revision_id,
                revision.lineage_record_id,
                revision.lifecycle_interpretation_result_id,
                revision.transition_record_id,
                revision.audit_id,
                serialize_governed_knowledge_repository_payload(
                    revision
                ),
            ),
        )
        connection.execute(
            "INSERT INTO knowledge_repository_audit_records "
            "VALUES (?, ?, ?, ?)",
            (
                audit.audit_id,
                audit.revision_id,
                audit.governed_knowledge_id,
                serialize_governed_knowledge_repository_payload(
                    audit
                ),
            ),
        )

    @staticmethod
    def _write_from_lookup(
        status: str,
        mutation_performed: bool,
        lookup: KnowledgeRepositoryLookupResult,
    ) -> KnowledgeRepositoryWriteResult:
        return KnowledgeRepositoryWriteResult(
            contract_version=(
                KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
            ),
            status=status,
            mutation_performed=mutation_performed,
            revision=lookup.revision,
            lineage_record=lookup.lineage_record,
            transition_record=lookup.transition_record,
            audit_record=lookup.audit_record,
            governed_knowledge=lookup.governed_knowledge,
            lifecycle_interpretation_result=(
                lookup.lifecycle_interpretation_result
            ),
            issue=None,
        )

    def append_lifecycle_transition(
        self,
        request: KnowledgeRepositoryLifecycleTransitionRequest,
    ) -> KnowledgeRepositoryWriteResult:
        if not isinstance(
            request,
            KnowledgeRepositoryLifecycleTransitionRequest,
        ):
            return self._rejected("invalid_request")
        if (
            request.contract_version
            != KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION
        ):
            return self._rejected(
                "unsupported_contract_version"
            )
        if (
            request.transition_policy_id
            != KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID
            or request.transition_policy_version
            != KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION
        ):
            return self._rejected(
                "unsupported_transition_policy"
            )
        try:
            request.__post_init__()
        except Exception:
            return self._rejected("invalid_request")

        lifecycle_issue = self._verify_lifecycle_result(
            request.next_lifecycle_interpretation_result,
            request.governed_knowledge_id,
        )
        if lifecycle_issue is not None:
            return self._rejected(lifecycle_issue)

        try:
            connection = self._connect()
            try:
                connection.execute("BEGIN IMMEDIATE")
                prior = self._lookup_by_revision_id(
                    connection,
                    request.expected_prior_revision_id,
                )
                if prior.status != "found":
                    connection.rollback()
                    return self._rejected(
                        "expected_prior_revision_not_found"
                    )
                if (
                    prior.revision.governed_knowledge_id
                    != request.governed_knowledge_id
                ):
                    connection.rollback()
                    return self._rejected(
                        "expected_prior_revision_identity_mismatch"
                    )
                if (
                    prior.revision.revision_number
                    != request.expected_prior_revision_number
                ):
                    connection.rollback()
                    return self._rejected(
                        "expected_prior_revision_number_mismatch"
                    )

                next_result = (
                    request.next_lifecycle_interpretation_result
                )
                next_id = (
                    next_result.governed_knowledge_lifecycle_assertion_interpretation_result_id
                )
                next_digest = (
                    calculate_governed_knowledge_repository_payload_digest(
                        next_result
                    )
                )
                if (
                    next_id
                    == prior.revision.lifecycle_interpretation_result_id
                    or next_digest
                    == prior.revision.lifecycle_interpretation_result_payload_digest
                ):
                    connection.rollback()
                    return self._rejected(
                        "lifecycle_transition_no_change"
                    )

                transition_kwargs = dict(
                    governed_knowledge_id=(
                        request.governed_knowledge_id
                    ),
                    from_revision_id=prior.revision.revision_id,
                    from_revision_number=(
                        prior.revision.revision_number
                    ),
                    previous_lifecycle_interpretation_result_id=(
                        prior.revision.lifecycle_interpretation_result_id
                    ),
                    next_lifecycle_interpretation_result_id=(
                        next_id
                    ),
                    transition_reason_codes=(
                        request.transition_reason_codes
                    ),
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                    transition_policy_id=(
                        request.transition_policy_id
                    ),
                    transition_policy_version=(
                        request.transition_policy_version
                    ),
                )
                transition = (
                    KnowledgeRepositoryLifecycleTransitionRecord(
                        contract_version=(
                            KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_RECORD_CONTRACT_VERSION
                        ),
                        transition_record_id=(
                            calculate_knowledge_repository_lifecycle_transition_record_id(
                                **transition_kwargs
                            )
                        ),
                        **transition_kwargs,
                    )
                )
                revision_kwargs = dict(
                    governed_knowledge_id=(
                        request.governed_knowledge_id
                    ),
                    revision_number=(
                        prior.revision.revision_number + 1
                    ),
                    previous_revision_id=(
                        prior.revision.revision_id
                    ),
                    governed_knowledge_payload_digest=(
                        prior.revision.governed_knowledge_payload_digest
                    ),
                    lineage_record_id=(
                        prior.revision.lineage_record_id
                    ),
                    lifecycle_interpretation_result_id=next_id,
                    lifecycle_interpretation_result_contract_version=(
                        next_result.contract_version
                    ),
                    lifecycle_interpretation_result_payload_digest=(
                        next_digest
                    ),
                    transition_record_id=(
                        transition.transition_record_id
                    ),
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                )
                revision_id = (
                    calculate_knowledge_repository_revision_id(
                        **revision_kwargs
                    )
                )
                audit_kwargs = dict(
                    action=_TRANSITION_ACTION,
                    revision_id=revision_id,
                    governed_knowledge_id=(
                        request.governed_knowledge_id
                    ),
                    revision_number=(
                        revision_kwargs["revision_number"]
                    ),
                    lineage_record_id=(
                        prior.revision.lineage_record_id
                    ),
                    transition_record_id=(
                        transition.transition_record_id
                    ),
                    actor_id=request.actor_id,
                    recorded_at_utc=request.recorded_at_utc,
                )
                audit_id = calculate_knowledge_repository_audit_id(
                    **audit_kwargs
                )
                revision = KnowledgeRepositoryRevision(
                    contract_version=(
                        KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION
                    ),
                    revision_id=revision_id,
                    audit_id=audit_id,
                    **revision_kwargs,
                )
                audit = KnowledgeRepositoryAuditRecord(
                    contract_version=(
                        KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION
                    ),
                    audit_id=audit_id,
                    **audit_kwargs,
                )

                child_row = connection.execute(
                    "SELECT revision_id "
                    "FROM knowledge_repository_revisions "
                    "WHERE previous_revision_id = ?",
                    (prior.revision.revision_id,),
                ).fetchone()
                if child_row is not None:
                    child = self._lookup_by_revision_id(
                        connection,
                        child_row["revision_id"],
                    )
                    connection.rollback()
                    if (
                        child.status == "found"
                        and child.revision == revision
                        and child.transition_record == transition
                        and child.audit_record == audit
                        and child.lifecycle_interpretation_result
                        == next_result
                    ):
                        return self._write_from_lookup(
                            "unchanged_exact_replay",
                            False,
                            child,
                        )
                    return self._rejected(
                        "lifecycle_transition_conflict"
                    )

                latest = connection.execute(
                    "SELECT MAX(revision_number) AS latest "
                    "FROM knowledge_repository_revisions "
                    "WHERE governed_knowledge_id = ?",
                    (request.governed_knowledge_id,),
                ).fetchone()["latest"]
                if latest != prior.revision.revision_number:
                    connection.rollback()
                    return self._rejected(
                        "stale_expected_prior_revision"
                    )

                existing_result = connection.execute(
                    "SELECT payload_digest, payload "
                    "FROM knowledge_repository_lifecycle_results "
                    "WHERE lifecycle_interpretation_result_id = ?",
                    (next_id,),
                ).fetchone()
                next_payload = (
                    serialize_governed_knowledge_repository_payload(
                        next_result
                    )
                )
                if existing_result is None:
                    connection.execute(
                        "INSERT INTO "
                        "knowledge_repository_lifecycle_results "
                        "VALUES (?, ?, ?, ?)",
                        (
                            next_id,
                            request.governed_knowledge_id,
                            next_digest,
                            next_payload,
                        ),
                    )
                elif (
                    existing_result["payload_digest"]
                    != next_digest
                    or bytes(existing_result["payload"])
                    != next_payload
                ):
                    connection.rollback()
                    return self._rejected(
                        "lifecycle_interpretation_identity_mismatch"
                    )

                connection.execute(
                    "INSERT INTO "
                    "knowledge_repository_transition_records "
                    "VALUES (?, ?, ?, ?)",
                    (
                        transition.transition_record_id,
                        transition.governed_knowledge_id,
                        transition.from_revision_id,
                        serialize_governed_knowledge_repository_payload(
                            transition
                        ),
                    ),
                )
                self._insert_revision_and_audit(
                    connection,
                    revision,
                    audit,
                )
                connection.commit()
                return KnowledgeRepositoryWriteResult(
                    contract_version=(
                        KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION
                    ),
                    status="appended_lifecycle_transition",
                    mutation_performed=True,
                    revision=revision,
                    lineage_record=prior.lineage_record,
                    transition_record=transition,
                    audit_record=audit,
                    governed_knowledge=prior.governed_knowledge,
                    lifecycle_interpretation_result=next_result,
                    issue=None,
                )
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()
        except Exception as error:
            return self._rejected(
                self._map_database_issue(error)
            )

    def _lookup_by_revision_id(
        self,
        connection: sqlite3.Connection,
        revision_id: str,
    ) -> KnowledgeRepositoryLookupResult:
        row = connection.execute(
            "SELECT payload "
            "FROM knowledge_repository_revisions "
            "WHERE revision_id = ?",
            (revision_id,),
        ).fetchone()
        if row is None:
            return KnowledgeRepositoryLookupResult(
                contract_version=(
                    KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
                ),
                status="not_found",
                revision=None,
                lineage_record=None,
                transition_record=None,
                audit_record=None,
                governed_knowledge=None,
                lifecycle_interpretation_result=None,
                issue=None,
            )

        revision = (
            deserialize_governed_knowledge_repository_payload(
                bytes(row["payload"])
            )
        )
        governed_row = connection.execute(
            "SELECT payload "
            "FROM governed_knowledge_payloads "
            "WHERE governed_knowledge_id = ?",
            (revision.governed_knowledge_id,),
        ).fetchone()
        lineage_row = connection.execute(
            "SELECT payload "
            "FROM knowledge_repository_lineage_records "
            "WHERE lineage_record_id = ?",
            (revision.lineage_record_id,),
        ).fetchone()
        lifecycle_row = connection.execute(
            "SELECT payload "
            "FROM knowledge_repository_lifecycle_results "
            "WHERE lifecycle_interpretation_result_id = ?",
            (revision.lifecycle_interpretation_result_id,),
        ).fetchone()
        audit_row = connection.execute(
            "SELECT payload "
            "FROM knowledge_repository_audit_records "
            "WHERE audit_id = ?",
            (revision.audit_id,),
        ).fetchone()
        if any(
            item is None
            for item in (
                governed_row,
                lineage_row,
                lifecycle_row,
                audit_row,
            )
        ):
            raise sqlite3.DatabaseError(
                "repository content is malformed"
            )

        transition = None
        if revision.transition_record_id is not None:
            transition_row = connection.execute(
                "SELECT payload "
                "FROM knowledge_repository_transition_records "
                "WHERE transition_record_id = ?",
                (revision.transition_record_id,),
            ).fetchone()
            if transition_row is None:
                raise sqlite3.DatabaseError(
                    "repository content is malformed"
                )
            transition = (
                deserialize_governed_knowledge_repository_payload(
                    bytes(transition_row["payload"])
                )
            )

        return KnowledgeRepositoryLookupResult(
            contract_version=(
                KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
            ),
            status="found",
            revision=revision,
            lineage_record=(
                deserialize_governed_knowledge_repository_payload(
                    bytes(lineage_row["payload"])
                )
            ),
            transition_record=transition,
            audit_record=(
                deserialize_governed_knowledge_repository_payload(
                    bytes(audit_row["payload"])
                )
            ),
            governed_knowledge=(
                deserialize_governed_knowledge_repository_payload(
                    bytes(governed_row["payload"])
                )
            ),
            lifecycle_interpretation_result=(
                deserialize_governed_knowledge_repository_payload(
                    bytes(lifecycle_row["payload"])
                )
            ),
            issue=None,
        )

    def get_by_revision_id(
        self,
        revision_id: str,
    ) -> KnowledgeRepositoryLookupResult:
        if not isinstance(revision_id, str) or not revision_id:
            return self._lookup_rejected("invalid_request")
        try:
            connection = self._connect()
            try:
                return self._lookup_by_revision_id(
                    connection,
                    revision_id,
                )
            finally:
                connection.close()
        except Exception as error:
            return self._lookup_rejected(
                self._map_database_issue(error)
            )

    def get_by_governed_knowledge_revision(
        self,
        governed_knowledge_id: str,
        revision_number: int,
    ) -> KnowledgeRepositoryLookupResult:
        if (
            not isinstance(governed_knowledge_id, str)
            or not governed_knowledge_id
            or not isinstance(revision_number, int)
            or revision_number < 1
        ):
            return self._lookup_rejected("invalid_request")
        try:
            connection = self._connect()
            try:
                row = connection.execute(
                    "SELECT revision_id "
                    "FROM knowledge_repository_revisions "
                    "WHERE governed_knowledge_id = ? "
                    "AND revision_number = ?",
                    (
                        governed_knowledge_id,
                        revision_number,
                    ),
                ).fetchone()
                if row is None:
                    return KnowledgeRepositoryLookupResult(
                        contract_version=(
                            KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
                        ),
                        status="not_found",
                        revision=None,
                        lineage_record=None,
                        transition_record=None,
                        audit_record=None,
                        governed_knowledge=None,
                        lifecycle_interpretation_result=None,
                        issue=None,
                    )
                return self._lookup_by_revision_id(
                    connection,
                    row["revision_id"],
                )
            finally:
                connection.close()
        except Exception as error:
            return self._lookup_rejected(
                self._map_database_issue(error)
            )

    def list_governed_knowledge_history(
        self,
        governed_knowledge_id: str,
    ) -> KnowledgeRepositoryHistoryResult:
        if (
            not isinstance(governed_knowledge_id, str)
            or not governed_knowledge_id
        ):
            return self._history_rejected(
                (
                    governed_knowledge_id
                    if isinstance(governed_knowledge_id, str)
                    else ""
                ),
                "invalid_request",
            )
        try:
            connection = self._connect()
            try:
                rows = connection.execute(
                    "SELECT revision_id "
                    "FROM knowledge_repository_revisions "
                    "WHERE governed_knowledge_id = ? "
                    "ORDER BY revision_number ASC",
                    (governed_knowledge_id,),
                ).fetchall()
                if not rows:
                    return KnowledgeRepositoryHistoryResult(
                        contract_version=(
                            KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
                        ),
                        status="not_found",
                        governed_knowledge_id=(
                            governed_knowledge_id
                        ),
                        governed_knowledge=None,
                        lineage_record=None,
                        revisions=(),
                        lifecycle_interpretation_results=(),
                        transition_records=(),
                        audit_records=(),
                        issue=None,
                    )
                lookups = tuple(
                    self._lookup_by_revision_id(
                        connection,
                        row["revision_id"],
                    )
                    for row in rows
                )
                if any(
                    item.status != "found"
                    for item in lookups
                ):
                    raise sqlite3.DatabaseError(
                        "repository content is malformed"
                    )
                return KnowledgeRepositoryHistoryResult(
                    contract_version=(
                        KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION
                    ),
                    status="found",
                    governed_knowledge_id=(
                        governed_knowledge_id
                    ),
                    governed_knowledge=(
                        lookups[0].governed_knowledge
                    ),
                    lineage_record=(
                        lookups[0].lineage_record
                    ),
                    revisions=tuple(
                        item.revision
                        for item in lookups
                    ),
                    lifecycle_interpretation_results=tuple(
                        item.lifecycle_interpretation_result
                        for item in lookups
                    ),
                    transition_records=tuple(
                        item.transition_record
                        for item in lookups
                        if item.transition_record is not None
                    ),
                    audit_records=tuple(
                        item.audit_record
                        for item in lookups
                    ),
                    issue=None,
                )
            finally:
                connection.close()
        except Exception as error:
            return self._history_rejected(
                governed_knowledge_id,
                self._map_database_issue(error),
            )
