# PR-024H — Accepted Evidence Materialization Snapshot Input Compatibility Contract Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `60f20a7135f9cf150e8c3a9ed0cf6cfbc4766ae9` |
| Gate type | Documentation-only |
| Final decision | **MATERIALIZATION SNAPSHOT INPUT COMPATIBILITY CONTRACT APPROVED; CANDIDATE SNAPSHOT DIGEST IMPLEMENTATION REQUIRED BEFORE MATERIALIZER** |
| Next gate | **PR-024I - Evidence Candidate Snapshot Digest Contract and Policy Implementation** |
| Next gate type | **Implementation** |

## 2. Purpose

PR-024H resolves the materialization-input ambiguity recorded in PR-024G by defining explicit immutable candidate-snapshot, materialization-snapshot, context, request, result, compatibility, and rejection contracts.

It does not implement any contract.

## 3. Verified checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `60f20a7135f9cf150e8c3a9ed0cf6cfbc4766ae9`;
- divergence: `0 0`;
- Phase 24 is exactly five commits ahead of main;
- exact five-commit Phase 24 chain;
- latest parent: `99d6ce8aff47d99d712a20328140e26924e18700`;
- latest subject: `docs: review accepted evidence materialization compatibility`;
- latest scope: exactly `docs/architecture/pr-024g-accepted-evidence-materialization-bootstrap-and-input-compatibility-review.md`;
- exact ten-file total Phase 24 scope;
- no merge commits;
- clean working tree before document creation.

## 4. Governing boundary

The future materializer remains a pure application service.

It receives explicit immutable values, validates cross-contract compatibility, recalculates deterministic factual Evidence identity, and either returns one immutable accepted Evidence aggregate or an explicit rejected result.

It must not:

- parse or inspect assets;
- calculate missing payload or source digests;
- infer schema versions;
- call a clock;
- generate UUIDs or random values;
- inspect a repository;
- persist anything;
- retry automatically;
- create Knowledge or Prompt Candidate output.

## 5. Candidate snapshot digest prerequisite

A versioned candidate snapshot policy is required before materializer implementation.

### Policy

| Item | Value |
|---|---|
| Policy ID | `rcis-evidence-candidate-snapshot` |
| Policy version | `1.0.0` |
| Canonicalization contract | `candidate-json-v1` |
| Digest algorithm | `sha256` |
| Digest representation | 64 lowercase hexadecimal characters |
| Text normalization | Unicode NFC |
| Encoding | UTF-8 |
| JSON whitespace | None |
| Key order | Fixed |
| Null insertion | Prohibited |
| Clock/random/path normalization | Prohibited |

### Exact candidate snapshot inputs

The snapshot input contains exactly the committed eighteen `EvidenceCandidate` fields in this order:

- `source_id`
- `source_type`
- `source_checksum_algorithm`
- `source_checksum`
- `source_authority`
- `source_lifecycle_state`
- `source_reference`
- `execution_id`
- `producer_name`
- `producer_version`
- `result_contract_version`
- `execution_timestamp`
- `payload_type`
- `raw_payload`
- `locator`
- `warnings`
- `errors`
- `candidate_contract_version`

Tuple values serialize as ordered JSON arrays. Immutable mapping representations preserve their explicitly supplied ordered pair sequence. Unsupported mutable values and non-finite floating-point values fail closed.

### Candidate snapshot result

`EvidenceCandidateSnapshotResult` contains exactly:

- `candidate_snapshot_digest`
- `digest_algorithm`
- `snapshot_policy_id`
- `snapshot_policy_version`
- `canonicalization_contract_version`
- `canonical_byte_length`

The result contains no repository state, eligibility decision, accepted Evidence, Knowledge, or Prompt data.

## 6. Materialization snapshot contract

`EvidenceMaterializationSnapshot` contains exactly:

- `accepted_evidence_contract_version`
- `source_snapshot`
- `producer_snapshot`
- `factual_payload`
- `provenance`
- `diagnostics`

