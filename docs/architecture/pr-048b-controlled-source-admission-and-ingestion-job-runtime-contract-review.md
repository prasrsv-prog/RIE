# PR-048B - Controlled Source Admission and Ingestion Job Runtime Contract Review

## 1. Review identity

Branch: `phase-048-controlled-source-admission-and-job-contract`

Starting checkpoint: `533f634ec40611336fac87406567a7b6ef7cc819`

Review type: architecture-only Gate 3 runtime contract review.

This review freezes the minimum contract selected by PR-048A. It does not implement production code, write an ingestion job manifest, read a governed source document, calculate a governed checksum, invoke a parser, run tests, mutate Git, close Gate 3, close Phase 48, or authorize Gate 4.

## 2. Accepted predecessor boundary

Accepted PR-048A commit: `533f634ec40611336fac87406567a7b6ef7cc819`

Selected boundary: `minimum_explicit_validated_source_id_to_immutable_auditable_ingestion_job_vertical_slice`

The contract begins with one valid Gate 2 registry result and one explicit `source_id`. It ends with one immutable validated IngestionJob and one write-once deterministic JSON manifest before parser execution.

## 3. Runtime contract family

IngestionJob contract version: `controlled_source_admission_ingestion_job_contract_v1`

Admission result contract version: `controlled_source_admission_result_contract_v1`

Execution policy id: `controlled_source_admission`

Execution policy version: `1.0.0`

Checksum algorithm: `sha256`

All contract values are immutable. Expected operational failures return deterministic result issues rather than raw exception text.

## 4. Operator request contract

The minimum immutable request contains exactly:

- `registry_path: str | Path` - explicit Gate 2 registry JSON path;
- `source_id: str` - one non-empty exact identifier;
- `output_location: str | Path` - one explicit JSON manifest file path.

The request does not accept a directory, glob, wildcard, recursion flag, source list, retry count, fallback policy, parser option, network location, clock value, random seed, Evidence target, or Knowledge target.

## 5. Admission sequence

The implementation must execute this exact fail-fast sequence:


1. validate request types and non-empty values;
2. reject wildcard or recursive input syntax;
3. run the accepted Gate 2 registry validation contract;
4. reject an invalid registry without reading referenced source bytes;
5. select exactly one source by exact `source_id`;
6. reject an unknown `source_id`;
7. evaluate explicit evidence eligibility;
8. reject `eligible_with_review`, `not_eligible`, and `unknown`;
9. reject `directory` and `unknown` source types;
10. resolve the explicit source path without scanning;
11. reject missing, non-file, or unreadable source paths;
12. calculate SHA-256 from exact source bytes through read-only streaming;
13. validate the explicit output location and write-once collision rule;
14. snapshot source and policy values;
15. derive deterministic `job_id`;
16. construct and validate the immutable IngestionJob;
17. serialize and exclusively create the deterministic manifest;
18. return the admitted result.

No parser or Gate 4 service may run at any step.

## 6. Immutable IngestionJob contract

The IngestionJob is a frozen dataclass with no defaults and fields in this exact order:

1. `contract_version: str`
2. `job_id: str`
3. `source_id: str`
4. `source_path: str`
5. `expected_source_type: str`
6. `authority_snapshot: str`
7. `lifecycle_snapshot: str`
8. `eligibility_snapshot: str`
9. `source_checksum_algorithm: str`
10. `source_checksum: str`
11. `execution_policy_id: str`
12. `execution_policy_version: str`
13. `output_location: str`

Field count: `13`

Field rules:

- `contract_version` must equal `controlled_source_admission_ingestion_job_contract_v1`;
- all string fields must be non-empty;
- `job_id` must be exactly 64 lowercase hexadecimal characters;
- `source_path` and `output_location` store canonical absolute paths used by the execution;
- `expected_source_type`, authority, lifecycle, and eligibility snapshots store enum `.value` strings;
- `source_checksum_algorithm` must equal `sha256`;
- `source_checksum` must be exactly 64 lowercase hexadecimal characters;
- `execution_policy_id` must equal `controlled_source_admission`;
- `execution_policy_version` must equal `1.0.0`;
- `source_path` and `output_location` must differ;
- mutation after construction is prohibited.

## 7. Deterministic job identity

