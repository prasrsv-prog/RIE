# PR-052B - Evidence Repository and Idempotency Runtime Contract Review

## 1. Review identity

Gate: `Gate 7 - Evidence Repository and Idempotency`

Phase: `Phase 52 - Evidence Repository and Idempotency`

Phase checkpoint: `8a8d6f96416e1c7de728d9c5f7026bc7617f11cf`

Selected minimum closure boundary: `single_source_scoped_append_only_evidence_collection_repository_with_atomic_idempotent_duplicate_detection_revision_lineage_and_audit_boundary`

Selected runtime contract: `new_isolated_gate_6_evidence_collection_sqlite_repository_runtime_contract_with_canonical_payload_atomic_source_revision_idempotency_and_append_only_audit`

## 2. Preflight interpretation

The accepted technical preflight parsed all 21 repository-name candidates without AST errors.

Eight direct Evidence repository candidates implement persistence for legacy `AcceptedEvidence` and `AcceptanceRecord` values. They do not consume Gate 6 `EvidenceCollection`, do not provide source-scoped collection revisions, and do not satisfy the selected Gate 7 boundary.

Therefore, no existing repository candidate, schema, serializer, protocol, adapter, status taxonomy, or migration path is promoted automatically.

The legacy repository remains untouched and is excluded from the authoritative Gate 7 runtime.

## 3. Authoritative upstream value

The only authoritative write input is a valid immutable Gate 6 `EvidenceCollection` with contract version `evidence_collection_contract_v1`.

The repository must revalidate the exact Gate 6 collection contract and rederive `collection_id` using the existing Gate 6 collection identity canonicalization before persistence.

The repository must not reconstruct Evidence, rerun extraction, reevaluate eligibility, normalize text, reorder Evidence items, deduplicate warnings, or import legacy AcceptedEvidence runtime types.

The exact collection payload field order is:

- `contract_version`
- `collection_id`
- `artifact_contract_version`
- `artifact_id`
- `upstream_contract_version`
- `job_id`
- `source_id`
- `source_path`
- `source_checksum`
- `eligibility_snapshot`
- `evidence_items`

## 4. Contract and canonicalization versions

Selected contract versions:

- `evidence_repository_write_request_contract_v1`
- `evidence_repository_write_result_contract_v1`
- `evidence_repository_revision_contract_v1`
- `evidence_repository_audit_record_contract_v1`
- `evidence_repository_lookup_result_contract_v1`
- `evidence_repository_history_result_contract_v1`
- `evidence_repository_issue_contract_v1`

Selected canonicalization versions:

- `evidence_collection_repository_payload_json_v1`
- `evidence_repository_revision_identity_json_v1`
- `evidence_repository_audit_identity_json_v1`

Revision identifier prefix: `evr1_`

Audit identifier prefix: `eva1_`

## 5. Canonical collection payload

The complete 11-field EvidenceCollection is serialized as deterministic UTF-8 JSON without BOM, insignificant whitespace, or trailing bytes.

Object keys use the reviewed field order. Tuple and Evidence item order are preserved exactly. Duplicate warning values are preserved. String content is encoded exactly and is not Unicode-normalized, trimmed, corrected, or rewritten.

The collection payload digest is lower-case SHA-256 over those canonical bytes.

Deserialization must recreate an equal Gate 6 EvidenceCollection and must fail closed on duplicate keys, unknown or missing fields, invalid UTF-8, unsupported versions, noncanonical bytes, digest mismatch, Evidence identity mismatch, or collection identity mismatch.

## 6. Write request
The immutable write request field order is:

- `contract_version`
- `collection`
- `expected_collection_payload_digest`
- `actor_id`
- `recorded_at_utc`

The caller supplies the exact canonical collection payload digest, a non-empty actor identifier, and a timezone-aware UTC operation timestamp.

The canonical operation timestamp format is `YYYY-MM-DDTHH:MM:SS.ffffffZ`.

The repository does not read the current clock and does not create random identifiers.

## 7. Revision contract
The immutable revision field order is:

- `contract_version`
- `revision_id`
- `source_id`
- `revision_number`
- `collection_id`
- `collection_payload_digest`
- `previous_revision_id`
- `actor_id`
- `recorded_at_utc`
- `audit_id`

Revision identity canonicalization uses:

- `contract_version`
- `source_id`
- `revision_number`
- `collection_id`
- `collection_payload_digest`
- `previous_revision_id`

Revision identifiers are lower-case SHA-256 identifiers prefixed with `evr1_`.

A source stream is keyed by exact `source_id`. A previously unseen source begins at revision `1`. A new collection identity for the same source appends exactly the next positive integer revision.

The first revision has no previous revision identifier. Every later revision points to the immediately preceding immutable revision.

Source path and checksum are preserved inside the collection payload and may change across revisions for the same stable source identifier.

## 8. Audit contract
The immutable persisted audit record field order is:

- `contract_version`
- `audit_id`
- `action`
- `revision_id`
- `source_id`
- `revision_number`
- `collection_id`
- `actor_id`
- `recorded_at_utc`

Audit identity canonicalization uses:

- `contract_version`
- `action`
- `revision_id`
- `source_id`
- `revision_number`
- `collection_id`
- `actor_id`
- `recorded_at_utc`