The snapshot carries all explicit factual values needed to assemble accepted Evidence, except the candidate object, eligibility result, deterministic identity result, and governance context supplied separately.

### Snapshot ownership

- `accepted_evidence_contract_version` is explicit and becomes `AcceptedEvidence.contract_version`.
- `source_snapshot` is an explicit `EvidenceSourceSnapshot`.
- `producer_snapshot` is an explicit `EvidenceProducerSnapshot`.
- `factual_payload` is an explicit `EvidencePayload`.
- `provenance` is an explicit `EvidenceProvenance`.
- `diagnostics` is an explicit tuple of `EvidenceDiagnostic`.

The materializer must not synthesize missing snapshot fields.

## 7. Materialization context contract

`EvidenceMaterializationContext` contains exactly:

- `materializer_id`
- `materializer_version`
- `materialized_at`
- `acceptance_record_id`
- `accepted_by`
- `acceptance_reason`
- `review_record_id`

All strings are non-empty after trimming. `materialized_at` must be a timezone-aware `datetime`.

Identity policy ID and version are not duplicated in context. They come from the validated `EvidenceIdentityResult` and are copied into `EvidenceMaterializationRecord`.

## 8. Materialization request contract

`EvidenceMaterializationRequest` contains exactly:

- `candidate`
- `candidate_snapshot_result`
- `snapshot`
- `eligibility_result`
- `identity_result`
- `context`

The request therefore preserves the original immutable candidate while supplying every additional explicit factual, eligibility, identity, and governance value required by PR-023C.

## 9. Materialization result contract

`EvidenceMaterializationResult` contains exactly:

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

No exception is used for ordinary contract rejection. Unexpected programming or infrastructure faults remain exceptions and must not be converted into success.

## 10. Explicit candidate-to-snapshot compatibility rules

The materializer validates exactly:

1. candidate contract version equals the snapshot result's reviewed candidate contract;
2. recalculated candidate snapshot result equals the supplied candidate snapshot result;
3. candidate has no errors;
4. candidate source checksum algorithm is exactly `sha256`;
5. candidate `source_checksum` equals `source_snapshot.source_content_digest`;
6. candidate `source_id` equals `source_snapshot.source_id`;
7. candidate `source_type` equals `source_snapshot.source_type`;
8. candidate `source_authority` equals `source_snapshot.authority_status`;
9. candidate `source_lifecycle_state` equals `source_snapshot.lifecycle_status`;
10. candidate `source_reference` equals `source_snapshot.source_path`;
11. candidate producer name/version equal producer snapshot name/version;
12. candidate result contract version equals producer contract version;
13. candidate payload type equals factual payload type;
14. candidate raw payload equals factual payload payload;
15. candidate locator equals factual payload locator value;
16. candidate execution ID equals provenance collection ID;
17. candidate execution timestamp parses to the exact timezone-aware provenance observation time.

Document classification, source eligibility, producer kind, payload schema version, payload digest, locator type/schema, producer output digest, source registry version, and diagnostics remain explicit snapshot values and are never inferred from candidate fields.

## 11. Candidate timestamp rule

`EvidenceCandidate.execution_timestamp` must be an RFC 3339 timestamp with an explicit `Z` or numeric UTC offset.

The materializer parses it without using the current clock and requires exact instant equality with `EvidenceProvenance.observed_at`.

Naive timestamps are rejected.

## 12. Candidate warning and error rule

- Any non-empty candidate `errors` tuple rejects materialization.
- Candidate warnings are not automatically converted into `EvidenceDiagnostic`.
- All accepted-Evidence diagnostics are supplied explicitly in the materialization snapshot.
- Snapshot diagnostics permit only `info` and `warning` severity.
- Candidate warnings may be checked against explicit diagnostics only when a later mapping policy is independently approved; no such mapping is required for this slice.

## 13. Eligibility compatibility rules

The materializer requires:

1. `eligibility_result.decision` equals `eligible`;
2. eligibility candidate snapshot digest equals the supplied and recalculated candidate snapshot digest;
3. eligibility source ID equals source snapshot source ID;
4. eligibility diagnostics contain no error severity;
5. policy ID/version are explicit and non-empty.

No eligibility policy executes inside materialization.

## 14. Deterministic identity compatibility rules

The materializer constructs `EvidenceIdentityInput` exclusively from:

- materialization snapshot accepted-Evidence contract version;
- source snapshot;
- producer snapshot;
- factual payload and locator;
- provenance producer output digest.

It recalculates `EvidenceIdentityResult` using the committed identity implementation.

The recalculated result must equal the supplied result across:

- Evidence ID;
- digest algorithm;
- digest hex;
- identity policy ID;
- identity policy version;
- canonicalization contract version;
- canonical byte length.

Any mismatch rejects materialization.

## 15. AcceptedEvidence construction rules

After all compatibility checks pass, the materializer constructs:

- `EvidenceCandidateReference` from candidate, candidate snapshot result, and factual payload digest;
- top-level Evidence ID from the validated identity result;
- source, producer, payload, provenance, eligibility, and diagnostics directly from explicit request values;
- `EvidenceMaterializationRecord` from context plus identity policy ID/version.

It performs no other transformation.

## 16. Candidate reference construction

`EvidenceCandidateReference` is constructed as follows:

| Target field | Explicit origin |
|---|---|
| `candidate_contract_version` | candidate |
| `candidate_snapshot_digest` | validated candidate snapshot result |
| `candidate_source_id` | candidate |
| `candidate_producer_name` | candidate |
| `candidate_producer_version` | candidate |
| `candidate_payload_digest` | explicit factual payload |

All values must also satisfy the accepted-Evidence cross-field invariants.

## 17. Materialization record construction

`EvidenceMaterializationRecord` is constructed as follows:

| Target field | Explicit origin |
|---|---|
| `materializer_id` | context |
| `materializer_version` | context |
| `materialized_at` | context |
| `acceptance_record_id` | context |
| `accepted_by` | context |
| `acceptance_reason` | context |
| `review_record_id` | context |
| `identity_policy_id` | validated identity result |
| `identity_policy_version` | validated identity result |

The materializer does not generate acceptance-record identity. The supplied `acceptance_record_id` remains an explicit governance input until a separate acceptance-record identity contract is implemented.

## 18. Rejection reason codes

The implementation may emit only these reason codes:

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

No free-form reason code is permitted.

## 19. Candidate snapshot implementation scope

The next implementation gate may create exactly:

1. `src/rie/application/evidence_candidate_snapshot.py`;
2. `tests/application/test_evidence_candidate_snapshot.py`.

No existing file modification is authorized.

The implementation may provide:

- immutable `EvidenceCandidateSnapshotInput` or direct exact-candidate input;
- immutable `EvidenceCandidateSnapshotResult`;
- canonical candidate serialization;
- deterministic SHA-256 snapshot digest;
- exact focused tests.

## 20. Candidate snapshot focused-test requirements

Focused tests must cover:

1. exact eighteen-field order;
2. immutable result contract;
3. no defaults;
4. fixed JSON key order;
5. UTF-8 and NFC;
6. tuple and immutable mapping representation;
7. no insignificant whitespace;
8. deterministic repeated result;
9. every candidate field changing the digest;
10. lowercase SHA-256;
11. mutable-value rejection;
12. non-finite float rejection;
13. no filesystem, network, clock, UUID, random, repository, Knowledge, Prompt, or materializer dependency;
14. exactly one focused execution and zero retry.

## 21. Materializer implementation remains deferred

The following must remain absent during PR-024I:

- `src/rie/application/evidence_materializer.py`;
- `tests/application/test_evidence_materializer.py`.

Materializer implementation is authorized only after candidate snapshot implementation, focused result review, commit, and push are independently verified.

## 22. Dependency direction

Allowed candidate snapshot direction:

`	ext
standard library
    -> EvidenceCandidate
    -> candidate snapshot canonicalization
    -> EvidenceCandidateSnapshotResult
`

Future materializer direction:

`	ext
EvidenceCandidate
+ EvidenceCandidateSnapshotResult
+ EvidenceMaterializationSnapshot
+ AcceptedEligibilityResult
+ EvidenceIdentityResult
+ EvidenceMaterializationContext
    -> pure compatibility validation
    -> AcceptedEvidence or rejected result
`

Prohibited:

`	ext
materializer
    -> repository
    -> persistence
    -> parser
    -> filesystem/network
    -> Knowledge
    -> Prompt
`

## 23. Full regression decision

Full regression remains deferred.

PR-024I may run only the exact focused candidate snapshot test file. No materializer or integration tests are authorized.

## 24. Options reviewed

### Option A — Implement materializer using the ambiguous current inputs

**Rejected.** PR-024G proved the inputs incomplete.

### Option B — Expand governance context to carry missing factual values

**Rejected.** This collapses factual snapshot and governance boundaries.

### Option C — Modify EvidenceCandidate

**Rejected.** The Phase 22 contract remains frozen.

### Option D — Define explicit snapshot/request contracts and a deterministic candidate snapshot prerequisite

**Selected.** This preserves candidate immutability and makes every required value and compatibility rule explicit.

### Option E — Start repository implementation

**Rejected.** Repository work still depends on valid accepted Evidence.

## 25. Final decision

# MATERIALIZATION SNAPSHOT INPUT COMPATIBILITY CONTRACT APPROVED; CANDIDATE SNAPSHOT DIGEST IMPLEMENTATION REQUIRED BEFORE MATERIALIZER

The materialization input contract is now explicit, but materializer implementation remains blocked until the candidate snapshot digest prerequisite is implemented and reviewed.

## 26. Exact next gate

**PR-024I - Evidence Candidate Snapshot Digest Contract and Policy Implementation**

Type: **Implementation**

Approved future implementation files:

1. `src/rie/application/evidence_candidate_snapshot.py`;
2. `tests/application/test_evidence_candidate_snapshot.py`.

## 27. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-024G commit/push checkpoint | PASSED |
| Five-commit Phase 24 chain | PASSED |
| Ten-file total Phase 24 scope | PASSED |
| Candidate snapshot policy | APPROVED |
| Candidate snapshot exact inputs | APPROVED |
| Materialization snapshot fields | APPROVED |
| Materialization context fields | APPROVED |
| Materialization request fields | APPROVED |
| Materialization result fields | APPROVED |
| Candidate compatibility rules | APPROVED |
| Eligibility compatibility rules | APPROVED |
| Identity compatibility rules | APPROVED |
| Candidate reference construction | APPROVED |
| Materialization record construction | APPROVED |
| Rejection reason codes | APPROVED |
| Candidate snapshot implementation scope | APPROVED |
| Materializer implementation | DEFERRED |
| Repository/persistence | DEFERRED |
| Knowledge/Prompt | DEFERRED |
| Earlier phases/environment preservation | PASSED |

## 28. Action truth table

| Action | Performed |
|---|---|
| Read-only Phase 24 verification | True |
| PR-024G commit verification | True |
| Exact branch-scope verification | True |
| Contract hash verification | True |
| Static contract inspection | True |
| Candidate snapshot contract defined | True |
| Materialization input contract defined | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Existing file modified | False |
| Dependency/configuration changed | False |
| Asset/parser execution | False |
| Candidate snapshot implemented | False |
| Materializer implemented | False |
| Repository/persistence implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 29. Gate conclusion

PR-024H concludes **MATERIALIZATION SNAPSHOT INPUT COMPATIBILITY CONTRACT APPROVED; CANDIDATE SNAPSHOT DIGEST IMPLEMENTATION REQUIRED BEFORE MATERIALIZER**.

Only `PR-024I - Evidence Candidate Snapshot Digest Contract and Policy Implementation` is authorized after PR-024H commit/push verification.