The `job_id` is the lowercase SHA-256 hexadecimal digest of a canonical identity payload.

The identity payload contains these fields in fixed order and excludes `job_id`:

- `contract_version`
- `source_id`
- `source_path`
- `expected_source_type`
- `authority_snapshot`
- `lifecycle_snapshot`
- `eligibility_snapshot`
- `source_checksum_algorithm`
- `source_checksum`
- `execution_policy_id`
- `execution_policy_version`
- `output_location`

Canonical identity serialization rules:

- one JSON object with the fixed field order above;
- UTF-8 encoding without BOM;
- `ensure_ascii=False`;
- compact separators `,` and `:`;
- no whitespace, final newline, clock, random value, environment field, or unordered collection;
- SHA-256 over the exact canonical UTF-8 bytes.

The same canonical source path, exact source bytes, snapshots, execution policy, and output location therefore produce the same job identity.

## 8. Source path, expected type, and checksum

A relative registry `source_path` is resolved against the directory containing the explicit registry file. An absolute path remains absolute. The resolved path is canonicalized and stored in the job.

Expected-type validation is intentionally narrow: the Gate 2 `SourceType` must be a supported non-container enum value, and the resolved source must be a regular file. PR-048B does not inspect magic bytes, infer type, or invoke a parser. Gate 4 owns PDF-content validation.

The checksum is SHA-256 over the exact source file bytes, read in bounded chunks through read-only access. No newline conversion, decoding, normalization, metadata mutation, lock removal, temporary copy, or source rewrite is permitted.

## 9. Authority, lifecycle, and eligibility snapshots

The job snapshots `authority_status.value`, `lifecycle_status.value`, and `evidence_eligibility.value` from the selected immutable OfficialSource.

Eligibility admission is exact:

- `eligible` is admitted;
- `eligible_with_review` is rejected as `source_review_required`;
- `not_eligible` is rejected as `source_ineligible`;
- `unknown` is rejected as `source_ineligible`.

PR-048B does not invent additional authority or lifecycle inference. Those values are preserved as audit snapshots. Locked source status never authorizes mutation.

## 10. Output location and manifest contract

The operator supplies one explicit `.json` output file path.

Output rules:

- wildcard and recursive syntax is rejected;
- the parent directory must already exist and be a directory;
- the output path must not be the source path;
- an existing output path is rejected as `output_collision`;
- no directory is created automatically;
- no existing file is overwritten, replaced, truncated, or merged;
- manifest creation uses exclusive write-once semantics.

The manifest contains exactly the 13 IngestionJob fields in the same order.

Manifest serialization is `json.dumps(..., indent=2, ensure_ascii=False)` followed by exactly one LF, encoded as UTF-8 without BOM. Keys are emitted in frozen contract order. The manifest contains no timestamps, parser result, Evidence, Knowledge, raw source content, or exception details.

A successful admission result may be returned only after the exact manifest bytes have been written and remain readable.

## 11. Admission result contract

The result contract consists of:

- `ControlledSourceAdmissionStatus` with `admitted` and `rejected`;
- frozen `ControlledSourceAdmissionIssue`;
- frozen `ControlledSourceAdmissionResult`.

The issue fields are `code`, `message`, and optional `upstream_issue_code`.

The result fields are `contract_version`, `status`, `job`, and `issue`.

Result invariants:

- `contract_version` must equal `controlled_source_admission_result_contract_v1`;
- admitted result contains one IngestionJob and no issue;
- rejected result contains no job and exactly one issue;
- validation is fail-fast;
- messages are deterministic and do not expose raw exception text;
- Gate 2 issue code is preserved as `upstream_issue_code` when registry validation rejects.

## 12. Admission issue codes

Issue code count: `13`

- `registry_invalid`
- `source_id_unknown`
- `source_review_required`
- `source_ineligible`
- `source_type_unsupported`
- `source_missing`
- `source_not_file`
- `source_unreadable`
- `checksum_failed`
- `output_location_invalid`
- `output_collision`
- `manifest_write_failed`
- `job_validation_failed`

These are Gate 3 admission and manifest failures. They are not parser failures and do not create a Gate 4 execution result.

## 13. Operator command and exit codes

The minimum operator command is:

```text
python -m rie.ingestion.create_controlled_ingestion_job <registry_json_path> <source_id> <output_json_path>
```

