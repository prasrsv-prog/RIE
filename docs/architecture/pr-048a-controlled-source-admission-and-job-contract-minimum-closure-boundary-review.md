# PR-048A - Controlled Source Admission and Job Contract Minimum Closure Boundary Review

## 1. Review identity

Branch: `phase-048-controlled-source-admission-and-job-contract`

Starting checkpoint: `48e907ac3a79c0a39247cadffafc99fd2945eafc`

Review type: architecture-only Gate 3 minimum closure boundary review.

This review does not implement IngestionJob, calculate a real source checksum, read a governed source document, invoke a parser, write a job manifest, modify production or test code, run tests, mutate Git, close Gate 3, close Phase 48, or authorize Gate 4.

## 2. Governing strategy and dependency

The frozen strategy remains `Runtime spine + targeted semantics`.

Gate 2 is formally closed through the verified official Phase 47 tag. Gate 3 is therefore the next valid runtime-spine subject.

Official predecessor tag: `v0.47.0-rcis-official-source-registry-runtime-phase`

Official predecessor tag object: `5494dccc0a2661dc68aea81a41f24cd41c2df1b6`

Official predecessor tag target: `48e907ac3a79c0a39247cadffafc99fd2945eafc`

## 3. Authoritative Gate 3 requirements

Required outcome: immutable controlled ingestion job.

Objective: convert one explicitly selected `source_id` into an immutable, auditable ingestion job carrying authority, lifecycle, eligibility, and checksum snapshots.

Required deliverables:

- IngestionJob
- job_id
- source_id
- source_path
- expected source type
- authority snapshot
- lifecycle snapshot
- eligibility snapshot
- source checksum
- execution policy
- output location

Required deliverable count: `11`

Boundaries:

- one job selects one explicit source
- no automatic folder discovery
- no wildcard or recursive processing
- ineligible source is rejected
- locked source is not modified

Boundary count: `5`

Operational Definition of Done:

- one source_id produces one controlled job
- job is validated before parser execution
- job stores authority snapshot
- job remains auditable after completion

Definition of Done count: `4`

## 4. Bounded reusable-foundation inventory

A bounded read-only scan of committed `src`, `tests`, `configs`, `pyproject.toml`, and `README.md` was used only to locate reusable foundation. File or token presence does not prove Gate 3 closure.

Tracked inventory count: `312`

Tracked inventory SHA-256: `fd1048f361a3bed4d2a8e0e74eb5e2b747aa05601786e905698c46189db78e8c`

Relevant path count: `162`

Relevant path inventory SHA-256: `9c8c8053b8eefb6d2c13f8535d528c242478a00c4b1a438c1f53b5c1bc302581`

Capability match count: `530`

Capability match inventory SHA-256: `2ff69978a4a2531944321d75a1697bd3a5095417834e654f95ab3bd4634272d8`

Relevant committed files with CR bytes: `0`

Relevant committed files with leading BOM: `10`

Relevant committed files without exactly one final LF: `13`

Pre-existing committed foundation byte formats are preserved as evidence and are not normalized by this architecture-only review.

Relevant committed paths:

