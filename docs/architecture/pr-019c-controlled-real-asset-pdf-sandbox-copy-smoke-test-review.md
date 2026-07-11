# PR-019C - Controlled Real Asset PDF Sandbox-Copy Smoke Test Review

## Status

Docs-only sandbox-copy smoke test review.

## Current checkpoint

- Tag: `v0.19.1-rcis-controlled-real-asset-pdf-sandbox-copy-execution-review`
- Commit: `95149e4 docs: review controlled real asset pdf sandbox copy execution`

## Purpose

Define the future smoke test checklist and verification commands for one manually placed real RSV PDF sandbox copy without creating, copying, parsing, or processing any real asset in PR-019C.

PR-019C documents future-only steps. It does not authorize sandbox creation, sandbox inspection, real asset placement, verification, or processing.

## PR-019C boundary

PR-019C:

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

PR-019A approved the future boundary for one manually selected real RSV PDF sandbox copy. It prohibited:

- direct production asset processing
- folder scans
- recursive scans
- Evidence creation
- Knowledge creation
- Prompt Candidate creation
- full `extracted_text` exposure

### PR-019B

PR-019B approved the future sandbox-copy procedure with:

- future sandbox directory: `sandbox/real_asset_pdf_smoke/`
- future sandbox filename: `real-asset-smoke-source.pdf`
- manual user-controlled copy only
- no automatic copy from production folders
- no folder sync
- no recursive copy
- no batch copy
- no use of the original production RSV asset as program input

PR-019C defines the future verification gate for that procedure without executing it.

## Future smoke test objective

The future smoke test may prove only that:

- exactly one sandbox-copy PDF exists at the approved target path
- the file extension is PDF
- the file size is greater than zero
- optional size and hash values can be recorded
- the sandbox-copy path can be passed as a controlled fixture path in a later approved execution PR
- no production source path is used
- no folder scan is required

The future smoke test must not prove:

- product claim extraction
- product benefit extraction
- layout understanding
- image extraction
- OCR
- Evidence creation
- Knowledge creation
- Prompt Candidate creation
- final prompt generation
- official product knowledge correctness

## Future approved target path

The only approved future target path is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The following rules apply:

- exactly one file
- PDF only
- no sidecar files
- no images
- no archives
- no nested folders
- no production folder mirror
- no product name in the filename
- no customer data in the filename
- no campaign name in the filename
- no production path encoded in the filename
- no overwrite without review

## Future preflight checklist

Before a later PR asks the user to place the PDF manually, that PR must verify:

- the current branch is `main` or an approved PR branch
- the Git working tree is clean
- the official checkpoint is known
- `pypdf` import succeeds
- the `pypdf` version is recorded
- the sandbox policy from PR-019B remains active
- no real asset path is supplied to RIE
- no production folder is supplied to RIE
- no wildcard path is used
- no recursive scan is planned
- no batch copy is planned
- no Evidence, Knowledge, or Prompt Candidate path is enabled

Failure of any preflight item stops the future placement and smoke test.

## Future manual placement step

A later approved PR may instruct the user to place exactly one manually selected RSV PDF at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The user must perform the copy manually outside RIE execution. PR-019C itself must not create the directory or perform, verify, or inspect this placement.

## Future-only verification commands

The following PowerShell commands are examples for a later approved PR only. They must not be run in PR-019C.

```powershell
$Target = "sandbox\real_asset_pdf_smoke\real-asset-smoke-source.pdf"
$Dir = "sandbox\real_asset_pdf_smoke"

Test-Path $Dir
Test-Path $Target

Get-ChildItem $Dir -File

(Get-ChildItem $Dir -File).Count

Get-Item $Target | Select-Object FullName, Length, Extension

Get-FileHash $Target -Algorithm SHA256
```

Rules for those future commands:

- They must target only the approved sandbox directory and file.
- They must not target a production path.
- They must not use wildcards.
- They must not recurse.
- They must not parse the PDF.
- They must not read PDF text.
- They must not create Evidence, Knowledge, or Prompt Candidate.

## Expected future verification result

A future smoke test may proceed only if:

- `Test-Path` for the directory returns `True`
- `Test-Path` for the target file returns `True`
- `Get-ChildItem $Dir -File` returns exactly one file
- the file extension is `.pdf` or `.PDF`
- the file length is greater than zero
- the hash is recorded for audit
- Git status does not show the sandbox PDF as tracked or staged
- no production path appears in command output except in user-facing manual notes, never as RIE input

## Stop conditions

The future smoke test must stop if:

- more than one file exists in the sandbox directory
- the target file is missing
- the target file is not PDF
- the target file size is zero
- any nested folder exists
- any sidecar file exists
- any wildcard path is needed
- any recursive command is needed
- any production source path is about to be used as program input
- any command would parse PDF content
- any command would expose `extracted_text`
- any command would create Evidence, Knowledge, or Prompt Candidate

## Future execution boundary

A later approved execution PR may process only the approved sandbox-copy PDF through this chain:

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

## Future cleanup rule

The default cleanup after the later smoke test is:

- delete only `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- do not recursively delete broader paths
- do not delete production files
- verify Git status afterward
- remove or keep the empty sandbox directory only if a later PR explicitly defines that behavior

PR-019C itself must not delete any sandbox file or directory.

## Forbidden scope

The following remain forbidden:

- creating the sandbox directory in PR-019C
- inspecting the sandbox directory in PR-019C
- copying any real asset in PR-019C
- parsing any real PDF in PR-019C
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

### Production path used by a future command

A future command could accidentally target or expose the production asset path. Future verification and execution must accept only the approved sandbox path, and the production path must never become RIE input.

### Recursive verification

A future directory check could expand into recursive enumeration. Verification must stay non-recursive and limited to the exact approved sandbox directory and target file.

### More than one sandbox file

An extra PDF, sidecar, image, archive, or other file would violate the single-file boundary. The future smoke test must stop unless exactly one approved PDF is present.

### Sandbox PDF tracked by Git

The real asset copy could be staged or committed accidentally. The future review must confirm the sandbox PDF remains untracked and unstaged, and must stop if that condition is violated.

### Asset retained longer than intended

The sandbox PDF could remain after its approved review window. The default policy is deletion of the exact sandbox PDF after the later smoke test unless temporary retention is explicitly approved.

### PDF parsing mixed into verification

Metadata verification could drift into opening or parsing PDF content. The future verification commands must be limited to path, count, extension, byte size, and optional hash checks.

### Full text exposed too early

A future parser result, log, error, or debugging path could expose full extracted text. Any later execution must exclude `extracted_text` and permit only a bounded `text_preview`.

### Extracted preview treated as Knowledge

A bounded parser preview could be interpreted or promoted as Knowledge. The preview must remain extraction output only and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

## Recommended next PR

`PR-019D - Controlled Real Asset PDF Sandbox-Copy Placement Review`

PR-019D should remain a review gate first. It should decide whether to create the sandbox directory and manually place one real RSV PDF in it.

No parsing should occur until a later approved execution PR.

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
- No commit is created by PR-019C preparation.