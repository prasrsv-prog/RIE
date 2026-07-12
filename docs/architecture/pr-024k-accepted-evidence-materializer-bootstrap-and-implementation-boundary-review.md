# PR-024K — Accepted Evidence Materializer Bootstrap and Implementation Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `606c706c68a695d9337073930bcbaa568ff147ea` |
| Gate type | Documentation-only |
| Final decision | **ACCEPTED EVIDENCE MATERIALIZER BOOTSTRAP BOUNDARY APPROVED; TWO-FILE MATERIALIZER IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE** |
| Next gate | **PR-024L - Accepted Evidence Materializer Contract and Compatibility Implementation** |
| Next gate type | **Implementation** |

## 2. Purpose

PR-024K verifies that the immutable accepted-Evidence contract, deterministic factual Evidence identity, deterministic candidate snapshot digest, and materialization input compatibility contract are all committed and compatible before authorizing materializer implementation.

This gate does not implement or execute a materializer.

## 3. Verified checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `606c706c68a695d9337073930bcbaa568ff147ea`;
- divergence: `0 0`;
- Phase 24 is exactly seven commits ahead of main;
- exact seven-commit Phase 24 chain;
- latest parent: `92e31387aa7be77ca260aee29db093c147bb9e20`;
- latest subject: `feat: add evidence candidate snapshot digest contract`;
- latest exact three-file candidate-snapshot scope;
- exact fourteen-file total Phase 24 scope;
- no merge commits;
- clean working tree before document creation.

## 4. Prerequisite closure

The following prerequisite slices are committed and verified:

1. immutable `AcceptedEvidence` domain contract;
2. deterministic factual Evidence identity;
3. explicit materialization snapshot/request/context/result boundary;
4. deterministic `EvidenceCandidate` snapshot digest;
5. focused result reviews for each implementation slice.

No materializer source or test file currently exists.

## 5. Dependency direction

The future materializer may depend only on:

`	ext
EvidenceCandidate
EvidenceCandidateSnapshotResult
calculate_evidence_candidate_snapshot
EvidenceMaterializationSnapshot
AcceptedEligibilityResult
EvidenceIdentityResult
calculate_evidence_identity
AcceptedEvidence and nested immutable contracts
EvidenceMaterializationContext
`

It must not depend on:

`	ext
repository interfaces or adapters
persistence
filesystem or network access
PDF/image/OCR/parser behavior
current clock
UUID or random values
automatic retry
Knowledge
Prompt Candidate
`

## 6. Materialization snapshot contract

`EvidenceMaterializationSnapshot` is a frozen dataclass with exactly:

- `accepted_evidence_contract_version`
- `source_snapshot`
- `producer_snapshot`
- `factual_payload`
- `provenance`
- `diagnostics`

All fields are explicit and have no defaults.

The materializer must never synthesize source classification, source eligibility, producer kind, schema versions, payload digest, locator type/schema, producer output digest, source registry version, or diagnostics.

## 7. Materialization context contract

`EvidenceMaterializationContext` is a frozen dataclass with exactly:

- `materializer_id`
- `materializer_version`
- `materialized_at`
- `acceptance_record_id`
- `accepted_by`
- `acceptance_reason`
- `review_record_id`

All strings are non-empty after trimming. `materialized_at` is timezone-aware.

The context contains governance/audit values only. It does not carry missing factual snapshot data.

## 8. Materialization request contract

`EvidenceMaterializationRequest` is a frozen dataclass with exactly:

- `candidate`
- `candidate_snapshot_result`
- `snapshot`
- `eligibility_result`
- `identity_result`
- `context`

All fields are required and exact-type validated.

The original candidate remains present and immutable.

## 9. Materialization result contract

`EvidenceMaterializationResult` is a frozen dataclass with exactly:

- `decision`
- `accepted_evidence`
- `reason_codes`
- `diagnostics`

Allowed decisions:

- `materialized`;
- `rejected`.

For `materialized`:

- `accepted_evidence` is present;
- `reason_codes` is empty;
- diagnostics contain no error severity.

For `rejected`:

- `accepted_evidence` is absent;
- `reason_codes` is non-empty;
- diagnostics explain the rejection.

Ordinary compatibility rejection is represented by this result, not by success or hidden fallback.

## 10. Candidate snapshot validation

The materializer recalculates `EvidenceCandidateSnapshotResult` from the exact candidate and requires complete equality with the supplied result.

This equality validates all eighteen candidate fields, including `candidate_contract_version`. No additional candidate-contract-version field is added to the snapshot result.