Exit codes:

- `0` - admitted and manifest written;
- `1` - deterministic admission rejection;
- `2` - command-line usage error.

Operator output is one deterministic human-readable report. An admitted report prints contract version, status, job_id, source_id, source_path, expected source type, checksum algorithm, checksum, execution policy, output location, and manifest-written status in fixed order. A rejected report prints contract version, status, issue code, optional upstream issue code, and deterministic issue message in fixed order.

The CLI does not print raw source content, traceback, arbitrary exception text, Evidence, Knowledge, parser output, or directory inventory.

## 14. Gate 3 and Gate 4 boundary

Gate 3 owns registry validation delegation, exact source selection, eligibility rejection, explicit path validation, expected-type admission, read-only checksum, immutable job validation, output collision control, manifest persistence, and deterministic admission reporting.

Gate 4 begins only after receiving an admitted IngestionJob whose manifest already exists. Gate 4 must not rescan a registry, select another source, recalculate identity policy, overwrite the Gate 3 manifest, or convert a Gate 3 rejection into parser execution.

PDF parsing, encrypted-PDF handling, structural metadata, page text extraction, parser failure, extraction failure, temporary parser asset cleanup, and extraction execution reporting remain Gate 4 subjects.

## 15. Required implementation acceptance

The eventual implementation must prove at minimum:

- frozen request, issue, result, and IngestionJob contracts;
- exact 13-field order and validation;
- exact 13-code issue enum;
- one explicit valid source creates one job and one manifest;
- repeated identical governed inputs reproduce job_id and manifest bytes when no collision exists;
- unknown, review-required, ineligible, missing, non-file, unreadable, unsupported-type, and collision cases reject before parser execution;
- checksum matches independent SHA-256 of exact source bytes;
- source bytes and metadata remain unchanged;
- manifest is UTF-8 without BOM, LF-only, one final LF, fixed key order, and write-once;
- operator output and exit codes are exact and reproducible;
- no directory discovery, wildcard expansion, recursion, retry, fallback, network, clock, randomness, parser, Extraction Artifact, Evidence, or Knowledge behavior occurs.

## 16. Reuse and protected boundaries

The implementation may reuse only narrow accepted behavior:

- Gate 2 registry validation and ordered OfficialSource results;
- existing immutable OfficialSource enums and fields;
- existing explicit eligibility-policy semantics;
- existing lowercase hexadecimal checksum validation style;
- existing deterministic JSON serialization style where compatible.

Existing Evidence workflow gates are evidence of explicit eligibility handling, but their Evidence-specific result names are not the Gate 3 IngestionJob contract and must not be broadened or repurposed silently.

Protected unchanged subjects include Gate 2 registry semantics, EvidenceCandidate, Evidence materialization, repositories, parser implementations, extraction contracts, Knowledge contracts, root CLI routing, packaging, dependency versions, and real official-source population unless a later implementation-boundary review proves an exact required change.

## 17. Deferred subjects

- exact implementation file paths and change set;
- implementation code and tests;
- real source population and real governed-source execution;
- Gate 4 orchestration and failure mapping;
- Extraction Artifact, Evidence, repository, Knowledge, Prompt Candidate, packaging, and release behavior.

## 18. Repository and execution scope

PR-048B adds exactly one architecture document: `docs/architecture/pr-048b-controlled-source-admission-and-ingestion-job-runtime-contract-review.md`.

Production files modified: `0`.

Test files modified: `0`.

Configuration files modified: `0`.

Tests run: `0`.

Project interpreter processes: `0`.

Governed source bytes read: `0`.

Git mutation commands: `0`.

## 19. Final decision

# GATE 3 RUNTIME CONTRACT SELECTED

Job contract: `controlled_source_admission_ingestion_job_contract_v1`

Result contract: `controlled_source_admission_result_contract_v1`

Next eligible architecture subject after independent PR-048B acceptance: `controlled_source_admission_and_ingestion_job_implementation_boundary_review`

Gate 3 remains OPEN.

Phase 48 implementation remains unauthorized.

Gate 4 remains unauthorized.

PR-048B does not implement the selected contract, create an ingestion job, write a manifest, invoke a parser, close Gate 3, or close Phase 48.
