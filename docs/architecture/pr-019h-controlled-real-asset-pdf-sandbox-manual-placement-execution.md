# PR-019H - Controlled Real Asset PDF Sandbox Manual Placement Execution

## Status

Controlled manual placement execution.

## Current checkpoint

- Tag: `v0.19.6-rcis-controlled-real-asset-pdf-sandbox-manual-placement-review`
- Commit: `776ea1b docs: review controlled real asset pdf sandbox manual placement`

## Phase branch

`phase-019-real-asset-pdf-manual-placement`

PR-019H uses the phase branch workflow. It does not merge to `main` by itself and does not create an official tag by itself.

## Purpose

Record the controlled manual placement of exactly one real RSV PDF copy into the approved sandbox path without parsing, extracting, reading PDF text, or creating Evidence, Knowledge, or Prompt Candidate.

## PR-019H boundary

PR-019H:

- does not modify production code
- does not modify tests
- does not modify `pyproject.toml`
- does not modify lock files
- does not install dependencies
- does not change the virtual environment
- does not parse PDFs
- does not create PDF fixtures
- does not extract PDF text
- does not ask for or record the production source path
- does not touch the original production RSV asset
- does not copy real RSV assets through Codex or RIE
- allows only a human/manual copy of one real RSV PDF into the approved sandbox target
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference
- does not stage or commit the real PDF

## PR-019G context

PR-019G approved the manual placement review boundary and locked this approved target:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

PR-019G established that manual placement is not extraction, future verification must not parse PDF content, and the production source path must never become RIE input.

## Execution performed

The user manually placed exactly one copied real RSV PDF at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Execution remained within these controls:

- the user performed the copy manually
- the original production source path was not provided to Codex
- the original production source path was not recorded
- the original production source path was not passed to RIE
- Codex did not copy from production
- RIE did not copy from production
- no wildcard path was used
- no recursive command was used
- no batch copy was used
- no PDF content was parsed
- no PDF text was read

## Verification performed

Verification was limited to:

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
```

The observed metadata-only result was:

- target directory exists: `True`
- target file exists: `True`
- target directory file count: `1`
- target filename: `real-asset-smoke-source.pdf`
- target extension: `.pdf`
- target byte size: `1292148`
- SHA256: `67E7D5F723FD84180BCFCF091DFC16801B3498D95B5CAEFE8BE351AEBFC40A82`
- Git status for the PDF: `?? sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf`
- PDF is untracked: `True`
- PDF is staged: `False`
- PDF is committed: `False`

No production source path, PDF text, `extracted_text`, product claim, product benefit, or inferred knowledge is included in this report.

## Placement result

The controlled placement result is acceptable:

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

The real PDF appears in Git status as an untracked file. That is expected during this phase.

- The real PDF must never be added with `git add`.
- The real PDF must never be committed.
- Only the PR-019H report document may be staged and committed after review.
- The phase branch must not be merged to `main` until the phase cleanup or closure decision is complete.

PR-019H preparation does not stage or commit any file.

## Boundary after execution

Even after placement succeeds:

- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- a later verification or extraction PR must explicitly approve any next action

Manual placement is not extraction.

## Future verification boundary

The next step should verify placement state without parsing PDF content. Verification must remain limited to the approved sandbox target and metadata such as existence, file count, extension, byte size, hash, and Git state.

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

PR-019H does not delete the sandbox PDF.

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
- merging the phase branch to `main` during PR-019H
- creating an official tag during PR-019H

## Risk review

### PDF is accidentally staged or committed

The untracked real PDF could be included in a broad Git operation. Only the report document may be selected for any later reviewed commit; the PDF must remain untracked and unstaged.

### Production source path leaks

The source path could leak into documentation, logs, or RIE input. It was not requested or recorded and must remain undisclosed.

### More than one sandbox file

Additional files would violate the single-file boundary. Verification observed exactly one file at placement time, and later verification must stop if that changes.

### Wrong file type

A non-PDF could be placed under the neutral filename. Verification observed the `.pdf` extension and positive size without parsing content.

### Verification expands into parsing

Metadata verification could drift into opening or reading the PDF. All verification must remain limited to path and file metadata until separately approved.

### Placement mistaken for extraction approval

Successful placement does not authorize parser execution. Extraction remains a separate gated action.

### Extraction output becomes Evidence or Knowledge

Future extraction output could be promoted prematurely. Any preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

### Retained PDF is forgotten

The sandbox copy could remain beyond its approved window. A later PR must explicitly decide retention or exact-file cleanup.

### Phase branch merged before closure

Merging before the real PDF is cleaned up or its retention is explicitly resolved could weaken the phase boundary. The branch must remain unmerged until closure review.

## Recommended next PR

`PR-019I - Controlled Real Asset PDF Sandbox Placement Verification`

PR-019I should verify the placed sandbox PDF without parsing it. It must not create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Phase branch phase-019-real-asset-pdf-manual-placement is used.
- Only one docs file is added for PR-019H.
- Exactly one real RSV PDF copy is manually placed by the user at sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf.
- Production source path is not provided to Codex.
- Production source path is not recorded.
- Production source path is not passed to RIE.
- Codex does not copy the real asset from production.
- RIE does not copy the real asset from production.
- Target directory exists.
- Target file exists.
- Target directory contains exactly one file.
- Target file extension is .pdf or .PDF.
- Target file byte size is greater than 0.
- SHA256 hash is recorded.
- Sandbox PDF remains untracked or at minimum unstaged.
- Sandbox PDF is not committed.
- No .gitkeep, .gitignore, or placeholder file is added to the sandbox directory.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed.
- No virtual environment changes are made.
- No PDF parsing is performed.
- No PDF text is read.
- No PDF fixture is created.
- No extracted_text is exposed.
- No Evidence, Knowledge, or Prompt Candidate is created.
- Full tests pass.
- pypdf imports successfully and version 6.14.2 is recorded.
- No non-ASCII or garbled characters remain.
- No commit is created by PR-019H preparation.
