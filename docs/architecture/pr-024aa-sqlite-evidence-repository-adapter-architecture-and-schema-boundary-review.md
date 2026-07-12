# PR-024AA — SQLite Evidence Repository Adapter Architecture and Schema Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed checkpoint | `5f48632d5f59bc43a66f1e2ce4876908351b9a9a` |
| Gate type | Documentation-only architecture review |
| Selected technology | Python standard-library `sqlite3` |
| Selected adapter | `SqliteEvidenceRepository` |
| Final decision | **SQLITE EVIDENCE REPOSITORY ADAPTER ARCHITECTURE AND SCHEMA V1 APPROVED FOR THE NEXT CONTROLLED IMPLEMENTATION SLICE** |

## 2. Scope

This review defines the first durable Evidence Repository adapter and its exact SQLite schema boundary.

It does not:

- create a database;
- create or alter SQLite tables;
- implement the adapter;
- implement migration behavior;
- modify serialization, domain, interface, or in-memory adapter contracts;
- run tests;
- stage, commit, or push;
- introduce Knowledge or Prompt behavior.

## 3. Prerequisite checkpoint

The following committed checkpoint is authoritative:

```text
HEAD: 5f48632d5f59bc43a66f1e2ce4876908351b9a9a
Subject: feat: add evidence repository persistence serialization contract
Phase 24 versus main: 0 18
Phase 24 commit count: 18
Phase 24 changed-file count: 37
```

The committed serialization contract is the only persistence payload codec approved for this adapter.

## 4. Exact next implementation scope

The next controlled implementation may create exactly:

```text
src/rie/infrastructure/sqlite_evidence_repository.py
tests/infrastructure/test_sqlite_evidence_repository.py
```

No existing file may be modified.

No re-export, dependency, configuration, migration, CLI, application wiring, or Knowledge/Prompt file is authorized.

## 5. Adapter public surface

The implementation shall expose exactly one public adapter class:

```python
class SqliteEvidenceRepository:
    def __init__(self, database_path: str) -> None: ...
    def get_evidence(self, evidence_id: str) -> EvidenceLookupResult: ...
    def get_acceptance_record(
        self,
        acceptance_record_id: str,
    ) -> AcceptanceRecordLookupResult: ...
    def list_acceptance_records(
        self,
        evidence_id: str,
    ) -> AcceptanceRecordListResult: ...
    def classify_write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteClassificationResult: ...
    def write(
        self,
        request: EvidenceWriteRequest,
    ) -> EvidenceWriteResult: ...
```

The class must satisfy the existing `EvidenceRepository` protocol structurally.

Forbidden public methods include:

- `update`;
- `delete`;
- `replace`;
- `upsert`;
- `merge`;
- `compact`;
- `bulk_write`;
- `clear`;
- `reset`;
- `seed`;
- `load`;
- `dump`;
- `export`;
- `close`.

Connections are operation-scoped, so no public lifecycle method is required.

## 6. Constructor and path boundary

`database_path` must be an exact non-empty string.

The constructor shall reject:

- empty or whitespace-only paths;
- `:memory:`;
- SQLite URI forms;
- paths whose parent directory does not exist;
- paths that resolve to a directory.

The constructor may create the SQLite database file when the target file is absent.

It must not create parent directories.

It must not delete, rename, replace, copy, or move an existing database file.

## 7. Connection policy

Use Python standard-library `sqlite3` only.

Each repository operation opens and closes its own connection.

Every connection must:

```text
uri = False
foreign_keys = ON
busy_timeout = 0
row_factory = sqlite3.Row
```

No connection pool is allowed.

No retry, sleep, backoff, or hidden second attempt is allowed.

The adapter must not force WAL mode or change global journal mode.

## 8. Schema identity

The first durable schema is:

```text
schema_id = rcis-evidence-repository-sqlite
schema_version = 1
repository_contract_version = 1.0.0
persistence_contract_version = 1.0.0
```

Schema version `1` is the only supported version in this slice.

Automatic migration is forbidden.

An existing database with missing, additional, or incompatible schema metadata must fail closed during construction.

## 9. Exact schema

The adapter shall create exactly two tables and one index.

### 9.1 `accepted_evidence_records`

```sql
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
);
```

### 9.2 `acceptance_records`

```sql
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
);
```

### 9.3 Acceptance lookup index

```sql
CREATE INDEX acceptance_records_by_evidence
ON acceptance_records (
    evidence_id,
    acceptance_record_id
);
```

