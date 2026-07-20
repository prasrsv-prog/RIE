# PR-051B - Evidence Materialization Runtime Contract Review

## 1. Contract identity

Gate: `Gate 6 - Evidence Materialization`

Phase: `Phase 51 - Evidence Materialization`

Selected minimum boundary: `single_valid_extraction_artifact_explicitly_eligible_source_page_scoped_exact_traceable_evidence_collection_boundary`

Result contract: `evidence_materialization_result_contract_v1`

Collection contract: `evidence_collection_contract_v1`

Evidence contract: `traceable_evidence_contract_v1`

Eligibility snapshot contract: `evidence_eligibility_snapshot_contract_v1`

## 2. Authoritative inputs

The materializer accepts exactly two explicit in-memory inputs:

1. one exact `ExtractionArtifact` using `extraction_artifact_contract_v1`;
2. one exact Gate 6 eligibility snapshot using `evidence_eligibility_snapshot_contract_v1`.

The materializer must not read the source file, inspect the registry, rerun eligibility policy, rerun Gate 3 through Gate 5, query a repository, use the current clock, or generate random values.

## 3. Eligibility snapshot contract

Exact field order (`15` fields):
- `contract_version`
- `source_id`
- `source_path`
- `source_checksum`
- `source_type`
- `document_classification`
- `authority_status`
- `lifecycle_status`
- `evidence_eligibility`
- `evidence_collection_allowed`
- `requires_review`
- `reason`
- `policy_id`
- `policy_version`
- `registry_version`

A materializable snapshot requires `evidence_eligibility == "eligible"`, `evidence_collection_allowed is True`, and `requires_review is False`.

Its `source_id`, `source_path`, and lowercase SHA-256 `source_checksum` must exactly match the Extraction Artifact. Policy ID, policy version, registry version, source classification, authority, lifecycle, and reason are explicit preserved values.

Eligibility canonicalization: `evidence_eligibility_snapshot_json_v1` using exact field order, compact JSON, UTF-8, no BOM, no CR, and exactly one final LF.

The eligibility snapshot digest is lowercase SHA-256 of those canonical bytes.

Existing `EvidenceWorkflowPreflightResult` is not the authoritative Gate 6 eligibility input because it lacks source path, source checksum, policy version, and registry version. Gate 6 does not silently adapt or enrich that legacy value.

## 4. Evidence provenance contract

Exact field order (`13` fields):
- `artifact_contract_version`
- `artifact_id`
- `upstream_contract_version`
- `job_id`
- `source_id`
- `source_path`
- `source_checksum`
- `page_index`
- `page_number`
- `extraction_index`
- `extraction_method`
- `extraction_status`
- `execution_report_location`

`page_index` equals the artifact extraction index, `page_number` preserves the artifact one-based page number, and `extraction_status` exactly copies the completed artifact upstream status.

## 5. Traceable Evidence contract

Exact field order (`8` fields):
- `contract_version`
- `evidence_id`
- `content_type`
- `content`
- `content_digest`
- `warnings`
- `provenance`
- `eligibility_snapshot_digest`

The only Gate 6 content type is `page_text_utf8`.

Each artifact page extraction produces exactly one Evidence item in the same order, including when `content` is an empty string. This preserves a one-to-one page outcome and does not silently discard warnings.

Content is copied byte-for-byte as a Python string value with no trimming, normalization, summarization, inference, semantic correction, paraphrase, or enrichment.

`content_digest` is lowercase SHA-256 of `content.encode("utf-8")`. Warning order and duplicates are preserved exactly.

Evidence identity payload order excludes `evidence_id` and contains exactly `7` fields:
- `contract_version`
- `content_type`
- `content`
- `content_digest`
- `warnings`
- `provenance`
- `eligibility_snapshot_digest`

Identity canonicalization: `traceable_evidence_identity_json_v1` using compact JSON, UTF-8, no BOM, no CR, and exactly one final LF.

