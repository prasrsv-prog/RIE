# PR-024X — Durable Evidence Repository Persistence Technology and Serialization Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `60b877b3a5e0313fc3e6c34d57c40511d822b943` |
| Gate type | Documentation-only |
| Final decision | **SQLITE SELECTED FOR THE FIRST DURABLE EVIDENCE REPOSITORY; EXACT TWO-FILE PERSISTENCE SERIALIZATION CONTRACT IMPLEMENTATION APPROVED AS THE NEXT CONTROLLED SLICE** |
| Exact next gate | **PR-024Y - Evidence Repository Persistence Serialization Contract Implementation** |

## 2. Purpose

PR-024X selects the first durable repository technology and defines the serialization prerequisite that must exist before any database adapter is implemented.

This gate does not create a database, serialize a record, or implement a durable adapter.

## 3. Verified checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `60b877b3a5e0313fc3e6c34d57c40511d822b943`;
- divergence: `0 0`;
- Phase 24 is exactly sixteen commits ahead of main;
- exact sixteen-commit chain;
- latest parent: `377430c709f9cb97d18eec2e10df678326d1f215`;
- latest subject: `feat: add in-memory evidence repository adapter`;
- latest exact three-file scope;
- exact thirty-three-file Phase 24 scope;
- zero merge commits;
- clean working tree.

## 4. Completed prerequisites

Committed prerequisites now include:

1. immutable accepted Evidence;
2. deterministic factual identity;
3. immutable acceptance record;
4. deterministic acceptance identity;
5. materializer;
6. exact repository request/result contracts;
7. exact five-method repository protocol;
8. process-local in-memory reference adapter;
9. focused replay, collision, ordering, and concurrency evidence.

## 5. Technology selection

The first durable adapter technology is:

`	ext
Python standard-library sqlite3
SQLite database
`

Reasons:

- no third-party runtime dependency;
- transactional insert behavior;
- primary and foreign-key constraints;
- deterministic local-file deployment;
- mature corruption and integrity primitives;
- appropriate scope for the first single-node durable repository;
- no network service or credential dependency.

This selection does not authorize adapter implementation yet.

## 6. Explicit technology limits

The first SQLite adapter will not claim:

- distributed consensus;
- multi-host writes;
- remote access;
- horizontal scaling;
- object storage;
- replication;
- automatic backup;
- high availability;
- cross-database migration;
- Knowledge storage;
- Prompt storage.

A later architecture gate is required before any technology change.

## 7. Serialization-first rule

No durable adapter may be implemented until deterministic persistence serialization is committed and independently reviewed.

The serializer is infrastructure-neutral and must perform no file or database I/O.

The serializer must preserve the full immutable aggregate, including fields excluded from identity.

## 8. Future serialization module

The next implementation may create exactly:

`	ext
src/rie/infrastructure/evidence_repository_serialization.py
tests/infrastructure/test_evidence_repository_serialization.py
`

No existing file may be modified.

## 9. Exact serialization constants

The future module must define exactly:

`python
EVIDENCE_PERSISTENCE_CONTRACT_VERSION = "1.0.0"
ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID = "accepted-evidence-json-v1"
ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID = "acceptance-record-json-v1"
PERSISTENCE_DIGEST_ALGORITHM = "sha256"
`

No value may be inferred from a path, environment variable, clock, or database.

## 10. Serialized accepted-Evidence record

The future module must define one frozen `SerializedAcceptedEvidenceRecord` with exact fields:

1. `persistence_contract_version`;
2. `payload_schema_id`;
3. `evidence_id`;
4. `identity_policy_id`;
5. `identity_policy_version`;
6. `canonical_identity_digest`;
7. `payload_bytes_digest`;
8. `payload_bytes`.

`payload_bytes` is exact canonical UTF-8 JSON bytes.

## 11. Serialized acceptance-record record

The future module must define one frozen `SerializedAcceptanceRecord` with exact fields:

1. `persistence_contract_version`;
2. `payload_schema_id`;
3. `acceptance_record_id`;
4. `evidence_id`;
5. `identity_policy_id`;
6. `identity_policy_version`;
7. `canonical_identity_digest`;
8. `payload_bytes_digest`;
9. `payload_bytes`.

The factual ID remains explicit for future relational integrity.

## 12. Exact public serialization functions

The future module exposes exactly:

`python
serialize_accepted_evidence(
    accepted_evidence: AcceptedEvidence,
    canonical_identity_digest: str,
) -> SerializedAcceptedEvidenceRecord

deserialize_accepted_evidence(
    serialized: SerializedAcceptedEvidenceRecord,
) -> AcceptedEvidence

serialize_acceptance_record(
    acceptance_record: AcceptanceRecord,
    canonical_identity_digest: str,
) -> SerializedAcceptanceRecord

deserialize_acceptance_record(
    serialized: SerializedAcceptanceRecord,
) -> AcceptanceRecord
`

No file-path, connection, cursor, transaction, or repository parameter is authorized.

## 13. Canonical payload encoding

Canonical persistence payloads use:

- UTF-8;
- NFC normalization for every string;
- `ensure_ascii=False`;
- compact JSON separators;
- fixed explicit key order;
- no duplicate keys;
- no unknown keys;
- no omitted required keys;
- no implicit defaults;
- exact arrays for ordered tuples;
- exact two-element arrays for ordered key/value pairs;
- lowercase booleans;
- no NaN or Infinity;
- no float coercion;
- no trailing whitespace;
- no byte-order mark.

Persistence canonicalization is distinct from identity canonicalization.

## 14. Datetime encoding

Every datetime is normalized to UTC and encoded as:

`	ext
YYYY-MM-DDTHH:MM:SS.ffffffZ
`

Exactly six fractional digits are required.

Naive datetimes and noncanonical datetime strings fail closed.

## 15. Full-fidelity aggregate boundary

Accepted-Evidence serialization must preserve:

- evidence ID;
- contract version;
- candidate reference;
- source snapshot;
- producer snapshot;
- factual payload;
- locator;
- provenance;
- eligibility result;
- materialization record;
- ordered diagnostics.

Acceptance-record serialization must preserve all fourteen fields and ordered diagnostics.

Identity-excluded fields remain persisted because replay and governance inspection require full aggregate fidelity.

## 16. Digest boundary

`payload_bytes_digest` is lowercase SHA-256 over exact `payload_bytes`.

`canonical_identity_digest` is the existing factual or acceptance identity digest supplied by the caller.

Serialization must verify:

- digest format;
- ID prefix and digest suffix;
- caller digest equality with ID suffix;
- recalculated existing identity equality;
- identity policy ID/version equality.

The serializer verifies existing identities; it does not select or generate a new identity.

## 17. Deserialization fail-closed order

Deserialization must reject, in order:

1. wrong exact serialized-record type;
2. unsupported persistence contract version;
3. unsupported payload schema ID;
4. invalid record ID;
5. invalid identity-policy metadata;
6. invalid payload digest format;
7. payload digest mismatch;
8. invalid UTF-8;
9. duplicate JSON key;
10. noncanonical JSON bytes;
11. missing or extra field;
12. invalid nested type or token;
13. invalid datetime;
14. reconstructed aggregate validation failure;
15. record-ID mismatch;
16. factual-ID mismatch for acceptance records;
17. recalculated identity mismatch.

No repair, coercion, fallback, or retry is permitted.

## 18. Canonical re-encoding check

After decoding and reconstructing the aggregate, the serializer must re-encode it.

The re-encoded bytes must exactly equal the stored `payload_bytes`.

Equivalent but noncanonical JSON is rejected.

## 19. Error boundary

The serializer may raise controlled `ValueError` messages.

Messages must not include:

- raw payload bytes;
- full record content;
- file paths;
- database paths;
- credentials;
- object addresses;
- stack traces.

No error object is persisted.

## 20. No-I/O boundary

PR-024Y must not import or use:

`	ext
os
pathlib
sqlite3
pickle
shelve
subprocess
requests
httpx
socket
logging
environment variables
open
`

The standard-library `json`, `hashlib`, `unicodedata`, and datetime utilities are allowed only for pure serialization.

## 21. No-retry boundary

Every serialization or deserialization call performs one attempt.

Forbidden:

- retry loops;
- recursive retry;
- sleep/backoff;
- alternate decoder;
- permissive parser fallback;
- repair mode.

## 22. Focused-test boundary

PR-024Y may run exactly:

`	ext
tests/infrastructure/test_evidence_repository_serialization.py
`

One pytest process, zero automatic retry.

Full regression remains deferred.

## 23. Required focused tests

The next focused module must cover:

- exact frozen serialized-record fields;
- no defaults;
- exact constants;
- exact public function set;
- deterministic byte equality;
- deterministic payload digests;
- round-trip equality for accepted Evidence;
- round-trip equality for acceptance records;
- preservation of diagnostics and materialization fields;
- UTC six-digit datetime encoding;
- Unicode NFC behavior;
- non-ASCII preservation;
- ordered tuple and key/value-pair preservation;
- invalid exact input type;
- unsupported contract version;
- unsupported schema ID;
- invalid record IDs;
- identity-policy mismatch;
- caller digest mismatch;
- payload digest mismatch;
- invalid UTF-8;
- duplicate-key rejection;
- missing-field rejection;
- extra-field rejection;
- noncanonical-byte rejection;
- invalid nested type rejection;
- invalid datetime rejection;
- reconstructed identity mismatch;
- factual-ID mismatch in acceptance serialization;
- no I/O, SQLite, retry, Knowledge, or Prompt behavior.

