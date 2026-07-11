# PR-019B - Controlled Real Asset PDF Sandbox-Copy Execution Review

## Status

Docs-only sandbox-copy execution review.

## Current checkpoint

- Tag: `v0.19.0-rcis-controlled-real-asset-pdf-processing-boundary-review`
- Commit: `cbb0bc7 docs: review controlled real asset pdf processing boundary`

## Purpose

Define the exact manual sandbox-copy procedure for a future single real RSV PDF smoke test without copying or processing any real asset in PR-019B.

PR-019B documents the procedure only. It does not authorize a real asset copy, verification, or processing run.

## PR-019B boundary

PR-019B:

- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not create PDF fixtures
- does not extract PDF text
- does not touch real RSV assets
- does not copy real RSV assets
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## PR-019A context

PR-019A approved the boundary for future controlled processing of one manually selected real RSV PDF sandbox copy. It did not allow direct production asset processing.

PR-019A required:

- manual file selection by the user
- a manual, user-controlled copy
- exactly one PDF
- no folder scan
- no recursive scan
- no Evidence creation
- no Knowledge creation
- no Prompt Candidate creation
- no full `extracted_text` exposure

PR-019B narrows that boundary into an exact future sandbox-copy procedure but does not execute the procedure.

## Approved future sandbox directory

The approved sandbox directory for a future smoke test is:

```text
sandbox/real_asset_pdf_smoke/
```

The following rules apply:

- The directory is for one manually copied PDF only.
- It must not contain production folders.
- It must not mirror any production folder structure.
- It must not be used for batch processing.
- It must be checked before use.
- It must be cleaned after the future smoke test unless explicitly retained for review.
- Files in the directory must remain untracked unless a later PR explicitly approves otherwise.

PR-019B does not create, inspect, or modify this directory.

## Allowed future file count and type

The future sandbox may contain exactly `1` PDF file.

The file rules are:

- PDF only
- extension must be `.pdf` or `.PDF`
- no images
- no folders
- no archives
- no sidecar files

Any other file count or file type is outside the approved boundary.

## Allowed future filename policy

The manually copied file should be renamed to this neutral sandbox name:

```text
real-asset-smoke-source.pdf
```

The filename must contain:

- no product name
- no customer data
- no campaign name
- no production folder path

The target file must not be overwritten without review.

## Manual copy policy

A future PR may ask the user to manually copy one selected RSV PDF to:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The user must perform that copy manually and outside RIE execution. PR-019B itself must not perform the copy.

The following copy methods are prohibited:

- automatic copy from a production folder
- script-based copy from a production folder
- folder sync
- recursive copy
- dragging in multiple files
- glob patterns
- wildcard paths
- batch operations

## Pre-copy checklist for a future PR

Before a future manual copy, the review must:

- confirm the branch is `main` or an approved PR branch
- confirm the Git working tree is clean
- confirm the sandbox directory policy is approved
- confirm the user manually selected exactly one source PDF
- confirm the source file was not opened or parsed by RIE before the manual copy
- confirm the target path is empty or reviewed before overwrite
- confirm no folder scan is required
- confirm no production path will be used as program input

Failure of any checklist item stops the future copy procedure.

## Future verification after manual copy

A future PR may verify only:

- the approved sandbox directory exists
- exactly one PDF exists at the approved target path
- the file size is greater than zero
- the file extension is PDF
- an optional hash is recorded
- an optional byte size is recorded
- Git status remains clean except for any approved documentation or test changes

No PDF parsing is allowed during verification unless a later execution PR explicitly approves it.

## Future processing boundary

A future approved execution PR may process only the sandbox-copy PDF through this chain:

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

## Cleanup policy

A future PR must define whether the sandbox copy is:

- deleted after the smoke test, or
- temporarily retained for manual review

The default policy is to delete the sandbox-copy PDF after the future smoke test.

Cleanup must:

- not delete production files
- target only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- not recursively delete broader paths
- verify Git status afterward

Any temporary retention must be explicit, reviewed, and bounded. PR-019B neither creates nor deletes the sandbox copy.

## No-mutation guarantee

The original production RSV asset must:

- never be opened as input by RIE
- never be modified
- never be renamed
- never be moved
- never be deleted
- never be used as a processing path
- only be manually copied by the user outside RIE execution

All future verification and processing must target the approved sandbox copy, never the production source path.

## Forbidden scope

The following remain forbidden:

- copying any real asset in PR-019B
- parsing any real PDF in PR-019B
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

### Accidental overwrite of the sandbox file

An existing sandbox file could be replaced without confirming its identity or review status. The future procedure must check the exact target path and stop before any unreviewed overwrite.

### Accidental use of the production source path

The production path could be passed directly to RIE instead of the sandbox path. Future verification and execution must accept only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf` as input.

### Accidental batch copy

A multi-select action, wildcard, sync, or script could copy more than the approved file. The copy must be a single manual user action for exactly one selected PDF.

### Accidental folder scan

Directory enumeration or input discovery could inspect files outside the exact target. Future checks must address the exact sandbox path only and must not scan a production folder, repository root, or current working directory.

### Accidental retention of the real asset copy

An untracked sandbox copy could remain after the smoke test. The default cleanup rule is deletion of the exact sandbox-copy file, followed by Git status verification. Retention requires explicit review.

### Accidental full text exposure

Parser output could leak through results, logs, errors, or debugging output. Any future execution must exclude full `extracted_text` and report only a bounded `text_preview`.

### Premature Evidence or Knowledge creation

Successful extraction does not make the output Evidence or Knowledge. The future flow must keep evidence creation disabled and must not route extraction output or previews into Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

## Recommended next PR

`PR-019C - Controlled Real Asset PDF Sandbox-Copy Smoke Test Review`

PR-019C should still be docs-only first or a very small review step before any real PDF parsing. It should confirm the exact commands and checks for manually placing one PDF in the sandbox.

If execution is approved later, it must process only the sandbox copy and must not expose `extracted_text` or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Only one docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF fixture is created.
- No real RSV asset is touched, copied, or scanned.
- Sandbox directory is not created, inspected, or modified by PR-019B.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019B preparation.