# PR-024R — Evidence Repository Interface Contract and Implementation Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `162ab30a73b29a9e74d14b398dfbfe9ca156029e` |
| Gate type | Documentation-only |
| Final decision | **EVIDENCE REPOSITORY INTERFACE CONTRACT APPROVED; TWO-FILE INTERFACE-ONLY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE** |
| Exact next gate | **PR-024S - Evidence Repository Interface Contract Implementation** |

## 2. Purpose

PR-024R reassesses the `EvidenceRepository` interface after the standalone acceptance-record and deterministic acceptance-identity prerequisites were committed.

This gate refines the interface-only contract. It creates no adapter, persistence mechanism, transaction implementation, repository data, or runtime write behavior.

## 3. Verified checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `162ab30a73b29a9e74d14b398dfbfe9ca156029e`;
- divergence: `0 0`;
- Phase 24 is exactly twelve commits ahead of main;
- exact twelve-commit chain;
- latest parent: `cd9cbd4fd802ad42332075190de3a026f2388df2`;
- latest subject: `feat: add acceptance record identity contracts`;
- latest exact five-file scope;
- exact twenty-five-file Phase 24 scope;
- zero merge commits;
- clean working tree.

## 4. Completed prerequisites

The following are now committed and verified:

1. immutable `AcceptedEvidence`;
2. deterministic factual Evidence identity using `ev1_`;
3. pure accepted-Evidence materializer;
4. immutable standalone `AcceptanceRecord`;
5. deterministic governance-event identity using `ar1_`;
6. canonical factual digest result;
7. canonical acceptance digest result;
8. PR-023E repository and persistence boundary.

The earlier PR-024N deferral condition is therefore closed for interface-only implementation.

## 5. Interface ownership

The authoritative interface is:

`	ext
EvidenceRepository
`

Intended module:

`	ext
src/rie/interfaces/evidence_repository.py
`

The module belongs to the application-facing interface boundary.

It owns no domain identity and performs no persistence.

## 6. Repository contract constant

The future module must expose:

`	ext
EVIDENCE_REPOSITORY_CONTRACT_VERSION = 1.0.0
`

`EvidenceWriteRequest.repository_contract_version` must equal this exact value.

No environment, package metadata, adapter, database, or file path may supply the version.

## 7. Exact public contracts

The future module defines exactly seven public contracts:

1. frozen `EvidenceWriteRequest`;
2. frozen `EvidenceLookupResult`;
3. frozen `AcceptanceRecordLookupResult`;
4. frozen `AcceptanceRecordListResult`;
5. frozen `EvidenceWriteClassificationResult`;
6. frozen `EvidenceWriteResult`;
7. `EvidenceRepository` protocol.

No field has a default.

Private validation helpers are permitted.

No serializer, adapter, repository implementation, database model, transaction class, or retry helper is permitted.

## 8. EvidenceWriteRequest

Exact fields:

1. `accepted_evidence`;
2. `canonical_evidence_bytes_digest`;
3. `acceptance_record`;
4. `canonical_acceptance_bytes_digest`;
5. `repository_contract_version`;
6. `expected_identity_policy_id`;
7. `expected_identity_policy_version`.

Validation requires:

- exact `AcceptedEvidence`;
- exact `AcceptanceRecord`;
- factual digest is 64 lowercase hexadecimal characters;
- acceptance digest is 64 lowercase hexadecimal characters;
- factual digest equals the suffix of `accepted_evidence.evidence_id`;
- acceptance digest equals the suffix of `acceptance_record.acceptance_record_id`;
- `acceptance_record.evidence_id` equals `accepted_evidence.evidence_id`;
- repository contract version equals `1.0.0`;
- expected factual identity policy equals the accepted-Evidence materialization policy;
- acceptance-record factual identity policy equals the same policy;
- materializer ID/version, acceptance record ID, reviewer, reason, review record, and event instant match the accepted-Evidence materialization record;
- all values are supplied explicitly;
- no identity is generated or recalculated by the repository interface.

For future `EvidenceWriteRequest`:

`	ext
canonical_evidence_bytes_digest == EvidenceIdentityResult.digest_hex
canonical_acceptance_bytes_digest == AcceptanceIdentityResult.digest_hex
`

## 9. EvidenceLookupResult

Exact fields:

1. `status`;
2. `accepted_evidence`;
3. `canonical_evidence_bytes_digest`;
4. `acceptance_record_ids`;
5. `reason_codes`;
6. `diagnostics`.

