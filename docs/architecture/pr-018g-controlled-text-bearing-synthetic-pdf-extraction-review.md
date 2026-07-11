# PR-018G - Controlled Text-Bearing Synthetic PDF Extraction Review

Status: Docs-only controlled text-bearing synthetic PDF extraction review.

Current checkpoint:

- v0.18.5-rcis-controlled-synthetic-pdf-parser-execution
- b654ecc test: add controlled synthetic pdf parser execution

## Purpose

PR-018G reviews the boundary for a future test that proves controlled
text-bearing synthetic PDF extraction returns an extracted result without
exposing full extracted_text and without creating Evidence, Knowledge, or
Prompt artifacts.

PR-018G does not modify production code, tests, pyproject.toml, or lock files.
It does not install dependencies, parse PDFs, create PDF fixtures, extract PDF
text, or touch real RSV assets. It does not create Evidence, Knowledge, or
Prompt Candidate artifacts and does not authorize AI inference.

This review defines a future tests-only boundary. It does not enable or perform
new PDF extraction behavior.

## Context

- PR-018A found pypdf declared but not importable.
- PR-018B planned dependency synchronization.
- PR-018C reviewed the local repair command.
- PR-018D installed and verified pypdf in the local `.venv`.
- PR-018D recorded pypdf version `6.14.2`.
- PR-018E reviewed controlled synthetic parser execution.
- PR-018F added a tests-only blank synthetic PDF parser execution test.
- PR-018F proved pypdf parser invocation through tmp_path and avoided
  unsupported_pdf.
- PR-018F observed status empty, not extracted.

## Environment Status

- Active Python executable:
  `D:\PROJECT\RIE\.venv\Scripts\python.exe`
- pypdf import succeeded: yes
- pypdf version: `6.14.2`
- Full test result for this review: 830 passed
- Dependency caveat: no lock-file reproducibility was added

The installed parser is a local environment repair. Version `6.14.2` is not a
locked repository-wide dependency selection.

## Reason For PR-018G

PR-018F proves that the approved chain reaches pypdf with a blank synthetic PDF
and returns deterministic bounded output. A blank page contains no text, so its
empty status does not prove text-bearing extraction.

A separate review is required before creating a synthetic PDF with an embedded
text content stream and asserting extracted status. This keeps the simplest
extracted path separate from truncation, parser-error, real-asset, Evidence,
Knowledge, and Prompt concerns.

## Controlled Text-Bearing Extraction Boundary

A future PR may add a text-bearing synthetic PDF extraction test only if it:

- uses tmp_path only
- creates the synthetic text-bearing PDF inside the test only
- does not add checked-in binary PDF fixtures
- does not use real RSV assets
- does not use real product PDFs
- does not use repository files as fixtures
- does not scan folders
- does not use the repository root
- does not use the current working directory
- does not recursively scan
- executes through the existing approved chain
- keeps full extracted_text storage disabled
- creates no Evidence, Knowledge, or Prompt Candidate artifacts

The required chain is:

```text
ControlledRealAssetFixtureContract
        ->
ControlledPdfTextExtractionContract
        ->
ControlledPdfTextExtractionExecutionContract
        ->
ControlledPdfTextExtractionImplementation
        ->
ControlledPdfTextExtractionResultContractResult
```

The final result must not expose extracted_text. It must keep
extracted_text_included False, evidence_allowed False,
allow_full_text_storage False, and allow_evidence_creation False.

## Synthetic Text PDF Generation Policy

A future PR should generate a minimal text-bearing PDF inside tmp_path using
only pypdf or the Python standard library. It must not introduce a PDF creation
dependency.

The synthetic text may be:

```text
SYNTHETIC PDF TEXT FOR CONTROLLED PARSER TEST ONLY
```

The future fixture must:

- use generic non-product text
- avoid real RSV copy
- avoid product specifications
- avoid product claims
- avoid brand knowledge
- avoid customer data
- avoid external PDF files
- avoid network access
- avoid checked-in binary fixtures
- avoid OCR
- avoid image extraction
- avoid layout semantic inference
- avoid product meaning inference

If pypdf does not provide a reliable high-level text-writing path, the future
test may construct a minimal standards-compatible PDF content stream with
Python standard-library bytes. That implementation must remain local to the
test and must not expand into a general PDF generator.

## Expected Future Result Behavior

A future PR may assert:

- result.allowed is True
- result.extraction_status is extracted
- result.text_length is greater than zero
- result.text_preview contains only bounded synthetic text
- result.text_preview length does not exceed max_preview_characters
- result.extracted_text_included is False
- result.evidence_allowed is False
- result does not have an extracted_text attribute
- result.fixture_path is the tmp_path synthetic PDF path
- unsupported_pdf is not produced when pypdf is importable

The test should also prove that the parser receives exactly the explicit
fixture path approved by the upstream contract chain.

## Preview Policy

The text_preview may contain bounded synthetic text only. It must not contain
real product or RSV asset information.

The preview is not Evidence, does not become Knowledge, and does not become a
Prompt Candidate. It remains bounded factual parser output used only to verify
the approved result contract.

## Truncation Policy

A later PR may add a separate deterministic truncation test. PR-018H should
first prove only the simplest extracted path.

Do not combine the extracted path, truncation path, parser-error path, or real
asset preparation in one PR.

## Forbidden Scope

- real RSV asset processing
- real product PDF ingestion
- folder scans
- repository-wide scans
- source file mutation
- full extracted_text exposure
- Evidence creation
- Official Knowledge creation
- Product Knowledge creation
- Prompt Candidate creation
- AI inference
- OCR
- image extraction
- layout interpretation
- product claim extraction
- product benefit extraction
- persona inference
- prompt inference
- CLI, API, or dashboard execution
- dependency policy changes
- lock-file generation

## Recommended Next PR

PR-018H - Controlled Text-Bearing Synthetic PDF Extraction

PR-018H may add tests only if the current production implementation already
supports text-bearing synthetic PDF extraction. It should prove extracted
status using a synthetic tmp_path PDF only.

PR-018H must not touch real RSV assets, expose extracted_text, or create
Evidence, Knowledge, or Prompt Candidate artifacts. It must not modify
production code unless a separately reviewed blocker proves the current
implementation cannot support the approved synthetic test path.

## Review Acceptance

- Only this docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed or changed.
- No standalone PDF parsing or fixture creation is performed.
- pypdf imports successfully and version `6.14.2` is recorded.
- No commit is created by PR-018G preparation.
