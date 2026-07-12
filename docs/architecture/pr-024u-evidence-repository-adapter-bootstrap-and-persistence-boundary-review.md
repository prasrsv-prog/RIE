# PR-024U — Evidence Repository Adapter Bootstrap and Persistence Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `e161cb90a013e1d08b48be2a8fc227ce5d4586d2` |
| Gate type | Documentation-only |
| Final decision | **IN-MEMORY EVIDENCE REPOSITORY REFERENCE ADAPTER APPROVED AS THE NEXT CONTROLLED SLICE; DURABLE PERSISTENCE DEFERRED** |
| Exact next gate | **PR-024V - In-Memory Evidence Repository Reference Adapter Implementation** |

## 2. Purpose

PR-024U reviews the first infrastructure implementation that may satisfy the committed `EvidenceRepository` protocol.

The selected next slice is a process-local in-memory reference adapter. It validates repository state transitions without introducing durable persistence, serializer formats, migrations, database technology, filesystem storage, configuration, or production wiring.

## 3. Verified checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `e161cb90a013e1d08b48be2a8fc227ce5d4586d2`;
- divergence: `0 0`;
- Phase 24 is exactly fourteen commits ahead of main;
- exact fourteen-commit chain;
- latest parent: `c04ce14d37dd65587456219102da436fc9acd08b`;
- latest subject: `feat: add evidence repository interface contract`;
- latest exact three-file scope;
- exact twenty-nine-file Phase 24 scope;
- zero merge commits;
- clean working tree.

## 4. Completed prerequisites

The following are committed and frozen for this slice:

1. immutable `AcceptedEvidence`;
2. deterministic factual identity and fourteen-field identity projection;
3. immutable standalone `AcceptanceRecord`;
4. deterministic acceptance identity and twelve-field identity projection;
5. accepted-Evidence materializer;
6. immutable repository request/result contracts;
7. exact five-method `EvidenceRepository` protocol;
8. replay, collision, append-only, atomicity, and no-retry boundaries.

## 5. Selected adapter

The next implementation class is:

`	ext
InMemoryEvidenceRepository
`

Exact intended module:

`	ext
src/rie/infrastructure/in_memory_evidence_repository.py
`

Exact focused test module:

`	ext
tests/infrastructure/test_in_memory_evidence_repository.py
`

This class is an infrastructure adapter and must satisfy the committed protocol structurally.

## 6. Reference-adapter status

The adapter is:

- process-local;
- volatile;
- deterministic;
- append-only for its lifetime;
- intended for contract validation;
- not a durable repository;
- not a production persistence claim;
- not a fallback after persistent storage failure;
- not an application cache;
- not a serializer.

Process exit discards all state.

## 7. Internal state boundary

The implementation must keep one private repository-state object containing:

1. factual Evidence entries keyed by `evidence_id`;
2. acceptance entries keyed by `acceptance_record_id`;
3. deterministic acceptance-ID membership per `evidence_id`.

Each factual entry stores:

- exact immutable `AcceptedEvidence`;
- canonical factual digest.

Each acceptance entry stores:

- exact immutable `AcceptanceRecord`;
- canonical acceptance digest.

No raw canonical bytes are stored because persistence serialization remains deferred.

No public state property, mutable mapping, seed mapping, export method, or mutation hook is authorized.

## 8. Synchronization and atomicity

The adapter may use one private standard-library re-entrant lock.

Every protocol method executes under that lock.

`write` must:

1. acquire the lock;
2. classify current state inside the lock;
3. create a complete replacement private state;
4. assign the replacement state once;
5. return the exact controlled result.

`classify_write` is advisory and performs no mutation.

A prior classification result is never accepted as an input to `write`.

The lock supplies process-local atomicity only. It is not a database transaction and creates no cross-process guarantee.

## 9. Factual equivalence boundary

Factual equivalence uses the existing fourteen-field projection produced by:

`python
identity_input_from_accepted_evidence(...)
`

The adapter may compare that projection for equality.

It must not:

- calculate a new digest;
- generate an `evidence_id`;
- select a different identity policy;
- serialize identity bytes;
- normalize additional fields.

`materialization_record` and top-level diagnostics are excluded from factual identity, so a later acceptance event may carry a different materialization record while retaining the same factual identity.

## 10. Acceptance equivalence boundary