Candidate snapshot mismatch rejects materialization.

## 11. Candidate compatibility checks

The materializer checks:

1. candidate errors tuple is empty;
2. source checksum algorithm is exactly `sha256`;
3. source checksum equals source snapshot content digest;
4. source ID/type/authority/lifecycle/reference equal the corresponding source snapshot fields;
5. producer name/version and result contract version equal producer snapshot values;
6. payload type and raw payload equal factual payload values;
7. candidate locator equals factual locator value;
8. execution ID equals provenance collection ID;
9. execution timestamp is RFC 3339 with explicit timezone and equals provenance observation instant.

No field is normalized beyond the already approved domain and canonicalization contracts.

## 12. Eligibility compatibility checks

The materializer requires:

- decision exactly `eligible`;
- eligibility candidate digest equals the validated candidate snapshot digest;
- eligibility source ID equals source snapshot source ID;
- eligibility policy metadata is non-empty;
- eligibility diagnostics satisfy accepted-Evidence restrictions.

No eligibility policy executes inside the materializer.

## 13. Identity compatibility checks

The materializer builds a temporary accepted-Evidence aggregate only from explicit request values, derives `EvidenceIdentityInput` through the committed identity function, recalculates `EvidenceIdentityResult`, and requires complete equality with the supplied result.

The validated Evidence ID becomes the top-level `AcceptedEvidence.evidence_id`.

No new identity policy or ID format is introduced.

## 14. Accepted-Evidence construction

On successful compatibility validation, the materializer constructs:

- `EvidenceCandidateReference` from candidate, validated snapshot result, and factual payload digest;
- `EvidenceMaterializationRecord` from explicit context plus identity policy metadata;
- one immutable `AcceptedEvidence` aggregate.

The materializer performs no persistence and does not mutate the candidate, snapshot, eligibility result, identity result, context, or returned accepted Evidence.

## 15. Timestamp rule

Candidate `execution_timestamp` must be RFC 3339 with `Z` or an explicit numeric UTC offset.

Parsing uses only the supplied value. Naive timestamps reject materialization.

The parsed instant must equal `EvidenceProvenance.observed_at`.

No current-time call is allowed.

## 16. Diagnostics rule

- non-empty candidate errors reject materialization;
- candidate warnings are not automatically converted into accepted-Evidence diagnostics;
- accepted-Evidence diagnostics are supplied explicitly by the snapshot;
- success diagnostics permit only `info` and `warning`;
- rejection diagnostics must identify the failed compatibility rule;
- no hidden diagnostic mapping exists.

## 17. Rejection reason codes

The materializer may return only:

- `candidate_has_errors`
- `unsupported_source_checksum_algorithm`
- `candidate_snapshot_mismatch`
- `candidate_contract_version_mismatch`
- `candidate_source_id_mismatch`
- `candidate_source_type_mismatch`
- `candidate_source_authority_mismatch`
- `candidate_source_lifecycle_mismatch`
- `candidate_source_reference_mismatch`
- `candidate_source_digest_mismatch`
- `candidate_producer_name_mismatch`
- `candidate_producer_version_mismatch`
- `candidate_producer_contract_mismatch`
- `candidate_payload_type_mismatch`
- `candidate_payload_value_mismatch`
- `candidate_locator_value_mismatch`
- `candidate_collection_id_mismatch`
- `candidate_observed_at_mismatch`
- `eligibility_not_eligible`
- `eligibility_candidate_digest_mismatch`
- `eligibility_source_id_mismatch`
- `identity_result_mismatch`
- `identity_policy_mismatch`
- `materialization_context_invalid`
- `diagnostics_invalid`
- `request_invalid`

No free-form reason code, hidden fallback, or retry classification is allowed.

## 18. Validation order

The implementation uses deterministic validation order:

1. request exact types and immutable contract invariants;
2. materialization context validation;
3. candidate error and checksum-algorithm checks;
4. candidate snapshot recalculation and equality;
5. candidate-to-snapshot factual compatibility;
6. timestamp compatibility;
7. eligibility compatibility;
8. deterministic Evidence identity recalculation and equality;
9. accepted-Evidence aggregate construction;
10. success result construction.

On rejection, reason codes are returned in this order without duplicate values.

## 19. Implementation scope

The next implementation gate may create exactly:

1. `src/rie/application/evidence_materializer.py`;
2. `tests/application/test_evidence_materializer.py`.

No existing file modification is authorized.