No other table, index, trigger, or view is authorized.

## 10. Schema version mechanism

Use SQLite `PRAGMA user_version`.

The exact value is:

```text
PRAGMA user_version = 1
```

Initialization rules:

1. a new empty database may receive the exact schema and `user_version = 1` in one transaction;
2. an existing exact schema with `user_version = 1` is accepted;
3. `user_version = 0` with any user object present is rejected;
4. any version other than `1` is rejected;
5. missing, extra, or altered user tables, indexes, columns, constraints, or foreign keys are rejected;
6. no migration is attempted.

## 11. Schema bootstrap transaction

Schema bootstrap shall use one explicit transaction.

Required order:

1. open connection;
2. enable foreign keys;
3. inspect `user_version` and `sqlite_master`;
4. for a new empty database, execute `BEGIN IMMEDIATE`;
5. create the exact tables and index;
6. set `PRAGMA user_version = 1`;
7. validate the created schema;
8. commit;
9. rollback on any failure.

No partial schema is acceptable.

## 12. Serialization boundary

The adapter must use only:

```text
serialize_accepted_evidence
deserialize_accepted_evidence
serialize_acceptance_record
deserialize_acceptance_record
```

from:

```text
src/rie/infrastructure/evidence_repository_serialization.py
```

The adapter must not define a second payload format.

It must not use:

- pickle;
- shelve;
- ORM models;
- ad-hoc JSON encoding;
- Python object repr;
- alternate identity calculation;
- raw domain-object persistence.

## 13. Stored row boundary

Each persisted row stores only the corresponding serialized-record fields.

No timestamp, mutable status, soft-delete marker, cache field, denormalized Knowledge field, or Prompt field is allowed.

The adapter stores canonical payload bytes exactly as returned by the serialization contract.

It must not edit, reformat, recompress, or re-encode those bytes.

## 14. Read behavior

### 14.1 Evidence lookup

`get_evidence`:

1. validates the requested `ev1_` identifier before opening the database;
2. reads at most one factual row;
3. deserializes and verifies the stored record;
4. queries acceptance IDs ordered lexicographically;
5. returns the existing `EvidenceLookupResult`.

### 14.2 Acceptance-record lookup

`get_acceptance_record`:

1. validates the requested `ar1_` identifier;
2. reads at most one acceptance row;
3. deserializes and verifies the stored record;
4. returns the existing `AcceptanceRecordLookupResult`.

### 14.3 Acceptance-record listing

`list_acceptance_records`:

1. validates the requested `ev1_` identifier;
2. selects rows using:

```sql
ORDER BY acceptance_record_id ASC
```

3. deserializes every row;
4. returns the existing `AcceptanceRecordListResult`.

No pagination is introduced.

## 15. Corruption boundary

A row is invalid when any of the following fails:

- identifier syntax;
- identifier-to-canonical-digest equality;
- payload digest verification;
- persistence contract version;
- payload schema ID;
- identity policy ID/version;
- canonical payload decoding;
- aggregate reconstruction;
- recalculated identity;
- acceptance factual-evidence linkage.

Corrupt or incompatible rows must fail closed.

Repository methods must return controlled failed results without exposing raw payload bytes or exception traces.

No corrupt row may be repaired, replaced, or deleted automatically.

## 16. Classification behavior

The SQLite adapter must reproduce the approved in-memory classification semantics exactly.

Fail-closed order:

1. invalid request type before database access;
2. factual same ID with different digest → `identity_collision`;
3. factual same ID with different identity projection → `identity_collision`;
4. acceptance same ID with different digest → `acceptance_collision`;
5. acceptance same ID with different identity projection → `acceptance_collision`;
6. factual and acceptance both absent → `new_evidence`;
7. factual match and acceptance absent → `same_fact_new_acceptance`;
8. both identities and exact objects match → `exact_replay`;
9. identity projections/digests match and only governance-excluded diagnostics differ → `governance_replay`;
10. unresolved state → `rejected`.

The adapter must not infer:

- semantic duplicates;
- conflicting evidence;
- supersession;
- Knowledge;
- Prompt Candidates.

## 17. `classify_write` transaction boundary

`classify_write` is advisory and non-mutating.

It may use a read transaction but must not:

- insert;
- update;
- delete;
- create schema;
- change `user_version`;
- acquire a write transaction;
- call `write`.

