# PR-054C - Knowledge Repository and Lifecycle Implementation Boundary Review

## 1. Review identity

This document selects the exact implementation boundary for Gate 9 - Knowledge Repository and Lifecycle.

Repository checkpoint: `a2f63fe62201fd90d7ad933b459f84b3ca9eea73`.

Phase branch: `phase-054-knowledge-repository-and-lifecycle`.

Selected minimum closure boundary: `persisted_existing_governed_knowledge_exact_revision_repository_with_explicit_idempotent_lifecycle_transition_records_and_verified_gate_8_candidate_lineage`.

Selected runtime contract: `caller_supplied_governed_knowledge_verified_gate_8_lineage_append_only_exact_revision_repository_and_explicit_structural_lifecycle_transition_runtime_contract`.

This review authorizes a bounded implementation in the next PR. It creates no production code, test code, database, migration, commit, or runtime mutation itself.

## 2. Selected implementation boundary

Selected implementation boundary: `ten_file_isolated_sqlite_governed_knowledge_repository_contract_canonicalization_protocol_backend_public_api_and_boundary_test_implementation`.

Package: `rie.knowledge_repository`.

Repository protocol: `GovernedKnowledgeRepository`.

Concrete backend: `SqliteGovernedKnowledgeRepository`.

SQLite schema ID: `rcis-gate9-governed-knowledge-repository-sqlite`.

SQLite schema version: `1`.

The backend is selected only for this bounded implementation. It remains isolated from the Gate 7 evidence repository and does not share tables, schema metadata, transactions, mutable pointers, or repository identities.

## 3. Exact file scope

Production file count: `5`.

- `src/rie/knowledge_repository/__init__.py`
- `src/rie/knowledge_repository/knowledge_repository_contract.py`
- `src/rie/knowledge_repository/knowledge_repository_canonicalization.py`
- `src/rie/knowledge_repository/knowledge_repository_protocol.py`
- `src/rie/knowledge_repository/sqlite_governed_knowledge_repository.py`

Test file count: `5`.

- `tests/test_knowledge_repository_contract.py`
- `tests/test_knowledge_repository_canonicalization.py`
- `tests/test_knowledge_repository_protocol.py`
- `tests/test_sqlite_governed_knowledge_repository.py`
- `tests/test_knowledge_repository_public_api.py`

Total implementation path count: `10`.

All ten paths are new. No existing repository path may be modified.

## 4. Production responsibilities

### `knowledge_repository_contract.py`

- owns the ten frozen dataclasses selected by PR-054B;
- owns contract versions, policies, statuses, issue codes, issue messages, ID prefixes, schema constants, and strict `__post_init__` validation;
- does not access SQLite, files, clocks, environment variables, Git, or application entrypoints.

### `knowledge_repository_canonicalization.py`

- serializes and deserializes complete governed-knowledge and lifecycle-result payloads;
- calculates canonical payload digests and lineage, transition, revision, and audit IDs;
- uses compact UTF-8 JSON, sorted keys, explicit UTC timestamps, deterministic unique-string ordering, SHA-256, no BOM, and no trailing newline;
- preserves diagnostics and nested frozen dataclass payloads;
- independently verifies existing domain identities during deserialization.

### `knowledge_repository_protocol.py`

- owns one runtime-checkable `GovernedKnowledgeRepository` protocol;
- exposes exactly the five PR-054B methods and no latest/current/delete/update methods.

### `sqlite_governed_knowledge_repository.py`

- owns schema initialization and schema compatibility validation;
- implements initial persistence, lifecycle append, exact replay, exact revision lookup, and ordered history;
- uses explicit all-or-nothing transactions and maps SQLite failures to the frozen issue codes;
- validates all caller-supplied frozen objects and identities before mutation;
- never calls construction, governance, acceptance, promotion, assertion, or interpretation entrypoints.

### `__init__.py`

- exports exactly the selected public API;
- contains no behavior, persistence, backend initialization, or side effects.

## 5. SQLite schema boundary

Table count: `7`.

