# PR-049C - PDF Ingestion Orchestrator Implementation Boundary Review

## 1. Review identity

Review subject:

`pdf_ingestion_orchestrator_implementation_boundary_review`

Selected planning boundary:

`single_accepted_pdf_job_deterministic_structural_metadata_and_page_text_orchestration_boundary`

Accepted corrected runtime contract identities:

- `pdf_ingestion_orchestrator_contract_v1`;
- `pdf_ingestion_orchestrator_result_contract_v1`;
- `pdf_ingestion_orchestrator_execution_report_contract_v1`.

This review selects and authorizes the minimum implementation boundary only. It does not implement the boundary.

## 2. Exact production scope

PR-049D may add exactly four production paths:
1. `src/rie/ingestion/pdf_ingestion_orchestrator_contract.py`
2. `src/rie/ingestion/pdf_ingestion_orchestrator_execution_report_contract.py`
3. `src/rie/ingestion/pdf_ingestion_orchestrator_execution_report_serializer.py`
4. `src/rie/ingestion/pdf_ingestion_orchestrator_service.py`

No existing production file may be modified.

## 3. Exact test scope

PR-049D may add exactly four test paths:
1. `tests/ingestion/test_pdf_ingestion_orchestrator_contract.py`
2. `tests/ingestion/test_pdf_ingestion_orchestrator_execution_report_contract.py`
3. `tests/ingestion/test_pdf_ingestion_orchestrator_execution_report_serializer.py`
4. `tests/ingestion/test_pdf_ingestion_orchestrator_service.py`

No existing test file may be modified.

## 4. Required production symbols

`src/rie/ingestion/pdf_ingestion_orchestrator_contract.py` must define:
- `class PdfIngestionOrchestratorIssue`
- `class PdfIngestionOrchestratorRequest`
- `class PdfIngestionOrchestratorResult`

`src/rie/ingestion/pdf_ingestion_orchestrator_execution_report_contract.py` must define:
- `class PdfIngestionOrchestratorExecutionReport`

`src/rie/ingestion/pdf_ingestion_orchestrator_execution_report_serializer.py` must define:
- `class PdfIngestionOrchestratorExecutionReportSerializer`

`src/rie/ingestion/pdf_ingestion_orchestrator_service.py` must define:
- `class PdfIngestionOrchestratorService`

All public contract dataclasses must be frozen and validate their own invariants.

## 5. Contract module responsibilities

`pdf_ingestion_orchestrator_contract.py` owns only:

- request validation for one immutable Gate 3 job and one explicit report path;
- the exact two result statuses: `completed` and `failed`;
- the exact ten public failure classes;
- immutable issue and result contracts;
- completed/failed result invariant enforcement.

`pdf_ingestion_orchestrator_execution_report_contract.py` owns only the frozen ten-field execution-report contract.

`pdf_ingestion_orchestrator_execution_report_serializer.py` owns only deterministic serialization, exclusive write-once publication, and exact read-back byte verification.

`pdf_ingestion_orchestrator_service.py` owns only deterministic orchestration of accepted Gate 3 job validation, checksum revalidation, authority validation, structural inspection, encrypted-PDF rejection, page-text extraction, result construction, report publication, and cleanup.

## 6. Reuse boundary

