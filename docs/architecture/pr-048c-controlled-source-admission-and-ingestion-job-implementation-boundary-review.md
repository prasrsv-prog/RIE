# PR-048C - Controlled Source Admission and Ingestion Job Implementation Boundary Review

## 1. Review identity

Branch: `phase-048-controlled-source-admission-and-job-contract`

Starting checkpoint: `9d1f87d24804da5502a3515fd9ed7c0d65e47bd3`

Review type: architecture-only Gate 3 implementation boundary review.

This review freezes the exact minimum implementation and test change set for the accepted PR-048B runtime contract. It does not write production or test code, execute tests, read a governed source, calculate a governed checksum, write a manifest, invoke a parser, mutate Git, close Gate 3, close Phase 48, or authorize Gate 4.

## 2. Accepted predecessor contracts

Accepted PR-048A boundary commit lineage checkpoint: `9d1f87d24804da5502a3515fd9ed7c0d65e47bd3`

Selected boundary: `minimum_explicit_validated_source_id_to_immutable_auditable_ingestion_job_vertical_slice`

Job contract: `controlled_source_admission_ingestion_job_contract_v1`

Result contract: `controlled_source_admission_result_contract_v1`

PR-048C may choose only the smallest file set required to implement these accepted contracts. It may not redesign them.

## 3. Implementation-boundary decision

Selected implementation shape: four new production modules and four new test modules inside the existing `rie.ingestion` and `tests/ingestion` boundaries.

Existing Gate 2 source models, registry loader, registry validation, eligibility policy, configuration, packaging, dependency versions, root CLI, parser contracts, extraction contracts, Evidence, repositories, and Knowledge remain unchanged.

## 4. Exact production change set

Production path count: `4`

- ADD `src/rie/ingestion/controlled_source_admission_job_contract.py`
- ADD `src/rie/ingestion/controlled_source_admission_manifest_serializer.py`
- ADD `src/rie/ingestion/controlled_source_admission_service.py`
- ADD `src/rie/ingestion/create_controlled_ingestion_job.py`

No existing production file is modified.

## 5. Production-module responsibilities

### `controlled_source_admission_job_contract.py`

- owns contract constants;
- owns frozen request, IngestionJob, issue, and result dataclasses;
- owns exact status and issue enums;
- owns field validation and admitted/rejected invariants;
- owns canonical identity payload bytes and deterministic `job_id`;
- performs no filesystem access, registry load, manifest write, CLI output, parser invocation, Evidence, or Knowledge behavior.

### `controlled_source_admission_manifest_serializer.py`

- converts only a validated IngestionJob into exact manifest bytes;
- preserves the frozen 13-key order;
- owns UTF-8 without BOM, LF-only, one-final-LF serialization;
- owns explicit parent validation and exclusive write-once creation;
- returns deterministic serializer success or failure information used by the service;
- does not load a registry, read a source, calculate a checksum, invoke a parser, or print operator output.

### `controlled_source_admission_service.py`

- owns the exact 18-step PR-048B admission sequence;
- delegates Gate 2 registry loading and validation to existing modules;
- selects exactly one source by exact `source_id`;
- applies the accepted eligibility decisions;
- resolves one explicit source path without scanning;
- validates regular-file and read access boundaries;
- calculates exact read-only SHA-256 in bounded chunks;
- snapshots authority, lifecycle, eligibility, policy, and output values;
- builds and validates one immutable IngestionJob;
- delegates write-once manifest persistence to the serializer;
- returns one deterministic admitted or rejected result;
- contains no parser, Extraction Artifact, Evidence, repository, Knowledge, retry, fallback, network, clock, randomness, or directory discovery behavior.

### `create_controlled_ingestion_job.py`

- owns only the dedicated `python -m rie.ingestion.create_controlled_ingestion_job` operator boundary;
- accepts exactly registry path, source_id, and output JSON path;
- renders the accepted fixed-order admitted or rejected report;
- returns exit code 0, 1, or 2 exactly as frozen by PR-048B;
- suppresses traceback and raw exception text for expected operator failures;
- does not change `src/rie/__main__.py` or global command routing.