Allowed statuses:

`	ext
found
not_found
failed
`

Rules:

- `found` contains exact accepted Evidence, a valid factual digest, and at least one valid `ar1_` ID;
- `not_found` and `failed` contain no accepted Evidence, no factual digest, and an empty ID tuple;
- acceptance-record IDs are unique and lexicographically ordered;
- reason codes and diagnostics are immutable tuples of non-empty strings;
- infrastructure exception objects are forbidden.

## 10. AcceptanceRecordLookupResult

Exact fields:

1. `status`;
2. `acceptance_record`;
3. `canonical_acceptance_bytes_digest`;
4. `evidence_id`;
5. `reason_codes`;
6. `diagnostics`.

Rules:

- `found` contains an exact `AcceptanceRecord`;
- its digest equals the suffix of `acceptance_record_id`;
- `evidence_id` equals the record's factual ID;
- `not_found` and `failed` contain no record, digest, or factual ID;
- reason codes and diagnostics remain immutable strings.

## 11. AcceptanceRecordListResult

Exact fields:

1. `status`;
2. `evidence_id`;
3. `acceptance_records`;
4. `reason_codes`;
5. `diagnostics`.

Rules:

- requested `evidence_id` is always explicit and valid;
- `found` contains at least one exact acceptance record;
- all records reference the requested factual ID;
- records are unique and ordered lexicographically by `acceptance_record_id`;
- `not_found` and `failed` contain an empty record tuple;
- pagination is not introduced.

## 12. EvidenceWriteClassificationResult

Exact fields:

1. `classification`;
2. `evidence_id`;
3. `acceptance_record_id`;
4. `existing_evidence_digest`;
5. `existing_acceptance_digest`;
6. `reason_codes`;
7. `diagnostics`.

Allowed classifications:

`	ext
new_evidence
exact_replay
governance_replay
same_fact_new_acceptance
identity_collision
acceptance_collision
semantic_duplicate_candidate
conflicting_evidence_candidate
superseding_evidence_candidate
rejected
`

Both identities must always be valid explicit IDs.

Existing digests are either null or valid lowercase SHA-256 hex.

This contract reports classification only. It performs no mutation.

## 13. EvidenceWriteResult

Exact fields:

1. `status`;
2. `classification`;
3. `evidence_id`;
4. `acceptance_record_id`;
5. `mutation_performed`;
6. `reason_codes`;
7. `diagnostics`.

Allowed statuses:

`	ext
inserted_new_evidence
appended_acceptance_record
unchanged_exact_replay
unchanged_governance_replay
rejected_identity_collision
rejected_acceptance_collision
rejected_invalid_request
failed_repository_operation
`

Required status mapping:

| Status | Classification | Mutation |
|---|---|---:|
| `inserted_new_evidence` | `new_evidence` | True |
| `appended_acceptance_record` | `same_fact_new_acceptance` | True |
| `unchanged_exact_replay` | `exact_replay` | False |
| `unchanged_governance_replay` | `governance_replay` | False |
| `rejected_identity_collision` | `identity_collision` | False |
| `rejected_acceptance_collision` | `acceptance_collision` | False |
| `rejected_invalid_request` | `rejected` | False |
| `failed_repository_operation` | any controlled final classification | False |

No silent success, silent upsert, overwrite, replacement identity, or hidden retry is permitted.

## 14. EvidenceRepository protocol

The protocol contains exactly:

`python
get_evidence(
    evidence_id: str,
) -> EvidenceLookupResult

get_acceptance_record(
    acceptance_record_id: str,
) -> AcceptanceRecordLookupResult

list_acceptance_records(
    evidence_id: str,
) -> AcceptanceRecordListResult

classify_write(
    request: EvidenceWriteRequest,
) -> EvidenceWriteClassificationResult

write(
    request: EvidenceWriteRequest,
) -> EvidenceWriteResult
`

No additional public method is authorized.

Specifically forbidden:

`	ext
update
delete
replace
upsert
merge
compact
bulk_write
`

## 15. Protocol behavior boundary

The protocol defines signatures only.

It does not:

- inspect repository state;
- classify a real write;
- store data;
- open a transaction;
- lock a resource;
- commit or roll back;
- generate an identity;
- serialize bytes;
- retry;
- access a clock;
- access files, databases, network, or environment;
- create Knowledge;
- create Prompt Candidates.

Implementing objects supply behavior in a later infrastructure-adapter gate.

## 16. Validation boundary

Constructor validation may verify:

- exact runtime contract types;
- ID and digest syntax;
- supported version;
- tuple structure;
- deterministic tuple order;
- status/classification mapping;
- cross-contract acceptance compatibility.

Constructor validation must not query repository state or infer semantic duplicate/conflict/supersession classifications.

## 17. Semantic candidate classifications

These tokens remain reserved:

`	ext
semantic_duplicate_candidate
conflicting_evidence_candidate
superseding_evidence_candidate
`

The repository interface does not infer them.

A later reviewed governance workflow must supply an explicit marker before an adapter may emit one of these classifications.

## 18. Future two-file implementation boundary

PR-024S may create exactly:

1. `src/rie/interfaces/evidence_repository.py`;
2. `tests/interfaces/test_evidence_repository.py`.

No existing file may be modified.

The interface module must use direct imports from the defining domain modules. No central re-export is required.

## 19. Required focused tests

The next implementation test module must cover:

- exact seven public contracts;
- six frozen dataclasses and no defaults;
- exact fields and field order;
- exact repository version constant;
- valid write request compatibility;
- factual and acceptance digest mismatch rejection;
- materialization-record compatibility rejection;
- lookup status shapes;
- ordered unique acceptance IDs;
- ordered acceptance-record lists;
- exact controlled classifications;
- exact controlled write statuses;
- exact write-status/classification/mutation mapping;
- protocol method names and return annotations;
- absence of forbidden methods;
- absence of filesystem, database, network, clock, UUID, random, retry, persistence, Knowledge, and Prompt behavior.

Only `tests/interfaces/test_evidence_repository.py` may be executed, exactly once, with zero automatic retry.

## 20. Explicit exclusions

PR-024S must not implement or modify:

- AcceptedEvidence;
- Evidence identity;
- AcceptanceRecord;
- acceptance identity;
- materializer;
- repository adapter;
- in-memory repository;
- filesystem repository;
- database repository;
- serializer;
- transaction manager;
- migration;
- persistence configuration;
- retry;
- semantic governance engine;
- Knowledge;
- Prompt Candidate;
- asset/parser behavior;
- full regression.

## 21. Options reviewed

### Option A — Continue deferring the interface

**Rejected.** All referenced immutable and identity contracts are now committed.

### Option B — Implement an in-memory repository together with the interface

**Rejected.** That would combine an interface contract with persistence behavior.

### Option C — Define placeholders using `object` or mutable mappings

**Rejected.** Placeholder typing would weaken the approved contract.

### Option D — Implement the exact protocol and immutable request/result contracts

**Selected.** This is the smallest safe interface-only slice.

## 22. Final decision

# EVIDENCE REPOSITORY INTERFACE CONTRACT APPROVED; TWO-FILE INTERFACE-ONLY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE

Approval is limited to the exact two-file PR-024S implementation boundary.

## 23. Exact next gate

**PR-024S - Evidence Repository Interface Contract Implementation**

The next gate may create the two approved files and execute the one focused test module exactly once.

## 24. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-024P/PR-024Q commit/push checkpoint | PASSED |
| Twelve-commit Phase 24 chain | PASSED |
| Twenty-five-file Phase 24 scope | PASSED |
| AcceptedEvidence prerequisite | PASSED |
| Factual Evidence identity prerequisite | PASSED |
| AcceptanceRecord prerequisite | PASSED |
| Acceptance identity prerequisite | PASSED |
| Materializer prerequisite | PASSED |
| PR-023E method boundary | PASSED |
| Request/result field boundary | PASSED |
| Replay/collision token boundary | PASSED |
| Interface-only implementation readiness | APPROVED |
| Repository adapter | NOT AUTHORIZED |
| Persistence | NOT AUTHORIZED |
| Knowledge/Prompt coupling | ABSENT |
| Earlier phases/environment preservation | PASSED |

## 25. Action truth table

| Action | Performed |
|---|---|
| Commit-output verification | True |
| Read-only checkpoint verification | True |
| Governing contract integrity review | True |
| Domain prerequisite inspection | True |
| PR-023E interface review | True |
| Existing repository-contract search | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Repository interface implemented | False |
| Repository adapter implemented | False |
| Persistence implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 26. Gate conclusion

PR-024R concludes **EVIDENCE REPOSITORY INTERFACE CONTRACT APPROVED; TWO-FILE INTERFACE-ONLY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE**.

Only `PR-024S - Evidence Repository Interface Contract Implementation` is authorized after PR-024R commit/push verification.