No interface, repository, adapter, persistence, configuration, dependency, asset, or documentation file may be changed by the implementation gate.

## 20. Required public API

The future source module provides exactly:

- frozen `EvidenceMaterializationSnapshot`;
- frozen `EvidenceMaterializationContext`;
- frozen `EvidenceMaterializationRequest`;
- frozen `EvidenceMaterializationResult`;
- `materialize_accepted_evidence(request) -> EvidenceMaterializationResult`.

Private helpers are permitted only for deterministic validation and construction.

## 21. Focused-test requirements

Focused tests must cover:

1. exact frozen contract fields and no defaults;
2. successful materialization;
3. immutable returned aggregate;
4. candidate snapshot recalculation;
5. each candidate compatibility rejection;
6. candidate errors rejection;
7. unsupported checksum algorithm rejection;
8. explicit-timezone parsing and naive timestamp rejection;
9. eligibility compatibility rejection;
10. identity result recalculation and mismatch rejection;
11. materialization record construction from explicit context;
12. candidate reference construction;
13. deterministic reason-code order and deduplication;
14. no mutation of input contracts;
15. no filesystem, network, repository, persistence, parser, current clock, UUID, random, retry, Knowledge, or Prompt behavior;
16. exactly one focused execution and zero retry.

## 22. Explicit exclusions

PR-024L must not implement:

- acceptance-record identity;
- repository replay or collision classification;
- repository interface or adapter;
- persistence;
- accepted-Evidence update/delete;
- Knowledge;
- Prompt Candidate;
- parser or asset behavior;
- full regression.

## 23. Full regression decision

Full regression remains deferred.

PR-024L may execute only its exact focused materializer test module. Broader regression requires a later result review and controlled integration gate.

## 24. Options reviewed

### Option A — Continue deferring materializer implementation

**Rejected.** All explicit prerequisites are now committed and verified.

### Option B — Combine materializer and repository persistence

**Rejected.** Materialization and storage remain separate responsibilities.

### Option C — Modify existing accepted-Evidence, identity, or candidate contracts

**Rejected.** The existing contracts are sufficient and frozen for this slice.

### Option D — Authorize the exact two-file pure materializer implementation

**Selected.** It preserves all established boundaries and permits focused compatibility validation.

## 25. Final decision

# ACCEPTED EVIDENCE MATERIALIZER BOOTSTRAP BOUNDARY APPROVED; TWO-FILE MATERIALIZER IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE

Authorization is limited to the exact two implementation files and focused tests described above.

## 26. Exact next gate

**PR-024L - Accepted Evidence Materializer Contract and Compatibility Implementation**

Type: **Implementation**

Approved implementation files:

1. `src/rie/application/evidence_materializer.py`;
2. `tests/application/test_evidence_materializer.py`.

## 27. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-024I/PR-024J commit/push checkpoint | PASSED |
| Seven-commit Phase 24 chain | PASSED |
| Fourteen-file total Phase 24 scope | PASSED |
| Candidate contract integrity | PASSED |
| Candidate snapshot integrity | PASSED |
| Accepted-Evidence integrity | PASSED |
| Evidence identity integrity | PASSED |
| Materialization contracts | APPROVED |
| Candidate compatibility rules | APPROVED |
| Eligibility compatibility rules | APPROVED |
| Identity compatibility rules | APPROVED |
| Timestamp and diagnostic rules | APPROVED |
| Rejection reason codes | APPROVED |
| Two-file implementation scope | APPROVED |
| Materializer implementation | AUTHORIZED FOR NEXT GATE |
| Repository/persistence | DEFERRED |
| Knowledge/Prompt | DEFERRED |
| Earlier phases/environment preservation | PASSED |

## 28. Action truth table

| Action | Performed |
|---|---|
| Read-only Phase 24 checkpoint verification | True |
| Latest candidate-snapshot commit verification | True |
| Exact branch-scope verification | True |
| Contract and implementation hash verification | True |
| Static contract inspection | True |
| Materializer boundary defined | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Existing file modified | False |
| Dependency/configuration changed | False |
| Asset/parser execution | False |
| Materializer implemented | False |
| Repository/persistence implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 29. Gate conclusion

PR-024K concludes **ACCEPTED EVIDENCE MATERIALIZER BOOTSTRAP BOUNDARY APPROVED; TWO-FILE MATERIALIZER IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE**.

Only `PR-024L - Accepted Evidence Materializer Contract and Compatibility Implementation` is authorized after PR-024K commit/push verification.
