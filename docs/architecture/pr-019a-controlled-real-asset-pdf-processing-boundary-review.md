# PR-019A - Controlled Real Asset PDF Processing Boundary Review

## Status

Docs-only real asset PDF processing boundary review.

## Current checkpoint

- Tag: `v0.18.8-rcis-controlled-pdf-text-extraction-phase-closure`
- Commit: `15eddc2 docs: close controlled pdf text extraction phase`

## Purpose

Review the boundary for future controlled processing of one manually selected real RSV PDF asset copied into a sandbox.

PR-019A documents constraints only. It does not authorize real asset copying or processing.

## PR-019A boundary

PR-019A:

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

## PR-018 closure context

PR-018 closed synthetic-only PDF extraction validation with these results:

- `pypdf` was validated in the local `.venv`.
- The validated `pypdf` version was `6.14.2`.
- Synthetic blank PDF parser execution returned `empty`.
- Synthetic text-bearing PDF extraction returned `extracted`.
- The final result did not expose `extracted_text`.
- `extracted_text_included` remained `False`.
- `evidence_allowed` remained `False`.
- No real RSV assets were touched.

PR-018 did not authorize processing of real RSV assets.

## Future real asset boundary

Future real asset PDF processing may be considered only when all of these conditions are satisfied:

- The user manually selects the file.
- The user manually copies the file into an approved sandbox location.
- The first smoke test uses exactly one PDF.
- The source production asset folder is not scanned.
- The source production asset folder is not used as processing input.
- No recursive scan is performed.
- No folder scan is performed.
- No repository-wide scan is performed.
- No current working directory scan is performed.
- The original asset is not mutated.
- No automatic Evidence is created.
- No automatic Knowledge is created.
- No automatic Prompt Candidate is created.
- Full `extracted_text` is not exposed.
- Only a bounded `text_preview` may be reported.
- Source trace identifies the input as a sandbox copy.

Meeting these conditions requires approval in a later PR. PR-019A itself does not permit a copy or processing run.

## Sandbox-copy policy required for a future PR

Before any real asset is copied or processed, a future PR must specify:

- the exact sandbox directory
- an allowed file count of `1`
- an allowed file type of PDF only
- a manual, user-controlled copy method
- no automatic copying from a production folder
- no batch copy
- no folder sync
- no recursive copy
- no overwrite of existing sandbox files without review
- a cleanup policy
- a file naming policy
- whether a hash or size record is required
- a rollback plan

The sandbox copy must remain distinguishable from the original production asset, and the original must remain unchanged.

## Allowed future execution chain

A later approved PR may process one sandbox-copy PDF only through this chain:

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

## Forbidden scope

The following remain forbidden:

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

### Accidental production folder scanning

A broad input path or discovery mechanism could scan production assets beyond the single approved file. The future boundary must accept only one exact sandbox-copy path and must not discover inputs from a folder, repository root, or current working directory.

### Accidental full text exposure

Parser output could leak through result objects, logs, errors, debugging output, or test artifacts. The future result contract must exclude full `extracted_text` and allow only a bounded `text_preview`.

### Premature Evidence creation

Successful extraction does not make extracted text Evidence. The future execution must keep `evidence_allowed` and `allow_evidence_creation` as `False` and must not route output into an Evidence path.

### Product information leaking into Knowledge

Real RSV text may contain product claims or benefits. Extraction output and its bounded preview must not be interpreted, classified, promoted, or routed into Official Knowledge, Product Knowledge, or any other Knowledge boundary.

### Uncontrolled file selection

Automatic selection, globbing, folder traversal, or accepting multiple paths could process an unintended asset. Selection and copying must remain manual and user-controlled, with exactly one reviewed PDF in the sandbox.

### Environment dependency mismatch

`pypdf` is available locally but is unlocked. A different environment may provide a missing or different version. A future execution review must verify the exact Python executable, successful `pypdf` import, and installed version without installing or changing dependencies as part of the review.

## Recommended next PR

`PR-019B - Controlled Real Asset PDF Sandbox-Copy Execution Review`

PR-019B should remain docs-only first. Before any real asset copy or processing occurs, it should define:

- the exact sandbox path
- the manual copy procedure
- the allowed filename pattern
- the cleanup rule
- the verification commands
- the no-mutation guarantee

No real asset execution should proceed until that review is approved.

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
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019A preparation.