Audit identifiers are lower-case SHA-256 identifiers prefixed with `eva1_`.

The only persisted audit action in the minimum closure boundary is `persisted_revision`.

Each accepted new revision and its audit record are committed atomically.

An exact replay returns the existing revision, collection, and original persisted audit record with status `unchanged_exact_replay`; it creates no additional audit mutation.

A rejected request returns an immutable fail-closed operation result and issue as audit evidence, but creates no durable repository mutation.

## 9. Write result and statuses
The immutable write result field order is:

- `contract_version`
- `status`
- `mutation_performed`
- `revision`
- `audit_record`
- `collection`
- `issue`

Exact write statuses:

- `persisted`
- `unchanged_exact_replay`
- `rejected`

For `persisted`, mutation is true and revision, audit record, and exact round-tripped collection are present.

For `unchanged_exact_replay`, mutation is false and the existing revision, original audit record, and exact stored collection are present.

For `rejected`, mutation is false; revision, audit record, and collection are absent; one reviewed issue is present.

## 10. Idempotency and collision rules

The repository first resolves exact `collection_id` under the write transaction.

If collection identity, canonical payload digest, and canonical payload bytes all match an existing record, the operation is an exact replay and performs no mutation.

If an existing collection identifier is paired with different canonical bytes or digest, the operation is rejected as `collection_identity_collision` and performs no mutation.

If the collection identifier is new, the repository appends exactly one source revision and one audit record.

## 11. Lookup and history contracts
The immutable lookup result field order is:

- `contract_version`
- `status`
- `revision`
- `audit_record`
- `collection`
- `issue`

The immutable history result field order is:

- `contract_version`
- `status`
- `source_id`
- `revisions`
- `audit_records`
- `issue`

Exact lookup and history statuses:

- `found`
- `not_found`
- `rejected`

The repository protocol exposes exactly:

- `persist`
- `get_by_collection_id`
- `get_by_source_revision`
- `list_source_history`
- `list_source_audit`

Collection lookup returns the exact persisted collection, revision, and audit record.

Source-revision lookup uses an exact source identifier and positive revision number.

Source history is ordered by ascending revision number. Source audit history is ordered by the same revision order. No sorting by caller-controlled actor or timestamp is allowed.

## 12. Issue contract
The immutable issue field order is:

- `code`
- `message`

Reviewed issue codes in exact order:

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

Each issue code has one fixed non-secret message. Error messages must not echo collection content, source text, canonical payload bytes, or database contents.

`not_found` is a valid lookup status and is not an issue.

## 13. Durable backend and schema boundary
The minimum durable closure backend is SQLite with schema identifier `rcis-gate7-evidence-repository-sqlite` and schema version `1`.

The schema contains exactly these Gate 7 tables:

- `evidence_collection_records`
- `evidence_revision_records`
- `evidence_audit_records`

`evidence_collection_records` stores collection identity, source identity, contract version, canonical payload digest, and canonical payload bytes.

`evidence_revision_records` stores the source-scoped revision lineage and has unique constraints for revision identity, `(source_id, revision_number)`, and collection identity.

`evidence_audit_records` stores exactly one persisted audit record for each accepted revision.

SQLite foreign keys are enabled. Schema identity and version are validated on every open. Unexpected objects, missing objects, incompatible columns, or unsupported schema versions fail closed.

No migration, import, wrapping, table reuse, or data copy from the legacy AcceptedEvidence repository is selected.

An in-memory adapter may be implemented only as a contract-conformance and concurrency test adapter. It does not satisfy durable Gate 7 closure evidence.

## 14. Atomicity and concurrency

SQLite writes use one explicit `BEGIN IMMEDIATE` transaction.

Collection insertion, duplicate identity indexing, source revision allocation, revision insertion, and audit insertion commit or roll back together.

Revision number allocation occurs while the write transaction owns the SQLite write lock.

The repository performs no automatic retry. A busy or locked database returns the controlled `repository_busy` issue and leaves no partial mutation.

Concurrent exact writes commit once and all later writers observe exact replay. Concurrent distinct collections for the same source serialize into consecutive revisions.

## 15. Explicit exclusions

This review does not authorize implementation or select implementation paths.

Deletion, update-in-place, revision rewriting, revision compaction, supersession semantics, semantic duplicate detection, Evidence merging, cross-source aggregation, retry orchestration, cleanup, CLI, API, Gate 8 Knowledge construction, Prompt Candidate behavior, and current-state Knowledge semantics remain excluded.

## 16. Decision

Decision:

`EVIDENCE_REPOSITORY_AND_IDEMPOTENCY_RUNTIME_CONTRACT_SELECTED`

Status after this review:

- Gate 6 closed: `True`;

- Gate 7 active closure target: `True`;

- Gate 7 minimum closure boundary selected: `True`;

- Gate 7 runtime contract selected: `True`;

- Gate 7 implementation boundary selected: `False`;

- Gate 7 implementation authorized: `False`;

- Gate 7 implementation started: `False`;

- Gate 7 closed: `False`;

- Gate 8 invoked: `False`.

The next safe review is PR-052C - Evidence Repository and Idempotency Implementation Boundary Review.
