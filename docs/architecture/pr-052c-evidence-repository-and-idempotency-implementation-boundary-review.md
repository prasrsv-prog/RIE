# PR-052C - Evidence Repository and Idempotency Implementation Boundary Review

## 1. Review identity

Gate: `Gate 7 - Evidence Repository and Idempotency`

Phase: `Phase 52 - Evidence Repository and Idempotency`

Phase checkpoint: `4a476eb3879110b02f96dacc6477e3d441f0ea2f`

Selected minimum closure boundary: `single_source_scoped_append_only_evidence_collection_repository_with_atomic_idempotent_duplicate_detection_revision_lineage_and_audit_boundary`

Selected runtime contract: `new_isolated_gate_6_evidence_collection_sqlite_repository_runtime_contract_with_canonical_payload_atomic_source_revision_idempotency_and_append_only_audit`

Selected implementation boundary: `new_isolated_gate_6_evidence_collection_repository_namespace_with_frozen_contract_canonicalization_protocol_sqlite_adapter_and_boundary_tests`

## 2. Implementation direction

Gate 7 implementation is authorized only as a new isolated `rie.evidence_repository` namespace.

The implementation consumes immutable Gate 6 EvidenceCollection values through the Gate 6 contract and canonicalization modules.

It must not import, wrap, modify, migrate, call, or re-export the legacy AcceptedEvidence repository interface, serialization, in-memory adapter, SQLite adapter, schema, or tests.

## 3. Exact authorized production paths

- `src/rie/evidence_repository/__init__.py`
- `src/rie/evidence_repository/evidence_repository_contract.py`
- `src/rie/evidence_repository/evidence_repository_canonicalization.py`
- `src/rie/evidence_repository/evidence_repository_protocol.py`
- `src/rie/evidence_repository/sqlite_evidence_collection_repository.py`

## 4. Exact authorized test paths

- `tests/evidence_repository/test_evidence_repository_contract.py`
- `tests/evidence_repository/test_evidence_repository_canonicalization.py`
- `tests/evidence_repository/test_sqlite_evidence_collection_repository.py`
- `tests/evidence_repository/test_evidence_repository_boundary.py`

No existing tracked path may be modified by PR-052D.

No additional production, test, documentation, configuration, migration, fixture, generated database, or packaging path is authorized.

## 5. Module responsibilities

`evidence_repository_contract.py` owns exact constants, immutable request/result/revision/audit/issue contracts, statuses, issue codes, and fixed messages.

`evidence_repository_canonicalization.py` owns deterministic collection payload bytes, strict round-trip deserialization, payload digest, revision identity, and audit identity.

`evidence_repository_protocol.py` owns the five-method structural protocol only.

`sqlite_evidence_collection_repository.py` owns the exact three-table SQLite adapter, schema validation, atomic persistence, idempotency, revision allocation, lookup, history, audit history, and controlled fail-closed issues.

`__init__.py` re-exports only the reviewed public surface.

## 6. Exact public surface
The namespace public surface contains exactly 32 symbols:

- `EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION`
- `EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION`
- `EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION`
- `EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION`
- `EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION`
- `EVIDENCE_REPOSITORY_REVISION_ID_PREFIX`
- `EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX`
- `SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID`
- `SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION`
- `EVIDENCE_REPOSITORY_WRITE_STATUSES`
- `EVIDENCE_REPOSITORY_LOOKUP_STATUSES`
- `EVIDENCE_REPOSITORY_ISSUE_CODES`
- `EVIDENCE_REPOSITORY_ISSUE_MESSAGES`
- `EvidenceRepositoryIssue`
- `EvidenceRepositoryWriteRequest`
- `EvidenceRepositoryRevision`
- `EvidenceRepositoryAuditRecord`
- `EvidenceRepositoryWriteResult`
- `EvidenceRepositoryLookupResult`
- `EvidenceRepositoryHistoryResult`
- `serialize_evidence_collection_repository_payload`
- `deserialize_evidence_collection_repository_payload`
- `calculate_evidence_collection_repository_payload_digest`
- `calculate_evidence_repository_revision_id`
- `calculate_evidence_repository_audit_id`
- `EvidenceCollectionRepository`
- `SqliteEvidenceCollectionRepository`

Every other module-level name must remain private or excluded from `__all__`.

## 7. Protocol surface
The repository protocol exposes exactly five methods:

- `persist`
- `get_by_collection_id`
- `get_by_source_revision`
- `list_source_history`
- `list_source_audit`

No delete, update, compact, supersede, migrate, retry, cleanup, knowledge, prompt, CLI, or generic execute method is allowed.

## 8. SQLite implementation boundary
The durable adapter creates and validates exactly three Gate 7 tables:

- `evidence_collection_records`
- `evidence_revision_records`
- `evidence_audit_records`

The schema identifier remains `rcis-gate7-evidence-repository-sqlite` and the schema version remains `1`.

SQLite foreign keys must be enabled. Schema identity, version, exact table set, exact columns, constraints, indexes, and foreign keys must be validated before operations.

Write transactions use explicit `BEGIN IMMEDIATE`. Collection storage, source revision allocation, revision insertion, and audit insertion must commit or roll back together.

The implementation performs no automatic retry and must return `repository_busy` without partial mutation when the database is locked.