Acceptance equivalence uses the existing twelve-field projection produced by:

`python
acceptance_identity_input_from_record(...)
`

The adapter may compare that projection for equality.

It must not calculate an acceptance digest or generate an `acceptance_record_id`.

Top-level acceptance diagnostics are excluded from acceptance identity.

## 11. Classification order

The adapter must classify in this fail-closed order:

1. invalid exact request type — reject before state access;
2. existing factual key with a different stored digest — `identity_collision`;
3. existing factual key with a different fourteen-field projection — `identity_collision`;
4. existing acceptance key with a different stored digest — `acceptance_collision`;
5. existing acceptance key with a different twelve-field projection — `acceptance_collision`;
6. absent factual and acceptance keys — `new_evidence`;
7. matching factual key and absent acceptance key — `same_fact_new_acceptance`;
8. matching factual and acceptance keys with exact stored object equality — `exact_replay`;
9. matching identity projections and digests with differences limited to diagnostics or governance-excluded aggregate values — `governance_replay`;
10. any unresolved combination — `rejected`.

The semantic candidate classifications remain reserved and are never inferred by this adapter:

`	ext
semantic_duplicate_candidate
conflicting_evidence_candidate
superseding_evidence_candidate
`

## 12. Write behavior

### New Evidence

`new_evidence` writes one factual entry and its first acceptance entry in one replacement state.

Result:

`	ext
inserted_new_evidence
mutation_performed=True
`

### Same fact, new acceptance

`same_fact_new_acceptance` preserves the stored factual entry and appends one acceptance entry.

Result:

`	ext
appended_acceptance_record
mutation_performed=True
`

### Exact replay

No state replacement.

Result:

`	ext
unchanged_exact_replay
mutation_performed=False
`

### Governance replay

No state replacement.

Result:

`	ext
unchanged_governance_replay
mutation_performed=False
`

### Collisions and rejection

No state replacement.

Results use the exact committed collision or invalid-request status and set:

`	ext
mutation_performed=False
`

## 13. Retrieval behavior

`get_evidence`:

- validates one explicit `ev1_` ID;
- returns `not_found` when absent;
- returns the exact stored immutable Evidence and digest when found;
- returns acceptance IDs sorted lexicographically;
- performs no access-time mutation.

`get_acceptance_record`:

- validates one explicit `ar1_` ID;
- returns the exact immutable record and digest when found;
- returns `not_found` when absent.

`list_acceptance_records`:

- validates one explicit factual ID;
- returns records sorted by `acceptance_record_id`;
- returns `not_found` with an empty tuple when none exist.

## 14. Controlled reason codes

The reference adapter may use only explicit infrastructure-neutral strings, including:

`	ext
evidence_not_found
acceptance_record_not_found
new_evidence
exact_replay_detected
governance_replay_detected
same_fact_new_acceptance
identity_collision_detected
acceptance_collision_detected
request_invalid
`

Raw exceptions, stack traces, object addresses, paths, credentials, or lock details must not cross the interface.

## 15. Error boundary

Invalid ID syntax may raise `ValueError` before state access because the committed result contracts require valid explicit IDs.

Unexpected internal errors must not be converted into replay or success.

No failure injection hook, callback, logger, retry policy, or alternate storage is introduced in PR-024V.

`failed_repository_operation` remains part of the protocol for later durable adapters.

## 16. No-retry boundary

Every method performs one attempt.

Forbidden:

- retry loops;
- recursive retry;
- reconnect behavior;
- fallback state;
- background queueing;
- delayed write;
- sleep/backoff;
- retry counters;
- converting failure into replay.

## 17. No-durable-persistence boundary

PR-024V must not use or import:

- `pathlib`;
- `os`;
- `sqlite3`;
- ORM libraries;
- JSON serializers;
- pickle or shelve;
- files or directories;
- environment variables;
- network clients;
- configuration readers;
- migration tools;
- transaction frameworks.

No repository artifact or storage file may be created.

## 18. Append-only lifecycle

The adapter exposes only the five protocol methods.

Forbidden public methods remain:

`	ext
update
delete
replace
upsert
merge
compact
bulk_write
clear
reset
seed
load
dump
export
`

Tests may create a new adapter instance for isolation. They may not clear or mutate an existing instance through a non-protocol method.

## 19. Future two-file implementation boundary

PR-024V may create exactly:

1. `src/rie/infrastructure/in_memory_evidence_repository.py`;
2. `tests/infrastructure/test_in_memory_evidence_repository.py`.

No existing file may be modified.

No central export, composition wiring, CLI, API, or configuration change is authorized.

## 20. Required focused tests

The focused test module must cover:

- structural protocol compatibility;
- initial empty lookups;
- new Evidence insertion;
- factual and acceptance retrieval;
- deterministic acceptance ordering;
- exact replay;
- governance replay limited to diagnostics;
- same fact with a new acceptance;
- factual digest collision;
- factual projection collision;
- acceptance digest collision;
- acceptance projection collision;
- no partial mutation after rejected writes;
- `classify_write` no-mutation behavior;
- `write` reclassification under the same lock;
- one committed mutation under concurrent identical writes;
- collision rejection under concurrent conflicting writes;
- exact status/classification/mutation mapping;
- absence of semantic candidate inference;
- absence of forbidden public methods;
- absence of filesystem, database, serializer, network, clock, UUID, random, retry, Knowledge, and Prompt behavior.

Only `tests/infrastructure/test_in_memory_evidence_repository.py` may run, exactly once, with zero automatic retry.

## 21. Durable persistence deferral

A durable adapter remains deferred until a later review defines:

- storage technology;
- canonical persistence serialization;
- schema/version headers;
- corruption detection;
- fail-closed deserialization;
- transaction mechanics;
- unique constraints;
- cross-process concurrency;
- crash recovery;
- migration;
- backup and recovery boundary;
- credential and path security.

The in-memory reference adapter does not satisfy those capabilities and must not be presented as doing so.

## 22. Full regression decision

Full regression remains deferred.

PR-024V may run only its exact focused adapter test module.

## 23. Options reviewed

### Option A — Implement a filesystem adapter now

**Rejected.** Canonical persistence serialization, corruption handling, and path security are not yet implementation-reviewed.

### Option B — Implement a SQLite adapter now

**Rejected.** Schema, transaction, migration, locking, and recovery choices are not yet implementation-reviewed.

### Option C — Skip adapter behavior and run full regression

**Rejected.** The interface has no implementing object yet.

### Option D — Implement a process-local in-memory reference adapter

**Selected.** It validates deterministic repository state transitions while preserving durable-persistence separation.

### Option E — Reopen Knowledge governance now

**Rejected.** Repository adapter behavior and later persistence/compatibility gates remain unfinished.

## 24. Final decision

# IN-MEMORY EVIDENCE REPOSITORY REFERENCE ADAPTER APPROVED AS THE NEXT CONTROLLED SLICE; DURABLE PERSISTENCE DEFERRED

Authorization is limited to the exact two-file in-memory reference-adapter implementation.

## 25. Exact next gate

**PR-024V - In-Memory Evidence Repository Reference Adapter Implementation**

The next gate may create only the two approved files and run the one focused test module exactly once.

## 26. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-024S/PR-024T commit/push checkpoint | PASSED |
| Fourteen-commit Phase 24 chain | PASSED |
| Twenty-nine-file Phase 24 scope | PASSED |
| Repository interface integrity | PASSED |
| Factual identity projection | PASSED |
| Acceptance identity projection | PASSED |
| PR-023E atomicity boundary | PASSED |
| PR-023E append-only boundary | PASSED |
| Existing adapter absence | PASSED |
| In-memory reference-adapter readiness | APPROVED |
| Durable persistence | DEFERRED |
| Serializer/migration | DEFERRED |
| Knowledge/Prompt coupling | ABSENT |
| Earlier phases/environment preservation | PASSED |

## 27. Action truth table

| Action | Performed |
|---|---|
| Commit-output verification | True |
| Read-only checkpoint verification | True |
| Contract integrity review | True |
| Infrastructure inventory | True |
| Existing adapter search | True |
| Static adapter-boundary review | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Adapter implemented | False |
| Durable persistence implemented | False |
| Serializer or migration implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 28. Gate conclusion

PR-024U concludes **IN-MEMORY EVIDENCE REPOSITORY REFERENCE ADAPTER APPROVED AS THE NEXT CONTROLLED SLICE; DURABLE PERSISTENCE DEFERRED**.

Only `PR-024V - In-Memory Evidence Repository Reference Adapter Implementation` is authorized after PR-024U commit/push verification.
