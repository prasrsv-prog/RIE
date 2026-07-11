# PR-019J - Controlled Real Asset PDF Sandbox Placement Closure and Retention Decision

## Status

Controlled closure and retention decision.

## Current phase branch

`phase-019-real-asset-pdf-manual-placement`

## Current phase checkpoint

`c4d1800 docs: verify controlled real asset pdf sandbox placement`

## Purpose

Decide the safe closure path for the manually placed sandbox PDF after placement and metadata verification, without deleting, parsing, opening, reading PDF text, extracting content, or creating Evidence, Knowledge, or Prompt Candidate in PR-019J.

## PR-019J boundary

PR-019J:

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

## Prior phase context

### PR-019H

PR-019H recorded the controlled manual placement of exactly one real RSV PDF copy at:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

PR-019H confirmed that the PDF was untracked, not staged, and not committed. It also confirmed that no production source path was provided, recorded, or passed to RIE, no PDF content was parsed, and no PDF text was read.

### PR-019I

PR-019I verified the placed sandbox PDF using metadata-only checks. It confirmed the target file count, filename, extension, byte size, SHA256 hash, and Git state.

PR-019I confirmed that the hash and byte size matched PR-019H. It did not delete or clean up the sandbox PDF, parse or open PDF content, read PDF text, or create Evidence, Knowledge, or Prompt Candidate.

## Current placement state

The current approved target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The current metadata-only state is:

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

The byte size and hash remain unchanged from PR-019H and PR-019I. PR-019J does not delete or modify the sandbox PDF.

No production source path, PDF text, `extracted_text`, product claim, product benefit, or inferred knowledge from the PDF is included.

## Decision

The selected closure decision is:

**Delete the sandbox PDF in a later explicit cleanup execution PR.**

Rationale:

- The placement and verification objective has been completed.
- The sandbox PDF is a real asset and should not remain in the repository working directory longer than needed.
- Keeping the sandbox PDF untracked during merge or tag preparation increases the risk of accidental staging or forgotten retention.
- A clean working tree is preferred before merging the phase branch and creating the official phase tag.
- If future extraction is needed, a later phase can repeat controlled manual placement or explicitly approve temporary retention before extraction.

## Decision status

- PR-019J records the decision only.
- PR-019J does not perform cleanup.
- PR-019J does not delete the sandbox PDF.
- PR-019J does not stage or commit the sandbox PDF.
- PR-019J does not merge the phase branch.
- PR-019J does not create an official tag.

Cleanup requires a later explicit execution PR.

## Approved future cleanup target

The only approved future cleanup target is:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

Future cleanup rules:

- cleanup must delete only the exact target file
- cleanup must not delete the sandbox directory
- cleanup must not delete production files
- cleanup must not use wildcard paths
- cleanup must not use recursive delete
- cleanup must not delete broader paths
- cleanup must verify Git status afterward
- cleanup must confirm the PDF is gone
- cleanup must confirm no production path was used
- cleanup must be recorded in a later explicit execution report

## Boundary after decision

Even after the closure decision:

- no PDF parsing is automatically allowed
- no extraction is automatically allowed
- no Evidence is automatically allowed
- no Knowledge is automatically allowed
- no Prompt Candidate is automatically allowed
- cleanup is not automatically performed until a later approved cleanup execution PR

The closure decision is not cleanup execution and is not extraction approval.

## Future extraction boundary

If a future extraction execution phase is approved, it must pass through a separate review gate.

It may process only an approved sandbox-copy PDF through this chain:

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

- deleting the sandbox PDF in PR-019J
- cleanup during PR-019J
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
- merging the phase branch to `main` during PR-019J
- creating an official tag during PR-019J

## Risk review

### PDF is accidentally staged or committed

The untracked real PDF could be included in a broad Git operation. Only the PR-019J report may be selected for a later reviewed commit, and the PDF must remain untracked and unstaged.

### PDF remains longer than needed

Deferring cleanup leaves a real asset in the working directory. PR-019K should perform the exact-file cleanup promptly after review.

### Cleanup deletes the wrong target

An incorrect path could remove an unintended file. Future cleanup must use only the exact approved sandbox-copy path and verify it before deletion.

### Cleanup uses wildcard or recursive delete

A broad delete could affect the sandbox directory or unrelated files. Future cleanup must use no wildcard, no recursion, and no broader target.

### Production source path leaks

The production source path could leak into documentation, logs, or RIE input. It was not requested or recorded and must remain undisclosed.

### Decision mistaken for cleanup execution

Recording the deletion decision does not authorize deletion in PR-019J. Cleanup requires the separately approved PR-019K execution.

### Decision mistaken for extraction approval

Closure does not authorize parser execution. Any future extraction requires a separate gated phase.

### Extraction output becomes Evidence or Knowledge

Future extraction output could be promoted prematurely. Any preview must remain bounded parser output and must not enter Evidence, Official Knowledge, Product Knowledge, or Prompt Candidate paths.

### Phase branch merged before cleanup

Merging while the real PDF remains untracked creates accidental staging and forgotten-retention risk. Cleanup and closure verification must occur before merge or tag creation.

## Recommended next PR

`PR-019K - Controlled Real Asset PDF Sandbox Cleanup Execution`

PR-019K should delete only:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

PR-019K must not delete the sandbox directory, parse any PDF, or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Phase branch phase-019-real-asset-pdf-manual-placement is used.
- Only one docs file is added for PR-019J.
- Existing sandbox PDF remains at sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf during PR-019J.
- PR-019J records the decision to delete the sandbox PDF in a later explicit cleanup execution PR.
- PR-019J does not delete or clean up the sandbox PDF.
- PR-019J does not stage the sandbox PDF.
- PR-019J does not commit the sandbox PDF.
- Target directory exists.
- Target file exists.
- Target directory contains exactly one file.
- Target filename is real-asset-smoke-source.pdf.
- Target file extension is .pdf or .PDF.
- Target file byte size is greater than 0.
- SHA256 hash is recorded.
- Sandbox PDF remains untracked or at minimum unstaged.
- Sandbox PDF is not committed.
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
- No commit is created by PR-019J preparation.
