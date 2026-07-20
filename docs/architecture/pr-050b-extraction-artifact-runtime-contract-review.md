# PR-050B - Extraction Artifact Runtime Contract Review

## 1. Review identity

Gate: `Gate 5 - Extraction Artifact Contract`

Phase: `Phase 50 - Extraction Artifact Contract`

Selected planning boundary:

`single_completed_pdf_ingestion_result_versioned_round_trip_safe_extraction_artifact_boundary`

This review freezes the field-level runtime contract, canonical byte representation, artifact identity algorithm, strict parsing behavior, and deterministic public issue classes. It does not choose implementation paths or authorize implementation.

The structural metadata result foundation is verified by exact Git-blob identity between the Phase 50 HEAD and the published main checkpoint, then validated by its exact required source fragments. Existing historical line-ending or final-LF characteristics are recorded but are not rewritten or treated as a Phase 50 defect.

## 2. Contract identities

Artifact contract version: `extraction_artifact_contract_v1`.

Canonical format version: `extraction_artifact_canonical_json_v1`.

Accepted upstream result contract: `pdf_ingestion_orchestrator_result_contract_v1`.

Artifact identity algorithm: `sha256`.

Only one successfully completed `PdfIngestionOrchestratorResult` may be converted. Failed results and arbitrary look-alike objects are rejected.

## 3. Exact top-level artifact field order
1. `contract_version`
2. `artifact_id`
3. `upstream_contract_version`
4. `upstream_status`
5. `job_id`
6. `source_id`
7. `source_path`
8. `source_checksum`
9. `structural_metadata`
10. `page_extractions`
11. `execution_report_location`
12. `cleanup_completed`

The artifact contains no issue field because only a completed Gate 4 result is accepted.

## 4. Exact artifact identity payload

`artifact_id` is exactly 64 lower-case hexadecimal characters produced by SHA-256 over canonical JSON bytes containing these fields in order, with `artifact_id` excluded:
1. `contract_version`
2. `upstream_contract_version`
3. `upstream_status`
4. `job_id`
5. `source_id`
6. `source_path`
7. `source_checksum`
8. `structural_metadata`
9. `page_extractions`
10. `execution_report_location`
11. `cleanup_completed`

The identity payload uses the same nested canonical forms and exactly one final LF as the full artifact representation.

## 5. Exact structural metadata field order
1. `allowed`
2. `reason`
3. `fixture_id`
4. `source_label`
5. `fixture_path`
6. `fixture_type`
7. `inspection_mode`
8. `inspection_status`
9. `encrypted`
10. `page_count`
11. `inspected_page_count`
12. `page_details_truncated`
13. `page_details`
14. `max_inspected_pages`
15. `inspection_error`
16. `evidence_allowed`
17. `notes`

All values are copied exactly from the accepted Gate 4 structural result. The artifact does not rerun inspection or reinterpret metadata.

## 6. Exact structural page field order
1. `page_index`
2. `width_points`
3. `height_points`
4. `rotation_degrees`
5. `inspection_status`

Structural page order remains the contiguous zero-based order accepted by Gate 4.

## 7. Exact page extraction field order
1. `source_path`
2. `size_bytes`
3. `page_number`
4. `extraction_index`
5. `extraction_method`
6. `content`
7. `warnings`

Page extraction order, page numbers, extraction indices, Unicode content, empty content, and warning order must remain unchanged.

## 8. Top-level invariants

- `contract_version` must equal `extraction_artifact_contract_v1`;
- `upstream_contract_version` must equal `pdf_ingestion_orchestrator_result_contract_v1`;
- `upstream_status` must equal `completed`;
- `job_id`, `source_id`, `source_path`, `source_checksum`, and `execution_report_location` must be non-empty strings copied exactly from Gate 4;
- `source_checksum` and `artifact_id` must use exact lower-case SHA-256 shape;
- `structural_metadata.allowed` must be true;
- `structural_metadata.encrypted` and `structural_metadata.evidence_allowed` must be false;
- structural inspection status must be `inspected` or `bounded`;
- structural page count must equal page extraction count;
- `cleanup_completed` must be true;
- no value may be derived from clock time, randomness, process identity, environment variables, or the current host.

## 9. Canonical serialization rules
- UTF-8 without BOM;
- top-level JSON object;
- ensure_ascii false;
- compact separators comma and colon;
- finite JSON numbers only;
- exact frozen field order at every object level;
- collection order preserved;
- exactly one final LF;
- no CR bytes;
- no clock, random, environment, or host-generated fields;

The canonical representation is compact JSON followed by exactly one LF. Serialization is an in-memory bytes operation only.

## 10. Strict deserialization rules
- bytes input only;
- strict UTF-8 decoding;
- BOM rejected;
- duplicate fields rejected at every object level;
- missing fields rejected;
- extra fields rejected;
- unsupported versions rejected;
- invalid enum, scalar, numeric, and collection values rejected;
- artifact_id recomputed and compared;
- canonical bytes regenerated and compared byte-for-byte;

A byte input is accepted only if parsing, value validation, identity verification, and exact canonical byte regeneration all succeed.

## 11. Public issue codes
1. `invalid_upstream_result`
2. `invalid_utf8`
3. `invalid_json`
4. `duplicate_field`
5. `missing_field`
6. `extra_field`
7. `unsupported_version`
8. `invalid_value`
9. `artifact_id_mismatch`
10. `non_canonical_bytes`

Only the first deterministic validation failure is exposed.

## 12. Round-trip contract

- accepted Gate 4 result -> artifact -> canonical bytes is deterministic;
- artifact -> canonical bytes -> artifact preserves exact values;
- canonical bytes -> artifact -> canonical bytes is byte-identical;
- repeated construction from the same accepted Gate 4 result produces the same `artifact_id` and identical bytes.

## 13. Publication decision

Gate 5 does not publish or manage an artifact file. No output location, extension, write-once file operation, repository, revision store, audit history, or discovery surface is part of this runtime contract.

The canonical bytes are the versioned Extraction Artifact representation. Persistence belongs to a later explicitly selected boundary.

## 14. Explicit exclusions

The runtime contract does not:

- reread, parse, OCR, render, mutate, rename, replace, or delete the source PDF;
- rerun Gate 3 admission or Gate 4 ingestion;
- accept failed Gate 4 results, multiple results, directories, or wildcards;
- normalize, trim, summarize, infer, classify, or semantically interpret text;
- construct Evidence, Knowledge, Prompt Candidate, or Final Prompt;

- add CLI, package entry points, UI, API, retry, fallback, file publication, or repository behavior;
- invoke Gate 6.

## 15. Decision

Decision:

`EXTRACTION_ARTIFACT_RUNTIME_CONTRACT_SELECTED`

Status after this review:

- Gate 5 minimum closure boundary selected: `True`;
- Gate 5 runtime contract selected: `True`;
- Gate 5 implementation boundary selected: `False`;
- Gate 5 implementation authorized: `False`;
- Gate 5 implementation started: `False`;
- Gate 5 closed: `False`;
- Gate 6 invoked: `False`.

Next review: `PR-050C - extraction_artifact_implementation_boundary_review`.
