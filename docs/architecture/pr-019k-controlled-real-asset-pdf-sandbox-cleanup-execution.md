# PR-019K - Controlled Real Asset PDF Sandbox Cleanup Execution

## Status

Controlled cleanup execution.

## Current phase branch

`phase-019-real-asset-pdf-manual-placement`

## Current phase checkpoint

`a052865 docs: decide controlled real asset pdf sandbox cleanup`

## Purpose

Execute the approved cleanup decision by deleting only the exact sandbox-copy real PDF after placement and metadata verification, without deleting the sandbox directory, parsing PDF content, reading PDF text, extracting content, or creating Evidence, Knowledge, or Prompt Candidate.

## PR-019K boundary

PR-019K:

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
- deletes only the exact sandbox-copy PDF
- does not delete the sandbox directory
- does not create Evidence, Knowledge, or Prompt Candidate
- does not authorize AI inference

## PR-019J context

PR-019J recorded the decision to delete the sandbox PDF in a later explicit cleanup execution PR. It did not delete or clean up the sandbox PDF.

PR-019J approved only this cleanup target:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

PR-019J prohibited wildcard deletion, recursive deletion, broader-path deletion, and sandbox-directory deletion.

## Pre-cleanup state

The approved cleanup target was:

```text
sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf
```

The verified pre-cleanup metadata was:

- target directory existed: `True`
- target file existed: `True`
- target directory file count: `1`
- target filename: `real-asset-smoke-source.pdf`
- target extension: `.pdf`
- target byte size: `1292148`
- SHA256: `67E7D5F723FD84180BCFCF091DFC16801B3498D95B5CAEFE8BE351AEBFC40A82`
- PDF was untracked: `True`
- PDF was staged: `False`
- PDF was committed: `False`
- staged diff was empty before cleanup: `True`
- production source path was absent: `True`
- PDF text was absent: `True`
- `extracted_text` was absent: `True`

No production source path, PDF text, `extracted_text`, product claim, product benefit, or inferred knowledge from the PDF is included.

## Cleanup executed

The exact cleanup command used was:

```powershell
Remove-Item -LiteralPath "sandbox\real_asset_pdf_smoke\real-asset-smoke-source.pdf" -Force
```

Cleanup remained within these controls:

- only the exact target file was deleted
- no wildcard path was used
- no recursive delete was used
- the sandbox directory was not deleted
- no broader path was deleted
- no production path was used
- no production file was touched
- no PDF content was parsed
- no PDF content was opened
- no PDF text was read
- no Evidence, Knowledge, or Prompt Candidate was created

## Post-cleanup verification

The observed post-cleanup result was:

- target directory exists: `True`
- target file exists: `False`
- target directory item count: `0`
- Git status after cleanup, before report creation: clean
- sandbox PDF appears in Git status: `False`
- sandbox PDF is staged: `False`
- sandbox PDF is committed: `False`
- staged diff is empty: `True`
- only the PR-019K report appears as untracked after report creation: `True`
- sandbox directory remains empty: `True`

The sandbox directory remains a local empty preparation artifact and is not tracked by Git.

## Cleanup result

The controlled cleanup result is acceptable:

- the sandbox directory exists
- the target file does not exist
- the sandbox directory item count is `0`
- the sandbox PDF is not staged
- the sandbox PDF is not committed
- the sandbox PDF no longer appears in Git status
- only the PR-019K report remains untracked before commit

## Boundary after cleanup

Even after cleanup succeeds:

- no PDF parsing occurred
- no extraction occurred
- no Evidence was created
- no Knowledge was created
- no Prompt Candidate was created
- no official merge or tag is automatically allowed until phase closure is reviewed

Cleanup is not extraction approval and is not phase closure by itself.

## Future phase closure boundary

A later closure PR should confirm:

- PR-019H, PR-019I, PR-019J, and PR-019K reports are committed on the phase branch
- the sandbox PDF is gone
- the sandbox directory is empty or remains local-only
- the Git working tree is clean after committing the PR-019K report
- no real asset remains untracked
- no PDF was committed
- no Evidence, Knowledge, or Prompt Candidate was created
- only after closure review should the phase branch be merged to `main` and tagged

## Future extraction boundary

If a future extraction execution phase is approved, it must start from a separate review gate and may require a fresh approved sandbox placement.

No extraction authority carries forward from placement or cleanup.

## Forbidden scope

The following remain forbidden:

- deleting the sandbox directory
- deleting broader paths
- using wildcard delete
- using recursive delete
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
- merging the phase branch to `main` during PR-019K
- creating an official tag during PR-019K

## Risk review

### Cleanup deletes the wrong target

An incorrect path could remove an unintended file. PR-019K used only the exact approved `LiteralPath` and verified the target before deletion.

### Cleanup deletes the sandbox directory

Deleting the directory would exceed the approved scope. PR-019K deleted only the file and verified that the directory still exists.

### Wildcard or recursive deletion is used

A broad delete could affect unrelated files or paths. PR-019K used neither a wildcard nor recursion.

### Cleanup mistaken for extraction approval

Removing the sandbox copy does not authorize parsing or extraction. Any future extraction requires a new gated phase and fresh approved placement if needed.

### Phase branch merged before closure review

Cleanup alone does not establish merge readiness. PR-019L must review committed reports, clean state, and phase boundaries first.

### Future extraction assumes the PDF still exists

The sandbox PDF has been deleted. Any future phase must not assume it remains available and must explicitly approve a fresh placement.

### Production source path leaks

The production source path could leak into documents or logs. It was not requested or recorded and remains undisclosed.

### Deleted copy is needed without a fresh review

Recreating the sandbox copy without a new placement gate would bypass the controlled boundary. Any new placement requires explicit review and user action.

## Recommended next PR

`PR-019L - Controlled Real Asset PDF Manual Placement Phase Closure Review`

PR-019L should verify that:

- PR-019H, PR-019I, PR-019J, and PR-019K reports are committed
- the sandbox PDF is gone
- the sandbox directory is empty
- no real asset remains untracked
- no PDF was staged or committed
- no parsing, extraction, Evidence, Knowledge, or Prompt Candidate occurred

PR-019L should remain review-only first. It must not parse any PDF or create Evidence, Knowledge, or Prompt Candidate.

## Acceptance Criteria

- Phase branch phase-019-real-asset-pdf-manual-placement is used.
- Only one docs file is added for PR-019K.
- Cleanup target before deletion is sandbox/real_asset_pdf_smoke/real-asset-smoke-source.pdf.
- Pre-cleanup target directory exists.
- Pre-cleanup target file exists.
- Pre-cleanup target directory contains exactly one file.
- Pre-cleanup target filename is real-asset-smoke-source.pdf.
- Pre-cleanup target file extension is .pdf or .PDF.
- Pre-cleanup target file byte size is greater than 0.
- Pre-cleanup SHA256 hash is recorded.
- Sandbox PDF is untracked or at minimum unstaged before cleanup.
- Sandbox PDF is not committed before cleanup.
- Cleanup deletes only the exact target file.
- Cleanup uses Remove-Item with LiteralPath.
- Cleanup does not use wildcard paths.
- Cleanup does not use recursive delete.
- Cleanup does not delete the sandbox directory.
- Cleanup does not delete production files.
- Post-cleanup sandbox directory exists.
- Post-cleanup target file does not exist.
- Post-cleanup sandbox directory item count is 0.
- Sandbox PDF no longer appears in git status after cleanup.
- Sandbox PDF is not staged.
- Sandbox PDF is not committed.
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
- No commit is created by PR-019K preparation.