The service must reuse the accepted existing foundations without modifying them:
- `src/rie/ingestion/controlled_source_admission_job_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py`
- `src/rie/extraction/pdf_page_text_extraction.py`
- `src/rie/extraction/pdf_text_extractor.py`
- `src/rie/extraction/pdf_text_extraction_report.py`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py`

The new service may use thin private adapters to normalize accepted upstream return shapes. It must not duplicate parser, structural inspection, page extraction, admission, or source-registry logic.

## 7. Deterministic service order

The service must execute in this exact fail-fast order:

1. validate request and immutable Gate 3 job;
2. validate authority, lifecycle, and eligibility snapshots;
3. validate explicit source path, regular-file state, PDF type, and report path;
4. recompute SHA-256 and compare it to the admitted checksum;
5. invoke accepted structural metadata inspection;
6. reject encrypted PDF before page-text extraction;
7. invoke accepted ordered page-level text extraction;
8. validate structural and extracted page-count consistency;
9. construct the immutable completed result and execution report;
10. publish the report with write-once and byte-read-back verification;
11. return the completed result;
12. on the first failure, remove every temporary or partial output and return exactly one failed result.

## 8. Failure mapping

The service must expose exactly these ten failure classes:
- `source_missing`
- `source_not_file`
- `source_checksum_mismatch`
- `unsupported_source`
- `encrypted_pdf`
- `parser_failure`
- `structural_metadata_failure`
- `text_extraction_failure`
- `output_failure`
- `authority_rejected`

Checksum mismatch must map only to `source_checksum_mismatch` and never to `authority_rejected`.

Unexpected parser dependency or parser execution exceptions map to `parser_failure`. Internal exception text and stack traces remain private.

## 9. Execution-report publication

The serializer must:

- emit UTF-8 without BOM;
- emit LF-only bytes;
- terminate with exactly one final LF;
- preserve frozen field order;
- reject an existing output path;
- create parent directories only when the explicit parent does not exist and only within the selected output path boundary;
- use an implementation-private temporary sibling path;
- atomically publish only after complete serialization;
- read back and byte-compare the published file;
- remove temporary and partial output on failure.

## 10. Required test matrix

The implementation must cover at least these `24` behavioral areas:
1. frozen request, issue, and result construction.
2. exact result statuses and ten failure classes.
3. invalid completed and failed result combinations.
4. frozen execution-report field order.
5. deterministic UTF-8 LF-only serialization with one final LF.
6. write-once output collision rejection.
7. successful raw-byte read-back verification.
8. single valid Gate 3 PDF job success path.
9. source missing and non-file rejection before parser execution.
10. source checksum mismatch rejection before parser execution.
11. unsupported source rejection.
12. authority, lifecycle, and eligibility rejection.
13. encrypted PDF rejection before text extraction.
14. structural metadata failure mapping.
15. page-text extraction failure mapping.
16. output failure mapping.
17. first-failure-only behavior.
18. source and job identity preservation.
19. structural page count and extracted page count consistency.
20. deterministic ordered page results.
21. temporary-path and partial-output cleanup on every failure.
22. no source mutation.
23. no OCR, rendering, image extraction, retry, or fallback.
24. no Evidence or Knowledge construction.

Targeted tests for the four new test files are mandatory. Full regression is mandatory before implementation acceptance.

## 11. Explicit prohibitions

PR-049D must not:

- modify any existing source, test, configuration, dependency, parser, extractor, serializer, CLI, Evidence, Knowledge, or locked-document path;
- introduce directory discovery, wildcard input, recursive input, or multi-job orchestration;
- mutate, rename, replace, delete, or rewrite the admitted source;
- perform OCR, rendering, image extraction, automatic retry, or parser fallback;
- create Evidence or Knowledge;
- establish the Gate 5 versioned Extraction Artifact;
- add a root CLI, package entry point, or release surface;
- invoke Gate 5.

## 12. Definition of done for PR-049D

PR-049D is acceptable only when:

- exactly eight authorized paths are added;
- no existing path is modified;
- all required public symbols exist;
- all ten failure classes are frozen and tested;
- targeted tests pass;
- full regression passes;
- repository scope remains exact;
- no Gate 5 behavior is introduced.

## 13. Decision

Decision:

`PDF_INGESTION_ORCHESTRATOR_IMPLEMENTATION_BOUNDARY_SELECTED`

Status after this review:

- Gate 4 planning boundary selected: `True`;
- Gate 4 runtime contract selected: `True`;
- Gate 4 implementation boundary selected: `True`;
- Gate 4 implementation authorized: `True`;
- Gate 4 implementation started: `False`;
- Gate 4 closed: `False`.

Next review: `PR-049D - pdf_ingestion_orchestrator_contract_implementation`.