## 24. Future SQLite schema boundary

After serialization is committed and reviewed, a later gate may define an SQLite adapter with three logical tables:

`	ext
repository_metadata
evidence_records
acceptance_records
`

Payloads will be stored as BLOBs containing exact canonical bytes.

Digests, IDs, schema IDs, and contract versions remain explicit columns.

No schema file or migration is authorized in PR-024Y.

## 25. Future transaction boundary

A later SQLite adapter must classify and mutate in one transaction.

Expected principles:

- `PRAGMA foreign_keys = ON`;
- explicit transaction start;
- insert-only factual and acceptance records;
- primary-key collision inspection;
- no last-write-wins;
- no `INSERT OR REPLACE`;
- no update/delete;
- rollback on every failure;
- no hidden retry.

Exact connection and transaction mechanics require a later review.

## 26. Database-path boundary

The future adapter must receive one explicit caller-supplied database path.

Forbidden future behavior:

- default path;
- current-directory discovery;
- environment lookup;
- home-directory lookup;
- repository-relative inference;
- network path inference;
- temporary fallback database;
- implicit in-memory fallback.

Path validation and security remain a later adapter-review concern.

## 27. In-memory adapter preservation

The committed in-memory adapter remains:

- process-local;
- volatile;
- reference-only;
- unchanged by PR-024Y.

It must not become a fallback when SQLite operations fail.

## 28. Options reviewed

### Option A — Implement SQLite and serialization together

**Rejected.** It would combine canonical format risk with transaction and schema risk.

### Option B — Use pickle

**Rejected.** It is not an acceptable stable or safe persistence contract.

### Option C — Store arbitrary dataclass dictionaries

**Rejected.** Implicit field ordering and permissive reconstruction weaken compatibility.

### Option D — Use canonical explicit JSON bytes, then implement SQLite later

**Selected.** This separates deterministic record fidelity from database mechanics.

### Option E — Use a remote database now

**Rejected.** It introduces credentials, networking, deployment, and operational concerns before the local durable contract is proven.

## 29. Final decision

# SQLITE SELECTED FOR THE FIRST DURABLE EVIDENCE REPOSITORY; EXACT TWO-FILE PERSISTENCE SERIALIZATION CONTRACT IMPLEMENTATION APPROVED AS THE NEXT CONTROLLED SLICE

Authorization is limited to the exact two-file pure serialization implementation.

## 30. Exact next gate

**PR-024Y - Evidence Repository Persistence Serialization Contract Implementation**

The next gate may create only the two approved serialization files and run the one focused test module exactly once.

## 31. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-024V/PR-024W commit/push checkpoint | PASSED |
| Sixteen-commit Phase 24 chain | PASSED |
| Thirty-three-file Phase 24 scope | PASSED |
| Repository interface integrity | PASSED |
| In-memory adapter integrity | PASSED |
| Existing durable adapter absence | PASSED |
| Existing serializer absence | PASSED |
| SQLite technology selection | APPROVED |
| Pure serialization prerequisite | APPROVED |
| Durable adapter implementation | DEFERRED |
| Schema/migration implementation | DEFERRED |
| Database creation | NOT AUTHORIZED |
| Full regression | DEFERRED |
| Knowledge/Prompt coupling | ABSENT |
| Earlier phases/environment preservation | PASSED |

## 32. Action truth table

| Action | Performed |
|---|---|
| Commit-output verification | True |
| Read-only checkpoint verification | True |
| Contract integrity review | True |
| Existing persistence search | True |
| Static serialization-boundary review | True |
| Technology selection | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Serialization implemented | False |
| Database created | False |
| SQLite adapter implemented | False |
| Migration implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 33. Gate conclusion

PR-024X concludes **SQLITE SELECTED FOR THE FIRST DURABLE EVIDENCE REPOSITORY; EXACT TWO-FILE PERSISTENCE SERIALIZATION CONTRACT IMPLEMENTATION APPROVED AS THE NEXT CONTROLLED SLICE**.

Only `PR-024Y - Evidence Repository Persistence Serialization Contract Implementation` is authorized after PR-024X commit/push verification.
