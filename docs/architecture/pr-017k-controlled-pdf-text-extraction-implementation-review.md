# PR-017K - Controlled PDF Text Extraction Implementation Review

Status: Docs-only PDF text extraction implementation review.

Current checkpoint:

- v0.17.9-rcis-controlled-pdf-text-extraction-result-contract
- f1f347d feat: add controlled pdf text extraction result contract

## Context

PR-017 has advanced through the controlled real-asset and controlled PDF text
extraction gates without approving actual PDF parsing:

- PR-017A controlled real asset smoke test architecture review
- PR-017B controlled real asset fixture policy review
- PR-017C controlled real asset fixture contract
- PR-017D controlled real asset metadata smoke test
- PR-017E controlled PDF text evidence review
- PR-017F controlled PDF text extraction contract
- PR-017G controlled PDF text extraction execution review
- PR-017H controlled PDF text extraction execution contract
- PR-017I controlled PDF text extraction result boundary review
- PR-017J controlled PDF text extraction result contract

PR-017J added a value-only result contract. It still does not parse PDFs, read
the filesystem for extraction, extract text from files, expose extracted_text in
the result, or create Evidence.

## Purpose

PR-017K defines the implementation boundary for a future controlled PDF text
extraction implementation PR. It does not implement extraction, connect any
extractor, create Evidence, or touch real assets.

PDF text extraction implementation is a new execution boundary. Actual parser
execution is not approved by PR-017K.

## Required Gate Chain

A future controlled PDF text extraction implementation must pass every existing
gate before parsing:

- ControlledRealAssetFixtureContract
- ControlledPdfTextExtractionContract
- ControlledPdfTextExtractionExecutionContract
- ControlledPdfTextExtractionResultContract

Actual extraction must be restricted to exactly one controlled
product_spec_pdf fixture. The implementation must use a sandbox copy only and
must use the explicit fixture path approved by the fixture contract chain.

The implementation must not scan folders, use the repository root, use the
current working directory, mutate source files, or infer additional assets from
surrounding paths.

The extraction result must be passed through
ControlledPdfTextExtractionResultContract. Actual extraction output is not
automatically Evidence. It does not create Official Knowledge, Product
Knowledge, or Prompt Candidate artifacts, and it does not authorize AI
inference.

## Future Implementation Preconditions

A future extraction implementation PR must require:

- fixture contract allowed
- PDF text extraction contract allowed
- PDF text extraction execution contract allowed
- PDF text extraction result contract allowed
- exactly one matching product_spec_pdf fixture
- fixture path comes from the approved fixture contract chain
- sandbox copy only
- read-only execution
- bounded extraction output
- bounded preview
- full text storage disabled unless later approved
- deterministic parser errors
- deterministic empty, unreadable, and encrypted handling
- no broad discovery
- no recursive scan
- no image or OCR interpretation
- no evidence creation unless separately allowed later

## Extractor Implementation Boundary

A future implementation may review one controlled extractor path only. PR-017K
does not select, install, connect, or execute an extractor.

At a high level, the extractor choice should favor the smallest deterministic
local parser path that can satisfy the approved contract without expanding the
workflow into image, OCR, semantic interpretation, evidence, knowledge, prompt,
network, or AI concerns.

A future extractor must:

- be deterministic
- run locally
- not call AI
- not call network
- not perform OCR
- not extract images
- not infer layout semantics
- not classify content
- not infer product claims
- not infer product benefits
- not infer persona
- not infer prompts
- not create Evidence

Forbidden extractor behavior:

- multiple extractor strategies
- automatic fallback chains
- OCR fallback
- image extraction
- layout interpretation
- AI-based PDF reading
- network calls
- content classification
- claim extraction
- benefit extraction
- product inference
- persona inference
- prompt inference
- Evidence creation
- Knowledge creation

## Future Result Handling

A future implementation must construct a
ControlledPdfTextExtractionResultInput and validate it through
ControlledPdfTextExtractionResultContract.

Result handling must preserve:

- fixture_id
- source_label
- fixture_path
- fixture_type
- extraction_mode
- extraction_status
- text_length
- bounded text_preview
- extracted_text_included False by default
- truncated
- extraction_error
- evidence_allowed False
- notes

## Text Output Policy

The future implementation must not store full extracted_text by default. It may
compute text_length and a bounded text_preview.

The implementation must respect max_extracted_characters and
max_preview_characters from the execution contract. It must set truncated
deterministically and must never pass unbounded text downstream.

## Evidence Boundary

Implementation output is not Evidence.

text_preview is not Evidence.

Extracted text is not automatically Evidence.

Evidence creation requires a separate explicit PDF Evidence contract. Official
Knowledge remains manual and governed. Product Knowledge remains outside
PR-017K. Prompt Candidate remains outside PR-017K. AI inference remains
forbidden.

## Relationship To Existing Components

ControlledRealAssetFixtureContract remains the first gate.

ControlledPdfTextExtractionContract remains the PDF text gate.

ControlledPdfTextExtractionExecutionContract remains the execution permission
gate.

ControlledPdfTextExtractionResultContract remains the result validation gate.

RealFilesystemMetadataAdapter remains metadata-only and must not extract text.

RealAssetMetadataCollector remains metadata-only and must not extract text.

CreativeAssetBatchScanner remains outside this workflow.

CreativeAssetTypeDetector remains outside this workflow.

Existing PDF extraction modules, if any, must not be connected until a later
controlled PR.

## Recommended Next PR

PR-017L - Controlled PDF Text Extraction Implementation Skeleton

PR-017L should add a minimal implementation skeleton only if approved. It
should use synthetic tmp_path PDF fixture tests only. It should not touch real
RSV assets, create Evidence, or store full extracted_text by default. It should
pass results through ControlledPdfTextExtractionResultContract.

## Forbidden Scope For PR-017K

PR-017K must not include:

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
