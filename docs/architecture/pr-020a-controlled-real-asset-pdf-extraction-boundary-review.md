# PR-020A - Controlled Real Asset PDF Extraction Boundary Review

## Status

Documentation-only architecture and boundary review.

## Current checkpoint

- PR-019 is complete and merged.
- The official checkpoint is `main` at `86c2a7f`.
- The official tag is `v0.19.7-rcis-controlled-real-asset-pdf-manual-placement-phase`.
- The PR-019 sandbox PDF was deleted during approved cleanup.
- No sandbox PDF is currently available for extraction.

## Purpose

Review and define the boundary for a future controlled real asset PDF extraction after PR-019 completed manual placement, metadata verification, cleanup, and phase closure.

PR-020A does not execute extraction.

## Scope

PR-020A is a documentation-only architecture and boundary review. It defines prerequisites and restrictions for later controlled real asset PDF extraction review stages.

PR-020A does not approve or perform fresh placement. It does not approve or perform extraction execution.

## Required future prerequisites

A later controlled extraction may be considered only after all of these prerequisites are separately reviewed and approved:

- a fresh, explicitly approved sandbox placement or equivalent approved sandbox-copy source
- one exact sandbox file path with no wildcard
- one controlled PDF only, unless a later batch review explicitly approves otherwise
- metadata verification before extraction
- an explicit extraction execution review before any parser execution
- use of only the existing controlled extraction chain

The production source path must not become RIE input. A missing sandbox PDF is a hard stop, not authority to restore or locate one.

## Existing controlled chain

Any later approved execution must use only this chain:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfTextExtractionContract
-> ControlledPdfTextExtractionExecutionContract
-> ControlledPdfTextExtractionImplementation
-> ControlledPdfTextExtractionResultContractResult
```

PR-020A does not invoke any element of this chain.

## Result boundary

Any future approved result must preserve all of these restrictions:

- `extracted_text` must not be exposed
- `extracted_text_included` must remain `False`
- `evidence_allowed` must remain `False`
- `allow_full_text_storage` must remain `False`
- `allow_evidence_creation` must remain `False`
- parser output remains extraction output only
- `text_preview` is bounded parser output only
- extracted PDF text is not Evidence
- bounded `text_preview` is not Knowledge
- no Prompt Candidate may be created

The result boundary does not authorize storage, promotion, inference, or downstream integration.

## Explicit prohibitions for PR-020A

PR-020A must not:

- copy, restore, move, or place any real PDF
- open PDF content
- read PDF text
- parse or extract PDFs
- create synthetic or real PDF fixtures
- use OCR
- extract or analyze images
- invoke AI
- infer product claims, benefits, personas, layouts, or prompts
- record production source paths
- scan production directories
- perform repository-wide, current-directory, recursive, or wildcard scans
- create Evidence, Knowledge, Product Knowledge, Official Knowledge, or Prompt Candidate
- change dependencies or the virtual environment
- modify locked or SSOT candidate documents
- use `CreativeAssetBatchScanner` or `CreativeAssetTypeDetector`
- run extractor, evidence, knowledge, or prompt modules against real assets
- run real-asset CLI, API, or dashboard flows

PR-020A also does not modify production code, tests, `pyproject.toml`, or lock files.

## Decision

PR-020A approves only the architectural boundary for later review stages.

PR-020A does not approve extraction execution.

The recommended next PR is:

`PR-020B - Controlled Real Asset PDF Fresh Placement for Extraction Review`

PR-020B must also begin as review-only. It must not place or extract a PDF until a later explicit execution step is approved.

## Acceptance criteria

- Only the PR-020A document is changed.
- No source code or tests are changed.
- No real asset exists, is staged, or is committed.
- The sandbox target remains absent.
- Existing architecture separation remains intact.
- The working tree contains only the intended uncommitted documentation file.
