# PR-019D - Controlled Real Asset PDF Sandbox-Copy Placement Review

## Status

Docs-only sandbox-copy placement review.

## Current checkpoint

- Tag: `v0.19.2-rcis-controlled-real-asset-pdf-sandbox-copy-smoke-test-review`
- Commit: `028468d docs: review controlled real asset pdf sandbox copy smoke test`

## Purpose

Review the readiness criteria for a future manual placement of exactly one real RSV PDF into the approved sandbox path without creating, inspecting, copying, parsing, or processing any real asset in PR-019D.

PR-019D is a review gate only. It does not authorize placement execution.

## PR-019D boundary

PR-019D:

- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not create PDF fixtures
- does not extract PDF text
- does not create the sandbox directory
- does not inspect the sandbox directory
- does not touch real RSV assets
- does not copy real RSV assets
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## Prior review context

### PR-019A

PR-019A approved the future real asset PDF processing boundary. It prohibited direct production asset processing, folder scans, recursive scans, Evidence, Knowledge, Prompt Candidate, and full `extracted_text` exposure.

### PR-019B

PR-019B approved the future sandbox-copy procedure with:

- future sandbox directory: `sandbox/real_asset_pdf_smoke/`
- future sandbox filename: `real-asset-smoke-source.pdf`
- manual, user-controlled copy only
- no automatic copy from production folders
- no folder sync
- no recursive copy
- no batch copy
- no use of the original production RSV asset as program input

### PR-019C

PR-019C approved future-only smoke test verification commands for this target:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Verification must not parse PDF content, read PDF text, or create Evidence, Knowledge, or Prompt Candidate. PR-019C did not create or inspect the sandbox directory.

## Placement review objective

PR-019D defines the readiness requirements for a later placement execution PR.

Future placement may be considered only if:

- the user explicitly approves moving from review to placement
- the branch is approved
- the working tree is clean
- the exact sandbox path remains approved
- the user manually selects exactly one real RSV PDF
- the selected source PDF is not opened by RIE
- the selected source PDF is not parsed by RIE
- the selected source PDF path is not passed to RIE as input
- the user manually copies the selected PDF outside RIE execution
- the target filename is neutral
- the target path is the only approved sandbox path
- no production folder scan is required
- no recursive scan is required
- no batch copy is required

Failure of any readiness requirement stops future placement.

## Approved future sandbox target

The only approved future target remains:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Placement rules:

- exactly one PDF only
- manual copy by the user only
- neutral target filename only
- no product name in the filename
- no customer data in the filename
- no campaign name in the filename
- no production folder path in the filename
- no automatic script copy
- no copy from RIE
- no wildcard source path
- no folder source path
- no recursive copy
- no batch copy
- no overwrite without review

## Production asset protection

The original production RSV PDF must:

- not be opened by RIE
- not be parsed by RIE
- not be renamed
- not be moved
- not be modified
- not be deleted
- not be used as program input
- not be used as a fixture path
- not be included in logs
- not be committed
- remain outside the repository unless the user manually copies it into the approved sandbox path

The production source path must never become RIE input.

## Future user instruction boundary

A later approved PR may provide a user-facing manual placement instruction, but it must:

- instruct the user to copy only one PDF
- instruct the user to rename it to `real-asset-smoke-source.pdf`
- instruct the user to place it only in `sandbox/real_asset_pdf_smoke/`
- not ask the user to provide a production folder path to RIE
- not ask the user to run recursive commands
- not ask the user to run wildcard commands
- not ask the user to parse or inspect PDF text
- not ask the user to upload or commit the real PDF to Git

PR-019D itself provides no placement execution instruction.

## Future verification after placement

A later approved PR may verify only:

- the target directory exists
- the target file exists
- exactly one file exists in the target directory
- the target file extension is `.pdf` or `.PDF`
- the target file size is greater than zero
- an optional SHA256 hash is recorded
- an optional byte size is recorded
- the sandbox PDF is not tracked or staged by Git
- no extra sidecar files exist
- no nested folders exist

Future verification must not:

- parse PDF content
- read PDF text
- expose `extracted_text`
- call AI
- run OCR
- extract images
- infer product claims
- infer product benefits
- create Evidence
- create Knowledge
- create Prompt Candidate

## Stop conditions

Future placement must stop if:

- the working tree is not clean
- more than one file is selected
- the selected source is not a PDF
- the selected source is a folder
- a wildcard is needed
- a recursive command is needed
- a batch copy is attempted
- the target file already exists and overwrite is not explicitly reviewed
- the production source path is about to be used as RIE input
- any command would parse PDF content
- any command would expose `extracted_text`
- any command would create Evidence, Knowledge, or Prompt Candidate

## Future execution boundary

Placement is not extraction.

Even after a future placement succeeds:

- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later execution PR must explicitly approve any parser run

If a later execution PR is approved, it may process only the approved sandbox-copy PDF through this chain:

```text
ControlledRealAssetFixtureContract
-> ControlledPdfTextExtractionContract
-> ControlledPdfTextExtractionExecutionContract
-> ControlledPdfTextExtractionImplementation
-> ControlledPdfTextExtractionResultContractResult
```

The future result must:

- not expose `extracted_text`
- keep `extracted_text_included` as `False`
- keep `evidence_allowed` as `False`
- keep `allow_full_text_storage` as `False`
- keep `allow_evidence_creation` as `False`
- report only status, `text_length`, bounded `text_preview`, and errors
- treat extracted PDF text as extraction output only, not Evidence
- treat `text_preview` as bounded parser output only, not Knowledge

## Cleanup boundary

A later placement or smoke-test PR must decide whether the sandbox copy is:

- deleted after verification, or
- temporarily retained for a later approved execution PR

The default policy is to delete the sandbox copy after its approved review window unless temporary retention is explicitly approved.

Cleanup must:

- target only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- not delete production files
- not recursively delete broader paths
- verify Git status afterward

PR-019D itself must not delete any sandbox file or directory.

## Forbidden scope

The following remain forbidden:

- creating the sandbox directory in PR-019D
- inspecting the sandbox directory in PR-019D
- copying any real asset in PR-019D
- parsing any real PDF in PR-019D
- production RSV folder scan
- direct production asset processing
- multiple real assets
- recursive scan
- current working directory scan
- repository-wide scan
- automatic copy from production folders
- batch processing
- full `extracted_text` exposure
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
- locked or SSOT document mutation

## Risk review

### Review becomes placement execution

Documentation work could drift into creating the directory or copying the asset. Placement requires separate explicit user approval and a later approved PR.

### More than one PDF is copied

Multi-select, batch, wildcard, or folder copy behavior could exceed the single-file boundary. Future placement must be one manual user action for exactly one PDF.

### Target file overwrite

An existing sandbox file could be replaced without knowing its identity or review state. Future placement must stop before overwrite unless the exact overwrite is explicitly reviewed.

### Production source path becomes program input

The original production path could be passed to RIE instead of the sandbox copy path. The production path must never be used as input, a fixture path, or log content.

### Sandbox PDF becomes tracked or staged

The real PDF could be staged or committed accidentally. Future verification must confirm that the sandbox PDF remains untracked and unstaged.

### Verification drifts into parsing

Path, count, extension, size, and hash checks could drift into opening PDF content. Verification must remain metadata-only until a later execution PR explicitly approves parsing.

### Retained PDF is forgotten

A temporarily retained real PDF could remain beyond its approved review window. Retention must be explicit, and the default policy remains deletion of the exact sandbox copy.

### Preview or extracted text becomes Evidence or Knowledge

Extraction output could be promoted prematurely. Any later preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

## Recommended next PR

`PR-019E - Controlled Real Asset PDF Sandbox Directory Creation Review`

PR-019E should remain a review gate or a very small execution step. It should decide whether to create the approved sandbox directory.

It must not copy a real PDF unless separately approved. It must not parse any PDF or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Only one docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF fixture is created.
- No sandbox directory is created.
- No sandbox directory is inspected.
- No real RSV asset is touched, copied, or scanned.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019D preparation.