- `knowledge_repository_metadata`
- `governed_knowledge_payloads`
- `knowledge_repository_lineage_records`
- `knowledge_repository_lifecycle_results`
- `knowledge_repository_transition_records`
- `knowledge_repository_revisions`
- `knowledge_repository_audit_records`

Schema constraints must enforce unique governed-knowledge identity, unique revision identity, unique `(governed_knowledge_id, revision_number)`, unique transition identity, unique audit identity, and at most one direct child revision per prior revision.

The metadata table stores only the Gate 9 schema ID and schema version. No migration path is selected. An incompatible non-empty schema is rejected as `unsupported_schema`.

## 6. Exact protocol surface

- `persist_initial(self, request: KnowledgeRepositoryInitialWriteRequest) -> KnowledgeRepositoryWriteResult`
- `append_lifecycle_transition(self, request: KnowledgeRepositoryLifecycleTransitionRequest) -> KnowledgeRepositoryWriteResult`
- `get_by_revision_id(self, revision_id: str) -> KnowledgeRepositoryLookupResult`
- `get_by_governed_knowledge_revision(self, governed_knowledge_id: str, revision_number: int) -> KnowledgeRepositoryLookupResult`
- `list_governed_knowledge_history(self, governed_knowledge_id: str) -> KnowledgeRepositoryHistoryResult`

The concrete SQLite backend must structurally satisfy this protocol.

## 7. Exact package public API

Public class count: `12`.

- class `KnowledgeRepositoryInitialWriteRequest`
- class `KnowledgeRepositoryLifecycleTransitionRequest`
- class `KnowledgeRepositoryLineageRecord`
- class `KnowledgeRepositoryRevision`
- class `KnowledgeRepositoryLifecycleTransitionRecord`
- class `KnowledgeRepositoryAuditRecord`
- class `KnowledgeRepositoryWriteResult`
- class `KnowledgeRepositoryLookupResult`
- class `KnowledgeRepositoryHistoryResult`
- class `KnowledgeRepositoryIssue`
- class `GovernedKnowledgeRepository`
- class `SqliteGovernedKnowledgeRepository`

Public function count: `7`.

- function `serialize_governed_knowledge_repository_payload`
- function `deserialize_governed_knowledge_repository_payload`
- function `calculate_governed_knowledge_repository_payload_digest`
- function `calculate_knowledge_repository_lineage_record_id`
- function `calculate_knowledge_repository_lifecycle_transition_record_id`
- function `calculate_knowledge_repository_revision_id`
- function `calculate_knowledge_repository_audit_id`

Public constant count: `29`.