Production code must not create temporary directories, choose a repository path, or delete a database. The caller supplies the SQLite file path.

## 9. Canonicalization boundary

Canonicalization imports only the Gate 6 EvidenceCollection contract and Gate 6 collection identity logic plus Python standard library modules.

Collection text, tuple order, Evidence item order, warning order, and duplicate warnings must be preserved exactly. Unicode normalization, trimming, correction, paraphrase, sorting, and deduplication are forbidden.

The strict deserializer must reject duplicate keys, missing or unknown fields, invalid UTF-8, unsupported versions, noncanonical bytes, payload digest mismatch, Evidence identity mismatch, and collection identity mismatch.

## 10. Identity and time boundary

Revision and audit identifiers are deterministic lower-case SHA-256 identifiers with prefixes `evr1_` and `eva1_`.

The write request supplies a timezone-aware UTC timestamp and actor identifier.

Production code must not import or call current clock, random, UUID, secrets, or environment-derived identity sources.

## 11. Exact status and issue boundary
Write statuses:

- `persisted`
- `unchanged_exact_replay`
- `rejected`

Lookup and history statuses:

- `found`
- `not_found`
- `rejected`

Issue codes in exact order:

- `invalid_request`
- `unsupported_contract_version`
- `invalid_collection`
- `collection_id_mismatch`
- `collection_payload_digest_mismatch`
- `collection_identity_collision`
- `revision_id_mismatch`
- `audit_id_mismatch`
- `unsupported_schema`
- `repository_busy`
- `repository_corrupt`
- `repository_unavailable`

Fixed issue messages must not echo source text, Evidence content, payload bytes, SQL values, database paths, or secrets.

## 12. Test authorization
PR-052D must cover these 52 behavioral areas:

- `exact_constants_and_public_symbols`
- `frozen_contracts_without_defaults`
- `exact_contract_field_orders`
- `exact_contract_input_types`
- `exact_write_statuses`
- `exact_lookup_statuses`
- `exact_issue_codes_and_messages`
- `caller_supplied_utc_timestamp_validation`
- `exact_gate6_collection_type`
- `payload_digest_shape_validation`
- `revision_contract_invariants`
- `audit_contract_invariants`
- `write_result_shape_invariants`
- `lookup_result_shape_invariants`
- `history_result_shape_invariants`
- `fixed_non_secret_errors`
- `deterministic_collection_payload_bytes`
- `canonical_payload_no_bom_or_trailing_bytes`
- `exact_text_order_and_duplicate_preservation`
- `collection_payload_round_trip_equality`
- `duplicate_json_key_rejection`
- `missing_or_extra_field_rejection`
- `invalid_utf8_rejection`
- `noncanonical_payload_rejection`
- `payload_digest_mismatch_rejection`
- `collection_identity_mismatch_rejection`
- `deterministic_revision_identity`
- `deterministic_audit_identity`
- `exact_repository_public_methods`
- `exact_three_table_schema`
- `schema_identity_and_version_validation`
- `sqlite_foreign_keys_enabled`
- `new_source_revision_one`
- `same_source_next_revision`
- `exact_replay_no_revision_or_audit_mutation`
- `collection_identity_collision_rejection`
- `lookup_by_collection_identity`
- `lookup_by_source_revision`
- `ordered_source_revision_history`
- `ordered_source_audit_history`
- `durable_reopen_round_trip`
- `concurrent_exact_writes_commit_once`
- `concurrent_distinct_writes_consecutive_revisions`
- `begin_immediate_atomic_rollback`
- `busy_repository_no_retry_or_partial_mutation`
- `corrupt_or_incompatible_schema_fail_closed`
- `no_legacy_repository_imports`
- `no_current_clock_or_random_identity`
- `no_gate8_or_knowledge_behavior`
- `no_update_delete_or_revision_rewrite_sql`
- `no_legacy_schema_migration`
- `exact_authorized_path_scope`

Targeted tests must execute only the four authorized Gate 7 test modules.

A full regression run is required after the targeted suite passes.

SQLite tests must use an external controlled temporary root outside the repository and must restore the environment and remove created databases afterward.

## 13. Explicit exclusions

No legacy AcceptedEvidence repository code or test may be edited.

No migration, data copy, compatibility adapter, dual write, fallback read, generic repository abstraction, ORM, dependency injection framework, asynchronous API, network service, CLI, packaging change, or Gate 8 behavior is authorized.

No deletion, update-in-place, source revision rewrite, revision compaction, supersession, semantic duplicate assessment, Evidence merging, or cross-source aggregation is authorized.

## 14. Decision

Decision:

`EVIDENCE_REPOSITORY_AND_IDEMPOTENCY_IMPLEMENTATION_BOUNDARY_SELECTED`

Status after this review:

- Gate 6 closed: `True`;

- Gate 7 active closure target: `True`;

- Gate 7 minimum closure boundary selected: `True`;

- Gate 7 runtime contract selected: `True`;

- Gate 7 implementation boundary selected: `True`;

- Gate 7 implementation authorized: `True`;

- Gate 7 implementation started: `False`;

- Gate 7 implementation completed: `False`;

- Gate 7 closed: `False`;

- Gate 8 invoked: `False`.

The next safe operation is PR-052D - Evidence Repository and Idempotency Contract Implementation.