## 6. Exact test change set

Test path count: `4`

- ADD `tests/ingestion/test_controlled_source_admission_job_contract.py`
- ADD `tests/ingestion/test_controlled_source_admission_manifest_serializer.py`
- ADD `tests/ingestion/test_controlled_source_admission_service.py`
- ADD `tests/ingestion/test_create_controlled_ingestion_job_cli.py`

No existing test file is modified.

Tests use only temporary directories, temporary synthetic source bytes, and temporary generated registry JSON. No committed real source asset or governed source document is added or read.

## 7. Required acceptance matrix

Contract behavior count: `13`

- request dataclass is frozen
- IngestionJob dataclass is frozen
- issue dataclass is frozen
- result dataclass is frozen
- status enum contains only admitted and rejected
- issue enum contains the exact 13 PR-048B codes
- IngestionJob field order is exactly the frozen 13-field order
- all required strings reject empty values
- job_id requires 64 lowercase hexadecimal characters
- source checksum requires 64 lowercase hexadecimal characters
- contract and policy constants reject mismatches
- admitted and rejected result invariants are enforced
- canonical identity bytes and job_id are deterministic

Serializer behavior count: `8`

- manifest contains exactly 13 keys in contract order
- manifest uses indent 2 and ensure_ascii false
- manifest is UTF-8 without BOM
- manifest is LF-only with exactly one final LF
- parent directory must already exist
- existing output is rejected without overwrite
- exclusive write-once creation is used
- written bytes remain readable and exactly reproducible

Service behavior count: `20`

- request type and empty-value rejection
- wildcard and recursion syntax rejection
- invalid Gate 2 registry rejection before source-byte read
- unknown source_id rejection
- eligible_with_review rejection
- not_eligible rejection
- unknown eligibility rejection
- directory and unknown source-type rejection
- relative source path resolution against registry parent
- absolute source path preservation
- missing source rejection
- non-file source rejection
- unreadable source rejection
- exact read-only SHA-256 calculation
- invalid output-location rejection
- source and output path equality rejection
- exact authority lifecycle and eligibility snapshots
- deterministic job identity construction
- source bytes and filesystem metadata remain unchanged
- no parser or Gate 4 invocation

CLI behavior count: `7`

- admitted flow exits 0
- deterministic rejection exits 1
- usage error exits 2
- admitted report field order is exact
- rejected report field order is exact
- no traceback or raw exception text is printed
- module runs without root CLI routing change

Total required behavior count: `48`

Behavior count is a coverage floor, not permission to broaden production scope.

## 8. Dependency direction

```text
existing Gate 2 official_source models / loader / validation / eligibility policy
                              |
                              v
controlled_source_admission_job_contract
                              |
                              v
controlled_source_admission_manifest_serializer
                              ^
                              |
controlled_source_admission_service
                              ^
                              |
create_controlled_ingestion_job
```

The contract module is pure and does not import the service, serializer, or CLI. The serializer depends on the contract only. The service depends on the accepted Gate 2 modules, contract, and serializer. The CLI depends on the service and contract result types only.

No new generalized interface, repository, adapter hierarchy, plugin system, factory, dependency injection container, event bus, or future Gate 4 abstraction is authorized.

## 9. Protected unchanged paths

- `configs/official_source_registry.json`
- `pyproject.toml`
- `src/official_source/official_source.py`
- `src/official_source/official_source_registry_loader.py`
- `src/official_source/official_source_registry_validation.py`
- `src/official_source/official_source_evidence_eligibility_policy.py`
- `src/official_source/official_source_evidence_eligibility_gate.py`
- `src/official_source/official_source_evidence_workflow_gate.py`
- `src/official_source/official_source_evidence_workflow_preflight.py`
- `src/rie/__main__.py`
- `src/rie/application/evidence_candidate.py`
- `src/rie/ingestion/__init__.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py`
- `src/rie/extraction/text_asset_extraction_report_serializer.py`