`evidence_id` equals `evm1_` plus the lowercase SHA-256 digest of the canonical Evidence identity bytes.

## 6. EvidenceCollection contract

Exact field order (`11` fields):
- `contract_version`
- `collection_id`
- `artifact_contract_version`
- `artifact_id`
- `upstream_contract_version`
- `job_id`
- `source_id`
- `source_path`
- `source_checksum`
- `eligibility_snapshot`
- `evidence_items`

Evidence items are immutable and retain artifact page order. The collection is empty only when the valid artifact contains zero page extractions.

Collection identity payload order excludes `collection_id` and contains exactly `10` fields:
- `contract_version`
- `artifact_contract_version`
- `artifact_id`
- `upstream_contract_version`
- `job_id`
- `source_id`
- `source_path`
- `source_checksum`
- `eligibility_snapshot`
- `evidence_items`

Collection identity canonicalization: `evidence_collection_identity_json_v1`.

`collection_id` equals `evc1_` plus the lowercase SHA-256 digest of the canonical collection identity bytes.

## 7. Result envelope

Exact result field order (`6` fields):
- `contract_version`
- `status`
- `artifact_id`
- `source_id`
- `collection`
- `issue`

Status values are exactly `materialized` and `rejected`.

A materialized result contains one collection and no issue. A rejected result contains no collection and exactly one deterministic issue. Partial Evidence is prohibited.

Issue field order (`2` fields): `code`, `message`.

Exact issue-code order (`11` codes):
- `invalid_artifact`
- `invalid_eligibility_snapshot`
- `source_id_mismatch`
- `source_path_mismatch`
- `source_checksum_mismatch`
- `source_not_eligible`
- `source_requires_review`
- `unsupported_version`
- `invalid_value`
- `evidence_id_mismatch`
- `collection_id_mismatch`

Every issue code has one fixed public message. Direct invalid contract construction and service rejection must use the same code-to-message mapping.

## 8. Determinism and validation

The runtime is pure and deterministic. Repeated materialization with equal artifact and eligibility values produces equal Evidence values, equal Evidence IDs, and an equal collection ID.

Canonical JSON uses exact declared order, `ensure_ascii=False`, compact separators, finite numeric values only, UTF-8 without BOM, no CR, and exactly one final LF.

All public values are frozen and deeply immutable. Lists, dictionaries, sets, mutable warning collections, extra fields, missing fields, unsupported versions, invalid SHA-256 values, and mismatched derived IDs fail closed.

## 9. Compatibility decision

The existing EvidenceCandidate, candidate snapshot, AcceptedEvidence, legacy EvidenceIdentity, and accepted-Evidence materializer remain committed compatibility foundations but are not promoted as the authoritative Gate 6 runtime contract.

Gate 6 must not import those legacy Evidence domain or materializer modules in its authoritative runtime implementation. No adapter, migration, replacement, or deletion is selected by PR-051B.

The authoritative Gate 6 runtime may coexist in a separate namespace selected later by PR-051C.

## 10. Excluded behavior

The contract excludes Evidence persistence, repository lookup, save/load/list/export, duplicate detection, idempotency records, source revision history, and audit storage. Those remain Gate 7.

It also excludes file publication, source reading, parsing, extraction, Knowledge construction, Prompt Candidate construction, CLI, API, network, clock, random identity, retries, fallback, and background processing.

## 11. Decision

Decision:

`EVIDENCE_MATERIALIZATION_RUNTIME_CONTRACT_SELECTED`

Status after this review:

- Gate 6 active closure target: `True`;

- Gate 6 minimum closure boundary selected: `True`;

- Gate 6 runtime contract selected: `True`;

- Gate 6 implementation boundary selected: `False`;

- Gate 6 implementation authorized: `False`;

- Gate 6 implementation started: `False`;

- Gate 6 closed: `False`;

- Gate 7 invoked: `False`.

The next safe review is PR-051C - Evidence Materialization Implementation Boundary Review.