- `configs/official_source_registry.json`
- `src/collection/pdf_text_extraction_evidence_collection.py`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py`
- `src/collection/pdf_text_extraction_evidence_collector.py`
- `src/collection/text_extraction_evidence_artifact_inspector.py`
- `src/collection/text_extraction_evidence_collection.py`
- `src/collection/text_extraction_evidence_collection_serializer.py`
- `src/collection/text_extraction_evidence_collector.py`
- `src/evidence/pdf_text_extraction_evidence.py`
- `src/evidence/pdf_text_extraction_evidence_artifact_inspector.py`
- `src/evidence/pdf_text_extraction_evidence_builder.py`
- `src/evidence/text_extraction_evidence.py`
- `src/evidence/text_extraction_evidence_builder.py`
- `src/knowledge/text_knowledge_artifact_inspector.py`
- `src/official_source/official_source.py`
- `src/official_source/official_source_evidence_eligibility_gate.py`
- `src/official_source/official_source_evidence_eligibility_policy.py`
- `src/official_source/official_source_evidence_workflow_gate.py`
- `src/official_source/official_source_evidence_workflow_preflight.py`
- `src/official_source/official_source_registry_loader.py`
- `src/official_source/official_source_registry_validation.py`
- `src/rie/application/evidence_candidate.py`
- `src/rie/application/evidence_candidate_snapshot.py`
- `src/rie/application/evidence_materializer.py`
- `src/rie/application/governed_knowledge_constructor.py`
- `src/rie/application/knowledge_promotion_executor.py`
- `src/rie/application/metadata_extractor.py`
- `src/rie/domain/accepted_evidence.py`
- `src/rie/domain/knowledge_promotion_execution.py`
- `src/rie/extraction/__init__.py`
- `src/rie/extraction/export_pdf_text_evidence.py`
- `src/rie/extraction/export_pdf_text_extractions.py`
- `src/rie/extraction/export_text_extraction_evidence.py`
- `src/rie/extraction/extract_text_assets.py`
- `src/rie/extraction/inspect_pdf_text_evidence.py`
- `src/rie/extraction/inspect_pdf_text_extractions.py`
- `src/rie/extraction/inspect_text_extraction_evidence.py`
- `src/rie/extraction/pdf_page_text_extraction.py`
- `src/rie/extraction/pdf_text_extraction_artifact_inspector.py`
- `src/rie/extraction/pdf_text_extraction_report.py`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py`
- `src/rie/extraction/pdf_text_extractor.py`
- `src/rie/extraction/text_asset_extraction.py`
- `src/rie/extraction/text_asset_extraction_report.py`
- `src/rie/extraction/text_asset_extraction_report_serializer.py`
- `src/rie/extraction/text_asset_extractor.py`
- `src/rie/infrastructure/evidence_repository_serialization.py`
- `src/rie/ingestion/__init__.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py`
- `src/rie/ingestion/creative_asset_batch_scanner.py`
- `src/rie/ingestion/creative_asset_scan_item.py`
- `src/rie/ingestion/creative_asset_scan_report.py`
- `src/rie/ingestion/creative_asset_scan_report_inspector.py`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py`
- `src/rie/ingestion/creative_asset_type.py`
- `src/rie/ingestion/creative_asset_type_detector.py`
- `src/rie/ingestion/inspect_scan_report.py`
- `src/rie/ingestion/inspect_unknown_assets.py`
- `src/rie/ingestion/real_asset_dry_run_contract.py`
- `src/rie/ingestion/real_asset_metadata_collection_contract.py`
- `src/rie/ingestion/real_asset_metadata_collector.py`
- `src/rie/ingestion/real_asset_metadata_dry_run_boundary.py`
- `src/rie/ingestion/real_asset_sandbox_policy.py`
- `src/rie/ingestion/real_filesystem_metadata_adapter.py`
- `src/rie/ingestion/real_filesystem_metadata_adapter_safety_contract.py`
- `src/rie/ingestion/scan_assets.py`
- `src/rie/ingestion/unknown_asset_header_inspector.py`
- `src/rie/knowledge/export_official_knowledge.py`
- `src/rie/knowledge/export_text_knowledge.py`
- `src/rie/knowledge/inspect_official_knowledge.py`
- `src/rie/knowledge/inspect_text_knowledge.py`
- `src/rie/official_source/__init__.py`
- `src/rie/official_source/inspect_evidence_eligibility.py`
- `src/rie/official_source/inspect_official_source_registry.py`
- `src/rie/prompt/export_text_prompt_candidates.py`
- `src/rie/prompt/inspect_text_prompt_candidates.py`
- `tests/application/test_evidence_candidate.py`
- `tests/application/test_evidence_candidate_snapshot.py`
- `tests/application/test_evidence_materializer.py`
- `tests/application/test_governed_knowledge_constructor.py`
- `tests/application/test_knowledge_constructor.py`
- `tests/application/test_knowledge_promotion_executor.py`
- `tests/domain/test_accepted_evidence.py`
- `tests/domain/test_evidence_identity.py`
- `tests/domain/test_knowledge_promotion_execution.py`
- `tests/extraction/test_export_pdf_text_evidence.py`
- `tests/extraction/test_export_pdf_text_extractions.py`
- `tests/extraction/test_export_text_extraction_evidence.py`
- `tests/extraction/test_extract_text_assets.py`
- `tests/extraction/test_inspect_pdf_text_evidence.py`
- `tests/extraction/test_inspect_pdf_text_extractions.py`
- `tests/extraction/test_inspect_text_extraction_evidence.py`
- `tests/extraction/test_pdf_page_text_extraction.py`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py`
- `tests/extraction/test_pdf_text_extraction_report.py`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py`
- `tests/extraction/test_pdf_text_extractor.py`
- `tests/extraction/test_text_asset_extraction_report_serializer.py`
- `tests/extraction/test_text_asset_extractor.py`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py`
- `tests/infrastructure/test_evidence_repository_serialization.py`
- `tests/infrastructure/test_in_memory_evidence_repository.py`
- `tests/infrastructure/test_sqlite_evidence_repository.py`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py`
- `tests/ingestion/test_creative_asset_batch_scanner.py`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py`
- `tests/ingestion/test_creative_asset_type_detector.py`
- `tests/ingestion/test_inspect_scan_report.py`
- `tests/ingestion/test_inspect_unknown_assets.py`
- `tests/ingestion/test_real_asset_dry_run_contract.py`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py`
- `tests/ingestion/test_real_asset_metadata_collector.py`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py`
- `tests/ingestion/test_real_asset_sandbox_policy.py`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py`
- `tests/ingestion/test_scan_assets.py`
- `tests/ingestion/test_unknown_asset_header_inspector.py`
- `tests/knowledge/test_text_knowledge_smoke_flow.py`
- `tests/test_inspect_evidence_eligibility_cli.py`
- `tests/test_inspect_official_source_registry_cli.py`
- `tests/test_official_source.py`
- `tests/test_official_source_evidence_eligibility_gate.py`
- `tests/test_official_source_evidence_eligibility_policy.py`
- `tests/test_official_source_evidence_workflow_gate.py`
- `tests/test_official_source_evidence_workflow_preflight.py`
- `tests/test_official_source_registry_loader.py`
- `tests/test_official_source_registry_validation.py`
- `tests/test_pdf_text_extraction_evidence.py`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py`
- `tests/test_pdf_text_extraction_evidence_builder.py`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py`
- `tests/test_pdf_text_extraction_evidence_collector.py`
- `tests/test_text_extraction_evidence_artifact_inspector.py`
- `tests/test_text_extraction_evidence_builder.py`
- `tests/test_text_extraction_evidence_collection_serializer.py`
- `tests/test_text_extraction_evidence_collector.py`

The inventory proves that Gate 2 registry behavior and related controlled-execution, checksum, source, parser, or extraction foundations can be reviewed for reuse. It does not authorize broad reuse, parser orchestration, or downstream Gate 4 behavior.

## 5. Candidate closure boundaries

### Candidate A - immutable data class only

Rejected. A standalone record does not prove explicit source admission, rejection of ineligible sources, checksum capture, pre-parser validation, operator workflow, output handling, or post-completion auditability.

### Candidate B - admission policy only

Rejected. Admission without the complete immutable job, snapshots, checksum, execution policy, output location, and auditable result cannot satisfy Gate 3.

### Candidate C - combined Gate 3 and Gate 4 ingestion service

Rejected as over-broad. Parser execution, structural metadata, page text extraction, failure classification, extraction artifacts, and cleanup belong to Gate 4 or later.

### Candidate D - minimum explicit-source immutable job vertical slice

Selected. It is the smallest operator-usable boundary that can satisfy all Gate 3 deliverables and Definition of Done while ending before parser execution.

## 6. Selected boundary

Selected boundary: `minimum_explicit_validated_source_id_to_immutable_auditable_ingestion_job_vertical_slice`

The boundary begins with a valid Gate 2 registry result and exactly one explicitly supplied `source_id`.

It ends with one validated immutable IngestionJob and one deterministic operator-visible job manifest at an explicitly supplied output location, before any parser or Gate 4 service is invoked.

The selected boundary must:

- resolve exactly one source entry from the valid Gate 2 registry without directory discovery;
- reject an unknown `source_id`;
- reject an ineligible source before checksum or parser handoff;
- preserve source path and expected source type from the validated source entry;
- capture immutable authority, lifecycle, and eligibility snapshots;
- calculate the source checksum through read-only access to the explicit source file;
- carry an explicit execution policy and explicit output location;
- construct and validate one immutable IngestionJob before parser execution;
- produce a deterministic auditable job representation that remains inspectable after completion;
- leave the locked source bytes unchanged;
- reject folder, wildcard, recursive, retry, fallback, clock-driven, random, network, Evidence, and Knowledge behavior.

## 7. Minimum runtime layers

```text
valid Gate 2 registry result
->
one explicit source_id lookup
->
source admission and eligibility validation
->
read-only source path and expected-type validation
->
read-only source checksum calculation
->
authority, lifecycle, eligibility, execution-policy, and output-location snapshots
->
immutable IngestionJob construction and validation
->
deterministic operator-visible job manifest before the parser boundary
```

Minimum layer count: `8`

## 8. Contract decisions reserved for PR-048B

PR-048A selects the runtime boundary but does not yet freeze representation details. PR-048B must decide only the minimum contract needed for this boundary, including:

- immutable IngestionJob representation and exact field types;
- deterministic or otherwise explicitly governed `job_id` policy;
- canonical source checksum algorithm and encoding;
- authority, lifecycle, and eligibility snapshot representation;
- execution-policy representation;
- explicit output-location rules and collision behavior;
- validation result and rejection reason contract;
- deterministic manifest serialization and operator output;
- exact boundary between admission validation and Gate 4 failure classification.

No contract decision may introduce directory discovery, parser execution, retries, fallback, network behavior, mutable source access, Evidence, Knowledge, repository expansion, or unrelated semantic frameworks.

## 9. Required eventual acceptance behaviors

The eventual Gate 3 implementation must prove at minimum:

- one valid explicit `source_id` produces exactly one controlled job;
- an unknown or ineligible source is rejected before parser execution;
- authority, lifecycle, and eligibility values are snapshotted rather than read live later;
- source checksum is calculated without modifying the source;
- wildcard, directory, and recursive inputs are rejected;
- every required field is validated before the parser boundary;
- the same governed inputs and identity policy produce reproducible job content;
- the job manifest remains inspectable after completion;
- parser, Extraction Artifact, Evidence, and Knowledge objects are not created.

## 10. Deferred subjects

The following remain outside the selected Gate 3 boundary:

- PDF parser execution and orchestration;
- structural metadata and page text extraction;
- Gate 4 failure taxonomy and controlled cleanup;
- Extraction Artifact construction or persistence;
- Evidence and Knowledge materialization;
- Evidence or Knowledge repositories;
- directory discovery, wildcard processing, recursive scan, retry, fallback, network, clock, and randomness;
- image intelligence, dashboard, multi-user workflow, asset-library runtime, and generator integration.

## 11. Targeted-semantics determination

No new semantic-chain blocker is proven by this review.

Gate 3 can proceed by reusing the valid Gate 2 source registry result and existing narrow source, execution, and checksum foundations only where their exact contracts fit the selected boundary.

No new Knowledge, assertion, interpretation, lifecycle-policy framework, repository abstraction, or generalized orchestration layer is authorized.

## 12. Repository and execution scope

PR-048A adds exactly one architecture document: `docs/architecture/pr-048a-controlled-source-admission-and-job-contract-minimum-closure-boundary-review.md`.

Production files modified: `0`.

Test files modified: `0`.

Configuration files modified: `0`.

Tests run: `0`.

Project interpreter processes: `0`.

Git mutation commands: `0`.

## 13. Final decision

# MINIMUM GATE 3 CLOSURE BOUNDARY SELECTED

Selected boundary: `minimum_explicit_validated_source_id_to_immutable_auditable_ingestion_job_vertical_slice`

Next eligible architecture subject after independent PR-048A acceptance: `controlled_source_admission_and_ingestion_job_runtime_contract_review`

Gate 3 remains OPEN.

Phase 48 implementation remains unauthorized.

PR-048A does not implement the selected boundary, close Gate 3, close Phase 48, start Gate 4, or authorize parser execution.
