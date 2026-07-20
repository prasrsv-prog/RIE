# PR-049A - PDF Ingestion Orchestrator Minimum Closure Boundary Review

## 1. Review identity

Review subject:

`pdf_ingestion_orchestrator_minimum_closure_boundary_review`

Decision:

`single_accepted_pdf_job_deterministic_structural_metadata_and_page_text_orchestration_boundary`

This review opens Gate 4 planning only. It does not authorize implementation.

## 2. Accepted dependency checkpoint

- Phase 48 and Gate 3 checkpoint: `9932e247c91919b17ca68beb80927137c8004d17`
- Official Phase 48 tag: `v0.48.0-rcis-controlled-source-admission-and-job-contract-phase`
- Official tag object: `b607f5bad3583befb2b2538c2589ce01683c1711`
- Gate 3 immutable controlled ingestion job is accepted.
- Gate 4 begins from one accepted Gate 3 job, not from directory discovery or a second source-selection mechanism.

## 3. Authoritative Gate 4 outcome

Required outcome: `deterministic_pdf_ingestion_service`.

The official application boundary must combine, in deterministic order:

1. accepted controlled ingestion job validation;
2. PDF source and immutable checksum preflight;
3. structural metadata inspection;
4. page-level PDF text extraction;
5. deterministic result and execution-report construction;
6. controlled output publication or complete cleanup.

## 4. Existing reusable foundation

Required reusable production-path count: `16`.

- `src/rie/ingestion/controlled_source_admission_job_contract.py`
- `src/rie/ingestion/controlled_source_admission_manifest_serializer.py`
- `src/rie/ingestion/controlled_source_admission_service.py`
- `src/rie/ingestion/create_controlled_ingestion_job.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py`
- `src/rie/extraction/pdf_page_text_extraction.py`
- `src/rie/extraction/pdf_text_extractor.py`
- `src/rie/extraction/pdf_text_extraction_report.py`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py`

These paths are foundation evidence only. Their existence does not by itself close Gate 4.

## 5. Selected minimum closure boundary

Gate 4 closure requires one official service boundary that:

1. accepts exactly one immutable Gate 3 ingestion job;
2. accepts only a PDF job and rejects non-PDF or invalid job input;
3. preserves the job identity, source identity, source path, source checksum, authority, lifecycle, and eligibility snapshots;
4. verifies that the execution source remains the same immutable source admitted by Gate 3;
5. executes structural metadata inspection before page-text extraction;
6. produces one deterministic Gate 4 execution result containing structural metadata and ordered page-level text results;
7. produces one deterministic execution report suitable for operator review;
8. maps every accepted failure to one required public failure class;
9. publishes no partial final output and leaves no temporary asset after failure;
10. provides a direct module-level operator workflow for acceptance while root CLI packaging remains deferred to Gate 11.

The Gate 4 execution result is not yet the official versioned Extraction Artifact. Artifact schema, persistence, and lossless round-trip remain Gate 5 responsibilities.

## 6. Required deterministic failure classes

- `source_missing`
- `source_not_file`
- `unsupported_source`
- `encrypted_pdf`
- `parser_failure`
- `structural_metadata_failure`
- `text_extraction_failure`
- `output_failure`
- `authority_rejected`

PR-049B must determine exact precedence when more than one failure condition is observable and must prevent lower-level exception text from becoming the public contract.

## 7. Protected exclusions

The Gate 4 boundary must not:

- create Evidence, EvidenceCandidate, AcceptedEvidence, Knowledge, or Prompt Candidate;
- define the official Gate 5 versioned Extraction Artifact;
- perform OCR, page rendering, image extraction, or image intelligence;
- use automatic retry, parser fallback, or best-effort recovery;
- scan directories or accept wildcard or recursive input;
- mutate, replace, rename, or delete the admitted source;
- overwrite an existing final output;
- change root CLI routing, installer entry points, or release packaging;
- introduce additional semantic decisions unless a concrete Gate 4 blocker is proven.

## 8. Definition-of-Done mapping

Gate 4 may close only when acceptance proves:

1. one official PDF is processed through the accepted Gate 3 job boundary;
2. output includes structural metadata and ordered page-level text;
3. repeated execution from the same valid immutable input is reproducible;
4. no Evidence or later-gate object is created;
5. each required failure class is deterministic and operator-visible;
6. every failed execution leaves no temporary or partial final asset;
7. targeted acceptance and full regression tests pass;
8. closure evidence is committed, merged, and officially tagged.

## 9. Risk-based verification policy

Gate 4 uses the frozen risk-based verification policy:

- normal architecture and implementation PRs receive one acceptance and one concise post-commit verification;
- final phase publication receives one consolidated merge, push, tag, ref, and cleanliness verification;
- forensic byte-level verification is triggered only by a concrete integrity or repository-state risk.

## 10. Decision and next action

Selected minimum boundary: `single_accepted_pdf_job_deterministic_structural_metadata_and_page_text_orchestration_boundary`.

Status after this review:

- Gate 4 planning boundary selected: `True`;
- Gate 4 runtime contract selected: `False`;
- Gate 4 implementation boundary selected: `False`;
- Gate 4 implementation authorized: `False`;
- Gate 4 closed: `False`.

Next review: `PR-049B - pdf_ingestion_orchestrator_runtime_contract_review`.
