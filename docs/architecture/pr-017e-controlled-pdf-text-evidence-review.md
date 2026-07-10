# PR-017E - Controlled PDF Text Evidence Review

Status:
Docs-only PDF text evidence architecture review.

Current checkpoint:
v0.17.3-rcis-controlled-real-asset-metadata-smoke-test
2f24218 test: add controlled real asset metadata smoke flow

## Context

Completed PR-017 stages:

- PR-017A controlled real asset smoke test architecture review
- PR-017B controlled real asset fixture policy review
- PR-017C controlled real asset fixture contract
- PR-017D controlled real asset metadata smoke test

PR-017D proved only metadata-only smoke flow over synthetic tmp_path fixtures.

PR-017E reviews the next boundary only: controlled PDF text extraction as a possible future Evidence input.

## Main Purpose

PR-017E defines the safety boundary for future controlled PDF text extraction and future Evidence creation.

PR-017E must not implement extraction.

PR-017E must not create evidence.

PR-017E must not touch real assets.

## PDF Text Extraction Boundary Statements

PDF text extraction is not metadata-only.

PDF text extraction is a new permission boundary.

Extracted PDF text is not automatically Evidence.

Extracted PDF text may become Evidence only after passing a later explicit Evidence contract.

PDF text extraction does not create Official Knowledge.

PDF text extraction does not create Product Knowledge.

PDF text extraction does not create Prompt Candidate.

PDF text extraction does not authorize AI inference.

PDF text extraction does not authorize image or OCR interpretation.

PDF text extraction does not authorize broad folder scanning.

## Allowed Future PDF Fixture Scope

The following scope may be discussed for future PR-017 work only. PR-017E does not implement it.

Future controlled PDF text extraction may use:

- exactly 1 controlled product specification PDF fixture
- sandbox copy only
- explicit fixture path only
- fixture must pass ControlledRealAssetFixtureContract
- fixture_type must be product_spec_pdf
- allowed_for_metadata must be True
- allowed_for_pdf_text_extraction must be explicitly reviewed and enabled in a later PR
- allowed_for_evidence must remain False until a separate Evidence contract allows it
- no recursive discovery
- no production RSV folder
- no locked or SSOT docs as mutable fixtures

## Future PDF Text Extraction Result Boundary

A future PDF text extraction result may contain only:

- fixture_id
- source_label
- fixture_path
- extraction_allowed
- extraction_status
- text_length
- text_preview or extracted_text only if later explicitly approved
- extraction_error
- notes

These are policy fields only.

Do not implement them in PR-017E.

## Evidence Boundary

Future Evidence creation from PDF text requires a separate explicit review and contract.

A future PDF Evidence contract should require:

- fixture contract allowed
- PDF extraction contract allowed
- explicit evidence intent
- explicit source traceability
- no automatic Official Knowledge creation
- no automatic Product Knowledge creation
- no automatic Prompt Candidate creation
- no AI inference
- deterministic source reference
- bounded extracted text
- safe error handling

Metadata results are not Evidence.

PDF text extraction results are not automatically Evidence.

Evidence is a separate artifact with separate governance.

Official Knowledge remains manual and governed.

Product Knowledge remains outside PR-017E.

Prompt Candidate remains outside PR-017E.

## Forbidden PDF Sources

Future controlled PDF work must not use:

- production RSV asset folders directly
- locked or SSOT documents as mutable fixtures
- official knowledge base docs
- master asset library docs
- project rulebooks
- architecture baseline docs
- broad product asset directories
- repository root
- current working directory
- user desktop or downloads folders
- auto-discovered folders
- recursive folder trees

## Relationship To Existing Components

ControlledRealAssetFixtureContract remains the first fixture gate.

The PR-016 metadata-only chain remains separate from PDF extraction.

RealFilesystemMetadataAdapter is metadata-only and must not perform PDF extraction.

RealAssetMetadataCollector is metadata-only and must not perform PDF extraction.

Existing PDF extraction modules, if any, must not be connected until a later controlled PR.

CreativeAssetBatchScanner remains outside this workflow.

CreativeAssetTypeDetector remains outside this workflow.

## Recommended Next PR

Recommended next PR:

PR-017F - Controlled PDF Text Extraction Contract

PR-017F should add a value-only contract skeleton first.

PR-017F should not parse PDFs.

PR-017F should not read filesystem.

PR-017F should use synthetic tests only.

A future PR after that may review actual controlled extraction if needed.

## Forbidden Scope For PR-017E

PR-017E forbids:

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
