# PR-019F - Controlled Real Asset PDF Sandbox Directory Creation Execution

## Status

Controlled sandbox directory creation execution.

## Current checkpoint

- Tag: `v0.19.4-rcis-controlled-real-asset-pdf-sandbox-directory-creation-review`
- Commit: `0f97a2d docs: review controlled real asset pdf sandbox directory creation`

## Purpose

Create only the approved empty sandbox directory for a future real asset PDF placement step, without copying, parsing, or processing any real RSV asset.

## PR-019F boundary

PR-019F:

- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not create PDF fixtures
- does not extract PDF text
- creates only the empty sandbox directory
- inspects only the exact sandbox directory to confirm it is empty
- does not touch real RSV assets
- does not copy real RSV assets
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## PR-019E context

PR-019E approved the directory creation review boundary. It allowed a later execution PR to create only:

```text
sandbox/real_asset_pdf_smoke/
```

PR-019E prohibited copying a PDF, parsing any PDF, or creating Evidence, Knowledge, or Prompt Candidate. It established that directory creation is not placement and is not extraction.

## Execution performed

PR-019F created this approved empty local directory:

```text
sandbox/real_asset_pdf_smoke/
```

The exact command used was:

```powershell
New-Item -ItemType Directory -Force -Path "sandbox\real_asset_pdf_smoke"
```

No file was created, copied, moved, opened, parsed, or read as part of directory creation.

## Verification performed

Verification was limited to these approved commands:

```powershell
Test-Path "sandbox\real_asset_pdf_smoke"

Get-ChildItem "sandbox\real_asset_pdf_smoke" -Force

(Get-ChildItem "sandbox\real_asset_pdf_smoke" -Force).Count

git status --short -uall
```

The observed result was:

- the directory exists
- the directory item count is `0`
- no PDF file exists in the sandbox directory
- no `.gitkeep` exists
- no `.gitignore` exists
- no placeholder file exists
- Git status shows only the PR-019F document as untracked after the document is added
- the empty directory is not tracked by Git

Verification did not inspect any production folder, parse a PDF, or read PDF text.

## Git tracking note

Git does not track empty directories. PR-019F commits only the execution report document. The empty sandbox directory remains a local runtime preparation artifact.

No placeholder file, `.gitkeep`, or sandbox-local `.gitignore` is added to force directory tracking.

## Boundary after execution

Even though the empty directory now exists:

- no real RSV PDF may be copied automatically
- no placement is automatically allowed
- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later placement PR must explicitly approve placing one PDF into the directory

Directory creation is not placement and is not extraction.

## Future placement boundary

A later approved PR must explicitly approve:

- manually selecting exactly one RSV PDF
- manually copying it outside RIE execution
- renaming it to `real-asset-smoke-source.pdf`
- placing it only at `sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- verifying it without parsing PDF content

The original production RSV asset path must never become RIE input.

## Future execution boundary

If a later extraction execution PR is approved after placement, it may process only the approved sandbox-copy PDF through this chain:

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

- copying any real asset in PR-019F
- placing any PDF in the sandbox directory in PR-019F
- adding `.gitkeep`
- adding placeholder files
- adding `.gitignore` in the sandbox directory
- parsing any real PDF in PR-019F
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

### Directory creation mistaken for placement approval

The empty directory does not authorize copying a real PDF. Manual placement remains subject to a separate explicit review and approval.

### Directory creation mistaken for extraction approval

The empty directory does not authorize PDF parsing, extraction, Evidence, Knowledge, or Prompt Candidate creation.

### PDF copied too early

A real PDF could be placed before the placement gate is approved. The directory must remain empty until a later PR explicitly authorizes one manual placement.

### Placeholder files committed

A `.gitkeep`, `.gitignore`, or other placeholder could be added to force Git tracking. The sandbox must remain empty, and PR-019F tracks only this report document.

### Sandbox becomes a batch input

Future code could treat the directory as a discovery root. The approved processing boundary remains one exact sandbox-copy file path, never a directory or batch input.

### Future verification expands into scanning

Verification could drift beyond the exact sandbox path. Future checks must remain non-recursive and must not inspect production folders, the repository root, or the current working directory.

### Extraction output becomes Evidence or Knowledge

Future extraction output could be promoted prematurely. Any later preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

## Recommended next PR

`PR-019G - Controlled Real Asset PDF Sandbox Manual Placement Review`

PR-019G should remain a review gate first. It should decide whether to manually place one real RSV PDF at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

It must not parse any PDF or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Only one docs file is added.
- Empty sandbox directory sandbox/real_asset_pdf_smoke/ is created locally.
- No .gitkeep, .gitignore, or placeholder file is added to the sandbox directory.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF fixture is created.
- No real RSV asset is touched, copied, or scanned.
- Sandbox directory is empty after creation.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019F preparation.
