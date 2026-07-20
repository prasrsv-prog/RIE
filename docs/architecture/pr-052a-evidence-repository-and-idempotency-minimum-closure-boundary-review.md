# PR-052A - Evidence Repository and Idempotency Minimum Closure Boundary Review

## 1. Review identity

Gate: `Gate 7 - Evidence Repository and Idempotency`

Phase: `Phase 52 - Evidence Repository and Idempotency`

Phase base checkpoint: `ffd3aa17a851763b1c2e27b1e432f5ca451c5639`

Selected minimum closure boundary: `single_source_scoped_append_only_evidence_collection_repository_with_atomic_idempotent_duplicate_detection_revision_lineage_and_audit_boundary`

## 2. Upstream authority

Gate 7 consumes only a valid immutable Gate 6 `EvidenceCollection` and its contained `TraceableEvidence` values.

Gate 7 must not reconstruct Evidence from source files, rerun extraction, reevaluate source eligibility, normalize content, or substitute legacy AcceptedEvidence as its authoritative input.

## 3. Minimum repository scope

The minimum closure boundary is one append-only repository operation over one valid EvidenceCollection, organized as a source-scoped immutable revision stream.

A previously unseen source starts one revision stream at revision `1`. A new valid collection for the same source appends exactly one next immutable revision when its collection identity is new.

The repository must preserve the exact Gate 6 collection, source identity, source checksum, artifact identity, extraction job identity, Evidence item order, Evidence identities, warnings, and provenance.

## 4. Minimum idempotency and conflict behavior

An exact replay of the same collection identity and canonical collection content is an idempotent duplicate: it returns the existing repository result and creates no new revision or duplicate audit mutation.

Reuse of an existing collection identity with different canonical content is a fail-closed identity conflict and creates no repository mutation.

A new collection identity for the same source appends one next revision atomically with its audit record.

## 5. Minimum read and history behavior

The repository must support exact retrieval by collection identity and exact source-scoped revision lookup.

The repository must expose an ordered immutable revision history for one source without collapsing, rewriting, or deleting prior revisions.

The repository must expose append-only audit evidence for persisted, duplicate, and rejected conflict outcomes. Exact audit fields and clock policy are deferred to PR-052B.

## 6. Atomicity

For a new accepted collection, collection storage, source revision indexing, duplicate identity indexing, and the corresponding audit record must succeed or fail as one transaction.

Partial repository state is not allowed.

## 7. Existing repository foundations

The repository scan found `21` tracked runtime or test paths whose names suggest repository, idempotency, duplicate, revision, audit, persistence, storage, or SQLite behavior.

These paths are compatibility candidates only. None is automatically promoted as the authoritative Gate 7 runtime, schema, repository contract, or migration path.

PR-052B must decide exact contracts and whether any existing component is reused, wrapped, migrated, or explicitly excluded.

## 8. Explicit exclusions

The minimum boundary does not authorize implementation, a storage backend, database schema, migration, serializer publication, current-clock access, concurrency policy, retry policy, cleanup policy, CLI, API, source ingestion, Evidence materialization, Knowledge construction, Knowledge repository behavior, Prompt Candidate behavior, or Gate 8.

Deletion, in-place Evidence mutation, revision rewriting, revision compaction, supersession semantics, and cross-source aggregation are excluded.

## 9. Deferred PR-052B decisions

PR-052B must define exact contract versions, repository command and result fields, persisted record fields, revision identity, audit identity, duplicate and conflict statuses, fixed issue codes and messages, canonicalization rules, transaction behavior, backend boundary, clock policy, concurrency behavior, and retrieval interfaces.

## 10. Decision

Decision:

`EVIDENCE_REPOSITORY_AND_IDEMPOTENCY_MINIMUM_CLOSURE_BOUNDARY_SELECTED`

Status after this review:

- Gate 6 closed: `True`;

- Gate 7 active closure target: `True`;

- Gate 7 minimum closure boundary selected: `True`;

- Gate 7 runtime contract selected: `False`;

- Gate 7 implementation boundary selected: `False`;

- Gate 7 implementation authorized: `False`;

- Gate 7 implementation started: `False`;

- Gate 7 closed: `False`;

- Gate 8 invoked: `False`.

The next safe review is PR-052B - Evidence Repository and Idempotency Runtime Contract Review.
