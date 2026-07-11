# PR-020E - Controlled Real Asset PDF Extraction Execution Review

## Status

- Controlled real asset PDF extraction execution review.
- Documentation-only.
- Extraction not yet authorized or executed.

## Current checkpoint

- Branch: `phase-020-real-asset-pdf-extraction`
- Pre-review HEAD: `8268cba`
- `main` remains at `86c2a7f`.
- PR-020A through PR-020D are committed on the phase branch.
- The phase branch is not merged.
- No official Phase 20 tag exists.
- Exact target: `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- Target directory exists: `True`
- Target exists: `True`
- Sandbox item count: `1`
- Filename: `real-asset-smoke-source.pdf`
- Extension: `.pdf`
- Byte size: `987120`
- SHA256: `E65168E219E41868D0DEB408F6D636BABDC7EC7DB8C8F6BCCA812B4EAF2079BF`
- The PDF remains local, untracked, and unstaged.

The metadata matches PR-020C and PR-020D. Any metadata or Git-state mismatch is a hard stop.

## Purpose

Review and define the exact bounded conditions required for one later controlled extraction execution against the already verified sandbox PDF.

PR-020E must not and does not execute extraction.

## Execution scope under review

A later explicitly approved execution may:

- target exactly one PDF
- use exactly the approved sandbox path
- invoke only the existing controlled extraction chain
- run one bounded parser execution
- produce only the approved bounded result contract

A later execution must not:

- use wildcard paths
- scan the current directory
- scan the repository
- recurse
- batch process
- discover another asset
- read from a production path
- mutate, move, rename, replace, or delete the PDF
- write extracted full text to disk, logs, documentation, tests, fixtures, or tracked output

No broader execution authority is approved.

## Exact controlled extraction chain

The only approved chain for a later execution is:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfTextExtractionContract
-> ControlledPdfTextExtractionExecutionContract
-> ControlledPdfTextExtractionImplementation
-> ControlledPdfTextExtractionResultContractResult
```

No alternate extractor, CLI, API, dashboard, batch scanner, or downstream workflow may be used.

## Required pre-execution checks for PR-020F

Before parser execution, a later execution PR must verify:

- the correct branch
- the expected HEAD
- the exact target exists
- the sandbox contains exactly one item
- the filename, extension, byte size, and SHA256 still match
- the PDF is untracked and unstaged
- only the approved execution command will run
- the active Python executable is the repository `.venv`
- `pypdf` is importable
- the installed `pypdf` version is recorded
- no dependency installation or virtual-environment mutation is required
- no unrelated tracked or untracked changes exist except the approved local PDF

Failure of any check stops execution.

## Approved result boundary

A later execution may expose only bounded result fields already approved by `ControlledPdfTextExtractionResultContractResult`, including applicable parser status, text length, bounded text preview, and errors.

The existing result contract is the source of allowed fields. PR-020E does not invent or approve new result fields.

The result must preserve:

- full `extracted_text` is not exposed
- `extracted_text_included` is `False`
- `evidence_allowed` is `False`
- `allow_full_text_storage` is `False`
- `allow_evidence_creation` is `False`
- parser output is extraction output only
- `text_preview` is bounded parser output only
- extracted PDF text is not Evidence
- bounded `text_preview` is not Knowledge
- no Prompt Candidate is created

## Output handling boundary

- Do not redirect full text to files.
- Do not print or log full extracted text.
- Do not store parser internals.
- Do not add generated output files to the repository.
- Execution output must be reviewed in the terminal only and recorded later only as bounded facts.
- Any unexpected full-text exposure is a hard stop requiring cleanup review.

## Content and downstream prohibitions

A later execution must not:

- use OCR
- extract images
- analyze layout
- infer product names, claims, benefits, specifications, personas, or prompts
- invoke AI
- create Evidence
- create Evidence Candidate
- create Knowledge
- create Product Knowledge
- create Official Knowledge
- create Prompt Candidate
- update a knowledge repository
- call extractor, evidence, knowledge, or prompt modules outside the approved chain

Extraction output must remain isolated from downstream semantic layers.

## Real asset Git boundary

- The PDF remains untracked.
- The PDF must never be staged or committed.
- Execution must not modify the PDF.
- Any accidental tracking, staging, mutation, or deletion is a hard stop.
- Only the PR-020E document may later be committed from this review step.

## PR-020E prohibitions

PR-020E does not:

- execute a parser
- open, read, parse, or extract PDF content
- invoke `pypdf`
- create output artifacts
- modify source code, tests, dependencies, the virtual environment, or locked documents
- create Evidence, Knowledge, or Prompt Candidate
- stage or commit any file
- push, merge, or tag

## Decision

PR-020E may approve only the bounded conditions for a later execution.

PR-020E does not itself execute extraction.

The recommended next PR is:

`PR-020F - Controlled Real Asset PDF Extraction Execution`

PR-020F may run only after PR-020E document review, commit, push, and explicit execution approval.

## Acceptance criteria

- Only the PR-020E document changes.
- No parser execution occurs.
- No PDF content is accessed.
- PDF metadata and Git state remain unchanged.
- Exactly one PDF remains at the exact sandbox target.
- The PDF remains untracked and unstaged.
- No source code, tests, dependencies, virtual environment, or locked documents change.
- No Evidence, Knowledge, or Prompt Candidate changes.
- The working tree contains only the untracked PR-020E document and the approved untracked local PDF.
