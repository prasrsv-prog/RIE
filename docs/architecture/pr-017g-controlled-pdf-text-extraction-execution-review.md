# PR-017G - Controlled PDF Text Extraction Execution Review

Status:
Docs-only PDF text extraction execution review.

Current checkpoint:
v0.17.5-rcis-controlled-pdf-text-extraction-contract
8e50051 feat: add controlled pdf text extraction contract

## Context

Completed PR-017 stages:

- PR-017A controlled real asset smoke test architecture review
- PR-017B controlled real asset fixture policy review
- PR-017C controlled real asset fixture contract
- PR-017D controlled real asset metadata smoke test
- PR-017E controlled PDF text evidence review
- PR-017F controlled PDF text extraction contract

PR-017F added a value-only gate only.

PR-017F intentionally did not enable actual PDF parsing or extraction.

## Main Purpose

PR-017G defines the safety boundary for a future controlled PDF text extraction execution PR.

PR-017G must not implement extraction.

PR-017G must not connect any extractor.

PR-017G must not create evidence.

PR-017G must not touch real assets.

## Execution Boundary Statements

PDF text extraction execution is a separate boundary from the PR-017F value-only contract.

The PR-017F contract does not authorize execution yet.

Execution requires explicit later approval.

Execution must be restricted to exactly 1 controlled product_spec_pdf fixture.

Execution must use sandbox copy only.

Execution must use explicit fixture path only.

Execution must not scan folders.

Execution must not use repository root or current working directory.

Execution must not mutate source files.

Execution result is not automatically Evidence.

Execution result does not create Official Knowledge.

Execution result does not create Product Knowledge.

Execution result does not create Prompt Candidate.

Execution result does not authorize AI inference.

## Future Execution Preconditions

A future extraction execution PR must require:

- ControlledRealAssetFixtureContract allowed
- ControlledPdfTextExtractionContract allowed
- explicit execution approval from a new execution contract
- exactly one matching product_spec_pdf fixture
- fixture path comes from the approved fixture contract result
- sandbox copy only
- read-only execution
- bounded output
- deterministic error handling
- no broad discovery
- no recursive scan
- no image or OCR interpretation
- no evidence creation unless separately allowed later

## Important Nuance

The current ControlledPdfTextExtractionContract keeps:

- allow_pdf_text_extraction False
- allow_evidence_creation False
- fixture.allowed_for_pdf_text_extraction False
- fixture.allowed_for_evidence False

A later execution-specific contract may open extraction execution, but only after this review.

## Future Extraction Result Boundary

A future controlled PDF text extraction execution result may contain only:

- allowed
- reason
- fixture_id
- source_label
- fixture_path
- extraction_mode
- extraction_status
- text_length
- text_preview only if explicitly bounded
- extracted_text only if explicitly approved in a later PR
- extraction_error
- evidence_allowed
- notes

These are policy fields only.

Do not implement them in PR-017G.

## Text Output Limits

A future execution PR must define limits before extraction, such as:

- maximum extracted characters
- maximum preview characters
- whether full extracted_text is allowed
- whether only text_length and preview are stored
- how empty PDFs are handled
- how encrypted or unreadable PDFs are handled
- how parser errors are handled
- how non-text PDFs are handled

## Evidence Boundary

PDF extraction execution result is not Evidence.

Extracted text is not automatically Evidence.

Evidence creation requires separate explicit PDF Evidence contract.

Evidence must preserve fixture_id, source_label, fixture_path, extraction status, and traceability.

Official Knowledge remains manual and governed.

Product Knowledge remains outside PR-017G.

Prompt Candidate remains outside PR-017G.

## Extractor Boundary

A future execution PR may review one controlled extractor path only.

It must not allow:

- multiple extractor strategies
- auto fallback extractor chains
- OCR fallback
- image extraction
- layout interpretation
- AI-based PDF reading
- content classification
- claim extraction
- product inference
- persona inference
- prompt inference

## Relationship To Existing Components

ControlledRealAssetFixtureContract remains the first fixture gate.

ControlledPdfTextExtractionContract remains the PDF extraction gate.

A new execution-specific contract should be added before actual parsing.

RealFilesystemMetadataAdapter remains metadata-only and must not extract text.

RealAssetMetadataCollector remains metadata-only and must not extract text.

CreativeAssetBatchScanner remains outside this workflow.

CreativeAssetTypeDetector remains outside this workflow.

Existing PDF extraction modules, if any, must not be connected until a later controlled PR.

## Recommended Next PR

PR-017H - Controlled PDF Text Extraction Execution Contract

PR-017H should add a value-only execution contract skeleton first.

PR-017H should not parse PDFs.

PR-017H should not read filesystem.

PR-017H should not create Evidence.

PR-017H should use synthetic tests only.

A later PR may implement actual controlled extraction using tmp_path synthetic PDF fixture or explicitly approved sandbox PDF fixture, depending on review.

## Forbidden Scope For PR-017G

PR-017G forbids:

- production code changes
- test changes
- fixture creation
- fixture loading
- filesystem calls
- real asset scans
- folder inspection
- content reads
- PDF parsing
- PDF text extraction
- image parsing
- OCR
- scanner or detector usage
- extractor connection
- evidence creation
- knowledge creation
- prompt creation
- AI calls
- API, CLI, or dashboard work
- locked or SSOT document changes
- master asset library changes
- registry autoloading

## Acceptance Criteria

- Only one docs file added.
- Full tests pass.
- No non-ASCII or garbled characters remain.
- No commit.
