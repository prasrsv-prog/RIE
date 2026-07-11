# PR-020B - Controlled Real Asset PDF Fresh Placement for Extraction Review

## Status

Documentation-only fresh-placement review.

## Current checkpoint

- PR-020A is committed on the phase branch at `46afeef`.
- PR-020A approved only the extraction architecture boundary.
- `main` remains at `86c2a7f`.
- The phase branch has not been merged.
- No official Phase 20 tag exists.
- The sandbox directory may exist locally but is empty.
- The target sandbox PDF is absent.

## Purpose

Review the conditions and exact controlled procedure required for a later fresh placement of one real PDF into the approved sandbox for controlled extraction preparation.

PR-020B does not execute placement and does not approve extraction.

## Scope

PR-020B is a documentation-only fresh-placement review. It defines the required gate for one later manual placement.

PR-020B does not place, copy, restore, locate, scan, open, parse, or extract a PDF. It does not approve extraction execution.

## Exact future sandbox target

The only approved future target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

A later approved execution must:

- use exactly one PDF
- use the exact target path
- prohibit wildcard paths
- prohibit recursive scans
- prohibit current working directory scans
- prohibit repository-wide scans
- prohibit batch placement
- prohibit automatic discovery or copy
- prohibit recording the production source path

Any different target or broader input scope requires a separate review.

## Placement authority boundary

- Placement must be manual or use another separately approved bounded mechanism.
- The user must explicitly select the real PDF outside RIE.
- RIE must not search for or discover the source PDF.
- The production source path must not be written into repository documentation, logs, tests, fixtures, or tracked configuration.
- A later execution PR must be separately approved before placement.
- Absence of the sandbox PDF is a hard stop.

PR-020B does not provide authority to place the file now.

## Required pre-placement checks

A later placement execution PR must confirm:

- the correct phase branch
- the expected HEAD
- a clean working tree before placement
- the sandbox directory exists
- the target file does not exist
- the sandbox directory contains zero files
- the target PDF is not tracked or staged
- no unrelated untracked files exist
- no dependency or virtual-environment changes exist

Failure of any pre-placement check stops placement.

## Required post-placement boundary

After a future approved manual placement, only metadata verification may occur before extraction review:

- exact file count
- exact extension
- byte size
- SHA256
- target-path presence

Post-placement verification must not:

- open PDF content
- read PDF text
- parse PDF objects
- extract text or images
- use OCR
- invoke AI
- create Evidence
- create Knowledge
- create Prompt Candidate

Placement metadata does not authorize content access.

## Real asset Git boundary

- The PDF must remain untracked.
- The PDF must never be staged or committed.
- Documentation commits must not include the PDF.
- `git ls-files --stage` for the target must remain empty.
- Any accidental tracking or staging is a hard stop requiring cleanup review.

## Existing extraction boundary

Fresh placement does not authorize extraction. Extraction requires later metadata verification and an explicit extraction execution review.

Any later approved extraction must use only this existing controlled chain:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfTextExtractionContract
-> ControlledPdfTextExtractionExecutionContract
-> ControlledPdfTextExtractionImplementation
-> ControlledPdfTextExtractionResultContractResult
```

The result boundary remains:

- full `extracted_text` must not be exposed
- `extracted_text_included` must remain `False`
- `evidence_allowed` must remain `False`
- `allow_full_text_storage` must remain `False`
- `allow_evidence_creation` must remain `False`
- extracted PDF text is not Evidence
- bounded `text_preview` is not Knowledge
- no Prompt Candidate may be created

## Explicit prohibitions for PR-020B

PR-020B must not:

- copy, restore, move, or place a real PDF
- request or reveal a production source path
- scan production directories
- use wildcard, recursive, repository-wide, or current-directory scans
- open PDF content
- read or extract PDF text
- create PDF fixtures
- invoke parser execution
- use OCR
- extract or analyze images
- invoke AI
- infer product claims, benefits, personas, layouts, or prompts
- create Evidence, Knowledge, Official Knowledge, Product Knowledge, or Prompt Candidate
- modify source code, tests, dependencies, the virtual environment, or locked documents
- use `CreativeAssetBatchScanner` or `CreativeAssetTypeDetector`
- run real-asset extractor, evidence, knowledge, prompt, CLI, API, or dashboard flows

## Decision

PR-020B may approve only a future fresh-placement execution gate.

PR-020B does not approve placement itself and does not approve extraction.

The recommended next PR is:

`PR-020C - Controlled Real Asset PDF Fresh Placement Execution`

PR-020C may occur only after PR-020B review and commit approval.

## Acceptance criteria

- Only the PR-020B document is changed.
- No real PDF is present.
- The sandbox remains empty.
- The target remains absent.
- No real asset is tracked or staged.
- No source code, tests, dependencies, or locked documents change.
- The working tree contains only the intended uncommitted PR-020B document.