A later implementation may prove that an exact protected path must change. Such proof requires a fresh architecture correction review before modification; it may not be inferred during implementation.

## 10. Test-first implementation sequence

Sequence step count: `11`

1. write failing contract tests
2. implement frozen contract and identity policy
3. write failing manifest serializer tests
4. implement deterministic manifest bytes and exclusive write
5. write failing admission service tests
6. implement exact fail-fast admission service
7. write failing CLI tests
8. implement the dedicated module CLI
9. run targeted PR-048D tests
10. run the full existing test suite
11. run diff and scope verification

The implementation must not combine architecture correction, real-source execution, Gate 4 parser work, merge, tag, or phase closure with the contract implementation.

## 11. Test execution boundary

The implementation review requires two test levels after the eight planned files exist:

1. targeted tests for the four new test modules;
2. the full existing test suite.

Targeted tests must pass before the full suite. Full-suite execution must preserve all prior accepted behaviors. The accepted `.pytest_cache` permission warning may be filtered, but no new warning or collection error is accepted automatically.

No real official-source file, parser, network, external generator, OCR, PDF extraction, Evidence repository, or Knowledge workflow is required by these tests.

## 12. Implementation scope invariants

- exact planned path count is 8;
- exact production path count is 4;
- exact test path count is 4;
- all eight paths are additions;
- existing tracked paths modified is 0;
- configuration paths modified is 0;
- dependency declarations modified is 0;
- root CLI paths modified is 0;
- committed fixture or real-source assets added is 0;
- parser invocation in tests is 0;
- Gate 4 contract or implementation paths changed is 0.

Any deviation fails the selected implementation boundary and requires a fresh correction review before further work.

## 13. Required implementation report evidence

The eventual implementation report must include:

- exact starting checkpoint and branch refs;
- exact eight-path scope and change types;
- complete snapshots and SHA-256 fingerprints of all eight implementation paths;
- targeted test command, collected count, passed count, and output;
- full-suite command, collected count, passed count, and output;
- exact contract constants, field order, issue code order, and CLI exit codes;
- proof that tests use only synthetic temporary source bytes;
- proof that no parser, Gate 4, real source, network, retry, fallback, Evidence, or Knowledge behavior ran;
- clean final unstaged state with only the exact eight implementation paths changed;
- explicit statement that Gate 3 remains open pending runtime and operator verification.

## 14. Deferred subjects

- real official-source registry population or amendment;
- real governed-source admission execution;
- persisted production manifest location policy beyond one explicit operator path;
- Gate 4 parser handoff implementation;
- structural metadata or page text extraction;
- Extraction Artifact, Evidence, repository, Knowledge, Prompt Candidate, release, merge, tag, and phase closure.

## 15. Repository and execution scope

PR-048C adds exactly one architecture document: `docs/architecture/pr-048c-controlled-source-admission-and-ingestion-job-implementation-boundary-review.md`.

Production files modified: `0`.

Test files modified: `0`.

Configuration files modified: `0`.

Tests run: `0`.

Project interpreter processes: `0`.

Governed source bytes read: `0`.

Git mutation commands: `0`.

## 16. Final decision

# GATE 3 IMPLEMENTATION BOUNDARY SELECTED

Exact planned implementation path count: `8`

Next eligible implementation subject after independent PR-048C acceptance: `controlled_source_admission_and_ingestion_job_contract_implementation`

Gate 3 remains OPEN.

Phase 48 implementation remains unauthorized inside PR-048C.

Independent PR-048C acceptance makes only the exact eight-path PR-048D implementation eligible; it does not start that implementation automatically.

Gate 4 remains unauthorized.

PR-048C does not implement the selected boundary, create an ingestion job, write a manifest, invoke a parser, close Gate 3, or close Phase 48.
