# PR-019I - Controlled Real Asset PDF Sandbox Placement Verification

## Status

Controlled placement verification.

## Current phase branch

`phase-019-real-asset-pdf-manual-placement`

## Current phase checkpoint

`ca5ebe3 docs: record controlled real asset pdf sandbox manual placement`

## Purpose

Verify the manually placed sandbox PDF using metadata-only checks without parsing, opening, reading PDF text, extracting content, or creating Evidence, Knowledge, or Prompt Candidate.

## PR-019I boundary

PR-019I:

- uses the phase branch workflow
- does not merge to `main` by itself
- does not create an official tag by itself
- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not open PDF content
- does not read PDF text
- does not create PDF fixtures
- does not extract PDF text
- does not ask for or record the production source path
- does not touch the original production RSV asset
- does not copy real RSV assets through Codex or RIE
- does not stage or commit the sandbox PDF
- does not delete or clean up the sandbox PDF
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## PR-019H context

PR-019H recorded the controlled manual placement of exactly one real RSV PDF copy at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

PR-019H confirmed that the PDF was untracked, not staged, and not committed. It also confirmed that no production source path was provided, recorded, or passed to RIE, no PDF content was parsed, and no PDF text was read.

PR-019H established that placement is not extraction.

## Verification performed

PR-019I verification was limited to:

```powershell
$Dir = "sandbox\real_asset_pdf_smoke"
$Target = "sandbox\real_asset_pdf_smoke\real-asset-smoke-source.pdf"

Test-Path $Dir
Test-Path $Target
Get-ChildItem $Dir -File
(Get-ChildItem $Dir -File).Count
Get-Item $Target | Select-Object FullName, Length, Extension
Get-FileHash $Target -Algorithm SHA256
git status --short -uall
git ls-files --stage -- sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
git diff --cached --name-only
```

The observed metadata-only result was:

- current branch: `phase-019-real-asset-pdf-manual-placement`
- target directory exists: `True`
- target file exists: `True`
- target directory file count: `1`
- target filename: `real-asset-smoke-source.pdf`
- target extension: `.pdf`
- target byte size: `1292148`
- SHA256: `67E7D5F723FD84180BCFCF091DFC16801B3498D95B5CAEFE8BE351AEBFC40A82`
- Git status: `?? sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- PDF is untracked: `True`
- PDF is staged: `False`
- PDF is committed: `False`
- staged diff was empty before report preparation: `True`
- production source path is absent: `True`
- PDF text is absent from this report: `True`
- `extracted_text` is absent from this report: `True`

The hash and byte size match the PR-019H placement record. The sandbox PDF was not deleted or modified by PR-019I.

No production source path, PDF text, `extracted_text`, product claim, product benefit, or inferred knowledge from the PDF is included.

## Verification result

The controlled verification result is acceptable:

- exactly one sandbox PDF exists
- the target filename is `real-asset-smoke-source.pdf`
- the target extension is `.pdf`
- the target byte size is greater than `0`
- the SHA256 hash is recorded
- the PDF is untracked
- the PDF is not staged
- the PDF is not committed
- no Evidence, Knowledge, or Prompt Candidate was created

## Git handling

The real PDF appears in Git status as an untracked file. This is expected during the phase.

- The real PDF must never be added with `git add`.
- The real PDF must never be committed.
- Only the PR-019I report document may be staged and committed after review.
- The phase branch must not be merged to `main` until the phase cleanup or closure decision is complete.

PR-019I preparation does not stage or commit any file.

## Boundary after verification

Even after verification succeeds:

- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later extraction PR must explicitly approve any parser run
- a later cleanup or retention PR must decide what happens to the sandbox PDF

Placement verification is not extraction approval.

## Future extraction boundary

If a later extraction execution PR is approved, it may process only the approved sandbox-copy PDF through this chain:

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

PR-019I does not delete the sandbox PDF.

A later PR must decide whether the sandbox copy is:

- deleted after verification, or
- temporarily retained for a later approved extraction execution PR

The default policy remains deletion after the approved review window unless temporary retention is explicitly approved.

## Forbidden scope

The following remain forbidden:

- production RSV folder scan
- direct production asset processing
- using the production source path as RIE input
- recording the production source path
- multiple real assets
- recursive scan
- current working directory scan
- repository-wide scan
- wildcard paths
- automatic copy from production folders
- batch processing
- parsing PDF content
- opening PDF content
- reading PDF text
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
- staging the real PDF
- committing the real PDF
- deleting the sandbox PDF
- cleanup during PR-019I
- merging the phase branch to `main` during PR-019I
- creating an official tag during PR-019I

## Risk review

### PDF is accidentally staged or committed

The untracked real PDF could be included in a broad Git operation. Only the report document may be selected for a later reviewed commit, and the PDF must remain untracked and unstaged.

### Sandbox contents change after verification

The verification record is a point-in-time metadata result. Any later action must reverify file count, size, hash, and Git state before proceeding.

### Production source path leaks

The production source path could leak into documentation, logs, or RIE input. It was not requested or recorded and must remain undisclosed.

### Verification expands into parsing

Metadata verification could drift into opening or reading the PDF. Verification must remain limited to approved path and file metadata until separately authorized.

### Verification mistaken for extraction approval

Successful placement verification does not authorize parser execution. Extraction remains a separate gated action.

### Extraction output becomes Evidence or Knowledge

Future extraction output could be promoted prematurely. Any preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

### Retained PDF is forgotten

The sandbox copy could remain beyond its approved window. A later PR must explicitly decide retention or exact-file cleanup.

### Phase branch merged before closure

Merging before cleanup or retention is resolved could weaken the phase boundary. The branch must remain unmerged until closure review.

## Recommended next PR

`PR-019J - Controlled Real Asset PDF Sandbox Placement Closure and Retention Decision`

PR-019J should decide whether to delete the sandbox PDF after verification or temporarily retain it for a later approved extraction execution PR.

PR-019J must not parse any PDF or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Phase branch phase-019-real-asset-pdf-manual-placement is used.
- Only one docs file is added for PR-019I.
- Existing sandbox PDF remains at sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf.
- Target directory exists.
- Target file exists.
- Target directory contains exactly one file.
- Target filename is real-asset-smoke-source.pdf.
- Target file extension is .pdf or .PDF.
- Target file byte size is greater than 0.
- SHA256 hash is recorded.
- Sandbox PDF remains untracked or at minimum unstaged.
- Sandbox PDF is not committed.
- Sandbox PDF is not deleted or cleaned up by PR-019I.
- No .gitkeep, .gitignore, or placeholder file is added to the sandbox directory.
- No production source path is provided, recorded, or passed to RIE.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF content is opened.
- No PDF text is read.
- No PDF fixture is created.
- No extracted_text is exposed.
- No Evidence, Knowledge, or Prompt Candidate is created.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019I preparation.
