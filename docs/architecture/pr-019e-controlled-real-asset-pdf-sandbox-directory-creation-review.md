# PR-019E - Controlled Real Asset PDF Sandbox Directory Creation Review

## Status

Docs-only sandbox directory creation review.

## Current checkpoint

- Tag: `v0.19.3-rcis-controlled-real-asset-pdf-sandbox-copy-placement-review`
- Commit: `cd797f7 docs: review controlled real asset pdf sandbox copy placement`

## Purpose

Review the readiness criteria and exact future command boundary for creating the approved real asset PDF sandbox directory without creating, inspecting, copying, parsing, or processing any real asset in PR-019E.

PR-019E is a review gate only. It does not authorize directory creation execution.

## PR-019E boundary

PR-019E:

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

PR-019C approved future-only smoke test verification commands. Verification must not parse PDF content, read PDF text, or create Evidence, Knowledge, or Prompt Candidate. PR-019C did not create or inspect the sandbox directory.

### PR-019D

PR-019D approved the placement readiness review. Placement is not extraction, future placement requires explicit user approval, and the production source path must never become RIE input. PR-019D did not create or inspect the sandbox directory.

## Directory creation review objective

PR-019E defines readiness requirements for a later directory creation execution PR.

Future directory creation may be considered only if:

- the user explicitly approves moving from review to directory creation
- the branch is approved
- the working tree is clean
- the exact sandbox path remains approved
- no real RSV PDF is copied during directory creation
- no PDF parsing occurs during directory creation
- no PDF text extraction occurs during directory creation
- no production folder is scanned
- no recursive scan is performed
- no batch operation is performed
- no Evidence, Knowledge, or Prompt Candidate path is enabled

Failure of any readiness requirement stops future directory creation.

## Approved future sandbox directory

The only approved future directory remains:

```text
sandbox/real_asset_pdf_smoke/
```

Directory creation rules:

- create only the approved sandbox directory
- do not create nested production-like structure
- do not mirror production folders
- do not copy any PDF into the directory
- do not move any PDF into the directory
- do not inspect any production folder
- do not scan the repository
- do not scan the current working directory
- do not recursively enumerate files
- do not create Evidence, Knowledge, or Prompt Candidate
- keep the directory empty after creation unless a later PR separately approves placement

## Future-only directory creation command

The following PowerShell command is for a later approved execution PR only. It must not be run in PR-019E.

```powershell
New-Item -ItemType Directory -Force -Path "sandbox\real_asset_pdf_smoke"
```

Rules for the future command:

- It must target only `sandbox\real_asset_pdf_smoke`.
- It must not target a production path.
- It must not use wildcards.
- It must not recurse.
- It must not copy any files.
- It must not parse PDFs.
- It must not read PDF text.
- It must not create Evidence, Knowledge, or Prompt Candidate.

## Future-only post-creation verification commands

The following PowerShell commands are for a later approved execution PR only. They must not be run in PR-019E.

```powershell
Test-Path "sandbox\real_asset_pdf_smoke"

Get-ChildItem "sandbox\real_asset_pdf_smoke" -Force

git status --short -uall
```

Rules for future verification:

- It must verify the approved sandbox directory exists.
- It must verify no PDF has been copied yet.
- It must verify no extra file is present unless explicitly approved.
- It must verify Git status afterward.
- It must not inspect production folders.
- It must not parse PDFs.
- It must not read PDF text.
- It must not expose `extracted_text`.

## Expected future result

A future directory creation execution PR may proceed only if:

- the directory exists at `sandbox/real_asset_pdf_smoke/`
- the directory is empty after creation
- no real RSV PDF is copied
- no real RSV asset is touched
- no production path is used as RIE input
- Git status is reviewed after creation
- no Evidence, Knowledge, or Prompt Candidate is created

## Stop conditions

Future directory creation must stop if:

- the working tree is not clean
- the approved path changes
- the command would create a production-like folder mirror
- the command would target a production path
- the command would use a wildcard
- the command would recursively create or inspect broader paths
- the command would copy or move a PDF
- the command would parse PDF content
- the command would expose `extracted_text`
- the command would create Evidence, Knowledge, or Prompt Candidate

## Future placement boundary

Directory creation is not placement.

Even after a future sandbox directory creation succeeds:

- no real RSV PDF may be copied automatically
- no placement is automatically allowed
- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later placement PR must explicitly approve placing one PDF into the directory

## Future execution boundary

Directory creation is not extraction.

If a later execution PR is approved after placement, it may process only the approved sandbox-copy PDF through this chain:

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

A later directory creation or placement PR must decide whether the empty sandbox directory is:

- retained for the next placement PR, or
- deleted if the process is paused or cancelled

It is acceptable to retain the empty sandbox directory only if a later execution PR explicitly approves creation and Git status confirms no tracked real asset file.

Cleanup must:

- target only `sandbox/real_asset_pdf_smoke/`
- not delete production files
- not recursively delete broader paths
- verify Git status afterward

PR-019E itself must not create or delete any sandbox file or directory.

## Forbidden scope

The following remain forbidden:

- creating the sandbox directory in PR-019E
- inspecting the sandbox directory in PR-019E
- copying any real asset in PR-019E
- parsing any real PDF in PR-019E
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

### Review becomes directory creation execution

Documentation work could drift into running the future creation command. Directory creation requires separate explicit approval and a later execution PR.

### Wrong directory path is created

A typo or broader path could create a directory outside the approved boundary. The later command must use only the exact approved relative path.

### Production-like structure is mirrored

Creating nested folders modeled on production could turn the sandbox into a production mirror. Only the single approved directory may be created.

### PDF is copied during directory creation

Directory creation could be combined with placement. The directory must remain empty, and placing a PDF requires separate approval.

### Verification drifts into file scanning

Post-creation verification could expand beyond the exact directory. It must be non-recursive, limited to the approved sandbox path, and must not inspect production folders.

### Sandbox becomes a batch input

Later code could treat the directory as a discovery root. The approved boundary is one exact sandbox-copy path, never a batch or folder input.

### Directory creation is mistaken for placement approval

An empty directory does not authorize copying a real PDF. Placement remains a separate gated action.

### Directory creation is mistaken for extraction approval

Creating an empty directory does not authorize PDF parsing, extraction, Evidence, Knowledge, or Prompt Candidate creation.

## Recommended next PR

`PR-019F - Controlled Real Asset PDF Sandbox Directory Creation Execution`

PR-019F may be a very small execution step if approved. It may create only the empty sandbox directory.

It must not copy a real PDF, parse any PDF, or create Evidence, Knowledge, or Prompt Candidate.

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
- No commit is created by PR-019E preparation.