- constant `KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_RECORD_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_ISSUE_CONTRACT_VERSION`
- constant `KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LINEAGE_IDENTITY_CANONICALIZATION_VERSION`
- constant `KNOWLEDGE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_IDENTITY_CANONICALIZATION_VERSION`
- constant `KNOWLEDGE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION`
- constant `KNOWLEDGE_REPOSITORY_POLICY_ID`
- constant `KNOWLEDGE_REPOSITORY_POLICY_VERSION`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION`
- constant `KNOWLEDGE_REPOSITORY_DIGEST_ALGORITHM`
- constant `KNOWLEDGE_REPOSITORY_LINEAGE_ID_PREFIX`
- constant `KNOWLEDGE_REPOSITORY_REVISION_ID_PREFIX`
- constant `KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_ID_PREFIX`
- constant `KNOWLEDGE_REPOSITORY_AUDIT_ID_PREFIX`
- constant `KNOWLEDGE_REPOSITORY_WRITE_STATUSES`
- constant `KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES`
- constant `KNOWLEDGE_REPOSITORY_ISSUE_CODES`
- constant `SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID`
- constant `SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION`

Total exact public API count: `48`.

No other public symbol may be exported from the package.

## 8. Exact constructor boundary

`SqliteGovernedKnowledgeRepository(database_path: str | Path, *, timeout_seconds: float = 5.0)`

The constructor stores configuration only. Schema initialization occurs deterministically before the first repository operation or through an internal idempotent initializer. Construction performs no governed-knowledge mutation.

## 9. Transaction boundary

- initial persistence: at most one payload row, one lineage row, one lifecycle-result row, one revision row, and one audit row in one transaction;
- lifecycle append: at most one lifecycle-result row, one transition row, one revision row, and one audit row in one transaction;
- exact replay: zero mutation;
- rejection: zero mutation;
- no cross-subject transaction;
- no hidden retry that changes identity inputs;
- no destructive SQL statement.

## 10. Dependency boundary

Allowed production dependencies are Python standard library modules plus exact existing RCIS/RIE domain and contract types required to validate `GovernedKnowledge`, Gate 8 lineage, governed-knowledge construction result, and structural lifecycle interpretation result.

The implementation may import existing identity and canonicalization helpers for verification. It may not invoke application workflow entrypoints.

Forbidden production import or call names include:

- `construct_knowledge_from_persisted_evidence`
- `construct_knowledge_candidate`
- `construct_governed_knowledge`
- `decide_governed_knowledge_acceptance`
- `interpret_governed_knowledge_lifecycle_assertion_premise_structurally`
- `govern_knowledge_candidate`
- `decide_knowledge_authority`
- `assess_knowledge_candidate_conflict`
- `decide_knowledge_promotion`
- `record_knowledge_promotion_execution`

No new third-party dependency and no `pyproject.toml` modification are permitted.

## 11. Test boundary

The five selected test modules must cover:

1. contract shape, frozen dataclass validation, versions, statuses, issue precedence, and immutability.
2. canonical payload round trip, fixed digests, fixed IDs, deterministic collection ordering, and non-cyclic identity derivation.
3. exact protocol method names and signatures plus runtime structural conformance.
4. SQLite schema initialization, initial persist, initial exact replay, lifecycle append, lifecycle exact replay, stale prior rejection, competing child rejection, exact lookup, ordered history, corruption, unsupported schema, busy, and unavailable handling.
5. exact package public API and forbidden import/call boundaries.

Execution boundary:

- one targeted pytest process covering exactly the five new test modules;
- one full regression pytest process;
- zero retries;
- controlled temporary database paths outside the repository;
- deterministic environment restoration and cleanup;
- no Git mutation by the test runner.

## 12. Fixed canonicalization fixtures

Implementation acceptance must freeze at least:

- one complete initial repository fixture with exact canonical byte length, SHA-256 payload digest, lineage ID, revision ID, and audit ID;
- one lifecycle transition fixture with exact canonical byte length, SHA-256 lifecycle payload digest, transition ID, child revision ID, and audit ID;
- one exact replay fixture proving byte-identical result reconstruction and zero mutation;
- one conflicting child fixture proving deterministic rejection and zero mutation.

Fixture values are selected during implementation and then reported as immutable fingerprints before commit.

## 13. Explicit exclusions

- modifying any existing source, test, documentation, configuration, or packaging file;
- sharing Gate 7 evidence repository tables or schema metadata;
- reusing Gate 7 revision, audit, request, result, or protocol classes as Gate 9 storage objects;
- automatic construction, governance, acceptance, promotion, assertion, interpretation, or source-authority inheritance;
- implicit latest/current lookup or mutable current pointer;
- overwrite, delete, compaction, history rewriting, or mutable revisions;
- repository search, ranking, graph traversal, aggregation, or bulk orchestration;
- CLI, HTTP API, worker, scheduler, packaging, or release behavior;
- Gate 10 Prompt Candidate behavior;
- Gate 11 behavior.

## 14. Implementation authorization decision

Gate 9 minimum closure boundary selected: `True`.

Gate 9 minimum closure boundary committed: `True`.

Gate 9 runtime contract selected: `True`.

Gate 9 runtime contract committed: `True`.

Gate 9 implementation boundary selected: `True`.

Gate 9 implementation boundary committed: `False`.

Gate 9 implementation authorized: `False`.

Gate 9 implementation started: `False`.

Gate 9 closed: `False`.

Gate 10 invoked: `False`.

The implementation becomes authorized only after this document is committed, pushed, and independently verified.

## 15. Next safe operation

`PR-054C_POST_COMMIT - Gate 9 Implementation Boundary Review Post-Commit Verification`

After that verification is accepted, the next operation is PR-054D - Knowledge Repository and Lifecycle Contract Implementation.