The returned classification may become stale before a later separate call to `write`.

## 18. `write` transaction boundary

`write` shall:

1. validate the exact `EvidenceWriteRequest` before opening the database;
2. open one connection;
3. execute `BEGIN IMMEDIATE`;
4. classify using the same connection and transaction;
5. perform only the mutation authorized by that classification;
6. commit only after all required inserts succeed;
7. rollback on any failure.

Allowed mutations:

- `new_evidence`: insert one factual row and one acceptance row;
- `same_fact_new_acceptance`: insert one acceptance row.

No mutation for:

- exact replay;
- governance replay;
- identity collision;
- acceptance collision;
- rejected request;
- repository failure.

## 19. Forbidden SQL behavior

The implementation must not use:

- `UPDATE`;
- `DELETE`;
- `REPLACE`;
- `INSERT OR REPLACE`;
- `INSERT OR IGNORE`;
- UPSERT clauses;
- trigger-driven mutation;
- cascading deletion;
- vacuum/compaction;
- attach/detach database;
- schema alteration;
- migration SQL.

Only exact plain `INSERT` statements are allowed for approved append operations.

## 20. Concurrency boundary

`BEGIN IMMEDIATE` provides the write serialization boundary.

SQLite lock or busy errors:

- are not retried;
- do not sleep;
- do not back off;
- return `failed_repository_operation`;
- perform no partial mutation.

No in-process global lock is required because each write transaction relies on SQLite locking.

## 21. Failure mapping

Controlled validation failures map to existing rejected/failed repository result contracts.

SQLite operational, integrity, or database errors must not escape from public repository methods.

Constructor failures may raise controlled `ValueError` for:

- invalid path;
- unsupported schema version;
- incompatible schema;
- invalid database header or unreadable database.

Public methods must not return raw SQLite exception objects.

## 22. Focused test boundary

The next implementation gate may execute exactly one focused pytest process for:

```text
tests/infrastructure/test_sqlite_evidence_repository.py
```

Required focused coverage includes:

- exact one-class/five-method public surface;
- exact schema objects and columns;
- exact `user_version`;
- new database bootstrap;
- reopen persistence;
- two adapter instances reading the same file sequentially;
- new evidence write;
- same-fact/new-acceptance append;
- exact replay;
- governance replay;
- factual identity collision;
- acceptance collision;
- read ordering;
- request validation;
- corrupt payload digest;
- corrupt canonical bytes;
- incompatible schema version;
- unexpected schema object;
- transaction rollback when acceptance insert fails;
- no retry on lock/busy;
- no update/delete/upsert SQL;
- no Knowledge or Prompt behavior.

Full regression remains deferred until the adapter implementation result has been independently reviewed and committed.

## 23. Implementation prohibitions

The next implementation must not:

- modify the repository interface;
- modify serialization;
- modify domain contracts;
- modify the in-memory adapter;
- add dependencies;
- add configuration;
- add CLI or application wiring;
- process real or synthetic assets;
- create a production database under the repository;
- create migration files;
- introduce Knowledge or Prompt behavior.

Test databases must be created only under the controlled pytest temporary parent and removed by the test process.

## 24. Phase-closure and office-PC handoff requirement

PR-024 must not be declared complete until all of the following are independently verified:

- Phase 24 branch is clean;
- every approved commit exists on the remote branch;
- Phase 24 is fast-forward merged into `main`;
- local `main`, `origin/main`, and remote `main` are identical;
- the official Phase 24 annotated tag is created and pushed;
- the tag object and peeled target are verified remotely;
- no commit, untracked file, database, or required document exists only on the current PC;
- a continuity handoff records exact branch, commit, tag, file scope, test result, and architecture boundaries;
- office-PC continuation commands use `git fetch --prune --tags`, `git checkout main`, and `git pull --ff-only origin main`;
- office-PC verification confirms the expected HEAD, tag target, divergence `0 0`, and clean working tree.

This handoff requirement is a closure condition, not part of the SQLite adapter implementation slice.

## 25. Decision

# SQLITE EVIDENCE REPOSITORY ADAPTER ARCHITECTURE AND SCHEMA V1 APPROVED FOR THE NEXT CONTROLLED IMPLEMENTATION SLICE

## 26. Exact next gate

**PR-024AB — SQLite Evidence Repository Adapter Implementation**

The next gate may create only the two approved source/test files and execute one focused test process with zero automatic retries.
