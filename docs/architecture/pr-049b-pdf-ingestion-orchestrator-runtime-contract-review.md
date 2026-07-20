# PR-049B - PDF Ingestion Orchestrator Runtime Contract Review

## 1. Review identity

Review subject:

`pdf_ingestion_orchestrator_runtime_contract_review`

Selected boundary:

`single_accepted_pdf_job_deterministic_structural_metadata_and_page_text_orchestration_boundary`

This review selects the Gate 4 runtime contract only. It does not authorize implementation.

## 2. Accepted predecessor

- PR-049A commit: `d93f3698ba5323ca7c569c153d0f3ba0f3a67216`
- PR-049A document SHA-256: `bac7082314ed16fc5eb97c0fb1bc388338982303d36eb5c7ba3f9cd24fd213fd`
- Gate 3 supplies exactly one immutable `IngestionJob`.
- Gate 4 must not introduce source discovery, wildcard processing, or a second admission mechanism.

## 3. Selected contract identities

- service contract: `pdf_ingestion_orchestrator_contract_v1`;
- result contract: `pdf_ingestion_orchestrator_result_contract_v1`;
- execution-report contract: `pdf_ingestion_orchestrator_execution_report_contract_v1`.

These Gate 4 contracts are operational orchestration contracts. They are not the Gate 5 versioned Extraction Artifact.

## 4. Request contract

The service accepts one frozen request containing exactly:
- `job`
- `execution_report_location`

`job` must be one valid immutable Gate 3 `IngestionJob`.

`execution_report_location` must be one explicit file path, distinct from the Gate 3 manifest location. Directory discovery, wildcard syntax, recursive processing, and output overwrite are rejected.

## 5. Deterministic execution order
1. validate immutable Gate 3 ingestion job.
2. verify PDF type, source path, regular-file state, and admitted checksum.
3. verify authority, lifecycle, and eligibility snapshots remain acceptable.
4. execute structural metadata inspection.
5. reject encrypted PDF before page-text extraction.
6. execute ordered page-level text extraction.
7. construct immutable Gate 4 result.
8. serialize and publish deterministic execution report.
9. remove every temporary path on failure.

Execution is fail-fast. The first failure in this order is the only public issue returned. Automatic retry, parser fallback, OCR, rendering, and image extraction are forbidden.

## 6. Result contract

Result statuses are exactly:
- `completed`
- `failed`

The frozen result field order is exactly:
1. `contract_version`
2. `status`
3. `job_id`
4. `source_id`
5. `source_path`
6. `source_checksum`
7. `structural_metadata`
8. `page_extractions`
9. `issue`
10. `execution_report_location`
11. `cleanup_completed`

A `completed` result requires:

- exact Gate 3 job, source, and checksum identity preservation;
- one accepted structural metadata result;
- deterministic ordered page extractions;
- no issue;
- successful deterministic report publication;
- `cleanup_completed=True`.

A `failed` result requires:

- exact job and source identity when available;
- exactly one issue;
- no partially accepted structural/page result;
- no committed partial output;
- `cleanup_completed=True`.

## 7. Issue contract

The issue fields are exactly:
- `code`
- `message`

The public failure classes are exactly:
- `source_missing`
- `source_not_file`
- `unsupported_source`
- `encrypted_pdf`
- `parser_failure`
- `structural_metadata_failure`
- `text_extraction_failure`
- `output_failure`
- `authority_rejected`

Failure mapping:

- missing source -> `source_missing`;
- non-file source -> `source_not_file`;
- non-PDF or unsupported PDF input -> `unsupported_source`;
- encrypted PDF -> `encrypted_pdf`;
- parser dependency or parser execution failure -> `parser_failure`;
- invalid or unsuccessful structural result -> `structural_metadata_failure`;
- invalid or unsuccessful page-text result -> `text_extraction_failure`;
- collision, serialization, write, read-back, or publication failure -> `output_failure`;
- invalid or unacceptable authority, lifecycle, or eligibility snapshot -> `authority_rejected`.

Internal exception text, host paths beyond the admitted source, and stack traces must not become public issue messages.

## 8. Execution report contract

The deterministic operator report field order is exactly:
1. `contract_version`
2. `status`
3. `job_id`
4. `source_id`
5. `source_checksum`
6. `structural_page_count`
7. `extracted_page_count`
8. `warning_count`
9. `issue`
10. `cleanup_completed`

The report is UTF-8 without BOM, LF-only, exactly one final LF, deterministic field order, write-once, and byte-verified after publication.

The report is an operational execution record only. It does not establish the Gate 5 artifact schema and does not contain Evidence or Knowledge.

## 9. Reused foundation and protected behavior

Verified reusable foundation path count: `9`.

- `src/rie/ingestion/controlled_source_admission_job_contract.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py`
- `src/rie/extraction/pdf_page_text_extraction.py`
- `src/rie/extraction/pdf_text_extractor.py`
- `src/rie/extraction/pdf_text_extraction_report.py`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py`

The implementation must reuse these accepted foundations through a thin orchestration adapter. It must not modify locked sources, create Evidence, create Knowledge, scan directories, or broaden extraction behavior.

## 10. Contract invariants

1. One request contains one Gate 3 job and one explicit report location.
2. Job identity and admitted checksum are revalidated before parser execution.
3. Structural inspection always precedes page-text extraction.
4. Encrypted PDFs never reach page-text extraction.
5. Page records are ordered deterministically and trace to the same admitted source.
6. Successful repeated execution over the same immutable source produces equivalent result content and report bytes, excluding no fields because the selected contract contains no clock-derived field.
7. Every failure maps to exactly one frozen public failure class.
8. Every failure leaves no temporary file or partial published output.
9. Evidence creation, Knowledge construction, OCR, rendering, image extraction, retry, and fallback remain forbidden.

## 11. Decision and next action

Selected runtime contract: `pdf_ingestion_orchestrator_contract_v1`.

Selected result contract: `pdf_ingestion_orchestrator_result_contract_v1`.

Selected execution-report contract: `pdf_ingestion_orchestrator_execution_report_contract_v1`.

Status after this review:

- Gate 4 planning boundary selected: `True`;
- Gate 4 runtime contract selected: `True`;
- Gate 4 implementation boundary selected: `False`;
- Gate 4 implementation authorized: `False`;
- Gate 4 closed: `False`.

Next review: `PR-049C - pdf_ingestion_orchestrator_implementation_boundary_review`.
